# POR Step 16.C Stream D — Phantom-Only + Assertion-Only WI Creation (Revision 2)

**Status:** REVISED (addressing NO-GO -004 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** por-step16c-stream-d-phantom-wi-creation
**Prior versions:** -001 (NEW), -002 (NO-GO), -003 (REVISED), -004 (NO-GO)

## NO-GO -004 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: `DISTINCT source_spec_id` post-condition doesn't prove one-to-one | Blocking | Changed to `GROUP BY source_spec_id HAVING COUNT(*)=1` with assertion that all 34 groups have count=1 (§ Idempotence & Coverage Invariant, revised) |
| F2: Mutation-scope exit criterion contradicts API's `pipeline_events` writes | Blocking | Exit criterion revised to allow `work_items` + one `pipeline_events.wi_created` per WI; still forbids specs/tests/assertions/unrelated tables (§ Exit Criteria, sharpened) |

## Prior NO-GO Findings (preserved from -002)

| Finding | Severity | Resolution (from -003) |
|---------|----------|-----------------------|
| F1: `insert_work_item` template missing required fields | Blocking | Full 10-field signature (unchanged) |
| F2: Idempotence must verify OPEN hygiene WIs specifically | Blocking | `resolution_status='open'` checks everywhere (tightened further in this revision) |
| F3: Title drift | Medium | Runtime read from inventory/DB (unchanged) |

## Prior Deliberations (unchanged)

- `DELIB-0711` / `DELIB-0712` / `DELIB-0713`
- Umbrella GO at `bridge/por-step16c-implemented-untested-remediation-002.md`
- Bridge precedent: `spec-hygiene-untested-verified-008`, `spec-hygiene-spa-remediation-006`

## Objective (unchanged)

Create exactly **34 hygiene work items** — one per spec — for all γ' and δ'
specs from the 16.B classifier. Specs remain `implemented`.

## Scope — Exact Spec IDs (unchanged from -003)

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

**Total: 34 specs.**

## Title Source of Truth (unchanged)

Titles read at runtime from inventory JSON (or `current_specifications` as
fallback) via `spec_id` lookup; never hand-copied.

## WI ID Allocation (unchanged)

Sequential from `max(WI-NNNN) + 1` = `WI-3185`. Range: `WI-3185` through
`WI-3218`. Pre-insert collision check per WI.

## WI Creation Template (unchanged — matches installed API)

```python
db.insert_work_item(
    id=wi_id,
    title=f"Test coverage gap: {spec_title}",
    origin="hygiene",
    component="Backend",
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
    priority="low",
    stage="created",
)
```

Category/rationale mapping unchanged from -003.

## Idempotence & Coverage Invariant (addresses -004 F1)

### Pre-flight (per spec) — revised to fail fast on duplicates

```python
existing_open = conn.execute("""
    SELECT id, version FROM current_work_items
    WHERE source_spec_id = ?
      AND origin = 'hygiene'
      AND resolution_status = 'open'
""", (spec_id,)).fetchall()

if len(existing_open) == 0:
    create_new_wi(...)              # happy path
elif len(existing_open) == 1:
    skip_already_covered(...)       # exactly one — umbrella invariant already met
else:
    # More than one open hygiene WI — NOT ALLOWED per umbrella one-to-one rule
    raise DuplicateOpenHygieneWI(
        f"{spec_id}: found {len(existing_open)} open hygiene WIs — expected 0 or 1"
    )
```

This fails fast on pre-existing duplicates rather than silently accepting them.

### Post-condition (addresses F1 — grouped check, not DISTINCT)

```python
# Compute per-spec open hygiene WI counts
rows = conn.execute(f"""
    SELECT source_spec_id, COUNT(*) AS open_hygiene_count
    FROM current_work_items
    WHERE source_spec_id IN ({placeholders})
      AND origin = 'hygiene'
      AND resolution_status = 'open'
    GROUP BY source_spec_id
""", stream_d_spec_ids).fetchall()

# Assertion 1: Exactly 34 groups (one per target spec, all covered)
assert len(rows) == 34, (
    f"Stream D coverage gap: {34 - len(rows)} target specs have no open hygiene WI. "
    f"Missing: {set(stream_d_spec_ids) - {r['source_spec_id'] for r in rows}}"
)

# Assertion 2: Every group has count == 1 (exactly-one invariant)
duplicates = [(r['source_spec_id'], r['open_hygiene_count']) for r in rows
              if r['open_hygiene_count'] != 1]
assert not duplicates, (
    f"Stream D one-to-one invariant violated: "
    f"{len(duplicates)} specs have >1 open hygiene WI: {duplicates}"
)
```

Only the combination of both assertions proves the umbrella's "exactly 34
hygiene WIs, one per spec" condition. The prior `len(DISTINCT)` check would
have accepted a state where SPEC-A has 2 WIs and SPEC-B has 0 (still 33
distinct source_spec_ids; still passing the old check; still wrong).

## Implementation Plan (revised steps 7+)

1-6. Same as -003 (load inventory, filter, allocate WI IDs, hash-bracket
open, per-spec loop with idempotence).

7. **Post-condition check** (revised):
   - Execute grouped SQL above.
   - Run both assertions. Fail loudly on either violation.
8. **DB hash bracket close** + **verify mutation scope** (revised per F2).
9. **Post-impl report** includes:
   - `{spec_id → wi_id → title}` mapping (all 34)
   - Any skipped specs with reason (exactly-one existing open hygiene WI)
   - Any duplicates found (should be 0)
   - DB hash pre/post
   - Grouped-SQL result listing all 34 specs with `open_hygiene_count = 1`
   - **`pipeline_events` delta**: count of new `wi_created` events with
     matching `artifact_id` (one per created WI)

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | Up to 34 new `work_items` rows + up to 34 new `pipeline_events` rows (audit trail) |
| `independent-progress-assessments/spec-hygiene/scripts/create_stream_d_wis.py` | New | Script performing batch WI creation |

No source code changes. No test changes. No spec status mutations.

## Exit Criteria (revised per -004 F2)

### Allowed DB mutations (addresses F2)

The API correctly writes to two tables per WI creation:

- **`work_items`**: new row per created WI (expected N rows, where N ≤ 34)
- **`pipeline_events`**: one `wi_created` event per created WI with
  `artifact_id = wi_id` and matching `event_type = 'wi_created'` (expected
  N rows, same N)

Both are **allowed** — they are the KB's canonical audit path for WI
creation.

**Forbidden**: any mutation to `specifications`, `tests`, `test_coverage`,
`assertion_runs`, `deliberations`, `documents`, or any other table.

### Full exit criteria

1. Post-condition grouped SQL returns exactly **34** rows, each with
   `open_hygiene_count = 1`.
2. No pre-flight duplicate-detection errors.
3. Post-impl report lists the full `{spec_id → wi_id}` mapping.
4. DB hash bracket documents mutations **only** to `work_items` and
   `pipeline_events`. Mutation audit: count of new `wi_created` events =
   count of new WIs.
5. Classifier re-run confirms γ'/δ' spec counts unchanged (Stream D does
   not mutate spec status).

## Reconciliation Against Umbrella

Umbrella condition #3 (`por-step16c-implemented-untested-remediation-002.md:198-204`):
"Stream D must create exactly 34 hygiene WIs, one per `gamma_prime` or
`delta_prime` spec, with `origin=hygiene` and a durable source-spec link."

This revision's post-condition enforces **both** the "exactly 34" AND the
"one per" invariants via the grouped check + `open_hygiene_count = 1`
assertion. ✓

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
