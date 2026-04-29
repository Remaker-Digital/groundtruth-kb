REVISED

# GTKB Spec Lifecycle Schema Migration (scoping) — REVISED-1

**Status:** REVISED (REVISED-1; supersedes -001 NO-GO at -002)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex Loyal Opposition NO-GO at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-002.md` identifying three blocking findings (F1: `parent NOT NULL` ordering; F2: governance backfill silent misclassification; F3: non-protocol bridge timestamp dependency).

This REVISED-1 addresses each of F1-F3 with surgical changes and preserves the rest of the -001 proposal substance. Sections unchanged from -001 are summarized; changed sections are presented in full.

bridge_kind: scoping_proposal
work_item_ids: [GTKB-SPEC-LIFECYCLE-SCHEMA-MIGRATION]
spec_ids: [SPEC-PROJECT-DASHBOARD-KPI-LINK-001]
target_project: groundtruth-kb
implementation_scope: schema_migration
requires_review: true
requires_verification: true

---

## Specification Links

(Unchanged from -001 §Specification Links.) Owner directives, governance specs, adjacent threads, and rule files all carry forward. Plus this revision adds:

- **`.claude/rules/file-bridge-protocol.md` lines 68-93** — explicitly cited as the authority that defines bridge protocol; F3 fix derives the timestamp source from KB-side records, not from a non-existent bridge field.

## Prior Deliberations

(Unchanged from -001 §Prior Deliberations.) Plus this revision:
- **`bridge/gtkb-spec-lifecycle-schema-2026-04-29-002.md`** (Codex NO-GO; recovered in commit `c8bfcd0e`) — substance basis for this REVISED-1.

---

## Change Log Vs -001

This REVISED-1 makes the following substantive changes:

| Change | Driving finding | Section |
|--------|-----------------|---------|
| `parent` column added as **nullable** in Slice 1; new Slice 1.5 enforces NOT NULL via table rebuild after backfill | F1 | §2.1, §2.1.5 |
| Backfill rules replaced with **conflict-aware classifier** + mandatory dry-run report + owner-review triage as the default for ambiguous specs | F2 | §2.4, §3.1 |
| `implementation_verified_at` backfill **timestamp authority defined** (`deliberation.changed_at` for the bridge thread's harvested deliberation; git commit timestamp as fallback; documented unknowable case) | F3 | §3.1 |
| Acceptance criterion #14 strengthened with **explicit fixture-test pair** for GOV-FILE-BRIDGE-AUTHORITY-001 (`gtkb`) vs GOV-ARTIFACT-APPROVAL-001 (`all`) | F2 | §4 |
| Slice 1 implementation bridge **MUST test against a populated fixture** (not only an empty schema) | F1 | §2.1, §9 |

Sections 1, 5, 6, 7, 9, 10 (parts), 11, 12, 13 are otherwise unchanged from -001.

---

## 1. Problem Statement

(Unchanged from -001 §1.) Live data scope: 2,181 specs, 1,588 implemented, 339 verified, 202 retired, 52 specified, 76 stated authority, 365 non-null priority. Owner-defined target model uses date-bearing lifecycle facts plus relationship table for deliberation sources; owner addition requires `parent` attribute (`gtkb` / `application` / `all`) on every spec.

---

## 2. Recovery Program Structure (Six → Seven Slices)

This REVISED-1 splits the original Slice 1 into Slice 1 (nullable `parent` + new columns + table) and a new Slice 1.5 (`parent` NOT NULL enforcement after backfill). All other slices renumbered are unchanged in scope (Slice 2-6 from -001 become Slice 2-6, slot positions preserved).

### 2.1 Slice 1 — Schema additions (nullable `parent`; new columns + source-link table)

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-1-additions-2026-04-29`

**Deliverable:** add new columns/tables to `current_specifications` schema. `parent` is **nullable** at this stage to make the migration safe against a populated 2,181-row table per F1 fix. Old columns remain in place during compat window.

**New columns on `specifications` table (and `current_specifications` view):**
- `implementation_verified_at TEXT` (nullable; ISO8601 timestamp; only LO can set per Slice 2 gate)
- `retired_at TEXT` (nullable; ISO8601 timestamp; requires owner approval evidence per Slice 2 gate)
- `parent TEXT` (**nullable in Slice 1**; per F1 fix; CHECK constraint and NOT NULL deferred to Slice 1.5; backfill happens between Slice 1 and Slice 1.5)

