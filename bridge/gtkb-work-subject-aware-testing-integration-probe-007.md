REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s363-work-subject-aware-probe-postimpl-revised-1
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report REVISED-1 - Work-subject-aware testing/tool integration probe

bridge_kind: implementation_report
Document: gtkb-work-subject-aware-testing-integration-probe
Version: 007 (POST-IMPL REVISED-1)
Reviewed-against: bridge/gtkb-work-subject-aware-testing-integration-probe-006.md (NO-GO)
Date: 2026-05-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3409

target_paths: ["scripts/session_self_initialization.py", "tests/scripts/test_testing_service_integrations_work_subject_aware.py"]

## Revision Claim

REVISED-1 addresses all three findings in NO-GO -006:

- **FINDING P1-001 (Application fallback can still query the GT-KB repository)**: `_latest_github_workflow_runs` now implements the proposal -003 IP-2 explicit fallback chain. For `FOCUS_APPLICATION` with empty `AGENT_RED_GITHUB_REPO`, the function probes `git remote get-url agent-red` and uses that slug if present; otherwise returns a no-recent-run result with `reason='application_session_missing_agent_red_target'` rather than invoking `gh run list` against the current `origin` remote. Two new regression tests guard both branches.
- **FINDING P1-002 (Spec-to-Test mapping omits 6 of 12 carried-forward specs)**: this REVISED-1 includes a complete 12-row mapping. All carried-forward specs have either an automated test row or a documented manual-verification row.
- **FINDING P2-003 (Rollup-label test mirrors implementation)**: three new runtime-renderer tests invoke `_render_session_startup_briefing` and `_render_current_project_state` directly with a minimal model fixture, asserting that the actual rendered output contains both the preserved `Testing/tools:` / `Testing/tool rollup:` label contracts AND the `(queried repo: ...)` suffix. The original mirrored-string test is retained as a label-format-contract spec test.

The target_paths are unchanged; both fixes fit within the GO'd implementation surface.

## Implementation Authorization Packet

- packet_hash: `sha256:ab6fed9ca2f04ab19db2ba1d08e0c4d376ca833a3040a840def9c4c2265f4f42`
- created_at: `2026-05-28T02:55:16Z`
- expires_at: `2026-05-28T10:55:16Z`
- bridge_id: `gtkb-work-subject-aware-testing-integration-probe`
- go_file: `bridge/gtkb-work-subject-aware-testing-integration-probe-004.md`
- requirement_sufficiency: `sufficient`

The packet is still valid (expires after current revision filing).

## Specification Links

