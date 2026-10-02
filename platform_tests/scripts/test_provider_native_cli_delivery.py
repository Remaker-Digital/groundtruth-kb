"""Provider transport uses agent-authored CLI calls, without a verdict publisher.

Transport and guard results are controlled here. Native service, concurrency and
Git finalization behavior are covered by the separate PostgreSQL/CLI suites.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.harness_invocation import SAMPLE_VALUES, render, sample_values

from platform_tests.scripts.provider_fixtures import (
    PROVIDERS,
    _response,
    create_provider_guard_fixtures,
    native_id_from_payload,
)
from scripts import alibaba_cloud_studio_harness as alibaba
from scripts import cloud_harness_base as base
from scripts import ollama_harness as ollama
from scripts import openrouter_harness as openrouter

ROOT = Path(__file__).resolve().parents[2]


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


# c123 (batch design WP2 2.1): the prompt is the shared root instructions alone. No launch argument selects or loads a
# role skill; the role is the binding's, and the bridge skills in the root are never read by the launcher.
BRIDGE_SKILLS = ("gtkb-bridge", "gtkb-proposal-review", "gtkb-verify")


@pytest.mark.parametrize("provider", PROVIDERS)
def test_prompt_is_the_shared_root_alone_beside_the_canonical_bridge_skills(provider, tmp_path, monkeypatch):
    monkeypatch.setenv("GTKB_INHERITED_SESSION_ID", "parent-context")
    (tmp_path / "AGENTS.md").write_text("Shared root instructions.\n", encoding="utf-8")
    for name in BRIDGE_SKILLS:
        relative = Path(".agents") / "skills" / name / "SKILL.md"
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    assert provider.build_system_prompt(tmp_path) == "Shared root instructions.\n"
    # A changed, blank or missing skill source neither reaches the prompt nor refuses it: the launcher reads none.
    target.write_text(target.read_text(encoding="utf-8") + "\nCurrent requirement changed.\n", encoding="utf-8")
    assert provider.build_system_prompt(tmp_path) == "Shared root instructions.\n"
    target.write_text(" \n", encoding="utf-8")
    assert provider.build_system_prompt(tmp_path) == "Shared root instructions.\n"
    target.unlink()
    assert provider.build_system_prompt(tmp_path) == "Shared root instructions.\n"


@pytest.mark.parametrize("provider", PROVIDERS)
def test_prompt_loading_takes_no_skill_and_assigns_no_context(provider, tmp_path):
    (tmp_path / "AGENTS.md").write_text("Shared root instructions.", encoding="utf-8")
    for name in ("gtkb-bridge", "gtkb-proposal-review"):
        target = tmp_path / ".agents" / "skills" / name / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Current source.", encoding="utf-8")
    prompt = provider.build_system_prompt(tmp_path)
    assert prompt == "Shared root instructions."
    assert "Native context identifier" not in prompt and "Immutable role" not in prompt
    with pytest.raises(TypeError):
        provider.build_system_prompt("bridge-review", tmp_path)


@pytest.mark.parametrize("provider", PROVIDERS)
def test_prompt_rereads_shared_root_without_assigning_runtime_identity(provider, tmp_path, monkeypatch):
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "parent-context")
    for name in BRIDGE_SKILLS:
        target = tmp_path / ".agents" / "skills" / name / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Selected skill body.", encoding="utf-8")
    source = tmp_path / "AGENTS.md"
    source.write_text("Root instruction one.", encoding="utf-8")
    first = provider.build_system_prompt(tmp_path)
    source.write_text("Root instruction two.", encoding="utf-8")
    second = provider.build_system_prompt(tmp_path)
    assert first == "Root instruction one."
    assert second == "Root instruction two."
    assert "Selected skill body." not in first + second
    assert "parent-context" not in first + second
    assert os.environ["GTKB_NATIVE_CONTEXT_ID"] == "parent-context"


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("kind", ["missing", "empty", "invalid_utf8", "directory"])
def test_prompt_refuses_unavailable_shared_root(provider, kind, tmp_path):
    source = tmp_path / "AGENTS.md"
    if kind == "empty":
        source.write_text(" \n", encoding="utf-8")
    elif kind == "invalid_utf8":
        source.write_bytes(b"\xff")
    elif kind == "directory":
        source.mkdir()
    with pytest.raises(RuntimeError, match="Shared root instructions are unavailable"):
        provider.build_system_prompt(tmp_path)


@pytest.mark.parametrize("provider", PROVIDERS)
def test_prompt_refuses_shared_root_that_resolves_outside_project(provider, tmp_path, monkeypatch):
    source = tmp_path / "AGENTS.md"
    source.write_text("local bytes", encoding="utf-8")
    original = Path.resolve

    def resolve(path, *args, **kwargs):
        if path == source:
            return tmp_path.parent / "foreign-root.md"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    with pytest.raises(RuntimeError, match="outside the project root"):
        provider.build_system_prompt(tmp_path)


@pytest.mark.parametrize("runtime", (base, ollama))
def test_retired_publisher_is_not_a_tool(runtime):
    assert {"Read", "Write", "Edit", "Grep", "Glob", "Bash"} == runtime.CANONICAL_TOOLS
    with pytest.raises(RuntimeError, match="unknown allowed tools"):
        runtime.build_tool_schemas(["PublishBridgeVerdict"])


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
    # c123 (batch design WP2 2.3): the assigned target alone makes this bridge work; no role skill is passed.
    kwargs = dict(
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
@pytest.mark.parametrize(
    "assignment",
    [
        # c123 (batch design WP2 2.3): only a partial or invalid target is refused; the skill-only rows are gone,
        # because a run takes no skill (test_run_tool_loop_takes_no_retired_skill_argument).
        {"bridge_document": "assigned"},
        {"bridge_version": 2},
        {"bridge_document": "assigned", "bridge_version": True},
        {"bridge_document": "", "bridge_version": 2},
        {"bridge_document": "assigned", "bridge_version": 0},
    ],
)
def test_bridge_task_requires_an_explicit_successor_before_model_execution(provider, assignment, tmp_path):
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
        provider.run_tool_loop(*args, chat_func=chat, **assignment)
    assert incomplete.value.code == "bridge_delivery_incomplete"


@pytest.mark.parametrize("provider", PROVIDERS)
def test_run_tool_loop_takes_no_retired_skill_argument(provider, tmp_path):
    """c123 (batch design WP2 2.1): a role skill can no longer be given to a run, so it cannot select bridge work."""
    args = [
        "::init gtkb lo\n::open build\nReview the proposal",
        provider.ModelRoute("fixture", "fixture-model", "v1", True, ()),
        "https://fixture.invalid",
    ]
    if provider is not ollama:
        args.append("fixture-key")
    args.extend([1, tmp_path])
    with pytest.raises(TypeError, match="skill"):
        provider.run_tool_loop(
            *args, skill="bridge-review", chat_func=lambda *_: pytest.fail("A skill argument must be refused first")
        )


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("subject,role", [("gtkb", "pb"), ("gtkb", "lo"), ("application", "pb"), ("application", "lo")])
def test_init_prompt_is_preserved_without_inventing_a_bridge_assignment(provider, subject, role, tmp_path):
    runtime = create_provider_guard_fixtures(provider, tmp_path)
    settings = tmp_path / provider.NATIVE_HOOK_SETTINGS_PATH
    settings.write_text(
        json.dumps(
            {
                "hooks": {
                    event: [{"hooks": [{"type": "command", "command": "fixture hook"}]}]
                    for event in ("SessionStart", "UserPromptSubmit", "Stop")
                }
            }
        ),
        encoding="utf-8",
    )
    original = f"Preserve this first message: café.\r\n::init {subject} {role}\r\n::open deliberation\r\nExplain the current model."
    observed = []
    prompts = []
    hook_ids = []

    def hook(command, payload, env, timeout):
        observed.append(payload["hook_event_name"])
        hook_ids.append(payload["session_id"])
        if payload["hook_event_name"] == "UserPromptSubmit":
            assert payload["prompt"] == original
        return runtime.GuardExecutionResult(0, "{}")

    def chat(*args):
        payload = args[-2]
        prompts.append([m["content"] for m in payload["messages"] if m["role"] == "user"])
        assert prompts[-1] == [original]
        assert native_id_from_payload(payload) in hook_ids
        return _response(provider, content="No measurements were supplied.")

    args = [original, provider.ModelRoute("fixture", "fixture-model", "v1", True, ()), "https://fixture.invalid"]
    if provider is not ollama:
        args.append("fixture-key")
    args.extend([1, tmp_path])
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert (
        provider.run_tool_loop(
            *args,
            chat_func=chat,
            native_hook_runner=hook,
            command_runner=lambda *_: pytest.fail("Initialization alone must not require bridge delivery"),
        )
        == "No measurements were supplied."
    )
    assert len(prompts) == 1
    assert observed == ["SessionStart", "UserPromptSubmit", "Stop"] and len(set(hook_ids)) == 1
    assert {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


# c123 (batch design WP2 2.1, step 3): the corrected F, D and H templates, after the launcher script.
REGISTERED_TEMPLATES = {
    openrouter: ["--init", "{{INIT_LINE}}", "--bridge-document", "{{DOCUMENT}}", "--bridge-version", "{{VERSION}}"]
    + ["--report", "{{REPORT}}", "-p", "{{PROMPT}}", "--model", "deepseek-v4-flash"],
    ollama: ["--init", "{{INIT_LINE}}", "--bridge-document", "{{DOCUMENT}}", "--bridge-version", "{{VERSION}}"]
    + ["--report", "{{REPORT}}", "-p", "{{PROMPT}}", "--model", "deepseek-v4-flash-cloud"],
    alibaba: ["--init", "{{INIT_LINE}}", "--bridge-document", "{{DOCUMENT}}", "--bridge-version", "{{VERSION}}"]
    + ["--report", "{{REPORT}}", "--prompt", "{{PROMPT}}", "--model", "alibaba-deepseek-v4-pro"],
}


@pytest.mark.parametrize("provider", PROVIDERS)
def test_each_launcher_parses_its_registered_template_and_refuses_the_retired_skill_selector(provider, capsys):
    """c123 (batch design WP2 2.1): --init replaces --skill; the rendered template carries the bridge target."""
    parser = provider.build_arg_parser()
    args = parser.parse_args(render(REGISTERED_TEMPLATES[provider], sample_values("fixture-root")))
    assert args.init == SAMPLE_VALUES["INIT_LINE"]
    assert (args.bridge_document, args.bridge_version) == (SAMPLE_VALUES["DOCUMENT"], int(SAMPLE_VALUES["VERSION"]))
    assert (args.report, args.prompt) == (SAMPLE_VALUES["REPORT"], SAMPLE_VALUES["PROMPT"])
    assert args.model == REGISTERED_TEMPLATES[provider][-1]
    assert not hasattr(args, "skill")
    for retired in (["--skill", "bridge-review"], ["--skill=verification"]):
        with pytest.raises(SystemExit) as refused:
            parser.parse_args(["--prompt", "Review", *retired])
        assert refused.value.code == 2
    assert "unrecognized arguments: --skill" in capsys.readouterr().err


def _entrypoint_fixtures(provider, tmp_path, monkeypatch):
    """Let a launcher's main run offline in tmp_path: no key file, no host and one fixture route."""
    from scripts import _env

    create_provider_guard_fixtures(provider, tmp_path)
    route = provider.ModelRoute("fixture", "fixture-model", "v1", True, ())
    monkeypatch.setattr(_env, "load_env_local", lambda: None)
    monkeypatch.setattr(provider, "ensure_utf8_output_streams", lambda: None)
    monkeypatch.setattr(provider, "resolve_project_root", lambda _root: tmp_path)
    monkeypatch.setattr(provider, "load_routing_config", lambda _root: object())
    # c123 (batch design WP2 2.1): the launcher resolves its route from --model alone; no skill reaches this call.
    monkeypatch.setattr(provider, "resolve_model", lambda _config, _requested_model: route)
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


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("delivered", [False, True])
def test_provider_entrypoint_returns_nonzero_for_undelivered_assignment(
    provider, delivered, tmp_path, monkeypatch, capsys
):
    _entrypoint_fixtures(provider, tmp_path, monkeypatch)
    # c123 (batch design WP2 2.1): the prompt is built from the project root alone.
    monkeypatch.setattr(provider, "build_system_prompt", lambda _project_root: None)
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
    # c123 (batch design WP2, item 10): an incomplete delivery has its own exit code, so a caller can tell it apart.
    assert code == (0 if delivered else base.EXIT_DELIVERY_INCOMPLETE)
    if delivered:
        assert "Model final prose." in output.out
    else:
        assert "bridge_delivery_incomplete" in output.err and "Model final prose." not in output.out


