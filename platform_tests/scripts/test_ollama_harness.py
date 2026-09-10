from __future__ import annotations

import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import ollama_harness as oh

FIXTURE_MODEL_ID = "fixture-model:fixture-version"
FIXTURE_MODEL_VERSION = oh.infer_model_version(FIXTURE_MODEL_ID)
READ_TRUNCATION_MARKER_RE = re.compile(
    r"\n\n\[Read truncated: returned characters \[(\d+), (\d+)\) of (\d+)\. "
    r"Continue with offset=(\d+)\.\]$"
)


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / oh.ROUTING_CONFIG_PATH.parent).mkdir(parents=True)
    (root / oh.ROUTING_CONFIG_PATH.parent / "settings.json").write_text('{"hooks": {}}', encoding="utf-8")
    (root / oh.ROUTING_CONFIG_PATH.parent / "hooks").mkdir(parents=True)
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
    for name in ("gtkb-bridge", "gtkb-proposal-review", "gtkb-verify"):
        relative = Path(".harness-baseline-configuration") / "skills" / name / "SKILL.md"
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((Path(__file__).resolve().parents[2] / relative).read_bytes())
    return root


def test_missing_own_native_settings_refuses_before_any_model_request(tmp_path):
    peer = tmp_path / ".claude/settings.json"
    peer.parent.mkdir()
    peer.write_text('{"hooks": {}}', encoding="utf-8")
    route = oh.ModelRoute("fixture", FIXTURE_MODEL_ID, FIXTURE_MODEL_VERSION, True, ("Read",))
    with pytest.raises(oh.OllamaHarnessError, match="native hook settings are missing"):
        oh.run_tool_loop(
            "Read the task",
            route,
            oh.DEFAULT_ENDPOINT,
            1,
            tmp_path,
            chat_func=lambda *_: pytest.fail("The missing settings must refuse before model execution"),
        )


@pytest.mark.parametrize("outcome", ["stop_refusal", "provider_failure"])
def test_ollama_native_stop_lifecycle_bounds_continuation_and_preserves_original_error(tmp_path, outcome):
    root = make_root(tmp_path)
    settings = root / oh.ROUTING_CONFIG_PATH.parent / "settings.json"
    settings.write_text(
        json.dumps(
            {
                "hooks": {
                    event: [{"hooks": [{"type": "command", "command": "qualification-only probe"}]}]
                    for event in ("SessionStart", "UserPromptSubmit", "Stop")
                }
            }
        ),
        encoding="utf-8",
    )
    route = oh.ModelRoute("fixture", FIXTURE_MODEL_ID, FIXTURE_MODEL_VERSION, True, ("Read",))
    observed = []
    calls = []

    def hook(_command, payload, _env, _timeout):
        observed.append((payload["hook_event_name"], payload["session_id"]))
        if payload["hook_event_name"] != "Stop":
            return oh.base.GuardExecutionResult(0, "{}")
        if outcome == "provider_failure":
            raise OSError("Stop transport failure must not replace the provider error")
        return oh.base.GuardExecutionResult(2, "", "Still incomplete")

    def chat(_endpoint, payload, _timeout):
        calls.append(payload)
        if outcome == "provider_failure":
            raise oh.OllamaHarnessError("original provider failure")
        if len(calls) > 1:
            assert "Still incomplete" in payload["messages"][-1]["content"]
        return {"message": {"content": "Final prose is not delivery evidence"}}

    match = "native Stop hook blocked completion" if outcome == "stop_refusal" else "original provider failure"
    with pytest.raises(oh.OllamaHarnessError, match=match):
        oh.run_tool_loop(
            "Complete the assigned task",
            route,
            oh.DEFAULT_ENDPOINT,
            oh.base.MAX_NATIVE_STOP_BLOCKS + 1,
            root,
            chat_func=chat,
            native_hook_runner=hook,
        )
    stops = oh.base.MAX_NATIVE_STOP_BLOCKS if outcome == "stop_refusal" else 1
    assert [event for event, _ in observed] == ["SessionStart", "UserPromptSubmit"] + ["Stop"] * stops
    assert len({native for _, native in observed}) == 1
    assert len(calls) == stops


