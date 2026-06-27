# Auth Troubleshooting

<!-- © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. -->

This guide covers authentication failures that bridge automation may
encounter when invoking Prime Builder (Claude Code) or Loyal Opposition
(Codex). groundtruth-kb does not manage tokens or credentials — it only
documents the steps needed to restore a working session.

---

## "Bridge says AUTH FAILURE"

The bridge dispatcher records `AUTH FAILURE` (or similar) in dispatch state or logs when
the underlying agent CLI exits with an authentication error. The most common
causes are:

| Cause | Symptom |
|-------|---------|
| Expired OAuth session | `claude` exits non-zero; logs show 401 or "session expired" |
| Missing `ANTHROPIC_API_KEY` | Claude Desktop / API mode exits with key error |
| Codex token expired | `codex exec` exits with 401 or token-expired message |
| Environment variable not inherited | Dispatched harness process does not see the token |

---

## Claude Code (Claude Desktop / OAuth)

Claude Code uses an OAuth session managed by Claude Desktop. When the
session expires:

1. Open **Claude Desktop** on your workstation.
2. Sign out and sign back in — this refreshes the OAuth token.
3. If bridge automation runs headlessly, verify the dispatched process inherits
   the updated session by running one manual foreground scan.
4. On Windows: the headless dispatch process must run as your user account
   (not SYSTEM) to inherit the Claude Desktop session context.

---

## Claude Code (API key mode — `ANTHROPIC_API_KEY`)

If you run `claude` with an API key instead of Claude Desktop OAuth:

1. Verify the key is valid: visit [console.anthropic.com](https://console.anthropic.com) and confirm the key is active.
2. Export the key in your shell: `export ANTHROPIC_API_KEY=sk-ant-...`
3. If using a headless launcher, add the environment variable to that process
   explicitly — inherited environment from your shell is often not available
   in background contexts.

---

## Codex

Codex uses its own authentication managed by OpenAI. When the token
expires:

1. Run `codex auth` (or the equivalent command for your Codex version)
   to refresh the token.
2. If bridge automation runs headlessly, re-run the auth command in the
   same user context the dispatcher uses.
3. Verify with a manual `codex exec "echo ok"` before relying on the
   scheduler.

---

## Environment Variable Not Inherited

Headless dispatch processes often run with a minimal environment that does not
include variables set in your shell profile.

**Windows process-launch fix:**

In the dispatch launcher, explicitly set the environment variable before
invoking the agent:

```powershell
$psi = [System.Diagnostics.ProcessStartInfo]::new("claude", $args)
$psi.EnvironmentVariables["ANTHROPIC_API_KEY"] = $env:ANTHROPIC_API_KEY
```

**cron or service-manager fix:**

Add the variable to the crontab entry:

```cron
*/3 * * * * ANTHROPIC_API_KEY=sk-ant-... /path/to/poller.sh
```

Or source your profile at the top of the launcher script:

```bash
#!/bin/bash
source ~/.bashrc
```

---

## Still Not Working?

1. Run `gt project doctor` — it reports bridge status and freshness.
2. Check bridge dispatch state directly:
   - `.gtkb-state/bridge-poller/dispatch-state.json`
   - `.gtkb-state/dispatcher-daemon/`
3. Check the raw dispatch logs for the most recent error output.
4. Run the failing harness command manually in a foreground terminal to see
   the exact error without headless-process buffering.

---

## What groundtruth-kb Does Not Do

groundtruth-kb provides documentation only for authentication issues. It
does not store, rotate, or validate API keys or OAuth tokens. All credential
management remains with the agent provider (Anthropic, OpenAI) and your
operating system's credential store.
