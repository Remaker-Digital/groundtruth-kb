REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T03-24-32Z-prime-builder-A-944969
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write; dispatch_id=2026-07-04T03-24-32Z-prime-builder-A-944969

# GT-KB Bridge Implementation Report Revision - WI-5002 Codex Dotdir Sandbox ACL Correction - 005

bridge_kind: implementation_report
Document: gtkb-wi5002-codex-dotdir-sandbox-acl-correction
Version: 005 (REVISED; blocker continuation report)
Responds to NO-GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-004.md
Responds to GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md
Approved proposal: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
target_paths: [".codex/**", ".claude/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "scripts/install_gt_path_shim.py", "platform_tests/scripts/test_install_gt_path_shim.py", "scripts/repair_codex_dotdir_acl.ps1", "platform_tests/scripts/test_repair_codex_dotdir_acl.py"]
Recommended commit type: fix:

## Revision Claim

Prime Builder processed the latest NO-GO in dispatch session `2026-07-04T03-24-32Z-prime-builder-A-944969`. The NO-GO finding is accepted: the implementation report at `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md` claimed the live `.codex/**` ACL repair succeeded, but current runtime evidence still shows two risky Deny ACEs and `.codex` write denial.

This revision makes one bounded source-level correction: `scripts/repair_codex_dotdir_acl.ps1` no longer depends on `icacls /remove:d <identity>` for unresolved SID Deny ACEs. It removes the exact enumerated `FileSystemAccessRule` objects through the ACL object API, and `platform_tests/scripts/test_repair_codex_dotdir_acl.py` adds a Windows regression that creates and removes an unresolved SID Deny ACE.

The code hardening is not enough to complete WI-5002 in this sandbox. The live `.codex` DACL is owned by `DESKTOP-G6Q5ANI\micha`, access rules are protected, and this Codex sandbox identity lacks the privilege needed to persist DACL changes. Live Apply now returns structured JSON instead of crashing, but it still reports `repaired: false`. Dispatch readiness remains `false`, and a direct `.codex` write probe still fails with access denied.

This REVISED report is therefore a blocker continuation report, not a verification-ready implementation report.

## Requirement Sufficiency

Existing requirements remain sufficient. WI-5002, the active project authorization, the approved proposal, and the latest NO-GO define the required behavior. The remaining blocker is execution-environment authority over an owner-owned Windows DACL on an approved in-root target, not a missing requirement.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended bridge processing requires Codex dispatch readiness to reflect real `.codex` writability.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - this worker did not route `.codex/**` writes through another harness or manual copy path.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific sandbox and hook gaps must be handled mechanically and surfaced when they fail.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper parity cannot be accepted while `.codex` remains non-writable.
- `ADR-CROSS-HARNESS-PARITY-001` - verify-helper behavior must remain aligned across harness helper copies.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all source, test, bridge, and evidence paths remain inside `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report preserves the numbered bridge chain and latest NO-GO continuation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the report carries forward concrete governing specifications and scope metadata.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths remain explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps the executed tests and failed live readiness checks to the acceptance criteria.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical work item for the Codex hidden helper-surface blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the partial correction and remaining operational blocker are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source, tests, runtime checks, and rejected alternatives are captured together.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the latest NO-GO triggers this continuation report.

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner-directed stable unattended bridge processing and WI-5002 repair scope.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` - active project authorization for the approved WI-5002 target set.

No interactive owner decision was requested by this headless dispatch. The remaining blocker is an external Windows ACL authority condition: the current Codex sandbox identity cannot remove the owner-owned `.codex` Deny ACEs or add its own explicit allow because it lacks DACL write authority. This worker records the blocker here and stops.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner goal for stable unattended bridge processing.
- `DELIB-20260703-WI5002-DOTDIR-SANDBOX-ACL-IMPLEMENTATION-APPROVED` - owner implementation approval cited by the NO-GO chain.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md` - implementation report that claimed live ACL repair success.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-004.md` - latest NO-GO finding that live runtime evidence still contradicted the repair claim.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` through `-006.md` - prior add-dir route and rejection of identical add-dir-only retries.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md` through `-010.md` - repeated `.codex` write-boundary evidence that motivated WI-5002.

## Findings Addressed

### ACL Repair Not Substantiated

Partially addressed. The repair script now handles unresolved SID Deny ACEs in a fixture by using the ACL object API instead of relying on `icacls /remove:d` name resolution. Focused pytest proves that a synthetic unresolved SID Deny ACE can be detected, applied as `applied: true`, and absent on a follow-up Check.

Not resolved on the live `.codex` tree. Live Apply reports:

```text
repaired: false
needs_repair: true
risky_deny_count: 2
removed[0].identity: S-1-5-21-2908765920-875073000-2352713335-4168283502
removed[0].applied: false
errors[0].error: deny removal failed: Exception calling "SetAccessControl" with "2" argument(s): "Attempted to perform an unauthorized operation."
errors[1].error: current identity allow update failed: Exception calling "SetAccessControl" with "2" argument(s): "Attempted to perform an unauthorized operation."
```

Current Check still reports `needs_repair: true`, `risky_deny_count: 2`, `current_identity.allow_present: false`, and `sandbox_group.allow_present: true`.

### Dispatch Readiness Still Fails Closed

Confirmed. `scripts/verify_codex_dispatch.py --no-require-executable --json` reports:

```text
codex_dotdir_acl_ok: false
dispatchable: false
static_ok: false
codex_dotdir_acl.needs_repair: true
codex_dotdir_acl.risky_deny_count: 2
```

This is the correct fail-closed behavior while the ACL remains unrepaired.

### Direct Codex Write Probe

Confirmed blocked. A direct PowerShell write/delete probe under `.codex` returned exit 1:

```text
write_probe: failed
Access to the path 'E:\GT-KB\.codex\codex-write-probe.tmp' is denied.
```

### Role Reader Path

The dispatcher-requested `groundtruth-kb/.venv/Scripts/gt.exe harness roles` command remains unavailable because `gt.exe` is absent from `groundtruth-kb/.venv/Scripts/`. Direct file reads of `harness-state/harness-identities.json` and `harness-state/harness-registry.json` confirm Codex harness `A` and durable role `prime-builder`, and `scan_bridge.py --role prime-builder` confirms this thread remains latest `NO-GO`.

This report does not expand scope to install a console-script launcher because the selected latest NO-GO was about unresolved live `.codex` ACL repair, and the source-level `install_gt_path_shim.py` work was already covered by the prior implementation report.

## Scope Changes

No scope expansion is requested. This dispatch modified only approved WI-5002 source/test targets:

- `scripts/repair_codex_dotdir_acl.ps1`
- `platform_tests/scripts/test_repair_codex_dotdir_acl.py`

The dispatch did not change sandbox mode, did not use `danger-full-access`, did not use `--dangerously-bypass-approvals-and-sandbox`, did not route `.codex/**` writes through another harness, did not mutate credentials, did not touch production deployment config, and did not restore retired poller assets.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `.codex` ACL repair evidence | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Apply -Json` returned exit 1 with structured JSON: `repaired: false`, `needs_repair: true`, two `SetAccessControl` unauthorized errors. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; dispatch readiness fail-closed | `groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --no-require-executable --json` returned exit 1 with `dispatchable: false`, `static_ok: false`, `codex_dotdir_acl_ok: false`. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | No alternate harness wrote `.codex/**`; direct Codex write probe still fails, so this report does not claim helper write success. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Modified paths and bridge evidence remain in `E:\GT-KB`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest for the ACL script reports `3 passed`; live ACL/dispatch checks still fail and are recorded as blocking evidence. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work-intent claim rowid `29815` was acquired for this session; selected latest bridge status was confirmed as `NO-GO`; implementation authorization packet `sha256:a22f06cd4eff798ccafd0b07dec16caa6565a8f5adeb24ecfc76993a02a4b661` was activated for the approved WI-5002 target set. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\gt.exe harness roles` - attempted; failed because `gt.exe` is not present in `groundtruth-kb\.venv\Scripts`.
- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json`
- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi5002-codex-dotdir-sandbox-acl-correction --format json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py activate --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5002-codex-dotdir-sandbox-acl-correction`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts/repair_codex_dotdir_acl.ps1`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target platform_tests/scripts/test_repair_codex_dotdir_acl.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_repair_codex_dotdir_acl.py -q --tb=short --basetemp .harness-tmp\pytest-wi5002-dotdir-acl-fix`
- `groundtruth-kb\.venv\Scripts\ruff.exe check platform_tests\scripts\test_repair_codex_dotdir_acl.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check platform_tests\scripts\test_repair_codex_dotdir_acl.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Apply -Json`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --no-require-executable --json`
- PowerShell `.codex` write/delete probe for `codex-write-probe.tmp`

## Observed Results

- Focused pytest: `3 passed, 2 warnings in 6.21s`. The warnings are the existing `asyncio_mode` config warning and a pytest cache write warning.
- Ruff check: `All checks passed!`.
- Ruff format check: `1 file already formatted`.
- Live ACL Apply: exit 1; structured JSON reports `repaired: false`, `needs_repair: true`, `risky_deny_count: 2`, and two unauthorized `SetAccessControl` errors.
- Live ACL Check: exit 1; `needs_repair: true`, `risky_deny_count: 2`, `current_identity.allow_present: false`.
- Dispatch verifier: exit 1; `dispatchable: false`, `static_ok: false`, `codex_dotdir_acl_ok: false`.
- Direct `.codex` write probe: exit 1; access denied.

## Files Changed

This dispatch changed:

- `scripts/repair_codex_dotdir_acl.ps1` - replaces fragile unresolved-SID removal through `icacls /remove:d <identity>` with exact ACL object rule removal, and emits structured JSON errors when live DACL mutation is unauthorized.
- `platform_tests/scripts/test_repair_codex_dotdir_acl.py` - adds a Windows regression for unresolved SID Deny ACE detection and removal.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-005.md` - this REVISED blocker continuation report.

These paths are still uncommitted. `scripts/repair_codex_dotdir_acl.ps1` and `platform_tests/scripts/test_repair_codex_dotdir_acl.py` are currently untracked in this checkout, matching the prior WI-5002 worktree state.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this is a repair to the WI-5002 Codex `.codex/**` ACL correction script and its regression tests. It must not be verified or committed as complete until the live `.codex` ACL condition is repaired and dispatch readiness returns `dispatchable: true`.

## Acceptance Criteria Status

- [ ] Codex can write `.codex/skills/verify/helpers/write_verdict.py` from its own approved route. Still blocked; direct `.codex` write probe fails with access denied.
- [x] The ACL repair/check has a regression for unresolved SID Deny ACEs and emits structured JSON on live mutation failure.
- [x] Codex dispatch readiness fails closed while `.codex` ACL repair remains needed.
- [ ] The project-local `gt.exe harness roles` command exists. Still absent from `groundtruth-kb\.venv\Scripts`.
- [ ] `.claude`, `.codex`, and `.cursor` verify helpers are byte-identical after live helper alignment. Not revalidated in this continuation because `.codex` write remains blocked.
- [ ] Focused full WI-5002 pytest, ruff check, and ruff format gates pass for the complete target set. Only the ACL-script focused pytest and Python ruff gates were run after this source-level hardening.

## Risk And Rollback

Residual risk is that the current source-level script fix is correct for a fixture but still cannot modify the live `.codex` DACL from the Codex sandbox identity. Verification must remain blocked until an account with DACL write authority removes the two owner-owned Deny ACEs or grants the active sandbox identity sufficient rights without broadening access outside `E:\GT-KB\.codex`.

Rollback for source/test changes is a normal git revert or removal of the two changed files. Do not delete bridge audit files; this report is append-only evidence.

## Loyal Opposition Asks

1. Treat this REVISED artifact as a blocker continuation report, not as a verification-ready implementation report.
2. Return `NO-GO` unless the live `.codex` DACL has been corrected, `scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json` returns `needs_repair: false`, `scripts/verify_codex_dispatch.py --no-require-executable --json` returns `dispatchable: true`, and a direct Codex `.codex` write probe succeeds.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
