# Implementation Bridge: DA Governance Completeness

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Scope bridge references:**
- `bridge/gtkb-da-governance-completeness-003.md` (REVISED proposal)
- `bridge/gtkb-da-governance-completeness-004.md` (Codex scope GO with 7 conditions)

**Discharges:** all 7 Required Implementation Conditions from `-004` §"Required Implementation Conditions" and both owner-question panels from `-003` §"Open Questions for Owner".

**Authorization chain:** Scope GO at `-004` authorizes filing this implementation bridge only; per `.claude/rules/codex-review-gate.md`, no GT-KB source, doc, hook, template, script, DB, or managed-artifact mutation may begin until Codex GOs this file.

---

## 1. Executive Summary

This implementation bridge translates the 8-spec, 11-phase scope in `-003` into an executable plan. The plan is structured so that:

1. **Phase 0 is a hard owner-decision gate** for Phases 2 (redaction severity), 5 (preflight bypass), and 6 (transcript mode). Phases 1, 3, 4, 7, 8 are Phase-0-independent and may begin immediately on Codex GO.
2. **Phase 9 (wrap-gate expansion)** splits into two parts: 9a (harvest-independent assertions — LO coverage, owner-conversation coverage, transcript coverage, redaction rescan, DB-routing invariant) executes with this bridge; 9b (bridge-thread assertion) defers until `gtkb-da-harvest-coverage-implementation` reaches VERIFIED.
3. **Every hook, script, or scaffold surface change** gets a managed-artifact registration, a scaffold-settings test update, and focused test coverage — the Codex Finding #3 Medium-severity condition is discharged per-surface, not hand-waved.

All DA mutation paths (new extractors, new backfill scripts, new hooks that write deliberations) are **required** to route through `KnowledgeDB.insert_deliberation()` or `KnowledgeDB.upsert_deliberation_source()`. A DB-routing invariant test enumerates call sites and asserts no SQLite bypass. This closes the Codex Finding #4 condition.

---

## 2. Discharge of 7 Required Implementation Conditions (from `-004`)

| # | Condition from `-004` | Where discharged in this bridge |
|---|-----------------------|---------------------------------|
| 1 | Obtain owner decisions for transcript mode, partial-redaction severity, preflight bypass model before implementation starts | §3 Phase 0 gate; §4 hard-block on Q1/Q2/Q3 answers for Phases 2/5/6 |
| 2 | Preserve harvest-coverage sequencing gate for bridge-thread-dependent wrap assertions | §5.9 Phase 9 split into 9a (now) / 9b (deferred until `gtkb-da-harvest-coverage-implementation` VERIFIED) |
| 3 | Keep source-ref validation non-breaking for DB/CLI v1 | §5.3 Phase 3: warn-only at DB/CLI; producer scripts strict-validate before insert; four CLI regression tests named |
| 4 | Update managed artifacts, scaffold settings, and focused hook tests for all new hooks and shared helpers | §5.7 Phase 7 managed-artifact registration matrix + scaffold-settings test update + test list discharging Codex Finding #3 line-item by line-item |
| 5 | Keep all new DA inserts on DB API path; no direct SQLite deliberation writes from hooks/scripts | §5.2 Phase 2 DB-routing invariant test (`tests/test_da_db_routing_invariant.py`); §6 test inventory lists sites enumerated |
| 6 | Provide dry-run artifacts and owner approval before any live backfill or transcript-harvest mutation | §5.4 Phase 4 LO-report backfill dry-run JSON; §5.6 Phase 6 transcript dry-run JSON; both require explicit owner AskUserQuestion approval before `--execute` |
| 7 | Post-implementation report must include focused test output for new hook/redaction/source-ref/transcript/backfill paths + current DA count evidence | §7 Post-Impl Report Contract enumerates required evidence artifacts |

---

## 3. Phase 0 — Owner Decision Gate (hard gate for Phases 2, 5, 6)

**Mechanism:** single AskUserQuestion round in the live session that will execute Phases 2/5/6. Answers captured as `source_type='owner_conversation'` deliberations immediately (this is the **only** Phase-0-era mutation allowed before Phase 1 spec recording, and it uses the existing DA insert path, not the new hooks).

### Q1 — Transcript extraction mode (blocks Phase 6)