# c123 (batch design WP2 2.1): with --init the launcher binds its own context through the native CLI before its first
# provider call and states the bound facts. The bind is replaced on the launcher's own base module, which is the
# module its bind_for_run reads.
BOUND = {"session_context_id": "bound-session-context", "role": "loyal-opposition"}


def _bind(events):
    def bind(native_context_id, init_line, project_root, runner=None):
        events.append(("bind", native_context_id, init_line, project_root))
        return {**BOUND, "native_context_id": native_context_id}

    return bind


def _with_transport(provider, monkeypatch, chat, command_runner=None):
    """Run the launcher's real loop over a controlled transport; return the keywords main passed to it."""
    run = provider.run_tool_loop
    seen = {}

    def wrapped(*args, **kwargs):
        seen.update(kwargs)
        extra = {} if command_runner is None else {"command_runner": command_runner}
        return run(*args, **kwargs, chat_func=chat, **extra)

    monkeypatch.setattr(provider, "run_tool_loop", wrapped)
    return seen


def _system_text(payload):
    return payload.get("system") or "\n".join(m["content"] for m in payload["messages"] if m["role"] == "system")


@pytest.mark.parametrize("provider", PROVIDERS)
def test_init_binds_the_context_before_the_first_model_call(provider, tmp_path, monkeypatch, capsys):
    _entrypoint_fixtures(provider, tmp_path, monkeypatch)
    (tmp_path / "AGENTS.md").write_text("Shared root instructions.", encoding="utf-8")
    events = []
    if provider is ollama:

        def tags(*args):
            events.append(("tags",))
            return []

        # D binds after its /api/tags probe and before its first model call.
        monkeypatch.setattr(provider, "call_ollama_tags", tags)
    monkeypatch.setattr(provider.base, "bind_native_context", _bind(events))

    def chat(*args):
        events.append(("chat", native_id_from_payload(args[-2])))
        return _response(provider, content="Bound final prose.")

    seen = _with_transport(provider, monkeypatch, chat)
    report = tmp_path / "run-report.json"
    code = provider.main(
        ["--prompt", "Explain the current model.", "--init", "::init gtkb lo", "--report", str(report)]
    )

    assert code == 0 and "Bound final prose." in capsys.readouterr().out
    assert [event[0] for event in events] == (["tags"] if provider is ollama else []) + ["bind", "chat"]
    (_, bound_id, init_line, project_root), (_, model_id) = events[-2:]
    assert (init_line, project_root) == ("::init gtkb lo", tmp_path)
    assert bound_id == model_id == seen["native_context_id"]
    assert seen["binding"] == {**BOUND, "native_context_id": bound_id}
    written = json.loads(report.read_text(encoding="utf-8"))
    assert (written["native_context_id"], written["session_context_id"], written["role"]) == (
        bound_id,
        BOUND["session_context_id"],
        BOUND["role"],
    )
    assert (written["exit_code"], written["error"]) == (0, None)


