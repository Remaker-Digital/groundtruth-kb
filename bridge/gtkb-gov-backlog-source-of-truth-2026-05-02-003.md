REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Scoping Proposal (REVISED-1)

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: REVISED (responding to Codex NO-GO at `-002.md` + owner scope refinement same turn)
Subject: Revised scoping for the formal backlog source-of-truth table.

## Revision Rationale (REVISED-1)

Two simultaneous inputs reshaped this revision:

**(A) Codex NO-GO at `-002.md`** issued 4 blocking findings, all Prime-fixable:

- **F1** — `.claude/rules/deliberation-protocol.md` was missing from `Specification Links`. Added in §"Specification Links" item 13 + mapped to verification.
- **F2** — `work_items`/`backlog_items` identity was unresolved. Resolved in new §"Authority Model" by adopting Codex's defensible default: `work_items` retains work-record authority; `backlog_items` is the scheduling+provenance authority and references work items indirectly via `related_bridge_threads`.
- **F3** — `UNIQUE(implementation_order)` conflicted with append-only versioning. Resolved by enforcing current-row uniqueness via a `current_backlog_items` view + service-layer reorder transactions (matching existing KB pattern at `db.py:224-257` for `current_work_items`).
- **F4** — Owner attribute #6 ("deliberation archive query") loses information when stored only as ID list. Resolved by storing BOTH the query (`source_deliberation_query`) and the result IDs (`related_deliberation_ids`); the row's `created_at` provides search timestamp by transitivity.

**(B) Owner scope refinement (same S327 turn, in response to my self-review and Codex NO-GO)** provided:

- An authoritative 24-column schema (verbatim adopted in §"Schema").
- A priority statement: "high, immediately after the current GTKB-ISOLATION critical path unless owner promotes it above isolation."
- An explicit supersession instruction: "should supersede the current markdown-linter direction in GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1, not create a parallel backlog-governance track."
- A key design constraint: "`related_spec_ids_at_creation` is a historical capture field, not an exhaustive applicability claim. Implementation proposals and reviews must still perform fresh spec/deliberation discovery when the item is actually worked."
- A concrete required-outcome list (creation, update, reorder, list, generated-view commands; migration of `memory/work_list.md`; updates to startup, dashboard, bridge citation checks, harvest audits, doctor checks).
- A regression-visibility list mapping to specific test requirements.

**Material changes from `-001.md`:**

- §"Origin" updated with owner refinement directive (verbatim).
- §"Specification Links" expanded from 12 to 13 items (added deliberation-protocol).
- §"Schema" replaced with the owner's 24-column list as the canonical schema; Prime-proposed extras retained only where required for F3 enforcement (`is_current` derived view) or where owner schema intent requires expansion.
- New §"Authority Model" resolving F2.
- §"Test plan" expanded to address the owner regression-visibility list verbatim + F1/F3/F4 coverage.
- §"Sequencing" updated with explicit supersession of GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1.
- §"Open Decisions" significantly trimmed — most prior open decisions resolved by owner refinement.

## Origin

Owner directive 2026-05-02 (S327, first turn), verbatim:

> The "backlog" is not adequately formal. The backlog should be implemented as a source-of-truth database table, with a defined schema that contains information about: the unique name of the backlog item, the unique name of the sub-project it belongs to, the date/time it was created, the date/time it was last updated, the long-form textual description of the work item's relevance and intent, the related deliberations (deliberation archive query), the related specifications (those known at the time the backlog item was created, not necessarily all the specifications which apply when the implementation proposal is created/reviewed), implementation order priority (all backlog items are implemented sequentially, so the priority is the presumed sequential position of the implementation in the continuing series that is the backlog), and any other attributes which GTKB requires (you decide).
>
> Please propose a new backlog item to clarify and enhance the backlog with a schema update and simplified, track-able use of the backlog that prevents fragmentation or loss of backlog items over time.

Owner refinement (S327, second turn), verbatim:

