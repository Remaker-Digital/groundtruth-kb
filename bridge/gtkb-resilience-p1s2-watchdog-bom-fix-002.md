GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-resilience-p1s2-watchdog-bom-fix
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-resilience-p1s2-watchdog-bom-fix-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4882
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `75cea783-a1f3-4f8b-b834-cca62d92299c` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** Root cause is credible and code-aligned: PowerShell 5.1
`Set-Content -Encoding utf8` writes a BOM; `storm_watchdog_reap.py` reads with
plain `utf-8`, causing `JSONDecodeError` and perpetual FAILSAFE
(`reaped=0 reason=decider exit=1`). Dual fix (`utf-8-sig` consumer + BOM-less
producer write) is minimal, safe, and leaves `decide_reap` untouched.

## Evidence

- Preflights: applicability pass; clause gate 0 blocking gaps.
- Confirmed at `scripts/ops/harness_storm_watchdog.ps1:143` and
  `storm_watchdog_reap.py:301,331,422`.
- Scoped to WI-4882 Slice 2 per `DELIB-20266276` D2 storm-recovery requirement.

## Residual Risks (non-blocking)

1. Post-fix, verify live watchdog log shows non-zero reap decisions when
   candidates exist (operational confirmation in implementation report).
2. Other ops JSON writes in the `.ps1` may still emit BOM — only the candidate
   file is fixed here; acceptable if decider reads all three inputs with
   `utf-8-sig`.

## Prior Deliberations

- `DELIB-20266276` — D2 storm auto-recovery requires working watchdog.
- bridge/gtkb-resilience-p1-daemon-supervisor-log-004.md (Slice 1 VERIFIED).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
