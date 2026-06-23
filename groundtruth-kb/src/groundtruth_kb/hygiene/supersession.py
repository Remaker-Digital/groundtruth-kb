"""Read-only supersession hygiene scanner.

Detects live working-directory files that advertise supersession, retirement,
withdrawal, or obsolescence signals while preserving audit-history locations by
default. Findings are advisory only; this module never deletes, moves, rewrites,
or mutates MemBase/formal artifacts.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import fnmatch
import json
import re
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_MAX_MATCH_EXCERPT_LEN = 200
_MAX_TEXT_FILE_BYTES = 2_000_000

_TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

_DEFAULT_EXCLUSION_GLOBS = (
    ".git/**",
    ".gtkb-state/**",
    ".mypy_cache/**",
    ".pytest_cache/**",
    ".ruff_cache/**",
    ".venv/**",
    "**/.git/**",
    "**/.gtkb-state/**",
    "**/.mypy_cache/**",
    "**/.pytest_cache/**",
    "**/.ruff_cache/**",
    "**/.venv/**",
    "**/__pycache__/**",
    "**/node_modules/**",
    "__pycache__/**",
    "archive/**",
    ".claude/worktrees/**",
    "independent-progress-assessments/archive/**",
    "memory/archive/**",
    "platform_tests/pytest*/**",
    "pytest*/**",
)

_AUDIT_HISTORY_GLOBS = (
    "bridge/*-[0-9][0-9][0-9].md",
    ".groundtruth/formal-artifact-approvals/**",
    ".groundtruth/narrative-artifact-approvals/**",
    "applications/*/docs/archive/**",
    "harness-state/*/session-envelope-archive/**",
)


@dataclass(frozen=True)
class SupersessionMarker:
    """One built-in lifecycle-state signal pattern."""

    id: str
    marker_class: str
    pattern: str
    classification: str
    remediation_hint: str
    _compiled_pattern: re.Pattern[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_compiled_pattern", re.compile(self.pattern, re.IGNORECASE))


@dataclass(frozen=True)
class SupersessionFinding:
    """One supersession hygiene finding against a live file."""

    marker_id: str
    marker_class: str
    classification: str
    file: str
    line: int
    matched_excerpt: str
    remediation_hint: str


@dataclass(frozen=True)
class SupersessionScanResult:
    """Aggregate output of one supersession scan invocation."""

    run_id: str
    generated_at: str
    root: str
    files_scanned: int
    findings: tuple[SupersessionFinding, ...]
    audit_history_preserved: bool = True

    @property
    def finding_count(self) -> int:
        return len(self.findings)


DEFAULT_MARKERS: tuple[SupersessionMarker, ...] = (
    SupersessionMarker(
        id="superseded-by",
        marker_class="supersession",
        pattern=r"\b(?:superseded\s+by|replaced\s+by|obsoleted\s+by)\b",
        classification="candidate_live_supersession_signal",
        remediation_hint=(
            "Confirm the live authority. If this artifact is no longer authoritative, use the governed "
            "cleanup/retirement path instead of following the stale clue."
        ),
    ),
    SupersessionMarker(
        id="retired-artifact",
        marker_class="retirement",
        pattern=r"\b(?:retired|retirement|deprecated)\b",
        classification="candidate_live_retirement_signal",
        remediation_hint=(
            "Confirm whether the file is historical or live. Preserve audit history, and only move or retire "
            "live artifacts through an approved follow-up action."
        ),
    ),
    SupersessionMarker(
        id="withdrawn-artifact",
        marker_class="withdrawal",
        pattern=r"\b(?:withdrawn|withdrawal)\b",
        classification="candidate_live_withdrawal_signal",
        remediation_hint=(
            "Check whether the withdrawn artifact remains in a live decision path. Preserve the evidence trail "
            "and route any cleanup through governance."
        ),
    ),
    SupersessionMarker(
        id="obsolete-artifact",
        marker_class="obsolescence",
        pattern=r"\b(?:obsolete|obsoleted|legacy-only|no\s+longer\s+authoritative)\b",
        classification="candidate_live_obsolescence_signal",
        remediation_hint=(
            "Treat this as an advisory candidate only. Verify the replacement authority before changing any "
            "artifact lifecycle state."
        ),
    ),
)


def _matches_any(rel_path: str, globs: Iterable[str]) -> bool:
    normalized = rel_path.replace("\\", "/")
    return any(fnmatch.fnmatchcase(normalized, pattern) for pattern in globs)


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in _TEXT_SUFFIXES


def _is_excluded(rel_path: str, *, preserve_audit_history: bool) -> bool:
    if _matches_any(rel_path, _DEFAULT_EXCLUSION_GLOBS):
        return True
    return preserve_audit_history and _matches_any(rel_path, _AUDIT_HISTORY_GLOBS)


def walk_live_files(root: Path, *, preserve_audit_history: bool = True) -> Iterator[Path]:
    """Yield text-like live files under ``root`` while pruning history/cache paths."""
    root = root.resolve()

    def walk(directory: Path) -> Iterator[Path]:
        try:
            entries = sorted(directory.iterdir())
        except (PermissionError, OSError):
            return
        for entry in entries:
            rel = _relative_path(entry, root)
            if entry.is_dir():
                if _is_excluded(rel + "/", preserve_audit_history=preserve_audit_history) or _is_excluded(
                    rel, preserve_audit_history=preserve_audit_history
                ):
                    continue
                yield from walk(entry)
            elif entry.is_file() and _is_text_candidate(entry):
                if _is_excluded(rel, preserve_audit_history=preserve_audit_history):
                    continue
                try:
                    if entry.stat().st_size > _MAX_TEXT_FILE_BYTES:
                        continue
                except OSError:
                    continue
                yield entry

    yield from walk(root)


def scan_supersession_file(
    path: Path,
    root: Path,
    markers: Iterable[SupersessionMarker] = DEFAULT_MARKERS,
) -> list[SupersessionFinding]:
    """Scan one file for supersession markers and return advisory findings."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (PermissionError, OSError):
        return []

    rel = _relative_path(path, root)
    findings: list[SupersessionFinding] = []
    marker_tuple = tuple(markers)
    for line_idx, line_text in enumerate(text.splitlines(), start=1):
        for marker in marker_tuple:
            if marker._compiled_pattern.search(line_text) is None:
                continue
            excerpt = line_text.strip()
            if len(excerpt) > _MAX_MATCH_EXCERPT_LEN:
                excerpt = excerpt[: _MAX_MATCH_EXCERPT_LEN - 3] + "..."
            findings.append(
                SupersessionFinding(
                    marker_id=marker.id,
                    marker_class=marker.marker_class,
                    classification=marker.classification,
                    file=rel,
                    line=line_idx,
                    matched_excerpt=excerpt,
                    remediation_hint=marker.remediation_hint,
                )
            )
    return findings