> Proposed new backlog item:
>
> GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
> Status: proposed; owner-directed; not yet filed as bridge implementation proposal
>
> Priority / implementation order: high, immediately after the current GTKB-ISOLATION critical path unless owner promotes it above isolation. This should supersede the current markdown-linter direction in GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1, not create a parallel backlog-governance track.
>
> Intent: Replace memory/work_list.md as the canonical backlog source of truth with a structured, append-only/versioned MemBase-backed backlog table. Markdown backlog views may remain, but only as generated views or temporary compatibility surfaces. The backlog must become a durable, queryable, ordered implementation queue so items cannot fragment across markdown prose, bridge files, MemBase work items, snapshots, and dashboard reports.
>
> Required schema direction: Add a canonical backlog_items table with at least: [24-column list, see §"Schema" below].
>
> Key design constraint: related_spec_ids_at_creation is a historical capture field, not an exhaustive applicability claim. Implementation proposals and reviews must still perform fresh spec/deliberation discovery when the item is actually worked.
>
> Required outcome: Implement backlog creation, update, reorder, list, and generated-view commands in GT-KB; migrate current actionable memory/work_list.md rows into the new table; update startup, dashboard, bridge citation checks, harvest audits, and doctor checks to read from the table; make manual markdown backlog edits non-authoritative or flagged as drift.
>
> Regression visibility: Tests must prove unique backlog names, unique subproject names where applicable, stable append-only version history, deterministic implementation ordering, no duplicate active item names, no lost migrated rows, generated markdown parity, dashboard visibility, and doctor failure when backlog state exists only in markdown.
>
> Next step: File bridge proposal bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-001.md with this item as the scope, explicitly superseding or absorbing the existing backlog-discipline linter work.

