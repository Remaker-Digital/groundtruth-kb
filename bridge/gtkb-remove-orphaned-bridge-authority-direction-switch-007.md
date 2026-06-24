REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T16-59-18Z-prime-builder-A-06e480
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; workspace-write

bridge_kind: implementation_report
Document: gtkb-remove-orphaned-bridge-authority-direction-switch
Version: 007 (REVISED; post-implementation report)
Responds to: bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-006.md
Prior implementation report: bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-005.md
Responds to GO: bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-004.md
Approved proposal: bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-003.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4629
target_paths: ["harness-state/bridge-authority-direction.json", "groundtruth-kb/tests/test_bridge_authority_direction.py"]
Recommended commit type: fix:

# Revised Implementation Report - WI-4629 Orphaned Bridge Authority Direction Switch

## Revision Claim

This REVISED post-implementation report responds to the `-006` NO-GO by supplying current evidence for the deletion-only implementation and a defensible alternate verification basis for Loyal Opposition disposition.

The implementation state remains unchanged from `-005`:

- `harness-state/bridge-authority-direction.json` is absent and appears as a tracked deletion.
- `groundtruth-kb/tests/test_bridge_authority_direction.py` is absent and appears as a tracked deletion.
- No source file, configuration file, MemBase row, application/adopter path, or non-approved target path is changed by this revision.

The exact full-regression command required by the approved `-003` proposal still does not pass in this headless workspace. It fails during collection before executing tests because this local `groundtruth-kb/.venv` lacks the web optional dependencies imported by three pre-existing web test modules. Because this auto-dispatched Prime Builder session cannot ask the owner for a waiver and cannot widen WI-4629 to repair test-environment dependencies, this report does not claim full-regression success. Instead, it asks Loyal Opposition to approve or reject the alternate verification floor below under the `-006` Required Revision option 3.

## First-Line Role Eligibility Check

Resolved session role: Prime Builder. Latest bridge status reviewed before drafting: `NO-GO` at `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-006.md`. Status authored here: `REVISED`. Prime Builder is authorized to write `REVISED` bridge artifacts in response to latest `NO-GO` entries.

## Implementation Authorization Evidence

- Durable harness identity resolved from `harness-state/harness-identities.json`: Codex = `A`.
- Durable role resolved with `groundtruth-kb/.venv/Scripts/gt.exe harness roles`: harness `A` has role `prime-builder`.
- Live bridge thread state confirmed with `show_thread_bridge.py`: latest version before this revision was `NO-GO` at `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-006.md`; drift `[]`.
- Work-intent claim command:
  - `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-remove-orphaned-bridge-authority-direction-switch`
  - Result: acquired for session `2026-06-23T16-59-18Z-prime-builder-A-06e480`, rowid `23653`, TTL expires `2026-06-23T17:17:54Z`.
- The implementation-start packet from `-005` remains the packet that authorized the two target deletions after the `-004` GO: packet `sha256:96014d547f110ade09095c4ea0ec4cb8cdf510f5d11f1d2d880a6a6ee8d9881b`, target path globs `["harness-state/bridge-authority-direction.json", "groundtruth-kb/tests/test_bridge_authority_direction.py"]`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - stale bridge authority switch state is removed so the live authority surface no longer advertises a consumer-less toggle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the cleanup remains recorded through the bridge audit chain rather than as an untracked cleanup.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised report carries forward the approved proposal and linked specification surface.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps the deletion to executed absence, reference, diff, quality-gate, collection, and full-regression-attempt evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths remain machine-readable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both implementation target paths and the ignored in-root test-environment scratch path are inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - the work remains tied to standing-backlog item `WI-4629`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the artifact retirement remains reviewable and reversible through the bridge and final commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the retired switch file and its dangling test are removed from the live working tree.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` / `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization for small defect/reliability fixes under active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ directing proposal authoring for open PROJECT-GTKB-RELIABILITY-FIXES work items; `WI-4629` is in that batch.

No new owner decision is claimed. This report explicitly does not claim an owner waiver for the red full-regression command.

## Prior Deliberations

- `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-001.md` - original proposal identifying the orphaned switch file and dangling test.
- `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-002.md` - Loyal Opposition NO-GO finding that post-delete ruff commands named files that would be deleted.
- `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-003.md` - revised proposal with executable deletion-focused verification plan.
- `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-004.md` - Loyal Opposition GO verdict approving the deletion-only implementation scope.
- `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-005.md` - prior post-implementation report.
- `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-006.md` - Loyal Opposition NO-GO requiring passing full regression, separate baseline repair, or a defensible approved alternate verification basis.
- `DELIB-20264698` - retired bridge artifact runtime source cleanout context.
- `DELIB-20263786` - bridge index retirement cleanout packet correction review.
- `DELIB-20263285` - TAFE live implementation-flow pilot proposal review.
- `DELIB-20263275` - TAFE Slice C bridge-thread ingestion verdict.
- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch.

## Blocking Finding Addressed

### P1 - Required full-regression evidence is not satisfied

Response: not fully resolved by a green full-regression command. The exact command still fails during collection in this local environment because optional web dependencies are missing:

- `groundtruth-kb/tests/test_ar_web_shim.py`: `ModuleNotFoundError: No module named 'starlette'`.
- `groundtruth-kb/tests/test_web.py`: `ModuleNotFoundError: No module named 'fastapi'`.
- `groundtruth-kb/tests/test_web_pipeline.py`: `ModuleNotFoundError: No module named 'fastapi'`.

The environment cannot be repaired in this dispatch without widening the approved WI-4629 scope. The local `groundtruth-kb/.venv` has no `pip` module, and an in-root `uv` environment attempt using the locked project dependencies failed because network egress is blocked:

- CI-style dependency attempt: `uv run --project groundtruth-kb --extra dev --extra search ...` failed while downloading `pyyaml==6.0.3` with socket permission error `10013`.
- Web/dev dependency attempt: `uv run --project groundtruth-kb --extra dev --extra web ...` failed while downloading `typing-extensions==4.15.0` with socket permission error `10013`.

This revised report therefore supplies the alternate verification basis requested by `-006` option 3 and asks Loyal Opposition to decide whether it is sufficient for this deletion-only change.

## Alternate Verification Basis

The proposed alternate floor is defensible for WI-4629 because the implementation is deletion-only and the red full-regression command fails before executing any tests, on pre-existing optional dependency imports unrelated to either approved target path.

The alternate floor is:

1. Both approved target paths are absent from the working tree.
2. The approved target diff is exactly two tracked deletions and no other WI-4629 target change.
3. Tracked and live Python reference scans find no remaining references to the retired `bridge_authority_cutover` API.
4. The conditional ruff gate over surviving modified Python targets in the approved target set reports `no surviving Python targets to lint`.
5. A collect-only run excluding only the three dependency-blocked web files collects `2564 tests` and does not collect the deleted `test_bridge_authority_direction.py`.
6. Bridge applicability and ADR/DCL clause preflights pass with no missing required specs or blocking gaps.

This floor does not replace the project-wide release obligation to restore a clean full `groundtruth-kb/tests` run. It is a proposed verification basis for this two-file retirement only.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `Test-Path -LiteralPath harness-state\bridge-authority-direction.json` returned `False`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `Test-Path -LiteralPath groundtruth-kb\tests\test_bridge_authority_direction.py` returned `False`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `git grep -n -E "bridge_authority_cutover|read_authority_direction|direction_state_path" -- ":(glob)groundtruth-kb/**/*.py" ":(glob)scripts/**/*.py" ":(glob).claude/**/*.py" ":(glob)config/**/*.py"` returned no matches (exit 1, empty stdout). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `rg -n "bridge_authority_cutover|read_authority_direction|direction_state_path" groundtruth-kb scripts .claude config --glob "*.py" --glob "!.claude/worktrees/**" --glob "!groundtruth-kb/pytest-kpi-retro-codex/**"` returned no matches (exit 1, empty stdout). |
| Python quality gate for deletion-only target set | The conditional surviving-target ruff gate returned `no surviving Python targets to lint`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact full regression command attempted and failed during collection on missing optional web dependencies before executing tests; failure recorded below rather than claimed as pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Alternate collect-only command excluding only the dependency-blocked web files collected `2564 tests in 12.05s` and did not collect the deleted `test_bridge_authority_direction.py`. |
| Target scope discipline | `git diff --name-status -- harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py` shows only two `D` entries for the approved targets. |

## Commands Run

```powershell
groundtruth-kb\.venv\Scripts\gt.exe harness roles
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-remove-orphaned-bridge-authority-direction-switch --format json --preview-lines 400
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-remove-orphaned-bridge-authority-direction-switch
Test-Path -LiteralPath harness-state\bridge-authority-direction.json
Test-Path -LiteralPath groundtruth-kb\tests\test_bridge_authority_direction.py
git diff --name-status -- harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py
git diff --stat -- harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py
git diff --numstat -- harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py
git grep -n -E "bridge_authority_cutover|read_authority_direction|direction_state_path" -- ":(glob)groundtruth-kb/**/*.py" ":(glob)scripts/**/*.py" ":(glob).claude/**/*.py" ":(glob)config/**/*.py"
rg -n "bridge_authority_cutover|read_authority_direction|direction_state_path" groundtruth-kb scripts .claude config --glob "*.py" --glob "!.claude/worktrees/**" --glob "!groundtruth-kb/pytest-kpi-retro-codex/**"
$survivingPy = @(git diff --diff-filter=ACMR --name-only -- harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py | Where-Object { $_ -like "*.py" }); if ($survivingPy.Count -gt 0) { groundtruth-kb\.venv\Scripts\python.exe -m ruff check @survivingPy; groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check @survivingPy } else { "no surviving Python targets to lint" }
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-remove-orphaned-bridge-authority-direction-switch
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-remove-orphaned-bridge-authority-direction-switch
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests --collect-only -q --tb=short --ignore=groundtruth-kb\tests\test_ar_web_shim.py --ignore=groundtruth-kb\tests\test_web.py --ignore=groundtruth-kb\tests\test_web_pipeline.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_ar_web_shim.py groundtruth-kb\tests\test_web.py groundtruth-kb\tests\test_web_pipeline.py --collect-only -q --tb=short
$env:UV_CACHE_DIR='E:\GT-KB\.tmp\uv-cache-gtkb'; $env:UV_PROJECT_ENVIRONMENT='E:\GT-KB\.tmp\uv-env-gtkb-fulltests'; uv run --project groundtruth-kb --extra dev --extra search python -c "import fastapi, starlette; print(fastapi.__version__); print(starlette.__version__)"
$env:UV_CACHE_DIR='E:\GT-KB\.tmp\uv-cache-gtkb'; $env:UV_PROJECT_ENVIRONMENT='E:\GT-KB\.tmp\uv-env-gtkb-fulltests-web'; uv run --project groundtruth-kb --extra dev --extra web python -c "import fastapi, starlette; print(fastapi.__version__); print(starlette.__version__)"
```

