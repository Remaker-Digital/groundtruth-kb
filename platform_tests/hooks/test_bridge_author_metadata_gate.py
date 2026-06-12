"""Bridge-compliance gate tests for bridge author/model audit metadata."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

AUTHOR_METADATA = (
    "author_identity: Codex\n"
    "author_harness_id: A\n"
    "author_session_context_id: session-123\n"
    "author_model: GPT-5.5\n"
    "author_model_version: 5.5\n"
    "author_model_configuration: Extra High\n"
)


def _load_gate(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=((LIVE_HOOK, "live"), (TEMPLATE_HOOK, "template")))
def gate(request: pytest.FixtureRequest) -> ModuleType:
    path, name = request.param
    return _load_gate(path, f"bridge_compliance_gate_author_metadata_{name}")


def _deny(gate: ModuleType, content: str) -> str | None:
    return gate._deny_reason_for_content(
        cwd_path=REPO_ROOT,
        file_path="bridge/test-author-metadata-001.md",
        content=content,
        run_pending_preflight=False,
    )


def test_bridge_verdict_missing_author_metadata_blocked(gate: ModuleType) -> None:
    reason = _deny(gate, "NO-GO\n\n## Findings\n\nNo blocking findings.\n")

    assert reason is not None
    assert "author/model audit metadata" in reason
    assert "author_model_configuration" in reason


def test_bridge_verdict_with_author_metadata_passes_metadata_gate(gate: ModuleType) -> None:
    reason = _deny(gate, "NO-GO\n" + AUTHOR_METADATA + "\n## Findings\n\nNo blocking findings.\n")

    assert reason is None


def test_bridge_author_metadata_placeholder_model_blocked(gate: ModuleType) -> None:
    content = (
        "NO-GO\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: unknown\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
        "\n## Findings\n"
    )

    reason = _deny(gate, content)

    assert reason is not None
    assert "author_model" in reason


def test_bridge_kind_exemption_does_not_exempt_author_metadata(gate: ModuleType) -> None:
    content = "NEW\nbridge_kind: governance_advisory\n\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"

    reason = _deny(gate, content)

    assert reason is not None
    assert "author/model audit metadata" in reason
