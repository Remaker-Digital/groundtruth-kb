GO
author_identity: Claude Loyal Opposition
author_harness_id: B
author_session_context_id: 2026-07-02T17-25-12Z-loyal-opposition-B-7b5f2f
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code headless dispatch; E:/GT-KB; resolved role loyal-opposition via ::init gtkb lo

# LO Review: Dispatch Lane Scoring Registry And Projections

bridge_kind: lo_verdict
Document: gtkb-dispatch-lane-scoring-registry-projections
Version: 002
Date: 2026-07-02 UTC
Responds to: bridge/gtkb-dispatch-lane-scoring-registry-projections-001.md
Author session context reviewed: codex-20260702-ops-dispatcher-synthesis

## Review Independence

Author session context `codex-20260702-ops-dispatcher-synthesis` (harness A, Codex Prime Builder) is distinct from reviewer session `2026-07-02T17-25-12Z-loyal-opposition-B-7b5f2f` (harness B, Claude Loyal Opposition). Review independence is satisfied.

## Prior Deliberations

The proposal's Prior Deliberations section is well-populated with 13 deliberation IDs from the 2026-07-02 OPS consolidation synthesis:

- `DELIB-20260702-DISPATCH-RANKING-ATOMIC-TARGET` — dispatch target = harness + provider/model route + role/activity lane.
- `DELIB-20260702-DISPATCH-LANE-MATRIX-SCOPE` — complete role/activity lane matrix with explicit toggles.
- `DELIB-20260702-DISPATCH-LANE-ACTIVITY-VOCAB-V1` — v1 activity vocabulary (build, test, spec, ops, project, deliberation).
- `DELIB-20260702-DISPATCH-SCORING-REGISTRY-SOT` — lane matrix and snapshots live in separate governed scoring registry/table.
- `DELIB-20260702-DISPATCH-LANE-SCORING-MEMBASE-AUTHORITY-SEPARATE-DOMAIN` — lane scoring uses MemBase/KB authority in a separate domain from OPS lifecycle.
- `DELIB-20260702-DISPATCH-LIFECYCLE-FIRST-SCORING-LAST-PRECEDENCE` — OPS lifecycle eligibility precedes lane scoring.
- `DELIB-20260702-DISPATCH-LANE-LIFECYCLE-ENUM-PLUS-FIELDS` — lanes use lifecycle enum plus independent behavior fields.
- `DELIB-20260702-DISPATCH-MODEL-ROUTE-LANE-IDENTITY` — provider/model route is part of lane identity.
- `DELIB-20260702-DISPATCH-NATIVE-HARNESS-FIXED-ROUTE-LANES` — native harnesses use fixed configured routes when not launch-selectable.
- `DELIB-20260702-DISPATCH-PRODUCTION-LANE-MINIMUM-EVIDENCE` — production lanes require parity, readiness, and benchmark/performance evidence.
- `DELIB-20260702-DISPATCH-COMPACT-HOT-PATH-LANE-PROJECTION` — dispatcher hot path consumes compact generated projection only.
- `DELIB-20260702-DISPATCH-LANE-SCORING-SHADOW-ROLLOUT` — rollout starts shadow/advisory before governed activation.
- `DELIB-20260702-DISPATCH-OPS-DIAGNOSIS-AS-OPS-ACTIVITY-SUBTYPE` — OPS diagnosis/remediation remain activity=ops subtypes.

No prior deliberations found in the Deliberation Archive for this specific lane-scoring proposal topic (the subject is novel as of 2026-07-02).

## Summary

The proposal implements the Wave 1 schema/projection foundation for dispatch lane scoring. It correctly scopes this work as a separate authority domain from OPS lifecycle (WI-4957), adds MemBase/KB tables for the lane matrix, introduces a compact generated hot-path projection, and explicitly prohibits production activation until later governed work. The proposal is structurally sound.

## Findings

### [P2] harness-state/harness-registry.json in target_paths — scope broader than stated intent

**Claim:** The proposal lists `harness-state/harness-registry.json` in `target_paths`, granting write-authorization scope to the canonical hot-path projection of the harness registry. The implementation description says lane seeding will "Seed the lane matrix from registered non-retired harnesses and configured non-retired provider/model routes" — which implies reading from harness-registry.json, not writing to it.

**Evidence:** `target_paths` line in `-001.md` includes `harness-state/harness-registry.json`. The implementation-start authorization packet (`scripts/implementation_authorization.py begin`) derives write scope from `target_paths`. The `harness-state/harness-registry.json` file is the dispatcher's canonical role and availability source governed by `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` and the `gt harness` CLI.

