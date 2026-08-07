REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-04T22-01-48Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;::open build
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Govern session-start ORIENT stable identifier template candidate

bridge_kind: prime_proposal
Document: gtkb-wi5575-session-orient-stable-identifier
Version: 008
Responds to: bridge/gtkb-wi5575-session-orient-stable-identifier-007.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-AUTHORIZE-WI-5575-IMPLEMENTATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-AUTHORIZE-WI-5575-IMPLEMENTATION","coverage":"included_work_item","included_work_item_count":1,"specificity_rank":[1,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5575

target_paths: ["groundtruth-kb/templates/rules/session-start-orientation.md", "groundtruth-kb/tests/test_session_start_orientation_template.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false


## Proposal Note (finalization-authority correction)

Fresh NEW proposal per LO NO-GO v007 Finding 1: cites the AUTHORIZE PAUTH (PAUTH-PROJECT-GTKB-TREE-STABILIZATION-AUTHORIZE-WI-5575-IMPLEMENTATION, DELIB-20260803084760) so that, once approved by GO, the WI-5575 implementation report finalization binds the AUTHORIZE PAUTH (git_commit allowed) instead of the PROJECT-SCOPE PAUTH. Scope and targets unchanged from v001.

## Summary

WI-5575 governs a pre-existing foreign one-line ORIENT template change. Existing managed-registry/baseline evidence is 32/32 PASS, but no test defines the session-id source or unavailable-ID behavior. Independent review must resolve those semantics, require a focused template contract, hold implementation behind WI-5483 linked-test authority, and finalize only exact reviewed hunks.

Work item description: Own the pre-existing tracked one-line candidate in groundtruth-kb/templates/rules/session-start-orientation.md replacing synthetic ORIENT S{N} with ORIENT <session_id-short>. Treat current bytes as foreign and unverified. Before implementation/finalization, determine the canonical session-identity source and format, verify collision and unavailable-ID behavior, update the generated managed target if applicable, add a focused contract test that rejects synthetic counters and requires the bounded canonical identifier, run managed-artifact projection checks, and finalize only the exact reviewed hunks without absorbing unrelated dirt. Governed linked-test creation is deferred to WI-5483 because live PHASE-003 test_ids is malformed and add-work-item correctly fails before mutation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5575` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/templates/rules/session-start-orientation.md`, `groundtruth-kb/tests/test_session_start_orientation_template.py`.

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666269` - Loyal Opposition GO Verdict - WI-5266 Backlog Versus Bridge Resource Routing
- `DELIB-20260712-WI5205-HUNK-SCOPED-FINALIZATION-WAIVER` - Owner decision: WI-5205 hunk-scoped finalization waiver
- `DELIB-202666104` - Loyal Opposition VERIFIED verdict — WI-5132 tolerate genuine version gaps in VERIFIED finalization
- `DELIB-202666233` - Loyal Opposition Verification Verdict - WI-5229 Binary VERIFIED Finalizer Hunk Patch Support
- `DELIB-20264294` - Loyal Opposition Review - LO Review Dispatch Reliability Revision

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5575`.

## Proposed Scope

- Independently determine the canonical bounded session identifier and unavailable-identity behavior before adopting or correcting the existing one-line ORIENT placeholder hunk.
- Replace synthetic session counters only if the chosen placeholder is supplied by an authoritative runtime/session-envelope source and cannot be confused with a durable role or dispatcher identifier.
- Add one focused template contract module that rejects ORIENT S{N}, requires the approved bounded identifier syntax, checks unavailable-ID fail-closed wording, and preserves the seven-item block contract.
- Confirm whether an in-repository generated target is applicable; do not invent or hand-edit a projection when the packaged template is the canonical source.
- Exclude bridge/TAFE/dispatcher/harness mutation, unrelated templates or registries, groundtruth.db finalization, Git index/history operations, release, deployment, credentials, and all foreign dirt.

## Cross-Harness Disposition

- **managed-adopter-surfaces**: One packaged template contract shared by generated adopters; no direct live harness or dispatcher mutation.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5575; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Own the pre-existing tracked one-line candidate in groundtruth-kb/templates/rules/session-start-orientation.md replacing synthetic ORIENT S{N} with ORIENT <session_id-short>. Treat current bytes as foreign and unverified. Before implementation/finalization, determine the canonical session-identity source and format, verify collision and unavailable-ID behavior, update the generated managed target if applicable, add a focused contract test that rejects synthetic counters and requires the bounded canonical identifier, run managed-artifact projection checks, and finalize only the exact reviewed hunks without absorbing unrelated dirt. Governed linked-test creation is deferred to WI-5483 because live PHASE-003 test_ids is malformed and add-work-item correctly fails before mutation.",
  "after_behavior": "WI-5575 governs a pre-existing foreign one-line ORIENT template change. Existing managed-registry/baseline evidence is 32/32 PASS, but no test defines the session-id source or unavailable-ID behavior. Independent review must resolve those semantics, require a focused template contract, hold implementation behind WI-5483 linked-test authority, and finalize only exact reviewed hunks.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5575",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/templates/rules/session-start-orientation.md",
      "groundtruth-kb/tests/test_session_start_orientation_template.py"
    ],
    "linked_specifications": [
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
      "DCL-ACTIVITY-CONTEXT-MANIFEST-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "WI-5575 governs a pre-existing foreign one-line ORIENT template change. Existing managed-registry/baseline evidence is 32/32 PASS, but no test defines the session-id source or unavailable-ID behavior. Independent review must resolve those semantics, require a focused template contract, hold implementation behind WI-5483 linked-test authority, and finalize only exact reviewed hunks.",
    "scope": [
      "Independently determine the canonical bounded session identifier and unavailable-identity behavior before adopting or correcting the existing one-line ORIENT placeholder hunk.",
      "Replace synthetic session counters only if the chosen placeholder is supplied by an authoritative runtime/session-envelope source and cannot be confused with a durable role or dispatcher identifier.",
      "Add one focused template contract module that rejects ORIENT S{N}, requires the approved bounded identifier syntax, checks unavailable-ID fail-closed wording, and preserves the seven-item block contract.",
      "Confirm whether an in-repository generated target is applicable; do not invent or hand-edit a projection when the packaged template is the canonical source.",
      "Exclude bridge/TAFE/dispatcher/harness mutation, unrelated templates or registries, groundtruth.db finalization, Git index/history operations, release, deployment, credentials, and all foreign dirt."
    ],
    "acceptance_criteria": [
      "Independent review names the canonical source, truncation/format rule, collision posture, and unavailable-ID behavior before source mutation.",
      "Focused tests reject synthetic S{N} counters, validate the exact approved placeholder and seven-item ORIENT block, and all managed-registry/baseline tests remain green.",
      "The current template hash is 5245DC55FCE4367C57DE54197BE74FB815B5A4454D8FB4088AD563F3F8680B51; hash drift fails closed.",
      "Implementation cannot start until WI-5483 provides a governed linked test, independent GO is current, and exact claim/start authority succeeds."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Focused template tests prove ORIENT identity is derived from the approved canonical session source and defines explicit fail-closed output when unavailable. |
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001` | Run groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_baseline_audit_skill.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_session_start_orientation_template.py -q --tb=short and preserve managed-template structure. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run Ruff check/format, git diff --check, exact target hash validation, and independent LO review; reject missing linked-test evidence, unreviewed projection edits, or unrelated hunks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Independent review names the canonical source, truncation/format rule, collision posture, and unavailable-ID behavior before source mutation.
- Focused tests reject synthetic S{N} counters, validate the exact approved placeholder and seven-item ORIENT block, and all managed-registry/baseline tests remain green.
- The current template hash is 5245DC55FCE4367C57DE54197BE74FB815B5A4454D8FB4088AD563F3F8680B51; hash drift fails closed.
- Implementation cannot start until WI-5483 provides a governed linked test, independent GO is current, and exact claim/start authority succeeds.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/templates/rules/session-start-orientation.md`
- `groundtruth-kb/tests/test_session_start_orientation_template.py`

## Recommended Commit Type

`feat`
