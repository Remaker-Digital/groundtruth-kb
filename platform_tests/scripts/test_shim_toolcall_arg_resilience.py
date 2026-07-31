# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5471: a malformed tool-call from the model must not abort the worker.

Both dispatch worker shims (``cloud_harness_base.py``'s shared ``run_tool_loop``
and ``ollama_harness.py``'s independent implementation) previously called
``_tool_call_parts`` outside any recoverable try/except, so a smaller/faster
model emitting one malformed tool call (invalid-JSON arguments, missing
function name, etc.) aborted the whole worker with no retry. The fix routes
the parse failure through the same recoverable "ERROR: ..." tool-result
pattern already used for ``dispatch_tool_call`` failures, so the model sees
the error and can retry, bounded by the existing repeated-signature backstop.
"""

from __future__ import annotations

from pathlib import Path

from scripts import cloud_harness_base as cloud_base
from scripts import ollama_harness as ollama


def _cloud_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / ".api-harness" / "routing.toml").write_text(
        "schema_version = 1\n"
        "[models.tc-default]\n"
        'model_id = "testvendor/tc-model"\n'
        'provider = "testcloud"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "[routing.testcloud]\n"
        'default_model = "tc-default"\n'
        "timeout_seconds = 900\n"
        "session_timeout_seconds = 3600\n"
        "max_turns = 600\n"
        "[routing.testcloud.skills]\n"
        'bridge-review = "tc-default"\n',
        encoding="utf-8",
    )
    return root


def _cloud_profile() -> cloud_base.AdopterProfile:
    return cloud_base.AdopterProfile(
        display_name="TestCloud",
        author_identity="TestCloud H",
        author_harness_id="H",
        default_endpoint="https://test.cloud/api/v1",
        auth_env_key="TESTCLOUD_API_KEY",
        provider_routing_key="testcloud",
        routing_config_path=Path(".api-harness") / "routing.toml",
        dialect=cloud_base.DIALECT_OPENAI_CHAT,
        hook_tier=cloud_base.HOOK_TIER_GUARD_ADAPTER_FLOOR,
        publish_bridge_verdict_tool=True,
        extra_headers={},
    )


def test_cloud_harness_malformed_json_arguments_is_recoverable(tmp_path: Path) -> None:
    root = _cloud_root(tmp_path)
    route = cloud_base.resolve_model(
        cloud_base.load_routing_config(
            root, provider_key="testcloud", config_path=Path(".api-harness") / "routing.toml"
        ),
        None,
    )
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
                                {"id": "bad_1", "function": {"name": "Read", "arguments": "{not valid json"}}
                            ],
                        }
                    }
                ]
            }
        tool_result = payload["messages"][-1]
        assert tool_result["role"] == "tool"
        assert tool_result["tool_call_id"] == "bad_1"
        assert tool_result["content"].startswith("ERROR:")
        return {"choices": [{"message": {"content": "recovered"}}]}

    result = cloud_base.run_tool_loop(
        "hello", route, "https://test.cloud/api/v1", "key", 3, root, _cloud_profile(), chat_func=chat
    )
    assert result == "recovered"
    assert len(turns) == 2


def test_cloud_harness_missing_function_name_is_recoverable(tmp_path: Path) -> None:
    root = _cloud_root(tmp_path)
    route = cloud_base.resolve_model(
        cloud_base.load_routing_config(
            root, provider_key="testcloud", config_path=Path(".api-harness") / "routing.toml"
        ),
        None,
    )
    turns: list[dict] = []

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        turns.append(payload)
        if len(turns) == 1:
            return {
                "choices": [
                    {"message": {"content": "", "tool_calls": [{"id": "bad_2", "function": {"arguments": "{}"}}]}}
                ]
            }
        tool_result = payload["messages"][-1]
        assert tool_result["role"] == "tool"
        assert tool_result["tool_call_id"] == "bad_2"
        assert tool_result["content"].startswith("ERROR:")
        return {"choices": [{"message": {"content": "recovered"}}]}

    result = cloud_base.run_tool_loop(
        "hello", route, "https://test.cloud/api/v1", "key", 3, root, _cloud_profile(), chat_func=chat
    )
    assert result == "recovered"


def _ollama_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / ".api-harness" / "routing.toml").write_text(
        "schema_version = 1\n"
        "[models.fixture-model]\n"
        'model_id = "fixture:latest"\n'
        'provider = "ollama"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "[routing.ollama]\n"
        'default_model = "fixture-model"\n'
        "timeout_seconds = 900\n"
        "session_timeout_seconds = 3600\n"
        "max_turns = 600\n"
        "[routing.ollama.skills]\n"
        'bridge-review = "fixture-model"\n',
        encoding="utf-8",
    )
    return root


def _ollama_route(root: Path) -> ollama.ModelRoute:
    config = ollama.load_routing_config(root)
    return ollama.resolve_model(config, None, skill="bridge-review")


def test_ollama_harness_malformed_json_arguments_is_recoverable(tmp_path: Path) -> None:
    root = _ollama_root(tmp_path)
    calls: list[dict] = []

    def chat(url: str, payload: dict, timeout: float) -> dict:
        calls.append(payload)
        if len(calls) == 1:
            return {
                "message": {
                    "content": "",
                    "tool_calls": [{"id": "bad_1", "function": {"name": "Read", "arguments": "{not valid json"}}],
                }
            }
        tool_result = payload["messages"][-1]
        assert tool_result["role"] == "tool"
        assert tool_result["tool_call_id"] == "bad_1"
        assert tool_result["content"].startswith("ERROR:")
        return {"message": {"content": "recovered"}}

    result = ollama.run_tool_loop("hello", _ollama_route(root), "http://ollama.test", 3, root, chat_func=chat)
    assert result == "recovered"
    assert len(calls) == 2


def test_ollama_harness_missing_function_name_is_recoverable(tmp_path: Path) -> None:
    root = _ollama_root(tmp_path)
    calls: list[dict] = []

    def chat(url: str, payload: dict, timeout: float) -> dict:
        calls.append(payload)
        if len(calls) == 1:
            return {"message": {"content": "", "tool_calls": [{"id": "bad_2", "function": {"arguments": "{}"}}]}}
        tool_result = payload["messages"][-1]
        assert tool_result["role"] == "tool"
        assert tool_result["tool_call_id"] == "bad_2"
        assert tool_result["content"].startswith("ERROR:")
        return {"message": {"content": "recovered"}}

    result = ollama.run_tool_loop("hello", _ollama_route(root), "http://ollama.test", 3, root, chat_func=chat)
    assert result == "recovered"
