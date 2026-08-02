#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Generate a mechanical applicability packet for a bridge document.

The preflight is intentionally conservative: it computes required
cross-cutting specs from explicit TOML triggers, compares them with the
operative bridge file's ``Specification Links`` section, and emits a stable
packet hash that Loyal Opposition verdicts can cite.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sqlite3
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

try:
    from scripts.implementation_authorization import (
        PATH_TOKEN_RE,
        AuthorizationError,
        extract_and_validate_project_authorization,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from implementation_authorization import (  # type: ignore[no-redef]
        PATH_TOKEN_RE,
        AuthorizationError,
        extract_and_validate_project_authorization,
    )

try:
    from scripts.bridge_author_metadata import REQUIRED_AUTHOR_METADATA_FIELDS
except ImportError:  # pragma: no cover - direct script execution path
    from bridge_author_metadata import REQUIRED_AUTHOR_METADATA_FIELDS

try:
    from groundtruth_kb.governance.project_authorization_operation_time import (
        classify_target as _classify_target,
    )
    from groundtruth_kb.governance.project_authorization_operation_time import (
        evaluate_envelope as _evaluate_envelope,
    )
    from groundtruth_kb.governance.project_authorization_operation_time import (
        load_operation_taxonomy as _load_operation_taxonomy,
    )
except ImportError:  # pragma: no cover
    _classify_target = None  # type: ignore[assignment]
    _evaluate_envelope = None  # type: ignore[assignment]
    _load_operation_taxonomy = None  # type: ignore[assignment]

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_BRIDGE_DIR: Final[Path] = PROJECT_ROOT / "bridge"
DEFAULT_CONFIG_PATH: Final[Path] = PROJECT_ROOT / "config" / "governance" / "spec-applicability.toml"
DEFAULT_DB_PATH: Final[Path] = PROJECT_ROOT / "groundtruth.db"
PACKET_HASH_SCHEMA_VERSION: Final[int] = 3
PACKET_HASH_MATERIAL_KEYS: Final[frozenset[str]] = frozenset(
    {
        "packet_hash_schema_version",
        "bridge_document_name",
        "source_identity",
        "source_content_hash",
        "rules_content_hash",
        "cited_specs",
        "target_paths",
        "declared_target_paths",
        "applicability_path_evidence",
        "work_items",
        "applicable_specs",
        "missing_required_specs",
        "missing_advisory_specs",
        "project_authorization_operation_time",
    }
)

BRIDGE_FILE_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED)\b",
    re.IGNORECASE,
)
SPEC_LINK_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    # Strict harvest heading. Tolerates a trailing qualifier ONLY when it is
    # introduced by a separator -- "(" (parenthetical), ":", en-dash, em-dash,
    # or a whitespace-prefixed hyphen -- e.g. "## Specification Links (carried
    # forward)". Requiring whitespace before an ASCII hyphen prevents compound
    # headings such as "Specification-Derived" from matching (WI-5330).
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?"
    r"specification(?:\s+links?|\s+references?)?"
    r"(?:\s*[(:–—].*|\s+-.*)?\s*$",
    re.IGNORECASE,
)
# Loose detector for spec-links-like headings the STRICT regex rejects (e.g. the
# prefix form "## Carried-Forward Specification Links" or a pluralized
# "## Specifications Links"). Used ONLY by the advisory diagnostic
# classify_spec_links_section(); it never widens spec-id harvesting (WI-4542).
SPEC_LINK_HEADING_LOOSE_RE: Final[re.Pattern[str]] = re.compile(
    r"^#{1,6}\s+.*\bspecification.*\b(?:link|reference)",
    re.IGNORECASE,
)
SPEC_ID_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ|DELIB)-[A-Z0-9][A-Z0-9_-]*\b")
RULE_PATH_RE: Final[re.Pattern[str]] = re.compile(r"\.claude/rules/[a-z0-9_-]+\.md")
WORK_ITEM_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:WI|GTKB)-[A-Z0-9][A-Z0-9_-]*\b")
DOCUMENT_DECLARATION_RE: Final[re.Pattern[str]] = re.compile(r"(?im)^\s*Document:\s*([A-Za-z0-9_.-]+)\s*$")
# PATH_TOKEN_RE is imported from implementation_authorization (HYG-046 single
# source; previously a drifted local copy that lacked 'memory/').
TARGET_PATH_RE: Final[re.Pattern[str]] = re.compile(r"^\s*target_paths?\s*[:=]\s*(.+)", re.IGNORECASE)
FILES_CHANGED_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"^#{1,6}\s+Files\s+(?:Changed|Expected\s+To\s+Change)\s*$",
    re.IGNORECASE,
)
OPERATIVE_REFERENCE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?im)^\s*(?:Responds\s+to|Corrects|Approved\s+proposal|Reviewed|Verified):\s*"
    r"(?:bridge/)?([^\s`]+)-(\d+)\.md\s*$"
)
PAUTH_AMENDMENT_SPEC_ID: Final[str] = "DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001"
OWNER_EVIDENCE_RE: Final[re.Pattern[str]] = re.compile(r"Owner evidence:\s*([^\s`)]+)", re.IGNORECASE)
JSON_FENCE_RE: Final[re.Pattern[str]] = re.compile(r"```json\s*(.*?)```", re.IGNORECASE | re.DOTALL)
BRIDGE_KIND_RE: Final[re.Pattern[str]] = re.compile(r"(?im)^\s*bridge_kind:\s*([a-z0-9_-]+)\s*$")
VERSION_DECLARATION_RE: Final[re.Pattern[str]] = re.compile(r"(?im)^\s*Version:\s*(\d+)\s*$")
PAUTH_METADATA_RE: Final[re.Pattern[str]] = re.compile(r"(?im)^\s*Project Authorization(?: ID)?:\s*\S+")
APPROVED_PROPOSAL_RE: Final[re.Pattern[str]] = re.compile(
    r"(?im)^\s*Approved proposal:\s*`?(?:bridge/)?([A-Za-z0-9_.-]+)-(\d{3})\.md`?\s*$"
)
PROPOSAL_BRIDGE_KINDS: Final[frozenset[str]] = frozenset({"prime_proposal", "implementation_proposal"})
FINALIZATION_BRIDGE_KINDS: Final[frozenset[str]] = frozenset(
    {"implementation_report", "implementation_report_revision"}
)
PAUTH_PHASE_OPERATIONS: Final[dict[str, tuple[str, ...]]] = {
    "proposal": ("implementation_packet_create", "implementation_start"),
    "finalization": ("git_commit", "protected_mutation"),
}
VERDICT_CANDIDATE_STATUSES: Final[frozenset[str]] = frozenset({"GO", "NO-GO", "VERIFIED"})
RESPONDS_TO_BRIDGE_PATH_RE: Final[re.Pattern[str]] = re.compile(
    r"(?im)^\s*Responds\s+to\s*:\s*`?(?P<path>[^`\r\n]+?\.md)`?\s*$"
)
APPLICABILITY_PREFLIGHT_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"(?im)^(?P<marks>#{1,6})\s*applicability\s+preflight\s*$"
)
CANDIDATE_EVIDENCE_HASH_SENTINEL: Final[str] = "<CANDIDATE_EVIDENCE_HASH>"
CANDIDATE_EVIDENCE_HASH_LINE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?im)^(?P<prefix>\s*[-*]?\s*candidate_evidence_hash\s*:\s*`?)"
    r"(?P<value>sha256:[0-9a-f]{64}|<CANDIDATE_EVIDENCE_HASH>)"
    r"(?P<suffix>`?\s*)$"
)


