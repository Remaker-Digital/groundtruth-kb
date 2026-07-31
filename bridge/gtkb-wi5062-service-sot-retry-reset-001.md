NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5 Codex
author_model_version: 2026-07-07 runtime
author_model_configuration: Codex desktop; Prime Builder role; interactive shell=powershell; approval_policy=never

# Implementation Proposal - Dispatcher supervisor self-healing and guarded disable controls

bridge_kind: prime_proposal
Document: gtkb-wi5062-service-sot-retry-reset
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

target_paths: ["groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py", "platform_tests/scripts/test_gtkb_service_sot_watchdog.py", ".gtkb-state/watchdog/restore-retries.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix WI-5062 service/SoT restore retry accounting so healthy probes clear stale retry debt instead of leaving recovered dispatcher supervisor artifacts retry-exhausted.

Work item description: Close the operational gap where GTKB-DispatcherDaemon can be disabled or missing while dispatcher state remains fresh. Register the dispatcher supervisor scheduled task as its own SoT/restorable service artifact; execute safe ensure_alive restores for disabled or missing scheduled-task services with audit records and retry caps; require TTL-bound or explicit owner-quiesce records for dispatcher supervisor/complex disable operations.

Scope amendment from DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE: WI-5062 acceptance also includes post-workstation-reboot recovery. If the workstation restarts and GTKB-DispatcherDaemon is disabled or missing with no active disable guard/quiesce record, the dispatcher supervisor/SoT watchdog mechanism must automatically restore or fail loud with audited blocked-restore evidence. Verification must include a reboot-equivalent scheduled-task registration/startup trigger check and a live or simulated post-reboot recovery check showing the dispatcher daemon complex returns to healthy without manual intervention.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5062` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`, `platform_tests/scripts/test_gtkb_service_sot_watchdog.py`, `.gtkb-state/watchdog/restore-retries.json`.

## Specification Links

- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - auto-linked governing or work-item specification.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE` - Add post-reboot dispatcher supervisor recovery to WI-5062 scope
- `DELIB-20266642` - Verdict
- `DELIB-20266353` - GO - gtkb-wi4896-startup-console-residual - Boot-time and Minute-cadence Windows console/focus-steal fix
- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` - Create WI-5062 for dispatcher supervisor self-healing and guarded disable
- `DELIB-20266268` - Owner decision: clear daemon residue WIs (WI-4859, WI-4861) before PHASE-Y

## Owner Decisions / Input

- `PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062` - active project authorization covering `WI-5062`.

## Proposed Scope

- Clear stale restore retry attempts when a fresh healthy probe reports PASS for an artifact.
- Preserve retry exhaustion for repeated failing restore attempts; do not widen auto-restore policy.
- Allow the next service/SoT watchdog run to remove the existing dispatcher-supervisor-task retry debt via the fixed healthy-probe path.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py and ruff format --check for the same files |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short |
| `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` | gt watchdog service-sot run --no-write --json and gt bridge dispatch complex status --json |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A seeded dispatcher-supervisor-task retry count is removed after a PASS probe.
- A failing probe with exhausted retries still escalates instead of auto-restoring.
- Current dispatcher complex health remains PASS after the retry ledger is cleaned.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`
- `platform_tests/scripts/test_gtkb_service_sot_watchdog.py`
- `.gtkb-state/watchdog/restore-retries.json`

## Recommended Commit Type

`feat`