def set_ollama_timeout(root: Path, timeout_seconds: float | str) -> None:
    config_path = root / oh.ROUTING_CONFIG_PATH
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace(
            '[routing.ollama]\ndefault_model = "fixture-full"',
            f'[routing.ollama]\ndefault_model = "fixture-full"\ntimeout_seconds = {timeout_seconds}',
        ),
        encoding="utf-8",
    )


def set_ollama_max_turns(root: Path, max_turns: int | float | str) -> None:
    config_path = root / oh.ROUTING_CONFIG_PATH
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace(
            '[routing.ollama]\ndefault_model = "fixture-full"',
            f'[routing.ollama]\ndefault_model = "fixture-full"\nmax_turns = {max_turns}',
        ),
        encoding="utf-8",
    )


def set_ollama_session_timeout(root: Path, session_timeout_seconds: float | str) -> None:
    config_path = root / oh.ROUTING_CONFIG_PATH
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace(
            '[routing.ollama]\ndefault_model = "fixture-full"',
            (f'[routing.ollama]\ndefault_model = "fixture-full"\nsession_timeout_seconds = {session_timeout_seconds}'),
        ),
        encoding="utf-8",
    )


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
    assert config.timeout_seconds is None
    assert config.session_timeout_seconds is None
    assert config.max_turns is None