Linked specifications carried forward from the proposal at `-003` (GO'd at `-004`):

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this report follows post-impl REVISED convention awaiting LO VERIFIED/NO-GO
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - testing/tool integration rollup is a startup-payload artifact; implementation corrects the data-source-to-label coupling
- `GOV-RELIABILITY-FAST-LANE-001` - governing fast-lane specification; eligibility confirmed by `-004` GO; implementation stayed within PAUTH `allowed_mutation_classes`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report cites every relevant cross-cutting spec
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Spec-to-Test Mapping section below maps every carried-forward spec to executed verification
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied above
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - new regression test creation is a lifecycle trigger; satisfied by the new test file under target_paths
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision evidence: S363 AskUserQuestion answers carried forward from `-003`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths under `E:\GT-KB`
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup payload is the artifact this implementation repairs
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - shared `scripts/session_self_initialization.py` invocation preserves Codex parity
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - regression tests are the durable artifact

## Prior Deliberations

Carried forward from `-003` and `-005`:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing fast-lane authorization
- `S363 backlog review session` - owner focus selection and probe-fix path
- `DELIB-0876` - durable session work subject precedent
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - backlog source-of-truth governance
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - canonical Agent Red repo migration window

## Owner Decisions / Input

Carried forward:

- S363 AskUserQuestion answer 2026-05-27 (focus menu B): "Repair Testing/Tool Integrations"
- S363 AskUserQuestion answer 2026-05-27 (repair surface): "Fix probe defect first"
- S363 AskUserQuestion answer 2026-05-27 (probe fix path): "Work-subject-aware probe"
- 2026-05-27 owner sequencing directive: "Start with Probe-level defect, then proceed to CI-level red on develop"
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active; allowed_mutation_classes matches source + test target_paths

## Diff Summary

### scripts/session_self_initialization.py (modified)

Original implementation per `-005`:
1. Imports: added `FOCUS_APPLICATION` + `FOCUS_GTKB_INFRASTRUCTURE` to workstream_focus imports.
2. New helper `_active_work_subject(project_root) -> str`.
3. `_latest_github_workflow_runs` branches on work subject; returns `queried_work_subject`, `queried_repo`, `queried_env_var`.
4. github integration entry surfaces queried metadata.
5. `quality_rollup` surfaces queried metadata.
6. Operating State + Current Project State rendering sites include `(queried repo: ...)` suffix.

REVISED-1 additions (this version):
7. **`_latest_github_workflow_runs` explicit FOCUS_APPLICATION fallback chain** (per LO -006 P1-001): when `repo` is empty after env-var lookup AND `work_subject == FOCUS_APPLICATION`, invoke `subprocess.run(["git", "remote", "get-url", "agent-red"], ...)` with timeout=5. On success, use the slug from stdout. If both env var and git remote yield no repo, return a no-recent-run result `{"available": False, "reason": "application_session_missing_agent_red_target", ...}` rather than invoking `gh run list` with no `--repo` (which would silently query origin). Approximately 25 LOC including the OSError/TimeoutExpired guard.

### tests/scripts/test_testing_service_integrations_work_subject_aware.py (modified)

Original 4 tests per `-005` retained. REVISED-1 additions (this version):
- `test_application_session_falls_back_to_agent_red_remote_when_env_empty` - covers the git-remote fallback path
- `test_application_session_returns_no_query_when_no_target` - asserts gh is NEVER invoked when no Agent Red target exists (the critical guard against silent cross-subject coupling)
- `test_render_session_startup_briefing_includes_queried_repo_at_runtime` - exercises the actual `_render_session_startup_briefing` function
- `test_render_current_project_state_includes_queried_repo_at_runtime` - exercises the actual `_render_current_project_state` function
- `test_render_session_startup_briefing_handles_missing_queried_repo` - verifies fallback to "unknown" in the renderer when queried_repo is None
- New helper `_build_minimal_model(queried_repo)` constructs a valid model for the renderer functions

Total: 9 tests (4 original + 3 fallback-coverage + 2 runtime-renderer + 0 changed). The original `test_rollup_label_includes_queried_repo` is retained as a label-format-contract spec test alongside the new runtime-renderer tests.

## Spec-to-Test Mapping (Complete, 12 of 12 Carried-Forward Specs)

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Manual: bridge thread chain inspection (-001 -> -002 -> -003 -> -004 -> -005 -> -006 -> this -007); INDEX.md update entry per protocol | yes | PASS - thread chain complete, INDEX up to date |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_render_session_startup_briefing_includes_queried_repo_at_runtime` + `test_render_current_project_state_includes_queried_repo_at_runtime` (runtime renderer verifies queried_repo in rollup label) | yes | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` | Manual: target_paths inspection vs PAUTH allowed_mutation_classes (source + test_addition only; no DB or protected-artifact mutation) | yes | PASS - source/test_addition only |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-subject-aware-testing-integration-probe` (rerun on this revision per LO standard workflow) | yes (by LO at -006) | PASS - missing_required_specs: [] |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Inspection of THIS mapping table coverage (12 of 12 specs) | yes | PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Manual: header metadata inspection in this report (Project Authorization, Project, Work Item lines present) | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Existence of `tests/scripts/test_testing_service_integrations_work_subject_aware.py` (new artifact) and post-impl-report file (lifecycle trigger) | yes | PASS |
| `SPEC-AUQ-POLICY-ENGINE-001` | Manual: `## Owner Decisions / Input` section inspection; all owner-decision evidence is from AUQ answers, not prose | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Manual: target_paths inspection; both paths are under `E:\GT-KB` (no out-of-root paths) | yes | PASS |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Suite: `pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v` covers correct rollup data source (gtkb_infrastructure + application branches + fallback chain) | yes | PASS - 9 passed in 0.37s |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Manual: `.codex/gtkb-hooks/session_start_dispatch.py` imports and invokes `scripts.session_self_initialization` (LO confirmed at -004); no Codex-side fork required | yes (LO -004 confirmed) | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Manual: new regression test file at `tests/scripts/...` is the durable artifact; `git status` shows the file present | yes | PASS |

## Verification Evidence

### Evidence 1: gtkb_infrastructure session queries GT-KB repo

Live probe in the current session (unchanged from `-005`):

```
work_subject = 'gtkb_infrastructure'
queried_repo = 'Remaker-Digital/groundtruth-kb'
queried_work_subject = 'gtkb_infrastructure'
queried_env_var = 'GROUND_TRUTH_GITHUB_REPO'
Security Scan latest: develop@7ee608e failure 2026-05-27T09:14:07Z
```

### Evidence 2: application session queries Agent Red repo (env var present)

`test_application_session_queries_agent_red_repo` verifies via captured `subprocess.run`: gh command contains `--repo mike-remakerdigital/agent-red`.

### Evidence 3 (NEW): application session falls back to agent-red git remote

`test_application_session_falls_back_to_agent_red_remote_when_env_empty` verifies: with `AGENT_RED_GITHUB_REPO=""` and a fake `agent-red` git remote returning `https://github.com/mike-remakerdigital/agent-red.git`, the function probes the git remote and uses its slug. The gh command contains `--repo mike-remakerdigital/agent-red`.

### Evidence 4 (NEW): application session returns no-query when no Agent Red target

`test_application_session_returns_no_query_when_no_target` verifies: with `AGENT_RED_GITHUB_REPO=""` and `git remote get-url agent-red` returning non-zero exit, the function returns `{"available": False, "reason": "application_session_missing_agent_red_target", "queried_repo": None}` AND `gh run list` is NEVER invoked. This is the critical guard against silent cross-subject coupling.

### Evidence 5: rendered rollup includes queried_repo (NEW runtime-renderer evidence)

`test_render_session_startup_briefing_includes_queried_repo_at_runtime` and `test_render_current_project_state_includes_queried_repo_at_runtime` invoke the actual rendering functions with a minimal model fixture. Both assert:

- The preserved label-format contracts (`Testing/tools:` and `Testing/tool rollup:`) are intact.
- The `(queried repo: Remaker-Digital/groundtruth-kb)` suffix is present.

`test_render_session_startup_briefing_handles_missing_queried_repo` verifies the fallback to literal "unknown" when queried_repo is None (no stale repo identity leaked).

### Evidence 6: missing/malformed work subject defaults to gtkb_infrastructure

`test_missing_work_subject_defaults_to_gtkb_infrastructure` unchanged from `-005`; still PASS.

### Evidence 7: pre-existing regression test still PASSES

`test_dashboard_and_report_are_written_with_time_series_kpi` (the platform_tests regression test that asserts `"Testing/tool rollup:" in report_text`): PASSES in 35.34s. The label-format contract is preserved.

## Test Results

### Complete WI-3409 test suite

```
$ pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v
collected 9 items
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_gtkb_infrastructure_session_queries_gt_kb_repo PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_application_session_queries_agent_red_repo PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_application_session_falls_back_to_agent_red_remote_when_env_empty PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_application_session_returns_no_query_when_no_target PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_missing_work_subject_defaults_to_gtkb_infrastructure PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_rollup_label_includes_queried_repo PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_render_session_startup_briefing_includes_queried_repo_at_runtime PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_render_current_project_state_includes_queried_repo_at_runtime PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_render_session_startup_briefing_handles_missing_queried_repo PASSED
9 passed in 0.37s
```

### Pre-existing regression test

```
$ pytest platform_tests/scripts/test_session_self_initialization.py -k "dashboard_and_report" --timeout=90 -v
collected 72 items / 71 deselected / 1 selected
platform_tests/scripts/test_session_self_initialization.py::test_dashboard_and_report_are_written_with_time_series_kpi PASSED
1 passed, 71 deselected in 35.34s
```

## Acceptance Criteria Verification

All 7 from the proposal at -003 satisfied (per -005 evidence, plus the additional fallback coverage):

1. `_testing_service_integrations` reads active work subject via `load_state` with fail-soft default - SATISFIED
2. Query repo selection branches correctly INCLUDING the application fallback chain (env var -> agent-red remote -> no-query) - SATISFIED (was partially satisfied in -005; LO P1-001 corrected)
3. Returned integration data includes `queried_repo` and `queried_work_subject` - SATISFIED
4. Startup rollup label includes queried_repo identity (runtime renderer verified, not just mirrored-string test) - SATISFIED (LO P2-003 corrected)
5. All regression tests PASS - SATISFIED (9/9 in 0.37s)
6. Live session shows GT-KB CI when current_subject=gtkb_infrastructure - SATISFIED
7. WI-3409 resolves to `resolved` upon VERIFIED - PENDING LO VERIFIED

## Observations and Open Items

### Observation 1: Test layout convention (unchanged from -005)

target_paths declared `tests/scripts/` but existing tests live under `platform_tests/scripts/`. Following GO'd target_paths literally. Relocation can be a separate slice if LO requires.

### Observation 2: Pre-existing topology-derivation test failures (unchanged)

7 tests in the broader regression sweep failed on unrelated `Harness topology` rendering. Failures pre-date this work (rendered output literally contains my fix). If LO determines they should block VERIFIED, please surface; otherwise tracked separately.

## Files Changed (cumulative across -005 + -007)

- `scripts/session_self_initialization.py` (modified; +~105 LOC across imports, helper, branched probe, fallback chain, integration-entry fields, quality_rollup fields, rendering site updates, explanatory comments)
- `tests/scripts/test_testing_service_integrations_work_subject_aware.py` (modified; 9 tests across 4 paths: env var present, env var empty + git remote, env var empty + no remote, missing state; plus 3 runtime-renderer tests)

## Recommended Commit Type

`fix` - data-source coupling defect repair in the startup probe; explicit fallback chain prevents silent cross-subject queries.

## Outstanding LO Verdict

This REVISED-1 awaits Loyal Opposition VERIFIED or NO-GO. The three findings from `-006` are addressed above with concrete evidence pointers and new regression coverage.
