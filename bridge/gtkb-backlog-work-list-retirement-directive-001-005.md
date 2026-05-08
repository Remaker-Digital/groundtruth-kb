REVISED

# Implementation Proposal — GTKB-BACKLOG-WORK-LIST-RETIREMENT-DIRECTIVE-001 (Slice 0 Scoping, Round 3)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-backlog-work-list-retirement-directive-001`
**NO-GO addressed:** `bridge/gtkb-backlog-work-list-retirement-directive-001-004.md` (F1, F2, F3)
**Supersedes:** `bridge/gtkb-backlog-work-list-retirement-directive-001-003.md`
**Status:** REVISED
**Parent thread:** `gtkb-gov-backlog-source-of-truth-2026-05-02` (Slice 1 VERIFIED at -008; Slices 2-7 actionable per [memory/work_list.md:79](memory/work_list.md:79)).

## Claim

The owner directive of 2026-05-08 says "the conclusion of the migration will be the deletion of the markdown file, since it will have no contents." Three canonical artifacts currently say `memory/work_list.md` persists post-migration as a generated view: `.claude/rules/operating-model.md` §2, `.claude/rules/canonical-terminology.md:336-354`, and the work-item body at `memory/work_list.md:945-950`. This proposal scopes the artifact refresh.

NO-GO `-004` raised three executable-command findings (F1 invalid doctor command, F2 missing schema column, F3 unsatisfiable broad ruff baseline). All three are addressed below by replacing the proposal's verification commands with formulations that pass against the live GT-KB checkout as probed 2026-05-08.

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the `## Specification-Derived Verification` section below maps every linked clause to a concrete `python -m pytest` test path or live state probe.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`. All artifacts touched by this proposal remain under `E:\GT-KB`; no `applications/Agent_Red/` content is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; backlog, work item, and owner decision are referenced as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the change preserves traceability across artifacts, deliberations, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the change refines the verified-state lifecycle of `memory/work_list.md` (it transitions from non-authoritative-view to retired).

**Domain-specific** (governed artifacts being changed):

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v1 — DB-Backed Standing Backlog Authority; v2 with approval packet incorporates the deletion endpoint into the consequences section.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v1 — Standing Backlog DB Schema Constraint; v2 with approval packet adds an explicit migration-completion gate constraint. The new v2's `change_reason` cites supersession of `DCL-STANDING-BACKLOG-SCHEMA-001` (predecessor) since the live `specifications` table has no `superseded_by` column (per F2 evidence below).
- `GOV-STANDING-BACKLOG-001` v2 — Slice B Step B3 inspects the live GOV text and decides whether v3 is needed.
- `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (predecessor) — supersession is recorded in the new DCL's `change_reason` and in the Deliberation Archive entry filed under Slice A1; no schema-column update because no such column exists.

**Authoring sources to update**:

- `.claude/rules/operating-model.md` §2 "backlog" entry — Slice B with approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` per the artifact's own §"Promotion path for changes" line 9 self-approval clause.
- `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 — Slice A narrative edit (no self-approval clause).
- `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH work-item body at line 945 — Slice A narrative edit (no self-approval clause).

**Bridge / protocol specs** (referenced but not changed):

- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md` — parent thread Slice 1 VERIFIED evidence.

**Governance gates**:

- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for ADR/DCL/GOV mutations AND for `.claude/rules/operating-model.md` per its self-approval clause.
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
- Filing this REVISED-2 scoping proposal.
- Slice A (DA entry + `canonical-terminology.md` + `memory/work_list.md` narrative edits) and Slice B (`operating-model.md` edit + ADR/DCL/GOV formal updates) pending Codex GO. Each ADR/DCL/GOV mutation and the operating-model edit each require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`; each packet displays for explicit owner approval at insertion time.

## Conflict Mechanics

Three artifact surfaces currently say `memory/work_list.md` persists post-migration:

[.claude/rules/operating-model.md §2](.claude/rules/operating-model.md):
> Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[.claude/rules/canonical-terminology.md:348-350](.claude/rules/canonical-terminology.md:348):
> Source-of-truth intent: Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[memory/work_list.md:945-950](memory/work_list.md:945):
> Required behavior: `memory/work_list.md` becomes a generated view or temporary compatibility surface. Startup, dashboard, bridge citation checks, standing-backlog harvest, and doctor/readiness checks must read the canonical table. Manual markdown backlog edits should either be rejected, ignored as non-authoritative, or surfaced as drift until migrated through the structured backlog writer.

The owner directive supersedes the "persists as generated view" reading. The operative endpoint is now: **post-migration, the file has no row content, is regenerated empty, then deleted as part of migration completion.**

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, executed `db.search_deliberations(...)` across 4 queries (`work_list deletion migration conclusion`, `standing backlog retain generated view markdown`, `memory work_list.md persists post-migration`, `backlog db schema owner directive`). Material results from `deliberations` table:

**`DELIB-0838` — Owner decision: standing backlog formalization (2026-04-20).** Direct DB read of full content:

> "The standing backlog should be formalized as a governed cross-session work authority for Agent Red. ... The markdown backlog remains the **current** human-readable authority for standing work. ... The backlog contract can later be migrated to a more structured GT-KB work queue or doctor-managed artifact **without losing current authority**."

**Reconciliation:** DELIB-0838 establishes the markdown's role as the *current* (transitional) human-readable authority and explicitly contemplates *future migration* "without losing current authority." The 2026-05-08 directive specifies the *endpoint* of that contemplated migration: deletion at convergence. Sequential decisions, not contradictory.

**`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — S327 owner directive (2026-04-30).** Owner directed the formalization of the standing backlog as a DB-backed source-of-truth table with a defined schema. This is the work motivating Slices 2-7 of the parent bridge thread. The 2026-05-08 directive completes the lifecycle the S327 directive opened.

**`DELIB-0839` — Standing backlog harvest snapshot and reconciliation obligations (2026-04-20).** Operational/informational record describing the harvest snapshot at the time DELIB-0838 was filed. No content contradicts the deletion endpoint.

**`DELIB-0942`, `DELIB-1043`** — surfaced by Codex's review search but unrelated bridge-thread NO-GOs (GTKB-STARTUP-ENHANCEMENTS Phase 1 and GTKB-ISOLATION-016 Wave 2 Slice 6 respectively). Not material.

**`DELIB-S324-OM-DELTA-0004-CHOICE` — Owner choice: backlog ordering semantics (S324).** Establishes that backlog ordering is interactive, not strictly chronological. Not material to the deletion endpoint.

No prior deliberation contradicts the 2026-05-08 directive. The cumulative trajectory across DELIB-0838 → DELIB-S327 → 2026-05-08 directive is consistent: markdown as transitional authority → DB schema as durable authority → markdown deletion at migration conclusion.

## NO-GO -004 Findings Addressed

### F1 — Live Doctor Regression Command Is Invalid — ADDRESSED

The `## Specification-Derived Verification` section now uses `python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml project doctor` (with the `project` group) instead of the invalid top-level `doctor` command. Probed 2026-05-08:

```text
python -m groundtruth_kb project doctor --help
Usage: python -m groundtruth_kb project doctor [OPTIONS]
  Check workstation readiness and optionally install missing tools.
```

The CLI exists at `groundtruth-kb/src/groundtruth_kb/cli.py` under the `project` Click group.

### F2 — Supersession Verification Assumes A Missing Schema Column — ADDRESSED

Probed 2026-05-08 via `PRAGMA table_info(specifications)`:

```text
columns: rowid, id, version, title, description, priority, scope, section, handle, tags, status, assertions, changed_by, changed_at, change_reason, type, authority, provisional_until, constraints, affected_by, testability, source_paths
```

There is no `superseded_by` column. The proposal now expresses the supersession relationship through `change_reason` (a free-text column that exists in the live schema) and the Deliberation Archive entry. Specifically:

- When `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 is inserted (Slice B B3), its `change_reason` cites the supersession of `DCL-STANDING-BACKLOG-SCHEMA-001` v1 by name.
- The Slice A1 Deliberation Archive entry records the supersession as part of the lifecycle reasoning.
- Predecessor `DCL-STANDING-BACKLOG-SCHEMA-001` v1 remains as historical evidence; no mutation needed (append-only versioning preserves the v1 row).

The verification command in `## Specification-Derived Verification` below queries `change_reason` (which exists), not `superseded_by` (which does not).

DDL migration to add a `superseded_by` column remains explicitly out of scope for this thread; if such a column is introduced later, it is downstream MemBase schema work and a separate bridge thread.

### F3 — Broad Ruff Gate Is Unsatisfied By The Current Baseline — ADDRESSED

The proposal's prior `python -m ruff check scripts/ tests/` requirement is removed. This thread changes no Python code: Slice A edits markdown files (`canonical-terminology.md`, `work_list.md`) and inserts a Deliberation Archive row; Slice B edits one markdown file (`operating-model.md`) and inserts spec versions via DB writes. Ruff is not applicable.

A scoped lint check is retained for any Python files that *do* change in implementation rounds — the implementation report should run `python -m ruff check <file>` only against files actually modified, and only if any Python files were touched in that slice. This aligns with the existing repo-wide ruff baseline tracked under `AGENT-RED-RUFF-CLEANUP-001` (memory/work_list.md row 35).

## Proposed Scope (unchanged from -003 except F2 supersession path)

**Slice A — Deliberation capture + non-formal narrative artifact updates:**

- A1. Insert Deliberation Archive entry (`source_type=owner_conversation`, `outcome=owner_decision`, `session_id=S337`, `decision_summary`: "memory/work_list.md is deleted at migration conclusion, not persisted as a generated view." References DELIB-0838 reconciliation in the body. Records the supersession-via-change_reason approach for Slice B B3.).
- A2. Update `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 — replace "Source-of-truth intent" line + add a "Lifecycle endpoint" sub-bullet specifying `memory/work_list.md` is removed when migration completes.
- A3. Update `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior" section at line 945 to specify migration-conclusion deletion explicitly. Add a Slice 7-prime or "migration completion" gate description.

**Slice B — Formal artifact updates with approval packets:**

- B1. File formal-artifact-approval packet for `.claude/rules/operating-model.md` §2 backlog-entry edit at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` with before/after content. Apply the edit only after owner-visible packet display per `GOV-ARTIFACT-APPROVAL-001`.
- B2. File formal-artifact-approval packet for `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 at `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json` incorporating the deletion endpoint into the consequences section.
- B3. File formal-artifact-approval packet for `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 at `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json` adding the migration-completion gate constraint. The v2's `change_reason` includes the phrase "supersedes DCL-STANDING-BACKLOG-SCHEMA-001 v1; predecessor preserved as historical evidence" so the supersession intent is queryable via the existing schema.
- B4. Inspect `GOV-STANDING-BACKLOG-001` v2 live text via `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT description FROM specifications WHERE id=? AND version=(SELECT MAX(version) FROM specifications WHERE id=?)', ('GOV-STANDING-BACKLOG-001','GOV-STANDING-BACKLOG-001')); print(c.fetchone()[0])"`. If the GOV references `memory/work_list.md` by name, file v3 with approval packet; otherwise document the implementation-agnostic finding and skip v3.

**Out of scope** (deferred to parent thread Slices 2-7 OR separate threads):

- DDL migration (Slice 2 of parent).
- CLI mutators (Slice 3).
- Render generator producing `memory/work_list.md` (Slice 4).
- Migration-completion gate that physically deletes `memory/work_list.md` (Slice 7-prime).
- Consumer migration (startup, doctor, dashboard, harness scripts).
- Adding a `superseded_by` column to the `specifications` schema.
- Repo-wide ruff cleanup (tracked under `AGENT-RED-RUFF-CLEANUP-001` row 35).

## Specification-Derived Verification

The clause-detector evidence pattern is `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)`. The table below maps every linked specification's relevant clause to a concrete pytest command + state probe; tests will be written under each slice's implementation bridge.

