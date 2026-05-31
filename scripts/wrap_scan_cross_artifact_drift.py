"""Report-only cross-artifact content drift scanner for session wrap-up.

Per bridge/gtkb-wrapup-enhancements-next-slice-003.md (GO at -004).
This scanner composes with, and does not replace,
``scripts/wrap_scan_consistency.py``. The existing W2/S2 scanner checks
reference integrity; this scanner checks semantic content drift across the
artifacts touched during a session.

EXIT CODES:
    0  Always. Findings are informational/report-only by design.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from _wrap_io import _atomic_write_text

SCANNER_ID = "wrap_scan_cross_artifact_drift"
SEVERITY_INFORMATIONAL = "informational"
EXIT_OK = 0

DEFAULT_SNAPSHOT_ROOT = ".groundtruth/session/snapshots"
STATUS_WORDS = frozenset(
    {
        "accepted",
        "active",
        "blocked",
        "closed",
        "completed",
        "created",
        "deferred",
        "done",
        "implemented",
        "in_progress",
        "open",
        "rejected",
        "retired",
        "specified",
        "superseded",
        "verified",
    }
)

SPEC_ID_RE = re.compile(r"\b(?:ADR|APP|DCL|DOC|GOV|OM|PB|SPEC)-[A-Z0-9][A-Z0-9_.-]*\b")
DELIB_ID_RE = re.compile(r"\bDELIB-[A-Z0-9][A-Z0-9_.-]*\b")
SESSION_RE = re.compile(r"^Session:\s*(?P<session>\S+)", re.MULTILINE)
TARGET_PATHS_RE = re.compile(r"target_paths:\s*(?P<paths>\[[^\n]+\])")


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _finding(check: str, message: str, **details: Any) -> dict[str, Any]:
    return {
        "check": check,
        "severity": SEVERITY_INFORMATIONAL,
        "report_only": True,
        "message": message,
        **details,
    }


def _default_session_id() -> str | None:
    for env_name in ("GTKB_SESSION_ID", "CODEX_SESSION_ID", "CLAUDE_SESSION_ID"):
        value = os.environ.get(env_name)
        if value:
            return value
    return None


def _connect_readonly(db_path: Path) -> sqlite3.Connection | None:
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name = ? AND type IN ('table', 'view')",
        (name,),
    ).fetchone()
    return row is not None


def _read_current_rows(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    if not _table_exists(conn, table):
        return []
    return list(conn.execute(f"SELECT * FROM {table}"))


def _row_text(row: sqlite3.Row, fields: Iterable[str]) -> str:
    keys = set(row.keys())
    parts: list[str] = []
    for field in fields:
        if field in keys and row[field] is not None:
            parts.append(str(row[field]))
    return "\n".join(parts)


def _session_matches(row: sqlite3.Row, session_id: str | None) -> bool:
    if not session_id:
        return True
    keys = set(row.keys())
    return "session_id" not in keys or row["session_id"] == session_id


def _extract_status_claim(text: str, artifact_id: str) -> str | None:
    for match in re.finditer(re.escape(artifact_id), text):
        window = text[match.start() : match.end() + 160]
        explicit = re.search(
            r"(?:status|resolution_status|stage)\s*[:=]\s*[`'\"]?"
            r"(?P<status>[A-Za-z_ -]+)[`'\"]?",
            window,
            flags=re.IGNORECASE,
        )
        if explicit:
            return explicit.group("status").strip().lower().replace(" ", "_")
        for status in STATUS_WORDS:
            if re.search(rf"\b{re.escape(status)}\b", window, flags=re.IGNORECASE):
                return status
    return None


def check_spec_delib_content_drift(
    project_root: Path,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """Flag session deliberations whose claimed spec status differs from MemBase."""
    conn = _connect_readonly(project_root / "groundtruth.db")
    if conn is None:
        return []
    try:
        specs = {}
        for row in _read_current_rows(conn, "current_specifications"):
            keys = set(row.keys())
            if {"id", "status"}.issubset(keys):
                specs[row["id"]] = str(row["status"]).lower()
        findings: list[dict[str, Any]] = []
        for row in _read_current_rows(conn, "current_deliberations"):
            if not _session_matches(row, session_id):
                continue
            text = _row_text(row, ("title", "summary", "content", "outcome"))
            for spec_id in sorted(set(SPEC_ID_RE.findall(text)) & specs.keys()):
                claimed = _extract_status_claim(text, spec_id)
                actual = specs[spec_id]
                if claimed and claimed != actual:
                    findings.append(
                        _finding(
                            "spec_delib_content_drift",
                            f"Deliberation {row['id']} claims {spec_id} status {claimed}, but MemBase current status is {actual}.",
                            deliberation_id=row["id"],
                            spec_id=spec_id,
                            claimed_status=claimed,
                            actual_status=actual,
                        )
                    )
        return findings
    finally:
        conn.close()


def _parse_target_paths(text: str) -> list[str]:
    match = TARGET_PATHS_RE.search(text)
    if not match:
        return []
    raw = match.group("paths")
    try:
        parsed = ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item).replace("\\", "/") for item in parsed if isinstance(item, str) and item]


def _bridge_file_session(text: str) -> str | None:
    match = SESSION_RE.search(text)
    if not match:
        return None
    return match.group("session").strip()


def _session_bridge_target_paths(project_root: Path, session_id: str | None) -> tuple[list[str], list[str]]:
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return [], []
    target_paths: list[str] = []
    documents: list[str] = []
    for path in bridge_dir.glob("*.md"):
        if path.name == "INDEX.md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if session_id and _bridge_file_session(text) != session_id:
            continue
        paths = _parse_target_paths(text)
        if not paths:
            continue
        target_paths.extend(paths)
        documents.append(f"bridge/{path.name}")
    return sorted(set(target_paths)), sorted(set(documents))


def _load_manifest_changed_paths(project_root: Path, session_id: str | None) -> list[str]:
    if not session_id:
        return []
    manifest_path = project_root / DEFAULT_SNAPSHOT_ROOT / session_id / "manifest.json"
    if not manifest_path.exists():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    changed: list[str] = []
    for key in ("uncommitted_paths", "untracked_paths"):
        values = manifest.get(key, [])
        if isinstance(values, list):
            changed.extend(str(item).replace("\\", "/") for item in values if item)
    return sorted(set(changed))


def _git_changed_paths(project_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line or len(line) < 4:
            continue
        paths.append(line[3:].replace("\\", "/"))
    return sorted(set(paths))


def _target_covers_path(target: str, actual: str) -> bool:
    normalized_target = target.replace("\\", "/").strip().rstrip("/")
    normalized_actual = actual.replace("\\", "/").strip()
    if normalized_target == normalized_actual:
        return True
    if normalized_actual.startswith(f"{normalized_target}/"):
        return True
    if "*" in normalized_target or "?" in normalized_target:
        from fnmatch import fnmatch

        return fnmatch(normalized_actual, normalized_target)
    return False


def check_bridge_target_paths_vs_actual_changes(
    project_root: Path,
    session_id: str | None = None,
    changed_paths: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Flag changed paths not covered by session bridge proposal target_paths."""
    target_paths, documents = _session_bridge_target_paths(project_root, session_id)
    if not target_paths:
        return []
    actual_paths = changed_paths
    if actual_paths is None:
        actual_paths = _load_manifest_changed_paths(project_root, session_id) or _git_changed_paths(project_root)
    findings: list[dict[str, Any]] = []
    for actual in sorted(set(path.replace("\\", "/") for path in actual_paths)):
        if actual.startswith(".groundtruth/session/snapshots/"):
            continue
        if any(_target_covers_path(target, actual) for target in target_paths):
            continue
        findings.append(
            _finding(
                "bridge_target_paths_actual_change_gap",
                f"Changed path {actual} is not covered by any session bridge target_paths entry.",
                path=actual,
                session_id=session_id,
                session_bridge_documents=documents,
                target_paths=target_paths,
            )
        )
    return findings


