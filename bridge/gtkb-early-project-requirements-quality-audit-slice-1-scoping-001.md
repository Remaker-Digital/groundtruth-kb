---
Status: NEW
Author: prime-builder (claude harness B)
Date: 2026-05-14
Session: S350
Source: WI-3247 — Critical quality and consistency audit of early-project requirements
Recommended commit type: docs
bridge_kind: implementation_proposal
target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUDIT-EARLY-PROJECT-REQUIREMENTS-*.md", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-14-early-project-requirements-audit-*.json", "scripts/audit_early_project_requirements.py", "tests/scripts/test_audit_early_project_requirements.py"]
---

# Critical Quality and Consistency Audit of Early-Project Requirements — Slice 1 (Scoping + Audit Execution)

## Summary

This proposal scopes and executes a critical quality-and-consistency audit of GT-KB's early-project requirement-type specifications — those created before GT-KB memory/knowledge-management practices matured and before the Loyal Opposition review gate was active. The audit produces a written triage report plus a Deliberation Archive (DA) record that classifies each in-scope requirement against deterministic and structured-analysis quality criteria, with proposed remediation actions (correction, supersession, retirement, accept-as-is). The audit itself MUTATES NO formal specifications; any remediation is downstream work routed through the standard bridge protocol and the per-artifact approval packet path under `GOV-ARTIFACT-APPROVAL-001`.

Slice scope: a SINGLE deliverable bundle (audit script + report + DA record + classified remediation backlog candidates). Remediation execution is explicitly out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge is authoritative coordination channel for this audit's proposal-review-verification cycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal's spec linkage discipline.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — audit deliverable verification must derive from the audit-criteria specification surface (this proposal).
- `GOV-STANDING-BACKLOG-001` — WI-3247 originates from the standing backlog; audit-derived remediation candidates land via the standing-backlog channel.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all audit deliverables remain within `E:\GT-KB` per project-root-boundary rule.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — audit findings preserve traceability across artifacts, tests, reports, and decisions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — audit-identified deficiencies become durable artifacts (DA record + work item candidates), not chat-only context.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — remediation classification uses the canonical state vocabulary (candidate, deferred, blocked, superseded, verified, retired).
- `GOV-ARTIFACT-APPROVAL-001` — audit produces no formal-artifact mutation; any downstream remediation requires the standard approval packet.
- `.claude/rules/operating-model.md` — §1 operating model and §2 canonical terminology are the alignment baseline for evaluating early-project requirement quality.
- `.claude/rules/canonical-terminology.md` — terminology baseline used to detect terminology drift in early-project requirements.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol contract for this proposal's filing, review, and verification cycle.
- `.claude/rules/codex-review-gate.md` — review-gate contract; the audit deliverable IS this proposal's implementation surface and is bound by the gate.
- `.claude/rules/project-root-boundary.md` — all audit deliverables under `E:\GT-KB`; no external paths.

## Prior Deliberations

