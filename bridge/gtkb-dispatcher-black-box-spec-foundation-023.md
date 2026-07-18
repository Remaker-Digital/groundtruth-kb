REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5268 Canonical-Only Dispatcher Black-Box Foundation Reimplementation Proposal

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 023
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-022.md
Supersedes for implementation authority: bridge/gtkb-dispatcher-black-box-spec-foundation-021.md, bridge/gtkb-dispatcher-black-box-spec-foundation-022.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268
Related Work Items: WI-5487, WI-5491
Related Test Artifacts: TEST-11578, TEST-11580
target_paths: ["groundtruth.db"]
implementation_scope: governance_foundation_formalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: fix:

## Revision Claim

Version 023 preserves version 022's canonical-only correction and fixes its
zero-executable-assertion defect. Version 022 correctly withdrew version 021
because version 021 cited ephemeral session state, generated approval outputs,
and noncanonical runtime evidence. Version 022 nevertheless proposed empty
assertion arrays, which `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
classifies as `UNASSESSED` and therefore insufficient for verification or
closure.

This revision is self-contained. Its evidence and dependencies are limited to:

- current MemBase records, including WI-5268, WI-5487, WI-5491, TEST-11578,
  TEST-11580, the active project authorization, and governing specifications;
- Deliberation Archive records identified below; and
- numbered bridge artifacts identified below.

The five exact native formal-artifact bodies and their complete proposed
machine metadata are embedded below. No scratchpad, harness-local state,
generated approval packet, retired progress-assessment surface, dispatcher
run record, or other ephemeral artifact is an input, target, citation, or
verification dependency of this proposal.

The only requested mutable target is the canonical MemBase carrier. No source,
test, hook, skill, configuration, dispatcher, TAFE, harness runtime, generated
approval output, Git index, commit, push, deployment, credential, or external
system mutation is requested.

## Canonical Reference Boundary

The following owner decisions are binding:

- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`: canonical bridge
  artifacts may cite MemBase, Deliberation Archive records, and numbered
  bridge artifacts; ephemeral state must first be promoted into a canonical
  home and must not cross session contexts.
- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT`: the retired
  progress-assessment surface is deleted and may not be read, cited, recreated,
  or used as a dependency.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`: this session
  may not mutate dispatcher configuration or runtime while an independent
  troubleshooter owns that surface.

Operational target declarations inside a requirement body identify future
implementation surfaces. They are not evidence citations and grant no
implementation authority. Any future mutation of such a surface still
requires its own work item, active project authorization, exact bridge GO,
work-intent claim, implementation-start packet, and compatible activity
envelope.

WI-5491 with TEST-11580 owns mechanical enforcement of this canonical-reference
boundary after the WI-5268 foundation is terminal VERIFIED. WI-5487 with
TEST-11578 owns fail-closed prevention of whole-carrier restore during review,
verification, cleanup, and finalization.

## Canonical Root-Cause Record

The canonical record supports a post-write whole-carrier restore as the cause
of the lost WI-5268 rows:

1. `bridge/gtkb-dispatcher-black-box-spec-foundation-019.md` records the
   implementation claim and immediate separate-process readback of WI-5268
   version 9 plus five formal specification rows.
2. `bridge/gtkb-dispatcher-black-box-spec-foundation-020.md` independently
   records that WI-5268 remained at version 8/resolved and that all five formal
   specification identifiers were absent.
3. WI-5487 canonically records the intervening whole-carrier restore finding,
   the recurrence class, and TEST-11578.
4. `bridge/gtkb-wi5138-database-incident-recovery-evidence-001.md` records the
   prior recurrence of the same whole-carrier restore failure class.

