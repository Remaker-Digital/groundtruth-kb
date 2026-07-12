# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slice-2 regression tests for the shared cloud-harness runtime base.

Spec-derived from ``ADR-CLOUD-HARNESS-TEMPLATE-001`` (WI-5078). Exercises the base
directly with a *synthetic* adopter profile (not OpenRouter) to prove the base is
adopter-agnostic and config-driven, and asserts the guarantees the ADR + linked specs
require:

* the five-axis :class:`AdopterProfile` config surface + direct-cloud invariant
  (``SPEC-INTAKE-9ec893``) + env-key-NAME auth (``GOV-ENV-LOCAL-AUTHORITY-001``);
* the dialect seam — ``openai-chat`` concrete, the two slice-3 dialects raise the
  slice-3 ``NotImplementedError`` sentinel (ADR Consequences; GO P3 #3);
* fail-closed guard-adapter enforcement for deny AND unavailable
  (``GOV-HARNESS-ONBOARDING-CONTRACT-001`` Layer-3; generalized ``DCL-OLLAMA-TOOL-PARITY-GATE-001``);
* bounded retry/backoff and the framework-free tool loop.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from scripts import cloud_harness_base as base

CFG_PATH = Path(".api-harness") / "routing.toml"

ROUTING_TOML = """
schema_version = 1

[models.tc-default]
model_id = "testvendor/tc-model"
provider = "testcloud"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[models.foreign-row]
model_id = "othervendor/other-model"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read"]

[routing.testcloud]
default_model = "tc-default"
timeout_seconds = 900
session_timeout_seconds = 28800
max_turns = 600

[routing.testcloud.skills]
bridge-review = "tc-default"
"""


def _profile(**overrides) -> base.AdopterProfile:
    kwargs = dict(
        display_name="TestCloud",
        author_identity="TestCloud H",
        author_harness_id="H",
        default_endpoint="https://test.cloud/api/v1",
        auth_env_key="TESTCLOUD_API_KEY",
        provider_routing_key="testcloud",
        routing_config_path=CFG_PATH,
        dialect=base.DIALECT_OPENAI_CHAT,
        hook_tier=base.HOOK_TIER_GUARD_ADAPTER_FLOOR,
        publish_bridge_verdict_tool=True,
        extra_headers={},
    )
    kwargs.update(overrides)
    return base.AdopterProfile(**kwargs)


def _meta() -> base.ModelMetadata:
    return base.ModelMetadata(
        model_id="testvendor/tc-model",
        model_version="tc-model",
        endpoint="https://test.cloud/api/v1",
        route_key="tc-default",
    )


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / CFG_PATH).write_text(ROUTING_TOML.strip() + "\n", encoding="utf-8")
    return root


def _write_native_hook_settings(root: Path, hooks: dict) -> None:
    settings_dir = root / ".claude"
    settings_dir.mkdir(exist_ok=True)
    (settings_dir / "settings.json").write_text(json.dumps({"hooks": hooks}), encoding="utf-8")


class _Resp:
    def __init__(self, body: str) -> None:
        self._body = body

    def __enter__(self) -> _Resp:
        return self

    def __exit__(self, *_exc) -> bool:
        return False

    def read(self) -> bytes:
        return self._body.encode("utf-8")


# --- AdopterProfile config surface (SPEC-INTAKE-9ec893 direct-cloud; GOV-ENV-LOCAL-AUTHORITY-001) ---


def test_profile_accepts_five_axis_config() -> None:
    profile = _profile()
    assert profile.dialect == base.DIALECT_OPENAI_CHAT
    assert profile.auth_env_key == "TESTCLOUD_API_KEY"
    assert profile.default_endpoint.startswith("https://")


def test_profile_rejects_unknown_dialect() -> None:
    with pytest.raises(base.CloudHarnessError, match="unknown dialect"):
        _profile(dialect="grpc-stream")


def test_profile_requires_direct_cloud_endpoint() -> None:
    with pytest.raises(base.CloudHarnessError, match="direct-cloud endpoint"):
        _profile(default_endpoint="")


def test_profile_requires_auth_env_key_name() -> None:
    with pytest.raises(base.CloudHarnessError, match="auth_env_key"):
        _profile(auth_env_key="")


# --- Dialect seam (ADR Consequences; GO P3 #3) ---


def test_openai_chat_dialect_resolves_to_callable() -> None:
    chat = base.resolve_dialect_chat_func(_profile())
    assert callable(chat)


def test_ollama_native_dialect_raises_slice4_sentinel() -> None:
    # anthropic-messages is implemented in slice 3; ollama-native is the lone remaining
    # seam point (implemented with the Ollama re-base in slice 4).
    with pytest.raises(NotImplementedError, match="slice-4"):
        base.resolve_dialect_chat_func(_profile(dialect=base.DIALECT_OLLAMA_NATIVE))


def test_anthropic_messages_dialect_resolves_to_strategy() -> None:
    strategy = base.resolve_dialect_strategy(_profile(dialect=base.DIALECT_ANTHROPIC_MESSAGES))
    assert callable(strategy.chat)
    assert callable(strategy.build_payload)
    assert callable(strategy.parse_message)
    assert callable(strategy.build_tool_schemas)


# --- Config-driven routing (cross-provider isolation) ---


def test_load_routing_config_filters_to_adopter_provider(tmp_path: Path) -> None:
    config = base.load_routing_config(_root(tmp_path), provider_key="testcloud", config_path=CFG_PATH)
    assert set(config.models.keys()) == {"tc-default"}
    assert "foreign-row" not in config.models


