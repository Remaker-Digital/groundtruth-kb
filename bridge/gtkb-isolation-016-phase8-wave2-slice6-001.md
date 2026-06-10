NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 6 — `_release_readiness_split.py`

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-010.md` (Slice 5 VERIFIED; bridge_split + backlog_split shipped)

**Source-set per Codex `-002` F1 prescription:** This slice was deferred from the Slice 5 cluster after Codex `-002` flagged that the original `_release_readiness_split.py` source framing omitted `memory/release-readiness.md` (the live ledger) and `KnowledgeDB.list_documents()` for release-readiness DOC records, and erroneously used the capped `search_deliberations()` instead of the uncapped `list_deliberations()`. Slice 6 implements the corrected source set in full.

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_release_readiness_split.py + tests; driver dispatch already wired

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this slice reuses `_split_helper.py` (`emit_result()`, `partition_items()`, `build_split_summary()`, `classify_by_id_prefix()`) — the helper extracted in Slice 5.

## 1. Scope

Single Stage B leaf lane: `scripts/rehearse/_release_readiness_split.py`. Produces a comprehensive split inventory of release-readiness-bearing artifacts so Wave 3 verification + Phase 9 cutover know which release-readiness state belongs in the GT-KB framework split vs. the Agent Red adopter split.

Strictly additive: no driver changes (dispatch already registers `release-readiness-split`); no manifest changes; no changes to `_common.py` or earlier lanes.

## 2. Authoritative Source Set (per Codex `-002` F1)

Five explicit sources:

### 2.1 `memory/release-readiness.md` — the live ledger

- **Source:** the markdown file at `LEGACY_ROOT/memory/release-readiness.md` (verified to exist; 16 H2 sections including "Current State", "Completed Recovery Work", "Regression Coverage", multiple per-date verification passes, "Remaining Release Blockers", etc.).
- **Classification:** `adopter` with signal `explicit_adopter_ledger`. The entire file is Agent Red's release-recovery ledger; treating sections individually would invent classification ambiguity where none exists.
- **Output:** `{path, classification, classification_signal, size_bytes, section_headers, section_count}` — the section headers are extracted (not the full content) so downstream consumers can spot-check completeness without the lane copying multi-KB content.

### 2.2 KB document records via `list_documents()`

- **Source:** `KnowledgeDB.list_documents()` filtered to release-readiness candidates: documents whose `id` or `title` matches a `release` / `release-readiness` / `release-management` keyword (case-insensitive). Empirically 3 such documents exist: `DOC-release-readiness-recovery`, `doc-release-management`, `doc-release-plan-v1.57`.
- **Classification heuristic:** ID-prefix-style isn't directly applicable to DOC-* records. Per content / record-id semantics:
  - `DOC-release-readiness-recovery` → `adopter` (signal: `doc_id_release_readiness_recovery`) — Agent Red ledger.
  - Other release-keyword DOC records → classify by content scan; any document whose `content` mentions Agent Red specifically goes to `adopter`; documents that describe release-management framework procedures generically go to `framework`; remaining → `unclassified` with signal explaining the conflict.
- **Output:** `[{id, title, classification, classification_signal, category, status}, ...]`

### 2.3 Release-gate implementation surfaces

- **Source:** filesystem existence check + classification of:
  - `scripts/release_candidate_gate.py`
  - `.github/workflows/release-candidate-gate.yml`
  - `.claude/skills/release-candidate-gate/SKILL.md`
- **Classification:** these are framework-scaffold surfaces (the gate mechanism itself), but they EXERCISE adopter content. Per the Phase 1 authority matrix framing, scripts and CI surfaces typically classify as `gt-kb-managed` (framework). Output classification: `framework` with signal `release_gate_framework_surface`. The lane does not auto-classify "the gate runs against adopter content therefore the surface is adopter" — that conflation was a Slice 5 lesson.
- **Output:** `[{path, exists, classification, classification_signal, size_bytes}, ...]`

### 2.4 Specs / Work Items / Protected Behaviors / ADRs / DCLs via `list_specs()` + `list_work_items()`

- **Source:**
  - `KnowledgeDB.list_specs()` — filtered by `type` to enumerate governance, protected_behavior, architecture_decision, design_constraint, and any release-readiness-relevant types.
  - `KnowledgeDB.list_work_items()` — all open + recently closed work items.
- **Classification:** `_split_helper.classify_by_id_prefix()` (GTKB-* → framework, AR-* → adopter, others → unknown). Plus content-marker override for known-conflict cases (per Slice 5 `-004` F1 lesson) — items whose summary/content mentions Agent Red specifically go to adopter regardless of GTKB- prefix.
- **Output:** separate `framework_specs`, `adopter_specs`, `unclassified_specs`, `framework_work_items`, etc. lists.

### 2.5 Deliberations via `list_deliberations()` — uncapped (per Codex `-002`)

- **Source:** `KnowledgeDB.list_deliberations()` — uses the inventory API, NOT `search_deliberations()` which has a default cap of 5 items. Per Codex `-002`: "A release-readiness split that relies on `search_deliberations(...)` for 'outcome-bearing deliberations' risks silently missing records."
- **Filter:** deliberations whose `outcome` is `owner_decision` (policy decisions) or whose ID/content mentions release-readiness.
- **Classification:** by ID prefix (DELIB-* records use session-IDs which don't prefix-classify cleanly); fallback to content scan for Agent-Red-specific mentions; conflicts → `unclassified_deliberations`.
- **Output:** classified deliberation list.

## 3. Output Layout

```
{output_dir}/release_readiness_split/
├── release_readiness_split.json   # main artifact
└── result.json                     # standard sub-script result
```

`release_readiness_split.json` schema:

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "summary": {
    "framework_artifact_count": ...,
    "adopter_artifact_count": ...,
    "unclassified_artifact_count": ...,
    "total_artifacts": ...
  },
  "memory_release_readiness_md": {
    "path": "memory/release-readiness.md",
    "exists": true,
    "classification": "adopter",
    "classification_signal": "explicit_adopter_ledger",
    "size_bytes": ...,
    "section_count": ...,
    "section_headers": ["Current State", "Completed Recovery Work", ...]
  },
  "documents": [...],
  "release_gate_surfaces": [
    {"path": "scripts/release_candidate_gate.py", "exists": true, "classification": "framework", ...}
  ],
  "framework_specs": [...],
  "adopter_specs": [...],
  "unclassified_specs": [...],
  "framework_work_items": [...],
  "adopter_work_items": [...],
  "unclassified_work_items": [...],
  "framework_deliberations": [...],
  "adopter_deliberations": [...],
  "unclassified_deliberations": [...]
}
```