This revision does not reproduce or cite the ephemeral observation source.
The durable conclusion is the fact promoted into WI-5487 and the numbered
bridge chain above. Version 019 therefore did not produce durable terminal
state, and version 020 correctly rejected the implementation claim.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`

## Owner Decisions And Canonical History

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE`
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET`
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT`
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING`
- `DELIB-20260715-DISPATCHER-BLACKBOX-PROJECT-HOME`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES`
- `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL`
- `DELIB-202666272`
- `DELIB-202666277`
- `DELIB-20265888`
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`
- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `bridge/gtkb-dispatcher-complex-black-box-advisory-001.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-017.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-018.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-019.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-020.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-021.md`
- `bridge/gtkb-wi5138-database-incident-recovery-evidence-001.md`

The owner approval phrase for the native packet is:
`APPROVE WI5268 FOUNDATION PACKET V2`.

The newer canonical-reference and retirement decisions change only provenance,
carrier, and evidence handling. They do not change the owner-approved
ordinary-worker definition, worker-safe packet contract, ordinary/ops/build
authority split, CLI-first facade decision, or foundation-first ordering.

## Exact Formalization Packet

All five records are create-only at version 1 with these common fields:

```json
{
  "status": "specified",
  "priority": "P0",
  "scope": "dispatcher-black-box-hardening",
  "testability": "automatable",
  "application_scope": "gtkb_platform",
  "change_reason": "WI-5268 dispatcher black-box governance/spec foundation",
  "approval_evidence": [
    "APPROVE WI5268 FOUNDATION PACKET V2",
    "DELIB-202666277",
    "DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY"
  ],
  "affected_by": [
    "bridge/gtkb-dispatcher-complex-black-box-advisory-001.md",
    "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
    "DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE",
    "DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET",
    "DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION",
    "DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY",
    "DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT",
    "DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST",
    "DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES",
    "DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL",
    "DELIB-202666277",
    "DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY",
    "ADR-DISPATCHER-ARCHITECTURE-001",
    "DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001",
    "GOV-ARTIFACT-APPROVAL-001",
    "PB-ARTIFACT-APPROVAL-001",
    "ADR-ARTIFACT-FORMALIZATION-GATE-001",
    "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001"
  ],
  "source_paths": [
    "bridge/gtkb-dispatcher-complex-black-box-advisory-001.md",
    "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md"
  ]
}
```

Each artifact below declares one executable outer assertion and a deterministic
evaluation contract. The outer assertion verifies the exact formalized
requirement against this canonical numbered bridge packet. Downstream runtime,
hook, CLI, and configuration behavior remains deferred to separately governed
implementation work; these foundation assertions verify canonical
formalization, not downstream implementation.

### DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001

```json
{
  "id": "DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001",
  "type": "design_constraint",
  "title": "Dispatcher ordinary-worker black-box boundary",
  "section": "Ordinary worker boundary",
  "full_content_sha256": "be3ff577ee08df976542de1ef9dd75284cc24a1edee5eb5f11056c1933a02574",
  "tags": [
    "dispatcher-black-box",
    "ordinary-worker",
    "activity-envelope",
    "worker-safe-facade",
    "foundation-first"
  ],
  "constraints": {
    "ordinary_worker": "session envelope without initialized activity envelope",
    "allowed_access": "worker-safe facade and assigned packet only",
    "protected_surfaces": [
      "raw_bridge_files",
      "TAFE_state",
      "dispatcher_config",
      "dispatcher_runtime",
      "harness_state",
      "leases",
      "scheduling",
      "other_harness_state"
    ],
    "exceptions": [
      "explicit_activity_envelope",
      "case_bound_owner_maintenance_capability",
      "break_glass_dispatcher_complex_outage"
    ],
    "evaluation_contract": {
      "evaluator_id": "canonical-assertion-runner",
      "supported_type": "all_of",
      "invocation_route": "gt assert --spec DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001",
      "required_outer_assertion_ids": ["DISPATCHER-ORDINARY-A1"],
      "evidence_kinds": ["file_exists", "grep"],
      "subject_version": 1,
      "subject_hash": "be3ff577ee08df976542de1ef9dd75284cc24a1edee5eb5f11056c1933a02574",
      "currentness": "invalid when canonical version 023 is absent or superseded by changed native content",
      "lifecycle_scope": "specified foundation formalization",
      "failure_severity": "P0",
      "affected_gate": "WI-5268 verification and closure",
      "incomplete_behavior": "FAIL or UNASSESSED; never PASS",
      "historical_evidence": "older numbered bridge versions remain historical only",
      "recovery": "file a new reviewed bridge revision and append a corrected spec version"
    }
  },
  "assertions": [
    {
      "id": "DISPATCHER-ORDINARY-A1",
      "type": "all_of",
      "description": "Canonical foundation packet specifies the ordinary-worker black-box boundary.",
      "assertions": [
        {
          "type": "file_exists",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "description": "Canonical version 023 exists."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "A GT-KB worker is an ordinary worker whenever its session envelope has not yet",
          "min_count": 1,
          "description": "Ordinary-worker status is envelope-state based."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "Both Prime Builder and",
          "min_count": 1,
          "description": "The boundary applies to both Prime Builder and Loyal Opposition."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "Protected internals include raw numbered bridge files",
          "min_count": 1,
          "description": "Protected surfaces are explicitly specified."
        }
      ]
    }
  ]
}
```

```markdown
# DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001

## Constraint

A GT-KB worker is an ordinary worker whenever its session envelope has not yet
been initialized with an activity envelope. Ordinary status is independent of
Prime Builder versus Loyal Opposition role, independent of interactive versus
headless execution, and independent of harness vendor. Both Prime Builder and
Loyal Opposition ordinary workers receive the baseline behaviors, constraints,
and knowledge needed for their role, but that baseline does not include direct
bridge/TAFE/dispatcher/harness-complex internals access.

An ordinary worker must treat the bridge/TAFE/dispatcher/harness complex as a
strict operational black box. The ordinary worker may use only worker-safe
facades, safe status summaries, safe blocker/no-work reasons, and assigned
worker-safe packets. The ordinary worker must not directly inspect, enumerate,
read, write, shell against, or derive live workflow state from protected
internals.

## Protected Surfaces

