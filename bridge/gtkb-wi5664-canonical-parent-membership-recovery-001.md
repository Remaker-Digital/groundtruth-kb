NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: gpt-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled and untouched
author_metadata_source: explicit_interactive_session_metadata


bridge_kind: prime_proposal
Document: gtkb-wi5664-canonical-parent-membership-recovery
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project Authorization Version: 3
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["groundtruth.db"]
implementation_scope: metadata | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
git_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: none

# WI-5664 Canonical Parent Membership Recovery

## Proposal Claim

Repair the current project-membership postimage so it matches the owner's
explicit canonical-parent decision in `DELIB-202667733`. The live state is the
opposite of the decision: WI-5664 is an active member of
`GTKB-SKILL-RENAME-REFERENCE-SWEEP` and is absent from
`PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`. The owner selected Obsolete Reference
Purge as the unique canonical parent and directed the Skill-Rename membership
to be detached.

This proposal performs only an append-only, governed membership correction in
service-owned `groundtruth.db`. It does not edit the database directly, alter
the WI-5664 implementation targets, generate protected-artifact approval
packets, implement the skill-reference repair, or change Git, dispatcher,
TAFE, harness, credential, deployment, release, or external-system state.

## Requirement Sufficiency

Existing requirements and the recorded owner decision are sufficient. No new
formal requirement is needed. `DELIB-202667733` gives the exact desired parent
postimage; the active Skill-Rename project PAUTH v3 permits metadata and
governance-evidence mutations for active project members while preserving the
ordinary proposal, independent review, exact claim, implementation-start,
report, and independent verification lifecycle.

## Current Evidence

Fresh governed reads establish:

- `gt projects show PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE --json` contains no
  active WI-5664 membership.
- `gt projects show GTKB-SKILL-RENAME-REFERENCE-SWEEP --json` contains active
  membership `PWM-GTKB-SKILL-RENAME-REFERENCE-SWEEP-WI-5664`, version 1.
- The Skill-Rename project is active.
- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION`
  is active v3, list-free, and permits `metadata`, `governance_evidence`, and
  `bridge`; it forbids dispatcher mutation, external mutation, credentials,
  push, history rewrite, deployment, release, and destructive cleanup.
- Candidate preflight for the attempted main WI-5664 revision failed closed
  because the proposal named Obsolete Reference Purge while WI-5664 was not an
  active member. No main revision was filed and no implementation claim/start
  was acquired.

The current backlog narrative still describes the earlier dual-membership
state. It is stale descriptive text and is not used as project-membership
authority.

## Exact Proposed Transaction

After independent GO, acquire an exact claim and schema-v3 implementation-start
packet for this recovery thread. Re-read both project memberships and the owner
decision, then execute only these governed service operations in this order:

1. Append an active WI-5664 membership to
   `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` with a change reason citing
   `DELIB-202667733` and this recovery thread.
2. Read back that active membership. If it is absent, stop without detaching
   the current parent.
3. Append a non-active `removed` version for WI-5664's
   `GTKB-SKILL-RENAME-REFERENCE-SWEEP` membership with the same decision and
   recovery provenance.
4. Read back both projects and require exactly one active first-class
   membership for WI-5664: Obsolete Reference Purge active; Skill-Rename
   removed.
5. File a factual report containing pre/post membership identities, versions,
   command results, and a changed-row census for independent verification.

Canonical service command shapes are:

```text
gt projects add-item PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE WI-5664 --source "DELIB-202667733 canonical-parent recovery" --changed-by "prime-builder/codex/A" --change-reason "Restore the owner-selected WI-5664 canonical parent under DELIB-202667733; governed by gtkb-wi5664-canonical-parent-membership-recovery" --json

gt projects remove-item GTKB-SKILL-RENAME-REFERENCE-SWEEP WI-5664 --status removed --changed-by "prime-builder/codex/A" --change-reason "Detach the noncanonical WI-5664 Skill-Rename membership after successful Obsolete Reference Purge membership readback, per DELIB-202667733 and gtkb-wi5664-canonical-parent-membership-recovery" --json
```

If the first operation succeeds and the second fails, preserve both append-only
histories, report the temporary dual-parent state, and correct forward through a
new reviewed revision. Never reverse the first row by raw SQL or destructive
cleanup. A zero-active-parent intermediate is prohibited by ordering.

## Relationship To The Main Repair

This controller is a prerequisite only. The original
`gtkb-wi5664-rules-config-skill-reference-repair` thread remains latest
`NO-GO` and receives no v015 until this recovery is independently `VERIFIED`
and the corrected membership is current. The later main revision must still
rebase its exact paths, shared-target owners, protected-artifact packets,
current project PAUTH, tests, risks, and rollback. This proposal gives it no
source/configuration implementation authority.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667733` is the controlling owner decision: Obsolete Reference
  Purge is WI-5664's unique canonical parent and Skill-Rename is to be detached
  through the governed path.
- `DELIB-202667718` establishes the list-free Obsolete Reference Purge PAUTH
  that becomes applicable after membership recovery.
- `DELIB-202667193` establishes the Skill-Rename program scope and the active
  project PAUTH lineage used only to authorize this recovery while WI-5664 is
  still an active Skill-Rename member.
- `DELIB-20260801-WI5664-BACKLOG-APPROVAL` permits normal governed proposal
  consideration and does not itself authorize the main implementation.

## Owner Decisions / Input

No new owner decision is required. This proposal implements only the exact
membership consequence already authorized by `DELIB-202667733`, subject to a
fresh independent GO and all normal mutation gates. It does not broaden that
decision or infer approval for the main WI-5664 repair.

## Specification-Derived Verification Plan

| Obligation | Required evidence |
| --- | --- |
| Owner-selected postimage | Governed project reads show exactly one active WI-5664 first-class membership: Obsolete Reference Purge active and Skill-Rename removed. |
| Append-only history | Membership versions show an added/active Obsolete row and a later non-active Skill-Rename version; no history row is deleted or overwritten. |
| Operation-time authority | Candidate/live applicability and clause gates, active Skill-Rename PAUTH v3, exact claim, and schema-v3 start all pass immediately before mutation. |
| Row containment | Changed-row census contains only the two exact WI-5664 membership lineages and required transaction/audit metadata. |
| Main-repair non-activation | Original WI-5664 thread remains NO-GO; no narrative packet, source, test, config, rule, helper, or Git byte changes. |
| Nonimpairment | Dispatcher/TAFE state remains deliberately disabled and unchanged; no harness, credential, deployment, release, or external action occurs. |

## Acceptance Criteria

1. The owner-selected Obsolete Reference Purge membership exists and is active.
2. The Skill-Rename WI-5664 membership has a current non-active `removed`
   version.
3. WI-5664 has exactly one active first-class parent.
4. The exact two membership lineages and required audit metadata are the only
   changed service-owned rows.
5. The main repair remains unimplemented and latest NO-GO pending its own
   current revision and independent review.
6. No raw SQLite, source/test/config/rule/helper/packet, Git/index,
   dispatcher/TAFE, harness, credential, deployment, release, cleanup, or
   external mutation occurs.

## Risk And Rollback

The only material risk is a partial two-command outcome. Adding the intended
parent first prevents a zero-parent state. After any partial append, rollback
is forward-only through the governed project service and a newly reviewed
bridge revision; membership history is never deleted. Currentness drift,
unexpected active memberships, a different owner decision, claim collision,
or PAUTH denial stops before mutation.

## Files Expected To Change

- `groundtruth.db`, only through the two exact governed membership lineages
  and their audit metadata.

No Git commit is requested or authorized.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
