REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-02T21-16-35Z-prime-builder-A-6c4c7c
author_model: GPT-5
author_model_version: Codex
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never; sandbox=workspace-write; cwd=E:\GT-KB
author_metadata_source: explicit-runtime-envelope
# Implementation Proposal REVISED - Codex SessionStart Timeout Alignment Execution Context

bridge_kind: prime_proposal
Document: gtkb-wi4929-codex-sessionstart-timeout-alignment
Version: 009 (REVISED; execution-context blocker disposition)
Date: 2026-07-02 UTC
Responds to: bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-008.md
Supersedes technical implementation scope from: bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-005.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4929

target_paths: [".codex/gtkb-hooks/run_py_no_window.py", "platform_tests/scripts/test_codex_no_window_timeout_alignment.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED entry responds to the `-008` NO-GO. The approved technical scope remains unchanged: modify `.codex/gtkb-hooks/run_py_no_window.py` so direct `session_start_dispatch.py` children receive startup-service headroom while ordinary children keep the existing short default, and add focused regression coverage in `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`.

This auto-dispatched Codex session did not complete the source implementation. The mandatory implementation-start packet succeeded, but the approved edit path remained unavailable to this Codex execution context: `apply_patch` rejected the source/test patch with `patch rejected: writing outside of the project; rejected by user approval settings`. No source or test target was changed.

The correction requested by this revision is execution-context routing, not a technical design change: continue under the existing GO at `-006` only in a Prime Builder context that can write the authorized `.codex/gtkb-hooks/` target, or after an owner-approved ACL/security posture change removes the Codex sandbox write-deny condition.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-4929`, `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, the approved REVISED proposal at `-005`, the GO at `-006`, and the NO-GO guidance at `-008` provide enough requirement surface. No new functional requirement is needed before implementation; only the execution context must be capable of writing the already-authorized target paths.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`

This revision creates only the append-only bridge audit entry for the existing in-root thread.

## Specification Links

- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - governs the startup relay behavior this defect breaks.
- `GOV-RELIABILITY-FAST-LANE-001` - governs small defect/reliability fixes routed through `PROJECT-GTKB-RELIABILITY-FIXES` and the standing PAUTH.
- `PROJECT-GTKB-RELIABILITY-FIXES` - active reliability fast-lane project containing `WI-4929`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs project-scoped implementation authorization.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - constrains the PAUTH envelope and implementation-start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable artifact handling when a defect becomes governed work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision evidence is cited through the standing fast-lane decision and any ACL/security posture change must use the owner-decision channel.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform hook work inside the GT-KB root and outside adopter application scope.
- `GOV-STANDING-BACKLOG-001` - keeps the work item visible in the durable backlog/project system.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - constrains Codex hook behavior and parity fallback handling.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - supports durable artifact handling for this revision and the planned regression test.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - applies to the new test artifact and bridge revision lifecycle.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing owner decision establishing the reliability fast-lane and standing PAUTH for small defect fixes.
- `bridge/gtkb-reliability-fast-lane-006.md` - VERIFIED fast-lane mechanism and covers-by-membership behavior.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-005.md` - approved technical and authorization-chain proposal, unchanged by this revision.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-006.md` - GO authorizing implementation under the corrected authorization chain.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-007.md` - Codex blocker report documenting write denial against `.codex/gtkb-hooks/run_py_no_window.py`.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-008.md` - LO NO-GO confirming the blocker and recommending execution by a Prime Builder context not subject to the Codex sandbox deny ACE, or owner ACL remediation.

## Owner Decisions / Input

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` remains the standing owner decision for small defect/reliability fixes routed through `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` remains active and authorized this session's implementation-start packet for `WI-4929`.
- No interactive owner input was requested in this headless auto-dispatch session.
- If the selected path is ACL/security posture remediation for `CodexSandboxUsers`, that is an owner-controlled environment/security decision and cannot be collected by this headless worker. The non-owner alternative is rerouting implementation to a Prime Builder session identity that can write the approved target file.

## Findings Addressed

### P0 ACL Write-Deny Confirmed

Response: Accepted. This Codex session did not try to bypass the write-deny posture. It verified the implementation-start packet and then stopped after the approved `apply_patch` edit path was rejected for the authorized source/test patch. The technical fix remains pending.

### P1 `apply_patch` Also Blocked

Response: Accepted. `apply_patch` remains unavailable for `.codex/gtkb-hooks/run_py_no_window.py` in this auto-dispatched Codex context. Since Codex cannot interactively ask the owner or switch execution identity, this revision records that the implementation must be rerouted or the ACL/security posture must be changed outside this worker.

### P3 Transient Test File Created and Removed

Response: Confirmed unchanged. This session did not create the regression test file because the paired source edit path failed first. Target-specific git status remains free of WI-4929 source/test changes.

## Scope Changes

No technical scope change.

The only changed instruction is execution-context routing: do not re-dispatch this same source implementation to Codex headless while `.codex/gtkb-hooks/run_py_no_window.py` remains unwritable through the approved Codex edit path. Use a Prime Builder context with effective write access, or perform owner-approved ACL remediation before retrying Codex headless implementation.

## Authorization Evidence

Implementation-start authorization succeeded before any protected source/test mutation:

```json
{
  "bridge_id": "gtkb-wi4929-codex-sessionstart-timeout-alignment",
  "go_file": "bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-006.md",
  "latest_status": "NO-GO",
  "project_authorization": {
    "id": "PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING",
    "project_id": "PROJECT-GTKB-RELIABILITY-FIXES",
    "status": "active",
    "work_item_id": "WI-4929"
  },
  "target_path_globs": [
    ".codex/gtkb-hooks/run_py_no_window.py",
    "platform_tests/scripts/test_codex_no_window_timeout_alignment.py"
  ]
}
```

Work-intent claim succeeded for this dispatched session:

```json
{
  "acting_role": "prime-builder",
  "claim_kind": "draft",
  "session_id": "2026-07-02T21-16-35Z-prime-builder-A-6c4c7c",
  "thread_slug": "gtkb-wi4929-codex-sessionstart-timeout-alignment",
  "project_id": "PROJECT-GTKB-RELIABILITY-FIXES"
}
```

## Execution Evidence

Commands/evidence gathered in this session:

- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness roles` - fallback package CLI invocation because `groundtruth-kb\.venv\Scripts\gt.exe` is absent in this venv; output confirms Codex harness `A` has role `prime-builder`.
- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json` - live scan showed this thread latest `NO-GO` at `-008`.
- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4929-codex-sessionstart-timeout-alignment --format json` - loaded the full version chain `-001` through `-008`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment` - authorized packet emitted, using GO `-006` despite latest `NO-GO` continuation status.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4929-codex-sessionstart-timeout-alignment` - work-intent claim acquired for this dispatch session.
- `apply_patch` against `.codex/gtkb-hooks/run_py_no_window.py` and `platform_tests/scripts/test_codex_no_window_timeout_alignment.py` - rejected before mutation with `patch rejected: writing outside of the project; rejected by user approval settings`.
- `Get-Acl .codex\gtkb-hooks\run_py_no_window.py` - explicit deny ACEs remain present before allow ACEs, consistent with the `-007` blocker evidence.

## Specification-Derived Verification Plan

| Spec | Required verification after implementation |
| --- | --- |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Focused test proving direct `session_start_dispatch.py` children get startup-service headroom. |
| `GOV-RELIABILITY-FAST-LANE-001` | Confirm implementation remains a small defect fix in the approved two-file scope. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment` before protected mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Packet must show active `PROJECT-GTKB-RELIABILITY-FIXES`, standing PAUTH, `WI-4929`, and the two approved target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File the next implementation report through the governed bridge writer after source/test work completes. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Carry forward project authorization, project, work item, and target path metadata. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused Codex hook runtime containment coverage proving ordinary child containment remains unchanged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry forward spec-to-test mapping and executed command evidence. |

Required commands after a successful source/test implementation:

```text
groundtruth-kb\.venv\Scripts\ruff.exe check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_no_window_timeout_alignment.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_no_window_timeout_alignment.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_no_window_timeout_alignment.py -q --tb=short
```

## Pre-Filing Preflight Subsection

Candidate preflights are run by the governed `revise_bridge.py file` helper before live filing this completed revision content. Successful filing requires both candidate preflights to pass against this content with no missing required specifications and no blocking clause gaps.

## Acceptance Criteria

- Latest live bridge state becomes `REVISED` at `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-009.md`.
- Technical implementation remains unchanged from `-005` and `-006`.
- Codex headless write-path blockage is recorded without bypassing the current sandbox/security boundary.
- Source/test target paths remain unmodified by this blocked Codex session.
- Loyal Opposition can decide whether this execution-context revision is sufficient to reroute the implementation or whether a different bridge state is needed.

## Risk And Rollback

Risk to source behavior is low because this session did not change source or test files. The active risk is workflow churn: repeated Codex headless dispatch will continue to fail on the same approved source edit path unless the dispatcher routes the work to a write-capable Prime Builder context or the owner changes the relevant ACL/security posture.

Rollback is not applicable to source/test files. Bridge audit files are append-only and must not be deleted.

## Files Changed In This Session

- No source files changed.
- No test files changed.
- This revision records the latest blocker disposition as an append-only bridge artifact.

## Recommended Commit Type

`chore`

