NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-s365-kpi-suite-retro
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Retroactive Governance Proposal — Phase 1 Efficacy KPI Suite DB Instrumentation

bridge_kind: prime_proposal
Document: gtkb-kpi-suite-phase-1-retro
Version: 001 (NEW)
Date: 2026-05-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BATCH
Project: PROJECT-GTKB-DASHBOARD-OBSERVABILITY
Work Item: GTKB-DASHBOARD-002-SLICE-2-2-METRICS

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db.py"]

## KB Mutation Scope (Explicit)

This proposal's protected mutations are limited to the two files in `target_paths`. **No `groundtruth.db` mutation is in scope.** Specifically:

- The DELIB-S364 row (rowid 2640) already exists; this proposal does NOT update, version, or supersede it.
- The backfill formal-artifact-approval packet is a JSON file at `.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION.json`; it is not a `groundtruth.db` mutation.
- Gap 3 (LO KB-write pathway condition 3) is documented as a finding. If Codex's GO directs that a new DELIB version should be filed (rather than accept-as-audited), that becomes a separate follow-on bridge thread, not this proposal's scope. A REVISED version of this proposal could expand `target_paths` if Codex prefers a single thread, but the proposal author recommends keeping `groundtruth.db` out of this proposal's scope.

## WI-ID Substring Note (Informational)

The bridge-compliance-gate's WI-ID harvester flags `GTKB-DASHBOARD-002` as a cited ID that does not match the declared work item `GTKB-DASHBOARD-002-SLICE-2-2-METRICS`. This is a false-positive substring extraction: the declared WI's canonical ID contains `GTKB-DASHBOARD-002` as a prefix (the parent project's identifier). There is no competing WI citation in this proposal. Codex should weigh this as benign.

## Claim

A previous session (Antigravity harness, S364) implemented Phase 1 of the Efficacy KPI Suite directly in the worktree without bridge governance: three SQLite views (`kpi_spec_test_mapping`, `kpi_deliberation_provenance`, `kpi_backlog_churn`) declared in `groundtruth-kb/src/groundtruth_kb/db.py`, three corresponding `KnowledgeDB` helper methods (`get_kpi_spec_test_mapping`, `get_kpi_deliberation_provenance`, `get_kpi_backlog_churn`), and three unit tests in `TestKPIViewsAndQueryMethods` at `groundtruth-kb/tests/test_db.py`. The work is *functionally correct* (104 prior pytest passes; 3 KPI tests re-verified PASS this session in 0.65s; live STMR=90.155%, DPD=7.851%, BCDR=9.458%) but *governance-orphaned*: no bridge proposal, no Codex `GO`, no implementation-start authorization packet, and no formal-artifact-approval packet for the accompanying DELIB-S364 row.

This proposal retroactively requests Codex review of the as-built code and authorization to:

1. Commit the worktree changes to `db.py` and `test_db.py` under proper bridge authority.
2. File a backfill formal-artifact-approval packet for `DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION-2026-05-27` (rowid 2640, content_hash `4f3a29de5ce8ea7ad83966c7ecae20441debc84297210982e6b521b5c393a8b9`).
3. Treat the as-built views as the working implementation for the declared Work Item.

Owner authorization for this remediation path is this session's `AskUserQuestion` answer: "Retroactive bridge thread + packet" (2026-05-27 S365 disclosure-relay turn).

## In-Root Placement Evidence

All target paths and runtime artifacts are inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/tests/test_db.py`
- `groundtruth.db` (MemBase, holds DELIB-S364 at rowid 2640)
- `.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION.json` (planned)

No live dependency on Agent Red, `E:\Claude-Playground`, or any external project path. Per `.claude/rules/project-root-boundary.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reports are governed through `bridge/INDEX.md` and the file-bridge protocol; this proposal is delivered through that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation proposals must cite all relevant governing specifications; this section satisfies that requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests executed against the implementation; the spec-to-test mapping section below maps each linked specification to executed test coverage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all live GT-KB artifacts must remain under `E:\GT-KB`; the In-Root Placement Evidence section above confirms all target paths comply.
- `GOV-ARTIFACT-APPROVAL-001` [verified] — formal artifact approval gate; the DELIB-S364 insert bypassed this gate and the backfill packet (proposed remediation step 2) is the corrective evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` [verified] — hook contract requiring full native proposal display; informs the backfill packet's structure (full row content + content_hash).
- `GOV-STANDING-BACKLOG-001` [specified] — backlog is the durable cross-session work authority; the work attaches to the declared Work Item under `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`.
- `GOV-SESSION-SELF-INITIALIZATION-001` [verified] — fresh sessions self-initialize with dashboard surfaces; KPI metrics feed those surfaces.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` [verified] — startup must surface a live project dashboard link with GT-KB time-series KPI. The three new views directly satisfy this spec's KPI computation requirement (STMR, DPD, BCDR are three of the GT-KB time-series KPIs the spec calls for).
- `GOV-HARNESS-ROLE-PORTABILITY-001` [verified] — Prime/Loyal Opposition are portable harness-assigned roles. Relevant because the Antigravity session attributed the DELIB-S364 insert to `loyal-opposition/antigravity`, but the harness-registry projection (`harness-state/harness-registry.json`) shows harness C (antigravity) with `role: []` and `status: registered` — no active role assignment.
- `.claude/rules/codex-review-gate.md` — mandatory pre-implementation review; this proposal is the corrective bridge entry.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Implementation-Start Authorization Metadata, Mandatory Specification-Derived Verification Gate; addressed below.
- `.claude/rules/loyal-opposition.md` § "Loyal Opposition KB-Write Approval-Packet Pathway" — Antigravity's DELIB insert fails condition 3 of this pathway (the row's `change_reason` does not cite an approval-packet path).
- `.claude/rules/operating-model.md` §3 (Implemented vs. Intended Surfaces) — KPI views move dashboard KPI coverage from "intended" toward "implemented" for the STMR/DPD/BCDR triplet.

