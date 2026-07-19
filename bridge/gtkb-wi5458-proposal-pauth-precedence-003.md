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

# WI-5458 Revised Deterministic Work-Item PAUTH Selection

bridge_kind: prime_proposal
Document: gtkb-wi5458-proposal-pauth-precedence
Version: 003
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-002.md
Revises: bridge/gtkb-wi5458-proposal-pauth-precedence-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458
Related Work Items: WI-5420, WI-5294, WI-5476, WI-5488

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision accepts the two material version-002 findings and replaces the
prose-only source-ownership sequence with an ordered first-class MemBase
subproject:

`PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-BRIDGE-PROPOSAL-FILING`

Its current active membership order is:

1. WI-5476, whose non-overlapping implementation report is already awaiting
   independent verification.
2. WI-5420, the current owner of all three WI-5458 target paths.
3. WI-5294, the previously undisclosed older proposal targeting the same three
   paths plus one additional test.
4. WI-5458.
5. WI-5488, which must validate the completed proposal-filing gate stack after
   the scaffold and authorization-selection work lands.

The V1 PAUTH is revoked. The active V2 PAUTH permits proposal filing now but
requires terminal independent VERIFIED/focused finalization of WI-5420 and
WI-5294, clean reviewed target preimages, independent GO, an exact claim, and
schema-v3 implementation-start authorization before WI-5458 source or test
mutation.

## Response To Version 002

### Blocking Finding 1 - Governed sequencing and WI-5294 disclosure

Accepted in substance and corrected through the DCL's project-membership
mechanism.

`DCL-PROJECT-DEPENDENCY-ORDERING-001` names versioned project-dependency and
project-membership records as the authority for project dependencies and
project-scoped work-item order. A `requires_project_state` edge cannot express
"WI-5420 reaches VERIFIED": its schema accepts only project states
`active`, `completed`, `retired`, or `cancelled`. Making the entire black-box
project depend on the unrelated parent modernization project completing would
be materially broader than the source collision and would not encode the
reviewer's requested work-item condition.

Prime Builder therefore used the other canonical mechanism named by the DCL:
the existing first-class `bridge-proposal-filing` child project now contains
WI-5420, WI-5294, WI-5458, and WI-5488 in explicit membership order. WI-5294
is no longer undisclosed. It precedes WI-5458 because its already-filed
non-impairment scaffold proposal is older and owns the same three files.
WI-5488 follows both because dry-run/live gate parity must test the resulting
complete writer stack.

Prime Builder also attempted a valid parent-closure dependency on this child
project. Admission failed atomically because the global dependency validator
found an unrelated existing retired-endpoint defect:
`PDEP-PROJECT-GTKB-ROLE-ENHANCEMENT-PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION-DEPENDS-ON`.
No dependency record was created and no foreign project state was changed.
The subproject's version-2 MemBase record preserves that admission result and
the operative membership order.

### Blocking Finding 2 - Preserve the terminal predecessor baseline

Accepted and corrected in both proposal and authorization.

WI-5458 no longer refers to preserving the current in-flux snapshot. It must
preserve the WI-5420 and WI-5294 hunks exactly as they exist after each
predecessor reaches independent VERIFIED and focused finalization. At
implementation start, Prime Builder must compute fresh hashes from that clean
terminal baseline, compare the three target paths with the finalized
predecessor evidence, and return for renewed review on any unexplained drift.

### Non-Blocking Observation - Direct PAUTH semantics deliberation

Accepted. `DELIB-20266083`, the owner decision establishing restrictive
`included_work_item_ids` semantics, is now cited under Prior Deliberations.

## Current Source Ownership

All three targets remain modified relative to committed HEAD as the
carried-forward WI-5420 implementation surface. WI-5420's corrected
implementation report is
`bridge/gtkb-wi5420-canonical-parity-disposition-cli-007.md`, current status
`NEW`, awaiting independent verification. WI-5294 remains open with its
historical proposal at
`bridge/gtkb-wi5294-proposal-generator-nonimpairment-schema-001.md`.

WI-5458 performs no source or test work while either predecessor remains
nonterminal, while the targets are dirty or claimed, or while their reviewed
terminal preimages are unavailable.

