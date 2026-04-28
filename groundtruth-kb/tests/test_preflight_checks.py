# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for Area 5 upgrade pre-flight checks (bridge ``gtkb-upgrade-pre-flight-checks``).

Covers all five Codex conditions from
``bridge/gtkb-upgrade-pre-flight-checks-implementation-002.md``:

- **C1** — non-mutating ``warning`` / ``informational`` action kinds never
  trigger git or file writes, even with ``--force``.
- **C2** — ``MalformedSettingsError`` raises before any git/file work in
  ``execute_upgrade``; dry-run preserves the diagnostic skip row; CLI
  exits 4.
- **C3** — ``_check_bridge_inflight`` parses by ``Document:`` and inspects
  only the first status line per block; older statuses under a terminal
  ``VERIFIED``/``NO-GO`` are silent.
- **C4** — ``enumerate_scaffold_outputs`` is read-only, profile+registry-
  guaranteed only, and ``_check_scaffold_coverage`` performs no target
  writes.
- **C5** — CLI label surface (``[WARNING]``, ``[INFORMATIONAL]``) and
  ``--ignore-inflight-bridges`` flag wiring.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.project.preflight import (
    _check_bridge_inflight,
    _check_scaffold_coverage,
)
from groundtruth_kb.project.scaffold import enumerate_scaffold_outputs
from groundtruth_kb.project.upgrade import (
    _NON_MUTATING_ACTION_KINDS,
    MalformedSettingsError,
    UpgradeAction,
    _has_malformed_settings_skip,
    execute_upgrade,
    plan_upgrade,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_minimal_toml(target: Path, *, profile: str = "local-only", version: str = "0.0.1") -> None:
    (target / "groundtruth.toml").write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test Owner"
profile = "{profile}"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{version}"
created_at = "2026-01-01T00:00:00Z"
""",
        encoding="utf-8",
    )


def _init_git_repo_with_snapshot(target: Path) -> None:
    """Initialize a git repo and commit the current tree so apply preconditions pass."""
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=target, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(
        ["git", "commit", "-m", "pre-upgrade snapshot", "--allow-empty"],
        cwd=target,
        check=True,
        capture_output=True,
    )


def _snapshot_file_tree(root: Path) -> dict[str, bytes]:
    """Capture every file under *root* as a {relpath: bytes} dict for exact-equality comparison."""
    tree: dict[str, bytes] = {}
    for p in root.rglob("*"):
        if p.is_file():
            tree[str(p.relative_to(root)).replace("\\", "/")] = p.read_bytes()
    return tree


# ---------------------------------------------------------------------------
# C1 — non-mutating action kinds never trigger git or file writes
# ---------------------------------------------------------------------------


def test_C1_non_mutating_action_constants_expose_warning_and_informational() -> None:
    """The filter set used by the CLI must contain exactly the two pre-flight kinds."""
    assert frozenset({"warning", "informational"}) == _NON_MUTATING_ACTION_KINDS


def test_C1_execute_upgrade_never_called_for_warning_only_plan(tmp_path: Path) -> None:
    """CLI with only warning/informational rows → execute_upgrade never invoked;
    no git needed; no files written. This is the structural proof for C1."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="local-only", version=__version__)
    # Stub every managed file (hook / rule / skill) for local-only so that the
    # drift check produces zero ``add`` actions. Informational coverage rows
    # will still appear (those are fine — they're non-mutating pre-flight).
    for p in enumerate_scaffold_outputs("local-only"):
        if p.startswith((".claude/hooks/", ".claude/rules/", ".claude/skills/")):
            full = tmp_path / p
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text("# stub\n", encoding="utf-8")

    (tmp_path / "bridge").mkdir(parents=True, exist_ok=True)
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "Document: test-inflight\nNEW: bridge/test-inflight-001.md\n",
        encoding="utf-8",
    )

    # Confirm plan produces only non-mutating rows before running the CLI.
    planned = plan_upgrade(tmp_path)
    non_mutating = {"warning", "informational"}
    mutating_rows = [a for a in planned if a.action not in non_mutating]
    assert mutating_rows == [], (
        f"test setup must leave zero mutating rows; got {[(a.action, a.file) for a in mutating_rows]}"
    )

    # NOT a git repo — proves execute_upgrade never ran (would have raised
    # NotAGitRepositoryError otherwise).
    snapshot_before = _snapshot_file_tree(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["project", "upgrade", "--apply", "--dir", str(tmp_path), "--force"])

    assert result.exit_code == 0, f"exit code {result.exit_code}; output:\n{result.output}"
    assert "Pre-flight only" in result.output
    # File tree byte-identical after apply — proves zero writes.
    assert _snapshot_file_tree(tmp_path) == snapshot_before