**New table** (unchanged from -001):
```sql
CREATE TABLE specification_deliberation_sources (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL,
    deliberation_id TEXT NOT NULL,
    source_role TEXT,
    added_at TEXT NOT NULL,
    added_by TEXT NOT NULL,
    UNIQUE(spec_id, spec_version, deliberation_id)
);
```

**Files touched (Slice 1):**
- `groundtruth-kb/src/groundtruth_kb/db.py` — schema additions; nullable `parent` column added.
- `groundtruth-kb/tests/test_db.py` — schema-shape tests; **populated-fixture test** (per F1 required revision: "the first implementation bridge must test against a populated fixture, not only an empty schema") — fixture inserts 50 representative spec rows from real `groundtruth.db` distribution before applying the migration.

**Why first:** every later slice depends on these columns/table existing.

**Does NOT deliver:** `parent` NOT NULL enforcement (Slice 1.5); API write-paths (Slice 2); read-path queries (Slice 3); UI/CLI updates (Slice 5); old-column removal (Slice 6).

### 2.1.5 Slice 1.5 — `parent` NOT NULL enforcement (NEW per F1 fix)

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-1-5-parent-notnull-2026-04-29`

**Deliverable:** after Slice 4 backfill completes, enforce `parent NOT NULL CHECK (parent IN ('gtkb', 'application', 'all'))` via SQLite table rebuild. Verify zero null/ambiguous rows remain before rebuild begins.

**Mechanism (per SQLite NOT NULL addition pattern):**
1. Verify zero null `parent` rows in `current_specifications` (else fail-fast with triage list path).
2. Create new `specifications_new` table with full constraints including `parent NOT NULL CHECK (parent IN ('gtkb', 'application', 'all'))`.
3. `INSERT INTO specifications_new SELECT * FROM specifications` (atomic transaction).
4. Verify row counts match.
5. `DROP TABLE specifications`; `ALTER TABLE specifications_new RENAME TO specifications`.
6. Recreate indexes, triggers, and `current_specifications` view.
7. Atomic `COMMIT`.

**Files touched (Slice 1.5):**
- `groundtruth-kb/src/groundtruth_kb/db.py` — table-rebuild migration.
- `groundtruth-kb/tests/test_db.py` — populated-fixture test verifies the rebuild preserves all rows; pre-rebuild null-check fails when test fixture has null `parent` rows.
- `groundtruth-kb/src/groundtruth_kb/migrations/` (new directory if not present) — explicit migration file `001_parent_notnull.sql` for reproducibility.

**Why between Slice 1 and Slice 2:** per F1 — migrating populated tables to NOT NULL requires the rebuild pattern; it must happen after backfill (Slice 4 phase 3.1 happens before Slice 1.5 in actual deployment order even though slice numbers suggest otherwise — see §5 sequencing fix).

**Does NOT deliver:** API write-paths (Slice 2); reads (Slice 3); etc.

### 2.2 Slice 2 — API additions + lifecycle gates

(Unchanged from -001 §2.2.) New methods: `mark_spec_implementation_verified`, `retire_spec`, `link_spec_deliberation_source`, `set_spec_parent`. Gates: LO authority for verification; owner approval for retirement.

### 2.3 Slice 3 — Read-path migration

(Unchanged from -001 §2.3.) Lifecycle derivation from dates. Update `audit_gtkb_triad_completeness.py` (committed at `73c41ee4`).

### 2.4 Slice 4 — Write-path migration + conflict-aware backfill (REWRITTEN per F2)

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-4-write-paths-2026-04-29`

**Deliverable:** spec creation paths no longer set lifecycle status; deliberation provenance lands in `specification_deliberation_sources`; backfill applies conflict-aware classifier with dry-run + triage rather than broad rules.

**Files touched (Slice 4):** as -001, plus the new backfill mechanism described below.

**Conflict-aware `parent` classifier (REPLACES -001 §2.4 broad rules per F2):**

The classifier is a **two-pass** mechanism with mandatory dry-run output before any mutation:

**Pass 1 — Demonstrably-non-conflicting rules** (auto-classify; emit dry-run report; do NOT mutate yet):
- `id LIKE 'AR-*'` OR `section LIKE 'agent-red-%'` → `parent='application'` (Agent Red is the only current hosted application; these prefixes are unambiguous).
- `id LIKE 'SHOPIFY-*'` OR `id LIKE 'CUSTOMER-*'` → `parent='application'` (application-domain prefixes).
- `id LIKE 'SPEC-INTAKE-*'` AND `section='membase-effective-use'` → `parent='all'` (intake mechanics by design apply to both workspaces; the SPEC-INTAKE-c9e997 / -2485e9 / -3623f1 family).
- `type='protected_behavior'` AND id starts `PB-*` → owner-review triage (PB scope varies; do not auto-classify).

