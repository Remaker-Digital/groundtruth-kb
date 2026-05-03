NEW

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Scoping Proposal

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: NEW (scoping; owner-directed)

## Origin

Owner directive 2026-05-02 (S327), verbatim:

> The "backlog" is not adequately formal. The backlog should be implemented as a source-of-truth database table, with a defined schema that contains information about: the unique name of the backlog item, the unique name of the sub-project it belongs to, the date/time it was created, the date/time it was last updated, the long-form textual description of the work item's relevance and intent, the related deliberations (deliberation archive query), the related specifications (those known at the time the backlog item was created, not necessarily all the specifications which apply when the implementation proposal is created/reviewed), implementation order priority (all backlog items are implemented sequentially, so the priority is the presumed sequential position of the implementation in the continuing series that is the backlog), and any other attributes which GTKB requires (you decide).
>
> Please propose a new backlog item to clarify and enhance the backlog with a schema update and simplified, track-able use of the backlog that prevents fragmentation or loss of backlog items over time.

This directive is itself a candidate Deliberation Archive entry: `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` (`source_type=owner_conversation`, `outcome=owner_decision`). Recording deferred to follow-on per `GOV-ARTIFACT-APPROVAL-001` formal-approval contract.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`GOV-STANDING-BACKLOG-001`** (DELIB-0838) — current standing-backlog governance contract; this proposal extends/supersedes its physical implementation while preserving its authority semantics. KB row.
2. **`PB-STANDING-BACKLOG-CONTINUITY-001`** — Prime Builder continuity contract for the standing backlog; the DB-backed implementation must preserve all continuity guarantees.
3. **`ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`** — authority decision; this proposal does NOT change the *authority* (backlog remains the work authority) but DOES change the *physical store*. Likely supersedes with a successor ADR.
4. **`DCL-STANDING-BACKLOG-SCHEMA-001`** — current schema constraint; will be **replaced** by a successor DCL grounding the constraint on the DB schema rather than markdown columns.
5. **`.claude/rules/operating-model.md` §1** — operating model: backlog as ordered set of active and candidate work; chronology preserved in audit trail but order is not merely chronological.
6. **`.claude/rules/operating-model.md` §2** — canonical terminology: `work item`, `backlog`, `MemBase`, `Deliberation Archive`. The proposal uses these terms canonically.
7. **`.claude/rules/operating-model.md` §3** — implemented-vs-intended: `memory/work_list.md` is currently the implemented standing backlog per `GOV-STANDING-BACKLOG-001`; this proposal moves it to "intended-but-partial" until DB-backed implementation lands.
8. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI-mediated plumbing is a defect; markdown maintenance of the backlog is exactly such plumbing. Aligns with the deterministic-services bias.
9. **`CLAUDE.md` § "Artifacts and Change Control"** — 9 managed artifact types in MemBase; the current `work_items` table is one of them. The proposal must cleanly extend or coexist with `work_items`, not duplicate it.
10. **`GOV-19-A1`** — outside-in testing; tests must exercise the public API (`db.insert_backlog_item`, `gt backlog ...` CLI), not just internal helpers.
11. **`GOV-20`** — architecture decisions; this work qualifies as cross-cutting and requires IPR/CVR documents per slice.
12. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`; the new DB columns + tables live in `groundtruth.db` per the existing root-binding contract; CLI implementation lives in `groundtruth-kb/src/groundtruth_kb/`.

## Problem Statement

The current standing backlog at `memory/work_list.md` is governed as a formal artifact (per `GOV-STANDING-BACKLOG-001`) but **physically implemented as a hand-maintained markdown table**. Observed deficiencies:

1. **Priority overloading** — file-wide caveat (work_list.md lines 63-67) acknowledges "TOP" is overloaded across ~10 historical entries. The 5-row "active" header is the only trustworthy ordering. There is no machine-checkable invariant that priority labels are unique or sequential.
2. **Drift risk** — markdown is hand-edited; rows added in different sessions have different formats; relations between rows (`blocks` / `blocked by`) live in prose, not typed fields.
3. **No structured spec linkage** — when a backlog item references a spec, the link is a markdown citation that doesn't track spec evolution. Owner directive: snapshot the specs *at creation time*, not as a live join.
4. **No structured deliberation linkage** — DA queries are mentioned in prose, not stored as queryable relations.
5. **Loss-prone** — items can be silently dropped during edits; there's no append-only invariant on the backlog itself (only on the artifacts it references).
6. **AI plumbing burden** — adding/updating rows is repetitive markdown formatting; aligns with `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` as a defect surface.
7. **No queryability** — "show all items in component X" or "show all items blocked on owner" requires scanning markdown.

## Proposed Direction (subject to owner + Codex review)

A new MemBase table `backlog_items` with append-only versioning, a `gt backlog` CLI surface, and a generated read-only markdown view that retains the current `memory/work_list.md` path for human consumption but is rendered from the DB. This is a *direction*, not a final design — open decisions in §"Open Decisions" below.

### Schema (owner-required attributes)

The owner-required attributes, with proposed column names and types:

| # | Owner attribute | Proposed column | Type | Notes |
|---|---|---|---|---|
| 1 | unique name of the backlog item | `id` | TEXT (PK) | Format `BL-NNNN` or human-readable slug; uniqueness enforced |
| 2 | unique name of sub-project | `sub_project_id` | TEXT (FK?) | Relates to a sub-project registry — proposed new entity (see Open Decision §A) |
| 3 | date/time created | `created_at` | TEXT (ISO-8601) | Set at insert; never updated |
| 4 | date/time last updated | `updated_at` | TEXT (ISO-8601) | Updated on each new version |
| 5 | long-form description | `description` | TEXT | Markdown-formatted; stored as-is |
| 6 | related deliberations | `related_deliberations` | TEXT (JSON array) | List of DELIB-IDs known at creation; queryable |
| 7 | related specifications (snapshot) | `related_specs_snapshot` | TEXT (JSON array) | List of SPEC/GOV/ADR/DCL IDs **at creation time only** — does NOT auto-update when specs evolve |
| 8 | implementation order priority | `priority` | INTEGER | Sequential position (1, 2, 3, ...); UNIQUE invariant; reorder operations adjust other rows |

### Schema (Prime-proposed additional attributes — owner-decision §B)

| # | Proposed column | Type | Rationale |
|---|---|---|---|
| 9 | `status` | TEXT enum | open / in-progress / blocked / done / cancelled — lifecycle visibility |
| 10 | `origin` | TEXT enum | regression / defect / new — alignment with `work_items` taxonomy in CLAUDE.md |
| 11 | `component` | TEXT | alignment with `work_items` taxonomy |
| 12 | `depends_on` | TEXT (JSON array) | typed relations to other `BL-*` IDs; supersedes prose "blocks/blocked by" |
| 13 | `created_by` | TEXT | provenance (e.g., `prime-builder/claude-code`, `owner-directive/S327`) |
| 14 | `updated_by` | TEXT | provenance for last update |
| 15 | `version` | INTEGER | append-only versioning per KB convention; current state = MAX(version) per ID |
| 16 | `change_reason` | TEXT | why this version exists |
| 17 | `acceptance_criteria` | TEXT | testable "done" conditions; markdown |
| 18 | `cancellation_reason` | TEXT | audit trail for cancelled items; nullable |
| 19 | `session_first_seen` | TEXT | session ID where item first added (e.g., `S327`) |
| 20 | `evidence_links` | TEXT (JSON array) | URLs/paths to supporting artifacts (LO reports, prior bridges, dashboard rows) |
| 21 | `expected_envelope` | TEXT | rough scope estimate (e.g., "~200 LOC + 10 tests"); narrative-only, not enforced |

These additional attributes are **proposed**, not assumed. Owner approves or removes per Open Decision §B.

### CLI surface (Prime-proposed; owner-decision §C)

```
gt backlog list [--status=...] [--component=...] [--blocked-on-owner]
gt backlog show <BL-id>
gt backlog add <id> --description=... --priority=... [--related-specs=...] [--related-delibs=...]
gt backlog update <BL-id> --status=... [--reason=...]
gt backlog reprioritize <BL-id> --to=<position>
gt backlog cancel <BL-id> --reason=...
gt backlog render-markdown [--out=memory/work_list.md]   # Generator for the markdown view
gt backlog migrate-from-markdown [--dry-run]              # One-shot migration tool
```

### Markdown view (Prime-proposed; owner-decision §D)

`memory/work_list.md` retained as a **generated read-only artifact** rendered from the DB. Header notes "GENERATED — do not edit; use `gt backlog ...`." A doctor check flags any drift between the rendered file and the DB authority. This preserves muscle memory + human readability while moving authority to DB.

Alternative: retire `memory/work_list.md` entirely; humans use `gt backlog list`. (Less preferred — the markdown view is currently embedded in startup discovery, hooks, and tests.)

### Migration plan (open-decision §E)

The current `memory/work_list.md` has ~26 active rows + a "Completed" section + standing-governance items (`GTKB-GOV-001..010`) listed below. Migration steps:

1. Define stable BL-IDs for each row (heuristic: slug from existing row identifier — e.g., row 5 `GTKB-GOV-PROPOSAL-STANDARDS Slice 1` → `BL-GOV-PROPOSAL-STANDARDS-SLICE-1`).
2. Parse markdown columns into DB row inserts via `gt backlog migrate-from-markdown`.
3. Preserve original row text in `description` field verbatim.
4. Preserve current ordering as `priority` 1..N.
5. Capture migration as a single Deliberation Archive entry citing the migration commit + the row→ID mapping.
6. After migration VERIFIED: regenerate `memory/work_list.md` from the DB; commit the regenerated version.

### Test plan

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate, tests derive from the linked specs:

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_backlog_items_table_exists_after_migration` | this proposal §"Schema" | Fresh KB has `backlog_items` table with all owner-required + Prime-proposed columns |
| T2 | `test_insert_and_read_roundtrip` | GOV-19-A1 (outside-in) | `db.insert_backlog_item(...)` + `db.get_backlog_item(id)` returns equal row |
| T3 | `test_priority_uniqueness_invariant` | this proposal §"Schema" attr 8 | Inserting two items with same priority raises; reprioritize cascades correctly |
| T4 | `test_specs_snapshot_immutability` | owner directive (verbatim) | After insert, mutating a referenced spec does NOT change `related_specs_snapshot` |
| T5 | `test_deliberation_linkage_query` | `.claude/rules/deliberation-protocol.md` | `gt backlog show <id>` resolves DELIB-IDs to real DA rows |
| T6 | `test_append_only_invariant` | KB convention | UPDATE attempts via raw SQL fail; new versions append; current state = MAX(version) per ID |
| T7 | `test_cli_list_orders_by_priority` | this proposal §"CLI surface" | `gt backlog list` output strictly priority-ordered |
| T8 | `test_markdown_render_matches_db` | this proposal §"Markdown view" | `gt backlog render-markdown` output diff-equal to a known fixture rendered from a known DB state |
| T9 | `test_migration_preserves_all_rows` | this proposal §"Migration plan" | `gt backlog migrate-from-markdown --dry-run` against current `memory/work_list.md` reports 26 rows + "Completed" section + standing-gov section, no losses |
| T10 | `test_doctor_flags_drift_between_render_and_db` | this proposal §"Markdown view" | Manual edit to rendered `memory/work_list.md` triggers a doctor warning |
| T11 | `test_regression_existing_governance_artifacts_intact` | `GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` | After landing, the existing GOV/ADR/PB/DCL rows referenced in `acting-prime-builder.md` still resolve via the KB query path |

