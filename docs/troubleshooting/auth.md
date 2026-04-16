# Auth Troubleshooting

<!-- © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. -->

This guide covers authentication failures that the bridge poller may
encounter when invoking Prime Builder (Claude Code) or Loyal Opposition
(Codex). groundtruth-kb does not manage tokens or credentials — it only
documents the steps needed to restore a working session.

---

## "Bridge says AUTH FAILURE"

The poller writes `AUTH FAILURE` (or similar) to the scan-status file when
the underlying agent CLI exits with an authentication error. The most common
causes are:

| Cause | Symptom |
|-------|---------|
| Expired OAuth session | `claude` exits non-zero; logs show 401 or "session expired" |
| Missing `ANTHROPIC_API_KEY` | Claude Desktop / API mode exits with key error |
| Codex token expired | `codex exec` exits with 401 or token-expired message |
| Environment variable not inherited | Scheduled-task spawn does not see the token |

---

## Claude Code (Claude Desktop / OAuth)

Claude Code uses an OAuth session managed by Claude Desktop. When the
session expires:

1. Open **Claude Desktop** on your workstation.
2. Sign out and sign back in — this refreshes the OAuth token.
3. If the poller runs in a scheduled task, verify the task inherits the
   updated session by running one manual foreground scan.
4. On Windows: the scheduled task must run as your user account (not
   SYSTEM) to inherit the Claude Desktop session context.

---

## Claude Code (API key mode — `ANTHROPIC_API_KEY`)

If you run `claude` with an API key instead of Claude Desktop OAuth:

1. Verify the key is valid: visit [console.anthropic.com](https://console.anthropic.com) and confirm the key is active.
2. Export the key in your shell: `export ANTHROPIC_API_KEY=sk-ant-...`
3. If using a scheduled task or cron job, add the environment variable
   to the task or cron entry explicitly — inherited environment from your
   shell is often not available in scheduled contexts.

---

## Codex

Codex uses its own authentication managed by OpenAI. When the token
expires:

1. Run `codex auth` (or the equivalent command for your Codex version)
   to refresh the token.
2. If the poller runs as a scheduled task, re-run the auth command in the
   same user context the scheduled task uses.
3. Verify with a manual `codex exec "echo ok"` before relying on the
   scheduler.

---

## Environment Variable Not Inherited

Scheduled tasks (Windows Task Scheduler, cron) often run with a minimal
environment that does not include variables set in your shell profile.

**Windows Task Scheduler fix:**

In the poller script, explicitly set the environment variable before
invoking the agent:

```powershell
$psi = [System.Diagnostics.ProcessStartInfo]::new("claude", $args)
$psi.EnvironmentVariables["ANTHROPIC_API_KEY"] = $env:ANTHROPIC_API_KEY
```

**cron fix:**

Add the variable to the crontab entry:

```cron
*/3 * * * * ANTHROPIC_API_KEY=sk-ant-... /path/to/poller.sh
```

Or source your profile at the top of the poller script:

```bash
#!/bin/bash
source ~/.bashrc
```

---

## Still Not Working?

1. Run `gt project doctor` — it reports bridge status and freshness.
2. Check the scan-status file directly:
   - Claude: `independent-progress-assessments/bridge-automation/logs/claude-scan-status.json`
   - Codex: `independent-progress-assessments/bridge-automation/logs/codex-scan-status.json`
3. Check the raw poller log under
   `independent-progress-assessments/bridge-automation/` for the most
   recent error output.
4. Run the poller script manually in a foreground terminal to see the
   exact error without scheduled-task buffering.

---

## What groundtruth-kb Does Not Do

groundtruth-kb provides documentation only for authentication issues. It
does not store, rotate, or validate API keys or OAuth tokens. All credential
management remains with the agent provider (Anthropic, OpenAI) and your
operating system's credential store.
