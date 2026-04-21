# Scope Proposal: Deliberation Archive Governance Completeness (REVISED)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Prior versions:** `bridge/gtkb-da-governance-completeness-001.md` (NEW), `bridge/gtkb-da-governance-completeness-002.md` (NO-GO).

This revision addresses all five Codex findings from `-002`. Changes are flagged inline with
`**[Finding N]**` so review can be performed diff-style against the NO-GO.

## Response to NO-GO Findings (summary)

| Finding | Severity | Change |
|---------|----------|--------|
| 1. Stale dependency boundary | High | Re-anchored on `gtkb-da-harvest-coverage-implementation-008 REVISED`; explicit sequencing gate added. |
| 2. Source-ref validation breaks `proposal` + CLI tests | High | `proposal` included; producer-owned vs user-supplied split; v1 warning-only + v2 strict roll-forward. |
| 3. Underspecified preflight / hook conflict | Medium | Concrete state source defined (`.groundtruth/delib-search-log.jsonl` turn-marker); relationship to existing gate/tracker stated; bypass + Codex-side coverage specified. |
| 4. Redaction reimplementation | Medium | Scope narrowed: preserve `KnowledgeDB.redact_content()` + `insert_deliberation()`; add residual re-scan tests + new-path DB-routing invariant only. |
| 5. Transcript extraction v1 contract | Medium | v1 acceptance contract added: JSONL field allow/deny list, dedupe key, dry-run artifact, failure modes, six required tests. |

## Relationship to in-flight work (**[Finding 1 — refreshed]**)

**Dependency anchor (current, not stale):**
- `bridge/gtkb-da-harvest-coverage-implementation-009.md` — NO-GO (latest). Per `bridge/INDEX.md`:
  ```
  Document: gtkb-da-harvest-coverage-implementation
  NO-GO:   bridge/gtkb-da-harvest-coverage-implementation-009.md
  REVISED: bridge/gtkb-da-harvest-coverage-implementation-008.md
  NO-GO:   bridge/gtkb-da-harvest-coverage-implementation-007.md
  NEW:     bridge/gtkb-da-harvest-coverage-implementation-006.md
  GO:      bridge/gtkb-da-harvest-coverage-implementation-005.md
  ```
- The harvest-coverage thread has undergone two NO-GO cycles since `-005 GO` (implementation
  scope drift + owner-gate protocol miscategorization). This umbrella scope therefore cannot
  assume the bridge-thread coverage baseline is settled.
- `-007 NO-GO` surfaced three live defects that must be resolved before this umbrella
  scope's Phase 9 (wrap-gate bridge-thread assertion) can execute:
  (a) `-006` was an owner-gate note, not a proposal or post-impl report;
  (b) execute set was 97 rows against a 96-row owner-approved dry-run (scope drift);
  (c) implementation evidence (final execute JSON, idempotence, doctor output, test output)
  was not in the queued bridge file.
- `-009 NO-GO` indicates the `-008 REVISED` did not yet satisfy Codex; the thread remains
  in active revision. This umbrella scope's sequencing gate applies until the thread is
  VERIFIED — the specific revision number is not load-bearing for this proposal.

**Sequencing gate for this umbrella scope:**

No phase of this bridge that depends on bridge-thread coverage being the *DA completeness
baseline* may begin execution until:

1. `gtkb-da-harvest-coverage-implementation` receives a coherent post-implementation report
   reconciling the 96→97 scope drift and is marked **VERIFIED** by Codex; AND
2. The resulting DA bridge_thread row set (canonical wildcard + legacy file-level) is either
   (i) all-wildcard at 100% active-VERIFIED-thread coverage, or (ii) explicitly documented
   as a transitional mixed state with a follow-on migration bridge filed.

The other phases of this umbrella (redaction narrowing, LO-report backfill, owner-decision
capture, preflight gate, wrap gate, backfill framework, transcript extraction) are **not**
blocked by the harvest-coverage resolution and may proceed in parallel after Codex GO on
this scope bridge. Phase ordering below marks each phase **[H-dep]** (harvest-dependent) or
**[H-indep]** (harvest-independent).

## Refreshed DA baseline (**[Finding 1 — refreshed counts]**)

