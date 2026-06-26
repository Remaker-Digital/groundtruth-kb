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
from pathlib import Path
from typing import Any, Final

try:
    from scripts.implementation_authorization import PATH_TOKEN_RE
except ImportError:  # pragma: no cover - direct script execution path
    from implementation_authorization import PATH_TOKEN_RE

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_BRIDGE_DIR: Final[Path] = PROJECT_ROOT / "bridge"
DEFAULT_CONFIG_PATH: Final[Path] = PROJECT_ROOT / "config" / "governance" / "spec-applicability.toml"
DEFAULT_DB_PATH: Final[Path] = PROJECT_ROOT / "groundtruth.db"

BRIDGE_FILE_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED)\b",
    re.IGNORECASE,
)
SPEC_LINK_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    # Strict harvest heading. Tolerates a trailing qualifier ONLY when it is
    # introduced by a separator -- "(" (parenthetical), ":", en-dash, em-dash,
    # or hyphen -- e.g. "## Specification Links (carried forward)". Bare trailing
    # words (e.g. "## Specification Format Guide") still do NOT match, so the
    # widening cannot over-harvest from unrelated headings (WI-4542).
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?"
    r"specification(?:\s+links?|\s+references?)?"
    r"(?:\s*[(:–—-].*)?\s*$",
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
    for status_set in ({"NEW", "REVISED"}, {"VERIFIED", "WITHDRAWN", "GO", "NO-GO"}):
        candidates = [v for v in versions if v.status in status_set]
        if candidates:
            return max(candidates, key=lambda v: v.version_number)
    return versions[0] if versions else None


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


def load_rules(config_path: Path) -> list[ApplicabilityRule]:
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
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


def build_packet(
    *,
    bridge_id: str,
    bridge_dir: Path = DEFAULT_BRIDGE_DIR,
    config_path: Path = DEFAULT_CONFIG_PATH,
    db_path: Path = DEFAULT_DB_PATH,
    content_file: Path | None = None,
) -> dict[str, Any]:
    versions = parse_index_for_document(bridge_dir, bridge_id)
    operative = choose_operative_version(versions)
    if operative is None and content_file is None:
        raise SystemExit(
            f"ERR_NO_BRIDGE_THREAD: no versioned bridge files found for bridge_id={bridge_id!r} under {bridge_dir}"
        )
    if operative is not None and not operative.abs_path.is_file():
        raise SystemExit(f"ERR_BRIDGE_FILE_MISSING: {operative.rel_path}")
    if content_file is not None:
        content = content_file.read_text(encoding="utf-8")
        content_source = {
            "mode": "pending_content",
            "path": _display_path(content_file),
        }
    elif operative is not None:
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
    target_paths = extract_target_paths(content)
    cited_implementation_paths = collect_cited_implementation_paths(content)
    project_root = bridge_dir.parent
    work_items = sorted(set(WORK_ITEM_RE.findall(content)))
    applicable = compute_applicable_specs(
        bridge_id=bridge_id,
        content=content,
        target_paths=target_paths,
        rules=load_rules(config_path),
    )
    enrich_from_membase(applicable, db_path)
    required = {sid for sid, item in applicable.items() if item.severity == "blocking"}
    missing_required = sorted(required - cited_specs)
    advisory_missing = sorted(
        sid for sid, item in applicable.items() if item.severity != "blocking" and sid not in cited_specs
    )
    packet: dict[str, Any] = {
        "bridge_document_name": bridge_id,
        "content_source": content_source,
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
        "target_paths": sorted(target_paths),
        "warnings": {
            "missing_parent_dirs": compute_missing_parent_dir_warnings(project_root, cited_implementation_paths),
            "spec_links_section": classify_spec_links_section(content),
        },
        "work_items": work_items,
        "applicable_specs": {sid: asdict(item) for sid, item in sorted(applicable.items())},
        "missing_required_specs": missing_required,
        "missing_advisory_specs": advisory_missing,
        "preflight_passed": not missing_required,
    }
    canonical = json.dumps(packet, sort_keys=True, separators=(",", ":"))
    packet["packet_hash"] = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return packet


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
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
        f"- content_source: `{content_source.get('mode', 'indexed_operative')}`",
        f"- content_file: `{content_source.get('path', operative_path)}`",
        f"- operative_file: `{operative_path}`",
        f"- preflight_passed: `{str(packet['preflight_passed']).lower()}`",
        f"- warnings.missing_parent_dirs: {json.dumps(packet.get('warnings', {}).get('missing_parent_dirs', []))}",
        f"- warnings.spec_links_section: {json.dumps(spec_links_diag)}",
        f"- missing_required_specs: {json.dumps(packet['missing_required_specs'])}",
        f"- missing_advisory_specs: {json.dumps(packet['missing_advisory_specs'])}",
    ]
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


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-id",
        help="Bridge document name / versioned bridge-thread slug. Optional when --content-file is supplied.",
    )
    parser.add_argument(
        "--content-file", type=Path, default=None, help="Evaluate pending Markdown content from a file."
    )
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
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
    return 0 if packet["preflight_passed"] else 5


if __name__ == "__main__":
    raise SystemExit(main())