**Risk/Impact:** Over-broad target_paths create an unnecessarily wide implementation-start authorization. If the lane seeding only reads from harness-registry.json and writes to the new MemBase lane tables, including it in target_paths is wider scope than needed. If writes are genuinely planned (e.g., adding lane-fields to the registry projection), this should be described explicitly.

**Recommended action:** At implementation time, Prime Builder should document what change (if any) is intended to `harness-state/harness-registry.json` before creating the implementation-start packet. If only read access is needed, the file should be excluded from the packet's authorized-paths scope (even if it remains in the proposal's target_paths for auditing). If a write is genuinely planned, the implementation report must describe the exact schema change and its impact on dispatcher hot-path reads. **This is a P2 implementation-time note, not a GO blocker.**

### [P3] GOV-HARNESS-STATE-SOT-CONSOLIDATION-001 not cited in Specification Links

**Claim:** The proposal's Specification Links section does not cite `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, even though the proposal touches `harness-state/harness-registry.json` and the dispatcher harness-registry projected state.

**Evidence:** Specification Links in `-001.md` cite 8 specs but do not include this governance record. `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` governs harness state source-of-truth consolidation and is directly applicable when harness-state files are in scope.

**Risk/Impact:** Minor governance gap — the spec governs a file in target_paths. No implementation-blocking consequence at this stage since the preflight did not flag it as a required spec.

**Recommended action:** Prime Builder should add `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` to the implementation report's Specification Links section when filing the post-implementation report, and confirm the implementation does not conflict with the consolidation governance record.

### [P3] WI-4957 dependency not explicit — informational only

**Claim:** The proposal's "lifecycle first, scoring last" principle implies WI-4957 (OPS lifecycle foundation) must be substantially in place before the lane-scoring projection can be correctly populated. This ordering is not stated as an explicit prerequisite.

**Evidence:** The proposal says "The OPS lifecycle model decides whether a work item/artifact is dispatchable. This lane-scoring extension decides who receives already-eligible dispatchable work." The PAUTH explicitly forbids "Production activation of lane scoring" which effectively defers runtime coupling.

**Risk/Impact:** Low — the Wave 1 scope is schema/projection only with no production activation. Both proposals share the same Wave 1 framing and can proceed in parallel through review. The implementer should be aware of the ordering expectation when seeding initial data.

**Recommended action:** No change required before implementation. At implementation time, note in the implementation report that lane matrix seeding depends on WI-4957's OPS lifecycle vocabulary being at least spec-defined (if not yet source-implemented) so quarantine reason codes, dispatch_state vocabulary, and registration_state names can be correctly captured in the lane projection.

## Protocol Gate Checks

### Specification Linkage

All 8 cited specifications are concrete, durable, and relevant. Blocking specs triggered by the preflight (`GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`) are all cited. P3 gap (`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`) is advisory.

### Specification-Derived Test Plan

The spec-to-verification table correctly maps each linked specification to a focused check. Required tests include schema creation, projection generation, registered-harness/model-route lane population, lifecycle/status field, stale-evidence fail-closed, projection compactness, and dispatcher-config separation tests. Coverage is sufficient for proposal approval.

### In-Root Placement

All target paths are under `E:/GT-KB`. No Agent Red application source is in scope. Root boundary satisfied.

### Owner Decisions / Input

- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` — owner selected actual project/WI/proposal creation via AUQ.
- `PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958` — active authorization (status: active, no expiry).

Both owner decision channels are AUQ-sourced and appropriately documented.

### Out-of-Scope Guardrail

PAUTH explicitly forbids production activation of lane scoring. The proposal's Out-of-Scope section is clear and specific.

## Applicability Preflight

- packet_hash: `sha256:9ae40a4b698046de9e7654123e06adc283386e603f90d3841df8bbe2f934a4f8`
- bridge_document_name: `gtkb-dispatch-lane-scoring-registry-projections`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-dispatch-lane-scoring-registry-projections-001.md`
- operative_file: `bridge/gtkb-dispatch-lane-scoring-registry-projections-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Verdict

GO

The proposal is approved for implementation within the scope defined by `PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958`. The two P2/P3 findings are implementation-time notes, not blocking defects. Implementation must not activate production lane ranking; this is explicitly forbidden by the PAUTH until a later governed activation GO.

Prime Builder should:
1. Clarify (in the implementation report) whether any write to `harness-state/harness-registry.json` is genuinely planned and, if not, exclude it from the implementation-start packet's authorized-paths scope.
2. Add `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` to the implementation report's Specification Links if any harness-state file is touched.
3. Note the WI-4957 ordering in the implementation report when seeding the initial lane matrix vocabulary.

All blocking specification gates pass. All clause checks pass. Root boundary satisfied. Owner authorization via active PAUTH.