def test_C1_apply_file_actions_is_no_op_for_warning_even_with_force(tmp_path: Path) -> None:
    """Defense-in-depth: if execute_upgrade sees a warning action (via library caller),
    _apply_file_actions must no-op even under force=True."""
    _write_minimal_toml(tmp_path, profile="local-only", version="0.0.1")
    _init_git_repo_with_snapshot(tmp_path)

    warning = UpgradeAction(
        file=".claude/hooks/attacker-would-love-this.py",
        action="warning",
        reason="test payload pretending to need a template copy",
    )
    # Need at least one mutating action so execute_upgrade reaches the apply loop.
    mutating = UpgradeAction(
        file=".gitignore",
        action="append-gitignore",
        reason="force a real payload",
        payload="test-payload/",
    )
    results = execute_upgrade(tmp_path, [warning, mutating], force=True)

    assert not (tmp_path / ".claude" / "hooks" / "attacker-would-love-this.py").exists()
    assert any("WARNING" in r and "attacker-would-love-this.py" in r for r in results)


def test_C1_artifact_classes_touched_excludes_warning_and_informational(tmp_path: Path) -> None:
    """The rollback receipt's artifact_classes_touched must not include
    pre-flight kinds even if they somehow reach execute_upgrade."""
    from groundtruth_kb.project.upgrade import _artifact_classes_touched

    actions = [
        UpgradeAction(file="bridge/foo", action="warning", reason="r"),
        UpgradeAction(file=".claude/hooks/x.py", action="informational", reason="r"),
        UpgradeAction(file=".claude/hooks/y.py", action="add", reason="r"),
        UpgradeAction(file=".gitignore", action="append-gitignore", reason="r", payload="p/"),
    ]
    classes = _artifact_classes_touched(actions)
    assert "warning" not in classes
    assert "informational" not in classes
    assert "hook" in classes
    assert "gitignore-pattern" in classes


# ---------------------------------------------------------------------------
# C2 — malformed settings halts apply before any git/file work
# ---------------------------------------------------------------------------


def _make_malformed_skip() -> UpgradeAction:
    return UpgradeAction(
        file=".claude/settings.json",
        action="skip",
        reason="Malformed JSON — manual repair required",
    )


def test_C2_dry_run_still_shows_malformed_skip(tmp_path: Path) -> None:
    """Dry-run UX unchanged: malformed settings surfaces as a skip action."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text("{ not valid json ", encoding="utf-8")

    actions = plan_upgrade(tmp_path)
    assert any(
        a.action == "skip" and a.file == ".claude/settings.json" and "Malformed JSON" in a.reason for a in actions
    ), f"expected malformed-settings skip; got {[(a.action, a.file) for a in actions]}"


def test_C2_execute_upgrade_raises_malformed_settings_before_any_git(tmp_path: Path) -> None:
    """Malformed-settings halt fires BEFORE _require_git_repo — proves ordering."""
    # NOT a git repo. If the malformed halt did NOT run first,
    # NotAGitRepositoryError would raise instead.
    _write_minimal_toml(tmp_path, profile="dual-agent", version="0.0.1")
    actions = [_make_malformed_skip()]
    with pytest.raises(MalformedSettingsError) as excinfo:
        execute_upgrade(tmp_path, actions, force=False)
    assert excinfo.value.action.file == ".claude/settings.json"


def test_C2_has_malformed_settings_skip_helper_identifies_it() -> None:
    """Pure helper used by both CLI and execute_upgrade."""
    assert _has_malformed_settings_skip([]) is None
    assert _has_malformed_settings_skip([UpgradeAction(file="x", action="skip", reason="other")]) is None
    # Right file, right reason pattern → matched
    found = _has_malformed_settings_skip([_make_malformed_skip()])
    assert found is not None and found.file == ".claude/settings.json"
    # Different file → not matched
    assert (
        _has_malformed_settings_skip([UpgradeAction(file="other.json", action="skip", reason="Malformed JSON blah")])
        is None
    )


def test_C2_cli_malformed_settings_exits_code_4(tmp_path: Path) -> None:
    """CLI catches MalformedSettingsError and exits 4 (distinct from 2/3)."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text("{ not valid json ", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["project", "upgrade", "--apply", "--dir", str(tmp_path)])
    assert result.exit_code == 4, f"expected exit 4, got {result.exit_code}:\n{result.output}"
    assert "Malformed .claude/settings.json" in result.output


# ---------------------------------------------------------------------------
# C3 — in-flight parser uses latest-status-only semantics
# ---------------------------------------------------------------------------


def test_C3_empty_or_missing_index_is_silent(tmp_path: Path) -> None:
    assert _check_bridge_inflight(tmp_path) == []
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text("", encoding="utf-8")
    assert _check_bridge_inflight(tmp_path) == []


def test_C3_only_comments_no_warnings(tmp_path: Path) -> None:
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "<!-- intro comment -->\n<!-- another -->\n\n",
        encoding="utf-8",
    )
    assert _check_bridge_inflight(tmp_path) == []