class VerdictCandidatePreparationError(ValueError):
    """Raised when exact verdict-candidate evidence cannot be rebuilt safely."""


@dataclass(frozen=True)
class BridgeVersion:
    status: str
    rel_path: str
    abs_path: Path
    version_number: int


@dataclass(frozen=True)
class ApplicabilityRule:
    spec_id: str
    severity: str = "blocking"
    rationale: str = ""
    applies_when_paths_match: tuple[str, ...] = ()
    applies_when_doc_matches: tuple[str, ...] = ()
    applies_when_content_matches: tuple[str, ...] = ()


@dataclass
class ApplicableSpec:
    spec_id: str
    severity: str
    rationale: str
    matched_by: list[str] = field(default_factory=list)
    title: str | None = None
    status: str | None = None
    type: str | None = None
    exists_in_membase: bool | None = None


_FENCE_OPEN_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")


def _is_fence_opener(run: str, rest: str) -> bool:
    """Return True when a fence-marker line is a genuine opener.

    An opener is a run of >=3 of the same fence char (backtick or tilde) optionally
    followed by a single-token info string. For backtick fences the info string must
    contain no backtick (the CommonMark rule). The single-token requirement keeps a
    wrapped prose line that merely begins with a fence marker followed by several words
    from being misread as a fence opener (WI-4838 prose-wrap desync).
    """
    info = rest.strip()
    if run[0] == "`" and "`" in info:
        return False
    return len(info.split()) <= 1


