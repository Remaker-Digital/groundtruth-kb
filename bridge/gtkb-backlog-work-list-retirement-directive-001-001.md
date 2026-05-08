NEW

# Implementation Proposal — GTKB-BACKLOG-WORK-LIST-RETIREMENT-DIRECTIVE-001 (Slice 0 Scoping)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-backlog-work-list-retirement-directive-001`
**Type:** Owner-directive-driven scope correction across canonical artifacts. Slice 0 = scoping; Slice A = narrative artifact updates; Slice B = formal artifact updates (ADR/DCL v2 with approval packets). Implementation requires Codex GO before any artifact mutation.
**Status:** NEW
**Parent thread:** `gtkb-gov-backlog-source-of-truth-2026-05-02` (Slice 1 VERIFIED at -008; Slices 2-7 actionable per [memory/work_list.md:79](memory/work_list.md:79)).

## Claim

The owner directive of 2026-05-08 says "the conclusion of the migration will be the deletion of the markdown file, since it will have no contents." This contradicts the current canonical-artifact text in [.claude/rules/operating-model.md §2](.claude/rules/operating-model.md) and [.claude/rules/canonical-terminology.md:336-354](.claude/rules/canonical-terminology.md:336), both of which state that `memory/work_list.md` persists post-migration as a generated view for human-readable compatibility. The work-item body at [memory/work_list.md:945-950](memory/work_list.md:945) carries the same wording.

This proposal scopes the artifact refresh: capture the owner directive as a Deliberation Archive entry, update the narrative artifacts (Slice A), and refresh the formal ADR/DCL specs via formal-artifact-approval packets (Slice B).

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the test plan below derives from each affected artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`. All artifacts touched by this proposal remain under `E:\GT-KB`; no `applications/Agent_Red/` content is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; backlog, work item, owner decision are referenced as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the change preserves traceability across artifacts, deliberations, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the change refines the verified-state lifecycle of `memory/work_list.md` (it transitions from non-authoritative-view to retired).

**Domain-specific** (governed artifacts being changed):

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v1 — DB-Backed Standing Backlog Authority; needs v2 to reflect deletion endpoint.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v1 — Standing Backlog DB Schema Constraint; may need v2 to add an explicit "no markdown writeback after migration completion" constraint.
- `GOV-STANDING-BACKLOG-001` v2 — currently states the standing backlog is the durable cross-session work authority. The intent is preserved; the implementation surface (markdown vs. table) is what changes. v3 may not be required if the GOV is implementation-agnostic; Slice B will make this call.
- `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (predecessor) — should be marked superseded by `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2.

**Authoring sources to update** (Slice A):

- `.claude/rules/operating-model.md` §2 "backlog" entry — update wording to make deletion the explicit endpoint.
- `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 — update "Source-of-truth intent" line + add a note clarifying the lifecycle endpoint.
- `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH work-item body at line 945 — update "Required behavior" to specify migration-conclusion deletion.

**Bridge / protocol specs** (referenced but not changed):

- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md` — parent thread Slice 1 VERIFIED evidence.

**Governance gates**:

- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for ADR/DCL/GOV mutations.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — chat-derived owner directive must produce owner-visible confirmation; the AUQ in `## Owner Decisions / Input` below satisfies this.

## Owner Decisions / Input

Owner-directive evidence captured this session via AUQ at 2026-05-08:

| Question | Answer |
|---|---|
| Reconcile the conflict between your statement and the canonical artifacts? | "Owner directive supersedes — update artifacts" |

Owner statement preceding the AUQ:

> "The conclusion of the migration will be the deletion of the markdown file, since it will have no contents."

This authorizes:

- Capturing the directive as a Deliberation Archive entry with `source_type=owner_conversation`, `outcome=owner_decision`.
- Filing this NEW scoping proposal.
- Slice A narrative artifact updates and Slice B formal artifact updates pending Codex GO.

