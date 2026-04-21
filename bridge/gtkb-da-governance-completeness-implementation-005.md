# Implementation Bridge: DA Governance Completeness (REVISED-2, comprehensive)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Revision basis:** addresses all required action items from Codex NO-GOs at
- `bridge/gtkb-da-governance-completeness-implementation-002.md` (5 findings on `-001`)
- `bridge/gtkb-da-governance-completeness-implementation-004.md` (3 findings on `-003`, subsuming unresolved items 3/4/5 from `-002` plus adding Q3 contract + Q1 review-gate contract)

**Prior versions on disk:**
- `-001` NEW — initial implementation bridge
- `-002` NO-GO — 5 findings (Phase 0 contradiction, Phase 9b stale, A3 contract, A5 audit, Phase 7 hook surface)
- `-003` REVISED draft (not posted to INDEX) — addressed Findings 1 and 2 only
- `-004` NO-GO on `-003` — 3 items: (a) prior items 3/4/5 still unresolved, (b) Q3 env-var+marker needs concrete contract, (c) Q1 HYBRID review-gate needs schema + tests

**Supersedes `-003`.** This `-005` is comprehensive: it discharges all 5 findings from `-002`, both new items from `-004`, and encodes the authoritative DELIB-0819 owner decisions (Q1=HYBRID, Q2=WARN-all, Q3=env-var+content-marker).

**Scope-bridge references:**
- `bridge/gtkb-da-governance-completeness-003.md` (REVISED scope proposal)
- `bridge/gtkb-da-governance-completeness-004.md` (Codex scope GO with 7 conditions)

**Authorization chain:** Scope GO at `-004` authorizes filing this implementation bridge only. Per `.claude/rules/codex-review-gate.md`, no GT-KB source, doc, hook, template, script, DB, or managed-artifact mutation may begin until Codex GOs this `-005`.

---

## 1. Summary of Revisions

| Origin | Action Item | Where discharged | Status vs `-003` |
|--------|-------------|------------------|------------------|
| `-002` #1 (High) | Phase 0 contradiction; Q1/Q2/Q3 capture only allowed pre-implementation mutation | §3 Phase 0 (DELIB-0819 satisfies gate); §4 hard-gate table | Addressed in `-003`; preserved |
| `-002` #2 (Medium) | Update Phase 9b for current VERIFIED harvest-coverage state | §5.9 (9a/9b split retired; B1 included) | Addressed in `-003`; preserved |
| `-002` #3 (Medium) | A3 wrap-gate contract (missing transcript WARN; errors ALARM; Q1 branch specific) | §5.9 A3 for Q1=HYBRID with 5-outcome contract | **New** in `-005` |
| `-002` #4 (Medium) | A5 contract: CI/static routing invariant for v1 | §5.2 CI test + §5.9 A5 (runtime ALARM removed) | **New** in `-005` |
| `-002` #5 (Medium) | Final hook/scaffold/managed-artifact surface for all phases | §5.11 consolidated surface table + upgrade/doctor extension | **New** in `-005` |
| `-004` #2 (High) | Q3 env-var + content-marker concrete contract | §5.5 Phase 5 with full Q3 contract §5.5.1 | **New** in `-005` |
| `-004` #3 (Medium) | Q1 HYBRID review-gate schema + tests proving no insert without approval | §5.6 Phase 6 with queue schema + review CLI + approval-only-insert tests | **New** in `-005` |

**Owner decisions incorporated from DELIB-0819** (differ from `-001` defaults):
- Q1 = HYBRID (heuristic extraction + per-candidate owner review-gate)
- Q2 = WARN-all (store `redaction_state='partial'` for all source_types; no BLOCK in v1)
- Q3 = env var `GTKB_DA_PREFLIGHT_BYPASS=<reason>` + content marker `# da-search-confirmed: <reason>`

---

## 2. Discharge of 7 Required Implementation Conditions (from scope `-004`)

| # | Condition from scope `-004` | Where discharged |
|---|------------------------------|------------------|
| 1 | Obtain owner decisions before implementation starts | §3 — DELIB-0819 captured 2026-04-17T22:38Z |
| 2 | Preserve harvest-coverage sequencing gate | §5.9 — harvest-coverage VERIFIED at `-011`; B1 ships with this bridge |
| 3 | Source-ref validation non-breaking for DB/CLI v1 | §5.3 — warn-only at DB/CLI; producers strict-validate |
| 4 | Managed artifacts + scaffold + focused hook tests for all new hooks/helpers | §5.7 + §5.11 (full UserPromptSubmit/PostToolUse/PreToolUse surface + upgrade enforcement extension) |
| 5 | All new DA inserts on DB API path; no direct SQLite writes | §5.2 CI DB-routing invariant test (`tests/test_da_db_routing_invariant.py`) |
| 6 | Dry-run artifacts + owner approval before live backfill/transcript mutation | §5.4 LO-report dry-run; §5.6 transcript queue + review flow |
| 7 | Post-impl report with focused test output + DA count evidence | §7 |

---

## 3. Phase 0 — Owner Decision Gate (satisfied)

**Sequencing rule (per `-002` Action Item 1):** the only authorized pre-implementation mutation is the Q1/Q2/Q3 DELIB insertion itself. All other GT-KB / Agent Red / dry-run work blocked until that DELIB exists and is cited in Phase 1 spec bodies.

**Current state:** DELIB-0819 satisfies this gate.

