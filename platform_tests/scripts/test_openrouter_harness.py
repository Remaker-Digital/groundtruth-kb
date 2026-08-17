from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import _env as env_loader
from scripts import openrouter_harness as orh

FIXTURE_MODEL_ID = "deepseek/fixture-model"
FIXTURE_MODEL_VERSION = orh.infer_model_version(FIXTURE_MODEL_ID)


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / ".claude" / "hooks").mkdir(parents=True)
    (root / "scripts").mkdir()
    for guard in {*orh.BRIDGE_WRITE_GUARDS, *orh.BRIDGE_EDIT_GUARDS, *orh.WRITE_EDIT_GUARDS, *orh.BASH_GUARDS}:
        path = root / guard
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("print('{}')\n", encoding="utf-8")
    (root / orh.ROUTING_CONFIG_PATH).write_text(
        """
schema_version = 1

[models.fixture-full]
model_id = "deepseek/fixture-model"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[routing.openrouter]
default_model = "fixture-full"
timeout_seconds = 900
session_timeout_seconds = 3600
max_turns = 600
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return root


def route(root: Path) -> orh.ModelRoute:
    return orh.resolve_model(orh.load_routing_config(root), None)


def metadata() -> orh.ModelMetadata:
    return orh.ModelMetadata(
        model_id=FIXTURE_MODEL_ID,
        model_version=FIXTURE_MODEL_VERSION,
        endpoint="https://openrouter.test",
        route_key="fixture-full",
    )


def allow_runner(records: list[tuple[str, dict, dict]]):
    def run_guard(path: Path, payload: dict, env: dict, timeout: float) -> orh.GuardExecutionResult:
        records.append((path.as_posix(), payload, dict(env)))
        return orh.GuardExecutionResult(returncode=0, stdout="{}")

    return run_guard


def test_load_routing_config_parses_openrouter_model(tmp_path: Path):
    root = make_root(tmp_path)
    selected = route(root)

    assert selected.key == "fixture-full"
    assert selected.model_id == FIXTURE_MODEL_ID
    assert selected.model_version == FIXTURE_MODEL_VERSION
    assert selected.allowed_tools == ("Read", "Write", "Edit", "Grep", "Glob", "Bash")
    assert selected.omit_payload_model is False
    config = orh.load_routing_config(root)
    assert (config.timeout_seconds, config.session_timeout_seconds, config.max_turns) == (900, 3600, 600)


def test_load_routing_config_parses_openrouter_cloud_default_omit_model(tmp_path: Path):
    root = make_root(tmp_path)
    (root / orh.ROUTING_CONFIG_PATH).write_text(
        """
schema_version = 1

[models.openrouter-cloud-default]
model_id = "moonshotai/kimi-k2.7-code"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
omit_payload_model = true

[routing.openrouter]
default_model = "openrouter-cloud-default"

[routing.openrouter.skills]
implementation = "openrouter-cloud-default"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    selected = orh.resolve_model(orh.load_routing_config(root), None, skill="implementation")

    assert selected.key == "openrouter-cloud-default"
    assert selected.model_id == "moonshotai/kimi-k2.7-code"
    assert selected.omit_payload_model is True


def test_glob_skips_root_escaping_resolved_matches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    (root / "inside.txt").write_text("ok", encoding="utf-8")
    (root / "escape.txt").write_text("outside by resolution", encoding="utf-8")

    def fake_relative(project_root: Path, path: Path) -> str:
        if path.name == "escape.txt":
            raise ValueError("escaped root")
        return path.resolve().relative_to(project_root.resolve()).as_posix()

    monkeypatch.setattr(orh, "_relative_path", fake_relative)

    result = orh.dispatch_tool_call("Glob", {"pattern": "*.txt"}, metadata(), root)

    assert "inside.txt" in result.splitlines()
    assert "escape.txt" not in result


def test_env_local_loader_falls_back_from_in_root_release_worktree(tmp_path: Path):
    primary = tmp_path / "GT-KB"
    worktree = primary / ".tmp" / "formal-release"
    worktree.mkdir(parents=True)
    (primary / "groundtruth.toml").write_text("[groundtruth]\n", encoding="utf-8")
    primary_env = primary / ".env.local"
    primary_env.write_text("OPENROUTER_API_KEY=test-key\n", encoding="utf-8")

    assert env_loader._default_env_local_path(worktree) == primary_env.resolve()


def test_main_classifies_missing_openrouter_key_as_configuration_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = make_root(tmp_path)
    monkeypatch.chdir(root)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(env_loader, "load_env_local", lambda: {})

    assert orh.main(["-p", "hello"]) == 1

    captured = capsys.readouterr()
    assert "OPENROUTER_API_KEY environment variable is not set" in captured.err


def test_main_loads_env_local_key_before_live_dispatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = make_root(tmp_path)
    config = orh.load_routing_config(root)
    monkeypatch.chdir(root)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    def fake_load_env_local() -> dict[str, str]:
        monkeypatch.setenv("OPENROUTER_API_KEY", "env-file-fixture-key")
        return {"OPENROUTER_API_KEY": "env-file-fixture-key"}

    def fake_run_tool_loop(
        prompt: str,
        model_route: orh.ModelRoute,
        endpoint: str,
        api_key: str,
        max_turns: int,
        project_root: Path,
        **kwargs,
    ) -> str:
        assert prompt == "hello"
        assert api_key == "env-file-fixture-key"
        assert project_root == root.resolve()
        assert max_turns == 600
        assert kwargs["skill"] == "bridge-review"
        assert kwargs["timeout"] == 900
        assert kwargs["session_timeout"] == 3600
        return "done"

    monkeypatch.setattr(env_loader, "load_env_local", fake_load_env_local)
    monkeypatch.setattr(orh, "load_routing_config", lambda _project_root: config)
    monkeypatch.setattr(orh, "run_tool_loop", fake_run_tool_loop)

    assert orh.main(["-p", "hello", "--skill", "bridge-review"]) == 0
    assert capsys.readouterr().out.strip() == "done"


def test_openrouter_reconfigures_output_streams_for_unicode_verdicts():
    class Stream:
        def __init__(self) -> None:
            self.calls: list[dict[str, str]] = []

        def reconfigure(self, **kwargs: str) -> None:
            self.calls.append(kwargs)

    stdout = Stream()
    stderr = Stream()

    orh.ensure_utf8_output_streams(stdout, stderr)
    orh.ensure_utf8_output_streams(object(), object())

    assert stdout.calls == [{"encoding": "utf-8", "errors": "backslashreplace"}]
    assert stderr.calls == [{"encoding": "utf-8", "errors": "backslashreplace"}]


def test_openrouter_bridge_review_inherits_shared_completion_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = make_root(tmp_path)
    selected = route(root)
    captured: dict[str, object] = {}

    def fake_base_loop(_prompt, _route, _endpoint, _api_key, _max_turns, _root, profile, **kwargs):
        captured["profile"] = profile
        captured["skill"] = kwargs["skill"]
        return "done"

    monkeypatch.setattr(orh.base, "run_tool_loop", fake_base_loop)

    assert (
        orh.run_tool_loop(
            "review",
            selected,
            "https://openrouter.test",
            "key",
            1,
            root,
            skill="bridge-review",
        )
        == "done"
    )
    assert captured["profile"] is orh._OPENROUTER_PROFILE
    assert captured["profile"].publish_bridge_verdict_tool is True
    assert captured["skill"] == "bridge-review"


def test_bridge_review_prompt_uses_no_index_bridge_instructions(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = orh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    assert "bridge/INDEX.md" not in prompt
    assert "full\nversioned bridge-file chain" in prompt
    assert "gt bridge dispatch config" in prompt
    assert "gt bridge dispatch status" in prompt
    assert "gt bridge dispatch\nhealth" in prompt
    assert "latest NEW, REVISED,\nor NO-ACTION" in prompt
    assert "governance-compliant verdict through review_no_action" in prompt
    assert "Do not encode an\nexclusive corrected-verdict status set" in prompt


def test_bridge_review_prompt_states_canonical_role_source_positively(tmp_path: Path):
    """The OpenRouter system prompt names the canonical role reader positively
    and no longer carries probative language naming the obsolete
    harness-local operating-role.md surface (WI-6017)."""
    root = make_root(tmp_path)
    prompt = orh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    assert "harness-state/harness-registry.json through the canonical role reader" in prompt
    assert "operating-role.md" not in prompt


def test_bridge_review_prompt_requires_governed_verdict_publication(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = orh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    claim_index = prompt.index("python scripts\\bridge_claim_cli.py claim <document-slug>")
    publisher_index = prompt.index("Publish numbered GO, NO-GO, and VERIFIED artifacts")
    bridge_workflow_index = prompt.index("Use the GT-KB file bridge")
    assert claim_index < publisher_index < bridge_workflow_index
    assert "only through\nPublishBridgeVerdict" in prompt
    assert "Never use raw Write, Edit, or Bash for a numbered bridge verdict" in prompt


def test_bridge_review_prompt_requires_atomic_verified_finalization(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = orh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    assert "include_paths" in prompt
    assert "commit_message" in prompt
    assert "performs atomic VERIFIED\nfinalization" in prompt
    assert "fail closed" in prompt
    assert "terminal\nVERIFIED file without its commit" in prompt


def test_publish_bridge_verdict_is_exposed_only_for_lo_skills(tmp_path: Path):
    root = make_root(tmp_path)
    selected = route(root)

    assert orh._OPENROUTER_PROFILE.publish_bridge_verdict_tool is True
    for skill in ("bridge-review", "verification"):
        allowed = orh.base.allowed_tools_for_skill(
            selected.allowed_tools,
            skill,
            publish_bridge_verdict_tool=orh._OPENROUTER_PROFILE.publish_bridge_verdict_tool,
        )
        assert allowed[-1] == orh.base.PUBLISH_BRIDGE_VERDICT_TOOL
    for skill in ("implementation", None):
        allowed = orh.base.allowed_tools_for_skill(
            selected.allowed_tools,
            skill,
            publish_bridge_verdict_tool=orh._OPENROUTER_PROFILE.publish_bridge_verdict_tool,
        )
        assert orh.base.PUBLISH_BRIDGE_VERDICT_TOOL not in allowed

    schema = orh.build_tool_schemas([orh.base.PUBLISH_BRIDGE_VERDICT_TOOL])[0]["function"]
    properties = schema["parameters"]["properties"]
    assert set(schema["parameters"]["required"]) == {"slug", "verdict", "content"}
    assert not {"path", "file_path", "version"} & properties.keys()


def test_run_tool_loop_threads_skill_to_shared_tool_exposure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    payloads: list[dict] = []

    class Published:
        def to_dict(self) -> dict[str, object]:
            return {"verdict_path": "bridge/example-002.md"}

    monkeypatch.setattr(
        orh.base,
        "_load_provider_verdict_publisher",
        lambda _root: lambda *_args, **_kwargs: Published(),
    )
    for key in orh.base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-F-exposure")

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        payloads.append(payload)
        if len(payloads) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "publish_1",
                                    "function": {
                                        "name": orh.base.PUBLISH_BRIDGE_VERDICT_TOOL,
                                        "arguments": {"slug": "example", "verdict": "GO", "content": "GO\n"},
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        return {"choices": [{"message": {"content": "done"}}]}

    orh.run_tool_loop(
        "review",
        route(root),
        "https://openrouter.test",
        "key",
        2,
        root,
        skill="bridge-review",
        chat_func=chat,
    )

    names = {tool["function"]["name"] for tool in payloads[0]["tools"]}
    assert orh.base.PUBLISH_BRIDGE_VERDICT_TOOL in names


def test_run_tool_loop_inherits_publisher_only_recovery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = make_root(tmp_path)
    payloads: list[dict] = []

    class Published:
        def to_dict(self) -> dict[str, object]:
            return {"verdict_path": "bridge/example-002.md"}

    monkeypatch.setattr(
        orh.base,
        "_load_provider_verdict_publisher",
        lambda _root: lambda *_args, **_kwargs: Published(),
    )
    for key in orh.base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-F-completion")

    def chat(_endpoint: str, _api_key: str, payload: dict, _timeout: float) -> dict:
        payloads.append(payload)
        if len(payloads) == 1:
            return {"choices": [{"message": {"content": "ready but unpublished"}}]}
        if len(payloads) == 2:
            assert [tool["function"]["name"] for tool in payload["tools"]] == [orh.base.PUBLISH_BRIDGE_VERDICT_TOOL]
            return {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "publish_f",
                                    "function": {
                                        "name": orh.base.PUBLISH_BRIDGE_VERDICT_TOOL,
                                        "arguments": {"slug": "example", "verdict": "GO", "content": "GO\n"},
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        return {"choices": [{"message": {"content": "published"}}]}

    assert (
        orh.run_tool_loop(
            "review",
            route(root),
            "https://openrouter.test",
            "key",
            3,
            root,
            skill="bridge-review",
            chat_func=chat,
        )
        == "published"
    )


def test_dispatch_publish_bridge_verdict_uses_openrouter_runtime_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import gtkb_bridge_writer as writer

    root = make_root(tmp_path)
    captured: dict[str, object] = {}

    class Published:
        def to_dict(self) -> dict[str, object]:
            return {"verdict_path": "bridge/example-002.md"}

    def fake_publish(slug, verdict, content, project_root, **kwargs):
        captured.update(slug=slug, verdict=verdict, content=content, project_root=project_root, **kwargs)
        return Published()

    monkeypatch.setattr(writer, "publish_lo_verdict", fake_publish)
    for key in orh.base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-F-parity")

    result = orh.dispatch_tool_call(
        orh.base.PUBLISH_BRIDGE_VERDICT_TOOL,
        {"slug": "example", "verdict": "GO", "content": "GO\n"},
        metadata(),
        root,
        skill="bridge-review",
    )

    assert orh.json.loads(result)["verdict_path"] == "bridge/example-002.md"
    assert captured["session_id"] == "dispatch-F-parity"
    assert captured["harness_name"] == "openrouter"
    author_metadata = captured["author_metadata"]
    assert isinstance(author_metadata, dict)
    assert author_metadata["author_harness_id"] == "F"
    assert author_metadata["author_model"] == FIXTURE_MODEL_ID


def test_dispatch_publish_bridge_verdict_fails_closed_without_lo_skill_or_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = make_root(tmp_path)
    arguments = {"slug": "example", "verdict": "GO", "content": "GO\n"}
    for key in orh.base.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(orh.OpenRouterHarnessError, match="bridge-review/verification"):
        orh.dispatch_tool_call(
            orh.base.PUBLISH_BRIDGE_VERDICT_TOOL,
            arguments,
            metadata(),
            root,
            skill="implementation",
        )
    with pytest.raises(orh.OpenRouterHarnessError, match="concrete dispatcher session id"):
        orh.dispatch_tool_call(
            orh.base.PUBLISH_BRIDGE_VERDICT_TOOL,
            arguments,
            metadata(),
            root,
            skill="bridge-review",
        )


def test_bridge_write_invokes_required_guard_sequence(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    orh.invoke_guard_adapter(
        "Write",
        {"path": "bridge/example-001.md", "content": "NEW\n"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )

    suffixes = [Path(path).as_posix().split("repo/")[-1] for path, _, _ in records]
    assert suffixes == [guard.as_posix() for guard in orh.BRIDGE_WRITE_GUARDS]


def test_bridge_edit_invokes_required_guard_sequence(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "bridge").mkdir()
    (root / "bridge" / "example-001.md").write_text("NEW\nold\n", encoding="utf-8")
    records: list[tuple[str, dict, dict]] = []
    orh.invoke_guard_adapter(
        "Edit",
        {"path": "bridge/example-001.md", "old_string": "old", "new_string": "new"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )

    suffixes = [Path(path).as_posix().split("repo/")[-1] for path, _, _ in records]
    assert suffixes == [guard.as_posix() for guard in orh.BRIDGE_EDIT_GUARDS]


def test_author_metadata_env_is_passed_to_bridge_write_guard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run")
    records: list[tuple[str, dict, dict]] = []

    orh.invoke_guard_adapter(
        "Write",
        {"path": "bridge/example-001.md", "content": "NEW\n"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
    )

    env = records[0][2]
    payload = records[0][1]
    assert env["GTKB_AUTHOR_IDENTITY"] == "OpenRouter F"
    assert env["GTKB_AUTHOR_HARNESS_ID"] == "F"
    assert env["GTKB_AUTHOR_MODEL"] == FIXTURE_MODEL_ID
    assert env["GTKB_AUTHOR_MODEL_VERSION"] == FIXTURE_MODEL_VERSION
    assert payload["session_id"] == "dispatch-run"


def test_tool_loop_uses_response_model_metadata_for_bridge_write(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "bridge").mkdir()
    served_model = "moonshotai/kimi-k2.7-code"
    records: list[tuple[str, dict, dict]] = []
    payloads: list[dict] = []

    stale_content = "\n".join(
        [
            "NEW",
            "author_model: deepseek/fixture-model",
            "author_model_version: fixture-model",
            "author_model_configuration: stale",
            "",
            "body",
            "",
        ]
    )

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        payloads.append(payload)
        if len(payloads) == 1:
            return {
                "model": served_model,
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_write",
                                    "function": {
                                        "name": "Write",
                                        "arguments": orh.json.dumps(
                                            {"path": "bridge/example-001.md", "content": stale_content}
                                        ),
                                    },
                                }
                            ],
                        }
                    }
                ],
            }
        return {"model": served_model, "choices": [{"message": {"content": "done"}}]}

    assert (
        orh.run_tool_loop(
            "write",
            route(root),
            "https://openrouter.test",
            "key",
            3,
            root,
            chat_func=chat,
            guard_runner=allow_runner(records),
        )
        == "done"
    )

    written = (root / "bridge" / "example-001.md").read_text(encoding="utf-8")
    assert "author_model: moonshotai/kimi-k2.7-code" in written
    assert "author_model_version: kimi-k2.7-code" in written
    assert "model_source=response.model" in written
    assert f"requested_model={FIXTURE_MODEL_ID}" in written
    assert "account_override=true" in written
    assert payloads[0]["model"] == FIXTURE_MODEL_ID

    guard_env = records[0][2]
    assert guard_env["GTKB_AUTHOR_MODEL"] == served_model
    assert guard_env["GTKB_AUTHOR_MODEL_VERSION"] == "kimi-k2.7-code"
    assert "model_source=response.model" in guard_env["GTKB_AUTHOR_MODEL_CONFIGURATION"]
    assert f"requested_model={FIXTURE_MODEL_ID}" in guard_env["GTKB_AUTHOR_MODEL_CONFIGURATION"]


def test_openrouter_wrapper_forwards_telemetry_observer(tmp_path: Path) -> None:
    root = make_root(tmp_path)

    class Recorder:
        def __init__(self) -> None:
            self.turns: list[tuple[int, list[str]]] = []
            self.stop_reasons: list[str] = []

        def record_turn(self, index: int, tool_names: list[str], **_kwargs) -> None:
            self.turns.append((index, tool_names))

        def set_model(self, _model_id: str, _model_version: str) -> None:
            return None

        def finish(self, *, stop_reason: str) -> None:
            self.stop_reasons.append(stop_reason)

    recorder = Recorder()

    def chat(_endpoint: str, _api_key: str, _payload: dict, _timeout: float) -> dict:
        return {"choices": [{"message": {"content": "done"}}], "usage": {"total_tokens": 0}}

    assert (
        orh.run_tool_loop(
            "hello",
            route(root),
            "https://openrouter.test",
            "key",
            1,
            root,
            chat_func=chat,
            telemetry=recorder,
        )
        == "done"
    )
    assert recorder.turns == [(1, [])]
    assert recorder.stop_reasons == ["final_response"]


def test_response_model_metadata_falls_back_to_routing_metadata_when_missing():
    original = metadata()

    updated = orh._metadata_from_response(original, {"choices": [{"message": {"content": "done"}}]})

    assert updated == original


def test_bridge_metadata_normalization_handles_blank_and_non_target_content(tmp_path: Path):
    root = make_root(tmp_path)
    (root / "bridge").mkdir()

    assert orh._content_status_token("") == ""
    assert orh._content_status_token(" \n\t\n") == ""
    assert orh._normalize_bridge_author_model_metadata("", metadata(), root, root / "bridge" / "blank.md") == ""
    assert (
        orh._normalize_bridge_author_model_metadata(" \n\t\n", metadata(), root, root / "bridge" / "blank.md")
        == " \n\t\n"
    )

    non_bridge_content = "NEW\nauthor_model: stale\n"
    assert (
        orh._normalize_bridge_author_model_metadata(non_bridge_content, metadata(), root, root / "notes.md")
        == non_bridge_content
    )

    non_status_content = "not-a-status\nauthor_model: stale\n"
    assert (
        orh._normalize_bridge_author_model_metadata(
            non_status_content,
            metadata(),
            root,
            root / "bridge" / "example-001.md",
        )
        == non_status_content
    )


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

    with pytest.raises(orh.OpenRouterHarnessError, match="Bash bridge artifact mutation denied"):
        orh.dispatch_tool_call(
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

    with pytest.raises(orh.OpenRouterHarnessError, match="Bash bridge artifact mutation denied"):
        orh.dispatch_tool_call(
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

    result = orh.dispatch_tool_call(
        "Bash",
        {"command": "Get-Content bridge/INDEX.md"},
        metadata(),
        root,
        guard_runner=allow_runner(records),
        command_runner=command_runner,
    )

    suffixes = [Path(path).as_posix().split("repo/")[-1] for path, _, _ in records]
    assert result == "Document: fixture\n"
    assert suffixes == [guard.as_posix() for guard in orh.BASH_GUARDS]


def test_dispatch_edit_raises_on_missing_file(tmp_path: Path):
    root = make_root(tmp_path)
    records: list[tuple[str, dict, dict]] = []
    with pytest.raises(orh.OpenRouterHarnessError, match="file not found"):
        orh.dispatch_tool_call(
            "Edit",
            {"path": "non_existent_file.txt", "old_string": "foo", "new_string": "bar"},
            metadata(),
            root,
            guard_runner=allow_runner(records),
        )


def test_tool_loop_enforces_session_timeout_between_turns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    (root / "note.txt").write_text("hello", encoding="utf-8")
    ticks = [100.0, 100.0, 101.5]

    def fake_monotonic() -> float:
        return ticks.pop(0) if ticks else 101.5

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        return {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_read",
                                "function": {"name": "Read", "arguments": {"path": "note.txt"}},
                            }
                        ],
                    }
                }
            ]
        }

    monkeypatch.setattr(orh.time, "monotonic", fake_monotonic)

    with pytest.raises(orh.OpenRouterHarnessError, match="session timeout exceeded"):
        orh.run_tool_loop(
            "loop",
            route(root),
            "https://openrouter.test",
            "key",
            3,
            root,
            chat_func=chat,
            timeout=10.0,
            session_timeout=1.0,
        )


def test_tool_loop_omits_model_for_openrouter_cloud_default_route(tmp_path: Path):
    root = make_root(tmp_path)
    model_route = orh.ModelRoute(
        key="openrouter-cloud-default",
        model_id="moonshotai/kimi-k2.7-code",
        model_version="kimi-k2.7-code",
        tool_calling_supported=True,
        allowed_tools=("Read", "Write", "Edit", "Grep", "Glob", "Bash"),
        omit_payload_model=True,
    )
    payloads: list[dict] = []

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        payloads.append(payload)
        return {"model": "moonshotai/kimi-k2.7-code", "choices": [{"message": {"content": "OK"}}]}

    assert (
        orh.run_tool_loop(
            "say OK",
            model_route,
            "https://openrouter.test",
            "key",
            1,
            root,
            chat_func=chat,
        )
        == "OK"
    )
    assert "model" not in payloads[0]


@pytest.mark.parametrize("content", ["", "   \r\n\t"])
def test_tool_loop_rejects_blank_final_text(tmp_path: Path, content: str):
    root = make_root(tmp_path)

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        return {"choices": [{"message": {"content": content}}]}

    with pytest.raises(orh.OpenRouterHarnessError, match="max-turn exhaustion"):
        orh.run_tool_loop(
            "return blank",
            route(root),
            "https://openrouter.test",
            "key",
            1,
            root,
            chat_func=chat,
        )


def test_tool_loop_caps_bash_timeout_to_remaining_session_budget(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = make_root(tmp_path)
    ticks = [100.0, 101.0, 102.0, 103.0]
    observed_timeouts: list[float] = []

    def fake_monotonic() -> float:
        return ticks.pop(0) if ticks else 103.0

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        if len(observed_timeouts) == 0 and len(payload["messages"]) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_bash",
                                    "function": {
                                        "name": "Bash",
                                        "arguments": {"command": "echo ok", "timeout_seconds": 99},
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        return {"choices": [{"message": {"content": "done"}}]}

    def command_runner(command: str, cwd: Path, env: dict, timeout: float) -> subprocess.CompletedProcess[str]:
        observed_timeouts.append(timeout)
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(orh.time, "monotonic", fake_monotonic)

    assert (
        orh.run_tool_loop(
            "run",
            route(root),
            "https://openrouter.test",
            "key",
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


def test_wi4933_grep_returns_without_exhausting_file_iterator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = make_root(tmp_path)
    first = root / "first.txt"
    first.write_text("needle\n", encoding="utf-8")

    def iter_files(_base: Path, **_kwargs):
        yield first
        raise AssertionError("grep exhausted the whole iterator before honoring max_results")

    monkeypatch.setattr(orh, "_iter_text_files", iter_files)

    result = orh.dispatch_tool_call("Grep", {"pattern": "needle", "max_results": 1}, metadata(), root)

    assert result == "first.txt:1:needle"


def test_wi4933_glob_prunes_runtime_cache_directories(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    (root / ".gtkb-state").mkdir()
    (root / ".gtkb-state" / "leak.secret").write_text("hidden", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "keep.secret").write_text("visible", encoding="utf-8")

    result = orh.dispatch_tool_call("Glob", {"pattern": "*.secret"}, metadata(), root)

    assert "src/keep.secret" in result.splitlines()
    assert ".gtkb-state/leak.secret" not in result


def test_wi4933_tool_loop_stops_repeated_no_progress_calls(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    (root / "note.txt").write_text("hello", encoding="utf-8")
    calls: list[dict] = []

    def chat(endpoint: str, api_key: str, payload: dict, timeout: float) -> dict:
        calls.append(payload)
        return {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_read",
                                "function": {"name": "Read", "arguments": {"path": "note.txt"}},
                            }
                        ],
                    }
                }
            ]
        }

    with pytest.raises(orh.OpenRouterHarnessError, match="repeated no-progress tool loop"):
        orh.run_tool_loop(
            "loop",
            route(root),
            "https://openrouter.test",
            "key",
            20,
            root,
            chat_func=chat,
            timeout=10.0,
            session_timeout=120.0,
        )

    assert len(calls) == orh.MAX_REPEATED_TOOL_SIGNATURE_TURNS + 1


# --- WI-4817: bounded transient-failure retry for call_openrouter_chat ---


class _RetryResponse:
    def __init__(self, body: str) -> None:
        self._body = body

    def __enter__(self) -> _RetryResponse:
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def read(self) -> bytes:
        return self._body.encode("utf-8")


def _openrouter_http_error(code: int, headers: dict[str, str] | None = None) -> orh.urllib.error.HTTPError:
    return orh.urllib.error.HTTPError("https://openrouter.test/chat/completions", code, "err", headers or {}, None)


def _patch_openrouter_urlopen(monkeypatch: pytest.MonkeyPatch, behaviors: list, calls: list) -> None:
    def fake_urlopen(request, timeout: float):
        calls.append(request.full_url)
        behavior = behaviors[min(len(calls) - 1, len(behaviors) - 1)]
        if isinstance(behavior, Exception):
            raise behavior
        return _RetryResponse(behavior)

    monkeypatch.setattr(orh.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(orh.time, "sleep", lambda _seconds: None)


def test_wi4817_openrouter_retry_then_success(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    body = orh.json.dumps({"choices": [{"message": {"content": "ok"}}]})
    _patch_openrouter_urlopen(monkeypatch, [_openrouter_http_error(502), body], calls)
    result = orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})
    assert result["choices"][0]["message"]["content"] == "ok"
    assert len(calls) == 2


def test_wi5060_openrouter_connection_reset_retry_then_success(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    body = orh.json.dumps({"choices": [{"message": {"content": "ok"}}]})
    reset = ConnectionResetError(10054, "An existing connection was forcibly closed by the remote host")
    _patch_openrouter_urlopen(monkeypatch, [reset, body], calls)

    result = orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})

    assert result["choices"][0]["message"]["content"] == "ok"
    assert len(calls) == 2


def test_wi5060_openrouter_connection_reset_exhaustion_fails_closed(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    reset = ConnectionResetError(10054, "An existing connection was forcibly closed by the remote host")
    behaviors = [reset] * (orh.CHAT_MAX_ATTEMPTS + 1)
    _patch_openrouter_urlopen(monkeypatch, behaviors, calls)

    with pytest.raises(orh.OpenRouterHarnessError, match="request failed"):
        orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})

    assert len(calls) == orh.CHAT_MAX_ATTEMPTS


def test_wi5060_openrouter_direct_timeout_retry_then_success(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    body = orh.json.dumps({"choices": [{"message": {"content": "ok"}}]})
    timeout = TimeoutError("The read operation timed out")
    _patch_openrouter_urlopen(monkeypatch, [timeout, body], calls)

    result = orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})

    assert result["choices"][0]["message"]["content"] == "ok"
    assert len(calls) == 2


def test_wi5060_openrouter_direct_timeout_exhaustion_fails_closed(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    timeout = TimeoutError("The read operation timed out")
    behaviors = [timeout] * (orh.CHAT_MAX_ATTEMPTS + 1)
    _patch_openrouter_urlopen(monkeypatch, behaviors, calls)

    with pytest.raises(orh.OpenRouterHarnessError, match="request failed"):
        orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})

    assert len(calls) == orh.CHAT_MAX_ATTEMPTS


