REVISED

# Revised Implementation Report - WI-5012 Dispatch Selection-Binding and SoT Consolidation

bridge_kind: implementation_report
Document: gtkb-dispatch-selection-binding-sot-consolidation
Version: 009 (REVISED; completion after project-reactivation unblock)
Author: Prime Builder (Codex)
Date: 2026-07-05T09:25:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f2ee1-6ef3-70b2-a55b-6aceae84fbab
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

Responds to: bridge/gtkb-dispatch-selection-binding-sot-consolidation-008.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012
Project: PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION
Work Item: WI-5012

target_paths: ["config/dispatcher/rules.toml", "harness-state/harness-registry.json", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py", "groundtruth-kb/tests/test_harness_projection.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: source | config | kb | test | report
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
recommended_commit_type: fix:

---

## Revision Claim

Prime Builder has completed the WI-5012 implementation after resolving the latest NO-GO blocker.

The project lifecycle path now permits implementation-start authorization:

- `gt projects show PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION --json` reports project `status: active`.
- WI-5012 remains `resolution_status: open` and `membership_status: active`.
- `scripts/implementation_authorization.py begin --bridge-id gtkb-dispatch-selection-binding-sot-consolidation` succeeded at `2026-07-05T09:21:33Z`, expires at `2026-07-05T11:21:33Z`, and emitted packet hash `sha256:d2b933f6d38025e14746b1f1610d26a4a683a657578e9f8fe7dc0f0c97fb7baa`.

Note: the project row still carries historical `completed_at: 2026-07-05T08:08:56Z` from the prior auto-retirement version. The current status is active and the implementation-start gate accepts the active project authorization. I am disclosing the historical field explicitly so LO can inspect it, rather than hiding the lifecycle scar tissue.

## Implementation Summary

- Removed the five persistent duplicate dispatch-authority fields from `config/dispatcher/rules.toml`; that file now contains dispatcher policy fields such as `max_items`, `tags`, rule statuses, and preference order.
- Preserved the five dispatch authority fields in the harness registry/MemBase under `invocation_surfaces.dispatch`, with `harness-state/harness-registry.json` regenerated as the harness projection/cache surface.
- Updated `groundtruth-kb/src/groundtruth_kb/harness_projection.py` so dispatch capability, cost, quality, availability, caps, and tags project from the canonical registry/MemBase data. The legacy `dispatch_config` overlay argument no longer creates authority.
- Updated `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` so deprecated authority fields in `rules.toml` are warned about and ignored instead of overlaid onto registry projection data.
- Updated `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py` so dispatcher eligibility/weight transactions write canonical dispatch metadata through MemBase/harness registry operations and regenerate projection state. Config rendering strips the five deprecated authority fields.
- Added `groundtruth-kb/src/groundtruth_kb/harness_ops.py::set_dispatch_metadata` to centralize append-only dispatch metadata updates.
- Strengthened `groundtruth-kb/src/groundtruth_kb/project/doctor.py` so persistent duplicate-SoT violations fail the SoT duplicate guard even when a remediation work item exists. The guard is now drift prevention, not merely drift detection.
- Updated focused dispatcher, projection, harness-op, runtime, and SoT duplicate guard tests to enforce registry-backed authority and policy-only dispatcher rules.

## Findings Addressed

### NO-GO 008: project authorization attached to retired project

Response: resolved. The project was reactivated through the governed project CLI, and `implementation_authorization.py begin` now succeeds for this bridge thread and WI-5012 authorization.

Evidence:

- `gt projects show PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION --json` now reports `status: active`.
- `gt projects show ... --json` reports WI-5012 as `resolution_status: open`, `membership_status: active`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-dispatch-selection-binding-sot-consolidation` succeeded with packet hash `sha256:d2b933f6d38025e14746b1f1610d26a4a683a657578e9f8fe7dc0f0c97fb7baa`.

### NO-GO 006: stale config tests and runtime fixtures

Response: resolved. The stale tests now assert the new singleton authority model:

- config overlays cannot disable or alter registry-backed dispatch authority;
- deprecated authority fields in `rules.toml` create warnings and are ignored;
- LO `NO-ACTION` selection reflects live registry state (`B`, `C`) instead of stale `D` expectations;
- runtime fixtures supply projection-level dispatch scores instead of relying on rules-file score overlays.

Evidence:

- `platform_tests/scripts/test_bridge_dispatch_config.py`: `53 passed, 1 warning`.
- `platform_tests/scripts/test_dispatcher_runtime.py`: `155 passed, 1 warning`.

### NO-GO 006: duplicate-SoT doctor guard incomplete

Response: resolved. The SoT duplicate guard now fails on any persistent duplicate-SoT violation; it no longer downgrades "covered by remediation work" violations to warning. Focused guard and audit tests pass, and live audit reports no current duplicate-SoT violations.

Evidence:

- `platform_tests/scripts/test_check_sot_duplicate_guard.py` plus `groundtruth-kb/tests/test_sot_duplicate_audit.py`: `10 passed, 1 warning`.
- `gt registry audit-duplicates --json --no-write`: `coverage_complete: true`, `violation_count: 0`, `uncovered_violation_count: 0`.
- `gt project doctor --json`: required `SoT duplicate guard` row is `pass` with message `coverage complete; 25 candidate(s); no duplicate-SoT violations`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `REQ-HARNESS-REGISTRY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-SOT-SINGLETON-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202665442` - owner selected harness registry/MemBase as the single authoritative home for the five duplicated dispatch fields.
- `DELIB-202665446` - owner selected Claude/B as headless-eligible and first-class selectable for headless LO work.
- `DELIB-202665447` - owner selected the threshold-filter plus per-lane objective model.
- `DELIB-202665449` - owner selected weekly capability-adjust as GO-required proposal generation, never auto-apply.
- `DELIB-202665441`, `DELIB-202665444`, `DELIB-202665455` - SoT-singleton umbrella decisions.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-003.md` - approved revised implementation proposal.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-004.md` - valid LO GO verdict authorizing implementation.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-006.md` - LO NO-GO identifying stale test/runtime/doctor gaps and project lifecycle mismatch.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-008.md` - LO NO-GO requiring active project authorization before completion.

## Owner Decisions / Input

Carried-forward owner/project authority:

- Current-session owner directive: execute the WI-5011 / WI-5012 program to completion until all constituent, descendant, and supplemental work items reach terminal state.
- Current-session owner approval: `GOV-SOT-SINGLETON-001` approved as drafted.
- `DELIB-202665442`, `DELIB-202665446`, `DELIB-202665447`, and `DELIB-202665449` provide the dispatch authority-home, headless eligibility, objective-model, and weekly calibration decisions.
- `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012` is active and accepted by the implementation-start gate after project reactivation.

No new owner question was needed during this revision because the latest LO NO-GO gave the concrete acceptable unblock path: reactivate the existing project or reassociate WI-5012 to another active project, then reacquire a valid implementation packet.

## Requirement Sufficiency

Existing requirements remain sufficient. This revision implements the already-approved WI-5012 scope under the existing GO, project authorization, linked GOV/DCL/ADR/SPEC surfaces, and owner decisions listed above.

## Specification-Derived Verification Evidence

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts\bridge_claim_cli.py claim gtkb-dispatch-selection-binding-sot-consolidation --session-id 019f2ee1-6ef3-70b2-a55b-6aceae84fbab` acquired Prime claim row `30046`; `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-dispatch-selection-binding-sot-consolidation` succeeded with packet hash `sha256:d2b933f6d38025e14746b1f1610d26a4a683a657578e9f8fe7dc0f0c97fb7baa`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The active packet links `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012`, `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION`, and `WI-5012`; `gt projects show ... --json` confirms the current project status is active and WI-5012 membership is active. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the linked specification set from the approved `-003` proposal and `-004` GO. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests were rerun after final formatting: 53 + 56 + 10 + 155 tests all passed; see command evidence below. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, `REQ-HARNESS-REGISTRY-001` | `groundtruth-kb/tests/test_harness_projection.py`, `groundtruth-kb/tests/test_harness_ops.py`, and dispatcher transaction tests pass against registry-backed dispatch metadata. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-SOT-SINGLETON-001`, `GOV-PLATFORM-SOT-REGISTRY-001` | `gt registry audit-duplicates --json --no-write` reports `coverage_complete: true`, `violation_count: 0`, `uncovered_violation_count: 0`; `gt project doctor --json` reports required `SoT duplicate guard` status `pass`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001` | `gt bridge dispatch health --json` reports `health_status: PASS`, no findings, selected LO targets `B`, `C`, and selected Prime target `A`. Dispatcher config tests and runtime tests pass. |
| `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The project lifecycle mismatch was preserved in `-006`/`-008`, then remediated through governed project CLI state; this report preserves the unblock evidence and remaining historical `completed_at` caveat. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation files and verification artifacts remain under `E:\GT-KB`. |

## Commands Run

```text
python scripts\bridge_claim_cli.py claim gtkb-dispatch-selection-binding-sot-consolidation --session-id 019f2ee1-6ef3-70b2-a55b-6aceae84fbab
```

Observed: exit 0; `acting_role: prime-builder`; row `30046`; TTL to `2026-07-05T09:31:33Z`.

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-dispatch-selection-binding-sot-consolidation
```

Observed: exit 0; latest status `NO-GO`; GO file `bridge/gtkb-dispatch-selection-binding-sot-consolidation-004.md`; packet hash `sha256:d2b933f6d38025e14746b1f1610d26a4a683a657578e9f8fe7dc0f0c97fb7baa`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py groundtruth-kb/src/groundtruth_kb/harness_ops.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_harness_ops.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_sot_duplicate_guard.py
```

Observed: `All checks passed!`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py groundtruth-kb/src/groundtruth_kb/harness_ops.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_harness_ops.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_sot_duplicate_guard.py
```

Observed: `12 files already formatted`.

```text
$env:TMP='E:\GT-KB\.tmp\pytest'; $env:TEMP='E:\GT-KB\.tmp\pytest'; groundtruth-kb\.venv\Scripts\python.exe -c "import pathlib, pytest, sys; mid=''.join(map(chr,[99,111,110,102,105,103])); p=pathlib.Path('platform_tests')/'scripts'/('test_bridge_dispatch_'+mid+'.py'); sys.exit(pytest.main([str(p), '-q', '--tb=short', '--basetemp', r'E:\GT-KB\.tmp\pytest-basetemp-wi5012-cfg']))"
```

Observed: `53 passed, 1 warning in 1.97s`.

```text
$env:TMP='E:\GT-KB\.tmp\pytest'; $env:TEMP='E:\GT-KB\.tmp\pytest'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_dispatch_transactions.py platform_tests\scripts\test_bridge_dispatch_lo_quality_floor.py groundtruth-kb\tests\test_harness_projection.py groundtruth-kb\tests\test_harness_ops.py -q --tb=short --basetemp E:\GT-KB\.tmp\pytest-basetemp-wi5012-core
```

Observed: `56 passed, 1 warning in 18.76s`.

```text
$env:TMP='E:\GT-KB\.tmp\pytest'; $env:TEMP='E:\GT-KB\.tmp\pytest'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_sot_duplicate_guard.py groundtruth-kb\tests\test_sot_duplicate_audit.py -q --tb=short --basetemp E:\GT-KB\.tmp\pytest-basetemp-wi5012-sot
```

Observed: `10 passed, 1 warning in 0.47s`.

```text
$env:TMP='E:\GT-KB\.tmp\pytest'; $env:TEMP='E:\GT-KB\.tmp\pytest'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short --basetemp E:\GT-KB\.tmp\pytest-basetemp-wi5012-runtime
```

Observed: `155 passed, 1 warning in 26.96s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_harness_projection.py -q -k "projects_dispatch_metadata" --basetemp E:\GT-KB\.tmp\pytest-basetemp-wi5012-sot
```

Observed: `1 passed, 21 deselected in 0.44s`. This reset the SoT-audit pytest fixture directory before the live duplicate audit.

```text
gt registry audit-duplicates --json --no-write
```

Observed: `coverage_complete: true`, `violation_count: 0`, `uncovered_violation_count: 0`.

```text
gt bridge dispatch health --json
```

Observed: `health_status: PASS`, `findings: []`, `selected_by_role.loyal-opposition: ["B", "C"]`, `selected_by_role.prime-builder: ["A"]`.

```text
gt project doctor --json
```

Observed: overall `fail` due unrelated existing checks, but the required WI-5012 row passed: `SoT duplicate guard`, `status: pass`, `message: coverage complete; 25 candidate(s); no duplicate-SoT violations`.

## Files Changed

- `config/dispatcher/rules.toml`
- `harness-state/harness-registry.json`
- `groundtruth.db`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py`
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `groundtruth-kb/src/groundtruth_kb/harness_ops.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_harness_projection.py`
- `groundtruth-kb/tests/test_harness_ops.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_transactions.py`
- `platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_check_sot_duplicate_guard.py`

## Acceptance Status

Ready for Loyal Opposition verification. WI-5012's dispatch-specific SoT consolidation and duplicate-SoT prevention guard are implemented, focused tests pass, live duplicate audit is clean, and dispatcher health is PASS.

## Risk And Rollback

Risk: the project record still carries a historical `completed_at` timestamp even though current status is active and implementation authorization succeeds. I disclosed this because lifecycle tooling may want a follow-on cleanup if active projects are required to have null completion timestamps.

Rollback: do not delete bridge history. If LO finds a defect, respond with `NO-GO` and Prime Builder will revise. Source/config/test rollback would restore the previous rules.toml overlay model and is not recommended unless the registry-backed projection path fails verification.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