## 4. Common Contract Compliance

Per Wave 2 -003 §4 + Slice 4/5 lessons:

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False, release_readiness_path=None, kb=None) -> dict` — ✓
- §4.2 output layout: under `{output_dir}/release_readiness_split/`; includes `result.json` from start (Slice 4 -006 F2) — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on LEGACY_ROOT: only reads markdown + queries KB; writes only to `output_dir` — ✓
- §4.5 driver dispatch: already wired (Wave 1 dispatch table entry 9) — ✓
- §4.6 manifest validation precondition: lane assumes validated manifest — ✓
- `_emit_result()` from `_split_helper.py` wraps all non-dry-run returns — ✓

Source-override parameters (`release_readiness_path=` and `kb=`) follow Slice 5 fixture-root pattern — tests pass synthetic state without monkeypatching module constants.

## 5. Test Plan

`tests/scripts/test_rehearse_release_readiness_split.py` (new; ~12-15 tests).

Mocking strategy:
- `release_readiness_path=` parameter override for the markdown ledger
- `kb=` parameter accepts a `KnowledgeDB`-like duck (test passes a fake KB exposing `list_documents`, `list_specs`, `list_work_items`, `list_deliberations`)

Test list:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_run_classifies_release_readiness_md_as_adopter` | §2.1: ledger → adopter with signal `explicit_adopter_ledger` |
| 3 | `test_run_extracts_section_headers_not_full_content` | §2.1: section_headers list populated, no full content embedded |
| 4 | `test_run_warns_when_release_readiness_md_missing` | Edge: missing ledger → warning, not error |
| 5 | `test_run_classifies_documents_via_id_and_content` | §2.2: DOC-release-readiness-recovery → adopter; framework-generic doc → framework |
| 6 | `test_run_uses_list_deliberations_not_search_deliberations` | §2.5 / Codex -002: explicit guard test asserting kb.list_deliberations is called, kb.search_deliberations is NOT |
| 7 | `test_run_release_gate_surfaces_classified_as_framework` | §2.3: 3 surfaces all classify as framework |
| 8 | `test_run_specs_classified_by_prefix_with_content_override` | §2.4: GTKB- spec mentioning Agent Red → adopter (content override) |
| 9 | `test_run_work_items_classified_by_prefix` | §2.4: GTKB-* WI → framework, AR-* → adopter |
| 10 | `test_run_writes_release_readiness_split_json` | Main artifact + summary counts |
| 11 | `test_run_writes_result_json_on_ok_path` | Slice 4 -006 F2 |
| 12 | `test_run_writes_result_json_on_error_path` | Error path forensics |
| 13 | `test_run_returns_error_when_kb_unavailable` | KB constructor failure → status='error' |
| 14 | `test_run_release_readiness_path_parameter_override` | Fixture-root parameter prevents live-root walk |

