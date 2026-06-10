"""Spec-derived tests for the WI-3420 ``gt hygiene sweep`` deterministic CLI.

Rebuild of the test module that VERIFIED at ``bridge/gtkb-hygiene-sweep-cli-004.md``
and was subsequently destroyed (uncommitted) by a parallel session's working-tree
cleanup. Restored under WI-3435 / PROJECT-GTKB-RELIABILITY-FIXES per bridge thread
``gtkb-hygiene-sweep-cli-test-rebuild`` (Codex GO at ``-002``).

Tests exercise the live interfaces only (GOV-10, GOV-19):
- the ``groundtruth_kb.hygiene`` package functions/dataclasses, and
- the click ``main -> hygiene -> sweep`` command in ``groundtruth_kb.cli``.

Seven categories, 23 tests:
load_pattern_set (6) | walk_repo (3) | scan_file (3) | run_sweep (2)
| emit_json/emit_markdown (3) | CLI surface (5) | MemBase non-participation (1).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.hygiene import (
    Finding,
    PatternSetError,
    SweepResult,
    emit_json,
    emit_markdown,
    load_pattern_set,
    run_sweep,
    scan_file,
    walk_repo,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers — build pattern-set TOML using TOML *literal* strings so
# regex content patterns (which may contain backslashes) need no escaping.
# ---------------------------------------------------------------------------


def _toml_str(value: object) -> str:
    return "'" + str(value) + "'"


def _toml_arr(items: list[str]) -> str:
    return "[" + ", ".join(_toml_str(i) for i in items) + "]"


def _pattern_block(p: dict[str, object]) -> str:
    return "\n".join(
        [
            "[[patterns]]",
            f"id = {_toml_str(p['id'])}",
            f"class = {_toml_str(p.get('class', 'drift'))}",
            f"description = {_toml_str(p.get('description', ''))}",
            f"file_globs = {_toml_arr(list(p.get('file_globs', [])))}",
            f"content_patterns = {_toml_arr(list(p.get('content_patterns', [])))}",
            f"exclusion_globs = {_toml_arr(list(p.get('exclusion_globs', [])))}",
            f"classification = {_toml_str(p.get('classification', 'unclassified'))}",
            f"remediation_hint = {_toml_str(p.get('remediation_hint', ''))}",
        ]
    )


def _write_patterns(toml_path: Path, patterns: list[dict[str, object]]) -> Path:
    toml_path.write_text("\n\n".join(_pattern_block(p) for p in patterns), encoding="utf-8")
    return toml_path


# ===========================================================================
# Category 1 — load_pattern_set (6)
# ===========================================================================


def test_load_pattern_set_valid_returns_all(tmp_path: Path) -> None:
    toml = _write_patterns(
        tmp_path / "patterns.toml",
        [
            {"id": "p1", "file_globs": ["*.md"], "content_patterns": ["agent-red"]},
            {"id": "p2", "file_globs": ["*.txt"], "content_patterns": ["TODO"]},
        ],
    )
    patterns = load_pattern_set(toml)
    assert [p.id for p in patterns] == ["p1", "p2"]


def test_load_pattern_set_filters_by_name(tmp_path: Path) -> None:
    toml = _write_patterns(
        tmp_path / "patterns.toml",
        [
            {"id": "p1", "file_globs": ["*.md"], "content_patterns": ["agent-red"]},
            {"id": "p2", "file_globs": ["*.txt"], "content_patterns": ["TODO"]},
        ],
    )
    patterns = load_pattern_set(toml, name="p2")
    assert len(patterns) == 1
    assert patterns[0].id == "p2"


def test_load_pattern_set_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(PatternSetError, match="not found"):
        load_pattern_set(tmp_path / "does-not-exist.toml")


def test_load_pattern_set_malformed_toml_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.toml"
    bad.write_text("patterns = [ this is = not valid toml", encoding="utf-8")
    with pytest.raises(PatternSetError, match="Malformed TOML"):
        load_pattern_set(bad)


def test_load_pattern_set_invalid_regex_raises(tmp_path: Path) -> None:
    toml = _write_patterns(
        tmp_path / "patterns.toml",
        [{"id": "p1", "file_globs": ["*.md"], "content_patterns": ["["]}],
    )
    with pytest.raises(PatternSetError, match="invalid regex"):
        load_pattern_set(toml)


def test_load_pattern_set_compiled_patterns_present(tmp_path: Path) -> None:
    toml = _write_patterns(
        tmp_path / "patterns.toml",
        [{"id": "p1", "file_globs": ["*.md"], "content_patterns": ["agent-red", "TODO"]}],
    )
    pattern = load_pattern_set(toml)[0]
    assert len(pattern._compiled_content_patterns) == 2
    assert all(isinstance(c, re.Pattern) for c in pattern._compiled_content_patterns)


# ===========================================================================
# Category 2 — walk_repo (3)
# ===========================================================================


def test_walk_repo_finds_matching_files(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("x", encoding="utf-8")
    (tmp_path / "b.txt").write_text("x", encoding="utf-8")
    names = {p.name for p in walk_repo(tmp_path, ["*.md"], [])}
    assert "a.md" in names
    assert "b.txt" not in names


def test_walk_repo_honors_exclusion_globs(tmp_path: Path) -> None:
    (tmp_path / "keep.md").write_text("x", encoding="utf-8")
    (tmp_path / "excluded").mkdir()
    (tmp_path / "excluded" / "skip.md").write_text("x", encoding="utf-8")
    names = {p.name for p in walk_repo(tmp_path, ["*.md"], ["excluded/*"])}
    assert "keep.md" in names
    assert "skip.md" not in names


def test_walk_repo_with_empty_file_globs_yields_nothing(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("x", encoding="utf-8")
    assert list(walk_repo(tmp_path, [], [])) == []


# ===========================================================================
# Category 3 — scan_file (3)
# ===========================================================================


def _single_pattern(tmp_path: Path, **overrides: object):
    base: dict[str, object] = {
        "id": "p1",
        "file_globs": ["*.md"],
        "content_patterns": ["agent-red"],
        "classification": "advisory",
        "remediation_hint": "rename to adopter",
    }
    base.update(overrides)
    toml = _write_patterns(tmp_path / "patterns.toml", [base])
    return load_pattern_set(toml)[0]


def test_scan_file_emits_findings(tmp_path: Path) -> None:
    pattern = _single_pattern(tmp_path)
    target = tmp_path / "drift.md"
    target.write_text("first line\nsee agent-red here\n", encoding="utf-8")
    findings = scan_file(target, pattern, tmp_path)
    assert len(findings) == 1
    assert findings[0].pattern_id == "p1"
    assert findings[0].line == 2
    assert "agent-red" in findings[0].matched_excerpt


def test_scan_file_no_match_returns_empty(tmp_path: Path) -> None:
    pattern = _single_pattern(tmp_path)
    target = tmp_path / "clean.md"
    target.write_text("nothing notable here\n", encoding="utf-8")
    assert scan_file(target, pattern, tmp_path) == []


def test_scan_file_long_line_excerpt_truncated(tmp_path: Path) -> None:
    pattern = _single_pattern(tmp_path)
    target = tmp_path / "long.md"
    target.write_text("agent-red " + "x" * 500 + "\n", encoding="utf-8")
    findings = scan_file(target, pattern, tmp_path)
    assert len(findings) == 1
    excerpt = findings[0].matched_excerpt
    assert len(excerpt) <= 200
    assert excerpt.endswith("...")


# ===========================================================================
# Category 4 — run_sweep (2)
# ===========================================================================


def test_run_sweep_e2e_synthetic(tmp_path: Path) -> None:
    (tmp_path / "drift.md").write_text("see agent-red here\n", encoding="utf-8")
    (tmp_path / "clean.md").write_text("all good\n", encoding="utf-8")
    (tmp_path / "excluded").mkdir()
    (tmp_path / "excluded" / "skip.md").write_text("agent-red lurking\n", encoding="utf-8")
    toml = _write_patterns(
        tmp_path / "patterns.toml",
        [
            {
                "id": "p1",
                "file_globs": ["*.md"],
                "content_patterns": ["agent-red"],
                "exclusion_globs": ["excluded/*"],
            }
        ],
    )
    result = run_sweep(tmp_path, toml)
    assert result.patterns_loaded == 1
    assert result.finding_count == 1
    assert result.findings[0].file == "drift.md"
    assert result.files_scanned == 2  # drift.md + clean.md; excluded/ pruned


def test_run_sweep_pattern_name_filter(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("see agent-red\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("TODO later\n", encoding="utf-8")
    toml = _write_patterns(
        tmp_path / "patterns.toml",
        [
            {"id": "p1", "file_globs": ["*.md"], "content_patterns": ["agent-red"]},
            {"id": "p2", "file_globs": ["*.txt"], "content_patterns": ["TODO"]},
        ],
    )
    result = run_sweep(tmp_path, toml, pattern_name="p1")
    assert result.patterns_loaded == 1
    assert result.finding_count == 1
    assert {f.pattern_id for f in result.findings} == {"p1"}


# ===========================================================================
# Category 5 — emit_json and emit_markdown (3)
# ===========================================================================


def _result(findings: tuple[Finding, ...]) -> SweepResult:
    return SweepResult(
        run_id="20260101T000000Z",
        generated_at="2026-01-01T00:00:00.000000Z",
        root="/repo",
        pattern_set_path="/repo/patterns.toml",
        patterns_loaded=1,
        files_scanned=2,
        findings=findings,
    )


def _finding(pattern_class: str = "terminology-drift") -> Finding:
    return Finding(
        pattern_id="p1",
        pattern_class=pattern_class,
        classification="advisory",
        file="drift.md",
        line=3,
        matched_excerpt="see agent-red here",
        remediation_hint="rename to adopter",
    )


def test_emit_json_schema(tmp_path: Path) -> None:
    out = tmp_path / "findings.json"
    emit_json(_result((_finding(),)), out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "run_id",
        "generated_at",
        "root",
        "pattern_set_path",
        "patterns_loaded",
        "files_scanned",
        "finding_count",
        "findings",
    }
    assert required <= set(payload)
    assert payload["finding_count"] == len(payload["findings"]) == 1


def test_emit_markdown_groups_by_class(tmp_path: Path) -> None:
    out = tmp_path / "summary.md"
    emit_markdown(_result((_finding("terminology-drift"),)), out)
    text = out.read_text(encoding="utf-8")
    assert "## terminology-drift (1)" in text


def test_emit_markdown_no_findings_renders_zero_section(tmp_path: Path) -> None:
    out = tmp_path / "summary.md"
    emit_markdown(_result(()), out)
    text = out.read_text(encoding="utf-8")
    assert "No findings." in text
    assert "## " not in text  # no per-class section headings


# ===========================================================================
# Category 6 — CLI surface (5): click `main -> hygiene -> sweep`
# ===========================================================================


def _cli_repo(tmp_path: Path, *, with_findings: bool) -> tuple[Path, Path, Path]:
    """Build a synthetic repo + pattern set; return (root, patterns_toml, out_dir)."""
    root = tmp_path / "repo"
    root.mkdir()
    body = "see agent-red here\n" if with_findings else "all clean here\n"
    (root / "doc.md").write_text(body, encoding="utf-8")
    toml = _write_patterns(
        tmp_path / "patterns.toml",
        [{"id": "p1", "file_globs": ["*.md"], "content_patterns": ["agent-red"]}],
    )
    return root, toml, tmp_path / "out"


def test_cli_help_lists_subcommand() -> None:
    result = CliRunner().invoke(main, ["hygiene", "--help"])
    assert result.exit_code == 0
    assert "sweep" in result.output


def test_cli_runs_against_synthetic_repo(tmp_path: Path) -> None:
    root, toml, out = _cli_repo(tmp_path, with_findings=True)
    result = CliRunner().invoke(
        main,
        ["hygiene", "sweep", "--root", str(root), "--patterns-path", str(toml), "--output", str(out)],
    )
    assert result.exit_code == 0, result.output
    assert (out / "findings.json").exists()
    assert (out / "summary.md").exists()
    assert "hygiene sweep:" in result.output


def test_cli_fail_on_findings_exits_two(tmp_path: Path) -> None:
    root, toml, out = _cli_repo(tmp_path, with_findings=True)
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "sweep",
            "--root",
            str(root),
            "--patterns-path",
            str(toml),
            "--output",
            str(out),
            "--fail-on-findings",
        ],
    )
    assert result.exit_code == 2


def test_cli_no_findings_fail_on_findings_exits_zero(tmp_path: Path) -> None:
    root, toml, out = _cli_repo(tmp_path, with_findings=False)
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "sweep",
            "--root",
            str(root),
            "--patterns-path",
            str(toml),
            "--output",
            str(out),
            "--fail-on-findings",
        ],
    )
    assert result.exit_code == 0, result.output


def test_cli_format_json_only(tmp_path: Path) -> None:
    root, toml, out = _cli_repo(tmp_path, with_findings=True)
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "sweep",
            "--root",
            str(root),
            "--patterns-path",
            str(toml),
            "--output",
            str(out),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert (out / "findings.json").exists()
    assert not (out / "summary.md").exists()


# ===========================================================================
# Category 7 — MemBase non-participation invariant (1)
# ===========================================================================


def test_hygiene_module_has_no_membase_mutation_surfaces() -> None:
    """DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001: the hygiene package must not carry
    any MemBase mutation surface (no insert_*/update_* calls, no KnowledgeDB())."""
    import groundtruth_kb.hygiene as hygiene_pkg

    pkg_dir = Path(hygiene_pkg.__file__).parent
    mutation_call = re.compile(r"\b(?:insert|update)_\w+\s*\(")
    knowledgedb_ctor = re.compile(r"\bKnowledgeDB\s*\(")
    offenders: list[str] = []
    for py_file in sorted(pkg_dir.glob("*.py")):
        text = py_file.read_text(encoding="utf-8")
        if mutation_call.search(text) or knowledgedb_ctor.search(text):
            offenders.append(py_file.name)
    assert offenders == [], f"MemBase mutation surface found in hygiene package: {offenders}"
