NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T17-04-15Z-prime-builder-A-3f1076
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex dispatcher-spawned headless; resolved_role=prime-builder; approval_policy=never; workspace=E:\GT-KB

# GT-KB Bridge Implementation Report - WI-5045 Watchdog Tiered Restoration Policy

bridge_kind: implementation_report
Document: gtkb-wi5045-watchdog-tiered-restoration-policy
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-002.md
Approved proposal: bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md
Recommended commit type: feat:

Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-5045

## Implementation Claim

Implemented the stateless watchdog restoration policy engine for WI-5045.

The implementation adds `groundtruth_kb.watchdog.restore_policy` with explicit result objects:

- `AutoRestoreAction` for safe/idempotent actions eligible for a later executor.
- `EscalateAction` for canonical/manual/unknown actions or retry exhaustion that must become visible as `ADVISORY`.
- `NoRestoreAction` for healthy, stale-probe, visibility-only, or no-op cases where auto-restore is forbidden or unnecessary.

The policy consumes fresh probe status plus SoT registry `restore_action` metadata. It classifies `ensure_alive` and `regenerate_from_source` as safe/idempotent, classifies `git_restore` and `membase_export_restore` as canonical fail-loud actions, blocks `visibility_only` before any auto-restore path, requires a fresh failed probe, and escalates when retry attempts are exhausted.

The existing service/SoT watchdog artifact probe now carries `restore_action` metadata in each artifact probe result so downstream execution/resource-bounding slices can make policy decisions without re-reading or reinterpreting registry records.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires tiered restoration across platform services and SoT-registry artifacts.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Requires safe-vs-canonical classification, fail-loud canonical handling, visibility-only overrides, fresh probes, retry exhaustion escalation, and no canonical auto-mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires this proposal and later report to flow through the bridge file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires complete specification linkage and verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the project authorization, project, and work item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires executed spec-derived tests before verification.
- `GOV-STANDING-BACKLOG-001` - Treats WI-5045 and the project as durable work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Require durable linkage and explicit lifecycle evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires all target paths to remain inside `E:\GT-KB`.

## Owner Decisions / Input

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` authorizes WI-5045 implementation under the project envelope.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` is the operative owner policy: safe/idempotent actions may auto-execute, canonical/at-risk actions must fail loud, and repeated failures must escalate.
- `DELIB-20266140` requires visibility-only overrides to remain no-auto-restore.

No new owner decision was required by this implementation.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized all watchdog work items with per-WI GO.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected tiered auto-restore plus fail-loud escalation.
- `DELIB-20266276` - Dispatcher D2/D4 precedent for full auto-recovery and alert-and-degrade behavior.
- `DELIB-20266140` - Visibility-only precedent forbidding automatic restoration of owner-marked manual controls.
- `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md` - Approved implementation proposal carried forward.
- `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Implementation Authorization Evidence

- Live Prime scan confirmed latest status `GO` for `gtkb-wi5045-watchdog-tiered-restoration-policy`.
- Work-intent claim command: `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5045-watchdog-tiered-restoration-policy`
- Claim result: acquired for dispatcher session `2026-07-06T17-04-15Z-prime-builder-A-3f1076`, project `PROJECT-GTKB-SERVICE-SOT-WATCHDOG`, work item `WI-5045`.
- Implementation-start command: `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5045-watchdog-tiered-restoration-policy`
- Authorization result: latest status `GO`; packet hash `sha256:a7b5e7e7dddf0958502418e22f5dda48dbbf1343b7bc2ed2e56383034be2ac6c`; requirement sufficiency `sufficient`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | `test_gtkb_service_sot_restore_policy.py` covers safe auto-restore, canonical fail-loud escalation, visibility-only blocking, retry-exhaustion escalation, and fresh-probe gating. Targeted pytest passed: 8 passed. |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | `test_policy_consumes_sot_artifact_restore_action_metadata` and `test_artifact_probe_carries_restore_action_metadata` verify policy decisions are derived from SoT registry metadata plus watchdog probe output, not ad hoc branches. Combined watchdog pytest passed: 14 passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Scoped changed paths are all under `E:\GT-KB` and within the approved target paths: `groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py`, `groundtruth-kb/src/groundtruth_kb/watchdog/restore_policy.py`, `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`, and `platform_tests/scripts/test_gtkb_service_sot_restore_policy.py`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed as the next numbered bridge file through the governed implementation-report helper after latest `GO`, claim, and implementation-start packet checks. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's linked specifications and maps them to executed evidence above. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project authorization, project, and work item metadata are repeated above and were validated by `implementation_authorization.py begin`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Executed pytest plus separate `ruff check` and `ruff format --check` commands are recorded below. |
| `GOV-STANDING-BACKLOG-001` | The implementation is scoped to WI-5045 under `PROJECT-GTKB-SERVICE-SOT-WATCHDOG` and the active project authorization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge proposal, GO verdict, implementation claim, command evidence, and this post-implementation report preserve the artifact lifecycle trail. |

## Commands Run

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_service_sot_restore_policy.py -q --tb=short --basetemp .gtkb-state\pytest-wi5045
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_service_sot_watchdog.py platform_tests\scripts\test_gtkb_service_sot_restore_policy.py -q --tb=short --basetemp .gtkb-state\pytest-wi5045-full
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\watchdog\__init__.py groundtruth-kb\src\groundtruth_kb\watchdog\restore_policy.py groundtruth-kb\src\groundtruth_kb\watchdog\service_sot.py platform_tests\scripts\test_gtkb_service_sot_restore_policy.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\watchdog\__init__.py groundtruth-kb\src\groundtruth_kb\watchdog\restore_policy.py groundtruth-kb\src\groundtruth_kb\watchdog\service_sot.py platform_tests\scripts\test_gtkb_service_sot_restore_policy.py
```