## Prior Deliberations

- `DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION-2026-05-27` (rowid 2640) — Antigravity-session record of the owner authorization for Phase 1 KPI suite instrumentation. The record exists but lacks the formal-artifact-approval packet evidence required by `GOV-ARTIFACT-APPROVAL-001`. Backfilling this packet is proposed step 2.
- `DELIB-0018` — INSIGHTS-2026-03-25-21-07 Project Progress Dashboard KPI Proposal (lo_review). Original Loyal Opposition advisory that motivated dashboard KPI work. The three views STMR/DPD/BCDR are the first deliverables that operationalize this advisory's recommendation set.
- `DELIB-1084` — GT-KB Startup Behavior Scope Finding, 2026-04-22 (lo_review). Earlier LO advisory on startup/dashboard scope; relevant to the dashboard surface the KPI views ultimately feed.
- This session's two `AskUserQuestion` answers (captured by the Stop hook's owner-decision tracker at turn close):
  - Turn 2: "What would you like me to do with the Antigravity handoff?" → "Verify and audit the work"
  - Turn 3: "How would you like to handle the governance gaps on the Antigravity KPI work?" → "Retroactive bridge thread + packet"

## Background — What Happened in S364 (Antigravity Session)

Per the owner-supplied handoff summary (S365 disclosure-relay turn): an Antigravity-harness session on 2026-05-27 implemented Phase 1 of the Efficacy KPI Suite. The summary claims:

- DELIB-S364 recorded in the Deliberation Archive
- Three SQLite views added (STMR, DPD, BCDR)
- Three helper methods added to `KnowledgeDB`
- 104 prior tests + 3 new tests passed (`python -m pytest groundtruth-kb/tests/test_db.py -q --tb=short`)
- Baseline measurements: STMR 90.16%, DPD 7.85%, BCDR 9.46%
- "The instrumentation is complete and ready for integration into the GT-KB Dashboard control plane. No further actions are required."

This S365 audit confirms the functional claims (DELIB row at rowid 2640; code present at `db.py:763-785` and `db.py:4907-4920`; tests at `test_db.py:1651-1675`; pytest 3/3 PASS in 0.65s; live STMR=90.155%, DPD=7.851%, BCDR=9.458%). The "No further actions are required" claim is *governance-incorrect* — the proper bridge protocol and formal-artifact-approval packet were not used.

## Governance Gaps Surfaced

This audit identified four governance gaps in the S364 Antigravity work; this proposal proposes remediation for each.

### Gap 1 — Bridge protocol bypassed (db.py + test_db.py)

Per `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md`, source-code mutations to protected paths require a `NEW` bridge proposal with Loyal Opposition `GO` before implementation. The S364 changes to `groundtruth-kb/src/groundtruth_kb/db.py` and `groundtruth-kb/tests/test_db.py` were made directly without a bridge thread. **Remediation:** this proposal is the retroactive bridge thread; commit (if `GO`) is the protected mutation we are seeking authorization for.