## Observed Results

- Absence checks returned `False` for both approved target paths.
- Approved target diff:

```text
D       groundtruth-kb/tests/test_bridge_authority_direction.py
D       harness-state/bridge-authority-direction.json
```

- Approved target stat:

```text
.../tests/test_bridge_authority_direction.py       | 174 ---------------------
harness-state/bridge-authority-direction.json      |   6 -
2 files changed, 180 deletions(-)
```

- Approved target numstat:

```text
0       174     groundtruth-kb/tests/test_bridge_authority_direction.py
0       6       harness-state/bridge-authority-direction.json
```

- Tracked and live Python reference scans returned no matches.
- Conditional ruff gate output: `no surviving Python targets to lint`.
- Applicability preflight passed on the operative thread: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet `sha256:38948a98062b39ea8ee3b7fb5e5bbc298fb65ddcbb4e719683eab4ee4d2d483b`.
- Clause preflight passed on the operative thread: `must_apply: 2`, evidence gaps `0`, blocking gaps `0`, exit `0`.
- Exact full regression command failed during collection:

```text
ERROR groundtruth-kb\tests\test_ar_web_shim.py
ModuleNotFoundError: No module named 'starlette'
ERROR groundtruth-kb\tests\test_web.py
ModuleNotFoundError: No module named 'fastapi'
ERROR groundtruth-kb\tests\test_web_pipeline.py
ModuleNotFoundError: No module named 'fastapi'
Interrupted: 3 errors during collection
```

- Web-only collect probe confirmed the same dependency blocker and collected no tests.
- Alternate collect-only command excluding only the dependency-blocked web files succeeded:

```text
2564 tests collected in 12.05s
```

- In-root `uv` environment setup could not repair the dependency gap under this session's network restrictions:

```text
Failed to download `pyyaml==6.0.3` ... socket permission error 10013
Failed to download `typing-extensions==4.15.0` ... socket permission error 10013
```

## Files Changed

Scoped implementation diff remains:

- `groundtruth-kb/tests/test_bridge_authority_direction.py` (deleted)
- `harness-state/bridge-authority-direction.json` (deleted)

Bridge/audit addition in this revision:

- `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-007.md` (this report)

Ignored scratch state from attempted dependency setup:

- `.tmp/uv-cache-gtkb/`
- `.tmp/uv-env-gtkb-fulltests/`
- `.tmp/uv-env-gtkb-fulltests-web/`

These `.tmp/` paths are ignored by `.gitignore` and are not part of the implementation diff.

## Acceptance Criteria Status

1. `harness-state/bridge-authority-direction.json` is deleted from the working tree: PASS.
2. `groundtruth-kb/tests/test_bridge_authority_direction.py` is deleted from the working tree: PASS.
3. Repo-wide live Python references to `bridge_authority_cutover`, `read_authority_direction`, or `direction_state_path`: PASS.
4. Deletion-only target set produces no surviving modified Python target paths: PASS; conditional ruff gate reported `no surviving Python targets to lint`.
5. Full `groundtruth-kb/tests` regression: FAIL in this environment because collection stops on missing `fastapi`/`starlette`.
6. Alternate verification floor for deletion-only scope: SUBMITTED for Loyal Opposition approval or rejection.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this is a deletion-only defect fix removing a stale bridge authority state file and its dangling test for a deleted module.

## Risk And Rollback

Residual risk: approving this report without a green full `groundtruth-kb/tests` run accepts deletion-specific evidence while leaving the broader test-environment/release-readiness problem open. The risk is bounded because the full-regression failure occurs during collection of pre-existing web test imports and does not execute code related to the two deleted WI-4629 target paths.

Rollback remains path-local before commit:

```powershell
git restore --staged --worktree harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py
```

After commit, rollback is a normal `git revert` of the implementing commit. Bridge files remain append-only.

## Loyal Opposition Asks

1. Decide whether the alternate verification floor is sufficient for this deletion-only WI-4629 change under the `-006` Required Revision option 3.
2. Return `VERIFIED` if the scoped evidence is sufficient despite the unrelated dependency-blocked full regression.
3. Return `NO-GO` if a green full `groundtruth-kb/tests` run remains mandatory before verification; if so, identify whether the dependency environment repair should be handled as separate bridge work.
