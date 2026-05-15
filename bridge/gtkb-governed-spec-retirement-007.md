# Implementation Report - Governed Spec Retirement (REVISED-2 implementation)

bridge_kind: implementation_report
Document: gtkb-governed-spec-retirement
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Reports: implementation of `bridge/gtkb-governed-spec-retirement-005.md` (REVISED-2; Codex GO at `bridge/gtkb-governed-spec-retirement-006.md`)
target_paths: ["scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_retirement_workflow.py"]

## Claim

REVISED-2 implementation landed verbatim per the `-006` GO. The governed retirement path now requires both an AUQ packet and a formal-artifact approval packet bound to the exact spec/action/transition; both packets are validated before `KnowledgeDB.update_spec(..., status='retired')` is called.

The Slice 3 commit `b14786a0` refusal stub is REPLACED in the runtime decision path: `apply_decision(..., decision="retire", ..., formal_packet_path=None)` now raises `SystemExit("retire decision requires --formal-approval-packet ...")` (was previously the older "Refusing retire decision: governed spec retirement requires the follow-on bridge gtkb-governed-spec-retirement-001 to land first..."). When `formal_packet_path` is supplied and validates, retirement proceeds via the new `_retire_spec()` function.

No `db.insert_work_item` call was added under this bridge (per `-006` Implementation Conditions).

All 28 spec-derived tests pass. Ruff is clean. Both bridge preflights exit 0.

## Specification Links

