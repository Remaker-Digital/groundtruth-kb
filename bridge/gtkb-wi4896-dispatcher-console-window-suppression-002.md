GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4896-dispatcher-console-window-suppression
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4896-dispatcher-console-window-suppression-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `019f09c3-be81-7771-8200-e81c58e3ae1e` (harness A);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** Narrow launcher-hygiene fix aligned with
`DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`: daemon/ensure paths currently
use `DETACHED_PROCESS` without `CREATE_NO_WINDOW`; Codex stop-hook and bridge
launcher spawns lack consistent no-window flags. Scope is dispatcher-owned
surfaces only — no topology/eligibility change. Cross-Harness Disposition is
adequate for the `.codex/gtkb-hooks/**` target.

## Evidence

- Preflights: applicability pass; clause gate 0 blocking gaps.
- Source review confirms gap at `cli.py` ~950, `ensure_dispatcher_daemon.py`
  ~38, `.codex/gtkb-hooks/session_stop_dispatch.py` bare `Popen`, and
  `launcher.py` wrapper spawn.

## Residual Risks (non-blocking)

1. Stale runtime watchers (e.g. WI-4893 temp scripts) may need manual cleanup
   outside repo — note in implementation report if still present post-fix.
2. Tests should assert Windows flag wiring without requiring a visible window
   (monkeypatch `subprocess.Popen` creationflags as proposed).

## Prior Deliberations

- `DELIB-20266297` — owner console-window suppression directive.
- `DELIB-20266276` — dispatcher resilience context.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
