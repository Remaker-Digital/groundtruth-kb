REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-04T03-49-42Z-prime-builder-A-3b9808
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write; dispatch_id=2026-07-04T03-49-42Z-prime-builder-A-3b9808

# WI-5002 Codex Dotdir Sandbox ACL Correction - Blocker Record

bridge_kind: implementation_report
Document: gtkb-wi5002-codex-dotdir-sandbox-acl-correction
Version: 007 (REVISED; headless blocker record)
Date: 2026-07-04 UTC
Responds to NO-GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-006.md
Responds to GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md
Approved proposal: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
target_paths: [".codex/**", ".claude/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "scripts/install_gt_path_shim.py", "platform_tests/scripts/test_install_gt_path_shim.py", "scripts/repair_codex_dotdir_acl.ps1", "platform_tests/scripts/test_repair_codex_dotdir_acl.py"]
Recommended commit type: fix

## Prime Role Eligibility Check

Prime Builder status filing eligibility was checked before drafting this status-bearing bridge file:

- Durable identity source: `harness-state/harness-identities.json` maps `codex` to harness ID `A`.
- Durable role reader fallback: `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness roles` returned harness `A`, `harness_name: codex`, `role: ["prime-builder"]`, `status: active`.
- Required wrapper caveat: `groundtruth-kb\.venv\Scripts\gt.exe harness roles` could not be executed because `groundtruth-kb\.venv\Scripts\gt.exe` is absent in this checkout. This artifact records that caveat and uses the project venv package CLI fallback only for read-only role/state checks.
- Status authority: Prime Builder may write `REVISED` after latest `NO-GO`; Prime Builder did not write `GO`, `NO-GO`, or `VERIFIED`.
- Work-intent claim: `scripts\bridge_claim_cli.py status gtkb-wi5002-codex-dotdir-sandbox-acl-correction` reported active claim rowid `29819`, `acting_role: prime-builder`, `latest_bridge_status: NO-GO`, and `ttl_expires_at: 2026-07-04T05:53:30Z`.

## Revision Claim

Prime Builder processed the latest `NO-GO` at `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-006.md` in auto-dispatch session `2026-07-04T03-49-42Z-prime-builder-A-3b9808`.

The latest NO-GO is accepted. The code-level unresolved-SID repair reported at `-005.md` is sound, but the live `.codex` DACL remains unrepaired and this headless Prime Builder session still lacks authority to persist the required DACL mutation. Because this auto-dispatched worker cannot ask the owner interactively, this artifact records the blocker and stops.

No source, test, helper, ACL, credential, deployment, or sandbox configuration changes were made in this dispatch. No broad sandbox bypass, `danger-full-access`, direct harness fallback, owner manual copy workaround, or retired poller restoration was used.

## Requirement Sufficiency

Existing requirements remain sufficient for the intended WI-5002 repair. The remaining gap is not an unclear requirement. It is an execution-environment authority blocker: the current Codex sandbox identity cannot write `.codex/**` and cannot remove or override the owner-owned Deny ACEs that block `.codex/**` writes.

## Owner Decisions / Input

Previously cited owner/project authority remains in effect:

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes stable unattended bridge processing and bounded WI-5002 repair work.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes the approved WI-5002 target set.

Blocked owner-side condition recorded for later interactive handling: resolving WI-5002 now requires owner-side Windows ACL authority or an owner scope decision. Practical routes are:

1. remove the two remaining `.codex` Deny ACEs from an account with DACL write authority;
2. grant the active Codex sandbox identity sufficient `.codex/**` write/DACL authority without broadening access outside `E:\GT-KB\.codex`; or
3. accept `.codex/**` write denial as a permanent Codex limitation and revise WI-5002 scope accordingly.

This headless dispatch does not request an interactive decision in prose.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended bridge processing requires Codex dispatch readiness to reflect live `.codex` writability.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - this dispatch did not route `.codex/**` writes through another harness.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific sandbox and hook gaps must be surfaced mechanically and fail closed when unresolved.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper parity cannot be completed while Codex cannot write `.codex/**`.
- `ADR-CROSS-HARNESS-PARITY-001` - verify-helper parity remains the target behavior after the write boundary is repaired.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all evidence and bridge artifacts remain inside `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this status update preserves the numbered bridge chain and latest `NO-GO` continuation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward governing specifications and target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths remain explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps runtime checks to the blocked acceptance criteria and does not claim verification.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical work item for the Codex hidden helper-surface blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-blocking condition is preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source-level repair evidence and remaining operational blocker are separated instead of collapsed into a false success claim.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the latest NO-GO triggered this blocker record.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner goal for stable unattended bridge processing.
- `DELIB-20260703-WI5002-DOTDIR-SANDBOX-ACL-IMPLEMENTATION-APPROVED` - owner implementation approval cited by the WI-5002 chain.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md` - initial implementation report that claimed live repair success.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-004.md` - NO-GO identifying live runtime contradiction and unresolved SID removal risk.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-005.md` - REVISED report with unresolved-SID source/test correction and explicit operational blocker.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-006.md` - latest NO-GO confirming the code revision is sound but WI-5002 remains blocked on owner-side ACL authority.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` through `-007.md` - prior add-dir route and rejection of identical add-dir-only retries.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md` through `-010.md` - repeated `.codex` write-boundary evidence that motivated WI-5002.

## Findings Addressed

### Blocker Requires Owner Intervention

Accepted and recorded. Prime Builder cannot complete the core acceptance criterion from this sandbox because the live DACL still blocks `.codex` writes and this session cannot persist DACL changes. The latest runtime checks show:

- `scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json` returned exit 1 with `needs_repair: true`, `risky_deny_count: 2`, and `current_identity.allow_present: false`.
- `scripts\verify_codex_dispatch.py --no-require-executable --json` returned exit 1 with `codex_dotdir_acl_ok: false`, `static_ok: false`, and `dispatchable: false`.
- A direct `.codex\codex-write-probe-dispatch-007.tmp` write/delete probe returned exit 1: `Access to the path 'E:\GT-KB\.codex\codex-write-probe-dispatch-007.tmp' is denied.`
- `Test-Path groundtruth-kb\.venv\Scripts\gt.exe` returned `False`; the requested project-local console wrapper remains absent.

## Scope Changes

No implementation scope changed in this dispatch. No file outside the bridge audit chain is claimed changed by this `REVISED` artifact. The previously modified WI-5002 source/test files remain unverified until the live `.codex` ACL blocker is resolved and the full approved verification plan can pass.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed evidence in this dispatch |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `scripts\verify_codex_dispatch.py --no-require-executable --json` returned `dispatchable: false`; dispatch remains correctly blocked. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | No alternate harness wrote `.codex/**`; direct Codex write probe still fails, so this report does not claim helper-write success. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json` returned structured fail-closed ACL evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All evidence and this bridge artifact remain in `E:\GT-KB`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Runtime checks are recorded as blocked evidence; this artifact does not request `VERIFIED`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge status was confirmed as `NO-GO`; Prime Builder filed the next numbered `REVISED` artifact only. |

## Commands Run

```text
Get-Content harness-state/harness-identities.json
groundtruth-kb\.venv\Scripts\gt.exe harness roles
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness roles
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch status --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge show gtkb-wi5002-codex-dotdir-sandbox-acl-correction --json --compact
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge threads --wi WI-5002 --json --compact
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --no-require-executable --json
PowerShell direct write/delete probe for .codex\codex-write-probe-dispatch-007.tmp
Test-Path groundtruth-kb\.venv\Scripts\gt.exe
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5002-codex-dotdir-sandbox-acl-correction
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py status gtkb-wi5002-codex-dotdir-sandbox-acl-correction
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\revise_bridge.py plan gtkb-wi5002-codex-dotdir-sandbox-acl-correction
```

## Observed Results

- Harness identity: Codex maps to durable harness ID `A`.
- Harness role: package CLI role reader returned harness `A` as active `prime-builder`.
- Required `gt.exe` wrapper: absent from `groundtruth-kb\.venv\Scripts`; PowerShell invocation returned command-not-found and `Test-Path` returned `False`.
- Dispatcher status: health `PASS`; selected Prime Builder harness is Codex `A`; runtime classification for Prime Builder shows the selected thread remains live but work-intent-held.
- Selected thread state: latest path `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-006.md`; latest status `NO-GO`; version count `6`.
- WI-5002 threads: this thread is the only latest `NO-GO` WI-5002 ACL-correction thread; sibling WI-5002 hidden-helper thread is `VERIFIED`; headless-add-dir thread is `WITHDRAWN`.
- ACL check: exit 1; `needs_repair: true`; `risky_deny_count: 2`; risky Deny identity `S-1-5-21-2908765920-875073000-2352713335-4168283502`; `sandbox_group.allow_present: true`; `current_identity.allow_present: false` for `DESKTOP-G6Q5ANI\CodexSandboxOffline`.
- Dispatch verifier: exit 1; `codex_dotdir_acl_ok: false`; `static_ok: false`; `dispatchable: false`; headless argv still includes `--sandbox workspace-write` and `--add-dir .codex`; forbidden flags remain absent.
- Direct `.codex` write probe: exit 1; access denied.
- Work-intent claim: active rowid `29819`, latest bridge status `NO-GO`, expires `2026-07-04T05:53:30Z`.

## Pre-Filing Preflight Subsection

Candidate content preflights were run before live filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5002-codex-dotdir-sandbox-acl-correction-007.md --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5002-codex-dotdir-sandbox-acl-correction-007.md
```

Observed pre-filing result:

- Applicability preflight: exit 0; `preflight_passed: true`; `packet_hash: sha256:62aec24aff7e156e0f6218dfb186bfd804f585fe8d4c20604c4afac65d56821d`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit 0; `Blocking gaps (gate-failing): 0`; must-apply evidence gaps: `0`.
- WI collision check: exit 0; `has_collisions: false`; declared work item `WI-5002` matches the cited work item.
- Helper file mode reruns the applicability and clause preflights before writing the live artifact.

## Acceptance Criteria Status

- [ ] Codex can write `.codex/skills/verify/helpers/write_verdict.py` from its own approved route. Still blocked; direct `.codex` write probe fails with access denied.
- [x] ACL failure is mechanically detected and reported as structured evidence.
- [x] Codex dispatch readiness fails closed while `.codex` ACL repair remains needed.
- [ ] The project-local `gt.exe harness roles` command exists. Still absent from `groundtruth-kb\.venv\Scripts`.
- [ ] `.claude`, `.codex`, and `.cursor` verify helper parity can be freshly completed by Codex. Still blocked because `.codex` is not writable.
- [ ] Full WI-5002 pytest, ruff, format, helper parity, and live write checks pass. Not rerun because the live ACL authority blocker makes completion impossible in this headless dispatch.

## Risk And Rollback

Primary risk is procedural churn: repeated headless dispatches will continue to rediscover the same `.codex` DACL authority blocker until owner-side ACL authority or scope direction changes. This artifact records the condition so later interactive handling can address it directly.

Rollback is limited to bridge state. Bridge artifacts are append-only and must not be deleted. No source or ACL change was made in this dispatch.

## Loyal Opposition Asks

Treat this as a blocker record, not as a verification-ready implementation report. Return `NO-GO` or another non-terminal response unless the live `.codex` DACL has been corrected, `scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json` returns `needs_repair: false`, `scripts\verify_codex_dispatch.py --no-require-executable --json` returns `dispatchable: true`, a direct `.codex` write probe succeeds, and the required role-reader wrapper or approved equivalent is available.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
