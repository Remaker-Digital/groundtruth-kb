NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3211 Community Feedback Harvesting Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3211-community-feedback-harvesting-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3211

target_paths: ["groundtruth-kb/tests/test_community_feedback_spec1875.py"]

## Claim

WI-3211 should be implemented as a narrow package-level pytest backfill for `SPEC-1875` Community Feedback Harvesting Loop.

Current in-root GT-KB package artifacts already expose the community-feedback surfaces named by the spec:

- `groundtruth-kb/.github/ISSUE_TEMPLATE/bug_report.yml` exists as a structured GitHub issue form for toolkit bug reports.
- `groundtruth-kb/.github/ISSUE_TEMPLATE/feature_request.yml` exists as a structured GitHub issue form for improvement requests and method feedback.
- `groundtruth-kb/.github/pull_request_template.md` exists and asks contributors to describe problem, approach, rationale, and testing.
- `groundtruth-kb/CONTRIBUTING.md` links the bug and feature templates, defines the `method-feedback` label, and documents monthly triage into actionable, informational, or needs-discussion outcomes.
- `groundtruth-kb/README.md` points contributors to `CONTRIBUTING.md` and specifically calls out `method-feedback`.
- `groundtruth-kb/CODE_OF_CONDUCT.md` exists.
- `groundtruth-kb/.github/workflows/ci.yml` exists and runs ruff plus pytest in the package CI lane.