def test_resolve_model_default_and_skill(tmp_path: Path) -> None:
    config = base.load_routing_config(_root(tmp_path), provider_key="testcloud", config_path=CFG_PATH)
    assert base.resolve_model(config, None).key == "tc-default"
    assert base.resolve_model(config, None, skill="bridge-review").key == "tc-default"


def test_routing_config_carries_runtime_limits_and_cli_overrides(tmp_path: Path) -> None:
    config = base.load_routing_config(_root(tmp_path), provider_key="testcloud", config_path=CFG_PATH)

    assert (config.timeout_seconds, config.session_timeout_seconds, config.max_turns) == (900, 28800, 600)
    assert base.resolve_runtime_limits(
        config,
        [],
        cli_timeout=1,
        cli_session_timeout=2,
        cli_max_turns=3,
    ) == (900, 28800, 600)
    assert base.resolve_runtime_limits(
        config,
        ["--timeout", "11", "--session-timeout=22", "--max-turns", "33"],
        cli_timeout=11,
        cli_session_timeout=22,
        cli_max_turns=33,
    ) == (11, 22, 33)


# --- Author-metadata injection (base owns it, adopter supplies identity) ---


def test_author_metadata_env_uses_profile_identity() -> None:
    env = base.set_author_metadata_env({}, "testvendor/tc-model", "tc-model", _profile())
    assert env["GTKB_AUTHOR_IDENTITY"] == "TestCloud H"
    assert env["GTKB_AUTHOR_HARNESS_ID"] == "H"
    assert env["GTKB_AUTHOR_MODEL"] == "testvendor/tc-model"
    assert env["GTKB_AUTHOR_MODEL_VERSION"] == "tc-model"
    assert "TestCloud endpoint=" in env["GTKB_AUTHOR_MODEL_CONFIGURATION"]


# --- Fail-closed guard-adapter enforcement (deny AND unavailable) ---


