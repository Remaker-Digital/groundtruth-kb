REVISED

# Implementation Proposal - Core Application Spec Intake: Slice 1 (Default Enrollment + Initial Prompt) (GTKB-CORE-001)

bridge_kind: implementation_proposal
Document: gtkb-core-spec-intake-default
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-CORE-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py", "groundtruth-kb/tests/test_core_spec_intake.py"]

This REVISED proposal lands the first slice of GTKB-CORE-001: default-on core-spec-intake enrollment plus the initial probe prompt. It is explicitly narrowed (per the `-002` NO-GO F2 accepted path) and does not claim to deliver the full cross-session repeated prompt loop in this slice.

## Revision Notes

This `-003` revision addresses every finding in the `-002` NO-GO:

- **F1 (P1) — cites a non-existent spec `SPEC-CORE-INTAKE-003`.** A live MemBase query (`SELECT id,status,type FROM current_specifications WHERE id LIKE 'SPEC-CORE-INTAKE%'`) confirms only `SPEC-CORE-INTAKE-001` and `SPEC-CORE-INTAKE-002` exist (plus `ADR-CORE-INTAKE-001` and `DCL-CORE-INTAKE-001`). All `SPEC-CORE-INTAKE-003` references are removed from `## Claim` and `## Requirement Sufficiency`. This proposal cites only currently-existing specs and does not create a new specification.
- **F2 (P1) — proposed scope under-implements the repeated prompt loop the claim promised.** Per the NO-GO's accepted first option, the claim is **narrowed to a first slice**: this slice delivers only (a) default-on enrollment of newly `gt project init`-scaffolded projects and (b) emission of the *initial* probe prompt into the scaffolded project's `MEMORY.md`. The cross-session repeated-prompt surface (session-start re-prompt, doctor surface, CLI answer-capture, owner-answer provenance capture) is explicitly **out of scope for this slice** and is named as a follow-on slice. The `## Claim`, `## Proposed Scope`, and `## Out Of Scope (Follow-On Slices)` sections now state this narrowing plainly so a GO authorizes exactly what is implemented and tested. The slot-state primitives (`next_missing_slot`, `mark_slot_complete`, `is_complete`) are still implemented in this slice because the initial-prompt content is derived from them and they are unit-testable in isolation, but the *driver* that re-invokes the prompt across sessions is the follow-on slice.
- **F3 (P2) — opt-in CLI claim (`gt project core-spec-intake enable`) not authorized by `target_paths`/tests.** Per the NO-GO's accepted first option, the opt-in CLI claim is **removed** from this slice. No `gt project core-spec-intake enable` command is proposed, authorized, or tested here. Enabling intake on pre-existing projects is named as part of the follow-on slice. `target_paths` is unchanged (scaffold + module + one test file); it contains no CLI file, consistent with the removed claim.
- **F4 (P2) — applicability preflight found uncited advisory specs.** The three advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are now cited in `## Specification Links`; they are relevant because this proposal concerns prompting for owner-stated requirements and preserving specification evidence.

No owner-decision scope change; the project authorization, project, and work item are unchanged from `-001`. The narrowing reduces deliverable scope; it does not add any owner-decision surface.

## Claim

Land the first slice of GTKB-CORE-001. After `gt project init` (any scaffold profile), newly-scaffolded adopter projects are enrolled in core-spec intake by default, and the project's `MEMORY.md` receives an initial "Pending Core Spec Intake" probe prompt for the first missing core-specification slot. Automation/unusual cases opt out with `--opt-out-core-spec-intake` per `DCL-CORE-INTAKE-001`. This slice does NOT deliver the cross-session repeated prompt loop or a CLI to enable intake on pre-existing projects; those are named follow-on slices (see `## Out Of Scope`).

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. `groundtruth-kb/src/groundtruth_kb/project/**` and `groundtruth-kb/tests/**` are in-root platform-package paths.

## Specification Links

- `SPEC-CORE-INTAKE-001` - GT-KB prompts for missing core application specifications; this slice emits the initial prompt for the first missing slot.
- `SPEC-CORE-INTAKE-002` - prompting stops at persisted completion; this slice implements the `is_complete` / `next_missing_slot` primitives the cessation logic rests on (the cross-session driver itself is a follow-on slice).
- `ADR-CORE-INTAKE-001` - completion uses persisted MemBase evidence; this slice derives slot state from persisted MemBase records.
- `DCL-CORE-INTAKE-001` - preserves scaffold/automation compatibility; honored by the `--opt-out-core-spec-intake` flag and by leaving non-init `gt project init` behavior unchanged.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - intake prompts surface candidate specs through the owner-visible approval path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan below maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-tracked work; GTKB-CORE-001 is the governed work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; an intake prompt is a lifecycle trigger toward a candidate specification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as governed artifacts (WI + bridge thread + spec-derived tests).
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization including PROJECT-GTKB-ADOPTER-EXPERIENCE and work item GTKB-CORE-001.
- `DELIB-0875` - GTKB-CORE-001 Phase 0 governance approval.
- `DELIB-0898` - prior `gtkb-core-spec-intake` bridge thread (protocol-only closure/withdrawal loop); informs keeping this slice tightly scoped.
- `DELIB-1181` - prior `gtkb-core-spec-intake` bridge thread record.
- `DELIB-0897` - prior `gtkb-core-spec-intake-phase1` package-module slice; precedent for the module placement under `groundtruth_kb/project/`.
- `DELIB-1182` - prior `gtkb-core-spec-intake-phase1` bridge thread record.
- `DELIB-0893` - prior `gtkb-core-spec-intake-phase3a-cli` read-only CLI slice; the CLI surface is out of scope for this slice and remains follow-on work.

