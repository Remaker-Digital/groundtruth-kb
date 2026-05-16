REVISED

# Implementation Proposal - Core Application Spec Intake: Slice 1 (Default Enrollment + Initial Prompt) (GTKB-CORE-001)

bridge_kind: implementation_proposal
Document: gtkb-core-spec-intake-default
Version: 005
Responds to: bridge/gtkb-core-spec-intake-default-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-CORE-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_core_spec_intake.py"]

This REVISED-2 (`-005`) lands the first slice of GTKB-CORE-001: default-on core-spec-intake enrollment plus the initial probe prompt. It is explicitly narrowed (per the `-002` NO-GO F2 accepted path) and does not claim to deliver the full cross-session repeated prompt loop in this slice.

## Revision Notes

This `-005` REVISED-2 addresses the single finding in the `-004` NO-GO (round-2 review), and carries forward all `-003` (round-1) fixes without regression.

### Round-2 NO-GO (`-004`) — finding-to-fix mapping

- **FINDING-P1-001 (P1) — the new `gt project init` opt-out flag is not authorized by `target_paths`.** Resolved via the NO-GO's **Option 1** (add the CLI parser file and a CLI-level test; do NOT narrow away the flag). Specifically:
  - `target_paths` now adds `groundtruth-kb/src/groundtruth_kb/cli.py`. The four authorized files are: the new module, `scaffold.py`, `cli.py`, and the one test file.
  - IP-2 is split into **IP-2a (CLI parser surface)** and **IP-2b (scaffold engine wiring)** so the proposal describes concretely how the `--opt-out-core-spec-intake` flag is declared on the `gt project init` Click command and how it threads into the scaffold path. The live `gt project init` command is the Click command `project_init` in `groundtruth-kb/src/groundtruth_kb/cli.py` (the command and its existing options are declared starting at the `@project.command("init")` decorator; the body constructs `ScaffoldOptions(...)` and calls `scaffold_project()`). The new flag is declared as a `--opt-out-core-spec-intake` boolean `is_flag` option on that command, added to the `project_init(...)` signature, and passed into `ScaffoldOptions` as a new `opt_out_core_spec_intake: bool = False` field. `scaffold.py` reads `ScaffoldOptions.opt_out_core_spec_intake` to decide whether to enroll.
  - The verification plan now includes a **CLI-level test** `test_project_init_opt_out_flag_disables_intake` that invokes the actual `gt project init` command (via `click.testing.CliRunner`, the existing command-test pattern in `groundtruth-kb/tests/`) with `--opt-out-core-spec-intake` and asserts the scaffolded project is NOT enrolled — proving the command parser accepts the flag and threads it into the scaffold path. The prior `test_opt_out_flag_disables_intake` is retained to cover the `ScaffoldOptions` field at the engine layer; both tests are now in scope.
  - The `## Claim`, IP-2a/IP-2b, the verification plan, `## Acceptance Criteria`, and `## Files Expected To Change` now all consistently describe a CLI flag whose parser file is inside `target_paths`. A GO on `-005` authorizes exactly the files needed to make `gt project init --opt-out-core-spec-intake` real and tested — closing the round-2 overclaim.

### Round-1 NO-GO (`-002`) fixes carried forward unchanged

- **F1 (P1) — cited a non-existent spec `SPEC-CORE-INTAKE-003`.** A live MemBase query confirmed only `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and `DCL-CORE-INTAKE-001` exist. No `SPEC-CORE-INTAKE-003` reference remains; this proposal cites only currently-existing specs and creates no new specification.
- **F2 (P1) — proposed scope under-implemented the repeated prompt loop the claim promised.** The claim remains narrowed to a first slice: (a) default-on enrollment of newly `gt project init`-scaffolded projects and (b) emission of the *initial* probe prompt into the scaffolded project's `MEMORY.md`. The cross-session repeated-prompt surface is explicitly out of scope and named as a follow-on slice (see `## Out Of Scope`).
- **F3 (P2) — opt-in CLI claim (`gt project core-spec-intake enable`) not authorized.** That opt-in command remains removed from this slice. Note this is distinct from the `--opt-out-core-spec-intake` flag, which the round-2 NO-GO explicitly required to be made real (FINDING-P1-001 Option 1): the opt-out flag is part of the `gt project init` scaffold path this slice already changes, whereas the removed opt-in command was a separate `gt project core-spec-intake enable` subcommand for pre-existing projects. Pre-existing-project enablement remains follow-on work.
- **F4 (P2) — applicability preflight found uncited advisory specs.** The three advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) remain cited in `## Specification Links`.

No owner-decision scope change; the project authorization, project, and work item are unchanged from `-001`. Adding `cli.py` to `target_paths` enlarges the implementation file set to match the already-claimed CLI flag; it does not add any owner-decision surface and does not change the deliverable's externally-visible scope.

