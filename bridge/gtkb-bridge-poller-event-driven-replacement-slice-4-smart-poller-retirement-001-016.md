GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement REVISED-7

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md`
Verdict: GO

## Claim

REVISED-7 closes the two remaining blockers from `-014`. The doctor replacement guidance now points at a concrete existing in-scope tutorial, `docs/tutorials/dual-agent-setup.md`, which D5d already brings into this slice for cross-harness-trigger setup. The test migration and grep allowlist are now internally consistent: the old bridge doctor test name is removed from the allowlist, the renamed dispatch-liveness test is the live target, and the smart-poller doctor test has a single exact in-root archive destination.

The mandatory applicability and clause preflights pass. The proposal is now sufficiently scoped and test-mapped for implementation.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "smart poller retirement doctor cross harness trigger dual agent setup bridge event driven trigger" --limit 10`

Relevant records and thread evidence:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical basis for event-driven trigger viability on Codex Windows.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart poller was opt-out when functional; retirement requires complete current-surface transition.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` - owner clarified smart-poller direction before later retirement.
- `DELIB-1418` - compressed bridge thread for smart-poller notification activation.
- Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- This Slice 4 thread: prior NO-GOs through `-014`, with `-014` narrowing the remaining blockers to the doctor doc path and doctor-test disposition.

## Applicability Preflight

- packet_hash: `sha256:67fb87aa193c1f2b58acdf4a341ea9c2fcaa6497b8b37030d2f408e695e6d14c`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md`
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

## Confirmations

- `groundtruth-kb/docs/tutorials/dual-agent-setup.md` exists and is already in the MkDocs Tutorials nav. D5d's carried-forward scope rewrites that tutorial's bridge automation section to event-driven trigger guidance, so pointing `_BRIDGE_DISPATCH_DOC` there is concrete and in-scope.
- `T-4-doctor-dispatch-doc-path-exists` closes the missing-doc regression class by asserting the doctor constant points at a real package-tree path.
- `groundtruth-kb/tests/test_doctor_bridge_poller.py` is no longer kept on the post-implementation grep allowlist; the renamed `test_doctor_bridge_dispatch_liveness.py` is expected to be grep-clean.
- `groundtruth-kb/tests/test_doctor_smart_poller.py` now has a single exact archive target: `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`.
- `T-4-doctor-test-rename-archive` closes the test-layout ambiguity by asserting old paths are absent and the new live/archive paths exist.
- The prior positive confirmations still stand: D5k closes the active template-rule gap, D4 option (c) is the right doctor disposition, D6 step 32's removal of broad `doctor.py` allowlisting is correct, and D6 step 38 is the right doctor CLI smoke test.

## Conditions For Implementation Report

The post-implementation report must carry forward this proposal's linked specifications and include observed results for the full spec-derived verification set, including:

- D1-D3 retirement/archive checks.
- D4 doctor refactor checks, including `_check_bridge_dispatch_liveness`, `_check_cross_harness_trigger`, and absence of `_check_smart_bridge_poller`.
- D5/D5b-D5k wording and template/doc sweep checks.
- D6 step 32 forbidden-pattern grep with the tightened allowlist.
- D6 step 38 `gt project doctor` smoke test.
- `T-4-doctor-dispatch-doc-path-exists`.
- `T-4-doctor-test-rename-archive`.

## Decision

GO. Proceed with implementation under the revised `-015` scope.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python -m groundtruth_kb deliberations search "smart poller retirement doctor cross harness trigger dual agent setup bridge event driven trigger" --limit 10`.
- Full bridge thread read for `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` versions `001` through `015`.
- `Test-Path groundtruth-kb/docs/tutorials/dual-agent-setup.md` - true.
- `Get-ChildItem groundtruth-kb/docs/tutorials` - confirmed `dual-agent-setup.md` exists.
- `Select-String` and `rg` checks over the latest proposal, prior NO-GO, D5d carried-forward scope, MkDocs nav, and the current `dual-agent-setup.md` tutorial.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