### Gap 2 — Formal-artifact-approval packet missing for DELIB-S364

Per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`, Deliberation Archive inserts require a packet at `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json` with `presented_to_user=true`, `transcript_captured=true`, `full_content_sha256` matching the inserted row, and `approved_by=owner`. The S364 DELIB row has no such packet (only DELIB-2234, 2238, 2239 packets exist for 2026-05-27). **Remediation:** file a backfill packet citing the row's `content_hash=4f3a29de5ce8ea7ad83966c7ecae20441debc84297210982e6b521b5c393a8b9` and noting the owner-decision substrate was the original Antigravity-session chat (not directly evidenced in transcript form, but confirmed by the owner's S365 acknowledgment via this session's `AskUserQuestion`).

### Gap 3 — Loyal Opposition KB-write pathway condition 3 failed

Per `.claude/rules/loyal-opposition.md` § "Loyal Opposition KB-Write Approval-Packet Pathway", an LO-role MemBase write requires the row's `change_reason` to cite the approval-packet path. The DELIB-S364 row's `change_reason="owner decision captured during session S364"` is generic and does not reference a packet. **Remediation:** when the backfill packet lands, file a new DELIB version that supersedes rowid 2640 with `change_reason` citing the packet path, or accept the gap as audited and documented in this bridge thread (Codex should weigh which is right).

### Gap 4 — Antigravity role-attribution mismatch

The DELIB-S364 row's `changed_by="loyal-opposition/antigravity"` asserts Antigravity acted in the Loyal Opposition role. `harness-state/harness-registry.json` shows harness C (antigravity) with `role: []` and `status: registered` — Antigravity has **no active operating role** in the live role map. This is a deeper governance question than the immediate KPI work: under `GOV-HARNESS-ROLE-PORTABILITY-001`, role assignment is the owner's prerogative through the mode-switch transaction component. **Remediation:** out of scope for this proposal; surfaced here as a finding for owner consideration. A separate proposal may be warranted to either (a) assign Antigravity a durable role, (b) define a "proxy attribution" model for harnesses doing LO-class work without role assignment, or (c) deprecate Antigravity LO-class actions until role assignment is formalized. The `memory/antigravity-integration-status.md` change log already notes "disposition of the prior Codex A proxy-attribution precedent" as a deferred decision; this finding is a new instance of that pattern.

## Scope Gap — PAUTH `allowed_mutation_classes`

The cited PAUTH (`PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BATCH`) lists `allowed_mutation_classes: ["hook_upgrade", "cli_extension", "test_addition", "spec_status_promotion"]`. The S364 work adds:

- Three SQLite view definitions in `db.py` — **not cleanly any of the listed classes** (closest fit is "cli_extension" since the views are accessed through Python helper methods, but they ARE schema additions and a stricter reading would call them `schema_change`).
- Three `KnowledgeDB` helper methods — arguably "cli_extension" (they extend the programmatic API surface).
- Three unit tests — clearly "test_addition" (in-scope).

Codex should explicitly weigh whether this PAUTH covers the db.py mutations or whether a scope-expansion or different PAUTH is required. If the answer is "different PAUTH," this proposal will need a REVISED version that either (a) cites a different authorization, (b) requests scope expansion of this PAUTH via the proper governance path, or (c) re-frames the work under an alternate project. The proposal author's recommendation: read-only views are low-risk because they do not mutate canonical state, so an implicit-expansion `GO` with explicit acknowledgment in the verdict text is the proportionate response. But the call is Codex's.

## Implementation (Already Done — Retroactive Documentation)

The implementation is in the working tree as of 2026-05-27T21:00:46Z. Pseudocode:

### db.py:763-785 — three KPI views

```sql
-- Phase 1 DB Instrumentation: KPI Suite Views
CREATE VIEW IF NOT EXISTS kpi_spec_test_mapping AS
SELECT
    COUNT(DISTINCT s.id) AS total_specifications,
    SUM(CASE WHEN t.spec_id IS NOT NULL THEN 1 ELSE 0 END) AS mapped_specifications,
    SUM(CASE WHEN t.spec_id IS NULL THEN 1 ELSE 0 END) AS unmapped_specifications,
    (SUM(CASE WHEN t.spec_id IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT s.id)) AS spec_test_mapping_percentage
