NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019edc60-386a-7d62-8cc1-e66b037edd59
author_model: GPT-5
author_model_version: Codex GPT-5 runtime
author_model_configuration: Codex desktop automation; Prime Builder; approval_policy=never

# GT-KB Bridge Implementation Report - gtkb-headless-worker-venv-interpreter-pin - 003

bridge_kind: implementation_report
Document: gtkb-headless-worker-venv-interpreter-pin
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-headless-worker-venv-interpreter-pin-002.md
Approved proposal: bridge/gtkb-headless-worker-venv-interpreter-pin-001.md
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4600
Recommended commit type: fix:

## Implementation Claim

Completed the approved WI-4600 repair. Headless worker prompt prose now pins package-importing commands to the in-root repository venv, and both dispatch substrates set a `PYTHONPATH` backstop that prepends `groundtruth-kb/src` for worker subprocesses.

Implemented behavior:

- Added `_repo_venv_command(...)` so prompt text uses repo-local venv literals such as `groundtruth-kb/.venv/Scripts/gt.exe harness roles` and `groundtruth-kb/.venv/Scripts/python.exe scripts/...` on Windows.
- Updated the worker role-resolution instruction to forbid `python -m groundtruth_kb.harness_projection` as a role reader and to avoid ambient bare `python` / bare `gt` for package-importing commands.
- Updated Loyal Opposition preflight instructions to use the repo venv Python for both bridge preflight scripts.
- Added `_worker_pythonpath(...)` and applied it to both `scripts/cross_harness_bridge_trigger.py` and `scripts/single_harness_bridge_dispatcher.py`.
- Added `_read_index_live(...)` as a compatibility alias for the single-harness dispatcher; the required focused dispatcher suite exposed that the dispatcher still called the older trigger read helper name.

Local implementation commit: `2e9f388ae fix: pin headless worker repo venv imports`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`: the cross-harness dispatch trigger is bridge infrastructure; dispatched workers must read and process current bridge state correctly.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: the proposal cites governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: this report maps verification evidence to the governing surfaces.
- `GOV-ENV-LOCAL-AUTHORITY-001`: env/path handling must not invent a new authority source.
- `.claude/rules/project-root-boundary.md`: all implementation paths and venv/package-source paths remain in-root under `E:/GT-KB`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: no Agent Red or out-of-root application path is touched.
- `GOV-RELIABILITY-FAST-LANE-001`: this is a bounded bridge-dispatch reliability defect fix.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory): work remains traceable through WI, bridge proposal, GO, implementation commit, and report.

## Owner Decisions / Input

No new owner decision is required by this implementation report.

Carried-forward authorization:

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`.
- The 2026-06-18 Hygiene PB automation directive authorized autonomous Prime Builder execution on incomplete HYGIENE project work.

## Prior Deliberations

- `bridge/gtkb-headless-worker-venv-interpreter-pin-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-headless-worker-venv-interpreter-pin-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `WI-4600` - captured headless-worker package-import failure under ambient Python.
- WI-3360 precedent - prior `_PACKAGE_SRC` repair for the trigger process, extended here to spawned workers.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - relevant boundary precedent; this implementation stays in-root and does not require the out-of-root executable exception.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_fab01_dispatch_substrate_revival.py -q --tb=short -o addopts=` passed `115 passed`, including tests for venv-pinned prompt prose, `_worker_pythonpath`, cross-harness worker env, and single-harness worker env. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's linked specifications and maps implementation tests to those surfaces. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The report includes this specification-derived verification table and exact observed command results. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Tests assert inherited `PYTHONPATH` is preserved while `groundtruth-kb/src` is prepended; no new env file or configuration authority was introduced. |
| `.claude/rules/project-root-boundary.md` | Prompt commands use in-root venv paths and worker env uses the in-root `_PACKAGE_SRC` path. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation changes are under `E:/GT-KB` target paths; no adopter or out-of-root path is modified. |
| `GOV-RELIABILITY-FAST-LANE-001` | Focused dispatch substrate tests passed after the repair, including the single-harness compatibility alias required by the existing dispatcher suite. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Work remains traceable through WI-4600, the approved proposal, GO verdict, local implementation commit, and this implementation report. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_dispatch_prompt_pins_role_and_preflight_commands_to_repo_venv platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_worker_pythonpath_prepends_package_src_without_clobbering platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_spawn_harness_worker_env_includes_package_src platform_tests\scripts\test_fab01_dispatch_substrate_revival.py::test_single_harness_worker_env_includes_package_src -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_dispatch_prompt_pins_role_and_preflight_commands_to_repo_venv platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_worker_pythonpath_prepends_package_src_without_clobbering platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_spawn_harness_worker_env_includes_package_src platform_tests\scripts\test_fab01_dispatch_substrate_revival.py::test_single_harness_worker_env_includes_package_src -q --tb=short -o addopts=`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_fab01_dispatch_substrate_revival.py -q --tb=short -o addopts=`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_fab01_dispatch_substrate_revival.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_fab01_dispatch_substrate_revival.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_fab01_dispatch_substrate_revival.py`
- `git diff --check -- scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_fab01_dispatch_substrate_revival.py`

## Observed Results

- First focused new-test pytest command failed before collection because the current venv does not recognize repository default addopt `--timeout=30`.
- Focused new-test pytest with addopts disabled passed: `4 passed, 1 warning in 5.70s`.
- First full focused suite with addopts disabled passed most tests but exposed the existing dispatcher compatibility gap: `single_harness_bridge_dispatcher.py` called `trigger._read_index_live`, while the trigger only exposed `_read_bridge_state_live`.
- Added `_read_index_live(...)` compatibility alias to the trigger and reran.
- Final full focused suite passed: `115 passed, 1 warning in 9.05s`.
- Final Ruff lint passed: `All checks passed!`
- Final Ruff format check passed: `4 files already formatted`.
- `git diff --check` passed for the scoped source/test diff.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py`

Bridge chain files recorded in the local implementation commit:

- `bridge/gtkb-headless-worker-venv-interpreter-pin-002.md` (LO GO verdict, already live bridge state; committed with the implementation so the bridge chain is complete locally).

## Acceptance Criteria Status

- PASS - Prompt prose uses repo venv `gt` for role reading and does not direct workers to `python -m groundtruth_kb.harness_projection`.
- PASS - Prompt preflight commands use repo venv Python and preserve required bridge preflight script arguments.
- PASS - `_worker_pythonpath(...)` prepends `groundtruth-kb/src` without clobbering inherited `PYTHONPATH`.
- PASS - Cross-harness worker child env includes the package source.
- PASS - Single-harness worker child env includes the package source.
- PASS - Required focused dispatch suites, Ruff lint, Ruff format, and diff whitespace checks passed.

## Risk And Rollback

Residual risk is moderate-low and localized to dispatch prompt text plus worker child environment construction. The implementation does not change bridge selection, claim semantics, dispatch provider ordering, or actionability classification.

Rollback is a normal revert of commit `2e9f388ae` plus this append-only bridge report if Loyal Opposition returns NO-GO.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Confirm the prompt and worker env behavior satisfy both cross-harness and single-harness dispatch substrates.
3. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with concrete findings.