@pytest.mark.parametrize("status", ["NEW", "REVISED", "GO"])
def test_C3_latest_non_terminal_status_emits_warning(tmp_path: Path, status: str) -> None:
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        f"Document: foo\n{status}: bridge/foo-001.md\n",
        encoding="utf-8",
    )
    warnings = _check_bridge_inflight(tmp_path)
    assert len(warnings) == 1
    assert warnings[0].action == "warning"
    assert warnings[0].file == "bridge/foo"
    assert status in warnings[0].reason


@pytest.mark.parametrize("status", ["VERIFIED", "NO-GO"])
def test_C3_latest_terminal_status_is_silent(tmp_path: Path, status: str) -> None:
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        f"Document: foo\n{status}: bridge/foo-002.md\nNEW: bridge/foo-001.md\n",
        encoding="utf-8",
    )
    assert _check_bridge_inflight(tmp_path) == []


def test_C3_older_new_below_terminal_verified_is_silent(tmp_path: Path) -> None:
    """Key C3 regression: NEW/REVISED/GO below a terminal VERIFIED/NO-GO must NOT warn."""
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "Document: closed-thread\n"
        "VERIFIED: bridge/closed-thread-004.md\n"
        "NEW: bridge/closed-thread-003.md\n"
        "GO: bridge/closed-thread-002.md\n"
        "REVISED: bridge/closed-thread-001.md\n",
        encoding="utf-8",
    )
    assert _check_bridge_inflight(tmp_path) == []


def test_C3_multiple_documents_mixed_terminal_and_active(tmp_path: Path) -> None:
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "<!-- header -->\n\n"
        "Document: closed-one\n"
        "VERIFIED: bridge/closed-one-002.md\n"
        "NEW: bridge/closed-one-001.md\n\n"
        "Document: active-one\n"
        "REVISED: bridge/active-one-003.md\n"
        "NO-GO: bridge/active-one-002.md\n"
        "NEW: bridge/active-one-001.md\n\n"
        "Document: closed-two\n"
        "NO-GO: bridge/closed-two-002.md\n"
        "NEW: bridge/closed-two-001.md\n",
        encoding="utf-8",
    )
    warnings = _check_bridge_inflight(tmp_path)
    assert [w.file for w in warnings] == ["bridge/active-one"]
    assert "REVISED" in warnings[0].reason


def test_C3_ignore_flag_suppresses_all(tmp_path: Path) -> None:
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "Document: foo\nNEW: bridge/foo-001.md\n",
        encoding="utf-8",
    )
    assert _check_bridge_inflight(tmp_path, ignore=True) == []


def test_C3_header_text_between_documents_tolerated(tmp_path: Path) -> None:
    """Markdown headers, table rows, and prose between Document: blocks must not trigger false status matches."""
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "# Bridge Index\n\n"
        "## Statuses\n\n"
        "| Status | Set by | Meaning |\n"
        "|--------|--------|---------|\n"
        "| NEW | Prime | Fresh proposal |\n"
        "| VERIFIED | Codex | Done |\n\n"
        "<!-- entries below -->\n\n"
        "Document: real-one\n"
        "NEW: bridge/real-one-001.md\n",
        encoding="utf-8",
    )
    warnings = _check_bridge_inflight(tmp_path)
    assert [w.file for w in warnings] == ["bridge/real-one"]


