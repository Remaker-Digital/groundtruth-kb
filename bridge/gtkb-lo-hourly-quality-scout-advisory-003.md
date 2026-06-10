ADVISORY

author_identity: Antigravity Investigator
author_harness_id: C
author_session_context_id: automation/scout/2026-05-30T20:07:33Z
author_model: Gemini 1.5 Pro
author_model_version: Antigravity C
author_model_configuration: Antigravity scheduled Scout Investigator

bridge_kind: governance_advisory
Document: gtkb-lo-hourly-quality-scout-advisory
Version: 003
Author: Antigravity Investigator
Date: 2026-05-30T20:07:33Z

# Hourly Quality Scout Advisory - Capability Registry Drift, Scaffold Fixture Drift, and Dashboard Test Timeouts

## Source

Harness-level scheduled Investigator Scout automation `scout` run, executing read-only spot checks on the GT-KB platform workspace.

## Inspected Surfaces

- `bridge/INDEX.md`
- `config/agent-control/harness-capability-registry.toml`
- `.claude/skills/`
- `groundtruth-kb/tests/`
- `platform_tests/scripts/`
- `scripts/session_self_initialization.py`
- `scripts/check_harness_parity.py`
- `scripts/audit_standing_backlog_sources.py`
- Git status and running test suites (`task-98` and `task-132` in the background)

## Summary Of Findings

1. **P2 - Harness Capability Registry Drift (Undeclared Project Surfaces)**: Skills `gtkb-hygiene-sweep` and `loyal-opposition-hygiene-assessment` are unregistered in TOML, causing the parity regression test suite to fail.
2. **P1 - Scaffold ID and Fixture Drift (27 Failing Core Tests)**: Scaffold, AST, and typing drift causes 27 failures in the core `groundtruth-kb` test suite, completely blocking clean release candidate gates.
3. **P2 - Performance Bottleneck and Test Timeout in Dashboard Writer**: The default historical backfill in the dashboard writer has $O(D \cdot N)$ complexity that is highly slow on the live DB, causing pytest timeouts in selector tests.

---

## Finding 1: Harness Capability Registry Drift (Undeclared Project Surfaces)

### Severity
P2

### Claim
The skills `gtkb-hygiene-sweep` and `loyal-opposition-hygiene-assessment` exist locally under `.claude/skills/` but are not declared in `config/agent-control/harness-capability-registry.toml`, causing the parity regression test suite to fail.

### Evidence
- `check_harness_parity.py` reports an overall status of `WARN` with two `EXTRA` findings.
- Running `python scripts/check_harness_parity.py --all --markdown` outputs:
  ```markdown
  | skill | gtkb-hygiene-sweep | EXTRA | .claude/skills/gtkb-hygiene-sweep/SKILL.md | Project skill exists but is not declared in the harness capability registry. |
  | skill | loyal-opposition-hygiene-assessment | EXTRA | .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md | Project skill exists but is not declared in the harness capability registry. |
  ```
- `platform_tests/scripts/test_check_harness_parity.py` contains `test_repository_registry_covers_project_skills`, which asserts that `report.extras` is empty. Because of these unregistered skills, this test fails.

### Risk/impact
Harnesses (Codex and Antigravity) cannot resolve these skills via automated adapter projection. Additionally, this capability registry drift breaks the platform regression test suite in CI, preventing clean runs.

### Recommended action
Prime Builder should declare both capabilities in `config/agent-control/harness-capability-registry.toml` under the `[[capabilities]]` table, setting up their native Claude paths and Codex/Antigravity adapter mappings.

### Owner decision needed
No.

### Recommended Prime Builder disposition
Convert to implementation proposal (simple fix).

---

## Finding 2: Scaffold ID and Fixture Drift (27 Failing Core Tests)

### Severity
P1 (Release Blocker)

### Claim
27 core tests are failing in `groundtruth-kb/tests` because new template files (e.g. `docs/upgrade-rehearsal-recipe.md`, `hooks/narrative-artifact-approval-gate.py`, bridge helper skills/hooks) were added to the scaffold and ownership registries, but the test baseline snapshots and golden fixtures were never regenerated or updated.

