NEW

# Post-Impl REPORT - GTKB-CI-COVERAGE-FOR-PLATFORM-001

Reported by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: `bridge/gtkb-ci-coverage-for-platform-001-003.md` REVISED-1; Loyal Opposition GO at `bridge/gtkb-ci-coverage-for-platform-001-004.md`
Requested bridge disposition: `VERIFIED`

## Claim

Dedicated GT-KB platform CI coverage is implemented.

- Added `.github/workflows/groundtruth-kb-tests.yml`.
- The workflow triggers on `groundtruth-kb/**`, its own workflow file, and `workflow_dispatch`.
- The workflow installs `./groundtruth-kb[dev,search]`.
- The workflow runs `python -m pytest tests/ -q --tb=short` from `groundtruth-kb`.
- The workflow uploads a JUnit pytest result artifact.
- Added static workflow tests in `tests/scripts/test_groundtruth_kb_tests_workflow.py`.

No GitHub settings, branch protection, required checks, secrets, release tags, PyPI publish, Agent Red migration, or external repository mutation were performed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed in `bridge/` and registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward required specs and release evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps CI tests to the cited release and bridge requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 37 of `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - CI evidence is durable and waiver state remains explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` - GT-KB platform tests are distinguished from Agent Red application tests.
- `.claude/rules/canonical-terminology.md` - GT-KB platform and Agent Red application surfaces are not conflated.
- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` - owner waived `python-tests.yml` as required-green for the GT-KB-only rc1 commit and created this GA follow-on.
- `bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md` - Codex F2 finding that surfaced workflow coverage ambiguity.
- `bridge/gtkb-ci-coverage-for-platform-001-003.md` - approved revised proposal.
- `bridge/gtkb-ci-coverage-for-platform-001-004.md` - Loyal Opposition GO.

## Owner Decisions / Input

Owner decision: `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER`.

- Waiver scope: applies to the `v0.7.0-rc1` Slice 8 / Slice 8.5 evidence chain because `python-tests.yml` targets Agent Red product paths and does not run `groundtruth-kb/tests/`.
- Expiry / retirement path: before `v0.7.0 GA`, future GT-KB-only release evidence should cite a dedicated platform workflow instead of the rc1 waiver.
- This implementation supplies that dedicated platform workflow.

This report does not retire the waiver by itself; retirement/narrowing should occur after the new workflow is green in GitHub Actions on a GT-KB platform commit.

## Workflow Binding

Workflow file: `.github/workflows/groundtruth-kb-tests.yml`

| Requirement | Implementation |
|---|---|
| GT-KB-only trigger | `pull_request` and `push` paths include `groundtruth-kb/**`. |
| Workflow self-trigger | Paths include `.github/workflows/groundtruth-kb-tests.yml`. |
| Manual trigger | `workflow_dispatch` is present. |
| Python version | `actions/setup-python@v5`, Python `3.12`. |
| Platform package install | `python -m pip install "./groundtruth-kb[dev,search]"`. |
| Platform test command | Working directory `groundtruth-kb`; command includes `python -m pytest tests/ -q --tb=short`. |
| Artifact | Uploads `groundtruth-kb/.pytest-results/groundtruth-kb-tests.xml`. |

No live GitHub Actions run URL is available in this local implementation turn because no push was performed. Static workflow validation and the local full platform test run are recorded below.

## Specification-Derived Verification

| Test ID | Spec coverage | Procedure | Result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` updated so this file is latest `NEW` | PASS |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ci-coverage-for-platform-001` | PASS - `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect report for waiver scope, expiry, and retirement path | PASS |
| T-platform-ci-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -m pytest tests/scripts/test_groundtruth_kb_tests_workflow.py -q --tb=short` | PASS - 2 passed |
| T-local-tests-1 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest tests/ -q --tb=short` from `groundtruth-kb` | PASS - 2028 passed, 1 skipped, 1 warning in 567.30s |
| T-lint-1 | CI quality guard | `python -m ruff check src tests` from `groundtruth-kb` | PASS - all checks passed |
| T-format-1 | CI quality guard | `python -m ruff format --check src tests` from `groundtruth-kb` | RESIDUAL - 24 pre-existing files would be reformatted; not caused by this workflow-only change and not bulk-formatted here to avoid touching unrelated dirty files |
| T-static-style-1 | New static workflow test style | `python -m ruff check tests/scripts/test_groundtruth_kb_tests_workflow.py` and `python -m ruff format --check tests/scripts/test_groundtruth_kb_tests_workflow.py` | PASS |

`T-format-1` residual files reported by ruff:

```text
src/groundtruth_kb/bridge/notify.py
src/groundtruth_kb/project/doctor.py
src/groundtruth_kb/project/scaffold.py
src/groundtruth_kb/project/upgrade.py
tests/test_bridge_poller_runner.py
tests/test_bridge_propose_helper.py
tests/test_cli.py
tests/test_doctor_bridge_poller.py
tests/test_doctor_canonical_terminology.py
tests/test_full_tree_type_checks.py
tests/test_governance_hooks.py
tests/test_internal_helpers_type_checks.py
tests/test_managed_registry.py
tests/test_owner_decision_tracker_regex_tightening.py
tests/test_owner_decision_tracker_structural_guards.py
tests/test_owner_decisions_section_gate.py
tests/test_pending_owner_decisions_audit.py
tests/test_public_api_type_checks.py
tests/test_release_gate_metrics.py
tests/test_scaffold_isolation.py
tests/test_spec_classifier_canonical_triggers.py
tests/test_spec_event_surfacer.py
tests/test_term_disambiguation.py
tests/test_upgrade_isolation.py
```

## Acceptance Criteria

- GT-KB-only commit trigger: satisfied statically by `groundtruth-kb/**` path filters.
- `groundtruth-kb/tests/` lane: satisfied by workflow command and local full test run.
- Manual dispatch: satisfied by `workflow_dispatch`.
- Waiver retirement path: preserved; future GitHub green run can retire/narrow `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER`.
- Live workflow URL: deferred until the next push or manual dispatch because this implementation did not push.

## Changed Files

- `.github/workflows/groundtruth-kb-tests.yml`
- `tests/scripts/test_groundtruth_kb_tests_workflow.py`
- `bridge/gtkb-ci-coverage-for-platform-001-005.md`
- `bridge/INDEX.md`
- `memory/work_list.md`

## Applicability Preflight

```text
packet_hash: sha256:01578d87b77f5b86b3ae7eadfc7ec00f77a3395cc01b8ba99d77161492dc14b8
bridge_document_name: gtkb-ci-coverage-for-platform-001
operative_file: bridge/gtkb-ci-coverage-for-platform-001-005.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```
