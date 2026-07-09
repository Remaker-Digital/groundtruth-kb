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


def test_run_tool_loop_rejects_blank_final_text(tmp_path: Path) -> None:
    root = _root(tmp_path)
    route = base.resolve_model(base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH), None)

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        return {"choices": [{"message": {"content": "   "}}]}

    with pytest.raises(base.CloudHarnessError, match="nonblank text content"):
        base.run_tool_loop("hello", route, "https://test.cloud/api/v1", "key", 1, root, _profile(), chat_func=chat)


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
