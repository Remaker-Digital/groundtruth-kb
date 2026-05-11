"""Tests for ``scripts/scaffold_upgrade_tier_a_apply.py``.

Per bridge ``gtkb-scaffold-upgrade-tier-a-009.md`` GO at ``-010``.

Six test cases covering:
    - filter correctness (KEPT_ACTION_KINDS and apply_tier_a filtering)
    - plan-count summary helper
    - JSON-safe action serialization
    - dry-run preserves manifest version (no execute_upgrade call)
    - applier propagates ``update_manifest=False`` + ``enforce_isolation=False``
    - ``main`` returns 0 on dry-run and emits valid JSON

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "scaffold_upgrade_tier_a_apply.py"

# Ensure groundtruth_kb is importable BEFORE loading the applier module,
# since the applier's top-level imports the package.
_GTKB_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(_GTKB_SRC))

_spec = importlib.util.spec_from_file_location("scaffold_upgrade_tier_a_apply", SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
applier = importlib.util.module_from_spec(_spec)
sys.modules["scaffold_upgrade_tier_a_apply"] = applier
_spec.loader.exec_module(applier)

from groundtruth_kb.project.upgrade import UpgradeAction  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers — fixture adopter project for the dry-run integration test.
# ---------------------------------------------------------------------------


def _write_minimal_toml(target: Path, version: str = "0.0.1") -> None:
    toml_path = target / "groundtruth.toml"
    toml_path.write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test Owner"
profile = "local-only"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{version}"
created_at = "2026-01-01T00:00:00Z"
""",
        encoding="utf-8",
    )


def _setup_git_clean_tree(target: Path) -> None:
    """Initialize a clean git tree at ``target`` so execute_upgrade preconditions pass."""
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=target, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial", "--allow-empty"],
        cwd=target,
        check=True,
        capture_output=True,
    )


# ---------------------------------------------------------------------------
# Test 1 — filter correctness via the KEPT_ACTION_KINDS constant.
# ---------------------------------------------------------------------------


def test_kept_action_kinds_constant_matches_tier_a_scope() -> None:
    """Tier A scope per bridge -009: ADD + APPEND-GITIGNORE only.

    Per bridge ``gtkb-scaffold-upgrade-tier-a-009.md`` SCOPE section:
        IN SCOPE: 12 ADD targets, 3 APPEND-GITIGNORE patterns.
        OUT OF SCOPE: 4 MERGE-EVENT-HOOKS, 13 SKIP, 34 in-flight WARNING.
    """
    assert applier.KEPT_ACTION_KINDS == frozenset({"add", "append-gitignore"})


# ---------------------------------------------------------------------------
# Test 2 — _summarize_plan helper produces the expected count shape.
# ---------------------------------------------------------------------------


def test_summarize_plan_counts_helper() -> None:
    actions = [
        UpgradeAction(file="a.py", action="add", reason="missing"),
        UpgradeAction(file="b.py", action="add", reason="missing"),
        UpgradeAction(file=".gitignore", action="append-gitignore", reason="pattern", payload="*.tmp"),
        UpgradeAction(file="settings.json", action="merge-event-hooks", reason="missing entries", event="PreToolUse"),
        UpgradeAction(file="c.py", action="skip", reason="customized"),
        UpgradeAction(file="preflight", action="warning", reason="bridge in flight"),
    ]
    counts = applier._summarize_plan(actions)
    assert counts["add"] == 2
    assert counts["append-gitignore"] == 1
    assert counts["merge-event-hooks"] == 1
    assert counts["skip"] == 1
    assert counts["warning"] == 1
    assert counts["total"] == 6


# ---------------------------------------------------------------------------
# Test 3 — apply_tier_a filters non-Tier-A actions in dry-run.
# ---------------------------------------------------------------------------


