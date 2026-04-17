# Phase 3: F7 + F5 — REVISED v4 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -008)

## NO-GO -008 Resolutions

### Finding 1: F5 confidence must be numeric float → FIXED

**Resolution:** `classify_requirement()` returns `confidence: float` in `[0.0, 1.0]`.

Classification algorithm:
- Count strong indicators per category (keyword/pattern matches)
- Assign confidence: 2+ strong indicators ��� 0.9, 1 strong → 0.7, ambiguous → 0.3
- Strongest category wins; ties resolved by priority order (directive > constraint > preference > question > exploration)

Persisted candidate stores `"confidence": 0.9` (numeric).
Tests assert `confidence > 0.8` for clear directive, `confidence < 0.5` for exploration.
Optional `confidence_label` derived field for display only (not persisted).

### Finding 2: F5 v10 adoption regression tests missing → FIXED

**Resolution:** Added the full v10 test set. Updated F5 test count from 20 → 30.

New adoption tests (10 additional):
- Scaffold bridge-profile activation — settings.local.json includes intake hook
- Scaffold local-only activation — settings.local.json omits intake hook
- Doctor only-intake active — passes (intake without spec-classifier is valid)
- Doctor only-spec active — passes (legacy backward compat)
- Doctor both active — warns (redundant classifiers)
- Doctor neither active — warns (gap)
- Doctor malformed JSON settings — warns without crash
- Doctor local-only no-false-warning — no settings file, no warning
- Upgrade copy — intake hook copied to target
- Upgrade preserve — existing hooks preserved alongside new intake hook

### Finding 3: F7 snapshot write contract not stated → FIXED

**Resolution:** Explicit write contract:

`capture_session_snapshot()` uses `INSERT OR REPLACE INTO session_snapshots`.
When the same `session_id` is captured twice (e.g., session start then session
end), the second capture replaces the first. This is the latest-snapshot
replacement contract from the cross-check.

**Test:** Capture S1, capture S1 again with more specs → only one row for S1,
contains the latest data.

---

## Complete F7 Spec (14 tests)

### Table + Write Contract

```sql
CREATE TABLE IF NOT EXISTS session_snapshots (
    session_id TEXT NOT NULL PRIMARY KEY,
    captured_at TEXT NOT NULL,
    data TEXT NOT NULL
);
```

Write: `INSERT OR REPLACE INTO session_snapshots`. Same session_id replaces.

### Snapshot Data

```python
{
    "lifecycle_metrics": db.get_lifecycle_metrics(),
    "summary": db.get_summary(),
    "quality_distribution": db.get_quality_distribution(),
    "constraint_coverage": db.get_constraint_coverage(),
    "captured_at": _now(),
}
```

### Thresholds (existing lifecycle metric IDs)

```python
DEFAULT_THRESHOLDS = {
    "M6_max": 0.25, "M11_max": 0.01, "M12_max": 0.15,
    "M16_min": 0.60, "M17_max": 0.50, "M18_max": 0,
}
```

### Methods

- `capture_session_snapshot(session_id)` — INSERT OR REPLACE
- `get_session_snapshot(session_id)` — retrieve one
- `get_snapshot_history(limit=10)` — ordered list
- `compute_session_delta(current_session=None)` — live-vs-last or snapshot-vs-previous

### CLI

- `gt health` — current state + delta from last snapshot
- `gt health snapshot <session_id>` — capture and display
- `gt health trends` — last N snapshots with deltas

### Files

- `src/groundtruth_kb/db.py`: schema, 4 methods, export table list
- `src/groundtruth_kb/health.py`: NEW — thresholds, render_health_text()
- `src/groundtruth_kb/cli.py`: `gt health` group, _IMPORTABLE_TABLES, import validation
- `templates/hooks/session-health.py`: NEW
- `tests/test_health.py`: NEW

### Tests

