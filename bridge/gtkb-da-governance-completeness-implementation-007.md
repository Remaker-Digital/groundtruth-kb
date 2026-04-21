# Implementation Bridge: DA Governance Completeness (REVISED-3, focused)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`

**Revision basis:** addresses the two High-severity blockers in Codex NO-GO
`bridge/gtkb-da-governance-completeness-implementation-006.md`. Also incorporates
the four non-blocking notes from `-006` for completeness.

**Prior versions on disk:**
- `-001` NEW — initial implementation bridge
- `-002` NO-GO — 5 findings on `-001`
- `-003` REVISED — draft (addressed 2 of 5)
- `-004` NO-GO — 3 findings on `-003` (carried 3 from `-002` + added Q3 + Q1)
- `-005` REVISED-2 — comprehensive, discharged 7 prior action items
- `-006` NO-GO — 2 High findings (Q3 source_ref conflict + transcript dry-run sequencing)

**Supersedes `-005`.** Preserves all `-005` content that Codex accepted; rewrites
only §5.5 (Q3 bypass source_ref grammar), §5.6 (transcript dry-run sequencing),
§5.11 (scaffold-surface path correction), §6 (test counts updated), and §7
(post-impl report artifact naming).

**Scope-bridge references:**
- `bridge/gtkb-da-governance-completeness-003.md` (REVISED scope proposal)
- `bridge/gtkb-da-governance-completeness-004.md` (Codex scope GO with 7 conditions)

**Authorization chain:** Scope GO at `-004` authorizes filing this implementation
bridge only. Per `.claude/rules/codex-review-gate.md`, no GT-KB source, doc,
hook, template, script, DB, or managed-artifact mutation may begin until Codex
GOs this `-007`.

---

## 1. Summary of Revisions vs `-005`

| Origin | Finding | Where discharged in `-007` |
|--------|---------|---------------------------|
| `-006` #1 (High) | Q3 bypass `source_ref` conflicts with canonical `owner_conversation` pattern | §5.5.1 (revised source_ref grammar) + §5.5.3 (updated tests) + §5.3 (Phase 3 validator cross-ref) |
| `-006` #2 (High) | Transcript dry-run artifact specified after mutation | §5.6.2 (queue = pre-insert dry-run artifact) + §5.6.3 (refusal contract) + §5.6.4 (new tests 12 + 13) + §7 (post-impl report renames) |
| `-006` non-blocking a | Phase 0 sequencing acceptable | Preserved from `-005` §3 |
| `-006` non-blocking b | A3 HYBRID branch acceptable once transcript fixed | Preserved from `-005` §5.9 A3 + finding #2 fix flows through |
| `-006` non-blocking c | A5 CI/static evidence acceptable; note CI-result source determinism | §5.9 A5 (CI-result source rule made explicit) |
| `-006` non-blocking d | Correct scaffold surface path | §5.11 (replaces stale `templates/scaffolded/settings.json` reference) |

All previously accepted content from `-005` is retained verbatim unless noted above.

**Owner decisions from DELIB-0819 (unchanged):**
- Q1 = HYBRID (heuristic extraction + per-candidate owner review-gate)
- Q2 = WARN-all (store `redaction_state='partial'` for all source_types; no BLOCK in v1)
- Q3 = env var `GTKB_DA_PREFLIGHT_BYPASS=<reason>` + content marker `# da-search-confirmed: <reason>`

---

## 2. Discharge of 7 Required Implementation Conditions (from scope `-004`)

*(Unchanged from `-005` §2.)*

| # | Condition from scope `-004` | Where discharged |
|---|------------------------------|------------------|
| 1 | Obtain owner decisions before implementation starts | §3 — DELIB-0819 captured 2026-04-17T22:38Z |
| 2 | Preserve harvest-coverage sequencing gate | §5.9 — harvest-coverage VERIFIED at `-011`; B1 ships with this bridge |
| 3 | Source-ref validation non-breaking for DB/CLI v1 | §5.3 — warn-only at DB/CLI; producers strict-validate |
| 4 | Managed artifacts + scaffold + focused hook tests for all new hooks/helpers | §5.7 + §5.11 (full UserPromptSubmit/PostToolUse/PreToolUse surface + upgrade enforcement extension) |
| 5 | All new DA inserts on DB API path; no direct SQLite writes | §5.2 CI DB-routing invariant test (`tests/test_da_db_routing_invariant.py`) |
| 6 | Dry-run artifacts + owner approval before live backfill/transcript mutation | §5.4 LO-report dry-run; **§5.6 transcript queue IS the pre-insert dry-run artifact (revised)** |
| 7 | Post-impl report with focused test output + DA count evidence | §7 |

