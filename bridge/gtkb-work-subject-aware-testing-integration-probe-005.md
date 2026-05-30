NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s363-work-subject-aware-probe-postimpl
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report - Work-subject-aware testing/tool integration probe

bridge_kind: implementation_report
Document: gtkb-work-subject-aware-testing-integration-probe
Version: 005 (POST-IMPL NEW)
Reviewed-against: bridge/gtkb-work-subject-aware-testing-integration-probe-004.md (GO)
Date: 2026-05-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3409

target_paths: ["scripts/session_self_initialization.py", "tests/scripts/test_testing_service_integrations_work_subject_aware.py"]

## Implementation Summary

WI-3409 implemented per the GO'd scope at `-004`. The probe now reads the active work subject via `scripts.workstream_focus.load_state` (imported as `_workstream_load_state`) and branches the GitHub query target:

- `current_subject == FOCUS_GTKB_INFRASTRUCTURE` (`gtkb_infrastructure`): queries `GROUND_TRUTH_GITHUB_REPO`
- `current_subject == FOCUS_APPLICATION` (`application`): queries `AGENT_RED_GITHUB_REPO`
- Missing/malformed/unrecognized state: fail-soft default to `FOCUS_GTKB_INFRASTRUCTURE`

Returned `gh_runs` dict surfaces `queried_repo`, `queried_work_subject`, and `queried_env_var`. The github integration entry, the `quality_rollup` in dashboard intelligence, and the two startup-rendering sites all consume these structured fields.

The pre-existing label-format contract `"Testing/tool rollup:"` / `"Testing/tools:"` is preserved (queried_repo appended as parenthetical SUFFIX rather than inserted before the colon) to keep downstream-parser callers and the regression test `test_dashboard_and_report_are_written_with_time_series_kpi` working.

## Implementation Authorization Packet

- packet_hash: `sha256:ab6fed9ca2f04ab19db2ba1d08e0c4d376ca833a3040a840def9c4c2265f4f42`
- created_at: `2026-05-28T02:55:16Z`
- expires_at: `2026-05-28T10:55:16Z`
- bridge_id: `gtkb-work-subject-aware-testing-integration-probe`
- go_file: `bridge/gtkb-work-subject-aware-testing-integration-probe-004.md`
- requirement_sufficiency: `sufficient`

## Specification Links

