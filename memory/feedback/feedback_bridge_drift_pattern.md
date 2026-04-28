---
name: Bridge/poller drift root-cause pattern
description: Rule for recognizing and restoring the OS-poller bridge when it has drifted from the working baseline. When owner says "bridge is garbage/drifted", the fix is a surgical revert of uncommitted drift, not a rewrite.
type: feedback
originSessionId: 955981a3-5bb7-49a4-ae2e-82cb564169c9
---
**Rule:** When the OS-poller bridge stops exchanging Prime/LO messages productively, the root cause is almost always uncommitted drift overlaying the last clean git commit. Fix by reverting, not rewriting.

**Why:** S304 incident (2026-04-23). Over ~6 days, three drift layers accumulated as uncommitted changes:
1. `Test-BridgeScanRoleAuthority` added to `bridge-scan-common.ps1` — made `.claude/rules/operating-role.md` a single-value mutex between Claude and Codex pollers. Whichever role the file named, the *other* poller paused.
2. `.claude/hooks/workstream-focus.py` (new, untracked) + matching `settings.json` hook registration — blocked capped-spawn children from reading `memory/work_list.md` and `operating-role.md` under "Application Focus," guaranteeing no-op spawns and a 33-FIRE-ACK loop on retired threads.
3. Non-canonical `PAUSED:`/`RETIRED` status sentinels were appended to `INDEX.md` and scanner helpers without being recognized by the scanner regex.

None of these were committed. `git checkout HEAD -- <file>` reverted the tracked drift; `rm` on the two untracked files removed the rest; `run-bridge-scan-noconsole.ps1 -NoExec` regenerated the wrappers from clean sources. Total restoration time ~15 minutes.

**How to apply:**
- **Diagnose first.** Look at `independent-progress-assessments/bridge-automation/logs/*-scan-status.json`. A `state: paused` with `ROLE-AUTHORITY-BLOCKED` message is the classic mutex symptom. A `state: completed, num_turns=N, api_ms=X0000` with no INDEX write is the workstream-focus-blocked spawn symptom.
- **Find the drift.** `git status` on `.claude/rules/` `.claude/hooks/` `.claude/settings.json` and `independent-progress-assessments/bridge-automation/`. Uncommitted modifications to tracked files + untracked `workstream-focus.py` / `operating-role.md` = drift signature.
- **Surgical revert, not rewrite.** `git checkout HEAD -- <drifted-tracked-files>` + `rm` on untracked drift + regenerate generated wrappers. Do NOT attempt to "improve" the bridge — the owner explicitly said the drift was garbage; the baseline is `b5f2559e` (Fri Apr 17).
- **Preserve legitimate in-flight bridges.** INDEX.md cleanup is surgical: remove retired/paused Document blocks + FIRE-ACK cruft, keep active GO/NO-GO/REVISED threads for work that's actually in flight.
- **Back up drift before deleting** (e.g., `.claude/_drift-backup-YYYY-MM-DD-S{N}/`) so the owner can inspect what was removed.
- **Verify by watching a full scan cycle.** Within 3-5 minutes of restoration, one side should write a productive response to INDEX (new status line from Codex review, or Claude capped-spawn filing REVISED). If both pollers show `state: completed` with substantive `num_turns > 2` and INDEX grows, the bridge is alive.
