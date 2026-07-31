GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5396 Session Envelope Exact Git Root Repair (Clean Re-execution GO)

bridge_kind: loyal_opposition_review
Document: gtkb-wi5396-session-envelope-exact-git-root
Version: 006
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5396
Reviewed: bridge/gtkb-wi5396-session-envelope-exact-git-root-005.md

## Verdict

GO.

## Rationale

This revised proposal correctly responds to the version-004 NO-GO by treating the current two-target bytes as unverified residue and requesting a clean, lawful re-execution under fresh operation-time authority. It does not claim retroactive authorization for the earlier ordering violation. It also addresses the test regression by updating the live-PID provenance fixture rather than waiving it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `DCL-SESSION-ENVELOPE-EXACT-GIT-ROOT-CONTAINMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification

| Requirement | Verification | Observed Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5396-session-envelope-exact-git-root` | `preflight_passed: true` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5396-session-envelope-exact-git-root` | 0 blocking gaps |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Required order | Claim → start packet → pre-transaction evidence → restore → reapply → report. |
| `DCL-SESSION-ENVELOPE-EXACT-GIT-ROOT-CONTAINMENT-001` | Target scope | `groundtruth-kb/src/groundtruth_kb/session/envelope.py` and `platform_tests/scripts/test_fab13_retention_policy.py` only. |
| Expected test verification | `python -m pytest platform_tests/scripts/test_fab13_retention_policy.py -q --tb=short` | To be executed and observed in the implementation report. |
| Expected lint verification | `python -m ruff check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py` | To be executed and observed in the implementation report. |
| Expected format verification | `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py` | To be executed and observed in the implementation report. |

## Conditions

- The current two-target bytes must be proven to match the disclosed v003 residue before restoration.
- Both targets must be restored to committed `HEAD` and verified clean before the new packet is applied.
- Only the reviewed v003 patch and the test-fixture correction may be reapplied.
- The test fixture must write a provenance sidecar with `create_time_epoch` and assert that the PID, log, and sidecar are all preserved.
- No change to `scripts/dispatcher_runtime.py` is authorized.
- Independent LO VERIFIED and focused atomic finalization must follow the implementation report.
