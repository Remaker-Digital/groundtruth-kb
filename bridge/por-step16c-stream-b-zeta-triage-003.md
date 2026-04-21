# POR Step 16.C Stream B — ζ' Test-ID Reassignment Triage (Revised)

**Status:** REVISED (addressing NO-GO -002 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** por-step16c-stream-b-zeta-triage
**Prior versions:** -001 (NEW), -002 (NO-GO)

## NO-GO -002 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: SPEC-1841 falsely covered by default relink | High | SPEC-1841 removed from relink path; treated as needing fresh deployment-modal test evidence — creates hygiene WI instead (§ SPEC-1841 Disposition) |
| F2: Missing 4th triage branch (historical covers superseded spec meaning) | Medium | Added as branch (c) in triage taxonomy: "superseded — test covers old meaning of spec ID" → create hygiene WI + flag for owner review of identity history (§ Triage Method) |
| F3: SPEC-1869/1870/1871 fine to relink | None | Preserved; explicit requirement for fresh test IDs (§ Relink Safety) |

## Prior Deliberations (unchanged)

- `DELIB-0711` / `DELIB-0712` / `DELIB-0713`
- Umbrella GO at `bridge/por-step16c-implemented-untested-remediation-002.md`

## The SPEC-1841 Identity Problem (new context)

Codex's -002 inspection uncovered a subtle data-integrity issue:

| SPEC-1841 version | Title |
|-------------------|-------|
| v1-v3 | "Untested Spec Backfill Program" (old backfill/risk-tier classifier) |
| v4-v5 (current) | "Deployment modal SHOULD pre-fill recommended next version..." |

The historical tests at `tests/quality_metrics/test_backfill_untested.py`
still exercise the **old** backfill meaning. The current `SPEC-1841`
requirement is about a **deployment modal** — completely unrelated to
backfill/risk-tier classification.

**This is NOT a typical ζ' reassignment** (where the test covers the
current spec but the spec_id field got rewritten elsewhere). This is a
**spec-identity reuse**: `SPEC-1841` was renamed/repurposed between v3
and v4 without preserving test coverage continuity.

**Triage implication**: relinking the backfill tests to current SPEC-1841
would create false coverage for an unrelated deployment-UI requirement.
The safe default is to treat current SPEC-1841 as needing fresh test
evidence (create hygiene WI) and flag the identity-reuse pattern for
potential future owner review.

## Scope — 4 ζ' Specs (unchanged)

| Spec | Title | Reassigned to | Triage class |
|------|-------|---------------|--------------|
| SPEC-1841 | Deployment modal — pre-fill next version | SPEC-1771 | **(c) superseded** — historical test covers old meaning |
| SPEC-1869 | Intent Confidence Threshold | SPEC-1874 | (b) relink — current test covers current spec |
| SPEC-1870 | Source Attribution Display | SPEC-1874 | (b) relink |
| SPEC-1871 | Response Tone Presets | SPEC-1874 | (b) relink |

## Triage Method (revised — 4 branches, addresses F2)

For each ζ' spec `S` with reassigned test_id set:

1. **Open test file** and read function bodies for the reassigned tests.
2. **Read current spec versions** for both `S` and `now_owned_by`.
3. **Compare semantic coverage** against current spec versions.
4. **Classify into one of 4 branches**:

| Branch | Criteria | Action |
|--------|----------|--------|
| **(a) Subsumed** | Test clearly covers `now_owned_by`'s current behavior; `S` is redundant | Retire `S` with forwarding pointer |
| **(b) Relink** | Test still covers `S`'s current behavior (including `insert_test` with fresh test_id) | Create new test row with `spec_id=S.id`, fresh test_id, preserved metadata |
| **(c) Superseded** | Test covers an OLD meaning of `S`'s spec_id (pre-identity-reuse) | Create hygiene WI for `S`; flag for owner review |
| **(d) Ambiguous** | Cannot confidently decide | Escalate to owner decision |

## SPEC-1841 Disposition (branch (c))

**Decision**: Create hygiene WI for `SPEC-1841` per Stream D pattern.
Do not relink to `tests/quality_metrics/test_backfill_untested.py`.

**Rationale**: Current SPEC-1841 requirement (deployment modal pre-fill)
has no test coverage in the repo. Historical backfill tests exercise a
different spec meaning. A fresh deployment-modal test would be needed to
cover SPEC-1841 properly — that work is out of Stream B's scope and
tracked via the new hygiene WI.