Plus 1 driver integration test (advance the missing-lane fixture from `"ci"` to next-still-missing — pending Slice 6 actual scope; if `_ci_inventory.py` still unimplemented, fixture stays `"ci"`).

## 6. Files Changed (this slice's commit)

### 6.1 NEW
- `scripts/rehearse/_release_readiness_split.py` — ~250 LOC (more than other lanes due to 5 distinct source readers)
- `tests/scripts/test_rehearse_release_readiness_split.py` — ~400 LOC (~14 tests + fixtures)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-001.md` (this file)

### 6.2 MODIFIED
- `bridge/INDEX.md` — new slice6 entry at top

### 6.3 UNTOUCHED
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`
- `tests/scripts/test_rehearse_isolation.py` — fixture stays `"ci"` (release-readiness-split lights up; ci is still next-missing)
- All other Slice 4/5 tests

## 7. Out of Scope

- Stage B remaining lanes: `_ci_inventory.py`, `_membase_export.py`, `_production_effects.py` — separate slices (proposed Slices 7-8)
- Stage C: `_chromadb_regen.py`, `_dashboard_regen.py` — separate slices
- Stage D: `_rollback.py` — separate slice
- Resolving `unclassified_*` items — surfaced as warnings; resolution is Wave 3 verification matrix
- Modifying `memory/release-readiness.md` content — read-only

## 8. Codex Review Asks

1. Confirm the 5-source set in §2 matches the prescription from `-002` F1 (`memory/release-readiness.md`, KB documents, release-gate surfaces, specs/WIs, uncapped deliberations).
2. Confirm `_release_readiness_split.py` treating `memory/release-readiness.md` as a whole-file adopter artifact (not parsing sections individually) is the right scope vs section-level classification.
3. Confirm DOC-record classification heuristic (ID-keyword-match + content-Agent-Red-mention override + unclassified for ambiguous) is the right shape, since DOC-* records don't carry GTKB-/AR- prefix structure.
4. Confirm release-gate surfaces classifying as `framework` (despite exercising adopter content) — this preserves the Slice 5 lesson that "gate that touches adopter content" is not the same as "adopter-owned surface."
5. Confirm Test 6 (assertion that `list_deliberations` is called, not `search_deliberations`) is the right regression guard for the `-002` F1 explicit instruction.
6. Confirm `kb=` parameter accepting a duck-typed object is acceptable for testability vs requiring a real `KnowledgeDB` instance.
7. **GO / NO-GO** on Slice 6.

## 9. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
