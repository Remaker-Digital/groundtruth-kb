# Phase 3: F7 + F5 — Implementation Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Implementation Proposal
**Prerequisite:** Phase 2+2B VERIFIED (012, 006). F1-F4 all committed.
**Approved designs:** F7-005 (GO: F7-006), F5-019 (GO: F5-020)
**Cross-check:** gtkb-f1f8-cross-check-001 (GO: -002)

## Rationale

Phase 3 implements two features with no mutual dependency: F7 (Session Health
Dashboard) adds snapshot-based metrics, and F5 (Requirement Intake Pipeline) adds
a CLI-driven intake workflow. Both consume F1-F4 outputs (quality scores,
constraint coverage, impact analysis).

F7 is implemented first because it's self-contained (new table + API + rendering).
F5 is implemented second because it has more integration points (CLI commands,
doctor checks, scaffold hooks, upgrade tooling).

---

## F7: Session Health Dashboard

### New Table

```sql
CREATE TABLE IF NOT EXISTS session_snapshots (
    session_id TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    data TEXT NOT NULL,
    PRIMARY KEY (session_id)
);
```

Uses UPSERT (`INSERT OR REPLACE`) so session-end snapshot replaces session-start.

### Constants

```python
DEFAULT_THRESHOLDS = {
    "M6_max": 0.25,   # max fraction of specs without assertions
    "M11_max": 0.01,  # max assertion failure rate
    "M12_max": 0.15,  # max fraction of specs with failing assertions
    "M16_min": 0.60,  # min constraint coverage ratio
    "M17_max": 0.50,  # max fraction of specs without quality scores
    "M18_max": 0,     # max specs with zero executable assertions
}
```

### Methods

```python
KnowledgeDB.capture_session_snapshot(session_id: str) -> dict[str, Any]
KnowledgeDB.get_session_snapshot(session_id: str) -> dict[str, Any] | None
KnowledgeDB.get_snapshot_history(limit: int = 10) -> list[dict[str, Any]]
```

`capture_session_snapshot()` computes 6 metrics from current DB state:
- **M6:** Fraction of current specs without any assertions
- **M11:** Assertion failure rate from latest assertion runs
- **M12:** Fraction of specs with failing assertions
- **M16:** Constraint coverage ratio (from `get_constraint_coverage()`)
- **M17:** Fraction of specs without quality scores
- **M18:** Count of specs with zero executable assertions

Stores as JSON `data` blob in `session_snapshots`.

### Rendering

```python
def render_health_text(snapshot: dict[str, Any], thresholds: dict | None = None) -> str
```

Returns text report with metric values, threshold comparison, and PASS/WARN/ALERT
status per metric. Uses `DEFAULT_THRESHOLDS` when no thresholds provided.

### Threshold Storage

Uses existing `insert_env_config()` / `get_env_config()`:
- `id="health-thresholds"`, `environment="shared"`, `category="health"`
- Falls back to `DEFAULT_THRESHOLDS` when no stored config exists

### Export/Import

- Add `session_snapshots` to `export_json()` table list (db.py:3206-3227)
- Add `session_snapshots` to `_IMPORTABLE_TABLES` (cli.py:317)
- Import validates `data` as JSON; skips invalid rows with warning

### Tests (9)

1. **Snapshot capture** — insert specs, capture S1, verify stored with metrics
2. **Delta computation** — capture S1, add specs, capture S2, verify metric changes
3. **Alert generation** — M18_max=0 with spec without assertions triggers ALERT
4. **Text rendering** — `render_health_text()` produces non-empty well-formed output
5. **Graceful degradation** — empty DB, no crash, metrics are 0/default
6. **Threshold storage** — store via insert_env_config, retrieve, verify values
7. **Threshold default fallback** — no stored config → DEFAULT_THRESHOLDS
8. **Threshold update** — store, update with new version, verify latest retrieved
9. **Snapshot export/import** — capture → export_json → fresh DB → import → verify roundtrip

### File Touchpoints

- `src/groundtruth_kb/db.py`: schema, 3 methods, export table list
- `src/groundtruth_kb/health.py`: NEW module — metrics computation, DEFAULT_THRESHOLDS, render_health_text()
- `src/groundtruth_kb/cli.py`: _IMPORTABLE_TABLES + data validation
- `tests/test_health.py`: NEW — 9 tests

---

## F5: Requirement Intake Pipeline

### No New Tables

Uses existing `deliberations` table with `source_type='owner_conversation'`.

### CLI Commands

```
gt intake classify <requirement_text>
gt intake capture <spec_id> <requirement_text>
gt intake confirm <deliberation_id>
gt intake reject <deliberation_id> --reason <text>
gt intake list [--pending]
```

### Implementation

`src/groundtruth_kb/intake.py`: NEW module

```python
def classify_requirement(db: KnowledgeDB, text: str) -> list[dict]
def capture_requirement(db: KnowledgeDB, spec_id: str, text: str) -> dict
def confirm_intake(db: KnowledgeDB, deliberation_id: str) -> dict
def reject_intake(db: KnowledgeDB, deliberation_id: str, reason: str) -> dict
def list_intakes(db: KnowledgeDB, *, pending_only: bool = False) -> list[dict]
```

**classify_requirement():** Searches specs by section/scope/title keyword overlap.
Returns ranked list of candidate spec matches with scores.

**capture_requirement():** Stores as deliberation with:
- `source_type="owner_conversation"`, `outcome="deferred"`
- `content` = JSON with `{spec_id, requirement_text, captured_at}`

**confirm_intake():** Updates deliberation outcome to `"owner_decision"`.
Runs `compute_impact()` and `check_constraints_for_spec()` as advisory output.

**reject_intake():** Updates deliberation outcome to `"no_go"` with reason.

**list_intakes():** Queries deliberations with `source_type="owner_conversation"`,
optionally filtered by `outcome="deferred"`.

### CLI Integration

Add `intake` group to `cli.py` with 5 subcommands.

### Tests (12)

1. **Classify basic** — 3 specs in different sections; classify text matching one section; candidate list contains correct spec
2. **Classify no match** — text matches nothing; empty list
3. **Capture stores deliberation** — capture; verify deliberation created with outcome="deferred"
4. **Confirm updates outcome** — capture → confirm; outcome="owner_decision"
5. **Reject updates outcome** — capture → reject with reason; outcome="no_go" + reason stored
6. **List pending** — 2 captured, 1 confirmed; pending_only returns 1
7. **List all** — 2 captured, 1 confirmed; list all returns 3
8. **Confirm shows impact** — confirm returns impact analysis data
9. **Confirm shows constraints** — confirm returns applicable constraints
10. **Roundtrip** — classify → capture → confirm; full workflow
11. **Reject reason required** — reject without reason raises error
12. **Double confirm idempotent** — confirm twice; no error, same outcome

### File Touchpoints

- `src/groundtruth_kb/intake.py`: NEW module — 5 functions
- `src/groundtruth_kb/cli.py`: `intake` command group with 5 subcommands
- `tests/test_intake.py`: NEW — 12 tests

---

## Implementation Order

1. F7 first (9 tests) — self-contained, new table
2. F5 second (12 tests) — CLI integration, deliberation workflow

## Combined Verification Plan

1. `python -m pytest -q` (509 → ~530 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Tests | Lines |
|---------|-----------|-------|-------|
| F7 | 1 (health.py) + 1 (test) | 9 | ~350 |
| F5 | 1 (intake.py) + 1 (test) | 12 | ~400 |
| **Total** | **4 new, 2 modified** | **21** | **~750** |

## Request

Codex review requested. GO authorizes Phase 3 implementation.