These two directives constitute a candidate Deliberation Archive entry: `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` (`source_type=owner_conversation`, `outcome=owner_decision`). Recording deferred to follow-on per `GOV-ARTIFACT-APPROVAL-001` formal-approval contract; capture it via `gt deliberations record` after Slice 1 ADR/DCL successors are filed.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`GOV-STANDING-BACKLOG-001`** (DELIB-0838) — current standing-backlog governance contract; this proposal extends/supersedes its physical implementation while preserving its authority semantics.
2. **`PB-STANDING-BACKLOG-CONTINUITY-001`** — Prime Builder continuity contract; the DB-backed implementation must preserve all continuity guarantees.
3. **`ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`** — authority decision; this proposal does not change the authority but DOES change the physical store. Successor `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` filed in Slice 1.
4. **`DCL-STANDING-BACKLOG-SCHEMA-001`** — current schema constraint; replaced by successor `DCL-STANDING-BACKLOG-DB-SCHEMA-001` grounding the constraint on the DB schema.
5. **`.claude/rules/operating-model.md` §1** — backlog as ordered set of active and candidate work; chronology preserved in audit trail but order is not merely chronological.
6. **`.claude/rules/operating-model.md` §2** — canonical terminology for `work item`, `backlog`, `MemBase`, `Deliberation Archive`. Used canonically throughout this proposal.
7. **`.claude/rules/operating-model.md` §3** — implemented-vs-intended boundary. After this proposal lands, `memory/work_list.md` becomes "intended-but-rendered" rather than "implemented authority."
8. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI plumbing is a defect; markdown maintenance of the backlog is exactly such plumbing. This proposal is a concrete manifestation of the principle.
9. **`CLAUDE.md` § "Artifacts and Change Control"** — 9 managed artifact types in MemBase. The `work_items` table is one of them; `backlog_items` is a new managed artifact type with a distinct authority scope.
10. **`GOV-19-A1`** — outside-in testing; tests must exercise public API (`db.insert_backlog_item`, `gt backlog ...` CLI), not just internal helpers.
11. **`GOV-20`** — architecture decisions; this work qualifies as cross-cutting and requires IPR/CVR documents per slice.
12. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`; new DB schema lives in `groundtruth.db`; CLI implementation lives in `groundtruth-kb/src/groundtruth_kb/`.
13. **`.claude/rules/deliberation-protocol.md`** *(new in REVISED-1 per Codex F1)* — defines deliberation search obligations before/during proposals and reviews, the owner-decision archival obligation, and the mapping of search results to citations. This proposal's `source_deliberation_query` + `related_deliberation_ids` schema columns operationalize the rule's archival obligation. Constraint: §"Test plan" T5 + T12 verify these columns satisfy the rule's traceability requirement.

## Authority Model (resolves Codex F2)

**`work_items`** — work-record authority. Continues to hold lifecycle, origin (regression/defect/new), component, and stage for the unit of *selectable work* (per `.claude/rules/operating-model.md` §2). Untouched by this proposal.

**`backlog_items`** — scheduling and provenance authority. Holds:
- The ordered queue position (`implementation_order`).
- Source attribution (`source_owner_directive`, `source_deliberation_query`, `related_deliberation_ids`, `related_spec_ids_at_creation`).
- Cross-references to other artifacts (`related_bridge_threads`, `depends_on_backlog_items`, `blocks_backlog_items`).
- Lifecycle in scheduling terms (`status` enum: proposed | active | blocked | in_progress | verified | superseded | deferred).
- Acceptance + verification narratives (`acceptance_summary`, `regression_visibility`, `completion_evidence`).
- Supersession chain (`supersedes`, `superseded_by`).

**Relationship to `work_items`:**

- `backlog_items` references work items **indirectly** via `related_bridge_threads`. Bridge threads in turn cite work items in their proposals/reports per existing convention. This avoids creating a direct FK that would couple the schema to the current `work_items` ID format.
- A backlog item MAY exist before any work item is decomposed (pre-WI candidate). In that case `related_bridge_threads` is empty and `status='proposed'`.
- A backlog item MAY span multiple work items (one backlog item → many work items via many bridge threads).
- A backlog item is "done" when its `acceptance_summary` is met. Typically this maps to one or more bridge threads reaching VERIFIED, but the gate is `acceptance_summary` satisfaction, not bridge state per se.
- The two tables are NOT synchronized automatically; reconciliation is a doctor-check responsibility (Slice 4+).

**Why not extend `work_items`:**

- `work_items` lifecycle is already mature (origin/component/stage; orchestrated via tests, regressions, and assertions). Conflating it with backlog scheduling would expand its surface to cover queue ordering, supersession chains, and DA query provenance — making it harder to reason about either concern.
- The owner schema includes fields (`source_deliberation_query`, `acceptance_summary`, `regression_visibility`, `completion_evidence`) that are scheduling/governance concerns, not work-record concerns.
- A separate table preserves Codex's caution against creating "two competing 'current work' sources" by making the relationship explicit and indirect.

## Problem Statement

The current standing backlog at `memory/work_list.md` is governed as a formal artifact (per `GOV-STANDING-BACKLOG-001`) but **physically implemented as a hand-maintained markdown table**. Observed deficiencies (per owner directive + S319 MemBase-effective-use assessment):

1. **Priority overloading** — file-wide caveat (work_list.md lines 63-67) acknowledges "TOP" is overloaded across ~10 historical entries. The 5-row "active" header is the only trustworthy ordering.
2. **Drift risk** — markdown is hand-edited; rows added in different sessions have different formats; relations live in prose, not typed fields.
3. **No structured spec linkage** — citations don't track spec evolution; owner directive specifies snapshot semantics.
4. **No structured deliberation linkage** — DA queries are mentioned in prose, not stored as reproducible queries.
5. **Loss-prone** — items can be silently dropped during edits; no append-only invariant.
6. **AI plumbing burden** — adding/updating rows is repetitive markdown formatting (DELIB-S312 deterministic-services principle).
7. **No queryability** — "all items in component X" or "all blocked-on-owner" requires markdown scanning.
8. **Fragmentation across surfaces** — backlog state spread across markdown prose, bridge files, MemBase work items, snapshots, and dashboard reports (owner directive: prevent this).

## Schema (owner-specified, REVISED-1)

The canonical `backlog_items` table with **owner-specified 24 columns** verbatim:

```sql
CREATE TABLE backlog_items (
    id                          TEXT NOT NULL,                    -- Stable surrogate ID (e.g., "BL-0001")
    version                     INTEGER NOT NULL,                 -- Append-only; current state = MAX(version) per id
    backlog_item_name           TEXT NOT NULL,                    -- Unique stable backlog item name (human-readable)
    subproject_name             TEXT NOT NULL,                    -- Unique project/subproject identifier
    implementation_order        INTEGER NOT NULL,                 -- Sequential backlog position (current-row uniqueness)
    status                      TEXT NOT NULL,                    -- proposed|active|blocked|in_progress|verified|superseded|deferred
    created_at                  TEXT NOT NULL,                    -- ISO-8601 UTC
    updated_at                  TEXT NOT NULL,                    -- ISO-8601 UTC
    created_by                  TEXT NOT NULL,                    -- Provenance (e.g., "owner-directive/S327")
    updated_by                  TEXT NOT NULL,                    -- Provenance for last update
    description                 TEXT NOT NULL,                    -- Long-form relevance and intent (markdown-formatted)
    source_owner_directive      TEXT,                             -- Nullable owner directive text/reference
    source_deliberation_query   TEXT,                             -- Stored DA query or relation criteria
    related_deliberation_ids    TEXT,                             -- JSON array of DELIB-IDs known at creation
    related_spec_ids_at_creation TEXT,                            -- JSON array of SPEC/GOV/ADR/DCL IDs known at creation; HISTORICAL CAPTURE ONLY
    related_bridge_threads      TEXT,                             -- JSON array of bridge document slugs (indirect work_item linkage)
    depends_on_backlog_items    TEXT,                             -- JSON array of BL-IDs this item depends on
    blocks_backlog_items        TEXT,                             -- JSON array of BL-IDs this item blocks
    acceptance_summary          TEXT,                             -- Testable "done" conditions
    regression_visibility       TEXT,                             -- Required regression coverage narrative
    completion_evidence         TEXT,                             -- Post-VERIFIED evidence pointers
    supersedes                  TEXT,                             -- BL-ID of item this supersedes (if any)
    superseded_by               TEXT,                             -- BL-ID that supersedes this item (if any)
    change_reason               TEXT NOT NULL,                    -- Reason this version was created
    PRIMARY KEY (id, version)
);

