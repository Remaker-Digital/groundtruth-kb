REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; interactive build envelope; approval_policy=never

# Bridge Revision - Dashboard Slice 2.1 Visibility no-index verification correction

bridge_kind: prime_proposal
Document: gtkb-dashboard-industry-alignment-slice2a-visibility
Version: 009
Responds-To: bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-008.md
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-DASHBOARD-OBSERVABILITY
Work Item: GTKB-DASHBOARD-003

target_paths: ["platform_tests/scripts/test_generate_bridge_swimlane.py", "scripts/gtkb_dashboard/generate_bridge_swimlane.py"]

implementation_scope: test_migration_with_source_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision addresses the live `-008` NO-GO by separating already-correct source reality from stale verification tests.

Current source reality: `scripts/gtkb_dashboard/generate_bridge_swimlane.py` no longer reads `bridge/INDEX.md`; it reads status-bearing numbered bridge files through `groundtruth_kb.bridge.versioned_files.scan_expected_documents` and `status_from_bridge_file`, and writes `source_state_sha` over versioned-file state rows.

Current verification gap: `platform_tests/scripts/test_generate_bridge_swimlane.py` still asserts the retired `bridge/INDEX.md` contract and `source_index_sha`. Focused rerun on 2026-07-05 produced 9 failures in that test module, while `platform_tests/scripts/test_dashboard_subject_selector.py` passed 11/11 and the dashboard alerting/Grafana non-regression lane passed 37/37. The corrective implementation should therefore migrate the generator tests to the current no-index contract, with source changes only if the migrated tests reveal a source defect.

## Finding Response

### P1 - Report depends on removed bridge index authority

Status: partially satisfied by current source, verification correction still needed.

Evidence: `scripts/gtkb_dashboard/generate_bridge_swimlane.py` imports `scan_expected_documents` and `status_from_bridge_file` from `groundtruth_kb.bridge.versioned_files`; no live source dependency on `bridge/INDEX.md` remains in that generator. The old implementation report is stale and should be superseded by a fresh corrective implementation report after tests are migrated.

Required corrective scope: update `platform_tests/scripts/test_generate_bridge_swimlane.py` so fixtures create status-bearing numbered bridge files and assert `source_state_sha` instead of `source_index_sha`. Keep `bridge/INDEX.md` coverage only where tests explicitly validate retired-aggregate compatibility or ignore behavior.

### P1 - Declared verification tests are not present

Status: path corrected, content not yet corrected.

Evidence: the former `tests/scripts/...` paths are absent, but the tests exist at current canonical paths under `platform_tests/scripts/`. `platform_tests/scripts/test_dashboard_subject_selector.py` passes. `platform_tests/scripts/test_generate_bridge_swimlane.py` exists but is stale against the retired index-era contract and currently fails 9 tests.

Required corrective scope: migrate the current `platform_tests/scripts/test_generate_bridge_swimlane.py` module to no-index fixtures and rerun the affected dashboard lane. Do not claim VERIFIED until the migrated generator tests and dashboard non-regression tests pass.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state is status-bearing numbered bridge files plus TAFE/dispatcher state, not retired aggregate `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries concrete specification links and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires executable tests aligned to current source authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision includes project authorization, project, work item, and target path metadata.
- `GOV-STANDING-BACKLOG-001` - `GTKB-DASHBOARD-003` remains open and explicitly records Slice 2.1 visibility blocked by this bridge thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active PAUTH covers `GTKB-DASHBOARD-003` source/test_addition work under `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - stale verification evidence must be replaced with durable current-state evidence rather than hand-waved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the stale NO-GO is a lifecycle trigger for corrective test migration.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dashboard Slice 2.1 state remains visible in the bridge and backlog.

## Prior Deliberations

- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-001.md` - original Slice 2.1 implementation proposal.
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-008.md` - live NO-GO identifying stale index authority and missing declared tests.
- `GTKB-DASHBOARD-003` MemBase record - open Slice 3 item whose status_detail states Slice 2.1 visibility is blocked by this latest NO-GO.
- `DELIB-20265586` - owner-directed dashboard observability project authorization used by the active PAUTH.

## Owner Decisions / Input

No new owner decision is required for this corrective revision.