Counts as of Codex NO-GO verification 2026-04-17 (read-only SQLite query against Agent Red
`groundtruth.db`):

| Artifact | Old baseline (proposal -001) | Current baseline (-002 verification) | Delta |
|----------|------------------------------|---------------------------------------|-------|
| Current deliberation rows | 722 | **821** | +99 (harvest sweep partially run) |
| `bridge_thread` rows | 59 (3 wildcard + 56 legacy) | **157** (101 wildcard-like + 56 legacy) | +98 (sweep execute artifact) |
| LO reports in `CODEX-INSIGHT-DROPBOX/` ≥100B | — | **660** | (baseline for LO coverage phase) |
| `lo_review` rows | — | **649** | missing refs = 11 (unchanged from -001) |

**Interpretation:** The 98-row bridge_thread growth is the harvest-coverage execute artifact
that `-007 NO-GO` flagged as scope-drifted. Treating the 157-row state as the *completeness
baseline* is therefore unsafe until harvest-coverage-implementation is VERIFIED. Until then,
this scope bridge treats the **56 legacy file-level rows** and the **11 missing LO-report
refs** as the only stable known-gap inventory.

## Owner Settlements (previously captured, still binding)

| # | Decision | Settlement (DELIB-0715 / DELIB-0719) |
|---|----------|--------------------------------------|
| 1 | Scope approach | File umbrella scope bridge now |
| 2 | Preflight enforcement | **Hard block** via PreToolUse hook |
| 3 | Transcript handling | Extract owner decisions + key discussions |

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0715` — MemBase canonical definition (triggering owner conversation for this scope).
- `DELIB-0716` / `-0717` / `-0718` — first examples of bridge-thread compression (manual).
- `DELIB-0719` — S299 owner-decision round including separate-bridge decision for harvest coverage.
- `DELIB-0721` — compressed bridge row for `bridge/gtkb-da-harvest-coverage-implementation-*.md`.
- `DELIB-0805` — compressed bridge row for `bridge/gtkb-da-harvest-coverage-*.md`.
- `DELIB-0817` — S299-continuation meta-summary (in-flight work overview).
- `DELIB-0818` — compressed bridge row for `bridge/gtkb-da-governance-completeness-*.md` (this thread).
- `DELIB-0105`, `DELIB-0020..0023`, `DELIB-0109` — MemBase historical trail.
- `.claude/rules/deliberation-protocol.md` — the procedural rule this scope mechanizes.
- `scripts/harvest_session_deliberations.py` header — current source classes (documented as incomplete).

No prior NO-GO rejected the *objective* of this scope; `-002` rejected the proposal shape.
No deliberations rejected hard-block preflight (that settlement is in DELIB-0715/0719).

## Scope (in)

### A. LO-report coverage closure — **[H-indep]**

- 11 LO reports in `CODEX-INSIGHT-DROPBOX/` lack DA rows.
- Extend `scripts/harvest_session_deliberations.py` to enumerate all `INSIGHTS-*.md` files
  ≥100 bytes and cross-check against `lo_review` rows by `source_ref`.
- Retroactive backfill for the 11 gaps using the same owner-approval dry-run pattern as the
  bridge-thread sweep. Dedupe key: `source_ref` + content-hash.
- Going-forward wrap-hook assertion: every LO report filed during the session must be in DA
  before wrap completes (ties into phase H).

### B. Owner-decision extraction policy — **[H-indep]**

- Today's DELIB-0715 / DELIB-0719 were inserted manually. Doesn't scale.
- **Policy:** every `AskUserQuestion` response + every GOV-09 specification-language owner
  message is archived as `source_type='owner_conversation'` by end of turn.
- **Implementation:** post-`AskUserQuestion` capture hook (session-scoped) + GOV-09 pattern
  detector (extends existing `spec-classifier.py` semantics).
- Storage routing: goes through `KnowledgeDB.insert_deliberation()` (not a bypass path), so
  the existing DB redaction contract applies automatically **[Finding 4 — narrowed]**.

### C. Transcript extraction — v1 acceptance contract (**[Finding 5 — specified]**)

**Owner decision required (Phase 0 gate):** heuristic-only v1 vs manual-annotation v1.
Default proposal: **heuristic-only v1 with a dry-run gate before first live insert**.

**Extracted material:** owner-decision messages, GOV-09 specification-language messages,
substantive design-discussion exchanges (owner+Prime pair-level). Raw transcripts stay out
of DA.

**Exact JSONL fields consumed** (allow-list; anything else is prohibited from storage):

| JSONL field | Use | Storage disposition |
|-------------|-----|---------------------|
| `session_id` | Dedupe key + `source_ref` construction | Stored in source_ref only |
| `turn_index` (or equivalent ordinal) | `source_ref` turn-range | Stored in source_ref only |
| `timestamp` | Ordering + staleness checks | Stored as `created_at` |
| `role` (owner / assistant) | Heuristic gating | Not stored separately |
| `text` content | Extracted excerpt (post-redaction) | Stored as `content` |

**Fields prohibited from storage:** tool_use results, tool_result payloads, internal system
messages, credential values in any field (redaction re-scan before store), attachments,
file paths from non-project-root directories.

**Dedupe key + `source_ref` derivation:** `session:{session_id}:{turn_start}-{turn_end}`.
Content-hash dedupe via existing `deliberation_content_hash` column.

**Dry-run artifact (required before first live insert):** JSON list of candidate excerpts
at `bridge/gtkb-da-governance-completeness-transcript-dryrun-{YYYY-MM-DD}.json` with per-row
fields `{session_id, turn_range, role, text_preview_200chars, classification,
redaction_flags}`. Owner must approve before execute.

**Failure mode when transcript access unavailable:** log a WARN to the session-health hook
output (non-blocking for wrap; visible in doctor). Does not block wrap. Harvest skip is
idempotent across future sessions when transcript reappears.

**v1 required tests (six minimum):**

1. Short owner decision (<50 chars but GOV-09 specification-language pattern) is extracted.
2. Long non-decision owner rant (≥50 chars but conversational) is not extracted.
3. Tool-output content is excluded from extracted pairs.
4. Credential-pattern content in candidate text triggers redaction before insert.
5. Missing transcript path produces WARN, not ALARM, and does not insert partial state.
6. Idempotent rerun: running transcript extractor twice on same session produces 0 new rows.

### D. Redaction scope (**[Finding 4 — narrowed]**)

**Scope narrowed:** this bridge does **not** re-implement DB redaction. Evidence confirmed
in `-002`:

- `KnowledgeDB.redact_content()` already uses `groundtruth_kb.governance.credential_patterns.db_pattern_list()`
  (`src/groundtruth_kb/db.py:4161-4183`).
- `insert_deliberation()` already hashes raw content, redacts before storage, sets
  `redaction_state="redacted"` when notes exist, stores redacted content (`src/groundtruth_kb/db.py:4229-4264`).
- Chroma indexing uses redacted content only (`src/groundtruth_kb/db.py:4556-4570`).

**What this bridge adds:**

1. **DB-routing invariant test:** every new extractor / backfill path (LO-report backfill,
   owner-decision capture, transcript extractor, session-wrap harvester) must call
   `KnowledgeDB.insert_deliberation()` or `KnowledgeDB.upsert_deliberation_source()`.
   A unit test enumerates insert sites in `scripts/` and the new hooks, asserting none
   bypass the DB layer. Any bypass is a CI failure.
2. **Residual re-scan test:** after redaction, extracted content is re-scanned using the
   same credential_patterns module; any residual match sets `redaction_state='partial'`
   and fires the severity gate (Finding-4-related owner decision below).
3. **Owner decision for partial-redaction severity** (Phase 0 gate):
   - **Option BLOCK (default proposal):** reject insert; surface to session-health hook.
     Safer for secret containment but may interrupt session wrap.
   - **Option WARN:** store with `redaction_state='partial'`; surface to doctor. Ensures
     wrap never fails but risks partial-secret storage.
   - **Recommendation:** BLOCK for owner-conversation + session-harvest source types;
     WARN for bridge_thread + lo_review (those are already post-redacted upstream). This
     split is proposed — owner to confirm, reject, or rebalance.

### E. Source-ref identity rules (**[Finding 2 — compatibility-safe]**)

**Scope correction:** GT-KB supports **six** source types, not five. Explicit table from
`src/groundtruth_kb/db.py:4214-4223` / `src/groundtruth_kb/cli.py:744-751`:

| source_type | Producer class | Proposed canonical pattern | Validation mode (v1) |
|-------------|----------------|-----------------------------|----------------------|
| `bridge_thread` | Producer-owned (harvest script) | `bridge/{thread-name}-*.md` (wildcard) | **Strict** (machine-produced) |
| `lo_review` | Producer-owned (harvest script) | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-{date}-{topic}.md` | **Strict** (machine-produced) |
| `session_harvest` | Producer-owned (transcript extractor) | `session:{session-id}:{turn-start}-{turn-end}` | **Strict** (machine-produced) |
| `owner_conversation` | Producer-owned (AskUserQuestion hook) | `{YYYY-MM-DDTHH:MM}-{topic-slug}` | **Strict** (machine-produced) |
| `report` | Mixed (harvest + CLI + manual) | path to the report file OR `methodology-review:{topic}` legacy-compat OR `{free-text}` (CLI) | **Warn-only v1 → strict v2** |
| `proposal` | **User-supplied** (CLI primary) | Any non-empty string; recommended: bridge file path or topic slug | **Warn-only v1; never strict** |

