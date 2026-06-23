"""Focused coverage for target_paths bridge proposal checkpoints."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=["live", "template"])
def gate(request: pytest.FixtureRequest) -> ModuleType:
    if request.param == "live":
        return _load_gate(LIVE_HOOK, "bcg_kb_mutation_live")
    return _load_gate(TEMPLATE_HOOK, "bcg_kb_mutation_template")


def _proposal(*, target_paths: str, body: str, bridge_kind: str = "prime_implementation_proposal") -> str:
    return (
        "NEW\n\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: test-session\n"
        "author_model: GPT-5\n"
        "author_model_version: GPT-5\n"
        "author_model_configuration: test\n\n"
        f"bridge_kind: {bridge_kind}\n\n"
        "Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING\n"
        "Project: PROJECT-GTKB-RELIABILITY-FIXES\n"
        "Work Item: WI-3372\n\n"
        f"target_paths: {target_paths}\n\n"
        f"{body}\n\n"
        "## Specification Links\n\n"
        "- DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001\n"
        "- SPEC-AUQ-NO-LLM-CLASSIFIER-001\n\n"
        "## Specification-Derived Verification\n\n"
        "Run `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py`.\n"
    )


def test_kb_mutation_without_groundtruth_db_asks(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This implementation inserts a new GOV version record into MemBase.",
    )

    reason = gate._ask_reason_for_content("bridge/test-kb-mutation-target-paths-001.md", content)

    assert reason is not None
    assert "groundtruth.db" in reason
    assert "KB/MemBase mutation" in reason


def test_kb_mutation_with_groundtruth_db_passes(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py", "groundtruth.db"]',
        body="This implementation inserts a new GOV version record into MemBase.",
    )

    assert gate._ask_reason_for_content("bridge/test-kb-mutation-target-paths-001.md", content) is None


def test_kb_mutation_with_dot_prefixed_groundtruth_db_passes(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py", "./groundtruth.db"]',
        body="This implementation writes a new Deliberation Archive record row.",
    )

    assert gate._ask_reason_for_content("bridge/test-kb-mutation-target-paths-001.md", content) is None


def test_membase_mention_only_not_flagged(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This proposal explains prior MemBase defects but performs no MemBase mutation or groundtruth.db write.",
    )

    assert gate._ask_reason_for_content("bridge/test-kb-mutation-target-paths-001.md", content) is None


def test_metadata_exempt_bridge_kind_not_flagged(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This spec intake writes a new Deliberation Archive record row.",
        bridge_kind="spec_intake",
    )

    assert gate._ask_reason_for_content("bridge/test-kb-mutation-target-paths-001.md", content) is None


def test_formal_artifact_approval_evidence_without_packet_path_asks(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This implementation writes formal artifact approval evidence for a new GOV version.",
    )

    reason = gate._ask_reason_for_content("bridge/test-approval-evidence-target-paths-001.md", content)

    assert reason is not None
    assert ".groundtruth/formal-artifact-approvals" in reason
    assert "approval-packet" in reason


def test_narrative_artifact_approval_packet_without_packet_path_asks(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This implementation writes a narrative-artifact approval-packet for AGENTS.md.",
    )

    reason = gate._ask_reason_for_content("bridge/test-approval-evidence-target-paths-001.md", content)

    assert reason is not None
    assert "formal/narrative artifact approval evidence" in reason


def test_approval_evidence_with_concrete_packet_path_passes(gate: ModuleType) -> None:
    content = _proposal(
        target_paths=(
            '[".claude/hooks/bridge-compliance-gate.py", '
            '".groundtruth/formal-artifact-approvals/2026-06-23-gov-update.json"]'
        ),
        body="This implementation writes formal artifact approval evidence for a new GOV version.",
    )

    assert gate._ask_reason_for_content("bridge/test-approval-evidence-target-paths-001.md", content) is None


def test_approval_evidence_with_directory_glob_passes(gate: ModuleType) -> None:
    content = _proposal(
        target_paths=('[".claude/hooks/bridge-compliance-gate.py", ".groundtruth/formal-artifact-approvals/**"]'),
        body="This implementation writes an approval packet for a narrative artifact.",
    )

    assert gate._ask_reason_for_content("bridge/test-approval-evidence-target-paths-001.md", content) is None


def test_approval_packet_mention_only_not_flagged(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This proposal explains prior approval packet defects but performs no approval packet work.",
    )

    assert gate._ask_reason_for_content("bridge/test-approval-evidence-target-paths-001.md", content) is None


def test_approval_evidence_metadata_exempt_bridge_kind_not_flagged(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This spec intake writes a formal artifact approval packet.",
        bridge_kind="spec_intake",
    )

    assert gate._ask_reason_for_content("bridge/test-approval-evidence-target-paths-001.md", content) is None


def test_approval_evidence_implementation_report_not_flagged(gate: ModuleType) -> None:
    content = _proposal(
        target_paths='[".claude/hooks/bridge-compliance-gate.py"]',
        body="This implementation report carries forward formal artifact approval evidence spec links.",
        bridge_kind="implementation_report",
    )

    assert gate._ask_reason_for_content("bridge/test-approval-evidence-target-paths-003.md", content) is None
