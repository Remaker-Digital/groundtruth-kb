NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-07-03T09-22-24Z-prime-builder-A-1f10ce
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless dispatch; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write

# GT-KB Bridge Implementation Report - WI-4985 Codex Headless Write Boundary

bridge_kind: implementation_report
Document: gtkb-wi4985-codex-headless-write-boundary
Version: 005
Date: 2026-07-03 UTC
Responds to GO: bridge/gtkb-wi4985-codex-headless-write-boundary-004.md
Approved proposal: bridge/gtkb-wi4985-codex-headless-write-boundary-003.md

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4985

Recommended commit type: feat:

## Implementation Claim

Implemented the WI-4985 Codex A headless write-boundary repair. Codex A's MemBase-backed headless invocation surface now preserves the required `gpt-5.5`, `approval_policy="never"`, and `model_reasoning_effort="xhigh"` pins while adding the narrow write-capable selector `--sandbox workspace-write` before `{{PROMPT}} --cd {{PROJECT_ROOT}}`.

The harness projection was regenerated from MemBase rather than hand-edited. The latest MemBase harness row for `A` is version 48, `changed_by=gt-harness-cli`, with change reason `WI-4985 Codex headless write boundary: add workspace-write sandbox while preserving gpt-5.5/never/xhigh pins`. The generated `harness-state/harness-registry.json` now reflects that row.

`scripts/verify_codex_dispatch.py` now fails closed unless the Codex A headless argv contains the model pin, approval-policy pin, reasoning-effort pin, project-root selector, and `workspace-write` sandbox. It explicitly rejects `danger-full-access`.

## Implementation-Start And Work-Intent Evidence

- Work-intent claim acquired for `gtkb-wi4985-codex-headless-write-boundary` by dispatch session `2026-07-03T09-22-24Z-prime-builder-A-1f10ce`; holder rowid `29497`; `claim_kind=go_implementation`.
- Implementation authorization packet reissued from the live latest `GO` with packet hash `sha256:17cd5f18ba1b7966357d22236503100faabae7e80ad5d183ef32c1cff38b2073`.
- `scripts/implementation_authorization.py validate` authorized all changed WI-4985 target paths.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`

## Owner Decisions / Input

- `DELIB-202665265` - owner authorization for the headless bridge-stability goal, including Codex as active Prime Builder headless dispatch target.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY` - active project authorization covering WI-4985.
- No new owner decision was required during implementation.

## Prior Deliberations

- `DELIB-202665265` - owner authorization for the bridge-stability repair goal.
- `WI-4977` - dispatch-stability predecessor context.
- `bridge/gtkb-headless-dispatch-model-pinning-006.md` - VERIFIED predecessor; this implementation preserves its `gpt-5.5`, `approval_policy="never"`, and `model_reasoning_effort="xhigh"` pins.
- `WI-4986` / `bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md` - sibling timer work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook/headless behavior remains a live enforcement surface.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `platform_tests/scripts/test_dispatcher_runtime.py::test_harness_command_builds_argv_from_invocation_surfaces` passed; the dispatcher builds commands from `invocation_surfaces.headless` and the fixture contains `--sandbox workspace-write` with `--cd {{PROJECT_ROOT}}`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge state was `GO` at `bridge/gtkb-wi4985-codex-headless-write-boundary-004.md`; implementation-start authorization and work-intent claim were created before protected mutation/report filing. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This report links owner decision, PAUTH, WI-4985, bridge proposal, GO, changed files, and tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The artifact chain is preserved: owner decision -> WI/PAUTH -> proposal -> GO -> MemBase/projection/test changes -> report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This report appends `NEW` version 005 after the `GO` version 004; prior bridge files were not rewritten. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal spec links are carried forward here and mapped to command evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff lint, ruff format, readiness, dispatcher, and authorization checks were executed and observed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project Authorization, Project, Work Item, and target-path evidence are present in this report. |
| `SPEC-AUQ-POLICY-ENGINE-001` | PAUTH/owner-decision evidence was carried forward; no extra owner decision was taken or inferred. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are all inside `E:\GT-KB` platform paths; no adopter application path changed for WI-4985. |
| `GOV-STANDING-BACKLOG-001` | WI-4985 remains the backlog authority; no duplicate work item was created. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex readiness tests now verify the live headless invocation and reject regressions to the prior no-sandbox or full-access forms. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4985-codex-headless-write-boundary` succeeded before implementation/report work. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `scripts/implementation_authorization.py validate` authorized `harness-state/harness-registry.json`, `groundtruth.db`, `platform_tests/groundtruth_kb/cli/test_harness_cli.py`, `scripts/verify_codex_dispatch.py`, and `platform_tests/scripts/test_verify_codex_dispatch.py`. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
# Failed locally because the venv currently has no generated gt.exe wrapper.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.cli import main; raise SystemExit(main(['harness','roles']))"
# Exit 0. Codex A role is prime-builder; headless argv includes --model gpt-5.5, approval_policy="never", model_reasoning_effort="xhigh", --sandbox workspace-write, {{PROMPT}}, --cd {{PROJECT_ROOT}}.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.cli import main; raise SystemExit(main(['bridge','dispatch','status']))"
# Exit 0. Bridge dispatch health PASS; selected candidates include prime-builder: A and loyal-opposition: D, B.

.\groundtruth-kb\.venv\Scripts\python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
# Exit 0. gtkb-wi4985-codex-headless-write-boundary latest_status=GO at -004.

.\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4985-codex-headless-write-boundary --session-id 2026-07-03T09-22-24Z-prime-builder-A-1f10ce --ttl-seconds 7200
# Exit 0. Claim acquired for this dispatch session.

.\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4985-codex-headless-write-boundary --session-id 2026-07-03T09-22-24Z-prime-builder-A-1f10ce
# Exit 0. Packet hash sha256:17cd5f18ba1b7966357d22236503100faabae7e80ad5d183ef32c1cff38b2073.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --no-require-executable
# Exit 0. static_ok=True; dispatchable=True; resolved_executable=C:\Users\micha\AppData\Local\OpenAI\Codex\bin\codex.EXE.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target harness-state/harness-registry.json --target groundtruth.db --target platform_tests/groundtruth_kb/cli/test_harness_cli.py --target scripts/verify_codex_dispatch.py --target platform_tests/scripts/test_verify_codex_dispatch.py
# Exit 0. authorized=true for all listed targets.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/groundtruth_kb/cli/test_harness_cli.py::test_harness_set_invocation_surface_cli_refreshes_projection -q --tb=short --basetemp .gtkb-state\pytest-basetemp-wi4985
# Exit 0. 10 passed, 2 warnings.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_harness_command_builds_argv_from_invocation_surfaces -q --tb=short --basetemp .gtkb-state\pytest-basetemp-wi4985-dispatcher
# Exit 0. 1 passed, 2 warnings.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\ruff.exe check scripts/verify_codex_dispatch.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/groundtruth_kb/cli/test_harness_cli.py
# Exit 0. All checks passed.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/verify_codex_dispatch.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/groundtruth_kb/cli/test_harness_cli.py
# Exit 0. 3 files already formatted.
```

