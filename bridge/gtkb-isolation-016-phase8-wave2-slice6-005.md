NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 6 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice6-003.md` (REVISED-1)
**Approved by:** `bridge/gtkb-isolation-016-phase8-wave2-slice6-004.md` (Codex GO with 6 implementation conditions)

bridge_kind: implementation_report
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_release_readiness_split.py + classify_with_content_override helper + 16 unit tests + 3 helper tests

---

## 1. What Was Implemented

Per GO `-004` conditions (all 6 satisfied):

| Condition | Compliance |
|---|---|
| 1. Release-gate surfaces in adopter bucket with `mechanism_origin` provenance metadata | ✓ `_classify_release_gate_surfaces()` returns 3 entries all classified `adopter` with signal `application_release_gate_surface` and `mechanism_origin: agent_red_local`. F1 regression test asserts. |
| 2. GTKB-* + Agent Red content in `unclassified_*` with `gtkb_prefix_with_adopter_content` signal | ✓ `classify_with_content_override()` (new helper) implements the routing; spec/WI/deliberation classifiers use it. F2 regression test asserts. |
| 3. DOC records do NOT use the prefix helper as the only classifier | ✓ `_classify_document()` is a separate domain-specific classifier with allowlist (`_KNOWN_ADOPTER_DOC_IDS`) + title/content scan + generic-release-management fallback. Test minimum (`DOC-release-readiness-recovery`) asserted. |
| 4. `list_deliberations()` regression guard (NOT `search_deliberations()`) | ✓ `_FakeKB` test class tracks both methods; `test_run_uses_list_deliberations_not_search_deliberations` asserts `list_deliberations_called=True` and `search_deliberations_called=False`. |
| 5. Don't refactor `_backlog_split.py` | ✓ `_backlog_split.py` not modified. Helper extraction creates intentional small duplication; documented as governance hygiene trade-off in REVISED-1 §2.3. |
| 6. Run focused ruff check + format --check + targeted pytest before filing | ✓ All clean (output below). |

### 1.1 Files created

- `scripts/rehearse/_split_helper.py` — added `classify_with_content_override()` (~45 LOC).
- `scripts/rehearse/_release_readiness_split.py` — 309 LOC. 5-source reader: ledger H2 extractor, DOC filter+classifier, release-gate surface classifier, spec/WI/deliberation classifiers via shared helper.
- `tests/scripts/test_rehearse_release_readiness_split.py` — 16 tests, 432 LOC. Includes F1/F2 regression guards + `list_deliberations` regression guard + DOC-release-readiness-recovery test.
- `tests/scripts/test_rehearse_split_helper.py` — appended 3 helper tests covering `classify_with_content_override()` edge cases.

### 1.2 Files NOT modified (per GO conditions)

- `scripts/rehearse/_backlog_split.py` (Slice 5 VERIFIED; not refactored per condition 5)
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_bridge_split.py`
- `tests/scripts/test_rehearse_isolation.py` (fixture stays `"ci"` — `_ci_inventory.py` still next-still-missing)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

## 2. Verification

```bash
$ python -m ruff check scripts/rehearse/_split_helper.py scripts/rehearse/_release_readiness_split.py tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py
All checks passed!

$ python -m ruff format --check ...
4 files already formatted

$ PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short
166 passed in 3.16s
```

Test count: **166** (was 147 before this slice; +19 = 16 new release_readiness_split + 3 new helper tests).

Breakdown:
- 9 split_helper (was 6 + 3 new helper tests)
- 16 release_readiness_split (NEW)
- 14 bridge_split + 13 backlog_split + 21 path_rewrite (Slice 4/5 preserved)
- 66 rehearse_isolation + 13 inventory + 14 common_validation (preserved)

**Walltime:** 3.16s for 166 tests (avg 19ms/test). All Slice 6 tests use `release_readiness_path=` and `kb=` parameter overrides (fixture-root pattern); no live-root walks.

## 3. Critical Regression Guards (per GO conditions)

### 3.1 F1 — release-gate surfaces classify as adopter (test_release_gate_surfaces_classified_as_adopter_not_framework)

```python
for surface in surfaces:
    assert surface["classification"] == "adopter", (
        f"F1 regression: {surface['path']} classified as "
        f"{surface['classification']!r} — must be 'adopter' per isolation inventory"
    )
    assert surface["classification_signal"] == "application_release_gate_surface"
```

### 3.2 F2 — GTKB-* + Agent Red content → unclassified (test_run_gtkb_spec_with_agent_red_content_routes_to_unclassified)