**Pass 2 — Suspicious patterns (route to owner-review triage; do NOT auto-classify):**
- `id LIKE 'GOV-*'` OR `type='governance'` → **owner-review triage** (per F2: GOV-FILE-BRIDGE-AUTHORITY-001 is `gtkb` while GOV-ARTIFACT-APPROVAL-001 is `all`; broad rule unsafe). The classifier writes one triage entry per GOV spec with proposed default + the conflicting evidence, owner reviews and confirms.
- `id LIKE 'ADR-*'` OR `id LIKE 'DCL-*'` OR `type='architecture_decision'` OR `type='design_constraint'` → **owner-review triage** (architecture-decision scope varies by topic).
- `id LIKE 'GTKB-*'` (with no section qualifier) → preliminary `parent='gtkb'` proposed, but routed to owner-review triage for confirmation given the size of this set.
- All other prefixes / no matching pattern → owner-review triage.

**Triage output format:**
- Single file: `memory/triage-spec-parent-backfill.md` (markdown; not formal canonical state).
- Per-spec entry: spec id, current title, current type, current section, proposed `parent`, reason for proposal, evidence-conflict markers if any.
- Owner reviews and confirms each entry; classifier re-runs with confirmed values; final pass mutates the database.

**Mandatory dry-run gate:**
- Slice 4 implementation bridge MUST include a dry-run mode that produces the triage report WITHOUT mutating any rows.
- Owner explicit approval required (formal-artifact-approval packet) before the mutation pass executes.
- Mutation pass is idempotent: re-running on already-classified rows is a no-op.

**Regression-test fixtures (per F2 required revision):**
- `tests/fixtures/spec_parent_backfill_classifier_test_data.json` — includes:
  - `GOV-FILE-BRIDGE-AUTHORITY-001` (expected: triage as `gtkb` candidate; owner confirms `gtkb`)
  - `GOV-ARTIFACT-APPROVAL-001` (expected: triage as `all` candidate; owner confirms `all`)
  - `AR-DASH-001` (expected: auto-classify `application`)
  - `SPEC-INTAKE-c9e997` (expected: auto-classify `all`)
  - `GTKB-COMMIT-TRIAGE-001` (expected: triage as `gtkb` candidate)
