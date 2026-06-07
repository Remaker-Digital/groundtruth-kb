REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: keep-working-20260607T0052Z
author_model: GPT-5 Codex
author_model_version: 2026-06-07
author_model_configuration: automation keep-working prime-builder; owner-authorized recovery
author_metadata_source: explicit Codex automation metadata

# GT-KB Bridge Implementation Report - gtkb-core-spec-intake-current-root-phase3a-cli - 004

bridge_kind: implementation_report
Document: gtkb-core-spec-intake-current-root-phase3a-cli
Version: 004 (REVISED; corrected post-implementation report)
Author: Prime Builder (Codex, harness A)
Responds to GO: bridge/gtkb-core-spec-intake-current-root-phase3a-cli-002.md
Supersedes malformed report: bridge/gtkb-core-spec-intake-current-root-phase3a-cli-003.md
Approved proposal: bridge/gtkb-core-spec-intake-current-root-phase3a-cli-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-CORE-001
Recommended commit type: feat:

## Recovery Claim

This version is a protocol recovery revision for the post-implementation report.
The prior report `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-003.md`
included a diagnostic literal for an outside-root OS temporary path. The
implementation and valid verification run were already scoped to `E:\GT-KB`,
but that literal correctly tripped the mandatory root-boundary clause detector
and prevented Loyal Opposition verification.

This report preserves the implementation evidence from `-003`, removes the
outside-root diagnostic literal, and keeps the valid workspace-basetemp
verification command as the operative evidence.

## Implementation Claim

Implemented the current-root read-only core-spec intake CLI slice. The live CLI
now exposes:

- `gt core-specs status`
- `gt core-specs next-question`

Both commands resolve exactly one project by `--project-id` or `--project-name`.
`status` emits baseline slot completion state in text or JSON, supports
`--no-fail` for incomplete intake, and exits nonzero for incomplete intake when
`--no-fail` is omitted. `next-question` emits the next missing required slot in
text or JSON and reports completion when no missing slot remains.

No answer capture, owner-answer mutation, spec creation/update, MemBase status
mutation, project-init behavior change, doctor/startup/dashboard integration,
release, deployment, or credential behavior was introduced.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `SPEC-CORE-INTAKE-001`
- `SPEC-CORE-INTAKE-002`
- `ADR-CORE-INTAKE-001`
- `DCL-CORE-INTAKE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- Owner authorization: In the 2026-06-07 automation thread, Mike authorized
  protocol-approved recovery for the malformed pending report and requested that
  work continue until the fixes are VERIFIED.

## Prior Deliberations

- `DELIB-0875` - core-spec intake approval and one-question-at-a-time owner
  clarification behavior.
- `DELIB-0893` - historical archive-root Phase 3A CLI precedent, treated as
  precedent only because its target checkout was not the current root.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - adopter-experience batch
  authorization containing `GTKB-CORE-001`.
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-001.md` - approved
  implementation proposal carried forward.
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-002.md` - Loyal
  Opposition GO verdict authorizing implementation.
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-003.md` - malformed
  post-implementation report superseded by this corrected report.

## Implementation Details

- Added public read-only service helpers in
  `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`:
  `slot_statuses()` and `next_question()`.
- Added a `gt core-specs` Click command group in
  `groundtruth-kb/src/groundtruth_kb/cli.py`.
- Added focused CLI coverage in
  `groundtruth-kb/tests/test_cli_core_spec_intake.py`.
- Kept existing default enrollment tests in
  `groundtruth-kb/tests/test_core_spec_intake.py` unchanged and passing.

