NEW

# gtkb-wi4896-dispatcher-console-window-suppression - Dispatcher Windows no-console background launch fix

bridge_kind: prime_proposal
Document: gtkb-wi4896-dispatcher-console-window-suppression
Version: 001
Author: Prime Builder Codex
Date: 2026-06-27T17:50:00Z

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c3-be81-7771-8200-e81c58e3ae1e
author_model: GPT-5
author_model_version: 2026-06-27
author_model_configuration: Codex desktop; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/ensure_dispatcher_daemon.py", ".codex/gtkb-hooks/session_stop_dispatch.py", "groundtruth-kb/src/groundtruth_kb/bridge/launcher.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_codex_hook_parity.py", "groundtruth-kb/tests/test_bridge_launcher.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Mike reported a visible Windows console popping up periodically after the recent dispatcher updates. Live process inspection showed GT-KB-related console-backed background loops, including a Cursor-launched Loyal Opposition auto-process PowerShell temp script, two Prime Builder auto-process Python loops, and an old `.tmp/daemon_kill_watch.ps1` trace watcher from WI-4893. Source review found dispatcher-owned launch surfaces that detach or hide the long-lived child but do not consistently apply Windows no-window creation flags to the launcher itself.

This proposal fixes the dispatcher-owned source gaps without changing topology, eligibility, dispatch selection, or scheduled-task registration semantics. The implementation will make daemon start/ensure child processes use `CREATE_NO_WINDOW` and non-inherited standard handles, make the Codex stop-hook background wrap-up spawn no-window on Windows, and make the bridge launcher's short PowerShell wrapper run with no window while it starts the already-hidden worker.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires this protected-source change to be proposed, reviewed, GO-approved, implemented under a matching work-intent claim, and verified through the bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this implementation proposal to cite the governing requirements rather than relying only on conversational intent.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the machine-readable Project Authorization, Project, and Work Item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the post-implementation report and Loyal Opposition verification to map tests back to these requirements.
- `GOV-STANDING-BACKLOG-001` - Supports capture of this owner-reported reliability defect as WI-4896 without treating capture alone as implementation approval.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Dispatch is a GT-KB-owned black-box service; launcher hygiene belongs in dispatcher-owned source rather than harness-specific ad hoc loops.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - The dispatcher composes and records headless dispatch activity; background spawn surfaces must preserve that service behavior without surfacing UI.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher wake paths must run non-interactively with no visible console window; this fix applies the same no-console discipline to adjacent daemon and hook background launch paths.
- `ADR-CROSS-HARNESS-PARITY-001` - Requires harness-surface changes to state their parity posture explicitly.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Enforces a non-empty cross-harness disposition section when `.codex/gtkb-hooks/**` is in target scope.

## Prior Deliberations

- `DELIB-20266297` - Owner directive and authorization for WI-4896 console-window suppression.
- `DELIB-20266276` - Daemon resilience scope-lock; context for the recent dispatcher daemon/supervisor updates that made Windows background launch hygiene operationally important.
- `DELIB-20266291` - Claude token-outage topology change; recent dispatcher topology context, but this proposal does not change topology.
- Related backlog precedent: `WI-4171` captured an older no-console bridge-poller advisory. This proposal is a fresh, bounded fix for current daemon/hook launch surfaces and does not reuse that stale advisory bucket.

## Owner Decisions / Input

Owner directive captured in `DELIB-20266297`: Mike asked Codex on 2026-06-27 to investigate and fix a periodic visible Windows console likely related to dispatcher updates. The bounded implementation authorization is `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION`.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` provides the Windows no-console constraint, while `ADR-DISPATCHER-ARCHITECTURE-001` and `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` provide the dispatcher ownership and headless-service context. No new or revised requirement is needed before implementing this narrow launcher hygiene fix.

## Cross-Harness Disposition

- Shared dispatcher code: `groundtruth-kb/src/groundtruth_kb/cli.py`, `scripts/ensure_dispatcher_daemon.py`, and `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py` apply to all harnesses that use the GT-KB dispatcher daemon or bridge launcher on Windows. No per-harness fork is needed for these shared launch paths.
- Codex harness A: `.codex/gtkb-hooks/session_stop_dispatch.py` is the only repo-managed Codex stop-hook background-spawn wrapper in scope. It will gain Windows no-window creation flags so the background wrap-up/self-initialization spawn does not surface a console.
- Claude Code harness B: no `.claude/gtkb-hooks/session_stop_dispatch.py` equivalent exists in this checkout, and Claude Code is currently suspended for token outage under WI-4895. No Claude hook file is changed by this proposal.
- Cursor harness E: no `.cursor/gtkb-hooks/session_stop_dispatch.py` equivalent exists in this checkout. The live Cursor-launched temp PowerShell auto-process observed during diagnosis is harness-scheduled runtime state outside repo source; this proposal fixes repo-owned dispatcher surfaces and will stop stale GT-KB watcher processes found during diagnosis.
- Ollama D, OpenRouter F, and retired Antigravity C: no equivalent repo-managed stop-hook wrapper exists in the target tree. Shared dispatcher launcher fixes cover any use of the daemon/bridge launcher paths.

## Spec-Derived Verification Plan

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`: Add/extend tests proving Windows background launcher surfaces set `CREATE_NO_WINDOW` or use the already-approved `pythonw.exe`/hidden scheduled-task path. Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_codex_hook_parity.py groundtruth-kb/tests/test_bridge_launcher.py -q --tb=short
```

- `ADR-DISPATCHER-ARCHITECTURE-001` and `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: Verify the change is launcher-only and preserves dispatcher selection/topology semantics by running the focused dispatcher daemon and launcher tests above plus read-only dispatcher status checks:

```text
gt bridge dispatch status --json
gt bridge dispatch health --json
```

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: Before filing and before implementation, run the proposal preflights and confirm no blocking gaps:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4896-dispatcher-console-window-suppression
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4896-dispatcher-console-window-suppression
```

## Risk / Rollback

Risk is low and localized to process launch behavior on Windows. Adding `CREATE_NO_WINDOW` and non-inherited standard handles could hide output that was previously inherited, but these are background service/hook paths whose output is already either logged or intentionally fire-and-forget. The bridge launcher continues to capture the PowerShell wrapper output needed to obtain the child PID.

Rollback is a single commit revert restoring the prior launcher flags. No topology, harness registry, dispatcher rules, credentials, or scheduled-task definitions are changed by this proposal.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4896-dispatcher-console-window-suppression`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
