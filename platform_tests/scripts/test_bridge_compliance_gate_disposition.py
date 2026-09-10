"""Harness proposals do not depend on knowing other harnesses.

Exercise the baseline and adopter-template content gates, without reading a
peer harness or requiring their projections to exist.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

_AUTHOR_METADATA = (
    "author_identity: prime-builder/codex/A\n"
    "author_harness_id: A\n"
    "author_session_context_id: test-session\n"
    "author_model: GPT-5\n"
    "author_model_version: GPT-5\n"
    "author_model_configuration: test\n"
)
_PROJECT_METADATA = "Project: PROJECT-TEST-X\nWork Item: WI-9999\n"
_SPEC_LINKS = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
_REQ_SUFF = "## Requirement Sufficiency\n\nExisting requirements sufficient. Rationale prose here.\n"
_SIMPLIFICATION = "## Simplification Accounting\n\nNothing gets smaller; this is a test fixture.\n"

_HARNESS_SURFACE_TARGET = 'target_paths: [".harness-baseline-configuration/hooks/bridge-compliance-gate.py"]\n'


def _load_gate(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=["live", "template"])
def gate(request: pytest.FixtureRequest) -> ModuleType:
    if request.param == "live":
        return _load_gate(LIVE_HOOK, "bcg_disposition_live")
    return _load_gate(TEMPLATE_HOOK, "bcg_disposition_template")


def _proposal(
    *,
    status: str = "NEW",
    bridge_kind: str = "implementation_proposal",
    target_paths: str | None = _HARNESS_SURFACE_TARGET,
    disposition: str | None = None,
) -> str:
    parts = [
        status,
        "::init gtkb lo",
        "::open build",
        "Document: test-disposition",
        "Version: 1",
        "Date: 2026-09-09",
        "recipient_role: loyal-opposition",
        _AUTHOR_METADATA.rstrip(),
        f"bridge_kind: {bridge_kind}",
        _PROJECT_METADATA.rstrip(),
        "work_item_version: 1",
        'spec_versions: {"GOV-FILE-BRIDGE-AUTHORITY-001": 1}',
        'test_artifact_targets: ["tests/test_effect.py"]',
    ]
    if target_paths is not None:
        parts.append(target_paths)
    parts.extend(["", "# Test Proposal", "", _SPEC_LINKS])
    parts.append("")
    parts.append(_REQ_SUFF)
    parts.append(_SIMPLIFICATION)
    authored_disposition = {
        "schema_version": 1,
        "applicability": "applicable",
        "provenance": "Agent-authored fixture for WI-9999 in PROJECT-TEST-X",
        "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
        "primary_route": "gt bridge deliver",
        "before_behavior": "The declared target returns the wrong result.",
        "after_behavior": "The declared target returns the specified result.",
        "self_descriptive_naming": "The target and test name the corrected behavior.",
        "obsolete_guidance_disposition": "Correct contradictory instructions at their source.",
        "history_preservation": "Preserve Git and formal history.",
        "baseline": {"behavior": "incorrect"},
        "expected_result": {"behavior": "correct"},
        "rollback": {"instructions": "Make a new forward correction and rerun the affected tests."},
        "hard_invariants": ["One project membership", "Independent review"],
        "fail_closed_conditions": ["Stale inputs", "Target outside the declared scope"],
        "essential_context_preservation": "Retain current requirements, targets and executable test instructions.",
    }
    parts.append(
        "## Intuitiveness / Non-Impairment Disposition\n\n```json\n" + json.dumps(authored_disposition) + "\n```"
    )
    if disposition is not None:
        parts.append("")
        parts.append(disposition)
    return "\n".join(parts)


def _deny(gate: ModuleType, content: str, cwd: Path) -> str | None:
    original_membership_gap = gate._wi_project_membership_gap
    gate._wi_project_membership_gap = lambda _content, _cwd: None
    try:
        return gate._deny_reason_for_content(
            cwd_path=cwd,
            file_path="bridge/test-disposition-001.md",
            content=content,
            run_pending_preflight=False,
        )
    finally:
        gate._wi_project_membership_gap = original_membership_gap


@pytest.mark.parametrize("status", ["NEW", "REVISED"])
@pytest.mark.parametrize(
    "target",
    [
        ".harness-baseline-configuration/hooks/local.py",
        ".harness-baseline-configuration/skills/example/SKILL.md",
        "groundtruth-kb/src/groundtruth_kb/example.py",
        "scripts/local.py",
    ],
)
def test_proposal_needs_no_other_harness_disposition(gate, tmp_path, status, target):
    reason = _deny(
        gate, _proposal(status=status, target_paths=f'target_paths: ["{target}"]\n', disposition=None), tmp_path
    )
    assert reason is None


def test_missing_requirement_sufficiency_still_denied(gate, tmp_path):
    content = _proposal(disposition=None).replace(_REQ_SUFF, "")
    reason = _deny(gate, content, tmp_path)
    assert reason is not None and "Requirement Sufficiency" in reason
