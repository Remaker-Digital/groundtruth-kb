#!/usr/bin/env python3
"""Advisory Grilling Gate Lint (Slice 3, WI-3446).

Deterministic, warning-phase lint implementing the machine-checkable contract in
``DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`` for the LO Advisory Owner-Grilling
Gate principle (``GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001``).

It scans Loyal Opposition advisory reports under
``independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`` and, for
advisories whose recommended disposition is ``adopt`` or ``adapt``, warns when
the mandatory ``## Required Prime Builder Owner-Grilling Gate`` section is
missing or structurally under-specified.

Phase 1 (this slice) is WARNING-ONLY and FAIL-OPEN: the lint never blocks a
write or a turn. Phase 2 (blocking) is intentionally out of scope and requires a
separate owner-approved bridge per the DCL's two-phase enforcement progression.

Detection contract (all three required for advisory shape):
  1. File name matches ``INSIGHTS-*.md``.
  2. A ``Mode: advisory report`` line (or ``Mode: advisory``) appears within the
     first 20 lines.
  3. Exactly one of ``adopt``/``adapt``/``reject``/``defer``/``monitor`` is
     declared inside a ``## Classification`` / ``## Recommended Prime Builder
     Disposition`` / ``## Disposition`` section (``##`` or ``###``).

Gate checks (only for ``adopt``/``adapt`` advisories without a waiver):
  - gate-presence: the ``## Required Prime Builder Owner-Grilling Gate`` heading
    must be present (warning if missing).
  - gate-content: that section must contain at least three enumerations
    (numbered, bulleted, or ``###`` named subsections) (warning if fewer).

Waiver path:
  A ``Grilling-gate waiver: <reason>`` line inside the disposition section
  suppresses the warnings and is recorded to
  ``.gtkb-state/advisory-grilling-gate/waivers.jsonl``.

Usage:
    python scripts/advisory_grilling_gate_lint.py [PATHS...]   # lint specific files
    python scripts/advisory_grilling_gate_lint.py              # scan the dropbox
    python scripts/advisory_grilling_gate_lint.py --json       # machine-readable
    python scripts/advisory_grilling_gate_lint.py --stop-hook  # Stop-hook (exit 0)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

DROPBOX_RELATIVE = Path("independent-progress-assessments") / "CODEX-INSIGHT-DROPBOX"
ADVISORY_GLOB = "INSIGHTS-*.md"
WAIVER_LOG_RELATIVE = Path(".gtkb-state") / "advisory-grilling-gate" / "waivers.jsonl"

MODE_HEADER_SCAN_LINES = 20
CLASSIFICATIONS = ("adopt", "adapt", "reject", "defer", "monitor")
GATE_REQUIRING = frozenset({"adopt", "adapt"})
MIN_GATE_ENUMERATIONS = 3

# Advisory-shape: ``Mode: advisory report`` plus the shorter ``Mode: advisory``
# variant, case-insensitive (per the DCL description's normalized variants).
MODE_HEADER_RE = re.compile(r"^Mode:\s*advisory(?:\s+report)?\s*$", re.IGNORECASE)

# Disposition section heading (level 2 or 3).
DISPOSITION_HEADING_RE = re.compile(
    r"^(#{2,3})\s+(?:Classification|Recommended Prime Builder Disposition|Disposition)\s*$",
    re.IGNORECASE,
)

# The mandatory gate heading (level 2, exact text modulo surrounding whitespace).
GATE_HEADING_RE = re.compile(r"^##\s+Required Prime Builder Owner-Grilling Gate\s*$")

# Any markdown ATX heading, capturing its level via the leading ``#`` run.
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")

# Gate-content enumeration: numbered item, bullet, or ``###`` named subsection.
ENUMERATION_RE = re.compile(r"^(?:\d+\.\s|[-*]\s|###\s)")

# Waiver line inside the disposition section.
WAIVER_RE = re.compile(r"^Grilling-gate waiver:\s*(\S.*?)\s*$", re.IGNORECASE)

# Classification token inside the disposition section.
CLASSIFICATION_TOKEN_RE = re.compile(r"\b(" + "|".join(CLASSIFICATIONS) + r")\b", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    """A single warning-phase lint finding."""

    file: str
    code: str
    message: str
    level: str = "warning"


@dataclass
class FileResult:
    """The lint outcome for one file."""

    rel: str
    shaped: bool = False
    classification: str | None = None
    waiver: str | None = None
    findings: list[Finding] = field(default_factory=list)


def _heading_level(line: str) -> int | None:
    match = HEADING_RE.match(line)
    return len(match.group(1)) if match else None


def _section_body(lines: list[str], start_index: int, heading_level: int) -> list[str]:
    """Return the lines of a section that begins at ``start_index``.

    The section runs from the line after its heading until the next heading whose
    level is less than or equal to ``heading_level`` (deeper ``###`` subsections
    stay inside the section), or end of file.
    """
    body: list[str] = []
    for line in lines[start_index + 1 :]:
        level = _heading_level(line)
        if level is not None and level <= heading_level:
            break
        body.append(line)
    return body


def _disposition_section(lines: list[str]) -> list[str] | None:
    for index, line in enumerate(lines):
        match = DISPOSITION_HEADING_RE.match(line)
        if match:
            return _section_body(lines, index, len(match.group(1)))
    return None


def has_mode_header(text: str) -> bool:
    """Return True when a ``Mode: advisory[ report]`` line is in the first lines."""
    return any(MODE_HEADER_RE.match(line.strip()) for line in text.splitlines()[:MODE_HEADER_SCAN_LINES])


def extract_classification(text: str) -> str | None:
    """Return the single disposition token, or None when absent or ambiguous.

    Per the contract, the classification must declare *exactly one* of the five
    tokens inside the disposition section. Zero or multiple distinct tokens make
    the file not advisory-shaped for gate purposes.
    """
    body = _disposition_section(text.splitlines())
    if body is None:
        return None
    # A free-text waiver reason must not pollute classification detection, so the
    # waiver line is excluded from token scanning.
    tokens = {
        match.group(1).lower()
        for line in body
        if not WAIVER_RE.match(line.strip())
        for match in CLASSIFICATION_TOKEN_RE.finditer(line)
    }
    if len(tokens) == 1:
        return next(iter(tokens))
    return None


def extract_waiver(text: str) -> str | None:
    """Return the waiver reason declared inside the disposition section, if any."""
    body = _disposition_section(text.splitlines())
    if body is None:
        return None
    for line in body:
        match = WAIVER_RE.match(line.strip())
        if match:
            return match.group(1).strip()
    return None


def has_gate_heading(text: str) -> bool:
    return any(GATE_HEADING_RE.match(line) for line in text.splitlines())


def count_gate_enumerations(text: str) -> int:
    """Count enumerations inside the owner-grilling-gate section."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if GATE_HEADING_RE.match(line):
            body = _section_body(lines, index, heading_level=2)
            return sum(1 for body_line in body if ENUMERATION_RE.match(body_line))
    return 0


