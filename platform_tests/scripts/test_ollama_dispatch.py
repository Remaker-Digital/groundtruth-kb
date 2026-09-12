from __future__ import annotations

import json
from pathlib import Path

import pytest

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
    event_driven_hooks: bool = True,
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
    (root / ".api-harness").mkdir(parents=True, exist_ok=True)
    tools_literal = json.dumps(allowed_tools)
    (root / ".api-harness" / "routing.toml").write_text(
        "schema_version = 1\n"
        "\n"
        "[models.review-route]\n"
        f'model_id = "{OLLAMA_MODEL_ID}"\n'
        "tool_calling_supported = true\n"
        f"allowed_tools = {tools_literal}\n"
        "\n"
        "[routing.ollama]\n"
        'default_model = "review-route"\n'
        "\n"
        "[routing.ollama.skills]\n"
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


def test_readiness_passes_with_mocked_tags(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _write_project(tmp_path)
    monkeypatch.setattr(verify, "call_ollama_tags", lambda endpoint, timeout: {OLLAMA_MODEL_ID})
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", lambda **_kwargs: {"checked": True, "configured": True})
    result = verify.evaluate_dispatch_readiness(root)
    assert result["ready"] is True
    assert result["route_key"] == "review-route"


def test_readiness_fails_closed_when_daemon_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _write_project(tmp_path)
    monkeypatch.setattr(
        verify,
        "evaluate_ollama_autostart",
        lambda **_kwargs: {"checked": True, "configured": False, "warning": "missing"},
    )

    def _raise_unavailable(endpoint: str, timeout: float) -> set[str]:
        raise verify.OllamaHarnessError("Ollama /api/tags unavailable")

    monkeypatch.setattr(verify, "call_ollama_tags", _raise_unavailable)
    result = verify.evaluate_dispatch_readiness(root)
    assert result["ready"] is False
    assert result["checks"][-1]["name"] == "ollama /api/tags"
    assert result["checks"][-1]["passed"] is False


def test_readiness_warns_when_autostart_missing_but_daemon_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _write_project(tmp_path)
    monkeypatch.setattr(verify, "call_ollama_tags", lambda endpoint, timeout: {OLLAMA_MODEL_ID})
    monkeypatch.setattr(
        verify,
        "evaluate_ollama_autostart",
        lambda **_kwargs: {
            "checked": True,
            "configured": False,
            "warning": "No Windows scheduled task or service matching Ollama was detected.",
        },
    )

    result = verify.evaluate_dispatch_readiness(root)

    assert result["ready"] is True
    assert result["autostart"]["configured"] is False
    assert result["warnings"] == [
        {
            "name": "ollama autostart",
            "detail": "No Windows scheduled task or service matching Ollama was detected.",
        }
    ]


def test_readiness_fails_when_required_review_tool_missing(tmp_path: Path) -> None:
    root = _write_project(tmp_path, allowed_tools=["Read", "Glob"])
    result = verify.evaluate_dispatch_readiness(root, require_daemon=False)
    assert result["ready"] is False
    detail = result["checks"][-1]["detail"]
    for tool in ("Bash", "Edit", "Grep", "Write"):
        assert tool in detail
