# Durable Operating Role Assignment

Owner directive date: 2026-04-23

active_role: loyal-opposition

This file is the authoritative fresh-session role switch for Agent Red Customer
Engagement. Session startup must read this file before applying role-specific
permissions, restrictions, startup text, or hook behavior.

Allowed role profile values:

- `prime-builder`
- `loyal-opposition`
- `acting-prime-builder`

The role assignment attaches to the operating role, not to a specific model,
vendor, or harness name. While Claude Code is unavailable, Codex may be assigned
either Prime Builder or Loyal Opposition so the normal Prime Builder / Loyal
Opposition process can continue instead of being suspended.

To change the next fresh session's operating mode, update only the
`active_role:` value above unless a broader governance change is intended.
Standalone owner prompts `switch mode next session` and `change mode next
session` toggle the next fresh-session role between Prime Builder and Loyal
Opposition by updating only this `active_role:` value. Explicit prompts
`prime builder mode next session` and `loyal opposition mode next session`
set the next fresh-session role directly.

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
