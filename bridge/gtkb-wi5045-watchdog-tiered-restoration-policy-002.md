GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 2026-07-06T16-32-46Z-loyal-opposition-C-63d65f
author_model: Gemini 3.5 Flash (High)
author_model_version: Gemini 3.5 Flash (High)
author_model_configuration: Antigravity dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Proposal Review - WI-5045 Watchdog Tiered Restoration Policy

bridge_kind: lo_verdict
Document: gtkb-wi5045-watchdog-tiered-restoration-policy
Version: 002
Responds to: gtkb-wi5045-watchdog-tiered-restoration-policy-001 (NEW, prime_proposal, Codex/A)
Reviewer: Loyal Opposition (Antigravity, harness C, dispatcher-spawned headless)
Date: 2026-07-06 UTC
Verdict: GO

## Verdict Summary

GO. The proposal is technically sound, root-contained, and properly aligned with the platform design constraints and specifications. All preflights pass with zero gaps. The proposal sets up a robust tiered decision matrix.

## Positive Confirmations (verified; do not rework)

- **Authorization chain INTACT**: `PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION` is active in MemBase, maps to `PROJECT-GTKB-SERVICE-SOT-WATCHDOG`, and covers `WI-5045`.
- **Spec-linkage completeness**: Cited specifications correctly cover all relevant requirements, including `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- **Preflights Pass**: Both the applicability preflight and the ADR/DCL clause preflight completed successfully with zero gaps or blocking issues.
- **Requirement Sufficiency**: The proposal correctly states that existing specifications/requirements are sufficient for this tiered restoration policy slice.

## Prime Builder Implementation Context

- **Stateless Decision Model**: The policy engine should focus on translating probe outputs + registry metadata into explicit restoration actions (e.g. `AutoRestoreAction`, `EscalateAction`, `NoRestoreAction`). Keep the decision interface stateless and cleanly separated from the execution and resource-bounding layers (which are addressed in other WIs).
- **Escalation Triggering**: Ensure the policy engine produces clear, structured result objects specifying when retry limits are exhausted so that the bridge dispatching code or CLI can raise appropriate `ADVISORY` tickets.
- **Exclusion List**: The visibility-only check must properly consult the configured exclusions (e.g. `visibility-only` status/records in TOML or configuration) before deciding on an auto-restore path.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized the full watchdog project.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected tiered auto-restore for safe/idempotent actions.

## Applicability Preflight

- packet_hash: `sha256:d037e151c07e81076b31a3b34eace67669de4b53040b83cc82108a91adc14b42`
- bridge_document_name: `gtkb-wi5045-watchdog-tiered-restoration-policy`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md`
- operative_file: `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py", "groundtruth-kb/src/groundtruth_kb/watchdog/restore_policy.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Methodology Trail

Files inspected:
- `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md`
- `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`

Commands run:
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5045-watchdog-tiered-restoration-policy`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5045-watchdog-tiered-restoration-policy`

## Owner Decisions / Input

None required. The project authorization is active and fully covers the scope of work.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
