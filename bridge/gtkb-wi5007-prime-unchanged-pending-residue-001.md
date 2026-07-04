NEW

# Defect-Fix Proposal - Clear Prime Fan-Out Unchanged Pending Residue So PB NO-GO Work Can Resume

bridge_kind: prime_proposal
Document: gtkb-wi5007-prime-unchanged-pending-residue
Version: 001
Date: 2026-07-04 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5
author_model_version: codex-desktop-2026-07-04
author_model_configuration: Codex Desktop interactive; owner-directed headless bridge stability goal; PB headless target remains GPT-5.5 with Extra High reasoning

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5007-UNCHANGED-PENDING-RESIDUE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5007

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

## Claim

The dispatcher has a Prime Builder duplicate-suppression defect: when PB candidate signatures are unchanged, the runtime records `last_result="unchanged"` but leaves `pending_count > 0`. Health then reports a WARN even though there is no live inflight worker and no dispatchable changed work for that recipient. This residue can make normal PB NO-GO/GO queue recovery look stuck after resets and verified finalizations.

The fix should make unchanged duplicate suppression terminal and benign for that tick: no selected work, no pending residue, no health warning, and no direct harness-to-harness fallback.

## Defect / Reproduction

Observed during the WI-4983 dispatcher recovery sequence:

- `gt bridge dispatch reset --soft --json` cleared stale recipients, stale run records, and lease locks; immediate dispatcher health returned PASS.
- On the next daemon tick, `gt bridge dispatch health --json` returned WARN: `dispatch runtime warning: prime-builder:A last_result=unchanged with pending_count=1`.
- `gt bridge dispatch report --json` showed `prime-builder:A` with `last_result="unchanged"`, `pending_count=1`, `selected_count=0`, and `live_inflight_dispatch_count=0`.
- The same report showed fan-out duplicate suppression for PB documents such as `gtkb-wi5002-codex-dotdir-sandbox-acl-correction` and `gtkb-wi4975-claimed-path-subpath-overmatch`, where per-document last dispatched signatures matched the candidate signatures.
- Code inspection found the same residue pattern in both live paths:
  - `scripts/dispatcher_runtime.py` records `recipient_state["pending_count"] = len(dispatched_filtered)` before the unchanged branch and then records `last_result="unchanged"` without clearing that pending count.
  - `scripts/gtkb_dispatcher_daemon.py` records `pending_count=len(selected)` in the fan-out unchanged branch while also setting `selected_count=0`.

This is not a supervisor failure. The Windows scheduled task supervisor and daemon are alive; the WARN is runtime state semantics.

## Requirement Sufficiency

Existing requirements sufficient. The owner explicitly directed the active goal to make headless bridge dispatch stable with Claude Code and Ollama as active LO targets and Codex as active PB, and separately prohibited direct harness-to-harness launches as standby behavior. WI-5007 and its project authorization narrow that goal to this reproducible dispatcher health/runtime defect.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`.

## Bridge File Chain Evidence

This proposal is filed as the append-only numbered bridge file `bridge/gtkb-wi5007-prime-unchanged-pending-residue-001.md`. It does not delete, rewrite, or supersede any prior versioned bridge files.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - The dispatcher must provide reliable centralized bridge dispatch state and health semantics. Duplicate-suppressed work must not masquerade as pending work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - The change preserves role boundaries and uses bridge authorization rather than direct harness-to-harness launch or manual worker spawning.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the implementation scope to governing specs, WI-5007, and the active PAUTH.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal includes the required machine-readable Project Authorization, Project, and Work Item headers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must include spec-derived tests proving benign unchanged suppression and continued dispatchability for changed PB work.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - Owner-directed operating goal for stable headless dispatch with Codex as PB and Claude/Ollama/Antigravity as LO targets; also used as the owner-decision anchor for the WI-5007 project authorization.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5007-UNCHANGED-PENDING-RESIDUE` authorizes WI-5007 under `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`.
- Owner prohibited direct harness-to-harness interaction; this proposal keeps recovery inside dispatcher and bridge mechanics.

## Proposed Scope

1. In `scripts/dispatcher_runtime.py`, correct the unchanged duplicate-suppression branch so it does not leave `pending_count` or other health-warning residue after selecting zero dispatchable changed items.
2. In `scripts/gtkb_dispatcher_daemon.py`, apply the same semantics to the live fan-out path: unchanged duplicate suppression should record zero selected and zero pending actionable work for that recipient.
3. Preserve normal behavior for genuinely new or changed PB candidates: those candidates must still dispatch or report a real launch/failure state.
4. Add focused regression coverage for both runtime and daemon paths.
5. Do not change dispatcher target eligibility, harness roles, model pins, direct launcher topology, or quiesce policy in this WI.

## Out Of Scope

- Directly starting Claude Code, Codex, Ollama, Antigravity, Cursor, or OpenRouter workers outside the dispatcher.
- Replacing the dispatcher daemon or restoring retired smart/OS poller behavior.
- Changing model pins, role assignments, or harness eligibility.
- Broad reset behavior rewrites except where a narrow assertion is needed to prove unchanged suppression no longer strands PB work.

## Specification-Derived Verification Plan

| Spec / Requirement | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - duplicate-suppressed work is not actionable pending work | Add a runtime test where PB selected documents match `last_dispatched_signatures_by_document`; assert `last_result="unchanged"`, `selected_count=0`, `pending_count=0`, no WARN-class health finding, and no worker launch. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - changed PB work remains dispatchable | Add or extend coverage where one candidate signature changes; assert the changed candidate remains selected/launched rather than being suppressed by stale per-document state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` - no direct harness-to-harness fallback | Test or inspect that the fix only changes dispatcher state accounting and does not introduce direct harness launch paths outside existing dispatcher launcher calls. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must name the focused tests and their passing output, plus any focused ruff checks for edited files. |

Expected focused commands:

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

## Acceptance Criteria

- Given a Prime recipient with unchanged per-document dispatch signatures and no live worker, a dispatcher tick records benign duplicate suppression with `pending_count=0` and `selected_count=0`.
- Dispatcher health remains PASS for that benign unchanged state.
- Genuinely new or changed PB work is still dispatched according to existing caps and target selection.
- The change is covered in both runtime and daemon regression tests.
- No direct harness-to-harness interaction is introduced.

## Risks / Rollback

Risk: clearing `pending_count` too broadly could hide genuinely stuck work. Mitigation: tests must distinguish unchanged duplicate suppression from changed dispatchable candidates.

Risk: runtime and daemon paths could diverge. Mitigation: update both paths and add tests for both.

Rollback: revert the narrow state-accounting changes and tests. This restores the current WARN behavior but does not affect bridge files, model pins, or harness eligibility.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

## Recommended Commit Type

`fix`
