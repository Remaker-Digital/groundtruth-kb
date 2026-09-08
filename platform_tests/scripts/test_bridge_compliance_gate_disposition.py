"""Harness proposals do not depend on knowing other harnesses.

Exercise the baseline and adopter-template content gates, without reading a
peer harness or requiring their projections to exist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

_DISPOSITION_MARKER = "Cross-Harness Disposition"

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

_HARNESS_SURFACE_TARGET = 'target_paths: [".claude/hooks/bridge-compliance-gate.py"]\n'
_OFF_SURFACE_TARGET = 'target_paths: ["scripts/example.py"]\n'

_CONCRETE_DISPOSITION = (
    "## Cross-Harness Disposition\n\n"
    "- Universal applicability; behaves identically on claude and codex via the "
    "canonical Python hook. No per-harness divergence; no waiver required.\n"
)
_PLACEHOLDER_DISPOSITION = "## Cross-Harness Disposition\n\nn/a\n"
_BULLET_ONLY_DISPOSITION = "## Cross-Harness Disposition\n\n-\n"
_BLANK_BULLET_DISPOSITION = "## Cross-Harness Disposition\n\n*\n"


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
    bridge_kind: str = "prime_proposal",
    target_paths: str | None = _HARNESS_SURFACE_TARGET,
    disposition: str | None = _CONCRETE_DISPOSITION,
) -> str:
    parts = [
        status,
        "::init gtkb lo",
        "::open build",
        "",
        "# Test Proposal",
        "",
        _AUTHOR_METADATA,
        f"bridge_kind: {bridge_kind}",
        "",
        _PROJECT_METADATA,
    ]
    if target_paths is not None:
        parts.append(target_paths)
    parts.append(_SPEC_LINKS)
    parts.append("")
    parts.append(_REQ_SUFF)
    parts.append(_SIMPLIFICATION)
    from groundtruth_kb.bridge.proposal_filing import build_nonimpairment_disposition, render_nonimpairment_disposition

    parts.append(
        render_nonimpairment_disposition(
            build_nonimpairment_disposition(
                wi_id="WI-9999",
                project_id="PROJECT-TEST-X",
                target_paths=("src/x.py",),
                summary="Correct the declared target behavior",
                description="The target has an incorrect behavior",
                scope_lines=("Correct the declared target",),
                acceptance_criteria=("Target behavior is correct",),
                spec_links=["GOV-FILE-BRIDGE-AUTHORITY-001"],
            )
        )
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
        ".claude/hooks/local.py",
        ".codex/gtkb-hooks/local.py",
        ".cursor/skills/local/SKILL.md",
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
