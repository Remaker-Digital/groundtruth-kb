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


@pytest.mark.parametrize("dialect", [base.DIALECT_OLLAMA_NATIVE, base.DIALECT_ANTHROPIC_MESSAGES])
def test_slice3_dialects_raise_not_implemented_sentinel(dialect: str) -> None:
    with pytest.raises(NotImplementedError, match="slice-3"):
        base.resolve_dialect_chat_func(_profile(dialect=dialect))


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