- `DELIB-S324-OM-DELTA-0001-CHOICE` — Owner-decision establishing LO authority over cited requirements; supports the audit's posture of questioning early requirement quality.
- `DELIB-S321-AUDIT-ARTIFACTS-FOR-AMBIGUITY` — S321 owner directive to audit artifacts for ambiguity; directly aligned with WI-3247 scope.
- `DELIB-S333-QUALITY-FIRST-DESIGN-GOALS` — Quality-first and fit-for-purpose design goals; informs audit acceptance criteria.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` — Records the matured requirements-collection workflow whose ABSENCE characterized the early-project period under audit.
- `DELIB-S330-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT` — Defense-in-depth posture for requirements; the audit identifies legacy gaps in this posture.
- `DELIB-1975` — `gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30` VERIFIED audit-class precedent (12-version chain; demonstrates audit-class proposal viability under current bridge protocol).
- `DELIB-1909` — `gtkb-docs-quality-remediation` VERIFIED quality-remediation precedent.
- `DELIB-S333-ISOLATION-017-CITATION-BACKFILL-AUDIT` — Citation-backfill audit precedent informing the structural-analysis methodology below.
- `DELIB-2049` / `DELIB-2050` — Operating-model Slice 0/1 ORPHAN records flagging that operating-model alignment work remains a live thread that the audit's quality criteria must respect.

## Owner Decisions / Input

- Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible." This authorizes batch filing of priority backlog proposals (WI-3247 is P1, project `GTKB-REQUIREMENTS-QUALITY-AUDIT`). Per-proposal Codex GO is still required before any implementation step proceeds.
- No additional AskUserQuestion answers are required for THIS proposal's filing. Downstream remediation proposals derived from the audit's findings will collect their own approval evidence per `GOV-ARTIFACT-APPROVAL-001` at the time each remediation is proposed.
- No formal-artifact mutation occurs as part of this audit. The audit DELIVERABLE includes a DA record; that DA insert is governed by `GOV-ARTIFACT-APPROVAL-001` and will carry its own approval packet at insertion time.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a SCOPED audit producing a SINGLE deliverable bundle (one report file, one DA record, one classification manifest). It is NOT a bulk operation against the `work_items` table or the `specifications` table. Specifically:

- The audit READS specifications; it does not mutate them. Any spec mutation is downstream work proposed as separate bridge threads.
- The audit produces an inventory of in-scope requirements (a read-only structural snapshot) — the word "inventory" is used in the deterministic-checks methodology below to denote this read-only enumeration, not a bulk write.
- DA insertion at audit-completion time uses the per-artifact formal-artifact-approval path (one packet for one DA record), not a bulk-insert path.
- Remediation candidates produced by the audit are CLASSIFICATIONS (data in the report), not `work_items` rows. Promotion to `work_items` is a separate, per-candidate downstream step.

Evidence tokens: `inventory` (read-only structural snapshot of in-scope requirements); `formal-artifact-approval` (the DA insert at audit completion is gated by the standard per-artifact packet path under `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`).

## Requirement Sufficiency

**Existing requirements sufficient.** WI-3247 ("Critical quality and consistency audit of early-project requirements") plus the cited governance specs (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) and the operating-model alignment baseline (`.claude/rules/operating-model.md` §§1–2) together specify the audit's purpose, the quality dimensions to evaluate, and the lifecycle states for classification. No new or revised formal requirement is needed before implementation; the audit consumes existing specs as evaluation criteria.

## Audit Scope and Methodology

### In-scope corpus

Live MemBase observation (recorded as inventory in the deliverable, not mutated):

- 2093 specifications with `version = 1` and `changed_at < 2026-04-01` (LO review gate matured during April 2026 per `DELIB-S324-OM-DELTA-0001-CHOICE` and the operating-model Slice 0 inventory at `independent-progress-assessments/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md`).
- Of those, the focus subset is the 1571 `type='requirement'` rows at `status='specified'` created before 2026-03-01 — the largest cohort of unverified early-project requirements.
- Secondary subsets: 80 verified, 46 implemented, 2 retired (pre-2026-03 requirements); 10 specified governance specs and 10 verified protected behaviors created in the same window.
- "Early-project" boundary: `changed_at < 2026-04-01` (cutoff justified by the LO-review-maturation marker above and verified by direct DB query).

The audit does NOT touch:
- The 202 already-retired requirements (already triaged out).
- Any spec touched (new version inserted) on/after 2026-04-01 (those rows have post-maturation review evidence).

### Quality dimensions evaluated

The audit classifies each in-scope row against six dimensions:

1. **Canonical-terminology alignment** — Does the spec text use terminology consistent with `.claude/rules/canonical-terminology.md` §§ Canonical Terms and GT-KB Platform & Lifecycle Terms? Deterministic check: substring scan for forbidden uses (per operating-model §2's "Forbidden:" clauses) and for known alias collisions.
2. **Operating-model alignment** — Does the spec describe behavior consistent with `.claude/rules/operating-model.md` §1, or does it presuppose a workflow the current operating model has superseded? Structured analysis (LLM-assisted) against the four §4 alignment tests.
3. **Implementation-evidence coherence** — Does the spec's `status` match the available implementation evidence (linked tests, assertions, related commits)? Deterministic check: row's `status` ∈ {`specified`} cross-referenced against presence of related `tests.spec_id` references and `assertions` field population.
4. **Internal contradiction / duplicate detection** — Are there pairs of in-scope rows whose `title` or `description` substantially overlap or contradict? Deterministic check: title-tokenization + jaccard threshold; followed by structured-analysis pair review for the top-N flagged pairs.
5. **Scope clarity** — Is the spec's scope statement unambiguous, or does it conflate UI/business-rule/infrastructure concerns? Structured analysis against scope-clarity rubric derived from `GOV-04` (spec granularity).
6. **Obsolescence / off-target detection** — Is the spec still on the project's current trajectory, or has it been superseded by GT-KB evolution (e.g., Agent-Red-specific REQ-NNN rows post-2026-05-04 boundary correction)? Structured analysis combining the canonical Agent-Red separation per `.claude/rules/canonical-terminology.md` § Agent Red and operating-model §1 application/platform separation.

### Deterministic vs. structured-analysis split

- Dimensions 1, 3, 4 (token-level): deterministic Python script `scripts/audit_early_project_requirements.py` consuming `groundtruth.db` and emitting JSON per-row classifications.
- Dimensions 2, 5, 6: structured-analysis pass over the deterministic JSON, applied by the implementing harness with explicit rubrics; LLM-assisted analysis is bounded by the deterministic enumeration (audit considers ONLY rows from the script's output; no free-form spec retrieval).

### Output classification states

Per-row state is one of (`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` aligned):

- `accept_as_is` — quality acceptable; no action.
- `correction_candidate` — minor textual or terminology fix recommended; downstream remediation needed.
- `supersession_candidate` — content overlaps a later, better-formed spec; recommend supersede.
- `retirement_candidate` — obsolete or off-target; recommend retire.
- `requires_owner_clarification` — substantive ambiguity that needs owner input.

## Audit Deliverables

1. **Audit report** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUDIT-EARLY-PROJECT-REQUIREMENTS-2026-05-14-001.md` (date-stamped, single document). Contains:
   - Methodology section (mirrors §"Audit Scope and Methodology" above).
   - Per-dimension findings with counts, examples, and representative spec-ID citations.
   - Classification manifest table (spec_id, current_status, audit_state, dimension_flags, recommended_action, rationale).
   - Cross-reference index from classification states to downstream remediation work-item candidates.
