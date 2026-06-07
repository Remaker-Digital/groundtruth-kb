from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import cross_harness_bridge_trigger as trigger
from scripts import verify_ollama_dispatch as verify

OLLAMA_MODEL_ID = "fixture-review:current"
OLLAMA_SURFACES = {
    "headless": {
        "argv": [
            "groundtruth-kb/.venv/Scripts/python.exe",
            "scripts/ollama_harness.py",
            "-p",
            "{{PROMPT}}",
            "--skill",
            "bridge-review",
        ]
    }
}


def _write_registry(root: Path, records: list[dict]) -> None:
    state = root / "harness-state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": records}),
        encoding="utf-8",
    )


def _ollama_record(
    *,
    role: list[str] | None = None,
    status: str = "registered",
    surfaces: dict | None = None,
    event_driven_hooks: bool = False,
) -> dict:
    return {
        "id": "D",
        "harness_name": "ollama",
        "harness_type": "ollama",
        "role": [] if role is None else role,
        "status": status,
        "event_driven_hooks": event_driven_hooks,
        "invocation_surfaces": OLLAMA_SURFACES if surfaces is None else surfaces,
    }


def _write_routing(root: Path, *, allowed_tools: list[str] | None = None) -> None:
    if allowed_tools is None:
        allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    (root / ".ollama").mkdir(parents=True, exist_ok=True)
    tools_literal = json.dumps(allowed_tools)
    (root / ".ollama" / "routing.toml").write_text(
        "schema_version = 1\n"
        "\n"
        "[models.review-route]\n"
        f'model_id = "{OLLAMA_MODEL_ID}"\n'
        "tool_calling_supported = true\n"
        f"allowed_tools = {tools_literal}\n"
        "\n"
        "[routing]\n"
        'default_model = "review-route"\n'
        "\n"
        "[routing.skills]\n"
        'bridge-review = "review-route"\n',
        encoding="utf-8",
    )


def _write_project(root: Path, *, allowed_tools: list[str] | None = None) -> Path:
    (root / "groundtruth.toml").write_text('[project]\nproject_name = "fixture"\n', encoding="utf-8")
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "ollama_harness.py").write_text("# fixture shim\n", encoding="utf-8")
    _write_registry(root, [_ollama_record()])
    _write_routing(root, allowed_tools=allowed_tools)
    return root


def test_build_dispatch_command_uses_registry_template(tmp_path: Path) -> None:
    root = _write_project(tmp_path)
    command = verify.build_dispatch_command(root, "hello")
    assert command == [
        "groundtruth-kb/.venv/Scripts/python.exe",
        "scripts/ollama_harness.py",
        "-p",
        "hello",
        "--skill",
        "bridge-review",
    ]


def test_readiness_passes_with_mocked_tags(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _write_project(tmp_path)
    monkeypatch.setattr(verify, "call_ollama_tags", lambda endpoint, timeout: {OLLAMA_MODEL_ID})
    result = verify.evaluate_dispatch_readiness(root)
    assert result["ready"] is True
    assert result["route_key"] == "review-route"


def test_readiness_fails_closed_when_daemon_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _write_project(tmp_path)

    def _raise_unavailable(endpoint: str, timeout: float) -> set[str]:
        raise verify.OllamaHarnessError("Ollama /api/tags unavailable")

    monkeypatch.setattr(verify, "call_ollama_tags", _raise_unavailable)
    result = verify.evaluate_dispatch_readiness(root)
    assert result["ready"] is False
    assert result["checks"][-1]["name"] == "ollama /api/tags"
    assert result["checks"][-1]["passed"] is False


def test_readiness_fails_when_required_review_tool_missing(tmp_path: Path) -> None:
    root = _write_project(tmp_path, allowed_tools=["Read", "Glob"])
    result = verify.evaluate_dispatch_readiness(root, require_daemon=False)
    assert result["ready"] is False
    detail = result["checks"][-1]["detail"]
    for tool in ("Bash", "Edit", "Grep", "Write"):
        assert tool in detail


def test_trigger_resolves_active_ollama_only_when_readiness_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_registry(tmp_path, [_ollama_record(role=["loyal-opposition"], status="active")])
    monkeypatch.setattr(trigger, "_evaluate_ollama_dispatch_readiness", lambda root: {"ready": True})

    target = trigger._resolve_dispatch_target("loyal-opposition", tmp_path, tmp_path / "state")

    assert target is not None
    assert target.harness_id == "D"
    assert target.command_handle == "ollama"
    assert target.canonical_mode == "lo"


@pytest.mark.parametrize(("role", "mode"), [("loyal-opposition", "lo"), ("prime-builder", "pb")])
def test_trigger_resolution_is_portable_across_roles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, role: str, mode: str
) -> None:
    _write_project(tmp_path)
    _write_registry(tmp_path, [_ollama_record(role=[role], status="active")])
    monkeypatch.setattr(trigger, "_evaluate_ollama_dispatch_readiness", lambda root: {"ready": True})

    target = trigger._resolve_dispatch_target(role, tmp_path, tmp_path / "state")

    assert target is not None
    assert target.harness_id == "D"
    assert target.canonical_mode == mode


def test_trigger_fails_closed_when_ollama_readiness_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_project(tmp_path)
    _write_registry(tmp_path, [_ollama_record(role=["loyal-opposition"], status="active")])
    monkeypatch.setattr(
        trigger,
        "_evaluate_ollama_dispatch_readiness",
        lambda root: {"ready": False, "checks": [{"name": "ollama /api/tags", "passed": False}]},
    )
    state_dir = tmp_path / "state"

    with pytest.raises(trigger.DispatchTargetNotReady) as excinfo:
        trigger._resolve_dispatch_target("loyal-opposition", tmp_path, state_dir)

    assert excinfo.value.reason == "ollama_dispatch_not_ready"
    assert excinfo.value.harness_id == "D"
    failures = [
        json.loads(line) for line in (state_dir / "dispatch-failures.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert any(record["reason"] == "ollama_dispatch_not_ready" for record in failures)
    assert not any(record["reason"] == "no_active_target_for_role" for record in failures)


def test_registered_ollama_without_role_is_not_selected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_project(tmp_path)
    calls = 0

    def _readiness(root: Path) -> dict:
        nonlocal calls
        calls += 1
        return {"ready": True}

    monkeypatch.setattr(trigger, "_evaluate_ollama_dispatch_readiness", _readiness)

    assert trigger._resolve_dispatch_target("loyal-opposition", tmp_path, tmp_path / "state") is None
    assert calls == 0