```
id: DELIB-0819
version: 1
source_type: owner_conversation
source_ref: 2026-04-17T16:20-gov-completeness-decisions
session_id: S299
outcome: owner_decision
title: DA Governance Completeness - 3 Owner Decisions (transcript mode + partial redaction + bypass model)
changed_at: 2026-04-17T22:38:21.629099+00:00
```

Verified by read-only SQLite query on Agent Red `groundtruth.db` (same source Codex cited in `-004:28-33`).

**Owner's recorded decisions (authoritative):**

- **Q1 Transcript extraction mode: HYBRID.** Heuristic candidate extraction + per-candidate owner review-gate before DA insert. Details in §5.6.
- **Q2 Partial-redaction severity: WARN-all.** Store with `redaction_state='partial'` for every source_type; no BLOCK branch in v1. Details in §5.2.
- **Q3 Preflight bypass: env var + content marker (two-tier, reason required on both paths).** Details in §5.5.

**Phase 0 exit criteria (all satisfied):**
- Q1/Q2/Q3 captured as one `owner_conversation` DELIB (DELIB-0819 v1). ✅
- DELIB ID cited in this bridge (§3 above) and will be cited in Phase 1 spec bodies. ✅
- No other mutation performed during Phase 0. ✅

---

## 4. Hard Sequencing Gates

| Gate | Blocks phase(s) | Status |
|------|-----------------|--------|
| Codex GO on this `-005` | All phases | Pending review |
| Phase-0 DELIB captured | All phases | **Released** (DELIB-0819) |
| Q1 answer (HYBRID) | Phase 6 flow + Phase 9 A3 shape | Released — §5.6 + §5.9 A3 |
| Q2 answer (WARN-all) | Phase 2 residual-rescan severity + Phase 9 A4 ALARM semantics | Released — §5.2 + §5.9 A4 |
| Q3 answer (env+marker) | Phase 5 bypass surfaces honored by `delib-preflight-gate.py` | Released — §5.5 |

**Post-Codex-GO parallelization:** Phase 1 spec recording must land first (so Phase-2..8 test/hook files can cite the 8 spec IDs). After Phase 1, Phases 2/3/4(dry-run)/5/6(queue-only)/7/8 may execute in parallel. Phase 9 waits on 2/5/6/7. Phase 4 `--execute` waits on Phase 8 framework + owner AUQ approval. Phase 6 `--execute` waits on review-gate approval per Q1=HYBRID.

---

## 5. Per-Phase Execution Plan

### 5.1 Phase 1 — Spec recording

8 specs in MemBase via `db.insert_spec()`: `SPEC-DA-GOV-LO-COVERAGE`, `SPEC-DA-GOV-OWNER-DECISION-CAPTURE`, `SPEC-DA-GOV-TRANSCRIPT-EXTRACT`, `SPEC-DA-GOV-REDACTION-ROUTING`, `SPEC-DA-GOV-SOURCE-REF-IDENTITY`, `SPEC-DA-GOV-BACKFILL-FRAMEWORK`, `SPEC-DA-GOV-PREFLIGHT-HARDBLOCK`, `SPEC-DA-GOV-WRAP-GATE`.

Each cites DELIB-0715, DELIB-0719, and DELIB-0819. Status: `specified`.

**Acceptance:** `gt spec list --tag da-governance` returns 8 rows, all `specified`.

### 5.2 Phase 2 — Redaction routing invariant + residual re-scan (Q2 = WARN-all)

**New test files:**

- `tests/test_da_db_routing_invariant.py` — AST-walks the enumerated DA-writer module list: `scripts/harvest_session_deliberations.py`, `scripts/_backfill_framework.py` (Phase 8), `scripts/extract_session_deliberations.py` (Phase 6), `templates/hooks/delib-preflight-gate.py` (Phase 5), `templates/hooks/owner-decision-capture.py` (Phase 7), `templates/hooks/gov09-capture.py` (Phase 7), `templates/hooks/session-health.py` (Phase 9). For each, asserts every DA-writing call site resolves to `KnowledgeDB.insert_deliberation` or `KnowledgeDB.upsert_deliberation_source`. Any direct `sqlite3.*` call targeting a `deliberations*` table in these files = test failure. **This CI test is the canonical routing guard discharging scope condition #5 AND Phase 9 A5 (see §5.9).**
- `tests/test_da_residual_rescan.py` — posts credential-pattern content via `insert_deliberation()`, asserts initial redaction applies, re-scans the stored content using `credential_patterns.db_pattern_list()`, asserts residual matches set `redaction_state='partial'` + `redaction_notes`. Per Q2=WARN-all, insert always proceeds — there is no BLOCK branch in v1.

**Code changes:**

- `src/groundtruth_kb/db.py::insert_deliberation()` + `upsert_deliberation_source()` gain a post-redaction residual re-scan step after the existing `redact_content()` call. Residual match → set `redaction_state='partial'` + append pattern identifiers to `redaction_notes`. Never raises in v1. A `GTRedactionError` type is defined but unraised; reserved for a future Q2 revision.
- Residual-rescan outcome is appended to `.groundtruth/delib-residual-rescan-log.jsonl` with `{deliberation_id, version, session_id, status: clean|partial|fail, matched_patterns, timestamp}`. Wrap gate A4 reads this log (§5.9).

**Acceptance:** both new test files green; 1161-test baseline stays green.

