NO-GO

# Loyal Opposition Review - Bridge Parallel-Session Collision Protection

bridge_kind: loyal_opposition_review
Document: gtkb-bridge-parallel-session-collision
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-bridge-parallel-session-collision-001.md`
Verdict: NO-GO

## Verdict

NO-GO. The proposal is directionally useful, but it cannot receive GO because the proposed implementation does not yet satisfy its own claimed protection behavior or the operative WI-3274 scope.

## Reviewed Materials

- `bridge/INDEX.md`
- `bridge/gtkb-bridge-parallel-session-collision-001.md`
- `groundtruth.db` current `WI-3274` row, queried with `KnowledgeDB.get_work_item("WI-3274")`
- `groundtruth.db` current project authorization `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH`
- Mandatory applicability and clause preflights below

## Prior Deliberations

- `DELIB-1499` - prior NO-GO on cross-harness trigger rename-race/liveness diagnostics; relevant because it documents bridge automation race risk.
- `DELIB-1517` - prior NO-GO on bridge-status automation; relevant because it rejected automation that did not match the real local execution surface.
- `DELIB-0573` - bridge closure-starvation root-cause report; relevant as background on bridge reliability and queue-state handling.

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "WI-3274 bridge parallel session collision work intent registry" --limit 5`
- `python -m groundtruth_kb deliberations search "parallel-session collision work-intent registry S341 bridge thread version race" --limit 8`

## Findings

### F1 - P1 - The proposed scope does not implement the claimed collision protection

Observation: The proposal says it will "prevent concurrent Prime Builder sessions from writing the same bridge thread version simultaneously" and says a session "must acquire the lock" before writing a bridge version or updating `bridge/INDEX.md` (`bridge/gtkb-bridge-parallel-session-collision-001.md:18`, `bridge/gtkb-bridge-parallel-session-collision-001.md:22`). But the implementation scope only adds a module and tests, then explicitly makes integration optional: "NOT a hard mechanical gate in this WI" (`bridge/gtkb-bridge-parallel-session-collision-001.md:78`). Acceptance likewise only requires the module and seven tests (`bridge/gtkb-bridge-parallel-session-collision-001.md:98`).

Deficiency rationale: A registry that no bridge writer is required to call does not prevent the observed same-thread/same-version collision. It creates a library, not the promised protection. The operative WI-3274 row says the recommended option is a work-intent registry with visibility before drafting, including AXIS-2/startup visibility; the proposal cites WI-3274 as sufficient (`bridge/gtkb-bridge-parallel-session-collision-001.md:46`) but does not include those surfaces in `target_paths` (`bridge/gtkb-bridge-parallel-session-collision-001.md:16`).

Impact: Prime could implement and test the new module while the actual bridge race remains unchanged for autonomous batch work, manual bridge edits, and helper paths that never call the registry.

Recommended action: Revise the proposal to choose one of two coherent scopes: either (a) rename this as a foundation-only module and remove "prevents concurrent writes" acceptance claims, with an explicit follow-up WI for helper/startup integration, or (b) include the bridge writer integration and visibility surfaces in `target_paths` and in the tests.

### F2 - P1 - The lock API does not specify an under-lock version revalidation step

Observation: The proposed API exposes only `acquire`, `release`, and `current_holder` (`bridge/gtkb-bridge-parallel-session-collision-001.md:62` through `bridge/gtkb-bridge-parallel-session-collision-001.md:74`). It does not require the writer to re-read live `bridge/INDEX.md`, recompute the next version, or assert that `bridge/<slug>-NNN.md` is still absent while the thread lock is held.

Deficiency rationale: The observed race is not only simultaneous byte writing; it is also stale next-version calculation. Two sessions can both compute `NNN`, then one writes and releases. If the second session later acquires the registry without recomputing against live `bridge/INDEX.md` and the filesystem, it can still target stale `NNN` or fail late after doing the work. The mandatory bridge protocol treats live `bridge/INDEX.md` as canonical queue state, so the collision guard must bind lock acquisition to live-state revalidation.

Impact: The module can reduce one narrow overlap case but still leaves the documented "first writer wins; second discovers collision only at file-write time" failure mode.

Recommended action: Add explicit acquire-then-refresh semantics: after acquiring, re-read `bridge/INDEX.md`, recompute the next version, check the target file does not already exist, then write file and index update before release. Cover this with a two-session stale-next-version regression test.

### F3 - P2 - Test placement and command are ambiguous

Observation: `target_paths` includes both `tests/scripts/test_bridge_work_intent_registry.py` and `platform_tests/scripts/test_bridge_work_intent_registry.py` (`bridge/gtkb-bridge-parallel-session-collision-001.md:16`), but the verification command runs only `tests/scripts/test_bridge_work_intent_registry.py` (`bridge/gtkb-bridge-parallel-session-collision-001.md:96`). Live path checks in this review returned `False` for both proposed test files, and this repo already uses `platform_tests/scripts/` for script-level tests.

Deficiency rationale: A proposal should authorize one concrete test location and run the same test it asks Prime to create. Creating a new top-level `tests/scripts` root without explanation adds structure drift and leaves the `platform_tests` target unused.

Impact: Prime could implement tests in one location while the acceptance command points to another, producing avoidable verification churn.

Recommended action: Pick the repo-native test target, likely `platform_tests/scripts/test_bridge_work_intent_registry.py`, remove the unused alternate path, and make the verification command match the target.

### F4 - P2 - Applicability preflight still reports missing advisory specs

Observation: The mandatory preflight passes blocking specs, but reports missing advisory specs:

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

Deficiency rationale: The bridge protocol's pre-filing subsection expects both `missing_required_specs: []` and `missing_advisory_specs: []`; non-empty missing spec lists are self-detected defects to clear before filing.

Impact: The proposal is missing durable governance context for artifact-oriented handling of owner decisions, work items, and lifecycle triggers.

Recommended action: Cite the applicable advisory specs in the revised `Specification Links` section or document why each does not apply after revising the proposal text.

## Applicability Preflight

- packet_hash: `sha256:f6f0bf40bb5e6d3c66a314e27345fa27beef10c215bf3ccaad93c319527257a5`
- bridge_document_name: `gtkb-bridge-parallel-session-collision`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-parallel-session-collision-001.md`
- operative_file: `bridge/gtkb-bridge-parallel-session-collision-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-parallel-session-collision`
- Operative file: `bridge\gtkb-bridge-parallel-session-collision-001.md`
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

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate when evidence is absent and no owner waiver line is cited. No blocking gap was reported here.

## Verification Commands

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-parallel-session-collision` - passed blocking preflight, advisory specs missing as shown above.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-parallel-session-collision` - exit 0, no blocking gaps.
- `Test-Path` checks for the proposed test and module paths - proposed module and both proposed test paths do not currently exist.
- `KnowledgeDB.get_work_item("WI-3274")` against root `groundtruth.db` - confirmed WI-3274 describes the registry as a work-intent visibility mechanism and cites the same collision symptoms.
