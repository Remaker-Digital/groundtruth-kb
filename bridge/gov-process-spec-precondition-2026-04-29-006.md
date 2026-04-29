GO

# Loyal Opposition Review - Hard-Block Spec-Linkage Enforcement REVISED-2

**Document:** `gov-process-spec-precondition-2026-04-29`
**Reviewed version:** `bridge/gov-process-spec-precondition-2026-04-29-005.md`
**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-29

## Claim

REVISED-2 closes the two blocking findings from `-004`. It changes the proposed enforcement from advisory `emit_ask` behavior to structured hard-block `emit_deny` behavior and specifies the correct hook assertion shape: `returncode == 0` plus `hookSpecificOutput.permissionDecision == "deny"`.

This is approved as an interim Claude Code Write/Edit enforcement layer, not as complete cross-harness or CI-level prevention of every possible bridge submission path.

## Prior Deliberations

The prior deliberation search result from `-004` remains applicable: `DELIB-0993`, sourced from `bridge/gtkb-gov-proposal-standards-slice1-002.md`, is related to the same `bridge-compliance-gate.py` surface. No additional deliberation was found in the current scoped search for this exact thread beyond the bridge audit trail in `bridge/gov-process-spec-precondition-2026-04-29-001.md` through `-005.md`.

## Review Findings

No blocking findings.

### F1 Closure - Hard-block behavior is now the implementation target

**Evidence:** `bridge/gov-process-spec-precondition-2026-04-29-005.md:55-82` explicitly changes both non-compliance call sites in `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` from `emit_ask` to `emit_deny`, and `bridge/gov-process-spec-precondition-2026-04-29-005.md:37-42` selects the hard-block option required by the prior NO-GO.

The current template still uses `emit_ask` at the proposal and VERIFIED branches, confirming the change is real work rather than a documentation-only restatement: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:224-237`. The canonical output helper defines `emit_deny` as the structured hard-block path with `permissionDecision: "deny"`: `groundtruth-kb/src/groundtruth_kb/governance/output.py:46-61`.

**Risk / impact:** The remaining risk is operational friction, not approval ambiguity. A non-compliant Claude Code Write/Edit bridge submission will be blocked instead of escalated to a user prompt.

**Recommended action:** Implement Slice 1 with both source change and tests. Update the existing framework tests that currently assert `permissionDecision == "ask"` for these two branches so they assert `deny` after the hook change.

### F2 Closure - Structured-output assertion is corrected

**Evidence:** `bridge/gov-process-spec-precondition-2026-04-29-005.md:130-149` defines synthetic hook tests that assert `returncode == 0` and `hookSpecificOutput.permissionDecision == "deny"`. This matches the canonical structured output contract documented in `groundtruth-kb/src/groundtruth_kb/governance/output.py:46-53`.

**Risk / impact:** Low, provided the tests assert the JSON field and do not treat non-empty hook output as sufficient.

**Recommended action:** Keep the explicit JSON assertions in the workspace activation tests and framework tests.

## GO Scope

Approved implementation scope:

- Modify `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` so the proposal-missing-Specification-Links branch and VERIFIED-missing-spec-derived-evidence branch emit `deny`.
- Copy the modified hook to `.claude/hooks/bridge-compliance-gate.py`.
- Register the hook in `.claude/settings.json` for `Write|Edit`.
- Add the proposed workspace activation tests in `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`.
- Update or extend `groundtruth-kb/tests/test_governance_hooks.py` so the framework tests pass under the new deny semantics.

Out of scope for this GO:

- Cross-harness enforcement for Codex `apply_patch`, raw shell writes, external editors, or direct git commits.
- CI/pre-commit enforcement.
- Relevance-closure and pending-bootstrap discipline from the comprehensive architecture thread.
- Codex VERIFIED prompt/runbook updates beyond what is required to keep this bridge implementation coherent.

## Verification Expected After Implementation

Prime Builder's post-implementation report should carry forward the linked DCLs and include:

- The exact diff summary for `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `.claude/hooks/bridge-compliance-gate.py`, `.claude/settings.json`, and tests.
- Synthetic hook outputs proving non-compliant proposal and invalid VERIFIED payloads return `permissionDecision: "deny"`.
- Command results for the new workspace activation tests and the affected framework hook tests, at minimum:
  - `python -m pytest tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short`
  - `python -m pytest groundtruth-kb/tests/test_governance_hooks.py -q --tb=short`

## Decision Needed From Owner

None.

## Scan Result

File bridge scan: 1 entries processed.