Protected internals include raw numbered bridge files and bridge index files,
TAFE queue and routing state, dispatcher configuration, dispatcher runtime
state, harness registry/state, activity-envelope internals, scheduling and
ranking data, leases, process details, other-harness state, and implementation
source or support files whose primary purpose is controlling those surfaces.

The protected boundary applies to ordinary Read, Grep, search, shell,
PowerShell, write, edit, apply-patch, app, browser, and connector-mediated
access. A tool being technically available to the harness does not make the
protected surface ordinary-worker accessible.

## Allowed Ordinary Access

Ordinary workers may consume:

- a worker-context or equivalent worker-safe CLI packet for the current
  dispatch or interactive assignment;
- role-safe bridge views that include the exact assigned content needed for the
  worker's task without exposing protected internals;
- safe project, work-item, test, and specification records that are not
  dispatcher/TAFE/harness internals;
- safe blocker messages that explain why no work can proceed without revealing
  protected routing or runtime internals.

## Exceptions

Direct protected access requires an explicit activity envelope or a case-bound
owner-granted maintenance capability. A role label alone, an interactive
session, a broad project assignment, or a bridge task is not sufficient.

Break-glass raw bridge-file inspection is allowed only when the
bridge/TAFE/dispatcher complex cannot serve the worker-safe packet or when the
owner explicitly authorizes that inspection. The exception must be auditable,
scoped to the current session and purpose, and must not become the normal work
path.

## Foundation-First Project Gate

Implementation work for downstream dispatcher black-box hardening work items
must not proceed from raw advisory decisions alone. Downstream implementation
proposals for WI-5269 through WI-5276 must cite the verified WI-5268
foundation artifacts or fail closed as premature. Until the backlog has a
governed dependency-edge writer for already-created work items, this formal
constraint plus the WI-5268 executable foundation test is the project gate that
represents the owner's foundation-first decision.

## Verification Requirements

Tests or assertions for this constraint must prove that ordinary worker
definition is envelope-state based, that both Prime Builder and Loyal
Opposition ordinary workers remain mediated by safe facades, that protected
surfaces include raw bridge files and dispatcher/TAFE/harness state, and that
downstream black-box implementation proposals are blocked until the foundation
is verified.
```

### DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001

```json
{
  "id": "DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001",
  "type": "design_constraint",
  "title": "Dispatcher worker-safe packet contract",
  "section": "Worker-safe packet contract",
  "full_content_sha256": "e6a58c02993a8a0350a0655b65ffd023f7402febf36bf5694b9dc845a88cd237",
  "tags": [
    "dispatcher-black-box",
    "worker-context",
    "safe-packet",
    "assigned-content",
    "bridge-facade"
  ],
  "constraints": {
    "required_payload": "full assigned content and governing metadata",
    "excluded_surfaces": [
      "raw_queue_mechanics",
      "dispatcher_config",
      "dispatcher_runtime",
      "TAFE_internals",
      "harness_registry",
      "scheduling_ranking",
      "leases",
      "process_details",
      "other_harness_state"
    ],
    "incomplete_packet_behavior": "safe blocker or mediated fetch path",
    "evaluation_contract": {
      "evaluator_id": "canonical-assertion-runner",
      "supported_type": "all_of",
      "invocation_route": "gt assert --spec DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001",
      "required_outer_assertion_ids": ["DISPATCHER-SAFE-PACKET-A1"],
      "evidence_kinds": ["file_exists", "grep"],
      "subject_version": 1,
      "subject_hash": "e6a58c02993a8a0350a0655b65ffd023f7402febf36bf5694b9dc845a88cd237",
      "currentness": "invalid when canonical version 023 is absent or superseded by changed native content",
      "lifecycle_scope": "specified foundation formalization",
      "failure_severity": "P0",
      "affected_gate": "WI-5268 verification and closure",
      "incomplete_behavior": "FAIL or UNASSESSED; never PASS",
      "historical_evidence": "older numbered bridge versions remain historical only",
      "recovery": "file a new reviewed bridge revision and append a corrected spec version"
    }
  },
  "assertions": [
    {
      "id": "DISPATCHER-SAFE-PACKET-A1",
      "type": "all_of",
      "description": "Canonical foundation packet specifies required packet content, exclusions, and incomplete handling.",
      "assertions": [
        {
          "type": "file_exists",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "description": "Canonical version 023 exists."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "the full assigned-content payload needed for the task",
          "min_count": 1,
          "description": "Full assigned content is required."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "The packet must not expose raw queue mechanics",
          "min_count": 1,
          "description": "Protected internals are excluded."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "emit a safe blocker or to use a governed mediated view",
          "min_count": 1,
          "description": "Incomplete packets fail to a safe blocker or mediated view."
        }
      ]
    }
  ]
}
```

```markdown
# DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001

## Constraint

The worker-safe packet is the ordinary-worker substrate for bridge,
implementation, review, verification, advisory-disposition, and safe blocker
work. The packet must be sufficient for normal assigned work without requiring
direct protected-surface inspection.