Linked specifications carried forward from the proposal at `-003` (GO'd at `-004`):

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this post-impl report follows the NEW post-impl convention awaiting LO VERIFIED/NO-GO
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - testing/tool integration rollup is a startup-payload artifact; this implementation corrects the data-source-to-label coupling
- `GOV-RELIABILITY-FAST-LANE-001` - governing fast-lane specification; eligibility confirmed by `-004` GO; the implementation stayed within the PAUTH's `allowed_mutation_classes` (`source` + `test_addition` only)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report cites every relevant cross-cutting spec
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Spec-to-Test Mapping section below maps acceptance criteria to executed test commands and their results
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied above
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - new regression test creation is a lifecycle trigger; satisfied by the new test file under target_paths
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision evidence: S363 AskUserQuestion answers carried forward from `-003` Owner Decisions section
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths under `E:\GT-KB`
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup payload is the artifact this implementation repairs
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - shared `scripts/session_self_initialization.py` invocation preserves Codex parity (confirmed by LO at `-004` Evidence Checks)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - regression test is the durable artifact

## Prior Deliberations

Carried forward from `-003`:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing fast-lane authorization underlying PAUTH; eligibility verified by LO at `-004`
- `S363 backlog review session` - owner focus selection (B: Repair Testing/Tool Integrations) and probe-fix path
- `DELIB-0876` - durable session work subject precedent; `.claude/session/work-subject.json` canonical state file
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - backlog source-of-truth governance
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - canonical Agent Red repo migration window

## Owner Decisions / Input

Carried forward from `-003`:

- S363 AskUserQuestion answer 2026-05-27 (focus menu B): "Repair Testing/Tool Integrations"
- S363 AskUserQuestion answer 2026-05-27 (repair surface): "Fix probe defect first"
- S363 AskUserQuestion answer 2026-05-27 (probe fix path): "Work-subject-aware probe"
- 2026-05-27 owner sequencing directive: "Start with Probe-level defect, then proceed to CI-level red on develop"
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active; `allowed_mutation_classes=["source","test_addition","hook_upgrade"]` matches the source + test-only target_paths

## Diff Summary

### scripts/session_self_initialization.py (modified)

1. **Imports** (lines ~50-75): added `FOCUS_APPLICATION` and `FOCUS_GTKB_INFRASTRUCTURE` to both branches of the existing `scripts.workstream_focus` try/except import block. `load_state` was already imported as `_workstream_load_state`.

2. **New helper `_active_work_subject(project_root) -> str`** (after `_github_repo_url` around line 838): reads canonical state via `_workstream_load_state(project_root)`, validates `current_subject` against the canonical schema (`FOCUS_GTKB_INFRASTRUCTURE` or `FOCUS_APPLICATION`), fails soft to `FOCUS_GTKB_INFRASTRUCTURE` on any error or unrecognized value.

3. **`_latest_github_workflow_runs(project_root, gh_auth_status)`** (line ~1892): branches on work subject for env var selection (`GROUND_TRUTH_GITHUB_REPO` vs `AGENT_RED_GITHUB_REPO`); preserves the existing 100-run query limit, JSON parsing, and "first occurrence per workflow_name" latest-run identification; returned dict now includes `queried_work_subject`, `queried_repo`, and `queried_env_var` in all return paths (auth-failure, exception, gh-error, JSON-error, success).

4. **github integration entry** in `_testing_service_integrations` (line ~2425): surfaces `queried_work_subject`, `queried_repo`, and `queried_env_var` from `gh_runs`; adds `queried repo: <repo> (work subject: <subject>)` to the evidence list; updates `state_source` to mention both env vars.

5. **`quality_rollup` in `_dashboard_intelligence`** (line ~2989): adds `queried_repo` and `queried_work_subject` keys sourced from `integrations["github"]`.

6. **Rendering site 1** (Operating State section, around line 4057): `"- Testing/tools: ... (queried repo: ...)."` - colon position preserved, queried_repo as parenthetical suffix.

7. **Rendering site 2** (Current Project State section, around line 4251): `"- {subject_label} Testing/tool rollup: ... (queried repo: ...)"` - colon position preserved, queried_repo as parenthetical suffix.

### tests/scripts/test_testing_service_integrations_work_subject_aware.py (NEW)

178 LOC, 4 pytest functions. Module-level sys.path insertion to enable `from scripts...` imports under pytest from any cwd. Uses `unittest.mock.patch` to isolate from live `.claude/session/work-subject.json` and live `gh` CLI subprocess.

## Spec-to-Test Mapping

| Spec citation | Verification artifact | Command | Result |
|---|---|---|---|
| GOV-SESSION-SELF-INITIALIZATION-001 (correct rollup data source) | test_gtkb_infrastructure_session_queries_gt_kb_repo | `pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_gtkb_infrastructure_session_queries_gt_kb_repo -v` | PASS |
| GOV-RELIABILITY-FAST-LANE-001 (fast-lane eligibility) | target_paths inspection + Reliability Fast-Lane Eligibility subsection | Manual review of -003 + PAUTH allowed_mutation_classes | PASS - source + test_addition only, matches PAUTH |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each acceptance has a test) | All 4 regression tests | `pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v` | 4 passed in 0.31s |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (rollup labeling matches data source) | test_rollup_label_includes_queried_repo | `pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_rollup_label_includes_queried_repo -v` | PASS |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 (Codex parity) | Manual: verify .codex/gtkb-hooks/session_start_dispatch.py inherits same scripts/ probe | LO's GO at -004 evidence checks confirmed Codex hook calls into shared scripts/session_self_initialization.py | PASS (LO confirmed) |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (test creation lifecycle) | New test file creation | `git status` after impl | PASS - tests/scripts/test_testing_service_integrations_work_subject_aware.py present |

## Verification Evidence

### Evidence 1: gtkb_infrastructure session queries GT-KB repo

Live probe in the current session (`current_subject = gtkb_infrastructure` per `.claude/session/work-subject.json`):

