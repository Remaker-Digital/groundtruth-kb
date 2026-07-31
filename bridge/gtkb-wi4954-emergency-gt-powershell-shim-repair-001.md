NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f1ec9-3f39-7fc0-9576-7f8e240ecb3e
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: approval_policy=never; sandbox=danger-full-access; interactive_role=prime-builder

# Implementation Proposal - Emergency repair of broken gt PowerShell shim

bridge_kind: prime_proposal
Document: gtkb-wi4954-emergency-gt-powershell-shim-repair
Version: 001
Date: 2026-07-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4954-GT-SHIM-EMERGENCY-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4954

requesting_role: Prime Builder
implementation_scope: defect_fix
authorization_status: proposal_only
requires_review: true
requires_verification: true
implementation_data_scope: no additional database changes in this slice
target_paths: ["scripts/install_gt_path_shim.py", "platform_tests/scripts/test_install_gt_path_shim.py", "groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py", "platform_tests/scripts/test_check_gt_cli_availability.py"]

## Claim

Repair the broken `gt` command launcher path used from native PowerShell. The current user-PATH shim resolves, but it targets a missing project venv console executable; the project venv Python also cannot import `groundtruth_kb` directly. As a result, the canonical `gt bridge dispatch config/status/health` command surface fails exactly when bridge health is being diagnosed.

## Owner Decisions / Input

- `DELIB-20260701-GT-SHIM-EMERGENCY-P0-AUTH` records Mike's 2026-07-01 emergency directive to file and prioritize this as P0, diagnose it, and route the fix ASAP.
- The same decision explicitly preserves the Prime Builder protected-file bridge precondition: implementation still requires independent Loyal Opposition `GO` and implementation-start authorization before protected source/test edits.

## Prior Deliberations

- `DELIB-20260701-GT-SHIM-EMERGENCY-P0-AUTH` - owner emergency P0 authorization for this repair proposal.
- `bridge/gtkb-wi4530-gt-cli-path-install-shim-001.md` and `-002.md` - prior WI-4530 path-shim generator proposal and GO.
- `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md` and `-002.md` - prior doctor-check proposal and GO for `gt` CLI availability.
- `WI-4954` - newly filed P0 defect work item for this emergency command-surface failure.

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

## Requirement Sufficiency

Existing requirements sufficient.

The observed command failure, `WI-4954`, the prior WI-4530/WI-4466 artifacts, and the owner emergency decision are sufficient to authorize a minimal repair. No new requirement is needed before implementation. Broader installer/bootstrap redesign is outside this emergency slice.

## Cross-Harness Disposition

This repair is cross-harness relevant but path-local. The implementation should make the canonical `gt` command surface reliable from native Windows/PowerShell while preserving POSIX launcher behavior in tests. It must not change role assignments, dispatcher routing policy, hook parity claims, or harness eligibility rules.

## Diagnosis Summary

Read-only diagnosis found:

- `gt` resolves to a user-PATH `.cmd` launcher, so PowerShell finds a command.
- The launcher target it reports is the project venv console executable path, but that executable is absent in the current checkout.
- The project venv Python exists, but direct `-m groundtruth_kb.cli` from that venv fails because the package is not importable there.
- Ambient project-root `python -m groundtruth_kb.cli ...` works because the current environment can import the in-root source tree.
- The in-root shim generator currently renders launchers that forward to the venv console executable, matching older assumptions that are false in this checkout.
- The availability doctor check treats `gt` being on PATH as a pass, which misses stale/broken PATH shims that resolve but fail immediately.

## Proposed Scope

Implement the smallest durable in-root repair needed for `WI-4954`:

- Update `scripts/install_gt_path_shim.py` so generated launchers do not depend on a missing venv `gt.exe` console script when a source-tree module launcher is the reliable in-root command path.
- Preserve argument forwarding and path-with-spaces safety for Windows and POSIX renderers.
- Update `groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py` so the doctor check can distinguish an on-PATH but broken/stale `gt` shim from a usable command surface where feasible without unsafe side effects.
- Update `platform_tests/scripts/test_install_gt_path_shim.py` and `platform_tests/scripts/test_check_gt_cli_availability.py` with regression cases for the observed missing-console-script/importability failure.
- Do not modify dispatcher selection, role registry, bridge protocol rules, unrelated skills, or unrelated bridge files.

