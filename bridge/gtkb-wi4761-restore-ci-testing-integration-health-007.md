REVISED

# gtkb-wi4761-restore-ci-testing-integration-health — Restore GitHub Actions CI/CD and testing integration health (REVISED-3)

bridge_kind: prime_proposal
Document: gtkb-wi4761-restore-ci-testing-integration-health
Version: 007
Author: Prime Builder (harness B, Claude)
Date: 2026-06-22 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-22T20-33-57Z-prime-builder-B-a32a4f
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code auto-dispatch; resolved prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4761

target_paths: ["platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py", "platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py", "platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py", "platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py", "platform_tests/hooks/test_glossary_expansion.py", "platform_tests/hooks/test_owner_decision_tracker.py", "platform_tests/hooks/test_project_completion_surface.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_active_session_heartbeat.py", "platform_tests/scripts/test_check_dev_environment_inventory_drift.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_collect_dev_environment_inventory.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py", "platform_tests/scripts/test_db_snapshot_doctor_checks.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py", "platform_tests/scripts/test_release_candidate_gate.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_spec_coherence_cli.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py", "Dockerfile", "scripts/release_candidate_gate.py", ".github/workflows/release-candidate-gate.yml", "scripts/deploy/build-context.ps1", "scripts/deploy/build-and-deploy-staging.ps1"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This REVISED-3 proposal resolves the single remaining NO-GO finding from
`bridge/gtkb-wi4761-restore-ci-testing-integration-health-006.md` (F1, P1):
the prior proposal promised to capture deploy build-context script drift as a
backlog item during implementation but declared `kb_mutation_in_scope: false`,
leaving no clean path for that capture.

**Resolution chosen: Option 1 — expand `target_paths` to include both deploy
scripts and fix the drift directly in this WI implementation.**

The two deploy scripts (`scripts/deploy/build-context.ps1` and
`scripts/deploy/build-and-deploy-staging.ps1`) reference root `docs-site/docs/`
as the Docker build-context source. The corrected Dockerfile (fix class 3) uses
`applications/Agent_Red/docs-site/docs/`. Both deploy scripts will be updated
to match: `$PROJECT_ROOT\docs-site\docs` → `$PROJECT_ROOT\applications\Agent_Red\docs-site\docs`.

This eliminates the known drift atomically alongside the CI fix, requires no KB
mutation, and removes the implementation-time side effect.

All three original fix classes from REVISED-2 are carried forward unchanged:

1. **Lint E501** in 22 `platform_tests/` files: wrap 36 errors at ≤120 chars.
2. **`core.hooksPath` CI failure**: add `git config core.hooksPath .githooks` to
   both `python-gate` and `frontend-gate` jobs in release-candidate-gate.yml.
3. **Dockerfile stale source path**: fix line 79 to use `applications/Agent_Red/docs-site/docs/`.
4. **Deploy script build-context drift** (new, addressing F1): fix both
   `scripts/deploy/build-context.ps1` and `scripts/deploy/build-and-deploy-staging.ps1`
   to use `applications/Agent_Red/docs-site/docs` as the Docker build-context source.

## Responds to

`bridge/gtkb-wi4761-restore-ci-testing-integration-health-006.md` (NO-GO)

### F1 Resolution (NO-GO -006 finding)

The -006 NO-GO finding was:

> The proposal depends on a future backlog mutation to make the Dockerfile-only
> scope safe, but it explicitly declares KB mutation out of scope. That leaves
> Prime Builder two bad options after GO: either create a MemBase work item
> without this proposal authorizing KB mutation, or skip the promised backlog
> capture and leave the deploy build-context drift untracked.

**Resolution**: Both deploy scripts are now included in `target_paths` and will
be fixed in this WI implementation. No backlog mutation or KB mutation is needed.

**`scripts/deploy/build-context.ps1`** — Live grep confirms references at
lines 40–46: `$PROJECT_ROOT\docs-site\docs` (path check, directory creation,
Copy-Item source, and warning message). All four references will be changed to
`$PROJECT_ROOT\applications\Agent_Red\docs-site\docs`.

**`scripts/deploy/build-and-deploy-staging.ps1`** — Live grep confirms
references at lines 126–131: identical pattern (`$PROJECT_ROOT\docs-site\docs`
for path check, Copy-Item source, and log message). All three references will
be changed to `$PROJECT_ROOT\applications\Agent_Red\docs-site\docs`.

### Carried-forward resolutions from -005

All -005 resolutions are unchanged and carried forward:

- **F1 from -004** (`core.hooksPath` must cover both jobs): resolved in -005,
  carried forward. Both `python-gate` and `frontend-gate` jobs get
  `git config core.hooksPath .githooks` before the gate invocation.
- **F1 from -003** (E501 scope): resolved in -005, carried forward. All 22 files
  with live E501 failures included in `target_paths`.
- **F3 from -003** (Dockerfile path): resolved in -005, carried forward.

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
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-006.md` — NO-GO finding
  F1: deploy build-context drift not tracked or authorized; resolved by expanding
  target_paths to include both deploy scripts.
- `DELIB-1691` — prior verification of release-candidate workflow path-filter and
  release-metric gate behavior; confirms the `core.hooksPath` gate was present in
  `release_candidate_gate.py` at VERIFIED time; the CI-missing-config gap is new.
- `DELIB-1726` — umbrella closeout confirming the release-gate enforcement surfaces
  and workflow filters after Sub-slice F.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — historical coverage of Agent Red
  root-path migration; confirms `applications/Agent_Red/docs-site/` is the canonical
  docs-site location post-migration.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — proposal formatting and
  verification compliance standards.

## Owner Decisions / Input

No new owner decisions are required. The work executes the owner's directive:
"Focus on restoring testing service/tool integration health. Start with GitHub
Actions." Expanding target_paths to fix the deploy build-context drift directly
(Option 1 of the three LO-offered paths) is within the
PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING authorization envelope and
requires no KB mutation.

## Requirement Sufficiency

Existing requirements sufficient — WI-4761 is the sole governing requirement.
All four fix classes are defect repairs within existing specifications.

## Spec-Derived Verification Plan

### 1. Lint gate — must pass clean within target_paths

```text
python -m ruff check platform_tests/ --select E501 --output-format concise
```

Expected: `Found 0 errors.` (or empty output). All 36 live E501 errors eliminated
by wrapping lines at ≤120 characters in the 22 target files.

### 2. Confirm `core.hooksPath` step present in both jobs

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

Expected: all tests pass.

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

### 8. Confirm build-context.ps1 no longer references root docs-site

```text
grep -n "docs-site" scripts/deploy/build-context.ps1
```

Expected: all occurrences reference `applications/Agent_Red/docs-site/docs`
(no bare `docs-site/docs` or `docs-site\docs` relative to project root).

### 9. Confirm build-and-deploy-staging.ps1 no longer references root docs-site

```text
grep -n "docs-site" scripts/deploy/build-and-deploy-staging.ps1
```

Expected: all occurrences reference `applications/Agent_Red/docs-site/docs`
(no bare `docs-site/docs` or `docs-site\docs` relative to project root).

## Risk / Rollback

Low risk. The four fix classes are:
- Mechanical E501 line-wrapping (no behavioral change to test logic).
- Two additive `git config` shell steps in the workflow (additive; does not
  change job dependency or gate invocation order).
- A single `COPY` path correction in the Dockerfile.
- Path string updates in two deploy scripts (all references to `docs-site\docs`
  become `applications\Agent_Red\docs-site\docs`; no logic changes, no new
  dependencies, no structural script changes).

Rollback: revert the single commit containing this work.

## Known Scope Exclusion

None. The prior scope exclusion for deploy build-context script drift is
resolved by including both scripts in `target_paths` and fixing them as part
of this WI implementation.

## Applicability Preflight

To be run by Loyal Opposition against the operative file
`bridge/gtkb-wi4761-restore-ci-testing-integration-health-007.md` before
issuing GO.

Expected result: `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs` advisory-only (same as prior runs).

## Project Root Boundary

All target paths in this proposal reside within `E:\GT-KB` (the mandatory project
root). No artifact, output, or dependency is created, read, or required from outside
`E:\GT-KB`. All in-root paths are relative to that root: `platform_tests/`,
`.github/workflows/`, `scripts/`, `Dockerfile`. This proposal complies with
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`.

## Bridge Filing

This REVISED-3 proposal is filed as the next status-bearing numbered bridge file for
`gtkb-wi4761-restore-ci-testing-integration-health`. No prior version is deleted or
rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the
live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: restore CI lint gate, workflow hooksPath config, Dockerfile and deploy script docs path

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
