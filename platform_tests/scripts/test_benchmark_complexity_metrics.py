"""Tests for the complexity-metrics benchmark (WI-6746).

The verification plan in bridge/gtkb-wi6746-complexity-metrics-benchmark-001.md
maps each linked specification to a check. These tests implement the rows that
are testable in isolation:

- benchmark contract              -> run() returns BenchmarkResult objects
- GOV-SOURCE-OF-TRUTH-FRESHNESS   -> two runs on an unchanged tree agree
- read-only invariant             -> no canonical table or registry is written
- ADR-ISOLATION-APPLICATION-PLACEMENT -> applications/ is never traversed
- GOV-DETERMINISTIC-SERVICES      -> runs standalone without session context
- registration                    -> the CLI can resolve and import it
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.benchmarks.common import BenchmarkResult  # noqa: E402
from scripts.benchmarks.complexity_metrics import (  # noqa: E402
    BENCHMARK_ID,
    DERIVED_ROOTS,
    STATE_ROOTS,
    run,
)

WINDOW = ("2026-01-01T00:00:00Z", "2026-12-31T23:59:59Z")


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A minimal fixture tree exercising every counted surface."""
    (tmp_path / ".gtkb-state" / "alpha").mkdir(parents=True)
    (tmp_path / ".gtkb-state" / "beta").mkdir(parents=True)
    (tmp_path / ".gtkb-state" / "loose.txt").write_text("x", encoding="utf-8")

    # Zero directories, only loose files -- the .claude/session shape that a
    # directories-only count would be blind to.
    (tmp_path / ".claude" / "session").mkdir(parents=True)
    for name in ("handoff-a.md", "role-b.json"):
        (tmp_path / ".claude" / "session" / name).write_text("x", encoding="utf-8")

    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude" / "hooks" / "projected.py").write_text("pass\n", encoding="utf-8")

    rules = tmp_path / ".harness-baseline-configuration" / "rules"
    rules.mkdir(parents=True)
    (rules / "one.md").write_text("# one\n", encoding="utf-8")
    (rules / "two.md").write_text("# two\n", encoding="utf-8")
    (rules / "not-a-rule.txt").write_text("ignored\n", encoding="utf-8")

    hooks = tmp_path / ".harness-baseline-configuration" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "gate.py").write_text("a\nb\nc\n", encoding="utf-8")

    registry = tmp_path / "config" / "registry"
    registry.mkdir(parents=True)
    (registry / "sot-artifacts.toml").write_text(
        "[[artifacts]]\nid = 'a'\n\n[[artifacts]]\nid = 'b'\n", encoding="utf-8"
    )
    return tmp_path


def _by_id(results: list[BenchmarkResult]) -> dict[str, BenchmarkResult]:
    return {r.benchmark_id: r for r in results}


def test_run_returns_benchmark_results(tree: Path) -> None:
    results = run(*WINDOW, tree)
    assert results, "benchmark returned no results"
    assert all(isinstance(r, BenchmarkResult) for r in results)
    assert all(r.benchmark_id.startswith(f"{BENCHMARK_ID}.") for r in results)
    assert all(r.window_start == WINDOW[0] and r.window_end == WINDOW[1] for r in results)


def test_counts_loose_files_not_only_directories(tree: Path) -> None:
    """The .claude/session shape: zero directories, files that must still count.

    This is the decisive behaviour. A directories-only rule reports zero for a
    root that holds the entire remaining session-object population.
    """
    state = _by_id(run(*WINDOW, tree))[f"{BENCHMARK_ID}.state_locations"]
    session = state.dimensions["per_root"][".claude/session"]
    assert session["directories"] == 0
    assert session["loose_files"] == 2
    # 2 dirs + 1 loose under .gtkb-state, plus 2 loose under .claude/session
    assert state.value == 5


def test_governance_rule_count_ignores_non_markdown(tree: Path) -> None:
    rules = _by_id(run(*WINDOW, tree))[f"{BENCHMARK_ID}.governance_rule_files"]
    assert rules.value == 2, "non-markdown files must not count as rule files"


def test_derived_artifacts_counted_separately(tree: Path) -> None:
    derived = _by_id(run(*WINDOW, tree))[f"{BENCHMARK_ID}.derived_artifacts"]
    assert derived.value >= 1
    assert ".claude" in derived.dimensions["per_projection"]


def test_registered_sot_artifacts_counted(tree: Path) -> None:
    reg = _by_id(run(*WINDOW, tree))[f"{BENCHMARK_ID}.registered_sot_artifacts"]
    assert reg.value == 2


def test_idempotent_on_unchanged_tree(tree: Path) -> None:
    """GOV-SOURCE-OF-TRUTH-FRESHNESS-001: values derive from a fresh read."""
    first = {r.benchmark_id: r.value for r in run(*WINDOW, tree)}
    second = {r.benchmark_id: r.value for r in run(*WINDOW, tree)}
    assert first == second


