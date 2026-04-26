"""W1 of GTKB-WRAPUP-ENHANCEMENTS Slice 1: S5 hygiene scanner.

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006).
Detects drift classes that have recurred across S294, S304, S307, S308:

    git_uncommitted_paths            (S304 layered drift)
    git_untracked_in_tracked_dirs    (S294 blanket-ignore class)
    bridge_files_not_in_index        (S308 dangling -016/-017 class)
    pyc_without_source               (S308 stale parallel-checkout artifacts)
    tmp_artifacts_in_repo            (S305 .tmp.driveupload precedent)
    hardcoded_old_project_root       (S307 feedback_no_hardcoded_paths)
    snapshots_non_manifest           (defense-in-depth for W0 manifest-only scope)

EXIT CODES (Slice 1 simple contract per -005 §3):
    0  Clean, info-only, OR warn findings present (advisory; do not block CI)
    2  At least one error-severity finding present (blocks CI)

Severity is reported in JSON output. The exit code distinguishes only the
pass/fail boundary, matching standard linter convention (ruff, mypy).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wrap_io import _atomic_write_text  # noqa: E402


SEVERITY_INFO = "info"
SEVERITY_WARN = "warn"
SEVERITY_ERROR = "error"

EXIT_OK = 0
EXIT_ERROR = 2

OLD_PROJECT_ROOT_PATTERNS = (
    r"E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
    r"E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement",
)

# Files to scan for hardcoded-old-root references. Source-only; skip binaries/large.
SCAN_GLOBS = ("**/*.py", "**/*.md", "**/*.json", "**/*.toml", "**/*.yaml", "**/*.yml")
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"}

TMP_ARTIFACT_AGE_SECONDS = 24 * 60 * 60  # 24 hours
TMP_ARTIFACT_SUFFIXES = (".tmp", ".bak", ".orig")
TMP_ARTIFACT_NAMES = (".tmp.driveupload",)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _finding(check: str, severity: str, message: str, **details: Any) -> dict:
    return {"check": check, "severity": severity, "message": message, **details}


def _run_git(args: list[str], project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, cwd=project_root, timeout=15
        )
        return result.stdout if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""


def check_git_uncommitted(project_root: Path) -> list[dict]:
    output = _run_git(["status", "--porcelain"], project_root)
    findings: list[dict] = []
    for line in output.splitlines():
        if not line or len(line) < 4:
            continue
        if line.startswith("??"):
            continue
        path = line[3:]
        findings.append(
            _finding(
                "git_uncommitted_paths",
                SEVERITY_WARN,
                f"Uncommitted change in tracked file: {path}",
                path=path,
                git_status=line[:2].strip(),
            )
        )
    return findings


def check_git_untracked_in_tracked_dirs(project_root: Path) -> list[dict]:
    output = _run_git(["ls-files", "--others", "--exclude-standard"], project_root)
    findings: list[dict] = []
    governed_dirs = ("bridge/", "memory/", "scripts/", ".claude/")
    for line in output.splitlines():
        if not line:
            continue
        if any(line.startswith(d) for d in governed_dirs):
            findings.append(
                _finding(
                    "git_untracked_in_tracked_dirs",
                    SEVERITY_WARN,
                    f"Untracked file in governed directory: {line}",
                    path=line,
                )
            )
    return findings


def check_bridge_files_not_in_index(project_root: Path) -> list[dict]:
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
                    "bridge_files_not_in_index",
                    SEVERITY_WARN,
                    f"Bridge file not referenced by INDEX.md: {ref}",
                    path=ref,
                )
            )
    return findings


def check_pyc_without_source(project_root: Path) -> list[dict]:
    findings: list[dict] = []
    for pyc in project_root.rglob("*.pyc"):
        if any(part in SKIP_DIRS for part in pyc.parts):
            pass  # __pycache__ is in SKIP_DIRS, but we want pyc detection across the tree
        # __pycache__/<name>.cpython-<ver>.pyc → ../<name>.py
        parent = pyc.parent
        if parent.name != "__pycache__":
            continue
        stem = pyc.stem.split(".")[0]
        source = parent.parent / f"{stem}.py"
        if not source.exists():
            findings.append(
                _finding(
                    "pyc_without_source",
                    SEVERITY_WARN,
                    f"Bytecode without source: {pyc.relative_to(project_root)} (expected {source.relative_to(project_root)})",
                    pyc=str(pyc.relative_to(project_root)),
                    expected_source=str(source.relative_to(project_root)),
                )
            )
    return findings


def check_tmp_artifacts_in_repo(project_root: Path) -> list[dict]:
    findings: list[dict] = []
    now = time.time()
    for entry in project_root.iterdir():
        if entry.name in TMP_ARTIFACT_NAMES or entry.suffix in TMP_ARTIFACT_SUFFIXES:
            try:
                age = now - entry.stat().st_mtime
            except OSError:
                continue
            if age >= TMP_ARTIFACT_AGE_SECONDS:
                findings.append(
                    _finding(
                        "tmp_artifacts_in_repo",
                        SEVERITY_WARN,
                        f"Stale tmp artifact ({int(age // 3600)}h old): {entry.name}",
                        path=entry.name,
                        age_seconds=int(age),
                    )
                )
    return findings


def check_hardcoded_old_project_root(project_root: Path) -> list[dict]:
    findings: list[dict] = []
    pattern = re.compile("|".join(re.escape(p) for p in OLD_PROJECT_ROOT_PATTERNS))
    for glob in SCAN_GLOBS:
        for path in project_root.glob(glob):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue
            if pattern.search(text):
                findings.append(
                    _finding(
                        "hardcoded_old_project_root",
                        SEVERITY_WARN,
                        f"Reference to old project root: {path.relative_to(project_root)}",
                        path=str(path.relative_to(project_root)),
                    )
                )
    return findings


def check_snapshots_non_manifest(project_root: Path) -> list[dict]:
    """Defense-in-depth for W0 manifest-only scope.

    Per -005 §2 (manifest-only): only manifest.json files should appear under
    .groundtruth/session/snapshots/<session-id>/. Any other file (transcript.jsonl,
    redacted-transcript.txt, etc.) indicates Slice 1 scope was exceeded; flag as
    error so the future WRAPUP-Slice-2A redaction/retention slice is filed first.
    """
    snapshots_root = project_root / ".groundtruth" / "session" / "snapshots"
    if not snapshots_root.exists():
        return []
    findings: list[dict] = []
    for path in snapshots_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name == "manifest.json":
            continue
        rel = path.relative_to(project_root)
        findings.append(
            _finding(
                "snapshots_non_manifest",
                SEVERITY_ERROR,
                f"Non-manifest file under snapshots/ (Slice 1 is manifest-only): {rel}",
                path=str(rel),
            )
        )
    return findings


CHECKS = (
    check_git_uncommitted,
    check_git_untracked_in_tracked_dirs,
    check_bridge_files_not_in_index,
    check_pyc_without_source,
    check_tmp_artifacts_in_repo,
    check_hardcoded_old_project_root,
    check_snapshots_non_manifest,
)


def run_all_checks(project_root: Path) -> list[dict]:
    findings: list[dict] = []
    for check in CHECKS:
        findings.extend(check(project_root))
    return findings


def render_markdown(findings: list[dict]) -> str:
    if not findings:
        return "# Wrap Hygiene Scan\n\nNo findings. Repository state is clean.\n"
    by_severity: dict[str, list[dict]] = {SEVERITY_ERROR: [], SEVERITY_WARN: [], SEVERITY_INFO: []}
    for f in findings:
        by_severity.setdefault(f["severity"], []).append(f)
    lines = ["# Wrap Hygiene Scan", ""]
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
    """Slice 1 simple contract: 0 unless any error-severity finding."""
    if any(f["severity"] == SEVERITY_ERROR for f in findings):
        return EXIT_ERROR
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--report-format", choices=("json", "markdown"), default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--write-report", default=None, help="Write report to this path (atomic)",
    )
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
