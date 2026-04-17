# Phase 3 Post-Implementation Report: F7 + F5

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Post-Implementation Report
**GO reference:** bridge/gtkb-phase3-implementation-014.md
**Commits:** 61b278a (F7), 63ea9c2 (F5)

## Implementation Summary

| Feature | Tests | New Files | Modified Files | Commit |
|---------|-------|-----------|----------------|--------|
| F7: Session Health Dashboard | 14 | 3 (health.py, session-health.py, test_health.py) | 3 (db.py, cli.py, cli.md) | 61b278a |
| F5: Requirement Intake Pipeline | 34 | 3 (intake.py, intake-classifier.py, test_intake.py) | 7 (cli.py, doctor.py, upgrade.py, settings.local.json, cli.md, templates.md, changelog.md) | 63ea9c2 |
| **Total** | **48** | **6** | **10** | — |

## GO Condition Compliance

### F7 (all conditions met)

1. **Snapshot write contract:** `session_snapshots` uses `INSERT OR REPLACE INTO` so repeated captures for the same `session_id` replace the previous snapshot. Verified by `test_same_session_replacement`.
2. **Snapshot contents:** stores `lifecycle_metrics`, `summary` (from `get_summary()`), `quality_distribution`, `constraint_coverage`, and `captured_at`. Verified by `test_snapshot_capture` and `test_snapshot_includes_summary`.
3. **Delta API:** `compute_session_delta(current_session=None)` computes live-vs-last snapshot with `no_prior=True` graceful degradation. Explicit session-vs-previous mode supported for trends. Uses `rowid` ordering to handle same-second captures deterministically. Verified by 3 delta tests.
4. **Alert thresholds:** `DEFAULT_THRESHOLDS` keyed on existing lifecycle metric IDs (M6/M11/M12/M16/M17/M18). `render_health_text()` emits `PASS`/`ALERT` per metric. Threshold storage via existing `insert_env_config()` / `get_env_config()`.
5. **CLI:** `gt health` (current + delta), `gt health snapshot <session_id>`, `gt health trends` group implemented.
6. **Hook template:** `templates/hooks/session-health.py` — Stop event hook that captures session-end snapshot.
7. **Export/import:** `session_snapshots` added to `export_json()` table list AND `_IMPORTABLE_TABLES`. Import validates `data` JSON with deterministic skip-or-error behavior. Negative test covers malformed JSON.
8. **Documentation:** `docs/reference/cli.md` documents all three health subcommands with parameter tables.

### F5 (all conditions met)

