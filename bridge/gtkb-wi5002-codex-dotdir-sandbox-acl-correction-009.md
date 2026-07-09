REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T04-09-35Z-prime-builder-A-0c4b1b
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write; dispatch_id=2026-07-04T04-09-35Z-prime-builder-A-0c4b1b

# WI-5002 Codex Dotdir Sandbox ACL Correction - Blocker Record

bridge_kind: prime_revised_report
Document: gtkb-wi5002-codex-dotdir-sandbox-acl-correction
Version: 009
Date: 2026-07-04 UTC
Responds to NO-GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-008.md
Responds to GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md
Approved proposal: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002

target_paths: [".codex/**", ".claude/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "scripts/install_gt_path_shim.py", "platform_tests/scripts/test_install_gt_path_shim.py", "scripts/repair_codex_dotdir_acl.ps1", "platform_tests/scripts/test_repair_codex_dotdir_acl.py"]

## Revision Claim

Prime Builder accepts the Loyal Opposition `NO-GO` at `-008` and rechecked the live WI-5002 execution boundary in this dispatcher-launched Codex session. The thread remains blocked by the same owner-side `.codex` DACL authority condition:

- `.codex` still has two risky explicit Deny ACEs.
- the active Codex sandbox identity `DESKTOP-G6Q5ANI\CodexSandboxOffline` still lacks a Modify allow entry on `.codex`;
- `scripts/repair_codex_dotdir_acl.ps1 -Mode Apply -Json` cannot persist the approved ACL repair because `SetAccessControl` raises `Attempted to perform an unauthorized operation.`;
- `scripts/verify_codex_dispatch.py --no-require-executable --json` still reports `dispatchable: false`;
- the dispatcher-prompt-required project-local role-reader executable `groundtruth-kb\.venv\Scripts\gt.exe` is still absent.

No source, test, helper, credential, deployment, sandbox configuration, or successful ACL change was made in this dispatch. This revision records the blocker and stops because this auto-dispatched worker cannot interactively request the required owner-side DACL decision or authority change.

## Requirement Sufficiency

Existing requirements remain sufficient for the original WI-5002 implementation. The blocker is not a missing product or governance requirement; it is an execution-environment authority boundary preventing Codex from applying the already-approved `.codex` ACL repair and completing the helper-write acceptance criteria.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-selected Prime Builder work must complete without manual intervention when the configured execution boundary permits it; here the readiness verifier correctly fails closed.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the work must not route `.codex/**` writes through another harness or direct harness fallback.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook/sandbox gaps must be handled mechanically and audibly; the ACL repair and verifier provide structured fail-closed evidence.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper parity remains unverified while Codex cannot write its own `.codex` helper copy.
- `ADR-CROSS-HARNESS-PARITY-001` - `.claude`, `.codex`, and `.cursor` helper surfaces must not claim parity until byte-identical helper state is freshly reachable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all evidence and bridge artifacts remain in `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this blocker record preserves the numbered bridge chain and latest status authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - linked governing surfaces and target paths remain explicit.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths remain explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report does not request `VERIFIED` because the spec-derived acceptance checks still fail.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical work item for this Codex hidden helper write blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the repeated blocker is preserved as durable bridge evidence rather than transient chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - accepted/rejected routes and the current blocker remain explicit in artifact form.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the latest NO-GO triggered this revised blocker record.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing and prohibited direct harness fallback.
- `DELIB-20260703-WI5002-DOTDIR-SANDBOX-ACL-IMPLEMENTATION-APPROVED` - owner implementation approval carried by the WI-5002 chain.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md` - Loyal Opposition GO authorizing the bounded ACL/helper/shim repair.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md` - initial implementation report.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-004.md` - NO-GO identifying live runtime contradiction and unresolved-SID removal risk.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-005.md` - revised report with unresolved-SID source/test correction and blocker evidence.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-006.md` - NO-GO accepting the code correction but rejecting unachieved WI-5002 goal.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-007.md` - Prime Builder blocker record from the previous headless dispatch.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-008.md` - latest NO-GO confirming the thread remains owner-side blocked and warning that further headless dispatches will not progress until the DACL authority condition changes.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` through `-007.md` - prior add-dir route and rejection of identical add-dir-only retries.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md` through `-010.md` - repeated `.codex` write-boundary evidence that motivated WI-5002.

## Owner Decisions / Input

- Carried forward: `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded implementation work to restore stable unattended bridge processing.
- Carried forward: `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes the WI-5002 repair scope while forbidding direct harness fallback, broad sandbox bypass, credential mutation, production deployment, and retired poller restoration.
- Current blocker for later interactive handling: the live `.codex` DACL is still protected in a way this Codex sandbox cannot change. Practical routes remain: owner-side removal of the two risky `.codex` Deny ACEs, owner-side grant of sufficient `.codex/**` authority to the active Codex sandbox identity, or an explicit owner/governance decision to revise WI-5002 scope and accept `.codex/**` write denial as a permanent Codex limitation.

This headless worker cannot ask for that decision interactively, so it records the blocker here and stops.

## Findings Addressed

### `-008` Finding: Blocker Record Is Honest and Appropriate

Accepted and preserved. This revision reran the live checks after `-008`, attempted the approved `Apply` path, and found the same DACL authority failure. It continues to avoid a false success claim.

### `-008` Finding: No New Implementation Was Attempted

Partially updated. This dispatch attempted only the already-approved ACL repair command after obtaining a valid implementation-start packet. The command failed before changing the DACL. No source, test, helper, credential, deployment, sandbox configuration, or successful ACL change resulted.

### `-008` Finding: No Forbidden Practices

Still satisfied. This dispatch did not use `danger-full-access`, did not add `--dangerously-bypass-approvals-and-sandbox`, did not route `.codex/**` writes through another harness, did not mutate credentials, did not restore retired poller assets, and did not move evidence outside `E:\GT-KB`.

### `-008` Finding: Blocker Routes Are Clearly Enumerated

Still satisfied. The same owner-side routes remain the only practical routes. Re-dispatching Codex headless work on this thread without one of those changes will continue to rediscover the same blocker.

## Scope Changes

None. The approved source/test/helper scope remains unchanged. No new implementation target is requested, and no acceptance criterion is claimed complete.

## Commands Run

```text
Get-Content harness-state\harness-identities.json
groundtruth-kb\.venv\Scripts\gt.exe harness roles
groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.harness_projection import read_roles; ..."
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi5002-codex-dotdir-sandbox-acl-correction --format json --preview-lines 260
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py status gtkb-wi5002-codex-dotdir-sandbox-acl-correction
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --no-require-executable --json
Test-Path -LiteralPath groundtruth-kb\.venv\Scripts\gt.exe
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Apply -Json
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\revise_bridge.py plan gtkb-wi5002-codex-dotdir-sandbox-acl-correction
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\revise_bridge.py scaffold gtkb-wi5002-codex-dotdir-sandbox-acl-correction
```

## Observed Results

- Harness identity: `harness-state/harness-identities.json` maps Codex to durable harness ID `A`.
- Prescribed role reader executable: `groundtruth-kb\.venv\Scripts\gt.exe harness roles` failed because `gt.exe` is absent from the project venv; `Test-Path` returned `False`.
- Fallback role reader evidence: the canonical `groundtruth_kb.harness_projection.read_roles` reader, executed through `groundtruth-kb\.venv\Scripts\python.exe`, returned harness `A` with role `prime-builder`.
- Live bridge state: Prime scan listed `gtkb-wi5002-codex-dotdir-sandbox-acl-correction` as latest `NO-GO`; show-thread resolved latest path `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-008.md`.
- Work-intent claim: active claim rowid `29821`, session `2026-07-04T04-09-35Z-prime-builder-A-0c4b1b`, latest bridge status `NO-GO`, expires `2026-07-04T04:19:35Z`.
- Implementation-start packet: issued successfully from the original GO; packet hash `sha256:810a150d80d8bd8cb751c2ccaf0ba30ff81ae9e3ee2a7ea003ab17d90b7c1c3d`; latest status recorded as `NO-GO`; GO file `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md`.
- ACL check: exit 1; `needs_repair: true`; `risky_deny_count: 2`; risky Deny identity `S-1-5-21-2908765920-875073000-2352713335-4168283502`; `sandbox_group.allow_present: true`; `current_identity.allow_present: false` for `DESKTOP-G6Q5ANI\CodexSandboxOffline`.
- Dispatch verifier: exit 1; `codex_dotdir_acl_ok: false`; `static_ok: false`; `dispatchable: false`; headless argv still includes `--sandbox workspace-write` and `--add-dir .codex`; forbidden flags remain absent.
- ACL apply attempt: exit 1; `needs_repair: true`; `repaired: false`; Deny removal failed with `Exception calling "SetAccessControl" with "2" argument(s): "Attempted to perform an unauthorized operation."`; current identity allow update failed with the same unauthorized operation.
- Direct `.codex` write probe: not executed because the Codex command policy rejected the probe command before shell execution; this revision therefore relies on the ACL check, failed ACL apply, and dispatch verifier evidence above.

## Pre-Filing Preflight Subsection

Candidate content preflights are required before live filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5002-codex-dotdir-sandbox-acl-correction-009.md --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5002-codex-dotdir-sandbox-acl-correction-009.md
```

Observed pre-filing result:

- Applicability preflight: exit 0; `preflight_passed: true`; `packet_hash: sha256:553d264b39159cef332beb15b2faa78bf0c1823eb70032ea4e3ce0cb8c198891`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit 0; clauses evaluated `5`; must-apply clauses `4`; evidence gaps in must-apply clauses `0`; blocking gaps `0`.
- Helper file mode will rerun both preflights against the candidate content before writing `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-009.md`.

## Specification-Derived Verification Plan

| Spec / governing surface | Evidence in this dispatch |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `scripts\verify_codex_dispatch.py --no-require-executable --json` returned `dispatchable: false`, correctly failing closed while `.codex` remains blocked. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | No alternate harness was used to write `.codex/**`; no direct harness fallback was attempted. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json` and `-Mode Apply -Json` returned structured ACL failure evidence. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Helper parity is not claimed because `.codex` remains unwritable by Codex. |
| `ADR-CROSS-HARNESS-PARITY-001` | No byte-identical helper hash claim is made. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All commands and this bridge artifact remain under `E:\GT-KB`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest status was confirmed as `NO-GO`; Prime Builder is filing the next numbered `REVISED` artifact only. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This artifact does not request `VERIFIED`; required acceptance checks remain failing. |

## Acceptance Criteria Status

- [ ] Codex can write `.codex/skills/verify/helpers/write_verdict.py` from its own approved route. Still blocked by `.codex` DACL authority.
- [x] ACL failure is mechanically detected and reported as structured evidence.
- [x] Codex dispatch readiness fails closed while `.codex` ACL repair remains needed.
- [ ] The project-local `groundtruth-kb\.venv\Scripts\gt.exe harness roles` command exists. Still absent.
- [ ] `.claude`, `.codex`, and `.cursor` verify helper parity can be freshly completed by Codex. Still blocked because `.codex` is not writable by Codex.
- [ ] Full WI-5002 pytest, ruff, format, helper parity, and live write checks pass. Not rerun because the approved ACL apply path still fails at DACL authority.

## Risk And Rollback

Primary risk is dispatch churn: further headless Codex dispatches on this same latest `NO-GO` will keep consuming worker cycles and rediscovering the same DACL authority blocker until owner-side ACL authority or WI-5002 scope changes.

Rollback is limited to bridge state. Bridge artifacts are append-only and must not be deleted. No source, test, helper, credential, deployment, sandbox configuration, or successful ACL change was made by this dispatch.

--- 

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