For an assigned bridge or implementation task, the packet must include the full
assigned-content payload needed for the task. Depending on assignment kind, this
includes the exact assigned proposal, verdict, implementation report, review
packet, advisory, or other bridge artifact content; governing specification
links; project authorization and work-item metadata; target paths; allowed
actions; forbidden actions; blockers; preflight state; citations; provenance;
session and dispatch identity; and content hashes or equivalent integrity
evidence.

## Required Inclusions

A worker-safe packet for ordinary Prime Builder or Loyal Opposition work must
include:

- role and activity state for the current assignment;
- dispatch, correlation, project, work-item, and bridge identifiers needed to
  route work and reports;
- exact assigned bridge/proposal/verdict/report/advisory content needed to
  perform the assigned action;
- governing specification links, prior deliberation links, target paths,
  project authorization identifiers, and verification obligations;
- role-authorized next actions and prohibited actions;
- safe blocker/no-work reasons when the assignment cannot proceed;
- citation and provenance data sufficient for audit and downstream LO/PB
  review;
- refresh or mediated-fetch instructions when the safe packet is incomplete.

## Required Exclusions

The packet must not expose raw queue mechanics, dispatcher configuration,
dispatcher runtime state, TAFE internals, harness registry internals, scheduling
or ranking internals, leases, process details, other-harness state, or raw
protected bridge/TAFE/dispatcher/harness files. Excluded information must not be
leaked through hidden debug sections, verbose mode defaults, stack traces, or
transcript-friendly summaries.

## Incomplete Packet Handling

If the worker-safe packet lacks content required for assigned ordinary work, the
correct behavior is to emit a safe blocker or to use a governed mediated view.
The missing content is not permission for an ordinary worker to inspect raw
protected internals.

## Verification Requirements

Tests or assertions for this constraint must prove that packet output includes
full assigned content and governing metadata, that it excludes protected
internals, and that missing required content produces a safe blocker or mediated
fetch path rather than a raw-file or raw-state access instruction.
```

### DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001

```json
{
  "id": "DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001",
  "type": "design_constraint",
  "title": "Dispatcher activity-envelope authority split",
  "section": "Activity-envelope authority",
  "full_content_sha256": "aa62220c8cbfd62ae43d48a61d6ca321c1f7cee4c803dfa474a5e575724d9d71",
  "tags": [
    "dispatcher-black-box",
    "activity-envelope",
    "ops",
    "build",
    "capability-token",
    "audit"
  ],
  "constraints": {
    "authority_classes": [
      "ordinary",
      "ops",
      "build"
    ],
    "ops": "black-box configuration mutation only",
    "build": "direct internals mutation only with case-specific authorization",
    "non_interchangeable": true,
    "capability_scope": [
      "session",
      "activity",
      "surfaces",
      "purpose",
      "allowed_operations",
      "TTL",
      "owner_or_project_authorization"
    ],
    "evaluation_contract": {
      "evaluator_id": "canonical-assertion-runner",
      "supported_type": "all_of",
      "invocation_route": "gt assert --spec DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001",
      "required_outer_assertion_ids": ["DISPATCHER-ACTIVITY-A1"],
      "evidence_kinds": ["file_exists", "grep"],
      "subject_version": 1,
      "subject_hash": "aa62220c8cbfd62ae43d48a61d6ca321c1f7cee4c803dfa474a5e575724d9d71",
      "currentness": "invalid when canonical version 023 is absent or superseded by changed native content",
      "lifecycle_scope": "specified foundation formalization",
      "failure_severity": "P0",
      "affected_gate": "WI-5268 verification and closure",
      "incomplete_behavior": "FAIL or UNASSESSED; never PASS",
      "historical_evidence": "older numbered bridge versions remain historical only",
      "recovery": "file a new reviewed bridge revision and append a corrected spec version"
    }
  },
  "assertions": [
    {
      "id": "DISPATCHER-ACTIVITY-A1",
      "type": "all_of",
      "description": "Canonical foundation packet specifies ordinary, ops, and build authority without interchangeability.",
      "assertions": [
        {
          "type": "file_exists",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "description": "Canonical version 023 exists."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "The minimum activity-envelope authority classes for the dispatcher black-box",
          "min_count": 1,
          "description": "The ordinary, ops, and build classes are specified."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "An ops activity envelope may authorize mutation",
          "min_count": 1,
          "description": "Ops owns black-box configuration mutation."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "Build authority is not blanket authority",
          "min_count": 1,
          "description": "Build direct-internals authority remains case-specific."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "Ops and build authorities are not interchangeable",
          "min_count": 1,
          "description": "Authority classes are non-interchangeable."
        }
      ]
    }
  ]
}
```

```markdown
# DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001

## Constraint

Protected bridge/TAFE/dispatcher/harness-complex access is granted by explicit
activity envelope authority or by a case-bound owner-granted maintenance
capability. It is not granted by ordinary worker status, role label, interactivity,
model identity, harness identity, generic bridge assignment, or broad project
membership.

The minimum activity-envelope authority classes for the dispatcher black-box
program are ordinary, ops, and build.