-- Codex F3 resolution: current-row uniqueness via view, not base-table UNIQUE.
CREATE VIEW current_backlog_items AS
SELECT b.* FROM backlog_items b
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM backlog_items
    GROUP BY id
) c ON b.id = c.id AND b.version = c.max_version;

-- Service-layer enforcement (validated at insert/reorder via gt backlog CLI):
--   - SELECT COUNT(*) FROM current_backlog_items WHERE implementation_order = ? must be 0 for active items
--   - SELECT COUNT(*) FROM current_backlog_items WHERE backlog_item_name = ? must be 0 for new items
--   - Reorder operations atomic via single transaction (BEGIN; INSERT new versions for affected rows; COMMIT)
```

**Columns 22-24 (`supersedes`/`superseded_by`/`change_reason`)** are append-only history aids consistent with KB convention.

**Field semantics (key design constraint per owner refinement):**

> `related_spec_ids_at_creation` is a historical capture field, not an exhaustive applicability claim. Implementation proposals and reviews must still perform fresh spec/deliberation discovery when the item is actually worked.

Implications for downstream tooling:
- `gt backlog show <id>` displays `related_spec_ids_at_creation` with a banner "Historical capture as of {created_at}; fresh discovery still required at implementation time."
- Bridge proposals derived from a backlog item MUST run fresh `db.list_specs(...)` and `db.search_deliberations(...)` at proposal time. The bridge-compliance-gate hook (Slice 5) enforces this via the implementation-proposal Spec Links section requirement.
- The doctor check for stale backlog items (Slice 5) compares `related_spec_ids_at_creation` to current spec versions and reports drift, but does NOT mutate the historical column.

**`source_deliberation_query` field semantics (Codex F4 resolution):**

- Stores the search string + parameters used to identify related deliberations at backlog-creation time.
- Format: JSON object `{"query": "...", "filters": {...}, "limit": N}` matching `db.search_deliberations()` signature.
- Paired with `related_deliberation_ids` (the result snapshot) and `created_at` (the search timestamp by transitivity). Together these three fields satisfy Codex F4's reconstruction requirement.

## Required Outcome (verbatim from owner directive)

- Implement backlog creation, update, reorder, list, and generated-view commands in GT-KB.
- Migrate current actionable `memory/work_list.md` rows into the new table.
- Update startup, dashboard, bridge citation checks, harvest audits, and doctor checks to read from the table.
- Make manual markdown backlog edits non-authoritative or flagged as drift.

CLI surface (Slice 2/3):

```
gt backlog list [--status=...] [--subproject=...] [--blocked-on-owner]
gt backlog show <BL-id>
gt backlog add --name=<n> --subproject=<sp> --description=<d> [--related-specs=...] [--related-delibs-query=...] [--related-bridge-threads=...] [--source-owner-directive=...]
gt backlog update <BL-id> --status=<s> [--reason=...] [--add-related-bridge-threads=...]
gt backlog reorder <BL-id> --to=<position>
gt backlog cancel <BL-id> --reason=...   # (sets status='deferred'; cancellation is append-only)
gt backlog supersede <BL-id> --by=<new-BL-id> --reason=...
gt backlog render-markdown [--out=memory/work_list.md]   # Generated view per owner directive
gt backlog migrate-from-markdown [--dry-run]              # One-shot migration tool
```

Integration touch-points (Slice 4/5):
- Startup self-init reads `current_backlog_items` instead of parsing `memory/work_list.md`.
- Dashboard project-state surfaces query the table directly.
- Bridge citation checks (bridge-compliance-gate hook) verify proposed bridges cite an existing `BL-id` if claiming to advance a backlog item.
- Harvest audits (kb-session-wrap-scan W2) cross-check that backlog state ↔ MemBase work_items ↔ bridge threads stay reconciled.
- Doctor check `_check_backlog_authoritative` flags any `memory/work_list.md` content that is not byte-equal to `gt backlog render-markdown` output.

## Test Plan (REVISED-1, derived from owner regression-visibility list + Codex findings)

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_backlog_items_table_and_view_after_migration` | this proposal §"Schema" | Fresh KB has `backlog_items` table with all 24 columns + `current_backlog_items` view |
| T2 | `test_insert_and_read_roundtrip_via_public_api` | GOV-19-A1 | `db.insert_backlog_item(...)` + `db.get_backlog_item(id)` returns equal row; tests use the public API not internal helpers |
| T3 | `test_unique_backlog_names_among_current_rows` | owner regression visibility | Inserting a second row with the same `backlog_item_name` while a current row exists raises; superseded historical rows MAY share names |
| T4 | `test_unique_subproject_names_where_applicable` | owner regression visibility | Subproject uniqueness invariants validated for top-level subprojects (canonicalization rule defined in implementation slice) |
| T5 | `test_deliberation_query_and_results_persist_across_da_growth` | rule item 13 (deliberation-protocol) + Codex F4 | Insert backlog item with query Q producing IDs [D1, D2]; later add D3 matching Q to DA; assert backlog row's `source_deliberation_query` = Q AND `related_deliberation_ids` = [D1, D2] (snapshot, not live) |
| T6 | `test_append_only_invariant_for_backlog_items` | KB convention + Codex F3 | Direct SQL UPDATE on backlog_items raises (CHECK constraint or trigger); new versions append; `current_backlog_items` view returns max-version row |
| T7 | `test_deterministic_implementation_ordering_via_view` | owner regression visibility + Codex F3 | Multiple insert/reorder/cancel/supersede operations leave `current_backlog_items.implementation_order` strictly increasing without gaps in active rows; historical rows may have arbitrary historical orders |
| T8 | `test_cli_list_orders_by_implementation_order` | this proposal §"Required Outcome" | `gt backlog list` output strictly ordered by `implementation_order ASC` for current rows; status filter works |
| T9 | `test_no_duplicate_active_item_names` | owner regression visibility | At most one row with `status IN ('active', 'in_progress')` per `backlog_item_name` |
| T10 | `test_migration_from_markdown_no_lost_rows` | owner regression visibility + this proposal §"Migration plan" | `gt backlog migrate-from-markdown --dry-run` against current `memory/work_list.md` reports row count = active + completed + standing-gov; no rows dropped |
| T11 | `test_render_markdown_parity_with_db` | owner regression visibility | `gt backlog render-markdown` output diff-equal to a known fixture rendered from a known DB state; round-trip migrate→render matches input markdown structure |
| T12 | `test_dashboard_visibility_of_backlog` | owner regression visibility | Dashboard project-state surface returns the same items as `current_backlog_items`; ordering preserved |
| T13 | `test_doctor_fails_when_backlog_state_only_in_markdown` | owner regression visibility | Manual edit to rendered `memory/work_list.md` (adding a row not in DB) triggers doctor `_check_backlog_authoritative` failure |
| T14 | `test_supersedes_chain_resolves` | this proposal §"Schema" cols 22-23 | Item A superseded by B; `db.get_backlog_item('A')` shows `superseded_by='B'`; `db.get_backlog_item('B')` shows `supersedes='A'`; chain resolution doesn't loop |
| T15 | `test_specs_snapshot_does_not_auto_update` | owner key design constraint | Insert backlog item referencing SPEC-X v3; later promote SPEC-X to v4; assert `related_spec_ids_at_creation` still references v3 (the spec ID format may include a version suffix per Slice 1 design) |
| T16 | `test_bridge_compliance_gate_requires_fresh_spec_discovery` | owner key design constraint + rule item 11 | A bridge proposal that copies `related_spec_ids_at_creation` directly into its `Specification Links` (without fresh discovery) is rejected by the bridge-compliance-gate hook with a "fresh discovery required at implementation time" message |
| T17 | `test_existing_governance_artifacts_intact` | rule items 1-4 | After landing, the existing `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, `DCL-STANDING-BACKLOG-SCHEMA-001` rows still resolve via `db.list_specs()` |
| T18 | `test_supersession_of_gov_backlog_discipline_slice1` | this proposal §"Sequencing" supersession | After Slice 1 lands, `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`'s markdown-linter scope is marked `superseded_by=BL-id-of-this-program` and excluded from active backlog |

## Acceptance Criteria

- New `backlog_items` table + `current_backlog_items` view created via DB migration with all 24 owner-specified columns.
- Append-only versioning enforced at the schema level (CHECK constraint or trigger preventing UPDATE).
- Current-row uniqueness enforced via service-layer + view combination (Codex F3 resolution).
- T1-T18 pass.
- `gt backlog ...` CLI surface implemented per §"Required Outcome".
- All actionable rows from `memory/work_list.md` migrated; `gt backlog list` reproduces them in implementation_order.
- `memory/work_list.md` becomes a generated read-only view; doctor flags drift.
- Successor `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` and successor `DCL-STANDING-BACKLOG-DB-SCHEMA-001` recorded in MemBase, owner-approved per `GOV-ARTIFACT-APPROVAL-001`.
- `GOV-STANDING-BACKLOG-001` updated to point at DB-backed authority (semantic preservation; physical-store change).
- `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`'s markdown-linter scope explicitly superseded; tracked as a BL-id with `superseded_by` set.
- IPR + CVR documents per implementing slice per `GOV-20`.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` archived.
- Ruff + lint clean on all touched files.

