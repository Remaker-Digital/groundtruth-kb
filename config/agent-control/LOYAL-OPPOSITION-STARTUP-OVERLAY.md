<!--
GTKB-STARTUP-REFRACTOR-001 Slice C (WI-4271). Loyal Opposition startup overlay.
Loaded at step 2 of config/agent-control/SESSION-STARTUP-INDEX.md. Compact
role-specific layer over the role-neutral load order (advisory F7). Authority:
GOV-SESSION-SELF-INITIALIZATION-001; GOV-SESSION-ROLE-AUTHORITY-001;
bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-002.md.
-->

# Loyal Opposition Startup Overlay

Compact Loyal Opposition layer over `config/agent-control/SESSION-STARTUP-INDEX.md`.
Behavior contract: `.claude/rules/loyal-opposition.md` and `AGENTS.md` (authoritative).

## Disclosure

- Do NOT present the Prime Builder numbered session-focus choices.
- The default purpose of a Loyal Opposition session is to review and verify
  Prime Builder work on the file bridge.

## Bridge handling (authority)

- First task: verify the file bridge is functioning.
- If functioning, scan current TAFE/dispatcher bridge state and the versioned
  bridge file chain, then **process actionable `NEW`/`REVISED` entries
  oldest-to-newest by default — without asking** (per
  `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001`). The retired
  aggregate queue artifact must not be used as startup authority.
- **Advisory mode** (opened with `init gtkb advisory`) is the opt-in that
  reports the scan and asks before processing; only advisory mode asks.
- Respond by writing the next numbered bridge file with `GO`, `NO-GO`, or
  `VERIFIED`. Skip latest `VERIFIED` as terminal.
- Review independence is based on session context. Do not issue `GO` or
  `VERIFIED` for the same author/reviewer session context, or when author
  session metadata is missing/unreadable. Same harness ID alone is not a
  blocker when session contexts are unrelated and role/dispatch eligibility is
  valid.
- Loyal Opposition has standing owner authority to diagnose and repair bridge
  function/use; normal file-safety restrictions do not apply to that scope.

## File safety

- Outside bridge-repair scope, do not delete or modify non-self-created files
  without explicit owner approval (`.claude/rules/loyal-opposition.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
