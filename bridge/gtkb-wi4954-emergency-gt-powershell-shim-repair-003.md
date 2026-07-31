NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 2026-07-01T19-06-35Z-prime-builder-A-13250b
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: approval_policy=never; sandbox=workspace-write; dispatcher_auto_dispatch=true

# GT-KB Bridge Implementation Report - Emergency repair of broken gt PowerShell shim

bridge_kind: implementation_report
Document: gtkb-wi4954-emergency-gt-powershell-shim-repair
Version: 003 (NEW; post-implementation report)
Date: 2026-07-01 UTC
Responds to GO: bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-002.md
Approved proposal: bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-001.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4954-GT-SHIM-EMERGENCY-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4954

Recommended commit type: fix

## Implementation Claim

Implemented the approved WI-4954 repair inside the four authorized target paths:

- `scripts/install_gt_path_shim.py` now generates launchers that invoke the durable `groundtruth_kb.cli` module through the project venv Python with `groundtruth-kb/src` on `PYTHONPATH`, instead of forwarding to the missing `.venv/Scripts/gt.exe` console script.
- The legacy `resolve_venv_gt_exe` path resolver remains available only for stale-shim diagnostics and tests.
- `groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py` now structurally inspects generated GT-KB shims without executing arbitrary PATH commands, fails stale generated shims that point at missing legacy venv console scripts, and warns when only the source-tree module fallback is available.
- Focused tests now cover the missing legacy `gt.exe` failure, valid generated source-tree module shims, missing generated-shim targets, preserved Windows/POSIX renderer behavior, and path-with-spaces quoting.

The pre-existing user-level PATH shim at `C:\Users\micha\.local\bin\gt.cmd` was not overwritten in this sandbox because it is outside `E:\GT-KB`. I validated the prescribed regenerated launcher by placing the generated `gt.cmd` first on PATH from an in-root temporary directory and running the native PowerShell smoke commands.

## Owner Decisions / Input

- `DELIB-20260701-GT-SHIM-EMERGENCY-P0-AUTH` records Mike's 2026-07-01 emergency P0 authorization for this repair lane.
- No new owner decision was required during implementation. The work stayed inside the PAUTH and latest `GO` conditions.

## Prior Deliberations

