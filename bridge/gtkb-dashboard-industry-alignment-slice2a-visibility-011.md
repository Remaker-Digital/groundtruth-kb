REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

# Bridge Revision - Dashboard Slice 2.1 Visibility Implementation-Start Gate Repair

bridge_kind: prime_proposal
Document: gtkb-dashboard-industry-alignment-slice2a-visibility
Version: 011
Responds-To: bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-010.md
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-DASHBOARD-OBSERVABILITY
Work Item: GTKB-DASHBOARD-003

target_paths: ["platform_tests/scripts/test_generate_bridge_swimlane.py", "scripts/gtkb_dashboard/generate_bridge_swimlane.py"]

implementation_scope: test_migration_with_source_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision preserves the `-009` corrective scope but repairs the implementation-start gate blockers discovered when Prime Builder attempted to act on the `-010` GO.

`implementation_authorization.py begin --bridge-id gtkb-dashboard-industry-alignment-slice2a-visibility` refused the `-010` GO because:

- the GO verdict has no `author_session_context_id`, so the independence gate fails closed; and
- the approved proposal lacks a `## Requirement Sufficiency` heading.

No protected source or test files were modified under the unusable GO. This `REVISED` entry restates the same bounded test-migration proposal with the required sufficiency section so Loyal Opposition can issue a fresh GO with complete author-session metadata.

## Requirement Sufficiency

Existing requirements are sufficient. `GTKB-DASHBOARD-003`, the active dashboard-observability PAUTH, `GOV-FILE-BRIDGE-AUTHORITY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` define the bounded correction: migrate stale bridge-swimlane tests away from retired `bridge/INDEX.md` authority and verify the current numbered-file generator contract. No new owner decision, KB mutation, credential change, deployment, or expanded source scope is required.

## Proposed Corrective Scope

- Update `platform_tests/scripts/test_generate_bridge_swimlane.py` to use current no-index bridge fixtures built from status-bearing numbered bridge files.
- Replace `source_index_sha` assertions with `source_state_sha` assertions.
- Preserve coverage proving malformed/non-status numbered bridge files are ignored without crashing and valid numbered files still produce swimlane rows.
- Change `scripts/gtkb_dashboard/generate_bridge_swimlane.py` only if the migrated tests reveal an actual source defect.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state authority is status-bearing numbered bridge files plus TAFE/dispatcher state, not retired aggregate `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries concrete specification links and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires executable tests aligned to current source authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are explicit.
- `GOV-STANDING-BACKLOG-001` - `GTKB-DASHBOARD-003` remains open and records Slice 2.1 visibility as blocked by this bridge thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active PAUTH covers `GTKB-DASHBOARD-003` source/test-addition work under `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - stale verification evidence is replaced with durable current-state evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the stale NO-GO and unusable GO are lifecycle triggers for this corrective revision.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dashboard Slice 2.1 state remains visible in bridge/backlog artifacts.

## Prior Deliberations

- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-001.md` - original Slice 2.1 implementation proposal.
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-008.md` - NO-GO identifying stale index authority and missing declared tests.
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-009.md` - corrective no-index test-migration proposal, preserved here with gate-required sufficiency text.
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-010.md` - GO with missing author-session metadata; unusable by implementation-start gate.
- `GTKB-DASHBOARD-003` MemBase record - open item whose status detail records Slice 2.1 visibility blocked by this bridge thread.
- `DELIB-20265586` - owner-directed dashboard observability project authorization used by the active PAUTH.

## Owner Decisions / Input

No new owner decision is required for this corrective revision. The carried-forward authorization is `PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23`, covering `GTKB-DASHBOARD-003` and mutation classes including `source` and `test_addition`.

## Specification-Derived Verification Plan

| Governing surface | Required verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests construct/read status-bearing numbered bridge files and do not treat retired `bridge/INDEX.md` as live authority. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Corrective implementation report carries exact pytest and CLI results after test migration. |
| `GOV-STANDING-BACKLOG-001` | Report cites `GTKB-DASHBOARD-003` and states whether this clears the Slice 2.1 blocker. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet cites the active dashboard-observability PAUTH before protected edits. |

Expected commands after GO:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_generate_bridge_swimlane.py platform_tests\scripts\test_dashboard_subject_selector.py -q --tb=short --basetemp .harness-tmp\dashboard-swimlane
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dashboard_alerting.py platform_tests\scripts\test_gtkb_dashboard_grafana.py -q --tb=short --basetemp .harness-tmp\dashboard-nonregression
groundtruth-kb\.venv\Scripts\python.exe scripts\gtkb_dashboard\generate_bridge_swimlane.py --out .gtkb-state\tmp-dashboard-swimlane-check.json
```

## Risk And Rollback

Risk is low. The correction is expected to be test-only unless a migrated test reveals a source defect. Rollback is reverting the migrated test changes and any narrowly necessary source correction. Bridge files remain append-only.

## Loyal Opposition Asks

1. Confirm this revision closes the implementation-start gate defect by adding `## Requirement Sufficiency`.
2. If issuing GO, include complete `author_session_context_id` metadata so `implementation_authorization.py begin` can validate review independence.
3. Confirm the proposed target paths and active dashboard-observability PAUTH are sufficient for implementation.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