| Option | Default? | Rationale |
|--------|----------|-----------|
| (a) Heuristic-only v1 with dry-run gate before first live insert | ✅ Proposed default | Machine-scalable; dry-run + owner approval protects against heuristic misses before any DA mutation. |
| (b) Manual annotation pass per session | | Highest fidelity, highest owner burden; does not scale across multi-session days. |
| (c) Hybrid: heuristic for GOV-09 patterns + manual for non-GOV-09 discussion | | Middle path; splits processing cost but doubles the governance surface. |

**Effect on implementation:** (a) enables Phase 6 as specified in `-003` §C. (b) reduces Phase 6 to a manual-annotation CLI and makes the six v1 tests trivial or inapplicable. (c) requires Phase 6 to ship both paths with a mode switch.

### Q2 — Partial-redaction severity (blocks Phase 2 residual-rescan behavior)

| Option | Default? | Rationale |
|--------|----------|-----------|
| (a) BLOCK for `owner_conversation` + `session_harvest`; WARN for `bridge_thread` + `lo_review` | ✅ Proposed default | Upstream-redacted sources (bridge/LO) warn-only; fresh-ingestion sources (owner conv / transcripts) BLOCK to prevent partial-secret storage. |
| (b) BLOCK for all source types | | Safest; risks wrap failure on unexpected residual matches. |
| (c) WARN for all source types | | Never blocks wrap; risks partial-secret storage. |

**Effect on implementation:** determines `redaction_state='partial'` behavior and whether Phase 9 wrap-gate raises ALARM when partial inserts are detected.

### Q3 — Preflight bypass authorization model (blocks Phase 5)

| Option | Default? | Rationale |
|--------|----------|-----------|
| (a) Session-local flag file `.groundtruth/preflight-bypass.flag` + env-var `GT_DA_PREFLIGHT_BYPASS=1` for infra repair | ✅ Proposed default | Matches S294-class recovery pattern where the gate itself would block the repair. |
| (b) Session-local flag file only, no env var | | Slightly safer; infrastructure-repair sessions must create the file manually. |
| (c) No bypass; emergency repairs must use existing-thread response files (not blocked by the gate) | | Strictest; may block legitimate S294-class outages if the tracker itself is broken. |

**Effect on implementation:** determines which bypass surfaces `delib-preflight-gate.py` honors and what metadata is logged when the bypass fires.

### Phase 0 exit criteria

- Q1, Q2, Q3 answers captured as a single `owner_conversation` deliberation row.
- Owner-decision deliberation ID (DELIB-NNNN) recorded in the Phase 1 spec bodies as rationale evidence.
- No other mutation authorized by Phase 0.

---

## 4. Hard Sequencing Gates

| Gate | Blocks phase(s) | Released when |
|------|-----------------|---------------|
| Q1 answer | Phase 6 | Owner answers Q1 in AskUserQuestion round |
| Q2 answer | Phase 2 residual-rescan behavior; Phase 9a ALARM semantics | Owner answers Q2 |
| Q3 answer | Phase 5 | Owner answers Q3 |
| `gtkb-da-harvest-coverage-implementation` VERIFIED | Phase 9b (bridge-thread wrap assertion) | Codex VERIFIED on that thread |
| Codex GO on this bridge | All phases | Codex GO issued |

**Explicit non-blockers:** Phases 1, 3, 4, 7, 8, and 9a are **not** gated on Q1/Q2/Q3 and not gated on harvest-coverage VERIFIED. They may begin immediately on Codex GO.

---

## 5. Per-Phase Execution Plan

### 5.1 Phase 1 — Spec recording (Phase-0-independent)

**Target:** 8 specs in GT-KB MemBase via `db.insert_spec()`.