# ---------------------------------------------------------------------------
# C4 — scaffold enumerator is read-only, profile+registry-guaranteed only
# ---------------------------------------------------------------------------


def test_C4_enumerate_local_only_returns_stable_path_set() -> None:
    paths = set(enumerate_scaffold_outputs("local-only"))
    # Core paths present
    assert "groundtruth.toml" in paths
    assert "CLAUDE.md" in paths
    assert ".gitignore" in paths
    assert "pyproject.toml" in paths
    # Registry-backed hook path (one representative)
    assert any(p.startswith(".claude/hooks/") for p in paths)
    # local-only does NOT have bridge bootstrap
    assert "bridge/INDEX.md" not in paths
    assert "AGENTS.md" not in paths
    # local-only does NOT have docker
    assert "Dockerfile" not in paths


def test_C4_enumerate_dual_agent_adds_bridge_bootstrap() -> None:
    paths = set(enumerate_scaffold_outputs("dual-agent"))
    assert "bridge/INDEX.md" in paths
    assert "AGENTS.md" in paths
    assert ".claude/settings.json" in paths
    assert ".claude/settings.local.json" in paths
    # dual-agent still no docker
    assert "Dockerfile" not in paths


def test_C4_enumerate_dual_agent_webapp_adds_docker() -> None:
    paths = set(enumerate_scaffold_outputs("dual-agent-webapp"))
    assert "bridge/INDEX.md" in paths
    assert "Dockerfile" in paths
    assert "docker-compose.yml" in paths
    assert ".env.example" in paths


def test_C4_enumerate_excludes_option_dependent_paths() -> None:
    """Paths gated on non-persisted scaffold options must NOT appear."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        paths = set(enumerate_scaffold_outputs(profile))
        # CI workflows (options.include_ci)
        assert not any(p.startswith(".github/workflows/") for p in paths), profile
        # Seed example (options.seed_example)
        assert "src/tasks.py" not in paths, profile


def test_C4_enumerate_unknown_profile_raises() -> None:
    with pytest.raises(ValueError):
        enumerate_scaffold_outputs("not-a-real-profile")


def test_C4_coverage_check_is_read_only(tmp_path: Path) -> None:
    """_check_scaffold_coverage must not touch any file in target."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version="0.0.1")
    (tmp_path / "pre-existing.txt").write_text("keep me\n", encoding="utf-8")
    before = _snapshot_file_tree(tmp_path)
    _check_scaffold_coverage(tmp_path, "dual-agent")
    after = _snapshot_file_tree(tmp_path)
    assert after == before, "coverage check modified target tree"


def test_C4_coverage_check_emits_informational_for_uncovered(tmp_path: Path) -> None:
    """Coverage delta reports at least one non-registry-managed scaffold output."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version="0.0.1")
    rows = _check_scaffold_coverage(tmp_path, "dual-agent")
    assert len(rows) > 0, "expected uncovered-path reporting for dual-agent profile"
    for r in rows:
        assert r.action == "informational"
        assert "gt project init" in r.reason


def test_C4_coverage_check_unknown_profile_emits_info_not_crash(tmp_path: Path) -> None:
    _write_minimal_toml(tmp_path, profile="not-a-real-profile", version="0.0.1")
    rows = _check_scaffold_coverage(tmp_path, "not-a-real-profile")
    assert len(rows) == 1
    assert rows[0].action == "informational"
    assert "unknown profile" in rows[0].reason


# ---------------------------------------------------------------------------
# C5 — CLI labels and flag wiring
# ---------------------------------------------------------------------------


def test_C5_cli_dry_run_shows_warning_and_informational_labels(tmp_path: Path) -> None:
    """dry-run output renders pre-flight rows with [WARNING] / [INFORMATIONAL] prefixes."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "Document: some-thread\nNEW: bridge/some-thread-001.md\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(main, ["project", "upgrade", "--dry-run", "--dir", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "[WARNING]" in result.output
    assert "[INFORMATIONAL]" in result.output


def test_C5_cli_ignore_flag_suppresses_warning(tmp_path: Path) -> None:
    """--ignore-inflight-bridges removes the [WARNING] line for in-flight bridges."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "Document: some-thread\nNEW: bridge/some-thread-001.md\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "project",
            "upgrade",
            "--dry-run",
            "--dir",
            str(tmp_path),
            "--ignore-inflight-bridges",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "In-flight bridge" not in result.output
