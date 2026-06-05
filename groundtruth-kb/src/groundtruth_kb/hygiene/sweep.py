"""Deterministic repository hygiene sweep — pattern-set-driven drift discovery.

Walks the repository against an owner-curated TOML pattern-set registry and
emits findings to ``.gtkb-state/hygiene-sweep/<run-id>/`` as JSON + markdown.

Read-only against the repository. No MemBase mutation surfaces. No bridge,
spec, work-item, or deliberation creation. Lifecycle decisions are the
orchestrating skill's responsibility (WI-3421), not this CLI's.

Per ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`` and
``GOV-ARTIFACT-ORIENTED-GOVERNANCE-001``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import fnmatch
import json
import re
import sys
import tomllib
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_MAX_MATCH_EXCERPT_LEN = 200


class PatternSetError(ValueError):
    """Raised when a pattern-set TOML cannot be parsed or validated."""


@dataclass(frozen=True)
class Pattern:
    """One owner-curated drift-class pattern entry."""

    id: str
    pattern_class: str
    description: str
    file_globs: tuple[str, ...]
    content_patterns: tuple[str, ...]
    exclusion_globs: tuple[str, ...]
    classification: str
    remediation_hint: str
    match_mode: str = "content"
    _compiled_content_patterns: tuple[re.Pattern[str], ...] = field(default=())

    def matches_path(self, rel_path: str) -> bool:
        """True if ``rel_path`` matches any file glob and no exclusion glob."""
        normalized = rel_path.replace("\\", "/")
        if any(fnmatch.fnmatchcase(normalized, g) for g in self.exclusion_globs):
            return False
        return any(fnmatch.fnmatchcase(normalized, g) for g in self.file_globs)


@dataclass(frozen=True)
class Finding:
    """One pattern match against a file."""

    pattern_id: str
    pattern_class: str
    classification: str
    file: str
    line: int
    matched_excerpt: str
    remediation_hint: str


@dataclass(frozen=True)
class SweepResult:
    """Aggregate output of one sweep invocation."""

    run_id: str
    generated_at: str
    root: str
    pattern_set_path: str
    patterns_loaded: int
    files_scanned: int
    findings: tuple[Finding, ...]

    @property
    def finding_count(self) -> int:
        return len(self.findings)


def load_pattern_set(toml_path: Path, name: str | None = None) -> list[Pattern]:
    """Load a pattern-set TOML registry.

    ``name`` filters by ``id``; if ``None`` returns all patterns. Raises
    ``PatternSetError`` on malformed TOML or invalid pattern entries.
    """
    if not toml_path.is_file():
        raise PatternSetError(f"Pattern set TOML not found: {toml_path}")
    try:
        with toml_path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise PatternSetError(f"Malformed TOML in {toml_path}: {exc}") from exc

    raw_patterns = data.get("patterns") or []
    if not isinstance(raw_patterns, list):
        raise PatternSetError(f"'patterns' must be an array in {toml_path}")

    patterns: list[Pattern] = []
    for idx, entry in enumerate(raw_patterns):
        if not isinstance(entry, dict):
            raise PatternSetError(f"Pattern entry #{idx} must be a table in {toml_path}")
        pattern_id = entry.get("id")
        if not isinstance(pattern_id, str) or not pattern_id:
            raise PatternSetError(f"Pattern entry #{idx} missing 'id' (string) in {toml_path}")
        if name is not None and pattern_id != name:
            continue
        try:
            compiled = tuple(re.compile(p) for p in entry.get("content_patterns") or [])
        except re.error as exc:
            raise PatternSetError(f"Pattern '{pattern_id}' has invalid regex in 'content_patterns': {exc}") from exc
        match_mode = str(entry.get("match_mode") or "content").strip().lower()
        if match_mode not in ("content", "presence"):
            raise PatternSetError(
                f"Pattern '{pattern_id}' has invalid match_mode '{match_mode}' "
                f"(expected 'content' or 'presence') in {toml_path}"
            )
        patterns.append(
            Pattern(
                id=pattern_id,
                pattern_class=str(entry.get("class") or "unspecified"),
                description=str(entry.get("description") or ""),
                file_globs=tuple(str(g) for g in entry.get("file_globs") or []),
                content_patterns=tuple(str(p) for p in entry.get("content_patterns") or []),
                exclusion_globs=tuple(str(g) for g in entry.get("exclusion_globs") or []),
                classification=str(entry.get("classification") or "unclassified"),
                remediation_hint=str(entry.get("remediation_hint") or ""),
                match_mode=match_mode,
                _compiled_content_patterns=compiled,
            )
        )
    return patterns


def _is_excluded(rel_path: str, exclusion_globs: Iterable[str]) -> bool:
    normalized = rel_path.replace("\\", "/")
    return any(fnmatch.fnmatchcase(normalized, g) for g in exclusion_globs)


def walk_repo(root: Path, file_globs: Iterable[str], exclusion_globs: Iterable[str]) -> Iterator[Path]:
    """Yield files under ``root`` matching ``file_globs`` and not under ``exclusion_globs``.

    Path matching is glob-based using forward-slash-normalized relative paths.
    Directories matched by an exclusion glob are pruned (not descended into).
    """
    root = root.resolve()
    file_globs_tuple = tuple(file_globs)
    exclusion_globs_tuple = tuple(exclusion_globs)
    if not file_globs_tuple:
        return

    def walk(directory: Path) -> Iterator[Path]:
        try:
            entries = sorted(directory.iterdir())
        except (PermissionError, OSError):
            return
        for entry in entries:
            try:
                rel = entry.relative_to(root).as_posix()
            except ValueError:
                continue
            if entry.is_dir():
                if _is_excluded(rel + "/", exclusion_globs_tuple) or _is_excluded(rel, exclusion_globs_tuple):
                    continue
                yield from walk(entry)
            elif entry.is_file():
                if _is_excluded(rel, exclusion_globs_tuple):
                    continue
                if any(fnmatch.fnmatchcase(rel, g) for g in file_globs_tuple):
                    yield entry

    yield from walk(root)


def scan_file(
    path: Path,
    pattern: Pattern,
    root: Path,
) -> list[Finding]:
    """Scan ``path`` content for ``pattern.content_patterns``; emit per-hit Findings."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (PermissionError, OSError):
        return []
    findings: list[Finding] = []
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = path.as_posix()
    lines = text.splitlines()
    for line_idx, line_text in enumerate(lines, start=1):
        for compiled in pattern._compiled_content_patterns:
            match = compiled.search(line_text)
            if match is None:
                continue
            excerpt = line_text.strip()
            if len(excerpt) > _MAX_MATCH_EXCERPT_LEN:
                excerpt = excerpt[: _MAX_MATCH_EXCERPT_LEN - 3] + "..."
            findings.append(
                Finding(
                    pattern_id=pattern.id,
                    pattern_class=pattern.pattern_class,
                    classification=pattern.classification,
                    file=rel,
                    line=line_idx,
                    matched_excerpt=excerpt,
                    remediation_hint=pattern.remediation_hint,
                )
            )
    return findings


