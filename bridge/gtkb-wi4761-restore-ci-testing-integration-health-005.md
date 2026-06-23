REVISED

# gtkb-wi4761-restore-ci-testing-integration-health — Restore GitHub Actions CI/CD and testing integration health (REVISED-2)

bridge_kind: prime_proposal
Document: gtkb-wi4761-restore-ci-testing-integration-health
Version: 005
Author: Prime Builder (harness B, Claude)
Date: 2026-06-22 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-22T20-04-02Z-prime-builder-B-d49d27
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code auto-dispatch; resolved prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4761

target_paths: [
  "platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py",
  "platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py",
  "platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py",
  "platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py",
  "platform_tests/hooks/test_glossary_expansion.py",
  "platform_tests/hooks/test_owner_decision_tracker.py",
  "platform_tests/hooks/test_project_completion_surface.py",
  "platform_tests/hooks/test_workstream_focus.py",
  "platform_tests/scripts/test_active_session_heartbeat.py",
  "platform_tests/scripts/test_check_dev_environment_inventory_drift.py",
  "platform_tests/scripts/test_claude_session_start_dispatcher.py",
  "platform_tests/scripts/test_collect_dev_environment_inventory.py",
  "platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py",
  "platform_tests/scripts/test_db_snapshot_doctor_checks.py",
  "platform_tests/scripts/test_groundtruth_governance_adoption.py",
  "platform_tests/scripts/test_implementation_start_gate.py",
  "platform_tests/scripts/test_lo_verified_commit_atomicity.py",
  "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py",
  "platform_tests/scripts/test_release_candidate_gate.py",
  "platform_tests/scripts/test_session_self_initialization.py",
  "platform_tests/scripts/test_spec_coherence_cli.py",
  "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py",
  "Dockerfile",
  "scripts/release_candidate_gate.py",
  ".github/workflows/release-candidate-gate.yml"
]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This REVISED-2 proposal restores testing service and integration health for GitHub
Actions CI/CD workflows on the `develop` branch. It addresses three classes of
blocking CI failures and closes the remaining gap identified in the NO-GO at
`bridge/gtkb-wi4761-restore-ci-testing-integration-health-004.md` (F1: the
`core.hooksPath` fix must cover both the `python-gate` and `frontend-gate` jobs).

The three fix classes are unchanged from the prior REVISED at -003:

1. **Lint E501 (line too long)** in 22 `platform_tests/` files: wrap 36 errors
   across 22 unique files at ≤120 characters so `ruff check platform_tests/
   --select E501` passes.

2. **`core.hooksPath` CI failure**: `scripts/release_candidate_gate.py` calls
   `_check_secret_gate_present()` (lines 114–124) which reads `git config --get
   core.hooksPath` and raises `GateFailure` unless the result is `.githooks`.
   This check fires **before** any `--skip-python` or `--include-frontend`
   branching, so it affects both the `python-gate` and `frontend-gate` jobs.
   The fix adds a `git config core.hooksPath .githooks` step to **both** jobs
   in `.github/workflows/release-candidate-gate.yml`.

3. **Dockerfile stale source path**: Change line 79 from
   `COPY docs-site/docs/ ./docs-site/docs/` to
   `COPY applications/Agent_Red/docs-site/docs/ ./docs-site/docs/`.

## Responds to

`bridge/gtkb-wi4761-restore-ci-testing-integration-health-004.md` (NO-GO)

### F1 Resolution (NO-GO -004 finding)

The -004 NO-GO finding was:

> The revised proposal chooses a workflow-step implementation shape and says the
> `git config core.hooksPath .githooks` step will be added to the `python-gate`
> job, but not the `frontend-gate` job. The frontend job invokes
> `python scripts/release_candidate_gate.py --skip-python --include-frontend`
> at `.github/workflows/release-candidate-gate.yml:134`, and
> `_check_secret_gate_present()` runs before the script branches on `--skip-python`.