**Compatibility-aware contract:**

1. **`proposal` is included** and is explicitly user-supplied. The CLI (and existing tests
   in `tests/test_cli_deliberations.py:103-128`, `:402-466`, `:706-715`) uses short refs like
   `test.md`, `upsert-auto.md`, `t.md`. These continue to work unchanged.
2. **Validation split by producer class, not by source_type alone:**
   - Producer-owned (`bridge_thread`, `lo_review`, `session_harvest`, `owner_conversation`):
     strict validation at the `scripts/*.py` layer (before calling the DB). DB layer stays
     permissive for these types so CLI rescue paths still work.
   - User-supplied (`proposal`, `report` v1): warn-only validation — `insert_deliberation()`
     may emit a structured warning (logged to `.groundtruth/delib-insert-warnings.jsonl`)
     but does not reject.
3. **Validation mode timeline:**
   - **v1 (this bridge):** warn-only across all source types; producer-owned scripts add
     their own pre-insert strict checks. No existing test is broken.
   - **v2 (follow-on bridge, not authorized by this scope):** promote producer-owned source
     types to strict at the DB layer after a two-session burn-in with zero warnings. Any
     promotion is a separate proposal.
4. **CLI behavior preserved:** `--source-type proposal` + `--source-ref test.md` continues
   to work. A deprecation hint may be added for refs that don't look like file paths, but
   it does not block. Existing tests pass unmodified; four new tests assert this.
