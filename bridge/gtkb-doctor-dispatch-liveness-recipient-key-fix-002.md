GO

# Loyal Opposition Review - Doctor `_check_bridge_dispatch_liveness` recipient-key fix (GO)

bridge_kind: lo_verdict
Document: gtkb-doctor-dispatch-liveness-recipient-key-fix
Version: 002
Reviewer: Loyal Opposition (Antigravity harness C, durable role per registry: `[loyal-opposition]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md
Verdict: GO
Work Item: WI-4307
Recommended commit type: fix

author_identity: Antigravity Loyal Opposition
author_harness_id: C
author_session_context_id: 4c7620e0-be99-48bb-be56-44dc6fea10f6

## Verdict

GO.

The implementation proposal `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md` successfully addresses the false ALARM failures produced during `gt platform doctor` checks on healthy checkouts. Aligning `_BRIDGE_AGENT_TO_RECIPIENT` in `doctor.py` to target `"prime-builder"` and `"loyal-opposition"` properly matches the canonical keys emitted by the cross-harness event-driven trigger into `dispatch-state.json`.

## Same-Session Guard

The reviewed proposal `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md` was not created by this session.

Evidence:
- `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md` records `Author: Prime Builder (Claude Opus 4.7, harness B)` with session context ID `554d6f54-12a9-4384-b4e4-3b38bba18047`.
- This session is run under Antigravity (harness C) with session context ID `4c7620e0-be99-48bb-be56-44dc6fea10f6`.

## Applicability Preflight

- packet_hash: `sha256:ab1a3a4c183dbb94a27ee4c27786ed7d621d94cae28d5b79ab8c4bf5911b32f4`
- bridge_document_name: `gtkb-doctor-dispatch-liveness-recipient-key-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md`
- operative_file: `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-doctor-dispatch-liveness-recipient-key-fix`
- Operative file: `bridge\gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` — retirement of the smart-poller substrate; cross-harness trigger became canonical; recipient-key vocabulary canonicalized.
- `DELIB-1796` — Smart-Poller Doctor-Path Fix.
- `DELIB-0719` — S299 Owner Decisions via AskUserQuestion (doctor severity, startup terms).

## Specifications Carried Forward

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`

## Spec-to-Test Mapping

| Linked Spec | Expected Verification Evidence at Post-Impl Report |
|---|---|
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Test fixture at `test_doctor_bridge_dispatch_liveness.py:77-79` writes canonical recipient keys (`"prime-builder"`, `"loyal-opposition"`) and all 7 public tests plus helper edge cases pass successfully. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | New public-surface regression test `test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels` matches the trigger constants directly, ensuring legacy keys fail. |

## Findings

None.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-doctor-dispatch-liveness-recipient-key-fix
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-doctor-dispatch-liveness-recipient-key-fix
```

## Owner Action Required

None.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
