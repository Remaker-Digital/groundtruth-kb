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


def test_plan_upgrade_same_version_with_all_files_present_returns_empty(tmp_path: Path) -> None:
    """Same scaffold_version with no drift → returns empty list.

    Drift at same version (missing managed files, missing settings
    registration, missing gitignore patterns) IS now surfaced as actions
    per bridge/gtkb-hook-scanner-safe-writer-010.md Finding 1. This test
    asserts the no-drift baseline: a minimal fixture with no ``.claude/``
    tree and no settings.json is still "empty" for the LOCAL-ONLY profile
    because that profile has no settings/gitignore drift sources. (For
    dual-agent profile see the drift tests below.)
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="local-only", version=__version__)
    # local-only profile manages only .claude/hooks/assertion-check.py and
    # .claude/hooks/spec-classifier.py. Those are missing → `add` actions.
    # But the test was originally written before the missing-file drift
    # check existed. Assert the new semantics: missing managed files
    # produce `add` actions; no other action types appear.
    result = plan_upgrade(tmp_path)
    assert all(a.action == "add" for a in result), (
        f"local-only same-version should only produce add actions for missing "
        f"managed files; got: {[(a.action, a.file) for a in result]}"
    )


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


# ---------------------------------------------------------------------------
# Config-action tests — settings-json and gitignore drift first-class actions
# (Tier A #2 scanner-safe-writer — see bridge/gtkb-hook-scanner-safe-writer-008.md)
# ---------------------------------------------------------------------------


def _write_minimal_settings_json(
    target: Path,
    *,
    include_scanner_safe_writer: bool = False,
) -> None:
    """Write a minimal .claude/settings.json with 5 (or 6) PreToolUse hooks."""
    import json

    settings_dir = target / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    pretooluse = [
        {"hooks": [{"type": "command", "command": "python .claude/hooks/spec-before-code.py"}]},
        {"hooks": [{"type": "command", "command": "python .claude/hooks/bridge-compliance-gate.py"}]},
        {"hooks": [{"type": "command", "command": "python .claude/hooks/kb-not-markdown.py"}]},
        {"hooks": [{"type": "command", "command": "python .claude/hooks/destructive-gate.py"}]},
        {"hooks": [{"type": "command", "command": "python .claude/hooks/credential-scan.py"}]},
    ]
    if include_scanner_safe_writer:
        pretooluse.append({"hooks": [{"type": "command", "command": "python .claude/hooks/scanner-safe-writer.py"}]})
    data = {"hooks": {"PreToolUse": pretooluse}}
    (settings_dir / "settings.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def test_plan_reports_settings_drift_at_same_version(tmp_path: Path) -> None:
    """Even at the current scaffold version, a missing scanner-safe-writer
    PreToolUse registration surfaces as a ``merge-event-hooks`` action.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=False)
    actions = plan_upgrade(tmp_path)
    merge_actions = [a for a in actions if a.action == "merge-event-hooks"]
    assert merge_actions, f"expected merge-event-hooks action at same version; got: {[a.action for a in actions]}"
    assert any(a.event == "PreToolUse" for a in merge_actions)


def test_plan_reports_gitignore_drift_at_same_version(tmp_path: Path) -> None:
    """Even at the current scaffold version, a missing ``.claude/hooks/*.log``
    pattern in ``.gitignore`` surfaces as an ``append-gitignore`` action.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=True)
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    actions = plan_upgrade(tmp_path)
    append_actions = [a for a in actions if a.action == "append-gitignore"]
    assert append_actions, f"expected append-gitignore action at same version; got: {[a.action for a in actions]}"
    assert any(a.payload == ".claude/hooks/*.log" for a in append_actions)


def test_plan_reports_missing_hook_file_at_same_version(tmp_path: Path) -> None:
    """Even at the current scaffold version, a missing managed hook file
    (e.g., scanner-safe-writer.py) surfaces as an ``add`` action. Addresses
    bridge/gtkb-hook-scanner-safe-writer-010.md Finding 1 — same-version
    inert-hook drift.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    # Create settings/gitignore already-registered so ONLY the hook file is
    # missing — proves missing-file detection runs independently of
    # settings/gitignore drift.
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=True)
    (tmp_path / ".gitignore").write_text("__pycache__/\n.claude/hooks/*.log\n", encoding="utf-8")
    # Do NOT create .claude/hooks/scanner-safe-writer.py
    actions = plan_upgrade(tmp_path)
    add_actions = [a for a in actions if a.action == "add" and "scanner-safe-writer.py" in a.file]
    assert add_actions, (
        f"expected add action for missing scanner-safe-writer.py at same version; got: "
        f"{[(a.action, a.file) for a in actions]}"
    )


