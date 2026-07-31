REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T01-42-03Z-prime-builder-A-e64e75
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write; dispatch_id=2026-07-04T01-42-03Z-prime-builder-A-e64e75

# WI-5002 Codex Headless Add-Dir Invocation Repair - Revised Implementation Report

bridge_kind: implementation_report_revision
Document: gtkb-wi5002-codex-headless-add-dir-invocation
Version: 005 (REVISED; blocker response to NO-GO 004)
Responds to NO-GO: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-004.md
Approved proposal: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md
Approved GO: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-002.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Implementation Claim

This revised post-implementation report is not VERIFIED-ready. The new Codex worker launched after the stage-one registry update still cannot write the approved `.codex/skills/verify/helpers/write_verdict.py` target.

The prior report at `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-003.md` completed the static invocation repair: harness `A` headless argv now includes `--add-dir .codex`, preserves `--sandbox workspace-write`, preserves `approval_policy="never"`, preserves `--model gpt-5.5`, preserves `model_reasoning_effort="xhigh"`, and does not include the rejected broad bypass flags. That static state remains true in this dispatch.

The final helper parity acceptance criteria remain blocked:

- `Copy-Item` from `.claude/skills/verify/helpers/write_verdict.py` to `.codex/skills/verify/helpers/write_verdict.py` still fails with access denied.
- A direct Codex `apply_patch` attempt against `.codex/skills/verify/helpers/write_verdict.py` was rejected by the sandbox as outside the project.
- The `.codex` helper hash still differs from the `.claude` and `.cursor` helper hashes.
- The focused pytest suite still reports the same four parser failures.

No source, test, registry, or helper target file was successfully changed by this dispatch. This report records the narrower blocker produced by the approved add-dir route.

## First-Line Role Eligibility Check

- Durable identity file `harness-state/harness-identities.json` maps Codex to harness ID `A`.
- The fresh registry projection in `harness-state/harness-registry.json` assigns harness `A` role `prime-builder`.
- `groundtruth-kb/.venv/Scripts/gt.exe harness roles` could not be executed because no `gt.exe`, `gt.cmd`, `gt.ps1`, or `gt` executable is present under `groundtruth-kb/.venv/Scripts/` or elsewhere in the checkout.
- The bridge scan helper run as `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json` listed `gtkb-wi5002-codex-headless-add-dir-invocation` as latest `NO-GO`, which is Prime Builder-actionable.
- `scripts/bridge_claim_cli.py claim gtkb-wi5002-codex-headless-add-dir-invocation` returned `acting_role: prime-builder`, rowid `29795`, session id `2026-07-04T01-42-03Z-prime-builder-A-e64e75`.

This session is authorized to file a Prime Builder `REVISED` response to the latest `NO-GO`. It is not authorized to write Loyal Opposition verdict statuses.

## Implementation Authorization Evidence

- Implementation-start command: `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5002-codex-headless-add-dir-invocation`
- Observed result: exit 0; `latest_status: NO-GO`; `go_file: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-002.md`; `packet_hash: sha256:9adf0fbfa20440ce565d3c9040d68ee25c33bb428af7661e96dc3053d65371eb`; active PAUTH `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES`; target path globs matched the GO proposal.
- Work-intent command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5002-codex-headless-add-dir-invocation`
- Observed result: exit 0; rowid `29795`; session id `2026-07-04T01-42-03Z-prime-builder-A-e64e75`; `claim_kind: draft`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Codex PB dispatch must complete approved work without manual intervention.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the fix must not use direct harness-to-harness fallback or a different harness as Codex's writer.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific hook/sandbox gaps must be handled mechanically and audibly.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper behavior must not diverge across Claude, Codex, and Cursor after the sandbox route is repaired.
- `ADR-CROSS-HARNESS-PARITY-001` - generated/adapted harness surfaces must preserve behavior parity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active implementation and evidence paths remain inside `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, implementation, and verification must use the numbered bridge chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing specs, target paths, and requirement sufficiency are cited before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the changed invocation and the subsequent `.codex` write path.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical backlog item for this blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the failed route and corrected route are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation preserves evidence for rejected broader sandbox routes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated blocked dispatches triggered this corrected lifecycle step.

## Owner Decisions / Input

- Owner decision `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded work items and implementation authorization records needed to restore stable unattended bridge processing.
- Project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes this WI-5002 repair scope.
- No new owner decision was requested in this headless worker. The current blocker is technical evidence, not an owner-decision blocker.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, and no direct harness fallback.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md` through `-007.md` - previous blocked attempts and discussions regarding Codex helper write boundaries.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` - replacement proposal for the `.codex` add-dir route.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-002.md` - Loyal Opposition GO verdict approving the route with conditions.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-003.md` - staged implementation report from the worker launched before the add-dir route could take effect.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-004.md` - Loyal Opposition NO-GO asking the next worker to prove the `.codex` write, align helper parity, fix parser regressions, and rerun focused tests.

## Specification-Derived Verification Evidence

