"""W2 of GTKB-WRAPUP-ENHANCEMENTS Slice 1: S2 cross-artifact consistency scanner.

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006).
Detects the phantom-INDEX-citation class and adjacent reference-integrity failures:

    index_cites_missing_bridge_file       (S308 phantom-INDEX recurrences)
    bridge_file_orphaned_from_index       (overlap with W1; reported with thread context)
    worklist_cites_missing_bridge_file    (latent class)
    memory_md_cites_missing_topic_file    (latent class)
    claude_md_cites_missing_rule          (latent class)
    da_cites_missing_bridge_file          (latent class)

EXIT CODES (Slice 1 simple contract):
    0  Clean, info-only, OR warn findings present
    2  At least one error-severity finding present
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wrap_io import _atomic_write_text  # noqa: E402


SEVERITY_INFO = "info"
SEVERITY_WARN = "warn"
SEVERITY_ERROR = "error"

EXIT_OK = 0
EXIT_ERROR = 2

# Per WRAPUP -011 §2: allowlist for known-acceptable historical phantom-INDEX
# entries. Stage 1 ships an empty production list; Stage 2 (separate follow-up
# bridge) populates with reviewed entries. Absent or empty allowlist preserves
# current behavior (all phantom citations at error-severity).
ALLOWLIST_PATH_RELATIVE = ".groundtruth/wrap-scan/historical-phantoms.toml"

INDEX_LINE_PATTERN = re.compile(
    r"^\s*(NEW|REVISED|GO|NO-GO|VERIFIED):\s+(bridge/[A-Za-z0-9_-]+-\d{3}\.md)\s*$"
)
WORKLIST_BRIDGE_REF_PATTERN = re.compile(r"`(bridge/[A-Za-z0-9_-]+-\d{3}\.md)`")
MEMORY_INDEX_REF_PATTERN = re.compile(r"\[[^\]]+\]\(([A-Za-z0-9_./-]+\.md)\)")
RULE_REF_PATTERN = re.compile(r"`(\.claude/rules/[A-Za-z0-9_./-]+\.md)`")


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _finding(check: str, severity: str, message: str, **details: Any) -> dict:
    return {"check": check, "severity": severity, "message": message, **details}


def _load_allowlist(project_root: Path) -> dict[str, dict]:
    """Load historical-phantom allowlist; fail loudly on malformed.

    Per WRAPUP -012 GO conditions: malformed allowlist must fail loudly
    (raise), not silently default. Absent/empty allowlist returns empty
    dict and preserves current behavior (all findings at error-severity).
    """
    allowlist_path = project_root / ALLOWLIST_PATH_RELATIVE
    if not allowlist_path.exists():
        return {}
    try:
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef,import-not-found]
        data = tomllib.loads(allowlist_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(
            f"Allowlist at {ALLOWLIST_PATH_RELATIVE} is malformed; refusing "
            f"to silently default. Fix or delete the file. Underlying error: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Allowlist at {ALLOWLIST_PATH_RELATIVE} must be a TOML mapping at the top level."
        )

    schema_version = data.get("schema_version")
    if schema_version != 1:
        raise RuntimeError(
            f"Allowlist schema_version={schema_version!r}; expected 1. "
            "Update the allowlist file or this scanner."
        )

    phantoms = data.get("phantoms", [])
    if not isinstance(phantoms, list):
        raise RuntimeError(
            f"Allowlist 'phantoms' field must be a list; got {type(phantoms).__name__}."
        )

    by_pattern: dict[str, dict] = {}
    for entry in phantoms:
        if not isinstance(entry, dict):
            raise RuntimeError(
                f"Allowlist phantom entry must be a mapping; got {type(entry).__name__}: {entry!r}"
            )
        pattern = entry.get("index_line_pattern")
        if not isinstance(pattern, str) or not pattern.strip():
            raise RuntimeError(
                f"Allowlist phantom entry missing/invalid 'index_line_pattern': {entry!r}"
            )
        by_pattern[pattern.strip()] = entry
    return by_pattern


def check_index_cites_missing_bridge_file(project_root: Path) -> list[dict]:
    """Detect INDEX lines citing missing bridge files.

    Per WRAPUP -012: matches against the allowlist (loaded via _load_allowlist
    above). Allowlisted lines emit info-severity finding with reason; un-
    allowlisted missing files remain error-severity (canonical S308 class).
    """
    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.exists():
        return []
    allowlist = _load_allowlist(project_root)
    findings: list[dict] = []
    for line_no, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), 1):
        match = INDEX_LINE_PATTERN.match(line)
        if not match:
            continue
        status, ref = match.groups()
        cited_path = project_root / ref
        if cited_path.exists():
            continue
        normalized = line.strip()
        allowlist_entry = allowlist.get(normalized)
        if allowlist_entry is not None:
            findings.append(
                _finding(
                    "index_cites_missing_bridge_file",
                    SEVERITY_INFO,
                    f"INDEX.md line {line_no} cites missing file (allowlisted historical phantom): {ref} ({status})",
                    line_number=line_no,
                    status=status,
                    cited_path=ref,
                    allowlist_reason=allowlist_entry.get("reason", "(no reason field)"),
                    codex_review_bridge=allowlist_entry.get("codex_review_bridge"),
                )
            )
        else:
            findings.append(
                _finding(
                    "index_cites_missing_bridge_file",
                    SEVERITY_ERROR,
                    f"INDEX.md line {line_no} cites missing file: {ref} ({status})",
                    line_number=line_no,
                    status=status,
                    cited_path=ref,
                )
            )
    return findings


def check_bridge_file_orphaned_from_index(project_root: Path) -> list[dict]:
    bridge_dir = project_root / "bridge"
    index_path = bridge_dir / "INDEX.md"
    if not index_path.exists() or not bridge_dir.is_dir():
        return []
    index_text = index_path.read_text(encoding="utf-8")
    findings: list[dict] = []
    for entry in bridge_dir.iterdir():
        if not entry.is_file() or entry.name == "INDEX.md" or entry.suffix != ".md":
            continue
        ref = f"bridge/{entry.name}"
        if ref not in index_text:
            findings.append(
                _finding(
                    "bridge_file_orphaned_from_index",
                    SEVERITY_WARN,
                    f"Bridge file present on disk but not referenced by any INDEX line: {ref}",
                    path=ref,
                )
            )
    return findings


def check_worklist_cites_missing_bridge_file(project_root: Path) -> list[dict]:
    worklist = project_root / "memory" / "work_list.md"
    if not worklist.exists():
        return []
    findings: list[dict] = []
    text = worklist.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), 1):
        for match in WORKLIST_BRIDGE_REF_PATTERN.finditer(line):
            ref = match.group(1)
            cited = project_root / ref
            if not cited.exists():
                findings.append(
                    _finding(
                        "worklist_cites_missing_bridge_file",
                        SEVERITY_WARN,
                        f"work_list.md line {line_no} cites missing bridge: {ref}",
                        line_number=line_no,
                        cited_path=ref,
                    )
                )
    return findings


def check_memory_md_cites_missing_topic_file(project_root: Path) -> list[dict]:
    """Check in-root MEMORY.md for missing topic refs."""
    memory_md = project_root / "memory" / "MEMORY.md"
    if not memory_md.exists():
        return []
    findings: list[dict] = []
    base = memory_md.parent
    for line_no, line in enumerate(memory_md.read_text(encoding="utf-8").splitlines(), 1):
        for match in MEMORY_INDEX_REF_PATTERN.finditer(line):
            ref = match.group(1)
            if ref.startswith(("http://", "https://")) or "/" in ref and ref.split("/")[0] in ("docs", "scripts"):
                continue
            cited = base / ref
            if not cited.exists():
                findings.append(
                    _finding(
                        "memory_md_cites_missing_topic_file",
                        SEVERITY_WARN,
                        f"MEMORY.md line {line_no} cites missing topic file: {ref}",
                        line_number=line_no,
                        cited_path=str(ref),
                    )
                )
    return findings


def check_claude_md_cites_missing_rule(project_root: Path) -> list[dict]:
    findings: list[dict] = []
    for source_name in ("CLAUDE.md", "AGENTS.md"):
        source = project_root / source_name
        if not source.exists():
            continue
        for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            for match in RULE_REF_PATTERN.finditer(line):
                ref = match.group(1)
                cited = project_root / ref
                if not cited.exists():
                    findings.append(
                        _finding(
                            "claude_md_cites_missing_rule",
                            SEVERITY_WARN,
                            f"{source_name} line {line_no} cites missing rule: {ref}",
                            source=source_name,
                            line_number=line_no,
                            cited_path=ref,
                        )
                    )
    rules_dir = project_root / ".claude" / "rules"
    if rules_dir.is_dir():
        for rule in rules_dir.glob("*.md"):
            for line_no, line in enumerate(rule.read_text(encoding="utf-8").splitlines(), 1):
                for match in RULE_REF_PATTERN.finditer(line):
                    ref = match.group(1)
                    cited = project_root / ref
                    if not cited.exists():
                        findings.append(
                            _finding(
                                "claude_md_cites_missing_rule",
                                SEVERITY_WARN,
                                f"{rule.relative_to(project_root)} line {line_no} cites missing rule: {ref}",
                                source=str(rule.relative_to(project_root)),
                                line_number=line_no,
                                cited_path=ref,
                            )
                        )
    return findings


def check_da_cites_missing_bridge_file(project_root: Path) -> list[dict]:
    db_path = project_root / "groundtruth.db"
    if not db_path.exists():
        return []
    findings: list[dict] = []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT id, content FROM deliberations WHERE content LIKE '%bridge/%-%.md%'"
            )
            for row in cursor:
                content = row["content"] or ""
                for ref in re.findall(r"bridge/[A-Za-z0-9_-]+-\d{3}\.md", content):
                    if not (project_root / ref).exists():
                        findings.append(
                            _finding(
                                "da_cites_missing_bridge_file",
                                SEVERITY_WARN,
                                f"Deliberation {row['id']} cites missing bridge: {ref}",
                                deliberation_id=row["id"],
                                cited_path=ref,
                            )
                        )
        finally:
            conn.close()
    except sqlite3.Error:
        return []
    return findings


CHECKS = (
    check_index_cites_missing_bridge_file,
    check_bridge_file_orphaned_from_index,
    check_worklist_cites_missing_bridge_file,
    check_memory_md_cites_missing_topic_file,
    check_claude_md_cites_missing_rule,
    check_da_cites_missing_bridge_file,
)


def run_all_checks(project_root: Path) -> list[dict]:
    findings: list[dict] = []
    for check in CHECKS:
        findings.extend(check(project_root))
    return findings


def render_markdown(findings: list[dict]) -> str:
    if not findings:
        return "# Wrap Consistency Scan\n\nNo findings. Cross-artifact references are intact.\n"
    by_severity: dict[str, list[dict]] = {SEVERITY_ERROR: [], SEVERITY_WARN: [], SEVERITY_INFO: []}
    for f in findings:
        by_severity.setdefault(f["severity"], []).append(f)
    lines = ["# Wrap Consistency Scan", ""]
    for sev in (SEVERITY_ERROR, SEVERITY_WARN, SEVERITY_INFO):
        items = by_severity.get(sev, [])
        if not items:
            continue
        lines.append(f"## {sev.upper()} ({len(items)})")
        lines.append("")
        for f in items:
            lines.append(f"- **{f['check']}**: {f['message']}")
        lines.append("")
    return "\n".join(lines)


def determine_exit_code(findings: list[dict]) -> int:
    if any(f["severity"] == SEVERITY_ERROR for f in findings):
        return EXIT_ERROR
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--report-format", choices=("json", "markdown"), default="json",
    )
    parser.add_argument("--write-report", default=None)
    args = parser.parse_args(argv)

    project_root = _project_root()
    findings = run_all_checks(project_root)

    if args.report_format == "markdown":
        output = render_markdown(findings)
    else:
        output = json.dumps({"findings": findings, "count": len(findings)}, indent=2) + "\n"

    if args.write_report:
        _atomic_write_text(Path(args.write_report), output)
    else:
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")

    return determine_exit_code(findings)


if __name__ == "__main__":
    sys.exit(main())