def _allow_runner(path: Path, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
    return base.GuardExecutionResult(returncode=0, stdout="{}")


def test_guard_denial_fails_closed(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "fake_guard.py").write_text("print('{}')\n", encoding="utf-8")

    def deny(path: Path, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(returncode=0, stdout='{"decision": "block", "reason": "nope"}')

    with pytest.raises(base.CloudHarnessError, match="guard denied"):
        base.invoke_guard_adapter(
            "Write",
            {"path": "bridge/example-001.md", "content": "NEW\n"},
            _meta(),
            root,
            _profile(),
            guard_runner=deny,
            guard_paths=[Path("fake_guard.py")],
        )


def test_guard_unavailable_fails_closed(tmp_path: Path) -> None:
    root = _root(tmp_path)
    with pytest.raises(base.CloudHarnessError, match="guard script is missing"):
        base.invoke_guard_adapter(
            "Write",
            {"path": "bridge/example-001.md", "content": "NEW\n"},
            _meta(),
            root,
            _profile(),
            guard_runner=_allow_runner,
            guard_paths=[Path("does-not-exist-guard.py")],
        )


def test_guard_empty_output_fails_closed(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "fake_guard.py").write_text("print('')\n", encoding="utf-8")

    def empty(path: Path, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(returncode=0, stdout="")

    with pytest.raises(base.CloudHarnessError, match="guard emitted empty output"):
        base.invoke_guard_adapter(
            "Write",
            {"path": "bridge/example-001.md", "content": "NEW\n"},
            _meta(),
            root,
            _profile(),
            guard_runner=empty,
            guard_paths=[Path("fake_guard.py")],
        )


@pytest.mark.parametrize(
    ("guard_result", "error_match"),
    [
        (base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True), "guard timed out"),
        (base.GuardExecutionResult(returncode=1, stdout="", stderr="failed"), "guard exited nonzero"),
        (base.GuardExecutionResult(returncode=0, stdout="not json", stderr=""), "guard emitted malformed JSON"),
    ],
    ids=("timeout", "nonzero", "malformed"),
)
def test_guard_adapter_runtime_failures_remain_fail_closed(
    tmp_path: Path,
    guard_result: base.GuardExecutionResult,
    error_match: str,
) -> None:
    root = _root(tmp_path)
    (root / "fake_guard.py").write_text("print('{}')\n", encoding="utf-8")

    def guard_runner(_path: Path, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return guard_result

    with pytest.raises(base.CloudHarnessError, match=error_match):
        base.invoke_guard_adapter(
            "Write",
            {"path": "out.txt", "content": "content"},
            _meta(),
            root,
            _profile(),
            guard_runner=guard_runner,
            guard_paths=[Path("fake_guard.py")],
        )


def test_read_only_tool_skips_guard(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "note.txt").write_text("hello", encoding="utf-8")
    result = base.dispatch_tool_call("Read", {"path": "note.txt"}, _meta(), root, _profile())
    assert result == "hello"


# --- Bounded retry (openai-chat dialect transport) ---


def test_openai_chat_retries_transient_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    body = base.json.dumps({"choices": [{"message": {"content": "ok"}}]})

    def fake_urlopen(request, timeout: float):
        calls.append(1)
        if len(calls) == 1:
            raise base.urllib.error.HTTPError("https://test.cloud/chat/completions", 502, "e", {}, None)
        return _Resp(body)

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(base.time, "sleep", lambda _s: None)

    result = base.openai_chat_completion("https://test.cloud/api/v1", "key", {"model": "m"}, label="TestCloud")
    assert result["choices"][0]["message"]["content"] == "ok"
    assert len(calls) == 2


def test_openai_chat_exhaustion_uses_provider_label(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request, timeout: float):
        raise base.urllib.error.HTTPError("https://test.cloud/chat/completions", 500, "e", {}, None)

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(base.time, "sleep", lambda _s: None)

    with pytest.raises(base.CloudHarnessError, match=r"TestCloud completions request failed .*HTTP 500"):
        base.openai_chat_completion("https://test.cloud/api/v1", "key", {"model": "m"}, label="TestCloud")


# --- WI-5066: DNS / wall-clock bound on the provider call ---


def test_wall_clock_bound_returns_result_when_call_completes() -> None:
    assert base._call_with_wall_clock_bound(lambda: "ok", 5.0, label="TestCloud", noun="completions") == "ok"


def test_wall_clock_bound_reraises_call_error() -> None:
    def _boom() -> str:
        raise ValueError("provider parse error")

    with pytest.raises(ValueError, match="provider parse error"):
        base._call_with_wall_clock_bound(_boom, 5.0, label="TestCloud", noun="completions")


def test_wall_clock_bound_times_out_on_stall_and_is_retryable() -> None:
    release = threading.Event()

    def _stall() -> str:
        release.wait(timeout=5.0)  # simulates an unbounded getaddrinfo/DNS stall
        return "late"

    try:
        with pytest.raises(base._ProviderCallTimeout) as excinfo:
            base._call_with_wall_clock_bound(_stall, 0.05, label="TestCloud", noun="completions")
    finally:
        release.set()
    # The synthetic timeout must be a TimeoutError the transport-retry classifier absorbs.
    assert isinstance(excinfo.value, TimeoutError)
    assert base._is_retryable_provider_transport_error(excinfo.value)


def test_openai_chat_dns_stall_is_bounded_and_raises_classified_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-5066: a urlopen that never returns (DNS stall) is bounded, retried, and finally
    fails with a classified CloudHarnessError instead of blocking the worker forever."""
    release = threading.Event()
    calls: list[int] = []

    def fake_urlopen(request, timeout: float):
        calls.append(1)
        release.wait(timeout=5.0)  # never resolves within the per-attempt wall-clock bound
        return _Resp("{}")

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(base.time, "sleep", lambda _s: None)

    try:
        with pytest.raises(base.CloudHarnessError, match=r"TestCloud completions request"):
            base.openai_chat_completion(
                "https://test.cloud/api/v1", "key", {"model": "m"}, timeout=0.3, label="TestCloud"
            )
    finally:
        release.set()
    assert calls  # the transport was attempted at least once before the bound fired


# --- Framework-free tool loop ---


def test_run_tool_loop_returns_final_text(tmp_path: Path) -> None:
    root = _root(tmp_path)
    route = base.resolve_model(base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH), None)

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        return {"choices": [{"message": {"content": "done"}}]}

    result = base.run_tool_loop("hello", route, "https://test.cloud/api/v1", "key", 1, root, _profile(), chat_func=chat)
    assert result == "done"


def test_run_tool_loop_reports_allowlisted_turn_metadata_to_telemetry(tmp_path: Path) -> None:
    root = _root(tmp_path)
    route = base.resolve_model(base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH), None)

    class Recorder:
        def __init__(self) -> None:
            self.turns: list[tuple[int, list[str], dict]] = []
            self.stop_reasons: list[str] = []

        def record_turn(self, index: int, tool_names: list[str], *, provider_response: dict) -> None:
            self.turns.append((index, tool_names, provider_response))

        def set_model(self, _model_id: str, _model_version: str) -> None:
            return None

        def finish(self, *, stop_reason: str) -> None:
            self.stop_reasons.append(stop_reason)

    recorder = Recorder()

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        return {"choices": [{"message": {"content": "done"}}], "usage": {"total_tokens": 1}}

    assert (
        base.run_tool_loop(
            "hello",
            route,
            "https://test.cloud/api/v1",
            "key",
            1,
            root,
            _profile(),
            chat_func=chat,
            telemetry=recorder,
        )
        == "done"
    )
    assert recorder.turns == [(1, [], {"choices": [{"message": {"content": "done"}}], "usage": {"total_tokens": 1}})]
    assert recorder.stop_reasons == ["final_response"]


def test_run_tool_loop_recovers_blank_final_without_empty_assistant_message(tmp_path: Path) -> None:
    root = _root(tmp_path)
    route = base.resolve_model(base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH), None)
    payloads: list[dict] = []
    responses = iter(
        [
            {"choices": [{"message": {"content": "   "}}]},
            {"choices": [{"message": {"content": ""}}]},
            {"choices": [{"message": {"content": "done"}}]},
        ]
    )

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        payloads.append(payload)
        return next(responses)

    assert (
        base.run_tool_loop("hello", route, "https://test.cloud/api/v1", "key", 3, root, _profile(), chat_func=chat)
        == "done"
    )
    assert payloads[1]["messages"][-1] == {"role": "user", "content": base.BLANK_FINAL_RECOVERY_PROMPT}
    assert payloads[2]["messages"][-2:] == [
        {"role": "user", "content": base.BLANK_FINAL_RECOVERY_PROMPT},
        {"role": "user", "content": base.BLANK_FINAL_RECOVERY_PROMPT},
    ]
    assert not any(
        message.get("role") == "assistant" and not str(message.get("content") or "").strip()
        for payload in payloads
        for message in payload["messages"]
    )


def test_run_tool_loop_repeated_blank_finals_fail_closed_at_overall_turn_budget(tmp_path: Path) -> None:
    root = _root(tmp_path)
    route = base.resolve_model(base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH), None)
    calls = 0

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        nonlocal calls
        calls += 1
        return {"choices": [{"message": {"content": "   "}}]}

    with pytest.raises(base.CloudHarnessError, match="max-turn exhaustion"):
        base.run_tool_loop("hello", route, "https://test.cloud/api/v1", "key", 5, root, _profile(), chat_func=chat)
    assert calls == 5


# --- Slice 3: hook-tier + auth-style validation (native-hook seam is a flag; floor stays enforced) ---


def _anthropic_profile(**overrides) -> base.AdopterProfile:
    return _profile(dialect=base.DIALECT_ANTHROPIC_MESSAGES, **overrides)


def test_profile_rejects_unknown_hook_tier() -> None:
    with pytest.raises(base.CloudHarnessError, match="unknown hook_tier"):
        _profile(hook_tier="webhook-callbacks")


def test_profile_rejects_unknown_auth_style() -> None:
    with pytest.raises(base.CloudHarnessError, match="unknown auth_style"):
        _profile(auth_style="oauth2")


def test_profile_accepts_native_full_hooks_tier() -> None:
    profile = _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL)
    assert profile.hook_tier == base.HOOK_TIER_NATIVE_FULL


def test_native_full_hooks_tier_still_enforces_guard_floor(tmp_path: Path) -> None:
    # Owner AUQ (DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE): the
    # native-full-hooks tier is a validated seam/flag; the fail-closed guard-adapter floor
    # remains the enforced mechanism regardless of tier.
    root = _root(tmp_path)
    (root / "fake_guard.py").write_text("print('{}')\n", encoding="utf-8")
    profile = _anthropic_profile(hook_tier=base.HOOK_TIER_NATIVE_FULL)

    def deny(path: Path, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(returncode=0, stdout='{"decision": "block", "reason": "nope"}')

    with pytest.raises(base.CloudHarnessError, match="guard denied"):
        base.invoke_guard_adapter(
            "Write",
            {"path": "bridge/example-001.md", "content": "NEW\n"},
            _meta(),
            root,
            profile,
            guard_runner=deny,
            guard_paths=[Path("fake_guard.py")],
        )


def test_native_full_hooks_lifecycle_runs_in_order(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "note.txt").write_text("file body", encoding="utf-8")
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_SESSION_START: [{"hooks": [{"type": "command", "command": "record session"}]}],
            base.NATIVE_HOOK_USER_PROMPT_SUBMIT: [{"hooks": [{"type": "command", "command": "record prompt"}]}],
            base.NATIVE_HOOK_PRE_TOOL_USE: [
                {"matcher": "Read", "hooks": [{"type": "command", "command": "record pre"}]}
            ],
            base.NATIVE_HOOK_POST_TOOL_USE: [
                {"matcher": "Read", "hooks": [{"type": "command", "command": "record post"}]}
            ],
            base.NATIVE_HOOK_STOP: [{"hooks": [{"type": "command", "command": "record stop"}]}],
        },
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    turns: list[dict] = []
    hook_events: list[tuple[str, dict, dict]] = []

    def hook_runner(command: str, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
        hook_events.append((command, dict(payload), dict(env)))
        return base.GuardExecutionResult(returncode=0, stdout="{}")

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "function": {"name": "Read", "arguments": {"path": "note.txt"}},
                                }
                            ],
                        }
                    }
                ]
            }
        return {"choices": [{"message": {"content": "done"}}]}

    result = base.run_tool_loop(
        "read the note",
        route,
        "https://test.cloud/api/v1",
        "key",
        3,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        native_hook_runner=hook_runner,
    )

    assert result == "done"
    assert [event[1]["hook_event_name"] for event in hook_events] == [
        base.NATIVE_HOOK_SESSION_START,
        base.NATIVE_HOOK_USER_PROMPT_SUBMIT,
        base.NATIVE_HOOK_PRE_TOOL_USE,
        base.NATIVE_HOOK_POST_TOOL_USE,
        base.NATIVE_HOOK_STOP,
    ]
    pre_payload = hook_events[2][1]
    post_payload = hook_events[3][1]
    assert pre_payload["tool_name"] == "Read"
    assert pre_payload["tool_input"] == {"path": "note.txt"}
    assert post_payload["tool_response"] == "file body"
    assert hook_events[0][2]["CLAUDE_PROJECT_DIR"] == str(root)


@pytest.mark.parametrize(
    "post_result",
    [
        base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True),
        base.GuardExecutionResult(returncode=1, stdout="", stderr="maintenance failed"),
        base.GuardExecutionResult(returncode=0, stdout="informational non-json output", stderr=""),
        base.GuardExecutionResult(returncode=0, stdout="[]", stderr=""),
    ],
    ids=("timeout", "nonzero", "malformed", "non-object"),
)
def test_native_posttool_lifecycle_failures_do_not_mask_completed_tool(
    tmp_path: Path,
    post_result: base.GuardExecutionResult,
) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_POST_TOOL_USE: [
                {"matcher": "Read", "hooks": [{"type": "command", "command": "maintenance hook"}]}
            ]
        },
    )

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return post_result

    assert (
        base.invoke_native_hooks(
            base.NATIVE_HOOK_POST_TOOL_USE,
            _meta(),
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            tool_name="Read",
            tool_input={"path": "note.txt"},
            tool_response="completed result",
            native_hook_runner=hook_runner,
        )
        == {}
    )


def test_native_posttool_explicit_block_remains_fail_closed(tmp_path: Path) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_POST_TOOL_USE: [{"matcher": "Read", "hooks": [{"type": "command", "command": "post gate"}]}]},
    )

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(returncode=0, stdout='{"decision": "block", "reason": "post denied"}')

    with pytest.raises(base.CloudHarnessError, match="native hook blocked PostToolUse.*post denied"):
        base.invoke_native_hooks(
            base.NATIVE_HOOK_POST_TOOL_USE,
            _meta(),
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            tool_name="Read",
            tool_input={"path": "note.txt"},
            tool_response="completed result",
            native_hook_runner=hook_runner,
        )


def test_native_posttool_fail_soft_does_not_change_pretool_timeout_enforcement(tmp_path: Path) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_PRE_TOOL_USE: [{"matcher": "Read", "hooks": [{"type": "command", "command": "pre gate"}]}]},
    )

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True)

    with pytest.raises(base.CloudHarnessError, match="native hook timed out: PreToolUse"):
        base.invoke_native_hooks(
            base.NATIVE_HOOK_PRE_TOOL_USE,
            _meta(),
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            tool_name="Read",
            tool_input={"path": "note.txt"},
            native_hook_runner=hook_runner,
        )


@pytest.mark.parametrize(
    "stop_result",
    [
        base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True),
        base.GuardExecutionResult(returncode=1, stdout="", stderr="informational failure"),
        base.GuardExecutionResult(returncode=0, stdout="informational non-json output", stderr=""),
    ],
    ids=("timeout", "nonblocking-nonzero", "malformed-informational-output"),
)
def test_native_stop_lifecycle_failures_preserve_candidate_result(
    tmp_path: Path,
    stop_result: base.GuardExecutionResult,
) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_STOP: [{"hooks": [{"type": "command", "command": "stop hook"}]}]},
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return stop_result

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        return {"choices": [{"message": {"content": "candidate result"}}]}

    assert (
        base.run_tool_loop(
            "finish",
            route,
            "https://test.cloud/api/v1",
            "key",
            1,
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            chat_func=chat,
            native_hook_runner=hook_runner,
        )
        == "candidate result"
    )


@pytest.mark.parametrize(
    "stop_result",
    [
        base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True),
        base.GuardExecutionResult(returncode=3, stdout="", stderr="informational failure"),
        base.GuardExecutionResult(returncode=0, stdout="informational non-json output", stderr=""),
    ],
    ids=("timeout", "nonblocking-nonzero", "malformed-informational-output"),
)
def test_native_stop_lifecycle_failures_preserve_original_exception(
    tmp_path: Path,
    stop_result: base.GuardExecutionResult,
) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_STOP: [{"hooks": [{"type": "command", "command": "stop hook"}]}]},
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return stop_result

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        raise RuntimeError("original provider exception")

    with pytest.raises(RuntimeError, match="original provider exception"):
        base.run_tool_loop(
            "finish",
            route,
            "https://test.cloud/api/v1",
            "key",
            1,
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            chat_func=chat,
            native_hook_runner=hook_runner,
        )


@pytest.mark.parametrize(
    ("first_stop_result", "expected_reason"),
    [
        (base.GuardExecutionResult(returncode=2, stdout="", stderr="exit-two reason"), "exit-two reason"),
        (
            base.GuardExecutionResult(
                returncode=0,
                stdout='{"decision": "block", "reason": "json-block reason"}',
                stderr="",
            ),
            "json-block reason",
        ),
    ],
    ids=("exit-two", "json-block"),
)
def test_native_stop_explicit_block_continues_model_loop_with_reason(
    tmp_path: Path,
    first_stop_result: base.GuardExecutionResult,
    expected_reason: str,
) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_STOP: [{"hooks": [{"type": "command", "command": "stop hook"}]}]},
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    stop_calls = 0
    turns: list[dict] = []

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        nonlocal stop_calls
        stop_calls += 1
        if stop_calls == 1:
            return first_stop_result
        return base.GuardExecutionResult(returncode=0, stdout="{}", stderr="")

    def chat(_endpoint: str, _api_key: str, payload: dict, _timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 2:
            assert any(expected_reason in message.get("content", "") for message in payload["messages"])
        return {"choices": [{"message": {"content": f"candidate {len(turns)}"}}]}

    result = base.run_tool_loop(
        "finish",
        route,
        "https://test.cloud/api/v1",
        "key",
        3,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        native_hook_runner=hook_runner,
    )

    assert result == "candidate 2"
    assert stop_calls == 2


def test_native_stop_repeated_blocks_fail_closed_at_eight_block_limit(tmp_path: Path) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_STOP: [{"hooks": [{"type": "command", "command": "stop hook"}]}]},
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    stop_calls = 0
    chat_calls = 0

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        nonlocal stop_calls
        stop_calls += 1
        return base.GuardExecutionResult(returncode=2, stdout="", stderr="still blocked")

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        nonlocal chat_calls
        chat_calls += 1
        return {"choices": [{"message": {"content": "candidate"}}]}

    with pytest.raises(base.CloudHarnessError, match="blocked completion 8 consecutive times"):
        base.run_tool_loop(
            "finish",
            route,
            "https://test.cloud/api/v1",
            "key",
            base.MAX_NATIVE_STOP_BLOCKS + 1,
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            chat_func=chat,
            native_hook_runner=hook_runner,
        )

    assert chat_calls == base.MAX_NATIVE_STOP_BLOCKS
    assert stop_calls == base.MAX_NATIVE_STOP_BLOCKS


@pytest.mark.parametrize(
    ("hook_result", "error_match"),
    [
        (base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True), "native hook timed out"),
        (base.GuardExecutionResult(returncode=1, stdout="", stderr="failed"), "native hook exited nonzero"),
        (base.GuardExecutionResult(returncode=0, stdout="not json", stderr=""), "native hook emitted malformed JSON"),
    ],
    ids=("timeout", "nonzero", "malformed"),
)
def test_native_pretool_lifecycle_errors_remain_fail_closed(
    tmp_path: Path,
    hook_result: base.GuardExecutionResult,
    error_match: str,
) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_PRE_TOOL_USE: [{"matcher": "Read", "hooks": [{"type": "command", "command": "pre hook"}]}]},
    )

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return hook_result

    with pytest.raises(base.CloudHarnessError, match=error_match):
        base.invoke_native_hooks(
            base.NATIVE_HOOK_PRE_TOOL_USE,
            _meta(),
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            tool_name="Read",
            tool_input={"path": "note.txt"},
            native_hook_runner=hook_runner,
        )


def test_native_full_hooks_empty_pretool_output_allows_later_hooks_and_tool(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "note.txt").write_text("file body", encoding="utf-8")
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_PRE_TOOL_USE: [
                {
                    "matcher": "Read",
                    "hooks": [
                        {"type": "command", "command": "empty pre"},
                        {"type": "command", "command": "later pre"},
                    ],
                }
            ]
        },
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    hook_commands: list[str] = []
    turns: list[dict] = []

    def hook_runner(command: str, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
        hook_commands.append(command)
        stdout = "" if command == "empty pre" else "{}"
        return base.GuardExecutionResult(returncode=0, stdout=stdout)

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "function": {"name": "Read", "arguments": {"path": "note.txt"}},
                                }
                            ],
                        }
                    }
                ]
            }
        assert any(message.get("content") == "file body" for message in payload["messages"])
        return {"choices": [{"message": {"content": "done"}}]}

    result = base.run_tool_loop(
        "read the note",
        route,
        "https://test.cloud/api/v1",
        "key",
        3,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        native_hook_runner=hook_runner,
    )

    assert result == "done"
    assert hook_commands == ["empty pre", "later pre"]


def test_native_full_hooks_pretool_block_feeds_reason_to_model(tmp_path: Path) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_SESSION_START: [{"hooks": [{"type": "command", "command": "record session"}]}],
            base.NATIVE_HOOK_USER_PROMPT_SUBMIT: [{"hooks": [{"type": "command", "command": "record prompt"}]}],
            base.NATIVE_HOOK_PRE_TOOL_USE: [
                {"matcher": "Read", "hooks": [{"type": "command", "command": "record pre"}]}
            ],
            base.NATIVE_HOOK_POST_TOOL_USE: [
                {"matcher": "Read", "hooks": [{"type": "command", "command": "record post"}]}
            ],
            base.NATIVE_HOOK_STOP: [{"hooks": [{"type": "command", "command": "record stop"}]}],
        },
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    turns: list[dict] = []
    hook_payloads: list[dict] = []

    def hook_runner(command: str, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
        hook_payloads.append(dict(payload))
        if payload["hook_event_name"] == base.NATIVE_HOOK_PRE_TOOL_USE:
            return base.GuardExecutionResult(0, '{"decision": "block", "reason": "native denied"}')
        return base.GuardExecutionResult(0, "{}")

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "function": {"name": "Read", "arguments": {"path": "missing.txt"}},
                                }
                            ],
                        }
                    }
                ]
            }
        assert any("native denied" in message.get("content", "") for message in payload["messages"])
        return {"choices": [{"message": {"content": "blocked noted"}}]}

    result = base.run_tool_loop(
        "read the missing note",
        route,
        "https://test.cloud/api/v1",
        "key",
        3,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        native_hook_runner=hook_runner,
    )

    assert result == "blocked noted"
    assert hook_payloads[3]["tool_response"] == "ERROR: native hook blocked Read: native denied"


def test_native_full_hooks_run_tool_loop_still_enforces_guard_floor(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / ".claude" / "hooks").mkdir(parents=True)
    (root / ".claude" / "hooks" / "credential-scan.py").write_text("print('{}')\n", encoding="utf-8")
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Write",))
    turns: list[dict] = []

    def deny_guard(path: Path, payload: dict, env: dict, timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(0, '{"decision": "block", "reason": "guard denied"}')

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "function": {
                                        "name": "Write",
                                        "arguments": {"path": "out.txt", "content": "content"},
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        assert any("guard denied Write" in message.get("content", "") for message in payload["messages"])
        return {"choices": [{"message": {"content": "done"}}]}

    result = base.run_tool_loop(
        "write the file",
        route,
        "https://test.cloud/api/v1",
        "key",
        3,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        guard_runner=deny_guard,
    )

    assert result == "done"
    assert not (root / "out.txt").exists()


# --- Slice 3: anthropic-messages dialect ---


def test_anthropic_build_tool_schemas_uses_input_schema() -> None:
    strategy = base.resolve_dialect_strategy(_anthropic_profile())
    schemas = strategy.build_tool_schemas(["Read", "Write"])
    assert [s["name"] for s in schemas] == ["Read", "Write"]
    for s in schemas:
        assert "input_schema" in s
        assert "function" not in s  # not the OpenAI wrapper shape
        assert s["input_schema"]["type"] == "object"


def test_anthropic_build_payload_translates_system_tooluse_and_toolresult() -> None:
    strategy = base.resolve_dialect_strategy(_anthropic_profile())
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    messages = [
        {"role": "system", "content": "sys-prompt"},
        {"role": "user", "content": "hello"},
        {
            "role": "assistant",
            "content": "thinking",
            "tool_calls": [{"id": "tu1", "function": {"name": "Read", "arguments": {"path": "note.txt"}}}],
        },
        {"role": "tool", "tool_call_id": "tu1", "content": "file contents"},
    ]
    payload = strategy.build_payload(messages, route, strategy.build_tool_schemas(["Read"]))

    assert payload["system"] == "sys-prompt"
    assert payload["max_tokens"] == base.DEFAULT_ANTHROPIC_MAX_TOKENS
    assert payload["model"] == "testvendor/tc-model"
    # user, assistant(text+tool_use), user(tool_result)
    assert [m["role"] for m in payload["messages"]] == ["user", "assistant", "user"]
    assistant_blocks = payload["messages"][1]["content"]
    assert {b["type"] for b in assistant_blocks} == {"text", "tool_use"}
    tool_use = next(b for b in assistant_blocks if b["type"] == "tool_use")
    assert tool_use["id"] == "tu1" and tool_use["name"] == "Read" and tool_use["input"] == {"path": "note.txt"}
    tool_result = payload["messages"][2]["content"][0]
    assert tool_result["type"] == "tool_result" and tool_result["tool_use_id"] == "tu1"
    assert tool_result["content"] == "file contents"


def test_anthropic_parse_message_extracts_text_and_tool_use() -> None:
    strategy = base.resolve_dialect_strategy(_anthropic_profile())
    response = {
        "model": "m",
        "stop_reason": "tool_use",
        "content": [
            {"type": "text", "text": "let me read that"},
            {"type": "tool_use", "id": "tu9", "name": "Read", "input": {"path": "x.txt"}},
        ],
    }
    message = strategy.parse_message(response)
    assert message["content"] == "let me read that"
    assert message["tool_calls"] == [{"id": "tu9", "function": {"name": "Read", "arguments": {"path": "x.txt"}}}]


def test_anthropic_auth_style_x_api_key_header(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}
    body = base.json.dumps({"content": [{"type": "text", "text": "ok"}]})

    def fake_urlopen(request, timeout: float):
        captured["request"] = request
        return _Resp(body)

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)
    base.anthropic_messages_completion(
        "https://alibaba.test/v1",
        "secret-token",
        {"model": "m"},
        label="TestCloud",
        auth_style=base.AUTH_STYLE_X_API_KEY,
    )
    headers = captured["request"].headers
    assert headers.get("X-api-key") == "secret-token"
    assert "Authorization" not in headers
    assert captured["request"].full_url == "https://alibaba.test/v1/messages"


def test_anthropic_auth_style_authorization_bearer_header(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}
    body = base.json.dumps({"content": [{"type": "text", "text": "ok"}]})

    def fake_urlopen(request, timeout: float):
        captured["request"] = request
        return _Resp(body)

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)
    base.anthropic_messages_completion(
        "https://alibaba.test/v1",
        "secret-token",
        {"model": "m"},
        label="TestCloud",
        auth_style=base.AUTH_STYLE_AUTHORIZATION_BEARER,
    )
    headers = captured["request"].headers
    assert headers.get("Authorization") == "Bearer secret-token"
    assert "X-api-key" not in headers


def test_anthropic_retry_parity_transient_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    body = base.json.dumps({"content": [{"type": "text", "text": "ok"}]})

    def fake_urlopen(request, timeout: float):
        calls.append(1)
        if len(calls) == 1:
            raise base.urllib.error.HTTPError("https://alibaba.test/v1/messages", 502, "e", {}, None)
        return _Resp(body)

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(base.time, "sleep", lambda _s: None)
    result = base.anthropic_messages_completion("https://alibaba.test/v1", "key", {"model": "m"}, label="TestCloud")
    assert result["content"][0]["text"] == "ok"
    assert len(calls) == 2


def test_anthropic_exhaustion_uses_messages_noun(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request, timeout: float):
        raise base.urllib.error.HTTPError("https://alibaba.test/v1/messages", 500, "e", {}, None)

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(base.time, "sleep", lambda _s: None)
    with pytest.raises(base.CloudHarnessError, match=r"TestCloud messages request failed .*HTTP 500"):
        base.anthropic_messages_completion("https://alibaba.test/v1", "key", {"model": "m"}, label="TestCloud")


def test_run_tool_loop_anthropic_round_trip(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "note.txt").write_text("file body", encoding="utf-8")
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    turns: list[dict] = []

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            return {
                "model": "m",
                "stop_reason": "tool_use",
                "content": [{"type": "tool_use", "id": "tu1", "name": "Read", "input": {"path": "note.txt"}}],
            }
        return {"model": "m", "content": [{"type": "text", "text": "done"}]}

    result = base.run_tool_loop(
        "read the note", route, "https://alibaba.test/v1", "key", 3, root, _anthropic_profile(), chat_func=chat
    )
    assert result == "done"
    # first payload is anthropic-shaped (top-level system absent here, messages list present, max_tokens set)
    assert turns[0]["max_tokens"] == base.DEFAULT_ANTHROPIC_MAX_TOKENS
    assert turns[0]["messages"][0]["role"] == "user"
    # second turn carried the tool_use + tool_result translation
    assert any(
        block.get("type") == "tool_result"
        for message in turns[1]["messages"]
        if isinstance(message.get("content"), list)
        for block in message["content"]
    )


def test_cloud_template_inherits_local_diagnostic_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from groundtruth_kb import harness_diagnostic

    root = _root(tmp_path)
    captured: dict[str, object] = {}

    def fake_diagnostic(project_root: Path, harness_id: str) -> dict[str, object]:
        captured.update({"project_root": project_root, "harness_id": harness_id})
        return {"schema_id": harness_diagnostic.SCHEMA_ID, "provider_health": {"mode": "local"}}

    monkeypatch.setattr(harness_diagnostic, "diagnose_harness", fake_diagnostic)

    result = base.run_diagnostic(root, harness_id="H")

    assert result["schema_id"] == "gtkb.harness_diagnostic.v1"
    assert captured == {"project_root": root, "harness_id": "H"}


def test_publish_bridge_verdict_schema_has_no_path_or_version_authority() -> None:
    schemas = base.build_tool_schemas([base.PUBLISH_BRIDGE_VERDICT_TOOL])

    schema = schemas[0]["function"]
    properties = schema["parameters"]["properties"]
    assert schema["name"] == "PublishBridgeVerdict"
    assert set(schema["parameters"]["required"]) == {"slug", "verdict", "content"}
    assert "path" not in properties
    assert "file_path" not in properties
    assert "version" not in properties
    assert properties["verdict"]["enum"] == ["GO", "NO-GO", "VERIFIED"]


def test_provider_verdict_publisher_bootstraps_project_root_under_safe_path() -> None:
    project_root = Path(__file__).resolve().parents[2]
    code = f"""
import sys
from pathlib import Path

project_root = Path({str(project_root)!r})
sys.path.insert(0, str(project_root / "scripts"))
import cloud_harness_base as base
sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != project_root.resolve()]
publisher = base._load_provider_verdict_publisher(project_root)
assert publisher.__module__ == "scripts.gtkb_bridge_writer"
assert str(project_root.resolve()) in sys.path
"""

    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout


def test_dispatch_worker_role_document_uses_canonical_keyword(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from groundtruth_kb.session import envelope

    root = _root(tmp_path)
    captured: dict[str, object] = {}
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    for key in base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-H-envelope")
    monkeypatch.setattr(
        envelope,
        "ensure_worker_session",
        lambda project_root, **kwargs: captured.update(project_root=project_root, **kwargs),
    )

    base.ensure_dispatch_worker_role_document(root, _profile())

    assert captured == {
        "project_root": root,
        "harness_name": "testcloud",
        "harness_id": "H",
        "session_id": "dispatch-H-envelope",
        "role": "loyal-opposition",
        "role_source": "dispatcher_composition",
        "init_keyword": "::init gtkb lo",
        "dispatch_run_id": "dispatch-H-envelope",
    }


def test_dispatch_worker_role_document_rejects_unknown_keyword(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb maybe")

    with pytest.raises(base.CloudHarnessError, match="unsupported dispatcher init keyword"):
        base.ensure_dispatch_worker_role_document(_root(tmp_path), _profile())


def test_publish_bridge_verdict_is_filtered_outside_lo_skills() -> None:
    allowed = ("Read", base.PUBLISH_BRIDGE_VERDICT_TOOL)

    assert base.allowed_tools_for_skill(allowed, "bridge-review", publish_bridge_verdict_tool=True) == allowed
    assert base.allowed_tools_for_skill(allowed, "verification", publish_bridge_verdict_tool=True) == allowed
    assert base.allowed_tools_for_skill(allowed, "implementation") == ("Read",)
    assert base.allowed_tools_for_skill(allowed, None) == ("Read",)


def test_dispatch_publish_bridge_verdict_uses_trusted_runtime_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import gtkb_bridge_writer as writer

    root = _root(tmp_path)
    captured: dict[str, object] = {}

    class _Published:
        def to_dict(self) -> dict[str, object]:
            return {"verdict_path": "bridge/example-002.md", "claim_released": True}

    def fake_publish(slug, verdict, content, project_root, **kwargs):
        captured.update(
            slug=slug,
            verdict=verdict,
            content=content,
            project_root=project_root,
            **kwargs,
        )
        return _Published()

    monkeypatch.setattr(writer, "publish_lo_verdict", fake_publish)
    for key in base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-H-1")

    result = base.dispatch_tool_call(
        base.PUBLISH_BRIDGE_VERDICT_TOOL,
        {
            "slug": "example",
            "verdict": "GO",
            "content": "GO\n\nResponds to: bridge/example-001.md\n",
        },
        _meta(),
        root,
        _profile(),
        skill="bridge-review",
    )

    assert json.loads(result)["verdict_path"] == "bridge/example-002.md"
    assert captured["session_id"] == "dispatch-H-1"
    assert captured["harness_name"] == "testcloud"
    metadata = captured["author_metadata"]
    assert isinstance(metadata, dict)
    assert metadata["author_harness_id"] == "H"
    assert metadata["author_model"] == "testvendor/tc-model"


def test_dispatch_publish_bridge_verdict_denies_non_lo_skill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _root(tmp_path)
    for key in base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-H-1")

    with pytest.raises(base.CloudHarnessError, match="bridge-review/verification"):
        base.dispatch_tool_call(
            base.PUBLISH_BRIDGE_VERDICT_TOOL,
            {"slug": "example", "verdict": "GO", "content": "GO\n"},
            _meta(),
            root,
            _profile(),
            skill="implementation",
        )


def test_dispatch_publish_bridge_verdict_denies_profile_without_capability(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path)
    for key in base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-F-1")

    with pytest.raises(base.CloudHarnessError, match="not enabled for this provider profile"):
        base.dispatch_tool_call(
            base.PUBLISH_BRIDGE_VERDICT_TOOL,
            {"slug": "example", "verdict": "GO", "content": "GO\n"},
            _meta(),
            root,
            _profile(publish_bridge_verdict_tool=False, author_harness_id="F"),
            skill="bridge-review",
        )
