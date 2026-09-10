"""Owner conversation remains in session logs, without an automatic ledger."""

from __future__ import annotations

import json

import pytest

from groundtruth_kb.project.doctor import _check_managed_artifact_drift
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project
from groundtruth_kb.project.upgrade import _apply_file_actions, _plan_settings_registration


@pytest.mark.parametrize("profile", ["dual-agent", "dual-agent-webapp"])
def test_scaffold_and_doctor_do_not_require_owner_capture(tmp_path, profile):
    target = tmp_path / "project"
    scaffold_project(
        ScaffoldOptions(
            project_name="Owner input test",
            profile=profile,
            owner="Test",
            target_dir=target,
            init_git=False,
            seed_example=False,
            include_ci=False,
        )
    )
    settings = (target / ".claude/settings.json").read_text(encoding="utf-8")
    assert "owner-decision" not in settings
    assert not (target / ".claude/hooks/owner-decision-capture.py").exists()
    assert not (target / "memory/pending-owner-decisions.md").exists()
    assert not (target / ".claude/skills/gtkb-decision-capture").exists()
    assert not (target / ".claude/skills/decision-capture").exists()
    assert not (target / ".groundtruth/formal-artifact-approvals").exists()
    assert not (target / ".codex/hooks.json").exists()
    assert not list((target / ".claude/rules").glob("CODEX-*.md"))
    assert not (target / "independent-progress-assessments/CODEX-INSIGHT-DROPBOX").exists()
    # Removing the ledger requirement must retain the independent safety gates.
    assert "credential-scan.py" in settings
    assert "destructive-gate.py" in settings
    check = _check_managed_artifact_drift(target, profile)
    assert "owner-decision" not in check.message
    assert "template-missing=" not in check.message


@pytest.mark.parametrize("mixed_group", [False, True])
def test_upgrade_retires_capture_preserves_foreign_handlers_and_history(tmp_path, mixed_group):
    settings = tmp_path / ".claude/settings.json"
    settings.parent.mkdir()
    retired = {"type": "command", "command": "python .claude/hooks/owner-decision-capture.py", "timeout": 5}
    foreign = {"type": "command", "command": "python my-local-hook.py", "timeout": 7}
    customized = {"type": "command", "command": "python .claude/hooks/owner-decision-capture.py --custom"}
    group = {"matcher": "AskUserQuestion", "hooks": [retired, foreign] if mixed_group else [retired]}
    other = {"matcher": "Write", "hooks": [customized] if mixed_group else [foreign, customized]}
    settings.write_text(json.dumps({"hooks": {"PostToolUse": [group, other]}, "custom": {"keep": True}}))
    history = tmp_path / "memory/pending-owner-decisions.md"
    history.parent.mkdir()
    history.write_bytes(b"historical log\r\n\xffpreserve every byte\r\n")
    historical_hook = settings.parent / "hooks/owner-decision-capture.py"
    historical_hook.parent.mkdir()
    historical_hook.write_bytes(b"# foreign edits retained, no managed registration\r\n")
    preimages = {p: p.read_bytes() for p in (history, historical_hook)}
    actions = _plan_settings_registration(tmp_path, "dual-agent")
    assert any(a.event == "PostToolUse" for a in actions)
    _apply_file_actions(tmp_path, actions, update_manifest=False)
    document = json.loads(settings.read_text())
    post = document["hooks"]["PostToolUse"]
    handlers = [h for entry in post for h in entry["hooks"]]
    assert retired not in handlers
    assert handlers.count(foreign) == handlers.count(customized) == 1
    assert {**group, "hooks": [foreign]} in post if mixed_group else group not in post
    assert other in post
    assert document["custom"] == {"keep": True}
    assert all(p.read_bytes() == b for p, b in preimages.items())
    after = settings.read_bytes()
    assert _plan_settings_registration(tmp_path, "dual-agent") == []
    _apply_file_actions(tmp_path, [], update_manifest=False)
    assert settings.read_bytes() == after
