from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import ollama_harness
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
    (root / ollama_harness.ROUTING_CONFIG_PATH.parent).mkdir(parents=True, exist_ok=True)
    tools_literal = json.dumps(allowed_tools)
    (root / ollama_harness.ROUTING_CONFIG_PATH).write_text(
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


def _write_project(root: Path, native_harness_record, *, allowed_tools: list[str] | None = None) -> Path:
    (root / "groundtruth.toml").write_text('[project]\nproject_name = "fixture"\n', encoding="utf-8")
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "ollama_harness.py").write_text("# fixture shim\n", encoding="utf-8")
    native_harness_record(root, _ollama_record())
    _write_routing(root, allowed_tools=allowed_tools)
    return root


def test_readiness_passes_with_mocked_tags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, native_harness_record
) -> None:
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(verify, "call_ollama_tags", lambda endpoint, timeout: {OLLAMA_MODEL_ID})
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", lambda **_kwargs: {"checked": True, "configured": True})
    result = verify.evaluate_readiness(root)
    assert result["probe_passed"] is True
    assert result["route_key"] == "review-route"


def test_readiness_fails_closed_when_daemon_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, native_harness_record
) -> None:
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(
        verify,
        "evaluate_ollama_autostart",
        lambda **_kwargs: {"checked": True, "configured": False, "warning": "missing"},
    )

    def _raise_unavailable(endpoint: str, timeout: float) -> set[str]:
        raise verify.OllamaHarnessError("Ollama /api/tags unavailable")

    monkeypatch.setattr(verify, "call_ollama_tags", _raise_unavailable)
    result = verify.evaluate_readiness(root)
    assert result["probe_passed"] is False
    assert result["checks"][-1]["name"] == "ollama /api/tags"
    assert result["checks"][-1]["passed"] is False


def test_readiness_warns_when_autostart_missing_but_daemon_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, native_harness_record
) -> None:
    root = _write_project(tmp_path, native_harness_record)
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

    result = verify.evaluate_readiness(root)

    assert result["probe_passed"] is True
    assert result["autostart"]["configured"] is False
    assert result["warnings"] == [
        {
            "name": "ollama autostart",
            "detail": "No Windows scheduled task or service matching Ollama was detected.",
        }
    ]


def test_readiness_fails_when_required_review_tool_missing(tmp_path: Path, native_harness_record) -> None:
    root = _write_project(tmp_path, native_harness_record, allowed_tools=["Read", "Glob"])
    result = verify.evaluate_readiness(root, require_daemon=False)
    assert result["probe_passed"] is False
    detail = result["checks"][-1]["detail"]
    for tool in ("Bash", "Edit", "Grep", "Write"):
        assert tool in detail


@pytest.mark.parametrize(
    "requested,advertised,expected",
    [
        ("fixture", {"fixture:latest"}, True),
        ("fixture:latest", {"fixture"}, True),
        ("fixture", {"fixture:other"}, False),
        ("fixture:cloud", {"fixture:cloud"}, True),
        ("fixture:cloud", {"fixture:cloud:extra"}, False),
        ("namespace/fixture", {"namespace/fixture:latest"}, True),
        ("fixture", set(), False),
    ],
)
def test_advertised_model_matches_exact_tag_or_default_latest(requested, advertised, expected):
    assert verify._model_advertised(requested, advertised) is expected


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["fixture", None],
        ["fixture", ""],
        ["python", "foreign/scripts/ollama_harness.py", "--skill", "bridge-review"],
        ["python", "scripts/ollama_harness.py", "--skill", "unrelated", "bridge-review"],
    ],
)
def test_malformed_launch_record_prevents_host_and_provider_checks(tmp_path, monkeypatch, native_harness_record, argv):
    root = _write_project(tmp_path, native_harness_record)
    native_harness_record(root, _ollama_record(surfaces={"headless": {"argv": argv}}))

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid launch metadata must not start host/provider checks")

    monkeypatch.setattr(verify, "call_ollama_tags", forbidden)
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", forbidden)
    assert verify.evaluate_readiness(root)["probe_passed"] is False


def test_omitted_daemon_check_is_explicitly_unqualified(tmp_path, monkeypatch, native_harness_record):
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", lambda **kwargs: {"checked": False, "configured": None})
    report = verify.evaluate_readiness(root, require_daemon=False)
    assert report["probe_passed"] is True
    assert report["probe_scope"] == "installation_and_routing"
    assert report["model_execution"] == report["harness_qualification"] == "unqualified"
    assert "argv" not in report and "ready" not in report
    assert not any(c["name"] == "ollama /api/tags" for c in report["checks"])
