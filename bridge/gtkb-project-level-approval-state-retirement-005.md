NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-30T23-06-19Z-prime-builder-A-c0de5d
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime, 2026-06-30
author_model_configuration: Codex desktop heartbeat session; sandbox=danger-full-access; approval_policy=never; role=Prime Builder

# GT-KB Bridge Implementation Report - Retire individual work-item approval-state authority

bridge_kind: implementation_report
Document: gtkb-project-level-approval-state-retirement
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-project-level-approval-state-retirement-004.md
Approved proposal: bridge/gtkb-project-level-approval-state-retirement-003.md
Date: 2026-06-30 UTC
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4936
Recommended commit type: feat:

## Implementation Claim

Implemented the bounded `WI-4936` slice to retire individual work-item approval-state authority from current load-bearing GT-KB behavior. Project authorization, live bridge `GO`, work-intent claim, and the implementation-start authorization packet remain the implementation authority chain.

Historical rows and compatibility imports are preserved, but legacy `approval_state` metadata no longer grants text-edit permission, creates doctor orphan findings, drives startup top-priority selection, drives backlog-triage retirement labels, or gets backfilled/promoted by helper scripts.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-PROJECT-FIT-AUTO-ATTACHMENT-001`
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`
- `SPEC-ENVELOPE-DISCLOSURE-UI-001`

## Owner Decisions / Input

- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - owner decision that project approval supersedes individual work-item approval state.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` - active PAUTH used by the implementation-start packet.
- No new owner decision is required by this report.

## Prior Deliberations

- `bridge/gtkb-project-level-approval-state-retirement-003.md` - approved revised proposal.
- `bridge/gtkb-project-level-approval-state-retirement-004.md` - Loyal Opposition GO verdict.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - owner decision carried into implementation.

## Implementation Details

- Rewrote `.claude/rules/backlog-approval-state.md` as a retirement rule: historical metadata only, not implementation authority.
- Converted `groundtruth_kb.backlog.approval_state` into a compatibility shim that preserves old labels but no longer derives implementation authority from bridge status, AUQ evidence, or transition state.
- Made `scripts/backlog_approval_gate.py` and `scripts/backfill_approval_state.py` compatibility no-ops, with JSON output marking them deprecated and non-mutating.
- Removed the `approval_state=bridge_authorized` text-edit bypass from `gt backlog update`; title/description edits now require `--owner-approved`, active PAUTH citation, or existing DELIB citation.
- Changed doctor backlog health so orphan findings are based on implementation-active `resolution_status` or `stage`, not legacy approval metadata.
- Changed startup backlog projection and top-priority selection so top priority uses non-terminal status and priority ordering, not legacy approval metadata.
- Renamed backlog-triage/disposition semantics from `retire_candidate_unapproved_noise` to `retire_candidate_router_low_signal`; candidate classification no longer inspects legacy approval metadata.
- Stopped Stage 3 advisory candidate promotion from stamping a legacy approval state.
- Updated focused tests to assert that legacy approval metadata is ignored and that project/status/PAUTH paths remain authoritative.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python -m pytest platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short` passed 123 tests; implementation-start packet succeeded for the active PAUTH. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work-intent claim acquired and extended for `gtkb-project-level-approval-state-retirement`; this report is filed through `.codex/skills/bridge/helpers/impl_report_bridge.py` as version 005. |
| `GOV-STANDING-BACKLOG-001` | `platform_tests/cli/test_backlog_update_title_desc.py` and `platform_tests/scripts/test_fab18_backlog_dignity.py` passed 13 tests, including negative coverage for legacy text-edit and doctor authority. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` / `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | Fixed-string scan found no old load-bearing patterns: `retire_candidate_unapproved_noise`, `implementation_authorized requires`, `approval_state=bridge_authorized`, `approval_state='implementation_authorized'`, `approval_state == "bridge_authorized"`, or `current['approval_state']` in the approved live target set. |
| `SPEC-ENVELOPE-DISCLOSURE-UI-001` | `python -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k "top_priority or recommender or backlog_metrics or membase"` passed 11 selected tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests, retired-helper smoke checks, lint, format, and obsolete-string scan are recorded below. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation edits are in approved GT-KB target paths; no adopter application paths were changed. |

## Commands Run

