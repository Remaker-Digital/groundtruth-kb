"""W2 of GTKB-WRAPUP-ENHANCEMENTS Slice 1: S2 cross-artifact consistency scanner.

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006).
Detects bridge-file structural drift and adjacent reference-integrity failures:

    bridge_numbered_file_missing_status   (status-bearing file without status)
    (retired: legacy standing-backlog cross-ref check removed at Slice 7-prime)
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
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wrap_io import _atomic_write_text  # noqa: E402

SEVERITY_INFO = "info"
SEVERITY_WARN = "warn"
SEVERITY_ERROR = "error"

EXIT_OK = 0
EXIT_ERROR = 2

BRIDGE_NUMBERED_FILE_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+-\d{3}\.md$")
MEMORY_INDEX_REF_PATTERN = re.compile(r"\[[^\]]+\]\(([A-Za-z0-9_./-]+\.md)\)")
RULE_REF_PATTERN = re.compile(r"`(\.claude/rules/[A-Za-z0-9_./-]+\.md)`")


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _finding(check: str, severity: str, message: str, **details: Any) -> dict:
    return {"check": check, "severity": severity, "message": message, **details}


def _ensure_bridge_helpers_importable(project_root: Path) -> None:
    gt_src = project_root / "groundtruth-kb" / "src"
    if gt_src.exists():
        src_text = str(gt_src)
        if src_text not in sys.path:
            sys.path.insert(0, src_text)


def _git_head_bridge_files(project_root: Path) -> set[str] | None:
    """Return paths of bridge numbered files present at HEAD, or None when git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "bridge"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        return set(result.stdout.strip().splitlines())
    except Exception:
        return None


def check_bridge_numbered_files_have_status(
    project_root: Path,
    *,
    head_resolver: Callable[[Path], set[str] | None] = _git_head_bridge_files,
) -> list[dict]:
    """Flag numbered bridge files that are new (not at HEAD) and missing a status token.

    Files already present at HEAD are grandfathered per GOV-FILE-BRIDGE-AUTHORITY-001's
    body-status-token grandfather clause.  When the HEAD resolver is unavailable, all
    files are treated as grandfathered and a single INFO finding is emitted instead of
    potentially false-positive ERRORs.
    """
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return []
    _ensure_bridge_helpers_importable(project_root)
    from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

    head_files = head_resolver(project_root)

    if head_files is None:
        # Fail toward not over-reporting: grandfather everything when git is unavailable.
        # The Write-time bridge-compliance gate remains the primary enforcement for new files.
        return [
            _finding(
                "bridge_status_grandfather_unavailable",
                SEVERITY_INFO,
                "Git HEAD unavailable; all bridge numbered files grandfathered (no missing-status check performed)",
            )
        ]

    findings: list[dict] = []
    for entry in bridge_dir.iterdir():
        if not entry.is_file() or not BRIDGE_NUMBERED_FILE_PATTERN.match(entry.name):
            continue
        ref = f"bridge/{entry.name}"
        if ref in head_files:
            continue  # grandfathered: already in committed history
        if status_from_bridge_file(entry) is None:
            findings.append(
                _finding(
                    "bridge_numbered_file_missing_status",
                    SEVERITY_ERROR,
                    f"Numbered bridge file is missing a lifecycle status token: {ref}",
                    path=ref,
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
            cursor = conn.execute("SELECT id, content FROM deliberations WHERE content LIKE '%bridge/%-%.md%'")
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
    check_bridge_numbered_files_have_status,
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
        "--report-format",
        choices=("json", "markdown"),
        default="json",
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