def test_run_id_has_second_resolution(tree: Path) -> None:
    """Documents the shared contract: run ids are second-resolution timestamps.

    ``common.new_run_id()`` returns ``YYYYMMDD-HHMMSS``, so two runs inside one
    second share a run id. Because ``write_run_outputs`` writes to
    ``.gtkb-state/benchmarks/<run_id>/``, same-second runs overwrite each other.

    This test asserts the behaviour that exists rather than the behaviour that
    would be preferable, so the assumption is visible to the next reader instead
    of being discovered as a silent overwrite. The collision hazard is a defect
    in the shared contract affecting every benchmark, not in this module, and is
    tracked as its own work item.
    """
    first = run(*WINDOW, tree)[0].run_id
    second = run(*WINDOW, tree)[0].run_id
    assert len(first) == len("YYYYMMDD-HHMMSS")
    # Same second -> identical id. Not asserted as equal, because a run
    # straddling a second boundary would legitimately differ and must not make
    # this test flaky.
    assert first <= second


def test_does_not_traverse_applications(tree: Path) -> None:
    """ADR-ISOLATION-APPLICATION-PLACEMENT-001: platform scope only."""
    app = tree / "applications" / "Agent_Red"
    app.mkdir(parents=True)
    for i in range(25):
        (app / f"f{i}.py").write_text("x\n", encoding="utf-8")
    before = {r.benchmark_id: r.value for r in run(*WINDOW, tree)}
    for i in range(25, 60):
        (app / f"f{i}.py").write_text("x\n", encoding="utf-8")
    after = {r.benchmark_id: r.value for r in run(*WINDOW, tree)}
    assert before == after, "application-scope files must not affect platform counts"
    assert not any(name.startswith("applications") for name in STATE_ROOTS + DERIVED_ROOTS)


def test_writes_nothing_to_the_tree(tree: Path) -> None:
    """Read-only invariant: run() mutates no file under the project root."""

    def snapshot() -> dict[str, float]:
        return {str(p.relative_to(tree)): p.stat().st_mtime for p in tree.rglob("*") if p.is_file()}

    before = snapshot()
    run(*WINDOW, tree)
    assert snapshot() == before, "benchmark modified the tree"


def test_membase_opened_read_only(tmp_path: Path) -> None:
    """A canonical table must not be created, migrated, or written."""
    db = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE specifications (id TEXT)")
    conn.execute("INSERT INTO specifications VALUES ('SPEC-1')")
    conn.commit()
    conn.close()
    mtime_before = db.stat().st_mtime

    results = _by_id(run(*WINDOW, tmp_path))
    governed = results[f"{BENCHMARK_ID}.governed_records"]
    assert governed.dimensions["specifications"] == 1
    assert db.stat().st_mtime == mtime_before, "database file was modified"


def test_missing_surfaces_degrade_to_zero(tmp_path: Path) -> None:
    """An empty tree yields zeros rather than raising.

    A benchmark that crashes on an unfamiliar tree cannot be run in CI or on a
    fresh clone, which are exactly the cases where a baseline is most useful.
    """
    results = _by_id(run(*WINDOW, tmp_path))
    assert results[f"{BENCHMARK_ID}.state_locations"].value == 0
    assert results[f"{BENCHMARK_ID}.governed_records"].value == 0


def test_every_result_carries_a_source_query(tree: Path) -> None:
    """source_query documents how each value was produced, per the contract."""
    for result in run(*WINDOW, tree):
        assert result.source_query, f"{result.benchmark_id} has no source_query"


def test_registered_with_the_benchmark_cli() -> None:
    """The benchmark is resolvable through the CLI registration surface."""
    from scripts.benchmarks import cli

    assert BENCHMARK_ID in cli.BENCHMARK_MODULES
    module = cli._BENCHMARK_LOADERS[BENCHMARK_ID]()
    assert hasattr(module, "run")


def test_dashboard_card_renders_against_the_live_tree() -> None:
    """The dashboard card must actually render, not silently return None.

    Regression guard. An earlier revision of ``_complexity_health_card`` called a
    helper that does not exist in that module; its ``except Exception`` handler
    turned the resulting ``NameError`` into a quiet ``return None``, producing a
    dashboard surface that could never appear and reported nothing about why.

    Asserting only that the function does not raise would have passed against
    that bug. This asserts the card is produced and carries its counts, so a
    swallowed programming error cannot masquerade as a benign absence.
    """
    from scripts.gtkb_dashboard.refresh_dashboard_db import _complexity_health_card

    card = _complexity_health_card()
    assert card is not None, "complexity card returned None against the live tree"
    assert card["label"] == "Platform Complexity"
    assert card["status"] == "info", "counts carry no threshold, so status must not imply one"
    assert "state locations" in card["tooltip"].lower()
    assert "WI-6746" in card["tooltip"]