def presence_finding(path: Path, pattern: Pattern, root: Path) -> Finding:
    """Emit a presence Finding for a file whose existence is itself the drift signal.

    Used by ``match_mode == "presence"`` patterns: the matched path is the
    finding (``line = 0``), with no content read. The presence of a file under
    the pattern's ``file_globs`` (and not under its ``exclusion_globs``) is the
    detection; ``content_patterns`` are not consulted for presence patterns.
    """
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = path.as_posix()
    return Finding(
        pattern_id=pattern.id,
        pattern_class=pattern.pattern_class,
        classification=pattern.classification,
        file=rel,
        line=0,
        matched_excerpt=rel,
        remediation_hint=pattern.remediation_hint,
    )


def run_sweep(
    root: Path,
    pattern_set_path: Path,
    pattern_name: str | None = None,
) -> SweepResult:
    """Walk ``root``, scan against the loaded pattern set, return aggregated findings."""
    root = root.resolve()
    patterns = load_pattern_set(pattern_set_path, name=pattern_name)
    findings: list[Finding] = []
    scanned_files: set[Path] = set()
    for pattern in patterns:
        for file_path in walk_repo(root, pattern.file_globs, pattern.exclusion_globs):
            scanned_files.add(file_path)
            if pattern.match_mode == "presence":
                findings.append(presence_finding(file_path, pattern, root))
            else:
                findings.extend(scan_file(file_path, pattern, root))
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return SweepResult(
        run_id=run_id,
        generated_at=generated_at,
        root=str(root),
        pattern_set_path=str(pattern_set_path.resolve()),
        patterns_loaded=len(patterns),
        files_scanned=len(scanned_files),
        findings=tuple(findings),
    )


def emit_json(result: SweepResult, out_path: Path) -> None:
    """Write ``result`` as structured JSON to ``out_path``."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_id": result.run_id,
        "generated_at": result.generated_at,
        "root": result.root,
        "pattern_set_path": result.pattern_set_path,
        "patterns_loaded": result.patterns_loaded,
        "files_scanned": result.files_scanned,
        "finding_count": result.finding_count,
        "findings": [asdict(f) for f in result.findings],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def emit_markdown(result: SweepResult, out_path: Path) -> None:
    """Write ``result`` as a human-readable markdown summary to ``out_path``."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Hygiene Sweep Summary",
        "",
        f"- Generated: {result.generated_at}",
        f"- Run id: {result.run_id}",
        f"- Root: {result.root}",
        f"- Pattern set: {result.pattern_set_path}",
        f"- Patterns loaded: {result.patterns_loaded}",
        f"- Files scanned: {result.files_scanned}",
        f"- Findings: {result.finding_count}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
    else:
        by_class: dict[str, list[Finding]] = {}
        for finding in result.findings:
            by_class.setdefault(finding.pattern_class, []).append(finding)
        for pattern_class in sorted(by_class):
            class_findings = by_class[pattern_class]
            lines.append(f"## {pattern_class} ({len(class_findings)})")
            lines.append("")
            for finding in class_findings:
                lines.append(
                    f"- `{finding.file}:{finding.line}` "
                    f"({finding.classification}, pattern `{finding.pattern_id}`): "
                    f"`{finding.matched_excerpt}`"
                )
                if finding.remediation_hint:
                    lines.append(f"  - Remediation: {finding.remediation_hint}")
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin CLI wrapper
    """Module-level entrypoint for ``python -m groundtruth_kb.hygiene.sweep``."""
    import argparse

    parser = argparse.ArgumentParser(description="Run a deterministic hygiene sweep.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--patterns-path", type=Path, default=Path("config/governance/hygiene-sweep-patterns.toml"))
    parser.add_argument("--pattern-set", default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        result = run_sweep(args.root, args.patterns_path, args.pattern_set)
    except PatternSetError as exc:
        print(f"error: {exc}", file=sys.stderr)  # print-ok
        return 2
    out_dir = args.output or args.root / ".gtkb-state" / "hygiene-sweep" / result.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    emit_json(result, out_dir / "findings.json")
    emit_markdown(result, out_dir / "summary.md")
    print(f"hygiene sweep: {result.finding_count} finding(s); output: {out_dir}")  # print-ok
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
