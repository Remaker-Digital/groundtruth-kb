#!/usr/bin/env python3
"""Create and validate implementation-start authorization packets.

The packet is a machine-readable proof that a local implementation session is
scoped to one bridge document whose live latest status is GO.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sqlite3
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_PACKET_RELATIVE_PATH = Path(".gtkb-state/implementation-authorizations/current.json")
BY_BRIDGE_DIRECTORY_RELATIVE_PATH = Path(".gtkb-state/implementation-authorizations/by-bridge")
DEFAULT_EXPIRY_MINUTES = 480
BOOTSTRAP_BRIDGE_IDS = frozenset({"gtkb-implementation-start-authorization-gate"})
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|pending|no relevant|not applicable|n/a)\b", re.IGNORECASE)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TARGET_PATHS_RE = re.compile(
    r"(?:\*\*)?target_paths(?:\*\*)?\s*:(?:\*\*)?\s*(\[[^\n]+\])",
    re.IGNORECASE,
)
PROJECT_AUTHORIZATION_KEYS = frozenset({"project authorization", "project authorization id"})
PROJECT_KEYS = frozenset({"project", "project id"})
WORK_ITEM_KEYS = frozenset({"work item", "work item id", "backlog item", "backlog item id"})


class AuthorizationError(RuntimeError):
    """Raised when an implementation authorization packet cannot be issued."""


@dataclass(frozen=True)
class BridgeEntry:
    bridge_id: str
    versions: list[tuple[str, str]]

    @property
    def latest_status(self) -> str:
        return self.versions[0][0]

    @property
    def latest_path(self) -> str:
        return self.versions[0][1]


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def now_iso() -> str:
    return now_utc().isoformat().replace("+00:00", "Z")


def parse_iso(value: str) -> datetime:
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def parse_optional_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return parse_iso(value)


def project_root_from_arg(value: str | None = None) -> Path:
    if value:
        return Path(value).resolve()
    return Path(__file__).resolve().parent.parent


def packet_path(project_root: Path) -> Path:
    return project_root / DEFAULT_PACKET_RELATIVE_PATH


def packet_path_for_bridge(project_root: Path, bridge_id: str) -> Path:
    """Return the named-cache packet path for `bridge_id`.

    Per-bridge packets live at `.gtkb-state/implementation-authorizations/by-bridge/<bridge-id>.json`
    and survive overwrites of the `current.json` active pointer.
    """
    safe_id = bridge_id.strip()
    if not safe_id or "/" in safe_id or "\\" in safe_id or safe_id in {".", ".."}:
        raise AuthorizationError(f"Invalid bridge_id for named packet path: {bridge_id!r}")
    return project_root / BY_BRIDGE_DIRECTORY_RELATIVE_PATH / f"{safe_id}.json"


def groundtruth_db_path(project_root: Path) -> Path:
    config_path = project_root / "groundtruth.toml"
    if config_path.is_file():
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        db_value = data.get("groundtruth", {}).get("db_path")
        if isinstance(db_value, str) and db_value.strip():
            db_path = Path(db_value)
            return db_path if db_path.is_absolute() else project_root / db_path
    return project_root / "groundtruth.db"


def _filename_matches_doc(path: str, doc_id: str) -> bool:
    """Return True iff path is bridge/<doc_id>.md or bridge/<doc_id>-NNN.md.

    Accepts both the v1 form (no version suffix; e.g. bridge/foo.md) and the
    v2+ form (zero-padded version suffix; e.g. bridge/foo-022.md). Boundary
    based matching avoids the disambiguation problem when a doc_id itself
    ends in -NNN (e.g. gtkb-single-harness-bridge-dispatcher-001).
    """
    prefix = f"bridge/{doc_id}"
    if not path.startswith(prefix):
        return False
    suffix = path[len(prefix):]
    return suffix == ".md" or re.match(r"^-\d{3,}\.md$", suffix) is not None


def parse_bridge_index(project_root: Path) -> dict[str, BridgeEntry]:
    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        raise AuthorizationError("bridge/INDEX.md not found")
    entries: dict[str, BridgeEntry] = {}
    current_id: str | None = None
    current_versions: list[tuple[str, str]] = []
    for raw_line in index_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if line.startswith("Document: "):
            if current_id is not None and current_versions:
                entries[current_id] = BridgeEntry(current_id, current_versions)
            current_id = line.removeprefix("Document: ").strip()
            current_versions = []
            continue
        match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+(bridge/.+\.md)$", line)
        if current_id and match:
            status, path = match.group(1), match.group(2)
            if not _filename_matches_doc(path, current_id):
                # Misattributed status line: silently skip in parse_bridge_index.
                # Strict per-bridge consistency is enforced by bridge_entry()
                # for the specific queried bridge_id, so unrelated malformed
                # entries elsewhere in the index do not globally block the gate.
                continue
            current_versions.append((status, path))
    if current_id is not None and current_versions:
        entries[current_id] = BridgeEntry(current_id, current_versions)
    return entries


def _validate_bridge_index_for(project_root: Path, bridge_id: str) -> None:
    """Strict per-bridge consistency check: raise if any status line under
    bridge_id's Document section has a filename that does not match bridge_id
    via _filename_matches_doc(). This is the gate's fail-closed enforcement
    point for the specific queried bridge.
    """
    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        raise AuthorizationError("bridge/INDEX.md not found")
    in_target = False
    for raw_line in index_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if line.startswith("Document: "):
            doc_id = line.removeprefix("Document: ").strip()
            in_target = doc_id == bridge_id
            continue
        if in_target:
            match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+(bridge/.+\.md)$", line)
            if match:
                path = match.group(2)
                if not _filename_matches_doc(path, bridge_id):
                    raise AuthorizationError(
                        f"Bridge INDEX status line filename does not match enclosing Document: "
                        f"{line!r} under Document: {bridge_id!r}; refusing to authorize"
                    )


def bridge_entry(project_root: Path, bridge_id: str) -> BridgeEntry:
    _validate_bridge_index_for(project_root, bridge_id)
    entries = parse_bridge_index(project_root)
    entry = entries.get(bridge_id)
    if entry is None:
        raise AuthorizationError(f"Bridge document not found in INDEX: {bridge_id}")
    return entry


def approved_files_for_go(entry: BridgeEntry) -> tuple[str, str]:
    if entry.latest_status != "GO":
        raise AuthorizationError(f"Implementation authorization requires latest GO; found {entry.latest_status}")
    go_file = entry.latest_path
    for status, path in entry.versions[1:]:
        if status in {"NEW", "REVISED"}:
            return path, go_file
    raise AuthorizationError(f"No approved proposal file found under latest GO for {entry.bridge_id}")


def section_body(markdown: str, heading: str) -> str:
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group(1).strip().lower() == heading.lower():
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
            return markdown[start:end].strip()
    return ""


def extract_spec_links(markdown: str) -> list[str]:
    body = section_body(markdown, "Specification Links")
    if not body:
        raise AuthorizationError("Approved proposal is missing ## Specification Links")
    if PLACEHOLDER_RE.search(body):
        raise AuthorizationError("Approved proposal has placeholder text in Specification Links")
    links: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith(("-", "*")):
            continue
        ticks = re.findall(r"`([^`]+)`", stripped)
        links.extend(ticks or [stripped.lstrip("-* ").strip()])
    links = [link for link in links if link]
    if not links:
        raise AuthorizationError("Approved proposal has no concrete specification links")
    return links


def extract_target_paths(markdown: str) -> list[str]:
    match = TARGET_PATHS_RE.search(markdown)
    if match:
        raw = match.group(1)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AuthorizationError("target_paths metadata is not valid JSON") from exc
        if not isinstance(parsed, list) or not all(isinstance(item, str) and item.strip() for item in parsed):
            raise AuthorizationError("target_paths must be a non-empty JSON list of strings")
        return [item.strip().replace("\\", "/") for item in parsed]

    body = section_body(markdown, "Files Expected To Change")
    targets: list[str] = []
    for line in body.splitlines():
        if not line.strip().startswith(("-", "*")):
            continue
        targets.extend(re.findall(r"`([^`]+)`", line))
    targets = [target.strip().replace("\\", "/") for target in targets if target.strip()]
    if not targets:
        raise AuthorizationError("Approved proposal is missing concrete target_paths or Files Expected To Change")
    return targets


def _clean_metadata_value(raw: str) -> str:
    ticked = re.search(r"`([^`]+)`", raw)
    if ticked:
        return ticked.group(1).strip()
    value = raw.strip().strip("*").strip()
    return value.split()[0].strip("`.,;") if value else ""


def extract_metadata_value(markdown: str, keys: set[str]) -> str | None:
    for raw_line in markdown.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        while stripped.startswith(("-", "*")):
            stripped = stripped[1:].strip()
        candidate = stripped.replace("**", "")
        if ":" not in candidate:
            continue
        raw_key, raw_value = candidate.split(":", 1)
        key = raw_key.strip().lower()
        if key in keys:
            value = _clean_metadata_value(raw_value)
            return value or None
    return None


def _json_list(row: sqlite3.Row, field: str) -> list[str]:
    raw = row[field]
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(value) for value in parsed]


def _project_authorization_row(project_root: Path, authorization_id: str) -> sqlite3.Row:
    db_path = groundtruth_db_path(project_root)
    if not db_path.is_file():
        raise AuthorizationError(f"GroundTruth DB not found for project authorization: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM current_project_authorizations WHERE id = ?",
            (authorization_id,),
        ).fetchone()
    except sqlite3.OperationalError as exc:
        raise AuthorizationError("GroundTruth DB is missing project authorization schema") from exc
    finally:
        conn.close()
    if row is None:
        raise AuthorizationError(f"Project authorization not found: {authorization_id}")
    return row


def packet_spec_links(packet: dict[str, Any]) -> list[str]:
    raw_links = packet.get("spec_links")
    if not isinstance(raw_links, list):
        raise AuthorizationError("Implementation authorization packet has invalid spec_links metadata")
    spec_links = [link.strip() for link in raw_links if isinstance(link, str) and link.strip()]
    if len(spec_links) != len(raw_links):
        raise AuthorizationError("Implementation authorization packet has invalid spec_links metadata")
    if not spec_links:
        raise AuthorizationError("Implementation authorization packet has empty spec_links metadata")
    return spec_links


def _project_is_active(project_root: Path, project_id: str) -> bool:
    conn = sqlite3.connect(groundtruth_db_path(project_root))
    try:
        row = conn.execute("SELECT status FROM current_projects WHERE id = ?", (project_id,)).fetchone()
    finally:
        conn.close()
    return bool(row and row[0] == "active")


def _work_item_in_project(project_root: Path, project_id: str, work_item_id: str) -> bool:
    conn = sqlite3.connect(groundtruth_db_path(project_root))
    try:
        row = conn.execute(
            """SELECT 1 FROM current_project_work_item_memberships
               WHERE project_id = ? AND work_item_id = ? AND status = 'active'""",
            (project_id, work_item_id),
        ).fetchone()
    finally:
        conn.close()
    return row is not None


def validate_project_authorization_row(
    project_root: Path,
    row: sqlite3.Row,
    *,
    proposal_project_id: str | None = None,
    work_item_id: str | None = None,
    spec_links: list[str] | None = None,
) -> dict[str, Any]:
    authorization_id = str(row["id"])
    project_id = str(row["project_id"])
    if row["status"] != "active":
        raise AuthorizationError(f"Project authorization {authorization_id} is not active")
    try:
        expires_at = parse_optional_iso(row["expires_at"])
    except ValueError as exc:
        raise AuthorizationError(f"Project authorization {authorization_id} has invalid expires_at") from exc
    if expires_at is not None and expires_at < now_utc():
        raise AuthorizationError(f"Project authorization {authorization_id} has expired")
    if proposal_project_id and proposal_project_id != project_id:
        raise AuthorizationError(
            f"Project authorization {authorization_id} is for {project_id}, not proposal project {proposal_project_id}"
        )
    if not _project_is_active(project_root, project_id):
        raise AuthorizationError(f"Project authorization {authorization_id} is not attached to an active project")

    included_items = set(_json_list(row, "included_work_item_ids"))
    excluded_items = set(_json_list(row, "excluded_work_item_ids"))
    if work_item_id:
        if work_item_id in excluded_items:
            raise AuthorizationError(f"Work item {work_item_id} is excluded by project authorization {authorization_id}")
        if work_item_id not in included_items and not _work_item_in_project(project_root, project_id, work_item_id):
            raise AuthorizationError(
                f"Work item {work_item_id} is neither included in nor an active member of project {project_id}"
            )

    excluded_specs = set(_json_list(row, "excluded_spec_ids"))
    blocked_specs = sorted(excluded_specs.intersection(spec_links or []))
    if blocked_specs:
        raise AuthorizationError(
            f"Spec link(s) excluded by project authorization {authorization_id}: {', '.join(blocked_specs)}"
        )

    return {
        "id": authorization_id,
        "project_id": project_id,
        "status": row["status"],
        "authorization_name": row["authorization_name"],
        "owner_decision_deliberation_id": row["owner_decision_deliberation_id"],
        "scope_summary": row["scope_summary"],
        "expires_at": row["expires_at"],
        "proposal_project_id": proposal_project_id,
        "work_item_id": work_item_id,
    }


def extract_and_validate_project_authorization(
    project_root: Path,
    proposal: str,
    spec_links: list[str],
) -> dict[str, Any] | None:
    authorization_id = extract_metadata_value(proposal, PROJECT_AUTHORIZATION_KEYS)
    if not authorization_id:
        return None
    row = _project_authorization_row(project_root, authorization_id)
    return validate_project_authorization_row(
        project_root,
        row,
        proposal_project_id=extract_metadata_value(proposal, PROJECT_KEYS),
        work_item_id=extract_metadata_value(proposal, WORK_ITEM_KEYS),
        spec_links=spec_links,
    )


def requirement_sufficiency_state(markdown: str) -> str:
    body = section_body(markdown, "Requirement Sufficiency")
    if not body:
        return "missing"
    if "New or revised requirement required before implementation" in body:
        return "gap"
    if "Existing requirements sufficient" in body:
        return "sufficient"
    return "missing"


def has_spec_derived_verification(markdown: str) -> bool:
    headings = (
        "Specification-Derived Verification",
        "Specification-Derived Verification Plan",
        "Spec-Derived Test Plan",
        "Verification Plan",
    )
    return any(section_body(markdown, heading) for heading in headings)


def normalize_relative_path(project_root: Path, path_text: str) -> str:
    raw = Path(path_text.replace("\\", "/"))
    candidate = raw if raw.is_absolute() else project_root / raw
    try:
        return candidate.resolve(strict=False).relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise AuthorizationError(f"Path escapes project root: {path_text}") from exc


def packet_hash(packet: dict[str, Any]) -> str:
    material = {key: value for key, value in packet.items() if key != "packet_hash"}
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def create_authorization_packet(
    project_root: Path,
    bridge_id: str,
    *,
    expires_minutes: int = DEFAULT_EXPIRY_MINUTES,
) -> dict[str, Any]:
    entry = bridge_entry(project_root, bridge_id)
    proposal_rel, go_rel = approved_files_for_go(entry)
    proposal_path = project_root / proposal_rel
    go_path = project_root / go_rel
    if not proposal_path.is_file() or not go_path.is_file():
        raise AuthorizationError("Approved proposal or GO file is missing on disk")

    proposal = proposal_path.read_text(encoding="utf-8-sig")

    # Accumulate all format-check failures in a single pass so authors see every
    # issue at once instead of discovering them serially. Per owner directive
    # 2026-05-14 S350 "When you find a problem, fix it" addressing the
    # deterministic-services-principle friction: fail-fast was consuming session
    # budget across repeated bridge revisions where each attempt revealed one
    # more format defect.
    errors: list[str] = []
    spec_links: list[str] = []
    target_paths: list[str] = []
    project_authorization: dict[str, Any] | None = None

    try:
        spec_links = extract_spec_links(proposal)
    except AuthorizationError as exc:
        errors.append(str(exc))

    try:
        target_paths = extract_target_paths(proposal)
    except AuthorizationError as exc:
        errors.append(str(exc))

    try:
        project_authorization = extract_and_validate_project_authorization(
            project_root, proposal, spec_links
        )
    except AuthorizationError as exc:
        errors.append(str(exc))

    if not has_spec_derived_verification(proposal):
        errors.append("Approved proposal is missing a spec-derived verification plan")

    sufficiency = requirement_sufficiency_state(proposal)
    if sufficiency == "gap":
        errors.append(
            "Approved proposal says new or revised requirements are required before implementation"
        )
    elif sufficiency == "missing" and bridge_id not in BOOTSTRAP_BRIDGE_IDS:
        errors.append("Approved proposal is missing ## Requirement Sufficiency")

    if errors:
        raise AuthorizationError("; ".join(errors))

    created_at = now_utc()
    packet = {
        "schema_version": 1,
        "bridge_id": bridge_id,
        "proposal_file": proposal_rel,
        "go_file": go_rel,
        "latest_status": entry.latest_status,
        "target_path_globs": target_paths,
        "spec_links": spec_links,
        "requirement_sufficiency": sufficiency if sufficiency != "missing" else "bootstrap_pre_rule",
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "expires_at": (created_at + timedelta(minutes=expires_minutes)).isoformat().replace("+00:00", "Z"),
    }
    if project_authorization is not None:
        packet["project_authorization"] = project_authorization
    packet["packet_hash"] = packet_hash(packet)
    return packet


def write_packet(project_root: Path, packet: dict[str, Any]) -> Path:
    path = packet_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_named_packet(project_root: Path, packet: dict[str, Any], bridge_id: str) -> Path:
    """Persist `packet` to the by-bridge named cache for `bridge_id`.

    Companion to `write_packet()` (which writes the active pointer at
    `current.json`). The named cache at
    `.gtkb-state/implementation-authorizations/by-bridge/<bridge_id>.json`
    survives subsequent `begin --bridge-id Y` operations so an earlier
    bridge's packet can be recovered via `activate --bridge-id X`.
    """
    path = packet_path_for_bridge(project_root, bridge_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _validate_packet(project_root: Path, packet: dict[str, Any]) -> None:
    """Validate packet hash, expiry, bridge latest-status, GO-file drift, and
    optional project-authorization drift. Raises AuthorizationError on any
    failure. Shared by `load_packet()` (active pointer) and `load_named_packet()`
    (by-bridge named cache).
    """
    if packet_hash(packet) != packet.get("packet_hash"):
        raise AuthorizationError("Implementation authorization packet hash mismatch")
    if parse_iso(str(packet["expires_at"])) < now_utc():
        raise AuthorizationError("Implementation authorization packet has expired")

    entry = bridge_entry(project_root, str(packet["bridge_id"]))
    go_file = packet.get("go_file")

    found_go = False
    statuses_after_go: list[str] = []

    for status, path in entry.versions:
        if path == go_file:
            if status == "GO":
                found_go = True
                break
            raise AuthorizationError(
                f"Bridge GO file status changed: {go_file} is now {status}"
            )
        statuses_after_go.append(status)

    if not found_go:
        raise AuthorizationError(f"Bridge GO file not found in chain: {go_file}")

    if any(status == "REVISED" for status in statuses_after_go):
        raise AuthorizationError(
            f"Bridge GO at {go_file} superseded by REVISED proposal in chain; "
            f"re-issue the implementation-authorization packet from the new GO."
        )
    if any(status == "GO" for status in statuses_after_go):
        raise AuthorizationError(
            f"Newer GO exists in bridge chain after {go_file}; "
            f"re-issue the implementation-authorization packet from the new GO."
        )
    if statuses_after_go:
        latest_status = statuses_after_go[0]
        if latest_status == "NEW":
            raise AuthorizationError(
                f"Post-implementation report at {entry.latest_path} is awaiting "
                f"Loyal Opposition review; additional mutations during review "
                f"would invalidate the report snapshot. Wait for VERIFIED or "
                f"NO-GO before resuming work."
            )
        if latest_status == "VERIFIED":
            raise AuthorizationError(
                f"Bridge thread is VERIFIED (terminal at {entry.latest_path}); "
                f"the implementation phase for this proposal is closed. File a "
                f"new bridge proposal for further work on this surface."
            )
    project_authorization = packet.get("project_authorization")
    if isinstance(project_authorization, dict):
        authorization_id = str(project_authorization.get("id") or "")
        if not authorization_id:
            raise AuthorizationError("Implementation authorization packet has invalid project_authorization metadata")
        row = _project_authorization_row(project_root, authorization_id)
        current = validate_project_authorization_row(
            project_root,
            row,
            proposal_project_id=project_authorization.get("proposal_project_id"),
            work_item_id=project_authorization.get("work_item_id"),
            spec_links=packet_spec_links(packet),
        )
        if current["project_id"] != project_authorization.get("project_id"):
            raise AuthorizationError("Project authorization project_id drifted since packet creation")


def load_packet(project_root: Path) -> dict[str, Any]:
    path = packet_path(project_root)
    if not path.is_file():
        raise AuthorizationError(
            "Implementation authorization packet is missing; run implementation_authorization.py begin"
        )
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuthorizationError("Implementation authorization packet is corrupt JSON") from exc
    _validate_packet(project_root, packet)
    return packet


def load_named_packet(project_root: Path, bridge_id: str) -> dict[str, Any]:
    """Load and validate the named-cache packet for `bridge_id` from
    `.gtkb-state/implementation-authorizations/by-bridge/<bridge_id>.json`.
    Validates the same invariants as `load_packet()` (hash, expiry, drift).
    """
    path = packet_path_for_bridge(project_root, bridge_id)
    if not path.is_file():
        raise AuthorizationError(
            f"Named packet for bridge {bridge_id!r} not found; "
            f"run implementation_authorization.py begin --bridge-id {bridge_id}"
        )
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuthorizationError(
            f"Named packet for bridge {bridge_id!r} is corrupt JSON"
        ) from exc
    _validate_packet(project_root, packet)
    return packet


def activate_packet(project_root: Path, bridge_id: str) -> dict[str, Any]:
    """Restore the named-cache packet for `bridge_id` to `current.json`.

    Reads and validates `by-bridge/<bridge_id>.json` (hash, expiry, bridge
    latest-status, GO-file drift, optional project-authorization drift), then
    writes it to `current.json`. This is the explicit recovery path when
    `current.json` has been overwritten by a concurrent `begin --bridge-id Y`.
    """
    packet = load_named_packet(project_root, bridge_id)
    write_packet(project_root, packet)
    return packet


def list_named_packets(project_root: Path) -> list[dict[str, Any]]:
    """Enumerate all named-cache packets under
    `.gtkb-state/implementation-authorizations/by-bridge/`. Each row reports
    `(bridge_id, expires_at, target_path_globs, valid, error)`. A row is
    `valid=True` iff the packet would pass `_validate_packet()` against live
    INDEX state right now.
    """
    by_bridge_dir = project_root / BY_BRIDGE_DIRECTORY_RELATIVE_PATH
    if not by_bridge_dir.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(by_bridge_dir.glob("*.json")):
        rel = path.relative_to(project_root).as_posix()
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            rows.append({
                "path": rel,
                "bridge_id": None,
                "expires_at": None,
                "target_path_globs": [],
                "valid": False,
                "error": f"corrupt or unreadable: {exc}",
            })
            continue
        bridge_id = packet.get("bridge_id")
        try:
            _validate_packet(project_root, packet)
            valid = True
            error: str | None = None
        except AuthorizationError as exc:
            valid = False
            error = str(exc)
        rows.append({
            "path": rel,
            "bridge_id": bridge_id,
            "expires_at": packet.get("expires_at"),
            "target_path_globs": packet.get("target_path_globs", []),
            "valid": valid,
            "error": error,
        })
    return rows


def path_authorized(packet: dict[str, Any], relative_path: str) -> bool:
    rel = relative_path.replace("\\", "/").lstrip("./")
    for pattern in packet.get("target_path_globs", []):
        normalized = str(pattern).replace("\\", "/").lstrip("./")
        if fnmatch.fnmatch(rel, normalized):
            return True
        if normalized.endswith("/**") and rel.startswith(normalized[:-3].rstrip("/") + "/"):
            return True
    return False


def validate_targets(project_root: Path, targets: list[str]) -> dict[str, Any]:
    packet = load_packet(project_root)
    normalized_targets = [normalize_relative_path(project_root, target) for target in targets]
    unauthorized = [target for target in normalized_targets if not path_authorized(packet, target)]
    if unauthorized:
        raise AuthorizationError("Target path outside implementation authorization scope: " + ", ".join(unauthorized))
    return {"packet": packet, "targets": normalized_targets}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    begin = subparsers.add_parser("begin")
    begin.add_argument("--bridge-id", required=True)
    begin.add_argument("--expires-minutes", type=int, default=DEFAULT_EXPIRY_MINUTES)
    begin.add_argument("--no-write", action="store_true", help="Print packet without writing current.json or the named-cache packet")

    validate = subparsers.add_parser("validate")
    validate.add_argument("--target", action="append", required=True)

    activate = subparsers.add_parser(
        "activate",
        help="Restore a previously-issued named-cache packet to current.json",
    )
    activate.add_argument("--bridge-id", required=True)

    subparsers.add_parser(
        "list",
        help="Enumerate named-cache packets under .gtkb-state/implementation-authorizations/by-bridge/",
    )

    args = parser.parse_args(argv)
    root = project_root_from_arg(args.project_root)
    try:
        if args.command == "begin":
            packet = create_authorization_packet(root, args.bridge_id, expires_minutes=args.expires_minutes)
            if not args.no_write:
                write_packet(root, packet)
                write_named_packet(root, packet, args.bridge_id)
            print(json.dumps(packet, indent=2, sort_keys=True))
            return 0
        if args.command == "validate":
            result = validate_targets(root, args.target)
            print(json.dumps({"authorized": True, "targets": result["targets"]}, indent=2, sort_keys=True))
            return 0
        if args.command == "activate":
            packet = activate_packet(root, args.bridge_id)
            print(json.dumps(packet, indent=2, sort_keys=True))
            return 0
        if args.command == "list":
            rows = list_named_packets(root)
            print(json.dumps(rows, indent=2, sort_keys=True))
            return 0
    except AuthorizationError as exc:
        print(json.dumps({"authorized": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
