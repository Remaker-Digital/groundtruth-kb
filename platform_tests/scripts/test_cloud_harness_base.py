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

import http.client
import io
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from scripts import cloud_harness_base as base

CFG_PATH = Path(".api-harness") / "testcloud" / "routing.toml"
READ_TRUNCATION_MARKER_RE = re.compile(
    r"\n\n\[Read truncated: returned characters \[(\d+), (\d+)\) of (\d+)\. "
    r"Continue with offset=(\d+)\.\]$"
)

# c123 (batch design WP2 2.1): no [routing.testcloud.skills] table; the loader refuses one (see the refusal test).
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
session_timeout_seconds = 3600
max_turns = 600
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
        native_hook_settings_path=CFG_PATH.parent / "settings.json",
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
    (root / CFG_PATH.parent).mkdir(parents=True)
    (root / CFG_PATH.parent / "settings.json").write_text('{"hooks": {}}', encoding="utf-8")
    (root / CFG_PATH).write_text(ROUTING_TOML.strip() + "\n", encoding="utf-8")
    return root


def _write_native_hook_settings(root: Path, hooks: dict) -> None:
    settings_dir = root / CFG_PATH.parent
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


def test_resolve_model_default_and_named_route(tmp_path: Path) -> None:
    config = base.load_routing_config(_root(tmp_path), provider_key="testcloud", config_path=CFG_PATH)
    assert base.resolve_model(config, None).key == "tc-default"
    # c123 (batch design WP2 2.1): a registration names its route with --model; there is no skill argument.
    assert base.resolve_model(config, "tc-default").key == "tc-default"
    for unrouted in ("foreign-row", "bridge-review"):
        with pytest.raises(base.CloudHarnessError, match=f"unknown model route: {unrouted}"):
            base.resolve_model(config, unrouted)
    with pytest.raises(TypeError):
        base.resolve_model(config, None, skill="bridge-review")


@pytest.mark.parametrize(
    "table",
    [
        '[routing.testcloud.skills]\nbridge-review = "tc-default"\n',
        '[routing.testcloud.skills.bridge-review]\nmodel = "tc-default"\n',
        "[routing.testcloud.skills]\n",
    ],
    ids=["string_route", "table_route", "empty_table"],
)
def test_load_routing_config_refuses_a_retired_skill_table(tmp_path: Path, table: str) -> None:
    """c123 (batch design WP2 2.1): a role skill no longer selects a model, so a skill table is refused, not read."""
    root = _root(tmp_path)
    (root / CFG_PATH).write_text(ROUTING_TOML.strip() + "\n\n" + table, encoding="utf-8")

    assert base.RETIRED_SKILL_TABLES == "routing skill tables are retired; registrations name --model"
    with pytest.raises(
        base.CloudHarnessError, match=re.escape(f"routing.testcloud.skills: {base.RETIRED_SKILL_TABLES}")
    ):
        base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH)


def test_load_routing_config_refuses_a_retired_skill_table_in_another_providers_section(tmp_path: Path) -> None:
    """c123 (batch design WP2 2.1): the shared file is refused for a stale table in any section, Goose's included."""
    root = _root(tmp_path)
    table = '[routing.goose.skills]\nbridge-review = "goose-route"\n'
    (root / CFG_PATH).write_text(ROUTING_TOML.strip() + "\n\n" + table, encoding="utf-8")

    with pytest.raises(base.CloudHarnessError, match=re.escape(f"routing.goose.skills: {base.RETIRED_SKILL_TABLES}")):
        base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH)


def test_routing_config_carries_runtime_limits_and_cli_overrides(tmp_path: Path) -> None:
    config = base.load_routing_config(_root(tmp_path), provider_key="testcloud", config_path=CFG_PATH)

    assert (config.timeout_seconds, config.session_timeout_seconds, config.max_turns) == (900, 3600, 600)
    assert base.resolve_runtime_limits(
        config,
        [],
        cli_timeout=1,
        cli_session_timeout=2,
        cli_max_turns=3,
    ) == (900, 3600, 600)
    assert base.resolve_runtime_limits(
        config,
        ["--timeout", "11", "--session-timeout=22", "--max-turns", "33"],
        cli_timeout=11,
        cli_session_timeout=22,
        cli_max_turns=33,
    ) == (11, 22, 33)


# --- Truthful bounded Read pagination (WI-5214 / TEST-11368) ---


