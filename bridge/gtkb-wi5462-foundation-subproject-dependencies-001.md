NEW
::init gtkb lo
::open build

# WI-5462 - Enforce foundation-first black-box child-project ordering

bridge_kind: prime_proposal
Document: gtkb-wi5462-foundation-subproject-dependencies
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-07-17T19:35:21Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5462-FOUNDATION-SUBPROJECT-DEPENDENCIES-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5462

target_paths: ["groundtruth.db", "platform_tests/groundtruth_kb/test_project_dependency_ordering.py"]

implementation_scope: metadata | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Make the owner-selected foundation-first sequence mechanically authoritative by
adding eight `requires_project_state` dependency edges. Each downstream
black-box child project will depend on the common foundation child project at
the `authorization` gate, with required prerequisite state `completed`.

The eight downstream authorizations already active in MemBase are scoped to the
parent project. Operation-time PAUTH validation does not re-evaluate the
downstream child project's dependency readiness, so adding child-project edges
without addressing those authorizations would leave a bypass. After all eight
edges are added, read back, and the complete project graph validates, revoke
exactly those eight premature parent-project PAUTHs. Replacement child-scoped
PAUTHs may be created only after the foundation project reaches `completed`;
their creation and all downstream implementation are outside this proposal.

This proposal does not complete the foundation, correct WI-5268's false-terminal
backlog record, create replacement downstream authority, mutate dispatcher/TAFE
runtime or configuration, edit platform source, or write the database directly.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - makes versioned MemBase project
  dependency records the sole dependency authority and defines directional,
  gate-specific, non-authorizing dependency semantics.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires implementation authority
  to remain bounded to the authorized project and mutation envelope.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs creation and
  revocation of the eight affected project authorization records.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` - requires the WI-5462
  carrier to remain restrictive and prevents it from authorizing WI-5269
  through WI-5276 implementation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent `GO`, an exact work
  intent, and the governed bridge lifecycle before protected test or metadata
  implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this
  proposal to cite the canonical requirements that derive its scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires machine-readable
  project, PAUTH, and work-item linkage plus a MemBase project artifact link.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  verification to derive evidence from these linked specifications.
- `GOV-12` - requires WI-5462 to retain its linked test, `TEST-11568`.
- `GOV-13` - requires `TEST-11568` to remain assigned to its governed test-plan
  phase.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the discovered ordering and
  authority defects to be preserved as governed records, not bridge prose alone.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires implementation and
  verification evidence to remain attached to durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs the proposal, implementation,
  report, verification, and terminalization transitions.
- `GOV-STANDING-BACKLOG-001` - keeps WI-5462 open until the implementation is
  independently verified and finalized.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all work and evidence inside
  the GT-KB project root and away from adopter/application authority.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` - Mike selected a
  formal specification foundation before any downstream source, prompt, hook,
  or CLI implementation and required downstream child work to depend on it.
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL` -
  approved the MemBase project-dependency model and its governed CLI authority.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded
  proposal carriers for defects discovered while stabilizing the
  bridge/TAFE/harness complex while preserving all later implementation gates.

## Owner Decisions / Input

Mike selected foundation-first ordering in
`DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` and directed Prime
Builder to complete the full black-box program to verified closure. That
decision authorizes this bounded proposal and its restrictive PAUTH; it does not
waive independent review, implementation-start, verification, or finalization.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-PROJECT-DEPENDENCY-ORDERING-001`
defines the dependency record, direction, supported `completed` prerequisite
state, `authorization` affected gate, fail-closed graph validation, recovery,
and non-authorizing semantics. The owner deliberation defines the exact
foundation-first sequence. No proposed black-box DCL or ADR is treated as
canonical authority until WI-5268 successfully formalizes it.

## Current-State Evidence

- Foundation project
  `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-FOUNDATION`
  is `active` and contains WI-5268.
- WI-5268 backlog metadata is currently `resolved`, but the latest canonical
  bridge state is `NO-GO` at
  `bridge/gtkb-dispatcher-black-box-spec-foundation-020.md`. This proposal does
  not treat that false-terminal backlog row as foundation completion.
- All eight downstream child projects are `active` and currently have no
  project dependencies or child-scoped authorizations.
