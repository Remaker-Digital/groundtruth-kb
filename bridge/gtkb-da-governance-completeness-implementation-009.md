# Implementation Bridge: DA Governance Completeness (REVISED-4, focused)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`

**Revision basis:** addresses the two blockers in Codex NO-GO
`bridge/gtkb-da-governance-completeness-implementation-008.md`:

1. Bypass audit relies on a non-existent `metadata` column on
   `deliberations` / `current_deliberations` that `insert_deliberation()`
   does not accept. Reworked in §5.5.1 to carry bypass discriminators in
   existing schema columns (`change_reason`, `title`, `source_ref`),
   without any DA schema change.
2. `templates/managed-artifacts.toml` registration was under-specified:
   the 5 file records alone do not render hook invocations into
   `.claude/settings.json` because `scaffold._write_settings_json()`
   consumes only `settings-hook-registration` records in registry order.
   §5.11 now specifies the 4 new `settings-hook-registration` records
   (turn-marker, gov09-capture, owner-decision-capture, delib-preflight-gate),
   their exact in-file placement relative to the existing 11 records, and
   upgraded tests that assert registry-driven rendered ordering.

**Prior versions on disk:**
- `-001` NEW — initial implementation bridge
- `-002` NO-GO — 5 findings
- `-003` REVISED — draft (addressed 2 of 5)
- `-004` NO-GO — 3 findings
- `-005` REVISED-2 — comprehensive, discharged 7 prior action items
- `-006` NO-GO — 2 High findings (Q3 source_ref conflict + transcript dry-run sequencing)
- `-007` REVISED-3 — fixed Q3 canonical grammar + transcript pre-insert artifact + scaffold path
- `-008` NO-GO — 2 findings (metadata column doesn't exist; settings-hook-registration missing)

**Supersedes `-007`.** Preserves all content accepted by `-008`:
Phase 0 DELIB-0819 sequencing; transcript queue as pre-insert dry-run
artifact + refusal contract; canonical `owner_conversation` source_ref
grammar; A3 HYBRID branch; A5 CI-result deterministic file; correct
scaffold surface path. Rewrites only:

- §5.5.1 (bypass DELIB storage contract — no `metadata` field)
- §5.5.3 (tests: no `metadata` assertions)
- §5.9 A2 (wrap-gate query shape)
- §5.11 (adds 4 settings-hook-registration records + registry-order tests)
- §6 (test counts updated)
- §7 item 7 (DA count evidence query shape)

**Scope-bridge references:**
- `bridge/gtkb-da-governance-completeness-003.md` (REVISED scope proposal)
- `bridge/gtkb-da-governance-completeness-004.md` (Codex scope GO with 7 conditions)

**Authorization chain:** Scope GO at `-004` authorizes filing this
implementation bridge only. Per `.claude/rules/codex-review-gate.md`, no
GT-KB source, doc, hook, template, script, DB, or managed-artifact
mutation may begin until Codex GOs this `-009`.

---

## 1. Summary of Revisions vs `-007`

| Origin | Finding | Where discharged in `-009` |
|--------|---------|---------------------------|
| `-008` #1 (High) | Bypass DELIB depends on non-existent `metadata` column on `deliberations` and non-existent `metadata=` kwarg on `insert_deliberation()` | §5.5.1 (bypass tier/reason carried in `change_reason`, `title`, `content` only) + §5.5.3 (tests drop metadata assertions, assert `change_reason`, `title`, `source_ref`) + §5.9 A2 (wrap-gate query uses `change_reason='preflight-bypass-authorization'`) + §7 item 7 (DA count evidence query uses the same discriminator) |
| `-008` #2 (Medium) | Scaffold registration underspecified; hook file records do not produce `.claude/settings.json` entries | §5.11 (adds 4 new `settings-hook-registration` records with explicit registry placement; upgrades scaffold/upgrade/doctor tests to assert rendered `.claude/settings.json` ordering per registry sequence) + §6 (+3 test cases) |
| `-008` non-blocking a (Q3 shape) | Canonical `owner_conversation` source_ref grammar accepted | Preserved verbatim from `-007` §5.5.1 |
| `-008` non-blocking b (transcript sequencing) | Queue-as-pre-insert-artifact + refusal contract accepted | Preserved verbatim from `-007` §5.6 |
| `-008` non-blocking c (Phase 0) | DELIB-0819-first sequencing accepted | Preserved verbatim from `-007` §3 |
| `-008` non-blocking d (A5 CI result) | Deterministic CI-result file acceptable as informational v1 | Preserved verbatim from `-007` §5.9 A5 |

All previously accepted content is retained verbatim unless noted above.

**Owner decisions from DELIB-0819 (unchanged):**
- Q1 = HYBRID (heuristic extraction + per-candidate owner review-gate)
- Q2 = WARN-all (store `redaction_state='partial'` for all source_types; no BLOCK in v1)
- Q3 = env var `GTKB_DA_PREFLIGHT_BYPASS=<reason>` + content marker `# da-search-confirmed: <reason>`

**Rejected schema-change path (new in `-009`):** adding a `metadata` JSON
column to `deliberations` plus a `metadata=` kwarg to
`insert_deliberation()` plus a migration was considered and rejected for
this bridge. Reasons: (a) scope `-004:340-344` kept DA schema changes out
of scope beyond the existing `redaction_state` / `redaction_notes`
columns; (b) a schema-change bridge would need migration tests, Chroma
metadata effects, backward-compatibility evidence, and producer-side
strict-validation widening; (c) no current DA consumer actually needs
structured metadata for query — the bypass discriminator can be carried
by `change_reason` (already an indexed-value-candidate column) without
widening the schema. If a future bridge wants structured deliberation
metadata, it should be proposed as a dedicated schema/API migration.

---

## 2. Discharge of 7 Required Implementation Conditions (from scope `-004`)

*(Unchanged from `-007` §2.)*

| # | Condition from scope `-004` | Where discharged |
|---|------------------------------|------------------|
| 1 | Obtain owner decisions before implementation starts | §3 — DELIB-0819 captured 2026-04-17T22:38Z |
| 2 | Preserve harvest-coverage sequencing gate | §5.9 — harvest-coverage VERIFIED at `-011`; B1 ships with this bridge |
| 3 | Source-ref validation non-breaking for DB/CLI v1 | §5.3 — warn-only at DB/CLI; producers strict-validate |
| 4 | Managed artifacts + scaffold + focused hook tests for all new hooks/helpers | §5.7 + §5.11 (both hook file records AND settings-hook-registration records; upgrade enforcement extension) |
| 5 | All new DA inserts on DB API path; no direct SQLite writes | §5.2 CI DB-routing invariant test (`tests/test_da_db_routing_invariant.py`) |
| 6 | Dry-run artifacts + owner approval before live backfill/transcript mutation | §5.4 LO-report dry-run; §5.6 transcript queue IS the pre-insert dry-run artifact |
| 7 | Post-impl report with focused test output + DA count evidence | §7 |

---

## 3. Phase 0 — Owner Decision Gate (satisfied)

*(Unchanged from `-007` §3.)*

**Sequencing rule:** the only authorized pre-implementation mutation is
the Q1/Q2/Q3 DELIB insertion itself. All other GT-KB / Agent Red /
dry-run work blocked until that DELIB exists and is cited in Phase 1
spec bodies.

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

*(Unchanged from `-007` §4.)*

| Gate | Blocks phase(s) | Status |
|------|-----------------|--------|
| Codex GO on this `-009` | All phases | Pending review |
| Phase-0 DELIB captured | All phases | **Released** (DELIB-0819) |
| Q1 answer (HYBRID) | Phase 6 flow + Phase 9 A3 shape | Released — §5.6 + §5.9 A3 |
| Q2 answer (WARN-all) | Phase 2 residual-rescan severity + Phase 9 A4 ALARM semantics | Released — §5.2 + §5.9 A4 |
| Q3 answer (env+marker) | Phase 5 bypass surfaces honored by `delib-preflight-gate.py` | Released — §5.5 |

**Post-Codex-GO parallelization:** Phase 1 spec recording must land
first (so Phase-2..8 test/hook files can cite the 8 spec IDs). After
Phase 1, Phases 2/3/4(dry-run)/5/6(queue-only)/7/8 may execute in
parallel. Phase 9 waits on 2/5/6/7. Phase 4 `--execute` waits on
Phase 8 framework + owner AUQ approval. Phase 6 `--insert-approved`
waits on per-candidate review approval per Q1=HYBRID.

---

## 5. Per-Phase Execution Plan

### 5.1 Phase 1 — Spec recording

*(Unchanged from `-007` §5.1.)* 8 specs in MemBase via `db.insert_spec()`:
`SPEC-DA-GOV-LO-COVERAGE`, `SPEC-DA-GOV-OWNER-DECISION-CAPTURE`,
`SPEC-DA-GOV-TRANSCRIPT-EXTRACT`, `SPEC-DA-GOV-REDACTION-ROUTING`,
`SPEC-DA-GOV-SOURCE-REF-IDENTITY`, `SPEC-DA-GOV-BACKFILL-FRAMEWORK`,
`SPEC-DA-GOV-PREFLIGHT-HARDBLOCK`, `SPEC-DA-GOV-WRAP-GATE`. Each cites
DELIB-0715, DELIB-0719, and DELIB-0819. Status: `specified`. Acceptance:
`gt spec list --tag da-governance` returns 8 rows, all `specified`.

### 5.2 Phase 2 — Redaction routing invariant + residual re-scan (Q2 = WARN-all)

*(Unchanged from `-007` §5.2.)*

### 5.3 Phase 3 — Source-ref validation (warn-only v1)

*(Unchanged from `-007` §5.3, including the Q3 canonical-format positive
case in `tests/test_source_ref_validation.py`.)*

### 5.4 Phase 4 — LO-report coverage closure + retroactive backfill

*(Unchanged from `-007` §5.4.)*

### 5.5 Phase 5 — Preflight hook infrastructure (Q3 = env var + content marker)

#### 5.5.1 Q3 contract — bypass DELIB storage (REVISED per `-008` #1)

**Env-var bypass (Tier A) and content-marker bypass (Tier B):** syntax,
file-location rules, and precedence unchanged from `-007` §5.5.1.

**Bypass logging — columns used (no `metadata` column):**

Each successful bypass inserts one `owner_conversation` row via
`KnowledgeDB.insert_deliberation()` using ONLY columns that exist on the
current `deliberations` schema and parameters accepted by the current
`insert_deliberation()` signature (verified against
`src/groundtruth_kb/db.py:331-354` and `:4189-4208`):

- `id`: newly allocated `DELIB-NNNN` per `_next_deliberation_version()` conventions
- `source_type`: `owner_conversation`
- `source_ref`: canonical grammar `{YYYY-MM-DDTHH:MM}-preflight-bypass-{env|marker}-{reason-slug}`
  - `{YYYY-MM-DDTHH:MM}` is the UTC timestamp when the bypass fired, truncated to minute precision.
  - `{env|marker}` is the literal string `env` (Tier A) or `marker` (Tier B).
  - `{reason-slug}` is the first 40 chars of the reason, slugified (lowercase, non-alphanumeric → `-`, collapsed, trimmed). Empty after slugify → `no-reason` (cannot occur because empty reasons ALARM).
  - Example: `2026-04-17T22:38-preflight-bypass-env-repair-s294-like-outage`
  - Example: `2026-04-17T22:41-preflight-bypass-marker-routine-edge-case`
- `title`: **exactly** `Preflight bypass (env)` (Tier A) or `Preflight bypass (marker)` (Tier B). Title strings are a contract — wrap-gate and tests compare against these exact values.
- `summary`: `reason={reason}; target={file_path}; session={session_id}; turn={turn_id}`
- `content`: JSON-in-markdown block with keys `{reason, tier, file_path, session_id, turn_id, timestamp}`. Tier discriminator is present in `content` as a machine-parseable record for anyone who wants structured detail (no column needed; this is canonical deliberation content use).
- `session_id`: current session
- `outcome`: `informational` (accepted by `insert_deliberation()` validation)
- `changed_by`: `delib-preflight-gate.py`
- `change_reason`: **exactly** `preflight-bypass-authorization`. This is the primary queryable discriminator for wrap-gate A2 and DA-count evidence. Rationale: `change_reason` is a `TEXT NOT NULL` column on every deliberation row, exists in `current_deliberations`, requires no schema change, and is produced by a small enumerated set of writers in this codebase — making it a stable predicate for audit queries.

**Discriminator layering:**

| Need | Query / assertion source |
|------|-----|
| "Is this row a preflight-bypass row?" | `change_reason = 'preflight-bypass-authorization'` |
| "Which tier fired?" | `title = 'Preflight bypass (env)'` OR `title = 'Preflight bypass (marker)'` |
| "When / what file / what reason?" | Structured `content` JSON; authoritative machine-readable detail |
| "Sortable audit ordering" | `source_ref` canonical timestamp prefix |

No column additions, no kwarg additions, no validator widening. All
inserts go through the existing DB API per scope condition #5.

**Rationale for rejecting the metadata-column path:** see §1. Cross-
reference: scope `-004:340-344` explicitly kept DA schema changes out of
scope beyond `redaction_state` / `redaction_notes`.

**Stale/abuse protections:**
- **Env-var tier:** no explicit TTL (env is process-scoped). Wrap-gate A2 (§5.9) surfaces every bypass row this session via the `change_reason` query (below). High-bypass sessions are visible to the owner.
- **Content-marker tier:** bounded by the file-location rule (new-topic `-001` writes only) and first-3-lines rule.
- **Missing reason:** empty env value → ALARM `reason required on env bypass`; empty marker capture group → ALARM `reason required on marker bypass`.
- **Missing search log:** conservative deny + ALARM.

**Failure behavior:** bypass-logging `insert_deliberation()` failure does
NOT gate the write silently — emit ALARM `bypass logging failed` and deny.

#### 5.5.2 `delib-preflight-gate.py` logic

*(Unchanged from `-007` §5.5.2.)*

#### 5.5.3 Tests (`tests/test_delib_preflight_gate.py`) — 23 total (REVISED assertions per `-008` #1)

Core preflight (7): unchanged.

Env-var tier (3; assertions updated):
8. `GTKB_DA_PREFLIGHT_BYPASS="repair S294-like outage"` with no search → passes; logs `owner_conversation` row with:
   - `source_type == "owner_conversation"`
   - `source_ref` matching regex `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}-preflight-bypass-env-repair-s294-like-outage$`
   - `title == "Preflight bypass (env)"`
   - `change_reason == "preflight-bypass-authorization"`
   - `json.loads(content)["tier"] == "env"` AND `json.loads(content)["reason"] == "repair S294-like outage"`
9. `GTKB_DA_PREFLIGHT_BYPASS=""` → ALARM `reason required on env bypass`; deny.
10. `GTKB_DA_PREFLIGHT_BYPASS="   "` → ALARM.

Marker tier (8; assertions updated):
11. Marker `# da-search-confirmed: routine edge case` at line 1 → passes; logs row with:
    - `source_type == "owner_conversation"`
    - `source_ref` matching regex `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}-preflight-bypass-marker-routine-edge-case$`
    - `title == "Preflight bypass (marker)"`
    - `change_reason == "preflight-bypass-authorization"`
    - `json.loads(content)["tier"] == "marker"` AND `json.loads(content)["reason"] == "routine edge case"`
12-14. Lines 2, 3, 5 behavior unchanged (2/3 pass with same canonical source_ref assertion; line 5 denies).
15-17. Empty-reason / non-`-001` path / existing-stem behavior unchanged.
18. Env AND marker both present → pass; two rows logged — env row has `title='Preflight bypass (env)'` and marker row has `title='Preflight bypass (marker)'`; both have `change_reason='preflight-bypass-authorization'`; source_refs differ by tier segment and reason-slug.

Path / integration (2):
19. DB write failure during bypass logging → ALARM + deny.
20. Existing-thread response-file writes pass.

Env-var unset (2):
21. Unset + no marker + no same-turn search → deny.
22. Windows path separators / `NotebookEdit` tool path extraction.

**Cross-contract test (unchanged):**
23. Source-ref validator regression: `tests/test_source_ref_validation.py` gains a positive case confirming the Q3 canonical format `{ts}-preflight-bypass-{tier}-{slug}` passes producer strict-validation. **Total Phase 5 tests: 23.**

**Explicit NON-assertion (per `-008` #1):** none of these tests reference
a `metadata` column, `metadata` kwarg, or `metadata->>` JSON extraction
operator. Any such assertion would be a regression.

**Acceptance:** 23 tests green; scaffold-settings tests updated (§5.11);
managed-artifacts.toml matches.

### 5.6 Phase 6 — Transcript extractor (Q1 = HYBRID)

*(Unchanged from `-007` §5.6 — queue-as-pre-insert-artifact, refusal
contract, execute-summary naming, 13 tests total.)*

### 5.7 Phase 7 — Owner-decision capture hook + GOV-09 capture

*(Unchanged from `-007` §5.7.)*

### 5.8 Phase 8 — Backfill framework generalization

*(Unchanged from `-007` §5.8.)*

### 5.9 Phase 9 — Session wrap gate

*(Unchanged from `-007` §5.9 except A2 query shape.)*

**A1 LO-report coverage:** ALARM on gap.

**A2 Owner-conversation coverage (REVISED per `-008` #1):** ALARM on
owner-conversation coverage gap for the session. Surfaces bypass rows
via the column-based discriminator query:

```sql
SELECT id, version, source_ref, title, session_id, changed_at
FROM current_deliberations
WHERE source_type = 'owner_conversation'
  AND change_reason = 'preflight-bypass-authorization'
  AND session_id = :session_id
ORDER BY changed_at ASC;
```

Rationale for rejecting regex-on-source_ref for this query: regex is
robust against format changes in only one direction (new formats still
match). The `change_reason` column is stable across format revisions
and doesn't rely on string parsing. Either path works against the
current schema; `change_reason` is preferred for clarity and cost.

**A3 Transcript extraction (Q1=HYBRID 5-outcome):** unchanged.
**A4 Redaction re-scan (Q2=WARN-all):** unchanged.
**A5 DB-routing invariant (CI-based):** unchanged from `-007`.

**B1 Bridge-thread coverage:** unchanged.

**Tests (`tests/test_wrap_gate.py`) — 16 total:** test cases referencing
A2 bypass-row surfacing assert:
- The query above returns the expected bypass rows after
  `delib-preflight-gate.py` inserts them.
- Tier discrimination via `title` substring match works: rows where
  `title = 'Preflight bypass (env)'` are Tier A, rows where
  `title = 'Preflight bypass (marker)'` are Tier B.
- No test references `metadata`, `metadata.bypass_tier`, or
  `metadata->>` SQL JSON operators.

### 5.10 Phase 10 — Dogfooding

*(Unchanged from `-007` §5.10.)*

### 5.11 Consolidated final hook / scaffold / managed-artifact surface (REVISED per `-008` #2)

**Scaffold path (unchanged from `-007`):**
- `templates/managed-artifacts.toml` — declarative registry.
- `src/groundtruth_kb/project/scaffold.py` — consumes the registry and
  renders `.claude/settings.json` + copies `.claude/hooks/*.py`.

**Two registry classes are required to produce a working hook
(re-confirmed against `src/groundtruth_kb/project/managed_registry.py:140-156`
and `src/groundtruth_kb/project/scaffold.py:379-406`):**

| Class | Purpose | Where it shows up after scaffold |
|-------|---------|------------------------------------|
| `hook` | Copies `templates/hooks/NAME.py` to `.claude/hooks/NAME.py` | File on disk |
| `settings-hook-registration` | Adds a per-event command entry to `.claude/settings.json` | JSON entry registering the hook with Claude Code |

A `hook` record alone puts the file on disk but Claude Code never runs
it; a `settings-hook-registration` record alone registers a command that
has no file behind it. Both classes are required for every invoked
hook. Helper modules (e.g., `_delib_common.py`) need only a `hook`-class
record since they are imported, not event-bound.

**Records to add (9 total = 5 file records + 4 settings-hook-registration records).**

**File records (5; `class='hook'`):**

| record id | template_path | target_path | initial/managed/doctor profiles | Rationale |
|-----------|---------------|-------------|---------------------------------|-----------|
| `hook._delib-common` | `hooks/_delib_common.py` | `.claude/hooks/_delib_common.py` | `dual-agent`, `dual-agent-webapp` on all three axes | Helper; shared by turn-marker + delib-preflight-gate + others |
| `hook.turn-marker` | `hooks/turn-marker.py` | `.claude/hooks/turn-marker.py` | `dual-agent`, `dual-agent-webapp` on all three axes | UserPromptSubmit; stamps `.groundtruth/current-turn.jsonl` |
| `hook.gov09-capture` | `hooks/gov09-capture.py` | `.claude/hooks/gov09-capture.py` | `dual-agent`, `dual-agent-webapp` on all three axes | UserPromptSubmit; runs after spec-classifier |
| `hook.owner-decision-capture` | `hooks/owner-decision-capture.py` | `.claude/hooks/owner-decision-capture.py` | `dual-agent`, `dual-agent-webapp` on all three axes | PostToolUse; AUQ filter |
| `hook.delib-preflight-gate` | `hooks/delib-preflight-gate.py` | `.claude/hooks/delib-preflight-gate.py` | `dual-agent`, `dual-agent-webapp` on all three axes | PreToolUse; end-of-chain deny-gate |

Each file record carries the standard schema required by
`_CLASS_REQUIRED_KEYS['hook']`: `class`, `id`, `initial_profiles`,
`managed_profiles`, `doctor_required_profiles`, `template_path`,
`target_path`. No `event`, `hook_filename`, or `target_settings_path`
keys (those are forbidden on `hook` records per
`_CLASS_FORBIDDEN_KEYS['hook']`).

**Settings-hook-registration records (4; `class='settings-hook-registration'`):**

Registry order matters: `scaffold._write_settings_json()` groups records
by `event` in registry order and appends each registration to its
event's list in encounter order (`scaffold.py:392-402`). To achieve the
target `.claude/settings.json` ordering per `-007` §5.11, the 4 new
records must be inserted at these positions in
`templates/managed-artifacts.toml`:

| New record | event | Placement in TOML (relative to existing 11 records) |
|------------|-------|-------------------------------------------------------|
| `settings.hook.turn-marker.userpromptsubmit` | UserPromptSubmit | **Before** `settings.hook.delib-search-gate.userpromptsubmit` (turn-marker must run first among UserPromptSubmit hooks) |
| `settings.hook.gov09-capture.userpromptsubmit` | UserPromptSubmit | **Between** `settings.hook.delib-search-gate.userpromptsubmit` and `settings.hook.intake-classifier.userpromptsubmit` (runs after delib-search-gate, before intake-classifier; matches `-007` contract) |
| `settings.hook.owner-decision-capture.posttooluse` | PostToolUse | **Before** `settings.hook.delib-search-tracker.posttooluse` (runs before search-tracker) |
| `settings.hook.delib-preflight-gate.pretooluse` | PreToolUse | **After** `settings.hook.scanner-safe-writer.pretooluse` (appended to tail of existing 6 PreToolUse records) |

Each record carries the standard schema required by
`_CLASS_REQUIRED_KEYS['settings-hook-registration']`: `class`, `id`,
`initial_profiles`, `managed_profiles`, `doctor_required_profiles`,
`event`, `hook_filename`, `target_settings_path=.claude/settings.json`.
No `template_path` or `target_path` keys (those are forbidden on
`settings-hook-registration` records per
`_CLASS_FORBIDDEN_KEYS['settings-hook-registration']`).

**Target rendered `.claude/settings.json` hook ordering** (authoritative
test assertion — see below):

```jsonc
"hooks": {
  "SessionStart": [
    {"hooks": [{"type": "command", "command": "python .claude/hooks/session-start-governance.py"}]},
    {"hooks": [{"type": "command", "command": "python .claude/hooks/assertion-check.py"}]}
  ],
  "UserPromptSubmit": [
    {"hooks": [{"type": "command", "command": "python .claude/hooks/turn-marker.py"}]},          // NEW — first
    {"hooks": [{"type": "command", "command": "python .claude/hooks/delib-search-gate.py"}]},
    {"hooks": [{"type": "command", "command": "python .claude/hooks/gov09-capture.py"}]},         // NEW — after delib-search-gate
    {"hooks": [{"type": "command", "command": "python .claude/hooks/intake-classifier.py"}]}
  ],
  "PostToolUse": [
    {"hooks": [{"type": "command", "command": "python .claude/hooks/owner-decision-capture.py"}]}, // NEW — first
    {"hooks": [{"type": "command", "command": "python .claude/hooks/delib-search-tracker.py"}]}
  ],
  "PreToolUse": [
    /* 6 existing records in current order */,
    {"hooks": [{"type": "command", "command": "python .claude/hooks/delib-preflight-gate.py"}]}   // NEW — tail
  ]
}
```

**Note on `-007` claim re: `spec-classifier.py`:** `-007` §5.11 included
`spec-classifier.py` in the UserPromptSubmit ordering table, but the
current `templates/managed-artifacts.toml` has no
`settings-hook-registration` record for spec-classifier (verified
against lines 290-398 of the file). This means spec-classifier is
already not rendered into the scaffold-generated `.claude/settings.json`
today — independent of this bridge. Changing that is out of scope for
this bridge; this bridge inserts `gov09-capture.py` **after**
`delib-search-gate.py` (the next registered UserPromptSubmit hook), not
after the un-registered `spec-classifier.py`. This preserves the
existing rendered order and closes the ambiguity flagged by `-008` #2.

**Upgrade / doctor enforcement extension:**

Current `src/groundtruth_kb/project/upgrade.py:223-228` enforces
managed-artifact settings for `PreToolUse` only. This bridge extends
enforcement to `UserPromptSubmit` and `PostToolUse`.

Files modified:
- `src/groundtruth_kb/project/upgrade.py` — generalize `_enforce_managed_hooks_in_settings()` or add parallel enforcement functions for UserPromptSubmit + PostToolUse, preserving PreToolUse behavior.
- `src/groundtruth_kb/project/doctor.py` — extend settings-check to report missing/out-of-order entries across all three events.
- `src/groundtruth_kb/project/scaffold.py` — no changes required (already registry-driven; verified against `:379-406`). Touch only if a gap is found.
- `tests/test_upgrade.py` — ~4 new cases for UserPromptSubmit + PostToolUse enforcement.
- `tests/test_doctor.py` — ~4 new cases for UserPromptSubmit + PostToolUse reporting.
- `tests/test_scaffold_settings.py` — **REVISED per `-008` #2:** assertions must verify the **rendered `.claude/settings.json` per-event order** matches the target above (not only file presence). Specifically, at least one test case per event writes settings via `_write_settings_json()` to a tmpdir, reads the JSON, and asserts the `hooks[event]` list matches the target command strings in order. +3 registry-order cases (one per event with new registrations: UserPromptSubmit, PostToolUse, PreToolUse).

### 5.12 Phase 11 — Post-implementation report + Codex VERIFIED

Contract in §7.

---

## 6. Test Inventory Summary (REVISED counts)

| Phase | Test file | New tests in `-009` | Δ vs `-007` |
|-------|-----------|---------------------|-------------|
| 2 | `tests/test_da_db_routing_invariant.py` | ~8 | — |
| 2 | `tests/test_da_residual_rescan.py` | ~4 | — |
| 3 | `tests/test_source_ref_validation.py` | ~13 (was 12+1) | — |
| 3 | `tests/test_cli_deliberations.py` | 0 new | — |
| 4 | `tests/test_lo_report_backfill.py` | 5 | — |
| 5 | `tests/test_delib_preflight_gate.py` | 23 (assertions revised; count unchanged) | — |
| 5+7 | `tests/test_scaffold_settings.py` | **+3 registry-order cases** (rendered settings.json order per event) | **+3** |
| 5+7 | `tests/test_upgrade.py` | ~4 | — |
| 5+7 | `tests/test_doctor.py` | ~4 | — |
| 6 | `tests/test_transcript_extract.py` | 13 | — |
| 7 | `tests/test_owner_decision_capture.py` | 8 | — |
| 8 | `tests/test_backfill_framework.py` | 6 | — |
| 9 | `tests/test_wrap_gate.py` | 16 (A2 query shape revised; count unchanged) | — |
| **Total** | | **~107 new** (was ~104) | **+3** |

All new tests ASCII-only. All new modules mypy --strict clean, ruff
check + format clean. Baseline 1161 stays green.

---

## 7. Post-Impl Report Contract (REVISED per `-008` #1)

Post-implementation report filed to this thread as the next version
(NEW). Contents:

1. **Commit SHA(s)** on `groundtruth-kb` main.
2. **Focused test output** per phase — `pytest -v tests/test_*.py::ClassName::test_node_id` with class-qualified node IDs per `feedback_postimpl_report_hygiene.md`.
3. **Full-suite output** — `pytest` ending in `PASSED` (expected 1161 + ~107 = ~1268).
4. **mypy --strict output** — `Success: no issues found in N source files`.
5. **ruff check + format** — both clean.
6. **DB-routing invariant evidence** — green result of `tests/test_da_db_routing_invariant.py` on the final commit SHA + timestamp. Include path to `.groundtruth/last-ci-routing-result.json` written by CI.
7. **Current DA count evidence (REVISED query shape):**
   - Baseline: `SELECT source_type, COUNT(*) FROM current_deliberations GROUP BY source_type;` against Agent Red `groundtruth.db`.
   - New rows this session: LO-report backfill (~11), AUQ rounds during dogfood, dogfood-run `session_harvest` approvals.
   - Bypass rows emitted by `delib-preflight-gate.py`: query `SELECT id, source_ref, title, session_id FROM current_deliberations WHERE source_type='owner_conversation' AND change_reason='preflight-bypass-authorization';`. No `metadata->>'bypass_tier'` JSON extraction (column does not exist).
8. **Pre-insert and post-insert artifacts:**
   - LO-backfill dry-run JSON: `bridge/gtkb-da-governance-completeness-lo-backfill-dryrun-{YYYY-MM-DD}.json`.
   - Transcript pre-insert dry-run artifact: `.groundtruth/session-extract-queue-{session-id}.jsonl`.
   - Transcript execute summary: `bridge/gtkb-da-governance-completeness-transcript-execute-summary-{YYYY-MM-DD}.json`.
9. **Rendered scaffold-settings evidence (new per `-008` #2):** output of `_write_settings_json()` to a tmpdir in a dogfood test, dumped as JSON, showing the full 4-event matrix with the 4 new registrations in the asserted order.
10. **Dogfood evidence** — `.groundtruth/dogfood-run-{date}.jsonl` + ALARM demonstration.
11. **Rollback instructions** — per phase; all changes reversible via `git revert` + per-phase DA row cleanup script.
12. **Delta summary** — commit-local line counts + range line counts (per `feedback_postimpl_report_hygiene.md`).

---

## 8. Rollback / Containment

*(Unchanged from `-007` §8.)* All reversible via `git revert` on
`groundtruth-kb` main. Bypass DELIB rows use the standard append-only
`insert_deliberation()` path; rollback scripts resolve them via the
`change_reason='preflight-bypass-authorization'` predicate.

---

## 9. Prior Deliberations

Required DA search performed; directly relevant rows (unchanged from
`-007`):

- `DELIB-0715` — MemBase canonical definition.
- `DELIB-0716` / `-0717` / `-0718` — bridge-thread compression examples.
- `DELIB-0719` — S299 owner-decision round.
- `DELIB-0720` / `DELIB-0818` — prior DA rows on this thread.
- `DELIB-0721` / `DELIB-0805` — harvest-coverage bridge-thread rows.
- `DELIB-0817` — S299-continuation meta-summary.
- **`DELIB-0819`** — Phase-0 Q1/Q2/Q3 owner-decision DELIB (authoritative for §3).

No prior deliberation rejected approaches chosen here.

REVISED-4 `-009` differs from `-007` only in:
- §5.5.1 (bypass DELIB storage: no `metadata`; use `change_reason` + `title` + structured `content`)
- §5.5.3 (Phase 5 test assertions revised to drop metadata, add `change_reason`/`title`/`content` checks)
- §5.9 A2 (wrap-gate query uses `change_reason` predicate)
- §5.11 (adds 4 explicit `settings-hook-registration` records with registry placement; tests assert rendered settings.json order)
- §6 (+3 scaffold-settings test cases)
- §7 item 7 (DA count evidence query shape)
- §7 item 9 (rendered settings evidence added)

All other content preserved verbatim from `-007`.

---

## 10. Required Next Steps After Codex GO on This REVISED-4 Bridge

1. **Phase 0 — already satisfied** (DELIB-0819).
2. **Phase 1** — record 8 specs in MemBase citing DELIB-0715/0719/0819.
3. **After Phase 1, in parallel:**
   - Phase 2 — redaction routing invariant + residual rescan.
   - Phase 3 — source-ref warn-only + CLI regression + Q3 canonical-format positive case.
   - Phase 4 (dry-run only) — LO-report coverage + dry-run JSON.
   - Phase 5 — preflight hook (canonical source_ref grammar + `change_reason` discriminator per §5.5.1).
   - Phase 7 — owner-decision capture + GOV-09 capture + upgrade/doctor enforcement extension.
   - Phase 8 — backfill framework.
4. **Phase 6** after Phase 5 `_delib_common.py` helper lands.
5. **Phase 9** after Phases 2/5/6/7 land.
6. **Phase 4 `--execute`** after Phase 8 framework + owner AUQ approval of Phase-4 dry-run JSON.
7. **Phase 6 `--insert-approved`** after queue + review + owner approval of queued candidates; refusal contract enforced.
8. **Phase 10** dogfood run.
9. **Phase 11** post-impl report as the next version (NEW).

---

## 11. Open Questions for Codex

None. Both `-008` blockers are resolved:
- Bypass DELIB contract uses only existing `deliberations` columns and
  existing `insert_deliberation()` parameters, with the discriminator
  carried by `change_reason` (audit query), `title` (tier display), and
  structured `content` JSON (machine-readable detail).
- Scaffold registration explicitly specifies both `hook` file records
  and `settings-hook-registration` records, their registry placement,
  and adds 3 rendered-order test cases that assert the final
  `.claude/settings.json` matrix.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
