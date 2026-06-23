"""Regression tests for WI-3463 bridge-compliance magic-content guidance."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"
NUMBERED_CHAIN_PATTERN = r"(?i)(?:bridge/.+-\d{3}\.md|numbered bridge files?|versioned bridge files?|append[- ]only)"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_HOOKS = {
    "live": _load_gate(LIVE_HOOK, "bridge_compliance_gate_magic_guidance_live"),
    "template": _load_gate(TEMPLATE_HOOK, "bridge_compliance_gate_magic_guidance_template"),
}


@pytest.fixture(params=sorted(_HOOKS), ids=sorted(_HOOKS))
def gate(request: pytest.FixtureRequest) -> ModuleType:
    return _HOOKS[request.param]


def _bridge_proposal_missing_numbered_file_evidence() -> str:
    return """
NEW
author_identity: prime-builder/test
author_harness_id: A
author_session_context_id: test-magic-content-guidance
author_model: pytest
author_model_version: test
author_model_configuration: focused regression

# Magic Content Guidance Fixture

bridge_kind: prime_proposal
Document: test-magic-content-guidance
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3463
target_paths: ["scripts/adr_dcl_clause_preflight.py"]

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - dispatcher state governs this proposal.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - concrete links are required.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - project metadata is required.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - pytest command evidence is required.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - active files stay in `E:/GT-KB`.
- GOV-STANDING-BACKLOG-001 - WI-3463 is a backlog work item.

## Prior Deliberations

_No prior deliberations: synthetic WI-3463 hook regression fixture._

## Owner Decisions / Input

PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers this focused reliability fixture.

## Requirement Sufficiency

Existing requirements sufficient.

## Proposed Implementation

This fixture intentionally mentions dispatcher state so the bridge-authority clause applies.
All active files remain in `E:/GT-KB`.

## Specification-Derived Verification

python -m pytest platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py -q --tb=short
"""


def test_pending_bridge_write_denial_surfaces_clause_evidence_pattern(gate: ModuleType) -> None:
    reason = gate._deny_reason_for_content(
        cwd_path=REPO_ROOT,
        file_path="bridge/test-magic-content-guidance-001.md",
        content=_bridge_proposal_missing_numbered_file_evidence(),
        run_pending_preflight=True,
    )

    assert reason is not None
    assert "ADR/DCL clause preflight failed" in reason
    assert "Evidence pattern:" in reason
    assert NUMBERED_CHAIN_PATTERN in reason
