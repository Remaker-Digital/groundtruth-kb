NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: keep-working-20260606T1625Z
author_model: GPT-5 Codex
author_model_version: 2026-06-06
author_model_configuration: automation keep-working prime-builder
author_metadata_source: explicit Codex automation metadata

# Current-root core spec intake Phase 3A CLI proposal

bridge_kind: implementation_proposal
Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-CORE-001
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py", "groundtruth-kb/tests/test_core_spec_intake.py", "groundtruth-kb/tests/test_cli_core_spec_intake.py"]

## Claim

Current-root GT-KB has the default core-spec enrollment slice verified, but it lacks the current-root Phase 3A read-only CLI surface described by GTKB-CORE-001. This proposal scopes only the deterministic read-only commands required before answer capture and downstream doctor/startup integration.

## Evidence

- Live work item: `GTKB-CORE-001` under `PROJECT-GTKB-ADOPTER-EXPERIENCE` requires `gt core-specs status`, `gt core-specs next-question`, and answer flow as Phase 3 before doctor/startup integration.
- Current-root verified slice: `bridge/gtkb-core-spec-intake-default-008.md` verifies default enrollment and opt-out behavior for the current checkout.
- Current-root implementation files already present: `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`, `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, and `groundtruth-kb/tests/test_core_spec_intake.py`.
- Current-root absence: no `gt core-specs` command group and no `groundtruth-kb/tests/test_cli_core_spec_intake.py` exist in this checkout.
- Historical boundary: old on-disk `gtkb-core-spec-intake-phase3a-cli-*` and `phase3b-answer-*` files target the archive checkout `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` and are not live current-root authority under the project-root boundary.

## Requirement Sufficiency

Existing requirements sufficient.

GTKB-CORE-001 already specifies the Phase 3 CLI surface, one-question-at-a-time intake semantics, multi-session completion behavior, explicit opt-out compatibility, and regression visibility. This slice is a read-only subset: status and next-question only. Answer capture remains a separate follow-on proposal so the selector behavior can be reviewed and tested before owner-answer mutation is introduced.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - file bridge is the governed handoff and review mechanism for implementation proposals.
- `SPEC-CORE-INTAKE-001` - core application specification intake must capture required baseline slots.
- `SPEC-CORE-INTAKE-002` - prompting continues until slots are owner-stated or explicitly not applicable.
- `ADR-CORE-INTAKE-001` - default-on intake loop with explicit opt-out compatibility.
- `DCL-CORE-INTAKE-001` - inferred or unclear evidence must not stop prompting.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable artifact-oriented lifecycle and evidence preservation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped authorization governs implementation work.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - proposal must cite the active project authorization and scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must link implementation scope to governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to cited specifications.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB artifacts must remain within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-0875` - Phase 0 core-spec intake formalization and approval evidence.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - adopter-experience batch authorization including GTKB-CORE-001.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - later adopter-experience extension; does not remove GTKB-CORE-001 scope.

## Scope

Implement a current-root read-only CLI group:

- `gt core-specs status --project-id PROJECT_ID` and `gt core-specs status --project-name PROJECT_NAME` report baseline slot completion state.
- `gt core-specs status --json` emits deterministic machine-readable status for tests and future hooks.
- `gt core-specs status --no-fail` keeps automation from treating incomplete intake as a command failure.
- `gt core-specs next-question --project-id PROJECT_ID` and `gt core-specs next-question --project-name PROJECT_NAME` report only the next missing or unclear slot.
- `gt core-specs next-question --json` emits deterministic machine-readable next-question data.
- Command behavior is read-only. No answer capture, spec creation, MemBase status mutation, project init behavior change, doctor integration, startup integration, or dashboard integration is included in this slice.

## Implementation Plan

1. Add a small CLI group in `groundtruth-kb/src/groundtruth_kb/cli.py` that resolves a project by id or name and calls the existing core-spec intake service.
2. Add read-only service helpers in `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` only if current helpers do not already provide the needed selector payload.
3. Add CLI tests in `groundtruth-kb/tests/test_cli_core_spec_intake.py` for text and JSON output, project id/name selection, all-complete behavior, next-question selection, and `--no-fail` incomplete status behavior.
4. Preserve existing default enrollment tests in `groundtruth-kb/tests/test_core_spec_intake.py` without weakening scaffold compatibility.
5. File a post-implementation report after GO and a fresh implementation-start packet.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | CLI output includes only project and slot metadata. | Helper credential scan plus targeted CLI tests. |  |
| CQ-PATHS-001 | Yes | Mutate only the declared current-root target paths. | Implementation-start packet and `git diff --name-only` review. |  |
| CQ-COMPLEXITY-001 | Yes | Keep selector logic in the existing core-spec intake service and CLI formatting thin. | Focused tests plus code review of target files. |  |
| CQ-CONSTANTS-001 | Yes | Reuse existing baseline slot definitions instead of duplicating slot text in CLI tests. | Targeted tests assert identifiers and next-question behavior. |  |
| CQ-SECURITY-001 | Yes | Keep commands read-only and do not create authorization bypasses. | Tests confirm no answer capture or project mutation path in this slice. |  |
| CQ-DOCS-001 | Yes | Add concise click help strings for the new commands. | CLI help invocation in focused tests. |  |
| CQ-TESTS-001 | Yes | Add deterministic CLI tests and keep existing intake tests passing. | `pytest groundtruth-kb/tests/test_core_spec_intake.py groundtruth-kb/tests/test_cli_core_spec_intake.py -q --tb=short`. |  |
| CQ-LOGGING-001 | N/A | Read-only CLI prints user-facing command output only. | Review target files for no new logging behavior. | No logging surface is required for this read-only selector slice. |
| CQ-VERIFICATION-001 | Yes | Map each cited requirement to a focused test or file review check. | Spec-derived verification bullets below. |  |

## Specification-Derived Verification

- `GOV-FILE-BRIDGE-AUTHORITY-001`: helper-mediated filing and live `bridge/INDEX.md` entry prove the proposal used the governed bridge path.
- `SPEC-CORE-INTAKE-001`: tests create a project with missing slots and assert status reports the required baseline slots.
- `SPEC-CORE-INTAKE-002`: tests mark all slots complete through existing service helpers and assert next-question reports completion.
- `ADR-CORE-INTAKE-001`: existing default enrollment tests remain green, proving this CLI slice does not weaken default-on enrollment.
- `DCL-CORE-INTAKE-001`: tests cover inferred or unclear slot state so next-question still selects that slot.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: post-implementation report must cite commands, test output, and target-file diff scope.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: implementation begins only after LO GO and a fresh implementation-start packet for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this proposal carries explicit spec links before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: Loyal Opposition can verify this section against the post-implementation test transcript.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: `git diff --name-only` must show only paths under `E:\GT-KB`.

## Acceptance Criteria

- `gt core-specs status` and `gt core-specs next-question` exist in the current-root CLI.
- Both commands support project id and project name selection.
- JSON output is stable enough for future doctor/startup hooks.
- Incomplete intake can be reported without a failing process status through `--no-fail`.
- The implementation does not introduce answer capture or downstream integration in this slice.
- Focused pytest and ruff checks pass for the declared target files, or residual failures are explicitly isolated outside the approved scope.

## Rollback

Revert the declared CLI and test target files from the implementation commit if GO-authorized implementation fails. No data migration is included in this read-only slice.

## Owner Decision Needed

None. This proposal uses the active adopter-experience authorization for GTKB-CORE-001 and narrows the work to read-only Phase 3A selector behavior.
