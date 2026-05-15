REVISED

# Implementation Proposal - Critical Quality and Consistency Audit of Early-Project Requirements - Slice 1 (Scoping + Audit Execution) - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-early-project-requirements-quality-audit-slice-1-scoping
Version: 003
Responds to: bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source: WI-3247 - Critical quality and consistency audit of early-project requirements
target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUDIT-EARLY-PROJECT-REQUIREMENTS-2026-05-14-001.md", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/audit-early-project-requirements-2026-05-14-deterministic.json", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-14-early-project-requirements-audit-da-record.json", "scripts/audit_early_project_requirements.py", "platform_tests/scripts/__init__.py", "platform_tests/scripts/test_audit_early_project_requirements.py"]

## Claim

This REVISED proposal commits to a single, internally consistent corpus model (historical version-1 quality drift) and relocates the audit script's test surface into the root-configured `platform_tests/` lane. Both changes directly address Codex's NO-GO at `-002` (F1 corpus inconsistency, F2 test-surface placement). All other elements of the `-001` proposal carry forward unchanged: read-only audit, single deliverable bundle (report + DA record + classification manifest), no formal-spec mutation, downstream remediation routed via separate bridge threads with their own approval evidence.

## In-Root Placement Evidence

Every entry in `target_paths` is under `E:\GT-KB`:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUDIT-EARLY-PROJECT-REQUIREMENTS-2026-05-14-001.md` — audit report (in-root deliverable surface, governed dropbox).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/audit-early-project-requirements-2026-05-14-deterministic.json` — deterministic-pass JSON appendix (in-root).
- `groundtruth.db` — in-root MemBase file; the only mutation is one DA-record insert via the formal-artifact-approval packet path.
- `.groundtruth/formal-artifact-approvals/2026-05-14-early-project-requirements-audit-da-record.json` — in-root approval-packet surface.
- `scripts/audit_early_project_requirements.py` — in-root audit script.
- `platform_tests/scripts/__init__.py` — package marker under root-configured `platform_tests/` testpath.
- `platform_tests/scripts/test_audit_early_project_requirements.py` — audit script test under the same testpath.

No path resolves outside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` is satisfied by construction.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge is authoritative coordination channel for this audit's proposal-review-verification cycle; this proposal lives in `bridge/` and registers its entry at the top of `bridge/INDEX.md` (insert a new `REVISED` line at the top of the existing thread's version list per file-bridge-protocol).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the linkage requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the audit's post-implementation report will carry forward this linkage table.
- `GOV-STANDING-BACKLOG-001` — WI-3247 originates from the standing backlog; audit-derived remediation candidates are surfaced via the standing-backlog channel and do not bulk-write to `work_items`.
- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — addressed in `Clause Scope Clarification (Not a Bulk Operation)` below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all `target_paths` reside under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — audit findings preserve traceability across the script, report, DA record, classification manifest, and downstream remediation candidates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — audit-identified deficiencies become durable artifacts (DA record + classification manifest), not chat-only context.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — per-row classification states are drawn from the canonical lifecycle vocabulary.
- `GOV-ARTIFACT-APPROVAL-001` — the single DA insert at audit completion is gated by the per-artifact formal-artifact-approval packet path; no other formal-artifact mutation occurs in this slice.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — approval-packet hook covers the DA insert path.
- `.claude/rules/operating-model.md` §§1-2 — the alignment baseline against which early-project requirement quality is evaluated.
- `.claude/rules/canonical-terminology.md` — terminology baseline used to detect terminology drift in early-project requirements.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol contract; the INDEX entry for this thread receives a new `REVISED: bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-003.md` line inserted at the top of this thread's version list.
- `.claude/rules/codex-review-gate.md` — review-gate contract governing this proposal's review and post-implementation verification.
- `.claude/rules/project-root-boundary.md` — all audit deliverables under `E:\GT-KB`.
- `bridge/INDEX.md` — canonical workflow-state file; the REVISED entry for this thread is inserted at the top of this thread's existing version list before review is dispatchable.

## Prior Deliberations

- `DELIB-S324-OM-DELTA-0001-CHOICE` — Owner decision establishing LO authority over cited requirements; supports the audit's posture of questioning early requirement quality.
- `DELIB-S321-AUDIT-ARTIFACTS-FOR-AMBIGUITY` — Owner directive to audit artifacts for ambiguity; directly aligned with WI-3247 scope.
- `DELIB-S333-QUALITY-FIRST-DESIGN-GOALS` — Quality-first design goals; informs audit acceptance criteria.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` — Records the matured requirements-collection workflow whose absence characterized the early-project period under audit.
- `DELIB-S330-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT` — Defense-in-depth posture for requirements; the audit identifies legacy gaps.
- `DELIB-1975` — `gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30` VERIFIED audit-class precedent.
- `DELIB-1909` — `gtkb-docs-quality-remediation` VERIFIED quality-remediation precedent.
- `DELIB-S333-ISOLATION-017-CITATION-BACKFILL-AUDIT` — Citation-backfill audit precedent informing the structural-analysis methodology.
- `DELIB-2049` / `DELIB-2050` — Operating-model Slice 0/1 ORPHAN records flagging that operating-model alignment remains a live thread whose terminology baseline the audit must respect.

