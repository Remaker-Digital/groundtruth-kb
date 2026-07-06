GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 2026-07-06T16-27-38Z-loyal-opposition-C-e3a9bd
author_model: Gemini 3.5 Flash (High)
author_model_version: Gemini 3.5 Flash (High)
author_model_configuration: Antigravity dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Proposal Review - WI-5043 Service and SoT Watchdog Runner

bridge_kind: lo_verdict
Document: gtkb-wi5043-service-sot-watchdog-runner
Version: 002
Responds to: gtkb-wi5043-service-sot-watchdog-runner-001 (NEW, prime_proposal, Codex/A)
Reviewer: Loyal Opposition (Antigravity, harness C, dispatcher-spawned headless)
Date: 2026-07-06 UTC
Verdict: GO

## Verdict Summary

GO. The proposal is technically sound, root-contained, and properly authorized. All governance preflights pass with zero gaps. The detection-first posture correctly satisfies safety constraints against auto-restoring canonical stores in this slice.

## Positive Confirmations (verified; do not rework)

- **Authorization chain INTACT**: `PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION` is active in MemBase (rowid=530), maps to `PROJECT-GTKB-SERVICE-SOT-WATCHDOG`, and covers `WI-5043` with allowed mutation classes `["source", "tests", "config", "scheduled-task"]`.
- **Spec-linkage completeness**: Cited specifications cover all relevant requirements, including `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- **Preflights Pass**: Both the applicability preflight and the ADR/DCL clause preflight completed successfully with zero gaps or blocking issues.
- **Requirement Sufficiency**: The proposal correctly states that existing specifications/requirements are sufficient for this detection-only runner slice.

## Prime Builder Implementation Context

- **Scheduled Task Wrapper Reuse**: Recommend studying `groundtruth_kb/dispatcher_watchdog.py` and `scripts/ops/harness_storm_watchdog.ps1` to align scheduled task status checking and powershell/JSON wrapper patterns.
- **Dependency-Light Probing**: Ensure the runner's implementation in `service_sot.py` is entirely dependency-light. In particular, failures or latency in queried services (like a down database or missing daemon processes) must be handled gracefully with error catching, rather than crashing or hanging the watchdog.
- **State Directory Location**: Recommend writing watchdog status outputs to a dedicated JSON file (e.g. `.gtkb-state/watchdog/service-sot-status.json`) to keep status data cleanly separated from the active session locks.
- **Doctor Parity**: Since `doctor.py` is in `target_paths`, implement a corresponding watchdog registration and health check function (e.g. `_check_service_sot_watchdog`) within `doctor.py` to assert scheduled-task presence and runner output health.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized the full watchdog project.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected tiered auto-restore for safe/idempotent actions.

## Applicability Preflight

- packet_hash: `sha256:9349360dd8b230966c6e3aaeb5441ea4690024da70d30a72a3fbcd1158ec0fa1`
- bridge_document_name: `gtkb-wi5043-service-sot-watchdog-runner`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5043-service-sot-watchdog-runner-001.md`
- operative_file: `bridge/gtkb-wi5043-service-sot-watchdog-runner-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Methodology Trail

Files inspected:
- `bridge/gtkb-wi5043-service-sot-watchdog-runner-001.md`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py`
- `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`

Commands run:
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5043-service-sot-watchdog-runner`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5043-service-sot-watchdog-runner`
- Python queries to `groundtruth.db` validating `PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION`, `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, and `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`.

## Owner Decisions / Input

None required. The authorization package is fully populated and active.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