## Risk and Rollback

- **Risk: schema design wrong; rework cost.** Mitigation: append-only versioning lets v2 columns land without breaking v1 rows. The 24-column owner-specified set is the canonical baseline; future extensions add columns, never remove.
- **Risk: migration loses or corrupts existing rows.** Mitigation: `--dry-run` mandatory before live migration; preserve `memory/work_list.md` as a frozen pre-migration snapshot at a tagged commit; T10 + T11 catch losses + drift.
- **Risk: markdown render drifts from DB.** Mitigation: T13 doctor check; CI runs render-and-diff on every commit.
- **Risk: replacing `DCL-STANDING-BACKLOG-SCHEMA-001` invalidates downstream tooling.** Mitigation: successor DCL filed first as `specified`; downstream tooling validated against successor before old DCL is retired (Slice 1 ADR/DCL choreography).
- **Risk: F4 semantics misinterpreted; query format incompatible with DA evolution.** Mitigation: `source_deliberation_query` is JSON, schema-versioned; future DA query evolution adds fields without breaking old queries.
- **Risk: `backlog_items`/`work_items` reconciliation drifts.** Mitigation: doctor check (Slice 5) cross-checks bridge_threads ↔ work_items ↔ backlog_items; harvest audits (Slice 5) flag fragmentation.
- **Rollback:** revert migration commit; markdown remains authoritative as a frozen snapshot. Successor ADR/DCL marked `withdrawn` rather than promoted; old GOV/ADR/DCL remain canonical.