def _is_fence_closer(line: str, fence_char: str, fence_len: int) -> bool:
    """Return True when ``line`` closes a fence opened by ``fence_len`` of ``fence_char``.

    A closer is a run of at least the opener length of the SAME fence char followed by
    only whitespace (CommonMark). This keeps a marker-plus-language line inside a fence
    from closing it early (WI-4838 inner-marker desync).
    """
    return re.match(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$", line) is not None


def _strip_code_fences(lines: list[str]) -> list[str]:
    """Blank fenced code blocks (and their delimiters) so residual prose can be scanned.

    Uses a matched open/close parser: a fence opens only on a valid opener
    (:func:`_is_fence_opener`) and closes only on a bare, same-char, length-matched
    closer (:func:`_is_fence_closer`). This replaces the prior single-toggle form that
    flipped ``in_fence`` on any marker-prefixed line and desynced on prose-wrap and
    inner-marker inputs (WI-4838).
    """
    in_fence = False
    fence_char = ""
    fence_len = 0
    out: list[str] = []
    for line in lines:
        if not in_fence:
            match = _FENCE_OPEN_RE.match(line)
            if match and _is_fence_opener(match.group(1), match.group(2)):
                in_fence = True
                fence_char = match.group(1)[0]
                fence_len = len(match.group(1))
                out.append("")
                continue
            out.append(line)
        else:
            if _is_fence_closer(line, fence_char, fence_len):
                in_fence = False
                fence_char = ""
                fence_len = 0
                out.append("")
                continue
            out.append("")
    return out


def parse_index_for_document(bridge_dir: Path, bridge_id: str) -> list[BridgeVersion]:
    return parse_versioned_files_for_document(bridge_dir, bridge_id)


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return _status_from_content(text)


def _status_from_content(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = BRIDGE_FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def parse_versioned_files_for_document(bridge_dir: Path, bridge_id: str) -> list[BridgeVersion]:
    """Return versioned bridge files for ``bridge_id`` when INDEX is absent."""
    versions: list[BridgeVersion] = []
    for path in bridge_dir.glob(f"{bridge_id}-*.md"):
        match = re.match(rf"^{re.escape(bridge_id)}-(\d+)\.md$", path.name)
        if not match:
            continue
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        versions.append(
            BridgeVersion(
                status=status,
                rel_path=f"bridge/{path.name}",
                abs_path=path,
                version_number=int(match.group(1)),
            )
        )
    return sorted(versions, key=lambda version: version.version_number, reverse=True)


def choose_operative_version(versions: list[BridgeVersion]) -> BridgeVersion | None:
    if versions:
        latest = max(versions, key=lambda v: v.version_number)
        if latest.status == "WITHDRAWN":
            return latest
        earlier_no_actions = [
            version
            for version in versions
            if version.status == "NO-ACTION" and version.version_number < latest.version_number
        ]
        if latest.status in {"GO", "NO-GO", "VERIFIED"} and earlier_no_actions:
            references = _operative_reference_versions(latest)
            if references:
                return latest
    for status_set in ({"NEW", "REVISED", "NO-ACTION"}, {"VERIFIED", "WITHDRAWN", "GO", "NO-GO"}):
        candidates = [v for v in versions if v.status in status_set]
        if candidates:
            return max(candidates, key=lambda v: v.version_number)
    return versions[0] if versions else None


def _operative_reference_versions(version: BridgeVersion) -> set[int]:
    """Return explicit same-thread version references from verdict metadata."""
    try:
        content = version.abs_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    thread_name = re.sub(r"-\d+\.md$", "", Path(version.rel_path).name)
    return {int(match.group(2)) for match in OPERATIVE_REFERENCE_RE.finditer(content) if match.group(1) == thread_name}


def extract_spec_links(content: str) -> set[str]:
    lines = _strip_code_fences(content.splitlines())
    start: int | None = None
    for idx, line in enumerate(lines):
        if SPEC_LINK_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return set()
    section: list[str] = []
    for line in lines[start:]:
        if line.strip().startswith("#"):
            break
        section.append(line)
    text = "\n".join(section)
    return set(SPEC_ID_RE.findall(text)) | set(RULE_PATH_RE.findall(text))


def classify_spec_links_section(content: str) -> dict[str, str | None]:
    """Diagnose the Specification-Links section WITHOUT changing harvesting.

    Distinguishes a strictly-recognized section (``harvested`` /
    ``section_empty``) from a present-but-unrecognized spec-links-like heading
    (``heading_unrecognized``, with the offending heading text in
    ``candidate_heading``) and from the genuine absence of any such heading
    (``no_section``). Advisory only: this MUST NOT be used to widen spec-id
    harvesting or to change ``preflight_passed`` (WI-4542).
    """
    lines = _strip_code_fences(content.splitlines())
    for idx, line in enumerate(lines):
        if SPEC_LINK_HEADING_RE.match(line.strip()):
            section: list[str] = []
            for tail in lines[idx + 1 :]:
                if tail.strip().startswith("#"):
                    break
                section.append(tail)
            text = "\n".join(section)
            harvested = set(SPEC_ID_RE.findall(text)) | set(RULE_PATH_RE.findall(text))
            return {
                "status": "harvested" if harvested else "section_empty",
                "candidate_heading": None,
            }
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") and SPEC_LINK_HEADING_LOOSE_RE.match(stripped):
            return {"status": "heading_unrecognized", "candidate_heading": stripped}
    return {"status": "no_section", "candidate_heading": None}


def extract_target_paths(content: str) -> set[str]:
    paths: set[str] = set()
    for line in content.splitlines():
        target_match = TARGET_PATH_RE.match(line)
        if target_match:
            paths.update(_parse_declared_path_values(target_match.group(1)))
    for match in PATH_TOKEN_RE.finditer(content):
        token = match.group(1).replace("\\", "/").strip("/")
        if token and not token.startswith(("http:/", "https:/")):
            paths.add(token)
    return paths


def extract_declared_target_paths(content: str) -> set[str]:
    paths: set[str] = set()
    for line in content.splitlines():
        target_match = TARGET_PATH_RE.match(line)
        if target_match:
            paths.update(_parse_declared_path_values(target_match.group(1)))
    return paths


def _normalize_path_token(value: str) -> str:
    token = value.replace("\\", "/").strip().strip("`'\"")
    token = token.rstrip(".,;:)")
    if "::" in token:
        token = token.split("::", 1)[0]
    return token.strip("/")


def _parse_declared_path_values(raw: str) -> set[str]:
    raw = raw.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = [p.strip("\"' ") for p in re.split(r"[,\s]+", raw) if p.strip("\"' ")]
    if isinstance(parsed, list):
        return {_normalize_path_token(str(p)) for p in parsed if _normalize_path_token(str(p))}
    parsed_token = _normalize_path_token(str(parsed))
    return {parsed_token} if parsed_token else set()


def _files_changed_section_lines(content: str) -> list[str]:
    lines = content.splitlines()
    collected: list[str] = []
    in_section = False
    for line in lines:
        if FILES_CHANGED_HEADING_RE.match(line.strip()):
            in_section = True
            continue
        if in_section and line.strip().startswith("#"):
            break
        if in_section:
            stripped = line.strip()
            if stripped.startswith(("-", "*", "|")):
                collected.append(line)
    return collected


def collect_cited_implementation_paths(content: str) -> set[str]:
    """Collect paths for missing-parent warnings from deliberate path fields.

    This deliberately does not reuse the broad document-wide PATH_TOKEN_RE scan
    from extract_target_paths(); incidental prose path mentions should not
    create warning noise.
    """
    paths: set[str] = set()
    for line in content.splitlines():
        target_match = TARGET_PATH_RE.match(line)
        if target_match:
            paths.update(_parse_declared_path_values(target_match.group(1)))
    for line in _files_changed_section_lines(content):
        for match in PATH_TOKEN_RE.finditer(line):
            token = _normalize_path_token(match.group(1))
            if token and not token.startswith(("http:/", "https:/")):
                paths.add(token)
    return paths


def compute_missing_parent_dir_warnings(project_root: Path, paths: set[str]) -> list[str]:
    warnings: list[str] = []
    root = project_root.resolve()
    for rel_path in sorted(paths):
        candidate = Path(rel_path)
        target = candidate if candidate.is_absolute() else root / candidate
        try:
            resolved = target.resolve(strict=False)
            resolved.relative_to(root)
        except ValueError:
            continue
        if resolved.exists():
            continue
        if not resolved.parent.exists():
            warnings.append(rel_path)
    return warnings


def _parse_rules(content: str) -> list[ApplicabilityRule]:
    data = tomllib.loads(content)
    rules: list[ApplicabilityRule] = []
    for raw in data.get("rules", []):
        rules.append(
            ApplicabilityRule(
                spec_id=str(raw["spec_id"]),
                severity=str(raw.get("severity", "blocking")),
                rationale=str(raw.get("rationale", "")),
                applies_when_paths_match=tuple(str(v) for v in raw.get("applies_when_paths_match", [])),
                applies_when_doc_matches=tuple(str(v) for v in raw.get("applies_when_doc_matches", [])),
                applies_when_content_matches=tuple(str(v) for v in raw.get("applies_when_content_matches", [])),
            )
        )
    return rules


def load_rules(config_path: Path) -> list[ApplicabilityRule]:
    return _parse_rules(config_path.read_text(encoding="utf-8"))


def _match_path(pattern: str, path: str) -> bool:
    normalized_pattern = pattern.replace("\\", "/").strip("/")
    normalized_path = path.replace("\\", "/").strip("/")
    return fnmatch.fnmatchcase(normalized_path, normalized_pattern)


def compute_applicable_specs(
    *,
    bridge_id: str,
    content: str,
    target_paths: set[str],
    rules: list[ApplicabilityRule],
) -> dict[str, ApplicableSpec]:
    lowered_content = content.lower()
    applicable: dict[str, ApplicableSpec] = {}
    for rule in rules:
        matches: list[str] = []
        for pattern in rule.applies_when_doc_matches:
            if fnmatch.fnmatchcase(bridge_id, pattern):
                matches.append(f"doc:{pattern}")
        for pattern in rule.applies_when_paths_match:
            if any(_match_path(pattern, p) for p in target_paths):
                matches.append(f"path:{pattern}")
        for needle in rule.applies_when_content_matches:
            if needle.lower() in lowered_content:
                matches.append(f"content:{needle}")
        if matches:
            applicable[rule.spec_id] = ApplicableSpec(
                spec_id=rule.spec_id,
                severity=rule.severity,
                rationale=rule.rationale,
                matched_by=matches,
            )
    return applicable


def enrich_from_membase(applicable: dict[str, ApplicableSpec], db_path: Path) -> None:
    if not db_path.is_file() or not applicable:
        return
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=2.0)
    except sqlite3.Error:
        return
    try:
        for spec_id, entry in applicable.items():
            if spec_id.startswith("DELIB-") or "/" in spec_id:
                continue
            row = conn.execute(
                "SELECT title, status, type FROM current_specifications WHERE id = ? LIMIT 1",
                (spec_id,),
            ).fetchone()
            entry.exists_in_membase = row is not None
            if row:
                entry.title, entry.status, entry.type = row[0], row[1], row[2]
    finally:
        conn.close()


def _load_json_fence(content: str) -> dict[str, Any] | None:
    for match in JSON_FENCE_RE.finditer(content):
        try:
            parsed = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _current_pauth_specs(db_path: Path, authorization_id: str) -> set[str]:
    if not db_path.is_file():
        return set()
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=2.0)
    except sqlite3.Error:
        return set()
    try:
        row = conn.execute(
            "SELECT included_spec_ids FROM current_project_authorizations WHERE id = ? LIMIT 1",
            (authorization_id,),
        ).fetchone()
    except sqlite3.Error:
        return set()
    finally:
        conn.close()
    if not row or not row[0]:
        return set()
    try:
        parsed = json.loads(row[0])
    except json.JSONDecodeError:
        return set()
    if not isinstance(parsed, list):
        return set()
    return {str(item) for item in parsed}


