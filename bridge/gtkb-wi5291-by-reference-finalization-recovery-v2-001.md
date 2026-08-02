NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex desktop; owner-designated Prime Builder; manual physical-bridge processing with dispatcher disabled
author_metadata_source: explicit_interactive_session_metadata

# WI-5291 By-Reference Finalization Recovery — Strict Controller v2

bridge_kind: prime_proposal
Document: gtkb-wi5291-by-reference-finalization-recovery-v2
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5291
Related quarantined thread: gtkb-wi5291-modernization-candidate-lint-normalization

target_paths: ["bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_activation_in_scope: false
source_or_test_mutation_in_scope: false

## Summary

Recover WI-5291 through one new strict-valid, evidence-only bridge controller.
The owner has now explicitly approved the bounded by-reference finalization in
`DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL`. The historical
implementation remains technically byte/AST-identical to the version-003 and
version-004 evidence and must not be re-touched.

The old thread cannot lawfully receive the requested v007 revision. Its v003
metadata says `Version: 003 (NEW; post-implementation report)`, and the current
public lifecycle resolver fails closed with `WRONG_BRIDGE_VERSION_METADATA`.
This proposal therefore preserves the old chain unchanged as quarantined audit
evidence and starts a fresh controller rather than rewriting history or
depending on unapproved WI-5637/WI-5827 parser-normalization work.

After independent `GO`, Prime Builder will acquire the exact
`go_implementation` claim and schema-v3 start packet, re-derive the current
evidence, and file only v003 of this controller. A session-independent Loyal
Opposition reviewer then decides whether the immutable evidence and disclosed
current-state drift support a commit-backed terminal v004.

## Historical Chain Quarantine

The six-file historical controller remains byte-for-byte unchanged:

- Versions 001 through 005 are tracked in custodial sweep commit
  `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`.
- Version 006 is the current untracked `NO-GO` that identified the missing
  durable owner decision, missing linkage, and legacy unapproved state.
- Strict lifecycle resolution stops at v003 with
  `WRONG_BRIDGE_VERSION_METADATA`; no successor on that slug can establish
  current implementation authority.

Version 006 is preservation evidence, not authority. No old file may be edited,
renamed, hidden, deleted, or reinterpreted as a valid continuation.

## Owner Approval And Current-State Reconciliation

`DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL` approves WI-5291 and
its by-reference finalization while excluding source/test edits, restaging,
broad Git operations, direct legacy-approval mutation, dispatcher/TAFE action,
push, release, deployment, and cleanup.

The decision was made against v005/v006's stale statement that the two subject
files remained untracked. Current Git authority proves that both paths were
already added by broad custodial sweep commit
`42a252ab57b5a203e9406b626c741d897e8fb196` on 2026-07-16. That commit is an
ancestor of HEAD and contains 916 paths; it is immutable implementation
provenance, not a scoped WI-5291 terminal-finalization transaction.

Making the stale `untracked` statement literally true would require destructive
untracking or history alteration, both outside the owner decision and the
PAUTH. This proposal applies the approved by-reference purpose conservatively:
leave both files at their current clean tracked identities, do not edit or
restage them, cite their immutable commit by reference, and let independent
review fail closed if that reconciliation is insufficient.

## By-Reference Finalization Waiver

The owner expressly authorizes a **by-reference finalization waiver** for
WI-5291 in `DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL`.

The following immutable implementation subjects are by-reference evidence and
MUST NOT be modified, restored, staged, recommitted, or included in the
recovery transaction:

- `platform_tests/scripts/test_check_artifact_evaluability.py`
- `platform_tests/scripts/test_modernization_authority_foundations.py`

The waiver changes only finalization mechanics. It does not waive current
evidence collection, content review, specification linkage, tests, review
independence, exact include-set checks, commit-first ordering, or fail-closed
behavior.

## Current Revalidated Evidence

At the current HEAD on 2026-08-01:

- Both subject paths are clean and tracked at index blob IDs
  `3799fa92a02c6d22c63f7b59fa7ff88163cf0e16` and
  `0e81f08b37bfce991f28ae9d32bbb68e0b52fc08`.
- Their raw SHA-256 values remain
  `69e4fac09572619dccd6c9fa526fbc14ba795ae1225949691e4574b612f15b67`
  and `40da822e7b7e2f4efde6bdeb42907f0f7103b3c2a5087c21881eefdd2363a807`.
- Their normalized AST SHA-256 values remain
  `3f04d3d21f2088a3fe0d9501e168991b6dd02a61d902b71499f60e86e156fced`
  and `562d9405bd86fa2e7c1e97037bf796eecff59d59938993e45d9b7b23f37e58dd`.
  All four identities exactly match the historical independently reviewed
  post-implementation evidence.
- Target-scoped Ruff E/F and Ruff format checks pass; scoped `git diff --check`
  passes.
- The original two-file focused pytest command now reports 14 passed and 3
  failures. Each failure is caused by later governance-state drift:
  `GOV-SESSION-ROLE-AUTHORITY-001` is now retired/zero-executable and
  `DCL-SESSION-ROLE-RESOLUTION-001` evaluates never-pass. The target test bytes
  themselves are unchanged.
- The historical broad release Ruff command now reports ten findings in other
  concurrent platform-test files. None is in either WI-5291 subject.

These current failures are disclosed evidence, not silently accepted as a
green VERIFIED gate. Version 003 must re-run and report them. Loyal Opposition
must issue `NO-GO` unless the immutable implementation evidence plus exact
later-drift attribution satisfies every applicable terminal requirement.

## Proposed Recovery Sequence

1. Independent Loyal Opposition reviews this current-state reconciliation and
   files v002 `GO` or `NO-GO`.
2. After `GO`, Prime Builder acquires a fresh exact claim and schema-v3
   implementation-start packet covering only v003.
3. Prime Builder re-derives commit ancestry/inventory, both current blob/raw/AST
   identities, target cleanliness, focused tests, target Ruff/format/diff, and
   the full old/new bridge inventories without changing subject bytes.
4. Prime Builder files v003 as a factual implementation report carrying the
   by-reference waiver, original independent verification, current-state drift,
   exact command results, and terminal include set.
5. Independent Loyal Opposition either files `NO-GO` or invokes the governed
   commit-first finalizer for v004.
6. Only after commit-backed `VERIFIED` may WI-5291 backlog metadata be
   reconciled through a separately authorized canonical operation.

## Prospective Terminal Include Set

Immediately before terminalization, the reviewer must validate an exact
five-path include set:

- `bridge/gtkb-wi5291-modernization-candidate-lint-normalization-006.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-001.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-002.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-004.md`

Versions 001 through 005 of the historical controller are already committed
and remain by-reference audit history. The two implementation subjects are
explicitly excluded. No unrelated path may enter the terminal transaction.

No source, test, configuration, registry, projection, dispatcher/TAFE,
credential, external-system, release, deployment, push, history-rewrite,
destructive-cleanup, or pre-verification KB mutation is authorized.

## Requirement Sufficiency

Existing requirements sufficient.

The owner decision supplies the missing WI/finalization approval;
`GOV-FILE-BRIDGE-AUTHORITY-001` supplies append-only and commit-backed terminal
requirements; the active v5 PAUTH supplies the bounded bridge,
governance-evidence, and governed local finalization envelope; and the linked
quality/nonimpairment specifications define the evidence floor. No platform
behavior or specification change is required by this evidence-only recovery.

## Specification Links

- `GOV-CODE-QUALITY-BASELINE-001`
- `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`
- `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL` — explicit owner
  approval for WI-5291 and its bounded by-reference finalization.
- `DELIB-202666307` — original independent GO conditions and technical
  evidence contract.
- `DELIB-202666274` — modernization program authority while preserving normal
  review and mechanical gates.
- Historical v004 — independent technical verification and the original
  by-reference finalizer blocker.
- Historical v006 — missing-decision/linkage NO-GO and current routing basis.

## Owner Decisions / Input

The owner replied `Approve WI-5291 by-reference finalization as written` in
this Prime Builder session. That decision is durably recorded at
`DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL` and resolves the approval
blocker. No further owner decision is required before independent review.

The legacy backlog `approval_state: unapproved` remains disclosed compatibility
metadata and is not directly mutated. The owner decision, active PAUTH,
independent GO, exact claim, and implementation-start packet remain the
conjunctive execution authority.

## Specification-Derived Verification Plan

| Specification / invariant | Command or evidence | Required or currently observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict lifecycle resolver on the new slug after every version; resolver on old slug | New chain resolves strictly; old chain remains quarantined with the exact `WRONG_BRIDGE_VERSION_METADATA` diagnostic. |
| Project authorization specs | Live PAUTH read, exact claim status, schema-v3 `implementation_authorization.py begin/validate` | PAUTH v5 active; after GO, only v003 admitted before any write. |
| By-reference subject identity | `git ls-files --stage`, raw SHA-256, normalized AST SHA-256, and commit ancestry/inventory | Current identities match historical reviewed values; commit `42a252ab...` is an ancestor, contains both subjects, and has 916 total paths. |
| `GOV-CODE-QUALITY-BASELINE-001` | Target-scoped Ruff E/F and format checks; broad release Ruff command | Target checks pass. Broad command currently fails only on ten disclosed non-target findings; no false all-green claim. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Focused 17-test pytest command | Current result is 14 passed/3 later-state failures. Version 003 records exact diagnostics; terminal review fails closed unless evidence meets the governing floor. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare raw/AST identities and scoped Git diff/status before/after | Subject identities and clean state unchanged; no subject mutation or staging. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact prospective five-path include census and staged diff immediately before finalization | Only old v006 plus new v001-v004; subject and unrelated paths excluded. |
| Proposal/spec-linkage constraints | Candidate/live applicability and mandatory clause preflights | No missing required/advisory specification, allowed operation-time PAUTH, zero blocking clause gaps. |
| Artifact lifecycle specs | GO/claim/start/report/verdict/commit ordering | No v003 before GO/start; terminal state only after exact commit-first finalization. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every target/evidence path under `E:/GT-KB` | No out-of-root dependency or artifact. |

## Acceptance Criteria

1. The new chain resolves strictly from v001 and the historical six-file chain
   remains unchanged.
2. Durable owner approval and active PAUTH v5 are cited without treating the
   legacy approval label as authority.
3. No source/test mutation, staging, restoration, or recommit occurs.
4. Version 003 re-derives the immutable commit, blob, raw, and AST identities
   and reports current test/lint outcomes without concealing drift.
5. Independent review fails closed on any unsatisfied VERIFIED requirement.
6. Any terminal commit is created before terminal publication and contains
   exactly old v006 plus new v001-v004.
7. No dispatcher/TAFE activation or configuration, push, release, deployment,
   external mutation, credential work, history rewrite, or cleanup occurs.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL and the independently reviewed WI-5291 v003-v006 evidence",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Fresh strict bridge controller: v001 proposal, v002 independent GO or NO-GO, v003 evidence-only implementation report, and v004 independent terminal review",
  "before_behavior": "The historical controller is append-blocked by malformed v003 Version metadata, the already reviewed subject bytes are clean and tracked through custodial sweep commit 42a252ab57b5a203e9406b626c741d897e8fb196, and current verification exposes later governance-state drift.",
  "after_behavior": "The historical chain remains quarantined unchanged while a strict controller transparently carries immutable by-reference subject identity, current drift, exact verification results, and the bounded terminal cohort to independent review.",
  "self_descriptive_naming": "The recovery-v2 slug identifies WI-5291, by-reference finalization, and recovery from the malformed historical controller.",
  "obsolete_guidance_disposition": "The old chain is retained as audit evidence but is not used as the live lifecycle controller; no parser relaxation or historical rewrite is performed.",
  "history_preservation": "All six historical controller files and the two implementation subjects remain byte-for-byte unchanged and queryable; the new controller is append-only.",
  "baseline": {
    "historical_versions": 6,
    "strictly_appendable_historical_versions": 0,
    "focused_tests_passed": 14,
    "focused_tests_failed_from_later_state_drift": 3,
    "implementation_subject_mutations_planned": 0
  },
  "expected_result": {
    "strict_new_controller_versions_before_terminal_review": 3,
    "implementation_subject_mutations": 0,
    "historical_controller_mutations": 0,
    "independent_review_gates": 2,
    "terminal_commit_path_ceiling": 5
  },
  "rollback": {
    "instructions": "If independent review rejects the recovery, leave the NEW/NO-GO audit trail in place, release the exact claim, and perform no v003 subject or terminal-finalization mutation.",
    "test": "Strict resolver still reports the historical WRONG_BRIDGE_VERSION_METADATA diagnostic, both subject raw/AST identities remain unchanged, and Git shows no subject staging or diff."
  },
  "hard_invariants": [
    "No mutation or staging of either WI-5291 implementation subject",
    "No rewrite of any historical controller file",
    "No bridge report before independent GO plus fresh claim and schema-v3 implementation-start authorization",
    "No terminal publication before commit-first independent review",
    "No dispatcher or TAFE activation or configuration"
  ],
  "fail_closed_conditions": [
    "The new controller does not resolve strictly",
    "Current subject identity differs from the reviewed raw or normalized-AST evidence",
    "The exact claim or operation-time project authorization is absent",
    "The proposed terminal cohort exceeds old v006 plus new v001-v004",
    "Independent review cannot substantiate the disclosed later-state test failures"
  ],
  "essential_context_preservation": "The owner decision, old-chain parser defect, custodial sweep ancestry, exact current subject identities, current 14-pass/3-fail verification state, five-path terminal ceiling, and disabled-dispatcher boundary are all preserved in the live controller."
}
```

## Risk / Rollback

The largest risk is silently translating the stale `untracked` premise into a
false current-state claim. This proposal instead discloses the custodial sweep
and treats the current clean tracked blobs as immutable by-reference evidence.
A second risk is laundering later failing governance state into VERIFIED; exact
current results and independent fail-closed review prevent that.

Before terminal commit, rollback is a no-op or a new append-only revision. A
failed finalizer must leave no published terminal candidate. After a valid
terminal commit, correction remains append-only or uses a separately authorized
revert; neither subject nor historical bridge content is rewritten.

## Recommended Commit Type

`chore(bridge)` for a separately authorized exact terminal-finalization commit.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