## Ordinary Authority

An ordinary session envelope has no initialized activity envelope. Ordinary
workers may consume worker-safe packets and role-safe facades only. Ordinary
workers may not directly read, write, enumerate, shell against, patch, or mutate
protected bridge/TAFE/dispatcher/harness internals.

## Ops Authority

An ops activity envelope may authorize mutation of bridge/TAFE/harness-complex
configuration: configuration of the black box itself. Ops authority does not
authorize direct mutation of black-box internals unless a separate build
authority and case-specific authorization are present.

Ops authority must be scoped to session, activity, target surfaces, purpose,
allowed operations, owner/project authorization, and TTL. Ops actions must emit
auditable evidence.

## Build Authority

A build activity envelope is required before a worker may directly mutate
black-box internals. Build authority is not blanket authority. Direct internal
mutation remains authorized case by case through an explicit work item, project
authorization, target path set, owner/governance approval, and bridge GO.

Build authority must be scoped to session, activity, target surfaces, purpose,
allowed operations, owner/project authorization, and TTL. Build actions must
emit auditable evidence and must fail closed when the case authorization is
missing, expired, or mismatched.

## Non-Interchangeability

Ops and build authorities are not interchangeable. An ops envelope cannot
perform direct internals mutation. A build envelope cannot mutate black-box
configuration unless the case authorization also grants that configuration
operation. Ordinary bridge review and implementation activities remain mediated
unless an explicit ops/build/maintenance authority is present.

## Capability Requirements

Maintenance capabilities must be recorded or signed, time-limited, scoped to
the current session and activity, bounded to paths or surfaces, tied to a
purpose, and linked to explicit owner permission or governed assignment. Broad
environment bypasses, implicit role-based access, and unbounded debug switches
are not valid capability carriers.

## Phased Hardening

Hard denial of ordinary protected reads, writes, and shell access must follow
safe-facade parity. Before hard enforcement, the project must provide worker-safe
packets rich enough for ordinary PB and LO work, then run audit or soft-deny
coverage to identify remaining ordinary-work dependencies on protected
internals. Hard enforcement must not ship while normal assigned work still
requires raw internals.

## Verification Requirements

Tests or assertions for this constraint must prove the ordinary/ops/build split,
the ops-only configuration mutation rule, the build-plus-case-authorization rule
for direct internals mutation, non-interchangeability, capability scoping, audit
evidence, and the facade-parity prerequisite for hard enforcement.
```

### ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001

```json
{
  "id": "ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001",
  "type": "architecture_decision",
  "title": "Use a worker-context facade for ordinary dispatcher work",
  "section": "Worker-context facade architecture",
  "full_content_sha256": "beffe6da9b2d75a471702a52d68cce865642fc77d34f617708f9e3577531a5b9",
  "tags": [
    "dispatcher-black-box",
    "worker-context",
    "CLI-facade",
    "safe-packet",
    "ordinary-worker"
  ],
  "constraints": {
    "selected_pattern": "CLI-first worker-context facade",
    "ordinary_prompt_payload": "role, dispatch/correlation identity, facade command",
    "facade_output": "assigned safe packet, allowed actions, blockers, exact assigned content",
    "excluded_default": "raw protected internals",
    "evaluation_contract": {
      "evaluator_id": "canonical-assertion-runner",
      "supported_type": "all_of",
      "invocation_route": "gt assert --spec ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001",
      "required_outer_assertion_ids": ["DISPATCHER-FACADE-A1"],
      "evidence_kinds": ["file_exists", "grep"],
      "subject_version": 1,
      "subject_hash": "beffe6da9b2d75a471702a52d68cce865642fc77d34f617708f9e3577531a5b9",
      "currentness": "invalid when canonical version 023 is absent or superseded by changed native content",
      "lifecycle_scope": "specified foundation formalization",
      "failure_severity": "P0",
      "affected_gate": "WI-5268 verification and closure",
      "incomplete_behavior": "FAIL or UNASSESSED; never PASS",
      "historical_evidence": "older numbered bridge versions remain historical only",
      "recovery": "file a new reviewed bridge revision and append a corrected spec version"
    }
  },
  "assertions": [
    {
      "id": "DISPATCHER-FACADE-A1",
      "type": "all_of",
      "description": "Canonical foundation packet specifies the CLI-first worker-context facade and safe outputs.",
      "assertions": [
        {
          "type": "file_exists",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "description": "Canonical version 023 exists."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "GT-KB will provide a worker-context facade",
          "min_count": 1,
          "description": "The facade is the selected ordinary interface."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "The worker-context facade must return the assigned worker-safe packet",
          "min_count": 1,
          "description": "Required safe facade outputs are specified."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "Hard gates against direct protected reads and writes must wait",
          "min_count": 1,
          "description": "Facade parity precedes hard denial."
        }
      ]
    }
  ]
}
```

```markdown
# ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001

## Decision

