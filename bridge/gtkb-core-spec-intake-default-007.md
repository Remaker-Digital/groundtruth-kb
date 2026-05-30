NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex Desktop default reasoning

# Post-Implementation Report - Core Spec Intake Default Slice 1

bridge_kind: implementation_report
Document: gtkb-core-spec-intake-default
Version: 007
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Implemented from GO: `bridge/gtkb-core-spec-intake-default-006.md`
Approved proposal: `bridge/gtkb-core-spec-intake-default-005.md`
Implementation authorization packet: `sha256:c300c819fe009cd495fe17a6bc51a57539d2c2f6f8bac0b38e6a82ab4bc08282`

## Implementation Claim

Implemented the approved first slice of `GTKB-CORE-001`: newly scaffolded adopter projects are enrolled in core-spec intake by default, the first missing core-specification prompt is appended to the scaffolded `MEMORY.md`, and `gt project init --opt-out-core-spec-intake` suppresses both enrollment and prompt emission.

The implementation adds a scoped `groundtruth_kb.project.core_spec_intake` module with the approved baseline slot set, `next_missing_slot`, `mark_slot_complete`, and `is_complete` primitives. Slot completions are persisted as current MemBase specification rows keyed by project and slot. Enrollment is persisted in the adopter database as a first-class project record with `core_spec_intake_enabled=true` in structured project notes.

This slice does not add a cross-session prompt driver, doctor/dashboard re-prompt surface, owner-answer capture command, or a `gt project core-spec-intake enable` command for pre-existing projects.

## Files Changed In This Implementation Scope

- `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` - new core-spec intake module with the baseline slots, MemBase-backed slot completion primitives, project enrollment helper, and initial `MEMORY.md` prompt renderer.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` - added `ScaffoldOptions.opt_out_core_spec_intake`; default scaffold path now enrolls the new project and appends the first pending prompt unless the option is true.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - added `--opt-out-core-spec-intake` to the existing `gt project init` Click command and threaded it into `ScaffoldOptions`.
- `groundtruth-kb/tests/test_core_spec_intake.py` - added spec-derived tests for slot order, completion, not-applicable handling, MemBase evidence, default enrollment, engine/CLI opt-out, CLI default-on behavior, and prompt emission.

Bridge filing also adds this post-implementation report as `bridge/gtkb-core-spec-intake-default-007.md` and updates `bridge/INDEX.md` with a new `NEW:` line for Loyal Opposition verification.

## Existing Dirty Target Note

Before this slice began, `groundtruth-kb/src/groundtruth_kb/cli.py` already contained an unrelated dirty change adding `bridge_group` from `groundtruth_kb.cli_bridge_propose`. I preserved that existing work and only changed the authorized `gt project init` option/signature/`ScaffoldOptions` call path for this slice.

`groundtruth-kb/src/groundtruth_kb/project/scaffold.py` was formatted by Ruff after the authorized edits. That produced small line-wrapping changes inside the same authorized file, but no unrelated behavior change.

## Specification Links

- `SPEC-CORE-INTAKE-001` - prompts for missing core application specifications; this implementation emits the initial prompt for the first missing slot.
- `SPEC-CORE-INTAKE-002` - prompting stops at persisted completion; this implementation adds `is_complete` and `next_missing_slot` over persisted slot evidence.
- `ADR-CORE-INTAKE-001` - completion uses persisted MemBase evidence; slot completions are stored as specification rows.
- `DCL-CORE-INTAKE-001` - scaffold/automation compatibility; `--opt-out-core-spec-intake` suppresses enrollment and prompt emission.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - initial prompt text is owner-visible and points toward owner-stated or not-applicable completion.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governs this report and INDEX transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved proposal's governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specifications to executed tests.
- `GOV-STANDING-BACKLOG-001` - `GTKB-CORE-001` is the tracked work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, bridge thread, project record, slot specs, and tests form the durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the initial prompt is a lifecycle trigger toward core specification capture.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - implementation state is captured through governed artifacts and tests.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Owner Decisions / Input

No new owner decision was required. This implementation carries forward `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`, which authorized the `PROJECT-GTKB-ADOPTER-EXPERIENCE` batch containing `GTKB-CORE-001`.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-approved batch authorization including `GTKB-CORE-001`.
- `DELIB-0875` - Phase 0 direction for default enrollment, explicit opt-out, persisted stop conditions, and the broader repeated prompt loop.
- `DELIB-0898` / `DELIB-1181` - prior `gtkb-core-spec-intake` bridge thread context.
- `DELIB-0897` - prior package-module slice context.
- `DELIB-0893` - prior read-only CLI slice context.
- `bridge/gtkb-core-spec-intake-default-005.md` - approved revised implementation proposal.
- `bridge/gtkb-core-spec-intake-default-006.md` - Loyal Opposition GO verdict authorizing this implementation.

## Specification-Derived Verification Plan

| Specification / behavior | Test or command | Observed result |
|---|---|---|
| `SPEC-CORE-INTAKE-001`: identify next missing slot in baseline order | `test_next_missing_slot_returns_baseline_order` | PASS in targeted suite |
| `SPEC-CORE-INTAKE-002`: incomplete state is not complete | `test_is_complete_false_while_incomplete` | PASS in targeted suite |
| `SPEC-CORE-INTAKE-002`: all owner-stated slots complete the intake baseline | `test_is_complete_true_when_all_slots_resolved` | PASS in targeted suite |
| `SPEC-CORE-INTAKE-002`: not-applicable satisfies a slot | `test_not_applicable_satisfies_slot` | PASS in targeted suite |
| `ADR-CORE-INTAKE-001`: slot state is derived from persisted MemBase evidence | `test_slot_state_from_membase_evidence` | PASS in targeted suite |
| `DCL-CORE-INTAKE-001`: scaffold defaults to enabled | `test_default_on_new_project_init` | PASS in targeted suite |
| `DCL-CORE-INTAKE-001`: engine opt-out disables enrollment and prompt | `test_opt_out_flag_disables_intake` | PASS in targeted suite |
| `DCL-CORE-INTAKE-001`: CLI opt-out flag is accepted and threaded | `test_project_init_opt_out_flag_disables_intake` | PASS in targeted suite |
| `DCL-CORE-INTAKE-001`: actual `gt project init` default path enrolls and emits prompt | `test_project_init_default_enrolls_and_emits_prompt` | PASS in targeted suite |
| `SPEC-CORE-INTAKE-001` + `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`: initial prompt is emitted into `MEMORY.md` | `test_initial_prompt_emitted_into_memory_md` | PASS in targeted suite |
| Prompt append is idempotent | `test_append_initial_prompt_is_idempotent` | PASS in targeted suite |
| No `SPEC-CORE-INTAKE-003` reference in implementation files | `rg -n "SPEC-CORE-INTAKE-003" <authorized files>` | No matches |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-core-spec-intake-default` - authorization packet issued.
- `python -m ruff format groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_core_spec_intake.py` - formatted authorized files.
- `cd groundtruth-kb; python -m pytest tests/test_core_spec_intake.py -q --tb=short` - 11 passed.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_core_spec_intake.py` - all checks passed.
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_core_spec_intake.py` - 4 files already formatted.
- `cd groundtruth-kb; python -m ruff check .` - failed on out-of-scope existing lint findings listed below.
- `cd groundtruth-kb; python -m ruff format --check .` - failed on out-of-scope existing formatting drift listed below.
- `cd groundtruth-kb; python -m pytest tests/test_scaffold_project.py -q --tb=short` - 6 passed.
- `cd groundtruth-kb; python -m pytest tests/test_cli.py::TestBootstrapDesktop::test_project_init_dual_agent_uses_file_bridge_defaults -q --tb=short` - 1 passed.
- `cd groundtruth-kb; python -m pytest tests/test_scaffold_isolation.py -q --tb=short` - 19 passed, 2 failed in golden-fixture checks; see residual notes.

