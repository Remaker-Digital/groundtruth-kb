#!/usr/bin/env python3
"""Skill-health static checker — Slice 0 of the skill-modernization umbrella.

Read-only detector over GroundTruth-KB skill markdown for the CLI-bypass
anti-patterns the umbrella targets:

1. ``fenced_python``  — fenced ```python blocks embedded in a skill body.
2. ``db_mutation``    — inline DB-mutation snippets a skill instructs the agent
   to run directly (``db.insert_*(`` / ``db.update_*(`` / ``KnowledgeDB(`` /
   ``INSERT INTO`` / ``UPDATE … SET`` / ``DELETE FROM``).
3. ``bridge_direct_write`` — direct numbered bridge-file write/edit
   instructions that are NOT routed through a governed helper
   (``bridge-propose`` / ``write_bridge.py``).
4. ``index_write`` — direct ``bridge/INDEX.md`` mutation/restoration
   instructions that are NOT routed through governed helper language.

The checker reports findings on stdout and creates no files or database.
Current formal anchors: GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 and
ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_SKILL_ROOTS: tuple[str, ...] = (".agents/skills",)

# --- Detection patterns ------------------------------------------------------

# A fenced code block opening that declares python (``` ```python ``` `` or `` ```py ``).
_FENCED_PYTHON_RE = re.compile(r"^`{3,}\s*(?:python|py)\b", re.IGNORECASE)

# Inline DB-mutation snippets. db.* and KnowledgeDB( are case-sensitive (Python
# identifiers); the SQL DML keywords are case-insensitive.
_DB_MUTATION_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdb\.(?:insert|update|delete)_\w+\s*\("),
    re.compile(r"\bKnowledgeDB\s*\("),
    re.compile(r"\bINSERT\s+INTO\b", re.IGNORECASE),
    re.compile(r"\bUPDATE\s+\w+\s+SET\b", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE),
)

# Direct numbered bridge-file write/edit instruction (either verb→path or path→verb).
_BRIDGE_DIRECT_WRITE_RE = re.compile(
    r"(?:insert|edit|add|append|write|update|modify)\b[^\n]{0,60}bridge/[A-Za-z0-9._-]+-\d{3}\.md"
    r"|bridge/[A-Za-z0-9._-]+-\d{3}\.md[^\n]{0,60}(?:insert|edit|add|append|write|update|modify)\b",
    re.IGNORECASE,
)

# Direct retired aggregate-index mutation instruction (either verb→path or path→verb).
_INDEX_WRITE_RE = re.compile(
    r"(?:insert|edit|add|append|write|update|modify|create|restore)\b[^\n]{0,80}bridge[/\\]INDEX\.md"
    r"|bridge[/\\]INDEX\.md[^\n]{0,80}(?:insert|edit|add|append|write|update|modify|create|restore)\b",
    re.IGNORECASE,
)

# Governed-helper references that legitimize bridge/index manipulation (suppress FP).
_GOVERNED_HELPER_RE = re.compile(
    r"bridge-propose|write_bridge\.py|helpers/write_bridge|gtkb-bridge|\bgt\s+bridge\b",
    re.IGNORECASE,
)

FINDING_TYPES = ("fenced_python", "db_mutation", "bridge_direct_write", "index_write")


@dataclass(frozen=True)
class Finding:
    """A single detected anti-pattern occurrence in a skill file."""

    skill_path: str
    finding_type: str
    line: int
    snippet: str


@dataclass
class Report:
    """The structured result of one checker run."""

    run_id: str
    generated_at: str
    skill_roots: list[str]
    skills_scanned: int
    findings: list[Finding]
    findings_by_type: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "skill_roots": list(self.skill_roots),
            "skills_scanned": self.skills_scanned,
            "finding_count": len(self.findings),
            "findings_by_type": dict(self.findings_by_type),
            "findings": [asdict(f) for f in self.findings],
        }


def scan_text(text: str, skill_path: str) -> list[Finding]:
    """Scan a single skill's markdown text and return detected findings.

    Pure function: no I/O. The line numbers are 1-based.
    """
    findings: list[Finding] = []
    for index, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        snippet = stripped[:200]

        if _FENCED_PYTHON_RE.match(stripped):
            findings.append(Finding(skill_path, "fenced_python", index, snippet))

        for pattern in _DB_MUTATION_RES:
            if pattern.search(line):
                findings.append(Finding(skill_path, "db_mutation", index, snippet))
                break

        if _BRIDGE_DIRECT_WRITE_RE.search(line) and not _GOVERNED_HELPER_RE.search(line):
            findings.append(Finding(skill_path, "bridge_direct_write", index, snippet))

        if _INDEX_WRITE_RE.search(line) and not _GOVERNED_HELPER_RE.search(line):
            findings.append(Finding(skill_path, "index_write", index, snippet))

    return findings


def discover_skill_files(roots: list[str], project_root: Path) -> list[Path]:
    """Return the sorted list of ``SKILL.md`` files under the given roots."""
    files: list[Path] = []
    for root in roots:
        base = (project_root / root).resolve()
        if not base.is_dir():
            continue
        files.extend(base.rglob("SKILL.md"))
    # Deduplicate and sort for deterministic output.
    return sorted(set(files))


def run(
    roots: list[str],
    run_id: str,
    generated_at: str,
    project_root: Path,
) -> Report:
    """Scan all skill files under ``roots`` and build a :class:`Report`.

    Read-only: skill files are opened for reading only; no DB is touched.
    """
    files = discover_skill_files(roots, project_root)
    findings: list[Finding] = []
    for file in files:
        text = file.read_text(encoding="utf-8", errors="replace")
        rel = file.relative_to(project_root).as_posix()
        findings.extend(scan_text(text, rel))

    by_type = {ftype: sum(1 for f in findings if f.finding_type == ftype) for ftype in FINDING_TYPES}
    return Report(
        run_id=run_id,
        generated_at=generated_at,
        skill_roots=list(roots),
        skills_scanned=len(files),
        findings=findings,
        findings_by_type=by_type,
    )


def exit_code_for(report: Report, warn_only: bool) -> int:
    """Return the process exit code for a report.

    ``0`` when there are no findings or ``warn_only`` is set (advisory phase);
    ``1`` when findings are present and ``warn_only`` is False.
    """
    if warn_only or not report.findings:
        return 0
    return 1


def render_summary(report: Report) -> str:
    """Render the human-readable markdown summary for a report."""
    lines = [
        "# Skill-Health Checker Summary",
        "",
        f"- run_id: {report.run_id}",
        f"- generated_at: {report.generated_at}",
        f"- skills_scanned: {report.skills_scanned}",
        f"- finding_count: {len(report.findings)}",
        "",
        "## Findings by type",
        "",
    ]
    for ftype in FINDING_TYPES:
        lines.append(f"- {ftype}: {report.findings_by_type.get(ftype, 0)}")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    if not report.findings:
        lines.append("_No findings._")
    else:
        for f in report.findings:
            lines.append(f"- `{f.skill_path}`:{f.line} [{f.finding_type}] {f.snippet}")
    lines.append("")
    return "\n".join(lines)


def _default_run_id() -> str:
    return datetime.now(UTC).strftime("run-%Y%m%dT%H%M%SZ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GT-KB skill-health static checker (read-only).")
    parser.add_argument(
        "--skills-root",
        action="append",
        dest="skill_roots",
        help="Skill root to scan (repeatable). Defaults to the shared authored .agents/skills.",
    )
    parser.add_argument("--run-id", default=None, help="Run label included in the report.")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root (defaults to the parent of scripts/).",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Advisory mode: report findings but always exit 0.",
    )
    parser.add_argument("--json", action="store_true", help="Print the JSON report to stdout.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    roots = args.skill_roots or list(DEFAULT_SKILL_ROOTS)
    run_id = args.run_id or _default_run_id()
    generated_at = datetime.now(UTC).isoformat()

    report = run(roots, run_id, generated_at, project_root)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_summary(report))

    return exit_code_for(report, args.warn_only)


if __name__ == "__main__":
    raise SystemExit(main())
