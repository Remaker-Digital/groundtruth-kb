REVISED

# WI-5321: Revised executable repair for WI-5299 failed VERIFIED finalization

bridge_kind: prime_proposal
Document: gtkb-wi5321-wi5299-failed-verified-finalization-repair
Version: 005
Responds to: bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-004.md

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5299-VERIFIED-FINALIZATION-20260715
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5321

target_paths: ["bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md", "independent-progress-assessments/WI-5321-wi5299-verdict-004.failed-finalizer.md"]

implementation_scope: governance_evidence | bridge failed-transaction rollback
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision preserves the version-001 repair design and addresses the sole
version-004 NO-GO finding by making the cited project authorization executable.
The active PAUTH is now version 3, rowid 777, with the same owner decision,
same two-path scope, same allowed mutation classes, same included work items,
and same included specs as the rejected version, but with only registered
forbidden-operation tokens:

- `credential_lifecycle`
- `destructive_cleanup`
- `dispatcher_mutation`
- `external_system_mutation`
- `git_history_rewrite`
- `git_push`
- `production_deployment`
- `release`

The repair still does not authorize committing the file-only WI-5299 verdict,
broad staging, history rewrite, dispatcher mutation, direct harness contact,
push, release, deployment, credential action, or unrelated dirty capture.

## Requirement Sufficiency

Existing requirements sufficient. The original WI-5321 proposal already cited
the requirements that govern failed VERIFIED finalization recovery. This
revision only corrects the PAUTH envelope so those requirements can be executed
through the normal claim, implementation-start, implementation report, and
independent verification gates.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666332` - owner authorizes exact local finalization of
  independently VERIFIED scopes to reach a clean worktree while forbidding
  broad or unrelated capture.
- `DELIB-202666274` - project implementation authority preserves bridge,
  implementation-start, independent verification, and mechanical gates.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-001.md` -
  original failed-finalizer repair proposal.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-004.md` -
  NO-GO finding requiring a PAUTH with registered operation vocabulary.
- `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-001.md` through
  `-004.md` - original WI-5299 proposal, GO, implementation report, and
  failed file-only verdict transaction.

## Owner Decisions / Input

No new owner decision is required for this revision. It relies on
`DELIB-202666332`, the existing owner decision already recorded on the active
PAUTH and WI-5321 backlog item. The PAUTH reissue did not broaden scope or
remove owner restrictions; it only replaced the non-registered operation values
that caused the operation-time evaluator to fail closed.

## Findings Addressed

### F1 (P0, blocking) - Unexecutable Project Authorization

Resolved for proposal review. The rejected PAUTH version 2 included three
unregistered forbidden-operation values:

- `direct_harness_to_harness_invocation`
- `broad_bulk_status_mutation`
- `committing_unrelated_dirty_files`

The active PAUTH version 3 removes those values and retains only operations
registered by `config/governance/project-authorization-operation-taxonomy.toml`.
Fresh `gt projects show-authorization` output reports `_forbidden_operations_parsed`
as the eight registered tokens listed in the Revision Claim section. A
subsequent no-write implementation-start probe no longer reported
`unknown_forbidden_operation`; it failed before implementation for the expected
reason that no implementation work-intent claim was active for a latest-`GO`
thread.

## Scope Changes

No implementation scope expansion. The executable repair remains exactly the
two-path failed-transaction rollback from version 001:

1. Preserve the exact untracked WI-5299 version 004 bytes at
   `independent-progress-assessments/WI-5321-wi5299-verdict-004.failed-finalizer.md`.
2. Remove only `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`
   after hash/byte identity is proven and after a GO, claim, and
   implementation-start packet authorize the repair.

The later WI-5299 verdict reissue remains separate Loyal Opposition work and
must use `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`.

## Pre-Filing Preflight Subsection

Prime Builder will file this completed revision through
`.codex/skills/bridge/helpers/revise_bridge.py file`, which performs the
candidate-content bridge applicability preflight and ADR/DCL clause preflight
before publishing live bridge state. The proposal cites every required and
advisory specification surfaced by the original WI-5321 thread plus the PAUTH
envelope specifications implicated by the version-004 NO-GO.

## Specification-Derived Verification Plan

| Specification | Required executed evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Before removal, prove the failed verdict is untracked, file-only, and missing finalization evidence; after removal, prove the WI-5299 chain resolves back to report 003 without changing versions 001-003. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Preserve the failed independent verdict body byte-for-byte and require any reissued 004 to add helper-generated finalization evidence without changing its substantive findings. |
| `GOV-WORK-TREE-HYGIENE-001` | Show `git status --short --` on the exact WI-5321 and WI-5299 target paths before and after the repair; no broad staging or unrelated capture is permitted. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Acquire a matching WI-5321 work-intent claim and implementation-start packet after any future GO; cite active PAUTH version 3. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Show the active PAUTH forbidden-operation list contains only registered operation tokens and that the implementation-start gate no longer fails for `unknown_forbidden_operation`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify the PAUTH keeps the same project, owner decision, included work items, allowed classes, included specs, and exact scope summary. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm PAUTH version 3 does not start implementation by itself; work remains blocked until LO records GO and Prime obtains the start packet. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This revision carries the project authorization, project, work item, and target_paths metadata in machine-readable header lines. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and clause preflights on this completed content pass before filing; Loyal Opposition independently re-runs them before GO. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The durable archive and implementation report preserve why the failed verdict was removed and how to reconstruct it exactly. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5321 is not complete until its repair is VERIFIED and the original WI-5299 004 is reissued through the atomic finalizer. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5321, the archive, report, and corrected finalization preserve the incident as governed evidence. |

## Acceptance Criteria

1. PAUTH version 3 remains active and contains no unregistered
   forbidden-operation values.
2. Loyal Opposition GO, if granted, applies only to the two declared target
   paths and the failed-transaction rollback procedure.
3. Implementation does not delete or alter any committed bridge history.
4. The failed WI-5299 004 bytes are preserved in the declared archive before
   the untracked bridge copy is removed.
5. The original WI-5299 thread becomes LO-actionable at report 003 `NEW`, and
   its replacement 004 can only be created by the atomic VERIFIED finalizer.

## Risk And Rollback

The main risk is mistaking PAUTH repair for implementation approval. This
revision keeps those separate: PAUTH version 3 only makes the future GO/start
path executable. If this revision is rejected, no WI-5299 bridge file has been
removed and the failed 004 verdict remains available at its original path. The
PAUTH reissue can be superseded by another `gt projects authorize` version with
the same owner decision and narrower registered vocabulary if Loyal Opposition
requires a different operation envelope.

## Recommended Commit Type

`chore:` - this remains governance-evidence recovery and atomic-finalization
repair.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
