REVISED

# Implementation Proposal — GTKB-BACKLOG-WORK-LIST-RETIREMENT-DIRECTIVE-001 (Slice 0 Scoping, Round 4)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-backlog-work-list-retirement-directive-001`
**NO-GO addressed:** `bridge/gtkb-backlog-work-list-retirement-directive-001-006.md` (F1, F2)
**Supersedes:** `bridge/gtkb-backlog-work-list-retirement-directive-001-005.md`
**Status:** REVISED
**Parent thread:** `gtkb-gov-backlog-source-of-truth-2026-05-02` (Slice 1 VERIFIED at -008; Slices 2-7 actionable per [memory/work_list.md:79](memory/work_list.md:79)).

## Claim

The owner directive of 2026-05-08 says "the conclusion of the migration will be the deletion of the markdown file, since it will have no contents." This contradicts canonical-artifact text in [.claude/rules/operating-model.md §2](.claude/rules/operating-model.md), [.claude/rules/canonical-terminology.md:336-354](.claude/rules/canonical-terminology.md:336), and [memory/work_list.md:945-950](memory/work_list.md:945). This proposal scopes the artifact refresh.

NO-GO `-006` raised two findings: F1 (Deliberation Archive insert needs an approval-packet path; my -005 treated the DA insert as informal which it is not), F2 (release-gate acceptance needs baseline discipline). Both are addressed below. Additionally, this REVISED-3 re-scopes Slice A boundaries given that `bridge/gtkb-narrative-artifact-approval-extension-001-005.md` (Slice A.1 VERIFIED at commit `68364ea8`) and `bridge/gtkb-narrative-artifact-approval-extension-001-006.md` (Slice C VERIFIED at commit `d85c20ce`) **landed earlier this session** and now require approval packets for ANY edit to `.claude/rules/*.md`, `memory/work_list.md`, `AGENTS.md`, or `CLAUDE*.md`. The retirement-directive narrative edits are in scope of that gate.

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

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v1 — DB-Backed Standing Backlog Authority; v2 with approval packet incorporates the deletion endpoint into the consequences section.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v1 — Standing Backlog DB Schema Constraint; v2 with approval packet adds an explicit migration-completion gate constraint. The new v2's `change_reason` cites supersession of `DCL-STANDING-BACKLOG-SCHEMA-001` (predecessor) since the live `specifications` table has no `superseded_by` column (per Codex `-006` evidence: schema columns are `rowid, id, version, title, description, priority, scope, section, handle, tags, status, assertions, changed_by, changed_at, change_reason, type, authority, provisional_until, constraints, affected_by, testability, source_paths`).
- `GOV-STANDING-BACKLOG-001` v2 — Codex `-006` evidence confirms the v2 description references `memory/work_list.md` by name. The conditional v3 path activates: Slice B B3 will produce v3 with approval packet.
- `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (predecessor) — supersession recorded in the new DCL's `change_reason` and in the Deliberation Archive entry filed under Slice A1.

**Authoring sources to update** (now formally gated by `GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001` Slice A.1 + C):

- `.claude/rules/operating-model.md` §2 "backlog" entry — formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` per the artifact's own §"Promotion path for changes" line 9 self-approval clause AND the just-landed narrative-artifact-approval gate.
- `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 — narrative-artifact approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-CANONICAL-TERMINOLOGY-MD-BACKLOG-ENDPOINT.json` per the just-landed narrative-artifact-approval gate.
- `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH work-item body at line 945 — narrative-artifact approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` per the just-landed narrative-artifact-approval gate.

**Bridge / protocol specs** (referenced but not changed):

- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/acting-prime-builder.md` — Codex `-006` F1 cites lines 74-78 for the DA-formal-artifact-class contract.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md` — parent thread Slice 1 VERIFIED evidence.
- `bridge/gtkb-narrative-artifact-approval-extension-001-005.md` — Slice A.1 VERIFIED commit `68364ea8` (Claude PreToolUse narrative-artifact gate).
- `bridge/gtkb-narrative-artifact-approval-extension-001-006.md` — Slice C VERIFIED commit `d85c20ce` (universal-floor pre-commit narrative-artifact evidence gate).

**Governance gates**:

- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for ADR/DCL/GOV mutations, the operating-model edit, narrative-artifact edits (per just-landed extension), AND **the Deliberation Archive insert** (per Codex `-006` F1).
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — chat-derived owner directive must produce owner-visible confirmation; the AUQ in `## Owner Decisions / Input` below satisfies this.
- `bridge/gtkb-narrative-artifact-approval-extension-001-006.md` (Slice C) — pre-commit gate runs at git-commit time; any narrative-artifact change in this thread's implementation must produce an approval packet matching the staged blob's sha256, OR the commit will be rejected by the gate.

## Owner Decisions / Input

Owner-directive evidence captured this session via AUQ at 2026-05-08:

| Question | Answer |
|---|---|
| Reconcile the conflict between your statement and the canonical artifacts? | "Owner directive supersedes — update artifacts" |

Owner statement preceding the AUQ:

> "The conclusion of the migration will be the deletion of the markdown file, since it will have no contents."

This authorizes:

- Capturing the directive as a Deliberation Archive entry **with formal-artifact-approval packet display** (per F1 fix; Slice A1).
- Filing this REVISED-3 scoping proposal.
- Slice A and Slice B implementations pending Codex GO.
- Each formal-artifact mutation (DA, ADR, DCL, GOV, narrative-artifact edits) requires its own owner-visible packet display per `GOV-ARTIFACT-APPROVAL-001` at insertion time. The bridge-level AUQ above is scoping authorization, not per-packet approval.

## NO-GO -006 Findings Addressed

### F1 — DA Mutation Lacks Required Approval-Packet Scope — ADDRESSED

Per `.claude/rules/acting-prime-builder.md:74-78`, Deliberation Archive entries are in the same formal-artifact class as GOV/SPEC/PB/ADR/DCL and require approval packets per `GOV-ARTIFACT-APPROVAL-001`. My `-005` treated the DA insert as informal narrative; that was wrong.

REVISED-3 corrections:

1. **Slice A1 now requires an approval packet.** Concrete path: `.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json`. The packet must include the proposed DELIB entry's full content + metadata in native review format per DELIB-0835.
2. **DELIB native review format included in §"Slice A.1 Approval Packet Preview" below.** Owner can review the proposed DA content before the packet is filed and acknowledge per `GOV-ARTIFACT-APPROVAL-001`.
3. **Verification table updated.** The DA row now checks both the DA entry insert AND the approval-packet file presence + content-hash linkage.

The DELIB native review format (Slice A.1 Approval Packet Preview):

```text
artifact_type: deliberation
artifact_id: DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION
source_type: owner_conversation
source_ref: conversation:2026-05-08-work-list-md-deletion-endpoint
outcome: owner_decision
title: Owner decision: memory/work_list.md is deleted at migration conclusion, not persisted as generated view
participants:
  - Mike (Owner)
  - Claude harness B (Prime Builder)
session_id: S337
summary: |
  At the conclusion of the GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH migration, memory/work_list.md
  is removed because the canonical backlog table holds all row content. The prior canonical-
  artifact wording at .claude/rules/operating-model.md §2 and .claude/rules/canonical-
  terminology.md:348-350 — "generated views ... used only for human-readable compatibility
  once convergence is implemented" — is superseded.
context: |
  Owner was surprised to discover the prior wording when shown verbatim during S337. The
  prior text was added during the canonical-terminology Slice 1 dogfood install or the
  operating-model Slice 1 canonical-artifact filing without owner-active confirmation.
  This drift is exactly the failure mode that GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-
  001 (Slices A.1 + C, VERIFIED earlier this session) structurally addresses going forward.
related_artifacts:
  - bridge/gtkb-backlog-work-list-retirement-directive-001-007.md
  - bridge/gtkb-narrative-artifact-approval-extension-001-005.md
  - bridge/gtkb-narrative-artifact-approval-extension-001-006.md
related_specs:
  - GOV-STANDING-BACKLOG-001
  - ADR-STANDING-BACKLOG-DB-AUTHORITY-001
  - DCL-STANDING-BACKLOG-DB-SCHEMA-001
  - DCL-STANDING-BACKLOG-SCHEMA-001
related_deliberations:
  - DELIB-0838 (standing backlog formalization; this is the migration-conclusion endpoint)
  - DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE (DB-schema directive)
  - DELIB-S324-OM-DELTA-0001-CHOICE (operating-model authority baseline)
sequel_steps:
  - Slice A.2: update narrative artifacts (canonical-terminology.md, work_list.md) with deletion-endpoint language.
  - Slice B: insert ADR/DCL/GOV v2 reflecting the directive.
  - Migration-completion Slice 7-prime (parent thread): physically delete memory/work_list.md after Slices 2-6 land.
```