## Observed Results

- Codex A projected headless argv now contains `--sandbox workspace-write` and retains `--model gpt-5.5`, `approval_policy="never"`, `model_reasoning_effort="xhigh"`, `{{PROMPT}}`, and `--cd {{PROJECT_ROOT}}`.
- `workspace-write` is the narrowest write-capable mode used here: it permits in-workspace writes needed by approved bridge work while the readiness code explicitly rejects `danger-full-access`.
- This report was produced inside dispatcher-launched Codex session `2026-07-03T09-22-24Z-prime-builder-A-1f10ce`, not by a direct interactive harness-to-harness spawn.
- The initial focused pytest command without `--basetemp` failed before test execution with `PermissionError: [WinError 5] Access is denied: 'C:\Users\micha\AppData\Local\Temp\pytest-of-micha'`. Rerunning the same targets with in-workspace basetemp paths passed.
- The expected `groundtruth-kb/.venv/Scripts/gt.exe` wrapper is absent in this venv, so the equivalent `groundtruth_kb.cli:main` entrypoint was invoked through the venv Python with `PYTHONPATH` set to `groundtruth-kb/src`. That wrapper issue is outside WI-4985's target scope.

## Files Changed

- `groundtruth.db` - latest MemBase harness row for Codex A version 48 updates the headless invocation surface through `gt-harness-cli`.
- `harness-state/harness-registry.json` - regenerated projection adds Codex A `--sandbox workspace-write`, keeps the model/approval/reasoning pins, and marks the headless surface dispatch-capable. Projection regeneration also reflects current B/D dispatchability state.
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py` - harness CLI projection test now covers the approval-policy pin, reasoning pin, sandbox selector, and headless `can_receive_dispatch`.
- `scripts/verify_codex_dispatch.py` - readiness check now validates required pins, project-root selector, `workspace-write`, and rejects full-access sandbox.
- `platform_tests/scripts/test_verify_codex_dispatch.py` - readiness tests cover the success path and fail-closed regressions for missing sandbox, full-access sandbox, missing pins, and missing project-root selector.

`platform_tests/scripts/test_dispatcher_runtime.py` was an approved target but did not require a new diff in this workspace because its Codex invocation fixture already contains `--sandbox workspace-write`; its targeted command-composition test was still executed.

## Targeted Diff Stat

```text
 groundtruth.db                                     | Bin 540135424 -> 541372416 bytes
 harness-state/harness-registry.json                |  13 +--
 .../groundtruth_kb/cli/test_harness_cli.py         |  11 ++-
 .../scripts/test_verify_codex_dispatch.py          |  89 ++++++++++++++++++++-
 scripts/verify_codex_dispatch.py                   |  51 +++++++++++-
 5 files changed, 156 insertions(+), 8 deletions(-)
```

## Working Tree Scope Note

The repository contains a large pre-existing dirty worktree outside this bridge scope. This implementation report covers only the WI-4985 target paths listed above. No unrelated modified or untracked files were intentionally changed by this dispatch.

## Acceptance Criteria Status

- [x] Codex A headless argv contains `--model gpt-5.5`, `approval_policy="never"`, `model_reasoning_effort="xhigh"`, `--sandbox workspace-write`, and `--cd {{PROJECT_ROOT}}`.
- [x] Focused readiness and harness CLI tests fail closed if the invocation regresses to the old no-sandbox form or drops required pins.
- [x] Dispatcher-runtime command composition was verified against `invocation_surfaces.headless`.
- [x] Live dispatcher-mediated Codex session could run authorized in-root write/report steps without the previous workspace write-boundary rejection.
- [x] No direct harness-to-harness fallback launch path was added.

## Risk And Rollback

Residual risk is limited to the harness registry/projection and readiness-test scope. The selected sandbox is `workspace-write`, not full access. Rollback is a revert of the five changed target paths followed by harness projection regeneration from the previous MemBase harness row. Bridge files and implementation authorization evidence remain append-only audit artifacts and must not be deleted.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Justification: this adds a write-capable Codex headless dispatch capability and readiness guardrails, with associated regression coverage.

## Loyal Opposition Asks

1. Verify that `workspace-write` is acceptable as the narrowest write-capable selector for approved in-root Codex dispatch.
2. Verify that the post-GO write evidence is dispatcher-mediated and not a direct harness-to-harness fallback.
3. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
