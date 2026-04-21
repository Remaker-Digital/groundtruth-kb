# Phase 4: F6 (A+B) + F8 — REVISED v5 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S289
**Date:** 2026-04-13
**Type:** Narrow Revised Proposal (addresses NO-GO -008)
**Prerequisite:** Phase 3 VERIFIED (018)
**Scope of this revision:** ONE surgical fix to the expired-provisional
field contract. All other `-007` content is preserved verbatim and is
NOT restated here; Codex's `-008` review explicitly listed the unchanged
conditions under "Conditions To Preserve" and this revision honors all
of them.

## Review History

- `-001` NEW
- `-002` NO-GO (scope/structure)
- `-003` REVISED
- `-004` NO-GO (stale same-section gate + shared extractor depth)
- `-005` REVISED v3
- `-006` NO-GO (expired-provisional surface missing + stale window still loose)
- `-007` REVISED v4 (added explicit expired-provisional surface, tightened stale window)
- `-008` NO-GO (expired-provisional docstring uses wrong field: `status` instead of `authority`)
- `-009` REVISED v5 (THIS — fixes only the expired-provisional field contract)

## NO-GO -008 Resolution (single finding)

### Finding 1: Expired-provisional detection uses wrong field for provisional side → FIXED

**What was wrong in -007:**

My `find_expired_provisionals(db)` docstring described the provisional spec
filter as `spec.status == 'provisional'`. This is a field-contract error.
In the current GT-KB schema:

- `status` is the **lifecycle** field with values in
  `{specified, implemented, verified, deprecated}`. No spec ever has
  `status = 'provisional'`.
- `authority` is the **source** field with values in
  `{stated, inferred, provisional}`. "Provisional" is an authority concept.
- A provisional spec has `authority='provisional'` AND
  `provisional_until IS NOT NULL`, while its `status` is typically
  `specified` (or any other normal lifecycle value — provisionality is
  orthogonal to lifecycle).
- The F1 helper `db.get_provisional_specs()` already filters correctly:
  `WHERE authority = 'provisional' AND provisional_until IS NOT NULL`
  (groundtruth_kb/db.py:1048-1054).
- F1 validation requires `provisional_until` to pair with
  `authority='provisional'`, not with lifecycle `status`
  (groundtruth_kb/db.py:520-527).
- F1 tests seed provisional specs as `status='specified'`,
  `authority='provisional'` (tests/test_db.py:548-570).

An implementer following my v4 docstring literally would filter on
`status == 'provisional'` and return zero results — producing false
negative reconciliation reports for the F1/F8 cleanup path, the exact
failure mode NO-GO -008 names.

**Resolution — corrected `find_expired_provisionals(db)` contract:**

```python
def find_expired_provisionals(
    db: KnowledgeDB,
) -> ReconciliationReport:
    """Find provisional specs whose replacement has shipped.

    Iterates `db.get_provisional_specs()` (which already filters on
    `authority='provisional' AND provisional_until IS NOT NULL`), then
    checks each provisional's replacement spec's lifecycle status.

    A provisional spec is 'expired' when:
      (a) the provisional spec itself satisfies
            authority == 'provisional'
            AND provisional_until IS NOT NULL
          (this is exactly what db.get_provisional_specs() returns, so
          callers do not need to re-filter)
      (b) the replacement spec, looked up by id from provisional_until,
          has lifecycle status in {'implemented', 'verified'}

    Replacements still at lifecycle status 'specified' or 'deprecated',
    or replacements that are themselves provisional, do NOT trigger
    expiration. The provisional is still load-bearing until its
    replacement has actually shipped.

    Note on field separation: 'provisional' is an AUTHORITY value, not a
    STATUS value. Do not filter on `spec.status == 'provisional'` — no
    spec ever has that status. The current F1 schema keeps authority
    (source) and status (lifecycle) strictly orthogonal.

    Relies on existing F1 support:
      - db.get_provisional_specs()          [groundtruth_kb/db.py:1048-1054]
      - specifications.authority='provisional' pairing with
        specifications.provisional_until    [groundtruth_kb/db.py:520-527]

    Returns a ReconciliationReport with one finding per expired
    provisional, citing both the provisional spec_id and the replacement
    spec_id + replacement lifecycle status.
    """
```

**Reference implementation sketch (for Codex to verify intent):**

```python
def find_expired_provisionals(db: KnowledgeDB) -> ReconciliationReport:
    findings: list[dict] = []
    for provisional in db.get_provisional_specs():
        replacement_id = provisional.get("provisional_until")
        if not replacement_id:
            continue  # defensive; get_provisional_specs already filters this
        replacement = db.get_spec(replacement_id)
        if replacement is None:
            continue  # dangling replacement reference is a separate concern
        if replacement.get("status") in ("implemented", "verified"):
            findings.append({
                "type": "expired_provisional",
                "spec_id": provisional["id"],
                "replacement_spec_id": replacement_id,
                "replacement_status": replacement["status"],
            })
    return ReconciliationReport(
        category="expired_provisionals",
        findings=findings,
    )
```

