NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3821-e2fc-75d2-814f-2a3ec0f71244
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB
Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-5046

# GT-KB Bridge Implementation Report - WI-5046 Watchdog Resource-Bounded Restore - 003

bridge_kind: implementation_report
Document: gtkb-wi5046-watchdog-resource-bounded-restore
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5046-watchdog-resource-bounded-restore-002.md
Approved proposal: bridge/gtkb-wi5046-watchdog-resource-bounded-restore-001.md
Recommended commit type: feat:

## Implementation Claim

Implemented the resource-bounded restore execution layer for the service/SoT watchdog.

- Added `groundtruth_kb.watchdog.resource_limits` with load deferral, fresh-probe gating, process-tree-cap abstraction, restore execution containment, and symptom-based success/failure results.
- The executor only runs `AutoRestoreAction` decisions from WI-5045 policy; canonical/manual/escalation decisions are skipped and cannot execute through this layer.
- A required whole-process-tree cap fails closed when unavailable.
- Success is judged by a post-restore symptom probe, not by aggregate load metrics.
- Exported the resource layer from `groundtruth_kb.watchdog`.
- Added spec-derived tests for load-aware deferral, CPU/memory thresholds, fresh-probe ordering, unavailable process-tree cap behavior, symptom-based success/failure, and non-auto policy skip behavior.

`groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py` and `scripts/gtkb_service_sot_watchdog.py` were inspected. No direct runner edit was needed in this slice because WI-5046 provides the reusable resource wrapper; restore invocation wiring remains constrained by WI-5045 policy decisions and later orchestration.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision is required. This implements the owner-authorized watchdog project scope under `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` and the tiered safety policy in `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED`.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION`
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED`
- `DELIB-20266276`
- `bridge/gtkb-wi5046-watchdog-resource-bounded-restore-001.md`
- `bridge/gtkb-wi5046-watchdog-resource-bounded-restore-002.md`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | `platform_tests/scripts/test_gtkb_service_sot_resource_limits.py` covers load deferral, fresh probe before restore, unavailable whole-process-tree cap fail-closed behavior, and symptom-probe success/failure. |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | Resource execution consumes WI-5045 `AutoRestoreAction` policy decisions and is exported from the watchdog package for runner orchestration. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are under approved GT-KB root target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / project-linkage DCL | Work ran after live claim and implementation authorization packet `sha256:1cc77354b0fb6f0b7f645b899685db7cd8b2d433c8f39275367fe68be70d413f`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, and format checks passed; exact commands are below. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-wi5046-watchdog-resource-bounded-restore --ttl-seconds 2400` - acquired live Prime Builder implementation claim.
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5046-watchdog-resource-bounded-restore` - passed; packet `sha256:1cc77354b0fb6f0b7f645b899685db7cd8b2d433c8f39275367fe68be70d413f`.
- `python -m pytest platform_tests\scripts\test_gtkb_service_sot_resource_limits.py platform_tests\scripts\test_gtkb_service_sot_watchdog.py platform_tests\scripts\test_gtkb_service_sot_restore_policy.py -q --tb=short` - 21 passed.
- `python -m ruff check groundtruth-kb\src\groundtruth_kb\watchdog\__init__.py groundtruth-kb\src\groundtruth_kb\watchdog\resource_limits.py platform_tests\scripts\test_gtkb_service_sot_resource_limits.py` - passed.
- `python -m ruff format --check groundtruth-kb\src\groundtruth_kb\watchdog\__init__.py groundtruth-kb\src\groundtruth_kb\watchdog\resource_limits.py platform_tests\scripts\test_gtkb_service_sot_resource_limits.py` - passed.

## Observed Results

- Host load over CPU or memory thresholds defers restore execution before restore is called.
- Fresh probe runs immediately before restore and can skip execution if the symptom is already healthy.
- Required process-tree cap unavailable returns a deferred result and does not call restore.
- Restore success is determined by a post-restore symptom probe.
- Non-auto policy decisions cannot execute through the resource layer.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/watchdog/resource_limits.py`
- `platform_tests/scripts/test_gtkb_service_sot_resource_limits.py`

## Inspected Paths

- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`
- `scripts/gtkb_service_sot_watchdog.py`

Other dirty worktree files pre-existed or belong to concurrent bridge or project work and were not edited for this WI.

## Acceptance Criteria Status

- [x] Heavy restore execution is deferred under simulated host load.
- [x] Restore execution is guarded by a fresh probe.
- [x] Whole-process-tree cap abstraction exists and fails closed when required but unavailable.
- [x] Success is measured by a symptom probe after restore.
- [x] Resource execution composes with WI-5045 policy decisions and does not broaden policy authorization.
- [x] Focused spec-derived tests, ruff check, and ruff format check pass.

## Risk And Rollback

Residual risk is moderate: this introduces an execution abstraction but does not yet wire a concrete Windows Job Object implementation. The fail-closed capability flag prevents false containment claims when the cap is unavailable. Rollback is a single revert of the three WI files above; bridge audit files remain append-only and must not be removed.

## Loyal Opposition Asks

1. Verify that the abstraction and fail-closed behavior satisfy the WI-5046 resource-bounding requirement without overclaiming OS-level enforcement.
2. Return `VERIFIED` if the implementation satisfies the approved proposal, otherwise return `NO-GO` with concrete target-path findings.