Carried-forward authorization:

- `PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23` - active, covers `GTKB-DASHBOARD-003`, mutation classes `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.

## Proposed Corrective Scope

- Update `platform_tests/scripts/test_generate_bridge_swimlane.py` to use current no-index bridge fixtures built from numbered status-bearing bridge files.
- Replace assertions for `source_index_sha` with assertions for `source_state_sha`.
- Preserve or add coverage that proves malformed/non-status numbered bridge files are ignored without crashing and valid numbered files still produce swimlane rows.
- Rerun:
  - `python -m pytest platform_tests\scripts\test_generate_bridge_swimlane.py platform_tests\scripts\test_dashboard_subject_selector.py -q --tb=short`
  - `python -m pytest platform_tests\scripts\test_gtkb_dashboard_alerting.py platform_tests\scripts\test_gtkb_dashboard_grafana.py -q --tb=short`
  - `python scripts\gtkb_dashboard\generate_bridge_swimlane.py --out .gtkb-state\tmp-dashboard-swimlane-check.json`

Source changes to `scripts/gtkb_dashboard/generate_bridge_swimlane.py` are allowed only if the migrated tests reveal an actual source defect; otherwise the implementation report should state that no source edit was needed.

## Current Verification Evidence

Commands run before this revision:

```text
python -m pytest platform_tests\scripts\test_generate_bridge_swimlane.py platform_tests\scripts\test_dashboard_subject_selector.py -q --tb=short
```

Observed result: 21 collected; `test_dashboard_subject_selector.py` passed 11/11; `test_generate_bridge_swimlane.py` failed 9 tests because tests still expect `bridge/INDEX.md` fixtures and `source_index_sha`.

```text
python -m pytest platform_tests\scripts\test_gtkb_dashboard_alerting.py platform_tests\scripts\test_gtkb_dashboard_grafana.py -q --tb=short
```

Observed result: 37 passed in 8.04s.

```text
python scripts\gtkb_dashboard\generate_bridge_swimlane.py --out .gtkb-state\tmp-dashboard-swimlane-check.json
```

Observed result: command exited 0 and reported `thread_count: 1573`.

## Pre-Filing Preflight Subsection

This revision is filed through `.codex/skills/bridge/helpers/revise_bridge.py file`, which performs credential scanning, candidate-content applicability preflight, candidate-content ADR/DCL clause preflight, latest-status validation, and governed bridge writer publication.

Manual candidate preflights were run before live filing; the live helper also reruns them.

- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`. The governed filing helper reruns this check and emits the live packet hash for the filed content.
- ADR/DCL clause preflight: mandatory mode; clauses evaluated 5; must_apply 3; blocking gaps 0; exit 0.

## Specification-Derived Verification Plan

| Governing surface | Required verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests must construct/read status-bearing numbered bridge files and avoid treating retired `bridge/INDEX.md` as live authority. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Corrective implementation report must carry exact pytest and CLI results after test migration. |
| `GOV-STANDING-BACKLOG-001` | Report must cite `GTKB-DASHBOARD-003` still open and explain whether this clears the Slice 2.1 blocker. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet must cite the active dashboard observability PAUTH before protected test/source edits. |

## Scope Changes

This revision does not claim the old `-007` implementation report is verified. It narrows the remaining work to current-path test migration, with source guarded as optional if migrated tests reveal a defect.

## Risk And Rollback

Risk is low. The proposed correction is test-only unless a source defect is discovered. Rollback is reverting the migrated test changes and any narrowly necessary generator source correction. Bridge files remain append-only.

## Files Expected To Change

- `platform_tests/scripts/test_generate_bridge_swimlane.py`
- `scripts/gtkb_dashboard/generate_bridge_swimlane.py` only if migrated tests reveal a source defect

## Recommended Commit Type

`test:` if the source remains unchanged; `fix:` if a generator source defect is corrected.

## Loyal Opposition Asks

1. Confirm this revision correctly identifies the current source as no-index and the tests as stale.
2. Confirm the proposed target paths and active dashboard-observability PAUTH are sufficient for a corrective implementation proposal.
3. Return `GO` if Prime Builder may migrate the tests and file a fresh implementation report; otherwise return `NO-GO` with the missing scope or authorization detail.
