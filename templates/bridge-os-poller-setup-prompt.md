# File Bridge OS Poller Setup Prompt

Use this prompt with Claude Code or Codex when a GroundTruth project needs a
durable file bridge between Prime Builder and Loyal Opposition agents.

Replace angle-bracket placeholders before use.

```text
You are configuring a durable file-based dual-agent bridge for this GroundTruth
project.

Project root:
<PROJECT_ROOT>

Prime Builder:
- Agent/tool: <CLAUDE_CODE_OR_OTHER_PRIME>
- CLI command: <PRIME_CLI_COMMAND>
- Model/runtime: <PRIME_MODEL_OR_RUNTIME>
- Required config files: <PRIME_CONFIG_FILES>
- Required plugins/MCP servers/skills: <PRIME_PLUGINS_MCP_SKILLS>

Loyal Opposition:
- Agent/tool: <CODEX_OR_OTHER_REVIEWER>
- CLI command: <LOYAL_OPPOSITION_CLI_COMMAND>
- Model/runtime: <LOYAL_OPPOSITION_MODEL_OR_RUNTIME>
- Required config files: <LOYAL_OPPOSITION_CONFIG_FILES>
- Required plugins/MCP servers/skills: <LOYAL_OPPOSITION_PLUGINS_MCP_SKILLS>

Bridge requirements:
1. Use the file bridge. The authoritative queue is bridge/INDEX.md.
2. Do not create or rely on a database-backed bridge or alternate queue unless
   the owner explicitly asks for that runtime.
3. Document any archived or inactive bridge runtime as inactive, and remove
   stale active config only with explicit owner approval.
4. Treat each bridge document entry as newest-first. Only the latest status for
   each entry is actionable.
5. Loyal Opposition scans for latest NEW or REVISED entries and writes the next
   numbered bridge file with GO, NO-GO, or VERIFIED.
6. Prime Builder scans for latest GO or NO-GO entries and writes the next
   numbered bridge file with NEW or REVISED when a response is needed.
7. VERIFIED is terminal and must not trigger Prime Builder action.
8. Poll from the OS scheduler, not from manual prompting. App-native automation
   may be optional responsiveness, but it is not the authoritative reliability
   mechanism unless run records prove it dispatches across sessions.
9. Create separate pollers for Prime Builder and Loyal Opposition.
10. Each poller must parse bridge/INDEX.md, acquire a lock, skip dispatch when
    no work exists, invoke its CLI only for real work, and append logs for both
    clear scans and dispatched runs.
11. Configure a recurring OS schedule for each poller at <POLL_INTERVAL>.
12. On Windows, prefer Task Scheduler -> hidden launcher -> PowerShell scanner.
    On Unix-like systems, use cron, systemd timers, or launchd with equivalent
    background behavior.
13. Store scripts, launchers, locks, logs, and prompt text under project-owned
    paths such as independent-progress-assessments/bridge-automation/.
14. Capture the full setup in BRIDGE-INVENTORY.md, including:
    - scheduler task names
    - script and launcher paths
    - lock and log paths
    - CLI commands and working directories
    - prompt text or prompt file paths
    - plugins, MCP servers, and skills required by each agent
    - relevant Claude Code and Codex configuration files
    - health-check commands
    - recovery procedure
15. Preserve project file-safety rules. Do not overwrite existing instructions,
    hooks, bridge files, or config without confirming ownership and scope.

Deliverables:
- Implement or update the poller scripts and scheduler definitions.
- Update BRIDGE-INVENTORY.md and any bridge protocol rule file needed by the
  agents.
- Provide exact task names, commands, paths, logs, and health-check commands.
- Verify with one no-work scan for each poller.
- If safe test bridge entries exist, verify one full Prime -> Loyal Opposition
  -> Prime status cycle.
- Report unresolved owner decisions separately.
```
