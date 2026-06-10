NEW

# Implementation Proposal - audit_standing_backlog_sources.py WITHDRAWN Regex Fix (WI-3276)

bridge_kind: prime_proposal
Document: gtkb-audit-script-withdrawn-regex-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SPEC-TEST-QUALITY-SPEC-TEST-QUALITY-BATCH
Project: PROJECT-GTKB-SPEC-TEST-QUALITY
Work Item: WI-3276

target_paths: ["scripts/audit_standing_backlog_sources.py", "tests/scripts/test_audit_standing_backlog_sources.py", "platform_tests/scripts/test_audit_standing_backlog_sources.py"]

This NEW proposal fixes a defect in `scripts/audit_standing_backlog_sources.py` line 39: the regex `^(NEW|REVISED|GO|NO-GO|VERIFIED):` excludes `WITHDRAWN` lines, causing the parser to fall through and misclassify withdrawn bridge entries.

## Claim

Extend the regex to include `WITHDRAWN` as a recognized actionable-status prefix. Add fixture coverage for withdrawn bridge entries to prevent regression.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status taxonomy.
- `GOV-STANDING-BACKLOG-001` - audit script supports this governance contract.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SPEC-TEST-QUALITY authorization including WI-3276.

## Requirement Sufficiency

Existing requirements sufficient. WI-3276 description identifies the exact line + regex defect.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-SPEC-TEST-QUALITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Regex extension

In `scripts/audit_standing_backlog_sources.py:39` (approximate), extend the regex from `^(NEW|REVISED|GO|NO-GO|VERIFIED):` to `^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):`. Note: ADVISORY is the new advisory-report status (per `gtkb-bridge-advisory-report-message-advisory-disposition` GO); WITHDRAWN is the parked-thread retirement marker.

### IP-2: Tests

Add fixture cases: bridge thread with WITHDRAWN status, bridge thread with ADVISORY status. Assert parser correctly classifies both.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| WITHDRAWN line recognized | `test_audit_recognizes_withdrawn_status` |
| ADVISORY line recognized | `test_audit_recognizes_advisory_status` |
| Existing statuses still recognized | `test_audit_existing_statuses_preserved` |
| Parser does not fall through on WITHDRAWN | `test_audit_no_fallthrough_on_withdrawn` |
| Mixed-status INDEX parses cleanly | `test_audit_mixed_status_index_parses` |

Run: `python -m pytest tests/scripts/test_audit_standing_backlog_sources.py -v`.

## Acceptance Criteria

- IP-1, IP-2 landed; 5 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: enabling WITHDRAWN/ADVISORY recognition surfaces previously-hidden bridge entries; downstream consumers may need updates. Mitigation: post-impl smoke run checking audit output diff.
- Rollback: revert single-line regex change.

## Recommended Commit Type

`fix` - defect fix. ~5 LOC + tests.