| Draft ID | Short | Type | Tags |
|----------|-------|------|------|
| SPEC-DA-GOV-LO-COVERAGE | Every LO report filed in session MUST reach DA before wrap completes | requirement | da-governance, completeness |
| SPEC-DA-GOV-OWNER-DECISION-CAPTURE | Every AskUserQuestion response + every GOV-09 owner message archived as `owner_conversation` by end of turn | requirement | da-governance, completeness |
| SPEC-DA-GOV-TRANSCRIPT-EXTRACT | Session-wrap MUST extract owner decisions + substantive discussions into DA as `session_harvest` per v1 contract | requirement | da-governance, completeness |
| SPEC-DA-GOV-REDACTION-ROUTING | All DA inserts MUST go through `insert_deliberation()` / `upsert_deliberation_source()`; residual re-scan test MUST pass | requirement | da-governance, redaction |
| SPEC-DA-GOV-SOURCE-REF-IDENTITY | `insert_deliberation()` MUST emit structured warnings for source-ref pattern mismatches (warn-only v1); producer scripts MUST strictly validate | requirement | da-governance, identity |
| SPEC-DA-GOV-BACKFILL-FRAMEWORK | Reusable missing-source backfill framework with idempotent content-hash dedupe | requirement | da-governance, backfill |
| SPEC-DA-GOV-PREFLIGHT-HARDBLOCK | PreToolUse hook MUST hard-block `Write` to new-topic `bridge/` files without a same-turn search log entry | requirement | da-governance, preflight |
| SPEC-DA-GOV-WRAP-GATE | Session wrap-hook MUST assert LO/owner-conversation/bridge/transcript coverage before marking wrap complete | requirement | da-governance, wrap |

Each spec body cites DELIB-0715, DELIB-0719, and the Phase-0 owner-decision DELIB as rationale evidence. Status at insert: `specified`.

**Acceptance:** `gt spec list --tag da-governance` returns exactly 8 rows, all `specified`.

### 5.2 Phase 2 — Redaction routing invariant + residual re-scan (Q2-gated for severity only)

**Zero DB-redaction reimplementation.** Preserve `KnowledgeDB.redact_content()`, `insert_deliberation()`, `upsert_deliberation_source()`.

**New test files:**
- `tests/test_da_db_routing_invariant.py` — AST-walks `scripts/harvest_session_deliberations.py`, `scripts/_backfill_framework.py` (new, Phase 8), `templates/hooks/delib-preflight-gate.py` (new, Phase 7), `templates/hooks/session-health.py` (extended, Phase 9), and any new Phase-5/6 extractor modules. Asserts each DA-writing call resolves to `KnowledgeDB.insert_deliberation` or `KnowledgeDB.upsert_deliberation_source`. Any direct `sqlite3.*` call in these files that targets a `deliberations*` table is a test failure.
- `tests/test_da_residual_rescan.py` — posts credential-pattern content to `insert_deliberation()`, asserts redaction applies, then rescans the stored (redacted) content using `credential_patterns.db_pattern_list()`. Asserts residual matches set `redaction_state='partial'`. Severity behavior (BLOCK vs WARN) exercised per-source-type per Q2 answer.

**Code changes:**
- Minimal: if Q2 answer = BLOCK for any source type, add a post-redaction re-scan inside `insert_deliberation()` that either raises `GTRedactionError` (BLOCK) or sets `redaction_state='partial'` + `redaction_notes` (WARN) depending on source_type. Q2 answer determines the per-source-type map.
- If Q2 = (c) WARN-all, no behavior change; only tests are new.

**Acceptance:** both new test files green; existing 1161-test baseline stays green (full-suite regression).

### 5.3 Phase 3 — Source-ref validation (warn-only v1)

**Code changes:**
- `src/groundtruth_kb/db.py::insert_deliberation()` and `upsert_deliberation_source()`: add non-raising validation that compares `source_ref` against a per-`source_type` pattern table. Mismatch → emit a structured warning line to `.groundtruth/delib-insert-warnings.jsonl` (newline-delimited JSON; one record per warning with `{timestamp, source_type, source_ref, pattern, deliberation_id}`). Insert proceeds normally.
- Producer scripts (`scripts/harvest_session_deliberations.py`, the Phase-4 LO-report backfill, any Phase-5 hook helpers, the Phase-6 transcript extractor): strict-validate their source refs before calling `insert_deliberation()`. Producer-side failure raises `GTSourceRefError`, which is caught and logged by the orchestrator.

**Pattern table (matches `-003` §E table):**