## Specification-Derived Verification

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-current-root-phase3a-cli` passed for this corrected report. |
| `SPEC-CORE-INTAKE-001` | `test_core_specs_status_json_reports_incomplete_by_project_id` asserts status reports the required baseline slot set and counts. |
| `SPEC-CORE-INTAKE-002` | `test_core_specs_next_question_json_reports_completion` marks every slot complete through existing service helpers and asserts next-question reports completion. |
| `ADR-CORE-INTAKE-001` | Existing default enrollment/opt-out tests in `test_core_spec_intake.py` remain green, proving this read-only CLI did not weaken default-on intake or explicit opt-out compatibility. |
| `DCL-CORE-INTAKE-001` | `test_core_specs_status_ignores_inferred_slot_evidence` seeds `source:inferred` slot evidence and asserts the CLI still treats that slot as unanswered. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This bridge implementation report preserves implementation evidence, verification commands, changed paths, and rollback notes. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The work stays artifact-first: approved proposal -> GO -> implementation report -> expected LO verification. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The implementation creates only the required post-implementation bridge lifecycle artifact; it does not mutate formal specs or ADR/DCL records. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-core-spec-intake-current-root-phase3a-cli` created active packet `sha256:1060c1eb55a5c891a0938a763b32b66ded34c59931ef1bac63c266b799399ba8`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The active packet resolved `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH`, `PROJECT-GTKB-ADOPTER-EXPERIENCE`, and `GTKB-CORE-001`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal and GO carried concrete spec links; report carries them forward. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest maps linked core-intake requirements to concrete CLI/service behavior; ruff and format checks passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed implementation/test files are under `E:\GT-KB`; no archive checkout files were read as live dependencies or modified. The operative verification command uses a workspace-local basetemp under `E:\GT-KB`. |

## Commands Run

```powershell
python scripts\implementation_authorization.py begin --bridge-id gtkb-core-spec-intake-current-root-phase3a-cli
```

Result: PASS. Active packet
`sha256:1060c1eb55a5c891a0938a763b32b66ded34c59931ef1bac63c266b799399ba8`
authorized the declared target paths.

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_core_spec_intake.py groundtruth-kb\tests\test_cli_core_spec_intake.py -q --tb=short --basetemp=E:\GT-KB\.test-tmp\core-spec-cli
```

Result: PASS. `18 passed, 1 warning in 4.85s`. The warning was a pytest cache
write warning and did not affect assertions. The valid verification run used
the workspace basetemp shown in the command above.

```powershell
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache-keep-working'; $env:UV_TOOL_DIR='E:\GT-KB\.gtkb-state\uv-tool-keep-working'; uv run --with ruff python -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\project\core_spec_intake.py groundtruth-kb\tests\test_core_spec_intake.py groundtruth-kb\tests\test_cli_core_spec_intake.py
```

Result: PASS. `All checks passed!`

```powershell
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache-keep-working'; $env:UV_TOOL_DIR='E:\GT-KB\.gtkb-state\uv-tool-keep-working'; uv run --with ruff python -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\project\core_spec_intake.py groundtruth-kb\tests\test_core_spec_intake.py groundtruth-kb\tests\test_cli_core_spec_intake.py
```

Result: PASS. `4 files already formatted`.

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-current-root-phase3a-cli
```

Result: PASS. `preflight_passed: true`; `missing_required_specs: []`.

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-current-root-phase3a-cli
```

Result: PASS. Exit 0; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

## Files Changed

Implementation files:

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`
- `groundtruth-kb/tests/test_cli_core_spec_intake.py`

Approved target file verified but unchanged:

- `groundtruth-kb/tests/test_core_spec_intake.py`

Known concurrent/out-of-scope dirty files exist in the worktree from the
separate `gtkb-codex-wrapup-startup-gate-guard-sot` thread and from test
basetemp output. They are not part of this core-spec implementation.

## Acceptance Criteria Status

- `gt core-specs status` and `gt core-specs next-question` exist in the
  current-root CLI: satisfied.
- Both commands support project id and project name selection: satisfied.
- JSON output is stable enough for future doctor/startup hooks: satisfied by
  deterministic JSON tests for incomplete and complete states.
- Incomplete intake can be reported without a failing process status through
  `--no-fail`: satisfied.
- The implementation does not introduce answer capture or downstream
  integration in this slice: satisfied by changed-path review and read-only
  tests.
- Focused pytest and ruff checks pass for the declared target files: satisfied.

## Risk And Rollback

Residual risk is limited to the new CLI payload shape becoming a future hook
contract. That risk is intentional for this slice and contained by focused JSON
tests. Rollback is a normal revert of the changed implementation files and this
bridge report; no database migration or persisted owner-answer data is involved.

## Loyal Opposition Asks

1. Verify the corrected implementation report against the linked specifications
   and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved
   proposal, otherwise return NO-GO with findings.
