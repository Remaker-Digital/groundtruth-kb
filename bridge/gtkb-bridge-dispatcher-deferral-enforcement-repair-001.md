NEW

# Implementation Proposal - Repair Bridge Dispatcher Deferral Enforcement (GTKB-GOV-008)

bridge_kind: implementation_proposal
Document: gtkb-bridge-dispatcher-deferral-enforcement-repair
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-008

target_paths: ["scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge/freshness_parser.py", "tests/scripts/test_cross_harness_bridge_trigger.py"]

This NEW proposal repairs bridge dispatcher deferral enforcement defects identified in WI-3308 description: shared freshness parser ignores `DEFERRED` status, status recognition duplicated across parser paths, generated-wrapper handling conflicts with ignored output policy, owner-only mute authority decisions not recorded.

## Claim

Four-point repair: (1) extend freshness parser status vocabulary to include DEFERRED + WITHDRAWN + ADVISORY (aligning with the broader status taxonomy fix in sibling WI-3276); (2) consolidate duplicated status-recognition logic into one shared module; (3) ensure generated wrappers do NOT commit ignored outputs; (4) record owner-mute authority decisions in MemBase deliberation rows.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; dispatcher operates within it.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the dispatch substrate.
- `GOV-ARTIFACT-APPROVAL-001` - owner-mute decisions are governance acts.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ADOPTER-EXPERIENCE authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI description enumerates the 4 defect points.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1..IP-4 four discrete fixes + IP-5 tests single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Status vocabulary extension

Locate the freshness parser (`groundtruth-kb/src/groundtruth_kb/bridge/freshness_parser.py` or equivalent). Extend the recognized status set to include `DEFERRED`, `WITHDRAWN`, `ADVISORY` (aligns with WI-3276 sibling fix for audit script).

### IP-2: Consolidate status recognition

Find all sites that parse bridge status independently (e.g., scripts/cross_harness_bridge_trigger.py, scripts/audit_standing_backlog_sources.py, doctor checks). Move status recognition into a single function in the freshness_parser module; refactor callers.

### IP-3: Generated-wrapper output hygiene

Inspect generated-wrapper paths used by the cross-harness trigger. Ensure no output file is both regenerated AND under `.gitignore` (which would cause silent drops). If found: either commit the output (remove gitignore entry) or write to a non-tracked path.

### IP-4: Owner-mute authority decision recording

When the owner mutes a bridge dispatch via env var or hook bypass, record a DELIB row with `source_type=owner_conversation` and `outcome=mute_authority` for audit. Mute application captures: WI/thread ID, reason, expiration if any.

### IP-5: Tests

Tests for each IP.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| DEFERRED status recognized by parser | `test_freshness_parser_recognizes_deferred` |
| WITHDRAWN status recognized | `test_freshness_parser_recognizes_withdrawn` |
| Single parser module called by all sites | `test_status_recognition_centralized` |
| No gitignored output regenerated | `test_no_gitignored_regen_outputs` |
| Mute decision recorded as DELIB | `test_owner_mute_recorded_in_deliberations` |
| Cross-harness trigger uses consolidated parser | `test_trigger_uses_freshness_parser` |
| No regression in existing dispatcher tests | full suite still passes |

Run: `python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py groundtruth-kb/tests/bridge/ -v`.

## Acceptance Criteria

- IP-1..IP-5 landed; 6 tests PASS.
- No regression.
- Both preflights PASS.

## Risks / Rollback

- Risk: refactor of duplicated status logic may surface other consumers I haven't found. Mitigation: grep extensively before refactor; cite all found sites in post-impl report.
- Risk: owner-mute DELIB recording may need new schema field. Mitigation: reuse existing source_type/outcome enum values.
- Rollback: per-IP revert (each IP is independent).

## Recommended Commit Type

`fix` - multi-point defect repair. ~80 LOC + refactor.
