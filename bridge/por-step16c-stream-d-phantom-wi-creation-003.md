# POR Step 16.C Stream D — Phantom-Only + Assertion-Only WI Creation (Revised)

**Status:** REVISED (addressing NO-GO -002 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16c-stream-d-phantom-wi-creation
**Prior versions:** -001 (NEW), -002 (NO-GO)

## NO-GO -002 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: `insert_work_item` template missing required fields | Blocking | Added full signature call: `id`, `component`, `resolution_status`, `stage` per `groundtruth_kb/db.py:2822-2896` (§ "WI Creation Template") |
| F2: Idempotence check must verify OPEN hygiene WIs specifically | Blocking | Pre-flight and post-condition rewritten to check `resolution_status='open'` explicitly (§ "Idempotence & Coverage Invariant") |
| F3: Title drift for SPEC-1712, SPEC-1881 | Medium | Implementation reads titles from inventory JSON / current DB at runtime; manual table below is informational only (§ "Title Source of Truth") |

## Prior Deliberations

- `DELIB-0711`, `DELIB-0712`, `DELIB-0713` (all S297): Same as prior version.
- Bridge precedent: `spec-hygiene-untested-verified-008` (VERIFIED) and
  `spec-hygiene-spa-remediation-006` (VERIFIED) — this revision's template
  matches their actual committed WI shapes (WI-3178 through WI-3184).

## Objective (unchanged)

Create exactly **34 hygiene work items** — one per spec — for all γ' and δ'
specs identified in the 16.B classifier. Specs themselves remain at
`implemented` status; no status mutations.

## Scope — Exact Spec IDs (unchanged from -001)

### γ' (gamma_prime) — 19 specs

```
SPEC-1707, SPEC-1708, SPEC-1709, SPEC-1710, SPEC-1711, SPEC-1712,
SPEC-1864, SPEC-1865, SPEC-1866, SPEC-1867, SPEC-1868, SPEC-1875,
SPEC-1879, SPEC-1880, SPEC-1881, SPEC-1882,
SPEC-2098, SPEC-2099, SPEC-2100
```

### δ' (delta_prime) — 15 specs

```
SPEC-1653,
SPEC-1740, SPEC-1741, SPEC-1742, SPEC-1743, SPEC-1744,
SPEC-1772, SPEC-1773, SPEC-1775, SPEC-1776, SPEC-1777, SPEC-1778,
SPEC-1799, SPEC-1800,
SPEC-1872
```

**Total: 34 specs.** Inventory filter: `classification.category IN ('gamma_prime', 'delta_prime')`.

## Title Source of Truth (addresses F3)

The implementation script generates WI titles **at runtime** by reading each
spec's current `title` field from the inventory JSON (or directly from
`current_specifications` as fallback). The spec-ID list above is the only
manually maintained list; titles are looked up, never hand-copied.

This addresses the two title drifts Codex flagged:
- SPEC-1712 actual title: "3rd-Party MCP Server Integrations -- External
  Service Connectors" (not "Connections")
- SPEC-1881 actual title: "Tenant Display Name — human-readable tenant
  identifier for SPA" (not "Superadmin")

## WI ID Allocation (addresses F1)

**Strategy: sequential allocation starting at the next available numeric ID.**

1. At script start, query the KB for the highest existing `WI-NNNN` ID:
   ```python
   row = conn.execute("""
       SELECT id FROM work_items
       WHERE id LIKE 'WI-%' AND id GLOB 'WI-[0-9][0-9][0-9][0-9]'
       ORDER BY CAST(SUBSTR(id, 4) AS INTEGER) DESC LIMIT 1
   """).fetchone()
   # Current max as of this proposal: WI-3184
   ```
2. Next ID = `WI-{max_num + 1:04d}` = `WI-3185` (given current DB state).
3. Allocate 34 sequential IDs: `WI-3185` through `WI-3218`.
4. **Collision handling**: Before each `insert_work_item` call, check if
   the planned ID is already taken via `SELECT id FROM work_items WHERE id=?`.
   If collision detected (should not happen given allocation is sequential
   from max+1), fail fast with clear error listing all taken IDs in the
   planned range.
5. Record the final `{spec_id → wi_id}` mapping in the post-impl report.

## WI Creation Template (addresses F1)

Executable call shape matching the installed API
(`groundtruth_kb/db.py:2822-2896`):

```python
db.insert_work_item(
    id=wi_id,                                    # "WI-NNNN" allocated sequentially
    title=f"Test coverage gap: {spec_title}",    # spec_title read from inventory
    origin="hygiene",
    component="Backend",                          # default; see note below
    resolution_status="open",
    changed_by="prime_builder",
    change_reason=(
        "POR Step 16.C Stream D: bulk WI creation for phantom-only (γ') "
        "and assertion-only-rejected (δ') specs per DELIB-0713"
    ),
    description=(
        f"Per 16.B methodology review (DELIB-0712) and owner decisions "
        f"(DELIB-0713), {spec_id} was classified as {category} — {rationale}. "
        f"This WI tracks the test-coverage gap to be remediated per GOV-10 "
        f"(live interfaces only)."
    ),
    source_spec_id=spec_id,
    priority="low",                               # matches 16.A precedent (WI-3178-3182)
    stage="created",
)
```