### Evidence
Running the `groundtruth-kb/tests` suite (task-132) fails with 27 errors, including:
- **`test_registry_drift_against_id_snapshot`**: Registry drift detected: added (6): `['hook.code-quality-baseline-proposal-check', 'skill.bridge.impl-report-helper', 'skill.bridge.revise-helper', 'skill.bridge.scan-helper', 'skill.bridge.show-thread-helper', 'skill.bridge.skill-md']`.
- **`test_scaffold_consumes_resolver`**: `assert len(ids) == 60` fails because `len(ids)` is 66 (due to new files like `gitignore.hook-logs`, `gitignore.kb-database`, etc.).
- **`test_scaffold_isolation`**: extra files produced in the sandbox not in the golden fixture, including `.claude/hooks/code-quality-baseline-proposal-check.py`, `.claude/skills/bridge/helpers/scan_bridge.py`, and `docs/upgrade-rehearsal-recipe.md`.
- **`test_registry_ast_coverage`**: AST gate failure: `['hooks/narrative-artifact-approval-gate.py']` template-source file lacks registry coverage.
- **`test_public_api_type_checks`**: mypy --strict found type issues on the public API surface:
  - `src\groundtruth_kb\config.py:229: error: Argument 1 to "Path" has incompatible type "object"`
  - `src\groundtruth_kb\cli.py:558: error: Module "groundtruth_kb.backlog" has no attribute "migrate_work_list_items"` / `"parse_work_list_file"`

### Risk/impact
Absolute block on any clean production build or release pipeline due to a heavily broken core test gate.

### Recommended action
Prime Builder must run the snapshot regeneration commands specified in the test traceback assertions, format/update the golden fixtures, register `hooks/narrative-artifact-approval-gate.py` in `templates/managed-artifacts.toml`, and fix the strict type mismatches in the config/cli files.

### Owner decision needed
No.

### Recommended Prime Builder disposition
Convert to implementation proposal.

---

## Finding 3: Performance Bottleneck and Test Timeout in Dashboard Writer

### Severity
P2

### Claim
`test_dashboard_data_json_carries_work_subject` in `platform_tests/scripts/test_dashboard_subject_selector.py` fails with a Timeout because the default historical backfill has $O(D \cdot N)$ complexity that is highly slow on the live `groundtruth.db`.

### Evidence
- Pytest timeout in task-98 inside `classify_dashboard_scope()` at `scripts/session_self_initialization.py:949` during `write_dashboard_and_report()`.
- The traceback indicates that during `write_dashboard_and_report()`, `_historical_agent_red_backfill()` is invoked because `seed_historical_backfill` defaults to `True`.
- `_historical_agent_red_backfill()` performs a daily loop over version history, classifying all specs, work items, and deliberations for every day. With a live database of thousands of records across hundreds of days, this pure-Python classification block requires over 30 seconds, timing out the test.

### Risk/impact
Blocks clean test suite execution, slows down the platform test lane, and consumes excessive CPU cycles during routine dashboard updates.

### Recommended action
Prime Builder should modify the dashboard selector test to call `write_dashboard_and_report()` with `seed_historical_backfill=False` since test data validation does not require real live historical backfill. Additionally, the $O(D \cdot N)$ loop in `_historical_agent_red_backfill()` should be optimized by pre-classifying records or avoiding loop-based re-classification for unchanged days.

### Owner decision needed
No.

### Recommended Prime Builder disposition
Convert to implementation proposal.

---

## Owner-Grilling Gate

### Does this advisory imply future implementation work?
Yes. All three findings recommend Prime Builder conversion proposals or scoped backlog work.

### Has owner approval been obtained for implementation?
Yes. Owner Mike explicitly approved filing this Advisory Report (Option A) on 2026-05-30T13:07:33-07:00.

### Why this should not be dismissed as already tracked:
This run adds fresh live evidence: 27 failing core tests in `groundtruth-kb/tests/`, harness capability registry drift breaking the parity suite, and a concrete pytest timeout traceback on the live database.

### Expected reply shape if owner input is later requested:
Choose `convert`, `defer`, or `reject` per finding. No owner input is needed to let Prime Builder file normal proposals.

## Recommended Prime Builder Disposition

Convert Findings 1, 2, and 3 into normal implementation proposals. Treat Finding 2 and Finding 1 as the most urgent release-readiness repairs because they directly affect core build and build-gate sanity.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
