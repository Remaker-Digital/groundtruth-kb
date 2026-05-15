"""Tests for the bridge-compliance-gate project-linkage metadata clause (WI-3314).

Covers 3 of the 4 clauses of DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001:
- CLAUSE-PROJECT-METADATA-PRESENT: NEW/REVISED implementation proposals must
  carry Project Authorization / Project / Work Item metadata lines.
- CLAUSE-VERDICT-FILES-EXCLUDED: GO/NO-GO/VERIFIED/WITHDRAWN verdict files are
  not subject to the metadata check.
- CLAUSE-NON-IMPLEMENTATION-EXEMPT: bridge_kind in {spec_intake,
  governance_review, loyal_opposition_advisory} exempts the proposal.

CLAUSE-PROJECT-AUTH-LIVE-CHECK is deferred to WI-3315 and is NOT tested here.

New test surface (per bridge/gtkb-bridge-compliance-project-metadata-005.md
REVISED-2, GO at -006). Does not regress
test_bridge_compliance_gate_hard_block_workspace.py.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_gate():
    """Import the hyphenated hook module by path."""
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate", ACTIVE_HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gate = _load_gate()

# A complete-enough NEW proposal body: has Specification Links (so the spec-links
# check passes), no owner-approval markers (so the owner-decisions check does not
# fire), so the project-metadata clause is the only variable under test.
_SPEC_LINKS_SECTION = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"

_META_AUTH = "Project Authorization: PAUTH-TEST-PROJECT-X\n"
_META_PROJECT = "Project: PROJECT-TEST-X\n"
_META_WI = "Work Item: WI-9999\n"


def _proposal(status: str, *, metadata: str, bridge_kind: str | None = None) -> str:
    parts = [status, "", "# Test Proposal", ""]
    if bridge_kind is not None:
        parts.append(f"bridge_kind: {bridge_kind}")
    parts.append(metadata.rstrip("\n"))
    parts.append("")
    parts.append(_SPEC_LINKS_SECTION)
    return "\n".join(parts)


def _deny(content: str) -> str | None:
    return _gate._deny_reason_for_content(
        cwd_path=REPO_ROOT,
        file_path="bridge/test-project-metadata-001.md",
        content=content,
        run_pending_preflight=False,
    )


_METADATA_CLAUSE = "CLAUSE-PROJECT-METADATA-PRESENT"


# --- CLAUSE-PROJECT-METADATA-PRESENT (blocked cases) ----------------------------

def test_bridge_proposal_missing_project_authorization_line_blocked() -> None:
    content = _proposal("NEW", metadata=_META_PROJECT + _META_WI)
    reason = _deny(content)
    assert reason is not None and _METADATA_CLAUSE in reason
    assert "Project Authorization:" in reason


def test_bridge_proposal_missing_project_line_blocked() -> None:
    content = _proposal("NEW", metadata=_META_AUTH + _META_WI)
    reason = _deny(content)
    assert reason is not None and _METADATA_CLAUSE in reason
    assert "Project:" in reason


def test_bridge_proposal_missing_work_item_line_blocked() -> None:
    content = _proposal("NEW", metadata=_META_AUTH + _META_PROJECT)
    reason = _deny(content)
    assert reason is not None and _METADATA_CLAUSE in reason
    assert "Work Item:" in reason


def test_bridge_proposal_all_three_metadata_lines_passes() -> None:
    content = _proposal("NEW", metadata=_META_AUTH + _META_PROJECT + _META_WI)
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


def test_bridge_proposal_metadata_accepts_wi_gtkb_worklist_id_formats() -> None:
    for wi_value in ("WI-9999", "GTKB-SOME-THING-001", "WORKLIST-A-B-C"):
        metadata = _META_AUTH + _META_PROJECT + f"Work Item: {wi_value}\n"
        content = _proposal("NEW", metadata=metadata)
        reason = _deny(content)
        assert reason is None or _METADATA_CLAUSE not in reason, (
            f"Work Item id format {wi_value} should be accepted"
        )


# --- CLAUSE-VERDICT-FILES-EXCLUDED ----------------------------------------------

def test_verdict_file_go_no_metadata_passes() -> None:
    # GO verdict file with no metadata: metadata clause must not fire.
    content = "GO\n\n# Verdict\n\n" + _SPEC_LINKS_SECTION
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


def test_verdict_file_verified_no_metadata_passes() -> None:
    content = "VERIFIED\n\n# Verdict\n\n" + _SPEC_LINKS_SECTION
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


def test_verdict_file_no_go_no_metadata_passes() -> None:
    content = "NO-GO\n\n# Verdict\n\n" + _SPEC_LINKS_SECTION
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


def test_verdict_file_withdrawn_no_metadata_passes() -> None:
    content = "WITHDRAWN\n\n# Withdrawal note\n\n" + _SPEC_LINKS_SECTION
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


# --- CLAUSE-NON-IMPLEMENTATION-EXEMPT -------------------------------------------

def test_bridge_kind_spec_intake_no_metadata_passes() -> None:
    content = _proposal("NEW", metadata="", bridge_kind="spec_intake")
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


def test_bridge_kind_loyal_opposition_advisory_no_metadata_passes() -> None:
    content = _proposal("NEW", metadata="", bridge_kind="loyal_opposition_advisory")
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


def test_bridge_kind_governance_review_no_metadata_passes() -> None:
    content = _proposal("NEW", metadata="", bridge_kind="governance_review")
    reason = _deny(content)
    assert reason is None or _METADATA_CLAUSE not in reason


# --- Regression guard: an implementation-kind proposal is NOT exempt ------------

def test_bridge_kind_implementation_proposal_still_gated() -> None:
    # A non-exempt bridge_kind must still require the metadata lines.
    content = _proposal("NEW", metadata="", bridge_kind="implementation_proposal")
    reason = _deny(content)
    assert reason is not None and _METADATA_CLAUSE in reason
