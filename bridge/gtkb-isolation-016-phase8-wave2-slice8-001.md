NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 — `_membase_export.py`

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-010.md` (Slice 5 VERIFIED; established split-pattern + `_split_helper`)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md` (Slice 6 VERIFIED; uncapped `list_deliberations` lesson)

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_membase_export.py + tests; driver dispatch already wired (table entry index 3: `("membase", "rehearse._membase_export", "run")`)

**Filed in parallel with:** Slices 7 (`_ci_inventory`) and 9 (`_production_effects`) per owner direction 2026-04-27. All three Stage B lanes are independent at the implementation level (umbrella -004: "Lanes 2-11 must consume the validated runtime manifest" with no inter-lane ordering).

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan — defines framework-vs-adopter classification basis.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this slice reuses `_split_helper.classify_by_id_prefix()`, `_split_helper.partition_items()`, and `_split_helper.emit_result()`.
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-010.md` (VERIFIED): established the F1 lesson — `GTKB-*` records with adopter-content references route to `unclassified` with signal `gtkb_prefix_with_adopter_content`, NOT silently to `framework`. Same pattern reused here for any KB record type.
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md` (VERIFIED): uncapped `list_deliberations()` (NOT `search_deliberations()` which has default cap of 5). Same lesson reused for the `deliberations` source in this slice.

## 1. Scope

Single Stage B leaf lane: `scripts/rehearse/_membase_export.py`. Produces a **partition manifest** of every artifact in the live KB (`groundtruth.db`), classified as framework / adopter / unclassified. The manifest is a *pointer record per artifact*, not a content dump — full content stays in `groundtruth.db`; the manifest is the operator's road map for selective SQL extraction at ISOLATION-018 cutover.

Strictly additive: no driver changes (dispatch already registers `membase`), no manifest changes, no changes to `_common.py` or any earlier lane.

## 2. Authoritative Source Set

The live KB at `LEGACY_ROOT/groundtruth.db`. Twelve `KnowledgeDB.list_*()` methods enumerated empirically (verified 2026-04-27 against `tools/knowledge-db/db.py`):

| # | Source | Method | Volume estimate (per S311 wrap) |
|---|---|---|---|
| 1 | Specifications | `list_specs()` | 2,105 |
| 2 | Tests | `list_tests()` | 11,055 |
| 3 | Work items | `list_work_items()` | 1,851 |
| 4 | Documents | `list_documents()` | 179 |
| 5 | Operational procedures | `list_op_procedures()` | 14 |
| 6 | Deliberations | `list_deliberations()` (uncapped — not `search_deliberations`!) | 710 |
| 7 | Design constraints (DCL) | `list_design_constraints()` | (subset of specs) |
| 8 | Implementation proposals (IPR) | `list_implementation_proposals()` | (variable) |
| 9 | Constraint verifications (CVR) | `list_constraint_verifications()` | (variable) |
| 10 | Test plans + phases + procedures + testable elements | `list_test_plans()`, `list_test_plan_phases()`, `list_test_procedures()`, `list_testable_elements()` | (test infrastructure) |
| 11 | Backlog snapshots | `list_backlog_snapshots()` | (per-session) |
| 12 | Aux: events, env_config, session_prompts | `list_events()`, `list_env_config()`, `list_session_prompts()` | (variable) |

