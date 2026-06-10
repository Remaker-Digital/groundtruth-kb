GO

bridge_kind: lo_verdict
Document: gtkb-project-completion-plan-incomplete-guard
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-06 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-project-completion-plan-incomplete-guard-001.md
Verdict: GO

# Loyal Opposition Review - Project Completion Plan-Incomplete Guard

## Verdict

GO.

The proposal is approved for implementation within the declared target-path
envelope. The defect is real, the proposed `plan_incomplete` guard is a narrow
and reversible suppression mechanism, and the verification plan covers both the
scanner and package lifecycle service paths that currently make automatic
completion decisions.

This GO does not authorize schema changes, production deployment, credential
lifecycle action, destructive cleanup, or history rewrite. If implementation
discovers that a separate guard-authoring/removal CLI or MemBase mutation is
needed, that must be filed through a separate bridge proposal or explicitly
covered in the implementation report with existing authorized surfaces.

## Review Scope

- Read live `bridge/INDEX.md` before acting. The selected document was still
  latest `NEW: bridge/gtkb-project-completion-plan-incomplete-guard-001.md`.
- Resolved durable role from `harness-state/harness-identities.json` and
  `harness-state/harness-registry.json`: Codex harness `A` is assigned
  `loyal-opposition`.
- Read the full thread version chain; only `-001` exists.
- Read bridge and review rules:
  `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Inspected the current completion decision code in
  `scripts/project_verified_completion_scanner.py` and
  `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`.
- Checked live project, work-item, and project-authorization state through the
  package venv.

## Prior Deliberations

Deliberation Archive searches were run before review:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3481 project verified completion plan_incomplete false positive retirement" --limit 8 --json
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "project completion scanner automatic retirement materialized slices plan incomplete" --limit 8 --json
```

Relevant results and live evidence:

- `memory/pending-owner-decisions.md:4914` through `:4923` records the S374
  owner AUQ where the project was prematurely retired because Slices 1-3 were
  VERIFIED while Slices 4-10 were not materialized; Mike selected
  `Reactivate + pre-bind all remaining slices`.
- `WI-3481` exists as an open defect with acceptance summary requiring either a
  scanner check against un-materialized slices or a documented project-level
  flag suppressing auto-completion until explicit completion confirmation.
- `DELIB-2275` and `DELIB-2276` preserve prior project-completion machinery
  review history and confirm that the automatic completion/retirement rule is
  real project lifecycle behavior, not a display-only surface.
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` confirms prior completion automation
  use for a verified authorization.
- No searched deliberation rejects an explicit, reversible project-level guard.

## Project And Authorization Checks

Read-only command evidence:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE --json
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-3481 --json
```

Observed:

- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE` is active.
- `WI-3481` is an active project work-item membership in that project.
- `PAUTH-GTKB-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001` is active and
  allows source and test mutations while forbidding production deploy,
  credential lifecycle, destructive cleanup, and history rewrite.
- `scripts/implementation_authorization.py:784` through `:793` shows the
  implementation-start validator accepts either an explicitly included work
  item or an active project membership, unless excluded. `WI-3481` satisfies
  the active-membership path.

## Applicability Preflight

- packet_hash: `sha256:14fbc2cdc44def40a060794676debf59f40d6904a7fa84fdd5fa76bd59a94aca`
- bridge_document_name: `gtkb-project-completion-plan-incomplete-guard`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-completion-plan-incomplete-guard-001.md`
- operative_file: `bridge/gtkb-project-completion-plan-incomplete-guard-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-project-completion-plan-incomplete-guard`
- Operative file: `bridge\gtkb-project-completion-plan-incomplete-guard-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

No blocking findings.

### Confirmation - The Current Completion Predicate Lacks The Guard

Observation: The scanner currently sets readiness with
`completion_ready = bool(included) and not unverified_ids` at
`scripts/project_verified_completion_scanner.py:223`; the package service
routes auto-completion through `_authorization_completion_ready()` and
`auto_complete_ready_authorizations()` at
`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:445`,
`:744`, and `:803`.

Impact: This matches the defect described by `WI-3481`: an incrementally
materialized project can look complete as soon as its currently materialized
members are verified.

Decision: The proposed `plan_incomplete` guard is a minimal correction because
it adds an explicit suppressor without weakening the base automatic-completion
rule for fully materialized projects.

### Confirmation - The Test Plan Maps To The Defect

Observation: The proposal requires scanner and lifecycle regressions for active
guards, inactive/superseded guards, and unguarded all-verified completion.

Impact: Those checks are sufficient for proposal approval. The
post-implementation report must provide executed command results for every
mapped check and must separately run `ruff check` plus `ruff format --check` on
changed Python files if Python files are changed.

## GO Conditions

Prime Builder may implement within:

- `scripts/project_verified_completion_scanner.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `platform_tests/scripts/test_project_verified_completion_scanner.py`
- `platform_tests/hooks/test_project_completion_surface.py`
- `groundtruth-kb/tests/test_project_artifacts.py`

The implementation report must show:

1. Active `plan_incomplete` guard suppresses scanner readiness.
2. Active `plan_incomplete` guard suppresses lifecycle auto-completion and
   project retirement.
3. Inactive or superseded guard rows do not suppress readiness.
4. Unguarded all-verified behavior remains unchanged.
5. Scanner JSON/text diagnostics make the guard visible to operators.
6. Exact pytest, ruff lint, ruff format, bridge applicability preflight, and
   ADR/DCL clause preflight results.

## Opportunity Radar

No separate advisory filed. The review did not reveal a new repeated manual
pattern beyond the defect already tracked by `WI-3481`; this GO directs the
deterministic fix into the implementation thread.

File bridge scan contribution: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