def is_advisory_shaped(text: str, *, file_name: str) -> bool:
    """Return True when all three advisory-shape conditions hold."""
    if not fnmatch.fnmatch(file_name, ADVISORY_GLOB):
        return False
    if not has_mode_header(text):
        return False
    return extract_classification(text) is not None


def lint_text(text: str, *, rel: str) -> FileResult:
    """Lint advisory text. Pure (no filesystem); the core of the contract."""
    file_name = Path(rel).name
    result = FileResult(rel=rel)
    if not is_advisory_shaped(text, file_name=file_name):
        return result

    result.shaped = True
    result.classification = extract_classification(text)
    result.waiver = extract_waiver(text)

    if result.classification not in GATE_REQUIRING:
        # reject / defer / monitor: gate not required at this stage.
        return result
    if result.waiver:
        # An explicit waiver suppresses the gate warnings (and is logged).
        return result

    if not has_gate_heading(text):
        result.findings.append(
            Finding(
                file=rel,
                code="gate_missing",
                message=(
                    "adopt/adapt advisory is missing the required "
                    "'## Required Prime Builder Owner-Grilling Gate' section."
                ),
            )
        )
        return result

    enumerations = count_gate_enumerations(text)
    if enumerations < MIN_GATE_ENUMERATIONS:
        result.findings.append(
            Finding(
                file=rel,
                code="gate_content_insufficient",
                message=(
                    f"owner-grilling-gate section has {enumerations} enumeration(s); "
                    f"at least {MIN_GATE_ENUMERATIONS} are required (implementation "
                    f"implied, grill-the-owner questions, required durable owner "
                    f"decisions)."
                ),
            )
        )
    return result