- The parent black-box project has eight active PAUTHs for WI-5269 through
  WI-5276. Those records are the exact revocation set below.
- WI-5156's dependency-ordering CLI proposal is latest `REVISED`; it must reach
  a terminal implementation disposition before this transaction.
- Global `gt projects dependencies validate --json` currently fails because one
  unrelated active edge has a retired dependent endpoint. WI-5482 owns that
  reconciliation and must be terminal before this transaction.
- `TEST-11568` exists and maps to
  `platform_tests/groundtruth_kb/test_project_dependency_ordering.py`; that test
  file does not yet exist.

## Exact Child-Project Edges

Every edge uses:

- prerequisite project:
  `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-FOUNDATION`
- kind: `requires_project_state`
- required state: `completed`
- affected gate: `authorization`
- provenance:
  `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST; WI-5462; TEST-11568; bridge/gtkb-wi5462-foundation-subproject-dependencies-001.md`

| Related WI | Dependent child project |
|---|---|
| `WI-5269` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-ACTIVITY-ENVELOPE-AUTHORITY` |
| `WI-5270` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-WORKER-PACKET` |
| `WI-5271` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-MEDIATED-BRIDGE-VIEW` |
| `WI-5272` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-PROMPT-SKILL-CONTRACT` |
| `WI-5273` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-CLI-SURFACE-SPLIT` |
| `WI-5274` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-CAPABILITY-AUDIT` |
| `WI-5275` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-GATE-ENFORCEMENT` |
| `WI-5276` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-CLOSURE-VERIFICATION` |

The implementation report must record each generated dependency ID and its
matching related WI. No other project dependency may be created, recovered,
retired, or revised.

## Exact PAUTH Revocation Set

After all eight edges exist and the global graph validates, revoke exactly:

- `PAUTH-DISPATCHER-BLACK-BOX-WI5269-ACTIVITY-ENVELOPE-AUTHORITY-20260717`
- `PAUTH-DISPATCHER-BLACK-BOX-WI5270-WORKER-CONTEXT-PACKET-20260717`
- `PAUTH-DISPATCHER-BLACK-BOX-WI5271-MEDIATED-BRIDGE-VIEWS-20260717`
- `PAUTH-DISPATCHER-BLACK-BOX-WI5272-ORDINARY-WORKER-PROMPT-SKILL-CONTRACT-20260717`
- `PAUTH-DISPATCHER-BLACK-BOX-WI5273-WORKER-OPERATOR-CLI-SPLIT-20260717`
- `PAUTH-DISPATCHER-BLACK-BOX-WI5274-CAPABILITY-ISSUANCE-AUDIT-20260717`
- `PAUTH-DISPATCHER-BLACK-BOX-WI5275-ENFORCEMENT-PARITY-GATES-20260717`
- `PAUTH-DISPATCHER-BLACK-BOX-WI5276-CLOSURE-SCANNER-GATE-20260717`

Authorization history must remain append-only. No unrelated PAUTH may change,
and no child-scoped replacement PAUTH may be created in this implementation.

## Implementation Sequence

1. Confirm WI-5156 is terminal and its dependency CLI behavior remains
   available through the installed `gt` entry point.
2. Confirm WI-5482 is terminal and
   `gt projects dependencies validate --json` reports `valid: true`.
3. Confirm no WI-5269 through WI-5276 work-intent claim or implementation-start
   packet is active.
4. Acquire an exact WI-5462 work-intent claim and schema-v3
   implementation-start packet for the two declared target paths.
5. Add `platform_tests/groundtruth_kb/test_project_dependency_ordering.py`.
   Its isolated temporary database must create the exact nine project IDs and
   prove all eight edge semantics, blocking before foundation completion,
   satisfaction after completion, and `grants_implementation_authority: false`.
6. Run the focused `TEST-11568` test before production metadata mutation.
7. Capture the current project, dependency, and eight-PAUTH baselines through
   governed CLI reads.
8. Add and read back all eight edges through
   `gt projects dependencies add|show|list|validate`. If any edge addition or
   validation fails, retire only the newly added WI-5462 edges and stop before
   revoking any PAUTH.
9. After all eight edges are present and the graph is valid, revoke the exact
   eight PAUTHs through `gt projects revoke-authorization`. If any revocation
   fails, preserve the fail-closed state and file a governed reconciliation
   rather than issuing or using downstream implementation authority.
