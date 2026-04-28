---
name: Poller circular-dependency limit
description: The bridge protocol cannot self-heal a broken poller because the autonomous worker depends on the component that needs fixing. Out-of-band foreground repair is the only escape.
type: feedback
originSessionId: 02cf7e50-fa96-4cd1-af96-c7e70464d7f2
---
When the autonomous Prime worker breaks the Claude poller itself (S291 incident: a one-line `$MAX_ITEMS_PER_SPAWN:` PowerShell syntax error inside `claude-file-bridge-scan.ps1`), the bridge protocol cannot fix it. Codex correctly NO-GO'd the broken proposal on post-implementation review, but the corrective revision cannot land via the same loop because the poller that would run the revision is the broken one. This is a hard circular dependency.

**Why:** The bridge protocol assumes the poller is always alive and can execute corrective work. When the poller itself is the failing component, the autonomous loop silently halts — no notifications fire, no bridge entries advance, no further work lands.

**How to apply:**
- If the Claude poller has gone silent for more than ~10 minutes, assume the bridge loop is broken and investigate directly. Do not wait for the loop to self-heal.
- The escape hatch is always direct foreground intervention: diagnose via `powershell -File` direct invocation, fix via Edit, verify via manual run.
- Owner authorizes direct edits to bridge-automation infrastructure when the poller is dead. Do not delay on protocol compliance when the failing component is the protocol itself.
- Post a retroactive bridge entry documenting the direct edits for audit trail after the poller is restored.
- Symmetric observability (status JSON files for both pollers, not just toasts) is the prerequisite for detecting this class of outage early. The Codex poller had `codex-scan-status.json` from the start; the Claude poller's equivalent `claude-scan-status.json` was added in S291 retroactively.

**Why this matters for future sessions:** If a new category of poller-affecting change is in flight (batch-size cap, timeout change, spawn command change), treat it as infrastructure-critical. Pre-commit PS1 syntax validation would have prevented the S291 incident entirely. Consider drafting that gate as a standalone proposal before any further poller-touching work lands.
