NEW

# Implementation Proposal - WI-5013 SoT Singleton GOV Foundation

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-gov-foundation
Version: 001
Date: 2026-07-04T23:18:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-04T23-08-04Z-prime-builder-A-894f2c
author_model: GPT-5.5 via Codex
author_model_version: current Codex runtime
author_model_configuration: headless bridge auto-dispatch; approval_policy=never; sandbox=workspace-write; model_reasoning_effort=xhigh

Project Authorization: PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA
Project: PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS
Work Item: WI-5013

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/**", ".gtkb-state/sot-singleton-gov-foundation/**", "bridge/gtkb-sot-singleton-gov-foundation-*.md"]

implementation_scope: governance | kb | formal_artifact
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This child proposal implements the first sequenced slice of `WI-5011`: formalize the owner-approved SoT-singleton principle as a GOV-class governance artifact before any platform-wide audit, doctor guard, or duplicate-SoT remediation begins.

The implementation will draft the GOV content, present the exact proposed formal artifact through the formal-artifact approval path, generate the approval packet only after owner approval evidence exists, and then insert the GOV record into MemBase. The GOV must extend the existing SoT governance chain without replacing it:

- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`

This proposal does not authorize the registry-plus-closure audit, the doctor guard, or any duplicate-SoT remediation. Those remain separate child work items under `WI-5014` through `WI-5019`.

## Claim

Prime Builder proposes a bounded governance-foundation implementation for `WI-5013`. The work creates the formal requirement surface needed by later child slices, while preserving bridge review, exact-content owner approval, MemBase insertion, and post-implementation verification gates.

## Requirement Sufficiency

Existing requirements are sufficient for this proposal and for drafting the GOV candidate. Exact-content formal artifact approval is still required before the GOV becomes canonical MemBase truth. If that approval is not present during implementation, the implementation report must record the blocker and stop without mutating `groundtruth.db` or `.groundtruth/formal-artifact-approvals/**`.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`:

- `groundtruth.db`
- `.groundtruth/formal-artifact-approvals/**`
- `.gtkb-state/sot-singleton-gov-foundation/**`
- `bridge/gtkb-sot-singleton-gov-foundation-*.md`

No Agent Red lifecycle-independent repository, out-of-root archive, or harness-local scratchpad is used as authority.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires Prime Builder to file this implementation proposal as `NEW` and wait for Loyal Opposition `GO` before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all operative governing specs to be linked in the implementation proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to carry forward spec-derived verification evidence.
- `GOV-ARTIFACT-APPROVAL-001` - requires full native-format owner approval evidence before creating or updating a GOV-class formal artifact.
- `PB-ARTIFACT-APPROVAL-001` - preserves the Prime Builder-facing formal artifact approval behavior.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - requires approval-packet evidence to bind formal artifact insertion.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - provides the harness-state SoT consolidation precedent this new GOV generalizes.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - provides freshness and declared-TTL cache discipline that the singleton GOV must extend.
- `GOV-PLATFORM-SOT-REGISTRY-001` - establishes the registry declaration surface for authoritative homes and coverage.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires owner decisions, requirements, and future work to remain durable artifact graph entries.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires implementation proposals, specifications, reports, and tests to remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs lifecycle treatment for candidate, active, deferred, and verified artifacts.
- `GOV-STANDING-BACKLOG-001` - governs work-item continuity and follow-on remediation work.
- `SPEC-AUQ-POLICY-ENGINE-001` - controls owner-decision collection and prevents prose-only approval substitution.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform governance work inside the GT-KB root and out of unqualified adopter scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - provides the Codex hook-surface context for proposal/write and read-discipline enforcement.

## Prior Deliberations

- `DELIB-202665441` - owner selected registry-governed authoritative homes and derived-cache semantics: one natural authority per SoT-bearing field, with only regenerated/read-only/TTL-bound/provenance-stamped/non-authoritative derived caches permitted.
- `DELIB-202665444` - owner selected registry-plus-closure coverage for the later audit; this proposal creates the GOV foundation the audit will use.
- `DELIB-202665455` - owner selected risk-first incremental sequencing; `WI-5013` is the governance foundation before audit and guard work.
- `DELIB-2521` - source-of-truth freshness owner decision that existing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` records.
- `bridge/gtkb-sot-singleton-completeness-umbrella-001.md` and `bridge/gtkb-sot-singleton-completeness-umbrella-002.md` - umbrella proposal and GO authorizing child proposal filings while preserving child-level GO gates.

## Owner Decisions / Input

- `DELIB-202665441` - owner approved the authoritative-home and permitted-cache rule used by this child slice.
- `DELIB-202665444` - owner approved the later coverage method; this slice only supplies the foundation for that method.
- `DELIB-202665455` - owner approved risk-first incremental sequencing and active PAUTH scope.
- `PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA` - active project authorization covering `WI-5013` and permitting formal GOV artifact draft/approval-packet work after child bridge `GO`.

No exact-content formal artifact approval has been collected for the new GOV body yet. A future implementation session must obtain or verify that approval before creating the approval packet or mutating `groundtruth.db`.

## Proposed Scope

- Draft a GOV-class specification that states the SoT-singleton principle: every SoT-bearing datum has exactly one persistent authoritative home.
- Define permitted derived caches as regenerated from the authoritative source, read-only to consumers, TTL-bound, provenance-stamped, and explicitly non-authoritative.
- Require authoritative homes to be declared in `config/registry/sot-artifacts.toml` or a GOV-linked registry extension when specialized registry coverage is needed.
- State that persistent duplicate SoT copies are violations even when currently synchronized.
- State that readers must use the authority or an explicitly permitted derived cache for their usage context.
- Generate the exact-content formal artifact approval packet only after owner approval evidence exists.
- Insert the approved GOV record into MemBase with change evidence citing the approval packet and linked owner deliberations.
- Preserve follow-on work boundaries: audit, doctor guard implementation, and duplicate-class remediation remain separate child proposals.

## Out Of Scope

- No registry-plus-closure audit execution. That is `WI-5014`.
- No duplicate-SoT doctor/check implementation. That is `WI-5015`.
- No MemBase/governance, harness/control, bridge/runtime/cache, or narrative/docs audit lane execution. Those are `WI-5016` through `WI-5019`.
- No dispatch self-optimization objective, ranking, selection-binding, or cost-weight mechanics. Those remain under `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION` / `WI-5012`.
- No remediation of discovered duplicate SoT violations.
- No credential lifecycle, production deployment, destructive cleanup, or out-of-root artifact use.

## Specification-Derived Verification Plan

| Specification | Verification Evidence Required In Implementation Report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show live latest `GO` for this child thread before implementation and include the implementation-start packet command/result. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm `Project Authorization`, `Project`, `Work Item`, and `target_paths` remain parseable in this proposal and in the filed bridge artifact. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-gov-foundation` after filing; expected missing required/advisory specs are empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands and observed results. |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Verify the exact-content formal approval packet exists, validates, and binds to the GOV content before insertion. Use `groundtruth-kb/.venv/Scripts/gt.exe generate-approval-packet ... --validate-after --json` or the current governed equivalent, then run `groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py <packet>`. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | Inspect the GOV text to confirm it generalizes the harness-state precedent without changing the three harness-state authoritative homes or dispatch project scope. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Inspect the GOV text for explicit regenerated/read-only/TTL/provenance/non-authoritative derived-cache semantics and no speculative cache permission. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Run `groundtruth-kb/.venv/Scripts/gt.exe registry validate --json`; expected result is no registry/projection divergence introduced by this slice. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the GOV record, approval packet, bridge proposal, implementation report, and later LO verdict form a durable traceable artifact chain. |
| `GOV-STANDING-BACKLOG-001` | Confirm this slice does not silently resolve or reorder `WI-5014` through `WI-5019`; follow-on remediation remains in the MemBase backlog. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Confirm any exact-content owner approval is recorded through the governed owner-decision path and cited in the approval packet. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm all mutated artifacts remain under `E:\GT-KB` and no unqualified Agent Red repository or CI surface is used. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Report whether Codex hook/compliance checks or helper-mediated bridge writes were used for this Codex session. |

## Acceptance Criteria

- A new or updated GOV-class specification exists in MemBase only after exact-content formal artifact approval evidence exists.
- The GOV text states singleton SoT semantics and permitted derived-cache semantics in machine-checkable terms.
- The GOV extends, but does not supersede, `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, and `GOV-PLATFORM-SOT-REGISTRY-001`.
- The implementation report includes the approval packet path, validation result, MemBase insertion/update evidence, and registry validation evidence.
- No audit, doctor guard, or duplicate-class remediation work is bundled into this slice.

## Risks / Rollback

The primary risk is accidentally treating bridge `GO` as a replacement for exact-content formal artifact approval. This proposal prevents that by making the approval packet a precondition for `groundtruth.db` mutation.

The second risk is over-broad scope creep into audit or remediation. This proposal confines the implementation to governance formalization and leaves all audit, guard, and remediation activity to child work items with their own bridge gates.

Rollback for an approved implementation is a governed MemBase supersession/update or retirement proposal for the GOV record plus removal or supersession of any generated approval packet only through the applicable formal artifact process. Bridge files remain append-only audit artifacts and are not deleted.

## Files Expected To Change

- `groundtruth.db`
- `.groundtruth/formal-artifact-approvals/**`
- `.gtkb-state/sot-singleton-gov-foundation/**`
- `bridge/gtkb-sot-singleton-gov-foundation-*.md`

## Pre-Filing Checks

Prime Builder will run the proposal applicability preflight and ADR/DCL clause preflight against this completed draft before filing, then rerun live preflights after filing.

## Recommended Commit Type

`feat`

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