---

## 3. Phase 0 — Owner Decision Gate (satisfied)

*(Unchanged from `-005` §3.)*

**Sequencing rule:** the only authorized pre-implementation mutation is the Q1/Q2/Q3 DELIB insertion itself. All other GT-KB / Agent Red / dry-run work blocked until that DELIB exists and is cited in Phase 1 spec bodies.

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

Verified by read-only SQLite query on Agent Red `groundtruth.db`.

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

*(Unchanged from `-005` §4.)*

| Gate | Blocks phase(s) | Status |
|------|-----------------|--------|
| Codex GO on this `-007` | All phases | Pending review |
| Phase-0 DELIB captured | All phases | **Released** (DELIB-0819) |
| Q1 answer (HYBRID) | Phase 6 flow + Phase 9 A3 shape | Released — §5.6 + §5.9 A3 |
| Q2 answer (WARN-all) | Phase 2 residual-rescan severity + Phase 9 A4 ALARM semantics | Released — §5.2 + §5.9 A4 |
| Q3 answer (env+marker) | Phase 5 bypass surfaces honored by `delib-preflight-gate.py` | Released — §5.5 |

**Post-Codex-GO parallelization:** Phase 1 spec recording must land first (so Phase-2..8 test/hook files can cite the 8 spec IDs). After Phase 1, Phases 2/3/4(dry-run)/5/6(queue-only)/7/8 may execute in parallel. Phase 9 waits on 2/5/6/7. Phase 4 `--execute` waits on Phase 8 framework + owner AUQ approval. Phase 6 `--insert-approved` waits on per-candidate review approval per Q1=HYBRID.

---

## 5. Per-Phase Execution Plan

### 5.1 Phase 1 — Spec recording

*(Unchanged from `-005` §5.1.)* 8 specs in MemBase via `db.insert_spec()`: `SPEC-DA-GOV-LO-COVERAGE`, `SPEC-DA-GOV-OWNER-DECISION-CAPTURE`, `SPEC-DA-GOV-TRANSCRIPT-EXTRACT`, `SPEC-DA-GOV-REDACTION-ROUTING`, `SPEC-DA-GOV-SOURCE-REF-IDENTITY`, `SPEC-DA-GOV-BACKFILL-FRAMEWORK`, `SPEC-DA-GOV-PREFLIGHT-HARDBLOCK`, `SPEC-DA-GOV-WRAP-GATE`. Each cites DELIB-0715, DELIB-0719, and DELIB-0819. Status: `specified`. Acceptance: `gt spec list --tag da-governance` returns 8 rows, all `specified`.

### 5.2 Phase 2 — Redaction routing invariant + residual re-scan (Q2 = WARN-all)

*(Unchanged from `-005` §5.2.)* New test files `tests/test_da_db_routing_invariant.py` (AST walk of DA-writer modules; failures on any direct `sqlite3.*` call targeting `deliberations*`) and `tests/test_da_residual_rescan.py` (verifies `redaction_state='partial'` set on residual matches, insert always proceeds per Q2=WARN-all). `insert_deliberation()` and `upsert_deliberation_source()` gain a post-redaction residual re-scan. Residual outcome appended to `.groundtruth/delib-residual-rescan-log.jsonl`.

### 5.3 Phase 3 — Source-ref validation (warn-only v1)

*(Body unchanged from `-001` §5.3.)* Warn-only at DB/CLI; producer scripts strict-validate before `insert_deliberation()` call. Structured warnings → `.groundtruth/delib-insert-warnings.jsonl`. Four CLI regression tests (`test.md`, `upsert-auto.md`, `t.md`, `bridge:msg-abc`) continue to insert without exception.

**Cross-reference to `-006` Finding #1 (new in `-007`):** The producer-side strict-validator for `owner_conversation` continues to enforce the canonical `{YYYY-MM-DDTHH:MM}-{topic-slug}` pattern defined in `-001:140-149`. The Q3 bypass rows defined in §5.5.1 below use this same canonical grammar (not a separate `bypass:*` shape). This keeps the `owner_conversation` identity contract single-shape.

### 5.4 Phase 4 — LO-report coverage closure + retroactive backfill

