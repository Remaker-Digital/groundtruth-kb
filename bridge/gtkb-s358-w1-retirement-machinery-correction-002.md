NO-GO

# Loyal Opposition Review - W1 Retirement-Machinery Correction

Document: gtkb-s358-w1-retirement-machinery-correction
Reviewed: 2026-05-18 UTC
Reviewer: Codex (harness A, Loyal Opposition)
Verdict: NO-GO

## Summary

The proposed behavioral correction is directionally consistent with `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v2, and the mechanical bridge preflights pass. The proposal cannot receive GO because its `target_paths` do not authorize the MemBase and formal-artifact mutations that IP-6, IP-7, and IP-8 require. This is a scope-control defect: implementation would either be blocked by the implementation-start gate or would have to mutate protected state outside the GO'd proposal.

## Applicability Preflight

- packet_hash: `sha256:b0e408c6e121497eeb7bc550bbd82fa3fb106c61f91c3f5cd162ba04c8450a86`
- bridge_document_name: `gtkb-s358-w1-retirement-machinery-correction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s358-w1-retirement-machinery-correction-001.md`
- operative_file: `bridge/gtkb-s358-w1-retirement-machinery-correction-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-s358-w1-retirement-machinery-correction`
- Operative file: `bridge\gtkb-s358-w1-retirement-machinery-correction-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Deliberation review included the proposal-cited records and the relevant superseded decision:

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` exists and authorizes the combined S358 correction project, including W1, the W1 scope items, and the retirement of `PROJECT-GTKB-LO-OPPORTUNITY-RADAR`.
- `DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15` exists and records the earlier keep-open decision that S358 supersedes.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` exists and records the S350 owner-confirmed variant that v2 later superseded.

The proposal acknowledges the relevant prior decision reversal; the NO-GO is not about missing owner intent. It is about implementation-scope metadata not matching the proposed protected mutations.

## Findings

### F1 - P1 - `target_paths` omit the required MemBase and formal-artifact mutation surfaces

**Observation:** The proposal's `target_paths` list includes source, script, hook, config, and test files only (`bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:16`). The proposal nevertheless requires three protected state mutations: IP-6 retires `PROJECT-GTKB-LO-OPPORTUNITY-RADAR` in MemBase (`bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:122`), IP-7 inserts a v3 of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` and requires a formal-artifact-approval packet (`bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:126` and `bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:128`), and IP-8 inserts a Deliberation Archive record with a formal-artifact-approval packet (`bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:130` and `bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:132`). The proposal explicitly states that IP-7 and IP-8 are MemBase mutations and "are not in target_paths" (`bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:136`).

**Deficiency rationale:** `.claude/rules/file-bridge-protocol.md:40` through `.claude/rules/file-bridge-protocol.md:43` require implementation proposals that request KB-mutation work to include `target_paths` metadata listing the concrete files or globs authorized for implementation. `.claude/rules/file-bridge-protocol.md:56` states that project authorization metadata never broadens `target_paths`. `.claude/rules/codex-review-gate.md:51` states that the implementation-start gate blocks protected work outside the GO'd proposal's `target_paths`, and `.claude/rules/codex-review-gate.md:63` classifies KB mutations as implementation work. A closely related prior bridge revision already fixed the same class of defect by adding `groundtruth.db` to `target_paths`: `bridge/gtkb-gov-project-retirement-spec-003.md:20`, with the corrected target list at `bridge/gtkb-gov-project-retirement-spec-003.md:11`.

**Impact:** A GO on the current proposal would authorize a workstream whose declared scope does not cover required protected mutations. Prime Builder would either be blocked when attempting the MemBase/formal-artifact writes or would have to exceed the GO scope, weakening the bridge audit trail.

**Recommended action:** Revise the proposal so the implementation scope and `target_paths` match. If IP-6, IP-7, and IP-8 remain in this W1 proposal, include `groundtruth.db` and concrete approval-packet paths or conservative approval-packet globs for the GOV v3 and provenance deliberation. If Prime Builder wants tighter separation, split IP-6, IP-7, and IP-8 into separate bridge proposals that carry their own `target_paths`, formal-artifact approval requirements, and post-implementation verification evidence.

### F2 - P2 - CLI test placement is ambiguous relative to `target_paths`

**Observation:** The proposal lists `groundtruth-kb/tests/test_project_artifacts.py` and `platform_tests/hooks/test_project_completion_surface.py` as the only test targets (`bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:16`). The verification plan then says the CLI subcommand may be tested in `test_project_artifacts.py` "or the CLI test module" (`bridge/gtkb-s358-w1-retirement-machinery-correction-001.md:147`), but no CLI test-module path is authorized.

**Deficiency rationale:** The implementation-start packet is derived from the proposal's `target_paths`, so test edits must be inside that scope. The alternate "CLI test module" option creates an avoidable scope ambiguity.

**Impact:** Prime Builder could reasonably implement the CLI test in an existing CLI test module and exceed the GO scope, or avoid the better local test home only because the proposal under-scoped it.

**Recommended action:** Either constrain the revised proposal to place the CLI test in the already listed `groundtruth-kb/tests/test_project_artifacts.py`, or add the specific CLI test path/glob that Prime Builder intends to modify.

## Non-Blocking Confirmations

- Live bridge state was checked before filing this verdict: the selected document was still latest `NEW` with no index drift.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` current MemBase version is v2, titled "VERIFIED-Driven Project Completion and Retirement Are Automatic (No Owner Confirmation)", and its body defines membership-link gating and automatic completion without owner AUQ.
- `PROJECT-GTKB-GOVERNANCE-CORRECTION-S358` is active, and its active authorization includes `WI-3365`.
- `PROJECT-GTKB-LO-OPPORTUNITY-RADAR` is currently active and has no active authorization, matching the proposal's premise that a retirement transition is needed.
- The live implementation currently still contains the old owner-confirmation gate and included-work-item scanner model cited by the proposal.

## Opportunity Radar

No separate advisory was filed from this review. The repeated target-scope issue is better handled immediately by revising this proposal; a future deterministic check could flag proposal text that requests MemBase or formal-artifact mutations while omitting `groundtruth.db` or approval-packet paths from `target_paths`, but that is secondary to correcting this thread.

## Required Revision

File a revised proposal that fixes F1 and F2, then re-run the bridge applicability preflight and ADR/DCL clause preflight. The revised proposal should preserve the current spec linkage, owner-decision citations, and verification plan strengths while making the protected mutation scope explicit.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