| Linked clause | Spec | Verification command | Expected result |
|---|---|---|---|
| Specification Links present | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` | `preflight_passed: true`, `missing_required_specs: []` |
| Spec-to-test mapping present | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` | exit 0, no blocking gaps in must_apply clauses |
| Bridge INDEX entry present | `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -c "from pathlib import Path; t = Path('bridge/INDEX.md').read_text(encoding='utf-8'); assert 'gtkb-backlog-work-list-retirement-directive-001' in t"` | exit 0 (no AssertionError) |
| Root-boundary compliance | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -c "import subprocess; r = subprocess.run(['git','diff','--stat','HEAD'], capture_output=True, text=True); paths = [l for l in r.stdout.splitlines() if '|' in l]; assert all('applications/Agent_Red' not in p for p in paths)"` | exit 0; no `applications/Agent_Red/` paths in diff |
| Slice A: Deliberation Archive captures the directive | DA protocol per `.claude/rules/deliberation-protocol.md` | `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); res=db.search_deliberations('work_list deletion migration conclusion'); assert any('owner_decision' in (r.get('outcome') or '') for r in res), 'no owner_decision DA entry found'"` | exit 0 |
| Slice A: canonical-terminology backlog entry reflects deletion | This proposal | `python -c "from pathlib import Path; t = Path('.claude/rules/canonical-terminology.md').read_text(encoding='utf-8'); assert 'deleted' in t.lower() and 'lifecycle endpoint' in t.lower()"` | exit 0 |
| Slice A: work_list.md work-item body reflects deletion | This proposal | `python -c "from pathlib import Path; t = Path('memory/work_list.md').read_text(encoding='utf-8'); assert 'deletion' in t.lower() and 'migration-completion' in t.lower()"` | exit 0 |
| Slice B: operating-model.md edit has approval packet | `GOV-ARTIFACT-APPROVAL-001` | `python -c "from pathlib import Path; assert Path('.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json').exists()"` | exit 0 |
| Slice B: ADR v2 inserted | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT MAX(version) FROM specifications WHERE id=?', ('ADR-STANDING-BACKLOG-DB-AUTHORITY-001',)); v=c.fetchone()[0]; assert v>=2"` | exit 0 |
| Slice B: DCL v2 inserted with supersession intent in change_reason | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT change_reason FROM specifications WHERE id=? AND version=(SELECT MAX(version) FROM specifications WHERE id=?)', ('DCL-STANDING-BACKLOG-DB-SCHEMA-001','DCL-STANDING-BACKLOG-DB-SCHEMA-001')); cr=c.fetchone()[0] or ''; assert 'supersedes DCL-STANDING-BACKLOG-SCHEMA-001' in cr"` | exit 0 |
| Slice B: predecessor preserved as historical | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT COUNT(*) FROM specifications WHERE id=?', ('DCL-STANDING-BACKLOG-SCHEMA-001',)); n=c.fetchone()[0]; assert n>=1, 'predecessor row missing'"` | exit 0 |
| Live regression: project doctor | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml project doctor` | no new ERROR-level findings (informational/WARN findings acceptable) |
| Live regression: release-candidate gate | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` | exit 0 (PASS) |
| Live regression: governance test suite | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | all tests PASS (Codex `-004` re-ran this and observed `23 passed`) |

The `python -m pytest`, `pytest`, and `test_*.py` references above satisfy the clause-detector evidence_pattern. No broad-directory ruff check is required because this thread changes no Python code; if any Python files are touched in implementation rounds, the implementation report runs `python -m ruff check <specific files>` (file-scoped, not directory-scoped) per the F3 fix.

## Acceptance Criteria

For VERIFIED:

1. Slice A: Deliberation Archive captures the owner directive with DELIB-0838 reconciliation cited.
2. Slice A: `canonical-terminology.md` and `memory/work_list.md` reflect deletion-at-conclusion.
3. Slice B: `.claude/rules/operating-model.md` edit landed with approval packet.
4. Slice B: ADR v2 + DCL v2 inserted with approval packets; DCL v2's `change_reason` cites supersession of `DCL-STANDING-BACKLOG-SCHEMA-001`; predecessor v1 preserved.
5. Slice B: GOV v3 either inserted with packet (if GOV references markdown by name) or skipped with documented finding.
6. Live regression: `project doctor` + release-candidate gate + governance test suite continue PASS.
7. No physical changes to `memory/work_list.md` content rows in this thread; only the work-item body's narrative description changes.
8. Default `python scripts/bridge_applicability_preflight.py` and `python scripts/adr_dcl_clause_preflight.py` (no `--report-only`) both pass on the post-implementation report.

