"""Provider configuration derives independently from the neutral baseline."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import groundtruth_kb
import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main

from scripts import alibaba_cloud_studio_harness as alibaba
from scripts import cloud_harness_base as base
from scripts import ollama_harness as ollama
from scripts import openrouter_harness as openrouter
from scripts.harness_projection import project_harness as projector

ROOT = Path(__file__).resolve().parents[2]
PROVIDERS = (("openrouter", openrouter), ("ollama", ollama), ("alibaba-cloud-studio", alibaba))


@pytest.fixture
def projection_root(tmp_path, monkeypatch):
    monkeypatch.setattr(projector, "PROJECT_ROOT", tmp_path)
    baseline = tmp_path / ".harness-baseline-configuration"
    (baseline / "hooks").mkdir(parents=True)
    (baseline / "routing.toml").write_bytes((ROOT / ".harness-baseline-configuration/routing.toml").read_bytes())
    (baseline / "hooks/manifest.toml").write_text(
        'schema_version=1\n[[hook]]\nevent="session_start"\nscript="identity_probe.py"\nblocking=true\n',
        encoding="utf-8",
    )
    (baseline / "hooks/identity_probe.py").write_text(
        "import json, os, sys\nfrom pathlib import Path\n"
        "payload = json.load(sys.stdin)\n"
        'out = Path(os.environ["{{HARNESS_PROJECT_DIR_VAR}}"])/"observed-hook.json"\n'
        'out.write_text(json.dumps({"path": __file__, "context": payload["session_id"], '
        '"env_context": os.environ["{{HARNESS_SESSION_ID_VAR}}"]}), encoding="utf-8")\n'
        'print("{}")\n',
        encoding="utf-8",
    )
    interpreter = tmp_path / "groundtruth-kb/.venv"
    interpreter.parent.mkdir()
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(interpreter), sys.prefix], capture_output=True, text=True, encoding="utf-8"
    )
    assert result.returncode == 0, result.stderr
    try:
        yield tmp_path
    finally:
        interpreter.rmdir()


@pytest.mark.parametrize("name,provider", PROVIDERS)
def test_each_provider_routing_and_hooks_are_independently_derived(name, provider, projection_root):
    config_root = Path(".api-harness") / name
    assert config_root / "routing.toml" == provider.ROUTING_CONFIG_PATH
    plan = projector.build_plan(name)
    assert not plan.gaps
    assert all(Path(path).is_relative_to(config_root) for path in plan.writes)
    routing = tomllib.loads(plan.writes[(config_root / "routing.toml").as_posix()])
    assert set(routing["routing"]) == {name}
    assert {row["provider"] for row in routing["models"].values()} == {name}
    assert projector.run(name, "write") == 0
    assert projector.run(name, "check") == 0
    loaded = provider.load_routing_config(projection_root)
    assert loaded.default_model in loaded.models
    assert set(loaded.skill_routes.values()) <= set(loaded.models)
    from groundtruth_kb.project.doctor import _check_provider_routing

    inspected = _check_provider_routing(projection_root, name)
    assert inspected.status == "pass", inspected.message
    metadata = base.ModelMetadata("fixture-model", "v1", "https://fixture.invalid", "fixture")
    profile = {
        alibaba: alibaba._ALIBABA_PROFILE,
        openrouter: openrouter._OPENROUTER_PROFILE,
        ollama: ollama._OLLAMA_HOOK_PROFILE,
    }[provider]
    base.invoke_native_hooks(base.NATIVE_HOOK_SESSION_START, metadata, projection_root, profile)
    observed = json.loads((projection_root / "observed-hook.json").read_text(encoding="utf-8"))
    assert Path(observed["path"]).resolve().is_relative_to((projection_root / config_root).resolve())
    assert observed["context"] == observed["env_context"] == metadata.native_context_id


@pytest.mark.parametrize("name,provider", PROVIDERS)
def test_missing_own_routing_never_uses_the_old_shared_catalog(name, provider, projection_root):
    shared = projection_root / ".api-harness/routing.toml"
    shared.parent.mkdir()
    shared.write_bytes((ROOT / ".harness-baseline-configuration/routing.toml").read_bytes())
    with pytest.raises(RuntimeError, match="routing config is missing"):
        provider.load_routing_config(projection_root)


@pytest.mark.parametrize(
    "profile", [alibaba._ALIBABA_PROFILE, openrouter._OPENROUTER_PROFILE, ollama._OLLAMA_HOOK_PROFILE]
)
def test_missing_own_hook_registration_is_refused_even_when_peer_settings_exist(projection_root, profile):
    peer = projection_root / ".claude/settings.json"
    peer.parent.mkdir()
    peer.write_text('{"hooks": {}}', encoding="utf-8")
    metadata = base.ModelMetadata("fixture-model", "v1", "https://fixture.invalid", "fixture")
    with pytest.raises(RuntimeError, match="hook settings.*missing"):
        base.invoke_native_hooks(base.NATIVE_HOOK_SESSION_START, metadata, projection_root, profile)


@pytest.mark.parametrize("name,provider", PROVIDERS)
def test_provider_loop_executes_own_five_events_and_honors_native_denial(projection_root, name, provider):
    baseline = projection_root / ".harness-baseline-configuration/hooks"
    events = ["session_start", "prompt_submit", "pre_tool_use", "post_tool_use", "turn_end"]
    baseline.joinpath("manifest.toml").write_text(
        "schema_version=1\n" + "".join(f'[[hook]]\nevent="{event}"\nscript="identity_probe.py"\n' for event in events),
        encoding="utf-8",
    )
    # These are transport probes. Real native claim/scope behavior is qualified
    # separately by test_projected_native_effect_gate against PostgreSQL/CLI.
    baseline.joinpath("identity_probe.py").write_text(
        "import json, os, sys\nfrom pathlib import Path\n"
        "p = json.load(sys.stdin)\n"
        'trace = Path(os.environ["{{HARNESS_PROJECT_DIR_VAR}}"])/"hook-events.jsonl"\n'
        'entry = {"event": p["hook_event_name"], "session": p["session_id"], '
        '"native": os.environ["{{HARNESS_SESSION_ID_VAR}}"], "script": __file__}\n'
        'with trace.open("a", encoding="utf-8") as f: f.write(json.dumps(entry)+"\\n")\n'
        'deny = {"hookSpecificOutput": {"hookEventName": "PreToolUse", '
        '"permissionDecision": "deny", "permissionDecisionReason": "qualification refusal"}}\n'
        'print(json.dumps(deny if p["hook_event_name"] == "PreToolUse" else {}))\n',
        encoding="utf-8",
    )
    assert projector.run(name, "write") == 0
    target = projection_root / "protected.txt"
    target.write_bytes(b"unrelated preimage")
    trace = projection_root / "hook-events.jsonl"
    calls = []

    def chat(_endpoint, _key, payload, _timeout):
        entries = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
        assert [entry["event"] for entry in entries[:2]] == ["SessionStart", "UserPromptSubmit"]
        calls.append(payload)
        if len(calls) == 1:
            message = {
                "content": "",
                "tool_calls": [
                    {
                        "id": "fixture-write",
                        "type": "function",
                        "function": {
                            "name": "Write",
                            "arguments": json.dumps({"file_path": str(target), "content": "wrong"}),
                        },
                    }
                ],
            }
        else:
            assert "qualification refusal" in json.dumps(payload["messages"][-1]["content"])
            message = {"content": "The tool was refused."}
        if provider is alibaba:
            if len(calls) == 1:
                return {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "fixture-write",
                            "name": "Write",
                            "input": {"file_path": str(target), "content": "wrong"},
                        }
                    ]
                }
            return {"content": [{"type": "text", "text": message["content"]}]}
        return {"message": message} if provider is ollama else {"choices": [{"message": message}]}

    def guards_must_not_run(*args, **kwargs):
        pytest.fail("The native refusal must precede tool guard/effect execution")

    common = (
        "Exercise the selected hooks",
        base.ModelRoute("fixture", "fixture", "v1", True, ("Write",)),
        "https://fixture.invalid",
    )
    if provider is ollama:
        result = provider.run_tool_loop(
            *common,
            2,
            projection_root,
            chat_func=lambda endpoint, payload, timeout: chat(endpoint, "", payload, timeout),
            guard_runner=guards_must_not_run,
        )
    else:
        result = provider.run_tool_loop(
            *common, "unused-fixture-key", 2, projection_root, chat_func=chat, guard_runner=guards_must_not_run
        )
    assert result == "The tool was refused."
    assert target.read_bytes() == b"unrelated preimage"
    entries = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
    assert [entry["event"] for entry in entries] == [
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "Stop",
    ]
    assert len({entry["session"] for entry in entries}) == 1
    assert all(entry["session"] == entry["native"] for entry in entries)
    assert all(
        Path(entry["script"]).is_relative_to(projection_root / provider.ROUTING_CONFIG_PATH.parent) for entry in entries
    )


@pytest.mark.parametrize("name,provider", PROVIDERS)
def test_provider_config_directory_cannot_be_a_junction_to_peer_material(name, provider, projection_root):
    peer = projection_root / "unrelated-config"
    peer.mkdir()
    peer.joinpath("routing.toml").write_bytes((ROOT / ".harness-baseline-configuration/routing.toml").read_bytes())
    own = projection_root / provider.ROUTING_CONFIG_PATH.parent
    own.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(own), str(peer)], capture_output=True, text=True, encoding="utf-8"
    )
    assert result.returncode == 0, result.stderr
    try:
        with pytest.raises(RuntimeError, match="configuration path.*redirected"):
            provider.load_routing_config(projection_root)
        from groundtruth_kb.project.doctor import _check_provider_routing

        inspected = _check_provider_routing(projection_root, name)
        assert inspected.status == "fail" and "configuration was not read" in inspected.message
    finally:
        own.rmdir()


def test_missing_routing_source_refuses_projection_before_any_output(projection_root):
    (projection_root / ".harness-baseline-configuration/routing.toml").unlink()
    assert projector.run("openrouter", "write") == 2
    assert not (projection_root / ".api-harness").exists()


@pytest.mark.parametrize("nested", (False, True))
def test_projection_refuses_redirected_output_before_writing(projection_root, nested):
    peer = projection_root / "unrelated-config"
    peer.mkdir()
    marker = peer / "routing.toml"
    marker.write_text("Unrelated configuration.", encoding="utf-8")
    own = projection_root / ".api-harness/openrouter"
    if nested:
        own = own / "hooks"
    own.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(own), str(peer)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    try:
        assert projector.run("openrouter", "write") == 2
        assert marker.read_text(encoding="utf-8") == "Unrelated configuration."
        assert sorted(path.name for path in peer.iterdir()) == ["routing.toml"]
    finally:
        own.rmdir()


def test_cli_projects_selected_sources_without_opening_a_database(projection_root, monkeypatch):
    for key in ("GT_PROJECT_ROOT", "GT_DB_PATH", "GT_AUTHORITY_URL"):
        monkeypatch.delenv(key, raising=False)
    config = projection_root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\nproject_root="."\ndb_path="sentinel.db"\nauthority_url="http://127.0.0.1:1"\n',
        encoding="utf-8",
    )
    sentinel = projection_root / "sentinel.db"
    sentinel.write_bytes(b"This operation must not open SQLite.")
    source_dir = Path("scripts/harness_projection")
    (projection_root / source_dir).mkdir(parents=True)
    for name in ("project_harness.py", "profiles.toml"):
        (projection_root / source_dir / name).write_bytes((ROOT / source_dir / name).read_bytes())
    args = ["--config", str(config), "harness", "project", "openrouter"]
    runner = CliRunner()
    validation = runner.invoke(main, [*args, "--validate"])
    assert validation.exit_code == 0, validation.output
    assert "VALID openrouter" in validation.output
    assert not (projection_root / ".api-harness").exists()
    projected = runner.invoke(main, args)
    assert projected.exit_code == 0, projected.output
    assert "PROJECTED openrouter" in projected.output
    assert runner.invoke(main, [*args, "--check"]).exit_code == 0
    baseline = projection_root / ".harness-baseline-configuration/routing.toml"
    text = baseline.read_text(encoding="utf-8")
    baseline.write_text(
        text.replace('model_id = "deepseek/deepseek-v4-pro"', 'model_id = "changed-model"'), encoding="utf-8"
    )
    check = runner.invoke(main, [*args, "--check"])
    assert check.exit_code == 1 and "drifted" in check.output
    rendered = tomllib.loads((projection_root / openrouter.ROUTING_CONFIG_PATH).read_text(encoding="utf-8"))
    assert rendered["models"]["deepseek-v4-pro"]["model_id"] == "deepseek/deepseek-v4-pro"
    conflicting = runner.invoke(main, [*args, "--check", "--validate"])
    assert conflicting.exit_code != 0
    retired = runner.invoke(main, ["--config", str(config), "harness", "roles"])
    assert retired.exit_code != 0 and "No such command" in retired.output
    separate = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb", *args, "--validate"],
        cwd=projection_root,
        env={**os.environ, "PYTHONPATH": str(Path(groundtruth_kb.__file__).resolve().parent.parent)},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert separate.returncode == 0, separate.stderr
    assert "VALID openrouter" in separate.stdout
    assert sentinel.read_bytes() == b"This operation must not open SQLite."