*(Unchanged from `-005` §5.4.)* Extends `scripts/harvest_session_deliberations.py`. Dry-run JSON → `bridge/gtkb-da-governance-completeness-lo-backfill-dryrun-{YYYY-MM-DD}.json`. Owner AUQ approval gates `--execute`. Expected backfill volume: ~11 missing refs.

### 5.5 Phase 5 — Preflight hook infrastructure (Q3 = env var + content marker)

#### 5.5.1 Q3 contract (REVISED per `-006` Finding #1)

**Env-var bypass (Tier A):**
- **Name:** `GTKB_DA_PREFLIGHT_BYPASS`
- **Accepted value:** non-empty string, interpreted as free-text `<reason>`. Whitespace-only values reject as empty.
- **Scope:** process-local environment; persists for the process lifetime.
- **Precedence:** env-var bypass takes precedence over the content marker (both log; env-var logs first).

**Content-marker bypass (Tier B):**
- **Syntax:** line matching regex `^# da-search-confirmed: (.+)$` where the capture group (reason) must be non-whitespace. Case-sensitive.
- **File-location rules:** allowed only on **new-topic bridge writes** (files matching `bridge/[^/]+-001\.md$` whose stem is not already in `bridge/INDEX.md`); marker must appear within the **first 3 lines**. Marker is retained in the written file (not stripped).
- **Bypass scope:** marker bypass is NOT a general-purpose search-proof bypass for arbitrary files.

**Bypass logging — canonical `owner_conversation` source_ref grammar (REVISED):**

Each successful bypass inserts one `owner_conversation` row via `KnowledgeDB.insert_deliberation()` using the **canonical source_ref pattern** `{YYYY-MM-DDTHH:MM}-{topic-slug}`:

- `source_type`: `owner_conversation`
- `source_ref`: `{YYYY-MM-DDTHH:MM}-preflight-bypass-{env|marker}-{reason-slug}`
  - `{YYYY-MM-DDTHH:MM}` is the UTC timestamp when the bypass fired, truncated to minute precision.
  - `{env|marker}` is the literal string `env` (Tier A) or `marker` (Tier B).
  - `{reason-slug}` is the first 40 chars of the reason, slugified (lowercase, non-alphanumeric → `-`, collapsed, trimmed). Empty after slugify → `no-reason` (but this cannot occur because empty reasons ALARM, see below).
  - Example: `2026-04-17T22:38-preflight-bypass-env-repair-s294-like-outage`
  - Example: `2026-04-17T22:41-preflight-bypass-marker-routine-edge-case`
- `title`: `Preflight bypass (env)` or `Preflight bypass (marker)` (unchanged)
- `summary`: `reason={reason}; target={file_path}; session={session_id}; turn={turn_id}` (unchanged)
- `content`: full `{reason, tier, file_path, session_id, turn_id, timestamp}` block in JSON-in-markdown format (unchanged)
- `metadata` (JSON): `{ "bypass_tier": "env|marker", "reason": "{full-reason}", "target_path": "{file_path}" }` — structured tier discriminator for downstream wrap-gate queries and dashboards
- `session_id`: current session (unchanged)
- `changed_by`: `delib-preflight-gate.py` (unchanged)
- `change_reason`: `preflight-bypass-authorization` (unchanged)

**Rationale for canonical grammar choice:** preserves the existing single-shape `owner_conversation` source_ref contract enforced by producer-side strict-validation (`-001:140-149`). The bypass tier and reason are carried in `title`, `summary`, `content`, and `metadata.bypass_tier` — a structured field that wrap-gate A2 (§5.9) can query directly without regex-parsing source_ref. The alternative (extending the validator to accept a second `bypass:*` shape) was rejected to avoid widening the `owner_conversation` identity contract and to keep `tests/test_source_ref_validation.py` / `tests/test_delib_preflight_gate.py` / wrap-gate owner-conversation coverage logic unchanged.

**Stale/abuse protections:**
- **Env-var tier:** no explicit TTL (env is process-scoped). Wrap-gate A2 (§5.9) surfaces every bypass row this session via a `metadata.bypass_tier IS NOT NULL` query (robust to source_ref format changes). High-bypass sessions are visible to the owner.
- **Content-marker tier:** bounded by the file-location rule (new-topic `-001` writes only) and first-3-lines rule.
- **Missing reason:** empty env value → ALARM `reason required on env bypass`; empty marker capture group → ALARM `reason required on marker bypass`.
- **Missing search log:** conservative deny + ALARM.

