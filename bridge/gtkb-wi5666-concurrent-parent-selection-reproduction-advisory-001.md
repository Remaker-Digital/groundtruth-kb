NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: governance_review
Document: gtkb-wi5666-concurrent-parent-selection-reproduction-advisory
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5762
Related Work Items: WI-5662, WI-5663, WI-5664, WI-5665, WI-5666, WI-5667, WI-5668
Source Thread: gtkb-wi5666-terminal-evidence-finalization-recovery
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report — concurrent WI5666 revision selected one of two active parents while owner choice was pending

## Summary

During a read-only audit of the WI5666 v008 `NO-GO`, a different Prime Builder
session appended v009 `REVISED` and selected
`PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` as the governing parent. Every work item
from WI-5662 through WI-5668 is simultaneously an active member of that project
and `GTKB-SKILL-RENAME-REFERENCE-SWEEP`, and no owner decision selecting one
canonical parent for the seven-item cohort was found.

Candidate applicability and operation-time authorization nevertheless passed
for the selected project. This is a live reproduction of WI-5762's finding that
an implementing agent can choose which owner grant governs its own work when
multiple active project authorities overlap.

The v009 file is now strict latest `REVISED` and therefore Loyal-Opposition
work. This Prime Builder will not review, receipt, quarantine, replace, or
implement it. This targetless Advisory preserves the race and routes it to
existing WI-5762 without creating a duplicate work item.

## Claim

The project-only authorization model requires each work item to inherit
implementation authority from its parent project, but current membership and
operation-time evaluation do not enforce a unique active parent. When one WI
has two active project memberships with valid PAUTHs, a Prime proposal can cite
either project and receive `allowed=true` without proving the owner selected
that project as canonical.

Concurrent version allocation compounds the issue: another session can consume
the next Prime-authored version slot and materialize its own parent selection
while the current session is waiting for owner direction.

## Exact Evidence

### Prior v008 state

- Path:
  `bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-008.md`
- Status: `NO-GO`
- SHA-256:
  `78f02a4295f6bde906f07ae8bba8a8628fb97744f312be4981dff30c569ef49b`
- Review is independent and role-correct, but it lacks mandatory Clause
  Applicability and Prior Deliberations sections and contains stale PAUTH facts.

### Concurrent v009 state

- Path:
  `bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-009.md`
- Status: `REVISED`
- Created/last written: `2026-07-30T17:40:53.6867202Z`
- SHA-256:
  `6468ec1142ed19edd5ef52610a72c76183ce3daafd1d36e4a1c31e5968e2b1d7`
- Author session:
  `019fb1f2-2f91-7b82-ac15-acdd56e13d1e`
- Current Git state at audit: untracked
- Selected project:
  `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`
- Selected PAUTH:
  `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730`
  v2
- Declared targets:
  `platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py`
  and future bridge report v011; neither target existed at audit time.

The v009 proposal states that no owner decision is required. That claim does
not resolve the concurrent active Skill Rename membership or establish one
canonical parent for the cohort.

### Dual-membership state

Every WI from WI-5662 through WI-5668 has active membership v1 in both:

1. `GTKB-SKILL-RENAME-REFERENCE-SWEEP`; and
2. `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`.

The Obsolete Reference Purge project has active list-free PAUTH v2, row950,
under `DELIB-202667718`. Skill Rename has active PAUTH v2, row948, under
`DELIB-202667715`, but retains an explicit WI-5662–WI-5668 list inconsistent
with the owner's newer project-only authorization direction.

No canonical-parent decision for the full seven-WI cohort was found.

### Mechanical authorization result

The v009 candidate applicability packet passed with packet hash
`sha256:bef2d3b855be01584d25aa5b2ea728a9bab4efe6f551eef71242e67e139bf7b9`.
Operation-time evaluation returned `allowed=true` for the selected Obsolete
Reference Purge project/PAUTH even though the duplicate active membership
remained. Post-appearance claim status was null; that observation does not prove
that no claim existed earlier.

## Risk And Impact

- Owner parent-selection intent can be bypassed by whichever project a proposal
  cites first.
- Two sessions can produce individually valid-looking proposal/GO/start
  evidence under different project authorities for the same work item.
- Project ordering, completion, dependency, retirement, and reporting can
  disagree because both projects consider the WI active.
- An operation-time `allowed=true` result can be mistaken for proof of unique
  authority when it proves only that the selected grant is sufficient.
- Concurrent Prime writers can consume version slots and harden an unresolved
  authority choice into the physical chain.
- Append-only history preserves the evidence but does not provide semantic
  uniqueness by itself.

## Existing Carrier And Non-Duplication

WI-5762 already owns project-authorization accumulation and the defect class in
which an agent selects its own governing grant. The live v009 event is a
concrete regression/acceptance case for that carrier, not a new work item.

