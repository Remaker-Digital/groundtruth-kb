"""Shared helpers of the provider CLI delivery qualification (c102, Q-3, owner ruling D23).

Moved verbatim from ``test_provider_native_cli_delivery.py`` (``PROVIDERS``,
``create_provider_guard_fixtures``, ``native_id_from_payload``, ``_response``) so that no test
module imports another test module. Not collected; defines no test.
"""

from __future__ import annotations

import json
import re
from uuid import UUID

from scripts import alibaba_cloud_studio_harness as alibaba
from scripts import cloud_harness_base as base
from scripts import ollama_harness as ollama
from scripts import openrouter_harness as openrouter

PROVIDERS = (openrouter, ollama, alibaba)


def create_provider_guard_fixtures(provider, root):
    runtime = ollama if provider is ollama else base
    paths = set(runtime.WRITE_EDIT_GUARDS + runtime.BASH_GUARDS)
    for relative in paths:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Controlled guard fixture", encoding="utf-8")
    (root / provider.NATIVE_HOOK_SETTINGS_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / provider.NATIVE_HOOK_SETTINGS_PATH).write_text('{"hooks": {}}', encoding="utf-8")
    return runtime


def native_id_from_payload(payload):
    system = payload.get("system") or "\n".join(
        message["content"] for message in payload["messages"] if message["role"] == "system"
    )
    identifiers = re.findall(r"Native context identifier: ([0-9a-f-]{36})\.", system)
    assert len(identifiers) == 1, system
    assert str(UUID(identifiers[0])) == identifiers[0]
    return identifiers[0]


def _response(provider, *, tool=None, arguments=None, content=""):
    if provider is alibaba:
        blocks = (
            [{"type": "tool_use", "id": "call-1", "name": tool, "input": arguments}]
            if tool
            else [{"type": "text", "text": content}]
        )
        return {"content": blocks, "stop_reason": "tool_use" if tool else "end_turn"}
    message = {"content": content}
    if tool:
        message["tool_calls"] = [
            {
                "id": "call-1",
                "function": {"name": tool, "arguments": arguments if provider is ollama else json.dumps(arguments)},
            }
        ]
    return {"message": message} if provider is ollama else {"choices": [{"message": message}]}