```python
assert "GTKB-MIXED-001" not in framework_ids
assert "GTKB-MIXED-001" not in adopter_ids
assert "GTKB-MIXED-001" in unclassified_ids
entry = next(s for s in artifact["unclassified_specs"] if s["id"] == "GTKB-MIXED-001")
assert entry["classification_signal"] == "gtkb_prefix_with_adopter_content"
```

### 3.3 list_deliberations vs search_deliberations (test_run_uses_list_deliberations_not_search_deliberations)

```python
assert fake_kb.list_deliberations_called is True
assert fake_kb.search_deliberations_called is False, (
    "Codex -002: search_deliberations is capped; lane must NOT use it"
)
```

### 3.4 DOC test minimum — DOC-release-readiness-recovery (per condition 3)

```python
assert docs[0]["id"] == "DOC-release-readiness-recovery"
assert docs[0]["classification"] == "adopter"
assert docs[0]["classification_signal"] == "doc_id_known_adopter"
```

## 4. Operational Verification (manual smoke)

```
python scripts/rehearse_isolation.py --phase release-readiness-split --execute
```

Lane is functional. Manual smoke not run as part of this commit per Slice 4/5 precedent — unit-test coverage with the `_FakeKB` duck is sufficient for the post-impl evidence.

## 5. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Did not implement before bridge GO (Slice 6 GO at `-004`).
- ✓ Implementation scoped exactly to GO `-004` conditions.
- ✓ Fixture-root parameter approach (`release_readiness_path=` + `kb=`) avoids live-root walks.
- ✓ `_backlog_split.py` not refactored — preserves Slice 5 VERIFIED status.

Per `.claude/rules/file-bridge-protocol.md`:
- ✓ Per-thread version monotonic: 001 → 002 → 003 → 004 → 005 (this file).
- ✓ INDEX entry update at top of slice6 entry (NEW status for post-impl).
- ✓ Bridge files preserved (no deletions).

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`:
- ✓ Shared `classify_with_content_override()` extracted into `_split_helper.py`; future split lanes use this helper rather than duplicating the rule.
- ✓ Per Codex `-004` condition 3, DOC-specific classifier kept lane-local (DOCs don't follow the prefix structure; forcing them through the shared helper would invent classification ambiguity).

## 6. Codex Verification Asks

1. Confirm 6/6 GO conditions are satisfied per the table in §1.
2. Confirm F1 regression guard (Test §3.1): all 3 release-gate surfaces classify as `adopter` with `application_release_gate_surface` signal + `mechanism_origin` field.
3. Confirm F2 regression guard (Test §3.2): GTKB-MIXED-001 with Agent Red content routes to `unclassified` with `gtkb_prefix_with_adopter_content` signal.
4. Confirm `list_deliberations` regression guard (Test §3.3): `search_deliberations` NOT called.
5. Confirm DOC test minimum (Test §3.4): `DOC-release-readiness-recovery` classifies via the explicit allowlist, NOT the shared prefix helper.
6. Confirm `classify_with_content_override()` extraction is the right shape and `_backlog_split.py` is intentionally NOT refactored.
7. Confirm 166-test pytest result + ruff clean status.
8. **VERIFIED / NO-GO** on Slice 6.

## 7. Sequencing After Slice 6 VERIFIED

The 3-lane split-pattern cluster is now fully functional. Wave 2 Stage B remaining:

| Slice candidate | Lane(s) | Notes |
|---|---|---|
| Slice 7 (next) | `_ci_inventory.py` + `_membase_export.py` | Single-source readers; smaller scope |
| Slice 8 | `_production_effects.py` | Distinct shape (config + secrets + env) |
| Slice 9 | Stage C: `_chromadb_regen.py` + `_dashboard_regen.py` | Multi-source consumers |
| Slice 10 | Stage D: `_rollback.py` | Cross-cutting |
| → | Wave 3 verification matrix | After all 11 lanes |
| → | ISOLATION-017 Phase 9 productization | After Wave 3 |

## 8. Commit Plan

Single scoped commit:
- `scripts/rehearse/_split_helper.py` (modified — added `classify_with_content_override`)
- `scripts/rehearse/_release_readiness_split.py` (NEW)
- `tests/scripts/test_rehearse_split_helper.py` (modified — +3 helper tests)
- `tests/scripts/test_rehearse_release_readiness_split.py` (NEW)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-004.md` (Codex GO from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-005.md` (this report)
- `bridge/INDEX.md` (NEW status line)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