### Acceptance criteria

- New `backlog_items` table created in `groundtruth.db` via DB migration with all required + Prime-proposed columns (after owner trim per Open Decision §B).
- Append-only versioning enforced.
- T1-T11 pass.
- `gt backlog ...` CLI surface implemented per Open Decision §C.
- Existing 26 markdown rows + "Completed" section migrated; `gt backlog list` reproduces them in priority order.
- `memory/work_list.md` becomes a generated read-only view; doctor flags drift.
- Successor `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` and successor `DCL-STANDING-BACKLOG-DB-SCHEMA-001` recorded in MemBase, superseding the markdown-era versions; supersession is owner-approved per `GOV-ARTIFACT-APPROVAL-001`.
- `GOV-STANDING-BACKLOG-001` updated to point at the DB-backed authority (semantic preservation; physical-store change).
- IPR + CVR documents per implementing slice.
- Ruff + lint clean on all touched files.

### Risk and rollback

- **Risk: schema design wrong; rework cost.** Mitigation: append-only versioning lets v2 columns land without breaking v1 rows; defer Prime-proposed extras (§B) until empirical need surfaces.
- **Risk: migration loses or corrupts existing rows.** Mitigation: `--dry-run` mode mandatory before live migration; preserve `memory/work_list.md` as a frozen pre-migration snapshot at a tagged commit.
- **Risk: markdown render generator drifts from DB.** Mitigation: doctor check (T10); CI runs the render-and-diff on every commit.
- **Risk: replacing `DCL-STANDING-BACKLOG-SCHEMA-001` invalidates downstream tooling.** Mitigation: successor DCL filed first as `specified`; downstream tooling validated against successor before old DCL is retired.
- **Rollback:** revert migration commit; markdown remains authoritative as a frozen snapshot. Successor ADR/DCL marked `withdrawn` rather than promoted; old GOV/ADR/DCL remain canonical.