## Sequencing (proposed slices)

1. **Slice 1 — This bridge thread + successor governance docs.** This proposal + `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`, and updated `GOV-STANDING-BACKLOG-001` filed and owner-approved per `GOV-ARTIFACT-APPROVAL-001`. **Pre-implementation only.** This bridge thread is Slice 1 itself; the successor docs are filed as separate formal-artifact-approval packets within the Slice 1 timeframe, NOT as additional bridges.
2. **Slice 2 — DB migration + read-side CLI.** `backlog_items` table + `current_backlog_items` view + `db.insert_backlog_item` / `db.get_backlog_item` / `db.list_backlog_items` Python APIs + `gt backlog list` / `gt backlog show` CLI commands. T1 + T2 + T6 + T8.
3. **Slice 3 — Mutation CLI + render generator.** `gt backlog add/update/reorder/cancel/supersede/render-markdown` + service-layer uniqueness enforcement. T3 + T4 + T7 + T9 + T11 + T14 + T15.
4. **Slice 4 — Migration of existing `memory/work_list.md` rows.** One-shot `gt backlog migrate-from-markdown` + commit; explicit `BL-id` mapping reviewed during dry-run. Existing markdown becomes a frozen snapshot at a tagged commit. T10.
5. **Slice 5 — Doctor + dashboard + bridge-compliance-gate integration.** `_check_backlog_authoritative` doctor check + dashboard surfacing + bridge-compliance-gate enforcement of fresh-discovery semantics. T12 + T13 + T16.
6. **Slice 6 — Supersession of GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1.** Mark the markdown-linter scope as superseded; remove its standalone tracking. T18.
7. **Slice 7 — Deliberation/spec evolution + reconciliation tests.** T5 + T15 + T17 + T18 reconciliation. Captures the key design constraint via runtime tests after the system is live.
8. **(Future, optional) Slice 8 — Hook integration: auto-capture from owner prompts.** Composes with `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` Slices A-D. Not part of this scoping.

