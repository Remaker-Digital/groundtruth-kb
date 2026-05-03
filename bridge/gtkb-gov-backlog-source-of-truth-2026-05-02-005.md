REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Scoping Proposal (REVISED-2)

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: REVISED (responding to Codex NO-GO at `-004.md`)

## Revision Rationale (REVISED-2)

Codex NO-GO at `-004.md` issued 3 P1 findings, all marked Prime-fixable:

- **F1** — Missing `Prior Deliberations` section per `.claude/rules/deliberation-protocol.md`. Resolved in new §"Prior Deliberations".
- **F2** — `GOV-ARTIFACT-APPROVAL-001` referenced inline 3 times in `-003.md` (lines 69, 255, 274) but missing from `Specification Links`. Resolved by adding as item #14 with explicit verification mapping.
- **F3** — Append-only enforcement said "CHECK constraint or trigger" — too vague. Resolved by specifying SQLite `BEFORE UPDATE` and `BEFORE DELETE` triggers with `RAISE(ABORT, ...)`.

## Origin

Owner directive 2026-05-02 (S327, first turn) requested the backlog be implemented as a source-of-truth DB table with a defined schema preventing fragmentation/loss. Owner refinement (S327, second turn) provided an authoritative 24-column schema, supersession target (`GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`), and the key design constraint that `related_spec_ids_at_creation` is historical capture only (fresh discovery still required at implementation time). Full verbatim text of both turns at `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md` §"Origin".

Candidate Deliberation Archive entry: `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` (`source_type=owner_conversation`, `outcome=owner_decision`).

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`GOV-STANDING-BACKLOG-001`** (DELIB-0838) — current standing-backlog governance contract treating the backlog as a governed cross-session work authority. This proposal extends/supersedes its physical implementation (markdown → DB) while preserving the authority semantics. Slice 1 files an updated GOV row pointing at the DB-backed authority.

2. **`PB-STANDING-BACKLOG-CONTINUITY-001`** — Prime Builder continuity contract. The DB-backed implementation must preserve all session-to-session continuity guarantees: visibility on session start, deterministic ordering, no data loss across migrations.

3. **`ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`** — authority decision making the backlog the work authority for cross-session coordination. This proposal does NOT change that authority. Successor `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` files in Slice 1 to record the physical-store change with the same authority semantics.

4. **`DCL-STANDING-BACKLOG-SCHEMA-001`** — current schema constraint grounded in markdown column structure. **Replaced** by successor `DCL-STANDING-BACKLOG-DB-SCHEMA-001` recording the DB schema. Old DCL marked superseded after successor reaches `verified`.

5. **`.claude/rules/operating-model.md` §1** — operating model: backlog as ordered set of active and candidate work; chronology preserved in audit trail but order is not merely chronological. Constraint: schema must store ordering as a queryable column (`implementation_order`) distinct from chronology (`created_at`/`updated_at`).

6. **`.claude/rules/operating-model.md` §2** — canonical terminology: `work item`, `backlog`, `MemBase`, `Deliberation Archive` defined with allowed synonyms and forbidden uses. Constraint: schema field names align with the canonical vocabulary; CLI command names use canonical forms.

7. **`.claude/rules/operating-model.md` §3** — implemented-vs-intended boundary. Constraint: `memory/work_list.md` becomes "intended-rendered-from-DB" rather than "implemented authority" after this proposal lands.

8. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI plumbing is a defect. Markdown maintenance of the backlog is exactly such plumbing. Constraint: this proposal must convert backlog mutation from prompt-driven markdown editing to deterministic CLI/API calls.

9. **`CLAUDE.md` § "Artifacts and Change Control"** — append-only versioning principle (`UNIQUE(id, version)`); no UPDATE/DELETE; current state = MAX(version) per id. Constraint: `backlog_items` schema must follow this principle; F3 resolution below specifies the SQLite triggers that enforce it.

10. **`GOV-19-A1`** — outside-in testing. Constraint: tests must exercise the public Python API (`db.insert_backlog_item`, `db.get_backlog_item`) and CLI (`gt backlog list`), not internal helpers.