def test_read_schema_and_short_file_output_remain_compatible(tmp_path: Path) -> None:
    root = _root(tmp_path)
    content = "short file\n"
    (root / "short.txt").write_text(content, encoding="utf-8")

    read_schema = base.build_tool_schemas(["Read"])[0]["function"]["parameters"]
    assert read_schema["properties"]["offset"] == {"type": "integer", "minimum": 0}
    assert base._dispatch_read({"path": "short.txt"}, root) == content
    assert base._dispatch_read({"path": "short.txt", "offset": len(content)}, root) == ""

    for invalid_offset in (-1, -1.0, "-1", 1.5, True):
        with pytest.raises(base.CloudHarnessError, match="offset must be a nonnegative integer"):
            base._dispatch_read({"path": "short.txt", "offset": invalid_offset}, root)


def test_read_pagination_is_bounded_marked_and_lossless_for_unicode(tmp_path: Path) -> None:
    root = _root(tmp_path)
    content = "segment-\u03b1-\U0001f642\n" * 1200
    (root / "long.txt").write_text(content, encoding="utf-8")

    offset = 0
    chunks: list[str] = []
    marker_count = 0
    while offset < len(content):
        result = base._dispatch_read({"path": "long.txt", "offset": offset}, root)
        assert len(result) <= base.MAX_TOOL_OUTPUT_CHARS
        marker = READ_TRUNCATION_MARKER_RE.search(result)
        if marker is None:
            chunks.append(result)
            break

        marker_count += 1
        chunk = result[: marker.start()]
        start, end, total, next_offset = (int(value) for value in marker.groups())
        assert start == offset
        assert end == offset + len(chunk)
        assert total == len(content)
        assert next_offset == end
        assert chunk
        chunks.append(chunk)
        offset = next_offset

    assert marker_count >= 2
    assert "".join(chunks) == content


def test_read_marker_survives_small_and_oversized_page_requests(tmp_path: Path) -> None:
    root = _root(tmp_path)
    content = "x" * 12_115
    (root / "h-report.txt").write_text(content, encoding="utf-8")

    small = base._dispatch_read({"path": "h-report.txt", "max_chars": 1}, root)
    small_marker = READ_TRUNCATION_MARKER_RE.search(small)
    assert small_marker is not None
    assert small_marker.start() == 1
    assert tuple(int(value) for value in small_marker.groups()) == (0, 1, len(content), 1)

    oversized = base._dispatch_read({"path": "h-report.txt", "max_chars": 1_000_000}, root)
    oversized_marker = READ_TRUNCATION_MARKER_RE.search(oversized)
    assert oversized_marker is not None
    assert len(oversized) <= base.MAX_TOOL_OUTPUT_CHARS
    assert int(oversized_marker.group(2)) == oversized_marker.start()
    assert int(oversized_marker.group(3)) == len(content)

    large_offset = 1_000_000
    large_content = "x" * (large_offset + 12_115)
    large_offset_result = base._bounded_read_result(large_content, large_offset, 1_000_000)
    large_offset_marker = READ_TRUNCATION_MARKER_RE.search(large_offset_result)
    assert large_offset_marker is not None
    assert len(large_offset_result) <= base.MAX_TOOL_OUTPUT_CHARS
    assert int(large_offset_marker.group(1)) == large_offset
    assert int(large_offset_marker.group(2)) == large_offset + large_offset_marker.start()
    assert int(large_offset_marker.group(4)) == int(large_offset_marker.group(2))


# --- Author-metadata injection (base owns it, adopter supplies identity) ---


def test_author_metadata_env_uses_profile_identity() -> None:
    env = base.set_author_metadata_env(
        {}, "testvendor/tc-model", "tc-model", _profile(), native_context_id="test-context"
    )
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