10. Rerun the focused test and all CLI postconditions, then file the
    implementation report for independent verification.

No step may use direct SQL, `KnowledgeDB` mutation, dispatcher/TAFE internals,
configuration mutation, or an ungoverned helper path.

## Related Work Items

- `WI-5156` - hard predecessor providing and finalizing the governed
  project-dependency CLI.
- `WI-5482` - hard predecessor restoring a globally valid dependency graph.
- `WI-5268` - foundation work item whose child project must later become
  `completed`; it is not implemented or terminalized here.
- `WI-5269` through `WI-5276` - downstream work items whose premature
  parent-scoped PAUTHs are revoked here; replacement child-scoped PAUTHs and
  implementation require later governed proposals after foundation completion.
- `WI-5467` and `WI-5470` - closure-tool defects remain independently governed
  and receive no authority from this proposal.

## Specification-Derived Verification Plan

| Requirement | Verification evidence | Required result |
|---|---|---|
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Capture `gt projects authorizations <parent> --json` before mutation. | Exactly the eight named parent-scoped PAUTHs are active for WI-5269 through WI-5276; no alternate downstream PAUTH is silently substituted. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` predecessor integrity | Run `gt projects dependencies validate --json` after WI-5482 and before WI-5462 mutation. | `valid: true`, with no endpoint, cycle, self-edge, duplicate-semantic-edge, or contradictory-state error. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` exact direction | Read each generated dependency through `gt projects dependencies show <id> --json` and list by dependent/prerequisite project. | Exactly eight active edges point from the named downstream children to the common foundation prerequisite, with kind `requires_project_state`, required state `completed`, affected gate `authorization`, matching related WI, and exact provenance. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` global validity | Rerun `gt projects dependencies validate --json`. | `valid: true`; active dependency count increases by exactly eight; no unrelated edge changes. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` pre-foundation readiness | Read all eight child project dependency readiness records while foundation is `active`. | Every edge reports current prerequisite state `active`, required state `completed`, `satisfied: false`, `blocked_gate: authorization`, and `grants_implementation_authority: false`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` premature authority removal | Read all eight exact PAUTH IDs plus unrelated authorization baseline after revocation. | Latest status is `revoked` for exactly the eight named PAUTHs; no unrelated authorization changes; no replacement child PAUTH exists. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` fail-closed use | Run applicability/start validation against the existing WI-5269 through WI-5276 proposal/PAUTH pairs without claiming or starting them. | Each fails closed because its named PAUTH is revoked; no work intent or implementation-start record is created. |
| `GOV-12`, `GOV-13`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_project_dependency_ordering.py -q --no-header`. | `TEST-11568` passes and remains linked to WI-5462 and its valid test-plan phase. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` completion semantics | In the isolated test database only, advance the foundation project to `completed` and re-read all eight edges. | Every edge becomes satisfied and unblocked, while `grants_implementation_authority` remains false and no PAUTH is created automatically. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability and ADR/DCL clause preflights against this exact filed version. | Both pass with zero blocking gaps; project artifact linkage resolves to the parent project and WI-5462. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect changed paths and implementation-start target set. | Changes are limited to `groundtruth.db`, the declared platform test, and governed bridge/evidence artifacts inside `E:/GT-KB`. |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run focused verified finalization after an independent `VERIFIED` verdict. | WI-5462 becomes terminal only from valid implementation and verification evidence; no other work item or project is closed by this transaction. |

## Risk / Rollback

The principal risk is a partial multi-command metadata transaction. The
ordering deliberately adds and validates all dependency edges before revoking
authority. An edge-stage failure is rolled back append-only by retiring only
the newly created WI-5462 edges before any PAUTH revocation. A revocation-stage
failure leaves downstream work fail-closed; the implementation report records
the exact partial state and a new governed reconciliation owns any remaining
repair.

Dependency records and authorization history are never deleted or rewritten.
Rollback uses new retirement/recovery or authorization versions under fresh
authority. The focused test file may be reverted only through a later approved
change. Foundation completion and replacement downstream authority remain
separate, later governed actions.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5462-foundation-subproject-dependencies`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(projects)` because the implementation corrects a dependency and
authorization-enforcement defect in governed project metadata and adds its
specification-derived regression test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