**Failure behavior:** bypass-logging `insert_deliberation()` failure does NOT gate the write silently — emit ALARM `bypass logging failed` and deny.

#### 5.5.2 `delib-preflight-gate.py` logic

*(Unchanged from `-005` §5.5.2.)* New files: `templates/hooks/_delib_common.py`, `templates/hooks/turn-marker.py`, `templates/hooks/delib-preflight-gate.py`. Eight-step logic: (1) path filter, (2) INDEX stem check, (3) turn-marker read with fallback, (4) search-log read, (5) topic-overlap check, (6a/6b/6c) bypass evaluation, (7) search-log failure handling, (8) bypass-logging failure handling. All ALARM/deny conditions from `-005` preserved.

#### 5.5.3 Tests (`tests/test_delib_preflight_gate.py`) — 22 total (REVISED: source_ref assertions)

Core preflight (7): unchanged from `-005`.

Env-var tier (3; source_ref assertion updated per `-006` Finding #1):
8. `GTKB_DA_PREFLIGHT_BYPASS="repair S294-like outage"` with no search → passes; logs `owner_conversation` row with:
   - `source_ref` matching regex `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}-preflight-bypass-env-repair-s294-like-outage$`
   - `metadata.bypass_tier == "env"` and `metadata.reason == "repair S294-like outage"`
9. `GTKB_DA_PREFLIGHT_BYPASS=""` → ALARM `reason required on env bypass`; deny. (Unchanged.)
10. `GTKB_DA_PREFLIGHT_BYPASS="   "` → ALARM. (Unchanged.)

Marker tier (8; source_ref assertion updated per `-006` Finding #1):
11. Marker `# da-search-confirmed: routine edge case` at line 1 → passes; logs row with:
    - `source_ref` matching regex `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}-preflight-bypass-marker-routine-edge-case$`
    - `metadata.bypass_tier == "marker"` and `metadata.reason == "routine edge case"`
12-14. Lines 2, 3, 5 behavior unchanged (2/3 pass with same canonical source_ref assertion; line 5 denies).
15-17. Empty-reason / non-`-001` path / existing-stem behavior unchanged.
18. Env AND marker both present → pass; two rows logged — env source_ref ends `-env-{env-slug}`, marker source_ref ends `-marker-{marker-slug}`. Both rows carry distinct `metadata.bypass_tier` values.

Path / integration (2):
19. DB write failure during bypass logging → ALARM + deny. (Unchanged.)
20. Existing-thread response-file writes pass. (Unchanged.)

Env-var unset (2):
21. Unset + no marker + no same-turn search → deny. (Unchanged.)
22. Windows path separators / `NotebookEdit` tool path extraction. (Unchanged.)

**Added cross-contract test** (new in `-007`):
23. Source-ref validator regression: `tests/test_source_ref_validation.py` gains a positive case confirming the Q3 canonical format `{ts}-preflight-bypass-{tier}-{slug}` passes producer strict-validation (no regex extension needed). **Total Phase 5 tests: 23.**

**Acceptance:** 23 tests green; scaffold-settings tests updated (§5.11); managed-artifacts.toml matches.

### 5.6 Phase 6 — Transcript extractor (Q1 = HYBRID — heuristic + review gate) — REVISED per `-006` Finding #2

#### 5.6.1 Q1=HYBRID authoritative semantics

HYBRID = heuristic extraction + per-candidate owner review-gate. **No candidate reaches DA without explicit per-candidate owner approval.** This is a stronger contract than per-batch dry-run-and-approve.

#### 5.6.2 Pre-insert dry-run artifact (REVISED per `-006` Finding #2)

**The `--queue` output file IS the schema-validated pre-insert dry-run artifact required by scope `-004:231-232`.**

`.groundtruth/session-extract-queue-{session-id}.jsonl` — one line per candidate. Per-line schema (unchanged from `-005`):

```jsonc
{
  "candidate_id": "c-{session-id}-{NNNN}",
  "session_id": "{session-id}",
  "turn_range": "{start_turn}-{end_turn}",
  "role": "owner" | "assistant" | "system",
  "text_preview_200chars": "...",
  "classification": "gov09" | "discussion" | "decision" | "other",
  "heuristic_signals": ["gov09_must", "gov09_numbered", "discussion_boundary"],
  "redaction_flags": ["credential_match_line_3"] | [],
  "review_state": "pending" | "approved" | "rejected" | "edited",
  "reviewed_at": null | "2026-04-17T22:40:00Z",
  "reviewer_comment": null | "...",
  "final_content": null | "..."
}
```

**Why the queue file qualifies as the pre-insert dry-run artifact under scope `-004:231-232`:**
- It contains all candidate IDs, previews, classifications, heuristic signals, and redaction flags **before any DA mutation**.
- It is schema-validated (schema defined here; validator lives in `scripts/extract_session_deliberations.py`).
- It is written by `--queue` which performs **zero DA inserts**.
- Owner approval is recorded per-candidate in `review_state` before `--insert-approved` runs.
- Per-candidate `review_state='approved'` is the approval evidence; approval granularity is finer than per-batch.

#### 5.6.3 CLI commands (REVISED: refusal contract + artifact naming)

- `--queue --session-id <id>`: reads transcript, runs heuristic extractor, writes queue file. **Zero DA inserts.** Idempotent; re-runs regenerate the queue and preserve `review_state` for unchanged `candidate_id`s (matched on content hash).
- `--review --session-id <id>`: interactive TUI showing each pending candidate; owner chooses `approve` / `reject` / `edit` / `skip` per candidate. Updates `review_state`, `reviewed_at`, optionally `final_content`.
- `--approve-ids <id1,id2,...> --session-id <id>`: non-interactive bulk approval for scripted/automation use (still requires explicit IDs).
- `--insert-approved --session-id <id>`: reads queue, for each `review_state='approved'`, inserts via `KnowledgeDB.insert_deliberation()` with `source_type='session_harvest'`, `source_ref=session:{session_id}:{turn_range}`, `content=final_content`. Updates queue to `review_state='inserted'`. Idempotent via content_hash dedupe.

**Refusal contract for `--insert-approved` (new in `-007`):**

Before any insert, `--insert-approved` performs these pre-flight checks; any failure aborts with non-zero exit code and emits ALARM via `session-health.py` on next wrap:

1. **Queue file must exist** at `.groundtruth/session-extract-queue-{session-id}.jsonl`. Missing → error `pre-insert queue artifact missing`; exit 2.
2. **Queue schema must validate** via the same schema used by `--queue`. Invalid → error `pre-insert queue schema invalid: {detail}`; exit 2.
3. **At least one candidate must be `review_state='approved'`**. If the approved-count is zero → error `no approved candidates; review required before insert`; exit 3. Rationale: protects against "ran `--insert-approved` without ever running `--review`" footgun.
4. **No candidate may be `review_state='pending'` at insert time** for the approved set path — this is the per-candidate approval contract. `pending` candidates are neither inserted nor error-causing; they are simply skipped. But if the owner believes they ran review and there are still `pending` rows, a final summary at the end of `--insert-approved` reports `pending=<N>` so the gap is visible.

**Post-insert artifact (renamed from "dry-run summary" to "execute summary"):**

After `--insert-approved` completes, an execute summary JSON lands at `bridge/gtkb-da-governance-completeness-transcript-execute-summary-{YYYY-MM-DD}.json` (previously called "dry-run" in `-005`; **this is not a dry-run artifact** — it is a post-mutation audit summary). Contents: `{session_id, candidates_total, approved, rejected, pending_skipped, inserted, skipped_duplicate, errors}`.

**Sequence and evidence summary:**
```
    --queue  →  queue file (pre-insert dry-run, schema-validated, zero DA mutation)
               ↓
    --review OR --approve-ids  →  queue updated with approval evidence
               ↓
    --insert-approved  →  refusal checks 1-4  →  DA inserts  →  execute summary JSON
```

#### 5.6.4 Missing-transcript behavior

Transcript access unavailable → WARN to session-health hook; A3 records WARN; not blocking.

#### 5.6.5 Tests (`tests/test_transcript_extract.py`) — 13 total (up from 11 in `-005`)

Core heuristic (5): unchanged from `-005`.

HYBRID review-gate (6): unchanged from `-005` except test #10 is strengthened (below).

**New tests per `-006` Finding #2 required-action item 4** ("Tests must prove `--insert-approved` refuses to run when pre-insert artifact or required approvals are missing"):

12. **Queue-missing refusal test.** Run `--insert-approved --session-id S-test` with no queue file on disk. Asserts: exit code 2, stderr contains `pre-insert queue artifact missing`, DA row count for session source_refs == 0.
13. **No-approved-candidates refusal test.** Construct a queue with 5 `pending` and 2 `rejected` candidates (zero approved). Run `--insert-approved`. Asserts: exit code 3, stderr contains `no approved candidates`, DA row count == 0.

Test #10 (existing) — **strengthened**: original asserted "DA row count for this session = 0" when all candidates pending. Now also asserts `--insert-approved` exits non-zero (code 3, per refusal check 3). Previously the test was compatible with silent no-op; the refusal contract requires an explicit exit.

**Acceptance:** 13 tests green; queue file schema validated; full-suite green.

### 5.7 Phase 7 — Owner-decision capture hook + GOV-09 capture

*(Unchanged from `-005` §5.7.)* `templates/hooks/owner-decision-capture.py` (PostToolUse, filtered on AUQ) + `templates/hooks/gov09-capture.py` (UserPromptSubmit, standalone, ordered after `spec-classifier.py`). 8 tests in `tests/test_owner_decision_capture.py`.

### 5.8 Phase 8 — Backfill framework generalization

*(Unchanged from `-005` §5.8.)* `scripts/_backfill_framework.py`. 6 tests.

### 5.9 Phase 9 — Session wrap gate

*(Unchanged from `-005` §5.9 except A5 CI-result source clarification.)*

**A1 LO-report coverage:** ALARM on gap.
**A2 Owner-conversation coverage:** ALARM on gap. Surfaces bypass rows via `metadata.bypass_tier IS NOT NULL` query (revised to use metadata field rather than regex-matching source_ref, consistent with §5.5.1 canonical grammar).
**A3 Transcript extraction (Q1=HYBRID 5-outcome):** unchanged.
**A4 Redaction re-scan (Q2=WARN-all):** unchanged.
**A5 DB-routing invariant (CI-based, clarified per `-006` non-blocking note c):**

- Canonical routing guard: `tests/test_da_db_routing_invariant.py` (Phase 2). Runs on every PR + main build as a required-check.
- Wrap output includes informational line `A5 DB-routing invariant: {green|red} on commit {SHA} at {timestamp}`.
- **CI-result source rule (new in `-007`):** the authoritative source is the file `.groundtruth/last-ci-routing-result.json`, updated by the CI workflow at the end of each successful routing-invariant test run (committed via routine housekeeping commit on the branch the CI ran against). Wrap hook reads this file. If the file is missing or older than 7 days, wrap output reports `A5 DB-routing invariant: unknown (CI result stale or missing)`; not ALARM (v1 informational). Post-impl report includes explicit `green-on-commit {SHA} at {timestamp}` evidence (§7 item 6).
- Rationale for rejecting `gh run list` live-fetch as v1 default: adds network dependency to wrap, doesn't work offline, varies by CI vendor. The committed-artifact path is deterministic and shell-independent. A `gh run list` adapter remains trivially substitutable if the repo later wants a live path.

**B1 Bridge-thread coverage:** unchanged.

**Tests (`tests/test_wrap_gate.py`) — 16 total:** unchanged from `-005`.

### 5.10 Phase 10 — Dogfooding

*(Unchanged from `-005` §5.10.)*

### 5.11 Consolidated final hook / scaffold / managed-artifact surface (REVISED per `-006` non-blocking note d)

**Scaffold path correction:** the current checkout does not contain `templates/scaffolded/settings.json`. The real registry-driven scaffold surface is:
- `templates/managed-artifacts.toml` — declarative registry of managed hooks/helpers with `installed_path`, `kind`, `event`, `template_path`, `content_hash`.
- `src/groundtruth_kb/project/scaffold.py` — consumes the registry and renders/installs `.claude/settings.json` + `.claude/hooks/*.py` into adopter projects.

**Target hook ordering after all phases land** (authoritative source = `templates/managed-artifacts.toml`; rendered into adopter `.claude/settings.json` by `scaffold.py`):

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

**`templates/managed-artifacts.toml` gains 5 new entries** (unchanged from `-005`):

| relative_path | installed_path | kind | event |
|---------------|----------------|------|-------|
| `templates/hooks/_delib_common.py` | `.claude/hooks/_delib_common.py` | helper | shared (not event-bound) |
| `templates/hooks/turn-marker.py` | `.claude/hooks/turn-marker.py` | hook | UserPromptSubmit |
| `templates/hooks/delib-preflight-gate.py` | `.claude/hooks/delib-preflight-gate.py` | hook | PreToolUse |
| `templates/hooks/owner-decision-capture.py` | `.claude/hooks/owner-decision-capture.py` | hook | PostToolUse |
| `templates/hooks/gov09-capture.py` | `.claude/hooks/gov09-capture.py` | hook | UserPromptSubmit |

Each entry includes `template_path` + `content_hash` per the existing schema.

**Upgrade / doctor enforcement extension:**

Current `src/groundtruth_kb/project/upgrade.py:223-228` enforces managed-artifact settings for `PreToolUse` only. This bridge extends enforcement to `UserPromptSubmit` and `PostToolUse`.

Files modified:
- `src/groundtruth_kb/project/upgrade.py` — generalize `_enforce_managed_hooks_in_settings()` or add parallel enforcement functions for UserPromptSubmit + PostToolUse, preserving PreToolUse behavior.
- `src/groundtruth_kb/project/doctor.py` — extend settings-check to report missing/out-of-order entries across all three events.
- `src/groundtruth_kb/project/scaffold.py` — confirm it reads the full registry and writes settings.json ordering per the target above (should already be registry-driven; touch only if a gap is found).
- `tests/test_upgrade.py` — ~4 new cases for UserPromptSubmit + PostToolUse enforcement.
- `tests/test_doctor.py` — ~4 new cases for UserPromptSubmit + PostToolUse reporting.
- `tests/test_scaffold_settings.py` — update expected lists per surface above. If `templates/scaffolded/settings.json` does not exist, this test should instead assert on `.claude/settings.json` rendered by `scaffold.py` into a tmpdir test fixture (implementation detail; pre-existing test structure will indicate the correct assertion target).

### 5.12 Phase 11 — Post-implementation report + Codex VERIFIED

Contract in §7.

---

## 6. Test Inventory Summary (REVISED counts)

| Phase | Test file | New tests in `-007` | Δ vs `-005` |
|-------|-----------|---------------------|-------------|
| 2 | `tests/test_da_db_routing_invariant.py` | ~8 | — |
| 2 | `tests/test_da_residual_rescan.py` | ~4 | — |
| 3 | `tests/test_source_ref_validation.py` | ~12 + 1 new positive case for Q3 canonical format | +1 |
| 3 | `tests/test_cli_deliberations.py` | 0 new | — |
| 4 | `tests/test_lo_report_backfill.py` | 5 | — |
| 5 | `tests/test_delib_preflight_gate.py` | 23 (was 22; +1 cross-contract check) | +1 |
| 5+7 | `tests/test_scaffold_settings.py` | 0 new (assertion target possibly updated per §5.11) | — |
| 5+7 | `tests/test_upgrade.py` | ~4 | — |
| 5+7 | `tests/test_doctor.py` | ~4 | — |
| 6 | `tests/test_transcript_extract.py` | 13 (was 11; +2 refusal tests per `-006` #2) | +2 |
| 7 | `tests/test_owner_decision_capture.py` | 8 | — |
| 8 | `tests/test_backfill_framework.py` | 6 | — |
| 9 | `tests/test_wrap_gate.py` | 16 (A1+A2+A3×5+A4×3+A5+B1+smoke) | — |
| **Total** | | **~104 new** (was ~100) | **+4** |

All new tests ASCII-only (per `tests/_print_guard.py`). All new modules mypy --strict clean, ruff check + format clean. Baseline 1161 stays green.

---

## 7. Post-Impl Report Contract (REVISED artifact naming per `-006` Finding #2)

Post-implementation report filed to this thread as `-008 NEW`. Contents:

1. **Commit SHA(s)** on `groundtruth-kb` main (one per phase ideally, or single bundled commit with per-phase subject lines).
2. **Focused test output** per phase — `pytest -v tests/test_*.py::ClassName::test_node_id` with class-qualified node IDs per `feedback_postimpl_report_hygiene.md`.
3. **Full-suite output** — `pytest` ending in `PASSED` (expected 1161 + ~104 = ~1265).
4. **mypy --strict output** — `Success: no issues found in N source files`.
5. **ruff check + format** — both clean.
6. **DB-routing invariant evidence** — green result of `tests/test_da_db_routing_invariant.py` on the final commit SHA + timestamp (discharges §5.9 A5). Include path to `.groundtruth/last-ci-routing-result.json` written by CI.
7. **Current DA count evidence** — `SELECT source_type, COUNT(*) FROM current_deliberations GROUP BY source_type;` against Agent Red `groundtruth.db`. New rows this session: LO-report backfill (~11), AUQ rounds during dogfood, dogfood-run `session_harvest` approvals, any bypass-authorization `owner_conversation` rows emitted (query `WHERE metadata->>'bypass_tier' IS NOT NULL`).
8. **Pre-insert and post-insert artifacts (renamed per `-006` Finding #2):**
   - LO-backfill dry-run JSON: `bridge/gtkb-da-governance-completeness-lo-backfill-dryrun-{YYYY-MM-DD}.json` (Phase 4).
   - **Transcript pre-insert dry-run artifact:** `.groundtruth/session-extract-queue-{session-id}.jsonl` used for dogfood review (Phase 6 `--queue` output; schema-validated; zero mutation).
   - **Transcript execute summary (NOT labeled dry-run):** `bridge/gtkb-da-governance-completeness-transcript-execute-summary-{YYYY-MM-DD}.json` (Phase 6 `--insert-approved` post-mutation audit).
9. **Dogfood evidence** — `.groundtruth/dogfood-run-{date}.jsonl` + ALARM demonstration.
10. **Rollback instructions** — per phase; all changes reversible via `git revert` + per-phase DA row cleanup script.
11. **Delta summary** — commit-local line counts + range line counts (per `feedback_postimpl_report_hygiene.md`).

---

## 8. Rollback / Containment

*(Unchanged from `-005` §8.)* All reversible via `git revert` on `groundtruth-kb` main.

---

## 9. Prior Deliberations

Required DA search performed; directly relevant rows:

- `DELIB-0715` — MemBase canonical definition.
- `DELIB-0716` / `-0717` / `-0718` — bridge-thread compression examples.
- `DELIB-0719` — S299 owner-decision round.
- `DELIB-0720` / `DELIB-0818` — prior DA rows on this thread.
- `DELIB-0721` / `DELIB-0805` — harvest-coverage bridge-thread rows.
- `DELIB-0817` — S299-continuation meta-summary.
- **`DELIB-0819`** — Phase-0 Q1/Q2/Q3 owner-decision DELIB (authoritative for §3).

No prior deliberation rejected approaches chosen here. The Option A vs Option B
choice for Q3 source_ref (preserve canonical grammar vs extend validator) is
resolved in favor of Option A; Option B remains available as a future-bridge
option if downstream queries ever require source_ref-level bypass discriminator
without touching metadata.

This REVISED-3 `-007` differs from `-005` only in §5.5.1 (Q3 source_ref grammar
realigned to canonical `owner_conversation` shape), §5.6.2–§5.6.5 (queue file is
now explicitly the pre-insert dry-run artifact; `--insert-approved` gets a
refusal contract with 2 new tests; post-insert JSON renamed to "execute
summary"), §5.9 A2 (metadata-based bypass query) + A5 (CI-result source rule),
§5.11 (scaffold surface path corrected), §6 (test counts +4), and §7 (artifact
renames). All other content preserved verbatim from `-005`.

---

## 10. Required Next Steps After Codex GO on This REVISED-3 Bridge

1. **Phase 0 — already satisfied** (DELIB-0819). Phase 1 cites DELIB-0819 directly.
2. **Phase 1** — record 8 specs in MemBase citing DELIB-0715/0719/0819.
3. **After Phase 1, in parallel:**
   - Phase 2 — redaction routing invariant + residual rescan.
   - Phase 3 — source-ref warn-only + CLI regression + Q3 canonical-format positive case.
   - Phase 4 (dry-run only) — LO-report coverage + dry-run JSON.
   - Phase 5 — preflight hook (canonical source_ref grammar per §5.5.1).
   - Phase 7 — owner-decision capture + GOV-09 capture + upgrade/doctor enforcement extension.
   - Phase 8 — backfill framework.
4. **Phase 6** after Phase 5 `_delib_common.py` helper lands.
5. **Phase 9** after Phases 2/5/6/7 land.
6. **Phase 4 `--execute`** after Phase 8 framework + owner AUQ approval of Phase-4 dry-run JSON.
7. **Phase 6 `--insert-approved`** after queue + review + owner approval of queued candidates; refusal contract enforced.
8. **Phase 10** dogfood run.
9. **Phase 11** post-impl report as `-008 NEW`.

---

## 11. Open Questions for Codex

None. The two `-006` blockers are resolved per canonical-grammar / pre-insert-artifact contracts above. All four non-blocking notes from `-006` are also addressed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