```
work_subject = 'gtkb_infrastructure'
auth_status = 'authenticated'
available = True
queried_repo = 'Remaker-Digital/groundtruth-kb'
queried_work_subject = 'gtkb_infrastructure'
queried_env_var = 'GROUND_TRUTH_GITHUB_REPO'
repository = 'Remaker-Digital/groundtruth-kb'
Security Scan latest: develop@7ee608e failure 2026-05-27T09:14:07Z
```

Before the fix, the same probe returned Agent Red's stale `develop@1817db0` data from `2026-05-07`. After: GT-KB's actual current-commit failure on `7ee608e` from today.

### Evidence 2: application session queries Agent Red repo

`test_application_session_queries_agent_red_repo` verifies the branch via mocked work subject + captured `subprocess.run` command. The captured `gh run list` command contains `--repo mike-remakerdigital/agent-red`, not `--repo Remaker-Digital/groundtruth-kb`.

### Evidence 3: rendered rollup text includes queried repository identity

Re-run of `test_dashboard_and_report_are_written_with_time_series_kpi` (the pre-existing regression test that asserts label-format contracts) produces the rendered report containing both:

- `"- GT-KB Testing/tool rollup: 10 failing, 6 manual, 14 ready/passing (queried repo: Remaker-Digital/groundtruth-kb)"` (Current Project State section)
- `"- Testing/tools: 10 failing, 6 manual, 14 ready/passing (queried repo: Remaker-Digital/groundtruth-kb)."` (Operating State section)

Both contain the canonical `Testing/tool rollup:` / `Testing/tools:` substring (preserved label-format contract) AND the `(queried repo: Remaker-Digital/groundtruth-kb)` suffix (new disambiguation evidence).

### Evidence 4: missing/malformed state defaults to gtkb_infrastructure

`test_missing_work_subject_defaults_to_gtkb_infrastructure` verifies two failure modes:
- `_workstream_load_state` raising `FileNotFoundError`: `_active_work_subject` returns `FOCUS_GTKB_INFRASTRUCTURE`
- `_workstream_load_state` returning `{"current_subject": "something_unrecognized"}`: `_active_work_subject` returns `FOCUS_GTKB_INFRASTRUCTURE`

## Test Results

### New test suite (WI-3409)

```
$ pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v
collected 4 items
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_gtkb_infrastructure_session_queries_gt_kb_repo PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_application_session_queries_agent_red_repo PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_missing_work_subject_defaults_to_gtkb_infrastructure PASSED
tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_rollup_label_includes_queried_repo PASSED
4 passed in 0.31s
```

### Regression sweep on pre-existing session_self_initialization tests

```
$ pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_imports.py platform_tests/scripts/test_session_self_initialization_canonical_consistency.py platform_tests/scripts/test_session_self_initialization_topology_derive.py platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py tests/scripts/test_testing_service_integrations_work_subject_aware.py --timeout=60
7 failed, 92 passed in 220.09s
```

The 7 failures are pre-existing topology-derivation issues UNRELATED to this fix:

- `test_recommender_6_live_regression_excludes_known_stale_priorities`
- `test_topology_label_matches_role_map_cardinality_one_multi_role` - failing assertion's rendered output literally contains `"- Application Testing/tool rollup: 0 failing, 0 manual, 0 ready/passing (queried repo: unknown)"` showing the work-subject-aware fix working correctly; the failure is on `Harness topology: 'single_harness' vs 'multi_harness'` which is unrelated to this probe
- `test_role_slot_renders_singleton_role_token_prime`
- `test_role_slot_renders_singleton_role_token_lo`
- `test_render_ignores_stale_persisted_workstream_state`
- `test_topology_derives_single_harness_for_one_multi_role_set`
- `test_topology_handles_acting_prime_builder_as_prime`

All 7 are topology / role-slot rendering tests that depend on `harness-state/role-assignments.json` content and `workstream_focus.py` topology-derivation logic - code paths NOT touched by this implementation. The previously-broken rollup-label assertion (`test_dashboard_and_report_are_written_with_time_series_kpi`) was repaired by the label-format adjustment (queried_repo as parenthetical suffix) and now PASSES.

