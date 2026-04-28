---
name: Bridge poller reliability + freshness indicator — the correct S292 fix
description: Windows Task Scheduler runs the bridge scan reliably every 3 min; a UserPromptSubmit hook surfaces scan-status freshness in every response so silent failures are visible
type: feedback
originSessionId: 12953966-5fb1-486d-abf4-94fa82fdb93a
---
The owner's requirement, stated explicitly in S292:

1. **Must: the 3-minute bridge scan cycle runs reliably.**
2. **Should: a visible indicator that the cycle is working**, because "poller
   failed and I did not know that it had failed, because there was no visible
   indication that it was working."

**How these are met (S292 implementation):**

### Reliability — already in place (Windows Task Scheduler)

Two Windows scheduled tasks run the pollers every 3 minutes and are confirmed
reliable:

- `AgentRedFileBridgeIndexScan-Claude` → runs
  `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
- `AgentRedFileBridgeIndexScan-Codex` → runs
  `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1`

Each PS1 reads `bridge/INDEX.md`, checks for NEW/REVISED entries, and on
detection spawns a headless `claude.exe -p` (or `codex exec`) to action the
entry. Output goes to `independent-progress-assessments/bridge-automation/logs/`
as `claude-scan.log` / `scan.log` plus structured `claude-scan-status.json` /
`codex-scan-status.json`.

The spawned `claude.exe -p` sessions run autonomously and complete work without
owner attention. That is how Phase 4B.5a, 4B.5b, the SPA remediation batches,
and many others have been landing while Mike was away.

**Why not CronCreate:** CronCreate has an in-memory scheduler that silently
drops jobs during long sessions (documented in CLAUDE.md around line 177:
"the in-memory scheduler may silently drop jobs during long sessions; if the
poller stops firing, recreate it manually"). The Windows Task Scheduler was
built precisely because CronCreate is unreliable. **Do not attempt to use
CronCreate as the primary poller mechanism.** The Windows scheduled task is
the answer.

### Freshness visibility — `.claude/hooks/poller-freshness.py`

A UserPromptSubmit hook (`.claude/hooks/poller-freshness.py`, registered in
`.claude/settings.local.json`) runs on every owner message and emits a
`systemMessage` instructing Claude to prepend a freshness block to its
response. The block looks like:

```
POLLER OK @ 16:41:12Z
  claude=OK 1m22s ago (clear) Bridge scan: clear.
  codex=OK 1m01s ago (running) codex exec running for 1 selected item(s) ...
```

Freshness bands:

- `OK`: last update <240s (within 3-min cadence + 1m grace)
- `WARN`: <600s (10 min) — investigate
- `ALARM`: >600s — outage confirmed

Overall status is `POLLER ALARM` if any leg is ALARM, `POLLER WARN` if any is
WARN, else `POLLER OK`. If either scan-status JSON file is missing or
unreadable, the leg reports `FILE-MISSING` or `UNREADABLE-TIMESTAMP` and
contributes `ALARM` to the overall.

The hook reads `claude-scan-status.json` and `codex-scan-status.json` with
`encoding='utf-8-sig'` to strip the PowerShell `Set-Content` UTF-8 BOM. Do
not remove that detail.

**Why a systemMessage, not direct chat output:** UserPromptSubmit hook stdout
is delivered as context to Claude, not as a chat bubble. The hook tells Claude
what to include in the response; Claude's normal response text is what
actually appears in the chat. The instruction is marked MANDATORY so Claude
includes it every turn.

**If the hook fails to produce output** (Python error, file missing,
unreadable JSON), it exits 0 with no stdout — Claude's response then has no
freshness prelude, which is itself a visible indicator that the hook is
broken.

### What NOT to do (retracted recommendations from earlier memory versions)

- **Do not use the Monitor tool** for this. Its `<task-notification>` events
  are Claude-internal and invisible to the owner.
- **Do not use `mcp__scheduled-tasks__create_scheduled_task`** as a poller
  replacement. It spawns new sessions rather than injecting into the current
  one, and its completion notifications are also invisible to the owner.
- **Do not use CronCreate** for the primary bridge poller. It silently stops.
  A prior version of this memory file recommended CronCreate based on CLAUDE.md
  line 171's documented protocol — but in practice, CronCreate's silent
  failures are exactly why the Windows Task Scheduler poller was built. The
  CLAUDE.md directive predates the Windows poller; it has not been updated
  to reflect the current architecture but should be.
- **Do not attempt to tail -F the poller log files.** Standing rule since
  S291: Git Bash `tail -F` collides with PowerShell writers' non-shared file
  handles.

### Session-start checklist

1. Run the bridge liveness check as normal.
2. Read `bridge/INDEX.md` for pending work.
3. **Trust that the Windows Task Scheduler pollers are running.** Do not
   create CronCreate jobs or mcp__scheduled-tasks as replacements.
4. Verify by checking that the poller-freshness hook is reporting `POLLER OK`
   at the top of responses. If it's not appearing, the hook is broken — check
   `.claude/settings.local.json` UserPromptSubmit block and
   `.claude/hooks/poller-freshness.py`.
5. If either scan-status file is showing ALARM or FILE-MISSING, investigate
   the Windows scheduled task (`Get-ScheduledTask -TaskName
   AgentRedFileBridgeIndexScan-*`).

### Known failure modes (investigate these first when POLLER reports WARN/ALARM)

- **PS1 syntax error** (S291 incident): a `$var:` line caused a 6-hour silent
  outage. The pre-commit PS1 validator (VERIFIED this session) should catch
  this class now.
- **OAuth token expiry** (S290 incident): the spawn needs a fresh
  `CLAUDE_CODE_OAUTH_TOKEN` injected from `.local/claude-oauth-token.txt`.
  Refresh from the interactive session's env var when rotated.
- **Windows scheduled task disabled**: check State != "Ready" or "Running".
- **Claude Code version change**: new versions may change the `claude.exe -p`
  flags or the `%APPDATA%\Claude\claude-code\<version>\claude.exe` path that
  the PS1 auto-detects.