5. **Legacy grandfathering:** 56 legacy file-level `bridge_thread` rows + `DELIB-0712`
   (methodology_review anomaly) + any other pre-existing non-canonical refs remain in DA.
   Canonicalization is opt-in per source type via follow-on backfill bridges.

### F. Missing-source backfill framework — **[H-indep]**

- Generalize the bridge-thread retroactive sweep pattern into a reusable framework covering
  LO reports, owner conversations (pre-policy archives), and future source classes.
- Framework modules: `scripts/_backfill_framework.py` (shared) + per-source-class thin
  scripts. Shared surface: dry-run JSON schema, owner-approval gate, idempotent
  content-hash insert, post-run coverage evidence, machine-readable warning baseline.
- First adopter: LO-report coverage (phase A). Bridge-thread sweep migrates in a follow-on
  bridge once harvest-coverage-implementation is VERIFIED (avoids cross-thread churn).

### G. Session preflight gate — HARD BLOCK (**[Finding 3 — concretized]**)

**Scope correction:** this phase must coexist with the **existing** advisory infrastructure,
not replace it blindly.

**Existing infrastructure (per `-002` evidence):**

- `templates/hooks/delib-search-gate.py` — `UserPromptSubmit` hook, emits `additionalContext`
  advisory. 24-hour window, topic-scoped.
- `templates/hooks/delib-search-tracker.py` — `PostToolUse` hook, records successful searches
  to `.groundtruth/delib-search-log.jsonl` (session-persistent JSONL).
- Scaffold registration (`tests/test_scaffold_settings.py:86-107`): `delib-search-gate.py`
  on `UserPromptSubmit`; `delib-search-tracker.py` on `PostToolUse`.

