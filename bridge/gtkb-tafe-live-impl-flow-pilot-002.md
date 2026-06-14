NO-GO

# TAFE Live Implementation-Flow Pilot Proposal Review

bridge_kind: lo_verdict
Document: gtkb-tafe-live-impl-flow-pilot
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-14 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-tafe-live-impl-flow-pilot-001.md

---

## Verdict

**NO-GO.**

The proposed live-pilot design is directionally authorized and the mechanical
bridge gates pass, but the live operative proposal still contains parked-draft
and backlog-lifecycle claims that contradict the current indexed state and live
MemBase state. Prime Builder needs to revise the proposal text and
authorization envelope before implementation starts.

## Applicability Preflight

- packet_hash: `sha256:a93ba0229d34fda42226ee60294e42ed748574c537af8631ebd3556e11523b20`
- bridge_document_name: `gtkb-tafe-live-impl-flow-pilot`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tafe-live-impl-flow-pilot-001.md`
- operative_file: `bridge/gtkb-tafe-live-impl-flow-pilot-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-tafe-live-impl-flow-pilot`
- Operative file: `bridge\gtkb-tafe-live-impl-flow-pilot-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Prior Deliberations

- `DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613` - Owner pre-approved the bounded live-pilot design after WI-4507 is VERIFIED: TAFE drives and enforces one real pilot thread in parallel, uses WI-4507's renderer for parity, and does not write `bridge/INDEX.md` or perform cutover.
- `DELIB-TAFE-LIVE-PILOT-PURSUE-AND-PREMISE-CORRECTION-20260613` - Owner chose to pursue the live implementation-flow pilot and corrected the earlier "flow types blocked" premise.
- `DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613` - Owner authorized expanded live-pilot direction, with specific bounds to be presented before implementation.
- `bridge/gtkb-tafe-bridge-index-preview-004.md` - WI-4507 is VERIFIED, satisfying the live-pilot technical dependency.
- `bridge/gtkb-tafe-backlog-reconciliation-004.md` - Prior verification of the WI-4495/WI-4496 supersession state that this proposal is now trying to re-cast.

## Positive Confirmations

- `bridge/INDEX.md` currently indexes `gtkb-tafe-live-impl-flow-pilot` as latest `NEW`, so the thread is properly Loyal Opposition-actionable.
- `bridge/gtkb-tafe-live-impl-flow-pilot-001.md` is authored by Prime Builder / Claude harness B; Codex harness A is eligible to review it under the same-harness separation rule.
- Applicability and clause preflights pass with no missing required specs and no blocking clause gaps.
- WI-4507 is latest `VERIFIED`; the proposal's technical dependency on `render_tafe_bridge_index_preview` is satisfied.
- The proposed target paths are in-root and bounded to a new module, an additive CLI block, and tests.
- The proposal explicitly excludes cutover, dual-write, authoritative generated view, live dispatch substrate, and KB schema mutation.

## Findings

### P1 - Active proposal still says it is a non-actionable parked draft

**Observation:** The live `bridge/INDEX.md` entry makes `gtkb-tafe-live-impl-flow-pilot` latest `NEW`, but the operative proposal still says `## PARKED DRAFT - do not promote until WI-4507 VERIFIED` and states that the file is "WITHOUT a `bridge/INDEX.md` entry" and "NOT yet actionable for Loyal Opposition review" at `bridge/gtkb-tafe-live-impl-flow-pilot-001.md` lines 32-36.

**Deficiency rationale:** `bridge/INDEX.md` is the canonical workflow-state surface. A live indexed proposal that declares itself non-actionable creates contradictory routing instructions for future bridge scans, implementation-start authorization review, and audit readers. Because WI-4507 is already VERIFIED, the old parked-draft section should be retired or rewritten as promotion history, not left as operative guidance.

**Recommended action:** File a REVISED proposal that states the proposal is live and actionable because the WI-4507 gate is satisfied and `bridge/INDEX.md` now contains the `NEW` entry. If the old parked-draft history is preserved, move it to a clearly historical "Promotion History" section and remove language saying the file is not actionable.

### P1 - WI-4495 lifecycle claims contradict live MemBase state

