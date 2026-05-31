# Current State Analysis — ChromaDB Vector Substrate

**Investigation run:** 20260528T002632Z
**Bridge thread:** `gtkb-chromadb-vector-continuity-v1-cut-scoping`
**Work item:** WI-3395
**Scope:** read-only inspection of the live `.groundtruth-chroma/` substrate, `groundtruth.db` deliberations table, and Python query API surface.

## 1. ChromaDB Store Inventory

**Location:** `.groundtruth-chroma/` at project root.

**Sub-tree:**
```
.groundtruth-chroma/
├── a44b3005-eddf-4379-8f2b-e59f5fb8060c/   (collection data dir; UUID per collection)
└── chroma.sqlite3                           (136 MB; metadata + persistence)
```

**Collections:** 1
- Name: `deliberations`
- Document count: **20,224 chunks**

**Sample document ID format:** `DELIB-NNNN::v1::chunk-NNN`
- Compound key: `<delib_id>::<version>::<chunk_index>`
- One DELIB record may produce multiple chunks (text-chunking for embedding); see `chunk_count` metadata for total chunks per record.

**Sample metadata schema (per-chunk):**
- `delib_id` — the canonical DELIB identifier (e.g., `DELIB-0003`, `DELIB-S347-...`)
- `version` — append-only version of the source record
- `chunk_index` — 0-based position within the chunked record
- `chunk_count` — total chunks produced from this record's content
- `title` — human-readable record title
- `outcome` — record outcome classification (e.g., `owner_decision`, `loyal_opposition_review`)
- `source_type` — origin classification (e.g., `owner_conversation`, `bridge_thread`, `lo_report`)
- `source_ref` — provenance path (often a bridge file or memory file)
- `origin_project` — project association (often null)
- `origin_repo` — repository association (typically `groundtruth-kb`)
- `sensitivity` — redaction classification
- `redaction_state` — applied redaction status
- `changed_at` — UTC timestamp

## 2. MemBase Deliberations Table Inventory

**Location:** `groundtruth.db` → `deliberations` table.

**Counts:**
- Total rows: **2,640** (multiple versions per record permitted)
- Distinct DELIB IDs: **2,622**
- Mean versions per DELIB: 1.007 (most have a single version; a few have 2+)

**ID format range:**
- **Oldest:** `DELIB-0001` (numeric four-digit padding, ~2026-Q1 era)
- **Newest:** `DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION-2026-05-27` (session-prefixed descriptive ID, current convention)
- **Two distinct ID conventions in use:**
  - Numeric: `DELIB-NNNN` (e.g., `DELIB-0001` through `DELIB-2497`)
  - Session-prefixed descriptive: `DELIB-SNNN-<TOPIC>-<DATE>` (e.g., `DELIB-S347-V1-RELEASE-STRATEGY-CHOICES-2026-05-13`)
- A v1.0 cut Option A reset would need to consider BOTH conventions; a substrate-agnostic backfill design should preserve the convention distinction.

## 3. ChromaDB-to-MemBase Binding

**Binding mechanism:** The chunk ID's `<delib_id>::` prefix mechanically references the `id` field of the source `deliberations` table row. The `delib_id` metadata field repeats the same value for query convenience.

**Asymmetry:** ChromaDB chunks outnumber MemBase rows (~20,224 chunks vs 2,640 rows = ~7.6 chunks per row average). This is because the deliberation harvest text-chunks long records (LO reports, owner-conversation transcripts) into multiple embedded segments to fit embedding-model token limits.

**Implication for backfill:** A naïve "translate IDs in MemBase" approach would miss the chunk-level binding. The backfill must operate on the ChromaDB chunk-ID level, applying HIST-DELIB-NNNN prefix to BOTH the chunk-ID prefix AND the `delib_id` metadata field.

## 4. Query API Surface

**Canonical Python API:**
- `KnowledgeDB.search_deliberations(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]` at `groundtruth-kb/src/groundtruth_kb/db.py:5959`
- Returns a list of dicts with semantic-score, DELIB metadata, and chunk content excerpt.

**Canonical CLI surface:**
- `python -m groundtruth_kb deliberations search "<query>" [--limit N] [--json]`
- Output format: human-readable header per hit (`[semantic score=N.NNN] DELIB-XXX v1: <title> / <preview>`) or JSON if `--json`.

**Identified consumers (read-only grep on `search_deliberations|chroma.*query|chroma.*search`):**

| Consumer | Location | Type |
|---|---|---|
| `KnowledgeDB.search_deliberations` | `groundtruth-kb/src/groundtruth_kb/db.py` | core API |
| `gt deliberations search` CLI | `groundtruth-kb/src/groundtruth_kb/cli.py` | user surface |
| `proposal_autoload` (Prior Deliberations seeder) | `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py` | bridge tooling |
| Bridge skill docs (CLI invocation examples) | `.claude/skills/bridge/SKILL.md`, `.codex/skills/bridge/SKILL.md`, `groundtruth-kb/templates/skills/bridge/SKILL.md` | documentation |
| Test fixture | `groundtruth-kb/tests/test_cli_bridge_propose.py` | regression |
| Owner-facing bridge proposals (search queries cited in Prior Deliberations) | various `bridge/` files | provenance evidence |

**Session-start hook consumers:** A grep of `.claude/hooks/*.py` and `.codex/gtkb-hooks/*.py` did not surface a direct ChromaDB query from any hook in this audit (no immediate consumer dependency at session-start time). This may be worth confirming separately if hooks gain ChromaDB awareness in future slices.

## 5. Cross-Reference: Citation Surface (DELIB ID Usage in Codebase)

Quantification of DELIB citations across the repository (grep counts of `DELIB-[A-Z0-9-]+` patterns):

| Subtree | Total citations | Note |
|---|---:|---|
| `bridge/` | 11,132 | Specification Links, Prior Deliberations sections, verdicts |
| `independent-progress-assessments/` | 7,197 | LO reports, audit reports, investigation evidence |
| `memory/` | 232 | Operational notes, feedback files, deliberation tracker |
| `.claude/rules/` | 70 | Rule-cited owner-decision references |
| **Total** | **18,631** | (citation hits, not distinct DELIB IDs) |

**Implication:** an identifier-reset cut without provenance preservation would invalidate ~18,631 textual citation hits across the codebase. Even with a text-translation manifest in place, semantic-search retrieval (the ChromaDB substrate) would degrade because the underlying vector embeddings remain bound to old IDs in the chunk metadata. The text-manifest mitigation is SUFFICIENT for textual citation translation but INSUFFICIENT for retrieval continuity.

## 6. Storage Footprint

- `.groundtruth-chroma/chroma.sqlite3`: 136 MB
- `groundtruth.db` (full DB): ~unknown — separate measurement scope
- A full HIST-DELIB-NNNN backfill would approximately double the ChromaDB footprint (current 20,224 chunks + HIST-prefixed copies, plus some metadata overhead).

## 7. Read-Only Confirmation

This analysis is the output of read-only inspection only. No mutation occurred against `.groundtruth-chroma/`, `groundtruth.db`, or any consumer file. The inspection commands are documented in the post-implementation report.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
