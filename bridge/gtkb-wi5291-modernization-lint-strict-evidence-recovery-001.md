NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner-declared ::init gtkb pb; delegated strict-recovery drafting; TAFE dispatcher deliberately disabled
author_metadata_source: explicit current owner transcript and parent Prime Builder session context

bridge_kind: governance_review
Document: gtkb-wi5291-modernization-lint-strict-evidence-recovery
Version: 001
Date: 2026-08-01 UTC
Quarantines structurally invalid predecessor: bridge/gtkb-wi5291-modernization-candidate-lint-normalization-001.md through bridge/gtkb-wi5291-modernization-candidate-lint-normalization-006.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5291

target_paths: []

implementation_scope: none; zero-mutation evidence recovery
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
git_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: docs:

This proposal performs no MemBase mutation.
This proposal performs no approval-evidence work and writes no approval packet.

# WI-5291 Modernization Lint Normalization — Strict Evidence Recovery Proposal

## Disposition

Create a fresh strict-valid evidence chain for the already-completed WI-5291
lint normalization. The predecessor thread cannot accept a governed successor:
its version 003 declares decorated metadata
`Version: 003 (NEW; post-implementation report)` instead of exact
`Version: 003`, and it lacks the canonical
`Responds to: bridge/gtkb-wi5291-modernization-candidate-lint-normalization-002.md`
field, carrying only `Responds to GO`. The strict lifecycle resolver currently
fails first with `WRONG_BRIDGE_VERSION_METADATA` on that file.

The malformed numbered history remains immutable audit evidence. This fresh
thread does not rewrite, delete, rename, normalize, supersede factually, or use
the predecessor as implementation-start authority. It restates the complete
current evidence so an independent reviewer can approve a zero-mutation
re-observation route and, after the external authority-foundation gates recover,
verify the existing implementation without staging or re-attributing either
test carrier.

No additional source or test work is proposed. The two WI-5291 postimages are
already tracked, clean, Ruff-clean, formatted, and byte/AST-identical to the
implementation evidence independently reproduced in predecessor version 004.
The only current test failures were introduced by later specification and
source changes outside the WI-5291 lint delta. They must recover in their own
governed lanes before this fresh thread may request terminal verification.

## First-Line Role Eligibility Check

The current interactive session is Prime Builder by the owner's `::init gtkb
pb` declaration. `NEW` is a Prime Builder status under
`GOV-FILE-BRIDGE-AUTHORITY-001`. This entry opens a fresh strict recovery
thread and requests independent proposal review. It does not author `GO`,
`NO-GO`, or `VERIFIED`.

## Quarantined Predecessor State

Read-only physical inspection found the complete predecessor sequence:

```text
001 NEW -> 002 GO -> 003 NEW -> 004 NO-GO -> 005 NO-ACTION -> 006 NO-GO
```

Version 006 is the latest physical numbered status; no physical version 007
exists. The exact-slug work-intent record is expired, not active. A direct
strict-resolver read fails at version 003 before a same-slug append can be
authorized. The predecessor therefore remains quarantined as append-only
history and this version 001 is self-contained.

This non-live draft was prepared without acquiring a claim. Before live filing,
Prime Builder must acquire a claim for this fresh slug and use the governed
physical writer. This proposal does not activate, publish to, or mutate TAFE or
dispatcher state.

## Corrected Project Authorization Evidence

Fresh governed CLI reads establish:

- `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE` is active at version 2.
- WI-5291 has active direct membership
  `PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5291`.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  is active at version 5, unexpired, and list-free:
  `included_work_item_ids=null` and `excluded_work_item_ids=null`.
- The PAUTH permits governed bridge, test, governance-evidence, and atomic
  local-finalization work while retaining independent `GO`, exact claim,
  implementation-start, specification-derived testing, scoped staging, and
  independent verification gates.
- WI-5291's legacy `approval_state: unapproved` field is noncontrolling under
  the owner's project-only implementation-authorization doctrine.

The content-file applicability preflight independently evaluates this active
PAUTH as operation-time `allowed`. Project readiness dependencies do not grant
or revoke implementation authority and do not justify bypassing any bridge or
verification gate.

## Exact Existing Postimage Evidence

The original implementation carriers are included by observation only; they
are not declared mutation targets:

| Existing carrier | Current byte SHA-256 | Current normalized AST SHA-256 | Current state |
| --- | --- | --- | --- |
| `platform_tests/scripts/test_check_artifact_evaluability.py` | `69E4FAC09572619DCCD6C9FA526FBC14BA795AE1225949691E4574B612F15B67` | `3F04D3D21F2088A3FE0D9501E168991B6DD02A61D902B71499F60E86E156FCED` | tracked and clean |
| `platform_tests/scripts/test_modernization_authority_foundations.py` | `40DA822E7B7E2F4EFDE6BDEB42907F0F7103B3C2A5087C21881EEFDD2363A807` | `562D9405BD86FA2E7C1E97037BF796EECFF59D59938993E45D9B7B23F37E58DD` | tracked and clean |

Both paths entered current ancestry together in commit
`42a252ab57b5a203e9406b626c741d897e8fb196` and currently have no working-tree
diff. Each still contains exactly the intended post-path-setup
`from groundtruth_kb.db import KnowledgeDB  # noqa: E402` disposition.

