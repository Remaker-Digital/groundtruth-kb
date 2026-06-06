from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_build_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "build.py"
    spec = importlib.util.spec_from_file_location("build_script_under_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _prepare_module(monkeypatch, tmp_path):
    build = _load_build_module()

    version_file = tmp_path / "src" / "multi_tenant" / "api_versioning.py"
    version_file.parent.mkdir(parents=True)
    version_file.write_text('PRODUCT_VERSION = "0.0.1"\n', encoding="utf-8")

    monkeypatch.setattr(build, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(build, "_init_log", lambda: None)
    monkeypatch.setattr(build, "_close_log", lambda: None)
    monkeypatch.setattr(build, "_check_tool", lambda _tool: True)
    monkeypatch.setattr(build, "build_frontends", lambda: True)
    monkeypatch.setattr(build.time, "sleep", lambda _seconds: None)

    return build


def test_default_build_commits_without_push_or_remote_workflows(monkeypatch, tmp_path):
    build = _prepare_module(monkeypatch, tmp_path)
    commands: list[str] = []

    def fake_run(cmd: str, timeout: int = 60):
        commands.append(cmd)
        if cmd == "git diff --cached --quiet":
            return 1, ""
        if "git push" in cmd or cmd.startswith("gh workflow run"):
            raise AssertionError(f"remote mutation command should not run by default: {cmd}")
        return 0, ""

    monkeypatch.setattr(build, "_run", fake_run)
    monkeypatch.setattr(build, "trigger_workflow", lambda *_args: False)
    monkeypatch.setattr(sys, "argv", ["build.py", "v1.2.3"])

    assert build.main() == 0

    commit_commands = [cmd for cmd in commands if cmd.startswith("git commit ")]
    assert len(commit_commands) == 1
    assert "git push" not in commit_commands[0]
    assert not any(cmd == "git push" for cmd in commands)


def test_explicit_push_uses_separate_push_and_triggers_workflows(monkeypatch, tmp_path):
    build = _prepare_module(monkeypatch, tmp_path)
    commands: list[str] = []
    triggered: list[tuple[str, str]] = []

    def fake_run(cmd: str, timeout: int = 60):
        commands.append(cmd)
        if cmd == "git diff --cached --quiet":
            return 1, ""
        return 0, ""

    monkeypatch.setattr(build, "_run", fake_run)
    monkeypatch.setattr(build, "trigger_workflow", lambda workflow, tag: triggered.append((workflow, tag)) or True)
    monkeypatch.setattr(build, "find_run_id", lambda _workflow: 123)
    monkeypatch.setattr(build, "poll_run", lambda _run_id, _label: True)
    monkeypatch.setattr(build, "verify_acr_tag", lambda _repo, _tag: True)
    monkeypatch.setattr(sys, "argv", ["build.py", "v1.2.3", "--push"])

    assert build.main() == 0

    commit_index = next(i for i, cmd in enumerate(commands) if cmd.startswith("git commit "))
    push_index = commands.index("git push")
    assert commit_index < push_index
    assert "git push" not in commands[commit_index]
    assert triggered
    assert {tag for _workflow, tag in triggered} == {"v1.2.3"}


def test_default_build_with_no_staged_changes_skips_remote_side_effects(monkeypatch, tmp_path):
    build = _prepare_module(monkeypatch, tmp_path)
    commands: list[str] = []

    def fake_run(cmd: str, timeout: int = 60):
        commands.append(cmd)
        if cmd == "git diff --cached --quiet":
            return 0, ""
        if cmd.startswith("git commit ") or cmd == "git push" or cmd.startswith("gh workflow run"):
            raise AssertionError(f"unexpected side-effect command: {cmd}")
        return 0, ""

    monkeypatch.setattr(build, "_run", fake_run)
    monkeypatch.setattr(build, "trigger_workflow", lambda *_args: False)
    monkeypatch.setattr(sys, "argv", ["build.py", "v1.2.3"])

    assert build.main() == 0
    assert "git diff --cached --quiet" in commands


def test_explicit_push_with_no_staged_changes_skips_commit_but_runs_remote_path(monkeypatch, tmp_path):
    build = _prepare_module(monkeypatch, tmp_path)
    commands: list[str] = []
    triggered: list[str] = []

    def fake_run(cmd: str, timeout: int = 60):
        commands.append(cmd)
        if cmd == "git diff --cached --quiet":
            return 0, ""
        if cmd.startswith("git commit "):
            raise AssertionError(f"commit should not run without staged changes: {cmd}")
        return 0, ""

    monkeypatch.setattr(build, "_run", fake_run)
    monkeypatch.setattr(build, "trigger_workflow", lambda workflow, _tag: triggered.append(workflow) or True)
    monkeypatch.setattr(build, "find_run_id", lambda _workflow: 123)
    monkeypatch.setattr(build, "poll_run", lambda _run_id, _label: True)
    monkeypatch.setattr(build, "verify_acr_tag", lambda _repo, _tag: True)
    monkeypatch.setattr(sys, "argv", ["build.py", "v1.2.3", "--push"])

    assert build.main() == 0
    assert "git push" in commands
    assert triggered