GT-KB will provide a worker-context facade as the ordinary interface to assigned
bridge/TAFE/dispatcher work. Ordinary dispatch prompts and ordinary interactive
continuations should provide the worker role, dispatch or correlation identity,
and a worker-safe CLI or equivalent facade command, rather than instructing the
worker to read raw bridge files, harness-state files, dispatcher configuration,
TAFE state, or runtime internals.

The worker-context facade must return the assigned worker-safe packet, allowed
actions, forbidden actions, safe blockers or no-work reasons, and the exact
assigned content required for the task. Skills and prompts for ordinary worker
operation must be built on this facade or on role-safe views with the same
black-box guarantees.

## Rationale

The dispatcher/TAFE/harness complex is platform infrastructure, not an ordinary
worker substrate. Prior worker prompts and skills exposed or encouraged direct
reads of bridge chains, harness registries, dispatcher status, runtime state,
configuration, and source-like operational internals. That made it impossible
to enforce the owner's strict black-box boundary without starving workers of the
content needed to perform assigned work.

A CLI-first facade gives ordinary workers a stable, auditable, role-safe source
for assigned content. It also gives ops and build maintenance paths a clear
boundary: if a task needs internals, it must initialize the correct activity
envelope or carry a case-bound maintenance capability instead of treating raw
inspection as normal work.

## Consequences

Ordinary worker prompts and skills must migrate away from raw
bridge/TAFE/dispatcher/harness-state inspection. The facade must be rich enough
to support ordinary Prime Builder and Loyal Opposition workflows, including
full assigned bridge/proposal/verdict/report/review content and governing
metadata. The facade must hide routing, scheduling, runtime, configuration, and
other-harness internals by default.

The design adds implementation work: packet generation, mediated views,
activity-envelope validation, capability checks, audit evidence, tests, and
prompt/skill rewrites. It also reduces future ambiguity by separating ordinary
work from ops and build maintenance work.

Hard gates against direct protected reads and writes must wait until the facade
has parity for ordinary work and audit/soft-deny evidence shows remaining raw
inspection dependencies have been removed or converted to safe blockers.

## Alternatives Considered

Prompt-first packet injection was considered. It would put the full safe packet
directly into each worker prompt and use CLI refresh as a secondary path. This
keeps worker startup simple but makes refresh, audit, and packet consistency
harder than a CLI-first facade.

Patching existing status, report, and bridge-file workflows was considered. It
would preserve familiar workflows but leaves too many raw inspection paths in
place and makes enforcement depend on instruction discipline.

Total opacity was considered. It would hide all bridge/TAFE/dispatcher state
from ordinary workers, but it would also prevent normal bridge review and
implementation work unless every assignment were manually expanded in prompt
text.

Keeping broad raw bridge-file readability was rejected because raw bridge-file
reads are the most common ordinary-worker path into protected dispatcher
complex state and conflict with the owner's strict black-box decision.

## Verification Requirements

Tests or assertions for this decision must prove that ordinary prompts and
skills can obtain assigned work through the facade, that the facade returns full
assigned content and safe blockers, that it excludes protected internals, and
that ops/build activity-envelope paths are separate from ordinary facade use.
```

### DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001

```json
{
  "id": "DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001",
  "type": "design_constraint",
  "title": "Dispatcher black-box foundation-first project gate",
  "section": "Foundation-first project gate",
  "full_content_sha256": "b2c2ffcf047a7d33a95e73f90f2b46525b3b55c25e383b4ad603a8c0fefe4088",
  "tags": [
    "dispatcher-black-box",
    "foundation-first",
    "project-gate",
    "work-item-dependencies",
    "bridge-preflight"
  ],
  "constraints": {
    "foundation_work_item": "WI-5268",
    "downstream_work_items": [
      "WI-5269",
      "WI-5270",
      "WI-5271",
      "WI-5272",
      "WI-5273",
      "WI-5274",
      "WI-5275",
      "WI-5276"
    ],
    "blocked_until": "WI-5268 terminal VERIFIED",
    "proposal_gate": "separately governed downstream enforcement",
    "implementation_start_gate": "separately governed downstream enforcement",
    "protected_mutation_gate": "separately governed downstream enforcement",
    "evaluation_contract": {
      "evaluator_id": "canonical-assertion-runner",
      "supported_type": "all_of",
      "invocation_route": "gt assert --spec DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001",
      "required_outer_assertion_ids": ["DISPATCHER-FOUNDATION-A1"],
      "evidence_kinds": ["file_exists", "grep"],
      "subject_version": 1,
      "subject_hash": "b2c2ffcf047a7d33a95e73f90f2b46525b3b55c25e383b4ad603a8c0fefe4088",
      "currentness": "invalid when canonical version 023 is absent or superseded by changed native content",
      "lifecycle_scope": "specified foundation formalization",
      "failure_severity": "P0",
      "affected_gate": "WI-5268 verification and closure",
      "incomplete_behavior": "FAIL or UNASSESSED; never PASS",
      "historical_evidence": "older numbered bridge versions remain historical only",
      "recovery": "file a new reviewed bridge revision and append a corrected spec version"
    }
  },
  "assertions": [
    {
      "id": "DISPATCHER-FOUNDATION-A1",
      "type": "all_of",
      "description": "Canonical foundation packet specifies WI-5268 as the fail-closed predecessor for WI-5269 through WI-5276.",
      "assertions": [
        {
          "type": "file_exists",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "description": "Canonical version 023 exists."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "WI-5268 is the foundation work item",
          "min_count": 1,
          "description": "WI-5268 is the foundation predecessor."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "WI-5269 through WI-5276 are downstream",
          "min_count": 1,
          "description": "All eight downstream work items are specified."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "The gate must fail closed",
          "min_count": 1,
          "description": "Missing foundation evidence blocks downstream work."
        },
        {
          "type": "grep",
          "file": "bridge/gtkb-dispatcher-black-box-spec-foundation-023.md",
          "pattern": "Absence of those citations is a blocking proposal defect",
          "min_count": 1,
          "description": "Downstream foundation citations are mandatory."
        }
      ]
    }
  ]
}
```

```markdown
# DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001