Notably **excluded from this slice**: `assertion_runs` (high-volume, low-information per row; export the latest run per assertion only would be a separate concern; this slice records assertions via the spec's assertions field, not as standalone records).

## 3. Classification Algorithm

Per record (in declaration order; first match wins):

### 3.1 ID-prefix tier (`_split_helper.classify_by_id_prefix()`)

- ID starts with `GTKB-` → tentative framework
- ID starts with `AR-` → tentative adopter
- ID starts with anything else → defer to content scan

### 3.2 Content-scan override tier

For records with non-prefix IDs (most of them — `SPEC-*`, `WI-*`, `PB-*`, `ADR-*`, `DCL-*`, `DOC-*`, `DELIB-*`) and as override on tentative tier-1 results:

| Content signal | Override action | Signal |
|---|---|---|
| Body / title / summary mentions Agent Red product specifics (Shopify, ACS toll-free, Cosmos, agent-red Azure resources, transport tests) | adopter | `agent_red_product_reference` |
| Body / title / summary mentions GroundTruth-KB framework (`groundtruth_kb`, `gt project`, isolation, scaffolding) | framework | `groundtruth_kb_framework_reference` |
| BOTH adopter and framework signals present | unclassified | `mixed_scope_owner_decision_required` |
| Tier-1 said `framework` but Agent Red content present (Slice 5 F1 lesson) | unclassified | `gtkb_prefix_with_adopter_content` |
| Tier-1 said `adopter` but GT-KB framework content present | unclassified | `ar_prefix_with_framework_content` |
| No content signal | unclassified | `no_classification_signal` |

### 3.3 Type-specific overrides

- **Tests** (`list_tests()`): test path is the strongest signal. `tests/groundtruth_kb/...` → framework. `tests/transport/...`, `tests/scripts/test_admin_*`, `tests/scripts/test_provider_*` → adopter. Tests under `tests/scripts/` covering both subjects (e.g., `test_release_candidate_gate.py`) → unclassified with signal `mixed_scope_test`.
- **Procedures** (`list_op_procedures()`): bridge-management / kb-session-wrap / formal-artifact procedures → framework. Deploy / build / staging procedures → adopter.
- **Documents** (`list_documents()`): Sarah Scenario, GT-KB onboarding, IDP concept → framework. Production runbooks, deploy guides, OrbaTech reports → adopter.
- **Deliberations** (`list_deliberations()`): per S312 lesson, GTKB-prefixed deliberations with Agent Red content go to unclassified. Apply Slice 5 F1 logic uniformly.

## 4. Output Layout

```
{output_dir}/membase_export/
├── membase_export.json           # top-level summary (counts per type per classification)
├── partition_manifest.json       # per-record {id, type, classification, classification_signal}
├── per_type_summary/
│   ├── specs.json
│   ├── tests.json
│   ├── work_items.json
│   ├── documents.json
│   ├── procedures.json
│   ├── deliberations.json
│   ├── design_constraints.json
│   ├── implementation_proposals.json
│   ├── constraint_verifications.json
│   ├── test_plans.json
│   ├── test_plan_phases.json
│   ├── test_procedures.json
│   ├── testable_elements.json
│   ├── backlog_snapshots.json
│   ├── events.json
│   ├── env_config.json
│   └── session_prompts.json
└── result.json
```

**Design rationale (output-volume control):** the partition manifest is sparse — `{id, type, classification, classification_signal}` per record, no content. With ~15,000+ records, the manifest weighs ~2-4 MB JSON. Per-type summary files are much smaller (typically a few hundred KB each). Operators inspecting "which work items are framework?" load `per_type_summary/work_items.json` (filtered by `classification == "framework"`), not the full partition manifest. Wave 3 verification + ISOLATION-018 cutover consume `partition_manifest.json` to drive selective SQL extraction.

## 5. Schemas

### 5.1 `membase_export.json` (top-level summary)

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "kb_path": "E:/GT-KB/groundtruth.db",
  "kb_size_bytes": 882347008,
  "record_counts": {
    "specs": {"framework": 312, "adopter": 89, "unclassified": 1704, "total": 2105},
    "tests": {"framework": 4123, "adopter": 5891, "unclassified": 1041, "total": 11055},
    "work_items": {...},
    "documents": {...},
    "procedures": {...},
    "deliberations": {...},
    ...
  },
  "totals": {"framework": ..., "adopter": ..., "unclassified": ..., "grand_total": ...},
  "warnings": []
}
```

### 5.2 `partition_manifest.json` (per-record sparse manifest)

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "records": [
    {"id": "SPEC-1834", "type": "spec", "classification": "adopter", "classification_signal": "agent_red_product_reference"},
    {"id": "WI-3168", "type": "work_item", "classification": "adopter", "classification_signal": "agent_red_product_reference"},
    {"id": "GTKB-ISOLATION-016", "type": "work_item", "classification": "unclassified", "classification_signal": "gtkb_prefix_with_adopter_content"},
    {"id": "DELIB-0877", "type": "deliberation", "classification": "framework", "classification_signal": "groundtruth_kb_framework_reference"},
    ...
  ]
}
```

### 5.3 `per_type_summary/<type>.json`

```json
{
  "type": "spec",
  "schema_version": 1,
  "framework_count": 312,
  "adopter_count": 89,
  "unclassified_count": 1704,
  "total": 2105,
  "framework": [{"id": "SPEC-...", "title": "...", "classification_signal": "..."}],
  "adopter": [...],
  "unclassified": [...]
}
```

Note: title field is included in `per_type_summary` for human spot-checking but NOT in `partition_manifest.json` (which stays sparse for size reasons).

## 6. Common Contract Compliance

