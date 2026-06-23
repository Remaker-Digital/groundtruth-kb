NEW

# gtkb-wi4761-restore-ci-testing-integration-health — Restore GitHub Actions CI/CD and testing integration health

bridge_kind: prime_proposal
Document: gtkb-wi4761-restore-ci-testing-integration-health
Version: 001
Author: Prime Builder (harness C)
Date: 2026-06-22 UTC

author_identity: prime-builder/antigravity
author_harness_id: C
author_session_context_id: 2026-06-22T11-48Z-prime-builder-C-ci-health-restore
author_model: gemini-2.5-flash
author_model_version: gemini-2.5-flash-interactive
author_model_configuration: Antigravity IDE interactive session; resolved prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4761

target_paths: ["platform_tests/scripts/test_check_dev_environment_inventory_drift.py", "platform_tests/scripts/test_active_session_heartbeat.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/hooks/test_owner_decision_tracker.py", "platform_tests/hooks/test_glossary_expansion.py", "platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py", "platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py", "platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py", "platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py", "Dockerfile", "scripts/release_candidate_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal restores testing service and integration health for GitHub Actions CI/CD workflows on the `develop` branch. It addresses three classes of blocking CI failures:
1. Lint errors (E501 - line too long) in 10 test files under `platform_tests/`.
2. Stale `docs-site/docs/` source path in `Dockerfile` (moved to `applications/Agent_Red/docs/`).
3. The git config `core.hooksPath` check in `scripts/release_candidate_gate.py` which fails in GitHub Actions runs (will run `git config core.hooksPath .githooks` inside the CI workflow).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Governs bridge-based change control, project-boundary containment, and target path compliance.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Mandates linking proposals to backlog work items (WI-4761) and active project authorizations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Enforces project-level linkage and verification boundaries.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Enforces that verification plan tests execute code changed by target paths.
- `GOV-STANDING-BACKLOG-001` — Enforces that work item tracking is maintained in the backlog database.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Governs path containment and project-root directory boundary for source and tests.

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — Establishes proposal formatting and verification compliance standards.

## Owner Decisions / Input

No new owner decisions are required. The work directly executes the owner's request: "Focus on restoring testing service/tool integration health. Start with GitHub Actions."

## Requirement Sufficiency

Existing requirements sufficient — The work item WI-4761 is the sole governing requirement.

## Spec-Derived Verification Plan

To verify that these changes resolve the CI/CD integration issues locally before pushing, we run the lint checks and the affected test suite:

1. Validate pycodestyle line length check passes on changed files:
```text
python -m ruff check platform_tests/ --select E,F
```

2. Run the release candidate gate locally (Python and Frontend checks):
```text
python scripts/release_candidate_gate.py --require-python 3.12 --skip-frontend
python scripts/release_candidate_gate.py --skip-python --include-frontend
```

3. Run the specific pytest files changed to ensure tests still pass:
```text
python -m pytest platform_tests/scripts/test_check_dev_environment_inventory_drift.py platform_tests/scripts/test_active_session_heartbeat.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/hooks/test_glossary_expansion.py platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py -q --no-header
```

## Risk / Rollback

Low risk. These are mechanical test formatting, configuration path, and CI setup repairs. Rollback can be performed by reverting the single commit containing this work.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4761-restore-ci-testing-integration-health`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: resolve lint, Dockerfile path, and release-gate hooksPath failures in CI

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