## Proposed Scope

- Rank every active PAUTH covering the requested work item by:
  - exact singleton `included_work_item_ids` first;
  - then explicit multi-work-item lists, with fewer included IDs more
    specific than larger lists;
  - unrestricted project-membership fallback last.
- Make selection independent of database insertion and row order.
- Fail closed when multiple covering active PAUTHs tie at the most-specific
  rank. Do not choose an arbitrary row.
- Preserve the existing restrictive coverage truth table; this change ranks
  multiple already-covering authorizations and does not make an excluded work
  item eligible.
- Return the selected PAUTH ID in dry-run JSON and ordinary successful filing
  metadata.
- Ensure ambiguous or invalid selection fails before bridge-file or
  dispatcher/TAFE publication.
- Add focused insertion-order, specificity, ambiguity, disclosure, and
  zero-write regression cases to the existing proposal-filing test module.
- Preserve every terminal WI-5420 and WI-5294 hunk outside the bounded
  selection delta.
- Do not mutate dispatcher configuration, dispatcher runtime state, TAFE
  state directly, harness configuration, credentials, Git state, deployment,
  release state, or unrelated files.

## Hard Implementation-Start Gates

1. WI-5476 is independently VERIFIED/finalized or confirmed non-overlapping.
2. WI-5420 is independently VERIFIED and focused-finalized.
3. WI-5294 is independently VERIFIED and focused-finalized.
4. The first-class `bridge-proposal-filing` subproject still orders WI-5458
   after WI-5420 and WI-5294.
5. The V2 PAUTH remains active and is selected for WI-5458.
6. This thread is latest `GO`.
7. All three targets are clean, unclaimed, and match fresh reviewed terminal
   preimages.
8. One exact `go_implementation` claim and schema-v3 implementation-start
   packet authorize all three paths.
9. Operation-time authorization passes immediately before each mutation.

Any failed gate returns the thread for renewed review. No foreign-hunk
adoption or current-dirty-baseline implementation is authorized.

## Requirement Sufficiency

Existing requirements sufficient.

The cited PAUTH envelope, restrictive included-work-item, bridge authority,
project ordering, lifecycle, and specification-derived verification contracts
already define the correction. Version 002 identified a missing use of
canonical ordering state, not a missing owner policy choice. The ordered
subproject and V2 authorization supply that state without inventing a
work-item condition in the project-dependency schema.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5458; TEST-11559; bridge/gtkb-wi5458-proposal-pauth-precedence-002.md; DELIB-20266083",
  "canonical_authority": "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001; DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001; DCL-PROJECT-DEPENDENCY-ORDERING-001",
  "primary_route": "gt bridge file-implementation-proposal --wi <WI-ID> --slug <slug> --target-path <path> --dry-run --json",
  "before_behavior": "The first covering active PAUTH in database row order can silently broaden proposal authority.",
  "after_behavior": "The most-specific covering PAUTH is selected deterministically and equal-rank ambiguity fails before publication.",
  "self_descriptive_naming": "Selected project_authorization_id remains visible in dry-run and live result metadata.",
  "obsolete_guidance_disposition": "Database insertion order and first-row selection are not authorization precedence.",
  "history_preservation": "Existing bridge chains and predecessor implementation hunks remain append-only and unchanged.",
  "baseline": {
    "ordered_subproject": "PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-BRIDGE-PROPOSAL-FILING",
    "predecessors": ["WI-5420", "WI-5294"],
    "linked_test": "TEST-11559"
  },
  "expected_result": {
    "success": "Exact singleton beats multi-WI coverage, which beats unrestricted fallback, independent of row order.",
    "ambiguity": "Equal most-specific candidates fail closed with no publication.",
    "predecessor_preservation": "Terminal WI-5420 and WI-5294 bytes remain unchanged outside the reviewed WI-5458 delta."
  },
  "rollback": {
    "instructions": "Governed revert of only the WI-5458 selection and focused test delta.",
    "verification": "Rerun the focused proposal-filing suite and compare predecessor hunk hashes."
  },
  "hard_invariants": [
    "Restrictive PAUTH coverage semantics do not change.",
    "Selection is independent of database row order.",
    "No equal-rank arbitrary selection.",
    "No bridge or TAFE publication after failed selection.",
    "No source mutation before terminal predecessor baselines."
  ],
  "fail_closed_conditions": [
    "No active covering PAUTH.",
    "Multiple equally most-specific covering PAUTHs.",
    "Predecessor not terminal or target preimage drift.",
    "Claim, implementation-start, or operation-time authorization mismatch."
  ],
  "essential_context_preservation": "Results retain the WI, project, selected PAUTH, candidate ranks, first blocking reason, and publication outcome."
}
```

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded PAUTH and proposal path while retaining all later gates.
- `DELIB-20266083` records the owner's restrictive
  `included_work_item_ids` semantics and is the direct decision ancestor for
  deterministic specific-authorization selection.
- `DELIB-20265833` records the earlier independent review history for those
  restrictive semantics.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` permits the
  WI-5458-specific V2 authorization and governed revision.