## Observed Results

- Targeted WI-5045 pytest: `8 passed, 2 warnings in 0.24s`.
- Combined watchdog regression pytest: `14 passed, 2 warnings in 0.45s`.
- Ruff lint: `All checks passed!`
- Ruff format check: `4 files already formatted`.

Warnings observed:

- Pytest reports `Unknown config option: asyncio_mode` from the repo config.
- Pytest cache writes report an existing cache-path warning under `.pytest_cache`.

Neither warning changes the targeted test outcomes.

## Files Changed

Scoped WI-5045 implementation files:

- `groundtruth-kb/src/groundtruth_kb/watchdog/restore_policy.py` - new stateless policy engine and structured result objects.
- `groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py` - exports the public policy decision objects and helpers.
- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py` - includes `restore_action` in artifact probe payloads.
- `platform_tests/scripts/test_gtkb_service_sot_restore_policy.py` - spec-derived tests for tier classification, fresh-probe gating, visibility-only override, canonical escalation, retry exhaustion, and metadata flow.

Approved target path not changed:

- `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py` - no mutation was needed; the policy imports the existing `STATUS_ADVISORY` constant.

Dirty-worktree note:

- The repository already contained many unrelated modified/untracked files before this implementation. They are not claimed by this report. The scoped WI-5045 status command after implementation showed only the four changed paths listed above.

## Acceptance Criteria Status

- [x] Safe/idempotent action returns explicit `AutoRestoreAction`.
- [x] Canonical-tier action returns fail-loud `EscalateAction` with `ADVISORY` escalation status and no auto-mutation path.
- [x] Visibility-only targets return `NoRestoreAction` before any auto-restore eligibility.
- [x] Fresh failed probe is required before auto-restore.
- [x] Retry exhaustion returns `EscalateAction` with `retry_exhausted=True`.
- [x] Policy consumes `SoTArtifact.restore_action` and watchdog probe output.
- [x] Artifact probe payload carries `restore_action` metadata for later execution/resource-bound slices.
- [x] Tests and separate ruff lint/format gates were executed.

## Risk And Rollback

Residual risk is limited to the classification mapping. This slice does not execute restore actions and does not mutate canonical stores. Later execution/resource-bounding work should consume these decisions rather than duplicate the safety matrix.

Rollback is a single revert of the four scoped files listed above plus this bridge report.

## Loyal Opposition Asks

1. Verify that the policy mapping satisfies `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`.
2. Verify that the report's executed commands satisfy the specification-derived verification gate.
3. Return `VERIFIED` if the implementation satisfies the approved proposal, otherwise return `NO-GO` with findings.

File bridge scan contribution: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
