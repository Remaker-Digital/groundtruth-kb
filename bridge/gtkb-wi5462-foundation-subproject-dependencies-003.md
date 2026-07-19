REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

# WI-5462 - Revised foundation-first black-box child-project ordering

bridge_kind: prime_proposal
Document: gtkb-wi5462-foundation-subproject-dependencies
Version: 003
Responds to: bridge/gtkb-wi5462-foundation-subproject-dependencies-002.md
Carries forward: bridge/gtkb-wi5462-foundation-subproject-dependencies-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5462-FOUNDATION-SUBPROJECT-DEPENDENCIES-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5462

target_paths: ["groundtruth.db", "platform_tests/groundtruth_kb/test_project_dependency_ordering.py"]

implementation_scope: metadata | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Revision Claim

This revision resolves every finding in version 002 without changing the
approved transaction, target paths, PAUTH, specification set, or test
obligation. It records the already-realized foundation-first sequencing
violation for WI-5270 and WI-5276, gives that history an explicit forward-only
disposition, updates the WI-5156 and WI-5268 current-state evidence, and
preserves WI-5156 plus WI-5482 as hard terminal predecessors.

No dependency, project, authorization, work-item, test, source, dispatcher,
TAFE, harness, configuration, runtime-state, Git, or other repository mutation
is performed by this proposal filing.

## Findings Addressed

### Finding 1 - WI-5270 and WI-5276 completed before the foundation

Accepted and corrected. WI-5270 and WI-5276 both reached independently
VERIFIED bridge status on 2026-07-17, after the 2026-07-15 owner decision that
selected foundation-first ordering and before WI-5268 formalized the foundation.
This is a realized instance of the narrative-only sequencing defect WI-5462
exists to prevent, not merely a hypothetical risk.

Disposition: the eight project-dependency edges are forward-only controls.
They do not retroactively invalidate, reopen, or rewrite the independently
VERIFIED WI-5270 and WI-5276 implementation histories. No source remediation is
authorized by WI-5462. After WI-5268 formalizes the five foundation artifacts,
the later downstream proposal revisions and the final black-box program
terminal audit must re-check the WI-5270 worker-packet output and WI-5276
closure-scanner output against those canonical foundation specifications. Any
substantive incompatibility discovered there requires its own governed repair;
none is assumed by this metadata transaction.

The numbered bridge chain now durably records both the violation and its
disposition. A separate defect work item would duplicate the existing WI-5462
remedy and is not created.

### Finding 2 - WI-5156 state was stale

Corrected. WI-5156 is no longer characterized as a pre-implementation REVISED
proposal. Its dependency-ordering implementation is filed as revised
implementation report
`bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md`, awaiting
independent Loyal Opposition verification and focused finalization. WI-5462
must not begin until that thread is terminal VERIFIED and its implementation is
available through the installed `gt` entry point.

### Finding 3 - WI-5268 state drift

Updated for current evidence. The WI-5268 foundation thread is latest REVISED
at `bridge/gtkb-dispatcher-black-box-spec-foundation-031.md`, awaiting an
independent verdict on its UTC-derived approval-packet filenames. Its MemBase
row remains non-authoritative for live bridge status. WI-5462 neither
implements nor terminalizes WI-5268.

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

This proposal does not complete the foundation, change WI-5268 backlog state,
create replacement downstream authority, mutate dispatcher/TAFE runtime or
configuration, edit platform source, or write the database directly.

## Requirement Sufficiency

Existing requirements sufficient.

