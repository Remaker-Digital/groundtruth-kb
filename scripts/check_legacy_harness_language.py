#!/usr/bin/env python3
"""Read-only scanner for legacy harness-role coupling language (WI-4801).

The scanner identifies candidate references that make a specific AI coding
harness name load-bearing where GT-KB should use role-based authority instead.
It is advisory: it exits 0, mutates nothing, and classifies findings for later
bridge proposals to cite.

Source: bridge thread ``gtkb-wi4801-legacy-harness-language-scan``
(Loyal Opposition GO at -002); obsolete-reference purge project authorization
``PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25``.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent

INCLUDED_ROOTS: Final[tuple[Path, ...]] = (
    Path(".claude/rules"),
    Path(".claude/skills"),
    Path(".codex/skills"),
    Path(".cursor/rules"),
    Path("config"),
    Path("scripts"),
    Path("groundtruth-kb/src"),
    Path("platform_tests"),
)
INCLUDED_FILES: Final[frozenset[Path]] = frozenset({Path("AGENTS.md"), Path("CLAUDE.md")})
EXCLUDED_ROOTS: Final[tuple[Path, ...]] = (
    Path("bridge"),
    Path(".claude/worktrees"),
    Path("memory"),
    Path("independent-progress-assessments"),
    Path(".gtkb-state"),
)
EXCLUDED_PARTS: Final[frozenset[str]] = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "node_modules",
        "pytest-tmp",
    }
)
TEXT_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        ".cfg",
        ".css",
        ".html",
        ".ini",
        ".json",
        ".md",
        ".mdc",
        ".py",
        ".ps1",
        ".sh",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)
GENERATED_LINE_MARKERS: Final[tuple[str, ...]] = (
    "Generated: true",
    "DO NOT EDIT",
    "AUTO-GENERATED",
)
GENERATED_SUBSTRING_MARKERS: Final[tuple[str, ...]] = (
    "Do not edit this adapter directly",
    "GTKB-CODEX-SKILL-ADAPTER",
    "GTKB-CURSOR-SKILL-ADAPTER",
)


@dataclass(frozen=True)
class CandidatePattern:
    pattern_id: str
    family: str
    regex: re.Pattern[str]


@dataclass(frozen=True)
class PathClassification:
    classification: str
    reason: str


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    classification: str
    reason: str
    pattern_id: str
    pattern_family: str
    matched_text: str
    line_excerpt: str


CANDIDATE_PATTERNS: Final[tuple[CandidatePattern, ...]] = (
    CandidatePattern(
        "reviewer-harness-term",
        "reviewer_harness_language",
        re.compile(r"\breviewer[-\s]+harness(?:es)?\b", re.IGNORECASE),
    ),
    CandidatePattern(
        "specific-harness-as-reviewer",
        "reviewer_harness_language",
        re.compile(
            r"\b(?:Codex|Claude(?: Code)?|Antigravity|Cursor)\b.{0,80}"
            r"\b(?:reviewer|reviewing harness|loyal opposition)\b",
            re.IGNORECASE,
        ),
    ),
    CandidatePattern(
        "codex-claude-role-pairing",
        "hard_coded_role_pairing",
        re.compile(
            r"\b(?:Codex\s*(?:/|and|&|\+)\s*Claude(?: Code)?|"
            r"Claude(?: Code)?\s*(?:/|and|&|\+)\s*Codex)\b",
            re.IGNORECASE,
        ),
    ),
    CandidatePattern(
        "specific-harness-load-bearing-role",
        "harness_role_coupling",
        re.compile(
            r"\b(?:Codex|Claude(?: Code)?|Antigravity|Cursor)\b.{0,80}"
            r"\b(?:Prime Builder|Loyal Opposition|reviewer|implementer)\b",
            re.IGNORECASE,
        ),
    ),
    CandidatePattern(
        "legacy-harness-name-role",
        "harness_role_coupling",
        re.compile(r"\blegacy\s+harness[-\s]+name/role\b", re.IGNORECASE),
    ),
    CandidatePattern(
        "hard-coded-harness-authority",
        "harness_role_coupling",
        re.compile(
            r"\bhard[-\s]+coded\b.{0,80}\b(?:Codex|Claude(?: Code)?|Antigravity|Cursor|harness)\b",
            re.IGNORECASE,
        ),
    ),
)


def _rel_posix(rel_path: Path) -> str:
    return rel_path.as_posix()


def _rel_posix_lower(rel_path: Path) -> str:
    return _rel_posix(rel_path).lower()


def _is_under(rel_path: Path, parent: Path) -> bool:
    rel_text = _rel_posix_lower(rel_path)
    parent_text = _rel_posix_lower(parent).rstrip("/")
    return rel_text == parent_text or rel_text.startswith(parent_text + "/")


def relative_to_root(project_root: Path, path: Path) -> Path:
    """Return ``path`` relative to ``project_root`` or raise ``ValueError``."""
    root = project_root.resolve()
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve()
    try:
        return resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path is outside project root: {path}") from exc


def _is_scannable_file(path: Path) -> bool:
    if path.name in {"AGENTS.md", "CLAUDE.md"}:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def _is_excluded(rel_path: Path) -> bool:
    parts = {_part.lower() for _part in rel_path.parts}
    if parts & EXCLUDED_PARTS:
        return True
    return any(_is_under(rel_path, excluded) for excluded in EXCLUDED_ROOTS)


def _is_included(rel_path: Path) -> bool:
    if rel_path in INCLUDED_FILES:
        return True
    return any(_is_under(rel_path, included) for included in INCLUDED_ROOTS)


def _looks_generated(text: str) -> bool:
    head = text[:4096]
    lines = [line.strip() for line in head.splitlines()]
    if any(any(line.startswith(marker) for marker in GENERATED_LINE_MARKERS) for line in lines):
        return True
    return any(marker in head for marker in GENERATED_SUBSTRING_MARKERS)


def _looks_like_test_fixture(rel_path: Path, line_text: str) -> bool:
    if not _is_under(rel_path, Path("platform_tests")):
        return False
    fixture_tokens = (
        "assert ",
        "fixture",
        "expected",
        "sample",
        "test data",
        "write_text(",
        "json.dumps(",
    )
    lowered = line_text.lower()
    return rel_path.name.startswith("test_") and any(token in lowered for token in fixture_tokens)


def classify_path(
    project_root: Path,
    path: Path,
    *,
    text: str = "",
    line_text: str = "",
) -> PathClassification:
    """Classify a candidate path/match under the WI-4801 scan policy."""
    rel_path = relative_to_root(project_root, path)
    if _is_excluded(rel_path):
        return PathClassification("EXCLUDED", "historical, audit, runtime, or temporary surface")
    if not _is_included(rel_path):
        return PathClassification("EXCLUDED", "outside configured load-bearing scan surfaces")
    if text and _looks_generated(text):
        return PathClassification("QUARANTINE", "generated or mirrored artifact; edit canonical source first")
    if _looks_like_test_fixture(rel_path, line_text):
        return PathClassification("KEEP", "test fixture or assertion text")
    return PathClassification("STRIP", "live load-bearing candidate for role-based rewrite")


def _candidate_files(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    candidates: set[Path] = set()
    for included_file in INCLUDED_FILES:
        path = root / included_file
        if path.is_file() and _is_scannable_file(path):
            candidates.add(path)
    for included_root in INCLUDED_ROOTS:
        root_path = root / included_root
        if not root_path.exists():
            continue
        if root_path.is_file():
            if _is_scannable_file(root_path):
                candidates.add(root_path)
            continue
        for path in root_path.rglob("*"):
            if not path.is_file() or not _is_scannable_file(path):
                continue
            try:
                rel_path = relative_to_root(root, path)
            except ValueError:
                continue
            if _is_excluded(rel_path):
                continue
            candidates.add(path.resolve())
    return sorted(candidates, key=lambda item: item.relative_to(root).as_posix().lower())


def scan_text(project_root: Path, path: Path, text: str) -> list[Finding]:
    """Return classified findings for ``text`` at ``path``."""
    rel_path = relative_to_root(project_root, path)
    findings: list[Finding] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        for pattern in CANDIDATE_PATTERNS:
            for match in pattern.regex.finditer(raw_line):
                classification = classify_path(project_root, path, text=text, line_text=raw_line)
                if classification.classification == "EXCLUDED":
                    continue
                excerpt = raw_line.strip()
                if len(excerpt) > 240:
                    excerpt = excerpt[:237].rstrip() + "..."
                findings.append(
                    Finding(
                        path=_rel_posix(rel_path),
                        line=line_number,
                        column=match.start() + 1,
                        classification=classification.classification,
                        reason=classification.reason,
                        pattern_id=pattern.pattern_id,
                        pattern_family=pattern.family,
                        matched_text=match.group(0),
                        line_excerpt=excerpt,
                    )
                )
    return findings


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def _counts(items: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return dict(sorted(counts.items()))


def evaluate(project_root: Path) -> dict[str, Any]:
    """Evaluate the configured load-bearing surfaces. Read-only."""
    root = project_root.resolve()
    files_scanned = 0
    findings: list[Finding] = []
    unreadable: list[dict[str, str]] = []

    for path in _candidate_files(root):
        try:
            text = _read_text(path)
        except OSError as exc:
            unreadable.append({"path": _rel_posix(relative_to_root(root, path)), "error": str(exc)})
            continue
        files_scanned += 1
        findings.extend(scan_text(root, path, text))

    findings.sort(key=lambda finding: (finding.path.lower(), finding.line, finding.column, finding.pattern_id))
    finding_dicts = [asdict(finding) for finding in findings]
    summary = {
        "files_scanned": files_scanned,
        "matches": len(findings),
        "unreadable": len(unreadable),
        "by_classification": _counts([finding.classification for finding in findings]),
        "by_pattern_family": _counts([finding.pattern_family for finding in findings]),
    }
    return {
        "project_root": str(root),
        "status": "advisory" if findings else "pass",
        "summary": summary,
        "findings": finding_dicts,
        "unreadable": unreadable,
    }


def _print_text_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    print(
        "[ADVISORY] legacy harness-language scan: "
        f"{summary['matches']} match(es) across {summary['files_scanned']} file(s)"
    )
    if summary["by_classification"]:
        classes = ", ".join(f"{name}={count}" for name, count in summary["by_classification"].items())
        print(f"Classification: {classes}")
    for finding in result["findings"]:
        print(
            f"  - {finding['classification']} {finding['path']}:{finding['line']}:"
            f"{finding['column']} [{finding['pattern_id']}] {finding['matched_text']!r}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args(argv)

    result = evaluate(args.project_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_text_report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