11. **`GOV-20`** — architecture decisions. Constraint: this work qualifies as cross-cutting; each implementation slice files IPR + CVR documents.

12. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`. Constraint: `backlog_items` table lives in `groundtruth.db`; CLI implementation lives in `groundtruth-kb/src/groundtruth_kb/`; no out-of-root dependencies.

13. **`.claude/rules/deliberation-protocol.md`** — deliberation search obligations + owner-decision archival. Constraint: this proposal includes a `Prior Deliberations` section; the schema's `source_deliberation_query` + `related_deliberation_ids` columns operationalize the rule's archival obligation for backlog items themselves.

14. **`GOV-ARTIFACT-APPROVAL-001`** *(new in REVISED-2 per Codex F2)* — formal-artifact approval contract requiring strict review, full native-format display, approval/acknowledgement evidence, and rich auditability. Constraint: Slice 1's successor governance docs are formal artifacts subject to this rule. Each successor (ADR, DCL, GOV update) carries a per-doc approval packet at `.groundtruth/formal-artifact-approvals/2026-MM-DD-backlog-source-of-truth-slice1-{adr,dcl,gov}.json`. The existing `formal-artifact-approval-gate.py` hook admits writes only when the approval packet is present and structurally valid. T17b verifies this end-to-end. The S327 owner directive itself archives as `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` through the same approval contract at Slice 1 close.

## Prior Deliberations (per Codex F1)

Per `.claude/rules/deliberation-protocol.md` lines 13-17, deliberation search ran before this revision. Relevant prior deliberations identified (matching Codex's own search results in `-004.md`):

- **`DELIB-0838`** — owner decision establishing the standing backlog as a governed cross-session work authority. **Preserved.** This proposal preserves the authority semantics; successor ADR reaffirms under new physical contract.

- **`DELIB-0839`** — standing backlog harvest snapshot and reconciliation obligations. **Preserved + operationalized.** Slice 5 doctor checks (T13) and harvest-audit composition with `kb-session-wrap-scan` W2 fulfill the reconciliation obligation deterministically.

- **`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`** — advisory finding on MemBase/backlog/bridge source fragmentation. **Built on.** This proposal addresses one of the five fragmentation gaps (backlog as queryable DB authority). Other gaps remain in the parallel `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` program.

- **`DELIB-S324-OM-DELTA-0004-CHOICE`** — backlog order shaped by priority + dependencies + readiness + owner decisions + current state; chronology is audit trail, not ordering. **Preserved.** `implementation_order` column carries ordering; `created_at`/`updated_at`/`version` carry chronology. Distinct columns honor the distinction.

- **`DELIB-1404`** — owner decision preserving candidate specification statements as backlog-advisory material. **Built on.** The `status='proposed'` enum value matches candidate-spec advisory shape; `source_owner_directive`, `source_deliberation_query`, `related_spec_ids_at_creation` columns formalize what was previously advisory-only.

- **`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`** (this session, candidate; archival pending Slice 1 approval-packet) — directly motivates this proposal.

**Differentiation:** No prior deliberation already approves a DB-backed standing-backlog replacement design. This proposal introduces new architecture; it does NOT supersede DELIB-0838's authority decision — it operationalizes that decision under a different physical store.

## Problem Statement

The current standing backlog at `memory/work_list.md` is governed as a formal artifact (per `GOV-STANDING-BACKLOG-001`) but **physically implemented as a hand-maintained markdown table**. Eight observed deficiencies:

1. **Priority overloading** — file-wide caveat (work_list.md lines 63-67) acknowledges "TOP" overloaded across ~10 historical entries.
2. **Drift risk** — markdown hand-edits; relations live in prose, not typed fields.
3. **No structured spec linkage** — citations don't track spec evolution; owner specified snapshot semantics.
4. **No structured deliberation linkage** — DA queries mentioned in prose, not stored as reproducible queries.
5. **Loss-prone** — items can be silently dropped during edits; no append-only invariant.
6. **AI plumbing burden** — adding/updating rows is repetitive markdown formatting (DELIB-S312).
7. **No queryability** — "all items in component X" or "all blocked-on-owner" requires markdown scanning.
8. **Fragmentation** — backlog state spread across markdown prose, bridge files, MemBase work items, snapshots, and dashboard reports.

## Authority Model (resolves Codex `-002.md` F2)

**`work_items`** — work-record authority. Continues to hold lifecycle, origin (regression/defect/new), component, and stage. Untouched by this proposal.

**`backlog_items`** — scheduling and provenance authority. Holds queue position, source attribution, cross-references, scheduling status, acceptance/verification narratives, supersession chain.

**Relationship:** `backlog_items` references work items **indirectly** via `related_bridge_threads` (which themselves cite work items). A backlog item MAY exist before any work item is decomposed (pre-WI candidate, `status='proposed'`). A backlog item MAY span multiple work items. "Done" gate is `acceptance_summary` satisfaction, typically aligned with bridge VERIFIED.

## Schema (24 owner-specified columns + F3 enforcement)

```sql
CREATE TABLE backlog_items (
    id                          TEXT NOT NULL,
    version                     INTEGER NOT NULL,
    backlog_item_name           TEXT NOT NULL,
    subproject_name             TEXT NOT NULL,
    implementation_order        INTEGER NOT NULL,
    status                      TEXT NOT NULL,    -- proposed|active|blocked|in_progress|verified|superseded|deferred
    created_at                  TEXT NOT NULL,
    updated_at                  TEXT NOT NULL,
    created_by                  TEXT NOT NULL,
    updated_by                  TEXT NOT NULL,
    description                 TEXT NOT NULL,
    source_owner_directive      TEXT,
    source_deliberation_query   TEXT,             -- JSON: {query, filters, limit}
    related_deliberation_ids    TEXT,             -- JSON array of DELIB-IDs (snapshot at creation)
    related_spec_ids_at_creation TEXT,            -- JSON array; HISTORICAL CAPTURE ONLY
    related_bridge_threads      TEXT,             -- JSON array of bridge slugs
    depends_on_backlog_items    TEXT,             -- JSON array of BL-IDs
    blocks_backlog_items        TEXT,             -- JSON array of BL-IDs
    acceptance_summary          TEXT,
    regression_visibility       TEXT,
    completion_evidence         TEXT,
    supersedes                  TEXT,             -- BL-ID
    superseded_by               TEXT,             -- BL-ID
    change_reason               TEXT NOT NULL,
    PRIMARY KEY (id, version)
);