def _pauth_amendment_blocking_errors(content: str, project_root: Path, db_path: Path) -> list[str]:
    if PAUTH_AMENDMENT_SPEC_ID not in content:
        return []
    envelope = _load_json_fence(content)
    if envelope is None:
        return ["PAUTH amendment approval check failed: no structured amendment envelope found."]
    project_id = str(envelope.get("project_id") or "")
    authorization_id = str(envelope.get("id") or "")
    included_specs = {str(item) for item in envelope.get("included_spec_ids", []) if str(item)}
    previous_specs = _current_pauth_specs(db_path, authorization_id)
    added_specs = included_specs - previous_specs or included_specs

    evidence_match = OWNER_EVIDENCE_RE.search(content)
    if evidence_match is None:
        return ["PAUTH amendment approval check failed: No packet path detected in owner evidence."]
    raw_path = evidence_match.group(1).strip().rstrip("\"',;}")
    approval_root = (project_root / ".groundtruth" / "formal-artifact-approvals").resolve(strict=False)
    candidate = (project_root / raw_path).resolve(strict=False)
    try:
        candidate.relative_to(approval_root)
    except ValueError:
        return [
            "PAUTH amendment approval check failed: approval packet path is outside the in-root approval directory."
        ]
    try:
        approval_packet = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["PAUTH amendment approval check failed: approval packet is not readable JSON."]
    if not isinstance(approval_packet, dict) or not all(
        approval_packet.get(field)
        for field in (
            "artifact_type",
            "artifact_id",
            "action",
            "approval_mode",
            "approved_by",
            "full_content",
            "explicit_change_request",
        )
    ):
        return ["PAUTH amendment approval check failed: approval packet fails schema validation."]
    if approval_packet.get("approval_mode") != "approve" or approval_packet.get("approved_by") != "owner":
        return ["PAUTH amendment approval check failed: approval packet is not owner-approved."]

    approval_text = " ".join(
        str(approval_packet.get(field, ""))
        for field in ("artifact_id", "full_content", "explicit_change_request", "change_reason", "source_ref")
    )
    if project_id not in approval_text or authorization_id not in approval_text:
        return ["PAUTH amendment approval check failed: approval packet does not mention project authorization."]
    if added_specs and not any(spec_id in approval_text for spec_id in added_specs):
        return ["PAUTH amendment approval check failed: approval packet does not cover the amendment."]
    return []


