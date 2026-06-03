"""Tests for hygiene-sweep presence-mode + WI-4249 detection patterns.

Covers the spec-derived verification plan from
`bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-003.md` (GO at -004):

- presence-mode emits one finding per matched file (line 0), no content read
- content-mode behavior unchanged (regression — GO condition 3)
- back-compat: a pattern with no `match_mode` loads as `content`
- the two approved real patterns (runtime-residue-paths,
  snapshots-non-manifest-recursion) detect their classes; clean tree = no findings

All tests build temp trees + temp pattern sets; the real-pattern tests load the
live `config/governance/hygiene-sweep-patterns.toml` but scan only temp roots.
No live repo or `groundtruth.db` mutation.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.hygiene import sweep

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL_PATTERNS = _REPO_ROOT / "config" / "governance" / "hygiene-sweep-patterns.toml"


def _write(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_pattern_toml(tmp_path: Path, body: str) -> Path:
    toml_path = tmp_path / "patterns.toml"
    toml_path.write_text("version = 1\n\n" + body, encoding="utf-8")
    return toml_path


# --------------------------------------------------------------------------
# Engine: presence mode + back-compat
# --------------------------------------------------------------------------


def test_pattern_without_match_mode_defaults_content(tmp_path: Path) -> None:
    toml_path = _write_pattern_toml(
        tmp_path,
        '[[patterns]]\nid = "p"\nclass = "c"\nfile_globs = ["**/*.txt"]\ncontent_patterns = ["FOO"]\n',
    )
    patterns = sweep.load_pattern_set(toml_path)
    assert len(patterns) == 1
    assert patterns[0].match_mode == "content"


def test_invalid_match_mode_rejected(tmp_path: Path) -> None:
    toml_path = _write_pattern_toml(
        tmp_path,
        '[[patterns]]\nid = "p"\nclass = "c"\nfile_globs = ["**/*.txt"]\nmatch_mode = "bogus"\n',
    )
    with pytest.raises(sweep.PatternSetError, match="match_mode"):
        sweep.load_pattern_set(toml_path)


def test_presence_mode_emits_finding_per_matched_file(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(root / "a" / "resid1.log")
    _write(root / "a" / "b" / "resid2.log")
    _write(root / "a" / "keep.txt")  # not matched by the presence glob
    toml_path = _write_pattern_toml(
        tmp_path,
        '[[patterns]]\nid = "resid"\nclass = "runtime_residue"\nmatch_mode = "presence"\n'
        'file_globs = ["**/*.log"]\ncontent_patterns = []\nclassification = "residue"\n',
    )
    result = sweep.run_sweep(root, toml_path)
    matched = sorted(f.file for f in result.findings)
    assert matched == ["a/b/resid2.log", "a/resid1.log"]
    for finding in result.findings:
        assert finding.line == 0
        assert finding.matched_excerpt == finding.file  # path is the excerpt
        assert finding.pattern_id == "resid"


def test_presence_mode_ignores_content(tmp_path: Path) -> None:
    """Presence patterns emit on file match regardless of content_patterns."""
    root = tmp_path / "repo"
    _write(root / "x" / "f.log", "nothing matches here")
    toml_path = _write_pattern_toml(
        tmp_path,
        '[[patterns]]\nid = "resid"\nclass = "c"\nmatch_mode = "presence"\n'
        'file_globs = ["**/*.log"]\ncontent_patterns = ["WILL-NOT-MATCH"]\n',
    )
    result = sweep.run_sweep(root, toml_path)
    assert result.finding_count == 1  # presence ignores the (non-matching) content pattern


def test_content_mode_unchanged(tmp_path: Path) -> None:
    """GO condition 3 regression: content patterns still emit only on regex hits."""
    root = tmp_path / "repo"
    _write(root / "hit.txt", "alpha FOO beta")
    _write(root / "miss.txt", "no token here")
    toml_path = _write_pattern_toml(
        tmp_path,
        '[[patterns]]\nid = "c"\nclass = "x"\nfile_globs = ["*.txt"]\ncontent_patterns = ["FOO"]\n',
    )
    result = sweep.run_sweep(root, toml_path)
    assert result.finding_count == 1
    f = result.findings[0]
    assert f.file == "hit.txt"
    assert f.line == 1
    assert "FOO" in f.matched_excerpt


def test_content_mode_empty_content_patterns_emits_nothing(tmp_path: Path) -> None:
    """A content pattern with no content_patterns is a no-op (unchanged behavior)."""
    root = tmp_path / "repo"
    _write(root / "f.txt", "anything")
    toml_path = _write_pattern_toml(
        tmp_path,
        '[[patterns]]\nid = "c"\nclass = "x"\nfile_globs = ["*.txt"]\ncontent_patterns = []\n',
    )
    result = sweep.run_sweep(root, toml_path)
    assert result.finding_count == 0


# --------------------------------------------------------------------------
# The two approved real patterns (loaded from the live registry)
# --------------------------------------------------------------------------


def test_runtime_residue_paths_detected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(root / "sandbox" / "PASS" / "bridge" / "INDEX.md")  # residue (nested PASS/bridge)
    _write(root / ".claude" / "rules" / "ok.md")  # legitimate top-level .claude (not residue)
    result = sweep.run_sweep(root, _REAL_PATTERNS, "runtime-residue-paths")
    files = sorted(f.file for f in result.findings)
    assert "sandbox/PASS/bridge/INDEX.md" in files
    assert all(f != ".claude/rules/ok.md" for f in files)
    assert all(f.line == 0 for f in result.findings)  # presence mode


def test_snapshots_non_manifest_detected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(root / "out" / "snapshots" / "run1" / "snapshots" / "recursed.json")  # self-recursion
    _write(root / "out" / "snapshots" / "run1" / "normal.json")  # single-level, not recursive
    result = sweep.run_sweep(root, _REAL_PATTERNS, "snapshots-non-manifest-recursion")
    files = sorted(f.file for f in result.findings)
    assert "out/snapshots/run1/snapshots/recursed.json" in files
    assert "out/snapshots/run1/normal.json" not in files


def test_clean_tree_has_no_findings(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(root / "src" / "module.py", "print('hello')")
    _write(root / "docs" / "readme.md", "# docs")
    for pattern_id in ("runtime-residue-paths", "snapshots-non-manifest-recursion"):
        result = sweep.run_sweep(root, _REAL_PATTERNS, pattern_id)
        assert result.finding_count == 0, f"{pattern_id} false-positived on a clean tree"


def test_pytest_basetemp_class_not_present(tmp_path: Path) -> None:
    """The pytest-basetemp class is deferred (F2 / WI-3469); it must not be in the registry yet."""
    ids = {p.id for p in sweep.load_pattern_set(_REAL_PATTERNS)}
    assert "pytest-basetemp-acl" not in ids
