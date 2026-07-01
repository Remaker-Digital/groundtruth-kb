NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1bfe-9f4b-7bc2-805e-c051192b5a73
author_model: gpt-5-codex
author_model_version: 2026-07-01
author_model_configuration: Codex Desktop interactive Prime Builder session; implementation report for WI-4951 load measurement

# GT-KB Bridge Implementation Report - gtkb-envelope-sharding-load-measurement - 003

bridge_kind: implementation_report
Document: gtkb-envelope-sharding-load-measurement
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-envelope-sharding-load-measurement-002.md
Approved proposal: bridge/gtkb-envelope-sharding-load-measurement-001.md
Recommended commit type: feat(benchmarks)

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4951
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4951
Implementation Authorization Packet: sha256:42641fba27cfce60bce1baac5667767f64733183db6f1a9e5376c9c3c7c53d5b
Work-Intent Claim: gtkb-envelope-sharding-load-measurement / prime-builder / session 019f1bfe-9f4b-7bc2-805e-c051192b5a73
Focused Commit: f0d2978da8da6cad5840bafd30e243b80fe2e2c2

target_paths: ["scripts/benchmarks/activity_envelope_load.py", "scripts/benchmarks/metric_registry.py", "groundtruth-kb/src/groundtruth_kb/cli.py", ".claude/skills/gtkb-benchmarks/SKILL.md", ".codex/skills/gtkb-benchmarks/SKILL.md", "config/agent-control/activity-envelope-sharding.toml", "platform_tests/scripts/test_benchmark_activity_envelope_load.py"]

## Implementation Claim

Implemented WI-4951 as a deterministic, read-only activity envelope load benchmark. The implementation adds `scripts/benchmarks/activity_envelope_load.py`, exposes it as `gt benchmarks activity-envelope-load --json`, registers the metric in `scripts/benchmarks/metric_registry.py`, documents it in the Claude and Codex benchmark skills, adds measurement thresholds to `config/agent-control/activity-envelope-sharding.toml`, and adds focused platform tests.

The benchmark reports global baseline surface size, rough token estimates, per-activity auto-load payload estimates, explicit-query source counts, never-startup payload coverage, warning/failure threshold status, and structured issues. It fails when activity payloads leak into the global baseline, when history state is not explicit-query, or when required forbidden raw archival payloads are absent from the never-startup class.

Unrelated dirty worktree state existed before this slice and is not part of this implementation report. The focused implementation was committed separately as `f0d2978da8da6cad5840bafd30e243b80fe2e2c2`.

## Specification Links