1. **Intent classification:** Approved taxonomy (`directive`, `constraint`, `preference`, `question`, `exploration`) with numeric confidence in `[0.0, 1.0]`. Precedence rules ensure exploration markers dominate directive verbs (so "maybe we should" → exploration) and constraint markers ("must not") override directive. Verified by 5 classification tests plus roundtrip.
2. **Numeric confidence contract:** directive → ≥ 0.85 when ≥ 2 hits, ≥ 0.9 when ≥ 3 hits; exploration → ≤ 0.4; tests assert `> 0.8` and `< 0.5`.
3. **Candidate payload:** stores `intake_type` discriminator, `intake_status`, `raw_text`, `classification`, `confidence`, `related_specs`, `proposed_title`/`section`/`scope`/`type`/`authority`, `captured_at`, `confirmed_spec_id`, `rejection_reason`. Verified by `test_capture_stores_full_payload`.
4. **Confirm creates KB spec:** `confirm_intake()` calls `db.insert_spec()` with the proposed `type` and `authority` fields, records `confirmed_spec_id` in the deliberation content, and uses `insert_deliberation()` (append-only) to write the updated version.
5. **F2/F3/F4 cross-feature integration in confirm:** `confirm_intake()` returns `impact` (from `compute_impact("add", created_spec)`), `quality` (from `score_spec_quality(created_spec)` with tier/flags/overall), and `constraints` (from `check_constraints_for_spec(spec_id)`). All three verified by dedicated tests.
6. **Reject with reason:** `reject_intake()` requires non-empty reason, persists as new deliberation version with `outcome="no_go"`.
7. **Intake discriminator:** `list_intakes()` filters by parsing `content` JSON and checking `intake_type == "requirement_candidate"`, skipping malformed/non-intake rows deterministically. Verified by `test_list_excludes_non_intake`.
8. **Redaction:** `insert_deliberation()` applies existing credential redaction before storage. Verified by `test_redaction` — an API key in the raw text is not present in the stored content, and the intake remains filterable.
9. **CLI:** `gt intake classify|capture|confirm|reject|list` group implemented. Smoke tests for list/confirm/reject use `CliRunner` with `--config` pointing to a temporary `groundtruth.toml`.
10. **Scaffold:** bridge-profile `templates/project/settings.local.json` activates `intake-classifier.py`. Local-only profile omits `settings.local.json` entirely (no classifier warnings). Both cases verified.
11. **Doctor:** `_check_settings_classifiers(target)` wired into `run_doctor()` inside the `if p.includes_bridge:` block. Handles all 8 approved cases: only-intake active, only-spec active (legacy), both active (warns), neither active (warns), malformed JSON, non-dict hooks, null hooks, local-only no-false-warning. All 8 verified by dedicated tests.
12. **Upgrade:** `_MANAGED_HOOKS` includes `intake-classifier.py` alongside `spec-classifier.py`. The local-only filter (`assertion-check.py`, `spec-classifier.py` only) excludes intake from local-only upgrades. Verified by 3 upgrade tests.
13. **Legacy compatibility:** `spec-classifier.py` remains in `_MANAGED_HOOKS` and doctor passes when it's the only active classifier.
14. **Documentation:** `docs/reference/cli.md` (intake commands), `docs/reference/templates.md` (hook references), `docs/changelog.md` (migration notes).

## Verification Results

```
python -m pytest -q                          → 557 passed (523 → 557, +34 F5)
python -m ruff check .                       → All checks passed
python -m ruff format --check .              → 61 files already formatted
python scripts/check_docs_cli_coverage.py    → All documentation checks passed
```

## Test Breakdown

| Category | Tests |
|----------|-------|
| F7 snapshot/delta/render | 9 |
| F7 thresholds | 2 |
| F7 export/import | 2 |
| F7 hook template | 1 |
| F5 core intake (classify/capture/confirm/reject) | 13 |
| F5 list/filter | 3 |
| F5 redaction + CLI smoke | 4 |
| F5 scaffold | 2 |
| F5 doctor (8 cases) | 8 |
| F5 upgrade | 3 |
| F5 roundtrip | 1 |
| **Total** | **48** |

## Notable Implementation Decisions

1. **Rowid-based delta ordering:** `compute_session_delta()` uses `rowid` ordering instead of `captured_at` to handle same-second captures deterministically. Same approach used by F3's `get_quality_distribution()`.

2. **Intent classifier precedence:** Exploration markers (`maybe`, `what if`) take precedence over directive verbs because they signal non-commitment. Constraint markers (`must not`, `cannot`) override directive because negation inverts intent. Without these precedence rules, the approved test expectations (directive > 0.8 AND "maybe we should" → exploration) cannot both hold.

3. **Append-only deliberation updates:** Intake status transitions (`pending` → `confirmed`/`rejected`) use `insert_deliberation()` to create new versions of the same ID, not a separate update method. This preserves the full audit trail.

4. **Spec ID generation:** Confirmed intakes create specs with `SPEC-INTAKE-{uuid8}` IDs. This avoids conflicts with hand-authored spec IDs and makes intake-sourced specs easy to identify.

5. **Docs site upgrading guide:** The approved proposal mentioned `docs/guides/upgrading.md`, but that file does not exist in the repo. Migration notes were added to `docs/changelog.md` under `[Unreleased]` instead — this is the actual location for release notes in this project.

## Request

Codex verification requested. VERIFIED authorizes Phase 3 completion and advancement to Phase 4 (F6-B + F8).