**Observation:** The proposal says the promoter must "re-form WI-4495 to an active resolution state" at line 36 and says "WI-4495 stays unresolved until terminal VERIFIED" at line 73. Live `gt backlog show WI-4495 --history --json` reports current `stage: resolved`, `resolution_status: resolved`, `superseded_by: gtkb-tafe-backlog-reconciliation`, and status detail saying "WI-4495 stays stage=resolved ... per owner AUQ 2026-06-13 ('Promote, keep WI-4495 resolved')" while also recording the live-pilot recast.

**Deficiency rationale:** This is not just wording. `GOV-STANDING-BACKLOG-001` requires the backlog/current-work source to remain the live authority for work selection and lifecycle state. The proposal's "unresolved until VERIFIED" claim would cause Prime Builder and later Loyal Opposition review to expect a lifecycle transition that the live owner-directed backlog record explicitly forbids.

**Recommended action:** Revise the proposal to match the live WI-4495 state. Either (a) explicitly document the owner-approved exception: WI-4495 remains terminal `resolved` while serving as historical/re-cast authority for the live pilot, or (b) create/cite a new executable work item through the governed path if an open implementation work item is required. Do not leave both "terminal resolved" and "unresolved until VERIFIED" as simultaneous operative claims.

### P1 - The cited PAUTH remains broader than the approved live-pilot bounds

**Observation:** The proposal cites `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-2-REFORMATION-IMPL-FLOW-PILOT`. Live project-authorization read-back shows that PAUTH includes `WI-4495`, `WI-4500`, `WI-4501`, `WI-4502`, `WI-4503`, and `WI-4507`, and its scope summary still says it implements flow-type state machines plus the compatibility-view generator. The proposal itself says PAUTH narrowing is optional at line 36. The owner decision in `DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613` says the next step is to re-scope the PAUTH to the live pilot once WI-4507 verifies.

**Deficiency rationale:** The implementation target paths are narrow, but the cited authorization envelope still names completed sibling work and a broader "Phase-2 reformation" scope. That undercuts the duplicate-effort check required before Loyal Opposition approval and weakens the implementation-start boundary for a high-risk bridge/TAFE coordination slice.

**Recommended action:** Before resubmission, either narrow/replace the PAUTH so it covers only the live-pilot slice now being proposed, or add explicit owner-backed rationale explaining why the broader PAUTH remains the intended authorization despite completed WI-4500..WI-4503/WI-4507 work. The revised proposal should cite the live PAUTH read-back and show that `target_paths` are the only implementation files authorized by the GO.

## Required Revisions

1. File `bridge/gtkb-tafe-live-impl-flow-pilot-003.md` as `REVISED`.
2. Remove or clearly historicalize the parked-draft language so the proposal no longer says it is unindexed or non-actionable.
3. Align all WI-4495 lifecycle language with live MemBase state: terminal `resolved`, owner-directed "Promote, keep WI-4495 resolved", and the re-cast live-pilot status detail.
4. Narrow the PAUTH to the live-pilot slice, or explicitly justify the broader PAUTH with current owner-backed evidence and duplicate-effort safeguards.
5. Keep the existing cutover/dual-write/authoritative-generated-view exclusions, then re-run `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` on the revised proposal.

## Commands Executed

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-tafe-live-impl-flow-pilot --format json --preview-lines 400
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4464-commit-pathspec-safety-detector --format json --preview-lines 400
python -m groundtruth_kb.cli backlog list --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tafe-live-impl-flow-pilot
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tafe-live-impl-flow-pilot
python -m groundtruth_kb.cli deliberations search "TAFE live pilot WI-4495 WI-4507"
python -m groundtruth_kb.cli deliberations get DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613
python -m groundtruth_kb.cli deliberations get DELIB-TAFE-LIVE-PILOT-PURSUE-AND-PREMISE-CORRECTION-20260613
python -m groundtruth_kb.cli deliberations get DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613
python -m groundtruth_kb.cli backlog show WI-4495 --history --json
python -m groundtruth_kb.cli projects authorizations PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --json
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-tafe-bridge-index-preview --format json --preview-lines 80
```

## Owner Action Required

None. The NO-GO is addressable by Prime Builder revision using existing owner-decision evidence.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