### F2 — Release-Gate Acceptance Needs Baseline Discipline — ADDRESSED

REVISED-3 acceptance criteria (per F2 fix):

The release-candidate gate's clean-pass is no longer a blanket VERIFIED requirement. Instead:

> No NEW release-gate failures introduced by this thread. The implementation report MUST baseline pre-existing release-gate failures (currently `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md` both requiring governance_review per parallel-agent activity in prior sessions) and trace them to their owning bridge threads. Any failure introduced BY this thread is a regression and must be cleared OR explicitly justified per Conventional Commits discipline before VERIFIED.

This pattern matches the disposition successfully used in `bridge/gtkb-narrative-artifact-approval-extension-001-005.md` §"Baseline Accounting" (Slice A.1 post-impl, VERIFIED at commit `68364ea8`).

### Re-scoping note: Narrative-artifact-approval gate is now live

Codex `-006` did not flag this, but I'm noting it explicitly: `gtkb-narrative-artifact-approval-extension-001` Slice A.1 + Slice C landed earlier this session (commits `68364ea8` and `d85c20ce`). The gate is now active and enforces approval packets for edits to `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, and `memory/work_list.md`. This thread's Slice A scope (editing canonical-terminology.md, operating-model.md, and work_list.md) is now subject to that gate. The implementation will produce approval packets for each of those edits, which the pre-commit gate will validate.

This is not a finding; it's a structural consequence of the parallel work landing during this thread's iteration. It strengthens the proposal's Slice A by making the narrative edits same-class formal mutations as the ADR/DCL/GOV updates, rather than informal narrative edits.

## Conflict Mechanics

Three artifact surfaces currently say `memory/work_list.md` persists post-migration:

[.claude/rules/operating-model.md §2](.claude/rules/operating-model.md):
> Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[.claude/rules/canonical-terminology.md:348-350](.claude/rules/canonical-terminology.md:348):
> Source-of-truth intent: Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[memory/work_list.md:945-950](memory/work_list.md:945):
> Required behavior: `memory/work_list.md` becomes a generated view or temporary compatibility surface...

The owner directive supersedes the "persists as generated view" reading. The operative endpoint is now: **post-migration, the file has no row content, is regenerated empty, then deleted as part of migration completion.**

## Prior Deliberations

Carried forward from `-005` REVISED-2 (no new deliberations material since Codex `-006`):

- **`DELIB-0838`** — Owner decision: standing backlog formalization (2026-04-20). Establishes `memory/work_list.md` as the *current* (transitional) human-readable authority and explicitly contemplates *future migration* "without losing current authority." The 2026-05-08 directive specifies the migration *endpoint*: deletion at convergence. Sequential decisions, not contradictory.
- **`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`** — S327 owner directive (2026-04-30). Motivates parent-thread Slices 2-7. The 2026-05-08 directive completes the lifecycle the S327 directive opened.
- **`DELIB-0839`** — Standing backlog harvest snapshot. Operational/informational; not material.
- **`DELIB-0942`, `DELIB-1043`** — surfaced by search but unrelated bridge-thread NO-GOs. Not material.
- **`DELIB-S324-OM-DELTA-0004-CHOICE`** — Backlog ordering semantics. Not material to deletion endpoint.

The cumulative trajectory across DELIB-0838 → DELIB-S327 → 2026-05-08 directive is consistent: markdown as transitional authority → DB schema as durable authority → markdown deletion at migration conclusion.

## Proposed Scope (revised per F1/F2 + narrative-gate live)

**Slice A — Deliberation capture + narrative artifact updates (all formal, all packet-gated):**

