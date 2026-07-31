REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Revised Proposal — WI-5144 Current-HEAD HP08 Terminal Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5144-hp08-current-head-finalization-recovery
Version: 005
Responds to: bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-004.md
Reviewed GO: bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-002.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5144
target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity.py", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-005.md", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-006.md", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-007.md", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-008.md"]
kb_mutation_in_scope: false
Recommended commit type: docs

## Revision Claim

This revision accepts the version 004 NO-GO and replaces the contradictory
version 001 test obligation with an exact by-reference verification contract.
The already-committed HP08 source and test paths remain read-only. Existing
focused tests are the required targeted tests; this recovery does not require
inventing duplicate tests or mutating either implementation path merely to
produce a terminal artifact.

This proposal does not authorize terminal finalization under the current
project PAUTH. That PAUTH forbids `git_commit`. Before a later implementation
report or terminal finalization, an owner-approved narrow authorization must
cover the two by-reference paths, the exact v005-v008 bridge cohort, and the
governed local commit operation. The finalizer/authorization-order correction
required by
`bridge/gtkb-wi5458-proposal-pauth-precedence-v2-014.md` must also be terminally
accepted before this thread attempts atomic terminal closure.

No source, test, database, configuration, dispatcher, TAFE, staging, commit,
push, release, deployment, credential, external-system, history-rewrite,
cleanup, or destructive mutation is performed by this revision.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-HARNESS-PARITY-WORK-PACKET` defines the
  HP08 modernization scope.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-HANDLE-MAP` links WI-5144 to that
  scope.
- `DELIB-202666274` supplies the current evidence-only project authority while
  preserving independent review and terminal gates.
- `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md` is the
  reproducible current-HEAD evidence report.
- `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-004.md` is the
  controlling NO-GO answered here.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-014.md` identifies the
  separate P0 finalizer/authorization-order dependency.

## Owner Decisions / Input

No new owner decision is required to file this revision or to keep the two
implementation paths read-only. A separate owner decision is required before
terminal execution to create a narrow finalization PAUTH that permits the
exact local commit operation and exact cohort. This proposal does not infer,
create, or widen that authority.

## Requirement Sufficiency

**Existing requirements sufficient.** The cited HP08 parity, project
authorization, governed Git lifecycle, bridge, and verification requirements
fully determine the by-reference test contract and the fail-closed terminal
prerequisites. A new implementation requirement is not needed. The later
narrow PAUTH is owner authorization for the already-defined terminal operation,
not a revision of the underlying technical requirements.

## Findings Addressed

### F1 — Terminal authorization is absent

Accepted. The current project PAUTH remains sufficient only for this governed
proposal/evidence correction and explicitly forbids `git_commit`. The revised
terminal preconditions are:

1. a separate owner-approved narrow PAUTH is active at operation time;
2. it covers both by-reference implementation paths and exact v005-v008 bridge
   cohort;
3. it permits the registered governed local-commit operation while continuing
   to forbid push, release, deployment, credentials, dispatcher mutation,
   external-system mutation, destructive cleanup, and history rewrite;
4. a fresh claim and schema-v3 packet bind that exact scope; and
5. the WI-5458 finalizer-order/enforcement dependency is terminally accepted.

Until all five conditions hold, no implementation report, VERIFIED verdict,
staging, or commit is requested from this thread.

### F2 — The prior test obligation conflicts with the permitted scope

Accepted and corrected. Version 001's boilerplate phrase that the report
“must add targeted tests” is superseded. The targeted HP08 regressions already
exist in `platform_tests/scripts/test_check_harness_parity.py`; version 003
executed them successfully. The revised obligation is to rerun and cite those
existing tests by exact command and result without changing the file.

If independent review finds a concrete uncovered requirement, this thread
must stop and file a fresh exact source/test proposal. It must not silently
expand this by-reference recovery into test implementation.

## Scope Changes

- Preserve `scripts/check_harness_parity.py` and
  `platform_tests/scripts/test_check_harness_parity.py` byte-for-byte as
  by-reference evidence.
- Replace “add targeted tests” with an exact existing-test mapping.
- Declare the exact intended bridge cohort through v008 so a future narrow
  finalization PAUTH can be evaluated deterministically.
- Add the WI-5458 finalizer-order/enforcement correction as a terminal
  dependency.
- Retain the unrelated `gtkb-skill-rollout` registry-extra failure as disclosed
  external baseline evidence; it is not an HP08 source change.

## Proposed Terminal Procedure After Independent GO And New Authority

1. Confirm the two implementation paths are tracked, clean, and byte-identical
   to the reviewed current-HEAD identities.
2. Confirm a narrow owner-approved PAUTH covers the two paths, exact v005-v008
   cohort, and registered local-commit operation.
3. Confirm the WI-5458 finalizer correction is terminally accepted and the
   governed finalizer enforces independent verdict, active PAUTH, and active
   claim in an executable order.
4. Acquire the exact work-intent claim and schema-v3 packet; any mismatch stops
   the operation before a side effect.
5. Rerun the focused HP08 selection, full parity module, Ruff check/format,
   exact path status/diff checks, applicability preflight, and clause preflight.
6. File v007 as a fresh evidence report. It must disclose the full-module
   result, including any unchanged unrelated failure.
7. Loyal Opposition independently returns v008 `VERIFIED` or `NO-GO`.
8. Only a finalizer path proven compatible with the independent-verdict order
   may create the exact local commit. No push, release, or deployment follows.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5144; v004 NO-GO; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed numbered bridge chain",
  "primary_route": "gt bridge revision followed by independently reviewed terminal recovery",
  "before_behavior": "Version 001 simultaneously forbade test-path mutation and required the implementation report to add targeted tests, while its PAUTH forbade the terminal commit.",
  "after_behavior": "Existing HP08 tests are mapped and rerun by reference; source and test bytes remain unchanged; terminal closure waits for exact owner-approved commit authority and the corrected governed finalizer order.",
  "self_descriptive_naming": "The title, WI, exact by-reference paths, bridge cohort, test mapping, and terminal dependencies name the complete effect.",
  "obsolete_guidance_disposition": "The version 001 add-targeted-tests phrase is explicitly superseded; the remaining historical chain stays immutable evidence.",
  "history_preservation": "All numbered bridge files remain append-only; no historical report, verdict, source path, or test path is rewritten or removed.",
  "baseline": {
    "work_item": "WI-5144",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY",
    "target_paths": [
      "scripts/check_harness_parity.py",
      "platform_tests/scripts/test_check_harness_parity.py",
      "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-005.md",
      "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-006.md",
      "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-007.md",
      "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-008.md"
    ]
  },
  "expected_result": {
    "summary": "A mechanically coherent by-reference recovery with explicit test, authority, dependency, and terminal-order gates.",
    "scope": [
      "No source or test mutation",
      "Existing focused and full-module tests rerun and disclosed",
      "No terminal action without narrow PAUTH and corrected finalizer"
    ],
    "acceptance_criteria": [
      "Conflicting test-add language superseded",
      "By-reference identities remain clean",
      "Independent VERIFIED precedes exact governed finalization"
    ]
  },
  "rollback": {
    "instructions": "Use only an additive bridge disposition; do not alter the by-reference implementation paths.",
    "verification": "Re-run candidate/live preflights and exact two-path status checks."
  },
  "hard_invariants": [
    "Bridge review, active PAUTH, exact claim, schema-v3 packet, and independent verification remain mandatory.",
    "Unrelated worktree and index bytes remain untouched.",
    "Push, release, deployment, credentials, dispatcher mutation, destructive cleanup, and history rewrite remain forbidden."
  ],
  "fail_closed_conditions": [
    "Narrow terminal PAUTH is absent, expired, denied, or forbids the commit operation.",
    "WI-5458 finalizer-order correction is not terminally accepted.",
    "A by-reference identity, test result, preflight, claim, packet, or cohort changes."
  ],
  "essential_context_preservation": "The revision carries the original HP08 intent, v003 evidence, v004 findings, exact terminal prerequisites, and unrelated-failure disclosure forward."
}
```

