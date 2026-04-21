# Phase 3: F7 + F5 — REVISED Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -002)

## NO-GO Resolutions

### Finding 1: F7 redefines existing metric IDs → FIXED

**Resolution:** F7 snapshots `get_lifecycle_metrics()` directly for all M* values.
Quality distribution (F3) and constraint coverage (F4) are stored under separate
snapshot keys, not as redefined M* metrics.

**Snapshot data structure:**
```python
{
    "lifecycle_metrics": db.get_lifecycle_metrics(),  # M2, M4, M6, M10-M18
    "quality_distribution": db.get_quality_distribution(),  # from F3
    "constraint_coverage": db.get_constraint_coverage(),  # from F4
    "captured_at": _now(),
}
```

**Thresholds** use the existing lifecycle metric IDs with their real semantics:
```python
DEFAULT_THRESHOLDS = {
    "M6_max": 0.25,   # defect injection rate
    "M11_max": 0.01,  # regression rate
    "M12_max": 0.15,  # spec retirement rate
    "M16_min": 0.60,  # verified with passing tests
    "M17_max": 0.50,  # stale test ratio
    "M18_max": 0,     # implemented without tests
}
```

### Finding 2: F7 omits delta, CLI, hook template → FIXED

**Resolution:** Full approved F7 surface restored:

**API:**
- `capture_session_snapshot(session_id)` — snapshots lifecycle + quality + coverage
- `get_session_snapshot(session_id)` — retrieve one snapshot
- `get_snapshot_history(limit=10)` — ordered list
- `compute_session_delta(session_id_a, session_id_b)` — diff two snapshots

**CLI:** `gt health` group with subcommands:
- `gt health` — current snapshot + threshold alerts
- `gt health snapshot <session_id>` — capture and display
- `gt health trends` — last N snapshots with deltas

**Hook template:** `templates/hooks/session-health.py` — captures snapshot on
session start/end via `Stop` event.

**Rendering:** `render_health_text(snapshot, thresholds=None)` — text report
with metric values, threshold comparison, PASS/WARN/ALERT per metric.

### Finding 3: F5 omits hook/scaffold/doctor/upgrade chain → FIXED

**Resolution:** Full approved F5 adoption chain restored:

**Hook template:** `templates/hooks/intake-classifier.py` — `UserPromptSubmit`
hook that classifies owner input against active specs.

**Settings template:** Update `templates/project/settings.local.json` to include
intake hook in `classifiers.hooks.UserPromptSubmit`.

**Scaffold:** Bridge profile generates `settings.local.json` with intake hook;
local-only profile omits it.

**Doctor:** `_check_settings_classifiers(target)` inside the `if p.includes_bridge:`
block. Warns when: both classifiers active (redundant), neither active (gap),
malformed JSON/hooks. Legacy `spec-classifier.py` without intake passes (backward
compatible).

**Upgrade:** Add `intake-classifier.py` to `_MANAGED_HOOKS`. Upgrade planner
copies hook, preserves existing hooks, handles local-only allowlist.

**CLI:** `gt intake classify|capture|confirm|reject|list` subcommands.

### Finding 4: F5 intake discriminator missing → FIXED

**Resolution:** Structured content with intake discriminator:

```python
content = json.dumps({
    "intake_type": "requirement_candidate",
    "intake_status": "pending",  # "pending" | "confirmed" | "rejected"
    "spec_id": spec_id,
    "requirement_text": text,
    "captured_at": _now(),
    "rejection_reason": None,  # populated on reject
})
```

**list_intakes():** Queries `source_type="owner_conversation"`, then filters by
parsing `content` JSON and checking `intake_type == "requirement_candidate"`.
Skips malformed/non-intake rows deterministically.

**confirm_intake():** Updates deliberation `outcome` to `"owner_decision"` and
patches `content` JSON to set `intake_status="confirmed"`.

**reject_intake():** Updates deliberation `outcome` to `"no_go"` and patches
`content` JSON to set `intake_status="rejected"` + `rejection_reason`.

---

## Revised F7 Spec (11 tests)

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
KnowledgeDB.compute_session_delta(session_a: str, session_b: str) -> dict
```

### File Touchpoints

- `src/groundtruth_kb/db.py`: schema, 4 methods, export table list
- `src/groundtruth_kb/health.py`: NEW — DEFAULT_THRESHOLDS, render_health_text()
- `src/groundtruth_kb/cli.py`: `gt health` group (3 subcommands), _IMPORTABLE_TABLES
- `templates/hooks/session-health.py`: NEW — hook template
- `tests/test_health.py`: NEW — 11 tests

### Tests

1. Snapshot capture — stores lifecycle + quality + coverage data
2. Delta computation — capture S1, add specs, capture S2, verify metric deltas
3. Alert generation — M18 above threshold triggers ALERT
4. Text rendering — non-empty well-formed output
5. Graceful degradation — empty DB, no crash
6. Threshold storage via env_config — store and retrieve
7. Threshold default fallback — no config → DEFAULT_THRESHOLDS
8. Threshold update — store, update, verify latest
9. Snapshot export/import roundtrip
10. CLI `gt health snapshot` produces output (Click testing)
11. Hook template exists and is syntactically valid Python

---

## Revised F5 Spec (15 tests)

### No New Tables

Uses `deliberations` with structured `content` discriminator.

### File Touchpoints

- `src/groundtruth_kb/intake.py`: NEW — 5 API functions
- `src/groundtruth_kb/cli.py`: `gt intake` group (5 subcommands)
- `src/groundtruth_kb/project/doctor.py`: `_check_settings_classifiers()` in bridge block
- `src/groundtruth_kb/project/upgrade.py`: `_MANAGED_HOOKS` + intake hook
- `src/groundtruth_kb/project/scaffold.py`: settings.local.json with intake hook
- `templates/hooks/intake-classifier.py`: NEW — hook template
- `tests/test_intake.py`: NEW — 15 tests

### Tests

1. Classify basic — matching spec returned
2. Classify no match — empty list
3. Capture stores deliberation with intake discriminator
4. Confirm updates outcome + intake_status
5. Reject updates outcome + intake_status + reason
6. List pending — filters by intake_type + pending status
7. List all intakes — returns all intake records, not other deliberations
8. Non-intake deliberation excluded from list
9. Confirm shows impact analysis (F2 integration)
10. Confirm shows constraints (F4 integration)
11. Roundtrip: classify → capture → confirm
12. Reject reason required
13. Double confirm idempotent
14. CLI `gt intake list` smoke test
15. Legacy spec-classifier.py backward compatibility (doctor passes)

---

## Implementation Order

1. F7 first (11 tests) — self-contained table + API + CLI + hook
2. F5 second (15 tests) — intake API + CLI + adoption chain

## Verification Plan

1. `python -m pytest -q` (509 → ~535 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Tests | Lines |
|---------|-----------|-------|-------|
| F7 | 2 (health.py, hook) + 1 test | 11 | ~500 |
| F5 | 2 (intake.py, hook) + 1 test | 15 | ~600 |
| **Total** | **6 new, 4 modified** | **26** | **~1100** |

## Request

Codex review requested. GO authorizes Phase 3 implementation.