def test_http_error_diagnostic_is_allowlisted_bounded_and_credential_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    read_sizes: list[int] = []

    class BoundedBody(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            read_sizes.append(size)
            return super().read(size)

    body = json.dumps(
        {
            "code": "InvalidToolChoice",
            "message": "named selector rejected; api_key=abcdefghijklmnop" + " x" * 400,  # placeholder
            "request_id": " request-\n 123 ",
            "authorization": "Bearer ignored-authorization-sentinel",  # placeholder
            "prompt": "ignored-prompt-sentinel",
            "details": {"secret": "ignored-nested-sentinel"},
        }
    ).encode("utf-8")

    def fake_urlopen(request, timeout: float):
        raise base.urllib.error.HTTPError(
            "https://alibaba.test/v1/messages",
            400,
            "Bad Request",
            {},
            BoundedBody(body),
        )

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(base.CloudHarnessError) as excinfo:
        base.anthropic_messages_completion(
            "https://alibaba.test/v1",
            "key",
            {"model": "m"},
            label="TestCloud",
        )

    message = str(excinfo.value)
    diagnostic = message.split("; provider_error: ", 1)[1]
    assert 'code="InvalidToolChoice"' in diagnostic
    assert 'request_id="request- 123"' in diagnostic
    assert "[REDACTED:api_key]" in diagnostic
    assert "abcdefghijklmnop" not in diagnostic
    assert "ignored-authorization-sentinel" not in message
    assert "ignored-prompt-sentinel" not in message
    assert "ignored-nested-sentinel" not in message
    assert len(diagnostic) <= base.MAX_HTTP_ERROR_DIAGNOSTIC_CHARS
    assert read_sizes == [base.MAX_HTTP_ERROR_BODY_BYTES]


def test_http_error_diagnostic_accepts_one_nested_error_object(monkeypatch: pytest.MonkeyPatch) -> None:
    body = json.dumps(
        {
            "error": {
                "code": "InvalidParameter",
                "message": "tool_choice is invalid",
                "request_id": "nested-request",
                "details": "ignored-error-detail",
            },
            "request_payload": "ignored-request-payload",
        }
    ).encode("utf-8")

    def fake_urlopen(request, timeout: float):
        raise base.urllib.error.HTTPError("https://alibaba.test/v1/messages", 400, "Bad Request", {}, io.BytesIO(body))

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(base.CloudHarnessError) as excinfo:
        base.anthropic_messages_completion(
            "https://alibaba.test/v1",
            "key",
            {"model": "m"},
            label="TestCloud",
        )

    message = str(excinfo.value)
    assert 'code="InvalidParameter"' in message
    assert 'message="tool_choice is invalid"' in message
    assert 'request_id="nested-request"' in message
    assert "ignored-error-detail" not in message
    assert "ignored-request-payload" not in message


@pytest.mark.parametrize(
    "body",
    [
        b"non-json ignored-prompt-sentinel",
        json.dumps({"error": ["ignored-array-sentinel"], "details": "ignored-details-sentinel"}).encode("utf-8"),
    ],
)
def test_http_error_diagnostic_falls_back_without_raw_body_leakage(
    monkeypatch: pytest.MonkeyPatch,
    body: bytes,
) -> None:
    def fake_urlopen(request, timeout: float):
        raise base.urllib.error.HTTPError("https://alibaba.test/v1/messages", 400, "Bad Request", {}, io.BytesIO(body))

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(base.CloudHarnessError) as excinfo:
        base.anthropic_messages_completion(
            "https://alibaba.test/v1",
            "key",
            {"model": "m"},
            label="TestCloud",
        )

    message = str(excinfo.value)
    assert "provider_error" not in message
    assert "ignored-" not in message


def test_http_error_incomplete_body_preserves_generic_cloud_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class IncompleteBody(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            assert size == base.MAX_HTTP_ERROR_BODY_BYTES
            raise http.client.IncompleteRead(b"ignored-partial-body-sentinel", 10)

    def fake_urlopen(request, timeout: float):
        raise base.urllib.error.HTTPError(
            "https://alibaba.test/v1/messages",
            400,
            "Bad Request",
            {},
            IncompleteBody(),
        )

    monkeypatch.setattr(base.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(base.CloudHarnessError) as excinfo:
        base.anthropic_messages_completion(
            "https://alibaba.test/v1",
            "key",
            {"model": "m"},
            label="TestCloud",
        )

    message = str(excinfo.value)
    assert "TestCloud messages request failed (HTTP 400) after 1 attempt(s)" in message
    assert "provider_error" not in message
    assert "ignored-partial-body-sentinel" not in message


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


def test_run_tool_loop_keeps_read_continuation_marker_model_visible(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "long.txt").write_text("x" * 12_115, encoding="utf-8")
    route = base.resolve_model(base.load_routing_config(root, provider_key="testcloud", config_path=CFG_PATH), None)
    turns: list[dict] = []

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
                                    "id": "read_1",
                                    "function": {"name": "Read", "arguments": {"path": "long.txt"}},
                                }
                            ],
                        }
                    }
                ]
            }
        tool_result = payload["messages"][-1]
        assert tool_result["role"] == "tool"
        assert len(tool_result["content"]) <= base.MAX_TOOL_OUTPUT_CHARS
        assert READ_TRUNCATION_MARKER_RE.search(tool_result["content"]) is not None
        return {"choices": [{"message": {"content": "marker observed"}}]}

    result = base.run_tool_loop(
        "read the report",
        route,
        "https://test.cloud/api/v1",
        "key",
        2,
        root,
        _profile(),
        chat_func=chat,
    )

    assert result == "marker observed"


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
    # c123 (batch design WP2, G38): beside the model's raw path, the hooks get Claude's absolute file_path.
    assert pre_payload["tool_input"] == {"path": "note.txt", "file_path": str((root / "note.txt").resolve())}
    assert post_payload["tool_response"] == "file body"
    assert hook_events[0][2]["GTKB_PROJECT_ROOT"] == str(root)


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