Fresh read-only checks returned:

- focused Ruff E/F: `All checks passed!`;
- Ruff format: `2 files already formatted`;
- exact target Git status and diff: no output;
- cross-claim target-overlap scan: no active overlapping reservation; and
- exact byte and normalized AST hashes: the values in the table above.

These observations prove the original lint normalization remains intact. They
do not convert this proposal into a new implementation transaction.

## Later-Spec Drift Classification

The exact approved 17-test command currently reports `14 passed, 3 failed`.
All failures are in
`platform_tests/scripts/test_modernization_authority_foundations.py`; none is a
lint, format, byte, AST, or current-concurrency failure in either carrier.

The failures postdate the predecessor version-004 verification evidence:

1. `GOV-SESSION-ROLE-AUTHORITY-001` is now retired at version 6, with zero
   assertions and zero source paths. The frozen authority-carrier test still
   requires it to be current, asserted, source-backed, and evaluable.
2. `DCL-SESSION-ROLE-RESOLUTION-001` is now specified at version 7. Its current
   evaluator passes nine outer assertions but fails `ROLE-DCL-A7` because
   `scripts/check_dispatched_role_bootstrap.py` lacks the required
   `fail-closed` evidence string.

The GOV changed on 2026-07-24 and the DCL changed on 2026-07-29; predecessor
version 004 independently reproduced all 17 passing tests on 2026-07-15. The
current failures are therefore later authority-spec/source drift. They are not
defects in WI-5291's behavior-neutral Ruff normalization and are not concurrent
dirt. WI-5291 must nevertheless remain fail-closed because its approved
specification-derived acceptance command does not currently pass.

## Current Dependency Disposition

- WI-5718 owns retirement/purge of
  `GOV-SESSION-ROLE-AUTHORITY-001`. The work item remains open; its predecessor
  bridge thread ends `WITHDRAWN` at version 017 and requires a fresh successor.
- WI-5679 owns the worker-session role-resolution source recovery. Its current
  work-item state explicitly waits for a fresh WI-5718 complete-postimage DCL
  repair before a new REVISED proposal can proceed.
- WI-5741 is no longer a live bridge dependency. Its physical bridge chain now
  ends `VERIFIED` at version 009. Its MemBase `status_detail` still describes
  version 006 `NO-GO` and is stale; it must not be used as current bridge-state
  authority.

This recovery thread does not absorb WI-5718 or WI-5679 specification, source,
test, database, registry, or bridge scope. It waits for those governed lanes to
restore the exact 17-test acceptance gate, then re-observes WI-5291 evidence.

## Owner By-Reference Decision Evidence

`DELIB-20260731-WI5291-BYREF-FINALIZATION` exists at version 1, rowid 13016,
with `outcome=owner_decision`, `work_item_id=WI-5291`, and
`source_ref=bridge/gtkb-wi5291-modernization-candidate-lint-normalization-004.md`.
It authorizes chain-only by-reference finalization for WI-5291 lint
normalization.

The decision text contains one clerical carrier-name mismatch: its
parenthetical names `test_check_authority_evaluability.py` instead of the actual
second carrier, `test_modernization_authority_foundations.py`. The title,
work-item ID, and exact version-004 source reference bind the decision to the
complete predecessor thread. This proposal relies only on its thread-level
chain-finalization safety intent and claims no path-mutation authority from the
mistaken filename.

Because this fresh proposal declares no implementation target and its later
report will claim no changed source/test file, terminal finalization must stage
only the complete fresh numbered recovery chain plus the independently authored
verdict. Neither existing test carrier nor any predecessor-chain file may be
staged or re-attributed by this recovery transaction.

## Requirement Sufficiency

Existing requirements are sufficient for the zero-mutation recovery. The
current failures expose post-v004 authority-spec and source drift already owned
by WI-5718/WI-5679; they do not require a new WI-5291 requirement or broaden
this thread into those implementation lanes.

## Proposed Zero-Mutation Recovery Route

1. Obtain independent `GO` on this fresh strict proposal. `GO` authorizes only
   the evidence-reobservation plan; it authorizes no protected mutation.