def _relpath(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def lint_file(path: Path, *, project_root: Path) -> FileResult:
    """Lint a single file path. Fail-open: unreadable files yield an empty result."""
    rel = _relpath(path, project_root)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return FileResult(rel=rel)
    return lint_text(text, rel=rel)


def discover_advisory_files(project_root: Path) -> list[Path]:
    dropbox = project_root / DROPBOX_RELATIVE
    if not dropbox.is_dir():
        return []
    return sorted(dropbox.glob(ADVISORY_GLOB))


def log_waiver(result: FileResult, *, project_root: Path, now: datetime | None = None) -> None:
    """Append a waiver observation to the waiver ledger (append-only JSONL)."""
    if not result.waiver:
        return
    log_path = project_root / WAIVER_LOG_RELATIVE
    record = {
        "observed_at": (now or datetime.now(UTC)).isoformat(),
        "file": result.rel,
        "classification": result.classification,
        "reason": result.waiver,
    }
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        # Warning-phase machinery must never block on a logging failure.
        pass


def lint_paths(paths: list[Path], *, project_root: Path, record_waivers: bool = True) -> list[FileResult]:
    results = [lint_file(path, project_root=project_root) for path in paths]
    if record_waivers:
        for result in results:
            if result.waiver:
                log_waiver(result, project_root=project_root)
    return results


def _resolve_project_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    env = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("GTKB_PROJECT_ROOT")
    return Path(env).resolve() if env else Path.cwd()


def _run_stop_hook(project_root: Path) -> int:
    """Stop-hook mode: scan, surface warnings to stderr, never block. Fail-open."""
    try:
        sys.stdin.read()
    except Exception:  # noqa: BLE001 - stdin is best-effort; never block the turn.
        pass
    try:
        results = lint_paths(discover_advisory_files(project_root), project_root=project_root)
        for finding in (f for result in results for f in result.findings):
            sys.stderr.write(f"[advisory-grilling-gate][WARNING] {finding.code}: {finding.file} - {finding.message}\n")
    except Exception:  # noqa: BLE001 - Phase 1 is fail-open; warnings never block.
        pass
    sys.stdout.write(json.dumps({}))
    return 0


def _print_human(results: list[FileResult]) -> None:
    findings = [f for result in results for f in result.findings]
    shaped = [result for result in results if result.shaped]
    waived = [result for result in results if result.waiver]
    for finding in findings:
        sys.stderr.write(f"[WARNING] {finding.code}: {finding.file} - {finding.message}\n")
    summary = (
        f"advisory-grilling-gate lint: {len(shaped)} advisory file(s), "
        f"{len(findings)} warning(s), {len(waived)} waiver(s). "
        f"Phase 1 (warning-only); no writes blocked."
    )
    print(summary)


def _results_to_json(results: list[FileResult]) -> dict[str, object]:
    return {
        "phase": "warning",
        "advisory_files": sum(1 for result in results if result.shaped),
        "warnings": sum(len(result.findings) for result in results),
        "waivers": sum(1 for result in results if result.waiver),
        "findings": [
            {
                "file": finding.file,
                "level": finding.level,
                "code": finding.code,
                "message": finding.message,
            }
            for result in results
            for finding in result.findings
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Advisory files to lint (default: scan the dropbox).")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable findings.")
    parser.add_argument(
        "--stop-hook",
        action="store_true",
        help="Stop-hook mode: read+discard stdin, emit {}, exit 0 (fail-open).",
    )
    args = parser.parse_args(argv)

    project_root = _resolve_project_root(args.project_root)

    if args.stop_hook:
        return _run_stop_hook(project_root)

    paths = [Path(p) for p in args.paths] if args.paths else discover_advisory_files(project_root)
    results = lint_paths(paths, project_root=project_root)

    if args.json:
        print(json.dumps(_results_to_json(results), indent=2, sort_keys=True))
    else:
        _print_human(results)

    # Phase 1 is warning-only and fail-open: never signal a non-zero (blocking)
    # exit, regardless of how many warnings were emitted.
    return 0


if __name__ == "__main__":
    sys.exit(main())
