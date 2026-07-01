REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1bfe-9f4b-7bc2-805e-c051192b5a73
author_model: gpt-5-codex
author_model_version: 2026-07-01
author_model_configuration: Codex Desktop interactive Prime Builder session; revision for WI-4946 taxonomy baseline NO-GO

# Bridge Revision - gtkb-envelope-sharding-taxonomy-baseline - 005

bridge_kind: implementation_report
Document: gtkb-envelope-sharding-taxonomy-baseline
Version: 005 (REVISED; post-implementation report correction)
Responds to NO-GO: bridge/gtkb-envelope-sharding-taxonomy-baseline-004.md
Responds to GO: bridge/gtkb-envelope-sharding-taxonomy-baseline-002.md
Approved proposal: bridge/gtkb-envelope-sharding-taxonomy-baseline-001.md
Recommended commit type: feat(config)

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4946
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4946

## Revision Claim

This revision addresses the single blocking NO-GO finding in `bridge/gtkb-envelope-sharding-taxonomy-baseline-004.md`: the WI-4946 implementation was verified but not committed. The six approved target-path changes are now committed in focused commit `b83abaab7` with message `feat(config): add session/activity envelope sharding taxonomy and profile classifications (WI-4946)`.

No implementation scope changed relative to `bridge/gtkb-envelope-sharding-taxonomy-baseline-003.md`. The commit contains only:

- `config/agent-control/activity-envelope-sharding.toml`
- `config/agent-control/activity-disposition-profiles.toml`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `platform_tests/scripts/test_activity_disposition_profiles.py`

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

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - owner directive to complete this project and retire it after governed verification.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4946` - bounded implementation authorization for WI-4946.

No new owner decision is required by this revision.

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
- `bridge/gtkb-envelope-sharding-taxonomy-baseline-003.md` - original implementation report.
- `bridge/gtkb-envelope-sharding-taxonomy-baseline-004.md` - Loyal Opposition NO-GO verdict requiring commit evidence.

## Findings Addressed

### Blocking finding: no commit exists for WI-4946

Response: resolved. The six target paths are now committed in focused commit `b83abaab7`.

Evidence:

- `git commit` created commit `b83abaab7` on branch `research`.
- The staged set before commit contained exactly the six target paths from the approved proposal.
- Pre-commit checks reported: secret scan clean, inventory drift clean, narrative-artifact evidence pass, Ruff format pass, and protected-commit authorization cleared.
- `git archive b83abaab7` was extracted to `.gtkb-state/clean-checkouts/wi4946-b83abaab7` and tested as a clean committed snapshot.

## Scope Changes

None. This revision adds commit and clean-checkout verification evidence only.

## Pre-Filing Preflight Subsection

This revision is being filed through `.codex/skills/bridge/helpers/revise_bridge.py file`, which runs:

- `scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-sharding-taxonomy-baseline --content-file <candidate>`
- `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-sharding-taxonomy-baseline --content-file <candidate>`

The helper must pass both gates before publishing this file to `bridge/`.

## Verification Plan

| Requirement / governing surface | Verification evidence |
| --- | --- |
| `SPEC-INTAKE-46594e` | Commit `b83abaab7` includes the machine-readable taxonomy and profile classifications. Clean committed-snapshot test run passed `platform_tests/scripts/test_activity_disposition_profiles.py` 17/17. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | The committed test suite validates all six activity profiles, required payload classes, classification metadata, and D4 headless eligibility. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This revision cites the clean committed-snapshot test evidence requested by LO. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The implementation is now durable and traceable through commit `b83abaab7`. |

Executed commands after the NO-GO:

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_activity_disposition_profiles.py -q` -> 17 passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py` -> all checks passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py` -> two files already formatted.
- `git archive b83abaab7 | tar -x -C .gtkb-state\clean-checkouts\wi4946-b83abaab7`
- From `.gtkb-state\clean-checkouts\wi4946-b83abaab7`, with `PYTHONPATH` pointed at the clean snapshot: `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_activity_disposition_profiles.py -q` -> 17 passed.

## Risk And Rollback

Residual risk is unchanged from `bridge/gtkb-envelope-sharding-taxonomy-baseline-003.md`. Rollback is `git revert b83abaab7` plus a follow-up bridge report if LO requires rollback evidence. Bridge audit files remain append-only.

## Loyal Opposition Asks

Please verify that commit `b83abaab7` resolves the NO-GO traceability blocker and return `VERIFIED` if the implementation now satisfies the approved proposal.
