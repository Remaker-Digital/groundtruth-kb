from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import ollama_harness as oh

FIXTURE_MODEL_ID = "fixture-model:fixture-version"
FIXTURE_MODEL_VERSION = oh.infer_model_version(FIXTURE_MODEL_ID)


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / ".claude" / "hooks").mkdir(parents=True)
    (root / "scripts").mkdir()
    for guard in {*oh.BRIDGE_WRITE_GUARDS, *oh.BRIDGE_EDIT_GUARDS, *oh.WRITE_EDIT_GUARDS, *oh.BASH_GUARDS}:
        path = root / guard
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("print('{}')\n", encoding="utf-8")
    (root / oh.ROUTING_CONFIG_PATH).write_text(
        """
schema_version = 1

[models.fixture-full]
model_id = "fixture-model:fixture-version"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[routing.ollama]
default_model = "fixture-full"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return root


def route(root: Path) -> oh.ModelRoute:
    return oh.resolve_model(oh.load_routing_config(root), None)


def metadata() -> oh.ModelMetadata:
    return oh.ModelMetadata(
        model_id=FIXTURE_MODEL_ID,
        model_version=FIXTURE_MODEL_VERSION,
        endpoint="http://localhost:11434",
        route_key="fixture-full",
    )


def allow_runner(records: list[tuple[str, dict, dict]]):
    def run_guard(path: Path, payload: dict, env: dict, timeout: float) -> oh.GuardExecutionResult:
        records.append((path.as_posix(), payload, dict(env)))
        return oh.GuardExecutionResult(returncode=0, stdout="{}")

    return run_guard


def deny_runner(records: list[tuple[str, dict, dict]], needle: str = "implementation_start_gate.py"):
    def run_guard(path: Path, payload: dict, env: dict, timeout: float) -> oh.GuardExecutionResult:
        records.append((path.as_posix(), payload, dict(env)))
        if needle in path.as_posix():
            return oh.GuardExecutionResult(returncode=0, stdout='{"decision":"block","reason":"denied"}')
        return oh.GuardExecutionResult(returncode=0, stdout="{}")

    return run_guard


def test_load_routing_config_parses_selected_model(tmp_path: Path):
    root = make_root(tmp_path)
    config = oh.load_routing_config(root)
    selected = oh.resolve_model(config, None)
    assert selected.key == "fixture-full"
    assert selected.model_id == FIXTURE_MODEL_ID
    assert selected.model_version == FIXTURE_MODEL_VERSION
    assert selected.allowed_tools == ("Read", "Write", "Edit", "Grep", "Glob", "Bash")


def test_routing_rejects_noncanonical_tool(tmp_path: Path):
    root = make_root(tmp_path)
    (root / oh.ROUTING_CONFIG_PATH).write_text(
        """
schema_version = 1
[models.bad]
model_id = "bad"
tool_calling_supported = true
allowed_tools = ["Read", "Delete"]
[routing]
default_model = "bad"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(oh.OllamaHarnessError, match="noncanonical"):
        oh.load_routing_config(root)


def test_cli_parser_accepts_required_flags():
    parser = oh.build_arg_parser()
    args = parser.parse_args(
        [
            "-p",
            "hello",
            "--model",
            "selected-route",
            "--skill",
            "bridge-review",
            "--endpoint",
            "http://x",
            "--max-turns",
            "2",
        ]
    )
    assert args.prompt == "hello"
    assert args.model == "selected-route"
    assert args.skill == "bridge-review"
    assert args.endpoint == "http://x"
    assert args.max_turns == 2


def test_tool_schemas_expose_only_canonical_tools():
    schemas = oh.build_tool_schemas(["Read", "Write", "Edit", "Grep", "Glob", "Bash"])
    names = [schema["function"]["name"] for schema in schemas]
    assert names == ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    with pytest.raises(oh.OllamaHarnessError):
        oh.build_tool_schemas(["Read", "Delete"])


def test_tool_loop_posts_chat_payload_and_returns_final_text(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "note.txt").write_text("hello from file", encoding="utf-8")
    calls: list[tuple[str, dict]] = []

    def chat(url: str, payload: dict, timeout: float) -> dict:
        calls.append((url, payload))
        if len(calls) == 1:
            return {
                "message": {
                    "content": "",
                    "tool_calls": [{"id": "c1", "function": {"name": "Read", "arguments": {"path": "note.txt"}}}],
                }
            }
        assert payload["messages"][-1]["role"] == "tool"
        assert "hello from file" in payload["messages"][-1]["content"]
        return {"message": {"content": "final answer"}}

    text = oh.run_tool_loop("read it", route(root), "http://ollama.test", 3, root, chat_func=chat)
    assert text == "final answer"
    assert calls[0][0] == "http://ollama.test"
    assert calls[0][1]["model"] == FIXTURE_MODEL_ID
    assert calls[0][1]["stream"] is False
    assert {tool["function"]["name"] for tool in calls[0][1]["tools"]} == oh.CANONICAL_TOOLS


def test_bridge_review_system_prompt_uses_selected_route_metadata(tmp_path: Path):
    root = make_root(tmp_path)
    calls: list[dict] = []
    prompt = oh.build_system_prompt("bridge-review", route(root))

    def chat(url: str, payload: dict, timeout: float) -> dict:
        calls.append(payload)
        return {"message": {"content": "done"}}

    text = oh.run_tool_loop(
        "review bridge item",
        route(root),
        "http://ollama.test",
        1,
        root,
        system_prompt=prompt,
        chat_func=chat,
    )

    assert text == "done"
    system_message = calls[0]["messages"][0]
    assert system_message["role"] == "system"
    assert calls[0]["messages"][1] == {"role": "user", "content": "review bridge item"}
    assert "Loyal Opposition" in system_message["content"]
    assert "bridge/INDEX.md" not in system_message["content"]
    assert "full\nversioned bridge-file chain" in system_message["content"]
    assert "retired bridge index" in system_message["content"]
    assert "bridge_claim_cli.py claim <document-slug>" in system_message["content"]
    assert f"author_model: {FIXTURE_MODEL_ID}" in system_message["content"]
    assert f"author_model_version: {FIXTURE_MODEL_VERSION}" in system_message["content"]


def test_system_prompt_is_only_for_lo_bridge_skills(tmp_path: Path):
    root = make_root(tmp_path)

    assert oh.build_system_prompt("bridge-review", route(root)) is not None
    assert oh.build_system_prompt("verification", route(root)) is not None
    assert oh.build_system_prompt("implementation", route(root)) is None
    assert oh.build_system_prompt(None, route(root)) is None


def test_bridge_review_prompt_requires_atomic_verified_finalization(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = oh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    assert "--finalize-verified" in prompt
    assert "--no-prepopulate" in prompt
    assert "local commit containing the verified path set" in prompt
    assert "fail closed" in prompt
    assert "terminal VERIFIED file" in prompt


def test_default_tool_loop_calls_single_chat_endpoint(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    root = make_root(tmp_path)
    urls: list[str] = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self) -> bytes:
            return json.dumps({"message": {"content": "done"}}).encode("utf-8")

    def fake_urlopen(request, timeout: float):
        urls.append(request.full_url)
        return Response()

    monkeypatch.setattr(oh.urllib.request, "urlopen", fake_urlopen)
    text = oh.run_tool_loop("hello", route(root), "http://ollama.test/", 1, root)
    assert text == "done"
    assert urls == ["http://ollama.test/api/chat"]


def test_utf8_output_stream_setup_allows_non_cp1252_final_text():
    output_bytes = io.BytesIO()
    stdout = io.TextIOWrapper(output_bytes, encoding="cp1252", errors="strict")
    error_bytes = io.BytesIO()
    stderr = io.TextIOWrapper(error_bytes, encoding="cp1252", errors="strict")

    oh.ensure_utf8_output_streams(stdout, stderr)
    print("ready \u2192 verified", file=stdout)
    print("error \u2192 visible", file=stderr)
    stdout.flush()
    stderr.flush()

    assert output_bytes.getvalue().decode("utf-8").splitlines() == ["ready \u2192 verified"]
    assert error_bytes.getvalue().decode("utf-8").splitlines() == ["error \u2192 visible"]


def test_tool_loop_fail_closed_on_max_turns(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "note.txt").write_text("hello", encoding="utf-8")

    def chat(url: str, payload: dict, timeout: float) -> dict:
        return {
            "message": {
                "content": "",
                "tool_calls": [{"function": {"name": "Read", "arguments": {"path": "note.txt"}}}],
            }
        }

    with pytest.raises(oh.OllamaHarnessError, match="max-turn exhaustion"):
        oh.run_tool_loop("loop", route(root), oh.DEFAULT_ENDPOINT, 1, root, chat_func=chat)


def test_tool_loop_rejects_malformed_tool_arguments(tmp_path: Path):
    root = make_root(tmp_path)

    def chat(url: str, payload: dict, timeout: float) -> dict:
        return {"message": {"content": "", "tool_calls": [{"function": {"name": "Read", "arguments": "{"}}]}}

    with pytest.raises(oh.OllamaHarnessError, match="arguments string must be JSON"):
        oh.run_tool_loop("bad", route(root), oh.DEFAULT_ENDPOINT, 2, root, chat_func=chat)


def test_write_edit_and_bash_enter_guards_before_side_effects(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    target = root / "allowed.txt"
    result = oh.dispatch_tool_call(
        "Write",
        {"path": "allowed.txt", "content": "one"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )
    assert result == "wrote allowed.txt"
    assert target.read_text(encoding="utf-8") == "one"
    assert records

    target.write_text("one", encoding="utf-8")
    records.clear()
    oh.dispatch_tool_call(
        "Edit",
        {"path": "allowed.txt", "old_string": "one", "new_string": "two"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )
    assert target.read_text(encoding="utf-8") == "two"
    assert records

    events: list[str] = []

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        events.append("command")
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="ok", stderr="")

    def guard(path: Path, payload: dict, env: dict, timeout: float) -> oh.GuardExecutionResult:
        events.append("guard")
        return oh.GuardExecutionResult(returncode=0, stdout="{}")

    assert (
        oh.dispatch_tool_call(
            "Bash",
            {"command": "echo ok"},
            metadata(),
            root,
            guard_runner=guard,
            command_runner=command_runner,
        )
        == "ok"
    )
    assert events[:3] == ["guard", "guard", "guard"]
    assert events[-1] == "command"


def test_bridge_write_invokes_required_guard_sequence(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    oh.invoke_guard_adapter(
        "Write",
        {"path": "bridge/example-001.md", "content": "NEW\n"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )
    suffixes = [Path(path).as_posix().split("repo/")[-1] for path, _, _ in records]
    assert suffixes == [guard.as_posix() for guard in oh.BRIDGE_WRITE_GUARDS]


def test_bridge_edit_invokes_required_guard_sequence(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "bridge").mkdir()
    (root / "bridge" / "example-001.md").write_text("NEW\nold\n", encoding="utf-8")
    records: list[tuple[str, dict, dict]] = []
    oh.invoke_guard_adapter(
        "Edit",
        {"path": "bridge/example-001.md", "old_string": "old", "new_string": "new"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )
    suffixes = [Path(path).as_posix().split("repo/")[-1] for path, _, _ in records]
    assert suffixes == [guard.as_posix() for guard in oh.BRIDGE_EDIT_GUARDS]


def test_guard_denial_blocks_source_write_before_mutation(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    with pytest.raises(oh.OllamaHarnessError, match="guard denied"):
        oh.dispatch_tool_call(
            "Write",
            {"path": "scripts/outside.py", "content": "x = 1\n"},
            metadata(),
            root,
            guard_runner=deny_runner(records),
        )
    assert not (root / "scripts" / "outside.py").exists()
    assert records


def test_narrative_write_without_packet_blocks_before_mutation(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    with pytest.raises(oh.OllamaHarnessError, match="guard denied"):
        oh.dispatch_tool_call(
            "Write",
            {"path": ".claude/rules/new-rule.md", "content": "rule"},
            metadata(),
            root,
            guard_runner=deny_runner(records, "narrative-artifact-approval-gate.py"),
        )
    assert not (root / ".claude" / "rules" / "new-rule.md").exists()


def test_destructive_bash_is_denied_before_subprocess(tmp_path: Path):
    root = make_root(tmp_path)
    command_called = False

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        nonlocal command_called
        command_called = True
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    records: list[tuple[str, dict, dict]] = []
    with pytest.raises(oh.OllamaHarnessError, match="guard denied"):
        oh.dispatch_tool_call(
            "Bash",
            {"command": "Remove-Item -Recurse important"},
            metadata(),
            root,
            guard_runner=deny_runner(records, "destructive-gate.py"),
            command_runner=command_runner,
        )
    assert command_called is False


def test_formal_and_membase_bash_is_denied_before_subprocess(tmp_path: Path):
    root = make_root(tmp_path)
    command_called = False

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        nonlocal command_called
        command_called = True
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    records: list[tuple[str, dict, dict]] = []
    with pytest.raises(oh.OllamaHarnessError, match="guard denied"):
        oh.dispatch_tool_call(
            "Bash",
            {"command": "python -m groundtruth_kb deliberations add"},
            metadata(),
            root,
            guard_runner=deny_runner(records, "formal-artifact-approval-gate.py"),
            command_runner=command_runner,
        )
    assert command_called is False


def test_bridge_bash_file_write_is_denied_before_guards_or_subprocess(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "bridge").mkdir()
    records: list[tuple[str, dict, dict]] = []
    command_called = False

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        nonlocal command_called
        command_called = True
        (cwd / "bridge" / "bypass-001.md").write_text("GO\n", encoding="utf-8")
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="wrote", stderr="")

    with pytest.raises(oh.OllamaHarnessError, match="Bash bridge artifact mutation denied"):
        oh.dispatch_tool_call(
            "Bash",
            {"command": "Set-Content bridge/bypass-001.md 'GO'"},
            metadata(),
            root,
            guard_runner=allow_runner(records),
            command_runner=command_runner,
        )

    assert records == []
    assert command_called is False
    assert not (root / "bridge" / "bypass-001.md").exists()


def test_bridge_bash_index_write_is_denied_and_index_unchanged(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "bridge").mkdir()
    bridge_file = root / "bridge" / "fixture-001.md"
    bridge_file.write_text("NEW\n\nFixture proposal\n", encoding="utf-8")
    before = bridge_file.read_text(encoding="utf-8")
    records: list[tuple[str, dict, dict]] = []
    command_called = False

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        nonlocal command_called
        command_called = True
        bridge_file.write_text("bad\n", encoding="utf-8")
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="wrote", stderr="")

    with pytest.raises(oh.OllamaHarnessError, match="Bash bridge artifact mutation denied"):
        oh.dispatch_tool_call(
            "Bash",
            {"command": "echo bad > bridge/fixture-001.md"},
            metadata(),
            root,
            guard_runner=allow_runner(records),
            command_runner=command_runner,
        )

    assert records == []
    assert command_called is False
    assert bridge_file.read_text(encoding="utf-8") == before


def test_bridge_bash_read_reference_still_uses_bash_guards(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text("Document: fixture\n", encoding="utf-8")
    records: list[tuple[str, dict, dict]] = []

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="Document: fixture\n", stderr="")

    result = oh.dispatch_tool_call(
        "Bash",
        {"command": "Get-Content bridge/INDEX.md"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
        command_runner=command_runner,
    )

    suffixes = [Path(path).as_posix().split("repo/")[-1] for path, _, _ in records]
    assert result == "Document: fixture\n"
    assert suffixes == [guard.as_posix() for guard in oh.BASH_GUARDS]


@pytest.mark.parametrize(
    ("result", "message"),
    [
        (oh.GuardExecutionResult(returncode=0, stdout='{"decision":"ask","reason":"needs owner"}'), "guard denied"),
        (
            oh.GuardExecutionResult(returncode=0, stdout='{"hookSpecificOutput":{"permissionDecision":"checkpoint"}}'),
            "guard denied",
        ),
        (oh.GuardExecutionResult(returncode=0, stdout="{"), "malformed JSON"),
        (oh.GuardExecutionResult(returncode=1, stdout="{}"), "nonzero"),
        (oh.GuardExecutionResult(returncode=0, stdout="{}", timed_out=True), "timed out"),
    ],
)
def test_guard_failure_modes_raise_before_mutation(tmp_path: Path, result: oh.GuardExecutionResult, message: str):
    root = make_root(tmp_path)

    def runner(path: Path, payload: dict, env: dict, timeout: float) -> oh.GuardExecutionResult:
        return result

    with pytest.raises(oh.OllamaHarnessError, match=message):
        oh.dispatch_tool_call("Write", {"path": "out.txt", "content": "x"}, metadata(), root, guard_runner=runner)
    assert not (root / "out.txt").exists()


def test_missing_guard_raises(tmp_path: Path):
    root = make_root(tmp_path)
    (root / ".claude" / "hooks" / "credential-scan.py").unlink()
    with pytest.raises(oh.OllamaHarnessError, match="guard script is missing"):
        oh.dispatch_tool_call("Write", {"path": "out.txt", "content": "x"}, metadata(), root)


def test_root_boundary_rejects_traversal_and_absolute_outside_before_guard(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    with pytest.raises(oh.OllamaHarnessError, match="escapes project root"):
        oh.dispatch_tool_call(
            "Write",
            {"path": "../outside.txt", "content": "x"},
            metadata(),
            root,
            guard_runner=allow_runner(records),
        )
    with pytest.raises(oh.OllamaHarnessError, match="escapes project root"):
        oh.dispatch_tool_call(
            "Read",
            {"path": str(tmp_path / "outside.txt")},
            metadata(),
            root,
            guard_runner=allow_runner(records),
        )
    assert records == []


def test_root_boundary_rejects_escape_fixture_resolved_outside(tmp_path: Path):
    root = make_root(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(oh.OllamaHarnessError, match="escapes project root"):
        oh._ensure_under_root(root, outside / "file.txt", "escape/file.txt")


def test_valid_in_root_missing_path_reaches_guards_and_writes(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    oh.dispatch_tool_call(
        "Write",
        {"path": "new/child.txt", "content": "ok"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )
    assert (root / "new" / "child.txt").read_text(encoding="utf-8") == "ok"
    assert records


def test_author_metadata_env_is_passed_to_every_guard(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    oh.dispatch_tool_call(
        "Write", {"path": "out.txt", "content": "x"}, metadata(), root, guard_runner=allow_runner(records)
    )
    assert records
    for _, _, env in records:
        assert env["GTKB_AUTHOR_IDENTITY"] == "Ollama D"
        assert env["GTKB_AUTHOR_HARNESS_ID"] == "D"
        assert env["GTKB_AUTHOR_MODEL"] == FIXTURE_MODEL_ID
        assert env["GTKB_AUTHOR_MODEL_VERSION"] == FIXTURE_MODEL_VERSION
        assert "endpoint=http://localhost:11434" in env["GTKB_AUTHOR_MODEL_CONFIGURATION"]


def test_import_does_not_load_disallowed_frameworks():
    assert {"langchain", "langgraph", "crewai", "autogen"}.isdisjoint(sys.modules)


def test_help_command_exits_zero():
    completed = subprocess.run(
        [sys.executable, "scripts/ollama_harness.py", "--help"],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "--prompt" in completed.stdout
    assert "--endpoint" in completed.stdout


def test_dispatch_edit_raises_on_missing_file(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    with pytest.raises(oh.OllamaHarnessError, match="file not found"):
        oh.dispatch_tool_call(
            "Edit",
            {"path": "non_existent_file.txt", "old_string": "foo", "new_string": "bar"},
            metadata(),
            root,
            guard_runner=allow_runner(records),
        )
