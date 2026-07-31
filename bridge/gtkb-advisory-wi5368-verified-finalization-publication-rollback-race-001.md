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
Document: gtkb-advisory-wi5368-verified-finalization-publication-rollback-race
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5742
Primary Existing Carrier: WI-5742
Related Existing Carriers: WI-5791, WI-5788, WI-5765
Source Thread: gtkb-wi5368-codex-git-window-command-family
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report — WI5368 VERIFIED finalization published before commit, then entered a cross-process rollback race

## Summary

A read-only Prime Builder audit found that WI5368 version 018 was physically
created and canonically consumed as `VERIFIED` without the required
same-transaction Git commit. The file later disappeared while its publication
capability remained `recovery_required`, the physical numbered chain fell back
to version 017 `NEW`, and a concurrent bridge publication failed while scanning
the disappearing aggregate member.

This is not Prime Builder processing of a `VERIFIED` item. `VERIFIED` is
non-actionable for Prime Builder. This report preserves a terminal-finalization
and bridge-publication concurrency incident for independent review.

The incident couples defect classes already carried by WI-5742
(publish-before-commit finalization and resumable cleanup), WI-5791
(cross-process aggregate-generation and rollback races), WI-5788 (append-only
access cost), and WI-5765 (atomicity regression coverage). No duplicate work
item is recommended.

## Claim

The current finalizer can publish and consume terminal `VERIFIED` before the
required backing commit exists. If the later commit phase fails, rollback can
become impossible after legitimate sibling bridge publications advance the
glob-backed aggregate. Cleanup can then split Git, physical lifecycle, registry
lifecycle, sidecar, and claim state and can impair unrelated publication.

## Exact Evidence

### Physical version 018

Earlier in the same read-only audit,
`bridge/gtkb-wi5368-codex-git-window-command-family-018.md` existed as a
5,524-byte `VERIFIED` file created at `2026-07-30T16:36:04Z` with raw SHA-256
`268c7a641e624114a60ef4d05d104c68a391c50239df066d9672c72d15e31dfe`
and Git blob ID `d8f4d769c48d69eca5370aad5aeacbc0e04e02e9`.

It declared a 19-path same-transaction cohort: numbered bridge versions
002–018, `scripts/ops/codex_snapshot_window_hider.py`, and
`platform_tests/scripts/test_codex_snapshot_window_hider.py`.

During the audit, version 018 disappeared. Strict physical resolution then
reported version 017 `NEW` as current. Prime Builder did not recreate, delete,
or process the terminal verdict.

### Git state

`HEAD` remained `8a35eabc8cae297cbd295223d6ec904aa15212b8`.
`git log --all -- bridge/gtkb-wi5368-codex-git-window-command-family-018.md`
found no commit, and `git ls-files --error-unmatch` rejected version 018. The
declared source and test postimages remained unstaged modifications; numbered
versions 007–017 remained untracked. No reachable commit contains the declared
verified cohort.

### Registry publication

Capability row464 exactly binds version 018:

- capability hash:
  `sha256:04d5270888e7f4c8736e4fcdc13e39ae045ef61046bef6e391d116d6dec76a2e`;
- created: `2026-07-30T16:35:46Z`;
- consumed: `2026-07-30T16:36:57Z`;
- mint-to-consume: 71 seconds;
- initial revision: `SOTREV-8F609305CA5C469E82989B5D766A59A5`;
- current state: `recovery_required`;
- compensation revision: null; and
- failure: `bridge publication rollback cannot restore its exact aggregate preimage`.

The protected-commit checker now rejects the exact path because the
publication capability is not consumed in its current state. The row preserves
evidence that canonical consumption occurred but is not a valid terminal commit
receipt.

### Coupled unrelated publication failure

While this audit was in progress, governed publication of
`bridge/gtkb-advisory-wi5368-cross-thread-target-collision-003.md` minted row480.
The writer enumerated version 018, then raised `FileNotFoundError` when another
session removed that member before `lstat`. Compensation could not restore the
preimage and left row480 `recovery_required` with its exact target, sidecar, and
claim retained.

This proves the race class and cross-thread impact. The retained records do not
identify the deleting process, so this report does not guess the actor.

## Findings

### F1 — P0: terminal publication preceded its backing commit

The terminal file and registry capability became visible and consumed before a
reachable commit existed. This violates the Mandatory VERIFIED
Commit-Finalization Gate. WI-5742 is the primary carrier.

### F2 — P0: cleanup could not compensate after concurrent aggregate growth

Once sibling publications changed the append-only aggregate, rollback could no
longer prove restoration of the original preimage. WI-5791 owns the required
cross-process exact-generation contract.

### F3 — P1: lifecycle authorities diverged

Git has no version 018; the physical chain ends at version 017 `NEW`; the
registry retains consumed-then-recovery-required version 018 evidence. A
consumer reading only one surface can report a false terminal state.

### F4 — P1: the initiating commit failure was overwritten by cleanup evidence