def test_apply_tier_a_filters_only_add_and_append_gitignore(tmp_path: Path) -> None:
    _write_minimal_toml(tmp_path, version="0.0.1")
    _setup_git_clean_tree(tmp_path)

    mixed_actions = [
        UpgradeAction(file=".claude/hooks/a.py", action="add", reason="missing"),
        UpgradeAction(file=".claude/hooks/b.py", action="add", reason="missing"),
        UpgradeAction(file=".gitignore", action="append-gitignore", reason="pattern", payload="*.bak"),
        UpgradeAction(file=".claude/settings.json", action="merge-event-hooks", reason="missing", event="PreToolUse"),
        UpgradeAction(file=".claude/rules/x.md", action="skip", reason="customized"),
        UpgradeAction(file="<preflight>", action="warning", reason="bridge in flight"),
    ]
    with patch.object(applier, "plan_upgrade", return_value=mixed_actions):
        output = applier.apply_tier_a(tmp_path, dry_run=True)

    assert output["kept_action_count"] == 3  # 2 add + 1 append-gitignore
    kinds_in_output = {a["action"] for a in output["kept_actions"]}
    assert kinds_in_output == {"add", "append-gitignore"}
    # The non-Tier-A kinds remain visible in the plan_counts summary even
    # though they are not in kept_actions.
    assert output["plan_counts"]["merge-event-hooks"] == 1
    assert output["plan_counts"]["skip"] == 1
    assert output["plan_counts"]["warning"] == 1


# ---------------------------------------------------------------------------
# Test 4 — dry-run does NOT call execute_upgrade and preserves manifest.
# ---------------------------------------------------------------------------


def test_dry_run_preserves_manifest_and_skips_execute_upgrade(tmp_path: Path) -> None:
    _write_minimal_toml(tmp_path, version="0.6.1")
    _setup_git_clean_tree(tmp_path)

    with patch.object(applier, "plan_upgrade", return_value=[]) as mock_plan, \
         patch.object(applier, "execute_upgrade") as mock_execute:
        output = applier.apply_tier_a(tmp_path, dry_run=True)

    assert mock_plan.called
    assert not mock_execute.called, "dry-run must not call execute_upgrade"
    assert output["dry_run"] is True
    assert output["pre_manifest_version"] == "0.6.1"
    assert output["post_manifest_version"] == "0.6.1"
    assert output["applier_results"] is None


# ---------------------------------------------------------------------------
# Test 5 — applier propagates the required execute_upgrade flags.
# ---------------------------------------------------------------------------


def test_apply_calls_execute_upgrade_with_correct_flags(tmp_path: Path) -> None:
    """Per bridge -009: execute_upgrade(enforce_isolation=False, update_manifest=False, force=False)."""
    _write_minimal_toml(tmp_path, version="0.6.1")
    _setup_git_clean_tree(tmp_path)

    one_add = [UpgradeAction(file=".claude/hooks/a.py", action="add", reason="missing")]

    with patch.object(applier, "plan_upgrade", return_value=one_add), \
         patch.object(applier, "execute_upgrade", return_value=["ADDED .claude/hooks/a.py"]) as mock_execute:
        output = applier.apply_tier_a(tmp_path, dry_run=False)

    assert mock_execute.called
    _, kwargs = mock_execute.call_args
    assert kwargs["force"] is False, "applier must call execute_upgrade with force=False"
    assert kwargs["enforce_isolation"] is False, (
        "applier must call execute_upgrade with enforce_isolation=False per bridge -009 scope"
    )
    assert kwargs["update_manifest"] is False, (
        "applier must call execute_upgrade with update_manifest=False to preserve SKIP=13 for Tier C"
    )
    assert output["applier_results"] == ["ADDED .claude/hooks/a.py"]


# ---------------------------------------------------------------------------
# Test 6 — main() returns 0 on dry-run and emits valid JSON to stdout.
# ---------------------------------------------------------------------------


def test_main_dry_run_emits_valid_json_and_exits_zero(tmp_path: Path) -> None:
    _write_minimal_toml(tmp_path, version="0.6.1")
    _setup_git_clean_tree(tmp_path)

    buf = io.StringIO()
    with patch.object(applier, "plan_upgrade", return_value=[]), \
         patch.object(sys, "stdout", buf):
        exit_code = applier.main(["--target", str(tmp_path), "--dry-run"])

    assert exit_code == 0
    payload = json.loads(buf.getvalue())
    assert payload["target"] == str(tmp_path)
    assert payload["dry_run"] is True
    assert payload["pre_manifest_version"] == "0.6.1"
    assert "plan_counts" in payload
    assert "kept_actions" in payload