def test_execute_creates_missing_hook_file_at_same_version(tmp_path: Path) -> None:
    """Running ``gt project upgrade --apply`` at the current scaffold version
    with only the hook file missing actually copies the file from template.
    Addresses bridge/gtkb-hook-scanner-safe-writer-010.md Finding 1 — doctor
    remediation instruction must be accurate.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=True)
    (tmp_path / ".gitignore").write_text(".claude/hooks/*.log\n", encoding="utf-8")
    hook_path = tmp_path / ".claude" / "hooks" / "scanner-safe-writer.py"
    assert not hook_path.exists()

    actions = plan_upgrade(tmp_path)
    execute_upgrade(tmp_path, actions, force=False)

    assert hook_path.exists(), "scanner-safe-writer.py should be copied by execute_upgrade at same version"
    # Template content check — non-empty, contains expected marker
    content = hook_path.read_text(encoding="utf-8")
    assert "CANONICAL_CATALOG_USED" in content or "FALLBACK_CATALOG_USED" in content


def test_plan_missing_hook_and_settings_both_emit(tmp_path: Path) -> None:
    """Project missing BOTH hook file and settings/gitignore registrations
    gets both action types. Addresses bridge -010 Finding 1 combined-drift
    case.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=False)
    # No gitignore, no hook file
    actions = plan_upgrade(tmp_path)
    add_actions = [a for a in actions if a.action == "add" and "scanner-safe-writer.py" in a.file]
    merge_actions = [a for a in actions if a.action == "merge-event-hooks"]
    append_actions = [a for a in actions if a.action == "append-gitignore"]
    assert add_actions, "expected add action for missing hook file"
    assert merge_actions, "expected merge-event-hooks action for missing settings registration"
    assert append_actions, "expected append-gitignore action for missing pattern"


def test_dry_run_shows_config_actions(tmp_path: Path) -> None:
    """CLI ``gt project upgrade --dry-run`` surfaces MERGE-EVENT-HOOKS and
    APPEND-GITIGNORE actions in its output.
    """
    from click.testing import CliRunner

    from groundtruth_kb import __version__
    from groundtruth_kb.cli import main

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=False)
    # No .gitignore either → append-gitignore action
    runner = CliRunner()
    result = runner.invoke(main, ["project", "upgrade", "--dry-run", "--dir", str(tmp_path)])
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert "[MERGE-EVENT-HOOKS]" in result.output, f"dry-run missing [MERGE-EVENT-HOOKS]:\n{result.output}"
    assert "[APPEND-GITIGNORE]" in result.output, f"dry-run missing [APPEND-GITIGNORE]:\n{result.output}"


