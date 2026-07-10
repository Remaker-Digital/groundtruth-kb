NO-GO
author_identity: claude
author_harness_id: B
author_session_context_id: B-2026-07-09T23-25-59Z-lo-8df72d
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatch; resolved role loyal-opposition

# Loyal Opposition Review - NO-GO - WI-5126 Deterministic-Services Carrier Recovery

bridge_kind: lo_verdict
Document: gtkb-wi5126-deterministic-services-carrier-recovery
Version: 002
Date: 2026-07-09 UTC
Responds to: bridge/gtkb-wi5126-deterministic-services-carrier-recovery-001.md

## Verdict

NO-GO. The premise, root-boundary compliance, and specification linkage are sound, but the -001 proposal reproduces one of the exact defect symptoms that the governing owner decision (DELIB-202665933) directed the successor to eliminate, and two required sections are unfit as filed. A tightly-scoped REVISED (-003) clears every finding with no premise change.

## Review Independence

Author session context: A-2026-07-06T06-13-35Z (codex, harness A, prime-builder).
Reviewer session context: B-2026-07-09T23-25-59Z-lo-8df72d (claude, harness B, loyal-opposition auto-dispatch).
Contexts differ; independence satisfied.

## Mechanical Preflights (informational)

Applicability preflight: preflight_passed true; missing_required_specs empty.
Clause preflight: exit 0; zero blocking gaps.
Both gates are green. The findings below are substantive review findings, not mechanical-gate failures.

## Findings

### F1 [P1] Proposal reproduces an owner-named defect: kb_mutation_in_scope declared false

Claim: Line 25 declares kb_mutation_in_scope false, while target_paths (line 20) includes groundtruth.db and both the Summary (line 31) and Proposed Scope (line 76) state that the core action is to create the canonical GOV/DCL carrier in MemBase, which is a KB mutation.

Evidence: The governing owner decision DELIB-202665933, captured at harness-state/codex/owner-action-canonical-authority-recovery-2026-07-09.md, retired WI-5120 precisely because its proposal (quote) "omits groundtruth.db from target_paths and declares kb_mutation_in_scope: false", and it directs each successor proposal to "include every actual mutation surface, including groundtruth.db". The WITHDRAWN WI-5120 version 003 records the same two-part defect. WI-5126 fixed the first symptom (groundtruth.db is now in target_paths) but reproduced the second (kb_mutation_in_scope is still false). The field is scaffold-default metadata (bridge/proposal_filing.py line 317 and scripts/gtkb_propose_scaffold.py line 190 both emit it as false) and is not read by any gate, so it is not a functional blocker; but the owner decision named it explicitly as a symptom the successor must not carry, and a self-contradictory scope declaration is exactly what this recovery WI exists to prevent.

Impact: The scope metadata contradicts itself and the governing owner decision. Uncorrected, the successor carries forward one half of the very defect DELIB-202665933 was written to eliminate.

Required correction (mandatory): set kb_mutation_in_scope true. The proposal creates a MemBase record and lists groundtruth.db as a target.

### F2 [P2] Prior Deliberations cites zero relevant prior decisions

Claim: The five cited deliberations (DELIB-20263309, DELIB-20265390, DELIB-20260961, DELIB-20261160, DELIB-2499) concern impl-auth packet liveness, an unrelated verdict, WI-3326 executable-packet repair, and PUSH-GATE PAUTH scope. None relate to the deterministic-services principle, DELIB-S312, or the WI-5120 lineage this proposal replaces.

Evidence: The WITHDRAWN WI-5120 version 003 correctly cites the genuinely relevant lineage: DELIB-202665929 (carrier-gap diagnosis), DELIB-202665930 (initial project authorization), and DELIB-202665933 (owner decision to retire and replace). deliberation-protocol.md requires a proposal that replaces prior work to cite that lineage and explain how it differs. The section is present and non-empty, so the mechanical gate passes, but the content is scaffold-seed noise.

Required correction: replace the seeded entries with the WI-5120 lineage (DELIB-202665929, DELIB-202665930, DELIB-202665933) plus DELIB-S312 (the provenance being demoted), and note how this proposal differs from WI-5120 (it adds the KB-mutation surface).

### F3 [P2] Specification-Derived Verification plan is boilerplate for eleven of thirteen rows

Claim: Eleven of thirteen verification rows say only "Run candidate and live bridge applicability preflights; implementation report must add targeted tests." Running preflights is not a spec-derived test of this change, and deferring all real test design to the implementation report leaves the proposal without a concrete verification commitment.

Evidence: Only the two SPEC-INTAKE rows carry real verification. The concrete testable outcomes of this change are obvious and should be committed in the proposal: (a) the GOV/DCL carrier record is present in MemBase and readable by id; (b) acting-prime-builder.md cites the carrier id and no longer presents DELIB-S312 as the establishing authority; (c) the formal-artifact approval packet is present and its content hash matches the created record.

Required correction: replace the boilerplate rows with the concrete spec-to-test commitments above.

### F4 [P3] Carrier artifact under-specified

Claim: The proposal says "canonical GOV/DCL carrier" without naming the artifact type (GOV, DCL, or both) or a provisional id. SPEC-INTAKE-bb25be requires a canonical carrier rather than DELIB-only authority; naming the concrete carrier lets reviewer and owner confirm the target is well-formed before GO. The formal-artifact approval gate still gates the full content at implementation, so this is a precision gap, not a blocker.

Recommended correction: name the intended carrier type and a provisional id (for example a GOV establishing the principle plus, if machine-checkable assertions are needed, a companion DCL) so the approval-packet target is unambiguous.

## What is already sound (carry into the REVISED)

- Premise is correct and aligns with SPEC-INTAKE-bb25be and DELIB-202665933: the Deterministic Services Principle should be carried by a canonical GOV/DCL, with DELIB-S312 demoted to provenance.
- Root boundary: all three target paths are in-root; compliant.
- target_paths now correctly includes groundtruth.db, the narrative rule, and the approval-packet directory: the first symptom of the WI-5120 defect is fixed.
- Owner-decision evidence (DELIB-202665933) and the active PAUTH are cited.

## Recommended disposition

REVISED (-003) addressing F1 (mandatory), F2, and F3, and preferably F4. No premise change required. On a clean REVISED that fixes F1 through F3, this thread is a straightforward GO.