2. Wait for the governed WI-5718/WI-5679 recovery to restore the exact 17-test
   acceptance command. Do not waive, skip, xfail, or rewrite the frozen test in
   this thread.
3. Recompute both target byte hashes, normalized AST hashes, exact Git status,
   active claim/packet overlaps, focused Ruff, format, and the exact 17-test
   command. Stop on any carrier drift, overlap, or test failure.
4. File a zero-mutation implementation report as the next version in this
   fresh thread. Its `Files Changed` section must say that no source or test
   file changed and must list the two carriers only as by-reference observation
   evidence.
5. An unrelated Loyal Opposition session independently reruns the same evidence
   and returns `NO-GO` on any mismatch. It may record `VERIFIED` only through
   the atomic finalizer, including solely the complete fresh recovery chain and
   the new verdict.
6. Preserve the malformed predecessor chain unchanged and retain its latest
   `NO-GO` as historical/quarantined state. Do not claim that this fresh chain
   rewrites or repairs those immutable bytes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-CODE-QUALITY-BASELINE-001`
- `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`
- `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`

## Prior Deliberations

- `DELIB-202666307` - independent predecessor version-002 GO and exact
  behavior-neutral WI-5291 conditions.
- `DELIB-20261887` - independently VERIFIED platform-tests Ruff-normalization
  precedent.
- `DELIB-20260731-WI5291-BYREF-FINALIZATION` - owner-authorized chain-only
  by-reference finalization for the WI-5291 predecessor report.
- `DELIB-202666274` and `DELIB-202667714` - controlling project-level
  implementation and governed atomic-local-finalization authority.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` - active
  parent-project authorization, not legacy WI approval state, controls member
  WI implementation approval.
- `bridge/gtkb-wi5291-modernization-candidate-lint-normalization-001.md`
  through version 006 - complete immutable predecessor context, including
  substantive verification, finalization NO-GO, invalid NO-ACTION, and current
  corrected NO-GO.

## Owner Decisions / Input

- The owner has directed that implementation approval is per project and that
  member work items inherit the active authorization of their direct parent
  project; legacy `work_items.approval_state` is noncontrolling.
- `DELIB-20260731-WI5291-BYREF-FINALIZATION` authorizes chain-only
  by-reference finalization for WI-5291 lint normalization.
- The owner has directed that append-only source-of-truth history be preserved
  when practical. The malformed predecessor remains unchanged; this fresh
  strict chain avoids rewriting it.
- The owner has deliberately disabled TAFE dispatcher repairs. This proposal
  neither activates nor mutates TAFE or dispatcher state.