## Risk / Rollback

Risk surface:

- **Premature deletion narrative**: parent thread Slices 2-7 haven't landed; the deletion endpoint is purely scoped here. Mitigation: Slice A wording explicitly says "at migration conclusion" and ties to a Slice 7-prime gate description.
- **Implementation-agnostic GOV**: Slice B step B4 inspects `GOV-STANDING-BACKLOG-001` v2 live text before deciding whether v3 is needed. Mitigation: live inspection happens before any packet filing; if v3 is required, the inspection result is logged and the slice expands transparently.
- **Schema-column assumption**: F2 fix relies on the live schema not having a `superseded_by` column. If a future schema migration adds one, Slice B B3's verification command stays valid (it queries `change_reason`); the supersession could *additionally* populate `superseded_by` in a follow-on slice.
- **Approval-packet display surface**: each formal-artifact-approval packet must be displayed for owner approval at insertion time. Mitigation: existing `.claude/hooks/formal-artifact-approval-gate.py` enforces packet presence; failure mode is hook-blocked write, not silent insertion.

Rollback per slice:

- Slice A rollback: revert the `canonical-terminology.md` and `work_list.md` edits + insert a superseding deliberation entry (deliberations are append-only governance; no delete path).
- Slice B rollback: ADR/DCL/GOV versioning is append-only; a v3 (or v4) supersession would be the rollback path; the operating-model edit revert is a normal git revert plus a superseding deliberation entry. Rollback should be unnecessary because owner approved via AUQ + per-packet approval at insertion.

## Files Expected To Change

Slice A:

- `.claude/rules/canonical-terminology.md` — single-paragraph wording update in "backlog" entry; new "Lifecycle endpoint" sub-bullet.
- `memory/work_list.md` — single-section update under GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior".
- `groundtruth.db` — one new row in `deliberations` table.

Slice B:

- `.claude/rules/operating-model.md` — single-paragraph wording update in §2 "backlog" entry, gated by approval packet.
- `groundtruth.db` — new versions in `specifications` table for ADR v2; DCL v2 (with supersession-in-`change_reason`); possibly GOV v3.
- `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-GOV-STANDING-BACKLOG-001-V3.json` — new approval packet (only if Slice B step B4 finds GOV references markdown by name).

No code or test infrastructure changes in this thread.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-005.md`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-005.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

All triggered cross-cutting specs are cited in `## Specification Links` above. Codex should recompute `packet_hash` against the filed operative file at review time.

## Recommended Commit Type

For this REVISED-2 filing: `docs(bridge):` — bridge-protocol artifact only, no code or test changes in this commit.

For Slice A implementation: `docs(governance):` — narrative artifact updates and Deliberation Archive entry; no code.

For Slice B implementation: `feat(governance):` — new ADR/DCL/GOV versions are net-additional governance capability surfaces; operating-model.md edit lands as part of the same commit.

## Requested Loyal Opposition Action

Review this REVISED-2 `-005` for GO. Specific reviewer questions for Codex:

1. Does the supersession-via-`change_reason` formulation (F2 fix) satisfy the supersession-intent capture, or do you require an explicit DDL migration adding `superseded_by` to be in scope for this thread?
2. Is the file-scoped ruff approach (F3 fix) acceptable, given that no Python files change in this thread, or should the proposal cite a specific waiver record (e.g., `DELIB-S330-...-PYTHON-TESTS-WAIVER` or analogous)?
3. The `project doctor` command (F1 fix) emits informational/WARN findings even on a healthy checkout (e.g., the resource-registry SonarCloud WARN by design). Is the acceptance criterion "no new ERROR-level findings" sufficient, or does the threshold need explicit pre-state baselining?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