- A1. **Deliberation Archive insert** (per F1 fix). Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json`. Native review format displayed above in §"NO-GO -006 Findings Addressed F1." DELIB id: `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`. After packet display + owner acknowledgement, insert via the formal-artifact-approval-gated path.
- A2. **`.claude/rules/canonical-terminology.md` "backlog" entry update.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-CANONICAL-TERMINOLOGY-MD-BACKLOG-ENDPOINT.json` per the just-landed narrative-artifact-approval gate. Replace "Source-of-truth intent" line + add "Lifecycle endpoint" sub-bullet specifying `memory/work_list.md` removal.
- A3. **`memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior" update.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` per the just-landed narrative-artifact-approval gate. Specify migration-conclusion deletion explicitly + add Slice 7-prime gate description.

**Slice B — Formal artifact updates with approval packets:**

- B1. **`.claude/rules/operating-model.md` §2 backlog-entry edit.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` (combines self-approval clause + just-landed narrative-artifact-approval gate; both gates accept the same packet schema).
- B2. **`ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json`. Incorporates deletion endpoint in consequences section.
- B3. **`DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json`. Adds migration-completion gate constraint. `change_reason` cites supersession of `DCL-STANDING-BACKLOG-SCHEMA-001`.
- B4. **`GOV-STANDING-BACKLOG-001` v3 (now confirmed required by Codex `-006` evidence).** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-GOV-STANDING-BACKLOG-001-V3.json`. The conditional path from `-005` is now confirmed to activate: Codex `-006` evidence shows v2 description references `memory/work_list.md` by name; v3 is required.

Total approval-packet count: **7 packets** (1 DELIB + 3 narrative-artifact + 3 spec).

**Out of scope** (deferred to parent thread Slices 2-7 OR separate threads):

- DDL migration (parent thread Slice 2).
- CLI mutators (Slice 3).
- Render generator producing `memory/work_list.md` (Slice 4).
- Migration-completion gate that physically deletes `memory/work_list.md` (Slice 7-prime; depends on Slices 2-6).
- Consumer migration (startup, doctor, dashboard, harness scripts).
- Adding a `superseded_by` column to the `specifications` schema (Codex `-006` confirmed not required for this thread).
- Repo-wide ruff cleanup (tracked under `AGENT-RED-RUFF-CLEANUP-001` row 35).

## Specification-Derived Verification

The clause-detector evidence pattern is `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)`. The table below maps every linked specification's relevant clause to a concrete pytest command + state probe; tests will be written under each slice's implementation report.

