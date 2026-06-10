NEW

# Implementation Proposal - Standing Backlog Harvest/Reconciliation Audit Maintenance (GTKB-GOV-010)

bridge_kind: prime_proposal
Document: gtkb-standing-backlog-harvest-audit-maintenance
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-010

target_paths: ["scripts/audit_standing_backlog_sources.py", "platform_tests/scripts/test_standing_backlog_harvest.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-14.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py"]

This NEW proposal advances the standing backlog harvest/reconciliation audit toward release-gate integration. Currently maintained as a hand-curated audit; the WI calls for promoting it to a first-class doctor check.

## Claim

Two-part advance: (1) refresh the harvest audit with current data for the S350 timeframe; (2) promote the audit logic into a first-class `gt project doctor` check that runs automatically as part of release-readiness evaluation.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - source spec for backlog governance.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness integration.
- `GOV-ARTIFACT-APPROVAL-001` - audit output is governance evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - doctor surface integration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ADOPTER-EXPERIENCE authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI description specifies the maintenance + promotion scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (refresh) + IP-2 (doctor promotion) + IP-3 (release-gate integration) + IP-4 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Refresh harvest audit

Run `python platform_tests/scripts/test_standing_backlog_harvest.py` (or rerun `audit_standing_backlog_sources.py`) for S350-current data. Write report at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-14.md` enumerating:
- bridge status counts (cross-reference INDEX.md)
- MemBase open work_items counts (with project authorization status breakdown)
- release-readiness blockers (cite specific GO-blocking WIs)
- independent-progress-assessment unresolved entries

### IP-2: Promote to doctor check

In `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, add `check_standing_backlog_health()` that:
1. Queries MemBase for open work_items not in any active authorization.
2. Parses bridge/INDEX.md for entries with stale NO-GO (older than configurable threshold).
3. Emits per-finding severity: orphaned-WI=WARN, stale-NO-GO=WARN, missing-evidence=FAIL.

### IP-3: Release-gate integration

Wire `check_standing_backlog_health()` into `scripts/release_candidate_gate.py` per WI description ("as release-gate input").

### IP-4: Tests

Tests verify check function output schema + release-gate integration.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Doctor check finds orphaned WIs | `test_doctor_finds_orphaned_wis` |
| Doctor check detects stale NO-GO | `test_doctor_detects_stale_no_go` |
| Severity classification correct | `test_doctor_severity_classification` |
| Release-gate calls standing-backlog check | `test_release_gate_calls_standing_backlog_check` |
| Refresh report file emitted | `test_harvest_report_emitted` |
| Clean state reports no findings | `test_clean_state_no_findings` |

Run: `python -m pytest groundtruth-kb/tests/project/test_doctor_standing_backlog.py platform_tests/scripts/test_standing_backlog_harvest.py -v`.

## Acceptance Criteria

- IP-1 refresh report emitted (timestamped).
- IP-2 doctor check landed.
- IP-3 release-gate integration.
- IP-4: 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: doctor check finding noise on first run (many orphaned WIs from this very session's authorization activity). Mitigation: this session's batch-1..5 authorizations cover most prior orphans; baseline should be cleaner than expected.
- Rollback: remove doctor check + release-gate wiring; refresh report stays as historical doc.

## Recommended Commit Type

`feat` - new doctor surface + release-gate input. ~120 LOC + tests.