- `SPEC-INTAKE-46594e`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - owner directive to complete the project work items and retire the project after governed verification.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4951` - bounded implementation authorization for WI-4951 only.

No new owner decision is required by this implementation report.

## Prior Deliberations

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - current owner execution directive.
- `DELIB-202665110` - umbrella program and PAUTH creation authorization.
- `DELIB-20266631` - Loyal Opposition context for activity-envelope context sharding.
- `DELIB-20265892` - disposition-profile ratification.
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` - prior envelope refinement authorization.
- `DELIB-20265287` - single-active activity envelope, named disposition profile, and headless eligibility decisions.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - context-load profile anatomy and activity vocabulary.
- `bridge/gtkb-envelope-sharding-load-measurement-001.md` - approved implementation proposal.
- `bridge/gtkb-envelope-sharding-load-measurement-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-INTAKE-46594e` | `test_activity_envelope_load_reports_real_config` and the public CLI output verify that the global session envelope is measured separately from activity-specific payloads; live output reported `status: PASS`, `global_surface_token_estimate: 48745`, `activity_auto_payload_token_estimate_total: 669`, and zero issues. |
| `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` | The benchmark reads the activity disposition profiles and reports all six configured activities with their classification and headless eligibility metadata. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Tests assert six activity profiles, `skills = activity_only`, and `history_state = explicit_query`; the benchmark fails if activity profile classification leaks into `global_baseline`. |
| `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` | The benchmark makes unrelated shard loading measurable by warning/failing when activity auto-load payload estimates exceed thresholds or activity payloads are globally classified. |
| `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001` | `history_state_not_explicit_query` is a benchmark failure condition; tests cover the positive real-config case and the global-leak failure case. |
| `ADR-CROSS-HARNESS-PARITY-001` | The metric is exposed through the shared `gt` CLI and documented in both `.claude` and `.codex` benchmark skills. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation occurred only after latest `GO`, Prime work-intent claim, and implementation-start packet. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The benchmark, thresholds, CLI surface, metric registry entry, skill docs, tests, commit, and bridge report are durable artifacts rather than transcript-only observations. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward every linked specification from the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps linked specifications to executed tests and observed command results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project Authorization, Project, and Work Item metadata are present in proposal, GO verdict, and this report. |
| `GOV-STANDING-BACKLOG-001` | No bulk backlog/project mutation was performed in this slice. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | No hook behavior was modified; Codex-facing docs were updated through the skill adapter path and the shared CLI remains available as the fallback surface. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Thresholds and measurement behavior live in config/code/tests, not scratchpad notes. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No new owner decision or requirement was introduced during implementation; existing governing artifacts were cited and preserved. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-envelope-sharding-load-measurement --session-id 019f1bfe-9f4b-7bc2-805e-c051192b5a73`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-envelope-sharding-load-measurement --session-id 019f1bfe-9f4b-7bc2-805e-c051192b5a73`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_benchmark_activity_envelope_load.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/benchmarks/activity_envelope_load.py scripts/benchmarks/metric_registry.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_benchmark_activity_envelope_load.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/benchmarks/activity_envelope_load.py scripts/benchmarks/metric_registry.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_benchmark_activity_envelope_load.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\benchmarks\activity_envelope_load.py --json`
- `cmd.exe /d /c C:\Users\micha\.local\bin\gt.cmd benchmarks activity-envelope-load --json`
- `git commit -m "feat(benchmarks): add activity envelope load measurement (WI-4951)"`
- `git archive f0d2978da | tar -x -C E:\GT-KB\.gtkb-state\clean-checkouts\wi4951-f0d2978da`
- Clean checkout: `python -m pytest E:\GT-KB\.gtkb-state\clean-checkouts\wi4951-f0d2978da\platform_tests\scripts\test_benchmark_activity_envelope_load.py -q --tb=short` with `PYTHONPATH` pointed at the clean checkout.
- Clean checkout: `python E:\GT-KB\.gtkb-state\clean-checkouts\wi4951-f0d2978da\scripts\benchmarks\activity_envelope_load.py --project-root E:\GT-KB\.gtkb-state\clean-checkouts\wi4951-f0d2978da --json`
- Clean checkout: `python -m ruff check` over the four changed Python paths in the clean checkout.
- Clean checkout: `python -m ruff format --check` over the four changed Python paths in the clean checkout.

## Observed Results

- Work-intent claim succeeded as `go_implementation` for Prime Builder session `019f1bfe-9f4b-7bc2-805e-c051192b5a73`.
- Implementation-start packet succeeded with packet hash `sha256:42641fba27cfce60bce1baac5667767f64733183db6f1a9e5376c9c3c7c53d5b`.
- Focused pytest: 3 tests collected; 3 passed.
- Focused ruff check: all checks passed.
- Focused ruff format check: 4 files already formatted.
- Direct benchmark script on live workspace: `status: PASS`, `global_surface_token_estimate: 48745`, `activity_auto_payload_token_estimate_total: 669`, `issue_count: 0`.
- Public `gt` CLI on live workspace: `status: PASS`, `global_surface_token_estimate: 48745`, `activity_auto_payload_token_estimate_total: 669`, `issue_count: 0`.
- Commit hook evidence for `f0d2978da8da6cad5840bafd30e243b80fe2e2c2`: scanned 7 staged files, found 0 potential secrets, inventory drift PASS, narrative-artifact evidence PASS, ruff format PASS for 4 staged Python files, protected-commit authorization PASS for 5 protected paths.
- Clean checkout pytest from committed snapshot: 3 tests collected; 3 passed.
- Clean checkout direct benchmark script: `status: PASS`, `global_surface_token_estimate: 46737`, `activity_auto_payload_token_estimate_total: 669`, `issue_count: 0`.
- Clean checkout ruff check: all checks passed.
- Clean checkout ruff format check: 4 files already formatted.

## Thresholds Chosen

- `global_surface_warning_tokens = 60000`
- `global_surface_failure_tokens = 120000`
- `activity_auto_warning_tokens = 1200`
- `activity_auto_failure_tokens = 2400`

Rationale: the committed baseline is below the warning line at 46737 estimated global tokens and 669 total activity auto-load tokens. These thresholds are deliberately advisory rather than release-blocking; they create early warning before global startup approaches unwieldy raw SoT behavior while leaving room for normal governance text growth.

## Files Changed

- `scripts/benchmarks/activity_envelope_load.py`
- `scripts/benchmarks/metric_registry.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `.claude/skills/gtkb-benchmarks/SKILL.md`
- `.codex/skills/gtkb-benchmarks/SKILL.md`
- `config/agent-control/activity-envelope-sharding.toml`
- `platform_tests/scripts/test_benchmark_activity_envelope_load.py`