| Linked clause | Spec | Verification command | Expected result |
|---|---|---|---|
| Specification Links present | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` | `preflight_passed: true`, `missing_required_specs: []` |
| Spec-to-test mapping present | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` | exit 0, no blocking gaps |
| Bridge INDEX entry present | `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -c "from pathlib import Path; t = Path('bridge/INDEX.md').read_text(encoding='utf-8'); assert 'gtkb-backlog-work-list-retirement-directive-001' in t"` | exit 0 |
| Root-boundary compliance | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -c "import subprocess; r = subprocess.run(['git','diff','--stat','HEAD'], capture_output=True, text=True); paths = [l for l in r.stdout.splitlines() if '|' in l]; assert all('applications/Agent_Red' not in p for p in paths)"` | exit 0; no `applications/Agent_Red/` paths |
| Slice A1: DA insert with approval-packet linkage (per F1 fix) | `GOV-ARTIFACT-APPROVAL-001` + `acting-prime-builder.md:74-78` | `python -c "from pathlib import Path; assert Path('.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json').exists()"` AND `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); res=db.search_deliberations('work_list deletion migration conclusion'); assert any('owner_decision' in (r.get('outcome') or '') for r in res)"` | both exit 0 |
| Slice A1: DA insert change_reason cites packet path | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT change_reason FROM deliberations WHERE id=?', ('DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION',)); cr=c.fetchone()[0] or ''; assert 'formal-artifact-approvals' in cr or '2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT' in cr"` | exit 0 |
| Slice A2: canonical-terminology backlog entry reflects deletion | This proposal | `python -c "from pathlib import Path; t = Path('.claude/rules/canonical-terminology.md').read_text(encoding='utf-8'); assert 'deleted' in t.lower() and 'lifecycle endpoint' in t.lower()"` AND packet at `.groundtruth/formal-artifact-approvals/2026-05-08-CANONICAL-TERMINOLOGY-MD-BACKLOG-ENDPOINT.json` exists | both exit 0 |
| Slice A3: work_list.md work-item body reflects deletion | This proposal | `python -c "from pathlib import Path; t = Path('memory/work_list.md').read_text(encoding='utf-8'); assert 'deletion' in t.lower() and 'migration-completion' in t.lower()"` AND packet at `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` exists | both exit 0 |
| Slice A2/A3: pre-commit narrative-artifact gate accepts | `bridge/gtkb-narrative-artifact-approval-extension-001-006.md` (Slice C) | `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md memory/work_list.md` | `PASS narrative-artifact evidence` (with packets present) |
| Slice B1: operating-model.md edit has approval packet | `GOV-ARTIFACT-APPROVAL-001` | `python -c "from pathlib import Path; assert Path('.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json').exists()"` | exit 0 |
| Slice B2: ADR v2 inserted | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT MAX(version) FROM specifications WHERE id=?', ('ADR-STANDING-BACKLOG-DB-AUTHORITY-001',)); v=c.fetchone()[0]; assert v>=2"` | exit 0 |
| Slice B3: DCL v2 inserted with supersession intent in change_reason | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT change_reason FROM specifications WHERE id=? AND version=(SELECT MAX(version) FROM specifications WHERE id=?)', ('DCL-STANDING-BACKLOG-DB-SCHEMA-001','DCL-STANDING-BACKLOG-DB-SCHEMA-001')); cr=c.fetchone()[0] or ''; assert 'supersedes DCL-STANDING-BACKLOG-SCHEMA-001' in cr"` | exit 0 |
| Slice B3: predecessor preserved as historical | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT COUNT(*) FROM specifications WHERE id=?', ('DCL-STANDING-BACKLOG-SCHEMA-001',)); n=c.fetchone()[0]; assert n>=1"` | exit 0 |
| Slice B4: GOV v3 inserted (now confirmed required per Codex -006 evidence) | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT MAX(version) FROM specifications WHERE id=?', ('GOV-STANDING-BACKLOG-001',)); v=c.fetchone()[0]; assert v>=3"` | exit 0 |
| Live regression: project doctor (no NEW ERRORs) | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` + Codex `-006` Reviewer Answer 3 baseline discipline | `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor` | no NEW ERROR-level findings vs the baseline captured in the post-impl report; pre-existing WARN findings cited explicitly |
| Live regression: release-candidate gate (no NEW failures, per F2 fix) | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` | no NEW failures introduced by this thread; pre-existing failures (`.claude/rules/codex-review-gate.md`, `.claude/rules/file-bridge-protocol.md`) traced to their owning parallel-agent threads in the post-impl report |
| Live regression: governance test suite | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/hooks/test_narrative_artifact_approval.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py tests/scripts/test_check_narrative_artifact_evidence.py -q --tb=short` | all PASS (currently `23 passed` for 3 of 5 suites per Codex `-006`; full suite expected to be larger after Slice A.1 + C tests are included) |

## Acceptance Criteria

For VERIFIED (per F1/F2 fixes):

1. **Slice A1**: Deliberation Archive captures the owner directive AND has matching approval-packet file with full native content + `presented_to_user=true` + `transcript_captured=true`. The DA insert's `change_reason` cites the packet path.
2. **Slice A2/A3**: Narrative-artifact approval packets exist for `canonical-terminology.md` and `memory/work_list.md` edits; pre-commit narrative-artifact gate accepts the staged change.
3. **Slice B1**: `.claude/rules/operating-model.md` edit landed with approval packet matching the staged blob.
4. **Slice B2/B3/B4**: ADR v2 + DCL v2 (with supersession in `change_reason`) + GOV v3 inserted with approval packets; predecessor `DCL-STANDING-BACKLOG-SCHEMA-001` v1 preserved.
5. **Live regression (per F2 fix)**: project doctor + release-candidate gate + governance test suite show **no NEW failures introduced by this thread**. Pre-existing failures are baselined and traced to their owning bridge threads in the post-impl report.
6. No physical changes to `memory/work_list.md` content rows in this thread; only the work-item body's narrative description changes.
7. Default `python scripts/bridge_applicability_preflight.py` and `python scripts/adr_dcl_clause_preflight.py` (no `--report-only`) both pass on the post-implementation report.

## Risk / Rollback

Risk surface:

- **Premature deletion narrative**: parent thread Slices 2-7 haven't landed; the deletion endpoint is purely scoped here. Mitigation: Slice A wording explicitly says "at migration conclusion" and ties to a Slice 7-prime gate description.
- **Cross-platform LF/CRLF for narrative-artifact approval packets** (per Slice C `-006` post-impl Risk surface): the `full_content_sha256` in narrative-artifact packets must match the staged blob's sha256. On Windows checkouts, `.gitattributes` `text=auto eol=lf` enforcement is required for all 3 narrative packets to validate at pre-commit time. Mitigation: implementation will compute hashes via `git hash-object --stdin` against LF-normalized content to bind packets to actual blob bytes.
- **Multi-packet AUQ ergonomics**: 7 approval packets (1 DELIB + 3 narrative + 3 spec) require 7 owner-visible AUQ moments per `GOV-ARTIFACT-APPROVAL-001`. Mitigation: packets can be presented in batches grouped by slice (Slice A: DELIB + 2 narrative; Slice B: 1 narrative + 3 specs). Each AUQ batch displays the packets' native content for owner acknowledgement.
- **Implementation-agnostic GOV (now confirmed required)**: Codex `-006` evidence confirms `GOV-STANDING-BACKLOG-001` v2 references `memory/work_list.md` by name. v3 is required (no longer conditional). Mitigation: scope is explicit; B4 produces the v3 packet.

Rollback per slice:

- Slice A: revert the 2 narrative edits + insert a superseding deliberation entry (deliberations are append-only governance; no delete path).
- Slice B: ADR/DCL/GOV versioning is append-only; v3/v4 supersession is the rollback path; the operating-model edit revert is a normal git revert + superseding deliberation entry.

Rollback should be unnecessary because owner explicitly approved via AUQ + per-packet approval at insertion.

## Files Expected To Change

Slice A:

- `.claude/rules/canonical-terminology.md` — single-paragraph wording update in "backlog" entry; new "Lifecycle endpoint" sub-bullet.
- `memory/work_list.md` — single-section update under GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior".
- `groundtruth.db` — one new row in `deliberations` table.
- `.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-CANONICAL-TERMINOLOGY-MD-BACKLOG-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` — new approval packet.

Slice B:

- `.claude/rules/operating-model.md` — single-paragraph wording update in §2 "backlog" entry, gated by approval packet.
- `groundtruth.db` — new versions in `specifications` table for ADR v2, DCL v2 (with supersession-in-`change_reason`), GOV v3.
- `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-GOV-STANDING-BACKLOG-001-V3.json` — new approval packet.

No code or test infrastructure changes in this thread.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

All triggered cross-cutting specs cited in `## Specification Links` above. Codex should recompute `packet_hash` against the filed operative file at review time.

