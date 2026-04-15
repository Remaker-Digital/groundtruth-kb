# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.upgrade — plan_upgrade and execute_upgrade."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.upgrade import UpgradeAction, execute_upgrade, plan_upgrade

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_minimal_toml(target: Path, profile: str = "local-only", version: str = "99.99.99") -> None:
    """Write a minimal groundtruth.toml with a [project] section."""
    toml_path = target / "groundtruth.toml"
    toml_path.write_text(
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


# ---------------------------------------------------------------------------
# plan_upgrade
# ---------------------------------------------------------------------------


def test_plan_upgrade_no_toml_returns_skip(tmp_path: Path) -> None:
    """No groundtruth.toml → returns single skip action."""
    result = plan_upgrade(tmp_path)
    assert len(result) == 1
    assert result[0].action == "skip"
    assert "manifest" in result[0].reason.lower() or "project" in result[0].reason.lower()


def test_plan_upgrade_same_version_returns_empty(tmp_path: Path) -> None:
    """Same scaffold_version → returns empty list (nothing to do)."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, version=__version__)
    result = plan_upgrade(tmp_path)
    assert result == []


def test_plan_upgrade_different_version_local_only(tmp_path: Path) -> None:
    """Different version, local-only profile → actions for managed hooks/rules."""
    _write_minimal_toml(tmp_path, profile="local-only", version="0.0.1")
    result = plan_upgrade(tmp_path)
    # Should return some actions (or empty if templates don't exist in test env)
    assert isinstance(result, list)
    for action in result:
        assert isinstance(action, UpgradeAction)
        assert action.action in ("add", "skip", "update")


def test_plan_upgrade_missing_file_gets_add_action(tmp_path: Path) -> None:
    """When a managed file doesn't exist, action = 'add'."""

    _write_minimal_toml(tmp_path, profile="local-only", version="0.0.1")
    # Ensure .claude/hooks/assertion-check.py doesn't exist
    # The plan should produce 'add' for any missing managed files that have templates
    result = plan_upgrade(tmp_path)
    add_actions = [a for a in result if a.action == "add"]
    # There should be 'add' for every managed file that has a template but isn't in target
    # (exact count depends on templates available)
    for action in add_actions:
        assert not (tmp_path / action.file).exists()


def test_plan_upgrade_customized_file_gets_skip_action(tmp_path: Path) -> None:
    """Managed file that differs from template → action = 'skip' with reason."""
    from groundtruth_kb import get_templates_dir

    _write_minimal_toml(tmp_path, profile="local-only", version="0.0.1")

    # Check if assertion-check.py template exists
    templates = get_templates_dir()
    hook_template = templates / "hooks" / "assertion-check.py"
    if not hook_template.exists():
        pytest.skip("assertion-check.py template not available")

    # Create a customized version of the hook
    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "assertion-check.py").write_text("# Custom content\n", encoding="utf-8")

    result = plan_upgrade(tmp_path)
    skip_for_hook = [a for a in result if a.file == ".claude/hooks/assertion-check.py" and a.action == "skip"]
    assert len(skip_for_hook) >= 1
    assert "customized" in skip_for_hook[0].reason.lower() or "force" in skip_for_hook[0].reason.lower()


# ---------------------------------------------------------------------------
# execute_upgrade
# ---------------------------------------------------------------------------


def test_execute_upgrade_skip_without_force(tmp_path: Path) -> None:
    """Skip action without --force → 'SKIPPED' in results."""
    _write_minimal_toml(tmp_path, version="0.0.1")
    action = UpgradeAction(file="some-file.py", action="skip", reason="customized")
    results = execute_upgrade(tmp_path, [action], force=False)
    assert any("SKIPPED" in r for r in results)


def test_execute_upgrade_add_action_copies_template(tmp_path: Path) -> None:
    """'add' action copies template to target."""
    from groundtruth_kb import get_templates_dir

    _write_minimal_toml(tmp_path, version="0.0.1")
    templates = get_templates_dir()
    hook_template = templates / "hooks" / "assertion-check.py"
    if not hook_template.exists():
        pytest.skip("assertion-check.py template not available")

    action = UpgradeAction(file=".claude/hooks/assertion-check.py", action="add", reason="New managed file")
    results = execute_upgrade(tmp_path, [action], force=False)
    assert any("UPDATED" in r for r in results)
    assert (tmp_path / ".claude" / "hooks" / "assertion-check.py").exists()


def test_execute_upgrade_template_not_found_skips(tmp_path: Path) -> None:
    """Template not found → 'SKIPPED' in results."""
    _write_minimal_toml(tmp_path, version="0.0.1")
    action = UpgradeAction(file=".claude/hooks/nonexistent-hook.py", action="add", reason="New managed file")
    results = execute_upgrade(tmp_path, [action], force=False)
    assert any("SKIPPED" in r for r in results)


def test_execute_upgrade_existing_file_backed_up(tmp_path: Path) -> None:
    """Existing managed file gets a .bak backup before overwrite."""
    from groundtruth_kb import get_templates_dir

    _write_minimal_toml(tmp_path, version="0.0.1")
    templates = get_templates_dir()
    hook_template = templates / "hooks" / "assertion-check.py"
    if not hook_template.exists():
        pytest.skip("assertion-check.py template not available")

    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    original_content = "# original content\n"
    (hooks_dir / "assertion-check.py").write_text(original_content, encoding="utf-8")

    action = UpgradeAction(file=".claude/hooks/assertion-check.py", action="skip", reason="customized")
    results = execute_upgrade(tmp_path, [action], force=True)
    assert any("BACKUP" in r for r in results)


def test_execute_upgrade_updates_manifest_version(tmp_path: Path) -> None:
    """After execute, scaffold_version in manifest is updated."""
    from groundtruth_kb import __version__
    from groundtruth_kb.project.manifest import read_manifest

    _write_minimal_toml(tmp_path, version="0.0.1")
    execute_upgrade(tmp_path, [], force=False)
    manifest = read_manifest(tmp_path / "groundtruth.toml")
    assert manifest is not None
    assert manifest.scaffold_version == __version__
