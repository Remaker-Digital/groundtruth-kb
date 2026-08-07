REVISED
::init gtkb pb
::open build

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T16-07-52Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: Goose Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ::open build
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi5723-session-resolver-fallback-removal
Version: 009
Responds to: bridge/gtkb-wi5723-session-resolver-fallback-removal-008.md (NO-GO)
Date: 2026-08-05 UTC
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5723
target_paths: ["scripts/session_self_initialization.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_modernization_end_to_end_workflow.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

KB Mutation: This proposal performs no MemBase write, no `groundtruth.db` mutation, and no other knowledge-base mutation. The implementation must not edit `groundtruth.db`.

# Revised Implementation Proposal - Session Resolver Fallback Removal (current-state, findings-resolved)

## First-Line Role Eligibility Check

PASS. This is a Prime Builder session (declared ::init gtkb pb). This session acquired the required draft work-intent claim (row 36297) for gtkb-wi5723-session-resolver-fallback-removal before this filing. Prime Builder may author REVISED bridge files; it is strictly prohibited from authoring Loyal Opposition status tokens.

This filing grants no implementation authority. Protected implementation still requires a fresh independent GO, a matching go_implementation work-intent claim, and a successful implementation-start packet against the live target set.

## Revision Disposition

The -008 NO-GO (2026-08-01) recorded four findings (F1-F4) plus resolved findings (C1, C2). This revision re-reads current state (2026-08-05) and resolves each open finding with fresh evidence. The approved v001 six-target scope is unchanged.

## Current-State Facts (re-read 2026-08-05)

- All six target paths are clean at HEAD (git status --short over the six paths: no output).
- Live SHA-256 (source targets):
  - groundtruth-kb/src/groundtruth_kb/session/envelope.py = 16D56A856CBCF606BBA14647A352D75D6BF92D7A60AAB43DA412A49B5ADC13B0
  - scripts/session_self_initialization.py = 0347E8C11C57DA86CB1154E130AC3D9BE98B1600AACF581DD600B3B55D19BA30
  - groundtruth-kb/src/groundtruth_kb/modernization/workflow.py = 7CE2C3C107CD986DC764EEE3464564EAAA5608CE61E608C5A58354C77199D2DE
- Active role boundary: DCL-SESSION-ROLE-RESOLUTION-001 v7 (verified) plus owner decisions DELIB-202667524 and DELIB-202667530.

## Finding Responses

### F1 (P0) - open WI-5653 dependency has no active project-authority lane

Response: Resolved. WI-5653 now has an active project-authority lane: active membership PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI-5653 v1 (row 4310) places it under PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES with list-free PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-20260715-PROJECT-SCOPE v2. The documented required order is WI-5580 terminal/clean -> WI-5653 -> WI-5723. WI-5653 scope is limited to exact-session envelope CLI rebind/reissue for a caller-supplied existing session id; session-resolver fallback removal remains WI-5723. This revision preserves the WI-5653 dependency and confirms it is sequenceable under a current authorization.

### F2 (P0) - three strict current GO lifecycles overlap the six-path cohort

Response: Resolved by current state. Strict lifecycle resolution on 2026-08-05:
- gtkb-wi5234-codex-session-model-author-metadata - latest NO-GO v004 (no implementation authority).
- gtkb-wi5586-scaffold-startup-canonical-routes - latest NO-GO v004 (no implementation authority).
- gtkb-wi5603-ipa-advisory-envelope-semantics - latest NO-GO v006 (no implementation authority).
- gtkb-wi5234-by-reference-finalization-recovery-v2 - latest GO v002, but target_paths is only bridge/gtkb-wi5234-by-reference-finalization-recovery-v2-003.md (a bridge file), which does NOT overlap the WI-5723 six-path source/test cohort.

Collision ledger: no current GO thread holds any of the six WI-5723 target paths. The three formerly-overlapping GOs are all now NO-GO, and the one remaining GO (WI-5234 recovery-v2) targets only a bridge file. No hunk ownership conflict exists at the current state.

### C2 - confirmed quarantine of WI-5546 / WI-5563

Response: Carried forward. Both remain quarantined (not lifecycle authority). No change.

### F3 (P0) - session/envelope.py is foreign-dirty and must not be adopted

Response: Resolved by current state. groundtruth-kb/src/groundtruth_kb/session/envelope.py is now clean at HEAD (SHA-256 16D56A85..., git status no output). WI-5580 is now DEFERRED v011 (owner deferral DELIB-20260803084759 to WI-5742 Layer C; its envelope.py bytes are the committed clean postimage). The foreign-dirty condition that v008 flagged no longer exists. This revision re-baselines envelope.py to its current clean state and preserves it unchanged; WI-5580's cohort is resolved through its own governed lane (deferred), not absorbed by WI-5723.

### F4 (P1) - retire retired GOV-SESSION-ROLE-AUTHORITY-001 citations

Response: Accepted. GOV-SESSION-ROLE-AUTHORITY-001 is verified retired and is omitted from this revision's active Specification Links. Behavior and tests map to active DCL-SESSION-ROLE-RESOLUTION-001 v7 assertions ROLE-DCL-A1 through ROLE-DCL-A10 together with owner decisions DELIB-202667524 and DELIB-202667530.

## Proposed Implementation (unchanged v001 scope)

Remove the session_resolver_fallback role source from the producer and fail closed on unresolvable role, per the owner directives:

1. Remove the session_resolver_fallback literal from the producer so no code path yields role_resolution_source=session_resolver_fallback.
2. An unresolved role writes no envelope rather than a fabricated one.
3. A SessionStart after ::init does not revert the transcript role.
4. All three interactive sources are protected from non-interactive overwrite.
5. Owner re-declaration and dispatcher composition still change the role.
6. Any residual envelope carrying the removed value fails closed.
7. Dispatched workers are unaffected.

## Acceptance Criteria

1. The session_resolver_fallback literal is removed from the producer.
2. An unresolved role writes no envelope rather than a fabricated one.
3. A SessionStart after ::init does not revert the transcript role, proven by a new regression test.
4. All three interactive sources are protected from non-interactive overwrite.
5. Owner re-declaration and dispatcher composition still change the role.
6. Any residual envelope carrying the removed value fails closed.
7. Dispatched workers are unaffected.
8. Existing session-envelope and modernization suites pass.
9. Only the six declared target paths are modified.

## Requirement Sufficiency

Existing requirements are sufficient. The owner directives (D1/D2 from the
2026-07-28 interactive transcript), active `DCL-SESSION-ROLE-RESOLUTION-001`
v7 assertions, and owner decisions `DELIB-202667524` / `DELIB-202667530`
fully bound the six-target session-resolver fallback removal. No new or
revised requirement is required before implementation. Existing requirements
sufficient.

## Specification Links

- DCL-SESSION-ROLE-RESOLUTION-001 (v7, active)
- DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001
- ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
- ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

Note: GOV-SESSION-ROLE-AUTHORITY-001 is retired and intentionally omitted per F4.

## Prior Deliberations

- DELIB-202667524 (CF-01/CF-02) - unresolved identity fails closed.
- DELIB-202667530 - explicit init direction is canonical.
- DELIB-202667721 - list-free Housekeeping Hardening project authority.
- DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT - legacy per-WI approval metadata is noncontrolling.
- DELIB-20260803084759 - WI-5580 owner deferral (envelope.py clean state).
- WI-5653 active Runtime Interfaces membership (row 4310) and PAUTH v2.

## Owner Decisions / Input

No new owner decision is required for this revision. The active Housekeeping Hardening PAUTH covers the six targets; the WI-5653 dependency now has a current authorization lane; envelope.py is clean; the GO overlaps are non-current; and the retired citation is omitted.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5723 revision 009; resolves v008 F1-F4 with current-state evidence over the unchanged six-target scope",
  "canonical_authority": "DCL-SESSION-ROLE-RESOLUTION-001 v7, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
  "primary_route": "session-envelope producer + applier removal of the session_resolver_fallback role source, with fail-closed role resolution",
  "before_behavior": "A worker-facing registry/dispatcher fallback can produce role_resolution_source=session_resolver_fallback and permit a non-interactive source to overwrite an interactive transcript role",
  "after_behavior": "No code path yields session_resolver_fallback; unresolvable role writes no envelope and fails closed; interactive transcript roles are protected",
  "self_descriptive_naming": "session_resolver_fallback removal, fail-closed role guard, and regression test names expose the boundary",
  "obsolete_guidance_disposition": "GOV-SESSION-ROLE-AUTHORITY-001 is retired and omitted; active DCL v7 assertions govern",
  "history_preservation": "Append-only bridge filing; no foreign bytes adopted (envelope.py re-based to clean committed postimage); no whole-file Git operation",
  "baseline": {
    "target_hashes": {
      "groundtruth-kb/src/groundtruth_kb/session/envelope.py": "16D56A856CBCF606BBA14647A352D75D6BF92D7A60AAB43DA412A49B5ADC13B0",
      "scripts/session_self_initialization.py": "0347E8C11C57DA86CB1154E130AC3D9BE98B1600AACF581DD600B3B55D19BA30",
      "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py": "7CE2C3C107CD986DC764EEE3464564EAAA5608CE61E608C5A58354C77199D2DE"
    },
    "target_diff": "git status --short over the six target paths: no output (clean)",
    "predecessor": "WI-5653 active Runtime Interfaces PAUTH; WI-5580 DEFERRED (envelope.py clean)"
  },
  "expected_result": {
    "session_resolver_fallback_removed": true,
    "unresolvable_role_fails_closed": true,
    "transcript_role_preserved": true,
    "foreign_bytes_adopted": 0
  },
  "essential_context_preservation": "WI-5653 dependency retained and sequenceable; WI-5580 cohort deferred in its own lane; GO overlaps non-current; no foreign bytes absorbed",
  "hard_invariants": [
    "No code path yields role_resolution_source=session_resolver_fallback.",
    "Unresolvable role writes no envelope and fails closed.",
    "Interactive transcript roles are never overwritten by non-interactive sources.",
    "Only the six declared target paths are implementation scope."
  ],
  "fail_closed_conditions": [
    "target hash drift from clean baseline",
    "implementation-start packet missing or outside target paths",
    "any GO overlap re-appears on the six-path cohort",
    "session_resolver_fallback reintroduced",
    "retired GOV-SESSION-ROLE-AUTHORITY-001 cited as active"
  ],
  "rollback": "Reverse only the exact WI-5723 source and test hunks; never restore whole targets"
}
```


## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| session_resolver_fallback removed | python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_modernization_end_to_end_workflow.py -q --tb=short | all pass |
| Fail-closed unresolvable role | focused fixture | writes no envelope, exits nonzero |
| Transcript role preserved | new regression test | ::init role survives SessionStart |
| Existing suites | python -m pytest groundtruth-kb/tests/test_session_envelope.py -q --tb=short + modernization suites | pass |
| Code quality | python -m ruff check / ruff format --check | pass |
| Scope isolation | git status over the six targets | only the six modified |

## Recommended Commit Type

fix - removes a prohibited role-source fallback and fail-closes role resolution per owner directives.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