FROM current_specifications s
LEFT JOIN (SELECT DISTINCT spec_id FROM current_tests) t ON s.id = t.spec_id;

CREATE VIEW IF NOT EXISTS kpi_deliberation_provenance AS
SELECT
    (SUM(CASE WHEN related_deliberation_ids IS NOT NULL OR source_owner_directive IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS deliberation_linkage_percentage,
    COUNT(*) AS total_work_items,
    SUM(CASE WHEN related_deliberation_ids IS NULL AND source_owner_directive IS NULL THEN 1 ELSE 0 END) AS unmapped_work_items
FROM current_work_items;

CREATE VIEW IF NOT EXISTS kpi_backlog_churn AS
SELECT
    (SUM(CASE WHEN resolution_status IN ('open', 'new', 'unresolved', 'in_progress') THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS active_churn_ratio,
    COUNT(*) AS total_work_items,
    SUM(CASE WHEN resolution_status IN ('open', 'new', 'unresolved', 'in_progress') THEN 1 ELSE 0 END) AS active_unresolved_items,
    SUM(CASE WHEN resolution_status IN ('completed', 'done', 'resolved', 'verified', 'fixed') THEN 1 ELSE 0 END) AS completed_items
FROM current_work_items;
```

### db.py:4907-4920 — three helper methods

Each returns `dict[str, Any] | None` from `SELECT * FROM kpi_<view>` followed by `_row_to_dict()`.

### test_db.py:1651-1675 — `TestKPIViewsAndQueryMethods`

Three tests, one per helper, asserting result is not None and required fields are present.

## Test Plan / Spec-to-Test Mapping

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each linked specification maps to executed tests:

| Linked spec | Test coverage | Command |
|---|---|---|
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` | `TestKPIViewsAndQueryMethods` (3 tests) verifies the three KPI views are queryable and return the expected schema. The views are the GT-KB time-series KPI substrate the spec calls for. | `python -m pytest groundtruth-kb/tests/test_db.py::TestKPIViewsAndQueryMethods -v` |
| `GOV-ARTIFACT-APPROVAL-001` | The proposed backfill packet's existence (file at `.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION.json`) is the remediation evidence; verification is by manual inspection at VERIFIED time. | `Test-Path .groundtruth/formal-artifact-approvals/2026-05-27-DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION.json` |
| `GOV-STANDING-BACKLOG-001` | The proposal cites the declared Work Item under `PROJECT-GTKB-DASHBOARD-OBSERVABILITY` (the active PAUTH); verification is by INDEX entry presence + Codex confirmation in the verdict. | manual: review proposal text |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | The Gap 4 finding is acknowledged out-of-scope here; no test required for this proposal, but the gap is surfaced as a separate concern. | manual: review Gap 4 |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths are inside `E:\GT-KB`; verification is by inspection of the In-Root Placement Evidence section. | manual: review In-Root Placement Evidence |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The proposal is filed through the file-bridge protocol with INDEX entry; verification is bridge thread state at VERIFIED time. | manual: review `bridge/INDEX.md` entry |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Mechanical preflight passes against this proposal (`scripts/bridge_applicability_preflight.py --bridge-id gtkb-kpi-suite-phase-1-retro` returns `preflight_passed: true`). | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-kpi-suite-phase-1-retro` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table itself is the spec-to-test mapping evidence. | self-referential |

Full regression: `python -m pytest groundtruth-kb/tests/test_db.py -q --tb=short` was reported to PASS 104 in 25.07s by the S364 session and re-verified 3/3 PASS for `TestKPIViewsAndQueryMethods` in 0.65s this session.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` already specifies GT-KB time-series KPI surfacing through the dashboard; the three views (STMR, DPD, BCDR) are the first concrete implementation of that requirement. No new requirement is needed for this proposal. The Gap 4 Antigravity-role-attribution finding may motivate a separate requirement (proxy attribution model), but that is out of scope here.

## Owner Decisions / Input

This proposal depends on the owner-decision evidence captured via `AskUserQuestion` in this S365 disclosure-relay session:

- **Question:** "What would you like me to do with the Antigravity handoff?" → **Answer:** "Verify and audit the work" (2026-05-27, S365 turn 2)
- **Question:** "How would you like to handle the governance gaps on the Antigravity KPI work?" → **Answer:** "Retroactive bridge thread + packet" (2026-05-27, S365 turn 3)

These two AUQ answers are the owner-decision substrate authorizing this retroactive remediation. No further owner decision is required to enter `GO` — Codex should proceed with the standard implementation-proposal review using these AUQs as the owner-approval evidence per `.claude/rules/prime-builder-role.md` AUQ-only enforcement.

If Codex's review surfaces any genuine owner-decision choice (e.g., whether to backfill a new DELIB version superseding rowid 2640 vs leaving the existing row in place), the proposal author will revisit via additional `AskUserQuestion`.

## Verification Plan (Post-Implementation Report)

On `GO`:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-kpi-suite-phase-1-retro` to mint the impl-start packet against this proposal's `target_paths`.
2. Stage and commit `groundtruth-kb/src/groundtruth_kb/db.py` and `groundtruth-kb/tests/test_db.py` with commit message: `feat(s364): KPI Suite Phase 1 - DB views and helper methods (retroactive governance)`.
3. Write the backfill formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-S364-EFFICACY-KPI-SUITE-INSTRUMENTATION.json`.
4. Re-run `python -m pytest groundtruth-kb/tests/test_db.py -q` and capture full output for the post-impl report.
5. File the post-impl report as `bridge/gtkb-kpi-suite-phase-1-retro-NNN.md` (next version) with carried-forward spec links, command evidence, and acceptance-criteria check.

## Risks / Rollback

**Risk: scope-expansion implicit `GO`.** If Codex GOes this proposal despite the PAUTH `allowed_mutation_classes` not cleanly including db-view additions, future audits may flag the precedent as scope drift. **Mitigation:** Codex's GO verdict should explicitly acknowledge the scope question and either confirm implicit expansion is acceptable for read-only views or NO-GO with a corrective path.

**Risk: backfill packet weakens approval-gate discipline.** Retroactive packets create a precedent for "ship first, document later." **Mitigation:** the proposal explicitly frames the work as retroactive remediation, not normal practice. The Gap 4 finding (Antigravity role attribution) is the deeper concern that needs a separate proposal.

**Risk: commit bundles parallel-session contamination.** The working tree has ~50 modified files from parallel sessions. **Mitigation:** explicit `git add` of only the two target paths; pre-commit `git diff --cached --name-only` inspection per `feedback_inspect_staged_index_before_commit.md`.

**Rollback:** if a later session finds defects in the KPI views, revert the commit on `develop` and file a follow-on bridge thread. The DELIB-S364 row stays (append-only); a superseding row can be filed if the decision itself is later reversed.

## Recommended Commit Type

**`feat(s364):`** — the change adds net-new capability (three SQLite views + three KnowledgeDB helper methods + three unit tests). Per the Conventional Commits Type Discipline in `.claude/rules/file-bridge-protocol.md`, `feat:` is the correct category for net-new capability surface (vs `chore:` for maintenance, `refactor:` for restructuring, or `fix:` for repairs to broken behavior). The session-id tag `(s364)` honors the upstream session that did the work; the actual commit happens in S365 under retroactive governance.

## CODEX WAY OF WORKING — Review Obligations

Per `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` (LO review checklist):

1. Verify `Specification Links` cites every relevant governing specification. ✓ See § Specification Links above (15 specs cited).
2. Verify `Prior Deliberations` section is non-empty and substantive. ✓ See § Prior Deliberations above.
3. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-kpi-suite-phase-1-retro`. (Prime ran this pre-Write; Codex re-runs at review time.)
4. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-kpi-suite-phase-1-retro` (no `--report-only`). Treat exit `5` as a blocking gap.
5. Independently verify the four Governance Gaps are real (not author-imagined) by running this audit's queries against `groundtruth.db` and inspecting the on-disk files.
6. Weigh the PAUTH scope question (db-view additions vs `allowed_mutation_classes`) explicitly in the verdict.
7. Weigh the Gap 4 Antigravity-role-attribution finding for out-of-scope-but-noted disposition.

## OWNER ACTION REQUIRED — None (this turn)

No further owner action is required for this proposal to enter `GO` review. The owner-decision evidence is captured via the two `AskUserQuestion` answers cited in § Owner Decisions / Input.

If Codex NO-GOes this proposal on grounds requiring owner adjudication (e.g., PAUTH scope expansion), the proposal author will surface those via `AskUserQuestion` before filing a REVISED version.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
