---
name: Poller autonomy — leave working infrastructure alone
description: If the Windows Task Scheduler bridge pollers are running, do not disable/stop/restart them; mitigate race concerns with other means.
type: feedback
originSessionId: 1ace762f-dc93-4dcb-8dcf-43b31ebdb886
---
**Rule:** When the OS-level bridge pollers (`AgentRedFileBridgeIndexScan-Claude`,
`AgentRedFileBridgeIndexScan-Codex`) are confirmed working, do not disable or
stop them to avoid concurrency concerns during interactive work. Mitigate
race risk with faster actions, not infrastructure shutdown.

**Why:** Owner directive (2026-04-13, S289): "If the poller is working, leave
it alone." The pollers are the project's steady-state automation layer —
they run every 3 minutes via Windows Task Scheduler, log to
`independent-progress-assessments/bridge-automation/logs/`, and invoke
`claude.exe --dangerously-skip-permissions` on unactioned GO/NO-GO entries.
They survive session restarts, they're the reason Phase 4 reviews complete
while Prime Builder is offline, and treating them as throwaway during
interactive work risks cascading trust issues with the whole automation
stack. Mike has also flagged general "desktop automations silently fail"
concerns in `project_codex_automation_failure.md`, so any disable/enable
cycle is an opportunity for that silent-failure mode to bite.

**How to apply:**
- When doing interactive bridge work (revising a proposal, writing a
  post-impl report, updating INDEX.md) while the pollers are live:
  - Do NOT propose `Disable-ScheduledTask` as a safety measure — the owner
    will reject it.
  - Work fast: flip the bridge entry from NO-GO to REVISED (or NEW to
    actioned status) as quickly as possible. Subsequent poller scans will
    see the new status and skip action.
  - Use atomic writes (single `Write` or targeted `Edit`) for INDEX.md
    changes rather than multi-step edits, to minimize the window where
    the index is in a partial state.
  - Check `codex-file-bridge-scan.lock` and `claude-file-bridge-scan.lock`
    state before editing INDEX.md — if HELD, a scan is mid-flight and
    the headless worker may be reading the index right now.
- Phase 4 S289 evidence confirms this works: after writing -007 and
  flipping INDEX.md to REVISED, the Prime Builder poller stopped firing
  on gtkb-phase4-implementation (its scan logic only triggers on GO/NO-GO
  at latest status).
- If the poller actually breaks (log stops, scheduled task stuck, lockfile
  held for > 60 minutes without valid reason), that IS a reason to
  investigate/fix — but always check with owner before disabling.