Where:
- `category` is `γ' (gamma_prime)` or `δ' (delta_prime)`
- `rationale` is:
  - For γ': "phantom-only evidence (no test_file paths, no assertion_runs)"
  - For δ': "assertion-only verification insufficient for behavioral requirement per DELIB-0713 Decision 2"

### Component assignment

All 34 WIs use `component="Backend"` as the default — matches the 16.A
precedent (5 of 7 prior hygiene WIs: WI-3178–WI-3182 used `Backend`).
Follow-on remediation sessions can reassign component when actual test work
begins, since the WI is a placeholder tracking the gap.

Exception: **none for this stream.** The handful of specs that might map to
non-Backend components (SPEC-2098 → `knowledge-db`, SPEC-1799/1800 →
`Deployment`, etc.) are still test-coverage-gap placeholders; the component
is cosmetic for now and does not affect WI validity or the umbrella's exit
criteria.

### Priority assignment

All 34 WIs use `priority="low"` — matches 16.A precedent for hygiene WIs
(WI-3178–WI-3182). The Pipeline Observatory specs (WI-3183/3184) used
`priority="medium"` because they blocked a larger cleanup; Stream D WIs
are standalone placeholders with no cascade, so `low` is appropriate.

## Idempotence & Coverage Invariant (addresses F2)

**Pre-flight (per spec):**
```python
existing = conn.execute("""
    SELECT id, resolution_status, version FROM current_work_items
    WHERE source_spec_id = ? AND origin = 'hygiene'
""", (spec_id,)).fetchall()

if not existing:
    create_new_wi(...)              # happy path
elif any(r['resolution_status'] == 'open' for r in existing):
    skip_already_covered(...)       # covered by existing open WI
else:
    # Has a resolved/closed hygiene WI but no open one. Coverage gap!
    # Create a new open WI so the umbrella exit condition is met.
    create_new_wi(..., change_reason="reopened coverage after resolved predecessor")
```

**Post-condition (umbrella exit requirement):**
```python
covered = conn.execute("""
    SELECT DISTINCT source_spec_id FROM current_work_items
    WHERE source_spec_id IN ({34_spec_ids})
      AND origin = 'hygiene'
      AND resolution_status = 'open'
""").fetchall()
assert len(covered) == 34, f"Stream D coverage gap: {34 - len(covered)} specs"
```

This enforces **exactly one current open hygiene WI per Stream D source spec**,
as Codex's F2 required. The umbrella's "34 hygiene WIs open, 1:1 linkage"
condition is now testable via a single SQL query.

## Implementation Plan

1. **Load inventory** from `S297-phase16b-target-inventory.json`.
2. **Filter** to `classification.category IN ('gamma_prime', 'delta_prime')`.
3. **Verify count**: assert 34 items. Fail fast if different.
4. **Allocate WI IDs** sequentially from `max(WI-NNNN) + 1`.
5. **DB hash bracket open**.
6. **Per-spec loop** (34 iterations):
   - Pre-flight: check for existing hygiene WIs matching `source_spec_id`.
   - Apply idempotence rule (§ "Idempotence & Coverage Invariant").
   - If creating: lookup `spec_title` from inventory (or DB fallback), build
     description with `{category, rationale}`, call `insert_work_item` with
     full signature.
7. **Post-condition check**: run the SQL above; assert 34 open hygiene WIs.
8. **DB hash bracket close**.
9. **Post-impl report** includes:
   - Full `{spec_id → wi_id → title}` mapping for all 34 created/skipped WIs
   - Any skipped specs with reason (existing open hygiene WI)
   - DB hash pre/post
   - Final post-condition check result (should be 34 = 34)

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | Up to 34 new `work_items` rows inserted (subject to idempotence) |
| `independent-progress-assessments/spec-hygiene/scripts/create_stream_d_wis.py` | New | Script performing batch WI creation |

No source code changes. No test changes. No spec status mutations.

## Risks (updated)

- **Low:** WI creation pattern now matches committed precedent exactly.
- **Low:** ID allocation is deterministic; collision check is defensive only.
- **Low:** All titles read at runtime from canonical source (inventory/DB).
- **Medium:** Component assignment is best-effort (Backend default); reassignment
  may happen in follow-on remediation when actual test work begins. Flagged as
  ancillary follow-up, not a blocker for this stream.

## Exit Criteria (sharpened)

1. Post-condition SQL returns exactly **34** current open hygiene WIs with
   `source_spec_id` matching the 34 Stream D spec set.
2. Post-impl report lists the `{spec_id → wi_id}` mapping for all 34 specs.
3. No spec from the 34-set is missing an open hygiene WI after the run.
4. DB hash bracket documents only `work_items` table mutations (no spec, test,
   or other-table changes).
5. Classifier re-run confirms γ'/δ' category counts unchanged (Stream D does
   not mutate spec status, only adds WIs).

## Reconciliation Against Umbrella

Umbrella condition #3 (from `bridge/por-step16c-implemented-untested-remediation-002.md`):
"Stream D must create exactly 34 hygiene WIs, one per gamma_prime or
delta_prime spec, with `origin=hygiene` and a durable source-spec link."

This revision's post-condition SQL tests exactly that invariant. ✓

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