`DCL-PROJECT-DEPENDENCY-ORDERING-001` defines the dependency record,
direction, supported `completed` prerequisite state, `authorization` affected
gate, fail-closed graph validation, recovery, and non-authorizing semantics.
The owner deliberation defines the exact foundation-first sequence. No proposed
black-box DCL or ADR is treated as canonical authority until WI-5268
successfully formalizes it.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-12`
- `GOV-13`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` - Mike selected a
  formal specification foundation before downstream source, prompt, hook, or
  CLI implementation and required downstream child work to depend on it.
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL` -
  approved the MemBase project-dependency model and its governed CLI authority.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes
  bounded proposal carriers for defects discovered while stabilizing the
  bridge/TAFE/harness complex while preserving all later implementation gates.
- `bridge/gtkb-wi5462-foundation-subproject-dependencies-002.md` - independently
  identified the realized WI-5270/WI-5276 sequencing violation and accepted a
  forward-only disposition as a valid correction.

The mandatory Deliberation Archive search found no separate owner decision
requiring retroactive invalidation of WI-5270 or WI-5276.

## Owner Decisions / Input

Mike selected foundation-first ordering in
`DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` and directed Prime
Builder to complete the full black-box program to verified closure. That
decision authorizes this bounded proposal and its restrictive PAUTH; it does not
waive independent review, implementation-start, verification, or finalization.

The owner-directed dispatcher configuration/troubleshooter hold remains fully
controlling. This proposal and its future implementation do not inspect or
mutate dispatcher configuration or runtime state.

## Current-State Evidence

- Foundation project
  `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-FOUNDATION`
  is active and contains WI-5268.
- WI-5268 is latest REVISED at
  `bridge/gtkb-dispatcher-black-box-spec-foundation-031.md`; no terminal
  foundation evidence exists yet.
- WI-5270 reached VERIFIED at
  `bridge/gtkb-wi5270-worker-context-full-assigned-content-packet-004.md` on
  2026-07-17.
- WI-5276 reached VERIFIED at
  `bridge/gtkb-wi5276-black-box-closure-scanner-gate-004.md` on 2026-07-17.
- All eight downstream child projects are active and currently have no project
  dependencies or child-scoped authorizations.
- The parent black-box project has eight active PAUTHs for WI-5269 through
  WI-5276. Those records are the exact revocation set below.
- WI-5156's implementation is latest REVISED at
  `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md`,
  awaiting independent verification and focused finalization.
- Global `gt projects dependencies validate --json` currently fails because one
  unrelated active edge has a retired dependent endpoint. WI-5482 is latest
  NO-GO and must be terminal after WI-5156 before this transaction.
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
  `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST; WI-5462; TEST-11568; bridge/gtkb-wi5462-foundation-subproject-dependencies-003.md`

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

1. Confirm WI-5156 is terminal VERIFIED, focused-finalized, and its dependency
   CLI behavior remains available through the installed `gt` entry point.
2. After that terminal evidence exists, file and complete the WI-5482 revision,
   retire its one stale edge, and confirm global
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
   fails, preserve the fail-closed state and file a governed reconciliation.
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
- `WI-5270` and `WI-5276` - already VERIFIED before the foundation; their
  histories remain valid, while their outputs receive a foundation-conformance
  re-check during later downstream revisions and final program closure.
- `WI-5269` through `WI-5276` - downstream work items whose premature
  parent-scoped PAUTHs are revoked here; replacement child-scoped PAUTHs and
  further implementation require later governed proposals after foundation
  completion.
- `WI-5467` and `WI-5470` - closure-tool defects remain independently governed
  and receive no authority from this proposal.

## Specification-Derived Verification Plan

| Requirement | Verification evidence | Required result |
|---|---|---|
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Capture `gt projects authorizations <parent> --json` before mutation. | Exactly the eight named parent-scoped PAUTHs are active; no alternate downstream PAUTH is substituted. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` predecessor integrity | Confirm WI-5156 terminal VERIFIED/finalized, WI-5482 terminal VERIFIED, then run `gt projects dependencies validate --json`. | Installed dependency CLI is independently verified and the production graph reports `valid: true` before WI-5462 mutation. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` exact direction | Read every generated dependency through `gt projects dependencies show <id> --json` and list by dependent/prerequisite project. | Exactly eight active edges point from the named downstream children to the common foundation prerequisite with the declared kind, state, gate, WI, and provenance. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` global validity | Rerun `gt projects dependencies validate --json`. | `valid: true`; active dependency count increases by exactly eight; no unrelated edge changes. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` pre-foundation readiness | Read all eight child-project dependency readiness records while foundation is active. | Every edge is unsatisfied, blocks `authorization`, and reports `grants_implementation_authority: false`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` premature authority removal | Read all eight exact PAUTH IDs plus unrelated authorization baseline after revocation. | Latest status is revoked for exactly the eight named PAUTHs; no unrelated authorization changes; no replacement child PAUTH exists. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` fail-closed use | Run applicability/start validation against the existing downstream proposal/PAUTH pairs without claiming or starting them. | Each fails closed because its named PAUTH is revoked; no work intent or implementation-start record is created. |
| `GOV-12`, `GOV-13`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_project_dependency_ordering.py -q --no-header`. | `TEST-11568` passes and remains linked to WI-5462 and its valid test-plan phase. |
| Foundation-first historical disposition | Read the exact WI-5270 and WI-5276 VERIFIED bridge artifacts and the final program closure evidence after WI-5268 formalization. | Existing VERIFIED histories remain unchanged; later closure evidence records whether each output conforms to the five canonical foundation artifacts. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` completion semantics | In the isolated test database only, advance the foundation project to `completed` and re-read all eight edges. | Every edge becomes satisfied and unblocked, while `grants_implementation_authority` remains false and no PAUTH is created automatically. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability and mandatory clause preflights against this exact filed version. | Both pass with zero blocking gaps; project linkage resolves to the parent project and WI-5462. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect changed paths and implementation-start targets. | Changes are limited to `groundtruth.db`, the declared platform test, and governed bridge/evidence artifacts inside `E:/GT-KB`. |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run focused VERIFIED finalization after an independent verdict. | WI-5462 becomes terminal only from valid implementation and verification evidence; no other work item or project is closed by this transaction. |

## Pre-Filing Preflight Subsection

Observed against this exact completed candidate before live filing:

- applicability packet hash:
  `sha256:bb3766308871e48302125cc9ed28b3cadfe8ec8018ee461b22706c9391aec1ef`;
- `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- `blocking_errors: []`;
- mandatory clause preflight: 5 clauses evaluated, 4 `must_apply`, 1
  `may_apply`, 0 evidence gaps in `must_apply`, 0 blocking gaps, exit 0.