No additional owner approval is required to file this NEW. Implementation of Slices A and B requires Codex GO. ADR/DCL formal mutations also require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001` (the AUQ evidence above seeds those packets).

## Conflict Mechanics

Three artifact surfaces currently say `memory/work_list.md` persists post-migration:

[.claude/rules/operating-model.md §2](.claude/rules/operating-model.md):
> Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[.claude/rules/canonical-terminology.md:348-350](.claude/rules/canonical-terminology.md:348):
> Source-of-truth intent: Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[memory/work_list.md:945-950](memory/work_list.md:945):
> Required behavior: `memory/work_list.md` becomes a generated view or temporary compatibility surface. Startup, dashboard, bridge citation checks, standing-backlog harvest, and doctor/readiness checks must read the canonical table. Manual markdown backlog edits should either be rejected, ignored as non-authoritative, or surfaced as drift until migrated through the structured backlog writer.

The owner directive supersedes the "persists as generated view" reading. The operative endpoint is now: **post-migration, the file has no row content, is regenerated empty, then deleted as part of migration completion.**

## Proposed Scope

**Slice A — Deliberation capture + narrative artifact updates:**

- A1. Insert Deliberation Archive entry recording the owner directive (`source_type=owner_conversation`, `outcome=owner_decision`, `session_id=S337`, `decision_summary`: "memory/work_list.md is deleted at migration conclusion, not persisted as a generated view.").
- A2. Update `.claude/rules/operating-model.md` §2 "backlog" entry — replace "generated views ... used only for human-readable compatibility" line with explicit deletion-at-conclusion language.
- A3. Update `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 similarly: replace "Source-of-truth intent" line + add a "Lifecycle endpoint" note specifying `memory/work_list.md` is removed when migration completes.
- A4. Update `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior" section to specify migration-conclusion deletion explicitly. Add a Slice 7-prime or "migration completion" gate description.

**Slice B — Formal artifact updates:**

- B1. File formal-artifact-approval packet for `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 incorporating the deletion endpoint into the consequences section.
- B2. File formal-artifact-approval packet for `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 (if needed) adding a constraint that the migration-completion gate verifies absence of `memory/work_list.md`.
- B3. Decide whether `GOV-STANDING-BACKLOG-001` v3 is needed; the GOV is implementation-agnostic about whether the standing backlog lives in markdown or DB, but if the wording references the markdown file by name, an update is needed.
- B4. Mark predecessor `DCL-STANDING-BACKLOG-SCHEMA-001` as `superseded_by` populated for `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2.

**Out of scope** (deferred to parent thread Slices 2-7):

- DDL migration (Slice 2 of parent).
- CLI mutators (Slice 3).
- Render generator producing `memory/work_list.md` (Slice 4) — generator may still exist temporarily during migration window; this proposal only changes post-completion endpoint.
- Migration-completion gate that physically deletes `memory/work_list.md` (Slice 7-prime; depends on Slices 2-6 landing first).
- Consumer migration (startup, doctor, dashboard, harness scripts) — tracked in parent thread.

## Spec-Derived Test Plan

Slice A tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-deliberation-1 | Deliberation Archive captures owner directive | `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); res=db.search_deliberations('work_list deletion migration conclusion'); print(any('owner_decision' in r.get('outcome','') for r in res))"` returns True |
| T-narrative-1 | operating-model §2 carries deletion endpoint | `grep -c "deleted" .claude/rules/operating-model.md` >= 1 in §2 backlog entry; `grep -c "human-readable compatibility" .claude/rules/operating-model.md` returns 0 in §2 |
| T-narrative-2 | canonical-terminology backlog entry carries deletion endpoint | matching grep checks against the "backlog" section |
| T-narrative-3 | work_list.md work-item body reflects deletion endpoint | `grep "deletion" memory/work_list.md` finds the new "Required behavior" line in GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH |
| T-doctor-1 | Canonical-terminology doctor check still passes | `gt project doctor --check canonical-terminology` returns PASS |
| T-no-formal-leak | No ADR/DCL/GOV mutation attempted in Slice A | git diff `groundtruth.db` shows no `specifications` table changes |
| T-root-boundary | All edits under E:\GT-KB | `git diff --stat` shows only project-root paths (T verifies `ADR-ISOLATION-APPLICATION-PLACEMENT-001`) |

Slice B tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-adr-1 | ADR v2 inserted with formal-approval evidence | `db.list_specs(type='architecture_decision', spec_id='ADR-STANDING-BACKLOG-DB-AUTHORITY-001')` returns version 2 with `change_reason` citing approval packet path |
| T-dcl-1 | DCL v2 inserted (if scoped) | matching list_specs check |
| T-approval-packet-presence | Formal-artifact-approval packet files exist on disk | `ls .groundtruth/formal-artifact-approvals/2026-05-08-{ADR,DCL}-*.json` returns non-empty |
| T-supersession | Predecessor DCL marked superseded | `db.get_spec('DCL-STANDING-BACKLOG-SCHEMA-001').superseded_by == 'DCL-STANDING-BACKLOG-DB-SCHEMA-001'` |

Live regression:

| Test | Method |
|---|---|
| T-live-doctor | `python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml doctor` returns no new ERRORs |
| T-live-release-gate | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` continues to PASS |

## Acceptance Criteria

For VERIFIED:

1. Slice A: Deliberation Archive captures the owner directive (T-deliberation-1).
2. Slice A: All three narrative artifacts (operating-model.md §2, canonical-terminology.md, memory/work_list.md) reflect deletion-at-conclusion (T-narrative-1..3).
3. Slice B: ADR v2 inserted with formal-artifact-approval packet (T-adr-1, T-approval-packet-presence).
4. Slice B: DCL v2 + supersession (if scoped per B2/B4) (T-dcl-1, T-supersession).
5. Live regression: doctor + release gate continue to pass.
6. No physical changes to `memory/work_list.md` content rows in this thread (the row migration is parent thread Slices 2-7); only the work-item body's narrative description changes.

## Risk / Rollback

Risk surface:

- **Premature deletion narrative**: Slices 2-7 of parent thread haven't landed; deletion endpoint is purely scoped here, not exercised. Risk: future readers may interpret "deletion is required" as "deletion happens immediately." Mitigation: Slice A wording explicitly says "at migration conclusion" and ties to a Slice 7-prime gate description.
- **Implementation-agnostic GOV**: if `GOV-STANDING-BACKLOG-001` v2 doesn't reference the markdown by name, no v3 update is needed. Slice B step B3 makes that determination; the proposal does not commit to a GOV update.
- **Formal-artifact-approval surface**: filing approval packets is an explicit owner-decision moment per `GOV-ARTIFACT-APPROVAL-001`. The AUQ evidence above seeds the packets but each ADR/DCL update should re-confirm via owner-visible packet display before insertion.

Rollback per slice:

- Slice A rollback: revert the three narrative artifact edits + insert a superseding deliberation entry (deliberations are append-only governance; no delete path).
- Slice B rollback: ADR/DCL versioning is append-only; a v3 supersession would be the rollback path. Rollback should be unnecessary because owner explicitly approved via AUQ.

## Files Expected To Change

Slice A:

- `.claude/rules/operating-model.md` — single-paragraph wording update in §2 "backlog" entry.
- `.claude/rules/canonical-terminology.md` — single-paragraph wording update in "backlog" entry; possible new "Lifecycle endpoint" sub-bullet.
- `memory/work_list.md` — single-section update under GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior".
- `groundtruth.db` — one new row in `deliberations` table.

Slice B:

- `groundtruth.db` — one new row in `specifications` table for ADR v2; possibly one for DCL v2; possibly one for GOV v3.
- `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001.json` — new approval packet (if scoped).

No code or test infrastructure changes in this thread. The migration-completion gate (Slice 7-prime) will be filed under the parent thread once Slices 2-6 are sequenced.

## Prior Deliberations

`db.search_deliberations("work_list deletion migration conclusion standing backlog markdown retire", limit=5)` to be run; preliminary expectation:

- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — owner decision motivating Slice 1 of parent thread.
- `DELIB-0838` — standing backlog as governed cross-session work authority.
- `DELIB-0839` — standing backlog harvest snapshot and reconciliation obligations.
- `DELIB-1404` — candidate specification statements backlog advisory.

No prior deliberation expected to contradict the deletion endpoint. If one surfaces, this proposal will revise to address it before requesting GO.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-001.md`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-001.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write (the hook runs the preflight and refuses Writes whose required-spec set is incomplete; this file passed after `ADR-ISOLATION-APPLICATION-PLACEMENT-001` was added to Specification Links).

All triggered cross-cutting specs are cited in `## Specification Links` above. Codex should recompute `packet_hash` against the filed operative file at review time.

## Recommended Commit Type

For this proposal filing: `docs(bridge):` — bridge-protocol artifact only, no code or test changes in this commit.

For Slice A implementation: `docs(governance):` — narrative artifact updates and Deliberation Archive entry; no code.

For Slice B implementation: `feat(governance):` — new ADR/DCL versions are net-additional governance capability surfaces (the deletion endpoint is a new constraint not previously expressed).

## Requested Loyal Opposition Action

Review this proposal for GO. Specific reviewer questions for Codex:

1. Is splitting Slice A (narrative + Deliberation Archive) from Slice B (formal ADR/DCL) correct, or should the formal artifact updates land before any narrative is updated? My read: narrative artifacts are the canonical authority surface that future agents read, so they should be updated synchronously with the formal specs; the split is for commit hygiene, not sequencing. Confirmation requested.
2. Does `GOV-STANDING-BACKLOG-001` v3 need to be in scope, or can the GOV remain implementation-agnostic? Slice B step B3 defers this; if Codex sees a hard dependency, please flag.
3. Is the `**Status:** VERIFIED (residual: ...)` annotation from the related startup-priority-recommender proposal also relevant here (the work-item body update may need a similar VERIFIED-with-residuals affordance to coexist with the parent thread's lifecycle)?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
