# Phase 3: F7 + F5 — REVISED v2 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -004)

## NO-GO -004 Resolutions

### Finding 1: F5 confirm must create a KB spec → FIXED

**Resolution:** Revised capture/confirm workflow:

**capture_requirement()** stores proposed spec fields in structured content:
```python
content = json.dumps({
    "intake_type": "requirement_candidate",
    "intake_status": "pending",
    "spec_id": spec_id,           # target spec section/context
    "requirement_text": text,
    "proposed_title": title,      # for new spec creation on confirm
    "proposed_section": section,
    "proposed_scope": scope,
    "captured_at": _now(),
    "confirmed_spec_id": None,
    "rejection_reason": None,
})
```

**confirm_intake()** creates the spec via `insert_spec()` and records the ID:
1. Parse deliberation content
2. Call `db.insert_spec(id=next_id, title=proposed_title, section=proposed_section, ...)`
3. Patch content: `intake_status="confirmed"`, `confirmed_spec_id=created_id`
4. Update deliberation `outcome="owner_decision"`
5. Return created spec + impact analysis + constraints

**Test coverage:** Roundtrip test proves `capture → confirm → spec exists in KB → confirmed_spec_id populated`.

### Finding 2: F5 adoption chain still incomplete → FIXED

**Additional file touchpoints:**
- `docs/reference/templates.md`: Add `intake-classifier.py` to hook reference
- `docs/guides/upgrading.md`: Add F5 migration instructions

**Additional tests:**
- CLI smoke for `gt intake confirm` (Click runner)
- CLI smoke for `gt intake reject` (Click runner)
- Redaction test: capture requirement containing credential pattern →
  stored content is redacted → intake filter still identifies it →
  confirm/reject still works on redacted content

### Finding 3: F7 snapshot should include get_summary() + current-vs-last delta → FIXED

**Revised snapshot data structure:**
```python
{
    "lifecycle_metrics": db.get_lifecycle_metrics(),
    "summary": db.get_summary(),
    "quality_distribution": db.get_quality_distribution(),
    "constraint_coverage": db.get_constraint_coverage(),
    "captured_at": _now(),
}
```

**Revised compute_session_delta():**
```python
def compute_session_delta(
    self,
    current_session: str | None = None,
) -> dict[str, Any]:
```

When `current_session` is None: computes live DB state vs most recent stored
snapshot (the approved session-start use case). When `current_session` is
provided: computes that snapshot vs the previous one (trend analysis).

Returns `{"current": dict, "previous": dict, "deltas": dict, "no_prior": bool}`.
When no prior snapshot exists: `no_prior=True`, deltas empty (graceful degradation).

**gt health:** Shows current state + delta from last snapshot (using
`compute_session_delta(current_session=None)`).

### Finding 4: F7 import validation for malformed snapshot JSON → FIXED

**Import validation:** In the import path, validate `session_snapshots.data` as
parseable JSON. Non-merge mode: raise `click.ClickException`. Merge mode: skip
row, emit warning. Same pattern as F3's `spec_quality_scores.flags` validation.

**Negative test:** Import with malformed `data` field → row rejected, DB clean.

---

## Revised F7 Spec (13 tests)

### New Table

```sql
CREATE TABLE IF NOT EXISTS session_snapshots (
    session_id TEXT NOT NULL PRIMARY KEY,
    captured_at TEXT NOT NULL,
    data TEXT NOT NULL
);
```

### Methods

```python
KnowledgeDB.capture_session_snapshot(session_id: str) -> dict
KnowledgeDB.get_session_snapshot(session_id: str) -> dict | None
KnowledgeDB.get_snapshot_history(limit: int = 10) -> list[dict]
KnowledgeDB.compute_session_delta(current_session: str | None = None) -> dict
```

### File Touchpoints

- `src/groundtruth_kb/db.py`: schema, 4 methods, export table list
- `src/groundtruth_kb/health.py`: NEW — DEFAULT_THRESHOLDS, render_health_text()
- `src/groundtruth_kb/cli.py`: `gt health` group (3 subcommands), _IMPORTABLE_TABLES, import validation
- `templates/hooks/session-health.py`: NEW
- `tests/test_health.py`: NEW — 13 tests

### Tests

1. Snapshot capture — stores lifecycle + summary + quality + coverage
2. Snapshot includes get_summary() data
3. Delta: current-vs-last (no prior session → graceful no_prior=True)
4. Delta: current-vs-last with prior snapshot → deltas computed
5. Delta: explicit session-vs-previous for trends
6. Alert generation — metric above threshold triggers ALERT
7. Text rendering — non-empty well-formed output
8. Graceful degradation — empty DB, no crash
9. Threshold storage via env_config
10. Threshold default fallback
11. Snapshot export/import roundtrip
12. Malformed snapshot JSON import rejected
13. Hook template exists and is valid Python

---

## Revised F5 Spec (18 tests)

### No New Tables

### File Touchpoints

- `src/groundtruth_kb/intake.py`: NEW — 5 API functions
- `src/groundtruth_kb/cli.py`: `gt intake` group (5 subcommands)
- `src/groundtruth_kb/project/doctor.py`: `_check_settings_classifiers()`
- `src/groundtruth_kb/project/upgrade.py`: `_MANAGED_HOOKS` + intake hook
- `src/groundtruth_kb/project/scaffold.py`: settings.local.json
- `templates/hooks/intake-classifier.py`: NEW
- `docs/reference/templates.md`: hook reference update
- `docs/guides/upgrading.md`: F5 migration instructions
- `tests/test_intake.py`: NEW — 18 tests

### Tests

1. Classify basic — matching spec returned
2. Classify no match — empty list
3. Capture stores deliberation with intake discriminator + proposed spec fields
4. Confirm creates spec in KB + records confirmed_spec_id
5. Confirm returns impact analysis
6. Confirm returns constraints
7. Reject updates outcome + intake_status + reason
8. Reject reason required
9. List pending — filters by intake_type + pending status
10. List all intakes — excludes non-intake deliberations
11. Non-intake deliberation excluded from list
12. Double confirm idempotent
13. Roundtrip: classify → capture → confirm → spec exists
14. Redaction: credential in requirement stored redacted, intake still filterable
15. CLI smoke: `gt intake list`
16. CLI smoke: `gt intake confirm`
17. CLI smoke: `gt intake reject`
18. Legacy spec-classifier.py backward compatibility (doctor)

---

## Implementation Order

1. F7 first (13 tests)
2. F5 second (18 tests)

## Verification Plan

1. `python -m pytest -q` (509 → ~540 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Tests | Lines |
|---------|-----------|-------|-------|
| F7 | 2 (health.py, hook) + 1 test | 13 | ~600 |
| F5 | 2 (intake.py, hook) + 1 test | 18 | ~800 |
| **Total** | **6 new, 5+ modified** | **31** | **~1400** |

## Request

Codex review requested. GO authorizes Phase 3 implementation.
