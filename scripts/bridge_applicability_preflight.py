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

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_INDEX_PATH: Final[Path] = PROJECT_ROOT / "bridge" / "INDEX.md"
DEFAULT_CONFIG_PATH: Final[Path] = PROJECT_ROOT / "config" / "governance" / "spec-applicability.toml"
DEFAULT_DB_PATH: Final[Path] = PROJECT_ROOT / "groundtruth.db"

INDEX_DOC_RE: Final[re.Pattern[str]] = re.compile(r"^Document:\s+(\S+)\s*$")
INDEX_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED):\s+(bridge/\S+\.md)\s*$"
)
SPEC_LINK_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?specification(?:\s+links?|\s+references?|\s*)$",
    re.IGNORECASE,
)
SPEC_ID_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ|DELIB)-[A-Z0-9][A-Z0-9_-]*\b")
RULE_PATH_RE: Final[re.Pattern[str]] = re.compile(r"\.claude/rules/[a-z0-9_-]+\.md")
WORK_ITEM_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:WI|GTKB)-[A-Z0-9][A-Z0-9_-]*\b")
# Anchored to an enumerated repo-directory set so prose "word/word" tokens
# (e.g. GO/NO-GO, prime-builder/loyal-opposition) are not harvested as
# repository paths. Kept consistent with scripts/implementation_start_gate.py.
PATH_TOKEN_RE: Final[re.Pattern[str]] = re.compile(
    r"(?P<path>(?:\.?/?(?:scripts|groundtruth-kb/src|groundtruth-kb/tests|platform_tests|tests|config|\.claude/hooks|\.codex/gtkb-hooks|\.github|bridge|independent-progress-assessments)/[^\s'\";]+|\.claude/settings\.json|\.codex/hooks\.json|pyproject\.toml|groundtruth\.toml))"
)
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


def _strip_code_fences(lines: list[str]) -> list[str]:
    fence_re = re.compile(r"^\s*(?:```|~~~)")
    in_fence = False
    out: list[str] = []
    for line in lines:
        if fence_re.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


def parse_index_for_document(index_path: Path, bridge_id: str) -> list[BridgeVersion]:
    if not index_path.is_file():
        return []
    versions: list[BridgeVersion] = []
    in_target = False
    root = index_path.parent.parent
    for line in index_path.read_text(encoding="utf-8").splitlines():
        doc_match = INDEX_DOC_RE.match(line.strip())
        if doc_match:
            in_target = doc_match.group(1) == bridge_id
            continue
        if not in_target:
            continue
        status_match = INDEX_STATUS_RE.match(line.strip())
        if status_match:
            rel_path = status_match.group(2)
            version_match = re.search(r"-(\d+)\.md$", rel_path)
            versions.append(
                BridgeVersion(
                    status=status_match.group(1),
                    rel_path=rel_path,
                    abs_path=root / rel_path,
                    version_number=int(version_match.group(1)) if version_match else 0,
                )
            )
        elif line.strip() == "":
            break
    return versions


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
    index_path: Path = DEFAULT_INDEX_PATH,
    config_path: Path = DEFAULT_CONFIG_PATH,
    db_path: Path = DEFAULT_DB_PATH,
    content_file: Path | None = None,
) -> dict[str, Any]:
    versions = parse_index_for_document(index_path, bridge_id)
    operative = choose_operative_version(versions)
    if operative is None and content_file is None:
        raise SystemExit(f"ERR_NO_INDEX_ENTRY: no entry for bridge_id={bridge_id!r} in {index_path}")
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
            "mode": "indexed_operative",
            "path": operative.rel_path,
        }
    else:
        raise SystemExit(f"ERR_NO_INDEX_ENTRY: no entry for bridge_id={bridge_id!r} in {index_path}")
    cited_specs = extract_spec_links(content)
    target_paths = extract_target_paths(content)
    cited_implementation_paths = collect_cited_implementation_paths(content)
    project_root = index_path.parent.parent
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


def format_markdown(packet: dict[str, Any]) -> str:
    operative = packet.get("operative_version")
    operative_path = operative["path"] if isinstance(operative, dict) else "(none)"
    content_source = packet.get("content_source") or {}
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
        f"- missing_required_specs: {json.dumps(packet['missing_required_specs'])}",
        f"- missing_advisory_specs: {json.dumps(packet['missing_advisory_specs'])}",
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
    parser.add_argument("--bridge-id", required=True, help="Document name from bridge/INDEX.md.")
    parser.add_argument(
        "--content-file", type=Path, default=None, help="Evaluate pending Markdown content from a file."
    )
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    packet = build_packet(
        bridge_id=args.bridge_id,
        index_path=args.index,
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