No prior deliberation rejected default-on enrollment plus an initial prompt as a first slice; the `-002` NO-GO explicitly offered this narrowing as an accepted path.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the PROJECT-GTKB-ADOPTER-EXPERIENCE authorization batch (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`), including this work item GTKB-CORE-001. The authorization `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH` is active and lists `GTKB-CORE-001` in its `included_work_item_ids`.
- 2026-04-22: owner directive that core-spec intake be repeatedly prompted post-init. This slice is the first increment toward that directive; the repeated-prompt driver is the named follow-on slice.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and `DCL-CORE-INTAKE-001` (all confirmed present in current MemBase) fully specify the intake-loop behavior. This slice lands the default-on enrollment plus initial-prompt increment of that specified behavior. No new or revised requirement or specification is created by this work. (The `-001` claim of `SPEC-CORE-INTAKE-003` was incorrect; that spec does not exist and is not relied on.)

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk backlog operation. It performs no batch resolve, promote, or retire of work items or specifications. It implements a single work item (GTKB-CORE-001), a single first slice. References to "work item", "backlog", and "standing backlog" describe that single governed work item and its membership in PROJECT-GTKB-ADOPTER-EXPERIENCE per the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. The review-packet inventory is a single thread: IP-1 (module) + IP-2 (scaffold wiring) + IP-3 (tests). The inventory of touched files is the three `target_paths` entries above; no formal artifact is created.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is appended under the existing `Document: gtkb-core-spec-intake-default` block above the prior `NO-GO` and `NEW` lines; the prior versions are preserved unchanged (append-only audit trail).

## Proposed Scope

### IP-1: Core-spec intake module

`groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` (new file):

1. Define the baseline slot set per `SPEC-CORE-INTAKE-001` (product identity, application type, tenancy, users/roles, data classification, compliance, security posture, reliability posture, external integrations, AI usage, operational/release path, first-release non-goals).
2. Function `next_missing_slot(db, project_id) -> slot_name | None` returns the next unanswered required slot in baseline order.
3. Function `mark_slot_complete(db, project_id, slot, value, source='owner_stated' | 'not_applicable')` persists slot state to MemBase-backed evidence.
4. Function `is_complete(db, project_id) -> bool` returns True only when every required slot is owner-stated or marked not-applicable.

These primitives are implemented and unit-tested in this slice because the initial-prompt content is derived from `next_missing_slot`. The cross-session *driver* that re-invokes the prompt is a follow-on slice (see `## Out Of Scope`).

### IP-2: Default-on scaffold wiring (initial prompt only)

In `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, modify the `gt project init` path to:

1. Enroll newly-scaffolded projects by default (set `core_spec_intake_enabled=True` in the project record).
2. Honor a new `--opt-out-core-spec-intake` flag for automation/unusual cases per `DCL-CORE-INTAKE-001`.
3. Emit the *initial* probe prompt content (the first missing slot, via `next_missing_slot`) into the scaffolded project's `MEMORY.md` under a "Pending Core Spec Intake" section.

This slice changes only the `gt project init` scaffold path. It does not add any session-start, doctor, dashboard, or CLI re-prompt surface.

### IP-3: Tests

`groundtruth-kb/tests/test_core_spec_intake.py`: tests verify default-on enrollment, the opt-out path, slot transitions, completion detection, and the initial-prompt emission.

## Out Of Scope (Follow-On Slices)

The following are explicitly NOT delivered by this slice and are named as follow-on work so a GO does not over-authorize:

- The cross-session repeated prompt loop: a session-start (or doctor/dashboard) surface that re-asks the next missing slot every session until completion, and the owner-answer capture surface with owner-stated/confirmation-needed provenance.
- A CLI to enable intake on pre-existing (non-init) projects (e.g., `gt project core-spec-intake enable`). Pre-existing projects are not auto-enrolled by this slice and there is no enable command in this slice.

These follow-on slices will be filed as their own bridge proposals with their own `target_paths` and spec-derived tests, including a persisted-state / multi-session test proving prompt continuation and cessation.

## Specification-Derived Verification Plan

Each linked specification clause exercised by this slice maps to at least one test. Tests are added only within the `target_paths` test file.

| Spec clause exercised by this slice | Test | Covers |
|---|---|---|
| SPEC-CORE-INTAKE-001: identifies the next missing slot in baseline order | `test_next_missing_slot_returns_baseline_order` | SPEC-CORE-INTAKE-001 |
| SPEC-CORE-INTAKE-002: `is_complete` primitive is False while a required slot is unanswered | `test_is_complete_false_while_incomplete` | SPEC-CORE-INTAKE-002 |
| SPEC-CORE-INTAKE-002: `is_complete` primitive is True once every slot is owner-stated/not-applicable | `test_is_complete_true_when_all_slots_resolved` | SPEC-CORE-INTAKE-002 |
| SPEC-CORE-INTAKE-002: not-applicable counts toward completion | `test_not_applicable_satisfies_slot` | SPEC-CORE-INTAKE-002 |
| ADR-CORE-INTAKE-001: slot state derived from persisted MemBase evidence | `test_slot_state_from_membase_evidence` | ADR-CORE-INTAKE-001 |
| DCL-CORE-INTAKE-001: default-on enrollment on new `gt project init` | `test_default_on_new_project_init` | DCL-CORE-INTAKE-001, SPEC-CORE-INTAKE-001 |
| DCL-CORE-INTAKE-001: `--opt-out-core-spec-intake` disables enrollment | `test_opt_out_flag_disables_intake` | DCL-CORE-INTAKE-001 |
| SPEC-CORE-INTAKE-001 + GOV-CHAT-DERIVED-SPEC-APPROVAL-001: initial probe prompt for the first missing slot is emitted into `MEMORY.md` | `test_initial_prompt_emitted_into_memory_md` | SPEC-CORE-INTAKE-001, GOV-CHAT-DERIVED-SPEC-APPROVAL-001 |

Verification commands (run from the `groundtruth-kb` package root, the lane for `groundtruth-kb/tests/**`):

```
cd groundtruth-kb && python -m pytest tests/test_core_spec_intake.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; all eight listed tests PASS.
- No reference to `SPEC-CORE-INTAKE-003` remains anywhere in the proposal or implementation; only currently-existing specs are cited (F1 resolved).
- The deliverable is exactly default-on enrollment + initial-prompt emission; the cross-session repeated-prompt loop and the opt-in CLI are not implemented and are named as follow-on slices (F2, F3 resolved).
- The three advisory specs are cited in `## Specification Links` (F4 resolved).
- `gt project init` on a test fixture produces an enrolled project plus an initial "Pending Core Spec Intake" prompt; `--opt-out-core-spec-intake` produces no enrollment.
- `ruff check` and `ruff format --check` are clean.
- Both preflights PASS.

## Risks / Rollback

- Risk: existing adopter projects break if intake auto-enrolls them. Mitigation: only NEW `gt project init` invocations enroll; pre-existing projects are untouched by this slice and there is no auto-enroll path for them.
- Risk: the slot-state primitives are landed without the driver that uses them across sessions, leaving partially-wired behavior. Mitigation: the primitives are pure functions, unit-tested in isolation, and the initial-prompt path does use `next_missing_slot`; the follow-on slice consumes the same primitives with no rework.
- Rollback: revert the scaffold default-on change in `scaffold.py`; delete `core_spec_intake.py` and its test file. No pre-existing project is affected.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` — new core-spec intake module with the slot-set definition and the `next_missing_slot` / `mark_slot_complete` / `is_complete` primitives (IP-1).
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` — `gt project init` default-on enrollment, `--opt-out-core-spec-intake` flag, and initial-prompt emission into the scaffolded `MEMORY.md` (IP-2).
- `groundtruth-kb/tests/test_core_spec_intake.py` — new spec-derived tests for enrollment, opt-out, slot primitives, completion detection, and initial-prompt emission (IP-3).

## Recommended Commit Type

`feat` - net-new core-spec intake module plus a new default-on scaffold behavior. ~150 LOC of source + tests (reduced from the `-001` ~200 LOC estimate because the cross-session driver and the CLI are deferred to follow-on slices).

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after filing the INDEX entry; outputs are embedded in `## Applicability Preflight` and `## Clause Applicability` below.

## Applicability Preflight

- packet_hash: `sha256:9ae7565958db5b41cd6664498d5282a3db3d311d225a91072f87e6c524d0126a`
- bridge_document_name: `gtkb-core-spec-intake-default`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-core-spec-intake-default-003.md`
- operative_file: `bridge/gtkb-core-spec-intake-default-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-core-spec-intake-default`
- Operative file: `bridge\gtkb-core-spec-intake-default-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Result: exit 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
