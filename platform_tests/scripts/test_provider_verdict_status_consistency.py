from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import cloud_harness_base as cloud
from scripts import gtkb_bridge_writer as writer
from scripts import ollama_harness as ollama

STATUS_MISMATCH_CODE = writer.PROVIDER_VERDICT_STATUS_MISMATCH_CODE


class _Published:
    def to_dict(self) -> dict[str, str]:
        return {"verdict_path": "bridge/example-002.md"}


def _writer_metadata() -> dict[str, str]:
    return {
        "author_identity": "Fixture LO",
        "author_harness_id": "F",
        "author_session_context_id": "dispatch-F-status",
        "author_model": "fixture-model",
        "author_model_version": "fixture-version",
        "author_model_configuration": "fixture configuration",
    }


def _prepare_writer_root(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bridge = root / "bridge"
    bridge.mkdir()
    (bridge / "example-001.md").write_text(
        "NEW\n\nbridge_kind: prime_proposal\nDocument: example\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        writer,
        "_resolve_lo_worker",
        lambda *_args, **_kwargs: {"role": "loyal-opposition", "harness_id": "F"},
    )
    monkeypatch.setattr(
        writer,
        "_claim_holder",
        lambda *_args, **_kwargs: {"session_id": "dispatch-F-status"},
    )


def _writer_content(first_status: str) -> str:
    return (
        f"{first_status}\n\n"
        "bridge_kind: lo_verdict\n"
        "Document: example\n"
        "Version: 002\n"
        "Responds to: bridge/example-001.md\n"
    )


@pytest.mark.parametrize(
    ("first_status", "reported_status"),
    [
        ("NO-GO", "NO-GO"),
        ("secret-value-that-must-not-escape", "<invalid>"),
    ],
)
def test_writer_rejects_mismatch_with_stable_sanitized_diagnostic_before_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    first_status: str,
    reported_status: str,
) -> None:
    _prepare_writer_root(tmp_path, monkeypatch)

    with pytest.raises(writer.BridgePublicationError) as exc_info:
        writer.publish_lo_verdict(
            "example",
            "GO",
            _writer_content(first_status),
            tmp_path,
            session_id="dispatch-F-status",
            harness_name="openrouter",
            author_metadata=_writer_metadata(),
        )

    diagnostic = str(exc_info.value)
    assert diagnostic.startswith(f"{STATUS_MISMATCH_CODE}: no publication occurred")
    assert "verdict_argument=GO" in diagnostic
    assert f"content_first_status={reported_status}" in diagnostic
    if reported_status == "<invalid>":
        assert first_status not in diagnostic
    assert not (tmp_path / "bridge" / "example-002.md").exists()


def _cloud_route() -> cloud.ModelRoute:
    return cloud.ModelRoute(
        key="fixture",
        model_id="fixture/model",
        model_version="fixture-version",
        tool_calling_supported=True,
        allowed_tools=("Read",),
    )


def _cloud_profile() -> cloud.AdopterProfile:
    return cloud.AdopterProfile(
        display_name="Fixture Cloud",
        author_identity="Fixture LO",
        author_harness_id="F",
        default_endpoint="https://fixture.invalid/v1",
        auth_env_key="FIXTURE_API_KEY",
        provider_routing_key="fixture",
        routing_config_path=Path(".api-harness/routing.toml"),
        publish_bridge_verdict_tool=True,
    )


def _cloud_response(call_number: int, *, matching: bool) -> dict:
    content_status = "GO" if matching else "NO-GO"
    return {
        "choices": [
            {
                "message": {
                    "content": "",
                    "tool_calls": [
                        {
                            "id": f"publish_{call_number}",
                            "function": {
                                "name": cloud.PUBLISH_BRIDGE_VERDICT_TOOL,
                                "arguments": {
                                    "slug": "example",
                                    "verdict": "GO",
                                    "content": f"{content_status}\n\nResponds to: bridge/example-001.md\n",
                                },
                            },
                        }
                    ],
                }
            }
        ]
    }


def test_cloud_status_mismatch_gets_one_publisher_only_correction_turn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payloads: list[dict] = []
    publish_calls = 0

    def publish(*_args, **_kwargs):
        nonlocal publish_calls
        publish_calls += 1
        if publish_calls == 1:
            raise RuntimeError(
                f"{STATUS_MISMATCH_CODE}: no publication occurred; verdict_argument=GO; content_first_status=NO-GO"
            )
        return _Published()

    monkeypatch.setattr(cloud, "_load_provider_verdict_publisher", lambda _root: publish)
    monkeypatch.setattr(cloud, "_ensure_provider_verdict_claim", lambda *_args, **_kwargs: None)
    for key in cloud.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-F-status")

    def chat(_endpoint: str, _api_key: str, payload: dict, _timeout: float) -> dict:
        payloads.append(json.loads(json.dumps(payload)))
        if len(payloads) == 1:
            return _cloud_response(1, matching=False)
        if len(payloads) == 2:
            assert [tool["function"]["name"] for tool in payload["tools"]] == [cloud.PUBLISH_BRIDGE_VERDICT_TOOL]
            assert STATUS_MISMATCH_CODE in payload["messages"][-1]["content"]
            return _cloud_response(2, matching=True)
        return {"choices": [{"message": {"content": "published"}}]}

    result = cloud.run_tool_loop(
        "review",
        _cloud_route(),
        "https://fixture.invalid/v1",
        "key",
        4,
        tmp_path,
        _cloud_profile(),
        skill="bridge-review",
        chat_func=chat,
    )

    assert result == "published"
    assert publish_calls == 2
    assert len(payloads) == 3