def _check_author_metadata_presence(content: str) -> list[str]:
    """Check for missing required author-metadata fields in bridge content."""
    warnings: list[str] = []
    for field_name in REQUIRED_AUTHOR_METADATA_FIELDS:
        pattern = re.compile(r"^" + re.escape(field_name) + r"\s*:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
        if not pattern.search(content):
            warnings.append(field_name)
    return warnings


def _check_unclassified_target_paths(target_paths: set[str]) -> list[str]:
    """Classify declared target paths and return any that are 'unclassified'."""
    if _classify_target is None:
        return []  # fail-soft when classifier unavailable
    unclassified: list[str] = []
    for path in sorted(target_paths):
        try:
            result = _classify_target(path)
            if result.mutation_class == "unclassified":
                unclassified.append(path)
        except Exception:
            pass  # fail-soft on classifier error
    return unclassified


def _normalize_lf(content: str) -> str:
    return content.replace("\r\n", "\n").replace("\r", "\n")


def normalize_verdict_candidate_path(candidate_path: str | Path, project_root: Path) -> tuple[str, Path]:
    """Return one canonical root-relative numbered bridge-candidate path."""

    cleaned = str(candidate_path).strip().strip("`").replace("\\", "/")
    if not cleaned:
        raise VerdictCandidatePreparationError("candidate path is empty")
    root = project_root.resolve()
    raw = Path(cleaned)
    resolved = (raw if raw.is_absolute() else root / raw).resolve(strict=False)
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise VerdictCandidatePreparationError("candidate path escapes the project root") from exc
    if resolved.parent != (root / "bridge").resolve():
        raise VerdictCandidatePreparationError(
            "candidate path must be a direct child of the canonical bridge directory"
        )
    if re.fullmatch(r".+-\d{3}\.md", resolved.name) is None:
        raise VerdictCandidatePreparationError("candidate path must name an exact three-digit numbered bridge file")
    return relative, resolved


def _candidate_bridge_identity(candidate_relative: str) -> tuple[str, int]:
    match = re.fullmatch(r"bridge/(?P<document>.+)-(?P<version>\d{3})\.md", candidate_relative)
    if match is None:  # pragma: no cover - guarded by normalize_verdict_candidate_path
        raise VerdictCandidatePreparationError("candidate path is not a canonical numbered bridge file")
    return match.group("document"), int(match.group("version"))


def resolve_verdict_responds_to_source(
    *,
    candidate_path: str | Path,
    content: str,
    project_root: Path,
) -> tuple[str, Path, str]:
    """Resolve the exact existing same-thread source named by ``Responds to``."""

    candidate_relative, _ = normalize_verdict_candidate_path(candidate_path, project_root)
    candidate_document, candidate_version = _candidate_bridge_identity(candidate_relative)
    matches = list(RESPONDS_TO_BRIDGE_PATH_RE.finditer(content))
    if len(matches) != 1:
        raise VerdictCandidatePreparationError(
            "verdict candidate must contain exactly one canonical `Responds to:` bridge path"
        )
    source_relative, source_path = normalize_verdict_candidate_path(
        matches[0].group("path"),
        project_root,
    )
    source_document, source_version = _candidate_bridge_identity(source_relative)
    if source_document != candidate_document:
        raise VerdictCandidatePreparationError("Responds to source must belong to the candidate bridge thread")
    if source_version >= candidate_version:
        raise VerdictCandidatePreparationError("Responds to source must be an earlier bridge version")
    if not source_path.is_file():
        raise VerdictCandidatePreparationError("Responds to source does not exist as a canonical bridge file")
    return source_relative, source_path, candidate_document


def candidate_evidence_hash(candidate_path: str | Path, content: str, project_root: Path) -> str:
    """Bind normalized candidate bytes to their exact root-relative path."""

    candidate_relative, _ = normalize_verdict_candidate_path(candidate_path, project_root)
    normalized = _normalize_lf(content)
    normalized, replacements = CANDIDATE_EVIDENCE_HASH_LINE_RE.subn(
        lambda match: match.group("prefix") + CANDIDATE_EVIDENCE_HASH_SENTINEL + match.group("suffix"),
        normalized,
    )
    if replacements != 1:
        raise VerdictCandidatePreparationError(
            "candidate content must contain exactly one candidate_evidence_hash field"
        )
    payload = candidate_relative + "\n" + normalized
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _applicability_preflight_span(content: str) -> tuple[int, int]:
    matches = list(APPLICABILITY_PREFLIGHT_HEADING_RE.finditer(content))
    if len(matches) != 1:
        raise VerdictCandidatePreparationError(
            "verdict candidate must contain exactly one Applicability Preflight section"
        )
    match = matches[0]
    heading_level = len(match.group("marks"))
    next_heading = re.compile(rf"(?m)^#{{1,{heading_level}}}\s+").search(content, match.end())
    end = next_heading.start() if next_heading is not None else len(content)
    return match.start(), end


def verdict_candidate_needs_preparation(content: str) -> bool:
    """Return whether the writer should rebuild an existing verdict section."""

    status = next((line.strip().upper() for line in _normalize_lf(content).splitlines() if line.strip()), "")
    return status in VERDICT_CANDIDATE_STATUSES and APPLICABILITY_PREFLIGHT_HEADING_RE.search(content) is not None


def _text_sha256(content: str) -> str:
    normalized = _normalize_lf(content).encode("utf-8")
    return "sha256:" + hashlib.sha256(normalized).hexdigest()


def _canonical_explicit_version(
    *,
    bridge_id: str,
    bridge_dir: Path,
    content_file: Path,
    content: str,
) -> BridgeVersion | None:
    """Resolve an explicit canonical bridge source without scanning siblings."""
    bridge_root = bridge_dir.resolve()
    source_path = content_file.resolve()
    if source_path.parent != bridge_root:
        return None

    versioned = re.fullmatch(r"(?P<document>.+)-(?P<version>\d+)\.md", source_path.name)
    looks_canonical = versioned is not None or source_path.name.startswith(f"{bridge_id}-")
    if versioned is None:
        if looks_canonical:
            raise SystemExit(
                "ERR_EXPLICIT_BRIDGE_SOURCE_MISMATCH: canonical-looking source does not have a numeric version"
            )
        return None
    if versioned.group("document") != bridge_id:
        raise SystemExit(
            "ERR_EXPLICIT_BRIDGE_SOURCE_MISMATCH: explicit versioned source belongs to another bridge thread"
        )

    status = _status_from_content(content)
    if status is None:
        raise SystemExit(
            "ERR_EXPLICIT_BRIDGE_SOURCE_STATUS: canonical explicit source lacks a recognized first-line status"
        )
    try:
        rel_path = source_path.relative_to(bridge_root.parent).as_posix()
    except ValueError as exc:
        raise SystemExit("ERR_EXPLICIT_BRIDGE_SOURCE_ESCAPE: canonical source escapes the project root") from exc
    return BridgeVersion(
        status=status,
        rel_path=rel_path,
        abs_path=source_path,
        version_number=int(versioned.group("version")),
    )


def _source_identity(version: BridgeVersion | None) -> dict[str, Any] | None:
    if version is None:
        return None
    return {
        "path": version.rel_path,
        "status": version.status,
        "version_number": version.version_number,
    }


def _stable_applicable_specs(applicable: dict[str, ApplicableSpec]) -> dict[str, dict[str, Any]]:
    return {
        spec_id: {
            "spec_id": item.spec_id,
            "severity": item.severity,
            "rationale": item.rationale,
            "matched_by": list(item.matched_by),
        }
        for spec_id, item in sorted(applicable.items())
    }


def _packet_hash_material(packet: dict[str, Any], applicable: dict[str, ApplicableSpec]) -> dict[str, Any]:
    pauth = packet.get("project_authorization_operation_time") or {}
    stable_pauth = {
        "applicable": pauth.get("applicable"),
        "phase": pauth.get("phase"),
        "status": pauth.get("status"),
        "allowed": pauth.get("allowed"),
        "reason_code": pauth.get("reason_code"),
        "authorization_id": pauth.get("authorization_id"),
        "authorization_version": pauth.get("authorization_version"),
        "project_id": pauth.get("project_id"),
        "authorization_source": pauth.get("authorization_source"),
        "requested_operations": pauth.get("requested_operations", []),
        "cohort": pauth.get("cohort", []),
        "target_classifications": pauth.get("target_classifications", []),
        "decisions": [
            {
                key: decision.get(key)
                for key in (
                    "allowed",
                    "reason_code",
                    "authorization_id",
                    "authorization_version",
                    "normalized_envelope_hash",
                    "normalized_operation",
                    "classified_targets",
                    "evaluator_id",
                    "evaluator_version",
                    "evaluator_sha256",
                    "taxonomy_version",
                    "taxonomy_sha256",
                )
            }
            for decision in pauth.get("decisions", [])
        ],
    }
    material = {
        "packet_hash_schema_version": PACKET_HASH_SCHEMA_VERSION,
        "bridge_document_name": packet["bridge_document_name"],
        "source_identity": packet["source_identity"],
        "source_content_hash": packet["source_content_hash"],
        "rules_content_hash": packet["rules_content_hash"],
        "cited_specs": packet["cited_specs"],
        "target_paths": packet["target_paths"],
        "declared_target_paths": packet["declared_target_paths"],
        "applicability_path_evidence": packet["applicability_path_evidence"],
        "work_items": packet["work_items"],
        "applicable_specs": _stable_applicable_specs(applicable),
        "missing_required_specs": packet["missing_required_specs"],
        "missing_advisory_specs": packet["missing_advisory_specs"],
        "project_authorization_operation_time": stable_pauth,
    }
    if set(material) != PACKET_HASH_MATERIAL_KEYS:  # pragma: no cover - construction invariant
        raise RuntimeError("packet hash material key set drifted")
    return material


def _bridge_kind(content: str) -> str | None:
    match = BRIDGE_KIND_RE.search(content)
    return match.group(1).lower() if match else None


def _pauth_phase(content: str, versions: list[BridgeVersion]) -> str | None:
    kind = _bridge_kind(content)
    if kind in PROPOSAL_BRIDGE_KINDS:
        return "proposal"
    if kind in FINALIZATION_BRIDGE_KINDS:
        return "finalization"
    if PAUTH_METADATA_RE.search(content) and extract_declared_target_paths(content):
        status = _status_from_content(content)
        if status in {"NEW", "REVISED"} and any(version.status == "GO" for version in versions):
            return "finalization"
        return "proposal"
    return None


def _declared_version(content: str) -> int | None:
    match = VERSION_DECLARATION_RE.search(content)
    return int(match.group(1)) if match else None


def _approved_proposal_for_report(
    *,
    bridge_id: str,
    report_content: str,
    versions: list[BridgeVersion],
) -> tuple[str | None, str | None, str | None]:
    report_version = _declared_version(report_content)

    def approved_by_go(proposal: BridgeVersion) -> bool:
        for verdict in versions:
            if verdict.status != "GO" or verdict.version_number <= proposal.version_number:
                continue
            if report_version is not None and verdict.version_number >= report_version:
                continue
            try:
                verdict_content = verdict.abs_path.read_text(encoding="utf-8")
            except OSError:
                continue
            for reference_slug, reference_version in OPERATIVE_REFERENCE_RE.findall(verdict_content):
                if reference_slug == bridge_id and int(reference_version) == proposal.version_number:
                    return True
        return False

    explicit = APPROVED_PROPOSAL_RE.search(report_content)
    if explicit:
        explicit_slug, explicit_version_text = explicit.groups()
        if explicit_slug != bridge_id:
            return None, None, f"Approved proposal references a different bridge thread: {explicit_slug}"
        explicit_version = int(explicit_version_text)
        match = next((version for version in versions if version.version_number == explicit_version), None)
        if match is None:
            return None, None, f"Approved proposal version is absent: bridge/{bridge_id}-{explicit_version:03d}.md"
        if report_version is not None and explicit_version >= report_version:
            return None, None, "Approved proposal must precede the implementation report"
        try:
            proposal_content = match.abs_path.read_text(encoding="utf-8")
        except OSError as exc:
            return None, None, f"Approved proposal is unreadable: {exc}"
        if _bridge_kind(proposal_content) not in PROPOSAL_BRIDGE_KINDS:
            return (
                None,
                None,
                f"Approved proposal metadata does not identify a proposal-kind artifact: {match.rel_path}",
            )
        if not approved_by_go(match):
            return None, None, f"Approved proposal has no matching earlier GO verdict: {match.rel_path}"
        return proposal_content, match.rel_path, None

    candidates: list[tuple[BridgeVersion, str]] = []
    for version in versions:
        if report_version is not None and version.version_number >= report_version:
            continue
        try:
            candidate_content = version.abs_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _bridge_kind(candidate_content) in PROPOSAL_BRIDGE_KINDS and approved_by_go(version):
            candidates.append((version, candidate_content))
    if not candidates:
        return (
            None,
            None,
            "Implementation report has no readable earlier proposal-kind artifact with a matching GO verdict",
        )
    proposal, proposal_content = max(candidates, key=lambda item: item[0].version_number)
    return proposal_content, proposal.rel_path, None


def _pauth_phase_cohort(
    *,
    phase: str,
    bridge_id: str,
    content: str,
    declared_target_paths: set[str],
    versions: list[BridgeVersion],
    approved_proposal_content: str | None = None,
) -> list[str]:
    cohort = set(declared_target_paths)
    if phase != "finalization":
        return sorted(cohort)

    if approved_proposal_content is not None:
        cohort.update(extract_declared_target_paths(approved_proposal_content))

    declared_version = _declared_version(content)
    observed_versions = [version.version_number for version in versions]
    if declared_version is not None:
        observed_versions.append(declared_version)
    next_version = max(observed_versions, default=0) + 1
    cohort.update(f"bridge/{bridge_id}-{version:03d}.md" for version in range(1, next_version + 1))
    return sorted(cohort)


def _evaluate_pauth_phase(
    *,
    content: str,
    project_root: Path,
    phase: str | None,
    cohort: list[str],
    cited_specs: set[str],
    authorization_source: str | None = None,
    decision_time: datetime | None = None,
) -> tuple[dict[str, Any], list[str]]:
    if phase is None:
        return {
            "applicable": False,
            "phase": None,
            "status": "not_applicable",
            "requested_operations": [],
            "cohort": [],
            "allowed": None,
            "reason_code": "not_applicable",
            "decisions": [],
        }, []

    requested_operations = list(PAUTH_PHASE_OPERATIONS[phase])
    base: dict[str, Any] = {
        "applicable": True,
        "phase": phase,
        "status": "error",
        "requested_operations": requested_operations,
        "cohort": cohort,
        "allowed": False,
        "reason_code": "evaluation_error",
        "authorization_source": authorization_source,
        "decisions": [],
    }
    try:
        envelope = extract_and_validate_project_authorization(
            project_root,
            content,
            sorted(cited_specs),
        )
        if envelope is None:
            raise AuthorizationError(
                "implementation-bearing bridge content does not cite Project Authorization metadata"
            )
        if _evaluate_envelope is None or _load_operation_taxonomy is None:
            raise AuthorizationError("canonical project-authorization operation evaluator is unavailable")
        taxonomy = _load_operation_taxonomy(project_root)
        effective_decision_time = (decision_time or datetime.now(UTC)).replace(microsecond=0)
        decisions = [
            _evaluate_envelope(
                envelope,
                requested_operation=operation,
                target_paths=cohort,
                decision_time=effective_decision_time,
                taxonomy=taxonomy,
            )
            for operation in requested_operations
        ]
        decision_payloads = [decision.as_dict() for decision in decisions]
        allowed = all(decision.allowed for decision in decisions)
        base.update(
            {
                "authorization_id": envelope.get("id"),
                "authorization_version": envelope.get("version"),
                "project_id": envelope.get("project_id"),
                "allowed": allowed,
                "status": "allowed" if allowed else "denied",
                "reason_code": "allowed"
                if allowed
                else next(decision.reason_code for decision in decisions if not decision.allowed),
                "decisions": decision_payloads,
                "target_classifications": (
                    decision_payloads[0].get("classified_targets", []) if decision_payloads else []
                ),
                "evaluator_id": decision_payloads[0].get("evaluator_id") if decision_payloads else None,
                "evaluator_version": decision_payloads[0].get("evaluator_version") if decision_payloads else None,
                "evaluator_sha256": decision_payloads[0].get("evaluator_sha256") if decision_payloads else None,
                "taxonomy_version": decision_payloads[0].get("taxonomy_version") if decision_payloads else None,
                "taxonomy_sha256": decision_payloads[0].get("taxonomy_sha256") if decision_payloads else None,
            }
        )
        errors = [
            "PAUTH operation-time denial "
            f"({decision.normalized_operation or operation}): {decision.reason_code}: {decision.reason}"
            for operation, decision in zip(requested_operations, decisions, strict=True)
            if not decision.allowed
        ]
        return base, errors
    except (AuthorizationError, OSError, RuntimeError, ValueError) as exc:
        base["error"] = str(exc)
        return base, [f"PAUTH operation-time evaluation failed closed: {exc}"]


def build_packet(
    *,
    bridge_id: str,
    bridge_dir: Path = DEFAULT_BRIDGE_DIR,
    config_path: Path = DEFAULT_CONFIG_PATH,
    db_path: Path = DEFAULT_DB_PATH,
    content_file: Path | None = None,
) -> dict[str, Any]:
    versions = parse_index_for_document(bridge_dir, bridge_id)
    scanned_operative = choose_operative_version(versions)
    if scanned_operative is None and content_file is None:
        raise SystemExit(
            f"ERR_NO_BRIDGE_THREAD: no versioned bridge files found for bridge_id={bridge_id!r} under {bridge_dir}"
        )
    if scanned_operative is not None and not scanned_operative.abs_path.is_file():
        raise SystemExit(f"ERR_BRIDGE_FILE_MISSING: {scanned_operative.rel_path}")
    if content_file is not None:
        content = content_file.read_text(encoding="utf-8")
        explicit_version = _canonical_explicit_version(
            bridge_id=bridge_id,
            bridge_dir=bridge_dir,
            content_file=content_file,
            content=content,
        )
        operative = explicit_version or scanned_operative
        content_source = {
            "mode": "pending_content",
            "path": _display_path(content_file, bridge_dir.parent),
        }
    elif scanned_operative is not None:
        operative = scanned_operative
        content = operative.abs_path.read_text(encoding="utf-8")
        content_source = {
            "mode": "bridge_file_operative",
            "path": operative.rel_path,
        }
    else:
        raise SystemExit(
            f"ERR_NO_BRIDGE_THREAD: no versioned bridge files found for bridge_id={bridge_id!r} under {bridge_dir}"
        )
    cited_specs = extract_spec_links(content)
    declared_target_paths = extract_declared_target_paths(content)
    applicability_path_evidence = extract_target_paths(content)
    cited_implementation_paths = collect_cited_implementation_paths(content)
    project_root = bridge_dir.parent
    work_items = sorted(set(WORK_ITEM_RE.findall(content)))
    rules_content = config_path.read_text(encoding="utf-8")
    applicable = compute_applicable_specs(
        bridge_id=bridge_id,
        content=content,
        target_paths=applicability_path_evidence,
        rules=_parse_rules(rules_content),
    )
    enrich_from_membase(applicable, db_path)
    required = {sid for sid, item in applicable.items() if item.severity == "blocking"}
    missing_required = sorted(required - cited_specs)
    advisory_missing = sorted(
        sid for sid, item in applicable.items() if item.severity != "blocking" and sid not in cited_specs
    )
    blocking_errors = _pauth_amendment_blocking_errors(content, project_root, db_path)
    pauth_phase = _pauth_phase(content, versions)
    authorization_content = content
    authorization_source = content_source.get("path")
    authorization_specs = set(cited_specs)
    proposal_error: str | None = None
    approved_content: str | None = None
    if pauth_phase == "finalization":
        approved_content, approved_path, proposal_error = _approved_proposal_for_report(
            bridge_id=bridge_id,
            report_content=content,
            versions=versions,
        )
        if approved_content is not None:
            authorization_content = approved_content
            authorization_source = approved_path
            authorization_specs.update(extract_spec_links(approved_content))
    pauth_cohort = _pauth_phase_cohort(
        phase=pauth_phase or "proposal",
        bridge_id=bridge_id,
        content=content,
        declared_target_paths=declared_target_paths,
        versions=versions,
        approved_proposal_content=approved_content,
    )
    if proposal_error is not None:
        pauth_operation_time = {
            "applicable": True,
            "phase": pauth_phase,
            "status": "error",
            "requested_operations": list(PAUTH_PHASE_OPERATIONS[pauth_phase]),
            "cohort": pauth_cohort,
            "allowed": False,
            "reason_code": "approved_proposal_resolution_failed",
            "authorization_source": None,
            "decisions": [],
            "error": proposal_error,
        }
        pauth_errors = [f"PAUTH operation-time evaluation failed closed: {proposal_error}"]
    else:
        pauth_operation_time, pauth_errors = _evaluate_pauth_phase(
            content=authorization_content,
            project_root=project_root,
            phase=pauth_phase,
            cohort=pauth_cohort,
            cited_specs=authorization_specs,
            authorization_source=authorization_source,
        )
    blocking_errors.extend(pauth_errors)
    packet: dict[str, Any] = {
        "packet_hash_schema_version": PACKET_HASH_SCHEMA_VERSION,
        "bridge_document_name": bridge_id,
        "content_source": content_source,
        "source_identity": _source_identity(operative),
        "source_content_hash": _text_sha256(content),
        "rules_content_hash": _text_sha256(rules_content),
        "operative_version": (
            {
                "status": operative.status,
                "path": operative.rel_path,
                "version_number": operative.version_number,
            }
            if operative is not None
            else None
        ),
        "cited_specs": sorted(cited_specs),
        "target_paths": sorted(declared_target_paths),
        "declared_target_paths": sorted(declared_target_paths),
        "applicability_path_evidence": sorted(applicability_path_evidence),
        "warnings": {
            "missing_parent_dirs": compute_missing_parent_dir_warnings(project_root, cited_implementation_paths),
            "spec_links_section": classify_spec_links_section(content),
            "author_metadata_warnings": _check_author_metadata_presence(content),
            "unclassified_target_paths": _check_unclassified_target_paths(declared_target_paths),
        },
        "work_items": work_items,
        "applicable_specs": {sid: asdict(item) for sid, item in sorted(applicable.items())},
        "missing_required_specs": missing_required,
        "missing_advisory_specs": advisory_missing,
        "project_authorization_operation_time": pauth_operation_time,
        "blocking_errors": blocking_errors,
        "preflight_passed": not missing_required and not blocking_errors,
    }
    packet["packet_hash_material"] = _packet_hash_material(packet, applicable)
    canonical = json.dumps(packet["packet_hash_material"], sort_keys=True, separators=(",", ":"))
    packet["packet_hash"] = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return packet


def _display_path(path: Path, project_root: Path = PROJECT_ROOT) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _derive_bridge_id_from_content_file(content_file: Path) -> str:
    content = content_file.read_text(encoding="utf-8")
    document_match = DOCUMENT_DECLARATION_RE.search(content)
    if document_match:
        return document_match.group(1)
    return re.sub(r"-\d{3}$", "", content_file.stem)


def format_markdown(packet: dict[str, Any]) -> str:
    operative = packet.get("operative_version")
    operative_path = operative["path"] if isinstance(operative, dict) else "(none)"
    content_source = packet.get("content_source") or {}
    spec_links_diag = (packet.get("warnings") or {}).get("spec_links_section") or {}
    lines = [
        "## Applicability Preflight",
        "",
        f"- packet_hash: `{packet['packet_hash']}`",
        f"- bridge_document_name: `{packet['bridge_document_name']}`",
        f"- declared_target_paths: {json.dumps(packet.get('declared_target_paths', []))}",
        f"- applicability_path_evidence: {json.dumps(packet.get('applicability_path_evidence', []))}",
        f"- content_source: `{content_source.get('mode', 'indexed_operative')}`",
        f"- content_file: `{content_source.get('path', operative_path)}`",
        f"- operative_file: `{operative_path}`",
        f"- preflight_passed: `{str(packet['preflight_passed']).lower()}`",
        f"- warnings.missing_parent_dirs: {json.dumps(packet.get('warnings', {}).get('missing_parent_dirs', []))}",
        f"- warnings.spec_links_section: {json.dumps(spec_links_diag)}",
        f"- warnings.author_metadata_warnings: {json.dumps(packet.get('warnings', {}).get('author_metadata_warnings', []))}",
        f"- warnings.unclassified_target_paths: {json.dumps(packet.get('warnings', {}).get('unclassified_target_paths', []))}",
        f"- missing_required_specs: {json.dumps(packet['missing_required_specs'])}",
        f"- missing_advisory_specs: {json.dumps(packet['missing_advisory_specs'])}",
        f"- blocking_errors: {json.dumps(packet.get('blocking_errors', []))}",
    ]
    pauth = packet.get("project_authorization_operation_time") or {}
    if pauth.get("applicable"):
        lines += [
            "",
            "### Project Authorization Operation-Time Evaluation",
            "",
            f"- phase: `{pauth.get('phase')}`",
            f"- status: `{pauth.get('status')}`",
            f"- reason_code: `{pauth.get('reason_code')}`",
            f"- authorization_id: `{pauth.get('authorization_id')}`",
            f"- authorization_version: `{pauth.get('authorization_version')}`",
            f"- project_id: `{pauth.get('project_id')}`",
            f"- authorization_source: `{pauth.get('authorization_source')}`",
            f"- requested_operations: {json.dumps(pauth.get('requested_operations', []))}",
            f"- cohort: {json.dumps(pauth.get('cohort', []))}",
            f"- allowed: `{str(pauth.get('allowed')).lower()}`",
            f"- evaluator: `{pauth.get('evaluator_id')}` v`{pauth.get('evaluator_version')}`",
            f"- evaluator_sha256: `{pauth.get('evaluator_sha256')}`",
            f"- taxonomy: v`{pauth.get('taxonomy_version')}` `{pauth.get('taxonomy_sha256')}`",
        ]
        if pauth.get("error"):
            lines.append(f"- error: `{pauth['error']}`")
        lines += [
            "",
            "| Operation | Allowed | Reason Code | Reason |",
            "| --- | --- | --- | --- |",
        ]
        for decision in pauth.get("decisions", []):
            reason = str(decision.get("reason") or "").replace("|", "\\|")
            lines.append(
                f"| `{decision.get('normalized_operation')}` | "
                f"`{str(decision.get('allowed')).lower()}` | "
                f"`{decision.get('reason_code')}` | {reason} |"
            )
    if packet.get("missing_required_specs") and spec_links_diag.get("status") == "heading_unrecognized":
        lines.append(
            "- NOTE: a Specification-Links-like heading "
            f"({json.dumps(spec_links_diag.get('candidate_heading'))}) was found "
            "but not recognized by SPEC_LINK_HEADING_RE; spec ids under it were "
            "NOT harvested. Use a canonical heading or a tolerated trailing "
            "qualifier, e.g. '## Specification Links (carried forward)'."
        )
    lines += [
        "",
        "| Spec | Severity | Cited | Matched By |",
        "|------|----------|-------|------------|",
    ]
    cited = set(packet["cited_specs"])
    for spec_id, item in packet["applicable_specs"].items():
        matched = ", ".join(item["matched_by"])
        lines.append(f"| `{spec_id}` | `{item['severity']}` | `{'yes' if spec_id in cited else 'no'}` | {matched} |")
    return "\n".join(lines) + "\n"


def prepare_verdict_candidate(
    *,
    candidate_path: str | Path,
    content: str,
    project_root: Path = PROJECT_ROOT,
    config_path: Path | None = None,
    db_path: Path | None = None,
) -> str:
    """Rebuild exact-source applicability evidence for final verdict bytes."""

    normalized = _normalize_lf(content)
    status = next((line.strip().upper() for line in normalized.splitlines() if line.strip()), "")
    if status not in VERDICT_CANDIDATE_STATUSES:
        raise VerdictCandidatePreparationError("candidate preparation is limited to GO, NO-GO, and VERIFIED verdicts")
    candidate_relative, _ = normalize_verdict_candidate_path(candidate_path, project_root)
    source_relative, source_path, bridge_id = resolve_verdict_responds_to_source(
        candidate_path=candidate_relative,
        content=normalized,
        project_root=project_root,
    )
    section_start, section_end = _applicability_preflight_span(normalized)
    packet = build_packet(
        bridge_id=bridge_id,
        bridge_dir=project_root / "bridge",
        config_path=config_path or project_root / "config" / "governance" / "spec-applicability.toml",
        db_path=db_path or project_root / "groundtruth.db",
        content_file=source_path,
    )
    rebuilt_section = format_markdown(packet)
    content_anchor = f"- content_file: `{source_relative}`"
    if content_anchor not in rebuilt_section:
        raise VerdictCandidatePreparationError("rebuilt applicability packet did not bind the exact Responds to source")
    packet_hash_line = f"- packet_hash: `{packet['packet_hash']}`\n"
    if rebuilt_section.count(packet_hash_line) != 1:
        raise VerdictCandidatePreparationError("rebuilt applicability packet has an ambiguous packet_hash field")
    rebuilt_section = rebuilt_section.replace(
        packet_hash_line,
        packet_hash_line + f"- candidate_evidence_hash: `{CANDIDATE_EVIDENCE_HASH_SENTINEL}`\n",
        1,
    )
    prefix = normalized[:section_start]
    suffix = normalized[section_end:]
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    prepared = prefix + rebuilt_section.rstrip("\n") + "\n"
    if suffix:
        prepared += ("\n" if not suffix.startswith("\n") else "") + suffix.lstrip("\n")
    evidence_hash = candidate_evidence_hash(candidate_relative, prepared, project_root)
    prepared, replacements = CANDIDATE_EVIDENCE_HASH_LINE_RE.subn(
        lambda match: match.group("prefix") + evidence_hash + match.group("suffix"),
        prepared,
    )
    if replacements != 1:  # pragma: no cover - construction invariant
        raise VerdictCandidatePreparationError("candidate evidence insertion was not singular")
    return prepared


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-id",
        help="Bridge document name / versioned bridge-thread slug. Optional when --content-file is supplied.",
    )
    parser.add_argument(
        "--content-file", type=Path, default=None, help="Evaluate pending Markdown content from a file."
    )
    parser.add_argument(
        "--prepare-verdict-candidate",
        action="store_true",
        help="Write final prepared verdict bytes to stdout without publishing them.",
    )
    parser.add_argument(
        "--candidate-path",
        type=Path,
        default=None,
        help="Exact intended bridge/<document>-<NNN>.md path for verdict candidate preparation.",
    )
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    if args.prepare_verdict_candidate:
        if args.content_file is None or args.candidate_path is None:
            parser.error("--prepare-verdict-candidate requires --content-file and --candidate-path")
        if args.json:
            parser.error("--prepare-verdict-candidate is incompatible with --json report output")
        try:
            prepared = prepare_verdict_candidate(
                candidate_path=args.candidate_path,
                content=args.content_file.read_text(encoding="utf-8"),
                project_root=args.bridge_dir.parent,
                config_path=args.config,
                db_path=args.db,
            )
        except (OSError, VerdictCandidatePreparationError, SystemExit) as exc:
            sys.stderr.write(f"verdict candidate preparation failed: {exc}\n")
            return 7
        sys.stdout.write(prepared)
        sys.stderr.write(
            "prepared verdict candidate bytes for "
            f"{normalize_verdict_candidate_path(args.candidate_path, args.bridge_dir.parent)[0]}\n"
        )
        return 0
    if args.candidate_path is not None:
        parser.error("--candidate-path is valid only with --prepare-verdict-candidate")
    if args.bridge_id is None:
        if args.content_file is None:
            parser.error("--bridge-id is required unless --content-file is supplied")
        args.bridge_id = _derive_bridge_id_from_content_file(args.content_file)
    packet = build_packet(
        bridge_id=args.bridge_id,
        bridge_dir=args.bridge_dir,
        config_path=args.config,
        db_path=args.db,
        content_file=args.content_file,
    )
    if args.json:
        sys.stdout.write(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(format_markdown(packet))
    missing_parent_dirs = packet.get("warnings", {}).get("missing_parent_dirs", [])
    if missing_parent_dirs:
        sys.stderr.write(
            "warning: bridge preflight missing parent directories: "
            + ", ".join(str(path) for path in missing_parent_dirs)
            + "\n"
        )
    pauth_status = (packet.get("project_authorization_operation_time") or {}).get("status")
    if pauth_status == "error":
        return 6
    return 0 if packet["preflight_passed"] else 5


if __name__ == "__main__":
    raise SystemExit(main())