2. **Audit script** at `scripts/audit_early_project_requirements.py` — deterministic dimensions 1/3/4 executor; reproducible; read-only against `groundtruth.db`; emits JSON at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/audit-early-project-requirements-2026-05-14-deterministic.json` for inclusion as appendix.
3. **Audit script test** at `tests/scripts/test_audit_early_project_requirements.py` — covers determinism (same input ⇒ same output), schema correctness, and dimension-1/3/4 rubric application against fixture data.
4. **Deliberation Archive record** — inserted at audit completion via the standard per-artifact formal-artifact-approval packet path. DA record's `outcome='informational'`, `source_type='audit_report'`, body cites the audit report path and SHA. (DA insert is the only MemBase mutation in this slice.)
5. **Classification manifest** as a section of deliverable #1 — this is the downstream work-item candidate list. Promotion to actual `work_items` rows is downstream (separate proposals), per `Clause Scope Clarification`.

## Test Mapping

| Specification clause / acceptance criterion | Test or verification command |
|---|---|
| WI-3247 description: "Scan early-stage requirements ... Produce a triage report" | Audit deliverable #1 exists at the named path; report contains a non-empty classification manifest table. Manual verification by Codex Loyal Opposition. |
| WI-3247 description: "classify remediation actions" | Classification manifest uses one of the five canonical states from §"Output classification states". Test: `tests/scripts/test_audit_early_project_requirements.py` asserts all classification states fall within the allowed enum. |
| WI-3247 description: "without mutating formal specs" | `git diff --stat HEAD~1 HEAD -- groundtruth.db` shows only the DA-record insert (one row in `deliberations`); no rows touched in `specifications`. Test: post-impl spec-row count delta = 0 for `version > 1` inserts during audit-execution commit. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping` returns `preflight_passed: true`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This Test Mapping table maps each audit acceptance criterion to a verification step; post-impl report carries forward and executes the table. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All `target_paths` under `E:\GT-KB`; verified by inspection. |
| Audit determinism | `python -m pytest tests/scripts/test_audit_early_project_requirements.py -q` passes; same input fixture yields byte-identical JSON output. |
| Audit script read-only against `groundtruth.db` | Script opens DB with `sqlite3.connect(..., uri=True)` in `mode=ro`; test asserts no INSERT/UPDATE/DELETE statements in script source. |

## Risk and Rollback

**Risks:**