@pytest.mark.parametrize("provider", PROVIDERS)
def test_the_bound_role_and_session_context_reach_the_system_message(provider, tmp_path, monkeypatch, capsys):
    _entrypoint_fixtures(provider, tmp_path, monkeypatch)
    (tmp_path / "AGENTS.md").write_text("Shared root instructions.", encoding="utf-8")
    monkeypatch.setattr(provider.base, "bind_native_context", _bind([]))
    systems = []
    checks = []

    def chat(*args):
        systems.append(_system_text(args[-2]))
        return _response(provider, content="Delivered and read back.")

    def runner(command, cwd, env, timeout):
        checks.append(command)
        proof = {
            "status": "delivered",
            "document": "assigned",
            "version": 2,
            "native_context_id": env["GTKB_NATIVE_CONTEXT_ID"],
            "author_session_context_id": BOUND["session_context_id"],
            "bridge_status": "GO",
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(proof), stderr="")

    _with_transport(provider, monkeypatch, chat, runner)
    code = provider.main(
        ["--prompt", "Review assigned", "--init", "::init gtkb lo", "--bridge-document", "assigned"]
        + ["--bridge-version", "2"]
    )

    assert code == 0 and "Delivered and read back." in capsys.readouterr().out
    (system,) = systems
    assert "Bound session context: bound-session-context. Immutable role: loyal-opposition." in system
    assert "do not bind it again" in system and "Bind only the exact init marker" not in system
    assert "Assigned bridge document: assigned. The artifact you deliver must be version 2." in system
    assert "gt bridge claim" in system and "gt bridge check-delivery" in system
    assert system.index("Immutable role: loyal-opposition") < system.index("Shared root instructions.")
    assert len(checks) == 1 and " bridge check-delivery assigned " in checks[0]


