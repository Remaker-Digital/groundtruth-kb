"""Native Codex/Claude prompt-adapter parity tests for WI-5266."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest
from groundtruth_kb.session.envelope import load_current, open_session

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = {
    "codex": REPO_ROOT / ".codex" / "gtkb-hooks" / "session_wrapup_trigger_dispatch.py",
    "claude": REPO_ROOT / ".claude" / "hooks" / "session-topic-envelope-router.py",
}


def _load_hook(harness_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"wi5266_{harness_name}_hook", HOOKS[harness_name])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_harnesses(root: Path) -> None:
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"codex": {"id": "A"}, "claude": {"id": "B"}},
            }
        ),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {"id": "A", "harness_name": "codex", "role": ["prime-builder"]},
                    {"id": "B", "harness_name": "claude", "role": ["prime-builder"]},
                ],
            }
        ),
        encoding="utf-8",
    )


def _configure_hook(
    module: ModuleType,
    harness_name: str,
    root: Path,
    prompt: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness_id = "A" if harness_name == "codex" else "B"
    module.PROJECT_ROOT = root
    module.OUT_DIR = root / ".test-hook-output" / harness_name
    monkeypatch.setattr(module, "_read_stdin", lambda: json.dumps({"prompt": prompt}))
    monkeypatch.setattr(module, "_startup_input_gate_active", lambda: False)
    monkeypatch.setattr(module, "_persistent_harness_id", lambda: harness_id)
    if harness_name == "codex":
        monkeypatch.setattr(module, "_ensure_session_role_latched", lambda: "prime-builder")


@pytest.mark.parametrize("harness_name", ["codex", "claude"])
def test_native_prompt_hook_routes_backlog_without_bridge_substitution(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _seed_harnesses(tmp_path)
    harness_id = "A" if harness_name == "codex" else "B"
    open_session(
        tmp_path,
        harness_name=harness_name,
        harness_id=harness_id,
        role="prime-builder",
        session_id=f"session-{harness_name}",
    )
    module = _load_hook(harness_name)
    _configure_hook(
        module,
        harness_name,
        tmp_path,
        "Process the P0/P1 backlog beginning with bridge/TAFE/harness-related items WI-5266",
        monkeypatch,
    )

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["hookSpecificOutput"]["additionalContext"]
    envelope = load_current(tmp_path, harness_name)

    assert "explicitly selects `backlog`" in context
    assert "`backlog` via `gt backlog list`" in context
    assert envelope is not None
    assert envelope["resource_selection"]["selected_resources"] == ["backlog"]
    assert envelope["active_work_item_id"] == "WI-5266"


@pytest.mark.parametrize("harness_name", ["codex", "claude"])
def test_native_prompt_hook_routes_an_explicit_bridge_queue(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _seed_harnesses(tmp_path)
    harness_id = "A" if harness_name == "codex" else "B"
    open_session(
        tmp_path,
        harness_name=harness_name,
        harness_id=harness_id,
        role="prime-builder",
        session_id=f"session-{harness_name}",
    )
    module = _load_hook(harness_name)
    _configure_hook(module, harness_name, tmp_path, "Process the bridge queue", monkeypatch)

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["hookSpecificOutput"]["additionalContext"]
    envelope = load_current(tmp_path, harness_name)

    assert "explicitly selects `bridge_queue`" in context
    assert "`bridge_queue` via `gt bridge state-report`" in context
    assert envelope is not None
    assert envelope["resource_selection"]["selected_resources"] == ["bridge_queue"]


@pytest.mark.parametrize("harness_name", ["codex", "claude"])
def test_topic_command_precedes_resource_routing(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _seed_harnesses(tmp_path)
    module = _load_hook(harness_name)
    _configure_hook(module, harness_name, tmp_path, "::open build", monkeypatch)
    monkeypatch.setattr(module, "handle_topic_command", lambda *_args, **_kwargs: {"topic": "build"})
    monkeypatch.setattr(module, "render_topic_context", lambda _result: "topic-command-context")
    monkeypatch.setattr(
        module,
        "route_prompt_resources",
        lambda *_args, **_kwargs: pytest.fail("ordinary resource routing stole a strict topic command"),
    )

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["hookSpecificOutput"]["additionalContext"] == "topic-command-context"


@pytest.mark.parametrize("harness_name", ["codex", "claude"])
def test_startup_relay_gate_precedes_resource_routing(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _seed_harnesses(tmp_path)
    module = _load_hook(harness_name)
    _configure_hook(module, harness_name, tmp_path, "process backlog", monkeypatch)
    monkeypatch.setattr(module, "_startup_input_gate_active", lambda: True)
    monkeypatch.setattr(
        module,
        "route_prompt_resources",
        lambda *_args, **_kwargs: pytest.fail("resource routing stole the startup relay prompt"),
    )

    assert module.main() == 0
    assert json.loads(capsys.readouterr().out) == {}
