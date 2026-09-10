"""Provider transport uses agent-authored CLI calls, without a verdict publisher.

Transport and guard results are controlled here. Native service, concurrency and
Git finalization behavior are covered by the separate PostgreSQL/CLI suites.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from uuid import UUID

import pytest

from scripts import alibaba_cloud_studio_harness as alibaba
from scripts import cloud_harness_base as base
from scripts import ollama_harness as ollama
from scripts import openrouter_harness as openrouter

PROVIDERS = (openrouter, ollama, alibaba)
ROOT = Path(__file__).resolve().parents[2]


def create_provider_guard_fixtures(provider, root):
    runtime = ollama if provider is ollama else base
    paths = set(runtime.WRITE_EDIT_GUARDS + runtime.BASH_GUARDS)
    if runtime is base:
        paths = base.projected_guard_paths(tuple(paths), provider.ROUTING_CONFIG_PATH)
    for relative in paths:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Controlled guard fixture", encoding="utf-8")
    (root / provider.ROUTING_CONFIG_PATH.parent / "settings.json").write_text('{"hooks": {}}', encoding="utf-8")
    return runtime


def native_id_from_payload(payload):
    system = payload.get("system") or "\n".join(
        message["content"] for message in payload["messages"] if message["role"] == "system"
    )
    identifiers = re.findall(r"Native context identifier: ([0-9a-f-]{36})\.", system)
    assert len(identifiers) == 1, system
    assert str(UUID(identifiers[0])) == identifiers[0]
    return identifiers[0]


@pytest.mark.parametrize("provider", PROVIDERS)
def test_fresh_runs_keep_independent_native_identity_through_tools_and_model_changes(provider, tmp_path, monkeypatch):
    for name in (
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CURSOR_CONVERSATION_ID",
        "ANTIGRAVITY_SESSION_ID",
        "GOOSE_SESSION_ID",
        "GTKB_SESSION_ID",
        "GTKB_NATIVE_CONTEXT_ID",
        "GTKB_AUTHOR_SESSION_CONTEXT_ID",
    ):
        monkeypatch.setenv(name, "parent-context")
    runtime = create_provider_guard_fixtures(provider, tmp_path)
    route = provider.ModelRoute("fixture", "requested-model", "v1", True, ("Bash",))

    def run_context():
        turn_ids, command_ids, guard_ids = [], [], []

        def chat(*args):
            payload = args[-2]
            turn_ids.append(native_id_from_payload(payload))
            if len(turn_ids) <= 2:
                response = _response(
                    provider,
                    tool="Bash",
                    arguments={"command": "gt session show --native-context-id " + turn_ids[-1] + " --json"},
                )
                response["model"] = "resolved-model"
                return response
            return _response(provider, content="Readback complete.")

        def runner(command, cwd, env, timeout):
            assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env
            command_ids.append(env["GTKB_NATIVE_CONTEXT_ID"])
            assert command == "gt session show --native-context-id " + command_ids[-1] + " --json"
            return subprocess.CompletedProcess(command, 0, stdout="{}", stderr="")

        def guard(path, payload, env, timeout):
            guard_ids.append(payload["session_id"])
            assert payload["session_id"] == env["GTKB_NATIVE_CONTEXT_ID"]
            assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env
            if provider is not ollama:
                assert env["GTKB_AUTHOR_MODEL"] == "resolved-model"
            return runtime.GuardExecutionResult(0, "{}")

        kwargs = dict(
            prompt="Read current binding.",
            model_route=route,
            endpoint="https://fixture.invalid",
            max_turns=3,
            project_root=tmp_path,
            chat_func=chat,
            guard_runner=guard,
            command_runner=runner,
        )
        if provider is not ollama:
            kwargs["api_key"] = "fixture-key"
        assert provider.run_tool_loop(**kwargs) == "Readback complete."
        assert len(turn_ids) == 3 and len(command_ids) == 2 and guard_ids
        assert set(turn_ids + command_ids + guard_ids) == {turn_ids[0]}
        return turn_ids[0]

    run_ids = [run_context(), run_context()]
    assert len(set(run_ids)) == 2
    assert os.environ["GTKB_NATIVE_CONTEXT_ID"] == "parent-context"


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("skill,selected", [("bridge-review", "gtkb-proposal-review"), ("verification", "gtkb-verify")])
def test_prompt_reads_current_selected_canonical_skills(provider, skill, selected, tmp_path, monkeypatch):
    monkeypatch.setenv("GTKB_INHERITED_SESSION_ID", "parent-context")
    for name in ("gtkb-bridge", selected):
        relative = Path(".harness-baseline-configuration") / "skills" / name / "SKILL.md"
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    prompt = provider.build_system_prompt(skill, tmp_path)
    assert "parent-context" not in prompt
    assert "gt bridge deliver" in prompt
    assert "PublishBridgeVerdict" not in prompt
    assert "write_verdict.py" not in prompt
    assert "Prior Deliberations" not in prompt
    assert "gt projects commit" in prompt
    target.write_text(target.read_text(encoding="utf-8") + "\nCurrent requirement changed.\n", encoding="utf-8")
    assert "Current requirement changed." in provider.build_system_prompt(skill, tmp_path)
    target.write_text(" \n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="empty source"):
        provider.build_system_prompt(skill, tmp_path)
    target.unlink()
    with pytest.raises(RuntimeError, match="canonical bridge skill instructions are unavailable"):
        provider.build_system_prompt(skill, tmp_path)


@pytest.mark.parametrize("provider", PROVIDERS)
def test_skill_loading_does_not_assign_a_context_before_the_runtime_starts(provider, tmp_path):
    for name in ("gtkb-bridge", "gtkb-proposal-review"):
        target = tmp_path / ".harness-baseline-configuration" / "skills" / name / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Current source.", encoding="utf-8")
    assert provider.build_system_prompt("bridge-review", tmp_path) == "Current source.\n\nCurrent source."
    assert provider.build_system_prompt(None, tmp_path) is None
    assert provider.build_system_prompt("implementation", tmp_path) is None


@pytest.mark.parametrize("runtime", (base, ollama))
def test_retired_publisher_is_not_a_tool(runtime):
    assert {"Read", "Write", "Edit", "Grep", "Glob", "Bash"} == runtime.CANONICAL_TOOLS
    with pytest.raises(RuntimeError, match="unknown allowed tools"):
        runtime.build_tool_schemas(["PublishBridgeVerdict"])


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


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("command_succeeds", (True, False))
def test_agent_authors_bytes_and_executes_cli_without_harness_publication(
    provider, command_succeeds, tmp_path, monkeypatch
):
    monkeypatch.delenv("GTKB_BRIDGE_DISPATCH_KEYWORD", raising=False)
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    runtime = create_provider_guard_fixtures(provider, tmp_path)
    route = provider.ModelRoute("fixture", "fixture-model", "v1", True, ("Write", "Bash"))
    authored = "GO\r\n::init gtkb pb\r\n::open build\r\nauthor_model: authored-model\r\n\r\nReview evidence: café.\r\n"
    message_path = "scratchpad/native-fixture/reply.md"
    command = (
        "gt bridge deliver assigned-document --native-context-id native-fixture --fence 4 --content-file "
        + message_path
        + " --json"
    )
    calls = []
    commands = []
    guards = []

    def guard(path, payload, env, timeout):
        guards.append((path, payload))
        return runtime.GuardExecutionResult(0, "{}")

    def runner(received, cwd, env, timeout):
        commands.append(received)
        if " bridge check-delivery " in received:
            return subprocess.CompletedProcess(
                received,
                0 if command_succeeds else 1,
                stdout=json.dumps(
                    {
                        "status": "delivered",
                        "document": "assigned-document",
                        "version": 2,
                        "native_context_id": env["GTKB_NATIVE_CONTEXT_ID"],
                        "author_session_context_id": "bound-fixture",
                        "bridge_status": "GO",
                    }
                ),
                stderr="" if command_succeeds else "authority unavailable",
            )
        assert received == command
        assert (cwd / message_path).read_bytes() == authored.encode("utf-8")
        return subprocess.CompletedProcess(
            received,
            0 if command_succeeds else 1,
            stdout='{"status":"GO"}' if command_succeeds else "",
            stderr="" if command_succeeds else "authority unavailable",
        )

    def chat(*args):
        payload = args[-2]
        calls.append(payload)
        assert {tool.get("name") or tool["function"]["name"] for tool in payload["tools"]} == {"Write", "Bash"}
        if len(calls) == 1:
            return _response(provider, tool="Write", arguments={"path": message_path, "content": authored})
        if len(calls) == 2:
            return _response(provider, tool="Bash", arguments={"command": command})
        assert ("GO" if command_succeeds else "authority unavailable") in json.dumps(payload)
        return _response(
            provider, content="CLI result inspected" if command_succeeds else "Unable to deliver: authority unavailable"
        )

    args = ["::init gtkb lo\n::open build\nReview assigned-document", route, "https://fixture.invalid"]
    if provider is not ollama:
        args.append("fixture-key")
    args.extend([5, tmp_path])
    kwargs = dict(
        skill="bridge-review",
        bridge_document="assigned-document",
        bridge_version=2,
        chat_func=chat,
        guard_runner=guard,
        command_runner=runner,
    )
    if command_succeeds:
        assert provider.run_tool_loop(*args, **kwargs) == "CLI result inspected"
    else:
        with pytest.raises(RuntimeError, match="bridge_delivery_incomplete") as incomplete:
            provider.run_tool_loop(*args, **kwargs)
        assert incomplete.value.code == "bridge_delivery_incomplete"
    assert len(commands) == 2 and commands[0] == command and " bridge check-delivery " in commands[1]
    assert len(calls) == 3
    assert guards
    assert not (tmp_path / "bridge").exists()
    assert (tmp_path / message_path).read_bytes() == authored.encode("utf-8")


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize(
    "failure", ["absent", "malformed", "wrong_document", "wrong_version", "wrong_context", "timeout"]
)
def test_final_prose_requires_exact_canonical_delivery(provider, failure, tmp_path):
    create_provider_guard_fixtures(provider, tmp_path)
    calls = []
    native_id = None

    def chat(*args):
        nonlocal native_id
        native_id = native_id_from_payload(args[-2])
        return _response(provider, content="Unable to deliver.")

    def runner(command, cwd, env, timeout):
        calls.append(command)
        assert " bridge check-delivery assigned " in command
        assert env["GTKB_NATIVE_CONTEXT_ID"] == native_id
        assert timeout <= 10
        if failure == "timeout":
            raise subprocess.TimeoutExpired(command, timeout)
        proof = {
            "status": "delivered",
            "document": "assigned",
            "version": 2,
            "native_context_id": native_id,
            "author_session_context_id": "bound",
            "bridge_status": "GO",
        }
        if failure == "wrong_document":
            proof["document"] = "unrelated"
        elif failure == "wrong_version":
            proof["version"] = 3
        elif failure == "wrong_context":
            proof["native_context_id"] = "another-context"
        return subprocess.CompletedProcess(
            command,
            1 if failure == "absent" else 0,
            stdout="not JSON" if failure == "malformed" else json.dumps(proof),
            stderr="",
        )

    args = [
        "::init gtkb lo\n::open build\nReview assigned",
        provider.ModelRoute("fixture", "fixture-model", "v1", True, ()),
        "https://fixture.invalid",
    ]
    if provider is not ollama:
        args.append("fixture-key")
    args.extend([1, tmp_path])
    with pytest.raises(RuntimeError, match="bridge_delivery_incomplete") as incomplete:
        provider.run_tool_loop(
            *args, bridge_document="assigned", bridge_version=2, chat_func=chat, command_runner=runner
        )
    assert incomplete.value.code == "bridge_delivery_incomplete"
    assert len(calls) == 1
    assert not (tmp_path / "bridge").exists()


@pytest.mark.parametrize("provider", PROVIDERS)
def test_bridge_task_requires_an_explicit_successor_before_model_execution(provider, tmp_path):
    def chat(*args):
        pytest.fail("An unscoped bridge task must be refused before contacting the model")

    args = [
        "::init gtkb lo\n::open build\nReview the proposal",
        provider.ModelRoute("fixture", "fixture-model", "v1", True, ()),
        "https://fixture.invalid",
    ]
    if provider is not ollama:
        args.append("fixture-key")
    args.extend([1, tmp_path])
    with pytest.raises(RuntimeError, match="--bridge-document") as incomplete:
        provider.run_tool_loop(*args, chat_func=chat)
    assert incomplete.value.code == "bridge_delivery_incomplete"


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("delivered", [False, True])
def test_provider_entrypoint_returns_nonzero_for_undelivered_assignment(
    provider, delivered, tmp_path, monkeypatch, capsys
):
    from scripts import _env

    create_provider_guard_fixtures(provider, tmp_path)
    route = provider.ModelRoute("fixture", "fixture-model", "v1", True, ())
    monkeypatch.setattr(_env, "load_env_local", lambda: None)
    monkeypatch.setattr(provider, "ensure_utf8_output_streams", lambda: None)
    monkeypatch.setattr(provider, "resolve_project_root", lambda _root: tmp_path)
    monkeypatch.setattr(provider, "load_routing_config", lambda _root: object())
    monkeypatch.setattr(provider, "resolve_model", lambda *args, **kwargs: route)
    monkeypatch.setattr(provider, "build_system_prompt", lambda *args: None)
    if provider is ollama:
        monkeypatch.setattr(provider, "resolve_runtime_timeouts", lambda *args: (10, 30))
        monkeypatch.setattr(provider, "resolve_runtime_max_turns", lambda *args: 1)
        monkeypatch.setattr(provider, "call_ollama_tags", lambda *args: [])
        monkeypatch.setattr(provider, "validate_advertised_models", lambda *args: None)
    else:
        monkeypatch.setattr(provider, "resolve_runtime_limits", lambda *args, **kwargs: (10, 30, 1))
        monkeypatch.setenv("OPENROUTER_API_KEY" if provider is openrouter else provider.API_KEY_ENV, "fixture-key")
        if provider is alibaba:
            monkeypatch.setenv(provider.ENDPOINT_ENV, "https://fixture.invalid")
            monkeypatch.setattr(provider, "_load_env_local", lambda: None)
    run = provider.run_tool_loop

    def wrapped(*args, **kwargs):
        assert (kwargs["bridge_document"], kwargs["bridge_version"]) == ("assigned", 2)

        def runner(command, cwd, env, timeout):
            proof = {
                "status": "delivered",
                "document": "assigned",
                "version": 2,
                "native_context_id": env["GTKB_NATIVE_CONTEXT_ID"],
                "author_session_context_id": "bound-fixture",
                "bridge_status": "GO",
            }
            return subprocess.CompletedProcess(command, 0 if delivered else 1, stdout=json.dumps(proof), stderr="")

        return run(
            *args,
            **kwargs,
            chat_func=lambda *args: _response(provider, content="Model final prose."),
            command_runner=runner,
        )

    monkeypatch.setattr(provider, "run_tool_loop", wrapped)
    code = provider.main(
        [
            "--prompt",
            "::init gtkb lo\n::open build\nReview assigned",
            "--bridge-document",
            "assigned",
            "--bridge-version",
            "2",
        ]
    )
    output = capsys.readouterr()
    assert code == (0 if delivered else 1)
    if delivered:
        assert "Model final prose." in output.out
    else:
        assert "bridge_delivery_incomplete" in output.err and "Model final prose." not in output.out