@pytest.mark.parametrize("provider", PROVIDERS)
def test_a_refused_bind_exits_bind_failed_without_a_model_call(provider, tmp_path, monkeypatch, capsys):
    _entrypoint_fixtures(provider, tmp_path, monkeypatch)
    (tmp_path / "AGENTS.md").write_text("Shared root instructions.", encoding="utf-8")

    def refuse(native_context_id, init_line, project_root, runner=None):
        raise provider.base.NativeBindFailed("native_bind_failed: gt session bind exited 2")

    def no_model_call(*args, **kwargs):
        pytest.fail("A refused bind must end the launch before any model call")

    monkeypatch.setattr(provider.base, "bind_native_context", refuse)
    monkeypatch.setattr(provider, "run_tool_loop", no_model_call)
    report = tmp_path / "run-report.json"
    code = provider.main(["--prompt", "Review assigned", "--init", "::init gtkb lo", "--report", str(report)])

    assert code == base.EXIT_BIND_FAILED == 4
    assert "native_bind_failed: gt session bind exited 2" in capsys.readouterr().err
    written = json.loads(report.read_text(encoding="utf-8"))
    assert (written["exit_code"], written["error"]) == (
        base.EXIT_BIND_FAILED,
        "native_bind_failed: gt session bind exited 2",
    )
    assert (written["session_context_id"], written["role"], written["turns"]) == (None, None, 0)


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize(
    ("target", "settings", "code", "message"),
    [
        (["--bridge-document", "assigned"], True, base.EXIT_DELIVERY_INCOMPLETE, "bridge_delivery_incomplete"),
        (["--bridge-version", "2"], True, base.EXIT_DELIVERY_INCOMPLETE, "bridge_delivery_incomplete"),
        ([], False, 1, "native hook settings are missing"),
    ],
    ids=["document_only", "version_only", "no_hook_settings"],
)
def test_a_launch_that_cannot_run_ends_before_the_bind(
    provider, target, settings, code, message, tmp_path, monkeypatch, capsys
):
    """c123 (batch design WP2 2.1): every launch input is checked before --init binds, so no session is registered."""
    _entrypoint_fixtures(provider, tmp_path, monkeypatch)
    (tmp_path / "AGENTS.md").write_text("Shared root instructions.", encoding="utf-8")
    if not settings:
        (tmp_path / provider.NATIVE_HOOK_SETTINGS_PATH).unlink()

    def no_bind(*args, **kwargs):
        pytest.fail("A launch that cannot run must not bind")

    def no_model_call(*args, **kwargs):
        pytest.fail("A launch that cannot run must not reach the loop")

    monkeypatch.setattr(provider.base, "bind_native_context", no_bind)
    monkeypatch.setattr(provider, "run_tool_loop", no_model_call)
    assert provider.main(["--prompt", "Review assigned", "--init", "::init gtkb lo", *target]) == code
    assert message in capsys.readouterr().err


