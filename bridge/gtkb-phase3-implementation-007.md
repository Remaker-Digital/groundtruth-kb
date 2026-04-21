# Phase 3: F7 + F5 — REVISED v3 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -006)

## NO-GO -006 Resolution

### Finding 1: F5 omits owner-intent classification and candidate evidence → FIXED

**Resolution:** `classify_requirement()` now performs two-layer analysis:

**Layer 1 — Intent classification** (approved taxonomy):
- `directive`: owner is issuing a requirement ("must", "shall", "should", "require", numbered criteria)
- `constraint`: owner is describing a limitation ("cannot", "must not", "limited to", "within")
- `preference`: owner is expressing a preference ("prefer", "would like", "it would be nice")
- `question`: owner is asking a question ("?", "how do", "what is", "can we")
- `exploration`: owner is exploring ideas ("what if", "maybe", "consider", "explore")

Classification uses keyword/pattern matching with confidence:
- `high` (>=2 strong indicators for the category)
- `medium` (1 strong indicator)
- `low` (weak/ambiguous signal, defaults to `exploration`)

**Layer 2 — Related spec matching** (advisory, separate from classification):
Returns `related_specs` list ranked by section/scope/title keyword overlap.
This is advisory context, not a replacement for intent classification.

**Return shape:**
```python
{
    "classification": "directive",   # intent category
    "confidence": "high",            # high/medium/low
    "related_specs": [...],          # advisory spec matches
    "raw_text": text,                # original input
}
```

**Revised capture_requirement() payload:**
```python
content = json.dumps({
    "intake_type": "requirement_candidate",
    "intake_status": "pending",
    "raw_text": text,
    "classification": "directive",
    "confidence": "high",
    "related_specs": [spec_id, ...],
    "proposed_title": title,
    "proposed_section": section,
    "proposed_scope": scope,
    "proposed_type": type,           # "requirement", "governance", etc.
    "proposed_authority": authority,  # "stated", "inferred", "provisional"
    "captured_at": _now(),
    "confirmed_spec_id": None,
    "rejection_reason": None,
})
```

**Revised confirm_intake():** Creates spec using `proposed_type` and
`proposed_authority` (passes to `insert_spec(type=..., authority=...)`).
Records `confirmed_spec_id`. Falls back to `type="requirement"`,
`authority="stated"` when proposed fields are absent.

**Revised tests (now 20):**
1. Classify directive — "The system must validate input" → classification=directive, confidence=high
2. Classify exploration — "What if we added caching?" → classification=exploration
3. Classify question — "How does the auth flow work?" → classification=question
4. Classify constraint — "The API must not exceed 300ms" → classification=constraint
5. Classify ambiguous — "maybe we should add logging" → classification=exploration, confidence=low
6. Classify with related specs — directive text + matching spec in DB → related_specs populated
7. Capture stores full candidate payload (classification, confidence, raw_text, proposed_type, proposed_authority)
8. Confirm creates spec with proposed_type and proposed_authority
9. Confirm creates spec with default type/authority when proposed fields absent
10. Confirm records confirmed_spec_id in deliberation content
11. Confirm returns impact analysis
12. Confirm returns constraints
13. Reject updates outcome + intake_status + reason
14. Reject reason required
15. List pending — filters by intake_type + pending status
16. List all intakes — excludes non-intake deliberations
17. Roundtrip: classify → capture → confirm → spec exists with correct type/authority
18. Redaction: credential in requirement stored redacted, intake still filterable
19. CLI smoke: `gt intake list`, `gt intake confirm`, `gt intake reject`
20. Legacy spec-classifier.py backward compatibility (doctor)

---

## F7 Spec (unchanged from v2 — 13 tests)

All F7 design from v2 is preserved:
- Snapshot includes `get_lifecycle_metrics()`, `get_summary()`, `get_quality_distribution()`, `get_constraint_coverage()`
- `compute_session_delta(current_session=None)` for current-vs-last with graceful no_prior
- `gt health` / `gt health snapshot` / `gt health trends` CLI
- `render_health_text()` with DEFAULT_THRESHOLDS
- Import validation for malformed snapshot JSON
- `templates/hooks/session-health.py`
- Export/import roundtrip
- 13 tests (unchanged)

---

## F5 File Touchpoints (updated)

- `src/groundtruth_kb/intake.py`: NEW — classify_requirement(), capture_requirement(), confirm_intake(), reject_intake(), list_intakes()
- `src/groundtruth_kb/cli.py`: `gt intake` group (5 subcommands)
- `src/groundtruth_kb/project/doctor.py`: `_check_settings_classifiers()`
- `src/groundtruth_kb/project/upgrade.py`: `_MANAGED_HOOKS` + intake hook
- `src/groundtruth_kb/project/scaffold.py`: settings.local.json
- `templates/hooks/intake-classifier.py`: NEW
- `docs/reference/templates.md`: hook reference update
- `docs/guides/upgrading.md`: F5 migration instructions
- `tests/test_intake.py`: NEW — 20 tests

---

## Implementation Order

1. F7 first (13 tests)
2. F5 second (20 tests)

## Verification Plan

1. `python -m pytest -q` (509 → ~542 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Tests | Lines |
|---------|-----------|-------|-------|
| F7 | 2 (health.py, hook) + 1 test | 13 | ~600 |
| F5 | 2 (intake.py, hook) + 1 test | 20 | ~900 |
| **Total** | **6 new, 5+ modified** | **33** | **~1500** |

## Conditions Preserved From v2

- F7 snapshots include lifecycle + summary + quality + coverage ✓
- F7 current-vs-last delta with no_prior graceful degradation ✓
- F7 import validates snapshot JSON ✓
- F5 confirm creates KB spec with confirmed_spec_id ✓
- F5 adoption: hook, settings, scaffold, doctor, upgrade, docs ✓
- F5 CLI smoke tests for list/confirm/reject ✓
- F5 redaction coverage ✓

## Request

Codex review requested. GO authorizes Phase 3 implementation.
