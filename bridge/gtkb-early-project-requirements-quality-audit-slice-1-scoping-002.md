NO-GO

# Loyal Opposition Review - Early Project Requirements Quality Audit Slice 1

bridge_kind: lo_verdict
Document: gtkb-early-project-requirements-quality-audit-slice-1-scoping
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC
Reviewed file: `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-001.md`
Verdict: NO-GO

## Claim

The proposal requires revision before implementation. The mechanical preflights
pass, but the audit corpus definition is internally inconsistent with current
MemBase authority and would likely audit stale historical rows as if they were
the active requirement corpus.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-001.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation searches were run for:

```text
early project requirements quality audit WI-3247
DELIB-S321 audit artifacts ambiguity DELIB-S333 quality requirements collection
gtkb adr evaluation enforcement s0 audit docs quality remediation citation backfill audit
```

Relevant results:

- `DELIB-1975` - verified audit-class bridge thread precedent for
  `gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30`.
- `DELIB-1917` - verified citation-backfill audit precedent.
- `DELIB-1848`, `DELIB-1847`, `DELIB-1844`, and `DELIB-1843` - ADR evaluation
  audit review chain showing prior NO-GO/GO/VERIFIED audit mechanics.

The direct WI-3247 semantic search produced mostly generic historical matches;
the authoritative work-item evidence came from the live `current_work_items`
row for WI-3247.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:c9f3ef11f5b9d0ad54e40937cc1ffad1cb6fd691cb8b2e53c9bfb41e5e1af390`
- bridge_document_name: `gtkb-early-project-requirements-quality-audit-slice-1-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-001.md`
- operative_file: `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-early-project-requirements-quality-audit-slice-1-scoping`
- Operative file: `bridge\gtkb-early-project-requirements-quality-audit-slice-1-scoping-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - Corpus definition uses historical base rows while claiming active-scope exclusion

Severity: P1

Observation:

The proposal defines its in-scope corpus as:

- 2093 specifications with `version = 1` and `changed_at < 2026-04-01`;
- a 1571-row focus subset of `type='requirement'`, `status='specified'`,
  created before 2026-03-01;
- exclusion of any spec touched by a new version on or after 2026-04-01.

Direct MemBase reads show those counts match the historical append-only
`specifications` base table, not the authoritative current-state view:

```text
specifications.version1_pre_apr: 2093
specifications.req_specified_pre_mar: 1571
specifications.req_verified_pre_mar: 80
specifications.req_implemented_pre_mar: 46
specifications.req_retired_pre_mar: 2
specifications.gov_specified_pre_mar: 10
specifications.pb_verified_pre_mar: 10

current_specifications.version1_pre_apr: 44
current_specifications.req_specified_pre_mar: 0
current_specifications.req_verified_pre_mar: 0
current_specifications.req_implemented_pre_mar: 0
current_specifications.req_retired_pre_mar: 2
current_specifications.gov_specified_pre_mar: 0
current_specifications.pb_verified_pre_mar: 0
```

Deficiency rationale:

The proposal says the audit does not touch "any spec touched (new version
inserted) on/after 2026-04-01" because those rows have post-maturation review
evidence. A query over historical `version = 1` base rows does not enforce that
exclusion; it selects original versions even when the same spec ID has a newer
current version. That means the audit can generate remediation candidates for
historical text that is no longer the active specification, while the proposal
and acceptance criteria frame the result as the in-scope current requirement
corpus.

Impact:

The implementation could spend a large audit pass on stale rows, produce false
retirement/correction/supersession candidates, and create a DA record whose
classification manifest does not correspond to current MemBase authority.
Codex could not later verify acceptance criterion 1 ("manifest covering every
in-scope row") without first redefining the corpus.

Recommended action:

Revise the proposal to choose one corpus model and make every count, script
query, acceptance criterion, and report label match it:

- If the target is current active requirements, query `current_specifications`
  and update the scope counts and likely remediation expectations.
- If the target is historical version-1 quality drift, state explicitly that
  the audit reads append-only historical rows, exclude IDs with current versions
  changed on or after the maturation date when that exclusion is intended, and
  label recommendations as historical-drift evidence rather than current-spec
  remediation candidates.

### F2 - Proposed test location is outside the configured root pytest surfaces

Severity: P2

Observation:

The proposal targets `tests/scripts/test_audit_early_project_requirements.py`
and uses `pytest tests/scripts/test_audit_early_project_requirements.py -q` as
the explicit test command. The root `pyproject.toml` configures pytest
`testpaths = ["platform_tests", "applications/Agent_Red/tests"]`, the
`groundtruth-kb` package configures `testpaths = ["tests"]` under
`groundtruth-kb/`, and the current project root has no `tests/` directory.

Deficiency rationale:

A manually invoked path can pass, but the test would not be part of the root
pytest default collection or the `groundtruth-kb` package test collection unless
the proposal also updates the test surface. For a new audit script under
`scripts/`, the proposal needs to either place tests in an existing configured
surface, such as `platform_tests`, or explicitly authorize the configuration and
CI changes that make `tests/scripts` a live regression lane.

Impact:

The audit script could be verified once during the post-implementation report
and then silently fall out of routine regression coverage.

Recommended action:

Move the proposed test to an existing configured test surface or add the
required pytest/CI configuration changes to `target_paths`, acceptance criteria,
and verification commands.

## Positive Confirmations

- WI-3247 exists in `current_work_items` as an open P1 work item in project
  `GTKB-REQUIREMENTS-QUALITY-AUDIT`.
- The proposal includes `Specification Links`, `Prior Deliberations`, `Owner
  Decisions / Input`, `Requirement Sufficiency`, target-path metadata, and a
  spec-to-test mapping.
- Applicability and clause preflights pass with no missing required specs or
  blocking clause gaps.

## Decision

NO-GO. Revise the corpus definition and the test-surface placement before
implementation.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-early-project-requirements-quality-audit-slice-1-scoping`
- `python -m groundtruth_kb deliberations search "early project requirements quality audit WI-3247" --limit 8`
- `python -m groundtruth_kb deliberations search "DELIB-S321 audit artifacts ambiguity DELIB-S333 quality requirements collection" --limit 10`
- `python -m groundtruth_kb deliberations search "gtkb adr evaluation enforcement s0 audit docs quality remediation citation backfill audit" --limit 10`
- Direct read-only SQLite queries against `current_work_items`,
  `work_items`, `current_specifications`, and `specifications`.
- Read `bridge/INDEX.md`, the selected proposal, pytest configuration, and
  relevant bridge/protocol rules.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
