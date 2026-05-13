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
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_PACKET_RELATIVE_PATH = Path(".gtkb-state/implementation-authorizations/current.json")
DEFAULT_EXPIRY_MINUTES = 480
BOOTSTRAP_BRIDGE_IDS = frozenset({"gtkb-implementation-start-authorization-gate"})
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|pending|no relevant|not applicable|n/a)\b", re.IGNORECASE)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TARGET_PATHS_RE = re.compile(
    r"(?:\*\*)?target_paths(?:\*\*)?\s*:(?:\*\*)?\s*(\[[^\n]+\])",
    re.IGNORECASE,
)


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


def project_root_from_arg(value: str | None = None) -> Path:
    if value:
        return Path(value).resolve()
    return Path(__file__).resolve().parent.parent


def packet_path(project_root: Path) -> Path:
    return project_root / DEFAULT_PACKET_RELATIVE_PATH


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
            current_versions.append((match.group(1), match.group(2)))
    if current_id is not None and current_versions:
        entries[current_id] = BridgeEntry(current_id, current_versions)
    return entries


def bridge_entry(project_root: Path, bridge_id: str) -> BridgeEntry:
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
    spec_links = extract_spec_links(proposal)
    target_paths = extract_target_paths(proposal)
    if not has_spec_derived_verification(proposal):
        raise AuthorizationError("Approved proposal is missing a spec-derived verification plan")

    sufficiency = requirement_sufficiency_state(proposal)
    if sufficiency == "gap":
        raise AuthorizationError(
            "Approved proposal says new or revised requirements are required before implementation"
        )
    if sufficiency == "missing" and bridge_id not in BOOTSTRAP_BRIDGE_IDS:
        raise AuthorizationError("Approved proposal is missing ## Requirement Sufficiency")

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
    packet["packet_hash"] = packet_hash(packet)
    return packet


def write_packet(project_root: Path, packet: dict[str, Any]) -> Path:
    path = packet_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


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
    if packet_hash(packet) != packet.get("packet_hash"):
        raise AuthorizationError("Implementation authorization packet hash mismatch")
    if parse_iso(str(packet["expires_at"])) < now_utc():
        raise AuthorizationError("Implementation authorization packet has expired")
    entry = bridge_entry(project_root, str(packet["bridge_id"]))
    if entry.latest_status != "GO":
        raise AuthorizationError(f"Bridge latest status drifted to {entry.latest_status}; latest GO required")
    if entry.latest_path != packet.get("go_file"):
        raise AuthorizationError("Bridge GO file drifted since authorization packet creation")
    return packet


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
    begin.add_argument("--no-write", action="store_true", help="Print packet without writing current.json")

    validate = subparsers.add_parser("validate")
    validate.add_argument("--target", action="append", required=True)

    args = parser.parse_args(argv)
    root = project_root_from_arg(args.project_root)
    try:
        if args.command == "begin":
            packet = create_authorization_packet(root, args.bridge_id, expires_minutes=args.expires_minutes)
            if not args.no_write:
                write_packet(root, packet)
            print(json.dumps(packet, indent=2, sort_keys=True))
            return 0
        if args.command == "validate":
            result = validate_targets(root, args.target)
            print(json.dumps({"authorized": True, "targets": result["targets"]}, indent=2, sort_keys=True))
            return 0
    except AuthorizationError as exc:
        print(json.dumps({"authorized": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