def test_wi5064_openrouter_ssl_bad_record_mac_retry_then_success(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    body = orh.json.dumps({"choices": [{"message": {"content": "ok"}}]})
    ssl_error = orh.ssl.SSLError("[SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac")
    _patch_openrouter_urlopen(monkeypatch, [ssl_error, body], calls)

    result = orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})

    assert result["choices"][0]["message"]["content"] == "ok"
    assert len(calls) == 2


def test_wi5064_openrouter_ssl_bad_record_mac_exhaustion_is_credential_safe(
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[str] = []
    ssl_error = orh.ssl.SSLError("[SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac")
    behaviors = [ssl_error] * (orh.CHAT_MAX_ATTEMPTS + 1)
    _patch_openrouter_urlopen(monkeypatch, behaviors, calls)

    with pytest.raises(orh.OpenRouterHarnessError) as exc_info:
        orh.call_openrouter_chat("https://openrouter.test", "secret-openrouter-key", {"model": "m"})

    message = str(exc_info.value)
    assert "OpenRouter provider transport failure" in message
    assert "SSLV3_ALERT_BAD_RECORD_MAC" in message
    assert "secret-openrouter-key" not in message
    assert len(calls) == orh.CHAT_MAX_ATTEMPTS


def test_wi4933_openrouter_429_retry_honors_retry_after(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    sleeps: list[float] = []
    body = orh.json.dumps({"choices": [{"message": {"content": "ok"}}]})

    def fake_urlopen(request, timeout: float):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise _openrouter_http_error(429, {"Retry-After": "3.5"})
        return _RetryResponse(body)

    monkeypatch.setattr(orh.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(orh.time, "sleep", sleeps.append)

    result = orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})

    assert result["choices"][0]["message"]["content"] == "ok"
    assert len(calls) == 2
    assert sleeps == [3.5]


def test_wi4933_openrouter_429_exhaustion_reports_backpressure(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    behaviors = [_openrouter_http_error(429)] * (orh.CHAT_MAX_ATTEMPTS + 1)
    _patch_openrouter_urlopen(monkeypatch, behaviors, calls)

    with pytest.raises(orh.OpenRouterHarnessError, match="rate limited .*provider backpressure"):
        orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})

    assert len(calls) == orh.CHAT_MAX_ATTEMPTS