@pytest.mark.parametrize(
    "first_result",
    [
        base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True),
        base.GuardExecutionResult(returncode=1, stdout="", stderr="maintenance failed"),
        base.GuardExecutionResult(returncode=0, stdout="informational non-json output", stderr=""),
        base.GuardExecutionResult(returncode=0, stdout="[]", stderr=""),
    ],
    ids=("timeout", "nonzero", "malformed", "non-object"),
)
def test_native_user_prompt_lifecycle_failures_preserve_prompt_and_run_later_hooks(
    tmp_path: Path,
    first_result: base.GuardExecutionResult,
) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_USER_PROMPT_SUBMIT: [
                {
                    "hooks": [
                        {"type": "command", "command": "failing enrichment"},
                        {"type": "command", "command": "later enrichment"},
                    ]
                }
            ]
        },
    )
    commands: list[str] = []
    provider_payloads: list[dict] = []

    def hook_runner(command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        commands.append(command)
        if command == "failing enrichment":
            return first_result
        return base.GuardExecutionResult(returncode=0, stdout='{"context": "available"}', stderr="")

    def chat(_endpoint: str, _api_key: str, payload: dict, _timeout: float) -> dict:
        provider_payloads.append(payload)
        return {"choices": [{"message": {"content": "review complete"}}]}

    result = base.run_tool_loop(
        "original governed assignment",
        base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",)),
        "https://test.cloud/api/v1",
        "key",
        2,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        native_hook_runner=hook_runner,
    )

    assert result == "review complete"
    assert commands[:2] == ["failing enrichment", "later enrichment"]
    assert {"role": "user", "content": "original governed assignment"} in provider_payloads[0]["messages"]


def test_native_user_prompt_explicit_block_remains_fail_closed(tmp_path: Path) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_USER_PROMPT_SUBMIT: [{"hooks": [{"type": "command", "command": "prompt policy"}]}]},
    )

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(
            returncode=0,
            stdout='{"decision": "block", "reason": "prompt denied"}',
            stderr="",
        )

    with pytest.raises(base.CloudHarnessError, match="native hook blocked UserPromptSubmit.*prompt denied"):
        base.invoke_native_hooks(
            base.NATIVE_HOOK_USER_PROMPT_SUBMIT,
            _meta(),
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            prompt="original governed assignment",
            native_hook_runner=hook_runner,
        )


def test_native_pretool_timeout_returns_bounded_block_and_stops_hook_chain(tmp_path: Path) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_PRE_TOOL_USE: [
                {
                    "matcher": "Read",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python .api-harness/testcloud/hooks/formal-artifact-approval-gate.py --token command-secret",
                            "timeout": 5,
                        },
                        {"type": "command", "command": "later hook.py"},
                    ],
                }
            ]
        },
    )
    commands: list[str] = []

    def hook_runner(command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        commands.append(command)
        return base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True)

    result = base.invoke_native_hooks(
        base.NATIVE_HOOK_PRE_TOOL_USE,
        _meta(),
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        tool_name="Read",
        tool_input={"path": "tool-input-secret.txt"},
        native_hook_runner=hook_runner,
    )

    assert result == {
        "decision": "block",
        "reason": ("timeout event=PreToolUse; tool=Read; hook=formal-artifact-approval-gate.py; timeout_seconds=5"),
    }
    assert commands == ["python .api-harness/testcloud/hooks/formal-artifact-approval-gate.py --token command-secret"]
    assert "tool-input-secret" not in result["reason"]
    assert "command-secret" not in result["reason"]


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
    "hook_result",
    [
        base.GuardExecutionResult(returncode=1, stdout="", stderr="failed"),
        base.GuardExecutionResult(returncode=0, stdout="not json", stderr=""),
        base.GuardExecutionResult(returncode=0, stdout="[1]", stderr=""),
    ],
    ids=("nonzero", "malformed", "not-an-object"),
)
def test_native_pretool_non_timeout_errors_remain_fail_closed(
    tmp_path: Path,
    hook_result: base.GuardExecutionResult,
) -> None:
    """c123 (batch design WP2, G39): a failing PreToolUse hook blocks its call as hook_failed; it no longer ends the
    run. The call stays refused (fail-closed)."""
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_PRE_TOOL_USE: [{"matcher": "Read", "hooks": [{"type": "command", "command": "pre hook"}]}]},
    )

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return hook_result

    block = base.invoke_native_hooks(
        base.NATIVE_HOOK_PRE_TOOL_USE,
        _meta(),
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        tool_name="Read",
        tool_input={"path": "note.txt"},
        native_hook_runner=hook_runner,
    )

    assert block == {
        "decision": "block",
        "reason": f"hook_failed: tool=Read; hook=pre; exit={hook_result.returncode}",
        "hook_failure": True,
    }


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


