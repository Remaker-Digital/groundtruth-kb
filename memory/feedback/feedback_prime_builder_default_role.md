---
name: Prime Builder is the default role — always
description: Claude Code must start in Prime Builder mode for every fresh session until owner explicitly requests otherwise
type: feedback
originSessionId: c002f66c-aced-4409-9602-c16758fcfa14
---
**Rule:** Always start in Prime Builder mode. Never start a session as Loyal Opposition unless Mike explicitly asks to switch roles.

**Why:** S305 (2026-04-23): the S304 session-wrap commit set `active_role: loyal-opposition` in `operating-role.md`. The S305 session incorrectly started as LO. Mike corrected: "Claude Code should now start in Prime Builder mode every time until I make an explicit request for that to change."

**How to apply:**
- At session start, verify `active_role` in `.claude/rules/operating-role.md` is `prime-builder`.
- If it is `loyal-opposition`, correct it immediately and notify the owner.
- Only accept `loyal-opposition` when Mike's prompt (or the bridge handoff message) explicitly assigns LO role for the session.
- Session-wrap commits must NOT change `active_role` from `prime-builder` to `loyal-opposition` as a side effect of automated wrap steps.
- The Codex OS-poller already handles Loyal Opposition reviews; the interactive Claude Code session is always Prime Builder.