## Claim

Land the first slice of GTKB-CORE-001. After `gt project init` (any scaffold profile), newly-scaffolded adopter projects are enrolled in core-spec intake by default, and the project's `MEMORY.md` receives an initial "Pending Core Spec Intake" probe prompt for the first missing core-specification slot. Automation/unusual cases opt out with a new `--opt-out-core-spec-intake` flag on the `gt project init` command per `DCL-CORE-INTAKE-001`; the flag is declared on the Click command in `groundtruth-kb/src/groundtruth_kb/cli.py` (an authorized target path) and threaded into the scaffold path via `ScaffoldOptions`. This slice does NOT deliver the cross-session repeated prompt loop or a CLI to enable intake on pre-existing projects; those are named follow-on slices (see `## Out Of Scope`).

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. `groundtruth-kb/src/groundtruth_kb/project/**`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `groundtruth-kb/tests/**` are in-root platform-package paths.

## Specification Links

- `SPEC-CORE-INTAKE-001` - GT-KB prompts for missing core application specifications; this slice emits the initial prompt for the first missing slot.
- `SPEC-CORE-INTAKE-002` - prompting stops at persisted completion; this slice implements the `is_complete` / `next_missing_slot` primitives the cessation logic rests on (the cross-session driver itself is a follow-on slice).
- `ADR-CORE-INTAKE-001` - completion uses persisted MemBase evidence; this slice derives slot state from persisted MemBase records.
- `DCL-CORE-INTAKE-001` - preserves scaffold/automation compatibility; honored by the `--opt-out-core-spec-intake` flag on `gt project init` and by leaving non-init behavior unchanged.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - intake prompts surface candidate specs through the owner-visible approval path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan below maps every linked spec to a test, including a CLI-level test for the opt-out flag.
- `GOV-STANDING-BACKLOG-001` - WI-tracked work; GTKB-CORE-001 is the governed work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; an intake prompt is a lifecycle trigger toward a candidate specification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as governed artifacts (WI + bridge thread + spec-derived tests).
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization including PROJECT-GTKB-ADOPTER-EXPERIENCE and work item GTKB-CORE-001.
- `DELIB-0875` - GTKB-CORE-001 Phase 0 governance approval, including default enrollment, explicit opt-out, persisted stop conditions, and the cross-session prompt loop as the broader approved direction (cited in the `-004` NO-GO Prior Deliberations).
- `DELIB-0898` - prior `gtkb-core-spec-intake` bridge thread (protocol-only closure/withdrawal loop); informs keeping this slice tightly scoped.
- `DELIB-1181` - prior `gtkb-core-spec-intake` bridge thread record.
- `DELIB-0897` - prior `gtkb-core-spec-intake-phase1` package-module slice; precedent for the module placement under `groundtruth_kb/project/`.
- `DELIB-1182` - prior `gtkb-core-spec-intake-phase1` bridge thread record.
- `DELIB-0893` - prior `gtkb-core-spec-intake-phase3a-cli` read-only CLI slice; relevant to keeping command-surface claims explicitly scoped — the `-005` revision applies this by making the one claimed CLI flag concrete with its parser file in `target_paths`, while leaving the broader CLI re-prompt surface as follow-on work.

