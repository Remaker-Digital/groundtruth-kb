REVISED

# Implementation Proposal — GTKB-BACKLOG-WORK-LIST-RETIREMENT-DIRECTIVE-001 (Slice 0 Scoping, Round 2)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-backlog-work-list-retirement-directive-001`
**NO-GO addressed:** `bridge/gtkb-backlog-work-list-retirement-directive-001-002.md` (F1, F2, F3, F4)
**Supersedes:** `bridge/gtkb-backlog-work-list-retirement-directive-001-001.md`
**Status:** REVISED
**Parent thread:** `gtkb-gov-backlog-source-of-truth-2026-05-02` (Slice 1 VERIFIED at -008; Slices 2-7 actionable per [memory/work_list.md:79](memory/work_list.md:79)).

## Claim

The owner directive of 2026-05-08 says "the conclusion of the migration will be the deletion of the markdown file, since it will have no contents." Three canonical artifacts currently say `memory/work_list.md` persists post-migration as a generated view: `.claude/rules/operating-model.md` §2, `.claude/rules/canonical-terminology.md:336-354`, and the work-item body at `memory/work_list.md:945-950`. This proposal scopes the artifact refresh.

NO-GO `-002` raised four findings (F1 mandatory clause gate, F2 deliberation search, F3 operating-model approval-packet path, F4 portable test commands). All four are addressed below.

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the `## Specification-Derived Verification` section below maps every linked clause to a concrete `python -m pytest` test path.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`. All artifacts touched by this proposal remain under `E:\GT-KB`; no `applications/Agent_Red/` content is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; backlog, work item, and owner decision are referenced as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the change preserves traceability across artifacts, deliberations, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the change refines the verified-state lifecycle of `memory/work_list.md` (it transitions from non-authoritative-view to retired).

**Domain-specific** (governed artifacts being changed):

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v1 — DB-Backed Standing Backlog Authority; needs v2 with approval packet to incorporate the deletion endpoint into the consequences section.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v1 — Standing Backlog DB Schema Constraint; v2 with approval packet adds an explicit migration-completion gate constraint.
- `GOV-STANDING-BACKLOG-001` v2 — Slice B Step B3 inspects the live GOV text and decides whether v3 is needed (per Codex `-002` answer 2; if the GOV references the markdown file by name, v3 is in scope).
- `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (predecessor) — marked superseded_by `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 in Slice B.

**Authoring sources to update**:

- `.claude/rules/operating-model.md` §2 "backlog" entry — narrative edit MOVED to Slice B per F3 because the artifact's own §"Promotion path for changes" requires "an owner-approved bridge proposal and a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001`." The Slice B approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` is the required gate.
- `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 — Slice A narrative edit (this artifact does NOT impose a self-approval clause; eligible for Slice A scope under existing governance).
- `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH work-item body at line 945 — Slice A narrative edit (this file does NOT impose a self-approval clause; eligible for Slice A scope).

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
- Filing this REVISED scoping proposal.
- Slice A (Deliberation Archive entry + `.claude/rules/canonical-terminology.md` + `memory/work_list.md` narrative edits) and Slice B (`.claude/rules/operating-model.md` edit + ADR/DCL/GOV formal artifact updates with approval packets) pending Codex GO.

ADR/DCL/GOV mutations and the `.claude/rules/operating-model.md` edit each require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`. Each packet will be displayed for explicit owner approval at the time of insertion (per the artifact-approval contract); the AUQ evidence above seeds those packets but does not pre-authorize them.

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

Per `.claude/rules/deliberation-protocol.md`, executed this command:

```text
python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); ..."
```

Search queries: `work_list deletion migration conclusion`, `standing backlog retain generated view markdown`, `backlog db schema owner directive`. Material results retrieved from `deliberations` table:

**`DELIB-0838` — Owner decision: standing backlog formalization (2026-04-20).**
Direct database read of the full content (`SELECT content FROM deliberations WHERE id='DELIB-0838'`):

> "The standing backlog should be formalized as a governed cross-session work authority for Agent Red. ... The markdown backlog remains the **current** human-readable authority for standing work. ... The backlog contract can later be migrated to a more structured GT-KB work queue or doctor-managed artifact **without losing current authority**."

**Reconciliation:** DELIB-0838 establishes the markdown's role as the *current* (transitional) human-readable authority and explicitly contemplates *future migration* "without losing current authority." The 2026-05-08 owner directive specifies the *endpoint* of that contemplated migration: deletion of the markdown once convergence completes. The two decisions are sequential, not contradictory: DELIB-0838 sets the transition's start state; the 2026-05-08 directive sets its end state. The intent ("durable cross-session work authority") is preserved; the implementation surface (markdown vs. DB) shifts at migration completion.

**`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — S327 owner directive (2026-04-30).**
Owner directed the formalization of the standing backlog as a DB-backed source-of-truth table with a defined schema. This is the work motivating Slices 2-7 of the parent bridge thread (`gtkb-gov-backlog-source-of-truth-2026-05-02`). The 2026-05-08 directive completes the lifecycle the S327 directive opened.

