GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5396 Session Envelope Exact Git Root

bridge_kind: loyal_opposition_review
Document: gtkb-wi5396-session-envelope-exact-git-root
Version: 002
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5396
Reviewed: bridge/gtkb-wi5396-session-envelope-exact-git-root-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5396-session-envelope-exact-git-root` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5396-session-envelope-exact-git-root` → 0 blocking gaps

The proposal addresses the frozen harness-parity timeout caused by an unbounded `git status` walking up to the GT-KB ancestor when a pytest temporary root is nested inside it. The fix is bounded: require exact top-level identity before collecting status, bound every Git probe, and fail-soft with explicit attestation when the supplied root is not an independent repository. No harness is terminated, suspended, or deprioritized.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-ENVELOPE-META-MODEL-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
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

- Target paths are limited to `groundtruth-kb/src/groundtruth_kb/session/envelope.py` and `platform_tests/scripts/test_fab13_retention_policy.py`.
- Exact-root, nested-root, timeout, output-bound, and frozen acceptance cases must be exercised in the implementation report.
- Independent VERIFIED must precede any mechanical finalization.
