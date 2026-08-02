REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher/TAFE deliberately disabled
author_metadata_source: explicit_owner_direction

bridge_kind: prime_proposal
Document: gtkb-wi5437-verdict-removal-claim-evidence
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5437-verdict-removal-claim-evidence-006.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5437
target_paths: ["scripts/verdict_evidence_anchor_preflight.py", "platform_tests/scripts/test_verdict_evidence_anchor_preflight.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Prime Builder Revision — Reject Unsupported Exact-Path Removal Claims

## Revision Claim

Prime Builder accepts v006 in full and withdraws reliance on v003/v005 as
lifecycle outcomes. The work approved in v001/v002 remains unimplemented;
this substantive revision restores it to the current review frontier with a
fresh baseline, current PAUTH v5 evidence, and explicit isolation from the
landed WI-5438 fixture regions.

No source or test mutation is performed by this filing. Both declared targets
are clean, no live WI-5437 claim exists, and the historical claim is expired.
Implementation requires a new independent GO, fresh exact claim, and passing
implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. The observed WI-5370 report/verdict pair,
WI-5437, TEST-11547, operative-document provenance, fail-closed bridge
authority, and modernization nonimpairment contract define a narrow mechanical
check. No open-ended semantic classifier or new owner decision is required.

## Current Authority And Baseline

- WI-5437 is open and an active member of active
  `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`.
- Active list-free project PAUTH v5, owner decision `DELIB-202667714`, permits
  source, test, bridge, metadata, configuration, documentation, runtime-state,
  and governance-evidence classes while retaining every ordinary gate.
- Source SHA-256:
  `A47FD9E95038E8271424DCEB3AFF7307B2B8BD22005394072CC42EEC9DF2099A`.
- Test SHA-256:
  `E7EC69825207DF25DC52882FCE7718CDD60744DF34367BB1FA098DDE8E113624`.
- The source still matches v001's baseline. The test baseline changed through
  landed WI-5438 fixture work and is clean at the hash above.
- Current source contains no unsupported-removal-claim implementation.

Five active project dependency edges are readiness/release-closure evidence
requirements for the Artifact Decontamination, Context Manifests, Git
Lifecycle, Harness Parity, and Runtime Interfaces modernization projects.
Each explicitly grants no implementation authority. They do not block this
proposal/GO/start cycle, but must remain visible in readiness and release
closure reporting.

## Proposed Scope

Extend the canonical shared verdict-evidence anchor validator with one bounded
rule:

1. For a gated Loyal Opposition verdict, recognize only explicit prose that
   says the operative implementation report claims removal of an exact
   backtick-delimited in-root path.
2. Bind to the exact operative report named by the verdict's governed
   predecessor/proposal chain; do not search unrelated reports.
3. Require an unambiguous positive removal statement for the same normalized
   path in that report, such as a Files Changed entry explicitly recording the
   removal.
4. Emit a named `unsupported_removal_claim` violation when that evidence is
   absent. The real WI-5370 v003 report/v004 verdict pair is the negative
   regression: the report says Prime Builder did not remove bridge files while
   the verdict asserts that it promised removal of
   `scripts/per_thread_finalization_repair.py`.
5. Preserve legitimate review: when the operative report really claims exact
   path removal and the reviewer observes the path reappeared, the verdict
   remains valid.
6. Leave ambiguous prose, general absence findings, other semantic assertions,
   non-gated statuses, non-operative documents, and paths without the exact
   removal-claim form outside this rule.
7. Reuse the existing shared validator so writer, compliance hook, provider,
   and verification paths receive identical behavior without harness-specific
   branches.

## WI-5438 Fixture Isolation

WI-5438's functional changes are present in clean HEAD even though its bridge
report lifecycle remains nonterminal. This revision does not edit or reuse
WI-5438's existing fixture blocks. New WI-5437 regression cases must occupy
distinct named fixture regions, preserving every existing hash-stable test
case. If the test target drifts before start, Prime Builder must rebaseline and
return for review rather than merge through an unexamined overlap.

## Explicitly Out Of Scope

- no open-ended natural-language or model-based semantic review;
- no bridge history rewrite, file deletion, or verdict auto-correction;
- no role, harness, dispatcher, TAFE, routing, or provider behavior change;
- no direct harness contact, external-system, credential, deployment, release,
  push, or history-rewrite operation; and
- no hard-coded timer, throttle, threshold, retry, fan-out, or concurrency
  value.

## Cross-Harness Disposition

The validator is the canonical shared evidence surface. The same narrow rule
applies to every harness and publication adapter; no vendor exception is
introduced. V006's reviewer session is distinct from this Prime Builder
session, and the next verdict must come from another independent Loyal
Opposition context.

## Governance And Start Boundary

- The numbered chain is append-only; no earlier file is edited.
- Project PAUTH does not replace independent GO, exact claim, packet,
  implementation report, independent VERIFIED, or protected-commit gates.
- A fresh implementation-start evaluation must authorize exactly the two
  declared targets under PAUTH v5.
- After implementation, Prime Builder files the first report as `NEW` with
  actual commands, counts, hashes, and exact diff evidence.
- Dispatcher and TAFE remain disabled and out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667714` — current list-free Assurance PAUTH v5 and governed local
  terminal-publication authority.
- The original requirement is defect-derived from WI-5370, WI-5437, and
  TEST-11547; no separate owner tradeoff changed the narrow rule.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — legacy per-WI
  approval metadata is noncontrolling.

## Owner Decisions / Input

No owner input is required. Active project membership and list-free PAUTH v5
provide project approval. The five readiness dependencies remain visible but
grant no implementation authority and create no additional WI approval gate.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5437, TEST-11547, WI-5370 v003/v004, current clean target hashes, and v006 lifecycle correction",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; GOV-DOCUMENT-AUTHOR-PROVENANCE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "scripts.verdict_evidence_anchor_preflight.validate_verdict_evidence_anchors",
  "before_behavior": "a gated verdict can falsely assert that its operative report claims removal of an exact path and still pass evidence validation",
  "after_behavior": "the narrow exact-path assertion must be grounded in an unambiguous same-path removal statement in the operative report",
  "self_descriptive_naming": "unsupported_removal_claim names the mechanically provable evidence failure without implying general semantic inference",
  "obsolete_guidance_disposition": "no guidance is removed; the validator contract gains the narrow evidence rule",
  "history_preservation": "existing bridge files remain append-only; v003 and v005 are retained as invalid lifecycle evidence and v007 is the substantive recovery",
  "baseline": {
    "source_sha256": "A47FD9E95038E8271424DCEB3AFF7307B2B8BD22005394072CC42EEC9DF2099A",
    "test_sha256": "E7EC69825207DF25DC52882FCE7718CDD60744DF34367BB1FA098DDE8E113624"
  },
  "expected_result": {
    "wi5437_false_claim": "blocked",
    "legitimate_removal_reappearance": "allowed",
    "adapter_specific_changes": 0
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused two-target implementation commit without amending history",
    "test": "rerun the complete focused evidence-anchor suite"
  },
  "hard_invariants": [
    "no open-ended semantic classifier",
    "only the operative report and exact claimed path are evaluated",
    "all harnesses use the shared validator",
    "WI-5438 fixture regions remain untouched",
    "bridge history is not rewritten"
  ],
  "fail_closed_conditions": [
    "operative report is unreadable",
    "exact removal evidence is absent",
    "focused regression fails",
    "GO, claim, or implementation-start authority is absent"
  ],
  "essential_context_preservation": "existing WI-4520 anchor behavior, absence opt-outs, legitimate report-removal findings, review independence, readiness dependencies, and unrelated worktree bytes remain intact"
}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Unsupported exact removal claim | Execute the actual WI-5370 v003/v004 fixture pair | Named violation; exact claimed path and operative report identified. |
| Legitimate removal then reappearance | Report explicitly records removal; verdict records current path reappearance | Verdict evidence passes. |
| Exact-path binding | Mismatched path and unrelated-report fixtures | No false grounding from another path/report. |
| Narrow language boundary | Ambiguous prose, absence claim, unrelated semantic claim | Existing behavior preserved; no new violation. |
| Gated-status boundary | Non-gated status with identical prose | Rule does not apply. |
| WI-5438 isolation | New cases use distinct fixture regions; existing WI-5438 cases unchanged | No collision or fixture overwrite. |
| Shared mechanical enforcement | Existing writer/hook/provider/verification integration cases | Same validator result across consumers. |
| Nonimpairment | Full focused suite plus Ruff and exact diff inspection | No new false positive; only two target paths change. |

Required implementation-report commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_evidence_anchor_preflight.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/verdict_evidence_anchor_preflight.py platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/verdict_evidence_anchor_preflight.py platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
git diff --check -- scripts/verdict_evidence_anchor_preflight.py platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
```

## Acceptance Criteria

- The actual WI-5370 unsupported exact-path claim is rejected mechanically.
- A legitimate exact removal plus path-reappearance finding remains allowed.
- Ambiguous and unrelated semantic prose is not classified by this rule.
- Existing evidence-anchor behavior and WI-5438 fixture regions remain intact.
- All mapped tests, Ruff checks, and diff check pass with reported outcomes.
- Diff is confined to the two declared targets and introduces no configured
  timing/concurrency policy value.

## Risk, Rollback, And Readiness Boundary

The primary risk is false-positive blocking from overbroad language matching.
Exact gated phrase, exact path, and exact operative-report binding plus positive
and negative fixtures constrain the rule. The overlap risk is test-fixture
commingling; distinct regions and a clean pre-start rebaseline prevent it.

Rollback is a separately governed revert of only the two target diffs, followed
by the full focused suite. Readiness dependency evidence remains unchanged and
must still be satisfied before project release closure.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