## Constraint

The dispatcher black-box hardening project must complete and verify its
formal-governance foundation before downstream source, prompt, hook, CLI,
runtime, configuration, or gate implementation work proceeds.

WI-5268 is the foundation work item. WI-5269 through WI-5276 are downstream
implementation or validation work items and must not receive implementation
start, PAUTH expansion, or bridge GO for implementation until WI-5268 is in a
terminal VERIFIED state and the foundation artifacts from WI-5268 exist in
MemBase with valid approval evidence.

## Governed Equivalent To Backlog Edges

The current public project/backlog CLI does not expose a dependency-edge writer
for already-created work items. Until such a governed writer exists, this DCL,
the bridge proposal gate, the implementation-start gate, and the focused WI-5268
executable foundation test are the governed equivalent project gate.

The bridge proposal gate must reject implementation-targeting `NEW` or
`REVISED` bridge proposals for WI-5269 through WI-5276 when WI-5268 is not
terminal VERIFIED or when the proposal omits the verified foundation artifact
citations.

The implementation-start gate must reject implementation authorization packets
and protected mutation starts for WI-5269 through WI-5276 when WI-5268 is not
terminal VERIFIED. This start gate applies even if a downstream proposal was
filed before the foundation gate existed.

The gate must fail closed; missing MemBase state, missing WI-5268 status,
missing foundation artifacts, missing required proposal citations, or a project
authorization that tries to include downstream implementation before WI-5268 is
VERIFIED must block the downstream operation.

If a future governed dependency-edge writer becomes available, the project may
backfill explicit dependency edges from WI-5269 through WI-5276 to WI-5268
without changing the owner-selected sequence.

## Allowed Pre-Foundation Work

Read-only analysis, owner clarification, proposal drafting, and safe
governance-preparation work may continue before WI-5268 is VERIFIED when it
does not mutate downstream implementation surfaces and does not bypass the
foundation artifacts. Any such work must remain non-implementation and must not
claim downstream readiness.

## Required Downstream Citations

Downstream proposals for WI-5269 through WI-5276 must cite the verified
foundation artifacts for ordinary-worker boundary, worker-safe packet contract,
activity-envelope authority, worker-context facade, and foundation-first gate.
Absence of those citations is a blocking proposal defect.

## Enforcement Surfaces

The enforcement surfaces for this constraint are:

- `.claude/hooks/bridge-compliance-gate.py`, for bridge proposal write-time
  rejection of premature downstream WI-5269 through WI-5276 implementation
  proposals;
- `scripts/implementation_authorization.py`, for implementation-start packet
  rejection before protected work begins;
- `scripts/implementation_start_gate.py`, for protected mutation fail-closed
  behavior when an active packet or work-intent claim does not satisfy the
  foundation-first condition;
- `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`, for
  executable regression coverage of the foundation artifacts and both gate
  surfaces.

## Verification Requirements