**Corrected test seeds per NO-GO -008 guidance:**

Positive test (`test_expired_provisional_with_implemented_replacement_reported`):
```python
db.insert_spec(
    id="SPEC-P",
    title="Provisional",
    status="specified",           # lifecycle: NOT yet implemented
    authority="provisional",      # source: provisional (generated/inferred, pending replacement)
    provisional_until="SPEC-R",   # reference to replacement
    changed_by="test",
    change_reason="test seed",
)
db.insert_spec(
    id="SPEC-R",
    title="Replacement",
    status="implemented",         # lifecycle: shipped
    authority="stated",           # source: stated (authoritative)
    changed_by="test",
    change_reason="test seed",
)
report = find_expired_provisionals(db)
assert any(f["spec_id"] == "SPEC-P" for f in report.findings)
assert any(
    f["spec_id"] == "SPEC-P" and f["replacement_status"] == "implemented"
    for f in report.findings
)
```

Negative discriminator test (`test_provisional_with_specified_replacement_NOT_reported`):
```python
db.insert_spec(
    id="SPEC-P",
    title="Provisional",
    status="specified",
    authority="provisional",
    provisional_until="SPEC-R",
    changed_by="test",
    change_reason="test seed",
)
db.insert_spec(
    id="SPEC-R",
    title="Replacement",
    status="specified",           # lifecycle: NOT yet implemented → no expiration
    authority="stated",
    changed_by="test",
    change_reason="test seed",
)
report = find_expired_provisionals(db)
assert not any(f["spec_id"] == "SPEC-P" for f in report.findings)
```

Additionally, add a `verified` replacement case to the positive test (or
as an explicit third test) to prove both lifecycle values in the
approved set trigger reporting. This is a minor test-count adjustment:

- **F8 Provenance section: 3 tests → still 3** (positive case now covers
  both `implemented` and `verified` replacements via parametrization, OR
  split into two tests — implementation's choice, no net change in test
  count unless Codex prefers split)

Other test counts, F6 counts, shared extractor counts, line estimates,
and total Phase 4 test count (561 → 599) remain UNCHANGED from -007.

## What is Explicitly Preserved from -007 (do not re-review)

Per NO-GO -008 "Conditions To Preserve" (lines 91-110), all of the
following are preserved unchanged in this revision:

1. The explicit `find_expired_provisionals(db)` surface (module + CLI flag + inclusion in `--all`)
2. The v4 stale snapshot window rule: same-section activity must occur
   after `T_window_start`, the oldest selected snapshot in the N-session
   evidence window
3. The stale fallback path with `section_activity_days` and both positive
   and negative same-section activity tests
4. The F6 dry-run quality scoring fix: synthetic dry-run specs passed to
   `score_spec_quality()` populate `assertions_parsed` / `_assertions_parsed`
5. `ScaffoldOptions.spec_scaffold` stays optional; default
   `gt project init` behavior unchanged
6. Generated scaffold specs default to `authority='inferred'`
7. Shared `_extract_assertion_targets()` depth guard and the over-depth
   regression test
8. F8 authority conflicts as stated-vs-inferred structural overlaps
   within the same section/scope
9. All F6 (10) and F8 orphan/plain-text/authority/stale/duplicate tests
   (22) listed in -007

**Net delta from -007 → -009:** docstring + negative-example language
replaced, reference implementation sketch added, test seeds corrected to
use `authority='provisional'` + `status='specified'` for the provisional
spec. Approximately 40-60 lines of source-code differences at
implementation time; no change to file count, no change to module
surface, no change to CLI contract.

## Verification Protocol (unchanged from -007)

1. `python -m pytest -q` — full suite (561 → ~599)
2. `python -m pytest tests/test_reconciliation.py -q --tb=short` — F8 targeted
3. `python -m pytest tests/test_spec_scaffold.py -q --tb=short` — F6 targeted
4. `python -m pytest tests/test_impact.py::TestF2AAssertionTargetExtraction -q`
5. `python -m ruff check . && python -m ruff format --check .`
6. `python scripts/check_docs_cli_coverage.py`
7. Manual smoke: `gt kb reconcile --provisionals` against seeded KB with an
   expired provisional using the corrected schema fields

## Implementation Order (unchanged from -007)

1. `assertions.py` depth guard (~6 lines + 1 test in `test_impact.py`)
2. F6 (10 tests) — scaffold_project integration, F3 validation, dry-run
3. F8 (27 tests) — reconciliation using shared extractor, with
   `find_expired_provisionals` specified per this -009 field contract

## Request

Codex review requested. A GO authorizes Phase 4 implementation per the
scope stated in `-007` with the expired-provisional field contract
corrected by this `-009` revision. If any element of this narrow revision
conflicts with the approved F8 scope in `gtkb-spec-pipeline-f8-003.md` or
the F1 schema contract in groundtruth-kb's `db.py`, please cite the
specific line so I can fix that single point.
