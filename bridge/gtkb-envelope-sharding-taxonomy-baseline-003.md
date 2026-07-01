NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1bfe-9f4b-7bc2-805e-c051192b5a73
author_model: gpt-5-codex
author_model_version: 2026-07-01
author_model_configuration: Codex Desktop interactive Prime Builder session; implementation report for WI-4946 taxonomy baseline

# GT-KB Bridge Implementation Report - gtkb-envelope-sharding-taxonomy-baseline - 003

bridge_kind: implementation_report
Document: gtkb-envelope-sharding-taxonomy-baseline
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-envelope-sharding-taxonomy-baseline-002.md
Approved proposal: bridge/gtkb-envelope-sharding-taxonomy-baseline-001.md
Recommended commit type: feat(config)

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4946
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4946
Implementation Authorization Packet: sha256:b372ba7722bc1edef627dab868262d8d090f20641e7c90c01bd9c3b2de9f8d79
Work-Intent Claim: gtkb-envelope-sharding-taxonomy-baseline / prime-builder / session 019f1bfe-9f4b-7bc2-805e-c051192b5a73

## Implementation Claim

Implemented the WI-4946 taxonomy baseline. The implementation adds a machine-readable sharding taxonomy with four required classes (`global_baseline`, `activity_only`, `explicit_query`, `never_startup`), makes each of the six activity disposition profiles classify `skills`, `terminology`, `history_state`, and `direction` against that taxonomy, validates those declarations in the profile loader, and updates startup control docs so startup points to the taxonomy boundary instead of broad implicit context loading.

Unrelated dirty worktree state existed before this slice and is not part of this implementation report.

## Specification Links

- `SPEC-INTAKE-46594e`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - owner directive to complete the project work items and retire the project after governed verification.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4946` - bounded implementation authorization for WI-4946 only.

No new owner decision is required by this implementation report.

## Prior Deliberations

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - current owner execution directive.
- `DELIB-202665110` - umbrella program and PAUTH creation authorization.
- `DELIB-20266631` - Loyal Opposition context for activity-envelope context sharding.
- `DELIB-20265892` - disposition-profile ratification.
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` - prior envelope refinement authorization.
- `DELIB-20265287` - single-active activity envelope, named disposition profile, and headless eligibility decisions.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - context-load profile anatomy and activity vocabulary.
- `bridge/gtkb-envelope-sharding-taxonomy-baseline-001.md` - approved implementation proposal.
- `bridge/gtkb-envelope-sharding-taxonomy-baseline-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-INTAKE-46594e` | `test_sharding_taxonomy_defines_required_classes`, `test_global_baseline_excludes_activity_and_archival_payloads`, and `test_profile_classifications_reference_sharding_taxonomy` verify the machine-readable split between global baseline, activity-only, explicit-query, and never-startup context. `gt spec show SPEC-INTAKE-46594e --json` returned the specified requirement. |
| `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` | Focused tests load the shipped activity profiles and validate the taxonomy-backed disposition contract. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Existing A1/A2/A3 tests plus new classification tests passed: all six activities exist; each defines and classifies skills, terminology, history state, and direction; headless eligibility remains D4-consistent. |
| `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` | Startup docs now point base startup to the taxonomy boundary, and profile classifications keep activity payloads behind activity-open or explicit-query semantics. |
| `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001` | `explicit_query` and `never_startup` classes require compact/on-demand query surfaces instead of automatic archival loading. |
| `ADR-CROSS-HARNESS-PARITY-001` | The taxonomy and profile declarations are shared config plus harness-neutral Python validation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation occurred only after latest `GO`, active Prime work-intent claim, and implementation authorization packet. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The owner directive and PAUTH are carried forward; implementation stayed inside the child work-item artifact boundary. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward every linked specification from the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps linked specifications to executed verification evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project Authorization, Project, and Work Item metadata are present in proposal, GO verdict, and this report. |
| `GOV-STANDING-BACKLOG-001` | No bulk backlog/project mutation was performed in this slice. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | No hook behavior was modified; taxonomy validation is deterministic Python/config. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The taxonomy is preserved as a durable config artifact, not transient session prose. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No new owner decision or requirement was introduced during implementation; existing governing artifacts were cited and preserved. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_activity_disposition_profiles.py -q`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py`
- `cmd.exe /d /c C:\Users\micha\.local\bin\gt.cmd spec show SPEC-INTAKE-46594e --json`

## Observed Results

- `pytest`: 17 tests collected; 17 passed in 0.70 seconds.
- `ruff check`: all checks passed.
- `ruff format --check`: two files already formatted.
- `gt spec show`: returned `SPEC-INTAKE-46594e` with status `specified`; description confirms the base session envelope should load only core GT-KB terminology and activity-specific terms/skills should load only for the related activity envelope.

## Files Changed

- `config/agent-control/activity-envelope-sharding.toml`
- `config/agent-control/activity-disposition-profiles.toml`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `platform_tests/scripts/test_activity_disposition_profiles.py`

## Recommended Commit Type

- Recommended commit type: `feat(config)`
- Justification: adds a new governed taxonomy config and validation/tests for the activity profile contract.

## Acceptance Criteria Status

- `WI-4946` is implemented only within the target paths listed in the approved proposal.
- `TEST-11251` has concrete PASS evidence: `platform_tests/scripts/test_activity_disposition_profiles.py` passed 17/17 and includes taxonomy/global-baseline/activity-only/explicit-query validation.
- Routine focused-agent workflow for this slice avoids loading unrelated activity content into the global session envelope by classifying `skills`, `terminology`, and `direction` as `activity_only`, `history_state` as `explicit_query`, and archival/raw surfaces as `never_startup`.
- No out-of-scope blocker was hidden in this slice. Existing unrelated dirty worktree state remains excluded.

## Risk And Rollback

Residual risk is limited to consumers that assumed the old `ActivityProfile` dataclass had no `classification` field or that profile TOML did not need classification metadata. The fail-closed validation is intentional for this slice and covered by focused tests.

Rollback for this slice is to remove `config/agent-control/activity-envelope-sharding.toml`, remove the `classification` tables from `activity-disposition-profiles.toml`, restore the prior `profiles.py` loader shape, and revert the focused tests/doc pointers. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the machine-readable taxonomy satisfies `SPEC-INTAKE-46594e`.
2. Verify that each activity profile classifies skills, terminology, history state, and direction against the taxonomy.
3. Return `VERIFIED` if the implementation and evidence satisfy the approved proposal; otherwise return `NO-GO` with findings.