def test_native_pretool_timeout_blocks_one_turn_then_rechecks_and_recovers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path)
    (root / "note.txt").write_text("file body", encoding="utf-8")
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_PRE_TOOL_USE: [
                {
                    "matcher": "Read",
                    "hooks": [
                        {"type": "command", "command": "slow gate.py", "timeout": 5},
                        {"type": "command", "command": "later gate.py"},
                    ],
                }
            ]
        },
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    hook_commands: list[str] = []
    dispatched_tools: list[str] = []
    turns: list[dict] = []
    original_dispatch = base.dispatch_tool_call

    def hook_runner(command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        hook_commands.append(command)
        if command == "slow gate.py" and hook_commands.count(command) == 1:
            return base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True)
        return base.GuardExecutionResult(returncode=0, stdout="{}", stderr="")

    def recording_dispatch(tool_name, *args, **kwargs):
        dispatched_tools.append(tool_name)
        return original_dispatch(tool_name, *args, **kwargs)

    monkeypatch.setattr(base, "dispatch_tool_call", recording_dispatch)

    def tool_call(call_id: str) -> dict:
        return {
            "id": call_id,
            "function": {"name": "Read", "arguments": {"path": "note.txt"}},
        }

    def chat(_endpoint: str, _api_key: str, payload: dict, _timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            return {"choices": [{"message": {"content": "", "tool_calls": [tool_call("call_1")]}}]}
        if len(turns) == 2:
            assert "timeout event=PreToolUse" in str(payload["messages"])
            assert "file body" not in str(payload["messages"])
            return {"choices": [{"message": {"content": "", "tool_calls": [tool_call("call_2")]}}]}
        assert "file body" in str(payload["messages"])
        return {"choices": [{"message": {"content": "done"}}]}

    result = base.run_tool_loop(
        "read the note",
        route,
        "https://test.cloud/api/v1",
        "key",
        5,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        native_hook_runner=hook_runner,
    )

    assert result == "done"
    assert dispatched_tools == ["Read"]
    assert hook_commands == ["slow gate.py", "slow gate.py", "later gate.py"]


def test_repeated_identical_pretool_timeouts_hit_existing_no_progress_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path)
    _write_native_hook_settings(
        root,
        {
            base.NATIVE_HOOK_PRE_TOOL_USE: [
                {"matcher": "Read", "hooks": [{"type": "command", "command": "slow gate.py", "timeout": 5}]}
            ]
        },
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    hook_calls = 0
    repeated_call = {
        "id": "same_call",
        "function": {"name": "Read", "arguments": {"path": "never-read.txt"}},
    }

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        nonlocal hook_calls
        hook_calls += 1
        return base.GuardExecutionResult(returncode=-1, stdout="", stderr="", timed_out=True)

    def forbidden_dispatch(*_args, **_kwargs):
        raise AssertionError("timed-out PreToolUse must not execute the requested tool")

    monkeypatch.setattr(base, "dispatch_tool_call", forbidden_dispatch)

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        return {"choices": [{"message": {"content": "", "tool_calls": [repeated_call]}}]}

    with pytest.raises(base.CloudHarnessError, match="repeated no-progress tool loop"):
        base.run_tool_loop(
            "read forever",
            route,
            "https://test.cloud/api/v1",
            "key",
            10,
            root,
            _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
            chat_func=chat,
            native_hook_runner=hook_runner,
        )

    assert hook_calls == base.MAX_REPEATED_TOOL_SIGNATURE_TURNS


def test_native_full_hooks_run_tool_loop_still_enforces_guard_floor(tmp_path: Path) -> None:
    root = _root(tmp_path)
    hooks = root / ".harness-baseline-configuration/hooks"
    hooks.mkdir(parents=True)
    (hooks / "credential-scan.py").write_text("print('{}')\n", encoding="utf-8")
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


# ---- c123 (batch design WP2, items 7 to 11) ---------------------------------------------------------------------


def _pretool(root: Path, hook_result: base.GuardExecutionResult, **kwargs) -> dict | None:
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_PRE_TOOL_USE: [{"matcher": "Read", "hooks": [{"type": "command", "command": "pre hook"}]}]},
    )
    return base.invoke_native_hooks(
        base.NATIVE_HOOK_PRE_TOOL_USE,
        _meta(),
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        tool_name="Read",
        tool_input={"path": "note.txt"},
        native_hook_runner=lambda *_args: hook_result,
        **kwargs,
    )