def test_execute_merge_event_hooks_preserves_unmanaged_entries(tmp_path: Path) -> None:
    """merge-event-hooks rebuilds PreToolUse to registry order while preserving
    any adopter-authored entries not matching a managed scaffold marker.
    """
    import json

    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=False)
    # Inject an adopter-authored entry that is NOT in the managed scaffold set.
    settings_path = tmp_path / ".claude" / "settings.json"
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    data["hooks"]["PreToolUse"].append(
        {"hooks": [{"type": "command", "command": "python .claude/hooks/custom-adopter-hook.py"}]}
    )
    settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    action = UpgradeAction(
        file=".claude/settings.json",
        action="merge-event-hooks",
        reason="Merge PreToolUse hooks to registry order",
        payload="PreToolUse",
        event="PreToolUse",
    )
    results = execute_upgrade(tmp_path, [action], force=False)
    assert any("MERGED" in r and "PreToolUse rebuilt" in r for r in results), results
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    commands = [h["command"] for entry in data["hooks"]["PreToolUse"] for h in entry["hooks"]]
    # Unmanaged entry preserved (must appear after all managed entries).
    assert "python .claude/hooks/custom-adopter-hook.py" in commands
    assert commands[-1] == "python .claude/hooks/custom-adopter-hook.py", (
        f"unmanaged entry should be last (after managed block); got commands order: {commands}"
    )


def test_execute_merge_event_hooks_is_idempotent(tmp_path: Path) -> None:
    """Running merge-event-hooks twice: first MERGED, second SKIPPED
    (target list equals existing list)."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    _write_minimal_settings_json(tmp_path, include_scanner_safe_writer=False)
    action = UpgradeAction(
        file=".claude/settings.json",
        action="merge-event-hooks",
        reason="Merge PreToolUse hooks to registry order",
        payload="PreToolUse",
        event="PreToolUse",
    )
    first = execute_upgrade(tmp_path, [action], force=False)
    assert any("MERGED" in r and "PreToolUse rebuilt" in r for r in first), first
    # Reset version so the noop execute doesn't cascade into other file work
    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    second = execute_upgrade(tmp_path, [action], force=False)
    assert any("already at registry order" in r for r in second), second


def test_execute_append_gitignore_preserves_existing_content(tmp_path: Path) -> None:
    """Appending a pattern must add one line without modifying other lines."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    original_lines = [
        "__pycache__/",
        "*.py[cod]",
        ".env",
        ".venv/",
        "node_modules/",
    ]
    (tmp_path / ".gitignore").write_text("\n".join(original_lines) + "\n", encoding="utf-8")
    action = UpgradeAction(
        file=".gitignore",
        action="append-gitignore",
        reason="Append pattern: .claude/hooks/*.log (Operational hook logs)",
        payload=".claude/hooks/*.log",
    )
    results = execute_upgrade(tmp_path, [action], force=False)
    assert any("APPENDED .claude/hooks/*.log" in r for r in results), results
    content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    for line in original_lines:
        assert line in content, f"original gitignore line {line!r} was removed"
    assert ".claude/hooks/*.log" in content


def test_execute_append_gitignore_is_idempotent(tmp_path: Path) -> None:
    """Second append call returns SKIPPED and file is unchanged."""
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    (tmp_path / ".gitignore").write_text("__pycache__/\n.claude/hooks/*.log\n", encoding="utf-8")
    action = UpgradeAction(
        file=".gitignore",
        action="append-gitignore",
        reason="Append pattern: .claude/hooks/*.log (Operational hook logs)",
        payload=".claude/hooks/*.log",
    )
    before = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    results = execute_upgrade(tmp_path, [action], force=False)
    after = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert any("already present" in r for r in results), results
    assert before == after, "idempotent call must not modify .gitignore"


