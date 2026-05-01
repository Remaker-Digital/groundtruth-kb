# Agent Red Cutover Freeze-Window Runbook

**Date:** 2026-05-01
**Authority:** `bridge/gtkb-isolation-016-phase8-wave3-execution-007.md` (REVISED-3, GO `-008`)
**Status:** Rehearsal evidence (not the cutover script itself; ISOLATION-018 produces its own runbook informed by what this surfaces).

---

## Purpose

Document the freeze-window protocol for running the `manifest_driven_filter` DB reconciliation strategy at cutover. This runbook is consumed by `GTKB-ISOLATION-018` (Agent Red child-directory cutover); it is NOT executed during Wave 3 rehearsal.

## Pre-Freeze Checks

1. **Legacy DB integrity:** `sqlite3 E:/GT-KB/groundtruth.db "PRAGMA integrity_check"` returns `ok`.
2. **No in-flight bridge proposals:** `bridge/INDEX.md` has no open NEW or REVISED entries other than the cutover bridge itself.
3. **Last `membase` lane run age under 1 hour:** `{output_dir}/membase_export/result.json` `run_started_at` field is within the past 60 minutes. (Stale partition manifest invalidates the filter.)
4. **`.driveignore` covers `{output_dir}`:** confirm via `git check-ignore -v {output_dir}` returns ignore-match. Defends against cloud-sync corruption per S311 incident.
5. **Output directory empty:** `{output_dir}` does not exist or is removable; the lane will create a fresh directory.

## Freeze Announcement Protocol

Owner-only single-harness operation. No parallel sessions. Steps:

1. Announce freeze in chat: "Freeze starts {ISO-8601 timestamp}; expected duration ≤ 60 minutes."
2. Stop any running smart-poller daemons or scheduled tasks that write to `groundtruth.db`.
3. Confirm no other Claude Code or Codex CLI sessions are active.

## Run `_db_filter_dryrun`

```bash
cd E:/GT-KB
python scripts/rehearse_isolation.py --phase membase --execute \
  --output-dir C:/temp/agent-red-rehearsal-cutover-{ISO-TIMESTAMP}
python scripts/rehearse_isolation.py --phase db-filter-dryrun --execute \
  --output-dir C:/temp/agent-red-rehearsal-cutover-{ISO-TIMESTAMP}
```

Expected runtime: under 5 minutes for the partition step + under 2 minutes for the filter step (most of the 1.0 GB legacy DB is `assertion_runs` telemetry which is excluded).

## Smoke Checks Against Filtered DB

Run against `{output_dir}/db-filter-dryrun/groundtruth-filtered-preview.db`:

1. **Schema parity:**
   ```bash
   sqlite3 legacy.db ".schema" > /tmp/legacy-schema.sql
   sqlite3 filtered-preview.db ".schema" > /tmp/filtered-schema.sql
   diff /tmp/legacy-schema.sql /tmp/filtered-schema.sql
   ```
   Expected: zero diff (filter copies schema unchanged).
2. **Integrity check:** `PRAGMA integrity_check` returns `ok`. Already enforced by the lane; reconfirm.
3. **Expected row counts:** read `db-filter-summary.json`, confirm `row_counts.adopter_inserted` equals partition manifest's adopter total; `row_counts.framework_excluded` equals partition manifest's framework total.
4. **Framework-row absence:** spot-check by ID prefix. For example, query `SELECT COUNT(*) FROM specifications WHERE id LIKE 'GTKB-%'` against the filtered DB; expected zero (or exactly the count of GTKB-prefixed adopter-content rows surfaced by Slice 8 — typically zero in practice).
5. **Telemetry tables empty:** `SELECT COUNT(*) FROM assertion_runs;` returns 0. Same for `pipeline_events`, `quality_scores`, `test_coverage`.

## Activation/Swap

**Out of scope for this runbook.** Cross-reference: `GTKB-ISOLATION-018` will define the activation protocol (renaming legacy DB out of the way, copying filtered DB into the child root's expected location, restarting affected services).

This runbook documents the rehearsal's freeze model only. The activation step is what makes ISOLATION-018 a separate work item with its own owner approval gate.

## Rollback Procedure

If smoke checks fail or the filtered DB is found defective:

1. **Delete child DB:** `rm -rf {output_dir}/db-filter-dryrun/`
2. **Resume on legacy:** no other state change required. Legacy DB is untouched (lane opens it `mode=ro`).
3. **End freeze:** announce in chat: "Freeze ended; rolled back; legacy DB authoritative."

Rollback is trivial because the lane is non-destructive on legacy. This is the primary justification for selecting `manifest_driven_filter` over alternatives that entangle legacy and child state.

## Post-Freeze Validation Checklist

- [ ] Legacy DB still passes `PRAGMA integrity_check`.
- [ ] No commits to `groundtruth.db` during freeze (verifiable via `git log -- groundtruth.db --since="freeze-start-time"`; expected empty).
- [ ] `db-filter-summary.json` archived alongside the cutover bridge proposal as evidence.
- [ ] Warning list (`db-filter-warnings.txt`) reviewed; unclassified row count documented; manual-reclassification queue captured for ISOLATION-018 follow-up.

## Notes

- This runbook is preview evidence only. ISOLATION-018 produces the operational cutover runbook.
- The `.driveignore` mechanism is critical: without it, Google Drive sync of `E:` would propagate the legacy DB's state to other locations during the freeze window, defeating the freeze guarantee.
- Per `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`, `{output_dir}` is intentionally outside `E:\GT-KB` to avoid this risk; the rule's Sandbox Output Exception clause permits this.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