def _session_work_item_ids(conn: sqlite3.Connection, session_id: str | None) -> set[str]:
    ids: set[str] = set()
    for row in _read_current_rows(conn, "current_deliberations"):
        if not _session_matches(row, session_id):
            continue
        keys = set(row.keys())
        if "work_item_id" in keys and row["work_item_id"]:
            ids.add(str(row["work_item_id"]))
        text = _row_text(row, ("title", "summary", "content", "outcome"))
        ids.update(re.findall(r"\b(?:WI|GTKB|PROJECT)-[A-Z0-9][A-Z0-9_.-]*\b", text))
    return ids


def _memory_texts(project_root: Path) -> list[tuple[str, str]]:
    memory_dir = project_root / "memory"
    if not memory_dir.is_dir():
        return []
    texts: list[tuple[str, str]] = []
    for path in memory_dir.glob("*.md"):
        try:
            texts.append((str(path.relative_to(project_root)).replace("\\", "/"), path.read_text(encoding="utf-8")))
        except OSError:
            continue
    return texts


def check_wi_status_membase_vs_memory(
    project_root: Path,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """Flag memory/*.md work-item status claims that disagree with MemBase."""
    conn = _connect_readonly(project_root / "groundtruth.db")
    if conn is None:
        return []
    try:
        candidate_ids = _session_work_item_ids(conn, session_id)
        if session_id and not candidate_ids:
            return []
        rows = _read_current_rows(conn, "current_work_items")
        if candidate_ids:
            rows = [row for row in rows if row["id"] in candidate_ids]
        findings: list[dict[str, Any]] = []
        texts = _memory_texts(project_root)
        for row in rows:
            keys = set(row.keys())
            if "id" not in keys or "resolution_status" not in keys:
                continue
            work_item_id = str(row["id"])
            actual_status = str(row["resolution_status"]).lower()
            for source, text in texts:
                if work_item_id not in text:
                    continue
                claimed = _extract_status_claim(text, work_item_id)
                if claimed and claimed != actual_status:
                    findings.append(
                        _finding(
                            "wi_status_membase_memory_drift",
                            f"{source} claims {work_item_id} status {claimed}, but MemBase current resolution_status is {actual_status}.",
                            source=source,
                            work_item_id=work_item_id,
                            claimed_status=claimed,
                            actual_status=actual_status,
                        )
                    )
        return findings
    finally:
        conn.close()


def check_cross_delib_references(
    project_root: Path,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """Flag DELIB references that are missing or retired."""
    conn = _connect_readonly(project_root / "groundtruth.db")
    if conn is None:
        return []
    try:
        deliberations = _read_current_rows(conn, "current_deliberations")
        by_id = {row["id"]: row for row in deliberations if "id" in set(row.keys())}
        findings: list[dict[str, Any]] = []
        for row in deliberations:
            if not _session_matches(row, session_id):
                continue
            source_id = str(row["id"])
            text = _row_text(row, ("title", "summary", "content", "outcome"))
            for cited_id in sorted(set(DELIB_ID_RE.findall(text)) - {source_id}):
                cited = by_id.get(cited_id)
                if cited is None:
                    findings.append(
                        _finding(
                            "cross_delib_reference_missing",
                            f"Deliberation {source_id} cites missing deliberation {cited_id}.",
                            deliberation_id=source_id,
                            cited_deliberation_id=cited_id,
                        )
                    )
                    continue
                cited_keys = set(cited.keys())
                outcome = str(cited["outcome"]).lower() if "outcome" in cited_keys and cited["outcome"] else ""
                if outcome in {"retired", "superseded"}:
                    findings.append(
                        _finding(
                            "cross_delib_reference_retired",
                            f"Deliberation {source_id} cites {outcome} deliberation {cited_id}.",
                            deliberation_id=source_id,
                            cited_deliberation_id=cited_id,
                            cited_outcome=outcome,
                        )
                    )
        return findings
    finally:
        conn.close()


CHECKS = (
    check_spec_delib_content_drift,
    check_bridge_target_paths_vs_actual_changes,
    check_wi_status_membase_vs_memory,
    check_cross_delib_references,
)


def run_all_checks(project_root: Path, session_id: str | None = None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for check in CHECKS:
        findings.extend(check(project_root, session_id=session_id))
    return findings


def build_report(findings: list[dict[str, Any]], session_id: str | None = None) -> dict[str, Any]:
    return {
        "scanner_id": SCANNER_ID,
        "session_id": session_id,
        "report_only": True,
        "severity_model": SEVERITY_INFORMATIONAL,
        "count": len(findings),
        "findings": findings,
    }


def render_markdown(findings: list[dict[str, Any]], session_id: str | None = None) -> str:
    report = build_report(findings, session_id=session_id)
    lines = ["# Cross-Artifact Drift Scan", ""]
    if session_id:
        lines.extend([f"Session: `{session_id}`", ""])
    lines.extend(
        [
            f"Scanner: `{SCANNER_ID}`",
            "Severity model: report-only informational findings.",
            "",
        ]
    )
    if not findings:
        lines.extend(["No findings. No cross-artifact content drift detected.", ""])
    else:
        lines.extend([f"## INFORMATIONAL ({len(findings)})", ""])
        for finding in findings:
            lines.append(f"- **{finding['check']}**: {finding['message']}")
        lines.append("")
    lines.extend(["## JSON", "", "```json", json.dumps(report, indent=2), "```", ""])
    return "\n".join(lines)


def determine_exit_code(findings: list[dict[str, Any]]) -> int:
    """Report-only scanner: findings never block wrap-up or CI."""
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--session-id", default=None, help="Session identifier to scan")
    parser.add_argument(
        "--report-format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("--write-report", default=None, help="Write report to this path (atomic)")
    args = parser.parse_args(argv)

    session_id = args.session_id or _default_session_id()
    project_root = _project_root()
    findings = run_all_checks(project_root, session_id=session_id)
    report = build_report(findings, session_id=session_id)

    if args.report_format == "markdown":
        output = render_markdown(findings, session_id=session_id)
    else:
        output = json.dumps(report, indent=2) + "\n"

    if args.write_report:
        _atomic_write_text(Path(args.write_report), output)
    else:
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")

    return determine_exit_code(findings)


if __name__ == "__main__":
    sys.exit(main())