@pytest.mark.parametrize("provider", PROVIDERS)
def test_without_init_the_run_stays_unbound_and_keeps_the_bind_request(provider, tmp_path, monkeypatch, capsys):
    _entrypoint_fixtures(provider, tmp_path, monkeypatch)
    (tmp_path / "AGENTS.md").write_text("Shared root instructions.", encoding="utf-8")

    def no_bind(*args, **kwargs):
        pytest.fail("Without --init the launcher must not bind")

    monkeypatch.setattr(provider.base, "bind_native_context", no_bind)
    systems = []

    def chat(*args):
        systems.append(_system_text(args[-2]))
        return _response(provider, content="Unbound final prose.")

    seen = _with_transport(provider, monkeypatch, chat)
    report = tmp_path / "run-report.json"
    code = provider.main(["--prompt", "::init gtkb lo\nExplain the current model.", "--report", str(report)])

    assert code == 0 and "Unbound final prose." in capsys.readouterr().out
    assert seen["binding"] is None
    (system,) = systems
    assert "Bind only the exact init marker supplied in the task through gt session bind." in system
    assert "Immutable role:" not in system and "Bound session context:" not in system
    written = json.loads(report.read_text(encoding="utf-8"))
    assert (written["session_context_id"], written["role"]) == (None, None)