**Proposed concrete design:**

1. **State source** — same-turn search proof comes from `.groundtruth/delib-search-log.jsonl`
   (the existing tracker output). Each entry already includes a timestamp and topic hash.
   **Same-turn semantics definition (this is the "exact state source" the NO-GO requested):**
   - **Turn boundary:** the PreToolUse hook reads the most recent line of
     `.groundtruth/current-turn.jsonl` (NEW file — written by a new
     `UserPromptSubmit` hook `turn-marker.py` that stamps `{turn_id, started_at}` on every
     prompt). Any search-log entry with `timestamp >= current-turn.started_at` counts.
   - **Fallback window (if turn-marker missing):** accept search entries within the last
     **10 minutes** (configurable via env var `GT_DA_PREFLIGHT_FALLBACK_SECONDS`).
   - **Topic match:** reuses the existing topic-normalization function from
     `delib-search-gate.py` / `delib-search-tracker.py` (shared stopword set + token hash).
     The bridge file path about to be written is normalized to a topic; the search log must
     contain at least one entry whose topic overlaps.

2. **Relationship to existing hooks:**
   - `delib-search-gate.py` (UserPromptSubmit advisory) → **kept unchanged**. It nudges at
     prompt time, which is still useful for non-proposal contexts.
   - `delib-search-tracker.py` (PostToolUse tracker) → **kept unchanged**. It remains the
     source of truth for "a search happened."
   - `delib-preflight-gate.py` (NEW, PreToolUse) → adds hard-block at write time. Reads the
     tracker's log; does not write new state. Zero overlap with existing gate logic.
   - `turn-marker.py` (NEW, UserPromptSubmit) → stamps current-turn.jsonl. Ordering: runs
     before `delib-search-gate.py` in the settings.json hook list.

3. **Trigger scope (Prime and Codex):**
   - Block `Write` / `Edit` / `NotebookEdit` when `tool_input.file_path` matches regex
     `bridge/[^/]+-001\.md$` **OR** `bridge/[^/]+-\d{3}\.md$` where the matched stem is not
     already present in `bridge/INDEX.md` (i.e., any new-topic proposal). This covers
     Codex-authored proposal writes too — Codex proposals don't always land at `-001.md`
     (e.g., `-003.md` REVISED is the first write for some revisions), so path-pattern alone
     is insufficient. The stem-vs-INDEX check catches Codex-side first-of-topic writes.
   - Does **not** block: responses (`-002.md` GO/NO-GO files for existing threads),
     post-impl reports (existing thread), the bridge INDEX itself.