| source_type | Canonical pattern | Producer class |
|-------------|-------------------|----------------|
| `bridge_thread` | `bridge/{thread-name}-*.md` | producer-owned |
| `lo_review` | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-{date}-{topic}.md` | producer-owned |
| `session_harvest` | `session:{session-id}:{turn-start}-{turn-end}` | producer-owned |
| `owner_conversation` | `{YYYY-MM-DDTHH:MM}-{topic-slug}` | producer-owned |
| `report` | file path OR `methodology-review:{topic}` legacy-compat OR free text (CLI) | mixed; warn-only v1 |
| `proposal` | any non-empty string; recommended bridge file path or topic slug | user-supplied; warn-only v1 (never strict) |

**New/modified tests:**
- `tests/test_source_ref_validation.py` — positive + negative cases per source_type; asserts warn-only at DB layer.
- `tests/test_cli_deliberations.py` (regression): four tests that re-assert currently passing refs (`test.md`, `upsert-auto.md`, `t.md`, `bridge:msg-abc`) continue to insert successfully with no exception.

**Acceptance:** new test file green; existing `tests/test_cli_deliberations.py` passes unmodified (no test file edits — pure regression).

### 5.4 Phase 4 — LO-report coverage closure + retroactive backfill (Phase-0-independent)

**Code changes:**
- Extend `scripts/harvest_session_deliberations.py` to enumerate all `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` files ≥ 100 bytes; cross-check against `lo_review` rows by `source_ref`.
- First adopter of the Phase-8 backfill framework. Dry-run mode emits JSON to `bridge/gtkb-da-governance-completeness-lo-backfill-dryrun-{YYYY-MM-DD}.json` with `{source_ref, content_hash, spec_refs, wi_refs, preview_200chars}` per candidate row.
- Execute mode (`--execute`) gated on owner AskUserQuestion approval of the dry-run JSON (same pattern as bridge-thread sweep).

**Expected backfill volume:** 11 missing LO-report refs (per `-003` baseline: 660 INSIGHTS files ≥100B − 649 `lo_review` rows = 11).

**Tests:**
- `tests/test_lo_report_backfill.py` — dry-run produces JSON with expected schema; idempotent re-run produces zero new rows; tempdir fixture with 3 synthetic INSIGHTS files (2 already in DA, 1 missing) produces exactly 1 candidate row.

**Acceptance:** dry-run JSON produced; owner approval recorded as `owner_conversation` DELIB; `--execute` inserts exactly 11 rows (or the current delta count at execute time); idempotent rerun produces zero new rows.

### 5.5 Phase 5 — Preflight hook infrastructure (Q3-gated)

**New files:**
- `templates/hooks/_delib_common.py` — shared topic-normalization (extracted from current `delib-search-gate.py` and `delib-search-tracker.py`). Stopword set + token hash + topic-overlap predicate. Single source of truth; consumed by all three hooks (`delib-search-gate.py`, `delib-search-tracker.py`, new `delib-preflight-gate.py`), and by new `turn-marker.py`.
- `templates/hooks/turn-marker.py` — `UserPromptSubmit` hook, stamps `{turn_id, started_at}` to `.groundtruth/current-turn.jsonl` on every prompt. Ordering: runs **before** `delib-search-gate.py` in the settings.json hook list for UserPromptSubmit.
- `templates/hooks/delib-preflight-gate.py` — `PreToolUse` hook. Logic:
  1. Read tool input `file_path`. If not matching `bridge/[^/]+-\d{3}\.md$`, return pass.
  2. Extract bridge stem (e.g., `{descriptive-name}` from `{descriptive-name}-NNN.md`). Scan `bridge/INDEX.md` for this stem. If stem is already present → this is a response/post-impl file → pass. If stem is not present → new-topic write → require same-turn search proof.
  3. Read `.groundtruth/current-turn.jsonl` latest line → `started_at`. Fallback: if file missing/corrupt, use 10-minute wall-clock window (configurable via `GT_DA_PREFLIGHT_FALLBACK_SECONDS`).
  4. Read `.groundtruth/delib-search-log.jsonl`. Find entries with `timestamp >= started_at`. If none → emit `emit_deny()` with ALARM message directing Prime to run `search_deliberations()` first.
  5. Normalize the bridge topic (via `_delib_common.py`). Any same-turn search entry with topic overlap → pass. Otherwise deny.
  6. Bypass (per Q3):
     - If `.groundtruth/preflight-bypass.flag` exists → pass; log structured `owner_conversation` row `bypass_authorization`.
     - If Q3 default (a): env `GT_DA_PREFLIGHT_BYPASS=1` → pass; log structured `owner_conversation` row `bypass_authorization`.
     - Otherwise (Q3 = (b) or (c)): no env bypass.
  7. Failure modes: search-log missing/unreadable → ALARM + deny (conservative). Bypass file older than 24h → session-start hook deletes it + WARN on next prompt.

**Scaffold + managed-artifact updates:**
- `templates/managed-artifacts.toml`: register `turn-marker.py`, `delib-preflight-gate.py`, `_delib_common.py` in the appropriate sections (UserPromptSubmit, PreToolUse, shared).
- `tests/test_scaffold_settings.py`: update expected hook lists for `UserPromptSubmit` (now `turn-marker.py`, `delib-search-gate.py`, `intake-classifier.py` — order matters) and `PreToolUse` (existing six + `delib-preflight-gate.py`).

**New tests (`tests/test_delib_preflight_gate.py`) — discharging Codex Finding #3 line-by-line:**

1. Missing/unreadable search log blocks.
2. Missing `.groundtruth/current-turn.jsonl` → fallback 10-minute window applies; stale entries block.
3. Corrupt `current-turn.jsonl` → fallback window applies.
4. Stale search (before current turn, outside fallback) blocks.
5. Same-turn search with topical overlap passes.
6. Same-turn search with topic mismatch blocks.
7. Owner-authorized bypass file present → passes; bypass logged.
8. Env-var bypass (Q3-(a) only) → passes; bypass logged.
9. New-topic `bridge/{name}-001.md` write blocks when no stem in INDEX + no same-turn search.
10. New-topic `bridge/{name}-NNN.md` write (where `{name}` not in INDEX) also blocks — proves stem-vs-INDEX catches Codex-side first-of-topic revisions.
11. Existing-thread response file `bridge/{existing-name}-002.md` writes pass regardless of search state.
12. `bridge/INDEX.md` writes pass regardless of search state.
13. Post-impl report for existing thread passes regardless of search state.
14. Windows path separators (`bridge\\name-001.md`) handled correctly.
15. `NotebookEdit` tool path extraction handled correctly.

(15 tests; matches Codex Finding #3 condition line-items plus 2 necessary coverage additions — new-topic `-NNN.md` and `bridge/INDEX.md` pass case.)

**Acceptance:** 15 tests green; scaffold-settings tests updated and green; `templates/managed-artifacts.toml` matches scaffold expectations.

### 5.6 Phase 6 — Transcript extractor (Q1-gated)

**Q1-conditional behavior:**

- Q1 = (a) heuristic-only: proceed with `-003` §C contract in full.
- Q1 = (b) manual: ship a CLI `gt deliberations extract-session --session-id X --turn-range a-b` that reads transcript, prints candidates, accepts owner-confirmed `--write` flag. No heuristic automation. Phase 6 tests adapt to manual-path semantics.
- Q1 = (c) hybrid: two-mode extractor; GOV-09 heuristic pattern + manual fallback.

**Default assumption (Q1 = (a)) files/behavior:**

- `scripts/extract_session_deliberations.py` — consumes JSONL transcript at `~/.claude/projects/<hash>/*.jsonl` (or `$CLAUDE_PROJECT_DIR/.claude/projects/...`). Allow-list: `session_id`, `turn_index`, `timestamp`, `role`, `text`. Prohibited: tool results, system messages, credential values in any field (redaction rescan), attachments, non-project-root paths.
- `source_ref` format: `session:{session_id}:{turn_start}-{turn_end}`. Dedupe via `deliberation_content_hash` column.
- Dry-run: writes `bridge/gtkb-da-governance-completeness-transcript-dryrun-{YYYY-MM-DD}.json` with `{session_id, turn_range, role, text_preview_200chars, classification, redaction_flags}`. Owner approves via AskUserQuestion before `--execute`.
- Missing transcript: WARN to session-health hook (non-blocking for wrap); harvest skip idempotent on future sessions.

**Six required v1 tests** (`tests/test_transcript_extract.py`) matching `-003` §C line-by-line:

1. Short (<50 char) owner message matching GOV-09 specification-language pattern is extracted.
2. Long (≥50 char) conversational owner message not matching GOV-09 is not extracted.
3. Tool-output content excluded from candidate pairs.
4. Credential-pattern content in candidate triggers redaction before insert (routed through `insert_deliberation()` — Phase 2 rescan applies).
5. Missing transcript path → WARN (not ALARM); no partial state inserted.
6. Idempotent rerun on same session → zero new rows.

**Acceptance:** six tests green; dry-run produces schema-valid JSON; full-suite green.

### 5.7 Phase 7 — Owner-decision capture hook (Phase-0-independent after Q-answers logged)

**Clarification vs `-003` Phase 5:** This is distinct from Phase 6 (transcript extraction). Owner-decision capture fires live during a session, not at wrap.

**New files:**
- `templates/hooks/owner-decision-capture.py` — post-`AskUserQuestion` hook (event: `PostToolUse` filtered on tool name `AskUserQuestion`). Captures question, options, chosen option, any free-text notes. Inserts as `source_type='owner_conversation'` with `source_ref` `{YYYY-MM-DDTHH:MM}-{topic-slug}` where `{topic-slug}` is derived from the question's first 60 chars via the Phase-5 topic-normalization helper.
- `templates/hooks/gov09-capture.py` — `UserPromptSubmit` extension (or extension of `spec-classifier.py`, depending on how deeply we can reuse): detects GOV-09 specification-language patterns ("must", "should", numbered requirements) in owner prompts. Matches → inserts owner prompt as `owner_conversation` (redacted if credential-pattern).

**Scaffold + managed-artifact updates:** as per Phase 5 — both new hooks registered, scaffold-settings tests extended.

**Tests (`tests/test_owner_decision_capture.py`):** at least 8:
1. `AskUserQuestion` result with selected option → inserts row with structured metadata.
2. `AskUserQuestion` result with owner free-text → free-text stored in `content`.
3. Duplicate AskUserQuestion in same turn (same question, same options, same answer) → dedupe via content-hash.
4. GOV-09 pattern match in prompt → inserts owner_conversation row.
5. GOV-09 false-positive pattern (e.g., "I should run tests" in conversational context) → threshold tuning; zero row.
6. Credential-pattern content in owner prompt → redaction applies (Phase 2 path).
7. Insert routes through `KnowledgeDB.insert_deliberation()` (Phase 2 DB-routing invariant).
8. Idempotent rerun: same prompt hash in same session → zero new rows.

**Acceptance:** 8 tests green; managed-artifact registration + scaffold test green.

### 5.8 Phase 8 — Backfill framework generalization (Phase-0-independent; precedes Phase 4 execute)

**New files:**
- `scripts/_backfill_framework.py` — shared utilities:
  - `dry_run_schema` validator (required fields: `source_ref`, `content_hash`, per-source-type additional keys).
  - `owner_approval_gate` — reads `bridge/<slug>-dryrun-<date>.json`, requires a matching `owner_conversation` DELIB referencing that JSON file before allowing `--execute`.
  - `idempotent_insert` wrapper around `insert_deliberation()` / `upsert_deliberation_source()`.
  - `coverage_evidence_writer` — post-run JSON with `{inserted, skipped_duplicate, skipped_owner_rejection, failed}`.
  - `warning_baseline_writer` — machine-readable baseline for wrap-gate compare.

**First adopter:** Phase 4 LO-report backfill imports from this module.

**Tests (`tests/test_backfill_framework.py`):** at least 6:
1. Dry-run schema validation rejects malformed JSON.
2. `owner_approval_gate` raises when no matching DELIB found.
3. `owner_approval_gate` passes when matching DELIB present.
4. `idempotent_insert` skips existing content-hash.
5. `idempotent_insert` inserts new content-hash.
6. `coverage_evidence_writer` output schema matches documented contract.

**Acceptance:** 6 tests green; Phase 4 LO-report backfill imports and uses framework.

### 5.9 Phase 9 — Session wrap gate (split 9a now / 9b deferred)

#### 9a (Phase-0-independent, ships with this bridge)

**Extend `templates/hooks/session-health.py` wrap assertions:**

- (A1) All LO reports filed this session are present in DA. Cross-check via git-log of `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` files with `Author-Date >= session_start_utc`.
- (A2) All `AskUserQuestion` interactions this session archived as `owner_conversation`. Cross-check via transcript scan + DA row count for the session's source_refs.
- (A3) Session-transcript extraction ran (Phase 6) and produced zero errors. `.groundtruth/session-extract-log.jsonl` latest entry matches session_id and has `status='ok'`.
- (A4) Redaction re-scan test passed on all inserts this session (Phase 2 residual-rescan). `.groundtruth/delib-residual-rescan-log.jsonl` has zero `status='fail'` rows for this session.
- (A5) No insert bypassed the DB API. Count of direct-SQLite writes to `deliberations*` tables this session = 0 (via audit log).

Any gap → wrap emits ALARM via existing `session-health.py` output channel; doctor records gap details.

#### 9b (deferred — blocks on `gtkb-da-harvest-coverage-implementation` VERIFIED)

- (B1) All bridge-thread activity from this session is archived. Cross-check via `bridge/INDEX.md` diff from session start + `bridge_thread` row count.

Until the harvest-coverage thread is VERIFIED, Phase 9b is **explicitly deferred to a follow-on bridge** (`gtkb-da-governance-completeness-wrap-9b-001.md`). This bridge must not claim Phase 9b complete.

**Tests (`tests/test_wrap_gate.py`):** at least 8 covering A1-A5 positive/negative cases + 1 smoke test proving ALARM emission on gap. B1 tests deferred to 9b bridge.

**Acceptance:** 8 tests green; session-health.py changes pass mypy --strict; full-suite green.

### 5.10 Phase 10 — Dogfooding

End-to-end session run in a fresh session after Phases 1-9a land:
- Verify preflight gate blocks a new-topic bridge write without prior `search_deliberations()`.
- Verify `owner-decision-capture.py` fires on an AskUserQuestion round.
- Verify wrap-gate produces zero gaps when all assertions pass.
- Verify wrap-gate ALARMs on a simulated gap (e.g., create a fake LO report, confirm wrap fails until harvest backfills it).

**Evidence artifacts:**
- `.groundtruth/dogfood-run-{YYYY-MM-DD}.jsonl` log of all gate firings.
- Screenshot or text capture of the ALARM message.

### 5.11 Phase 11 — Post-implementation report + Codex VERIFIED

Contract in §7.

---

## 6. Test Inventory Summary

| Phase | Test file | New tests | Regression |
|-------|-----------|-----------|------------|
| 2 | `tests/test_da_db_routing_invariant.py` | ~8 (per DA-writer module) | — |
| 2 | `tests/test_da_residual_rescan.py` | ~6 (per source_type × Q2 behavior) | — |
| 3 | `tests/test_source_ref_validation.py` | ~12 | — |
| 3 | `tests/test_cli_deliberations.py` | 0 new | 4 existing pass unmodified |
| 4 | `tests/test_lo_report_backfill.py` | 5 | — |
| 5 | `tests/test_delib_preflight_gate.py` | 15 | — |
| 5 | `tests/test_scaffold_settings.py` | 0 new | Updated expected lists; 2 regression |
| 6 | `tests/test_transcript_extract.py` | 6 | — |
| 7 | `tests/test_owner_decision_capture.py` | 8 | — |
| 8 | `tests/test_backfill_framework.py` | 6 | — |
| 9a | `tests/test_wrap_gate.py` | 8 | — |
| **Total** | | **~74 new** | baseline 1161 stays green |

All new tests ASCII-only (per `tests/_print_guard.py` convention). All new modules mypy --strict clean, ruff check + format clean.

---

## 7. Post-Impl Report Contract (discharges `-004` Condition #7)

The post-implementation report (`bridge/gtkb-da-governance-completeness-implementation-002.md` NEW) will include:

1. **Commit SHA(s)** on `groundtruth-kb` main (one per phase ideally, or a single bundled commit with per-phase subject lines).
2. **Focused test output** per phase table above — `pytest -v tests/test_*.py::specific_node_ids` with class-qualified node IDs per `feedback_postimpl_report_hygiene.md`.
3. **Full-suite output** — `pytest` ending in `PASSED` with final count (expected 1161 + ~74 = ~1235).
4. **mypy --strict output** — `Success: no issues found in N source files`.
5. **ruff check + format** — both clean.
6. **Current DA count evidence** — read-only SQLite query on Agent Red `groundtruth.db`:
   - `SELECT source_type, COUNT(*) FROM current_deliberations GROUP BY source_type;`
   - New rows this session: LO-report backfill (11), Phase-0 owner-decision DELIB (1), and whatever the dogfood run inserted.
7. **Dry-run artifacts filed in bridge/** — `lo-backfill-dryrun-{date}.json` + `transcript-dryrun-{date}.json`.
8. **Dogfood evidence** — `.groundtruth/dogfood-run-{date}.jsonl` pointer + ALARM demonstration.
9. **Rollback instructions** — per phase; all changes reversible via `git revert` + per-phase DA row cleanup script.
10. **Delta summary** — commit-local line counts + range line counts (per `feedback_postimpl_report_hygiene.md`).

---

## 8. Rollback / Containment

| Phase | Rollback |
|-------|----------|
| 1 | `gt spec retire` on all 8 spec IDs; no data loss (append-only versioning) |
| 2 | Remove `tests/test_da_db_routing_invariant.py`, `tests/test_da_residual_rescan.py`; revert `insert_deliberation()` rescan logic if Q2 behavior shipped |
| 3 | Revert warn-only validation; log-suppression only (no existing rows break) |
| 4 | `DELETE FROM deliberations WHERE source_type='lo_review' AND created_at >= {execute_timestamp}` (only for rows inserted by this phase) |
| 5 | Remove new hooks + scaffold registration; scaffold-settings reverts to pre-phase state |
| 6 | Dry-run gate prevents any live insert until owner approves; if live rows exist, same delete pattern as Phase 4 |
| 7 | Remove new hooks + scaffold registration |
| 8 | Remove `scripts/_backfill_framework.py`; Phase 4 reverts to standalone logic |
| 9a | Remove wrap-gate assertion branches; session-health.py reverts to prior behavior |

All changes reversible via `git revert` on `groundtruth-kb` main.

---

## 9. Prior Deliberations (per `.claude/rules/deliberation-protocol.md`)

Required DA search performed; directly relevant rows:

- `DELIB-0715` — MemBase canonical definition owner settlement (triggering conversation).
- `DELIB-0716` / `-0717` / `-0718` — first examples of bridge-thread compression (manual, pre-pattern).
- `DELIB-0719` — S299 owner-decision round including separate-bridge decision for harvest coverage.
- `DELIB-0720` / `DELIB-0818` — prior DA rows on this governance-completeness thread.
- `DELIB-0721` / `DELIB-0805` — harvest-coverage bridge-thread rows.
- `DELIB-0817` — S299-continuation meta-summary covering in-flight DA work.

No prior deliberation rejected any of the approaches chosen here (hard-block preflight, owner-decision capture, transcript extraction heuristics, LO-report coverage closure, backfill framework, wrap-gate, warn-only source-ref).

This implementation bridge differs from prior-rejected `-002` (scope NO-GO) by: anchoring on current harvest-coverage dependency state (not stale `-005`), including `proposal` source type with warn-only validation (not omitting it), defining a concrete same-turn state model with turn-marker + fallback window (not vague "conversation history"), narrowing redaction scope to routing invariant + residual rescan (not reimplementation), and providing a v1 acceptance contract for transcript extraction.

---

## 10. Required Next Steps After Codex GO on This Bridge

1. **Phase 0** — open AskUserQuestion round for Q1/Q2/Q3; record answers as `owner_conversation` DELIB.
2. **Phase 1** — record 8 specs in MemBase citing DELIB-0715/0719/Phase-0 DELIB.
3. **Parallel** — Phases 3, 4 (dry-run only), 7, 8 may begin.
4. **Phase 2** once Q2 is answered.
5. **Phase 5** once Q3 is answered.
6. **Phase 6** once Q1 is answered, and after the Phase-8 framework is imported.
7. **Phase 9a** once Phases 2/5/6/7 land.
8. **Phase 4 `--execute`** once Phase 8 framework + dry-run + owner approval all in place.
9. **Phase 10** dogfood run.
10. **Phase 11** post-impl report to this bridge as `-002 NEW`.

**Phase 9b is explicitly deferred** and will be filed as a separate bridge (`gtkb-da-governance-completeness-wrap-9b-001.md`) once `gtkb-da-harvest-coverage-implementation` is VERIFIED.

---

## 11. Open Questions for Codex

1. **Phase split granularity** — is this single implementation bridge (11 phases, ~74 new tests, ~8 new/modified hook/script/module files) the right unit of review, or does Codex prefer sub-bridges per phase (e.g., 5 sub-bridges grouping 1+2+3 / 4+8 / 5 / 6+7 / 9a)?
2. **Phase 7 clarification** — is the split between Phase 6 (transcript extraction at wrap) and Phase 7 (live `AskUserQuestion` + GOV-09 capture) correct? The scope `-003` lumped them together as "phase B"; this bridge separates them for execution-ordering reasons. Codex may prefer the `-003` packaging.
3. **Phase 9a (A5) audit-log mechanism** — "count of direct-SQLite writes this session = 0" requires an audit log. Simplest implementation: the DB-routing invariant test is a CI-only guard, and wrap-gate A5 trusts CI. Alternative: runtime audit log via a sqlite3 connection hook. Codex preference?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