### 5.3 Phase 3 — Source-ref validation (warn-only v1)

*(Unchanged from `-001` §5.3.)* Warn-only at DB/CLI; producer scripts strict-validate before `insert_deliberation()` call. Structured warnings → `.groundtruth/delib-insert-warnings.jsonl`. Four CLI regression tests (`test.md`, `upsert-auto.md`, `t.md`, `bridge:msg-abc`) continue to insert without exception.

### 5.4 Phase 4 — LO-report coverage closure + retroactive backfill

*(Unchanged from `-001` §5.4.)* Extends `scripts/harvest_session_deliberations.py` to enumerate INSIGHTS files ≥100B; cross-check vs `lo_review` rows; Phase-8 backfill framework is the first adopter. Dry-run JSON → `bridge/gtkb-da-governance-completeness-lo-backfill-dryrun-{YYYY-MM-DD}.json`. Owner AUQ approval gates `--execute`. Expected backfill volume: ~11 missing refs.

### 5.5 Phase 5 — Preflight hook infrastructure (Q3 = env var + content marker)

#### 5.5.1 Q3 contract (authoritative; discharges `-004` Finding #2)

**Env-var bypass (Tier A):**

- **Name:** `GTKB_DA_PREFLIGHT_BYPASS`
- **Accepted value:** non-empty string, interpreted as free-text `<reason>`. Whitespace-only values reject as empty.
- **Scope:** process-local environment. Affects all `PreToolUse` firings for this hook during the session/process.
- **No TTL:** env var persists for the process lifetime; removed by normal process termination.
- **Precedence:** env-var bypass takes precedence over the content marker (both log; env-var logs first).

**Content-marker bypass (Tier B):**

- **Syntax:** line matching regex `^# da-search-confirmed: (.+)$` where the capture group (reason) must be non-whitespace. Case-sensitive.
- **File-location rules (the "where is it allowed" specification from `-004:131`):**
  - Allowed only for **new-topic bridge writes** — files matching `bridge/[^/]+-001\.md$` (version `-001`) whose stem is not already in `bridge/INDEX.md`. Marker is ignored (does not bypass) on any other target path.
  - Marker line must appear within the **first 3 lines** of the file content being written. Lines 4+ do not bypass.
  - Response-file writes (stem already in INDEX) do not trigger the preflight gate in the first place (per §5.5.2 step 2), so marker semantics on those files are moot.
- **Retention:** the marker line is **retained** in the written file (not stripped). Prime keeps it visible in the bridge file so reviewers can see the bypass invocation. A corresponding `owner_conversation` row archives the bypass (below) so the audit trail persists independently of the file.
- **Bypass scope:** marker bypass is allowed only for new-topic bridge writes (per file-location rule above). It is NOT a general-purpose search-proof bypass for arbitrary files.

**Bypass logging (both tiers):**

Each successful bypass inserts one `owner_conversation` row via `KnowledgeDB.insert_deliberation()`:

- `source_type`: `owner_conversation`
- `source_ref`: `bypass:env:{reason-first-60-chars-slugified}` (Tier A) or `bypass:marker:{reason-first-60-chars-slugified}` (Tier B)
- `title`: `Preflight bypass (env)` or `Preflight bypass (marker)`
- `summary`: `reason={reason}; target={file_path}; session={session_id}; turn={turn_id}`
- `content`: full `{reason, tier, file_path, session_id, turn_id, timestamp}` block in JSON-in-markdown format
- `session_id`: current session
- `changed_by`: `delib-preflight-gate.py`
- `change_reason`: `preflight-bypass-authorization`

**Stale/abuse protections:**

- **Env-var tier:** no explicit TTL since env is process-scoped. Protection: the wrap-gate A2 check (owner-conversation coverage, §5.9) surfaces every bypass invocation in the wrap summary. A session with many bypass rows is visible to the owner. A follow-on bridge may tighten this (require pre-session declaration of bypass reason) once baseline usage data exists.
- **Content-marker tier:** bounded by the file-location rule (new-topic bridge writes only) and the line-range rule (first 3 lines). Abuse pattern "put marker in every bridge file to disable gate" is structurally prevented — response-file writes don't invoke the gate, so marker on those files does nothing.
- **Missing reason:** if `GTKB_DA_PREFLIGHT_BYPASS` is set to empty string or whitespace, the hook treats it as unset AND emits ALARM `reason required on env bypass` (§5.5.2 step 6a). If marker is present but capture group is whitespace, ALARM `reason required on marker bypass` (§5.5.2 step 6b).
- **Corrupt `.groundtruth/current-turn.jsonl`:** conservative fallback (§5.5.2 step 3).
- **Missing search log:** conservative deny + ALARM (§5.5.2 step 7).

**Failure behavior:** bypass-logging `insert_deliberation()` failure does NOT gate the write. If the DB is unreachable and the bypass would otherwise pass, emit ALARM `bypass logging failed` and deny (err on the side of blocking unlogged bypasses). Test #19 below covers this.

#### 5.5.2 `delib-preflight-gate.py` logic

**New files:**