4. **Bypass behavior (per NO-GO Required-Action #3):**
   - **Session-local authorized bypass file:** `.groundtruth/preflight-bypass.flag`. Empty
     content, created only by explicit owner instruction in-session. Lifetime: one session;
     session-start hook deletes any stale flag file older than 24 hours.
   - **Environment variable bypass:** `GT_DA_PREFLIGHT_BYPASS=1` — persistent bypass, intended
     only for infrastructure-repair sessions (S294-class hook outages where the gate itself
     would block the fix). Env-var bypass is logged on every activation as a structured
     `owner_conversation` row marked `bypass_authorization`.
   - **No silent bypass under any other condition.**

5. **Failure modes:**
   - If `.groundtruth/delib-search-log.jsonl` is missing or unreadable → gate emits ALARM and
     blocks (conservative default). The owner can then fix the tracker or use a bypass.
   - If the topic normalization fails to produce a token set → gate treats the write as
     unmatched and blocks.
   - If the bypass file exists and is older than its 24-hour horizon → session-start hook
     deletes it and emits a WARN on next prompt.

6. **Reused infrastructure:** topic-normalization code is extracted from
   `delib-search-gate.py` / `delib-search-tracker.py` into a shared module
   (`templates/hooks/_delib_common.py`), consumed by all three hooks. This closes the
   NO-GO's "duplicated governance surfaces" concern by making the topic matcher authoritative
   in one place.

### H. Session wrap gate (expanded) — **[H-dep for bridge-thread coverage, H-indep for everything else]**

Wrap-hook assertions beyond "harvest ran without errors":

1. All LO reports filed this session are present in DA (phase A invariant).
2. All `AskUserQuestion` interactions are archived as `owner_conversation` (phase B).
3. All bridge-thread activity from this session is archived **only after
   harvest-coverage-implementation is VERIFIED** (phase H-dep portion).
4. Session-transcript extraction ran (phase C) and produced zero errors.
5. Redaction re-scan test passed on all inserts this session (phase D residual test).
6. No insert bypassed `KnowledgeDB.insert_deliberation()` / `upsert_deliberation_source()`
   (phase D routing invariant).

Any gap → wrap fails with ALARM; doctor records the gap details for post-session review.

## Scope (out)

- Full raw transcript ingestion (owner decision #3).
- Code for harvest-coverage bridge-thread pieces (owned by `gtkb-da-harvest-coverage-implementation`).
- DA schema changes beyond existing `redaction_state` / `redaction_notes` columns.
- Cross-project harvesting beyond Agent-Red-as-dogfood-adopter + GT-KB-as-product.
- **v2 strict-mode promotion** of source-ref validation at the DB layer (explicit follow-on bridge).
- **Re-implementation of DB redaction** (Finding 4).

## Proposed Spec Inventory (for Codex review)

After Codex GO, record in GT-KB MemBase (`type=requirement`, `tags=['da-governance','completeness']`):

| # | Draft ID | Requirement |
|---|----------|-------------|
| 1 | SPEC-DA-GOV-LO-COVERAGE | Every LO report filed in a session MUST reach DA before wrap completes; gap → ALARM. |
| 2 | SPEC-DA-GOV-OWNER-DECISION-CAPTURE | Every AskUserQuestion response + every GOV-09 owner message MUST be archived as `owner_conversation` by end of turn. |
| 3 | SPEC-DA-GOV-TRANSCRIPT-EXTRACT | Session-wrap MUST extract owner decisions + substantive discussions from session transcripts into DA as `session_harvest` per the v1 contract in phase C. |
| 4 | SPEC-DA-GOV-REDACTION-ROUTING | All DA inserts MUST go through `KnowledgeDB.insert_deliberation()` / `upsert_deliberation_source()`; residual re-scan test MUST pass. |
| 5 | SPEC-DA-GOV-SOURCE-REF-IDENTITY | `insert_deliberation()` MUST emit structured warnings for source-ref pattern mismatches (warn-only v1); producer scripts MUST strictly validate their own source classes. |
| 6 | SPEC-DA-GOV-BACKFILL-FRAMEWORK | Reusable missing-source backfill framework MUST exist, callable for any supported source class with idempotent content-hash dedupe. |
| 7 | SPEC-DA-GOV-PREFLIGHT-HARDBLOCK | PreToolUse hook MUST hard-block `Write` to new-topic `bridge/` files without a same-turn `search_deliberations()` entry; bypass only via documented owner-authorized flag or env var. |
| 8 | SPEC-DA-GOV-WRAP-GATE | Session wrap-hook MUST assert LO/owner-conversation/bridge/transcript coverage (per phase H) before marking wrap complete; any gap → ALARM. |

## Open Questions for Codex (reduced from -001)

1. Source-ref validation — is warn-only v1 with producer-side strict validation acceptable,
   or does Codex prefer an immediate strict-at-DB promotion for at least one source type?
2. Preflight gate — is `.groundtruth/current-turn.jsonl` + 10-minute fallback the right
   same-turn state model, or does Codex prefer a different turn-boundary signal
   (e.g., process-start timestamp, parent-process PID, Claude Code session ID)?
3. Preflight scope — is the bridge-stem-vs-INDEX check sufficient to cover Codex-side first-of-topic
   writes, or is a separate explicit Codex-review hook needed?

(Questions previously raised about redaction duplication, source-ref breakage, and transcript
heuristic severity are resolved in this revision; the remaining three are genuinely open.)

## Open Questions for Owner (explicit decisions required before implementation starts)

**[Finding 5 — transcript mode]** **Q1.** Transcript extraction v1 mode:
  - (a) **Heuristic-only with dry-run gate** (default proposal) — faster, machine-scalable,
    may miss edge cases.
  - (b) **Manual annotation pass per session** — slower, owner-burdening, highest fidelity.
  - (c) **Hybrid: heuristic-only for GOV-09 patterns + manual for non-GOV-09 discussion** —
    moderate owner burden, high fidelity on decisions.

**[Finding 4 — partial-redaction severity]** **Q2.** Partial-redaction behavior:
  - (a) **BLOCK for owner_conversation + session_harvest; WARN for bridge_thread + lo_review**
    (default proposal).
  - (b) **BLOCK for all source types** — safest, but risks wrap failures on unexpected matches.
  - (c) **WARN for all source types** — never blocks, but risks partial-secret storage.

**[Finding 3 — preflight bypass]** **Q3.** Preflight bypass authorization model:
  - (a) **Session-local flag file + env-var for infra repair** (default proposal).
  - (b) **Session-local flag file only; no env-var** — safer, forces infrastructure-repair
    sessions to jump through an extra hoop.
  - (c) **No bypass at all** — strictest; requires emergency-repair paths to be structured as
    `bridge/` response files (which are not blocked).

## Implementation Approach (high level, sequenced against findings)

**Phase 0 — Owner decisions (gate for Phases 2, 5, 6):** Q1 / Q2 / Q3 answered.

**Phase 1 — Spec recording:** 8 specs into GT-KB MemBase (KB mutation, governed by `.claude/rules/codex-review-gate.md`).

**Phase 2 — Redaction routing invariant + residual re-scan tests:** narrow scope per Finding 4.

**Phase 3 — Source-ref validation (warn-only v1) + producer-script strict checks:** per Finding 2.

**Phase 4 — LO-report coverage extension + retroactive backfill:** reuses backfill framework (phase 8).

**Phase 5 — Owner-decision capture hook (AskUserQuestion post-hook + GOV-09 detector):** per phase B.

**Phase 6 — Transcript extractor (v1 per phase C contract):** dry-run artifact, owner gate, live execute.

**Phase 7 — Preflight hook infrastructure:** turn-marker + preflight-gate + shared `_delib_common.py`.

**Phase 8 — Backfill framework generalization + LO-report first adopter.**

**Phase 9 — Wrap-gate expansion:** per phase H; the bridge-thread-coverage portion is gated
on harvest-coverage-implementation VERIFIED.

**Phase 10 — Dogfooding:** end-to-end session run; every assertion exercised.

**Phase 11 — Post-impl + Codex VERIFIED.**

Phases 2/3/5/7/8 are harvest-independent and may parallelize after Phase 0. Phase 4 can start
after Phase 8 stub lands. Phase 6 depends on Phase 0 Q1 answer. Phase 9 (bridge-thread
portion) blocks on external VERIFIED.

## Timeline (revised)

- **2026-04-17:** revised scope bridge filed (this file).
- **2026-04-17 / 18:** Codex review of -003.
- **2026-04-18:** owner answers Phase 0 Q1/Q2/Q3 via AskUserQuestion round.
- **2026-04-18–20:** on GO, Phases 1–8 in sequence/parallel as constraints allow.
- **2026-04-20–21:** Phase 9 pending harvest-coverage VERIFIED; Phases 10–11 follow.

## Rollback / Containment

- **Phase 2 (redaction routing):** additive; the DB redaction contract is unchanged, so rollback
  is test-removal only.
- **Phase 3 (source-ref warn-only):** warn-only v1 is inherently non-breaking; rollback is
  log-suppression only.
- **Phase 6 (transcript extractor):** dry-run gate prevents any live insert until owner approves.
- **Phase 7 (preflight hook):** bypass file + env var provide immediate recovery if the gate
  false-positives. Git revert of the hook file + scaffold entry removes it entirely.
- **Phase 9 (wrap gate):** assertions are additive; disabling the hook restores current wrap.

All changes reversible via git revert; DA row cleanup scripted per-phase if any live insert
needs to be rolled back.

## Required Next Steps After Codex GO

1. Obtain owner decisions on Q1 / Q2 / Q3 (Phase 0 gate).
2. File implementation bridge `gtkb-da-governance-completeness-implementation-001.md`.
3. Execute Phases 1–11 on feature branch in GT-KB.
4. Dogfood in fresh session; verify gate behavior on a simulated MemBase-style failure.
5. VERIFIED + merge.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
