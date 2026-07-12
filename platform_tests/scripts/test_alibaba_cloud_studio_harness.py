from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import alibaba_cloud_studio_harness as ach
from scripts import cloud_harness_base as base


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / ach.ROUTING_CONFIG_PATH).write_text(
        """
schema_version = 1

[models.alib-route]
model_id = "alibaba-deepseek-v4-pro"
provider = "alibaba-cloud-studio"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[models.openrouter-same-model]
model_id = "alibaba-deepseek-v4-pro"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read"]

[routing.alibaba-cloud-studio]
default_model = "alib-route"
timeout_seconds = 900
session_timeout_seconds = 28800
max_turns = 600

[routing.alibaba-cloud-studio.skills]
bridge-review = "alib-route"

[routing.openrouter]
default_model = "openrouter-same-model"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return root


def test_profile_declares_alibaba_identity_anthropic_bearer_and_native_hooks() -> None:
    profile = ach._ALIBABA_PROFILE

    assert profile.display_name == "Alibaba Cloud Studio"
    assert profile.author_identity == "Alibaba Cloud Studio H"
    assert profile.author_harness_id == "H"
    assert profile.auth_env_key == "ALIBABA_API_KEY"
    assert profile.provider_routing_key == "alibaba-cloud-studio"
    assert profile.dialect == base.DIALECT_ANTHROPIC_MESSAGES
    assert profile.hook_tier == base.HOOK_TIER_NATIVE_FULL
    assert profile.auth_style == base.AUTH_STYLE_AUTHORIZATION_BEARER


def test_routing_loads_alibaba_default_and_ignores_same_model_from_other_provider(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    config = ach.load_routing_config(root)
    selected = ach.resolve_model(config, None)

    assert config.default_model == "alib-route"
    assert set(config.models) == {"alib-route"}
    assert selected.model_id == "alibaba-deepseek-v4-pro"
    assert ach.resolve_model(config, None, skill="bridge-review") == selected


def test_transport_delegates_to_anthropic_messages_with_bearer_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_completion(endpoint, api_key, payload, timeout, **kwargs):
        captured.update(endpoint=endpoint, api_key=api_key, payload=payload, timeout=timeout, **kwargs)
        return {"content": [{"type": "text", "text": "ok"}]}

    monkeypatch.setattr(base, "anthropic_messages_completion", fake_completion)

    assert ach.call_alibaba_cloud_studio_chat("https://example.test/v1", "fixture-token", {"model": "m"})["content"]
    assert captured["label"] == "Alibaba Cloud Studio"
    assert captured["auth_style"] == base.AUTH_STYLE_AUTHORIZATION_BEARER


def test_anthropic_endpoint_normalization_preserves_or_adds_version_prefix() -> None:
    assert ach.normalize_anthropic_endpoint("https://example.test/apps/anthropic") == (
        "https://example.test/apps/anthropic/v1"
    )
    assert ach.normalize_anthropic_endpoint("https://example.test/apps/anthropic/v1/") == (
        "https://example.test/apps/anthropic/v1"
    )


def test_run_tool_loop_delegates_profile_and_native_hook_runner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = make_root(tmp_path)
    route = ach.resolve_model(ach.load_routing_config(root), None)
    captured: dict[str, object] = {}
    hook_runner = object()

    def fake_run_tool_loop(*args, **kwargs):
        captured["profile"] = args[6]
        captured["native_hook_runner"] = kwargs["native_hook_runner"]
        return "done"

    monkeypatch.setattr(base, "run_tool_loop", fake_run_tool_loop)

    assert (
        ach.run_tool_loop(
            "hello", route, "https://example.test/v1", "fixture-token", 1, root, native_hook_runner=hook_runner
        )
        == "done"
    )
    assert captured == {"profile": ach._ALIBABA_PROFILE, "native_hook_runner": hook_runner}


def test_alibaba_native_hook_adapter_accepts_empty_non_tool_lifecycle_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def empty_native_hook(*_args, **_kwargs):
        return base.GuardExecutionResult(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(base, "_default_native_hook_runner", empty_native_hook)

    result = ach.run_alibaba_native_hook(
        "python hook.py",
        {"hook_event_name": base.NATIVE_HOOK_USER_PROMPT_SUBMIT},
        {},
        5,
    )

    assert result.stdout == "{}"


def test_alibaba_native_hook_adapter_keeps_empty_pretool_output_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def empty_native_hook(*_args, **_kwargs):
        return base.GuardExecutionResult(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(base, "_default_native_hook_runner", empty_native_hook)

    result = ach.run_alibaba_native_hook(
        "python hook.py",
        {"hook_event_name": base.NATIVE_HOOK_PRE_TOOL_USE},
        {},
        5,
    )

    assert result.stdout == ""


def test_shared_native_hook_layer_accepts_real_alibaba_empty_pretool_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = make_root(tmp_path)
    settings_dir = root / ".claude"
    settings_dir.mkdir()
    (settings_dir / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    base.NATIVE_HOOK_PRE_TOOL_USE: [
                        {"matcher": "Read", "hooks": [{"type": "command", "command": "empty pre"}]}
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    def empty_native_hook(*_args, **_kwargs):
        return base.GuardExecutionResult(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(base, "_default_native_hook_runner", empty_native_hook)

    result = base.invoke_native_hooks(
        base.NATIVE_HOOK_PRE_TOOL_USE,
        base.ModelMetadata(
            model_id="alibaba-deepseek-v4-pro",
            model_version="alibaba-deepseek-v4-pro",
            endpoint="https://example.test/v1",
            route_key="alib-route",
        ),
        root,
        ach._ALIBABA_PROFILE,
        tool_name="Read",
        tool_input={"path": "note.txt"},
        native_hook_runner=ach.run_alibaba_native_hook,
    )

    assert result == {}


def test_alibaba_native_hook_adapter_wraps_non_json_lifecycle_context(monkeypatch: pytest.MonkeyPatch) -> None:
    def text_native_hook(*_args, **_kwargs):
        return base.GuardExecutionResult(returncode=0, stdout="informational lifecycle context", stderr="")

    monkeypatch.setattr(base, "_default_native_hook_runner", text_native_hook)

    result = ach.run_alibaba_native_hook(
        "python hook.py",
        {"hook_event_name": base.NATIVE_HOOK_USER_PROMPT_SUBMIT},
        {},
        5,
    )

    assert json.loads(result.stdout) == {"hookSpecificOutput": {"additionalContext": "informational lifecycle context"}}


def test_alibaba_native_full_loop_continues_when_posttool_maintenance_times_out(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    (root / "note.txt").write_text("governed evidence", encoding="utf-8")
    settings_dir = root / ".claude"
    settings_dir.mkdir()
    (settings_dir / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    base.NATIVE_HOOK_POST_TOOL_USE: [
                        {
                            "matcher": "Read",
                            "hooks": [{"type": "command", "command": "slow maintenance", "timeout": 10}],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    route = ach.resolve_model(ach.load_routing_config(root), None)
    chat_calls = 0

    def hook_runner(
        _command: str,
        payload: dict,
        _env: dict,
        _timeout: float,
    ) -> base.GuardExecutionResult:
        assert payload["hook_event_name"] == base.NATIVE_HOOK_POST_TOOL_USE
        assert payload["tool_response"] == "governed evidence"
        return base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True)

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        nonlocal chat_calls
        chat_calls += 1
        if chat_calls == 1:
            return {
                "model": route.model_id,
                "content": [{"type": "tool_use", "id": "tool_1", "name": "Read", "input": {"path": "note.txt"}}],
            }
        return {"model": route.model_id, "content": [{"type": "text", "text": "H verdict ready"}]}

    assert (
        ach.run_tool_loop(
            "review",
            route,
            "https://example.test/v1",
            "fixture-token",
            3,
            root,
            chat_func=chat,
            native_hook_runner=hook_runner,
        )
        == "H verdict ready"
    )
    assert chat_calls == 2


def test_bridge_review_enables_readonly_native_hook_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOYAL_OPPOSITION_READONLY", raising=False)
    monkeypatch.delenv("GTKB_NO_AXIS_2_SURFACE", raising=False)
    monkeypatch.delenv("GTKB_NO_PROJECT_COMPLETION_SURFACE", raising=False)

    ach.configure_lo_readonly_environment("bridge-review")

    assert ach.os.environ["LOYAL_OPPOSITION_READONLY"] == "1"
    assert ach.os.environ["GTKB_NO_AXIS_2_SURFACE"] == "1"
    assert ach.os.environ["GTKB_NO_PROJECT_COMPLETION_SURFACE"] == "1"


def test_non_bridge_skill_does_not_change_readonly_native_hook_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOYAL_OPPOSITION_READONLY", raising=False)
    monkeypatch.delenv("GTKB_NO_AXIS_2_SURFACE", raising=False)
    monkeypatch.delenv("GTKB_NO_PROJECT_COMPLETION_SURFACE", raising=False)

    ach.configure_lo_readonly_environment("implementation")

    assert "LOYAL_OPPOSITION_READONLY" not in ach.os.environ
    assert "GTKB_NO_AXIS_2_SURFACE" not in ach.os.environ
    assert "GTKB_NO_PROJECT_COMPLETION_SURFACE" not in ach.os.environ


def test_main_missing_key_reports_only_the_environment_variable_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_root(tmp_path)
    monkeypatch.chdir(root)
    monkeypatch.delenv(ach.API_KEY_ENV, raising=False)
    monkeypatch.setenv(ach.ENDPOINT_ENV, "https://example.test/v1")
    monkeypatch.setattr(ach, "_load_env_local", lambda: None)

    assert ach.main(["-p", "hello"]) == 1

    captured = capsys.readouterr()
    assert ach.API_KEY_ENV in captured.err
    assert "https://example.test/v1" not in captured.err


def test_main_uses_env_only_endpoint_and_never_prints_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_root(tmp_path)
    config = ach.load_routing_config(root)
    key = "fixture-token"
    endpoint = "https://example.test/v1"
    monkeypatch.chdir(root)
    monkeypatch.setenv(ach.API_KEY_ENV, key)
    monkeypatch.setenv(ach.ENDPOINT_ENV, endpoint)
    monkeypatch.setattr(ach, "_load_env_local", lambda: None)
    monkeypatch.setattr(ach, "load_routing_config", lambda _root: config)

    def fake_run_tool_loop(prompt, model_route, selected_endpoint, api_key, max_turns, *_args, **kwargs):
        assert prompt == "hello"
        assert model_route.key == "alib-route"
        assert selected_endpoint == endpoint
        assert api_key == key
        assert max_turns == 600
        assert kwargs["timeout"] == 900
        assert kwargs["session_timeout"] == 28800
        return "done"

    monkeypatch.setattr(ach, "run_tool_loop", fake_run_tool_loop)

    assert ach.main(["-p", "hello", "--model", "alib-route"]) == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == "done"
    assert key not in captured.out + captured.err
    assert endpoint not in captured.out + captured.err


def test_main_explicit_runtime_limits_override_routing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = make_root(tmp_path)
    key = "fixture-token"
    endpoint = "https://example.test/v1"
    monkeypatch.chdir(root)
    monkeypatch.setenv(ach.API_KEY_ENV, key)
    monkeypatch.setenv(ach.ENDPOINT_ENV, endpoint)
    monkeypatch.setattr(ach, "_load_env_local", lambda: None)

    def fake_run_tool_loop(_prompt, _route, _endpoint, _key, max_turns, _root, **kwargs):
        assert max_turns == 12
        assert kwargs["timeout"] == 34
        assert kwargs["session_timeout"] == 56
        return "done"

    monkeypatch.setattr(ach, "run_tool_loop", fake_run_tool_loop)

    assert (
        ach.main(
            [
                "-p",
                "hello",
                "--model",
                "alib-route",
                "--max-turns",
                "12",
                "--timeout",
                "34",
                "--session-timeout",
                "56",
            ]
        )
        == 0
    )
