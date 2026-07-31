from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"


def _load_gate(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=[("active", ACTIVE_HOOK), ("template", TEMPLATE_HOOK)])
def gate(request: pytest.FixtureRequest):
    name, path = request.param
    return _load_gate(path, f"bridge_compliance_gate_envelope_{name}")


def _versioned(tmp_path: Path, name: str = "gtkb-envelope-head-001.md") -> str:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    return str(bridge_dir / name)


def _metadata() -> str:
    return (
        "author_identity: fixture\n"
        "author_harness_id: T\n"
        "author_session_context_id: test-session\n"
        "author_model: fixture-model\n"
        "author_model_version: fixture-version\n"
        "author_model_configuration: fixture-config\n"
    )


def _body(head: str, *, bridge_kind: str = "spec_intake") -> str:
    return (
        f"{head}"
        f"{_metadata()}\n"
        f"bridge_kind: {bridge_kind}\n"
        "Document: gtkb-envelope-head\n"
        "Version: 001\n\n"
        "## Specification Links\n\n"
        "- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`\n\n"
        "## Prior Deliberations\n\n"
        "_No prior deliberations: envelope-head unit test._\n"
    )


def _deny(gate, tmp_path: Path, content: str) -> str | None:
    return gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=_versioned(tmp_path),
        content=content,
        run_pending_preflight=False,
    )


def test_missing_dispatchable_envelope_is_denied(gate, tmp_path: Path) -> None:
    reason = _deny(gate, tmp_path, _body("NEW\n"))

    assert reason is not None
    assert "artifact-head envelope" in reason
    assert "::init gtkb pb" in reason


def test_mismatched_responder_role_is_denied(gate, tmp_path: Path) -> None:
    reason = _deny(gate, tmp_path, _body("NEW\n::init gtkb lo\n::open build\n"))

    assert reason is not None
    assert "responder-role mismatch" in reason


def test_invalid_activity_is_denied(gate, tmp_path: Path) -> None:
    reason = _deny(gate, tmp_path, _body("NEW\n::init gtkb pb\n::open unknown\n"))

    assert reason is not None
    assert "invalid" in reason


def test_unmapped_status_rejects_envelope_lines(gate, tmp_path: Path) -> None:
    reason = _deny(
        gate,
        tmp_path,
        _body("ADVISORY\n::init gtkb lo\n::open deliberation\n", bridge_kind="loyal_opposition_advisory"),
    )

    assert reason is not None
    assert "no formal responder-role" in reason


def test_valid_dispatchable_envelope_reaches_later_checks(gate, tmp_path: Path) -> None:
    reason = _deny(gate, tmp_path, _body("NEW\n::init gtkb pb\n::open build\n"))

    if reason is not None:
        assert "artifact-head envelope" not in reason