- R1 (low): Structured-analysis dimensions (2, 5, 6) may produce reviewer-disputable classifications. Mitigation: audit report lists rationale per classification; Codex Loyal Opposition may NO-GO classifications it disputes, triggering revision.
- R2 (low): Audit report length may strain Codex review attention. Mitigation: report uses a fixed-schema classification manifest table consumable by deterministic spot-checks; full prose only in methodology and exemplar discussion sections.
- R3 (negligible): Audit script accidentally mutates `groundtruth.db`. Mitigation: read-only DB connection enforced by test; audit script never imports the write-side `groundtruth_kb` API.
- R4 (low): Downstream remediation candidates accumulate without owner triage, becoming stale. Mitigation: classification manifest is delivered as a single ranked list; promotion to `work_items` rows is a separate, owner-prioritized step.

**Rollback:**

- This slice produces additive artifacts (one report file, one script, one test, one DA record). Rollback is `git revert <commit>` plus a DA-record retirement (mark `outcome='retired'`, append rationale). No formal-spec mutations to undo.

## Acceptance Criteria

1. Audit report exists at the named path, contains all six dimensions evaluated, and contains a classification manifest covering every in-scope row (count matches the deterministic enumeration).
2. Audit script is deterministic (verified by test) and read-only (verified by test).
3. Audit script test passes (`pytest tests/scripts/test_audit_early_project_requirements.py -q`).
4. No `specifications`-table rows are touched (`version > 1` insertion count = 0 in the audit-execution commit, verified by post-impl diff).
5. DA record inserted with a formal-artifact-approval packet present at `.groundtruth/formal-artifact-approvals/2026-05-14-early-project-requirements-audit-*.json`.
6. All `target_paths` are within `E:\GT-KB`; no external paths.
7. Classification manifest uses ONLY the five canonical states from §"Output classification states".
8. Post-implementation report carries forward the Test Mapping table with observed results for each row.

## Verification Plan

1. **Pre-implementation (Codex Loyal Opposition review of this proposal):**
   - Verify `Specification Links` cites every applicable cross-cutting spec.
   - Verify the preflight result embedded below.
   - Verify the `Clause Scope Clarification (Not a Bulk Operation)` evidence tokens (`inventory`, `formal-artifact-approval`) appear and the rationale is substantive.
   - Verify the audit scope is genuinely bounded (single deliverable bundle; no implementation-class commitments).
2. **Implementation execution:**
   - Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping` after Codex GO.
   - Implement audit script and test under `target_paths`.
   - Execute audit; produce report; produce DA approval packet; insert DA record.
3. **Post-implementation (Codex VERIFIED review):**
   - Codex verifies each row of the Test Mapping table.
   - Codex spot-checks 5–10 classification manifest rows against the cited rationale.
   - Codex confirms no formal-spec mutations occurred (diff `specifications` table).
   - Codex issues `VERIFIED` only if all acceptance criteria pass; otherwise `NO-GO` with specific findings.

## Bridge Filing and INDEX Convention

This proposal file is filed under `bridge/` per the file-bridge-protocol authority model (`GOV-FILE-BRIDGE-AUTHORITY-001`). It is append-only; no prior version is deleted or rewritten. The corresponding INDEX update — inserting a new `Document:` entry at the top of `bridge/INDEX.md` with the line `NEW: bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-001.md` — is the owner's pending action per the parallelize-priority-backlog directive. The INDEX entry is the canonical workflow-state record for this thread; the proposal file itself is the auditable artifact. No version of this thread will be removed from disk.

## Applicability Preflight

The mechanical preflight executes against this proposal's INDEX entry once filed. For Codex Loyal Opposition's pre-review check the expected result is:

```
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

This proposal cites every required cross-cutting spec listed in `config/governance/spec-applicability.toml` per the path patterns triggered (`bridge/**`, the in-body presence of `Specification Links`, `implementation proposal`, `bridge proposal`, `VERIFIED`, `verification`, `Specification-Derived Verification`, `owner decision`, `requirement`, `specification`, `ADR`, `DCL`, `work item`, `backlog`, `artifact`, `traceability`, `deliberation`, `MemBase`, `candidate`, `deferred`, `blocked`, `superseded`, `verified`, `retired`). The advisory rules (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) are also cited explicitly above.

The clause preflight (`scripts/adr_dcl_clause_preflight.py`) is advisory-only per Slice 1 of `gtkb-adr-dcl-clause-test-enforcement`; the §"Clause Scope Clarification (Not a Bulk Operation)" section addresses the historical bulk-ops false-positive pattern with the required evidence tokens.

End of proposal.