## Sequencing — Supersession of GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1

Per owner directive: "should supersede the current markdown-linter direction in GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1, not create a parallel backlog-governance track."

Action: at Slice 1 close, file an explicit `gt backlog supersede` operation (or, pre-Slice-3 when the CLI lands, capture the supersession in `GOV-STANDING-BACKLOG-001`'s update text) marking GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1's markdown-linter scope as `superseded_by=<BL-id-of-this-program>`. Any work products of GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1 already on disk are absorbed into Slice 4 migration tooling rather than discarded.

## Open Decisions (REVISED-1: significantly trimmed)

§A. **Subproject canonicalization:** Owner schema lists `subproject_name` as "unique project/subproject identifier." For uniqueness, do we need a normalization rule (lowercase, underscores) or accept verbatim? Suggest: verbatim with NOCASE collation; doctor check warns on near-duplicates.

§B. **`BL-id` format:** `BL-NNNN` sequential vs. content-derived slug (e.g., `BL-FORMAL-BACKLOG-DB-SCHEMA`)? Suggest: `BL-NNNN` for stability; `backlog_item_name` carries the human-readable identifier.

§C. **`status='deferred'` semantics:** Is `cancel` an alias for `status='deferred'`, or do we need both `deferred` (paused, may resume) and `cancelled` (terminal)? Suggest: defer this to Slice 3 design; not blocking for Slice 1 schema approval.

§D. **`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` archival:** Confirm capture per `.claude/rules/deliberation-protocol.md`. Recommendation: archive at Slice 1 close as part of the formal-artifact-approval packet, not now (avoids racing with Slice 1's other governance writes).

All prior `-001.md` Open Decisions §A-§H are now resolved by owner refinement except those listed above.

## Out of scope (this proposal)

- Implementation of Slices 2-8 (each files its own bridge with code + tests).
- Replacing the `work_items` artifact type. `work_items` continues to exist; `backlog_items` references it indirectly via `related_bridge_threads` (per §"Authority Model").
- Cross-application backlog queries (multi-application MemBase joins). Future slice if owner wants it.
- Hook integration for chat-derived backlog candidate capture (Slice 8 future).

## Spec-to-test mapping (summary)

Every linked specification (§"Specification Links") maps to at least one test:

- GOV-STANDING-BACKLOG-001 → T17 (governance preservation)
- PB-STANDING-BACKLOG-CONTINUITY-001 → T10, T11, T17 (continuity through migration)
- ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001 → T17 (authority preservation under successor ADR)
- DCL-STANDING-BACKLOG-SCHEMA-001 → T1, T17 (successor schema; existing rows survive migration)
- operating-model.md §1 + §2 → T8, T9 (terminology + ordering)
- operating-model.md §3 → T11, T13 (implemented-vs-intended boundary)
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE → T11 (markdown maintenance becomes deterministic)
- CLAUDE.md § Artifacts and Change Control → T1 (managed artifact extension)
- GOV-19-A1 → T2, T8 (outside-in via public API)
- GOV-20 → IPR/CVR per slice
- project-root-boundary → all slices (no out-of-root dependencies)
- **deliberation-protocol.md → T5, T16 (deliberation-query + ID snapshot persistence; fresh-discovery enforcement)** *(new in REVISED-1)*
- Owner directive verbatim attributes → T1 (column existence), T3 (uniqueness), T4 (subproject uniqueness), T5 (DA query+IDs), T7 (priority), T15 (snapshot semantics), T16 (key design constraint)
- Owner regression-visibility list → T3, T4, T6, T7, T9, T10, T11, T12, T13 verbatim mappings

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