## Known Residuals And Dependency Notes

- WI-4951 depends on the WI-4946 taxonomy baseline. WI-4946 now has focused commit evidence in `b83abaab7` and a revised bridge entry at `bridge/gtkb-envelope-sharding-taxonomy-baseline-005.md`, but it is still awaiting Loyal Opposition verification at the time of this report. If Loyal Opposition wants strict dependency ordering, verify WI-4946 first, then verify this report.
- `scripts/generate_codex_skill_adapters.py --check` currently reports unrelated adapter/manifest drift outside the WI-4951 target paths. The generated benchmark adapter itself was regenerated from `.claude/skills/gtkb-benchmarks/SKILL.md`, and the drift report did not include `.codex/skills/gtkb-benchmarks/SKILL.md` after regeneration.
- The implementation-report helper plan lists unrelated dirty worktree files because this checkout has broad pre-existing local changes. This report intentionally scopes implementation evidence to focused commit `f0d2978da8da6cad5840bafd30e243b80fe2e2c2` and the seven approved target paths.

## Acceptance Criteria Status

- [x] Added compact read-only benchmark/reporting surface for global and activity envelope load.
- [x] Exposed the report through `gt benchmarks activity-envelope-load --json`.
- [x] Added threshold configuration for global and per-activity payload estimates.
- [x] Added failure detection for activity payloads classified as global baseline, history state outside explicit-query, and missing never-startup raw archival payload coverage.
- [x] Updated benchmark skill docs for Claude and Codex.
- [x] Added focused tests for the real config, a global-leak failure mode, and the public `gt` CLI JSON output.
- [x] Produced focused commit and clean-checkout verification evidence.

## Risk And Rollback

Residual risk: token estimates use a deterministic 4-character heuristic rather than model-specific tokenizer accounting. This is intentional for stable, no-network, cross-harness reporting.

Residual risk: the global baseline estimate reflects configured surfaces and does not prove every harness runtime loaded exactly those files. Harness projection parity remains in WI-4950.

Rollback for this slice is to remove `scripts/benchmarks/activity_envelope_load.py`, remove the CLI command and metric registry entry, remove the threshold table, revert the benchmark skill doc additions, and remove `platform_tests/scripts/test_benchmark_activity_envelope_load.py`. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the benchmark measures the session/activity envelope split and flags raw archival or unrelated activity loads.
2. Verify that the public `gt benchmarks activity-envelope-load --json` surface produces compact PASS output.
3. Verify that the focused commit and clean-checkout evidence satisfy the approved proposal.
4. Return `VERIFIED` if the implementation and evidence satisfy the approved proposal; otherwise return `NO-GO` with findings.