def test_load_routing_config_parses_ollama_timeout_seconds(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_timeout(root, 42.5)

    config = oh.load_routing_config(root)

    assert config.timeout_seconds == pytest.approx(42.5)


def test_load_routing_config_rejects_non_positive_ollama_timeout(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_timeout(root, 0)

    with pytest.raises(oh.OllamaHarnessError, match="routing.ollama.timeout_seconds"):
        oh.load_routing_config(root)


def test_load_routing_config_parses_distinct_ollama_session_timeout(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_session_timeout(root, 3600)

    config = oh.load_routing_config(root)

    assert config.session_timeout_seconds == 3600


def test_load_routing_config_parses_ollama_max_turns(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_max_turns(root, 200)

    config = oh.load_routing_config(root)

    assert config.max_turns == 200


def test_load_routing_config_rejects_non_positive_ollama_max_turns(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_max_turns(root, 0)

    with pytest.raises(oh.OllamaHarnessError, match="routing.ollama.max_turns"):
        oh.load_routing_config(root)


def test_load_routing_config_rejects_fractional_ollama_max_turns(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_max_turns(root, 42.5)

    with pytest.raises(oh.OllamaHarnessError, match="routing.ollama.max_turns"):
        oh.load_routing_config(root)


def test_runtime_timeouts_use_routing_config_when_cli_uses_defaults(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_timeout(root, 42.5)
    raw_argv = ["-p", "hello"]
    args = oh.build_arg_parser().parse_args(raw_argv)

    operation_timeout, session_timeout = oh.resolve_runtime_timeouts(
        args,
        oh.load_routing_config(root),
        raw_argv,
    )

    assert operation_timeout == pytest.approx(42.5)
    assert session_timeout == pytest.approx(42.5 + oh.ROUTING_SESSION_TIMEOUT_GRACE_SECONDS)


def test_runtime_timeouts_preserve_explicit_cli_overrides(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_timeout(root, 42.5)
    raw_argv = ["-p", "hello", "--timeout=10.0", "--session-timeout", "20.0"]
    args = oh.build_arg_parser().parse_args(raw_argv)

    operation_timeout, session_timeout = oh.resolve_runtime_timeouts(
        args,
        oh.load_routing_config(root),
        raw_argv,
    )

    assert operation_timeout == pytest.approx(10.0)
    assert session_timeout == pytest.approx(20.0)


def test_runtime_timeouts_use_distinct_routing_session_timeout(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_timeout(root, 900)
    set_ollama_session_timeout(root, 3600)
    raw_argv = ["-p", "hello"]
    args = oh.build_arg_parser().parse_args(raw_argv)

    operation_timeout, session_timeout = oh.resolve_runtime_timeouts(
        args,
        oh.load_routing_config(root),
        raw_argv,
    )

    assert operation_timeout == 900
    assert session_timeout == 3600


def test_read_schema_and_short_file_output_remain_compatible(tmp_path: Path):
    root = make_root(tmp_path)
    content = "short file\n"
    (root / "short.txt").write_text(content, encoding="utf-8")

    read_schema = oh.build_tool_schemas(["Read"])[0]["function"]["parameters"]
    assert read_schema["properties"]["offset"] == {"type": "integer", "minimum": 0}
    assert oh._dispatch_read({"path": "short.txt"}, root) == content
    assert oh._dispatch_read({"path": "short.txt", "offset": len(content)}, root) == ""

    for invalid_offset in (-1, -1.0, "-1", 1.5, True):
        with pytest.raises(oh.OllamaHarnessError, match="offset must be a nonnegative integer"):
            oh._dispatch_read({"path": "short.txt", "offset": invalid_offset}, root)


def test_read_pagination_is_bounded_marked_and_lossless_for_unicode(tmp_path: Path):
    root = make_root(tmp_path)
    content = "segment-\u03b1-\U0001f642\n" * 1200
    (root / "long.txt").write_text(content, encoding="utf-8")

    offset = 0
    chunks: list[str] = []
    marker_count = 0
    while offset < len(content):
        result = oh._dispatch_read({"path": "long.txt", "offset": offset}, root)
        assert len(result) <= oh.MAX_TOOL_OUTPUT_CHARS
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


def test_read_marker_survives_small_and_oversized_page_requests(tmp_path: Path):
    root = make_root(tmp_path)
    content = "x" * 12_115
    (root / "h-report.txt").write_text(content, encoding="utf-8")

    small = oh._dispatch_read({"path": "h-report.txt", "max_chars": 1}, root)
    small_marker = READ_TRUNCATION_MARKER_RE.search(small)
    assert small_marker is not None
    assert small_marker.start() == 1
    assert tuple(int(value) for value in small_marker.groups()) == (0, 1, len(content), 1)

    oversized = oh._dispatch_read({"path": "h-report.txt", "max_chars": 1_000_000}, root)
    oversized_marker = READ_TRUNCATION_MARKER_RE.search(oversized)
    assert oversized_marker is not None
    assert len(oversized) <= oh.MAX_TOOL_OUTPUT_CHARS
    assert int(oversized_marker.group(2)) == oversized_marker.start()
    assert int(oversized_marker.group(3)) == len(content)

    large_offset = 1_000_000
    large_content = "x" * (large_offset + 12_115)
    large_offset_result = oh._bounded_read_result(large_content, large_offset, 1_000_000)
    large_offset_marker = READ_TRUNCATION_MARKER_RE.search(large_offset_result)
    assert large_offset_marker is not None
    assert len(large_offset_result) <= oh.MAX_TOOL_OUTPUT_CHARS
    assert int(large_offset_marker.group(1)) == large_offset
    assert int(large_offset_marker.group(2)) == large_offset + large_offset_marker.start()
    assert int(large_offset_marker.group(4)) == int(large_offset_marker.group(2))


def test_runtime_timeouts_preserve_default_session_when_timeout_override_is_explicit(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_timeout(root, 42.5)
    raw_argv = ["-p", "hello", "--timeout", "10.0"]
    args = oh.build_arg_parser().parse_args(raw_argv)

    operation_timeout, session_timeout = oh.resolve_runtime_timeouts(
        args,
        oh.load_routing_config(root),
        raw_argv,
    )

    assert operation_timeout == pytest.approx(10.0)
    assert session_timeout == pytest.approx(oh.DEFAULT_SESSION_TIMEOUT_SECONDS)


def test_runtime_max_turns_use_routing_config_when_cli_uses_default(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_max_turns(root, 200)
    raw_argv = ["-p", "hello"]
    args = oh.build_arg_parser().parse_args(raw_argv)

    max_turns = oh.resolve_runtime_max_turns(args, oh.load_routing_config(root), raw_argv)

    assert max_turns == 200


def test_runtime_max_turns_preserve_explicit_cli_override(tmp_path: Path):
    root = make_root(tmp_path)
    set_ollama_max_turns(root, 200)
    raw_argv = ["-p", "hello", "--max-turns", "5"]
    args = oh.build_arg_parser().parse_args(raw_argv)

    max_turns = oh.resolve_runtime_max_turns(args, oh.load_routing_config(root), raw_argv)

    assert max_turns == 5


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


def test_main_threads_skill_and_preserves_generous_runtime_limits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_root(tmp_path)
    set_ollama_timeout(root, 900)
    set_ollama_session_timeout(root, 3600)
    set_ollama_max_turns(root, 600)
    captured: dict[str, object] = {}

    def fake_run_tool_loop(prompt, model_route, endpoint, max_turns, project_root, **kwargs):
        captured.update(
            prompt=prompt,
            model_route=model_route,
            endpoint=endpoint,
            max_turns=max_turns,
            project_root=project_root,
            **kwargs,
        )
        return "done"

    monkeypatch.chdir(root)
    monkeypatch.setattr(oh, "call_ollama_tags", lambda _endpoint, _timeout: [FIXTURE_MODEL_ID])
    monkeypatch.setattr(oh, "run_tool_loop", fake_run_tool_loop)

    assert oh.main(["-p", "review", "--skill", "bridge-review"]) == 0
    assert capsys.readouterr().out.strip() == "done"
    assert captured["skill"] == "bridge-review"
    assert captured["max_turns"] == 600
    assert captured["timeout"] == 900
    assert captured["session_timeout"] == 3600


def test_tool_schemas_expose_only_canonical_tools():
    schemas = oh.build_tool_schemas(["Read", "Write", "Edit", "Grep", "Glob", "Bash"])
    names = [schema["function"]["name"] for schema in schemas]
    assert names == ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    with pytest.raises(oh.OllamaHarnessError):
        oh.build_tool_schemas(["Read", "Delete"])


def test_glob_skips_root_escaping_resolved_matches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    (root / "inside.txt").write_text("ok", encoding="utf-8")
    (root / "escape.txt").write_text("outside by resolution", encoding="utf-8")

    def fake_relative(project_root: Path, path: Path) -> str:
        if path.name == "escape.txt":
            raise ValueError("escaped root")
        return path.resolve().relative_to(project_root.resolve()).as_posix()

    monkeypatch.setattr(oh, "_relative_path", fake_relative)

    result = oh.dispatch_tool_call("Glob", {"pattern": "*.txt"}, metadata(), root)

    assert "inside.txt" in result.splitlines()
    assert "escape.txt" not in result


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
    assert {tool["function"]["name"] for tool in calls[0][1]["tools"]} == (oh.CANONICAL_TOOLS)


def test_tool_loop_keeps_read_continuation_marker_model_visible(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "long.txt").write_text("x" * 12_115, encoding="utf-8")
    calls: list[tuple[str, dict]] = []

    def chat(url: str, payload: dict, timeout: float) -> dict:
        calls.append((url, payload))
        if len(calls) == 1:
            return {
                "message": {
                    "content": "",
                    "tool_calls": [{"id": "read_1", "function": {"name": "Read", "arguments": {"path": "long.txt"}}}],
                }
            }
        tool_result = payload["messages"][-1]
        assert tool_result["role"] == "tool"
        assert len(tool_result["content"]) <= oh.MAX_TOOL_OUTPUT_CHARS
        assert READ_TRUNCATION_MARKER_RE.search(tool_result["content"]) is not None
        return {"message": {"content": "marker observed"}}

    result = oh.run_tool_loop("read the report", route(root), "http://ollama.test", 2, root, chat_func=chat)

    assert result == "marker observed"


def test_tool_loop_emits_allowlisted_turn_metadata_to_telemetry(tmp_path: Path):
    root = make_root(tmp_path)

    class Recorder:
        def __init__(self) -> None:
            self.turns: list[tuple[int, list[str]]] = []
            self.stop_reasons: list[str] = []

        def record_turn(self, index: int, tool_names: list[str], **_kwargs) -> None:
            self.turns.append((index, tool_names))

        def finish(self, *, stop_reason: str) -> None:
            self.stop_reasons.append(stop_reason)

    recorder = Recorder()

    def chat(_url: str, _payload: dict, _timeout: float) -> dict:
        return {"message": {"content": "done"}, "prompt_eval_count": 0, "eval_count": 0}

    assert (
        oh.run_tool_loop("hello", route(root), "http://ollama.test", 1, root, chat_func=chat, telemetry=recorder)
        == "done"
    )
    assert recorder.turns == [(1, [])]
    assert recorder.stop_reasons == ["final_response"]


def test_bridge_review_system_prompt_loads_current_canonical_skills(tmp_path: Path):
    root = make_root(tmp_path)
    calls: list[dict] = []
    prompt = oh.build_system_prompt("bridge-review", root)

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
    assert "gt context work-item" in system_message["content"]
    assert "gt bridge deliver" in system_message["content"]
    assert "The supplied init marker" in system_message["content"]
    assert "PublishBridgeVerdict" not in system_message["content"]


def test_system_prompt_is_only_for_lo_bridge_skills(tmp_path: Path):
    root = make_root(tmp_path)

    assert oh.build_system_prompt("bridge-review", root) is not None
    assert oh.build_system_prompt("verification", root) is not None
    assert oh.build_system_prompt("implementation", root) is None
    assert oh.build_system_prompt(None, root) is None


def test_prompt_requires_native_readback_and_complete_project_finalization(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = oh.build_system_prompt("bridge-review", root)
    assert "Read back the result with `gt bridge show" in prompt
    assert "gt projects commit" in prompt
    assert "The CLI prepares the reviewed cohort, commits and confirms" in prompt
    assert "Project commit establishes activation" in prompt
    assert "finalization helper" not in prompt


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


@pytest.mark.parametrize("content", ["", "   \r\n\t"])
def test_tool_loop_rejects_blank_final_text(tmp_path: Path, content: str):
    root = make_root(tmp_path)

    def chat(url: str, payload: dict, timeout: float) -> dict:
        return {"message": {"content": content}}

    with pytest.raises(oh.OllamaHarnessError, match="nonblank text content"):
        oh.run_tool_loop("return blank", route(root), oh.DEFAULT_ENDPOINT, 1, root, chat_func=chat)


def test_tool_loop_stops_repeated_no_progress_calls(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "note.txt").write_text("hello", encoding="utf-8")
    calls: list[dict] = []

    def chat(url: str, payload: dict, timeout: float) -> dict:
        calls.append(payload)
        return {
            "message": {
                "content": "",
                "tool_calls": [{"id": "c1", "function": {"name": "Read", "arguments": {"path": "note.txt"}}}],
            }
        }

    with pytest.raises(oh.OllamaHarnessError, match="repeated no-progress tool loop"):
        oh.run_tool_loop("loop", route(root), oh.DEFAULT_ENDPOINT, 20, root, chat_func=chat)

    assert len(calls) == oh.MAX_REPEATED_TOOL_SIGNATURE_TURNS + 1


def test_tool_loop_enforces_session_timeout_between_turns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    (root / "note.txt").write_text("hello", encoding="utf-8")
    ticks = [100.0, 100.0, 101.5]

    def fake_monotonic() -> float:
        return ticks.pop(0) if ticks else 101.5

    def chat(url: str, payload: dict, timeout: float) -> dict:
        return {
            "message": {
                "content": "",
                "tool_calls": [{"function": {"name": "Read", "arguments": {"path": "note.txt"}}}],
            }
        }

    monkeypatch.setattr(oh.time, "monotonic", fake_monotonic)

    with pytest.raises(oh.OllamaHarnessError, match="session timeout exceeded"):
        oh.run_tool_loop(
            "loop",
            route(root),
            oh.DEFAULT_ENDPOINT,
            3,
            root,
            chat_func=chat,
            timeout=10.0,
            session_timeout=1.0,
        )


def test_tool_loop_caps_bash_timeout_to_remaining_session_budget(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    ticks = [100.0, 101.0, 102.0, 103.0]
    observed_timeouts: list[float] = []

    def fake_monotonic() -> float:
        return ticks.pop(0) if ticks else 103.0

    def chat(url: str, payload: dict, timeout: float) -> dict:
        if not any(message["role"] == "assistant" for message in payload["messages"]):
            return {
                "message": {
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "Bash",
                                "arguments": {"command": "echo ok", "timeout_seconds": 99},
                            }
                        }
                    ],
                }
            }
        return {"message": {"content": "done"}}

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        observed_timeouts.append(timeout)
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(oh.time, "monotonic", fake_monotonic)

    assert (
        oh.run_tool_loop(
            "run",
            route(root),
            oh.DEFAULT_ENDPOINT,
            3,
            root,
            chat_func=chat,
            command_runner=command_runner,
            timeout=20.0,
            session_timeout=5.0,
        )
        == "done"
    )
    assert observed_timeouts == [3.0]


def test_tool_loop_recovers_from_malformed_tool_arguments(tmp_path: Path):
    root = make_root(tmp_path)
    calls: list[dict] = []

    def chat(url: str, payload: dict, timeout: float) -> dict:
        calls.append(payload)
        if len(calls) == 1:
            return {
                "message": {
                    "content": "",
                    "tool_calls": [{"id": "bad_1", "function": {"name": "Read", "arguments": "{"}}],
                }
            }
        tool_result = payload["messages"][-1]
        assert tool_result["role"] == "tool"
        assert tool_result["name"] == "Read"
        assert tool_result["tool_call_id"] == "bad_1"
        assert tool_result["content"].startswith("ERROR:")
        assert "arguments string must be JSON" in tool_result["content"]
        return {"message": {"content": "recovered"}}

    assert oh.run_tool_loop("bad", route(root), oh.DEFAULT_ENDPOINT, 2, root, chat_func=chat) == "recovered"
    assert len(calls) == 2


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
    (root / oh.ROUTING_CONFIG_PATH.parent / "hooks" / "credential-scan.py").unlink()
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


# --- WI-4817: bounded transient-failure retry for call_ollama_chat ---


class _RetryResponse:
    def __init__(self, body: str) -> None:
        self._body = body

    def __enter__(self) -> _RetryResponse:
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def read(self) -> bytes:
        return self._body.encode("utf-8")


def _ollama_http_error(code: int) -> oh.urllib.error.HTTPError:
    return oh.urllib.error.HTTPError("http://ollama.test/api/chat", code, "err", None, None)


def _patch_ollama_urlopen(monkeypatch: pytest.MonkeyPatch, behaviors: list, calls: list) -> None:
    def fake_urlopen(request, timeout: float):
        calls.append(request.full_url)
        behavior = behaviors[min(len(calls) - 1, len(behaviors) - 1)]
        if isinstance(behavior, Exception):
            raise behavior
        return _RetryResponse(behavior)

    monkeypatch.setattr(oh.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(oh.time, "sleep", lambda _seconds: None)


def test_wi4817_ollama_retry_then_success(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    body = json.dumps({"message": {"content": "ok"}})
    _patch_ollama_urlopen(monkeypatch, [_ollama_http_error(502), body], calls)
    result = oh.call_ollama_chat("http://ollama.test", {"model": "m"})
    assert result == {"message": {"content": "ok"}}
    assert len(calls) == 2


def test_wi4817_ollama_bounded_exhaustion(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    behaviors = [_ollama_http_error(503)] * (oh.CHAT_MAX_ATTEMPTS + 1)
    _patch_ollama_urlopen(monkeypatch, behaviors, calls)
    with pytest.raises(oh.OllamaHarnessError, match="HTTP 503"):
        oh.call_ollama_chat("http://ollama.test", {"model": "m"})
    assert len(calls) == oh.CHAT_MAX_ATTEMPTS


def test_wi4933_ollama_bare_timeout_is_classified(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    behaviors = [TimeoutError("timed out")] * (oh.CHAT_MAX_ATTEMPTS + 1)
    _patch_ollama_urlopen(monkeypatch, behaviors, calls)
    with pytest.raises(oh.OllamaHarnessError, match="timed out"):
        oh.call_ollama_chat("http://ollama.test", {"model": "m"})
    assert len(calls) == oh.CHAT_MAX_ATTEMPTS


def test_wi4817_ollama_fail_fast_on_non_transient(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    _patch_ollama_urlopen(monkeypatch, [_ollama_http_error(401)], calls)
    with pytest.raises(oh.OllamaHarnessError, match="HTTP 401"):
        oh.call_ollama_chat("http://ollama.test", {"model": "m"})
    assert len(calls) == 1


def test_wi4817_ollama_happy_path_single_attempt(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    _patch_ollama_urlopen(monkeypatch, [json.dumps({"ok": True})], calls)
    result = oh.call_ollama_chat("http://ollama.test", {"model": "m"})
    assert result == {"ok": True}
    assert len(calls) == 1