No new owner decision is requested. Independent proposal review and the
existing governed dependency lanes are the required next steps.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5291 predecessor versions 001-006, DELIB-202666307, DELIB-20260731-WI5291-BYREF-FINALIZATION, and fresh 2026-08-01 read-only evidence",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
  "primary_route": "fresh strict zero-mutation evidence chain after external authority-foundation recovery",
  "before_behavior": "The verified lint postimages are clean and unchanged, but the immutable predecessor chain is structurally malformed and later authority-spec/source drift makes three of seventeen acceptance tests fail.",
  "after_behavior": "The malformed history remains untouched; a fresh strict chain independently re-observes the same postimages only after all seventeen acceptance tests pass again.",
  "self_descriptive_naming": "The recovery slug identifies WI-5291, modernization lint, strictness, and evidence-only recovery.",
  "obsolete_guidance_disposition": "Predecessor NO-ACTION closure and legacy WI approval-state gating remain historical evidence and are not reused as authority.",
  "history_preservation": "All predecessor numbered files remain byte-for-byte unchanged; the recovery is a new append-only thread.",
  "baseline": {
    "evaluability_byte_sha256": "69E4FAC09572619DCCD6C9FA526FBC14BA795AE1225949691E4574B612F15B67",
    "evaluability_ast_sha256": "3F04D3D21F2088A3FE0D9501E168991B6DD02A61D902B71499F60E86E156FCED",
    "authority_byte_sha256": "40DA822E7B7E2F4EFDE6BDEB42907F0F7103B3C2A5087C21881EEFDD2363A807",
    "authority_ast_sha256": "562D9405BD86FA2E7C1E97037BF796EECFF59D59938993E45D9B7B23F37E58DD",
    "current_focused_tests": "14 passed, 3 later-spec/source-drift failures"
  },
  "expected_result": {
    "target_byte_changes": 0,
    "target_ast_changes": 0,
    "focused_tests": "17 passed",
    "ruff_errors": 0,
    "format_drift_files": 0,
    "fresh_chain_strict": true
  },
  "essential_context_preservation": "Preserve exact lint postimages, later-spec drift classification, project-only authorization, by-reference safety, and immutable malformed history.",
  "hard_invariants": [
    "no source or test mutation",
    "no predecessor bridge rewrite or deletion",
    "no target staging or re-attribution",
    "no test waiver, xfail, or frozen-carrier edit",
    "no TAFE or dispatcher activation or mutation"
  ],
  "fail_closed_conditions": [
    "either byte or AST hash changes",
    "either target is dirty or concurrently reserved",
    "the exact seventeen-test command does not pass",
    "Ruff lint or format check fails",
    "fresh chain metadata or preflight is invalid"
  ],
  "rollback": "No source rollback exists for a zero-mutation proposal. Withdraw only the fresh draft or later strict chain through governed lifecycle handling; retain the predecessor audit history."
}
```

## Specification-Derived Verification Plan

| Governing surface | Required evidence and expected result |
| --- | --- |
| `GOV-CODE-QUALITY-BASELINE-001`; code-quality ADR/DCL | Focused Ruff and Ruff format commands pass without any new waiver or source change. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; evaluability DCL | Both byte and normalized AST hashes equal the recorded postimages; exact target Git status/diff is clean. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact two-file pytest command collects 17 and passes all 17 after WI-5718/WI-5679 recovery. |
| Project authorization surfaces | Governed CLI read shows active project, active direct WI membership, and active list-free PAUTH v5; legacy WI approval state is not used. |
| Bridge authority and provenance | Strict resolver accepts every version of the fresh chain; predecessor remains unchanged and quarantined. |
| Dependency ordering | Recheck live claims and target packet overlaps immediately before evidence collection; require no collision. |
| Source-of-truth freshness | Use physical numbered files for bridge status, governed CLI for project/spec/Deliberation Archive state, and exact Git reads for carrier identity. |

Required report-time commands:

```text
python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py -q --tb=short
python -m ruff check platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py --select E,F --ignore E501,E741
python -m ruff format --check platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py
git status --short -- platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py
git diff -- platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py
python scripts/bridge_applicability_preflight.py --content-file <fresh-numbered-report>
python scripts/adr_dcl_clause_preflight.py --content-file <fresh-numbered-report>
```

The report must also recompute the exact byte and normalized AST hashes and
record the active-claim/packet overlap result. Evidence from this proposal-time
audit is baseline context, not a substitute for the later executed report.

## Acceptance Criteria

1. The predecessor chain remains byte-for-byte unchanged and explicitly
   quarantined for malformed v003 metadata.
2. The fresh recovery chain is strict-resolver-clean and independently reviewed.
3. Both existing carriers remain tracked, clean, byte/AST-identical to the
   version-004 postimages, Ruff-clean, and formatted.
4. The exact focused command collects and passes all 17 tests; no waiver,
   xfail, carrier-list edit, or WI-5291 target mutation supplies the pass.
5. WI-5718/WI-5679 recovery remains separate; WI-5741 is correctly treated as
   physically `VERIFIED` v009 rather than a current blocker.
6. Active Assurance project membership and list-free PAUTH v5 remain current at
   operation time; no legacy WI approval-state gate is introduced.
7. The zero-mutation implementation report claims no changed source/test path
   and distinguishes the two observed carriers from the finalizer include set.
8. Independent Loyal Opposition verification uses the atomic finalizer with
   only the complete fresh recovery chain and the new verdict.
9. No protected file, MemBase record, Git state, external system, TAFE, or
   dispatcher state changes under this proposal.

## Risks / Rollback

The primary risk is false terminal closure: the lint postimages are correct,
but later authority-spec/source drift currently breaks one required acceptance
command. The secondary risk is laundering malformed history or re-attributing
test files through a new chain. The fail-closed 17-test gate, zero-target scope,
exact hash/currentness checks, fresh strict lifecycle, by-reference disposition,
and independent atomic finalizer contain those risks.

There is no source rollback because this proposal authorizes no source change.
If the recovery design is rejected, retain the draft or withdraw a later live
entry through the governed lifecycle; do not rewrite the predecessor or mutate
the existing carriers.

## Non-Approval And No-Mutation Boundary

This entry authorizes no implementation, protected mutation, target rewrite,
test waiver, specification mutation, work-item/project/PAUTH mutation, claim,
implementation-start packet, Git staging/commit/history action, release,
deployment, credential action, external-system mutation, dispatcher action, or
TAFE action.

The next lawful live action is independent `GO` or `NO-GO` review after a fresh
Prime Builder claim and governed physical filing. The later evidence report is
permitted only after all stated dependencies and acceptance gates pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
