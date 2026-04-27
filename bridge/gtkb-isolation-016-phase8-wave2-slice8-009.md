REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 — Post-Implementation Report (REVISED-1)

**Status:** REVISED (post-impl revision; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S314)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice8-007.md` (NO-GO at `-008`)
**Addresses:** Codex `-008` Finding 1 (P1) — type-specific classification overrides were missing.

---

## 0. NO-GO Acknowledgement

Codex `-008` correctly held two findings:

1. **P1 (blocking) — Type-specific classification overrides missing.** My initial implementation classified versioned records only by ID prefix + content scan. The original Slice 8 proposal called for type-specific overrides per versioned-table type, most importantly `tests.test_file` path-based classification. I dropped this from the impl without documenting the omission. Live evidence: 10,669 test rows came back `unclassified` because the lane never read the `test_file` column.

2. **P2 (non-blocking) — Whole rehearsal package not green.** `_chromadb_regen.py` (Slice 10 WIP at commit `c4acfc13`) trips `ruff format --check`. Not a Slice 8 defect; addressed in Slice 10 work, not this revision.

REVISED-1 implements the type-specific override layer (Finding 1) and explicitly documents the no-override decisions for tables without distinct scope signals. Finding 2 is acknowledged as a Slice 10 concern.

## 1. Implementation Changes

### 1.1 New helpers in `scripts/rehearse/_membase_export.py`

- `_classify_test_path(test_file)` — path-based classifier for the `tests` table.
- `_classify_deliberation_origin(origin_project)` — origin-based classifier for the `deliberations` table.
- `_classify_by_type_specific_signal(table_name, type_columns)` — dispatcher that returns `(classification, signal)` if a strong type-specific signal applies, or `None` if no signal (caller falls through to ID-prefix + content scan).

### 1.2 New constants

- `_TABLE_SPECIFIC_TYPE_COLUMNS`: per-table additional columns the lane queries for type-specific classification. Currently `{"tests": ("test_file", "test_class", "test_function"), "deliberations": ("origin_project", "origin_repo")}`.
- `_TEST_PATH_FRAMEWORK_PREFIXES`, `_TEST_PATH_MIXED_SCOPE_MARKERS`, `_TEST_PATH_ADOPTER_NAMED_PREFIXES`, `_TEST_PATH_DEFAULT_ADOPTER_PREFIX`: test-path classification rules.
- `_DELIBERATION_ORIGIN_FRAMEWORK_MARKERS`, `_DELIBERATION_ORIGIN_ADOPTER_MARKERS`: deliberation origin markers.

### 1.3 Updated `_enumerate_versioned_table()`

Now reads both `_CONTENT_BEARING_COLUMNS` (generic) and `_TABLE_SPECIFIC_TYPE_COLUMNS[table_name]` (type-specific). For each unique `id`, takes the first non-null value across version rows for type-specific columns. Classification cascade:

1. Tier 1: `_classify_by_type_specific_signal(table_name, type_columns)` — if not None, use it.
2. Tier 2: `_classify_artifact_id(id, content_text)` — existing ID-prefix + content scan fallback.

### 1.4 Updated module docstring

Added "Type-Specific Override Decisions" section documenting:
- The classification cascade
- Which tables get overrides (tests, deliberations) and why
- Which tables have **no override** (operational_procedures, documents, work_items, specifications, test_plans, test_plan_phases, test_procedures, testable_elements, backlog_snapshots, environment_config) — explicitly per Codex `-008` required-action option ("Either implement... or explicitly revise the design to remove them with evidence").

## 2. Test-Path Classification Rules

Order is significant — earlier rules win when paths overlap:

| Rule | Match | Classification | Signal |
|---|---|---|---|
| 1. Mixed-scope marker | `test_release_candidate_gate`, `test_groundtruth_governance_adoption` (substring match) | `unclassified` | `mixed_scope_test` |
| 2. Framework prefix | `tests/groundtruth_kb/` | `framework` | `test_path_framework_groundtruth_kb` |
| 3. Adopter named prefix | `tests/transport/`, `tests/scripts/test_admin_`, `tests/scripts/test_provider_` | `adopter` | `test_path_adopter_named` |
| 4. Adopter product default | any other `tests/` path | `adopter` | `test_path_adopter_product` |
| 5. Outside `tests/` or NULL | (no match) | None — falls through | (caller uses ID prefix + content) |

**Justification for rule 4 (default adopter):** this lane runs against the *adopter* project's KB. Framework tests live in the upstream `groundtruth-kb` repo's KB. Tests in this DB that reference product-area paths (`tests/widget/`, `tests/multi_tenant/`, `tests/integration/`, etc.) are adopter content by construction. A future framework-side import would still be caught: an explicit `tests/groundtruth_kb/` prefix overrides the default (rule 2).

## 3. Why Codex's Listed Paths Don't Appear in Live Data

Codex `-008` named `tests/groundtruth_kb/`, `tests/transport/`, `tests/scripts/test_admin_*`, `tests/scripts/test_provider_*`, and `test_release_candidate_gate.py`. Source verification against the live KB:

```
tests/groundtruth_kb/* rows: 0
tests/transport/* rows: 0
tests/scripts/test_admin_* rows: 0
tests/scripts/test_provider_* rows: 0
test_release_candidate_gate rows: 0
```

This matters: implementing only Codex's listed patterns would have classified zero rows differently in the live data. The principled "default adopter for any `tests/` path that isn't explicitly framework or mixed" rule (rule 4) is what reclassifies the 10,669-row backlog. The named patterns remain in the rules as forward-compatible coverage for future schema additions.

## 4. Deliberation Origin Classification

The strongest scope signal in this KB. Live distribution of `deliberations.origin_project`:

| origin_project value | Row count | Classification |
|---|---|---|
| `agent-red` | 1,240 | adopter |
| `Agent Red Customer Engagement` | 9 | adopter (matches "agent red" marker) |
| `agent_red` | 9 | adopter |
| `Agent Red Customer Experience` | 4 | adopter |
| `agent-red-customer-engagement` | 2 | adopter |
| `groundtruth-kb` | 1 | framework |
| NULL | 53 | (falls through to content scan) |

Implementation matches all variants via lowercase substring scan against `_DELIBERATION_ORIGIN_ADOPTER_MARKERS = ("agent-red", "agent_red", "agent red")` and `_DELIBERATION_ORIGIN_FRAMEWORK_MARKERS = ("groundtruth", "gt-kb")`.

## 5. Live-DB Classification Improvement

### Before REVISED-1 (commit `3a76e1ad`)

```
Versioned records: 17,352
  framework:    252
  adopter:    1,325
  unclassified: 15,775
```

Test records: 11,142 total → 10,669 unclassified.

### After REVISED-1

```
Versioned records: 17,352
  framework:    40
  adopter:    11,712
  unclassified: 5,600
```

Test records by signal:
- `test_path_adopter_product`: 9,963 (formerly unclassified)
- `agent_red_product_reference`: 53 (existing content-scan)
- `no_classification_signal`: 1,126 (NULL `test_file`; cannot path-classify)

Deliberation records by signal:
- `deliberation_origin_project_agent_red`: 1,264
- `deliberation_origin_project_framework`: 1
- `agent_red_product_reference`: 4 (NULL origin, content-scan adopter)
- `groundtruth_kb_reference`: 11 (NULL origin, content-scan framework)
- `mixed_scope_content`: 11 (NULL origin, mixed content markers)
- `no_classification_signal`: 12 (NULL origin, no content markers)

**Net change:**
- **65% reduction in unclassified records** (15,775 → 5,600).
- **Adopter records up 9.0×** (1,325 → 11,712).
- **Framework records down** (252 → 40), but more *accurately* framework — deliberations previously content-scanned as framework had `origin_project='agent-red'` and now correctly classify as adopter (origin signal trumps content keyword).

### Note on the framework count drop

The original 252 framework count was inflated by deliberations that mention `groundtruth-kb` in their text but are owned by the Agent Red project (`origin_project='agent-red'`). REVISED-1 correctly classifies these as adopter — they're deliberations *about* framework topics that belong in the adopter cutover. The remaining 40 framework records are: 1 deliberation explicitly originated in groundtruth-kb, 11 deliberations with framework content + NULL origin, and 28 records (specs/WIs/etc.) with GTKB-* IDs.

## 6. Verification Performed

### 6.1 Slice 8 lane suite

```
$ python -m pytest tests/scripts/test_rehearse_membase_export.py -q --tb=short --timeout=60
================================== 35 passed in 3.76s ==================================
```

Up from 24 tests in `-007` to 35 tests in REVISED-1 (11 new tests).

### 6.2 Driver-fixture regression

```
$ python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
================================== 66 passed ==================================
```

No driver-test regressions; the `dashboard` fixture advance from `-007` is preserved.

### 6.3 Full Wave 2 lane regression

```
$ python -m pytest tests/scripts/test_rehearse_*.py (9 lane suites) -q --tb=line --timeout=120
================================== 252 passed in 8.13s ==================================
```

No regressions in any sibling lane.

### 6.4 Ruff lint + format

```
$ python -m ruff check scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py
All checks passed!

$ python -m ruff format scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py
2 files reformatted
```

Auto-format applied to both files; format check now clean.

### 6.5 Live-DB driver smoke

```
$ python scripts/rehearse_isolation.py --phase membase --execute \
    --output-dir C:/temp/agent-red-rehearsal-slice8-revised1-smoke
rehearse_isolation: --execute set; running with dry_run=False
  -> membase ... ok
```

Manifest at `C:/temp/agent-red-rehearsal-slice8-revised1-smoke/membase_export/membase-partition-manifest.json` shows the post-REVISED-1 classification breakdown above. Warnings count: 0. Live row counts unchanged (40,034 versioned rows / 17,352 unique artifacts / 445 relationship rows / 138 per-session rows).

## 7. New Tests Added (11 total)

### 7.1 Test-path classification (8 tests)

| Test | Coverage |
|---|---|
| `test_run_classifies_test_path_groundtruth_kb_as_framework` | Rule 2 — framework prefix; description includes adopter content marker to prove path beats content |
| `test_run_classifies_test_path_transport_as_adopter_named` | Rule 3 — `tests/transport/` |
| `test_run_classifies_test_path_admin_scripts_as_adopter_named` | Rule 3 — `test_admin_*` |
| `test_run_classifies_test_path_provider_scripts_as_adopter_named` | Rule 3 — `test_provider_*` |
| `test_run_classifies_test_path_release_candidate_gate_as_mixed_scope` | Rule 1 — mixed-scope must run before adopter-default |
| `test_run_classifies_other_test_path_under_tests_as_adopter_product` | Rule 4 — default for `tests/widget/`, `tests/multi_tenant/`, etc. |
| `test_run_falls_through_to_id_prefix_when_test_file_null` | Rule 5 — NULL test_file → fall through to ID prefix (AR-* in this case) |
| `test_run_falls_through_when_test_file_outside_tests_dir` | Rule 5 — non-`tests/` path → fall through |

### 7.2 Deliberation origin classification (3 tests)

| Test | Coverage |
|---|---|
| `test_run_classifies_deliberation_origin_agent_red_as_adopter` | origin_project='agent-red' beats content scan; description contains no scope content |
| `test_run_classifies_deliberation_origin_groundtruth_kb_as_framework` | origin_project='groundtruth-kb' → framework |
| `test_run_classifies_deliberation_with_null_origin_falls_through_to_content` | NULL origin → falls through; content "agent red migration" → adopter via existing `_classify_artifact_id` |

### 7.3 Fixture extension

`_create_minimal_live_schema` now creates `tests` with `(test_file, test_class, test_function)` and `deliberations` with `(origin_project, origin_repo)` columns. Existing tests that don't insert into these columns still work — the type-specific classifier returns None for NULL values and falls through.

## 8. Files Changed

### MODIFIED

- `scripts/rehearse/_membase_export.py` (~+150 LOC): new helpers, new constants, new docstring section, rewired `_enumerate_versioned_table`, ruff-format applied
- `tests/scripts/test_rehearse_membase_export.py` (~+260 LOC): new fixture schemas, 11 new tests

### NEW

- `bridge/gtkb-isolation-016-phase8-wave2-slice8-009.md` (this file)

### MODIFIED (bridge state)

- `bridge/INDEX.md`: REVISED line at top of slice8 thread

### UNTOUCHED

- All other Slice 1-7, 9, 10, 11 sources and tests
- `scripts/rehearse_isolation.py`, `_common.py`, `_split_helper.py`
- `tests/scripts/test_rehearse_isolation.py` (no fixture advance — `dashboard` remains the next missing leaf)

## 9. Codex `-008` Finding Closure

| Finding | Status | Evidence |
|---|---|---|
| F1 (P1) Type-specific overrides missing | **CLOSED** | Type-specific override layer implemented for `tests` (path) and `deliberations` (origin_project); explicit no-override decision documented for the other 10 versioned tables in module docstring |
| F2 (P2) Package not fully ruff-clean | Acknowledged; deferred to Slice 10 | `_chromadb_regen.py` is Slice 10 WIP at commit `c4acfc13`; format issue is in that file, not Slice 8. Slice 10 post-impl will address it |

## 10. Codex Review Asks (REVISED-1)

1. Confirm the type-specific override layer's two-table scope (`tests`, `deliberations`) plus explicit no-override documentation for the other 10 versioned tables addresses Finding 1's required action.
2. Confirm the "default-to-adopter for any `tests/` path that isn't framework or mixed" rule (rule 4) is principled. Justification: this lane runs against the adopter KB; framework tests live upstream. Alternative: keep rule 4 narrow (only the named patterns), accept that 10,669 test rows remain unclassified. My read: rule 4 is the principled answer.
3. Confirm the deliberation origin signal (1,264 rows reclassified to adopter via `origin_project`) correctly trumps content scan when both signals exist. The 11 + 12 deliberations that fall through to content scan because origin_project is NULL are the correct fallback population.
4. Confirm the `mixed_scope_test` ordering (rule 1 first) is correct — without it, `tests/scripts/test_release_candidate_gate.py` would otherwise be absorbed by rule 4's adopter-product default.
5. Confirm Test 7.1.1 (`test_run_classifies_test_path_groundtruth_kb_as_framework` with adopter content in description) is the right primary regression guard against the "content beats path" mistake.
6. **VERIFIED / NO-GO** on Slice 8 REVISED-1.

## 11. Decision Needed From Owner

None.

(If Codex flags additional type-specific overrides for `documents`, `work_items`, `specifications`, etc. in the VERIFIED response, those become a separate revision — not part of this REVISED-1.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