Per Wave 2 -003 §4 + Slice 4/5/6 lessons:

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False, kb=None) -> dict` — ✓
- §4.2 output layout: under `{output_dir}/membase_export/`; includes `result.json` from start (Slice 4 -006 F2) — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on LEGACY_ROOT: only queries KB; writes only to `output_dir` — ✓
- §4.5 driver dispatch: already wired (table index 3) — ✓
- §4.6 manifest validation precondition: lane assumes validated manifest — ✓
- `_emit_result()` from `_split_helper.py` wraps non-dry-run returns — ✓

`kb=` parameter accepts a duck-typed object (per Slice 6 pattern) so tests can pass synthetic state without monkeypatching `KnowledgeDB`.

## 7. Test Plan

`tests/scripts/test_rehearse_membase_export.py` (new; ~16-20 tests).

Mocking strategy:
- `kb=` parameter accepts a fake KB exposing all 17 `list_*` methods (or a subset; methods called but unimplemented return `[]`).
- No live `groundtruth.db` reads in tests.

Test list:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_run_uses_list_deliberations_not_search_deliberations` | Slice 6 F1 regression — explicit guard test |
| 3 | `test_run_classifies_gtkb_prefix_specs_as_framework_when_no_adopter_content` | §3.1 + clean tier-1 |
| 4 | `test_run_classifies_ar_prefix_specs_as_adopter_when_no_framework_content` | §3.1 + clean tier-1 |
| 5 | `test_run_classifies_gtkb_isolation_016_as_unclassified` | Slice 5 F1 regression reused — `GTKB-ISOLATION-016` work item with Agent Red content |
| 6 | `test_run_classifies_neutral_id_specs_by_content` | §3.2 — `SPEC-1834` w/ Cosmos mention → adopter |
| 7 | `test_run_classifies_test_by_path_groundtruth_kb_framework` | §3.3 type-specific override (tests/groundtruth_kb/...) |
| 8 | `test_run_classifies_test_by_path_transport_adopter` | §3.3 (tests/transport/...) |
| 9 | `test_run_classifies_test_with_mixed_scope_as_unclassified` | §3.3 — `test_release_candidate_gate.py` |
| 10 | `test_run_classifies_procedure_by_kind` | §3.3 — bridge-management → framework |
| 11 | `test_run_classifies_document_by_topic` | §3.3 — production runbook → adopter |
| 12 | `test_run_emits_per_type_summary_files_for_each_source` | All 17 `list_*` methods produce a per-type summary file |
| 13 | `test_run_emits_partition_manifest_with_sparse_schema` | §5.2 — id, type, classification, signal only; no content |
| 14 | `test_run_emits_top_level_summary_with_record_counts` | §5.1 |
| 15 | `test_run_writes_result_json_on_ok_path` | Slice 4 -006 F2 |
| 16 | `test_run_writes_result_json_on_error_path` | Error path forensics |
| 17 | `test_run_returns_error_when_kb_constructor_fails` | KB unavailable |
| 18 | `test_run_kb_parameter_override_prevents_live_db_read` | Fixture safety |
| 19 | `test_run_handles_empty_kb_gracefully` | Edge case — fresh KB |
| 20 | `test_run_does_not_export_assertion_runs` | §2 explicit exclusion |

Plus 1 driver integration test: advance the missing-lane fixture from `"membase"` to next-still-missing (depends on which Stage B slices are GO'd by then).

## 8. Files Changed (this slice's commit)

### 8.1 NEW
- `scripts/rehearse/_membase_export.py` — ~280 LOC (17 source readers + classifier + emitters)
- `tests/scripts/test_rehearse_membase_export.py` — ~520 LOC (~20 tests + fake-KB fixtures)
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md` (this file)

### 8.2 MODIFIED
- `bridge/INDEX.md` — new slice8 entry at top
- `tests/scripts/test_rehearse_isolation.py` — fixture advances per Slice 7/8/9 GO ordering

### 8.3 UNTOUCHED
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`
- All other Slice 1-6 tests
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- `groundtruth.db` (read-only access)

## 9. Out of Scope

- Stage B sibling lanes: `_ci_inventory.py` (Slice 7), `_production_effects.py` (Slice 9) — separate parallel slices.
- Stage C: `_chromadb_regen.py`, `_dashboard_regen.py` — separate slices.
- Stage D: `_rollback.py` — separate slice.
- Resolving `unclassified` records — surfaced in summary; resolution is Wave 3 verification matrix.
- Exporting full record content (the manifest is sparse by design; full content stays in `groundtruth.db`).
- Selective SQL extraction at cutover — that's ISOLATION-018 work; this slice produces the manifest that drives it.
- Exporting `assertion_runs` (excluded per §2 — high volume, low information per row; live assertions tracked via spec's assertions field).
- ChromaDB embeddings — separate Stage C slice (`_chromadb_regen.py`).

## 10. Codex Review Asks

1. Confirm the 17-source roster in §2 is complete and correct, or flag missing `KnowledgeDB.list_*()` methods that should be inventoried (or sources that should be excluded for the same reason `assertion_runs` is excluded).
2. Confirm the §3.2 content-scan override rules correctly capture the Slice 5 F1 lesson uniformly across all KB record types (not just work_items where it was originally caught).
3. Confirm Test 2 (assertion that `list_deliberations` is called, not `search_deliberations`) — same Codex `-002` regression guard from Slice 6, reused here for the deliberations source.
4. Confirm the **sparse manifest** design (id+type+classification+signal, no content) is the right granularity for ISOLATION-018 cutover. Alternative: include record body in manifest to avoid SQL re-query at cutover; tradeoff is manifest file size (~50-200 MB instead of ~2-4 MB).
5. Confirm the per-type summary file roster in §4 (17 files, one per source) is the right organizational shape, vs. a single combined file or a different grouping.
6. Confirm the type-specific overrides in §3.3 (test path classification, procedure classification by kind, document classification by topic) are correct. Specifically: the `test_release_candidate_gate.py` example as `unclassified` — does the `mixed_scope_test` signal correctly handle the broader pattern, or should the slice define a more specific list of "known mixed-scope tests"?
7. Confirm exclusion of `assertion_runs` is appropriate. Alternative: include the most-recent run per assertion only.
8. **GO / NO-GO** on Slice 8.

## 11. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
