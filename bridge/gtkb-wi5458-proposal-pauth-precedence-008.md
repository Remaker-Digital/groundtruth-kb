NO-GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5458-proposal-pauth-precedence
Version: 008
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-007.md
Date: 2026-07-19 UTC
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Verification Verdict - NO-GO - WI-5458 Proposal PAUTH Precedence

## Verdict

NO-GO. The implemented ranking logic is useful and the focused tests pass, but the work item and governing PAUTH surface still require a validated explicit project-authorization selector for equal-rank ambiguity and a currentness check that excludes expired status-active authorizations before proposal filing. The implementation has neither path, so it cannot be treated as a verified repair for proposal-authority selection.

## First-Line Role Eligibility Check

- Role authority for this interactive session: Loyal Opposition by Mike's direct current-chat assignment.
- Verdict status: `NO-GO`, a Loyal Opposition verification status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Implementation report author session context: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.
- GO reviewer session context: `6863e929-50d6-4dc2-8bd0-6f2295e0f562`.
- The author and reviewer session contexts are present and distinct; review independence passes.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence --content-file bridge/gtkb-wi5458-proposal-pauth-precedence-007.md --json
```

Result:

- packet_hash: `sha256:f4b27a5b326844091caf9b297cbc84f3b168d8b8fcb5231d4969b198b9adc60e`
- bridge_document_name: `gtkb-wi5458-proposal-pauth-precedence`
- content_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-007.md`
- operative_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-007.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:c11efb45a84e6b863fb9eeef7bfb939b14316fcc341614138c402ec1453cd7d8`

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence
```

Result:

- Bridge id: `gtkb-wi5458-proposal-pauth-precedence`
- Operative file: `bridge\gtkb-wi5458-proposal-pauth-precedence-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: 0

## Prior Deliberations

- `DELIB-20266083` - owner decision establishing restrictive `included_work_item_ids` semantics.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded owner-authorized defect-remediation envelope.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - durable prohibition on dispatcher-configuration mutation during this work.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-002.md` - prior NO-GO requiring deterministic PAUTH precedence and fail-closed ambiguity behavior.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-004.md` - prior NO-GO for undisclosed sibling-claimant ordering.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-006.md` - GO for the revised v005 proposal, with the explicit-selector/currentness risk still left to implementation verification.

