WITHDRAWN

bridge_kind: withdrawal
Document: gtkb-tafe-runtime-schema
Version: 002
Date: 2026-06-13 UTC
Author: Codex Prime Builder (interactive PB override)
Responds to: bridge/gtkb-tafe-runtime-schema-001.md
Status: WITHDRAWN
Recommended commit type: docs

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebe11-2c38-7f42-9383-81db49281ddd
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

target_paths: ["bridge/gtkb-tafe-runtime-schema-002.md", "bridge/INDEX.md"]

---

# WI-4488 Duplicate Proposal Withdrawal

## Disposition

This duplicate WI-4488 runtime-schema proposal is withdrawn before Loyal
Opposition review because the same work item already has an older canonical GO
thread:

- `bridge/gtkb-tafe-runtime-tables-schema-001.md` - Prime Builder proposal.
- `bridge/gtkb-tafe-runtime-tables-schema-002.md` - Loyal Opposition GO.

The canonical GO thread also resolves the WI-4488 F5 scoping question
conservatively: `stage_leases`, `stage_attempts`, and
`agent_capability_snapshots` remain split to follow-on work rather than being
folded into this Phase 0 runtime-table slice. This withdrawn duplicate made a
different scoping call, so keeping it active would create avoidable duplicate
review work and an unnecessary conflict.

Implementation should proceed only through `gtkb-tafe-runtime-tables-schema`
and its implementation-start packet.

## Evidence

The live top of `bridge/INDEX.md` showed:

```text
Document: gtkb-tafe-runtime-schema
NEW: bridge/gtkb-tafe-runtime-schema-001.md

Document: gtkb-tafe-runtime-tables-schema
GO: bridge/gtkb-tafe-runtime-tables-schema-002.md
NEW: bridge/gtkb-tafe-runtime-tables-schema-001.md
```

`show_thread_bridge.py gtkb-tafe-runtime-tables-schema` reported no drift and
showed latest status `GO` at `bridge/gtkb-tafe-runtime-tables-schema-002.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains the canonical
  workflow state; this append-only withdrawal makes the duplicate thread
  terminal without deleting prior evidence.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation remains
  constrained to the valid GO'd thread and its implementation-start packet.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the duplicate proposal is closed
  through a durable bridge artifact rather than being silently ignored.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the latest status is now terminal,
  so Loyal Opposition no longer needs to process this duplicate `NEW` entry.

## Owner Decisions / Input

No owner decision is required. This withdrawal does not change the owner-
authorized TAFE Phase 0 scope; it only removes a duplicate bridge thread filed
after an older WI-4488 proposal had already received GO.

## Verification

| Surface | Evidence |
| --- | --- |
| Bridge queue state | `bridge/INDEX.md` records this `WITHDRAWN` status above the duplicate `NEW` entry. |
| Canonical implementation lane | `gtkb-tafe-runtime-tables-schema` remains latest `GO` in `bridge/INDEX.md`. |

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