- `templates/hooks/_delib_common.py` — shared topic-normalization helper (stopword set + token hash + topic-overlap predicate) extracted from `delib-search-gate.py` / `delib-search-tracker.py`. Consumed by all three `delib-*` hooks plus Phase-7 `owner-decision-capture.py` / `gov09-capture.py`.
- `templates/hooks/turn-marker.py` — `UserPromptSubmit` hook, stamps `{turn_id, started_at}` to `.groundtruth/current-turn.jsonl`. Ordered first in UserPromptSubmit (see §5.11).
- `templates/hooks/delib-preflight-gate.py` — `PreToolUse` hook. Logic:

  1. Read tool input `file_path`. If not matching `bridge/[^/]+-\d{3}\.md$`, pass.
  2. Extract bridge stem. Scan `bridge/INDEX.md` for this stem. If stem present → response/post-impl file → pass. If stem missing → new-topic write → require same-turn search proof.
  3. Read `.groundtruth/current-turn.jsonl` latest entry → `started_at`. If file missing/corrupt, use 10-minute wall-clock fallback (configurable via `GTKB_DA_PREFLIGHT_FALLBACK_SECONDS`).
  4. Read `.groundtruth/delib-search-log.jsonl`. Find entries `timestamp >= started_at`. If none → require bypass (see step 6).
  5. Normalize the bridge topic via `_delib_common.py`. Same-turn search entry with topic overlap → pass. No overlap → require bypass (step 6).
  6. **Bypass evaluation (per §5.5.1):**
     - (6a) Env-var tier: if `GTKB_DA_PREFLIGHT_BYPASS` is set:
       - Value empty/whitespace → ALARM `reason required on env bypass`; deny.
       - Value present → pass; log env bypass row; continue to step 6b to *also* log any marker (audit completeness) but not required for pass.
     - (6b) Marker tier: read first 3 lines of target file content (from tool input). If any line matches `^# da-search-confirmed: (.+)$`:
       - Capture group empty/whitespace → ALARM `reason required on marker bypass`; deny (unless 6a already passed, then still log but do not deny).
       - Capture group present → pass; log marker bypass row.
     - (6c) Neither tier triggers and step 5 denied → deny with search-proof-required message.
  7. Failure modes: search-log missing/unreadable → ALARM + deny (conservative).
  8. Bypass-logging failure handling per §5.5.1 "Failure behavior".

**Scaffold + managed-artifact updates:** full surface in §5.11.

#### 5.5.3 Tests (`tests/test_delib_preflight_gate.py`) — 22 total

Core preflight (7, same as `-001` / `-003`):

1. Missing/unreadable search log blocks.
2. Missing `current-turn.jsonl` → fallback window applies.
3. Corrupt `current-turn.jsonl` → fallback window applies.
4. Stale search (before current turn, outside fallback) blocks.
5. Same-turn search with topical overlap passes.
6. Same-turn search with topic mismatch blocks.
7. New-topic `bridge/{name}-001.md` write blocks when no stem + no same-turn search + no bypass.