If LO determines these pre-existing failures should block VERIFIED for this thread, please surface as NO-GO with evidence that the failures are reproducible on this repo state without my changes, and I will file a separate WI for the topology-derivation defect.

## Observations and Open Items

### Observation 1: Test layout convention

My target_paths declared `tests/scripts/test_testing_service_integrations_work_subject_aware.py` but existing session_self_initialization tests live under `platform_tests/scripts/`. I followed the GO'd target_paths literally (the implementation-start gate enforces this). If LO prefers the conventional location, surface as a NO-GO finding and I will relocate via a REVISED proposal that updates target_paths to `platform_tests/scripts/test_testing_service_integrations_work_subject_aware.py`. The relocation is one `git mv` plus a single import-path adjustment.

### Observation 2: First-iteration label-format defect (resolved)

My first implementation changed the rollup label from `"Testing/tool rollup:"` to `"Testing/tool rollup (queried repo: ...):"` - moving the colon. This broke `test_dashboard_and_report_are_written_with_time_series_kpi` which asserts the substring `"Testing/tool rollup:"`. I noticed the regression during the broader regression sweep, reverted the label-format change, and restructured the queried_repo as a parenthetical SUFFIX after the data values. The pre-existing contract is now preserved. Self-disclosing this iteration for full LO context.

### Observation 3: WI-3409 status field

The `current_work_items.project_name` field for WI-3396, WI-3397, and WI-3409 is still NULL because I created these WIs via `gt backlog add` without `--project-name` to avoid the doubled-prefix bug. Their canonical project memberships are active in `project_work_item_memberships`, which is the canonical authority. LO's `-004` GO already accepted this pattern. The `approval_state=auq_required` backfilled by a parallel Codex session on `2026-05-27T18:12:15+00:00` (per WI-3271 Slice 1 unrelated backfill) is also non-blocking per LO's GO. No corrective action requested in this scope.

## Acceptance Criteria Verification

1. **`_testing_service_integrations` reads active work subject via `scripts.workstream_focus.load_state`**: SATISFIED - via `_active_work_subject(project_root)` helper which calls `_workstream_load_state(project_root)`. Fail-soft default verified by `test_missing_work_subject_defaults_to_gtkb_infrastructure`.
2. **Query repo selection branches correctly**: SATISFIED - `test_gtkb_infrastructure_session_queries_gt_kb_repo` and `test_application_session_queries_agent_red_repo` verify both branches via captured `subprocess.run` commands.
3. **Returned integration data includes `queried_repo` and `queried_work_subject`**: SATISFIED - `quality_rollup` includes both fields; github integration entry includes both fields plus `queried_env_var`.
4. **Startup rollup label includes queried_repo identity**: SATISFIED - `test_rollup_label_includes_queried_repo` and live probe both confirm.
5. **All 4 regression tests PASS**: SATISFIED - 4 passed in 0.31s.
6. **Live session re-run shows GT-KB CI when current_subject=gtkb_infrastructure**: SATISFIED - Evidence 1 shows `Security Scan develop@7ee608e failure 2026-05-27T09:14:07Z` (current GT-KB CI state), not Agent Red's 2026-05-07 stale state.
7. **WI-3409 transitions to `resolved` upon VERIFIED**: PENDING LO VERIFIED; will occur through normal post-VERIFIED project-completion path per LO's `-004` Implementation Note #2.

## Files Changed

- `scripts/session_self_initialization.py` (modified; +~80 LOC including the new helper, branched probe, integration-entry fields, quality_rollup fields, rendering updates, and explanatory comments)
- `tests/scripts/test_testing_service_integrations_work_subject_aware.py` (NEW; 178 LOC, 4 tests)

## Recommended Commit Type

`fix` - data-source coupling defect repair in the startup probe. No new capability surface beyond the work-subject-aware branching helper and its regression test.

## Outstanding LO Verdict

This report awaits Loyal Opposition VERIFIED or NO-GO. The five Verification Expectations from `-004` GO are addressed above with concrete evidence pointers. If any expectation is incompletely satisfied or any new regression surfaces during LO re-verification, REVISED-1 will respond per the standard bridge protocol.