Tests or assertions for this constraint must prove that WI-5268 is the
foundation item, that WI-5269 through WI-5276 are treated as downstream, that
downstream proposal filing and implementation readiness fail while WI-5268 is
not VERIFIED, and that the required foundation artifact identifiers are present
in the downstream gate.
```

## Requirement Sufficiency

Existing requirements sufficient.

The exact native bodies above preserve the owner-approved foundation semantics.
The metadata is canonicalized only to remove scratch, generated-output, and
not-yet-governed implementation-file dependencies from this formalization-only
slice. The formal records remain fully specified through their native content,
tags, constraints, canonical provenance, and exact field values.

The enforcement carriers named by the foundation-first requirement are future
implementation surfaces, not WI-5268 targets. They may not be changed under
this proposal. Their implementation requires a separate approved proposal
after WI-5268 is terminal VERIFIED.

## Reimplementation Plan

After a fresh independent GO responding to version 023:

1. Acquire a fresh `go_implementation` claim and create a fresh schema-v3
   implementation-start packet bound to version 023, the GO, WI-5268, the
   active project authorization, this session, and the one declared target.
2. Re-run applicability and mandatory-clause preflights against the exact
   authorized proposal and fail closed on any gap.
3. Read WI-5268 and all five proposed specification identifiers through a new
   governed CLI process. Exact existing matches are idempotent no-ops; any
   conflicting current row stops implementation and returns to review.
4. Append the WI-5268 corrective version first, restoring
   `stage=backlogged`, `resolution_status=open`, and truthful status detail.
5. Create the five exact version-1 `specified` formal records from the
   self-contained bodies and metadata above through the canonical CLI or
   KnowledgeDB API. Do not use raw SQL, another database, binary replacement,
   whole-file restore, or generated scratch input.
6. Close the writer process. In a separate process, read WI-5268 and all five
   specification records and compare every declared field and each exact
   native-body hash.
7. After a delay spanning at least two normal dispatcher cycles, repeat the
   six separate-process reads without inspecting or mutating dispatcher
   configuration or runtime internals.
8. File an implementation report only if both readback rounds pass.
9. Independent verification must use read-only canonical CLI and numbered
   bridge evidence. It must not restore, checkout, reset, replace, stage, or
   commit the live MemBase carrier while evaluating the report.

No existing generated approval file is an implementation input or output.
Formal approval evidence is the exact owner phrase and canonical Deliberation
Archive records embedded above.

## Specification-Derived Verification Plan

| Specification or requirement | Canonical verification evidence | Required result |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Active project-authorization read plus fresh claim/start readback | Exact active PAUTH, independent GO, current claim, schema-v3 start, and one target |
| Five proposed ADR/DCL artifacts; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Five separate `gt spec show` results compared to the embedded bodies and metadata | Exact IDs, types, titles, contents, hashes, fields, tags, constraints, canonical provenance, version 1, and `specified` |
| `GOV-STANDING-BACKLOG-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Separate `gt backlog show WI-5268` results in both readback rounds | Version at least 9, open/backlogged, truthful non-terminal detail |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Canonical work-item reads for WI-5269 through WI-5276 | All remain open and blocked from implementation until WI-5268 is independently VERIFIED |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; WI-5487 | Immediate and delayed exact MemBase reads | All six current records persist; no whole-carrier restore or snapshot substitution |
| Canonical reference boundary; WI-5491 | Review of version 023 citations and self-contained packet | No scratch, retired, generated-output, harness-local, or runtime-log evidence dependency |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Run the five declared outer assertions through the canonical assertion route | Exactly five outer assertions execute from current canonical evidence; zero unsupported, stale, missing, or partial entries |
| Dispatcher troubleshooter hold | Target and action review | No dispatcher configuration or runtime mutation |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent execution of every mapped canonical read and comparison | Every required check runs and passes; report-only substitution fails |

## Pre-Filing Preflight

The completed version-023 candidate passed the governed applicability preflight
with no blocking errors and no missing required or advisory specifications.
The mandatory ADR/DCL clause preflight reported zero blocking gaps. A separate
canonical-boundary scan found no scratch, retired progress-assessment,
harness-local, generated approval-output, or dispatcher-runtime-log citation.

The filing helper must re-run final-byte compliance checks and fail closed on
any intervening change.

## Acceptance Criteria

- [x] Versions 021 and 022 are superseded as implementation authority.
- [x] The proposal is self-contained and cites only canonical evidentiary
  authorities.
- [x] All five exact native bodies and complete proposed metadata are embedded.
- [x] Each artifact has one deterministic executable outer assertion and a
  complete evaluation contract.
- [x] Scope is reduced to the canonical MemBase carrier.
- [x] WI-5487/TEST-11578 own carrier-restore recurrence prevention.
- [x] WI-5491/TEST-11580 own canonical-reference recurrence prevention.
- [x] The dispatcher configuration/runtime hold is explicit.
- [ ] Fresh independent GO approves this canonical-only reimplementation.
- [ ] Fresh claim and schema-v3 start authorize the one target.
- [ ] WI-5268 is truthfully restored to open/backlogged.
- [ ] All five exact formal records persist through immediate and delayed
  separate-process readback.
- [ ] Independent Loyal Opposition issues VERIFIED from canonical read-only
  evidence without restoring or replacing the carrier.
- [ ] Terminal finalization preserves concurrent MemBase rows and does not
  absorb unrelated work.

## Risk And Rollback

The principal risk is recurrence of an unrelated whole-file restore against
the shared MemBase carrier. The containment is exact row-level mutation,
separate-process readback, delayed durability readback, and an explicit
no-restore verification rule. WI-5487 owns permanent prevention.

Rollback is append-only correction or supersession of the six WI-5268 records.
It is never checkout, reset, byte-for-byte replacement, or restoration of the
live carrier from another state. If any step fails, retain the canonical bridge
and MemBase evidence, release the claim, and file a truthful revised report.

The canonical-reference boundary is fail-closed. If a required fact lacks a
canonical home, promote it to MemBase or the Deliberation Archive, or route it
through an Advisory Proposal before citing it. Do not bridge ephemeral evidence
directly.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