The governed filing helper re-runs both checks against these exact bytes and
must refuse publication on any drift.

## Acceptance Criteria

- The realized WI-5270/WI-5276 sequencing violation and forward-only
  disposition are explicit in the numbered bridge chain.
- WI-5156 and WI-5482 are terminal VERIFIED and focused-finalized before any
  WI-5462 implementation start.
- Exactly eight active child-to-foundation dependency edges are created.
- The production project graph remains globally valid.
- Exactly the eight listed parent-scoped PAUTHs are revoked.
- No replacement downstream authority is created.
- The focused TEST-11568 regression passes.
- No dispatcher configuration or runtime state is inspected or mutated.
- Independent Loyal Opposition verification is the only terminal closure path.

## Risk And Rollback

The principal risk is a partial multi-command metadata transaction. The
ordering adds and validates all dependency edges before revoking authority. An
edge-stage failure is rolled back append-only by retiring only newly created
WI-5462 edges before any PAUTH revocation. A revocation-stage failure leaves
downstream work fail-closed; the implementation report records exact partial
state and a new governed reconciliation owns remaining repair.

The historical-risk disposition is also explicit: forward-only controls do not
erase or invalidate WI-5270/WI-5276 VERIFIED history. Any later foundation
incompatibility is repaired through a new governed slice, not by rewriting
history in WI-5462.

Dependency records and authorization history are never deleted or rewritten.
Rollback uses new retirement/recovery or authorization versions under fresh
authority. Foundation completion and replacement downstream authority remain
separate governed actions.

## Recommended Commit Type

`fix(projects)` because the implementation corrects a dependency and
authorization-enforcement defect in governed project metadata and adds its
specification-derived regression test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