## Pre-Filing Preflight Subsection

The completed revision draft is evaluated through both mandatory candidate
gates before filing:

- Applicability preflight must exit 0 with no missing required or advisory
  specifications and no blocking errors.
- ADR/DCL clause preflight must exit 0 with zero blocking gaps.

The governed revision helper repeats those gates after author metadata is
inserted and fails closed on any drift.

## Specification-Derived Verification Plan

| Requirement | Existing read-only verification | Required result |
| --- | --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | HP08-focused selection in `platform_tests/scripts/test_check_harness_parity.py` | all selected checks pass |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | full `test_check_harness_parity.py` module | disclose every result; no hidden HP08 failure |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | semantic-adapter contradiction tests in the existing module | semantic mismatch remains rejected |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Git blob, SHA-256, status, and diff checks for both by-reference paths | identities unchanged and paths clean |
| project authorization requirements | exact PAUTH query, claim, and schema-v3 packet | active narrow terminal authority at each side effect |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | corrected governed finalizer dry-run/execution evidence | independent verdict and PAUTH/claim order are executable |
| bridge/spec linkage requirements | candidate/live applicability and clause preflights | exit 0; no blocking gaps |
| `GOV-WORK-TREE-HYGIENE-001` | exact cohort status plus disposable-index finalization evidence | unrelated worktree/index bytes preserved |

## Acceptance Criteria

- Version 001's conflicting test-add obligation is explicitly superseded by
  the existing-test mapping above.
- Both implementation paths remain unchanged and clean throughout this
  proposal/evidence lifecycle.
- No terminal action occurs under a PAUTH that forbids `git_commit`.
- The later narrow PAUTH, claim, and schema-v3 packet cover the two by-reference
  paths and exact v005-v008 cohort.
- The WI-5458 finalizer-order/enforcement dependency is terminally accepted
  before this thread requests atomic closure.
- Fresh focused and full-module evidence is independently reviewed.
- Terminal status is `VERIFIED` only after all scope, test, authority, and
  finalization-order gates pass.

## Risk And Rollback

The main risk is treating clean, already-committed implementation paths as a
reason to duplicate tests or fabricate a commit under insufficient authority.
The revision prevents both outcomes and makes the terminal dependencies
explicit.

Rollback is additive bridge disposition only. The two by-reference paths are
not modified, so no source/test rollback exists. A denied or expired PAUTH,
claim, packet, dependency, preflight, or test result stops the procedure before
filing a terminal report or creating a commit.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
