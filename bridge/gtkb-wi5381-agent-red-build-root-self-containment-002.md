GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5381 Agent Red Build Root Self-Containment

bridge_kind: loyal_opposition_review
Document: gtkb-wi5381-agent-red-build-root-self-containment
Version: 002
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5381
Reviewed: bridge/gtkb-wi5381-agent-red-build-root-self-containment-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5381-agent-red-build-root-self-containment` → `preflight_passed: true` (warning: missing parent directories is expected for the migration paths to be created)
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5381-agent-red-build-root-self-containment` → 0 blocking gaps

The proposal completes the Agent Red application lifecycle migration by relocating Docker, workflow, dependency, and test-host surfaces from the platform root into `applications/Agent_Red/`. It restores the test-host package required by `SPEC-1825` and corrects the frozen portability suite guard to accept the relocated host while still rejecting original-source reads. The proposal is correctly hard-sequenced after WI-5392 finalization because both touch the same portability test file.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `DCL-APP-ROOT-MINIMIZATION-001`
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`
- `SPEC-1825`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Conditions

- No WI-5381 mutation may begin until WI-5392 is independently VERIFIED and mechanically finalized.
- All relocated files must remain within `applications/Agent_Red/`; no platform root files may be treated as application-owned after migration except the retained registry/release-gate evidence.
- The five-file test-host service must be restored byte-for-byte from the last tracked version, then modified only to pass current application-local tests and security checks.
- The frozen portability suite guard must deny original-source reads while explicitly allowing the relocated host.
- Independent VERIFIED must precede any mechanical finalization.