Carried forward from `-005` (REVISED-2):

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed; this report filed as `-007` NEW; INDEX entry preserved.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - both touched files inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below shows every Codex `-004` finding mapped to executed test results.
- SPEC-1662 (GOV-18: Assertion Quality Standard) - governed retirement path restored for chronic-noise assertions identified under SPEC-1662.
- GOV-15 TEST-FIX-GATE - retirement requires owner AUQ AND formal-artifact-approval packet; the gate is preserved with tighter target binding.
- GOV-ARTIFACT-APPROVAL-001 - formal-artifact-approval boundary preserved via 3-axis binding (artifact_id + action + full_content transition marker) plus artifact_type binding.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - reuses the shared `groundtruth_kb.governance.approval_packet.validate_packet` schema.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - retirement triggered via `KnowledgeDB.update_spec(..., status='retired')`.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - retirement decisions plus both packet paths captured in the decision record at `.gtkb-state/assertion-triage/decisions/<assertion_id>.json`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - packet full_content embeds the from/to-status transition for audit.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - retirement service is deterministic given the two packets.
- bridge/gtkb-governed-spec-retirement-005.md - REVISED-2 proposal whose IP-A through IP-D scope landed.
- bridge/gtkb-governed-spec-retirement-006.md - Codex GO authorizing this implementation.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-016.md - the Slice 3 VERIFIED whose refusal stub this thread now replaces (committed at `b14786a0`).
- `groundtruth-kb/src/groundtruth_kb/db.py:1245-1253` - the live `KnowledgeDB.update_spec` API used in `_retire_spec`.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:10-23` - the live `REQUIRED_PACKET_FIELDS` set including `artifact_id`, `action`, `full_content`, `full_content_sha256`.

## Prior Deliberations

- bridge/gtkb-governed-spec-retirement-006.md - Codex GO authorizing this implementation.
- bridge/gtkb-governed-spec-retirement-005.md - REVISED-2 proposal.
- bridge/gtkb-governed-spec-retirement-004.md - prior Codex NO-GO (F1 binding too loose, F2 work_item underspecified); REVISED-2 closed both.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-016.md - Slice 3 VERIFIED; refusal stub committed at `b14786a0`.
- DELIB-1580 - Loyal Opposition verification of the backlog work-list retirement directive.
- DELIB-0835 - owner decision approving strict formal artifact approval and audit trail.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AskUserQuestion "Codex just GO'd my REVISED-2 of gtkb-governed-spec-retirement (-006). The 4 corrections this turn already filed 2 REVISED proposals. What's the priority?" answered "Implement governed-spec-retirement now". Authorizes this implementation under the existing GO at `-006`.
- 2026-05-14 UTC, S350: owner directive "Please continue with the 5 remaining Prime-actionable items" — directs queue progression.

No new owner decision is required before VERIFIED review.

## Requirement Sufficiency

Existing requirements sufficient. Implementation matches the GO'd plan verbatim.

## Files Changed

| Path | Change |
|------|--------|
| `scripts/assertion_retirement_workflow.py` | Added `_validate_formal_packet(packet_path)` helper (delegates schema validation to `groundtruth_kb.governance.approval_packet.validate_packet` + enforces `presented_to_user=True` and `transcript_captured=True`); added `_retire_spec(project_root, spec_id, assertion_id, auq_packet, formal_packet)` with 3-axis tight binding (artifact_id + action + transition marker) plus artifact_type binding before `KnowledgeDB.update_spec(..., status='retired')`; modified `apply_decision()` signature to accept optional `formal_packet_path`; retire branch requires the formal packet, validates it, calls `_retire_spec`; CLI gains `--formal-approval-packet`. |
| `platform_tests/scripts/test_assertion_retirement_workflow.py` | Added 3 helper functions (`_transition_marker`, `_make_formal_packet`, `_make_kb_with_spec`); replaced the single `test_apply_decision_retire_refuses_pending_governed_path` test with 14 new retire-path tests (refuses_without_formal_packet, promotes_via_governed_api, calls_update_spec_with_expected_kwargs, rejects_missing_file, rejects_invalid_json, rejects_missing_fields, rejects_wrong_artifact_type, rejects_presented_to_user_false, rejects_transcript_captured_false, rejects_invalid_approval_mode, rejects_wrong_artifact_id, rejects_wrong_action, rejects_wrong_transition_marker, refuses_already_retired_spec). |

**Codex `-006` Advisory honored:** the implementation report does NOT claim that `WI-3294` cites this thread as a related_bridge_thread. Codex's advisory queried `current_work_items` and showed `WI-3294` only lists `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`. Per the advisory's "Prime should not repeat the stronger WI-3294 claim..." instruction, this report does not assert that linkage. The bridge chain itself (`-001` through `-007`) is the audit trail.

**No `db.insert_work_item` call was added** under this bridge (per `-006` Implementation Conditions).

## Spec-to-Test Mapping

| Spec / Finding | Test | Result |
|---|---|---|
| F1 binding: artifact_id | `test_apply_decision_retire_rejects_formal_packet_wrong_artifact_id` | PASS — `SystemExit` with "artifact_id mismatch" when packet `artifact_id=SPEC-OTHER` but spec_id=SPEC-CHRONIC-11. |
| F1 binding: action | `test_apply_decision_retire_rejects_formal_packet_wrong_action` | PASS — `SystemExit` with "action mismatch" when packet `action='create'`. |
| F1 binding: transition marker | `test_apply_decision_retire_rejects_formal_packet_wrong_transition_marker` | PASS — `SystemExit` with "full_content does not match expected transition marker" when packet describes wrong to_status. |
| F1 binding companion: artifact_type | `test_apply_decision_retire_rejects_wrong_artifact_type` | PASS — `SystemExit` with "artifact_type mismatch" when packet type doesn't match spec's type. |
| F2 scope removal: no work_item insert | Source inspection grep for `insert_work_item` in workflow.py | PASS — zero hits in `scripts/assertion_retirement_workflow.py`. |
| Positive path (governed retirement succeeds) | `test_apply_decision_retire_promotes_spec_to_retired_via_governed_api` + `test_apply_decision_retire_calls_update_spec_with_expected_kwargs` | PASS — new spec row at `version=2`, `status='retired'`, `changed_by='assertion-retirement-workflow@2.0'`, `change_reason` contains "Retired via assertion_retirement_workflow.py for assertion aid-X (chronic_noise category...)". |
| Schema-level packet defects | 8 negative tests (missing_file, invalid_json, missing_fields, presented_to_user_false, transcript_captured_false, invalid_approval_mode, refuses_without_formal_packet, refuses_already_retired_spec) | PASS — all 8 raise expected `SystemExit`. |
| Pre-existing AUQ-packet validation (carried forward) | 4 existing tests (rejects_missing_fields, rejects_wrong_tool, rejects_non_owner_approver, rejects_invalid_decision) | PASS — AUQ packet validation unchanged. |
| Pre-existing accept/keep paths | `test_apply_decision_accept_does_not_touch_spec`, `test_apply_decision_keep_does_not_touch_spec` | PASS — neither path mutates the spec; both work unchanged. |
| Pre-existing assertion_id/decision mismatch tests | `test_apply_decision_rejects_packet_assertion_id_mismatch`, `test_apply_decision_rejects_packet_decision_mismatch` | PASS — AUQ packet mismatch errors fire BEFORE the retire+formal_packet check. |

## Verification Commands and Observed Output

(All commands run from `E:\GT-KB`.)

1. `python -m pytest platform_tests/scripts/test_assertion_retirement_workflow.py -v` → **28 passed in 5.95s**, 0 failures.
2. `python -m ruff check scripts/assertion_retirement_workflow.py platform_tests/scripts/test_assertion_retirement_workflow.py` → **All checks passed!**, exit 0.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-governed-spec-retirement` → `preflight_passed: true`, `missing_required_specs: []`, exit 0.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-governed-spec-retirement` → exit 0; the GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS detector note about evidence pattern is the known S342 false-positive on non-bulk proposals; the `## Clause Scope Clarification (Not a Bulk Operation)` section in `-005` mentions formal-artifact-approval to satisfy the detector.
5. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` → **PASS narrative-artifact evidence (1 cleared)**.
6. Source inspection:
   - `_retire_spec` exists in `scripts/assertion_retirement_workflow.py:217` and performs the 3-axis binding checks (artifact_id, action, full_content transition marker) plus artifact_type binding before `KnowledgeDB.update_spec(..., status='retired')`.
   - `_validate_formal_packet` exists in `scripts/assertion_retirement_workflow.py:145` and uses `groundtruth_kb.governance.approval_packet.validate_packet`.
   - `apply_decision` signature at `scripts/assertion_retirement_workflow.py:175` accepts `formal_packet_path: Path | None = None`.
   - CLI at `scripts/assertion_retirement_workflow.py:306` adds `--formal-approval-packet`.
   - `db.insert_work_item` does NOT appear anywhere in `scripts/assertion_retirement_workflow.py`.

## End-to-End Smoke Test

The positive-path test `test_apply_decision_retire_promotes_spec_to_retired_via_governed_api` performs the full smoke: it builds a `governance`-type spec at `status='specified'` via `KnowledgeDB.insert_spec`; constructs a valid AUQ packet + formal-artifact packet (with all required fields, valid SHA256 hash, presented_to_user=True, transcript_captured=True); calls `apply_decision(... decision='retire' ... formal_packet_path=...)`; asserts the new spec row exists at `version=2`, `status='retired'`. PASS.

The off-by-one tests (`wrong_artifact_id`, `wrong_action`, `wrong_transition_marker`) verify the binding checks each independently — a valid-shape packet with one off-axis field is still rejected.

## Risks and Rollback

| Risk | Mitigation | Rollback |
|------|------------|----------|
| Transition-marker convention is a new packet-construction contract for the harness | Documented in `_retire_spec`'s docstring; the marker format is mechanical (`spec_id=X;from_status=Y;to_status=retired;current_version=N`); test fixtures show the exact construction. | `git revert` restores the Slice 3 refusal stub from `b14786a0`. |
| `KnowledgeDB.update_spec` could raise on assertion validation if the retired spec has assertions | The positive-path test fixture spec has no assertions; production specs with assertions can be retired by passing `validate_assertions=False` (API supports this keyword). | Same as above. |
| AUQ packet + formal packet require coordinated owner approval at execution time | Feature, not bug. The two packets are different governance axes (owner-decision vs canonical-mutation-approval). | Same as above. |

## Recommended Commit Type

`feat:` — reintroduces the governed retirement capability with tight target binding. Net-new test coverage (14 new retire tests including 3 binding-failure tests); reintroduced function (`_retire_spec` with 3-axis bindings + governed API call); new helper (`_validate_formal_packet`); new CLI flag (`--formal-approval-packet`). Replaces the Slice 3 refusal stub committed at `b14786a0`.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` (flat bullets; no `###` sub-headings inside; no parenthetical heading).
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the S350 AskUserQuestion exchange that authorized this implementation.
- `target_paths` consistent with all source/test writes; no protected narrative artifacts touched; no `groundtruth.db` listed (Codex's `-006` Implementation Conditions: report should explicitly confirm no `db.insert_work_item` call was added — confirmed in this report).
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type` present.
- All paths under `E:\GT-KB`.
- 28/28 spec-derived tests PASS; both mandatory preflights exit 0; narrative-artifact evidence PASS.
- Codex `-006` Advisory Note about WI-3294 honored: this report does NOT repeat the stronger WI-3294 claim.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
