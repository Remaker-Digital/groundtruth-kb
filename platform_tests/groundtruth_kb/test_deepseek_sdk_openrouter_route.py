"""DeepSeek SDK harness OpenRouter route (owner rulings D51, D53-D55; live evidence 2026-09-24).

OpenRouter refuses the runtime's DeepSeek-specific provider, while the provider-neutral pi-ai route works through the
GT-KB preset. The launcher keeps the tool-minimal profile and its guard, inserts only the pi-ai provider row, defaults to
the preset, and takes GTKB_OPENROUTER_API_KEY from the environment or GT-KB's own .env.local loader, placing it only in
the runtime's environment and never in a report, patch or message.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SDK_SOURCE = ROOT / "infrastructure" / "deepseek-sdk"
PRESET = "@preset/gtkb-openrouter-deepseek-v4-flash"
CREDENTIAL = "fixture-openrouter-credential-value"


def _launcher():
    spec = importlib.util.spec_from_file_location("deepseek_sdk_harness_route", SDK_SOURCE / "harness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _loader_root(root: Path, body: str) -> Path:
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "_env.py").write_text(body, encoding="utf-8")
    return root


def test_the_route_patch_inserts_only_the_pi_ai_provider_row(tmp_path):
    launcher = _launcher()
    patch = launcher.write_route_patch(tmp_path, PRESET)
    assert patch.name == "gtkb-openrouter.patch.yml"
    assert yaml.safe_load(patch.read_text(encoding="utf-8")) == [
        {
            "insert": [
                {
                    "id": "llm-pi-ai",
                    "name": "@deepseek-ai/dsh-llm-pi-ai",
                    "config": {
                        "providers": {
                            "gtkb-openrouter": {
                                "displayName": "GT-KB OpenRouter",
                                "apiKeyEnv": "GTKB_OPENROUTER_API_KEY",
                                "api": "openai-completions",
                                "baseURL": "https://openrouter.ai/api/v1",
                                "models": [{"id": PRESET}],
                            }
                        }
                    },
                }
            ]
        }
    ]
    guard = yaml.safe_load(launcher.write_patch(tmp_path).read_text(encoding="utf-8"))
    assert guard == [{"insert": [{"id": "gtkb-effect-guard", "name": launcher.GUARD.resolve().as_uri()}]}]


def test_the_credential_comes_from_the_environment_first(tmp_path):
    launcher = _launcher()
    _loader_root(tmp_path, "raise AssertionError('the loader is not consulted when the environment has the key')\n")
    assert launcher.openrouter_credential(tmp_path, {"GTKB_OPENROUTER_API_KEY": CREDENTIAL}) == {
        "GTKB_OPENROUTER_API_KEY": CREDENTIAL
    }


def test_the_credential_falls_back_to_gtkbs_env_local_loader(tmp_path):
    launcher = _launcher()
    root = _loader_root(
        tmp_path,
        "def load_env_local(*, check_only=False, **_):\n"
        "    assert check_only, 'the launcher must not change its own process environment'\n"
        f"    return {{'GTKB_OPENROUTER_API_KEY': {CREDENTIAL!r}}}\n",
    )
    assert launcher.openrouter_credential(root, {}) == {"GTKB_OPENROUTER_API_KEY": CREDENTIAL}


def test_a_missing_credential_is_a_typed_failure_that_names_no_value(tmp_path):
    launcher = _launcher()
    root = _loader_root(tmp_path, "def load_env_local(**_):\n    return {'OTHER_KEY': 'unrelated-secret-value'}\n")
    with pytest.raises(launcher.LauncherError) as info:
        launcher.openrouter_credential(root, {})
    assert info.value.code == launcher.EXIT_STARTUP_FAILED
    assert "GTKB_OPENROUTER_API_KEY" in str(info.value) and "unrelated-secret-value" not in str(info.value)


def test_a_failing_or_missing_loader_names_only_the_error_type(tmp_path):
    launcher = _launcher()
    root = _loader_root(tmp_path, "def load_env_local(**_):\n    raise RuntimeError('sk-or-v1-secret-in-message')\n")
    with pytest.raises(launcher.LauncherError) as info:
        launcher.openrouter_credential(root, {})
    assert "RuntimeError" in str(info.value) and "sk-or" not in str(info.value)
    with pytest.raises(launcher.LauncherError) as missing:
        launcher.openrouter_credential(tmp_path / "absent-root", {})
    assert missing.value.code == launcher.EXIT_STARTUP_FAILED


def _main(launcher, tmp_path, monkeypatch, *extra: str, env: dict[str, str] | None = None):
    calls: list[list[str]] = []
    captured: dict[str, object] = {}
    seen_cli_env: list[dict[str, str]] = []

    def fake_cli(arguments):
        calls.append(arguments[:2])
        if arguments[:2] == ["session", "bind"]:
            native = arguments[arguments.index("--native-context-id") + 1]
            binding = {"session_context_id": "SC-route", "role": "loyal-opposition", "native_context_id": native}
            return {"status": "init_requested", "binding": binding}
        if arguments[:2] == ["bridge", "check-delivery"]:
            return {"delivered": True}
        raise AssertionError(arguments)

    def fake_cli_runner(root, config, environment):
        seen_cli_env.append(dict(environment))
        return fake_cli

    def fake_run_session(installation, **kwargs):
        captured.update(kwargs)
        return {"finish_reason": "completed", "events": 1, "turn": "completed"}

    monkeypatch.setattr(launcher.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(launcher, "verify_installation", lambda source=None: {"executable": tmp_path / "dsh.exe"})
    monkeypatch.setattr(launcher, "cli_runner", fake_cli_runner)
    monkeypatch.setattr(launcher, "run_session", fake_run_session)
    monkeypatch.delenv("GTKB_OPENROUTER_API_KEY", raising=False)
    for name, value in (env or {}).items():
        monkeypatch.setenv(name, value)
    (tmp_path / "AGENTS.md").write_text("Neutral baseline instructions.\n", encoding="utf-8")
    task = tmp_path / "task.md"
    task.write_text("qualification task", encoding="utf-8")
    report = tmp_path / "report.json"
    code = launcher.main(
        [
            "--root",
            str(tmp_path),
            "--init",
            "::init gtkb lo",
            "--document",
            "doc-1",
            "--version",
            "1",
            "--task-file",
            str(task),
            "--report",
            str(report),
            *extra,
        ]
    )
    return code, calls, captured, seen_cli_env, report.read_text(encoding="utf-8")


def test_a_default_turn_uses_the_preset_and_hands_a_loaded_key_only_to_the_runtime(tmp_path, monkeypatch):
    launcher = _launcher()
    _loader_root(tmp_path, f"def load_env_local(**_):\n    return {{'GTKB_OPENROUTER_API_KEY': {CREDENTIAL!r}}}\n")
    code, calls, captured, cli_envs, report = _main(launcher, tmp_path, monkeypatch)
    assert code == launcher.EXIT_DELIVERED
    assert (captured["provider"], captured["model"]) == ("gtkb-openrouter", PRESET)
    assert captured["credential"] == {"GTKB_OPENROUTER_API_KEY": CREDENTIAL}
    assert "GTKB_OPENROUTER_API_KEY" not in captured["environment"]
    assert all("GTKB_OPENROUTER_API_KEY" not in environment for environment in cli_envs), "never given to the gt CLI"
    assert CREDENTIAL not in report
    assert ["session", "bind"] in calls and ["bridge", "check-delivery"] in calls


def test_a_turn_without_any_key_fails_before_binding(tmp_path, monkeypatch):
    launcher = _launcher()
    _loader_root(tmp_path, "def load_env_local(**_):\n    return {}\n")
    code, calls, captured, _cli_envs, report = _main(launcher, tmp_path, monkeypatch)
    assert code == launcher.EXIT_STARTUP_FAILED
    assert calls == [] and not captured, "no context is bound without a credential"
    assert "GTKB_OPENROUTER_API_KEY" in json.loads(report)["error"]


def test_a_no_prompt_start_needs_no_credential(tmp_path, monkeypatch):
    launcher = _launcher()
    code, _calls, captured, _cli_envs, _report = _main(launcher, tmp_path, monkeypatch, "--no-prompt")
    assert code == launcher.EXIT_DELIVERED
    assert captured["credential"] is None and captured["provider"] == "gtkb-openrouter"


def test_the_deepseek_official_route_needs_no_openrouter_key(tmp_path, monkeypatch):
    launcher = _launcher()
    code, _calls, captured, _cli_envs, _report = _main(
        launcher, tmp_path, monkeypatch, "--provider", "deepseek-official", "--model", "deepseek-v4-flash"
    )
    assert code == launcher.EXIT_DELIVERED
    assert (captured["provider"], captured["model"], captured["credential"]) == (
        "deepseek-official",
        "deepseek-v4-flash",
        None,
    )


def test_run_session_adds_the_route_patch_and_key_only_for_the_openrouter_provider(tmp_path, monkeypatch):
    launcher = _launcher()
    configs: list[dict] = []
    api = types.ModuleType("deepseek_harness.api")
    errors = types.ModuleType("deepseek_harness.errors")

    class HarnessError(Exception):
        pass

    class Config:
        def __init__(self, **kwargs):
            configs.append(kwargs)

    class Harness:
        def __init__(self, config):
            self.config = config

        def start(self):
            return None

        def close(self):
            return None

    errors.HarnessError = HarnessError
    api.DeepSeekHarnessConfig = Config
    api.DeepSeekHarness = Harness
    monkeypatch.setitem(sys.modules, "deepseek_harness", types.ModuleType("deepseek_harness"))
    monkeypatch.setitem(sys.modules, "deepseek_harness.api", api)
    monkeypatch.setitem(sys.modules, "deepseek_harness.errors", errors)
    installation = {"executable": tmp_path / "dsh.exe", "profile": "sdk-minimal"}
    for provider, credential in (
        ("gtkb-openrouter", {"GTKB_OPENROUTER_API_KEY": CREDENTIAL}),
        ("deepseek-official", None),
    ):
        home = tmp_path / provider
        result = launcher.run_session(
            installation,
            root=tmp_path,
            cwd=tmp_path,
            home=home,
            native_context_id="ctx-1",
            prompt=None,
            provider=provider,
            model=PRESET,
            timeout_seconds=5,
            environment={"PATH": "fixture"},
            credential=credential,
        )
        assert result["turn"] == "none"
        config = configs[-1]
        assert config["profile"] == "sdk-minimal"
        names = [Path(patch).name for patch in config["patches"]]
        if credential:
            assert names == ["gtkb-guard.patch.yml", "gtkb-openrouter.patch.yml"]
            assert config["env"]["GTKB_OPENROUTER_API_KEY"] == CREDENTIAL
        else:
            assert names == ["gtkb-guard.patch.yml"]
            assert "GTKB_OPENROUTER_API_KEY" not in config["env"]
        for written in home.rglob("*"):
            if written.is_file():
                assert CREDENTIAL not in written.read_text(encoding="utf-8", errors="replace"), written