## Owner Decisions / Input

- S350 owner directive: "Parallel research + serialized Writes now (Recommended)" (AUQ answer for S350 batch authorization). This authorizes batch filing of priority backlog proposals; per-proposal Codex GO remains required before any implementation step proceeds.
- S350 current-turn directive: "Please continue to parallelize work." This proposal's research-and-revision step is executed in parallel with sibling priority-backlog research; the file Write of the REVISED proposal is serialized per the AUQ recommendation.
- No additional AskUserQuestion answers are required for THIS proposal's filing. The corpus-model commitment (historical-drift) and the test-surface relocation are deficiency corrections within the existing scope of WI-3247; neither expands scope, neither requires new owner approval.
- Downstream remediation proposals derived from the audit's findings will collect their own approval evidence per `GOV-ARTIFACT-APPROVAL-001` at the time each remediation is proposed.
- The single DA insert at audit completion is governed by `GOV-ARTIFACT-APPROVAL-001` and will carry its own approval packet at insertion time.

## Requirement Sufficiency

Existing requirements sufficient.

WI-3247 ("Critical quality and consistency audit of early-project requirements") plus the cited governance specs and the operating-model alignment baseline (`.claude/rules/operating-model.md` §§1-2) together specify the audit's purpose, the quality dimensions to evaluate, the lifecycle states for classification, and the approval gates for the single DA insert. No new or revised formal requirement is needed before implementation; the audit consumes existing specs as evaluation criteria.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a SCOPED audit producing a SINGLE deliverable bundle: one report file, one deterministic-pass JSON appendix, one DA record, one classification manifest (embedded as a section of the report). It is NOT a bulk operation against `work_items` or `specifications`. Specifically:

- The audit READS specifications; it does not mutate them. Any spec mutation is downstream work proposed as separate bridge threads.
- The audit produces an `inventory` of in-scope historical-version-1 rows (a read-only structural snapshot) — this is enumeration, not a bulk write.
- DA insertion at audit-completion time uses the per-artifact `formal-artifact-approval` packet path (one packet for one DA record), not a bulk-insert path.
- Remediation candidates produced by the audit are CLASSIFICATIONS (data in the report), not `work_items` rows. Promotion to `work_items` is a separate, per-candidate downstream step.
- DECISION DEFERRED on whether to bulk-promote classification-manifest rows into `work_items` at any later phase: that decision is explicitly out of scope for Slice 1 and will be re-raised in Slice 2 (or in a separate bridge thread) once Slice 1's manifest exists for owner review.

Evidence tokens: `inventory`; `formal-artifact-approval`; `DECISION DEFERRED`.

## Proposed Scope

### IP-1 — Historical-Version-1 Corpus Definition (F1 fix)

The audit corpus is the **historical-version-1 cohort**: rows of the append-only `specifications` table that satisfy ALL of the following:

1. `version = 1` (the originally-filed version of each spec_id).
2. `changed_at < 2026-04-01` (created before LO-review-gate maturation).
3. The same `spec_id` does NOT have a current version in `current_specifications` with `changed_at >= 2026-04-01` (i.e., rows already subject to post-maturation review evidence are excluded from this slice).