- No new owner choice is required. This revision uses the existing first-class
  subproject and the ordering mechanism already specified by
  `DCL-PROJECT-DEPENDENCY-ORDERING-001`.
- The owner's dispatcher-configuration hold remains binding. Neither this
  revision nor the proposed implementation may inspect or mutate dispatcher
  configuration or runtime state.

## Specification-Derived Verification Plan

| Requirement | Executed implementation verification | Expected result |
| --- | --- | --- |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | Seed exact singleton, explicit multi-WI, and unrestricted PAUTHs in both insertion orders. | Exact singleton wins; without it, the smallest explicit list wins; unrestricted is fallback only. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Seed two equally most-specific active PAUTHs. | Dry-run and live calls fail closed before writer invocation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Inspect temporary bridge and publication fakes after every denied case. | No bridge file or dispatcher/TAFE publication occurs. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-STANDING-BACKLOG-001` | Read the ordered `bridge-proposal-filing` subproject and fresh WI-5420/WI-5294 terminal state before start. | WI-5458 remains after both shared-file predecessors. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Execute candidate and live proposal preflights. | Exact project, V2 PAUTH, WI, target, and specification linkage pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the full focused proposal-filing module, scoped Ruff check/format, and diff checks. | Existing WI-5420/WI-5294 behavior and all new TEST-11559 cases pass. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect WI, TEST-11559, V2 PAUTH, ordered child project, bridge chain, claim/start packet, report, verdict, and finalization evidence. | Every lifecycle transition remains independently reconstructable. |

## Pre-Filing Preflight Subsection

The exact candidate bytes were checked before filing:

- First-line role eligibility: active Prime Builder role is authorized to
  author `REVISED`.
- Applicability preflight: `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `blocking_errors: []`.
- Mandatory clause preflight: five clauses evaluated, three `must_apply`,
  zero evidence gaps, zero blocking gaps, exit `0`.
- Bridge compliance audit: `decision: pass`, `preflight_passed: true`.
- WI-ID collision check in strict mode: four declared related IDs, zero
  collisions, zero relationship errors.
- Target-path coverage in strict mode: `verdict: clean`; every implied path is
  present in the declared target set.
- Canonical-reference forbidden-surface scan: zero hits.
- PAUTH readback: V2 is active, singleton-scoped to WI-5458, and permits only
  bridge, metadata, governance-evidence, source, and test mutation classes
  subject to its registered prohibitions.

The governed revision helper will rerun candidate applicability, clause,
credential, compliance, and publication-admission checks while filing.
Live applicability and clause preflights will then be rerun against the
numbered bridge file.

## Risk And Rollback

The primary risk remains authorization selection in a shared proposal-filing
chokepoint. The ordered predecessor gates prevent WI-5458 from overwriting
in-flight WI-5420 or WI-5294 work. The specificity matrix and zero-write
assertions prevent a ranking correction from becoming a broader authority
path. Rollback is limited to the eventual reviewed WI-5458 source/test delta;
the V2 PAUTH, ordered project records, and numbered bridge audit chain remain
append-only evidence.

Recommended commit type: fix(bridge):
