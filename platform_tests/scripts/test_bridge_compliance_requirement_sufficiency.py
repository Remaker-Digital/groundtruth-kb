"""Tests for the bridge-compliance-gate ``## Requirement Sufficiency`` presence
check (WI-3439).

Per ``.claude/rules/file-bridge-protocol.md`` section "Mandatory
Implementation-Start Authorization Metadata", every implementation proposal that
requests source/test/script/hook/config/deploy/repo-state/KB-mutation work must
carry a ``## Requirement Sufficiency`` subsection with exactly one operative
state. Before WI-3439 this contract was only enforced post-GO at
implementation-start, so a proposal could lose the subsection across REVISED
versions and still receive GO. The Write-time check added in WI-3439 closes that
gap.

Constraints carried forward from the GO at
``bridge/gtkb-wi3439-requirement-sufficiency-presence-check-002.md``:

1. The gate is scoped to implementation-proposal bridge_kind tokens
   (``prime_proposal`` / ``implementation_proposal``), NOT a broad
   "NEW|REVISED + non-exempt bridge_kind + target_paths" trigger. A
   ``implementation_report`` with target_paths and no subsection must NOT be
   denied (constraint 2).
2. Both operative states are structurally valid (constraint 3): "Existing
   requirements sufficient" AND "New or revised requirement required before
   implementation".
3. The check reuses the shared first-line status trigger
   (``PROJECT_METADATA_STATUSES``); it must not introduce a divergent status
   parser (constraint 5).
4. The template source is the canonical hook and the ``.claude/hooks`` copy must
   be byte-identical (constraint 6); the parametrized ``gate`` fixture exercises
   BOTH, and ``test_template_and_active_hook_byte_identical`` asserts parity.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

_MARKER = "WI-3439"

_AUTHOR_METADATA = (
    "author_identity: Codex\n"
    "author_harness_id: A\n"
    "author_session_context_id: test-session\n"
    "author_model: GPT-5\n"
    "author_model_version: GPT-5\n"
    "author_model_configuration: test\n"
)
_PROJECT_METADATA = "Project Authorization: PAUTH-TEST-PROJECT-X\nProject: PROJECT-TEST-X\nWork Item: WI-9999\n"
_SPEC_LINKS = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
_TARGET_PATHS = 'target_paths: ["scripts/example.py"]\n'

_SUFFICIENT = "## Requirement Sufficiency\n\nExisting requirements sufficient. Rationale prose here.\n"
_GAP_STATE = (
    "## Requirement Sufficiency\n\nNew or revised requirement required before implementation. Rationale prose here.\n"
)
# Both mutually exclusive operative states asserted in one section. The
# file-bridge-protocol requires EXACTLY ONE; this must be DENIED (WI-3439
# verification NO-GO -008: the prior presence-of-either check wrongly accepted it).
_DUAL_STATE = (
    "## Requirement Sufficiency\n\n"
    "Existing requirements sufficient.\n"
    "New or revised requirement required before implementation.\n"
)


def _load_gate(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=["live", "template"])
def gate(request: pytest.FixtureRequest) -> ModuleType:
    if request.param == "live":
        return _load_gate(LIVE_HOOK, "bcg_req_suff_live")
    return _load_gate(TEMPLATE_HOOK, "bcg_req_suff_template")


def _proposal(
    *,
    status: str = "NEW",
    bridge_kind: str = "prime_proposal",
    requirement_sufficiency: str | None = _SUFFICIENT,
    target_paths: str | None = _TARGET_PATHS,
) -> str:
    """Build a NEW/REVISED bridge proposal body that passes every gate ahead of
    the Requirement Sufficiency check, so that check is the sole variable.

    The fixture uses the canonical ``prime_proposal`` token by default because
    the colloquial ``implementation_proposal`` token is rejected earlier by
    ``_bridge_kind_validation_error`` in the Write-hook path (it is not in the
    BridgeKind enum); predicate coverage of that token is asserted directly
    against ``_bridge_kind_is_implementation_proposal``.
    """
    parts = [status, "", "# Test Proposal", "", _AUTHOR_METADATA, f"bridge_kind: {bridge_kind}", "", _PROJECT_METADATA]
    if target_paths is not None:
        parts.append(target_paths)
    parts.append(_SPEC_LINKS)
    if requirement_sufficiency is not None:
        parts.append("")
        parts.append(requirement_sufficiency)
    return "\n".join(parts)


def _deny(gate: ModuleType, content: str, cwd: Path) -> str | None:
    return gate._deny_reason_for_content(
        cwd_path=cwd,
        file_path="bridge/test-requirement-sufficiency-001.md",
        content=content,
        run_pending_preflight=False,
    )


# --- Acceptance criteria: deny cases --------------------------------------------


def test_missing_requirement_sufficiency_denied(gate: ModuleType, tmp_path: Path) -> None:
    content = _proposal(requirement_sufficiency=None)
    reason = _deny(gate, content, tmp_path)
    assert reason is not None
    assert _MARKER in reason
    assert "Requirement Sufficiency" in reason


def test_placeholder_requirement_sufficiency_denied(gate: ModuleType, tmp_path: Path) -> None:
    content = _proposal(requirement_sufficiency="## Requirement Sufficiency\n\nn/a\n")
    reason = _deny(gate, content, tmp_path)
    assert reason is not None and _MARKER in reason


def test_requirement_sufficiency_without_operative_state_denied(gate: ModuleType, tmp_path: Path) -> None:
    content = _proposal(
        requirement_sufficiency="## Requirement Sufficiency\n\nThe requirements were considered carefully.\n"
    )
    reason = _deny(gate, content, tmp_path)
    assert reason is not None and _MARKER in reason


# --- Acceptance criteria: allow cases -------------------------------------------


def test_substantive_requirement_sufficiency_allowed(gate: ModuleType, tmp_path: Path) -> None:
    content = _proposal(requirement_sufficiency=_SUFFICIENT)
    assert _deny(gate, content, tmp_path) is None


def test_second_operative_state_allowed(gate: ModuleType, tmp_path: Path) -> None:
    # GO constraint 3: the gap-state operative phrase is structurally valid and
    # must remain write-allowed.
    content = _proposal(requirement_sufficiency=_GAP_STATE)
    assert _deny(gate, content, tmp_path) is None


def test_dual_state_requirement_sufficiency_denied(gate: ModuleType, tmp_path: Path) -> None:
    # WI-3439 verification NO-GO -008: the file-bridge-protocol requires EXACTLY
    # ONE operative state. A section that asserts BOTH mutually exclusive states
    # must be DENIED at Write-time. The pre-fix presence-of-either check wrongly
    # accepted this; the state-counting helper now rejects it. Exercised against
    # BOTH hook copies via the parametrized ``gate`` fixture.
    content = _proposal(requirement_sufficiency=_DUAL_STATE)
    reason = _deny(gate, content, tmp_path)
    assert reason is not None and _MARKER in reason
    assert "Requirement Sufficiency" in reason


def test_revised_status_also_gated(gate: ModuleType, tmp_path: Path) -> None:
    # GO constraint 5: the check is gated on the shared NEW/REVISED status set,
    # not hardcoded to NEW.
    content = _proposal(status="REVISED", requirement_sufficiency=None)
    reason = _deny(gate, content, tmp_path)
    assert reason is not None and _MARKER in reason


# --- Acceptance criteria: not-gated cases ---------------------------------------


def test_implementation_report_with_target_paths_not_gated(gate: ModuleType, tmp_path: Path) -> None:
    # GO constraint 2: an implementation_report can be NEW with target_paths and
    # correctly lack ## Requirement Sufficiency; the WI-3439 check must not deny it.
    content = _proposal(bridge_kind="implementation_report", requirement_sufficiency=None)
    reason = _deny(gate, content, tmp_path)
    assert reason is None or _MARKER not in reason


def test_non_implementation_proposal_not_gated(gate: ModuleType, tmp_path: Path) -> None:
    # A proposal that requests no implementation work (no target_paths) is not
    # subject to the Requirement Sufficiency contract.
    content = _proposal(requirement_sufficiency=None, target_paths=None)
    reason = _deny(gate, content, tmp_path)
    assert reason is None or _MARKER not in reason


def test_verdict_files_exempt(gate: ModuleType, tmp_path: Path) -> None:
    # Verdict files (first line GO/NO-GO/VERIFIED) are evidence narratives, not
    # authoring artifacts; the NEW/REVISED status trigger excludes them.
    content = "NO-GO\n\n# Verdict\n\n" + _SPEC_LINKS
    reason = _deny(gate, content, tmp_path)
    assert reason is None or _MARKER not in reason


# --- Direct helper unit tests ---------------------------------------------------


def test_bridge_kind_predicate_covers_both_proposal_tokens(gate: ModuleType) -> None:
    # GO constraint 1: positive predicate for implementation proposals, covering
    # the canonical prime_proposal AND the colloquial implementation_proposal
    # token, while excluding reports/verdicts/advisories.
    assert gate._bridge_kind_is_implementation_proposal("bridge_kind: prime_proposal\n") is True
    assert gate._bridge_kind_is_implementation_proposal("bridge_kind: implementation_proposal\n") is True
    assert gate._bridge_kind_is_implementation_proposal("bridge_kind: implementation_report\n") is False
    assert gate._bridge_kind_is_implementation_proposal("bridge_kind: lo_verdict\n") is False
    assert gate._bridge_kind_is_implementation_proposal("bridge_kind: governance_advisory\n") is False
    assert gate._bridge_kind_is_implementation_proposal("# no bridge_kind line\n") is False


def test_requirement_sufficiency_gap_helper(gate: ModuleType) -> None:
    assert gate._requirement_sufficiency_section_gap("# no section here\n") == "section absent"
    assert gate._requirement_sufficiency_section_gap("## Requirement Sufficiency\n\n## Next\n") == "section empty"
    assert (
        gate._requirement_sufficiency_section_gap("## Requirement Sufficiency\n\nTBD\n") == "section placeholder-only"
    )
    no_op = gate._requirement_sufficiency_section_gap("## Requirement Sufficiency\n\nSome prose with no phrase.\n")
    assert no_op is not None and "operative state" in no_op
    assert (
        gate._requirement_sufficiency_section_gap("## Requirement Sufficiency\n\nExisting requirements sufficient.\n")
        is None
    )
    assert (
        gate._requirement_sufficiency_section_gap(
            "## Requirement Sufficiency\n\nNew or revised requirement required before implementation.\n"
        )
        is None
    )
    # WI-3439 NO-GO -008: both states present is a gap (exactly one required).
    dual = gate._requirement_sufficiency_section_gap(_DUAL_STATE)
    assert dual is not None and "multiple operative states" in dual


def test_shared_status_trigger_constant(gate: ModuleType) -> None:
    # GO constraint 5: the check reuses the project-linkage gate's status set
    # rather than a divergent parser.
    expected_statuses = frozenset({"NEW", "REVISED"})
    expected_kinds = frozenset({"prime_proposal", "implementation_proposal"})
    assert expected_statuses == gate.PROJECT_METADATA_STATUSES
    assert expected_kinds == gate.BRIDGE_KIND_IMPLEMENTATION_PROPOSAL


# --- Deployment parity (GO constraint 6) ----------------------------------------


def test_template_and_active_hook_byte_identical() -> None:
    template_bytes = TEMPLATE_HOOK.read_bytes()
    live_bytes = LIVE_HOOK.read_bytes()
    assert template_bytes == live_bytes, (
        "The .claude/hooks activation copy must be byte-identical to the canonical "
        "groundtruth-kb/templates/hooks source (GO constraint 6)."
    )