## Implementation Plan

1. After `GO`, re-run the failing command evidence: `gt bridge dispatch status --json` and the fallback `python -m groundtruth_kb.cli bridge dispatch status --json`.
2. Patch the in-root shim generator to render a robust launcher shape that uses an importable in-root source path or an explicitly validated executable target.
3. Patch the doctor check to fail or warn on a stale PATH shim instead of passing merely because `shutil.which("gt")` returns a path.
4. Add/adjust tests for Windows `.cmd` content, POSIX shell content, missing `gt.exe` fallback behavior, path-with-spaces preservation, and doctor-check stale-shim classification.
5. Run targeted tests and command smoke checks.
6. File a post-implementation bridge report with exact commands and observed results.

## Acceptance Criteria

- Bare `gt bridge dispatch status --json`, `gt bridge dispatch health --json`, and `gt bridge show gtkb-wi4954-emergency-gt-powershell-shim-repair` work from native PowerShell after applying/regenerating the launcher path prescribed by the implementation.
- `python -m groundtruth_kb.cli bridge dispatch status --json` remains a valid fallback.
- The generated launcher no longer assumes a missing venv console executable is present.
- The doctor check no longer reports PASS solely because a broken `gt` shim is on PATH.
- Targeted tests cover the regression and pass.
- No protected files outside the declared target paths are changed.

## Specification-Derived Verification Plan

| Governing artifact | Verification evidence required after implementation |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge dispatch status --json`, `gt bridge dispatch health --json`, and `gt bridge show gtkb-wi4954-emergency-gt-powershell-shim-repair` execute from native PowerShell without the launcher failure. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_install_gt_path_shim.py platform_tests/scripts/test_check_gt_cli_availability.py -q --tb=short` includes regression tests for stale/missing executable behavior. |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | Command smoke confirms bridge dispatch/status surfaces remain available through the shared CLI without role-registry or dispatcher-rule changes. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Test assertions confirm Windows launcher behavior is represented as command-surface availability, not hook-interception parity. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- scripts/install_gt_path_shim.py platform_tests/scripts/test_install_gt_path_shim.py groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py platform_tests/scripts/test_check_gt_cli_availability.py` shows only in-root target files. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report cites `WI-4954`, `DELIB-20260701-GT-SHIM-EMERGENCY-P0-AUTH`, this PAUTH, and this bridge thread. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation report links root-cause evidence to changed tests and observed command results. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The emergency directive remains captured as `WI-4954` and this proposal before implementation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair` passes with `missing_required_specs: []`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance confirms PAUTH/project/WI metadata and target paths are present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report includes this table's spec-to-test mapping, exact commands, and observed results. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation report cites `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4954-GT-SHIM-EMERGENCY-20260701`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Diff review confirms implementation stayed within source/script/test/doctor-check repair and avoided forbidden operations. |

Additional targeted commands:

```powershell
python -m pytest platform_tests/scripts/test_install_gt_path_shim.py platform_tests/scripts/test_check_gt_cli_availability.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4954-emergency-gt-powershell-shim-repair
gt bridge dispatch status --json
gt bridge dispatch health --json
gt bridge show gtkb-wi4954-emergency-gt-powershell-shim-repair
```

## Out Of Scope

- Reworking dispatcher routing, target selection, harness roles, or provider backpressure behavior.
- Editing the existing unauthorized LO revert proposal thread.
- Broad bootstrap redesign beyond the minimal launcher/doctor/test repair.
- Production deployment, credential lifecycle work, git history rewrite, or broad dirty-worktree cleanup.

## Risks And Mitigations

- Risk: a generated launcher that works only from one working directory. Mitigation: tests must assert stable root/source path behavior and path-with-spaces quoting.
- Risk: doctor check becomes too invasive by executing arbitrary PATH commands. Mitigation: keep execution bounded and side-effect-free, or classify only deterministic in-root/user-shim patterns that can be safely inspected.
- Risk: emergency repair creates a second command authority. Mitigation: keep `groundtruth_kb.cli:main` as the only CLI entrypoint and update only launcher pathing around it.

## Recommended Commit Type

fix
