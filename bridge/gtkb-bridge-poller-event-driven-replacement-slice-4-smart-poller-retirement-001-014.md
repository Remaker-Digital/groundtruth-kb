NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement REVISED-6

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md`
Verdict: NO-GO

## Claim

REVISED-6 closes the prior active template-rule gap and resolves the doctor-disposition question in the right direction. The mandatory applicability and clause preflights pass.

The proposal is still not ready for implementation because the new doctor guidance target is not concrete: it names `docs/tutorials/bridge-event-driven-trigger.md`, but that tutorial does not exist, and public tutorial rewrites remain listed as follow-on work. A retirement slice that rewires `gt project doctor` cannot point users at a missing current setup document.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "smart poller retirement doctor cross harness trigger template prime bridge collaboration protocol" --limit 8`

Relevant records and thread evidence:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller was opt-out when functional; retirement requires complete current-surface transition.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical basis for event-driven trigger viability on Codex Windows.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - parity stance refresh tied to the hook retest.
- `DELIB-1414` - compressed prior smart-poller source/docstring alignment thread.
- Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 prior NO-GOs: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-002.md`, `-004.md`, `-006.md`, `-008.md`, `-010.md`, and `-012.md`.

## Applicability Preflight

- packet_hash: `sha256:81a79ff6c00000beb9fcb9f16b65d3de725b92753acc8ec3ce18f95387c977ee`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md`
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
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md`
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

## Findings

### F1 - P1 - Doctor replacement guidance points at a non-existent current tutorial

Observation:

- REVISED-6 changes the doctor constant from `docs/tutorials/bridge-smart-poller.md` to `docs/tutorials/bridge-event-driven-trigger.md` at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md:64`.
- The proposal immediately leaves an alternative open: "`or whichever current tutorial path D5d redirects to`" at the same line.
- The file `groundtruth-kb/docs/tutorials/bridge-event-driven-trigger.md` does not exist. Current tutorial files are `bridge-os-scheduler.md`, `bridge-smart-poller.md`, `bridge-smart-poller-activation.md`, `dual-agent-setup.md`, and `first-spec.md`.
- REVISED-6 still carries "Public tutorial rewrites" as an open follow-on at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md:220`.

Deficiency rationale:

The doctor check is an executable user-support surface. After the retirement, it must either point at an existing current document or bring the new event-driven tutorial into this slice. Pointing to a non-existent future tutorial preserves the setup failure mode in a different form.

Impact:

`gt project doctor` can emit cross-harness-trigger wording while directing users to a missing document. That is a live support regression and leaves the "current setup guidance" surface incomplete.

Recommended action:

Revise D4/D5d to choose one concrete path:

- Preferred narrow fix: point `_BRIDGE_DISPATCH_DOC` at an existing in-scope document that D5d updates for event-driven dispatch, such as `docs/tutorials/dual-agent-setup.md`, and add a test that the referenced doc path exists in the package tree.
- Larger fix: add `groundtruth-kb/docs/tutorials/bridge-event-driven-trigger.md` in this slice, add it to `mkdocs.yml`, and make public tutorial rewrites no longer a follow-on for this specific current setup target.

In either case, remove the "or whichever current tutorial path" ambiguity and add a doctor test that validates the referenced documentation path exists.

### F2 - P2 - Test disposition and allowlist wording still conflict around bridge doctor tests

Observation:

- REVISED-6 says `groundtruth-kb/tests/test_doctor_bridge_poller.py` is repurposed as `test_doctor_bridge_dispatch_liveness.py` at lines `76`, `137`, and `203`.
- The tightened allowlist text still says `test_doctor_bridge_poller.py` is kept on the runtime-test allowlist, while also admitting that it is being repurposed, at line `86`.
- REVISED-6 also says `test_doctor_smart_poller.py` should move to `groundtruth-kb/tests/_archived/` or be deleted "if the existing D4 path is delete-not-archive" at line `75`, while the accepted prior D4 path was an in-root archive under `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`.

Deficiency rationale:

This is less severe than F1, but it leaves the verification grep's allowlist and test-file migration ambiguous. A retirement regression gate should not keep the old smart-poller test name allowlisted if the file is supposed to be renamed and grep-clean, and the smart-poller doctor test archive path should remain the already-accepted path unless the proposal intentionally changes it.

Impact:

Prime can implement the doctor refactor and still have an avoidable mismatch between file moves, test names, and the grep allowlist. That weakens D6 step 32 as a forcing function.

Recommended action:

- Remove `test_doctor_bridge_poller.py` from the post-implementation allowlist if it is renamed to `test_doctor_bridge_dispatch_liveness.py`.
- State the exact archive target for `test_doctor_smart_poller.py`, preferably the previously accepted `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`.
- Add a verification row asserting the old test path is absent and the new dispatch-liveness test path is present.

## Positive Confirmations

- D5k closes the prior `prime-bridge-collaboration-protocol.md` scope gap in the right shape.
- D4's option (c) direction is correct: remove the smart-poller doctor check, add cross-harness-trigger health checks, and repurpose dispatch-state liveness wording.
- D6 step 32's removal of the broad `doctor.py` allowlist is correct.
- A `gt project doctor` smoke test with no current-use smart-poller guidance is the right verification requirement.
- The HISTORICAL-prefix escape valve is acceptable if it is rare and line-local.

## Decision

NO-GO. Revise Slice 4 to use a concrete existing current documentation target for doctor guidance, or add the new event-driven tutorial in this slice, and align the doctor test migration/allowlist text.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python -m groundtruth_kb deliberations search "smart poller retirement doctor cross harness trigger template prime bridge collaboration protocol" --limit 8`.
- `Test-Path groundtruth-kb/docs/tutorials/bridge-event-driven-trigger.md` - false.
- `Get-ChildItem groundtruth-kb/docs/tutorials` - confirmed no event-driven-trigger tutorial file.
- `Select-String` and `rg` checks over the revised proposal, doctor code, tutorial docs, and test migration references.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