```powershell
$session = '2026-06-30T23-06-19Z-prime-builder-A-c0de5d'
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts\bridge_claim_cli.py claim gtkb-project-level-approval-state-retirement --session-id $session --ttl-seconds 7200
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts\implementation_authorization.py begin --bridge-id gtkb-project-level-approval-state-retirement --session-id $session --expires-minutes 180
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts\bridge_claim_cli.py extend gtkb-project-level-approval-state-retirement --session-id $session
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts\backlog_approval_gate.py WI-4936 implementation_authorized --json
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts\backfill_approval_state.py --json
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m pytest platform_tests/cli/test_backlog_update_title_desc.py platform_tests/scripts/test_fab18_backlog_dignity.py -q --tb=short
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m pytest platform_tests/scripts/test_backlog_triage_benchmark.py platform_tests/scripts/test_router_corpus_dispose.py platform_tests/scripts/test_advisory_candidate_promote.py -q --tb=short
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k "top_priority or recommender or backlog_metrics or membase"
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m pytest platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe' check <changed-python-targets>
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe' format --check <changed-python-targets>
rg -n -F -e 'retire_candidate_unapproved_noise' -e 'implementation_authorized requires' -e 'approval_state=bridge_authorized' -e "approval_state='implementation_authorized'" -e 'approval_state == "bridge_authorized"' -e "current['approval_state']" <approved-live-target-files>
```

## Observed Results

- Work-intent claim acquired at `2026-06-30T23:09:11Z`; extension set implementation grace to `2026-07-01T00:19:11Z`.
- Implementation-start packet succeeded with `packet_hash: sha256:9fb1f961ad02fd116b84d43d1b8028c3dd01ab78b73db423c09e619353807cf3` and latest GO `bridge/gtkb-project-level-approval-state-retirement-004.md`.
- `scripts/backlog_approval_gate.py ... --json` returned deprecated no-op payload with `allowed: true` and no authority claim.
- `scripts/backfill_approval_state.py --json` returned deprecated no-op payload with `updated: 0`.
- CLI/doctor tests: `13 passed, 1 warning`.
- Benchmark/disposition/promotion tests: `35 passed`.
- Startup targeted tests: `11 passed, 87 deselected`.
- Project/implementation authorization tests: `123 passed, 1 warning`.
- Ruff check: `All checks passed!`.
- Ruff format check: `19 files already formatted`.
- Retired load-bearing string scan: no matches; `rg` exited 1 due zero matches.

## Additional Verification Observation

A broader startup run was also attempted:

```powershell
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short
```

It produced `97 passed, 1 failed`. The failure is unrelated to this slice: `test_dashboard_and_report_are_written_with_time_series_kpi` expected dashboard title `Agent Red GT-KB Dashboard`, while current code emitted `GT-KB Operations Dashboard`. I did not change that dashboard expectation because it is outside the approved approval-state retirement scope.

## Files Changed

- `.claude/rules/backlog-approval-state.md`
- `groundtruth-kb/src/groundtruth_kb/backlog.py`
- `groundtruth-kb/src/groundtruth_kb/backlog/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth.db` - governance/claim/authorization state; no approval-state data migration was performed by this implementation.
- `platform_tests/cli/test_backlog_update_title_desc.py`
- `platform_tests/governance/__init__.py`
- `platform_tests/scripts/test_advisory_candidate_promote.py`
- `platform_tests/scripts/test_backlog_triage_benchmark.py`
- `platform_tests/scripts/test_fab18_backlog_dignity.py`
- `platform_tests/scripts/test_router_corpus_dispose.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`
- `scripts/backfill_approval_state.py`
- `scripts/backlog_approval_gate.py`
- `scripts/benchmarks/backlog_triage.py`
- `scripts/hygiene/advisory_candidate_promote.py`
- `scripts/hygiene/router_corpus_dispose.py`
- `scripts/session_self_initialization.py`

Approved target paths intentionally not changed after scan/verification because no current load-bearing approval-state reference was found or existing coverage remained valid:

- `.claude/rules/codex-standing-priorities.md`
- `.claude/skills/kb-batch/SKILL.md`
- `.codex/skills/kb-batch/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`
- `platform_tests/scripts/test_project_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: source, script, rule, and test surfaces changed to retire a governance behavior and preserve compatibility shims.

## Acceptance Criteria Status

- [x] Active project-level PAUTH plus project membership remains the approval evidence path; no live surface blocks on legacy work-item approval metadata.
- [x] Startup Top-3/project priority selection no longer filters on legacy approval metadata and uses status/priority instead.
- [x] Old WI-3271 approval-state taxonomy is historical/superseded outside append-only bridge/audit history and compatibility shims.
- [x] Bridge GO, implementation-start packet, target path scope, spec-derived tests, implementation report, and Loyal Opposition verification remain mandatory.

## Risk And Rollback

Risk is moderate because the slice touches governance, startup, doctor, CLI, benchmark, and test surfaces. The key residual risk is compatibility: historical rows and external imports may still mention legacy approval labels. The implementation keeps compatibility shims but makes them non-authoritative.

Rollback is a revert of the listed source/rule/test changes plus any related non-bridge governance state if directed by the owner. Bridge files are append-only audit artifacts and must not be deleted by rollback.

## Loyal Opposition Asks

1. Verify that legacy work-item approval metadata no longer grants, blocks, or prioritizes implementation work in the touched live surfaces.
2. Verify that remaining literal references are retirement/compatibility or negative-test evidence, not authority.
3. Confirm the unrelated dashboard-title test failure is outside this bridge scope or return NO-GO only if it materially affects this implementation.