- Test asserts: pass-1 auto-classifies the four unambiguous rows; pass-2 routes the GOV-* and GTKB-* rows to triage; classifier produces zero silent misclassifications (acceptance criterion #14).

### 2.5 Slice 5 — UI/CLI/docs migration

(Unchanged from -001 §2.5.)

### 2.6 Slice 6 — Old-column removal (cleanup; final closure)

(Unchanged from -001 §2.6.)

---

## 3. Backfill Strategy Detail (REWRITTEN per F2 + F3)

### 3.1 Phase Sequence (revised per F1 + F3)

The migration script (Slice 4 deliverable) operates in four phases, with explicit timestamp authority and dry-run discipline:

**Phase 3.1.a — Schema additions (Slice 1)**
- Add nullable columns + table per Slice 1.

**Phase 3.1.b — Conflict-aware backfill, dry-run pass (Slice 4 part 1)**
- Run Pass 1 + Pass 2 classifier (per §2.4).
- Emit triage report at `memory/triage-spec-parent-backfill.md`.
- **No database mutation.**

**Phase 3.1.c — Owner triage review (out-of-band)**
- Owner reviews triage report; confirms or revises proposed `parent` values.
- Owner explicit approval packet required before phase 3.1.d.

**Phase 3.1.d — Backfill mutation pass (Slice 4 part 2)**
- Apply classifier with confirmed triage values.
- Set `parent` for all rows.
- Verify zero null `parent` rows.

**Phase 3.1.e — `implementation_verified_at` and `retired_at` backfill (Slice 4 part 3)**
- Per F3 fix: timestamp authority precedence:
  1. **Primary:** for each spec at current `status='verified'`, find the bridge thread that VERIFIED it (cross-reference via spec id mention in bridge files OR via the spec's `source_paths` field). Read the harvested deliberation for that bridge thread (`DELIB-NNNN` from `bridge_thread` source_type) and use its `changed_at` field. **`changed_at` IS defined on KB deliberation rows**, even though it is not defined on bridge files themselves.
  2. **Fallback 1:** if no harvested deliberation exists for the bridge thread, use the `git log -1 --format=%aI -- bridge/<thread>-*.md` of the file with VERIFIED status. Deterministic git timestamp lookup.
  3. **Fallback 2:** if no bridge thread can be linked to the spec at all, leave `implementation_verified_at` NULL and flag the spec for owner review at `memory/triage-spec-implementation-verified-backfill.md`. Do NOT use migration-script execution timestamp as the value (per advisory §Risks: would recreate the flaw the owner is correcting).
- For `retired_at`: same precedence — primary from owner-decision deliberation `changed_at`; fallback 1 from git timestamp of the spec's last-known retirement bridge; fallback 2 to NULL with flag for owner review.
- All ambiguous cases write to triage files (not silent NULL or silent timestamp).

**Phase 3.1.f — `parent` NOT NULL enforcement (Slice 1.5 deployment)**
- Per F1 fix: after phase 3.1.d completes with zero nulls, run Slice 1.5 table rebuild (per §2.1.5 mechanism).

### 3.2 Compat Window (Slices 1-5 Active Simultaneously)

(Unchanged from -001 §3.2.) Old columns remain readable/writable; new columns take precedence in derived queries.

### 3.3 Cleanup (Slice 6)

(Unchanged from -001 §3.3.) Old columns removed from active API; preserved in version-history rows.

---

## 4. Acceptance Criteria (per advisory + REVISED-1 strengthening)

Items #1-#13 unchanged from -001 §4. **Item #14 strengthened per F2:**

14. **(parent-attribute, REVISED per F2)** Backfill rules per §2.4 produce zero silent misclassifications. **Specifically tested:** `GOV-FILE-BRIDGE-AUTHORITY-001` is routed to owner-review triage (proposed `gtkb`; owner confirms); `GOV-ARTIFACT-APPROVAL-001` is routed to owner-review triage (proposed `all`; owner confirms); the classifier never auto-stamps either as `all` or `gtkb` without owner triage. Test fixture: `tests/fixtures/spec_parent_backfill_classifier_test_data.json` (per §2.4).

**New item #15** (per F1 fix):
15. **(slice 1.5 table rebuild)** Slice 1.5 enforcing `parent NOT NULL` happens via SQLite table rebuild (per §2.1.5 mechanism). Test: applying Slice 1.5 against a populated fixture (50+ rows) preserves all rows, all `parent` values, all foreign keys, all indexes; failed transaction (e.g., null `parent` row present) leaves the database unchanged.

**New item #16** (per F3 fix):
16. **(implementation_verified_at timestamp authority)** Backfill never uses migration-script execution timestamp for `implementation_verified_at`. Tests assert: harvested-deliberation `changed_at` used when available; git timestamp used as documented fallback; remaining ambiguous specs are NULL with triage flag (NOT silent or invented timestamps).

---

## 5. Sequencing and Concurrency

(Mostly unchanged from -001 §5.) **REVISED ordering:** Slice 1 → Slice 4 phases 3.1.b through 3.1.e (backfill + triage; owner approval gated) → Slice 1.5 (NOT NULL rebuild after zero-nulls verified) → Slice 2 → Slice 3 → Slice 5 → Slice 6.

**Reason for the reorder:** Slice 1.5's table rebuild requires Slice 4 backfill to have already completed (zero null `parent` rows). This means Slice 4 happens before Slice 1.5 in deployment order, even though Slice 1.5's number suggests otherwise. The slice number is preserved for cross-reference clarity; the deployment order is documented here.

External sequencing constraints: as -001 (active-workspace alignment optional; spec-coverage architecture coordination).

---

## 6. Project Root Boundary

(Unchanged from -001 §6.)

---

## 7. Files Touched (this bridge — scoping only)

(Unchanged from -001 §7.)

---

## 8. Verification Matrix (this scoping bridge)

| Risk | Verification at scoping VERIFIED |
|------|-----------------------------------|
| F1 fix (parent NOT NULL ordering) creates a different unbuildable state | Codex review confirms §2.1 nullable + §2.1.5 rebuild + §5 reordered deployment sequence is buildable. Populated-fixture test (per §2.1) is mandatory at Slice 1 implementation. |
| F2 fix (conflict-aware classifier) over-routes to triage and creates owner overhead | Codex review confirms §2.4 Pass 1 covers demonstrably-non-conflicting rules so AR-* / SHOPIFY-* / CUSTOMER-* / SPEC-INTAKE-* + section-`membase-effective-use` are auto-classified; only ~365 GOV-* + ADR-* + DCL-* + uncategorized specs go to triage. Owner overhead bounded. |
| F3 fix (timestamp authority) silently picks wrong source when fallbacks chain | Codex review confirms §3.1.e precedence is explicit; fallback 2 is "leave NULL + triage" not "use migration timestamp". Tests assert this per acceptance criterion #16. |
| Slice 1.5 table rebuild loses rows | Test asserts row count preserved; transaction rolled back if any check fails; populated-fixture test specifically covers this. |
| Acceptance criterion #14 fixture pair (GOV-FILE-BRIDGE-AUTHORITY-001 vs GOV-ARTIFACT-APPROVAL-001) doesn't actually exercise the classifier conflict | Codex review confirms test fixture in `tests/fixtures/spec_parent_backfill_classifier_test_data.json` includes BOTH rows AND asserts both are routed to triage (not silently auto-classified). |
| Triage file format (`memory/triage-spec-parent-backfill.md`) too informal for a canonical-state-affecting artifact | §2.4 explicitly notes "not formal canonical state"; triage file is a working document; canonical state mutation requires owner approval packet per phase 3.1.c. |
| Slice ordering creates an unbuildable dependency chain | §5 walks the new sequence; Codex review confirms each gate's prereq is achievable from prior-slice outputs alone. |
| Old column removal at Slice 6 breaks audit trail | §3.3 + §2.6 specify append-only schema means version-history rows preserve old-column values. |

---

## 9. Out of Scope

(Mostly unchanged from -001 §9.) Plus:
- The existing harvest of bridge-thread → deliberation links (queried by §3.1.e fallback 1) is assumed available; if it isn't, Slice 4 implementation bridge will need to declare a dependency on `scripts/harvest_session_deliberations.py` or equivalent. Out of scope for this scoping bridge.

---

## 10. `parent` Attribute Detailed Design

(Mostly unchanged from -001 §10.) **Schema correction per F1 fix:**

```sql
-- Slice 1 (initial):
parent TEXT  -- nullable; CHECK constraint deferred to Slice 1.5

-- After Slice 4 backfill + Slice 1.5 rebuild:
parent TEXT NOT NULL CHECK (parent IN ('gtkb', 'application', 'all'))
```

Backfill heuristics (revised per F2): see §2.4 conflict-aware classifier (NOT broad rules from -001 §2.4).

---

## 11. Open Questions for Loyal Opposition Review

(Mostly unchanged from -001 §11.) Plus revised:

1. **(Replaces -001 Q1)** Owner-triage workflow scope. §2.4 + §3.1.c require owner explicit approval for the `parent` backfill mutation. Is the simplest approach a single bulk approval (owner reviews triage report once and approves the whole mutation pass), or per-spec confirmation? Bulk approval is faster but coarser; per-spec is finer but higher friction. Codex preference?

2. (Unchanged from -001 Q2) `set_spec_parent` operation as separate API.

3. (Unchanged from -001 Q3) Deprecation warning channel.

4. **(Replaces -001 Q4)** Triage file format. §2.4 + §3.1 reference `memory/triage-spec-parent-backfill.md` and `memory/triage-spec-implementation-verified-backfill.md`. Markdown owner-readable, but a JSON or KB-table representation might integrate better with future tooling. Codex preference?

5. (Unchanged from -001 Q5) Migration script invocation surface.

6. (Unchanged from -001 Q6) `parent='all'` semantics.

7. (Unchanged from -001 Q7) Slice 6 (removal) timing.

8. **(NEW per F3)** Timestamp authority precedence ordering — should fallback 1 (git timestamp) be preferred over fallback 2 (NULL + triage), OR should the migration always prefer NULL over a synthetic timestamp? §3.1.e proposes git timestamp as the documented fallback before NULL, on the rationale that git history is auditable and reproducible. Codex preference?

---

## 12. Decision Needed From Owner

(Mostly unchanged from -001 §12.) Plus:

3. **(NEW per F3)** Approval of the timestamp authority precedence in §3.1.e. The owner directive says specs at `verified` should be migrated using implementation as reference (DELIB-0707); this revision interprets that as "use the bridge VERIFIED's harvested deliberation timestamp" (primary) with documented fallbacks. If owner intended a different timestamp source, Slice 4 needs to know before backfill executes.

---

## 13. Aligns With

(Unchanged from -001 §13.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