**`DELIB-0839` — Standing backlog harvest snapshot and reconciliation obligations (2026-04-20).**
Operational/informational record describing the harvest snapshot at the time DELIB-0838 was filed. No content contradicts the deletion endpoint.

**`DELIB-0942`, `DELIB-1043`** — surfaced by Codex's review search but are unrelated bridge-thread NO-GOs (GTKB-STARTUP-ENHANCEMENTS Phase 1 and GTKB-ISOLATION-016 Wave 2 Slice 6 respectively). Not material to the retirement directive.

**`DELIB-1325`** — search did not return a record under that ID in the current `deliberations` table; treated as a Codex search-tooling reference rather than a contradicting decision.

**`DELIB-S324-OM-DELTA-0004-CHOICE` — Owner choice: backlog ordering semantics (S324).**
Establishes that backlog ordering is interactive, not strictly chronological. Not material to the deletion endpoint.

No prior deliberation contradicts the 2026-05-08 directive. The cumulative trajectory across DELIB-0838 → DELIB-S327 → 2026-05-08 directive is consistent: markdown as transitional authority → DB schema as durable authority → markdown deletion at migration conclusion.

## NO-GO -002 Findings Addressed

### F1 (blocking) — Mandatory Clause Gate Fails — ADDRESSED

The `## Specification-Derived Verification` section below maps every linked spec clause to a concrete `python -m pytest tests/...` test path. The clause detector's evidence_pattern (`(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)`) matches multiple times in this document.

### F2 (blocking) — Prior Deliberation Search Was Not Completed Before Filing — ADDRESSED

`## Prior Deliberations` section above is now populated with executed search results, full DELIB-0838 content quoted via direct SQLite read, explicit reconciliation against the retain-as-generated-view text, and dispositions for each DELIB ID Codex flagged.

### F3 (blocking) — Operating-Model Edit Lacks Required Approval Packet — ADDRESSED

`.claude/rules/operating-model.md` §"Promotion path for changes" line 9 requires "an owner-approved bridge proposal and a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001`." The operating-model edit has been **moved from Slice A into Slice B** alongside the ADR/DCL/GOV formal-artifact updates. The approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` is the gate; the packet must be filed before the edit is written.

The other two narrative artifacts (`canonical-terminology.md` and `memory/work_list.md`) do NOT impose self-approval clauses in their own text and remain in Slice A. (The separately-proposed `gtkb-narrative-artifact-approval-extension-001` would extend approval to those files but is not yet VERIFIED, so it does not retroactively gate this thread's Slice A work.)

### F4 (recommendation) — Test Commands Are Not Portable To The Active Harness Shell — ADDRESSED

All `grep` references in the prior round have been replaced with PowerShell `Select-String` or repo-native Python equivalents. The `## Specification-Derived Verification` section uses `python -m pytest` for test execution and `python -c "..."` for state probes, both of which are portable to PowerShell.

## Proposed Scope (revised per F3)

**Slice A — Deliberation capture + non-formal narrative artifact updates:**

- A1. Insert Deliberation Archive entry recording the owner directive (`source_type=owner_conversation`, `outcome=owner_decision`, `session_id=S337`, `decision_summary`: "memory/work_list.md is deleted at migration conclusion, not persisted as a generated view." References DELIB-0838 reconciliation in the body.).
- A2. Update `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 — replace "Source-of-truth intent" line + add a "Lifecycle endpoint" sub-bullet specifying `memory/work_list.md` is removed when migration completes.
- A3. Update `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior" section at line 945 to specify migration-conclusion deletion explicitly. Add a Slice 7-prime or "migration completion" gate description.