- `DELIB-20260701-GT-SHIM-EMERGENCY-P0-AUTH` - owner emergency P0 authorization for this repair.
- `bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-002.md` - Loyal Opposition `GO` verdict.
- `bridge/gtkb-wi4530-gt-cli-path-install-shim-001.md` / `-002.md` - prior path-shim generator proposal and GO.
- `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md` / `-002.md` - prior doctor-check proposal and GO.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge commands must remain available through the governed command surface used by agents and dispatcher workflows.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - command-surface availability must be mechanically tested, not assumed from docs.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - the `gt` command is a shared harness command path used by role resolution, bridge dispatch, and diagnostics.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex/native Windows command behavior must be represented honestly; fallback scripts must not claim unavailable live-hook behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - durable implementation files and tests for this repair stay under `E:/GT-KB`; any user-PATH placement remains a runtime installation concern, not an authoritative project artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the emergency directive is captured as a work item, PAUTH, DELIB, proposal, implementation report, and verification chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix must preserve traceability between root cause, tests, and the implemented command path.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner emergency directive crossed from chat into actionable P0 work and was captured as `WI-4954`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specs before GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal names the active PAUTH, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map linked specs to executed command evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must remain within the active PAUTH for `WI-4954`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the repair must stay within allowed source/script/test/doctor-check mutation classes and forbidden-operation boundaries.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Generated-shim smoke in native PowerShell: `gt bridge dispatch status --json`, `gt bridge dispatch health --json`, and `gt bridge show gtkb-wi4954-emergency-gt-powershell-shim-repair` all exited 0 with the generated in-root shim first on PATH. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Focused pytest slice passed: 27 tests cover generator and doctor-check regressions for stale/missing executable behavior. |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | CLI role reader worked through the explicit venv Python/source-tree module path; bridge dispatch status/health smoke worked through the generated `gt` path. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests assert launcher/doctor command-surface behavior only; no hook-interception claims or dispatcher policy changes were introduced. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- <authorized paths>` showed only the four approved in-root target files before this implementation report was filed. User-PATH placement was not mutated. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This report cites `WI-4954`, the PAUTH, the owner DELIB, and the bridge thread. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Tests link the root cause to the repair: generated launchers now target venv Python + source tree; doctor check fails stale legacy generated shims. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The emergency directive remains captured as `WI-4954`, the PAUTH, this proposal/report chain, and `DELIB-20260701-GT-SHIM-EMERGENCY-P0-AUTH`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `bridge_applicability_preflight.py --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair` exited 0 with `preflight_passed: true` and empty missing spec lists. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `implementation_authorization.py begin --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair` exited 0 and returned the active PAUTH, project, WI, latest `GO`, and target path globs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every linked specification to executed command evidence and observed results below. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet `sha256:fc87ef9ad6f12e49dc6e5e627f01e251085ee7f35b524a8f8bb4c50869410d4a` confirmed the PAUTH was active for `WI-4954`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Diff review stayed within script/source/test/doctor-check repair paths and avoided forbidden operations, deployment, credential changes, and out-of-root mutation. |

## Commands Run

- `Get-Content -Raw harness-state\harness-identities.json` - confirmed Codex durable harness id `A`.
- `.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness roles` with `PYTHONPATH=E:\GT-KB\groundtruth-kb\src` - confirmed harness `A` role `prime-builder`.
- `.\groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json` - confirmed latest selected thread status `GO`.
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair` - confirmed active implementation-start packet.
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4954-emergency-gt-powershell-shim-repair` - acquired Prime implementation work-intent claim for this session.
- `gt bridge dispatch status --json` - baseline failure reproduced with existing user PATH shim: it still targets missing `E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe`.
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_install_gt_path_shim.py platform_tests\scripts\test_check_gt_cli_availability.py -q --tb=short --basetemp <in-root temp>` - focused regression suite.
- `.\groundtruth-kb\.venv\Scripts\ruff.exe check scripts\install_gt_path_shim.py groundtruth-kb\src\groundtruth_kb\project\checks\gt_cli_availability.py platform_tests\scripts\test_install_gt_path_shim.py platform_tests\scripts\test_check_gt_cli_availability.py`
- `.\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\install_gt_path_shim.py groundtruth-kb\src\groundtruth_kb\project\checks\gt_cli_availability.py platform_tests\scripts\test_install_gt_path_shim.py platform_tests\scripts\test_check_gt_cli_availability.py`
- Generated-shim smoke from native PowerShell with generated `gt.cmd` first on PATH:
  - `gt bridge dispatch status --json`
  - `gt bridge dispatch health --json`
  - `gt bridge show gtkb-wi4954-emergency-gt-powershell-shim-repair`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch status --json` with `PYTHONPATH=E:\GT-KB\groundtruth-kb\src`
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair`
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair`

## Observed Results

- Focused pytest: `27 passed, 2 warnings in 0.35s`. Warnings were existing pytest configuration/cache warnings: unknown `asyncio_mode` and `.pytest_cache` write warning.
- Ruff lint: `All checks passed!`
- Ruff format check: `4 files already formatted`
- Baseline existing user shim: exit 1, message `'"E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe"' is not recognized as an internal or external command, operable program or batch file.`
- Generated-shim smoke: all three `gt bridge ...` commands exited 0 when the generated `gt.cmd` was first on PATH.
- Module fallback smoke: `venv python -m groundtruth_kb.cli bridge dispatch status --json: ok`.
- Applicability preflight: exit 0, `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:e6832a710752af0b8c1df94890b21315d5eecb6ded9a1cf9cd7cee9de5b50b61`.
- Clause preflight: exit 0, 5 clauses evaluated, `must_apply: 4`, evidence gaps in must-apply clauses: 0, blocking gaps: 0.

## Files Changed

- `scripts/install_gt_path_shim.py`
- `platform_tests/scripts/test_install_gt_path_shim.py`
- `groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py`
- `platform_tests/scripts/test_check_gt_cli_availability.py`
- `bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-003.md` (this implementation report, filed after helper publication)

## Acceptance Criteria Status

- PASS: generated launcher no longer assumes the missing venv console executable; it launches `groundtruth_kb.cli` through venv Python with the in-root source tree on `PYTHONPATH`.
- PASS: generated `gt` command surface passed `bridge dispatch status`, `bridge dispatch health`, and `bridge show` smoke checks from native PowerShell when the regenerated launcher was first on PATH.
- PASS: explicit source-tree module fallback passed `bridge dispatch status`.
- PASS: doctor check no longer reports PASS solely because a broken generated `gt` shim is on PATH; focused tests cover stale legacy shim failure.
- PASS: targeted tests and code-quality gates passed.
- PASS: implementation changed only the declared source/script/test target paths before filing this report.
- Residual operational note: the existing user-level `C:\Users\micha\.local\bin\gt.cmd` remains stale until regenerated outside the sandbox; this report validates the prescribed regenerated content but does not mutate that out-of-root runtime placement.

## Risk And Rollback

Risk is limited to launcher text generation and the advisory doctor check. Rollback is to revert the four implementation target files; no database, dispatcher, role registry, credential, deployment, or user-PATH mutation was performed by this implementation.

## Loyal Opposition Asks

1. Verify that the generated launcher shape and doctor-check stale-shim classification satisfy the approved `GO` conditions.
2. Return `VERIFIED` if the implementation and this report satisfy the linked specification-derived evidence; otherwise return `NO-GO` with concrete findings.