The current failure reason records rollback failure, not the Git error that
initiated rollback. Corrective journaling must retain the primary error and all
secondary cleanup/currentness failures in order.

### F5 — P2: append-only access cost widened the race window

Row464 took 71 seconds from mint to consume, and contemporary governed
publications took roughly 45 seconds mint-to-consume and 76–86 seconds
end-to-end. Append-only history remains valuable and should not be deleted or
rewritten, but repeated full-aggregate hot-path scans widen lock convoys and
overlap windows. WI-5788 owns this evidence.

## Recommended Carrier Disposition

1. Keep WI-5742 as the primary finalizer-ordering and resumable-transaction
   carrier; it now contains this exact recurrence.
2. Keep WI-5791 as the cross-process aggregate-generation and
   `recovery_required` adoption carrier.
3. Keep WI-5788 as the access-cost, fairness, progress, and incremental
   currentness carrier.
4. Keep WI-5765 as the deterministic terminal-atomicity regression lane.
5. Create no new work item and do not recreate version 018.

## Corrective Acceptance And Verification Mapping

| Acceptance condition | Required deterministic verification |
| --- | --- |
| No observer can see or consume terminal `VERIFIED` before a reachable commit contains the verdict and declared cohort. | Barrier test pauses before commit and proves physical and registry lifecycle remain nonterminal. |
| Commit failure leaves no consumed terminal publication, or one exact resumable transaction. | Inject commit failure; retry converges without a new numbered verdict, manual staging, or owner repair. |
| Sibling publication cannot make cleanup delete, lose, or misattribute any generation. | Interleave commit failure, sibling append, rollback, and retry; assert exact bytes and ownership. |
| Git, physical frontier, capability, aggregate revision, sidecar, and claim converge. | Assert all six surfaces after success, commit failure, process death, cleanup failure, and retry. |
| Primary and secondary failures remain durably ordered. | Inject distinct Git and cleanup errors and prove neither overwrites the other. |
| Recovery resumes the same exact version. | Retry interrupted version 018 and prove no version 019 is synthesized. |
| Safety remains bounded as history grows. | Report mint/create/consume/commit/cleanup timings at representative aggregate sizes and return typed contention/failure. |
| Repair has no dispatcher/TAFE dependency. | Direct API tests assert no dispatcher or TAFE side effects. |

Future corrective implementation should run at minimum:

- `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q`
- `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q`
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q`
- `python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q`

## Clause Applicability

| Clause family | Applicability | Evidence |
| --- | --- | --- |
| Bridge role and transition authority | applicable | Prime Builder authors targetless `NEW` Advisory evidence and does not author or process a `VERIFIED` verdict. |
| Mandatory VERIFIED commit finalization | applicable to the incident | Physical/registry terminal publication occurred without the required reachable commit; corrective acceptance is mapped above. |
| Specification-derived testing | applicable to future correction | Exact deterministic commands and acceptance mappings are preserved; this Advisory claims no VERIFIED result. |
| Project authorization and implementation start | not triggered by this filing | Existing carriers are project-linked; this targetless Advisory grants no implementation authority. |
| Protected mutation and Git/release controls | not triggered | `target_paths` is empty; no source, Git, release, deployment, credential, dispatcher, or TAFE mutation is performed. |
| Application isolation | not triggered | All evidence is in-root GT-KB platform state; no adopter application is changed. |

## Specification-Derived Verification

| Specification | Command evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | strict physical resolver plus exact numbered-file inspection | Current physical thread ends at v017 NEW; PB does not process missing v018 VERIFIED. |
| Mandatory VERIFIED Commit-Finalization Gate | `git log --all`, `git ls-files --error-unmatch`, HEAD and cohort inspection | No reachable commit or tracked v018 exists despite prior terminal publication. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | read-only capability/revision inspection for rows464 and480 | Both incidents retain exact evidence in `recovery_required`; cross-thread aggregate race is concrete. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5742`, `WI-5791`, `WI-5788`, `WI-5765` | Existing project-linked carriers cover every derived correction; no duplicate is required. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --content-file <candidate> --json` | Candidate must pass before publication. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --content-file <candidate>` | Mandatory clause gate must pass; this Advisory does not claim VERIFIED. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Decision And Requirement Sufficiency

`DELIB-202667533` selects commit-before-terminal ordering and atomicity-test
restoration. Existing bridge, registry, project-authorization, and deterministic
service requirements are sufficient. This Advisory adds incident evidence and
carrier routing; it does not select implementation mechanics.

## Owner Decision

No new owner decision is required to preserve this Advisory or route its
findings to existing carriers. Any later target-bearing implementation still
requires one active parent project, a current whole-project PAUTH covering the
operation classes, proposal, independent GO, exact claim, and schema-v3 start.

## Non-Approval And Mutation Boundary

This Advisory authorizes no source, test, script, hook, configuration,
formal-artifact, project, PAUTH, MemBase, database, implementation-start, Git
index, commit, push, cleanup, credential, deployment, release, dispatcher, or
TAFE mutation. The dispatcher and TAFE remain deliberately disabled and
untouched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