**WI template** (matches Stream D pattern):
```python
db.insert_work_item(
    id=next_wi_id,                            # e.g., "WI-3219"
    title="Test coverage gap: Deployment modal SHOULD pre-fill...",
    origin="hygiene",
    component="Backend",
    resolution_status="open",
    changed_by="prime_builder",
    change_reason=(
        "POR Step 16.C Stream B: SPEC-1841 spec-identity reuse pattern — "
        "historical test tests/quality_metrics/test_backfill_untested.py "
        "covers old 'Untested Spec Backfill Program' meaning (v1-v3), not "
        "current 'Deployment modal' requirement (v4-v5). Fresh test evidence "
        "required per GOV-10."
    ),
    description=(
        "SPEC-1841's spec_id was reused between v3 and v4 for a different "
        "requirement. The historical test IDs TEST-10612..TEST-10621 exercise "
        "the old backfill/risk-tier classifier at "
        "tests/quality_metrics/test_backfill_untested.py and are now "
        "legitimately owned by SPEC-1771 (admin API tests). Current SPEC-1841 "
        "(deployment modal pre-fill UI) needs a fresh test suite. This WI "
        "tracks that gap."
    ),
    source_spec_id="SPEC-1841",
    priority="low",
    stage="created",
)
```

**Ancillary finding for owner review**: The pattern "spec_id reused between
v3 and v4 for semantically different requirement" is a distinct data-quality
issue from the ζ' reassignment pattern. It's a **spec identity-reuse**
issue, not a test identity-reuse issue. Flagged for potential future owner
review; not a blocker for Stream B.

## Relink Safety for SPEC-1869/1870/1871 (addresses F3)

For the 3 branch (b) specs, the implementation must:

1. **NOT mutate** current `TEST-11003`–`TEST-11020` rows (those legitimately
   belong to `SPEC-1874` now).
2. **Allocate fresh test IDs** sequentially from `max(TEST-NNNN) + 1`.
3. Insert new test rows with `spec_id=<original ζ' spec>`, preserving the
   historical metadata (title, test_type, expected_outcome, test_file,
   test_function, description).
4. Run the test via pytest to establish fresh `last_result` and
   `last_executed_at`.
5. Record {old test_id → new test_id} mapping per spec in the post-impl
   report.

## Implementation Plan

1. **Load inventory + target ζ' set** (4 specs).
2. **Per-spec classification loop**:
   - SPEC-1841: classify as (c); skip to step 3b.
   - SPEC-1869/1870/1871: classify as (b); proceed to step 3a.
3a. **Branch (b) — relink with fresh test_id** (for 1869/1870/1871):
   - Read historical row metadata (12 fields per Stream A -005 method).
   - Allocate new test_id.
   - Run pytest on historical nodeid.
   - `insert_test()` with `spec_id=<original>` and fresh test_id.
3b. **Branch (c) — create hygiene WI** (for 1841):
   - Allocate new wi_id.
   - `insert_work_item()` with the template above.
4. **Post-condition check**: all 4 ζ' specs have terminal dispositions.
5. **DB hash bracket + mutation audit**.
6. **Classifier rerun**: confirm ζ' count reduction.

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | Up to ~18 new `tests` rows (relinks for 3 specs), 1 new `work_items` row (SPEC-1841 WI), corresponding `pipeline_events.test_created` + `wi_created` audit rows |
| `independent-progress-assessments/spec-hygiene/scripts/stream_b_zeta_triage.py` | New | Implementation script |
| Triage log | In post-impl report | Per-spec decision with code excerpts + rationale |

## Exit Criteria

1. **All 4 ζ' specs** have a terminal bucket:
   - 3 `relinked` (SPEC-1869/1870/1871 — with fresh test_ids + pytest results)
   - 1 `wi_created_superseded` (SPEC-1841 — new hygiene WI)
2. **No current TEST-11003–TEST-11020 rows mutated** (SPEC-1874 preserved).
3. **Post-impl report** includes:
   - Per-spec triage decision + branch (a/b/c/d)
   - {old test_id → new test_id} mapping for branch (b) specs
   - New WI ID for SPEC-1841 (branch c)
   - Pytest output for branch (b) tests (pass/fail/skip)
   - DB hash bracket + mutation audit
4. **Classifier rerun**: ζ' count goes from 4 → 0 (or 4 → 1 if SPEC-1841
   stays ζ'-flagged via classifier; depends on classifier's definition of
   ζ' vs "has open hygiene WI").

## Ancillary Findings Spun Off

1. **SPEC-1841 identity-reuse pattern**: spec_id reused for semantically
   different requirement. Post-impl report documents for potential owner
   review. Not in Stream B scope.
2. **Schema invariant proposal** (carry-over from 16.B methodology):
   forbid spec_id changes on test rows — would prevent ζ' test-id
   reassignment entirely. Tracked separately, not in Stream B scope.

## Reconciliation Against Umbrella

Umbrella requires: "Stream B: 4 ζ' specs have a terminal decision (re-linked,
new test, or retired)." Revision satisfies this with the 4-branch taxonomy:
3 relinks + 1 hygiene WI = 4 terminal decisions, all covered.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
