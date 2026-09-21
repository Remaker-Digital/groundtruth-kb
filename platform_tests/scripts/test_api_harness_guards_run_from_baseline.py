"""Execute real authored guards; these child processes do not qualify vendor hosts.

Default provider guard sequences and runners are used. Fixture roots own every
potential output, carry the selected hooks, and never contact provider services.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import groundtruth_kb
import pytest

from platform_tests.scripts.sot_hook_fixtures import REGISTRY, SUBSTITUTE
from scripts import alibaba_cloud_studio_harness as alibaba
from scripts import cloud_harness_base as base
from scripts import ollama_harness as ollama
from scripts import openrouter_harness as openrouter
from scripts.harness_projection import project_harness as projector

ROOT = Path(__file__).resolve().parents[2]
HOOKS = Path(".harness-baseline-configuration/hooks")
PROVIDERS = (
    ("ollama", ollama, ollama._OLLAMA_HOOK_PROFILE),
    ("openrouter", openrouter, openrouter._OPENROUTER_PROFILE),
    ("alibaba-cloud-studio", alibaba, alibaba._ALIBABA_PROFILE),
)


@pytest.fixture
def root(tmp_path, monkeypatch):
    root = tmp_path / "selected host"
    shutil.copytree(ROOT / HOOKS, root / HOOKS, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (root / ".agents/skills").mkdir(parents=True)
    (root / "scripts").mkdir()
    for name in (
        "implementation_start_gate.py",
        "codex_hook_adapter.py",
        "antigravity_hook_adapter.py",
        "cursor_hook_adapter.py",
        "lo_file_safety_payloads.py",
    ):
        shutil.copyfile(ROOT / "scripts" / name, root / "scripts" / name)
    (root / "groundtruth.toml").write_text('[project]\nname="guard-fixture"\n', encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    monkeypatch.setenv("GTKB_PROJECT_ROOT", str(root))
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    monkeypatch.delenv("GTKB_GATE_DENIALS_PATH", raising=False)
    monkeypatch.delenv("GTKB_SOT_READ_DISCIPLINE_BYPASS", raising=False)
    monkeypatch.setattr(projector, "PROJECT_ROOT", root)
    monkeypatch.setattr(projector, "APPLICATION_NAME", None)
    return root


def metadata():
    return base.ModelMetadata("fixture-model", "v1", "https://fixture.invalid", "fixture")


def invoke(provider, root, tool, args):
    # No guard_paths or guard_runner override: actual default paths and children.
    if provider is alibaba:
        return base.invoke_guard_adapter(tool, args, metadata(), root, alibaba._ALIBABA_PROFILE)
    return provider.invoke_guard_adapter(tool, args, metadata(), root)


@pytest.mark.parametrize("name,provider,profile", PROVIDERS)
@pytest.mark.parametrize(
    "kind,hook",
    [
        ("credential", "credential-scan.py"),
        ("scanner", "scanner-safe-writer.py"),
        ("destructive", "destructive-gate.py"),
    ],
)
def test_real_guard_denies_before_any_effect(name, provider, profile, kind, hook, root):
    if kind == "destructive":
        tool, args = "Bash", {"command": "rm -rf src"}
    else:
        # The DB-scoped bearer catalog entry is scanner-only for a bridge path.
        content = ("AK" + "IA" + "ABCDEFGHIJKLMNOP") if kind == "credential" else "Bearer synthetic-fixture"
        tool, args = "Write", {"path": "bridge/guard-fixture.md", "content": content}
    with pytest.raises(RuntimeError, match="guard denied") as error:
        invoke(provider, root, tool, args)
    assert (HOOKS / hook).as_posix() in str(error.value)
    assert not (root / "bridge/guard-fixture.md").exists()
    if kind == "scanner":
        rows = [
            json.loads(line)
            for line in (root / ".groundtruth/runtime/gate-denials.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        assert len(rows) == 1
        row = rows[0]
        assert row["schema_version"] == 1 and row["gate"] == row["hook"] == "scanner-safe-writer"
        assert row["event"] == "deny" and row["pattern_id"] == "bearer_header"
        assert row["hits"] and row["session_id"] and row["command_hash"] and row["reason"]
    assert not list((root / HOOKS).glob("__pycache__"))


@pytest.mark.parametrize("name,provider,profile", PROVIDERS)
def test_missing_guard_is_refused_without_effect(name, provider, profile, root):
    (root / HOOKS / "credential-scan.py").unlink()
    with pytest.raises(RuntimeError, match="guard script is missing") as error:
        invoke(provider, root, "Write", {"path": "bridge/guard-fixture.md", "content": "clear"})
    assert (HOOKS / "credential-scan.py").as_posix() in str(error.value)


@pytest.mark.parametrize("name,provider,profile", PROVIDERS)
def test_redirected_guard_directory_is_refused(name, provider, profile, root):
    source = root / HOOKS
    saved = root / "owned-hook-preimage"
    source.rename(saved)
    completed = subprocess.run(["cmd", "/c", "mklink", "/J", str(source), str(saved)], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    try:
        with pytest.raises(RuntimeError, match="configuration path is redirected"):
            invoke(provider, root, "Write", {"path": "bridge/guard-fixture.md", "content": "clear"})
    finally:
        source.rmdir()
        saved.rename(source)


@pytest.fixture
def interpreter(root):
    target = root / "groundtruth-kb/.venv"
    target.parent.mkdir()
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(target), sys.prefix], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    try:
        yield target
    finally:
        target.rmdir()


@pytest.mark.parametrize("name,provider,profile", PROVIDERS)
def test_rendered_native_settings_execute_real_baseline_deny(name, provider, profile, root, interpreter):
    (root / HOOKS / "manifest.toml").write_text(
        'schema_version=1\n[[hook]]\nevent="pre_tool_use"\nintents=["shell_exec"]\nscript="destructive-gate.py"\nblocking=true\n',
        encoding="utf-8",
    )
    assert projector.run(name, "write") == 0
    text = (root / provider.NATIVE_HOOK_SETTINGS_PATH).read_text(encoding="utf-8")
    assert str(HOOKS.as_posix()) in text and "--harness " + name in text
    result = base.invoke_native_hooks(
        base.NATIVE_HOOK_PRE_TOOL_USE, metadata(), root, profile, tool_name="Bash", tool_input={"command": "rm -rf src"}
    )
    assert result and result["decision"] == "block", result
    assert "rm -rf" in result["reason"] or "destructive" in result["reason"].lower()


def adapter_call(name, root, target):
    if name == "antigravity":
        data = {
            "conversationId": "fixture-native",
            "workspacePaths": [str(root)],
            "toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf src", "Cwd": str(root)}},
        }
    else:
        data = {
            "session_id": "fixture-native",
            "cwd": str(root),
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf src"},
            "command": "rm -rf src",
        }
    flags = [] if name == "cursor" else ["--event", "PreToolUse", "--timeout", "10"]
    result = subprocess.run(
        [sys.executable, "-B", str(root / "scripts" / (name + "_hook_adapter.py")), *flags, target, "--harness", name],
        input=json.dumps(data),
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode in (0, 2), result.stderr
    return result, json.loads(result.stdout)


@pytest.mark.parametrize("name", ["codex", "antigravity", "cursor"])
def test_native_adapter_executes_baseline_deny(name, root):
    result, value = adapter_call(name, root, (HOOKS / "destructive-gate.py").as_posix())
    if name == "cursor":
        assert result.returncode == 2 and value["permission"] == "deny", value
    elif name == "codex":
        assert value["hookSpecificOutput"]["permissionDecision"] == "deny", value
    else:
        # The existing Antigravity native adapter maps a block to decision=deny.
        assert value["decision"] == "deny", value


@pytest.mark.parametrize("name", ["codex", "antigravity"])
@pytest.mark.parametrize(
    "target",
    [
        ".claude/hooks/probe.py",
        ".codex/hooks/probe.py",
        "elsewhere/probe.py",
        "scripts/../.harness-baseline-configuration/hooks/destructive-gate.py",
    ],
)
def test_native_adapter_refuses_retired_or_redirected_targets(name, target, root):
    if ".." not in Path(target).parts:
        path = root / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("raise RuntimeError('must not execute')\n", encoding="utf-8")
    _, value = adapter_call(name, root, target)
    assert "Hook target must" in json.dumps(value) or "Redirected hook target" in json.dumps(value), value


@pytest.mark.parametrize("name", ["codex", "antigravity"])
def test_hosted_application_registration_target_keeps_host_binding(name, root, monkeypatch):
    monkeypatch.setattr(projector, "APPLICATION_NAME", "fixture-app")
    profile = {**projector.load_profiles()["harnesses"][name], "name": name}
    target = projector._hook_target({"script": "destructive-gate.py"}, profile)
    assert target == (HOOKS / "destructive-gate.py").as_posix() and ".." not in Path(target).parts
    _, value = adapter_call(name, root, target)
    assert "deny" in json.dumps(value) or value.get("decision") == "block", value


def test_rendered_claude_read_guard_uses_authored_installation_registry(root, interpreter):
    registry = root / "config/registry/sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text(REGISTRY, encoding="utf-8")
    (root / HOOKS / "manifest.toml").write_text(
        'schema_version=1\n[[hook]]\nevent="pre_tool_use"\nintents=["read_access"]\nscript="sot-read-discipline.py"\nblocking=true\n',
        encoding="utf-8",
    )
    plan = projector.build_plan("claude")
    assert not plan.gaps, plan.gaps
    settings = json.loads(plan.writes[".claude/settings.json"])
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    command = command.replace("$CLAUDE_PROJECT_DIR", str(root))
    assert "--harness claude" in command
    unregistered = root / "unregistered-root"
    unregistered.mkdir()
    for target, expected in [(str(root / SUBSTITUTE), "block"), (str(unregistered / SUBSTITUTE), None)]:
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": target},
            "cwd": str(unregistered),
            "project_root": str(unregistered),
        }
        result = subprocess.run(
            command,
            shell=True,
            input=json.dumps(payload),
            cwd=unregistered,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout).get("decision") == expected


def test_hook_context_root_order_and_relative_denial_override(root, tmp_path, monkeypatch):
    path = root / HOOKS / "_hook_context.py"
    spec = importlib.util.spec_from_file_location("hook_context_fixture", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    explicit = tmp_path / "explicit"
    explicit.mkdir()
    envroot = tmp_path / "environment"
    envroot.mkdir()
    monkeypatch.setenv("GTKB_PROJECT_ROOT", str(envroot))
    assert module.resolve_root({"project_root": str(explicit), "cwd": str(root)}) == explicit
    assert module.resolve_root({"cwd": str(root)}) == envroot
    monkeypatch.delenv("GTKB_PROJECT_ROOT")
    nested = root / "nested"
    nested.mkdir()
    assert module.resolve_root({"cwd": str(nested)}) == root
    monkeypatch.chdir(tmp_path)
    assert module.resolve_root({}) == root
    monkeypatch.setenv("GTKB_GATE_DENIALS_PATH", "telemetry/denials.jsonl")
    result = subprocess.run(
        [sys.executable, "-B", str(root / HOOKS / "scanner-safe-writer.py"), "--harness", "fixture"],
        input=json.dumps(
            {
                "project_root": str(explicit),
                "tool_name": "Write",
                "tool_input": {"file_path": "bridge/fixture.md", "content": "Bearer synthetic-fixture"},
            }
        ),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert len((explicit / "telemetry/denials.jsonl").read_text(encoding="utf-8").splitlines()) == 1
    assert not (tmp_path / "telemetry").exists()