### Sequencing (proposed slices)

1. **Slice 1 — Schema design + governance docs.** This bridge thread + successor ADR/DCL/GOV proposals filed and owner-approved. Pre-implementation only.
2. **Slice 2 — DB migration + minimal `gt backlog list`/`show`.** Read-side surface lands; markdown remains hand-maintained.
3. **Slice 3 — Mutation CLI + markdown render generator.** `gt backlog add/update/reprioritize/cancel`; render replaces hand-maintenance.
4. **Slice 4 — Migration of existing 26 rows.** One-shot tooling + commit; markdown becomes generated.
5. **Slice 5 — Doctor check + CI integration.** Drift detection.
6. **Slice 6 (optional/future) — Hook integration: auto-capture from owner prompts.** Composes with `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` row 19 Slices A-D.

## Open Decisions (require owner direction)

§A. **Sub-project registry:** Owner attribute #2 names a "unique sub-project." Is `sub_project` a free-text TEXT column today, or a structured FK to a new `sub_projects` registry? (Free-text is faster; FK gives validation.) Suggest free-text with optional registry promotion in a later slice.

§B. **Prime-proposed extra columns (§"Schema additional attributes"):** Approve all? Trim to essentials (status / origin / depends_on / version + change_reason)? Defer all to later slices?

