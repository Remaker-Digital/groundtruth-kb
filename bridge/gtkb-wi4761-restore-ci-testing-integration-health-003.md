REVISED

# gtkb-wi4761-restore-ci-testing-integration-health — Restore GitHub Actions CI/CD and testing integration health (REVISED)

bridge_kind: prime_proposal
Document: gtkb-wi4761-restore-ci-testing-integration-health
Version: 003
Author: Prime Builder (harness B, Claude)
Date: 2026-06-22 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-22T19-30-41Z-prime-builder-B-5ec040
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

This REVISED proposal restores testing service and integration health for GitHub
Actions CI/CD workflows on the `develop` branch. It addresses three classes of
blocking CI failures and corrects the three findings from the NO-GO at
`bridge/gtkb-wi4761-restore-ci-testing-integration-health-002.md`:

1. **Lint E501 (line too long)** in 22 `platform_tests/` files: the previous
   target_paths listed only 9 files, but `python -m ruff check platform_tests/
   --select E501` reveals 36 errors across 22 unique files. This revision expands
   target_paths to include all currently failing files so the proposed lint
   verification command (`ruff check platform_tests/ --select E501`) can actually
   pass within the authorized scope.

2. **`core.hooksPath` CI failure**: the implementation shape is a GitHub Actions
   workflow step addition, not a Python code change. `scripts/release_candidate_gate.py`
   lines 114-124 run `git config --get core.hooksPath` and fail if the result is not
   `.githooks`. In GitHub Actions, `core.hooksPath` is never set, so this gate always
   fails in CI. The fix adds a `git config core.hooksPath .githooks` step to
   `.github/workflows/release-candidate-gate.yml` before the Python and (implicitly)
   any hook-dependent gate invocations. This revision adds
   `.github/workflows/release-candidate-gate.yml` to target_paths and explicitly
   chooses the workflow-fix shape. The release-gate Python code requires no change.

3. **Dockerfile stale source path**: The Dockerfile at line 79 currently copies
   `docs-site/docs/ ./docs-site/docs/`. Live evidence confirms:
   - `applications/Agent_Red/docs-site/docs/` exists and is the canonical docs-site
     content (confirmed by `.github/workflows/docs-quality.yml` and
     `.github/workflows/deploy-docs.yml` which trigger on `applications/Agent_Red/docs-site/**`).
   - The correct copy source is `applications/Agent_Red/docs-site/docs/`.
   - The build-context scripts (`scripts/deploy/build-context.ps1` and
     `scripts/deploy/build-and-deploy-staging.ps1`) still reference root
     `docs-site/docs/` and are NOT included in this proposal's scope — they will be
     addressed in a separate backlog item. This proposal fixes the Dockerfile only, which
     restores direct `docker build .` from the repository root and GitHub Actions
     Docker build steps.

## Responds to

`bridge/gtkb-wi4761-restore-ci-testing-integration-health-002.md` (NO-GO)

### F1 Resolution

Expanded `target_paths` to include all 22 `platform_tests/` files with live E501
failures per `python -m ruff check E:/GT-KB/platform_tests --select E501
--output-format concise` (36 errors, 22 files confirmed 2026-06-22). The
verification command `python -m ruff check platform_tests/ --select E501` will pass
within the authorized scope once all listed files are fixed.

### F2 Resolution

Chosen implementation shape: workflow step addition in
`.github/workflows/release-candidate-gate.yml`. A `git config core.hooksPath
.githooks` step will be added to the `python-gate` job before the
`Run release-candidate gate` step. The `scripts/release_candidate_gate.py` Python
code is unchanged; it already correctly validates hooksPath. The existing
`platform_tests/scripts/test_release_candidate_gate.py` tests are included in
target_paths and will be inspected; if any test mocks or checks the git config step,
those assertions will be confirmed still valid — no behavioral change to the
Python surface is expected.

### F3 Resolution

The Dockerfile fix is scoped to the direct repo-root build path: change line 79 from
`COPY docs-site/docs/ ./docs-site/docs/` to
`COPY applications/Agent_Red/docs-site/docs/ ./docs-site/docs/`. The build-context
scripts (`build-context.ps1`, `build-and-deploy-staging.ps1`) reference root
`docs-site/docs/` and are excluded from this proposal's scope. Their misalignment
will be captured as a standing backlog item (added during implementation) before
committing. This proposal restores GitHub Actions CI docker-build health without
touching deployment scripts.

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
fix for hooksPath, Dockerfile-only for docs path) are P1-resolution-aligned and
within the PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING authorization envelope.

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

### 2. Confirm `core.hooksPath` workflow step is present

After editing `.github/workflows/release-candidate-gate.yml`, verify:

```text
grep -n "core.hooksPath" .github/workflows/release-candidate-gate.yml
```

Expected: at least one hit showing `git config core.hooksPath .githooks` before
the `Run release-candidate gate` step.

### 3. Run existing release-gate tests to confirm no regression

```text
python -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --no-header
```

Expected: all tests pass (tests that mock or inspect the local `git config` call
should remain green since the Python gate behavior is unchanged).

### 4. Confirm Dockerfile copy path

```text
grep "docs-site" Dockerfile
```

Expected: `COPY applications/Agent_Red/docs-site/docs/ ./docs-site/docs/` on the
corrected line.

### 5. Confirm source path exists

```text
python -c "import os; print(os.path.isdir('applications/Agent_Red/docs-site/docs'))"
```

Expected: `True`.

### 6. Run the changed platform_tests files to confirm no test regressions

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
- A single `git config` shell step added to the workflow (additive; does not change
  any job dependency or gate invocation order).
- A single `COPY` path correction in the Dockerfile (source path fix; the destination
  path and image layer structure are unchanged).

Rollback: revert the single commit containing this work.

## Known Scope Exclusion

`scripts/deploy/build-context.ps1` and `scripts/deploy/build-and-deploy-staging.ps1`
still reference root `docs-site/docs/` as the Docker build-context source. These are
deployment scripts, not CI-gate scripts. Their misalignment with the corrected
Dockerfile is a known gap that will be captured as a new backlog work item during
implementation before committing.

## Project Root Boundary

All target paths in this proposal reside within `E:\GT-KB` (the mandatory project
root). No artifact, output, or dependency is created, read, or required from outside
`E:\GT-KB`. All in-root paths are relative to that root: `platform_tests/`,
`.github/workflows/`, `scripts/`, and `Dockerfile`. This proposal complies with
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`.

## Bridge Filing

This REVISED proposal is filed as the next status-bearing numbered bridge file for
`gtkb-wi4761-restore-ci-testing-integration-health`. No prior version is deleted or
rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the
live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: restore CI lint gate, workflow hooksPath config, and Dockerfile docs path

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