## Specifications Carried Forward

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Static review of CLI request surface and filing request data model | yes | FAIL: no explicit requested PAUTH can be supplied or validated |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | `python -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short` | yes | PASS for automatic specificity ranking; not sufficient for ambiguity override |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | `gt spec show DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 --json` plus static review | yes | FAIL: proposal filing does not bind expiration/currentness or a requested PAUTH before publishing |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation report start evidence and target review | yes | No independent implementation-start blocker found |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain read via `show_thread_bridge.py` | yes | PASS: v007 is latest verifier-actionable report |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight and generated metadata review | yes | Partial: selected PAUTH is disclosed, but requested PAUTH cannot be enforced |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight plus currentness-DCL review | yes | FAIL: v007 does not cite the operation-time PAUTH enforcement DCL despite touching its proposal-filing enforcement point |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5458-proposal-pauth-precedence --dry-run --json` | yes | `verified_overall=false`; several specs have no derived tests |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | v007 project-order evidence review | yes | No independent blocker found |
| `GOV-STANDING-BACKLOG-001` | `gt backlog list --id WI-5458 --json` | yes | FAIL: current work item still records the explicit-selector/currentness revision as required |
| `ADR-CROSS-HARNESS-PARITY-001` | Shared service path review | yes | No harness-specific branch introduced |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Shared CLI/service tests | yes | No independent parity blocker found beyond missing selector/currentness |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Work item, report, PAUTH, and test traceability review | yes | Blocked by acceptance mismatch |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Bridge chain and implementation report review | yes | Blocked by acceptance mismatch |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge lifecycle review | yes | PASS; latest remains verifier-actionable until this verdict |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path review | yes | PASS; changed paths are in-root |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped git status and focused checks | yes | PASS for reviewed target scope amid unrelated dirt |

## Positive Confirmations

- Bridge chain is coherent: v001 `NEW`, v002 `NO-GO`, v003 `REVISED`, v004 `NO-GO`, v005 `REVISED`, v006 `GO`, v007 implementation-report `NEW`.
- Applicability preflight passes with `missing_required_specs: []`.
- Mandatory clause preflight passes with zero blocking gaps.
- Focused pytest for `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` passes: `20 passed`.
- Ruff check passes on the three target files.
- Ruff format check passes on the three target files.
- The implementation usefully ranks exact singleton PAUTH coverage ahead of broader explicit lists and unrestricted project fallback.

## Findings

### F1 - P1 - No explicit validated PAUTH selector exists, so equal-rank ambiguity remains unrecoverable

Observation: The CLI command surface for `file-implementation-proposal` declares options at `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py:348` through `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py:365`; it has `--wi`, `--slug`, `--target-path`, `--project`, and other metadata options, but no `--project-authorization` or equivalent selector. The command function signature at `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py:374` through `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py:390` likewise has no parameter that can carry a requested authorization. The service request model at `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:53` through `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:68` has no requested-authorization field.

Current behavior: `_active_authorization_for_work_item()` gathers automatic candidates at `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:168` through `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:175`, sorts them, and raises `ProposalFilingError` on equal best rank at `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:183` through `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:191`. The focused ambiguity test confirms fail-closed publication behavior at `platform_tests/groundtruth_kb/test_cli_bridge_propose.py:353` through `platform_tests/groundtruth_kb/test_cli_bridge_propose.py:382`, but no adjacent test proves a validated explicit selector can resolve the ambiguity.

Deficiency rationale: WI-5458's current canonical backlog record requires the resolver to "fail closed when multiple candidates are equally most-specific unless an explicit validated selector is provided" and states that the current candidate "still exposes no validated --project-authorization selector in cli_bridge_propose.py." Version 007 claims the residual behavior is intentional fail-closed ambiguity at `bridge/gtkb-wi5458-proposal-pauth-precedence-007.md:217` through `bridge/gtkb-wi5458-proposal-pauth-precedence-007.md:220`, but that only implements half of the requirement: it denies ambiguous rows and provides no governed way to select the intended current PAUTH.

Required revision: add an explicit selector, preferably `--project-authorization`, and carry it through `FilingRequest` into the resolver. Validate that the selected authorization exists, is current, active, unexpired, not superseded, belongs to the same project envelope, covers the requested WI/spec set, permits the requested operation and target classes, and exactly matches the selected candidate before any proposal content, preflight, writer, or bridge file side effect. Add success, unknown, stale/expired, cross-project, non-covering, ambiguity-override, help text, JSON output, text output, and no-side-effect failure tests.

### F2 - P1 - Automatic proposal filing still does not exclude expired status-active PAUTH rows or bind operation-time currentness

Observation: `_active_authorization_for_work_item()` iterates `db.list_project_authorizations(project_id, status="active")` at `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:175`. The database helper applies only project and status filters at `groundtruth-kb/src/groundtruth_kb/db.py:5685` through `groundtruth-kb/src/groundtruth_kb/db.py:5695`; its own docstring names terminal/expired records at `groundtruth-kb/src/groundtruth_kb/db.py:5675` through `groundtruth-kb/src/groundtruth_kb/db.py:5681`, but the query does not check `expires_at` or supersession/currentness. By contrast, the implementation-start validator rejects expired authorizations at `scripts/implementation_authorization.py:1097` through `scripts/implementation_authorization.py:1101`.

Governing requirement: `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` states that bridge proposal filing must validate the cited authorization, work item, specifications, requested operation, and every active target path before filing or publishing bridge state. Its required inputs include authorization status, expiration, supersession state, requested operation, target paths, acting session/role, evaluator version, decision time, and currentness evidence. Version 007's cited-spec list from the applicability preflight omits this DCL, and the report's verification plan at `bridge/gtkb-wi5458-proposal-pauth-precedence-007.md:124` through `bridge/gtkb-wi5458-proposal-pauth-precedence-007.md:141` does not map it.

Deficiency rationale: A status-active but expired PAUTH can remain a candidate for automatic selection, and a requested explicit selector cannot be rejected for currentness because no selector path exists. That leaves proposal filing weaker than the operation-time enforcement contract and weaker than implementation-start validation.

Required revision: make proposal filing use the same currentness semantics as the canonical PAUTH evaluator or a shared helper. Automatic ranking must exclude or deny expired/stale/superseded status-active rows before ranking; explicit selection must fail closed on the same currentness inputs; and tests must prove denied currentness creates no proposal content, no preflight invocation, no writer call, and no bridge file.

## Required Revisions

1. Add and document an explicit PAUTH selector for proposal filing, wired through CLI, service request, resolver, generated metadata, dry-run output, live output, and tests.
2. Validate explicit selections against existence, active/unexpired/current version, supersession, same project envelope, WI/spec coverage, requested operation, and target mutation classes before side effects.
3. Exclude or deny expired/stale/superseded status-active rows in automatic ranking before choosing the best candidate.
4. Add focused regressions for selector success, unknown selector, expired/stale selector, cross-project selector, non-covering selector, ambiguity override, help/output disclosure, and no-side-effect denial.
5. Revise the implementation report to cite and map `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, then rerun focused tests, Ruff check, Ruff format check, applicability preflight, clause preflight, and spec-derived verification.

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5458-proposal-pauth-precedence --format json --preview-lines 20
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence --content-file bridge/gtkb-wi5458-proposal-pauth-precedence-007.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5458-proposal-pauth-precedence --dry-run --json
python -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
gt backlog list --id WI-5458 --json
gt spec show DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 --json
rg -n -- "--project-authorization|project_authorization|project-authorization|FilingRequest|list_project_authorizations|expires|expired|DCL-PROJECT-AUTHORIZATION-OPERATION" groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/src/groundtruth_kb/db.py scripts/implementation_authorization.py bridge/gtkb-wi5458-proposal-pauth-precedence-007.md
```

Observed key outputs:

```text
Applicability preflight: preflight_passed=true; missing_required_specs=[]; blocking_errors=[]
Clause preflight: Blocking gaps (gate-failing): 0
Spec-derived dry run: verified_overall=false
Focused pytest: 20 passed
Ruff check: All checks passed!
Ruff format: 3 files already formatted
```

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, gtkb-verify
