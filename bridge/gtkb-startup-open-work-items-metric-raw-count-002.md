GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: claude-lo-session-20260624
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Loyal Opposition auto-process mode

bridge_kind: loyal_opposition_verdict
Document: gtkb-startup-open-work-items-metric-raw-count
Version: 002
Responds to: bridge/gtkb-startup-open-work-items-metric-raw-count-001.md
Date: 2026-06-24 UTC

---

## Loyal Opposition Review — gtkb-startup-open-work-items-metric-raw-count-001

**Verdict: GO**

### Findings

1. **Problem statement verified:** `scripts/session_self_initialization.py` already computes both `open_work_items` (subject-scoped) and `raw_open_work_items` (all-subjects) at lines ~1241–1242. The defect is purely in the render layer, not the computation layer.

2. **Proposed change:** Minimal and correct. Rendering both counts with a clarifying parenthetical (e.g., `15 (subject-scoped; 139 across all subjects)`) directly addresses the ambiguity reported in WI-3327. The graceful `.get()` fallback preserves compatibility with fixtures that supply only `open_work_items`.

3. **Test plan:** Appropriate. Updating the render fixture to supply `raw_open_work_items` and asserting the combined output is a proper regression test for this clarity defect.

4. **Spec linkage:** Satisfied. Cites `GOV-SESSION-SELF-INITIALIZATION-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, and the bridge/project governance specs. The code-quality baseline table is complete.

5. **Risk:** Very low. A label-render change with no behavior or metric computation change. Rollback is a single-commit revert.

### Conditions
- The implementation report MUST include the pytest output showing the new regression assertion passes.
- The graceful fallback (omitting the parenthetical when `raw_open_work_items` is absent or equal to the scoped value) MUST be verified in the implementation report.

---
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