§C. **CLI command set:** Approve the 7-command surface? Trim?

§D. **Markdown view fate:** (i) Generated read-only at `memory/work_list.md`, (ii) Retire `memory/work_list.md` entirely, (iii) Move generated view to a different path (e.g., `memory/backlog-rendered.md`).

§E. **Migration cutover style:** (i) One-shot conversion + commit; (ii) Parallel-run period where DB and markdown both live for N sessions; (iii) Big-bang switch.

§F. **Naming alignment:** Owner attribute #1 calls it a "backlog item." `work_items` already exists in MemBase as a managed artifact type. Are these the same thing under different names, distinct entities, or is `backlog_items` a wrapper around `work_items` adding scheduling metadata? Suggest: distinct table; `backlog_items` reference `work_items` via a typed `work_item_id` column when applicable. But `work_item_id` may be NULL for backlog entries that aren't yet decomposed into work items.

§G. **Priority semantics:** Owner attribute #8 says "all backlog items are implemented sequentially." Strict total order? Or is "blocked" status orthogonal to priority? (Suggest: priority is total order; status conveys whether an item is *eligible* to be picked up. Highest-priority eligible item is "next.")

§H. **Owner directive archival:** Confirm capture of this S327 directive as `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` per `.claude/rules/deliberation-protocol.md` (`source_type=owner_conversation`).

## Out of scope (this proposal)

- Implementation of any of the slices above. This bridge proposes design only; each slice files its own bridge with code + tests.
- Replacing the `work_items` artifact type. The proposal assumes `work_items` continues to exist and `backlog_items` either references or extends it (Open Decision §F).
- Cross-application backlog queries (multi-application MemBase joins). Slice 4+ if owner wants it.
- Sub-project registry beyond free-text capture. Open Decision §A.

## Sequencing

Non-blocking parallel program; can ship in parallel with isolation Phases 4-8. The current `memory/work_list.md` continues to be hand-maintained until Slice 4 cutover.

Composes with:
- **Row 19 `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY`** — chat-to-backlog auto-capture is Slice 6 here, which depends on (or wraps) Recovery Slice B/C work.
- **Row 24 `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`** — independent; both reduce AI plumbing burden but on different surfaces.
- **`GTKB-GOV-BACKLOG-DISCIPLINE`** (referenced in CLAUDE.md but not yet a tracked work_list row) — likely subsumed by this proposal.

## Spec-to-test mapping (summary)

Every linked specification (§"Specification Links") maps to at least one test:

- GOV-STANDING-BACKLOG-001 → T11 (governance preservation)
- PB-STANDING-BACKLOG-CONTINUITY-001 → T9, T11 (continuity through migration)
- ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001 → T11 (authority preservation under successor ADR)
- DCL-STANDING-BACKLOG-SCHEMA-001 → T1, T11 (schema constraint replaced; existing rows survive migration)
- operating-model.md §1 + §2 → T7, T9 (terminology + ordering)
- operating-model.md §3 → T8, T10 (implemented-vs-intended boundary)
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE → T8 (markdown maintenance becomes deterministic)
- CLAUDE.md § Artifacts and Change Control → T1 (managed artifact extension)
- GOV-19-A1 → T2, T7 (outside-in via public API)
- GOV-20 → IPR/CVR per slice (governance artifact compliance)
- project-root-boundary → all slices (no out-of-root dependencies)
- Owner directive (verbatim attributes 1-8) → T1 (column existence), T3 (priority), T4 (snapshot semantics)

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
