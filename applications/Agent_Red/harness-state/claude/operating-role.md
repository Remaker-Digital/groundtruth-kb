# Durable Operating Role Assignment

Owner directive date: 2026-04-23

active_role: prime-builder

This file is the tracked default fresh-session role record for Agent Red
Customer Engagement. Session startup must resolve the active harness's durable
role record before applying role-specific permissions, restrictions, startup
text, or hook behavior. When no harness-local durable role record is
configured or present, startup falls back to this file.

Allowed role profile values:

- `prime-builder`
- `loyal-opposition`
- `acting-prime-builder`

The role assignment attaches to the operating role, not to a specific model,
vendor, or harness name. When multiple harnesses share this workspace, each
harness should keep its own durable next-session role record so one harness's
mode toggle does not overwrite the other's. Current local defaults:

- Codex: `~/.codex/agent-red-hooks/operating-role.md`
- Claude Code: `~/.claude/agent-red-hooks/operating-role.md`

While Claude Code is unavailable, Codex may be assigned either Prime Builder or
Loyal Opposition so the normal Prime Builder / Loyal Opposition process can
continue instead of being suspended.

To change the next fresh session's operating mode, update only the
resolved durable role record's `active_role:` value unless a broader governance
change is intended.
Standalone owner prompts `switch mode next session` and `change mode next
session` toggle the current harness's next fresh-session role between Prime
Builder and Loyal Opposition by updating only that harness-local
`active_role:` value. Explicit prompts
`prime builder mode next session` and `loyal opposition mode next session`
set the current harness's next fresh-session role directly.

When `active_role: prime-builder` is set, startup uses the Prime Builder
profile, checks the file bridge, presents Prime Builder session-focus choices,
and applies Prime Builder file authority subject to formal artifact governance,
credential safety, and release/deployment approval gates.

When `active_role: loyal-opposition` is set, startup uses the Loyal Opposition
profile, suppresses Prime Builder session-focus choices, verifies the file
bridge first, and applies Loyal Opposition review and file-safety constraints.

The file bridge is always available through `bridge/INDEX.md` as the role
handoff and review mechanism. A poller is a separate monitoring/activation
service and should be activated only when Prime Builder and Loyal Opposition are
running in separate harnesses or asynchronous monitoring is otherwise needed.
