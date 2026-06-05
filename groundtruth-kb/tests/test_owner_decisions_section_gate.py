"""Tests for Sub-slice C: bridge-compliance-gate Owner Decisions / Input section check.

Per
bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-003.md
(Codex GO at -004): conditional gate fires only when proposal/report content
indicates owner-approval scope. Verdict files (GO/NO-GO/VERIFIED) are excluded
per Codex -004 condition (verdict files are evidence narratives, not approval
claims).

Hermetic by construction: synthetic content + subprocess invocation; no live
state mutation per Sub-slice A's -012 hermetic-isolation lesson.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _run_hook(file_path: str, content: str, cwd: str | None = None) -> dict:
    """Invoke bridge-compliance-gate.py as subprocess; return parsed stdout JSON."""
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": file_path, "content": content},
            "session_id": "test-slice-c",
            "cwd": cwd or str(REPO_ROOT),
        }
    )
    env = dict(os.environ)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


# Synthetic proposal claiming owner-approval (cites Sub-slice B's VERIFIED rule)
# AND lacks Owner Decisions / Input section. Includes Spec Links + spec-derived
# test plan to satisfy the prior gates so we test the new gate in isolation.
PROPOSAL_CLAIMS_NO_SECTION = """NEW

# Test Proposal Claiming Owner Approval Without Section

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001
- bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md

## Specification-Derived Verification Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| T-x | spec-to-test mapping | python -m pytest test.py | PASS |

VERIFIED contingent on test execution.
"""

PROPOSAL_CLAIMS_WITH_SECTION = (
    PROPOSAL_CLAIMS_NO_SECTION
    + """
## Owner Decisions / Input

Owner approval cited from S331 AskUserQuestion answer "Autonomous progression"
authorizing this sub-slice under standard lifecycle.
"""
)

PROPOSAL_CLAIMS_WITH_SECTION_AND_NONE_STATUS = (
    PROPOSAL_CLAIMS_NO_SECTION
    + """
## Owner Decisions / Input

- Owner approval cited from S331 AskUserQuestion answer "Autonomous progression".
- Current owner input needed: none.
"""
)

# Routine proposal that does NOT claim owner-approval scope (no AUQ markers,
# no Sub-slice B citation).
PROPOSAL_NO_CLAIM = """NEW

# Routine Refactor Proposal

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001

## Specification-Derived Verification Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| T-x | spec-to-test mapping | python -m pytest test.py | PASS |
"""

# Verdict file that mentions AUQ in its evidence narrative (per Codex -004
# condition: must NOT be blocked even though AUQ markers present).
VERDICT_GO_DISCUSSING_AUQ = """GO

# Loyal Opposition Review

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001

## Applicability Preflight
- packet_hash: `sha256:0000000000000000000000000000000000000000000000000000000000000000`
- preflight_passed: `true`
- missing_required_specs: []

## Verdict

GO. The proposal cites Sub-slice B's AUQ-only rule and the AskUserQuestion
answer "Autonomous progression" provides owner authorization. Approval is
sufficient.
"""


def _write_claim(tmp_path: Path, thread_slug: str, session_id: str = "test-slice-c") -> None:
    intent_dir = tmp_path / ".gtkb-state" / "work-intent"
    intent_dir.mkdir(parents=True, exist_ok=True)
    import datetime

    now = datetime.datetime.now(datetime.UTC)
    expiry = now + datetime.timedelta(seconds=60)
    record = {
        "session_id": session_id,
        "acquired_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ttl_expires_at": expiry.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (intent_dir / f"{thread_slug}.json").write_text(json.dumps(record), encoding="utf-8")


def test_hook_blocks_proposal_claiming_approval_without_section(tmp_path):
    """T-hook-blocks-missing: proposal claims owner approval but lacks section -> deny."""
    _write_claim(tmp_path, "test-fixture")
    out = _run_hook("bridge/test-fixture-001.md", PROPOSAL_CLAIMS_NO_SECTION, cwd=str(tmp_path))
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
    reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    assert decision == "deny", f"Expected deny; got {decision!r} (reason: {reason[:200]!r})"
    assert "Owner Decisions" in reason, f"Expected reason to mention Owner Decisions; got: {reason[:300]!r}"


def test_hook_allows_proposal_claiming_approval_with_section(tmp_path):
    """T-hook-allows-present: proposal claims approval AND has substantive section -> not blocked on this check."""
    _write_claim(tmp_path, "test-fixture")
    out = _run_hook("bridge/test-fixture-002.md", PROPOSAL_CLAIMS_WITH_SECTION, cwd=str(tmp_path))
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
    reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    if decision == "deny":
        assert "Owner Decisions" not in reason, (
            f"Owner Decisions check should NOT fire when section is present; got reason: {reason[:300]!r}"
        )


def test_hook_allows_substantive_owner_decisions_section_with_none_status(tmp_path):
    """A substantive section remains valid when it also says no current input is needed."""
    _write_claim(tmp_path, "test-fixture")
    out = _run_hook("bridge/test-fixture-002b.md", PROPOSAL_CLAIMS_WITH_SECTION_AND_NONE_STATUS, cwd=str(tmp_path))
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
    reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    if decision == "deny":
        assert "Owner Decisions" not in reason, (
            f"Owner Decisions check should NOT treat a substantive section as placeholder-only; got: {reason[:300]!r}"
        )


def test_hook_does_not_fire_on_non_claiming_proposal(tmp_path):
    """T-hook-skips-non-claiming: routine proposal -> Owner Decisions check inactive."""
    _write_claim(tmp_path, "test-fixture")
    out = _run_hook("bridge/test-fixture-003.md", PROPOSAL_NO_CLAIM, cwd=str(tmp_path))
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
    reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    if decision == "deny":
        assert "Owner Decisions" not in reason, (
            f"Owner Decisions check should NOT fire on non-claiming proposal; got: {reason[:300]!r}"
        )


def test_hook_skips_verdict_files_per_codex_minus_004_condition(tmp_path):
    """Per Codex -004 condition: verdict files (GO/NO-GO/VERIFIED) excluded from gate even when discussing AUQ."""
    _write_claim(tmp_path, "test-fixture")
    out = _run_hook("bridge/test-fixture-004.md", VERDICT_GO_DISCUSSING_AUQ, cwd=str(tmp_path))
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
    reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    if decision == "deny":
        assert "Owner Decisions" not in reason, (
            f"Owner Decisions check must NOT fire on verdict files (per Codex -004 condition); got: {reason[:300]!r}"
        )