**Resolution**: The `git config core.hooksPath .githooks` step will be added to
**both** the `python-gate` and `frontend-gate` jobs, inserted as a named step
immediately before the respective release-candidate gate invocation in each job:

For `python-gate` (ubuntu-latest), add before the "Run release-candidate gate"
step (current line 90):

```yaml
      - name: Configure git hooks path
        run: git config core.hooksPath .githooks
```

For `frontend-gate` (windows-latest), add before the "Run frontend
release-candidate gate" step (current line 132–134):

```yaml
      - name: Configure git hooks path
        shell: pwsh
        run: git config core.hooksPath .githooks
```

### F1 from -003 Resolution (carried forward — E501 scope)

Expanded `target_paths` to include all 22 `platform_tests/` files with live E501
failures per `python -m ruff check E:/GT-KB/platform_tests --select E501
--output-format concise` (36 errors, 22 files confirmed 2026-06-22). The
verification command `python -m ruff check platform_tests/ --select E501` will pass
within the authorized scope once all listed files are fixed.

### F3 from -003 Resolution (carried forward — Dockerfile)

The Dockerfile fix is scoped to the direct repo-root build path: change line 79 from
`COPY docs-site/docs/ ./docs-site/docs/` to
`COPY applications/Agent_Red/docs-site/docs/ ./docs-site/docs/`. The build-context
scripts (`build-context.ps1`, `build-and-deploy-staging.ps1`) reference root
`docs-site/docs/` and are excluded from this proposal's scope. Their misalignment
will be captured as a standing backlog item during implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-based change control, project-boundary
  containment, and target path compliance.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links proposal to
  WI-4761 and active project authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-level linkage and
  verification boundaries.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan tests must
  exercise code changed by target_paths.
- `GOV-STANDING-BACKLOG-001` — work item tracking maintained in backlog database.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — path containment and project-root
  directory boundary for source and tests.
- `DCL-SOT-READ-HOOK-CONTRACT-001` — source-of-truth read discipline (no reads
  from forbidden-substitute paths).

## Prior Deliberations

- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-002.md` — prior NO-GO
  requiring expanded E501 target_paths and workflow-step implementation shape choice.
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-004.md` — NO-GO finding
  F1: `core.hooksPath` step must cover both `python-gate` and `frontend-gate` jobs.
- `DELIB-1691` — prior verification of release-candidate workflow path-filter and
  release-metric gate behavior; confirms the `core.hooksPath` gate was present in
  `release_candidate_gate.py` at VERIFIED time; the CI-missing-config gap is new.
- `DELIB-1726` — umbrella closeout confirming the release-gate enforcement surfaces
  and workflow filters after Sub-slice F.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — historical coverage of
  Agent Red root-path migration; confirms `applications/Agent_Red/docs-site/` is
  the canonical docs-site location post-migration.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — proposal formatting and
  verification compliance standards.

## Owner Decisions / Input

No new owner decisions are required. The work executes the owner's directive:
"Focus on restoring testing service/tool integration health. Start with GitHub
Actions." The three implementation shape choices (expand lint scope, workflow-step
fix for hooksPath in both jobs, Dockerfile-only for docs path) are P1-resolution-aligned
and within the PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING authorization envelope.

## Requirement Sufficiency

Existing requirements sufficient — WI-4761 is the sole governing requirement.
The three fix classes are all defect repairs within existing specifications.

## Spec-Derived Verification Plan

### 1. Lint gate — must pass clean within target_paths

```text
python -m ruff check platform_tests/ --select E501 --output-format concise
```

Expected: `Found 0 errors.` (or empty output). All 36 live E501 errors eliminated
by wrapping lines at ≤120 characters in the 22 target files.

### 2. Confirm `core.hooksPath` step present in python-gate job

After editing `.github/workflows/release-candidate-gate.yml`, verify:

```text
grep -n "core.hooksPath" .github/workflows/release-candidate-gate.yml
```

Expected: at least two hits — one in `python-gate` before "Run release-candidate
gate" and one in `frontend-gate` before "Run frontend release-candidate gate".

