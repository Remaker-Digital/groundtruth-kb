# VERIFIED - halt OS bridge pollers token regression response

Date: 2026-04-24 23:32 -07:00
Reviewer: Codex Loyal Opposition
Reviewed record: `bridge/halt-os-pollers-token-regression-001.md`
Status: VERIFIED

## Claim

The owner-directed removal of automated bridge polling is verified. The four
Windows scheduled tasks that drove OS-level bridge polling are disabled, the
project-level freshness hook is removed, the canonical operating docs now
describe manual bridge scans, and no application source, test, schema, or KB
artifact mutation was needed for the halt.

During verification, Codex found one local-only residue not covered by the
post-action record: `.claude/settings.local.json` still registered the deleted
`.claude/hooks/poller-freshness.py` hook. Because the owner explicitly confirmed
"The poller should be removed. It is costing too many tokens," Codex removed
that stale local registration as part of completing the operational halt.

After the owner showed the still-open `Agent Red Bridge Monitor` window, Codex
also stopped the foreground monitor process, stopped the
`BridgeBackgroundLauncher.exe watchdog` process that could keep it alive, and
removed the user Startup shortcut that would relaunch that monitor on login.

## Evidence

### Scheduled tasks disabled

Command:

```powershell
Get-ScheduledTask -TaskName AgentRedFileBridgeIndexScan-Claude,AgentRedFileBridgeIndexScan-Codex,AgentRedBridgeLivenessAlert,AgentRedPollerLivenessWatcher
```

Observed state:

- `AgentRedBridgeLivenessAlert`: `Disabled`
- `AgentRedFileBridgeIndexScan-Claude`: `Disabled`
- `AgentRedFileBridgeIndexScan-Codex`: `Disabled`
- `AgentRedPollerLivenessWatcher`: `Disabled`

### Freshness hook removed

`Test-Path .claude/hooks/poller-freshness.py` returned `False`.

`.claude/settings.json` no longer has a `UserPromptSubmit` block for
`poller-freshness.py`; it only retains project-level non-poller hooks.

Codex also removed the stale local registration from
`.claude/settings.local.json`, where `UserPromptSubmit` still contained:

```json
"command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/poller-freshness.py\""
```

Post-edit verification:

- `python -m json.tool .claude/settings.local.json` succeeds.
- `rg "poller-freshness" .claude/settings.local.json` returns no active match.

### Canonical docs reflect manual mode

`.claude/rules/bridge-essential.md` states that automated bridge pollers are
halted, the four scheduled tasks are disabled, the `poller-freshness.py`
`UserPromptSubmit` hook has been removed, and bridge scans are manual.

`CLAUDE.md` states that both OS-level Windows scheduled-task pollers and the
in-session `CronCreate` poller are retired, and warns not to recreate them
without explicit owner approval plus the required cost/benefit analysis.

### Foreground monitor watchdog removed

Codex identified these live processes and stopped them:

- `powershell.exe -File E:\GT-KB\independent-progress-assessments\bridge-automation\bridge-scan-monitor-window.ps1`
- `BridgeBackgroundLauncher.exe watchdog`
- the `WindowsTerminal.exe` instance titled `Agent Red Bridge Monitor`

Codex also removed:

```text
C:\Users\micha\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Agent Red Bridge Monitor Watchdog.lnk
```

`Test-Path` against that shortcut returned `False` after removal.

### Commit scope check

`git show --name-status HEAD -- .claude/settings.json .claude/hooks/poller-freshness.py .claude/rules/bridge-essential.md CLAUDE.md bridge/halt-os-pollers-token-regression-001.md`
shows the S308 commit scope:

- deleted `.claude/hooks/poller-freshness.py`
- modified `.claude/rules/bridge-essential.md`
- modified `.claude/settings.json`
- modified `CLAUDE.md`
- added `bridge/halt-os-pollers-token-regression-001.md`

No source code, test, schema, or KB artifact is included in that commit scope.

## Risk / impact

The token-regression driver is removed from the active OS scheduler, from both
project-level and local prompt-hook configuration, and from the foreground
monitor watchdog startup path. Residual poller scripts, logs, and historical
worktree copies remain on disk, but they are inert unless a human explicitly
re-registers or runs them.

The only material risk is future accidental re-enablement through the preserved
scripts or scheduled tasks. The canonical docs now require explicit owner
approval and cost/benefit analysis before re-enabling, which is sufficient for
the current operational state.

## Recommended action

Keep bridge scans manual. Do not re-enable the scheduled tasks, the freshness
hook, the foreground monitor watchdog, or any in-session `CronCreate` bridge
poller unless the owner explicitly approves a new lower-cost design.

## Decision needed from owner

None. The poller removal is verified complete.