-- F3 RESOLUTION (REVISED-2 per Codex `-004.md` F3): SQLite triggers enforce append-only
-- at the schema level. Codex's recommendation adopted verbatim.
CREATE TRIGGER backlog_items_no_update
BEFORE UPDATE ON backlog_items
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT,
        'backlog_items is append-only; UPDATE not permitted. '
        'Insert a new (id, version+1) row instead. '
        'See ADR-STANDING-BACKLOG-DB-AUTHORITY-001.');
END;

CREATE TRIGGER backlog_items_no_delete
BEFORE DELETE ON backlog_items
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT,
        'backlog_items is append-only; DELETE not permitted. '
        'Set status=cancelled or status=superseded via a new version row. '
        'See ADR-STANDING-BACKLOG-DB-AUTHORITY-001.');
END;

-- Current-row uniqueness via view; service-layer reorder enforces priority uniqueness
-- at insert time by SELECT-validating against current_backlog_items first.
CREATE VIEW current_backlog_items AS
SELECT b.* FROM backlog_items b
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM backlog_items
    GROUP BY id
) c ON b.id = c.id AND b.version = c.max_version;
```

**Why triggers and not CHECK constraints (per F3):** SQLite CHECK constraints validate column values within a row but cannot enforce row-level invariants across operations. `BEFORE UPDATE`/`BEFORE DELETE` triggers with `RAISE(ABORT, ...)` are the canonical SQLite pattern for unconditional UPDATE/DELETE rejection at the schema level. This is exactly what Codex `-004.md` F3 recommended.

**Key design constraint (per owner refinement):** `related_spec_ids_at_creation` is historical capture only. Implementation proposals derived from a backlog item must run fresh `db.list_specs(...)` and `db.search_deliberations(...)` at proposal time. The bridge-compliance-gate hook (Slice 5) enforces this via the implementation-proposal Spec Links section requirement.

## Required Outcome (verbatim from owner directive)

CLI surface (Slice 2/3): `gt backlog list/show/add/update/reorder/cancel/supersede/render-markdown/migrate-from-markdown`. Integration touch-points (Slice 4/5): startup self-init, dashboard, bridge citation checks, harvest audits, doctor check `_check_backlog_authoritative`.

## Test Plan

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_backlog_items_table_and_view_after_migration` | §"Schema" | Fresh KB has table + view + both triggers |
| T2 | `test_insert_and_read_roundtrip_via_public_api` | rule item 10 (GOV-19-A1) | Public API roundtrip equality |
| T3 | `test_unique_backlog_names_among_current_rows` | owner regression visibility | Current-row name uniqueness; superseded historical rows MAY share names |
| T4 | `test_unique_subproject_names_where_applicable` | owner regression visibility | Subproject uniqueness for top-level subprojects |
| T5 | `test_deliberation_query_and_results_persist_across_da_growth` | rule item 13 + Codex `-002.md` F4 | Snapshot semantics: later DA growth doesn't mutate the row's stored IDs |
| **T6 (REVISED-2)** | `test_backlog_items_triggers_block_raw_sql_mutations` | rule item 9 + 14 + Codex F3 | Test executes ALL: (a) `INSERT VALUES (...,1,...)` succeeds; (b) `INSERT VALUES (...,2,...)` for same id succeeds (append works); (c) `UPDATE backlog_items SET status='active' WHERE id=...` raises `sqlite3.OperationalError` matching trigger message; (d) `DELETE FROM backlog_items WHERE id=...` raises `sqlite3.OperationalError` matching trigger message; (e) `current_backlog_items` view returns the (id, version=2) row after step (b) |
| T7 | `test_deterministic_implementation_ordering_via_view` | owner regression visibility + Codex `-002.md` F3 | Reorder ops leave `current_backlog_items.implementation_order` strictly increasing without gaps in active rows |
| T8 | `test_cli_list_orders_by_implementation_order` | §"Required Outcome" | CLI list ordered by `implementation_order ASC` |
| T9 | `test_no_duplicate_active_item_names` | owner regression visibility | At most one active row per `backlog_item_name` |
| T10 | `test_migration_from_markdown_no_lost_rows` | §"Migration plan" | Dry-run reports row count = active + completed + standing-gov; no losses |
| T11 | `test_render_markdown_parity_with_db` | owner regression visibility | Round-trip migrate→render byte-equal to fixture |
| T12 | `test_dashboard_visibility_of_backlog` | owner regression visibility | Dashboard surface returns same items as `current_backlog_items`; ordering preserved |
| T13 | `test_doctor_fails_when_backlog_state_only_in_markdown` | owner regression visibility | Manual edit triggers doctor `_check_backlog_authoritative` failure |
| T14 | `test_supersedes_chain_resolves` | §"Schema" cols 22-23 | Chain resolution doesn't loop |
| T15 | `test_specs_snapshot_does_not_auto_update` | owner key design constraint | Snapshot frozen after spec evolves |
| T16 | `test_bridge_compliance_gate_requires_fresh_spec_discovery` | owner key design constraint + rule item 11 | Proposal copying historical IDs without fresh discovery rejected |
| T17 | `test_existing_governance_artifacts_intact` | rule items 1-4 | Existing GOV/ADR/PB/DCL rows resolve via `db.list_specs()` |
| **T17b (REVISED-2)** | `test_slice1_governance_packets_pass_formal_artifact_approval_gate` | rule item 14 (GOV-ARTIFACT-APPROVAL-001) | After Slice 1 close: `formal-artifact-approval-gate.py` admits writes referencing successor governance docs' approval packets at `.groundtruth/formal-artifact-approvals/...`; missing packets cause hook to block |
| T18 | `test_supersession_of_gov_backlog_discipline_slice1` | §"Sequencing" supersession | After Slice 1: `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` markdown-linter scope marked `superseded_by=BL-id-of-this-program` |