WI-5762's approved v001 scope excludes membership-wide authorizations from
multi-coverage math under OD-C. That exclusion is now stale under the owner's
project-only model and this seven-WI reproduction. The current GO v002 must not
be implemented unchanged; a later REVISED proposal must include unique-parent
or multi-membership conflict detection for membership-inherited authority.

Resolved WI-4823 is related precedent for concurrent Prime same-slice ownership
and provenance. It should be reopened or a separate carrier created only if an
independent investigation proves a distinct claim/lease failure beyond the
already-carried authorization-accumulation defect.

## Recommended Action

1. Loyal Opposition should review WI5666 v009 at v010 and return `NO-GO` unless
   the owner has selected the canonical parent and duplicate membership has
   been append-only retired.
2. The v010 review must include complete candidate Applicability, mandatory
   Clause Applicability, and Prior Deliberations evidence.
3. The owner should later select one canonical parent for WI-5662–WI-5668; the
   noncanonical memberships should be retired through governed append-only
   successor records rather than deletion.
4. WI-5762 should be revised so project-membership-derived authorization enters
   its multi-coverage/conflict detection and doctor tests.
5. Proposal/start evaluation should fail closed when one WI has more than one
   active parent unless an explicit governed multi-parent exception exists.
6. Version-slot ownership should be protected by the exact claim/session
   contract so a concurrent writer cannot silently materialize a pending owner
   choice.
7. No dispatcher or TAFE behavior should be introduced.

## Corrective Acceptance And Verification Mapping

| Acceptance condition | Required deterministic verification |
| --- | --- |
| One normal WI has exactly one active parent at implementation start. | Create two active memberships and assert proposal/start fails with both project IDs until one is retired. |
| The evaluator cannot treat selected-grant sufficiency as unique authority. | Cite either PAUTH in the dual-parent fixture; both attempts return a typed multi-parent conflict. |
| Project-only PAUTHs participate in accumulation/conflict math. | Doctor test includes membership-inherited list-free PAUTHs and reports the seven-WI pattern. |
| Owner selection is durable and append-only. | Retire the noncanonical membership by successor row; history remains queryable and current projection has one parent. |
| Concurrent proposal writers cannot consume a pending authority choice. | Barrier test with two Prime sessions and one WI; only the exact claimed canonical-parent proposal may publish. |
| No dispatcher/TAFE dependency is introduced. | Direct project/bridge tests assert no dispatcher or TAFE side effects. |

## Clause Applicability

| Clause family | Applicability | Evidence |
| --- | --- | --- |
| Bridge role and transition authority | applicable | Prime Builder authors targetless `NEW` Advisory and does not author the LO v010 verdict or process v009 `REVISED`. |
| Project authorization and unique membership | applicable | Two active parents and valid grants exist; evaluator allowed the arbitrarily selected parent. |
| Specification-derived testing | applicable to the future WI5762 correction | Deterministic unique-parent and concurrency cases are mapped above; this report claims no implementation or VERIFIED result. |
| Protected mutation and Git/release controls | not triggered | `target_paths` is empty and no source, membership, PAUTH, Git, release, dispatcher, or TAFE mutation occurs. |
| Application isolation | not triggered | All evidence is in-root GT-KB platform state. |

## Specification-Derived Verification

| Specification | Command evidence | Observed result |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | read-only current membership and PAUTH inspection | Seven WIs have two active project authority paths; no canonical parent is recorded. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | v009 candidate applicability packet | Selected project returned `allowed=true` despite duplicate active parent membership. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | strict physical resolver plus v008/v009 hashes/session metadata | V009 is current PB `REVISED`; this session does not review or implement it. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5762` | Existing carrier owns governing-grant accumulation; no duplicate WI is required. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --content-file <candidate> --json` | Advisory candidate must pass before publication. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --content-file <candidate>` | Mandatory clause gate must pass; this Advisory does not claim VERIFIED. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — implementation
  authority is inherited from the parent project and orphan WIs cannot
  implement.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — legacy per-WI
  approval state is noncontrolling.
- `DELIB-202667715` — Skill Rename PAUTH v2.
- `DELIB-202667718` — Obsolete Reference Purge list-free PAUTH v2.
- `DELIB-202667531` and `DELIB-202667532` — Advisory Corrections capture and
  authorization-deconfliction direction.

## Owner Decision

The seven-WI canonical-parent choice remains necessary before the WI5666 lane
can become executable. It is not requested inside this report because owner
input must be asked one decision at a time and the newer WI5800 project-PAUTH
decision is already pending. No parent choice is inferred here.

## Non-Approval

This Advisory authorizes no implementation, protected mutation, membership or
PAUTH change, bridge GO/NO-GO, claim, implementation start, Git action,
terminal verdict, release, deployment, dispatcher/TAFE action, or external
system mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