def test_wi4817_openrouter_bounded_exhaustion(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    behaviors = [_openrouter_http_error(500)] * (orh.CHAT_MAX_ATTEMPTS + 1)
    _patch_openrouter_urlopen(monkeypatch, behaviors, calls)
    with pytest.raises(orh.OpenRouterHarnessError, match="HTTP 500"):
        orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})
    assert len(calls) == orh.CHAT_MAX_ATTEMPTS


def test_wi4817_openrouter_fail_fast_on_non_transient(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    _patch_openrouter_urlopen(monkeypatch, [_openrouter_http_error(401)], calls)
    with pytest.raises(orh.OpenRouterHarnessError, match="HTTP 401"):
        orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})
    assert len(calls) == 1


def test_invalid_openrouter_credential_is_not_retried(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    _patch_openrouter_urlopen(monkeypatch, [_openrouter_http_error(403)], calls)

    with pytest.raises(orh.OpenRouterHarnessError, match="HTTP 403"):
        orh.call_openrouter_chat("https://openrouter.test", "bad-key", {"model": "m"})

    assert len(calls) == 1


def test_wi4817_openrouter_non_json_retry_then_success(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    good = orh.json.dumps({"choices": []})
    _patch_openrouter_urlopen(monkeypatch, ["<html>proxy</html>", "not json", good], calls)
    result = orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})
    assert result == {"choices": []}
    assert len(calls) == 3


def test_wi4817_openrouter_non_json_exhaustion_includes_body_snippet(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    behaviors = ["<html>err</html>"] * (orh.CHAT_MAX_ATTEMPTS + 1)
    _patch_openrouter_urlopen(monkeypatch, behaviors, calls)
    with pytest.raises(orh.OpenRouterHarnessError, match="body snippet"):
        orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})
    assert len(calls) == orh.CHAT_MAX_ATTEMPTS


def test_wi4817_openrouter_happy_path_single_attempt(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    _patch_openrouter_urlopen(monkeypatch, [orh.json.dumps({"ok": True})], calls)
    result = orh.call_openrouter_chat("https://openrouter.test", "key", {"model": "m"})
    assert result == {"ok": True}
    assert len(calls) == 1
