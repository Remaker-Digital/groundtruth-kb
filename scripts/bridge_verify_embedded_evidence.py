#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Verify bridge-file embedded appendix evidence against source files.

This read-only helper checks bridge reports that embed source snapshots in
appendix code fences. It compares each appendix body to the corresponding
declared ``target_paths`` source file after LF normalization, and it scans the
bridge file for the canonical CLAUSE-IN-ROOT forbidden path regex.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

try:
    from scripts.bridge_applicability_preflight import (
        BridgeVersion,
        choose_operative_version,
        parse_versioned_files_for_document,
    )
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from bridge_applicability_preflight import (  # type: ignore[no-redef]
        BridgeVersion,
        choose_operative_version,
        parse_versioned_files_for_document,
    )

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_BRIDGE_DIR: Final[Path] = PROJECT_ROOT / "bridge"
DEFAULT_CLAUSES_CONFIG: Final[Path] = PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"
EXIT_CHECK_FAILED: Final[int] = 5

DOCUMENT_DECLARATION_RE: Final[re.Pattern[str]] = re.compile(r"(?im)^\s*Document:\s*([A-Za-z0-9_.-]+)\s*$")
TARGET_PATHS_DECLARATION_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:\*\*)?target_paths?(?:\*\*)?\s*[:=]\s*(.+)",
    re.IGNORECASE,
)
APPENDIX_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*#{0,6}\s*(?P<label>Appendix\s+A\d+)\s*[-\u2013\u2014]\s*`?(?P<filename>[^`\r\n]+?)`?\s*$",
    re.IGNORECASE,
)
FENCE_RE: Final[re.Pattern[str]] = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})")
IN_ROOT_DISCLOSURE_START_RE: Final[re.Pattern[str]] = re.compile(
    r"<!--\s*in-root-disclosure\s*-->",
    re.IGNORECASE,
)
IN_ROOT_DISCLOSURE_END_RE: Final[re.Pattern[str]] = re.compile(
    r"<!--\s*/in-root-disclosure\s*-->",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AppendixBlock:
    label: str
    filename: str
    body: str
    heading_line: int


@dataclass(frozen=True)
class AppendixCheck:
    appendix: str
    filename: str
    heading_line: int
    source_path: str | None
    embedded_sha256: str | None
    source_sha256: str | None
    match: bool
    status: str


@dataclass(frozen=True)
class RootBoundaryOccurrence:
    line: int
    text: str
    matches: int


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
    token = _normalize_path_token(str(parsed))
    return {token} if token else set()


def extract_declared_target_paths(content: str) -> set[str]:
    paths: set[str] = set()
    for line in content.splitlines():
        match = TARGET_PATHS_DECLARATION_RE.match(line)
        if match:
            paths.update(_parse_declared_path_values(match.group(1)))
    return paths


def extract_appendix_blocks(content: str) -> list[AppendixBlock]:
    lines = content.splitlines()
    blocks: list[AppendixBlock] = []
    idx = 0
    while idx < len(lines):
        heading = APPENDIX_HEADING_RE.match(lines[idx])
        if not heading:
            idx += 1
            continue
        search_idx = idx + 1
        while search_idx < len(lines) and not lines[search_idx].strip():
            search_idx += 1
        if search_idx >= len(lines):
            blocks.append(
                AppendixBlock(
                    label=heading.group("label").strip(),
                    filename=heading.group("filename").strip(),
                    body="",
                    heading_line=idx + 1,
                )
            )
            idx += 1
            continue
        fence_match = FENCE_RE.match(lines[search_idx])
        if not fence_match:
            blocks.append(
                AppendixBlock(
                    label=heading.group("label").strip(),
                    filename=heading.group("filename").strip(),
                    body="",
                    heading_line=idx + 1,
                )
            )
            idx = search_idx
            continue
        fence = fence_match.group("fence")[0]
        close_re = re.compile(rf"^\s*{re.escape(fence * 3)}")
        body_lines: list[str] = []
        body_idx = search_idx + 1
        while body_idx < len(lines):
            if close_re.match(lines[body_idx]):
                break
            body_lines.append(lines[body_idx])
            body_idx += 1
        blocks.append(
            AppendixBlock(
                label=heading.group("label").strip(),
                filename=heading.group("filename").strip(),
                body="\n".join(body_lines),
                heading_line=idx + 1,
            )
        )
        idx = body_idx + 1
    return blocks


def normalize_lf_single_trailing_newline(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.rstrip("\n") + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _display_path(path: Path, root: Path = PROJECT_ROOT) -> str:
    resolved = path.resolve(strict=False)
    try:
        return resolved.relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        try:
            return resolved.relative_to(PROJECT_ROOT.resolve(strict=False)).as_posix()
        except ValueError:
            return str(path)


def _resolve_target(project_root: Path, target_path: str) -> Path | None:
    raw = Path(target_path)
    candidate = raw if raw.is_absolute() else project_root / raw
    if not _is_under(candidate, project_root):
        return None
    return candidate.resolve(strict=False)


def _infer_project_root(content_file: Path | None, bridge_dir: Path, target_paths: set[str]) -> Path:
    if content_file is not None:
        bases = [content_file.parent, *content_file.parents]
        for base in bases:
            if any((base / target).exists() for target in target_paths):
                return base
    return bridge_dir.parent


def _basename(value: str) -> str:
    return Path(value.replace("\\", "/")).name.lower()


def check_appendices(
    *,
    blocks: list[AppendixBlock],
    target_paths: set[str],
    project_root: Path,
) -> list[AppendixCheck]:
    checks: list[AppendixCheck] = []
    for block in blocks:
        basename = _basename(block.filename)
        matches = sorted(path for path in target_paths if _basename(path) == basename)
        embedded_normalized = normalize_lf_single_trailing_newline(block.body)
        embedded_sha = _sha256_text(embedded_normalized)
        if not matches:
            checks.append(
                AppendixCheck(
                    appendix=block.label,
                    filename=block.filename,
                    heading_line=block.heading_line,
                    source_path=None,
                    embedded_sha256=embedded_sha,
                    source_sha256=None,
                    match=False,
                    status="unresolved",
                )
            )
            continue
        if len(matches) > 1:
            checks.append(
                AppendixCheck(
                    appendix=block.label,
                    filename=block.filename,
                    heading_line=block.heading_line,
                    source_path=", ".join(matches),
                    embedded_sha256=embedded_sha,
                    source_sha256=None,
                    match=False,
                    status="ambiguous",
                )
            )
            continue
        source = _resolve_target(project_root, matches[0])
        if source is None:
            checks.append(
                AppendixCheck(
                    appendix=block.label,
                    filename=block.filename,
                    heading_line=block.heading_line,
                    source_path=matches[0],
                    embedded_sha256=embedded_sha,
                    source_sha256=None,
                    match=False,
                    status="out_of_root",
                )
            )
            continue
        if not source.is_file():
            checks.append(
                AppendixCheck(
                    appendix=block.label,
                    filename=block.filename,
                    heading_line=block.heading_line,
                    source_path=_display_path(source, project_root),
                    embedded_sha256=embedded_sha,
                    source_sha256=None,
                    match=False,
                    status="source_missing",
                )
            )
            continue
        source_normalized = normalize_lf_single_trailing_newline(source.read_text(encoding="utf-8"))
        source_sha = _sha256_text(source_normalized)
        checks.append(
            AppendixCheck(
                appendix=block.label,
                filename=block.filename,
                heading_line=block.heading_line,
                source_path=_display_path(source, project_root),
                embedded_sha256=embedded_sha,
                source_sha256=source_sha,
                match=embedded_sha == source_sha,
                status="match" if embedded_sha == source_sha else "mismatch",
            )
        )
    return checks


def load_clause_in_root_pattern(config_path: Path) -> tuple[str, bool]:
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    for clause in data.get("clauses", []):
        if str(clause.get("clause_id", "")).endswith("/CLAUSE-IN-ROOT"):
            pattern = clause.get("failure_pattern")
            if not pattern:
                raise SystemExit("ERR_CLAUSE_IN_ROOT_MISSING_FAILURE_PATTERN")
            return str(pattern), bool(clause.get("failure_pattern_disclosure_exempt", False))
    raise SystemExit("ERR_CLAUSE_IN_ROOT_NOT_FOUND")


def _iter_root_boundary_scan_lines(content: str, disclosure_exempt: bool) -> list[tuple[int, str]]:
    if not disclosure_exempt:
        return [(idx, line) for idx, line in enumerate(content.splitlines(), start=1)]

    scan_lines: list[tuple[int, str]] = []
    in_disclosure = False
    for idx, line in enumerate(content.splitlines(), start=1):
        starts = bool(IN_ROOT_DISCLOSURE_START_RE.search(line))
        ends = bool(IN_ROOT_DISCLOSURE_END_RE.search(line))
        if starts:
            in_disclosure = True
        if in_disclosure:
            if TARGET_PATHS_DECLARATION_RE.match(line):
                scan_lines.append((idx, line))
            if ends:
                in_disclosure = False
            continue
        scan_lines.append((idx, line))
        if ends:
            in_disclosure = False
    return scan_lines


def scan_root_boundary(
    *,
    content: str,
    pattern: str,
    disclosure_exempt: bool,
) -> dict[str, Any]:
    regex = re.compile(pattern)
    occurrences: list[RootBoundaryOccurrence] = []
    for line_no, line in _iter_root_boundary_scan_lines(content, disclosure_exempt):
        matches = list(regex.finditer(line))
        if matches:
            occurrences.append(RootBoundaryOccurrence(line=line_no, text=line.strip(), matches=len(matches)))
    return {
        "pattern": pattern,
        "disclosure_exempt": disclosure_exempt,
        "occurrences": sum(item.matches for item in occurrences),
        "lines": [asdict(item) for item in occurrences],
    }


def _derive_bridge_id_from_content_file(content_file: Path) -> str:
    content = content_file.read_text(encoding="utf-8")
    document_match = DOCUMENT_DECLARATION_RE.search(content)
    if document_match:
        return document_match.group(1)
    return re.sub(r"-\d{3}$", "", content_file.stem)


def _load_content(
    *,
    bridge_id: str,
    bridge_dir: Path,
    content_file: Path | None,
) -> tuple[str, dict[str, Any], BridgeVersion | None, list[BridgeVersion]]:
    if content_file is not None:
        return (
            content_file.read_text(encoding="utf-8"),
            {"mode": "pending_content", "path": _display_path(content_file)},
            None,
            [],
        )
    versions = parse_versioned_files_for_document(bridge_dir, bridge_id)
    operative = choose_operative_version(versions)
    if operative is None:
        raise SystemExit(
            f"ERR_NO_BRIDGE_THREAD: no versioned bridge files found for bridge_id={bridge_id!r} under {bridge_dir}"
        )
    if not operative.abs_path.is_file():
        raise SystemExit(f"ERR_BRIDGE_FILE_MISSING: {operative.rel_path}")
    return (
        operative.abs_path.read_text(encoding="utf-8"),
        {"mode": "bridge_file_operative", "path": operative.rel_path},
        operative,
        versions,
    )


def _is_implementation_report(content: str) -> bool:
    return bool(re.search(r"(?im)^\s*bridge_kind:\s*implementation_report\s*$", content))


def _approved_proposal_target_paths(versions: list[BridgeVersion]) -> tuple[set[str], dict[str, Any] | None]:
    for version in sorted(versions, key=lambda item: item.version_number, reverse=True):
        if version.status not in {"NEW", "REVISED"} or not version.abs_path.is_file():
            continue
        content = version.abs_path.read_text(encoding="utf-8")
        if _is_implementation_report(content):
            continue
        target_paths = extract_declared_target_paths(content)
        if target_paths:
            return target_paths, {"mode": "approved_proposal", "path": version.rel_path}
    return set(), None


def build_report(
    *,
    bridge_id: str,
    bridge_dir: Path = DEFAULT_BRIDGE_DIR,
    clauses_config: Path = DEFAULT_CLAUSES_CONFIG,
    content_file: Path | None = None,
) -> dict[str, Any]:
    content, content_source, operative, versions = _load_content(
        bridge_id=bridge_id,
        bridge_dir=bridge_dir,
        content_file=content_file,
    )
    target_paths = extract_declared_target_paths(content)
    target_path_source: dict[str, Any] = dict(content_source)
    if not target_paths and content_file is None:
        proposal_paths, proposal_source = _approved_proposal_target_paths(versions)
        if proposal_paths and proposal_source is not None:
            target_paths = proposal_paths
            target_path_source = proposal_source
    project_root = _infer_project_root(content_file, bridge_dir, target_paths)
    appendix_checks = check_appendices(
        blocks=extract_appendix_blocks(content),
        target_paths=target_paths,
        project_root=project_root,
    )
    pattern, disclosure_exempt = load_clause_in_root_pattern(clauses_config)
    root_boundary = scan_root_boundary(content=content, pattern=pattern, disclosure_exempt=disclosure_exempt)
    appendix_failures = [check for check in appendix_checks if not check.match]
    root_failures = int(root_boundary["occurrences"])
    passed = not appendix_failures and root_failures == 0
    return {
        "bridge_id": bridge_id,
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
        "project_root": _display_path(project_root, project_root),
        "target_paths": sorted(target_paths),
        "target_path_source": target_path_source,
        "appendices": [asdict(check) for check in appendix_checks],
        "root_boundary": root_boundary,
        "summary": {
            "appendix_count": len(appendix_checks),
            "appendix_failures": len(appendix_failures),
            "root_boundary_failures": root_failures,
        },
        "passed": passed,
    }


def format_markdown(report: dict[str, Any]) -> str:
    source = report.get("content_source") or {}
    lines = [
        "## Embedded Evidence Verification",
        "",
        f"- bridge_id: `{report['bridge_id']}`",
        f"- content_source: `{source.get('mode')}`",
        f"- content_file: `{source.get('path')}`",
        f"- passed: `{str(report['passed']).lower()}`",
        f"- appendix_failures: `{report['summary']['appendix_failures']}`",
        f"- root_boundary_failures: `{report['summary']['root_boundary_failures']}`",
        "",
        "| Appendix | Filename | Status | Source |",
        "|---|---|---|---|",
    ]
    for appendix in report["appendices"]:
        lines.append(
            f"| `{appendix['appendix']}` | `{appendix['filename']}` | `{appendix['status']}` | "
            f"`{appendix['source_path'] or ''}` |"
        )
    if report["root_boundary"]["lines"]:
        lines += ["", "### Root-Boundary Matches", ""]
        for item in report["root_boundary"]["lines"]:
            lines.append(f"- line {item['line']}: `{item['text']}`")
    return "\n".join(lines) + "\n"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-id",
        help="Bridge document name / versioned bridge-thread slug. Optional when --content-file is supplied.",
    )
    parser.add_argument("--content-file", type=Path, help="Evaluate pending Markdown content from a file.")
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--clauses-config", type=Path, default=DEFAULT_CLAUSES_CONFIG)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    if args.bridge_id is None:
        if args.content_file is None:
            parser.error("--bridge-id is required unless --content-file is supplied")
        args.bridge_id = _derive_bridge_id_from_content_file(args.content_file)
    report = build_report(
        bridge_id=args.bridge_id,
        bridge_dir=args.bridge_dir,
        clauses_config=args.clauses_config,
        content_file=args.content_file,
    )
    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(format_markdown(report))
    return 0 if report["passed"] else EXIT_CHECK_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