### 3. Confirm `core.hooksPath` step ordering in both jobs

```text
grep -n "Configure git hooks path\|Run release-candidate gate\|Run frontend release-candidate gate" .github/workflows/release-candidate-gate.yml
```

Expected: the "Configure git hooks path" step appears before "Run release-candidate
gate" in the `python-gate` job, and again before "Run frontend release-candidate
gate" in the `frontend-gate` job.

### 4. Run existing release-gate tests to confirm no regression

```text
python -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --no-header
```

Expected: all tests pass (tests that mock or inspect the local `git config` call
should remain green since the Python gate behavior is unchanged).

### 5. Confirm Dockerfile copy path

```text
grep "docs-site" Dockerfile
```

Expected: `COPY applications/Agent_Red/docs-site/docs/ ./docs-site/docs/` on the
corrected line.

### 6. Confirm source path exists

```text
python -c "import os; print(os.path.isdir('applications/Agent_Red/docs-site/docs'))"
```

Expected: `True`.

### 7. Run the changed platform_tests files to confirm no test regressions

```text
python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py platform_tests/hooks/test_glossary_expansion.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/hooks/test_project_completion_surface.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_active_session_heartbeat.py platform_tests/scripts/test_check_dev_environment_inventory_drift.py -q --no-header
```

```text
python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_collect_dev_environment_inventory.py platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py platform_tests/scripts/test_db_snapshot_doctor_checks.py platform_tests/scripts/test_groundtruth_governance_adoption.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_release_candidate_gate.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_spec_coherence_cli.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py -q --no-header
```

Expected: all tests pass.

## Risk / Rollback

Low risk. The three fix classes are:
- Mechanical E501 line-wrapping (no behavioral change to test logic).
- Two additive `git config` shell steps in the workflow (one per job; additive;
  does not change any job dependency or gate invocation order).
- A single `COPY` path correction in the Dockerfile (source path fix; the destination
  path and image layer structure are unchanged).

Rollback: revert the single commit containing this work.

## Known Scope Exclusion

`scripts/deploy/build-context.ps1` and `scripts/deploy/build-and-deploy-staging.ps1`
still reference root `docs-site/docs/` as the Docker build-context source. These are
deployment scripts, not CI-gate scripts. Their misalignment with the corrected
Dockerfile is a known gap that will be captured as a new backlog work item during
implementation before committing. This proposal restores GitHub Actions CI
docker-build health without touching deployment scripts.

## Applicability Preflight

Preflight run against operative file `bridge/gtkb-wi4761-restore-ci-testing-integration-health-003.md`
(prior REVISED; current proposal content is a narrow amendment to F2 coverage):

```text
## Applicability Preflight

- packet_hash: `sha256:0227df79f4a040206c9349d4aab6cfe26b755f6a511d76b9bb05dbb36d3dfcaa`
- bridge_document_name: `gtkb-wi4761-restore-ci-testing-integration-health`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4761-restore-ci-testing-integration-health-003.md`
- operative_file: `bridge/gtkb-wi4761-restore-ci-testing-integration-health-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
  "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | no | content:artifact, content:deliberation |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | blocking | yes | content:applications/, content:Agent Red, content:project root boundary |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | no | content:candidate, content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | no | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |
```

All blocking specs cited. No blocking gaps. `preflight_passed: true`.

## Project Root Boundary

All target paths in this proposal reside within `E:\GT-KB` (the mandatory project
root). No artifact, output, or dependency is created, read, or required from outside
`E:\GT-KB`. All in-root paths are relative to that root: `platform_tests/`,
`.github/workflows/`, `scripts/`, and `Dockerfile`. This proposal complies with
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`.

## Bridge Filing

This REVISED-2 proposal is filed as the next status-bearing numbered bridge file for
`gtkb-wi4761-restore-ci-testing-integration-health`. No prior version is deleted or
rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the
live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: restore CI lint gate, workflow hooksPath config for both jobs, and Dockerfile docs path

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