## Observed Results

Core test lane:

```text
11 passed in 2.49s
```

Authorized-file lint/format:

```text
All checks passed!
4 files already formatted
```

Nearby scaffold/CLI regressions:

```text
6 passed in 1.35s
1 passed in 0.80s
```

Full-package Ruff check failed on files not changed by this slice:

```text
src/groundtruth_kb/intake.py:280:121 E501 line too long
src/groundtruth_kb/mcp_surface/authority.py:30:7 UP042 use StrEnum
src/groundtruth_kb/mcp_surface/server.py:12:1 I001 import block unsorted
tests/test_doctor_bridge_dispatch_liveness.py:21:1 I001 import block unsorted
tests/test_doctor_cross_harness_trigger.py:4:121 E501 line too long
tests/test_harness_lifecycle.py:53:12 SIM300 Yoda condition
```

Full-package Ruff format check reported 38 out-of-scope files would be reformatted. `git diff --name-only` for the full-package Ruff-check failure files returned no paths, confirming those specific lint failures are not files changed by this slice.

## Acceptance Criteria Status

- IP-1 complete: `core_spec_intake.py` defines baseline slots and the approved primitives.
- IP-2a complete: `gt project init --opt-out-core-spec-intake` is declared in `cli.py` and threaded into `ScaffoldOptions`.
- IP-2b complete: scaffold default enrollment and initial prompt emission are implemented; opt-out suppresses both.
- IP-3 complete: the approved test file contains the spec-derived tests and one additional CLI default-on regression.
- No implementation reference to `SPEC-CORE-INTAKE-003` exists in the authorized files.
- Cross-session repeated prompting and pre-existing-project enablement remain out of scope and unimplemented.
- Authorized files pass Ruff check and Ruff format check.
- Full-package Ruff commands were executed but are not clean because of out-of-scope baseline findings; I did not edit those unrelated files under this bridge authorization.

## Residual Notes / Non-Blocking Verification Findings

- `tests/test_scaffold_isolation.py` currently fails two golden-fixture tests. The dual-agent failure is dominated by out-of-scope extra scaffold files from the separately filed Tier A managed-skill adoption work (`code-quality-baseline-proposal-check.py` and managed `bridge` skill templates). The local-only failure includes a `MEMORY.md` byte mismatch from this slice's new default prompt plus pre-existing hook/rule fixture drift. This bridge GO did not authorize golden fixture regeneration, so I did not update fixture directories here.
- The full-package Ruff failures are not in the four authorized target files. Repairing them would require a separate bridge item or a broader cleanup authorization.

## Risk And Rollback

Risk: adding a default `MEMORY.md` prompt changes byte-level scaffold fixtures and any consumer expecting the old template-only memory file. Mitigation: the change is the approved behavior for this slice, and prompt emission is suppressed by the new opt-out flag.

Risk: slot completion currently uses specification rows keyed by deterministic project/slot IDs. A future answer-capture driver must reuse these keys rather than inventing a second storage path.

Rollback path: remove `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`; remove the `opt_out_core_spec_intake` field and default enrollment block from `scaffold.py`; remove the Click option, signature parameter, and constructor keyword from `cli.py`; remove `groundtruth-kb/tests/test_core_spec_intake.py`. Bridge audit files remain append-only.

## Recommended Commit Type

`feat:` - adds the first default core-spec intake capability to project scaffolding, with CLI opt-out and regression coverage.