| Spec / governing surface | Executed verification evidence | Status |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --no-require-executable --json` returned `static_ok: true`, `dispatchable: true`, `codex_helper_add_dir: ".codex"`, and `codex_helper_add_dir_ok: true`. | Static dispatch readiness remains satisfied; runtime helper write is not satisfied. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | This dispatch did not launch another harness, did not ask another harness to write `.codex/**`, and did not add direct harness fallback. | Satisfied. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `Copy-Item -LiteralPath '.claude\skills\verify\helpers\write_verdict.py' -Destination '.codex\skills\verify\helpers\write_verdict.py' -Force` returned access denied. `apply_patch` against `.codex/skills/verify/helpers/write_verdict.py` was rejected as outside the project. | Not satisfied. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Helper hashes remain mismatched: `.claude` and `.cursor` are `E2FFEFBF5ADFBFE8582FCE8A0352422A5C91C688FC405EB9E0690F99ED4D0976`; `.codex` is `9B342375416890D3D3A905DDDEB4EB3C416118565314E118D3A13437963BBD05`. | Not satisfied. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live scan showed latest status `NO-GO`; implementation authorization and work-intent claim succeeded before attempted protected target writes; this response is filed as the next numbered bridge version through the revision helper. | Satisfied for reporting. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest command returned `177 passed, 4 failed, 3 warnings`; ruff check passed; ruff format check passed. | Not satisfied for final verification. |

## Commands Run

- `Get-ChildItem -Path 'groundtruth-kb\.venv\Scripts' -Filter 'gt*'`
  - Observed result: no `gt.exe` or related shim returned.
- `rg --files -g 'gt.exe' -g 'gt.cmd' -g 'gt.ps1' -g 'gt'`
  - Observed result: no matching executable in the checkout.
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json`
  - Observed result: selected thread listed as latest `NO-GO`; Prime Builder actionable.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5002-codex-headless-add-dir-invocation`
  - Observed result: exit 0; `latest_status: NO-GO`; packet hash `sha256:9adf0fbfa20440ce565d3c9040d68ee25c33bb428af7661e96dc3053d65371eb`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5002-codex-headless-add-dir-invocation`
  - Observed result: exit 0; rowid `29795`; `acting_role: prime-builder`; `claim_kind: draft`.
- `Copy-Item -LiteralPath '.claude\skills\verify\helpers\write_verdict.py' -Destination '.codex\skills\verify\helpers\write_verdict.py' -Force`
  - Observed result: exit 1; `Access to the path 'E:\GT-KB\.codex\skills\verify\helpers\write_verdict.py' is denied.`
- `apply_patch` update attempt against `.codex/skills/verify/helpers/write_verdict.py`
  - Observed result: rejected before write with `writing outside of the project; rejected by user approval settings`.
- `Get-Acl -LiteralPath '.codex\skills\verify\helpers\write_verdict.py'`
  - Observed result: file is not read-only, but ACL contains explicit `Deny` entries with `Write` and `Delete` rights for sandbox SID identities.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --no-require-executable --json`
  - Observed result: `static_ok: true`; `dispatchable: true`; `codex_helper_add_dir: ".codex"`; `forbidden_flags_present: []`.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short --basetemp .harness-tmp/pytest-wi5002-add-dir-rerun`
  - Observed result: `177 passed, 4 failed, 3 warnings`.
- `groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py scripts/verify_codex_dispatch.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py`
  - Observed result: `All checks passed!`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py scripts/verify_codex_dispatch.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py`
  - Observed result: `6 files already formatted`.

## Focused Pytest Failures

- `test_claimed_repo_path_parser_preserves_dot_directories[claude]`
- `test_claimed_repo_path_parser_preserves_dot_directories[codex]`
- `test_claimed_repo_path_parser_preserves_dot_directories[cursor]`
- `test_claimed_repo_path_parser_does_not_extract_subpath_suffix[codex]`

The three dot-directory failures still show `.cursor/skills/verify/helpers/write_verdict.py,` being retained with the trailing comma. The Codex subpath failure still extracts the extra suffix `scripts/test_bridge_dispatch_config.py` from a diff-stat style line because the Codex helper copy has not received the current negative-lookbehind regex change.

## Files Changed By This Run

- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-005.md`

No approved implementation target file was successfully changed by this dispatch. Existing dirty files from prior work remain outside this report's change claim.

## Acceptance Criteria Status

- [x] Harness `A` headless argv preserves `--model gpt-5.5`.
- [x] Harness `A` headless argv preserves `approval_policy="never"`.
- [x] Harness `A` headless argv preserves `model_reasoning_effort="xhigh"`.
- [x] Harness `A` headless argv preserves `--sandbox workspace-write`.
- [x] Harness `A` headless argv includes in-root `.codex` add-dir.
- [x] Harness `A` headless argv does not include `--dangerously-bypass-approvals-and-sandbox`.
- [x] Harness `A` headless argv does not include `--sandbox danger-full-access`.
- [ ] `.codex/skills/verify/helpers/write_verdict.py` write succeeds from Codex.
- [ ] `.codex`, `.claude`, and `.cursor` helper hashes match.
- [ ] Full spec-derived verification passes.
- [ ] Required role-reader command `groundtruth-kb/.venv/Scripts/gt.exe harness roles` is available.

## Risk And Rollback

This dispatch made no implementation target changes, so there is no source rollback. The new evidence narrows the WI-5002 failure from "worker launched before add-dir was active" to "updated add-dir static configuration is present, but `.codex` remains unwritable under the active Codex sandbox/ACL boundary."

The likely next repair is not another identical retry of this thread. The next proposal should target the actual `.codex` ACL/sandbox projection layer or the missing local `gt.exe` shim, with explicit target paths for whatever component owns those permissions. Broad sandbox bypass, direct harness-to-harness fallback, and manual owner copy remain rejected.

--- 

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
