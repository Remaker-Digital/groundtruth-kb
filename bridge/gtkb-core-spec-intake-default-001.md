NEW

# Implementation Proposal - Make Core Application Spec Intake Default GT-KB Behavior (GTKB-CORE-001)

bridge_kind: implementation_proposal
Document: gtkb-core-spec-intake-default
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-CORE-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py", "groundtruth-kb/tests/test_core_spec_intake.py"]

This NEW proposal makes core application specification intake the default GT-KB behavior. Per owner directive 2026-04-22, after `gt project init` (any scaffold profile), GT-KB must repeatedly prompt the owner for missing core specifications until the baseline set is complete.

## Claim

Wire the core-spec intake loop (already specified as `SPEC-CORE-INTAKE-001..003` + `ADR-CORE-INTAKE-001` + `DCL-CORE-INTAKE-001`) into the default `gt project init` path so newly-scaffolded adopter projects enroll automatically. Existing projects opt-in via `gt project core-spec-intake enable`.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-CORE-INTAKE-001` - GT-KB prompts for missing core application specifications.
- `SPEC-CORE-INTAKE-002` - prompting stops at persisted completion.
- `ADR-CORE-INTAKE-001` - completion uses persisted MemBase evidence.
- `DCL-CORE-INTAKE-001` - preserves scaffold/automation compatibility.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - intake prompts surface candidate specs through approval path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-0875` - GTKB-CORE-001 Phase 0 governance approval.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ADOPTER-EXPERIENCE authorization including this WI.
- 2026-04-22: owner directive that core-spec intake be repeatedly prompted post-init.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-CORE-INTAKE-001..003 + ADR-CORE-INTAKE-001 + DCL-CORE-INTAKE-001 fully specify the loop behavior. This WI lands the default-on wiring.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 + IP-3 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Core-spec intake module

In `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` (new file):
1. Define baseline slot set per SPEC-CORE-INTAKE-001 (product identity, application type, tenancy, users/roles, data classification, compliance, security posture, reliability posture, external integrations, AI usage, operational/release path, first-release non-goals).
2. Function `next_missing_slot(db, project_id) -> slot_name | None` returns next unanswered required slot.
3. Function `mark_slot_complete(db, project_id, slot, value, source='owner_stated' | 'not_applicable')` persists.
4. Function `is_complete(db, project_id) -> bool` returns True only when every required slot is owner-stated or marked not-applicable.

### IP-2: Default-on scaffold wiring

In `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, modify `gt project init` to:
1. Enroll new projects by default (set `core_spec_intake_enabled=True` in project record).
2. Honor `--opt-out-core-spec-intake` for automation/unusual cases per DCL-CORE-INTAKE-001.
3. Emit initial probe prompt content into project's `MEMORY.md` "Pending Core Spec Intake" section.

### IP-3: Tests

Tests verify: default-on enrollment, opt-out path, slot transitions, completion detection, prompt cessation.

## Specification-Derived Verification Plan

| Spec | Test |
|---|---|
| SPEC-CORE-INTAKE-001: identifies next missing slot | `test_next_missing_slot_returns_baseline_order` |
| SPEC-CORE-INTAKE-002: prompts continue until complete | `test_prompts_continue_while_incomplete` |
| SPEC-CORE-INTAKE-002: prompts stop at completion | `test_prompts_stop_at_completion` |
| SPEC-CORE-INTAKE-002: not-applicable counts as complete | `test_not_applicable_satisfies_slot` |
| ADR-CORE-INTAKE-001: completion derived from MemBase | `test_completion_from_membase_evidence` |
| DCL-CORE-INTAKE-001: default-on for new projects | `test_default_on_new_project_init` |
| DCL-CORE-INTAKE-001: opt-out path works | `test_opt_out_flag_disables_intake` |

Run: `python -m pytest groundtruth-kb/tests/test_core_spec_intake.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 7 tests PASS.
- Both preflights PASS.
- `gt project init` on test fixture produces enrolled project + initial intake prompt.

## Risks / Rollback

- Risk: existing adopter projects break if intake auto-enrolls them on next session. Mitigation: only NEW `gt project init` invocations enroll; existing projects opt in explicitly.
- Rollback: revert scaffold default + module removal.

## Recommended Commit Type

`feat` - new default behavior + module. ~200 LOC.
