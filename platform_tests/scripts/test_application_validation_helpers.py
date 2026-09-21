"""Exercise application validation commands with offline HTTP responses."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from collections import deque
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def load_helper(monkeypatch):
    monkeypatch.setattr(sys, "path", sys.path.copy())
    env = ModuleType("scripts._env")
    env.load_env_local = Mock()
    monkeypatch.setitem(sys.modules, "scripts._env", env)

    def load(name):
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        env.load_env_local.assert_not_called()
        return module

    return load


def test_admin_headers_and_unavailable_service_are_not_false_passes(load_helper):
    mod = load_helper("test_admin_ui_validation")
    mod.BASE_URL, mod.API_KEY = "https://fixture.invalid", "fixture-key"
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(503, text="Unavailable")

    async def exercise():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            unauthenticated = await mod.api_call(client, "GET", "/health", headers={})
            authenticated = await mod.api_call(client, "GET", "/protected")
        assert not unauthenticated.passed and not authenticated.passed
        assert "X-API-Key" not in requests[0].headers
        assert requests[1].headers["X-API-Key"] == "fixture-key"
        assert str(requests[0].url) == "https://fixture.invalid/health"

    asyncio.run(exercise())


def test_missing_conversation_id_fails_dependent_admin_checks(load_helper):
    mod = load_helper("test_admin_ui_validation")
    mod.BASE_URL = "https://fixture.invalid"

    async def exercise():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
        ) as client:
            rows = await mod.test_chat_api_with_widget_key(client)
        dependent = [row for row in rows if "(state)" in row.name or row.name.endswith("/end")]
        assert len(dependent) == 2
        assert all(not row.passed and "not executed" in row.failure_reason for row in dependent)

    asyncio.run(exercise())


@pytest.mark.parametrize(
    "url", ["", "https://fixture.invalid?bad=1", "https://fixture.invalid#bad", "https://user:pass@fixture.invalid"]
)
@pytest.mark.parametrize(
    "name,url_key", [("test_admin_ui_validation", "AGENT_RED_BASE_URL"), ("test_chat_battery", "PROD_URL")]
)
def test_invalid_target_fails_before_http(load_helper, monkeypatch, name, url_key, url):
    mod = load_helper(name)
    monkeypatch.setenv(url_key, url)
    monkeypatch.setenv("SUPERADMIN_PREVIEW_API_KEY", "fixture-key")
    monkeypatch.setenv("PREVIEW_WIDGET_KEY", "fixture-widget")
    if name == "test_admin_ui_validation":
        monkeypatch.setattr(mod.httpx, "AsyncClient", Mock(side_effect=AssertionError("HTTP must not start")))
        assert asyncio.run(mod.main()) == 1
    else:
        monkeypatch.setattr(mod, "chat", Mock(side_effect=AssertionError("HTTP must not start")))
        assert asyncio.run(mod.main()) is False
    mod.load_env_local.assert_called_once_with(env_file=mod.APP_ROOT / ".env.local")


def event(name, **data):
    return f"event: {name}\ndata: {json.dumps(data)}\n\n".encode()


class Response:
    def __init__(self, payload=None, chunks=(), error=None):
        self.payload, self.chunks, self.error = payload, chunks, error
        self.content = self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    def raise_for_status(self):
        if self.error:
            raise self.error

    async def json(self):
        return self.payload

    async def iter_any(self):
        for chunk in self.chunks:
            if isinstance(chunk, Exception):
                raise chunk
            yield chunk


@pytest.fixture
def chat_call(load_helper, monkeypatch):
    mod = load_helper("test_chat_battery")
    mod.API, mod.WIDGET_KEY = "https://fixture.invalid", "fixture-widget"

    async def no_delay(_):
        pass

    monkeypatch.setattr(mod.asyncio, "sleep", no_delay)

    def call(chunks, *, messages=None, turn=2, state_conversation="conv", accepted=None, http_error=None):
        acknowledgement = (
            accepted
            if accepted is not None
            else {"accepted": True, "conversation_id": "conv", "message_id": "customer-now", "turn_count": 1}
        )
        state = {
            "conversation_id": state_conversation,
            "turn_count": turn,
            "messages": messages
            if messages is not None
            else [
                {"role": "customer", "message_id": "customer-now", "content": "scrubbed question"},
                {"role": "ai", "message_id": "ai-now", "content": "Persisted answer"},
            ],
        }
        queue = deque(
            [
                ("/api/chat/message", Response(acknowledgement)),
                ("/api/chat/stream/conv", Response(chunks=chunks, error=http_error)),
                ("/api/chat/conversations/conv", Response(state)),
            ]
        )

        class Session(Response):
            def request(self, url, **kwargs):
                expected, response = queue.popleft()
                assert url == mod.API + expected
                assert kwargs["headers"]["X-Widget-Key"] == "fixture-widget"
                return response

            post = get = request

        monkeypatch.setitem(
            sys.modules, "aiohttp", SimpleNamespace(ClientSession=Session, ClientTimeout=lambda **kwargs: kwargs)
        )
        return asyncio.run(mod.chat("current question", "conv"))

    return call


def test_native_done_and_previous_buffer_resolve_exact_persisted_reply(chat_call):
    previous = event("token", text="old answer", sequence=1) + event("done", conversation_id="conv", turn_count=1)
    current = (
        event("token", text="provisional", sequence=2)
        + event("validated", conversation_id="conv", message_id="ai-now")
        + event("done", conversation_id="conv", turn_count=2)
    )
    data = previous + current
    answer, conversation, _ = chat_call([data[:23], data[23:69], data[69:]])
    assert (answer, conversation) == ("Persisted answer", "conv")


def test_retracted_body_and_confirmed_escalation_appendix(chat_call):
    data = event("token", text="rejected provisional", sequence=1)
    data += event("retracted", fallback_text="Persisted answer", reason="rejected")
    data += event("token", text="; escalation appendix", sequence=2)
    data += event("validated", conversation_id="conv", message_id="escalation")
    data += event("done", conversation_id="conv", turn_count=2)
    assert chat_call([data])[0] == "Persisted answer; escalation appendix"


def test_completed_empty_stream_requires_current_persisted_message(chat_call):
    assert chat_call([])[0] == "Persisted answer"
    old_messages = [{"role": "customer", "message_id": "old-customer"}, {"role": "ai", "content": "Old answer"}]
    with pytest.raises(RuntimeError, match="No persisted AI reply"):
        chat_call([], messages=old_messages)


@pytest.mark.parametrize(
    "chunks",
    [
        [event("token", text="incomplete answer", sequence=1)],
        [b'event: done\ndata: {"conversation_id":"conv"'],
        [event("error", message="failed")],
        [event("error", message="failed") + event("done", conversation_id="conv", turn_count=0)],
        [event("done", conversation_id="conv", turn_count=1)],
        [TimeoutError("stream timeout")],
        [event("done", conversation_id="wrong", turn_count=2)],
    ],
)
def test_incomplete_or_failed_stream_never_passes(chat_call, chunks):
    with pytest.raises(RuntimeError):
        chat_call(chunks)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"http_error": RuntimeError("HTTP failure")},
        {"state_conversation": "wrong"},
        {"turn": 1},
        {"accepted": {"accepted": False}},
        {
            "messages": [
                {"role": "customer", "message_id": "customer-now"},
                {"role": "customer", "message_id": "another"},
                {"role": "ai", "content": "Other answer"},
            ]
        },
    ],
)
def test_unconfirmed_current_reply_never_passes(chat_call, kwargs):
    with pytest.raises(RuntimeError):
        chat_call([], **kwargs)


@pytest.mark.parametrize(
    "prefix",
    [
        event("validated", conversation_id="conv", message_id="ai-now")
        + event("token", text="unconfirmed appendix", sequence=3),
        event("validated", conversation_id="conv"),
        event("retracted", reason="rejected"),
    ],
)
def test_unconfirmed_stream_content_cannot_improve_quality_result(chat_call, prefix):
    with pytest.raises(RuntimeError):
        chat_call([prefix + event("done", conversation_id="conv", turn_count=2)])