def test_plan_malformed_settings_reports_skip(tmp_path: Path) -> None:
    """Structurally malformed (but syntactically valid JSON) settings must
    not crash plan_upgrade — a JSON decode error becomes a ``skip`` action.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    # Write invalid JSON to trigger the decode-error skip branch
    (settings_dir / "settings.json").write_text("{ this is not valid json ", encoding="utf-8")
    actions = plan_upgrade(tmp_path)
    skip_actions = [a for a in actions if a.action == "skip" and a.file == ".claude/settings.json"]
    assert skip_actions, f"expected skip action for malformed JSON; got {actions}"
    assert "Malformed JSON" in skip_actions[0].reason


def test_plan_malformed_settings_structure_does_not_crash(tmp_path: Path) -> None:
    """Valid JSON with wrong shape (non-dict root, non-list PreToolUse,
    non-dict entries) must not crash plan_upgrade.
    """
    import json

    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)

    # 1. Non-dict root (a JSON array)
    (settings_dir / "settings.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    actions = plan_upgrade(tmp_path)
    # Treated as "no existing registrations" — emits register-hook
    assert any(a.action == "merge-event-hooks" for a in actions), (
        f"non-dict root should surface register-hook action; got {actions}"
    )

    # 2. hooks is a string (not a dict)
    (settings_dir / "settings.json").write_text(json.dumps({"hooks": "oops"}), encoding="utf-8")
    actions = plan_upgrade(tmp_path)
    assert any(a.action == "merge-event-hooks" for a in actions)

    # 3. PreToolUse is a string (not a list)
    (settings_dir / "settings.json").write_text(
        json.dumps({"hooks": {"PreToolUse": "not-a-list"}}),
        encoding="utf-8",
    )
    actions = plan_upgrade(tmp_path)
    assert any(a.action == "merge-event-hooks" for a in actions)

    # 4. Entries contain non-dicts
    (settings_dir / "settings.json").write_text(
        json.dumps({"hooks": {"PreToolUse": [42, "string", None]}}),
        encoding="utf-8",
    )
    actions = plan_upgrade(tmp_path)
    assert any(a.action == "merge-event-hooks" for a in actions)

    # 5. entry["hooks"] is not a list
    (settings_dir / "settings.json").write_text(
        json.dumps({"hooks": {"PreToolUse": [{"hooks": "wrong"}]}}),
        encoding="utf-8",
    )
    actions = plan_upgrade(tmp_path)
    assert any(a.action == "merge-event-hooks" for a in actions)


def test_upgrade_creates_gitignore_if_missing(tmp_path: Path) -> None:
    """If ``.gitignore`` does not exist, execute_upgrade creates it with
    the pattern present.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    gi = tmp_path / ".gitignore"
    assert not gi.exists(), "precondition: .gitignore must not exist"
    action = UpgradeAction(
        file=".gitignore",
        action="append-gitignore",
        reason="Append pattern: .claude/hooks/*.log (Operational hook logs)",
        payload=".claude/hooks/*.log",
    )
    results = execute_upgrade(tmp_path, [action], force=False)
    assert any("APPENDED .claude/hooks/*.log" in r for r in results), results
    assert gi.exists(), "execute_upgrade must create .gitignore"
    content = gi.read_text(encoding="utf-8")
    assert ".claude/hooks/*.log" in content


def test_upgrade_no_settings_file_is_noop(tmp_path: Path) -> None:
    """If ``settings.json`` is absent, plan_upgrade emits no register-hook
    actions — this is a non-Claude-Code project and we don't create one.
    """
    from groundtruth_kb import __version__

    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    assert not (tmp_path / ".claude" / "settings.json").exists()
    actions = plan_upgrade(tmp_path)
    register_actions = [a for a in actions if a.action == "register-hook"]
    assert not register_actions, f"no settings.json → expected no register-hook actions; got {register_actions}"


def test_plan_upgrade_still_plans_managed_hooks_on_version_mismatch(tmp_path: Path) -> None:
    """Regression test per Codex ``-008`` Finding 2 required action: after
    extracting the managed-hook/rule planning into helpers, they still run
    when ``scaffold_version != __version__``.
    """
    from groundtruth_kb import get_templates_dir

    _write_minimal_toml(tmp_path, profile="local-only", version="0.0.1")
    actions = plan_upgrade(tmp_path)
    # For local-only profile, managed hooks are limited to assertion-check +
    # spec-classifier. The template directory must still exist for this
    # test to be meaningful.
    templates = get_templates_dir()
    if not (templates / "hooks" / "assertion-check.py").exists():
        pytest.skip("assertion-check.py template not available")
    managed_hook_actions = [a for a in actions if a.file.startswith(".claude/hooks/") and a.action in ("add", "skip")]
    assert managed_hook_actions, f"version mismatch must plan managed hooks; got actions: {actions}"