@pytest.mark.parametrize(
    ("hook_result", "reason"),
    [
        (
            base.GuardExecutionResult(2, json.dumps({"decision": "block", "reason": "provenance missing"}), ""),
            "provenance missing",
        ),
        (base.GuardExecutionResult(2, "", "stderr reason\n"), "stderr reason"),
        (base.GuardExecutionResult(2, "", ""), "hook=pre exited 2"),
    ],
    ids=("json-reason", "stderr-reason", "bare"),
)
def test_a_pretool_exit_two_blocks_the_call_with_its_reason(
    tmp_path: Path, hook_result: base.GuardExecutionResult, reason: str
) -> None:
    assert _pretool(_root(tmp_path), hook_result) == {"decision": "block", "reason": reason}


def test_a_blocked_write_does_not_end_the_run(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "note.txt").write_text("file body", encoding="utf-8")
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_PRE_TOOL_USE: [{"matcher": "Write", "hooks": [{"type": "command", "command": "gate.py"}]}]},
    )
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read", "Write"))
    turns: list[dict] = []

    def hook_runner(_command: str, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(2, json.dumps({"decision": "block", "reason": "missing provenance"}), "")

    def chat(_endpoint: str, _api_key: str, payload: dict, _timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            call = {"id": "c1", "function": {"name": "Write", "arguments": {"path": "x.md", "content": "y"}}}
            return {"choices": [{"message": {"content": "", "tool_calls": [call]}}]}
        if len(turns) == 2:
            assert "missing provenance" in str(payload["messages"])
            call = {"id": "c2", "function": {"name": "Read", "arguments": {"path": "note.txt"}}}
            return {"choices": [{"message": {"content": "", "tool_calls": [call]}}]}
        return {"choices": [{"message": {"content": "done"}}]}

    result = base.run_tool_loop(
        "write then read",
        route,
        "https://test.cloud/api/v1",
        "key",
        5,
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        chat_func=chat,
        native_hook_runner=hook_runner,
    )

    assert result == "done"
    assert not (root / "x.md").exists()


@pytest.mark.parametrize(
    ("tool", "arguments", "canonical"),
    [
        ("Write", {"path": "docs/new.md", "content": "text"}, {"file_path": "docs/new.md", "content": "text"}),
        (
            "Edit",
            {"path": "note.txt", "old_string": "file", "new_string": "note"},
            {"file_path": "note.txt", "old_string": "file", "new_string": "note"},
        ),
        ("Read", {"path": "note.txt"}, {"file_path": "note.txt"}),
    ],
)
def test_the_native_hooks_get_an_api_file_tool_call_in_claude_shape(
    tmp_path: Path, tool: str, arguments: dict, canonical: dict
) -> None:
    """c123 (batch design WP2, G38): the raw keys stay and Claude's keys are added, the path made absolute, so the
    content hooks that read only file_path judge an API harness's writes (test_hook_payload_conformance.py)."""
    root = _root(tmp_path)
    (root / "note.txt").write_text("file body", encoding="utf-8")
    _write_native_hook_settings(
        root,
        {base.NATIVE_HOOK_PRE_TOOL_USE: [{"matcher": tool, "hooks": [{"type": "command", "command": "pre hook"}]}]},
    )
    seen: list[dict] = []

    def runner(_command: str, payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        seen.append(dict(payload))
        return base.GuardExecutionResult(0, "{}", "")

    base.invoke_native_hooks(
        base.NATIVE_HOOK_PRE_TOOL_USE,
        _meta(),
        root,
        _profile(hook_tier=base.HOOK_TIER_NATIVE_FULL),
        tool_name=tool,
        tool_input=arguments,
        native_hook_runner=runner,
    )

    assert len(seen) == 1
    assert seen[0]["tool_input"] == {
        **arguments,
        **canonical,
        "file_path": str((root / canonical["file_path"]).resolve()),
    }


def test_the_guard_log_records_each_layer_and_never_the_input(tmp_path: Path) -> None:
    root = _root(tmp_path)
    log_path = tmp_path / "log" / "guard-decisions.jsonl"
    log = base.GuardDecisionLog(log_path, "native-1")
    _pretool(root, base.GuardExecutionResult(0, "{}", ""), decision_log=log.record)
    _pretool(root, base.GuardExecutionResult(2, "", "refused"), decision_log=log.record)
    guard = root / "guard.py"
    guard.write_text("", encoding="utf-8")

    def deny(_path: Path, _payload: dict, _env: dict, _timeout: float) -> base.GuardExecutionResult:
        return base.GuardExecutionResult(0, json.dumps({"decision": "deny", "reason": "credential_like: no"}), "")

    with pytest.raises(base.CloudHarnessError, match="guard denied Write"):
        base.invoke_guard_adapter(
            "Write",
            {"path": "note.txt", "content": "SECRET-CONTENT-NEVER-LOGGED"},
            _meta(),
            root,
            _profile(),
            guard_runner=deny,
            guard_paths=[guard],
            decision_log=log.record,
        )
    with pytest.raises(base.CloudHarnessError):
        base._dispatch_bash(
            {"command": "echo x > bridge/item-001.md"},
            _meta(),
            root,
            _profile(),
            None,
            None,
            decision_log=log.record,
        )

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert [record["layer"] for record in records] == ["native_hook", "native_hook", "guard_adapter", "bridge_shell"]
    assert [record["allowed"] for record in records] == [True, False, False, False]
    assert records[2]["reason_code"] == "credential_like"
    assert all(record["native_context_id"] == "native-1" for record in records)
    assert "SECRET-CONTENT-NEVER-LOGGED" not in log_path.read_text(encoding="utf-8")
    assert log.counts == {"allowed": 1, "blocked": 3}


def test_an_unwritable_guard_log_warns_once_and_never_fails(tmp_path: Path, capsys) -> None:
    log = base.GuardDecisionLog(tmp_path, "native-1")  # a directory: every append fails

    log.record({"allowed": True})
    log.record({"allowed": False})

    assert capsys.readouterr().err.count("guard decision log not written") == 1
    assert log.counts == {"allowed": 1, "blocked": 1}


def test_the_guard_log_path_prefers_the_option_then_the_environment() -> None:
    assert base.guard_log_path("a.jsonl", {"GTKB_GUARD_LOG": "b.jsonl"}) == Path("a.jsonl")
    assert base.guard_log_path(None, {"GTKB_GUARD_LOG": "b.jsonl"}) == Path("b.jsonl")
    assert base.guard_log_path(None, {}) is None


def test_the_run_report_counts_turns_tools_and_usage_and_holds_no_content(tmp_path: Path) -> None:
    guard_log = base.GuardDecisionLog(None, "native-1")
    report = base.RunReport(
        harness="testcloud",
        native_context_id="native-1",
        route_key="tc",
        requested_model="testvendor/tc-model",
        endpoint="https://test.cloud/api/v1?key=never",
        guard_log=guard_log,
    )
    guard_log.record({"allowed": False})
    report.set_model("testvendor/tc-model-2")
    report.record_turn(1, ["Read", "Bash"], provider_response={"usage": {"prompt_tokens": 10, "nested": {"x": 1}}})
    report.record_turn(2, ["Read"], provider_response={"usage": {"prompt_tokens": 5}, "message": "PROMPT-TEXT"})
    report.finish("final_response")
    path = tmp_path / "report.json"
    report.write(path, exit_code=0)

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["turns"] == 2
    assert written["tool_calls"] == {"Read": 2, "Bash": 1}
    assert written["token_usage"] == {"prompt_tokens": 15}
    assert written["endpoint"] == "test.cloud"
    assert written["guard_decisions"] == {"allowed": 0, "blocked": 1}
    assert (written["stop_reason"], written["exit_code"]) == ("final_response", 0)
    assert "PROMPT-TEXT" not in path.read_text(encoding="utf-8")


def test_an_interrupt_is_classified_and_propagates(tmp_path: Path) -> None:
    root = _root(tmp_path)
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    report = base.RunReport(harness="t", native_context_id="n", route_key="tc", requested_model=None, endpoint=None)

    def chat(*_args) -> dict:
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        base.run_tool_loop(
            "x", route, "https://test.cloud/api/v1", "key", 3, root, _profile(), chat_func=chat, telemetry=report
        )

    assert report.data["stop_reason"] == "interrupted"


def test_the_launcher_names_the_native_context_id(tmp_path: Path) -> None:
    root = _root(tmp_path)
    route = base.ModelRoute("tc", "testvendor/tc-model", "tc-model", True, ("Read",))
    seen: list[str] = []

    def chat(_endpoint: str, _api_key: str, payload: dict, _timeout: float) -> dict:
        seen.append(payload["messages"][0]["content"])
        return {"choices": [{"message": {"content": "done"}}]}

    base.run_tool_loop(
        "x",
        route,
        "https://test.cloud/api/v1",
        "key",
        3,
        root,
        _profile(),
        chat_func=chat,
        native_context_id="named-context-id",
    )

    assert "Native context identifier: named-context-id." in seen[0]


def test_bind_for_run_binds_only_with_an_init_line_and_records_the_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """c123 (batch design WP2 2.1): without --init the run stays unbound; with it the bind's facts reach the report."""
    binding = {"session_context_id": "session-1", "role": "loyal-opposition", "native_context_id": "native-1"}
    calls: list[tuple[str, str, Path]] = []

    def bind(native_context_id: str, init_line: str, project_root: Path, runner=None) -> dict:
        calls.append((native_context_id, init_line, project_root))
        return binding

    monkeypatch.setattr(base, "bind_native_context", bind)
    report = base.RunReport(
        harness="t", native_context_id="native-1", route_key="tc", requested_model=None, endpoint=None
    )

    assert base.bind_for_run(None, "native-1", tmp_path, report) is None
    assert calls == [] and (report.data["session_context_id"], report.data["role"]) == (None, None)
    bound = base.bind_for_run("::init gtkb lo", "native-1", tmp_path, report)
    assert bound == binding and bound is not binding
    assert calls == [("native-1", "::init gtkb lo", tmp_path)]
    assert (report.data["session_context_id"], report.data["role"]) == ("session-1", "loyal-opposition")


def test_the_bash_tool_names_the_shell_that_runs_it() -> None:
    assert "cmd.exe /c" in base.bash_tool_description("nt")
    assert "/bin/sh -c" in base.bash_tool_description("posix")
    schema = base.build_tool_schemas(["Bash"])[0]
    assert base.bash_tool_description() in json.dumps(schema)


def test_the_shell_command_line_keeps_the_command_whole() -> None:
    windows = base.shell_command_line('echo "a b" && dir', "nt")
    assert isinstance(windows, str)
    assert windows.endswith(' /d /s /c "echo "a b" && dir"')
    assert base.shell_command_line("echo x", "posix") == ["/bin/sh", "-c", "echo x"]


def test_undecodable_command_output_is_replaced_not_lost(tmp_path: Path) -> None:
    command = f'"{sys.executable}" -c "import sys; sys.stdout.buffer.write(bytes([111, 107, 255]))"'

    completed = base._default_command_runner(command, tmp_path, dict(os.environ), 60)

    assert completed.returncode == 0
    assert completed.stdout == "ok�"


@pytest.mark.skipif(os.name != "nt", reason="the process-tree end is the Windows path (taskkill /T)")
def test_a_timed_out_command_ends_its_whole_process_tree(tmp_path: Path) -> None:
    script = tmp_path / "parent.py"
    script.write_text(
        "import subprocess, sys, time\n"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
        "print(child.pid, flush=True)\n"
        "time.sleep(120)\n",
        encoding="utf-8",
    )

    with pytest.raises(subprocess.TimeoutExpired) as expired:
        base._default_command_runner(f'"{sys.executable}" "{script}"', tmp_path, dict(os.environ), 5)

    grandchild = int(str(expired.value.output).split()[0])
    listing = subprocess.run(
        ["tasklist", "/FI", f"PID eq {grandchild}", "/NH"], capture_output=True, text=True, check=False
    ).stdout
    assert str(grandchild) not in listing


def test_grep_and_glob_skip_other_contexts_scratch_and_checkouts(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / ".git").mkdir()
    for relative in ("src/a.txt", "scratchpad/SENV-a/b.txt", ".worktrees/SENV-b/c.txt", ".venv/d.txt"):
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text("needle\n", encoding="utf-8")

    assert base._dispatch_grep({"pattern": "needle", "path": "."}, root) == "src/a.txt:1:needle"
    assert base._dispatch_glob({"pattern": "*.txt", "path": "."}, root) == "src/a.txt"
    assert base._dispatch_grep({"pattern": "needle", "path": "scratchpad/SENV-a"}, root) == (
        "scratchpad/SENV-a/b.txt:1:needle"
    )