def test_cloud_second_status_mismatch_stops_without_generic_retry_exhaustion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publish_calls = 0

    def publish(*_args, **_kwargs):
        nonlocal publish_calls
        publish_calls += 1
        raise RuntimeError(
            f"{STATUS_MISMATCH_CODE}: no publication occurred; verdict_argument=GO; content_first_status=NO-GO"
        )

    monkeypatch.setattr(cloud, "_load_provider_verdict_publisher", lambda _root: publish)
    monkeypatch.setattr(cloud, "_ensure_provider_verdict_claim", lambda *_args, **_kwargs: None)
    for key in cloud.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-F-status")

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        return _cloud_response(publish_calls + 1, matching=False)

    with pytest.raises(cloud.CloudHarnessError) as exc_info:
        cloud.run_tool_loop(
            "review",
            _cloud_route(),
            "https://fixture.invalid/v1",
            "key",
            8,
            tmp_path,
            _cloud_profile(),
            skill="bridge-review",
            chat_func=chat,
        )

    assert publish_calls == 2
    assert STATUS_MISMATCH_CODE in str(exc_info.value)
    assert "stopped after 2 mismatches" in str(exc_info.value)
    assert "publisher recovery exhausted" not in str(exc_info.value)


def _ollama_route() -> ollama.ModelRoute:
    return ollama.ModelRoute(
        key="fixture",
        model_id="fixture-model",
        model_version="fixture-version",
        tool_calling_supported=True,
        allowed_tools=("Read",),
    )


def _ollama_response(call_number: int, *, matching: bool) -> dict:
    content_status = "GO" if matching else "NO-GO"
    return {
        "message": {
            "content": "",
            "tool_calls": [
                {
                    "id": f"publish_{call_number}",
                    "function": {
                        "name": ollama.PUBLISH_BRIDGE_VERDICT_TOOL,
                        "arguments": {
                            "slug": "example",
                            "verdict": "GO",
                            "content": f"{content_status}\n\nResponds to: bridge/example-001.md\n",
                        },
                    },
                }
            ],
        }
    }


def test_ollama_status_mismatch_gets_one_publisher_only_correction_turn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payloads: list[dict] = []
    publish_calls = 0

    def publish(*_args, **_kwargs):
        nonlocal publish_calls
        publish_calls += 1
        if publish_calls == 1:
            raise RuntimeError(
                f"{STATUS_MISMATCH_CODE}: no publication occurred; verdict_argument=GO; content_first_status=NO-GO"
            )
        return _Published()

    monkeypatch.setattr(ollama, "_load_provider_verdict_publisher", lambda _root: publish)
    for key in ollama.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-D-status")

    def chat(_endpoint: str, payload: dict, _timeout: float) -> dict:
        payloads.append(json.loads(json.dumps(payload)))
        if len(payloads) == 1:
            return _ollama_response(1, matching=False)
        if len(payloads) == 2:
            assert [tool["function"]["name"] for tool in payload["tools"]] == [ollama.PUBLISH_BRIDGE_VERDICT_TOOL]
            assert STATUS_MISMATCH_CODE in payload["messages"][-1]["content"]
            return _ollama_response(2, matching=True)
        return {"message": {"content": "published"}}

    result = ollama.run_tool_loop(
        "review",
        _ollama_route(),
        ollama.DEFAULT_ENDPOINT,
        4,
        tmp_path,
        skill="bridge-review",
        chat_func=chat,
    )

    assert result == "published"
    assert publish_calls == 2
    assert len(payloads) == 3


def test_ollama_second_status_mismatch_stops_without_generic_retry_exhaustion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publish_calls = 0

    def publish(*_args, **_kwargs):
        nonlocal publish_calls
        publish_calls += 1
        raise RuntimeError(
            f"{STATUS_MISMATCH_CODE}: no publication occurred; verdict_argument=GO; content_first_status=NO-GO"
        )

    monkeypatch.setattr(ollama, "_load_provider_verdict_publisher", lambda _root: publish)
    for key in ollama.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-D-status")

    def chat(_endpoint: str, _payload: dict, _timeout: float) -> dict:
        return _ollama_response(publish_calls + 1, matching=False)

    with pytest.raises(ollama.OllamaHarnessError) as exc_info:
        ollama.run_tool_loop(
            "review",
            _ollama_route(),
            ollama.DEFAULT_ENDPOINT,
            8,
            tmp_path,
            skill="bridge-review",
            chat_func=chat,
        )

    assert publish_calls == 2
    assert STATUS_MISMATCH_CODE in str(exc_info.value)
    assert "stopped after 2 mismatches" in str(exc_info.value)
    assert "publisher recovery exhausted" not in str(exc_info.value)