def run_supersession_scan(
    root: Path,
    *,
    preserve_audit_history: bool = True,
    markers: Iterable[SupersessionMarker] = DEFAULT_MARKERS,
) -> SupersessionScanResult:
    """Walk ``root`` and return advisory supersession hygiene findings."""
    root = root.resolve()
    marker_tuple = tuple(markers)
    files_scanned = 0
    findings: list[SupersessionFinding] = []
    for file_path in walk_live_files(root, preserve_audit_history=preserve_audit_history):
        files_scanned += 1
        findings.extend(scan_supersession_file(file_path, root, marker_tuple))
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return SupersessionScanResult(
        run_id=run_id,
        generated_at=generated_at,
        root=str(root),
        files_scanned=files_scanned,
        findings=tuple(sorted(findings, key=lambda f: (f.file, f.line, f.marker_id))),
        audit_history_preserved=preserve_audit_history,
    )


def emit_supersession_json(result: SupersessionScanResult, out_path: Path) -> None:
    """Write ``result`` as structured JSON to ``out_path``."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_id": result.run_id,
        "generated_at": result.generated_at,
        "root": result.root,
        "files_scanned": result.files_scanned,
        "finding_count": result.finding_count,
        "audit_history_preserved": result.audit_history_preserved,
        "findings": [asdict(f) for f in result.findings],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def emit_supersession_markdown(result: SupersessionScanResult, out_path: Path) -> None:
    """Write ``result`` as a human-readable markdown summary to ``out_path``."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Supersession Hygiene Summary",
        "",
        f"- Generated: {result.generated_at}",
        f"- Run id: {result.run_id}",
        f"- Root: {result.root}",
        f"- Files scanned: {result.files_scanned}",
        f"- Findings: {result.finding_count}",
        f"- Audit history preserved: {result.audit_history_preserved}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
    else:
        by_class: dict[str, list[SupersessionFinding]] = {}
        for finding in result.findings:
            by_class.setdefault(finding.marker_class, []).append(finding)
        for marker_class in sorted(by_class):
            class_findings = by_class[marker_class]
            lines.append(f"## {marker_class} ({len(class_findings)})")
            lines.append("")
            for finding in class_findings:
                lines.append(
                    f"- `{finding.file}:{finding.line}` "
                    f"({finding.classification}, marker `{finding.marker_id}`): "
                    f"`{finding.matched_excerpt}`"
                )
                lines.append(f"  - Remediation: {finding.remediation_hint}")
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
