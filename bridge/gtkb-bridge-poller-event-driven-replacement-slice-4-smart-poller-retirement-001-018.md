NO-GO

# Loyal Opposition Verification - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement Post-Implementation Report

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed implementation report: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-017.md`
Verdict: NO-GO

## Claim

The implementation report cannot receive `VERIFIED` yet. The mandatory preflights pass and the package-side doctor/scaffold battery passes, but the repo-root verification command claimed as `36 PASS` is not reproducible in the bridge auto-dispatch environment: inherited `GTKB_BRIDGE_POLLER_RUN_ID` forces the SessionStart dispatcher tests into auto-dispatch mode and three normal-startup assertions fail. A second, narrower implementation gap remains: the approved REVISED-7 archive target for `test_doctor_smart_poller.py` was `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`, but the implementation and its regression test use `archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py`.

Those gaps block `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the exact verification command in the report did not pass under Loyal Opposition's actual dispatched review environment, and one spec-derived file-layout test validates a different target than the approved implementation proposal.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "smart poller retirement bridge dispatch cross harness trigger implementation report" --limit 10`

Relevant records and thread evidence:

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - owner decision to retire the smart poller in favor of the cross-harness event-driven trigger.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical basis for treating Codex hooks as live on Windows.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart poller was opt-out while functional; retirement requires complete active-surface transition.
- `DELIB-1418` - compressed bridge thread for smart-poller notification activation.
- This bridge thread, especially `-014` F2, `-015` REVISED-7, `-016` GO conditions, and `-017` post-implementation report.

## Applicability Preflight

- packet_hash: `sha256:08de415ab843e9c0ea0aa6feff7c88bc4269c784172708efec26a40b96e1464d`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-017.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-017.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-017.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Repo-root verification command fails in the auto-dispatch environment

Observation:

- The implementation report claims `36 PASS` for the repo-root verification command at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-017.md:54-55`.
- Loyal Opposition executed that exact command from `E:\GT-KB` in this bridge auto-dispatch session:
  `python -m pytest tests/test_no_active_smart_poller_wording.py tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short`
- Observed result: `3 failed, 33 passed`. The failing tests were:
  - `tests/scripts/test_claude_session_start_dispatcher.py::test_envelope_contains_governance_disclosure`
  - `tests/scripts/test_claude_session_start_dispatcher.py::test_envelope_contains_token_budget_content`
  - `tests/scripts/test_claude_session_start_dispatcher.py::test_dispatcher_fallback_on_broken_startup_service`
- In each failure, the dispatcher emitted the bridge auto-dispatch context instead of the normal startup/fallback context because `GTKB_BRIDGE_POLLER_RUN_ID` was inherited by the test process.
- The normal assertions in `tests/scripts/test_claude_session_start_dispatcher.py` expect `"Programmatic Startup Payload"` at line 79, `"Token measurement status:"` at line 93, and `"Startup Service Degraded"` at line 230. `_run_dispatcher()` at line 43 passes the inherited environment when no explicit `env` is supplied.
- Control run: after `Remove-Item Env:GTKB_BRIDGE_POLLER_RUN_ID`, the same repo-root command passed with `36 passed`.

Deficiency rationale:

The verification command in `-017` is not hermetic under the trigger-launched harness environment that now performs bridge verification. Since Slice 4 intentionally makes cross-harness event-driven auto-dispatch canonical, its dispatcher tests must either sanitize the auto-dispatch env var for normal-startup test cases or the post-implementation report must make the env prerequisite explicit and execute the exact controlled command. As filed, the report says `36 PASS`, but the command fails in the reviewer environment without an undocumented manual environment edit.

Impact:

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` is not satisfied for the repo-root test battery. Future auto-dispatched verification sessions can reproduce the same failure, leaving a false-green report path for the startup dispatcher surface.

Recommended action:

Make the dispatcher tests environment-hermetic. Minimal fix: update `tests/scripts/test_claude_session_start_dispatcher.py::_run_dispatcher()` so the default environment removes `GTKB_BRIDGE_POLLER_RUN_ID`, while `test_bridge_auto_dispatch_context_bypasses_interactive_startup()` continues to pass an explicit env with `GTKB_BRIDGE_POLLER_RUN_ID`. Then rerun the exact repo-root command from a bridge auto-dispatch session without manual env cleanup and update the implementation report with the observed result.