This corpus model is explicitly **historical-text quality drift**, not current-state authority. Direct MemBase observation:

```sql
-- Historical-version-1 base counts (audit corpus before maturation-exclusion):
SELECT COUNT(*) FROM specifications WHERE version=1 AND changed_at < '2026-04-01';
-- 2093

SELECT COUNT(*) FROM specifications
 WHERE version=1 AND type='requirement' AND status='specified'
   AND changed_at < '2026-03-01';
-- 1571 (focus subset)

-- Maturation exclusion (these IDs are dropped from the audit corpus):
SELECT COUNT(DISTINCT s.spec_id)
  FROM specifications s
  JOIN current_specifications cs USING (spec_id)
 WHERE s.version=1 AND s.changed_at < '2026-04-01'
   AND cs.changed_at >= '2026-04-01';
```

### IP-2 — Output Labeling Discipline

All classification outputs are labeled **historical-drift evidence** + **remediation candidates for spec_id <ID>**. The report explicitly states for each classification row: (a) which historical-version-1 text is being evaluated, (b) what the spec_id's current text is (if different), and (c) the recommendation applies to whichever surface is still live and matches the historical text. This prevents the audit from being read as a current-state mutation plan.

### IP-3 — Quality Dimensions Evaluated (unchanged from -001)

Six dimensions: (1) canonical-terminology alignment, (2) operating-model alignment, (3) implementation-evidence coherence, (4) internal contradiction / duplicate detection, (5) scope clarity, (6) obsolescence / off-target detection. Dimensions 1, 3, 4 run deterministically in the audit script; dimensions 2, 5, 6 run as structured analysis bounded by the deterministic enumeration.

### IP-4 — Test Surface Placement (F2 fix)

Audit script tests live at `platform_tests/scripts/test_audit_early_project_requirements.py` with `platform_tests/scripts/__init__.py` for package recognition. This places the test inside the root-configured `[tool.pytest.ini_options].testpaths = ["platform_tests", "applications/Agent_Red/tests"]` lane, ensuring the test is collected by default `pytest` invocations and remains in regression coverage after this slice's verification. No `pyproject.toml` edit is required.

### IP-5 — Deliverables (single bundle)

1. Audit report at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUDIT-EARLY-PROJECT-REQUIREMENTS-2026-05-14-001.md`.
2. Deterministic-pass JSON at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/audit-early-project-requirements-2026-05-14-deterministic.json`.
3. Audit script at `scripts/audit_early_project_requirements.py` (read-only DB access via `sqlite3.connect(..., uri=True, mode=ro)`).
4. Audit script test at `platform_tests/scripts/test_audit_early_project_requirements.py` plus package marker.
5. Single DA record inserted at audit completion via per-artifact formal-artifact-approval packet (`outcome='informational'`, `source_type='audit_report'`).

## Specification-Derived Verification Plan