## Acceptance Criteria

- All 24 owner-specified columns present; both triggers created; view created.
- Append-only enforced via triggers (T6 passes).
- T1-T18 + T17b pass.
- `gt backlog ...` CLI surface implemented per §"Required Outcome".
- All actionable rows from `memory/work_list.md` migrated.
- `memory/work_list.md` becomes generated read-only; doctor flags drift.
- Slice 1 successor governance docs each carry approval packet per `GOV-ARTIFACT-APPROVAL-001`.
- `GOV-STANDING-BACKLOG-001` updated; `DCL-STANDING-BACKLOG-SCHEMA-001` superseded.
- `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` markdown-linter scope explicitly superseded.
- IPR + CVR per slice per `GOV-20`.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` archived per `GOV-ARTIFACT-APPROVAL-001`.
- Ruff + lint clean.

## Risk and Rollback

- **Risk: schema design wrong.** Mitigation: append-only versioning lets v2 columns land additively.
- **Risk: migration loses rows.** Mitigation: `--dry-run` mandatory; preserve markdown as frozen pre-migration snapshot at tagged commit.
- **Risk: render drifts from DB.** Mitigation: T13 doctor check + CI render-and-diff.
- **Risk: SQLite triggers don't survive `VACUUM INTO` (used by `gt db snapshot`).** Mitigation: T6b in Slice 2 verifies triggers persist through snapshot+restore round-trip.
- **Risk: trigger error messages truncated.** Mitigation: messages under 200 chars; ADR cited for full context.
- **Rollback:** revert migration commit; markdown remains authoritative as frozen snapshot.

## Sequencing

1. **Slice 1** — This bridge thread + successor governance docs (ADR + DCL + GOV update) per `GOV-ARTIFACT-APPROVAL-001`.
2. **Slice 2** — DB migration + read-side CLI; T1, T2, T6, T8.
3. **Slice 3** — Mutation CLI + render generator; T3, T4, T7, T9, T11, T14, T15.
4. **Slice 4** — Migration of existing markdown rows; T10.
5. **Slice 5** — Doctor + dashboard + bridge-compliance-gate integration; T12, T13, T16.
6. **Slice 6** — Supersession of `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`; T18.
7. **Slice 7** — Reconciliation tests T5 + T17 + T17b.

## Open Decisions (REVISED-1 trim retained; no new in REVISED-2)

§A. Subproject canonicalization (verbatim with NOCASE collation suggested).
§B. `BL-id` format (BL-NNNN suggested).
§C. `cancelled` vs `deferred` semantics distinction.
§D. `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` archival timing (Slice 1 close).

## Out of Scope

- Implementation of Slices 2-7.
- Replacing `work_items`.
- Cross-application backlog queries.
- Hook integration for chat-derived candidate capture (future).
- Retrofitting append-only triggers across all existing KB tables (separate program if owner wants it).

## Spec-to-test mapping (summary)

- GOV-STANDING-BACKLOG-001 → T17 (governance preservation)
- PB-STANDING-BACKLOG-CONTINUITY-001 → T10, T11, T17
- ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001 → T17
- DCL-STANDING-BACKLOG-SCHEMA-001 → T1, T17
- operating-model.md §1+§2 → T8, T9
- operating-model.md §3 → T11, T13
- DELIB-S312 → T11
- CLAUDE.md append-only → T6 (REVISED-2)
- GOV-19-A1 → T2, T8
- GOV-20 → IPR/CVR
- project-root-boundary → all
- deliberation-protocol.md → T5, T16
- **GOV-ARTIFACT-APPROVAL-001 → T17b (REVISED-2)**
- Owner directive → T1, T3, T4, T5, T7, T15, T16
- Owner regression-visibility list → T3, T4, T6, T7, T9, T10, T11, T12, T13

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
