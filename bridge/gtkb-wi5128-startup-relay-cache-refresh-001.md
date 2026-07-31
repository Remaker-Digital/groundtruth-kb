NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f3d48-b886-7be2-a656-99678002edf1
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Restore bounded Codex startup-relay cache refresh

bridge_kind: prime_proposal
Document: gtkb-wi5128-startup-relay-cache-refresh
Version: 001
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-STARTUP-RELAY-REPAIR
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5128

target_paths: ["scripts/workstream_focus.py", "scripts/session_start_dispatch_core.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair bounded Codex startup-relay cache refresh without weakening the init-keyword relay guard.

Work item description: Repair the interactive startup relay so a stale but integrity-valid role-scoped cache is refreshed within the hook budget or yields a focused, diagnosable result. Preserve cache integrity and freshness validation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5128` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/workstream_focus.py`, `scripts/session_start_dispatch_core.py`, `platform_tests/hooks/test_workstream_focus.py`, `platform_tests/hooks/test_session_start_dispatch_role_cache.py`.

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - auto-linked governing or work-item specification.
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

## Prior Deliberations

- `DELIB-20266120` - Owner decision: resolve WI-3502 and WI-3503 as substantially-addressed (SoT-freshness final closure)
- `DELIB-20264942` - Loyal Opposition Verification - Startup Relay Truncation Fix Refile
- `DELIB-20260961` - Loyal Opposition Verification - WI-3326 Executable Packet Repair Corrected Report
- `DELIB-20261160` - Loyal Opposition Verification - WI-3326 Executable Packet Repair Corrected Report
- `DELIB-20264941` - Loyal Opposition Verification - Startup Relay Truncation Fix Refile

## Owner Decisions / Input

- `DELIB-202665935` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-STARTUP-RELAY-REPAIR` - active project authorization covering `WI-5128`.

## Proposed Scope

- Repair the bounded refresh path for a stale but integrity-valid role-scoped startup relay cache.
- Preserve hash, byte-length, harness, role, disclosure-shape, and freshness validation; do not permit stale cache acceptance.
- Add focused regression coverage for the Codex interactive Prime Builder init path.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Verify the canonical interactive init keyword retains its role-scoped startup disclosure after a stale-cache recovery. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- An interactive Codex Prime Builder init can recover a stale integrity-valid relay cache inside the bounded refresh contract.
- Invalid integrity, role, or disclosure-shape cache data remains fail-closed.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/workstream_focus.py`
- `scripts/session_start_dispatch_core.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/hooks/test_session_start_dispatch_role_cache.py`

## Recommended Commit Type

`feat`