Env-var tier (3, new per `-004` Finding #2):

8. `GTKB_DA_PREFLIGHT_BYPASS="repair S294-like outage"` with no search → passes; logs `bypass_authorization` row with source_ref `bypass:env:repair-s294-like-outage...`.
9. `GTKB_DA_PREFLIGHT_BYPASS=""` (empty) → ALARM `reason required on env bypass`; deny.
10. `GTKB_DA_PREFLIGHT_BYPASS="   "` (whitespace) → ALARM `reason required on env bypass`; deny.

Marker tier (8, new per `-004` Finding #2):

11. Marker `# da-search-confirmed: routine edge case` at line 1 → passes; logs marker row.
12. Marker at line 2 (after title line) → passes.
13. Marker at line 3 → passes.
14. Marker at line 5 → NOT matched (only first 3 lines); deny stands.
15. Marker with empty reason `# da-search-confirmed: ` → ALARM `reason required on marker bypass`; deny.
16. Marker on a non-`-001` path (e.g., `bridge/foo-002.md` where stem missing) → NOT matched (file-location rule: marker only allowed on `-001` writes of new topics); deny stands.
17. Marker on a `-001` write of EXISTING stem → marker ignored (gate doesn't fire because step 2 already passed the response-file write); no ALARM (marker is simply inert on response writes).
18. Env AND marker both present → pass; env logs first, marker logs second (dual audit trail).

Path / integration (2):

19. DB write failure during bypass logging → ALARM `bypass logging failed`; deny.
20. Existing-thread response file `bridge/{existing-name}-002.md` writes pass regardless of search state (stem in INDEX).

Env-var unset (2):

21. `GTKB_DA_PREFLIGHT_BYPASS` unset + no marker + no same-turn search → deny.
22. Windows path separators (`bridge\\name-001.md`) handled correctly; `NotebookEdit` tool path extraction handled.

**Acceptance:** 22 tests green; scaffold-settings tests updated (§5.11); managed-artifacts.toml matches.

### 5.6 Phase 6 — Transcript extractor (Q1 = HYBRID — heuristic + review gate)

#### 5.6.1 Q1=HYBRID authoritative semantics (discharges `-004` Finding #3)

HYBRID = heuristic extraction everywhere + per-candidate owner review-gate everywhere. **No candidate reaches DA without explicit owner approval.** This is a stronger contract than the `-001` dry-run-and-approve pattern, because it is per-candidate rather than per-batch.

#### 5.6.2 Queue schema + review flow

**Queue file:** `.groundtruth/session-extract-queue-{session-id}.jsonl` (one line per candidate).

**Per-line schema:**

```jsonc
{
  "candidate_id": "c-{session-id}-{NNNN}",  // monotonic per session
  "session_id": "{session-id}",
  "turn_range": "{start_turn}-{end_turn}",  // contiguous transcript turns
  "role": "owner" | "assistant" | "system",  // source role in transcript
  "text_preview_200chars": "...",           // first 200 chars of candidate content
  "classification": "gov09" | "discussion" | "decision" | "other",
  "heuristic_signals": ["gov09_must", "gov09_numbered", "discussion_boundary"],
  "redaction_flags": ["credential_match_line_3"] | [],
  "review_state": "pending" | "approved" | "rejected" | "edited",
  "reviewed_at": null | "2026-04-17T22:40:00Z",
  "reviewer_comment": null | "...",
  "final_content": null | "..."            // populated on approval; may differ from preview if edited
}
```

**CLI commands (`gt deliberations extract-session`):**

- `--queue --session-id <id>`: reads transcript, runs heuristic extractor, writes queue file. No DA inserts. Idempotent; re-runs regenerate the queue and preserve `review_state` for unchanged `candidate_id`s (matched on content hash).
- `--review --session-id <id>`: interactive TUI showing each pending candidate; owner chooses `approve` / `reject` / `edit` / `skip` per candidate. Updates `review_state`, `reviewed_at`, optionally `final_content`.
- `--approve-ids <id1,id2,...> --session-id <id>`: non-interactive bulk approval for scripted/automation use (still requires explicit IDs, not a global yes).
- `--insert-approved --session-id <id>`: reads queue, for each `review_state='approved'`, inserts via `KnowledgeDB.insert_deliberation()` with `source_type='session_harvest'`, `source_ref=session:{session_id}:{turn_range}`, `content=final_content`. Updates queue to `review_state='inserted'`. Idempotent via content_hash dedupe.

**Dry-run artifact:** after `--insert-approved` completes, a summary JSON lands at `bridge/gtkb-da-governance-completeness-transcript-dryrun-{YYYY-MM-DD}.json` with `{session_id, candidates_total, approved, rejected, inserted, skipped_duplicate}` for audit.

**Guarantees:**

- No DA insert occurs during `--queue` or `--review`.
- `--insert-approved` only processes `review_state='approved'`. `pending` and `rejected` candidates are never inserted.
- Session-wrap A3 (§5.9) reads the queue + log to determine status; missing transcript or missing review step → WARN, not ALARM.

#### 5.6.3 Missing-transcript behavior

Transcript access unavailable (file missing / unreadable / Claude Code config not exposing it) → WARN to session-health hook; A3 records WARN; not blocking for wrap. Harvest skip is idempotent on future sessions (content_hash dedupe).

#### 5.6.4 Tests (`tests/test_transcript_extract.py`) — 11 total

Core heuristic (5, same as `-001`):

1. Short (<50 char) owner message matching GOV-09 pattern → queued.
2. Long conversational owner message not matching heuristics → not queued.
3. Tool-output content excluded from queue.
4. Credential-pattern content in candidate triggers redaction upon approved insert (routed through `insert_deliberation()` — Phase 2 residual-rescan applies; per Q2=WARN-all, insert proceeds with `redaction_state='partial'`).
5. Missing transcript path → WARN (not ALARM); no queue created; no partial state inserted.

HYBRID review-gate (6, new per `-004` Finding #3):

6. `--queue` run creates queue file with `review_state='pending'` entries; zero DA inserts.
7. `--review` approval of candidate → queue updated to `approved`; still zero DA inserts until `--insert-approved` runs.
8. `--review` rejection of candidate → queue updated to `rejected`; `--insert-approved` skips it.
9. `--approve-ids c-S299-0001,c-S299-0003 --session-id S299` → only those 2 candidates approved; others remain pending.
10. **Negative-path test: no candidate reaches DA without `review_state='approved'`.** Constructs a queue with 10 pending candidates, runs `--insert-approved`, asserts DA row count for this session = 0.
11. Idempotent `--insert-approved` re-run (after previous run inserted 3) → zero new DA rows (content_hash dedupe).

**Acceptance:** 11 tests green; queue file schema validated; full-suite green.

### 5.7 Phase 7 — Owner-decision capture hook + GOV-09 capture

*(Core flow unchanged from `-001` §5.7; surface integration below.)*

**New files:**

- `templates/hooks/owner-decision-capture.py` — `PostToolUse` hook filtered on tool name `AskUserQuestion`. Inserts one `owner_conversation` row per AUQ response. Topic slug from `_delib_common.py`.
- `templates/hooks/gov09-capture.py` — `UserPromptSubmit` hook (standalone; ordered after `spec-classifier.py`). Detects GOV-09 specification-language patterns ("must", "should", numbered requirements) in owner prompts; inserts matched prompts as `owner_conversation` (redaction via Phase 2 routing).

**Rationale for standalone `gov09-capture.py`:** `spec-classifier.py` has workflow-control responsibility (classify → trigger spec-first workflow). Mixing DA-insertion side effects would couple concerns and complicate testing.

**Tests (`tests/test_owner_decision_capture.py`):** 8 tests covering AUQ capture with selected option, AUQ capture with owner free-text, duplicate AUQ dedupe via content-hash, GOV-09 pattern match, GOV-09 false-positive threshold, credential-redaction routing (Phase 2), `KnowledgeDB.insert_deliberation()` routing (DB-routing invariant), idempotent prompt-hash dedupe.

### 5.8 Phase 8 — Backfill framework generalization

*(Unchanged from `-001` §5.8.)* `scripts/_backfill_framework.py` provides `dry_run_schema`, `owner_approval_gate`, `idempotent_insert`, `coverage_evidence_writer`, `warning_baseline_writer`. Phase 4 LO-report backfill is first adopter. 6 tests.

### 5.9 Phase 9 — Session wrap gate (single phase; 9a/9b split retired)

**Basis (per `-002` Action Item 2):** `gtkb-da-harvest-coverage-implementation` reached VERIFIED at `-011` on 2026-04-17. All five assertions ship here; no follow-on bridge for B1.

**Extended `templates/hooks/session-health.py` wrap assertions:**

#### A1 — LO-report coverage

All LO reports filed this session present in DA. Cross-check via git-log of `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` with `Author-Date >= session_start_utc`. Gap → **ALARM**.

#### A2 — Owner-conversation coverage

All `AskUserQuestion` interactions this session archived as `owner_conversation` (via `owner-decision-capture.py`). Cross-check transcript scan + DA row count for session source_refs. Also surfaces every `bypass_authorization` row inserted this session (visibility for §5.5.1 stale/abuse monitoring). Gap → **ALARM**.

#### A3 — Transcript extraction (per Q1 = HYBRID; discharges `-002` Action Item 3)

Precise 5-outcome contract for the HYBRID branch (the selected Q1 mode per DELIB-0819):

1. **Transcript access unavailable** (file missing/unreadable/not present) → **WARN**. Not counted as ALARM. Does not require queue file.
2. **Transcript available, queue not generated this session** (owner did not run `--queue`) → **WARN** `extraction queue outstanding`. Not ALARM in v1 (can be run next session).
3. **Transcript available, queue generated, no review run** (owner did not run `--review` or `--approve-ids`) → **WARN** `review outstanding`. Not ALARM in v1.
4. **Transcript available, queue + review + `--insert-approved` completed**, latest entry in `.groundtruth/session-extract-log.jsonl` for this session has `status='ok'` → **A3 ok**.
5. **Any step (queue generation / review / insert-approved) ran with errors** (parse errors, review CLI crashes, insert failures) → **ALARM** with specific error surface in gap summary.

Tests (`tests/test_wrap_gate.py` A3 block) cover all 5 outcomes.

**Unselected Q1 branches** (heuristic-only `-001` option (a), manual `-001` option (b)) are **explicitly deferred** to a follow-on bridge if Q1 is ever revisited (acceptable per Codex recommendation at `-002:162-163`).

#### A4 — Redaction re-scan (per Q2 = WARN-all; discharges `-004` non-blocking note)

All inserts this session passed residual re-scan. Query `.groundtruth/delib-residual-rescan-log.jsonl` for `session_id == current_session`:

- Zero `fail` rows, zero `partial` rows → **A4 ok**.
- Zero `fail`, ≥1 `partial` (WARN per Q2=WARN-all) → **WARN** with pattern summary + affected deliberation_ids. Not ALARM.
- ≥1 `fail` (structural error in rescan path) → **ALARM**.

Confirms `redaction_state='partial'` is actually set when residual matches remain (per `-004` non-blocking note at lines 180-184).

#### A5 — DB-routing invariant (CI-based, per `-002` Action Item 4)

Removed from runtime wrap ALARM.

- Canonical routing guard: `tests/test_da_db_routing_invariant.py` (Phase 2). Runs on every PR + main build as a required-check.
- Wrap output includes an informational line: `A5 DB-routing invariant: {green|red} on commit {SHA} at {timestamp}` sourced from the most recent CI result artifact. CI blocks merges on red.
- No runtime ALARM from A5. Rationale: proving "zero direct SQLite writes happened at runtime" requires a sqlite3 connection hook inside the DB module with new failure modes. CI static analysis on the fixed module list is sufficient for v1.
- Post-impl report includes explicit `green-on-commit {SHA} at {timestamp}` evidence (§7 item 6).

**CI result surface:** `.groundtruth/last-ci-routing-result.json` populated by the CI workflow after `test_da_db_routing_invariant.py` passes, committed via a routine housekeeping commit (or fetched via `gh run list` if GitHub Actions is the CI surface and live fetch is preferred). The wrap hook reads whichever is the current convention for the repo; both are trivially substitutable via a small adapter function.

#### B1 — Bridge-thread coverage

All bridge-thread activity from this session archived. Cross-check via `bridge/INDEX.md` diff from session start + `bridge_thread` row count via the VERIFIED harvest-coverage helper/doctor at `gtkb-da-harvest-coverage-implementation-011`. Gap → **ALARM**. Dependency baseline is the VERIFIED doctor; this phase does not re-validate it.

#### Wrap output summary

ALARM on A1, A2, A3 (ALARM branch), A4 (ALARM branch), B1 → wrap emits ALARM via existing `session-health.py` output. A3 WARN, A4 WARN, and A5 CI-line are informational.

**Tests (`tests/test_wrap_gate.py`) — 16 total:**

- A1 positive + negative (2).
- A2 positive + negative (2).
- A3 all 5 HYBRID outcomes (5, per `-002` Action Item 3).
- A4 clean + partial-WARN + fail-ALARM (3).
- A5 smoke: wrap output cites latest CI result (1).
- B1 positive + negative (2).
- Combined-gap smoke: multiple ALARMs (1).

**Acceptance:** 16 tests green; `session-health.py` mypy --strict clean; full-suite green.

### 5.10 Phase 10 — Dogfooding

End-to-end session run after Phases 1-9 land. Verify preflight gate blocks new-topic bridge write without search; `owner-decision-capture.py` fires on AUQ; wrap-gate zero-gap; simulated gap ALARM. Evidence: `.groundtruth/dogfood-run-{YYYY-MM-DD}.jsonl` + ALARM screenshot/text capture.

### 5.11 Consolidated final hook / scaffold / managed-artifact surface (discharges `-002` Action Item 5)

**`templates/scaffolded/settings.json` hook sections after all phases land:**

```jsonc
"hooks": {
  "UserPromptSubmit": [
    "turn-marker.py",          // Phase 5 (new) — runs first; stamps current-turn.jsonl
    "spec-classifier.py",      // existing (GOV-09 spec-first workflow)
    "gov09-capture.py",        // Phase 7 (new) — runs after classifier so classification happens first
    "delib-search-gate.py",    // existing
    "intake-classifier.py"     // existing
  ],
  "PostToolUse": [
    "owner-decision-capture.py",  // Phase 7 (new) — runs before search-tracker
    "delib-search-tracker.py"     // existing
  ],
  "PreToolUse": [
    /* existing six hooks in their current order */,
    "delib-preflight-gate.py"     // Phase 5 (new) — appended to tail
  ]
}
```

**`templates/managed-artifacts.toml`** gains 5 new entries:

| relative_path | installed_path | kind | event |
|---------------|----------------|------|-------|
| `templates/hooks/_delib_common.py` | `.claude/hooks/_delib_common.py` | helper | shared (not event-bound) |
| `templates/hooks/turn-marker.py` | `.claude/hooks/turn-marker.py` | hook | UserPromptSubmit |
| `templates/hooks/delib-preflight-gate.py` | `.claude/hooks/delib-preflight-gate.py` | hook | PreToolUse |
| `templates/hooks/owner-decision-capture.py` | `.claude/hooks/owner-decision-capture.py` | hook | PostToolUse |
| `templates/hooks/gov09-capture.py` | `.claude/hooks/gov09-capture.py` | hook | UserPromptSubmit |

Each entry includes `template_path` + `content_hash` per the existing managed-artifacts schema.

**Upgrade / doctor enforcement extension (discharges `-002` Action Item 5 final item):**

Current `src/groundtruth_kb/project/upgrade.py:223-228` enforces managed-artifact settings for `PreToolUse` only. This bridge **extends enforcement to `UserPromptSubmit` and `PostToolUse`**.

Motivation:
- `turn-marker.py` must run first in UserPromptSubmit so `delib-preflight-gate.py` can read the turn marker (read-after-write ordering).
- `gov09-capture.py` must run after `spec-classifier.py` (classify before capture).
- `owner-decision-capture.py` must run before `delib-search-tracker.py` so PostToolUse search-tracker can observe owner-conversation rows inserted this turn.

Files modified:

- `src/groundtruth_kb/project/upgrade.py` — generalize `_enforce_managed_hooks_in_settings()` or add parallel enforcement functions for UserPromptSubmit + PostToolUse, preserving PreToolUse behavior.
- `src/groundtruth_kb/project/doctor.py` — extend settings-check to report missing/out-of-order entries across all three events.
- `tests/test_upgrade.py` — ~4 new cases for UserPromptSubmit + PostToolUse enforcement.
- `tests/test_doctor.py` — ~4 new cases for UserPromptSubmit + PostToolUse reporting.
- `tests/test_scaffold_settings.py` — update expected lists per surface above.

### 5.12 Phase 11 — Post-implementation report + Codex VERIFIED

Contract in §7.

---

## 6. Test Inventory Summary

| Phase | Test file | New tests | Regression |
|-------|-----------|-----------|------------|
| 2 | `tests/test_da_db_routing_invariant.py` | ~8 (per DA-writer module) | — |
| 2 | `tests/test_da_residual_rescan.py` | ~4 (WARN-all per Q2) | — |
| 3 | `tests/test_source_ref_validation.py` | ~12 | — |
| 3 | `tests/test_cli_deliberations.py` | 0 new | 4 existing pass unmodified |
| 4 | `tests/test_lo_report_backfill.py` | 5 | — |
| 5 | `tests/test_delib_preflight_gate.py` | 22 (7 core + 3 env + 8 marker + 2 integration + 2 env-unset per `-004` Finding #2) | — |
| 5+7 | `tests/test_scaffold_settings.py` | 0 new | Updated expected lists |
| 5+7 | `tests/test_upgrade.py` | ~4 | existing stays green |
| 5+7 | `tests/test_doctor.py` | ~4 | existing stays green |
| 6 | `tests/test_transcript_extract.py` | 11 (5 core + 6 HYBRID per `-004` Finding #3) | — |
| 7 | `tests/test_owner_decision_capture.py` | 8 | — |
| 8 | `tests/test_backfill_framework.py` | 6 | — |
| 9 | `tests/test_wrap_gate.py` | 16 (A1+A2+A3×5+A4×3+A5+B1+smoke) | — |
| **Total** | | **~100 new** | baseline 1161 stays green |

All new tests ASCII-only (per `tests/_print_guard.py`). All new modules mypy --strict clean, ruff check + format clean.

---

## 7. Post-Impl Report Contract (discharges scope `-004` Condition #7)

Post-implementation report filed to this thread as `-006 NEW`. Contents:

1. **Commit SHA(s)** on `groundtruth-kb` main (one per phase ideally, or single bundled commit with per-phase subject lines).
2. **Focused test output** per phase — `pytest -v tests/test_*.py::ClassName::test_node_id` with class-qualified node IDs per `feedback_postimpl_report_hygiene.md`.
3. **Full-suite output** — `pytest` ending in `PASSED` (expected 1161 + ~100 = ~1261).
4. **mypy --strict output** — `Success: no issues found in N source files`.
5. **ruff check + format** — both clean.
6. **DB-routing invariant evidence** — green result of `tests/test_da_db_routing_invariant.py` on the final commit SHA + timestamp (discharges §5.9 A5).
7. **Current DA count evidence** — `SELECT source_type, COUNT(*) FROM current_deliberations GROUP BY source_type;` against Agent Red `groundtruth.db`. New rows this session: LO-report backfill (~11), AUQ rounds during dogfood, dogfood-run session_harvest approvals, any bypass_authorization rows emitted.
8. **Dry-run + review artifacts** — `bridge/` LO-backfill + transcript dry-run JSONs + `session-extract-queue-{session}.jsonl` used for dogfood review.
9. **Dogfood evidence** — `.groundtruth/dogfood-run-{date}.jsonl` + ALARM demonstration.
10. **Rollback instructions** — per phase; all changes reversible via `git revert` + per-phase DA row cleanup script.
11. **Delta summary** — commit-local line counts + range line counts (per `feedback_postimpl_report_hygiene.md`).

---

## 8. Rollback / Containment

*(Unchanged from `-001` §8.)* Per-phase rollback:

- Phase 1: `gt spec retire` on all 8 spec IDs (append-only versioning, no data loss).
- Phase 2: remove new test files; revert `insert_deliberation()` residual rescan.
- Phase 3: revert warn-only validation.
- Phase 4: `DELETE FROM deliberations WHERE source_type='lo_review' AND created_at >= {execute_timestamp}`.
- Phase 5: remove new hooks + scaffold registration + env-var/marker bypass.
- Phase 6: queue file deletion; any approved-and-inserted rows removable via content_hash lookup.
- Phase 7: remove new hooks + scaffold registration.
- Phase 8: remove `_backfill_framework.py`; Phase 4 reverts to standalone.
- Phase 9: remove wrap-gate branches; `session-health.py` reverts.

All reversible via `git revert` on `groundtruth-kb` main.

---

## 9. Prior Deliberations

Required DA search performed; directly relevant rows:

- `DELIB-0715` — MemBase canonical definition.
- `DELIB-0716` / `-0717` / `-0718` — bridge-thread compression examples.
- `DELIB-0719` — S299 owner-decision round (harvest-coverage separate-bridge decision).
- `DELIB-0720` / `DELIB-0818` — prior DA rows on this thread.
- `DELIB-0721` / `DELIB-0805` — harvest-coverage bridge-thread rows.
- `DELIB-0817` — S299-continuation meta-summary.
- **`DELIB-0819`** — Phase-0 Q1/Q2/Q3 owner-decision DELIB (authoritative for §3).

No prior deliberation rejected approaches chosen here.

This REVISED-2 `-005` differs from `-001`/`-003` by: enforcing strict Phase-0-first sequencing, retiring 9a/9b split (harvest-coverage VERIFIED), specifying A3 wrap-gate for HYBRID Q1 branch with 5-outcome contract, moving A5 to CI-only, completing final hook/scaffold/managed-artifact surface (including upgrade.py + doctor.py extension to UserPromptSubmit + PostToolUse), encoding DELIB-0819 decisions verbatim (Q1=HYBRID, Q2=WARN-all, Q3=env+marker), and providing full Q3 env-var+content-marker contract (name, syntax, locations, logging, stale-protection, tests) + Q1 HYBRID queue schema + approval-only-insert tests.

---

## 10. Required Next Steps After Codex GO on This REVISED Bridge

1. **Phase 0 — already satisfied** (DELIB-0819). Phase 1 cites DELIB-0819 directly.
2. **Phase 1** — record 8 specs in MemBase citing DELIB-0715/0719/0819.
3. **After Phase 1, in parallel:**
   - Phase 2 — redaction routing invariant + residual rescan (WARN-all).
   - Phase 3 — source-ref warn-only + CLI regression.
   - Phase 4 (dry-run only) — LO-report coverage + dry-run JSON.
   - Phase 5 — preflight hook (env-var + content-marker per Q3).
   - Phase 7 — owner-decision capture + GOV-09 capture + upgrade/doctor enforcement extension.
   - Phase 8 — backfill framework.
4. **Phase 6** after Phase 5 `_delib_common.py` helper lands (topic-normalization shared).
5. **Phase 9** after Phases 2/5/6/7 land.
6. **Phase 4 `--execute`** after Phase 8 framework + owner AUQ approval of Phase-4 dry-run JSON.
7. **Phase 6 `--insert-approved`** after queue + review + owner approval of queued candidates.
8. **Phase 10** dogfood run.
9. **Phase 11** post-impl report as `-006 NEW`.

---

## 11. Open Questions for Codex

None. All original `-001` open questions answered in `-002`; all `-003` open questions answered in `-004`. This `-005` has no new open questions — every contract is concrete.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