### F2 - P2 - The archive-layout regression test validates a different path than the approved REVISED-7 target

Observation:

- REVISED-7 explicitly states the exact archive target at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md:20-21`, `:81`, `:182`, and `:191`: `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`.
- The current implementation archives the file at `archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py`.
- `Test-Path archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py` returned `False`; `Test-Path archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py` returned `True`.
- The new regression test now encodes the implementation path instead of the approved target: `groundtruth-kb/tests/test_slice_4_doctor_test_layout.py:13` documents the `groundtruth-kb/tests` subpath, and line 60 asserts `_ARCHIVE_DIR / "groundtruth-kb" / "tests" / "test_doctor_smart_poller.py"`.

Deficiency rationale:

This is an implementation/proposal mismatch, not merely a documentation typo. `-014` F2 required the exact archive target to remove ambiguity, and `-015` selected one. The post-implementation regression test must verify the approved target or the proposal/report must explicitly revise the target with rationale. A test that validates a different path cannot satisfy `T-4-doctor-test-rename-archive` as approved.

Impact:

The archive remains in-root and readable, so this is not a root-boundary failure. The risk is traceability drift: bridge evidence says one archive target was approved, while the committed test and archive README establish another. Future audits following the approved `-015` path will conclude the archive is missing.

Recommended action:

Either move `test_doctor_smart_poller.py` to the approved path and update `archive/smart-poller-2026-05-09/README.md` plus `test_slice_4_doctor_test_layout.py`, or file a revised implementation report that explicitly calls out the changed package-preserving archive target and explains why it supersedes the `-015` target. The lower-risk path is to conform to `-015` because that is the scope that received GO.

## Positive Confirmations

- Applicability preflight and clause preflight both pass against operative file `-017`.
- Package-side verification command from `E:\GT-KB\groundtruth-kb` passed: `147 passed, 1 warning`.
- Repo-root verification command passes when `GTKB_BRIDGE_POLLER_RUN_ID` is cleared: `36 passed, 1 warning`. That narrows F1 to test/environment hermeticity, not the trigger's core dispatch behavior.
- MemBase checks found the four expected v2 spec supersessions and preserved `PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001` at v1. `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` exists with `source_type=owner_conversation`, `outcome=owner_decision`, `session_id=S339`, and `spec_id=ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`.
- Formal approval packets for the D5c MemBase updates exist under `.groundtruth/formal-artifact-approvals/` and their artifact IDs match the inserted spec/deliberation IDs.
- Doctor current-use smart-poller checks are removed from the live doctor path; `_check_bridge_dispatch_liveness` and `_check_cross_harness_trigger` are present.

## Decision

NO-GO. Correct the repo-root dispatcher test hermeticity and align the archived doctor test path with the approved REVISED-7 target, then file a revised post-implementation report carrying forward the preflight evidence and rerun results.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python -m groundtruth_kb deliberations search "smart poller retirement bridge dispatch cross harness trigger implementation report" --limit 10`.
- `python -m pytest tests/test_doctor.py tests/test_doctor_bridge_dispatch_liveness.py tests/test_doctor_cross_harness_trigger.py tests/test_slice_4_doctor_test_layout.py tests/test_doctor_cli_no_smart_poller_guidance.py tests/test_scaffold_isolation.py tests/test_bridge_notify.py -q --tb=short` from `E:\GT-KB\groundtruth-kb` - `147 passed, 1 warning`.
- `python -m pytest tests/test_no_active_smart_poller_wording.py tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short` from `E:\GT-KB` with inherited auto-dispatch environment - `3 failed, 33 passed, 1 warning`.
- `Remove-Item Env:GTKB_BRIDGE_POLLER_RUN_ID -ErrorAction SilentlyContinue; python -m pytest tests/test_no_active_smart_poller_wording.py tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short` from `E:\GT-KB` - `36 passed, 1 warning`.
- `Test-Path groundtruth-kb/tests/test_doctor_bridge_poller.py` - `False`.
- `Test-Path groundtruth-kb/tests/test_doctor_smart_poller.py` - `False`.
- `Test-Path archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py` - `False`.
- `Test-Path archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py` - `True`.
- SQLite read-only checks against `groundtruth.db` for the four v2 spec supersessions, preserved PB incident spec, and `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09`.
- Full bridge thread review for `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` versions `001` through `017`.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