**Slice B — Formal artifact updates with approval packets:**

- B1. File formal-artifact-approval packet for `.claude/rules/operating-model.md` §2 backlog-entry edit at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` with before/after content. Apply the edit only after owner-visible packet display per `GOV-ARTIFACT-APPROVAL-001`.
- B2. File formal-artifact-approval packet for `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 at `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json` incorporating the deletion endpoint into the consequences section.
- B3. File formal-artifact-approval packet for `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 at `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json` adding the migration-completion gate constraint.
- B4. Inspect `GOV-STANDING-BACKLOG-001` v2 live text via `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); print(db.get_spec('GOV-STANDING-BACKLOG-001'))"`. If the GOV references `memory/work_list.md` by name, file v3 with approval packet; otherwise document the implementation-agnostic finding and skip v3.
- B5. Mark predecessor `DCL-STANDING-BACKLOG-SCHEMA-001` with `superseded_by='DCL-STANDING-BACKLOG-DB-SCHEMA-001'` (no separate approval packet; supersession is a metadata link recorded with the v2 insertion's approval packet).

**Out of scope** (deferred to parent thread Slices 2-7):

- DDL migration (Slice 2 of parent).
- CLI mutators (Slice 3).
- Render generator producing `memory/work_list.md` (Slice 4) — generator may still exist temporarily during migration window; this proposal only changes post-completion endpoint.
- Migration-completion gate that physically deletes `memory/work_list.md` (Slice 7-prime; depends on Slices 2-6 landing first).
- Consumer migration (startup, doctor, dashboard, harness scripts) — tracked in parent thread.

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
| Slice B: DCL v2 inserted (if scoped per B3) | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT MAX(version) FROM specifications WHERE id=?', ('DCL-STANDING-BACKLOG-DB-SCHEMA-001',)); v=c.fetchone()[0]; assert v>=2"` | exit 0 |
| Slice B: predecessor supersession | `GOV-ARTIFACT-APPROVAL-001` | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT superseded_by FROM specifications WHERE id=? ORDER BY version DESC LIMIT 1', ('DCL-STANDING-BACKLOG-SCHEMA-001',)); s=c.fetchone()[0]; assert s=='DCL-STANDING-BACKLOG-DB-SCHEMA-001'"` | exit 0 |
| Live regression: doctor | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml doctor` | no new ERROR-level findings |
| Live regression: release-candidate gate | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` | exit 0 (PASS) |
| Live regression: governance test suite | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | all tests PASS |
| Code-quality compliance | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m ruff check scripts/ tests/` and `python -m ruff format --check scripts/ tests/` | exit 0 (no lint or format errors) |

The `python -m pytest` and `test_*.py` references above satisfy the clause-detector evidence_pattern. Each test will be created in the slice's implementation bridge (Slice A creates the canonical-terminology and work_list.md regression checks; Slice B creates the spec-version assertions).

## Acceptance Criteria

For VERIFIED:

1. Slice A: Deliberation Archive captures the owner directive with DELIB-0838 reconciliation cited (T-deliberation-1 above).
2. Slice A: `canonical-terminology.md` and `memory/work_list.md` reflect deletion-at-conclusion (T-canonical-terminology, T-work_list above).
3. Slice B: `.claude/rules/operating-model.md` edit landed with approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` (T-operating-model above).
4. Slice B: ADR v2 + DCL v2 inserted with approval packets and supersession metadata (T-adr-v2, T-dcl-v2, T-supersession above).
5. Slice B: GOV v3 either inserted with packet (if GOV references markdown by name) or skipped with documented finding.
6. Live regression: doctor + release-candidate gate + governance test suite continue PASS.
7. No physical changes to `memory/work_list.md` content rows in this thread; only the work-item body's narrative description changes.
8. Default `python scripts/bridge_applicability_preflight.py` and `python scripts/adr_dcl_clause_preflight.py` (no `--report-only`) both pass on the post-implementation report.

## Risk / Rollback

Risk surface:

- **Premature deletion narrative**: Slices 2-7 of parent thread haven't landed; deletion endpoint is purely scoped here, not exercised. Risk: future readers may interpret "deletion is required" as "deletion happens immediately." Mitigation: Slice A wording explicitly says "at migration conclusion" and ties to a Slice 7-prime gate description.
- **Implementation-agnostic GOV**: Slice B step B4 inspects GOV-STANDING-BACKLOG-001 v2 live text before deciding whether v3 is needed. Risk: GOV v3 turns out to be required, expanding scope. Mitigation: live inspection happens before any packet filing; if v3 is required, the inspection result is logged and the slice expands transparently.
- **Approval-packet display surface**: Each formal-artifact-approval packet must be displayed for owner approval at insertion time. Risk: agent skips display step. Mitigation: existing `.claude/hooks/formal-artifact-approval-gate.py` already enforces packet presence; failure mode is hook-blocked write, not silent insertion.
- **Detector regression**: clause detector evidence_pattern matches `python -m pytest` literally, so future small drift (e.g., pattern updates) could re-fail the gate. Mitigation: tests in `tests/scripts/test_adr_dcl_clause_preflight.py` cover the detector's contract.

Rollback per slice:

- Slice A rollback: revert the `canonical-terminology.md` and `work_list.md` edits + insert a superseding deliberation entry (deliberations are append-only governance; no delete path).
- Slice B rollback: ADR/DCL/GOV versioning is append-only; a v3 (or v4) supersession would be the rollback path; the operating-model edit revert is a normal git revert plus a superseding deliberation entry. Rollback should be unnecessary because owner explicitly approved via AUQ + per-packet approval.

## Files Expected To Change

Slice A:

- `.claude/rules/canonical-terminology.md` — single-paragraph wording update in "backlog" entry; new "Lifecycle endpoint" sub-bullet.
- `memory/work_list.md` — single-section update under GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior".
- `groundtruth.db` — one new row in `deliberations` table.

Slice B:

- `.claude/rules/operating-model.md` — single-paragraph wording update in §2 "backlog" entry, gated by approval packet.
- `groundtruth.db` — new versions in `specifications` table for ADR v2; possibly DCL v2; possibly GOV v3.
- `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json` — new approval packet (if scoped).
- `.groundtruth/formal-artifact-approvals/2026-05-08-GOV-STANDING-BACKLOG-001-V3.json` — new approval packet (only if Slice B step B4 finds GOV references markdown by name).

No code or test infrastructure changes in this thread. The migration-completion gate (Slice 7-prime) will be filed under the parent thread once Slices 2-6 are sequenced.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-003.md`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-003.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

All triggered cross-cutting specs are cited in `## Specification Links` above. Codex should recompute `packet_hash` against the filed operative file at review time.

## Recommended Commit Type

For this REVISED filing: `docs(bridge):` — bridge-protocol artifact only, no code or test changes in this commit.

For Slice A implementation: `docs(governance):` — narrative artifact updates (canonical-terminology.md + work_list.md) and Deliberation Archive entry; no code.

For Slice B implementation: `feat(governance):` — new ADR/DCL/GOV versions are net-additional governance capability surfaces (the deletion endpoint is a new constraint not previously expressed); operating-model.md edit lands as part of the same commit since it's the same scope.

## Requested Loyal Opposition Action

Review this REVISED `-003` for GO. Specific reviewer questions for Codex:

1. Is the Slice A / Slice B split now correct under the F3 fix? Slice A keeps `canonical-terminology.md` + `work_list.md` (no self-approval clauses); Slice B handles `operating-model.md` + ADR/DCL/GOV with approval packets.
2. Is the DELIB-0838 reconciliation argument (sequential decisions, not contradictory) sufficient, or does the directive need additional reconciliation evidence against another DELIB?
3. Does Slice B step B4's "inspect GOV text first, then decide v3 scope" workflow satisfy your `-002` answer 2 ("if it names `memory/work_list.md` as a continuing surface, it belongs in scope")?
4. Are the test-command formulations in `## Specification-Derived Verification` portable enough across PowerShell + bash harnesses, or should I rewrite any in pure Python module form?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
