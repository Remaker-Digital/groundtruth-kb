from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

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


def test_bridge_review_prompt_uses_no_index_bridge_instructions(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = orh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    assert "bridge/INDEX.md" not in prompt
    assert "full\nversioned bridge-file chain" in prompt
    assert "gt bridge dispatch config" in prompt
    assert "gt bridge dispatch status" in prompt
    assert "gt bridge dispatch\nhealth" in prompt


def test_bridge_review_prompt_seeds_prior_deliberations_before_verdict_write(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = orh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    claim_index = prompt.index("python scripts\\bridge_claim_cli.py claim <document-slug>")
    helper_index = prompt.index("python .claude/skills/verify/helpers/write_verdict.py")
    bridge_workflow_index = prompt.index("Use the GT-KB file bridge")
    assert claim_index < helper_index < bridge_workflow_index
    assert (
        "python .claude/skills/verify/helpers/write_verdict.py --slug <document-slug> --body-file <draft-body-file>"
    ) in prompt
    assert "Review and prune the helper-seeded Prior Deliberations" in prompt
    assert "silently omitting Prior Deliberations" in prompt


def test_bridge_review_prompt_requires_atomic_verified_finalization(tmp_path: Path):
    root = make_root(tmp_path)
    prompt = orh.build_system_prompt("bridge-review", route(root))

    assert prompt is not None
    assert "--finalize-verified" in prompt
    assert "--no-prepopulate" in prompt
    assert "local commit containing the verified path set" in prompt
    assert "fail closed" in prompt
    assert "terminal VERIFIED file" in prompt


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


def _openrouter_http_error(code: int) -> orh.urllib.error.HTTPError:
    return orh.urllib.error.HTTPError("https://openrouter.test/chat/completions", code, "err", None, None)


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