| Specification clause / acceptance criterion | Test or verification command |
|---|---|
| WI-3247 description: "Scan early-stage requirements ... produce a triage report" | Audit deliverable #1 exists at the named path; report contains a non-empty classification manifest table covering every row in the post-maturation-exclusion historical corpus. |
| WI-3247 description: "classify remediation actions" | Classification manifest uses ONLY the five canonical states (`accept_as_is`, `correction_candidate`, `supersession_candidate`, `retirement_candidate`, `requires_owner_clarification`). Test asserts all classification states fall within the allowed enum. |
| WI-3247 description: "without mutating formal specs" | Post-impl diff shows zero rows added to `specifications` with `version > 1` during the audit-execution commit. Only mutation is one row in `deliberations`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping` returns `preflight_passed: true`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This table maps each acceptance criterion to a verification step. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All `target_paths` under `E:\GT-KB`; verified by inspection. |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | This thread's REVISED entry is at the top of its version list in `bridge/INDEX.md`. |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `Clause Scope Clarification (Not a Bulk Operation)` section is present with required evidence tokens. |
| Corpus correctness (F1 fix) | Audit script emits its corpus-selection SQL and observed row counts as the first section of the deterministic-pass JSON; Codex verifies counts match the maturation-exclusion model. |
| Test-surface correctness (F2 fix) | `python -m pytest platform_tests/scripts/test_audit_early_project_requirements.py -q` collects and passes the test under default root pytest invocation. |
| Audit determinism | Same input fixture yields byte-identical JSON output across two consecutive runs. |
| Audit script read-only against `groundtruth.db` | Script opens DB with `sqlite3.connect("file:groundtruth.db?mode=ro", uri=True)`; test asserts no INSERT/UPDATE/DELETE/CREATE/ALTER/DROP statements in script source via AST scan. |

## Risks and Rollback

Risks:

- R1 (low): Structured-analysis dimensions (2, 5, 6) may produce reviewer-disputable classifications. Mitigation: each classification carries rationale prose; Codex may NO-GO disputed classifications, triggering revision.
- R2 (low): Audit report length may strain Codex review attention. Mitigation: fixed-schema classification manifest table supports deterministic spot-checks; full prose only in methodology and exemplar discussion.
- R3 (negligible): Audit script accidentally mutates `groundtruth.db`. Mitigation: read-only URI mode enforced at connect time; AST-level test rejects any write-mode SQL keywords in the script source.
- R4 (low): Downstream remediation candidates accumulate without owner triage. Mitigation: classification manifest is delivered as a single ranked list; promotion to `work_items` rows is a separate per-candidate owner-prioritized step.
- R5 (low; introduced by F1 fix): Historical-corpus framing could be misread as a current-state mutation plan. Mitigation: IP-2 output-labeling discipline + per-row inclusion of the current text alongside the historical text being classified.

Rollback:

- Additive artifacts only (one report file, one JSON, one script, one test, one package marker, one DA record). Rollback is `git revert <commit>` plus DA-record retirement (mark `outcome='retired'`, append rationale). No formal-spec mutations to undo.

## Sequenced Dependencies

1. Codex GO recorded on this REVISED proposal at `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-004.md`.
2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping` to mint the session-local implementation packet.
3. Implement `scripts/audit_early_project_requirements.py` (deterministic dimensions 1/3/4) and `platform_tests/scripts/test_audit_early_project_requirements.py` (+ `__init__.py`).
4. Run `python -m pytest platform_tests/scripts/test_audit_early_project_requirements.py -q`.
5. Execute audit script; emit deterministic JSON; perform structured-analysis pass for dimensions 2/5/6 over the deterministic enumeration.
6. Compose audit report.
7. Mint formal-artifact-approval packet for the DA insert; insert the DA record via the standard governed path.
8. File implementation report at `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-005.md` for VERIFIED review.

## Recommended Commit Type

`feat:` — this slice adds net-new infrastructure: a new audit script, a new test module, a new package directory under `platform_tests/`, and a new audit report surface under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`. The deterministic-audit capability is novel; `docs:` (used at -001) understated the diff.

## Bridge-Compliance Self-Check

- First line: `REVISED` (line 1).
- Title line: `# Implementation Proposal - <Title> - REVISED-1`.
- Metadata: `bridge_kind`, `Document`, `Version: 003`, `Responds to`, `Author`, `Date`, `Session`, `target_paths` (JSON list, all in-root) all present.
- Required sections (presence check): `Claim`, `In-Root Placement Evidence`, `Specification Links` (plain flat list, no `###` sub-headings; cites `bridge/INDEX.md` and the `insert at top of this thread's version list` convention), `Prior Deliberations` (substantive, non-empty), `Owner Decisions / Input` (substantive; cites S350 parallelization directive), `Requirement Sufficiency` (exactly one operative state: `Existing requirements sufficient`), `Clause Scope Clarification (Not a Bulk Operation)` (includes `inventory`, `formal-artifact-approval`, `DECISION DEFERRED`), `Proposed Scope` (with `### IP-N` sub-sections), `Specification-Derived Verification Plan`, `Risks and Rollback`, `Sequenced Dependencies`, `Recommended Commit Type`, `Bridge-Compliance Self-Check`, footer copyright.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