1. Snapshot capture — stores lifecycle + summary + quality + coverage
2. Snapshot includes get_summary() data
3. Same-session replacement — capture twice, one row, latest data
4. Delta: current-vs-last with no prior → no_prior=True
5. Delta: current-vs-last with prior → deltas computed
6. Delta: explicit session-vs-previous for trends
7. Alert generation — metric above threshold
8. Text rendering — non-empty output
9. Graceful degradation — empty DB
10. Threshold storage via env_config
11. Threshold default fallback
12. Snapshot export/import roundtrip
13. Malformed snapshot JSON import rejected
14. Hook template exists and is valid Python

---

## Complete F5 Spec (30 tests)

### Intake API (intake.py)

- `classify_requirement(db, text)` — intent classification (directive/constraint/preference/question/exploration) with numeric confidence + related_specs advisory
- `capture_requirement(db, text, *, proposed_title, proposed_section, proposed_scope=None, proposed_type="requirement", proposed_authority="stated")` — stores candidate deliberation
- `confirm_intake(db, deliberation_id)` — creates spec, records confirmed_spec_id
- `reject_intake(db, deliberation_id, reason)` — marks rejected
- `list_intakes(db, *, pending_only=False)` — filters by intake_type discriminator

### Candidate Payload

```python
{
    "intake_type": "requirement_candidate",
    "intake_status": "pending"|"confirmed"|"rejected",
    "raw_text": str,
    "classification": str,
    "confidence": float,  # 0.0-1.0
    "related_specs": [str],
    "proposed_title": str,
    "proposed_section": str,
    "proposed_scope": str | None,
    "proposed_type": str,
    "proposed_authority": str,
    "captured_at": str,
    "confirmed_spec_id": str | None,
    "rejection_reason": str | None,
}
```

### Files

- `src/groundtruth_kb/intake.py`: NEW
- `src/groundtruth_kb/cli.py`: `gt intake` group (5 subcommands)
- `src/groundtruth_kb/project/doctor.py`: `_check_settings_classifiers()`
- `src/groundtruth_kb/project/upgrade.py`: `_MANAGED_HOOKS` + intake hook
- `src/groundtruth_kb/project/scaffold.py`: settings.local.json
- `templates/hooks/intake-classifier.py`: NEW
- `docs/reference/templates.md`: hook reference
- `docs/guides/upgrading.md`: migration instructions
- `tests/test_intake.py`: NEW

### Tests

**Core intake (13):**
1. Classify directive — confidence > 0.8
2. Classify exploration — confidence < 0.5
3. Classify question — "?" detected
4. Classify constraint — "must not" detected
5. Classify ambiguous → exploration, low confidence
6. Classify with related specs populated
7. Capture stores full candidate (classification, confidence, raw_text, proposed_type, proposed_authority)
8. Confirm creates spec with proposed_type/authority, records confirmed_spec_id
9. Confirm with default type/authority when absent
10. Confirm returns impact + constraints
11. Reject stores reason, updates status
12. Reject reason required
13. Roundtrip: classify → capture → confirm → spec exists with correct type/authority

**List/filter (3):**
14. List pending — only pending intakes
15. List all — excludes non-intake deliberations
16. Double confirm idempotent

**Redaction + CLI (4):**
17. Redaction: credential in requirement stored redacted, still filterable
18. CLI smoke: `gt intake list`
19. CLI smoke: `gt intake confirm`
20. CLI smoke: `gt intake reject`

**Adoption chain (10):**
21. Scaffold bridge-profile — settings includes intake hook
22. Scaffold local-only — settings omits intake hook
23. Doctor only-intake active — passes
24. Doctor only-spec active — passes (backward compat)
25. Doctor both active — warns
26. Doctor neither active — warns
27. Doctor malformed JSON settings — warns without crash
28. Doctor local-only no-false-warning
29. Upgrade copy — intake hook copied
30. Upgrade preserve — existing hooks preserved

---

## Implementation Order

1. F7 first (14 tests)
2. F5 second (30 tests)

## Verification

1. `python -m pytest -q` (509 → ~553 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Request

Codex review requested. GO authorizes Phase 3 implementation.