Existing tests do not map these community-feedback artifacts to `SPEC-1875`; `gt deliberations list --spec-id SPEC-1875` and `gt deliberations list --work-item-id WI-3211` returned no directly-linked deliberations, and `gt bridge threads --wi WI-3211 --json` returned `match_count: 0`. This proposal adds one deterministic structural test file under `groundtruth-kb/tests/` so the package CI can collect it naturally. It does not authorize documentation, workflow, or source edits. If the tests expose a source/docs drift, Prime Builder must stop and return through the bridge with a revised proposal rather than expanding target paths.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1875` is the governing implemented requirement. It identifies the public `groundtruth-kb` repository community loop: structured issue templates, PR template, `CONTRIBUTING.md` with `method-feedback` and monthly triage, `CODE_OF_CONDUCT.md`, GitHub Actions CI, and the publish/adopt/feedback/improve/publish loop. The live package artifacts above make those requirements concrete enough for a test-only structural coverage backfill.

No owner clarification is needed because this proposal tests accepted live repository infrastructure and does not alter community process semantics.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and GT-KB package test subtree:

- `E:\GT-KB\groundtruth-kb\tests\test_community_feedback_spec1875.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\groundtruth-kb\.github\ISSUE_TEMPLATE\bug_report.yml`
- `E:\GT-KB\groundtruth-kb\.github\ISSUE_TEMPLATE\feature_request.yml`
- `E:\GT-KB\groundtruth-kb\.github\pull_request_template.md`
- `E:\GT-KB\groundtruth-kb\.github\workflows\ci.yml`
- `E:\GT-KB\groundtruth-kb\CONTRIBUTING.md`
- `E:\GT-KB\groundtruth-kb\README.md`
- `E:\GT-KB\groundtruth-kb\CODE_OF_CONDUCT.md`

## Specification Links

- `SPEC-1875` - Direct requirement for community feedback harvesting loop repository infrastructure.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live package community templates, contributor docs, code of conduct, and CI workflow are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live files rather than rely on stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native test mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline changed-file hygiene; Python coverage will use targeted pytest plus ruff check and ruff format checks on the touched test file.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing AUQ-backed project authorization; no prose owner decision is requested by this proposal.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms application artifacts stay under `applications/Agent_Red/`; this WI intentionally targets the `groundtruth-kb/` package because `SPEC-1875` names the public GroundTruth repository surfaces, not Agent Red runtime artifacts.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3211`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying phantom-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0212` - S236 Prime Strategy Advisory Review identified the need for a concrete community-feedback harvesting loop, including feedback channels, issue/discussion taxonomy, contribution capture workflow, and normalization back into KB/work items/procedures.
- `gt deliberations list --spec-id SPEC-1875 --limit 10 --json` returned `[]`; no spec-linked deliberation entries exist for `SPEC-1875`.
- `gt deliberations list --work-item-id WI-3211 --limit 10 --json` returned `[]`; no WI-linked deliberation entries exist for `WI-3211`.
- `gt bridge threads --wi WI-3211 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3211 --json` shows open/backlogged `WI-3211`, source spec `SPEC-1875`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1875 --json` shows title "Community Feedback Harvesting Loop", status `implemented`, and description naming structured issue templates, PR template, `CONTRIBUTING.md` with `method-feedback` and monthly triage, `CODE_OF_CONDUCT.md`, GitHub Actions CI, and the feedback loop.
- `groundtruth-kb/tests/test_community_feedback_spec1875.py` does not currently exist.
- `groundtruth-kb/.github/ISSUE_TEMPLATE/bug_report.yml` and `feature_request.yml` exist and can be parsed by the same `yaml.safe_load` dependency already used by existing `groundtruth-kb/tests/test_azure_cicd_scaffold.py` and `groundtruth-kb/tests/test_scaffold_ci_tiers.py`.
- `groundtruth-kb/.github/pull_request_template.md`, `groundtruth-kb/CONTRIBUTING.md`, `groundtruth-kb/README.md`, and `groundtruth-kb/CODE_OF_CONDUCT.md` exist.
- `groundtruth-kb/.github/workflows/ci.yml` exists and includes package lint/test commands; tests under `groundtruth-kb/tests/` are collected by the existing package pytest lane.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3211-community-feedback-harvesting-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `warnings.missing_parent_dirs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3211-community-feedback-harvesting-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `groundtruth-kb/tests/test_community_feedback_spec1875.py`.
2. In the new pytest file, parse `groundtruth-kb/.github/ISSUE_TEMPLATE/bug_report.yml` and assert it is a structured GitHub issue form with bug label, required component, expected, actual, and reproduction fields.
3. Parse `groundtruth-kb/.github/ISSUE_TEMPLATE/feature_request.yml` and assert it is a structured GitHub issue form with enhancement label and required problem, approach, and scope fields.
4. Read `groundtruth-kb/.github/pull_request_template.md` and assert it asks for problem, approach, rationale, testing, and assertion/test evidence.
5. Read `groundtruth-kb/CONTRIBUTING.md` and assert it links the YAML issue templates, defines `method-feedback`, says the label is triaged monthly, and documents actionable/informational/needs-discussion triage outcomes that feed specs or work items.
6. Read `groundtruth-kb/README.md` and assert it points contributors to `CONTRIBUTING.md` and `method-feedback`.
7. Read `groundtruth-kb/CODE_OF_CONDUCT.md` and assert the code of conduct exists with community scope and reporting contact language.
8. Parse or read `groundtruth-kb/.github/workflows/ci.yml` and assert the package CI runs ruff and pytest so the feedback-loop repository infrastructure is guarded by GitHub Actions.
9. Keep implementation test-only unless the test exposes a current artifact drift; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1875` | New pytest verifies the structured bug/feature issue templates, PR template, `method-feedback` contributor loop, monthly triage documentation, code of conduct, README contributor pointer, and package CI workflow. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic spec-mapping test file, using live in-repository package artifacts. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3211-community-feedback-harvesting-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, and whitespace diff checks on the touched Python test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest groundtruth-kb/tests/test_community_feedback_spec1875.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_registry_schema_and_ci.py groundtruth-kb/tests/test_community_feedback_spec1875.py -q --tb=short
python -m ruff check groundtruth-kb/tests/test_community_feedback_spec1875.py
python -m ruff format --check groundtruth-kb/tests/test_community_feedback_spec1875.py
git diff --check -- groundtruth-kb/tests/test_community_feedback_spec1875.py
```

## Acceptance Criteria

- PASS when the new pytest verifies both structured issue templates parse as YAML and contain required feedback fields.
- PASS when the new pytest verifies the PR template captures problem, approach, rationale, and testing/assertion evidence.
- PASS when the new pytest verifies `CONTRIBUTING.md` links the issue templates, defines `method-feedback`, and documents monthly triage outcomes that feed specifications or work items.
- PASS when the new pytest verifies `README.md` points contributors toward `CONTRIBUTING.md` and `method-feedback`.
- PASS when the new pytest verifies `CODE_OF_CONDUCT.md` exists with community scope and reporting contact language.
- PASS when the new pytest verifies the package GitHub Actions CI workflow runs ruff and pytest.
- PASS when targeted pytest, adjacent package meta-test pytest, ruff check, ruff format check, and diff whitespace checks all pass.
- PASS when no source edits, existing-test rewrites, documentation changes, workflow changes, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low. The proposal adds deterministic structural coverage for repository-community artifacts. It does not contact GitHub, create labels, inspect live issue state, or validate monthly triage execution in production. It verifies that the intended capture path is present in the package repository artifacts and protected by package CI.

Rollback is to delete `groundtruth-kb/tests/test_community_feedback_spec1875.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `groundtruth-kb/tests/test_community_feedback_spec1875.py`

## Recommended Commit Type

`test:`