No prior deliberation rejected default-on enrollment plus an initial prompt as a first slice; the `-002` NO-GO explicitly offered this narrowing as an accepted path, and the `-004` NO-GO explicitly offered adding the CLI parser file as an accepted path. No retrieved deliberation waives the bridge requirement that implementation authorization target every file required by the claimed behavior.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the PROJECT-GTKB-ADOPTER-EXPERIENCE authorization batch (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`), including this work item GTKB-CORE-001. The authorization `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH` is active and lists `GTKB-CORE-001` in its `included_work_item_ids`.
- 2026-04-22: owner directive that core-spec intake be repeatedly prompted post-init. This slice is the first increment toward that directive; the repeated-prompt driver is the named follow-on slice.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and `DCL-CORE-INTAKE-001` (all confirmed present in current MemBase) fully specify the intake-loop behavior. This slice lands the default-on enrollment plus initial-prompt increment of that specified behavior, including the `DCL-CORE-INTAKE-001` opt-out path expressed as a `gt project init --opt-out-core-spec-intake` flag. No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk backlog operation. It performs no batch resolve, promote, or retire of work items or specifications. It implements a single work item (GTKB-CORE-001), a single first slice. References to "work item", "backlog", and "standing backlog" describe that single governed work item and its membership in PROJECT-GTKB-ADOPTER-EXPERIENCE per the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. The review-packet inventory is a single thread: IP-1 (module) + IP-2a (CLI parser) + IP-2b (scaffold wiring) + IP-3 (tests). The inventory of touched files is the four `target_paths` entries above; no formal artifact is created.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-005` REVISED line is inserted under the existing `Document: gtkb-core-spec-intake-default` block above the prior `-004` NO-GO, `-003` REVISED, `-002` NO-GO, and `-001` NEW lines; the prior versions are preserved unchanged (append-only audit trail).

## Proposed Scope

### IP-1: Core-spec intake module

`groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` (new file):

1. Define the baseline slot set per `SPEC-CORE-INTAKE-001` (product identity, application type, tenancy, users/roles, data classification, compliance, security posture, reliability posture, external integrations, AI usage, operational/release path, first-release non-goals).
2. Function `next_missing_slot(db, project_id) -> slot_name | None` returns the next unanswered required slot in baseline order.
3. Function `mark_slot_complete(db, project_id, slot, value, source='owner_stated' | 'not_applicable')` persists slot state to MemBase-backed evidence.
4. Function `is_complete(db, project_id) -> bool` returns True only when every required slot is owner-stated or marked not-applicable.

These primitives are implemented and unit-tested in this slice because the initial-prompt content is derived from `next_missing_slot`. The cross-session *driver* that re-invokes the prompt is a follow-on slice (see `## Out Of Scope`).

### IP-2a: CLI parser surface — `gt project init --opt-out-core-spec-intake` (FINDING-P1-001 closure)

In `groundtruth-kb/src/groundtruth_kb/cli.py`, on the existing `project_init` Click command (decorated `@project.command("init")`):

1. Add a `@click.option("--opt-out-core-spec-intake", is_flag=True, default=False, help="Skip default core-spec intake enrollment for this project (automation/unusual cases).")` declaration alongside the command's existing options.
2. Add the corresponding `opt_out_core_spec_intake: bool` parameter to the `project_init(...)` function signature.
3. Thread the value into the `ScaffoldOptions(...)` constructor call already present in the command body, as a new keyword argument `opt_out_core_spec_intake=opt_out_core_spec_intake`.

This is the file that must be edited to make the command-line flag real; it is now an authorized target path. No other CLI command is touched.

### IP-2b: Default-on scaffold wiring (initial prompt only)

In `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`:

1. Add an `opt_out_core_spec_intake: bool = False` field to the `ScaffoldOptions` dataclass.
2. Modify the `gt project init` scaffold path so that, unless `opt_out_core_spec_intake` is True, newly-scaffolded projects are enrolled by default (set `core_spec_intake_enabled=True` in the project record).
3. When enrolled, emit the *initial* probe prompt content (the first missing slot, via `next_missing_slot`) into the scaffolded project's `MEMORY.md` under a "Pending Core Spec Intake" section.
4. When `opt_out_core_spec_intake` is True, perform no enrollment and emit no intake prompt.

This slice changes only the `gt project init` scaffold path. It does not add any session-start, doctor, dashboard, or CLI re-prompt surface.

### IP-3: Tests

`groundtruth-kb/tests/test_core_spec_intake.py`: tests verify default-on enrollment, the engine-layer opt-out path (`ScaffoldOptions.opt_out_core_spec_intake`), the CLI-layer opt-out path (the actual `gt project init --opt-out-core-spec-intake` command), slot transitions, completion detection, and the initial-prompt emission.

## Out Of Scope (Follow-On Slices)

The following are explicitly NOT delivered by this slice and are named as follow-on work so a GO does not over-authorize:

- The cross-session repeated prompt loop: a session-start (or doctor/dashboard) surface that re-asks the next missing slot every session until completion, and the owner-answer capture surface with owner-stated/confirmation-needed provenance.
- A CLI to enable intake on pre-existing (non-init) projects (e.g., `gt project core-spec-intake enable`). Pre-existing projects are not auto-enrolled by this slice and there is no enable command in this slice. (Distinct from the in-scope `--opt-out-core-spec-intake` flag on `gt project init`.)

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
| DCL-CORE-INTAKE-001: engine-layer opt-out — `ScaffoldOptions.opt_out_core_spec_intake=True` disables enrollment | `test_opt_out_flag_disables_intake` | DCL-CORE-INTAKE-001 |
| DCL-CORE-INTAKE-001: CLI-layer opt-out — `gt project init --opt-out-core-spec-intake` invoked via `CliRunner` accepts the flag and produces no enrollment | `test_project_init_opt_out_flag_disables_intake` | DCL-CORE-INTAKE-001 |
| SPEC-CORE-INTAKE-001 + GOV-CHAT-DERIVED-SPEC-APPROVAL-001: initial probe prompt for the first missing slot is emitted into `MEMORY.md` | `test_initial_prompt_emitted_into_memory_md` | SPEC-CORE-INTAKE-001, GOV-CHAT-DERIVED-SPEC-APPROVAL-001 |

`test_project_init_opt_out_flag_disables_intake` is the CLI-level test required by the `-004` NO-GO: it exercises the actual `gt project init` Click command (via `click.testing.CliRunner`, the existing command-test pattern in `groundtruth-kb/tests/`) and asserts the command parser accepts `--opt-out-core-spec-intake` and threads it into the scaffold path. `test_opt_out_flag_disables_intake` covers the same behavior at the `ScaffoldOptions` engine layer.

Verification commands (run from the `groundtruth-kb` package root, the lane for `groundtruth-kb/tests/**`):

```
cd groundtruth-kb && python -m pytest tests/test_core_spec_intake.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

- IP-1, IP-2a, IP-2b, IP-3 landed; all nine listed tests PASS.
- No reference to `SPEC-CORE-INTAKE-003` remains anywhere in the proposal or implementation; only currently-existing specs are cited (round-1 F1 resolved).
- The deliverable is exactly default-on enrollment + initial-prompt emission + the `gt project init --opt-out-core-spec-intake` flag; the cross-session repeated-prompt loop and the opt-in `gt project core-spec-intake enable` CLI are not implemented and are named as follow-on slices (round-1 F2, F3 resolved).
- The `--opt-out-core-spec-intake` flag is declared on the `gt project init` Click command in `groundtruth-kb/src/groundtruth_kb/cli.py` (an authorized target path), is threaded into `ScaffoldOptions`, and is proven by the CLI-level test `test_project_init_opt_out_flag_disables_intake` (round-2 FINDING-P1-001 resolved).
- The three advisory specs are cited in `## Specification Links` (round-1 F4 resolved).
- `gt project init` on a test fixture produces an enrolled project plus an initial "Pending Core Spec Intake" prompt; `gt project init --opt-out-core-spec-intake` produces no enrollment and no prompt.
- `ruff check` and `ruff format --check` are clean.
- Both preflights PASS.

## Risks / Rollback

- Risk: existing adopter projects break if intake auto-enrolls them. Mitigation: only NEW `gt project init` invocations enroll; pre-existing projects are untouched by this slice and there is no auto-enroll path for them.
- Risk: the slot-state primitives are landed without the driver that uses them across sessions, leaving partially-wired behavior. Mitigation: the primitives are pure functions, unit-tested in isolation, and the initial-prompt path does use `next_missing_slot`; the follow-on slice consumes the same primitives with no rework.
- Risk: the new `cli.py` Click option drifts from the `ScaffoldOptions` field. Mitigation: the CLI-level test `test_project_init_opt_out_flag_disables_intake` exercises the full command-to-scaffold path, so a parameter-threading break fails a test.
- Rollback: revert the `--opt-out-core-spec-intake` option block and signature/`ScaffoldOptions` argument in `cli.py`; revert the `ScaffoldOptions` field and the scaffold default-on change in `scaffold.py`; delete `core_spec_intake.py` and its test file. No pre-existing project is affected.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` — new core-spec intake module with the slot-set definition and the `next_missing_slot` / `mark_slot_complete` / `is_complete` primitives (IP-1).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — new `--opt-out-core-spec-intake` Click option on the `gt project init` command, the corresponding `project_init(...)` signature parameter, and the keyword threaded into the `ScaffoldOptions(...)` constructor call (IP-2a).
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` — new `ScaffoldOptions.opt_out_core_spec_intake` field, `gt project init` default-on enrollment honoring that field, and initial-prompt emission into the scaffolded `MEMORY.md` (IP-2b).
- `groundtruth-kb/tests/test_core_spec_intake.py` — new spec-derived tests for enrollment, engine-layer opt-out, CLI-layer opt-out, slot primitives, completion detection, and initial-prompt emission (IP-3).

## Recommended Commit Type

`feat` - net-new core-spec intake module, a new `gt project init` Click flag, and a new default-on scaffold behavior. ~165 LOC of source + tests (the `-003` ~150 LOC estimate plus the small `cli.py` option block and the additional CLI-level test).

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-005` content after filing the INDEX entry; outputs are embedded in `## Applicability Preflight` and `## Clause Applicability` below.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-default`

- packet_hash: `sha256:c4ea16ddee057b57b713eb0fa06c47a1049308612d11e3b918c15d37ab4a220c`
- bridge_document_name: `gtkb-core-spec-intake-default`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-core-spec-intake-default-005.md`
- operative_file: `bridge/gtkb-core-spec-intake-default-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-default`

- Bridge id: `gtkb-core-spec-intake-default`
- Operative file: `bridge\gtkb-core-spec-intake-default-005.md`
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

Slice 2 mandatory gate note: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate when evidence is absent and no explicit
owner-waiver line is cited. No blocking gaps were reported here.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
