VERIFIED
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: implementation_verification
Document: gtkb-resilience-p1s2-watchdog-bom-fix
Version: 004
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-resilience-p1s2-watchdog-bom-fix-003.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4882
Recommended commit type: fix

## Separation Check

Report `-003` author session `75cea783-a1f3-4f8b-b834-cca62d92299c` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).
GO at `-002` from this LO session.

## Verification Summary

**VERIFIED.** Storm-watchdog BOM I/O defect repaired: three `utf-8-sig` reads in
decider, BOM-less `WriteAllText` in `.ps1`, BOM regression test added.
16/16 tests pass; `decide_reap` logic unchanged.

## Evidence

Independent re-run (2026-06-27):

```text
python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=line
=> 16 passed in 0.85s
```

Encoding changes confirmed at `storm_watchdog_reap.py:301,331,422` and
`harness_storm_watchdog.ps1:148`.

## Prior Deliberations

- bridge/gtkb-resilience-p1s2-watchdog-bom-fix-002.md (GO).
- `DELIB-20266276` — D2 storm auto-recovery requires working watchdog.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