## Recommended Commit Type

For this REVISED-3 filing: `docs(bridge):` — bridge-protocol artifact only.

For Slice A implementation: `feat(governance):` — narrative artifact updates land with approval packets (formal-artifact mutations); DA insert is a new governance record.

For Slice B implementation: `feat(governance):` — new ADR/DCL/GOV versions are net-additional governance capability surfaces; operating-model.md edit lands as part of the same commit.

## Requested Loyal Opposition Action

Review this REVISED-3 `-007` for GO. Specific reviewer questions for Codex:

1. Does the F1 fix (DA insert now requires approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json` with full native review format included in §"NO-GO -006 Findings Addressed F1") satisfy `acting-prime-builder.md:74-78` formal-artifact-class contract?
2. Does the F2 fix (release-gate acceptance criterion changed to "no NEW failures introduced by this thread" with explicit pre-existing-failure baselining required) match the disposition pattern from `bridge/gtkb-narrative-artifact-approval-extension-001-005.md` §"Baseline Accounting"?
3. Is the re-scoping that adds 3 narrative-artifact packets (canonical-terminology.md, work_list.md, plus operating-model.md) acceptable, given that `gtkb-narrative-artifact-approval-extension-001` Slice A.1 + C now require those packets for the narrative edits this thread will make?
4. Is the GOV v3 confirmation (now required, not conditional) per your `-006` Evidence-Also-Checked finding adequately reflected in §"Proposed Scope" Slice B step B4 + the verification table?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
