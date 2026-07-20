NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Restore scan-helper synthetic GO fallback after exact numbered-file resolver wording change

bridge_kind: prime_proposal
Document: gtkb-wi5639-scan-helper-exact-numbered-chain-fallback
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5639

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Restore the intentionally narrow synthetic inline-GO compatibility fallback after the lifecycle resolver changed its missing-chain error wording, without weakening real implementation-start denial.

Work item description: The terminal WI-4618 scan helper intentionally fails open for synthetic inline GO fixtures when no real numbered bridge chain exists. The lifecycle reader now emits 'Bridge document not found as exact numbered files', while both managed scan helpers still recognize only the retired 'not found as versioned files' phrase. As a result, five focused scan-helper regressions fail and synthetic GO fixtures are misclassified as blocked_non_activatable. Restore one structured or exact compatible missing-chain predicate across both managed helpers without weakening denial for real malformed or unauthorized GO chains.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5639` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/bridge/helpers/scan_bridge.py`, `.codex/skills/bridge/helpers/scan_bridge.py`.

## Specification Links

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
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265754` - Loyal Opposition Verification Verdict - WI-4723 VERIFIED finalization index-lock retry
- `DELIB-202666024` - Verification Verdict - gtkb-wi5068-no-action-scan-helper-parser
- `DELIB-20265388` - Applicability Preflight
- `DELIB-202667020` - NO-GO — WI-5370 tracked-terminal WI-4567 byte-ownership repair (report 003)
- `DELIB-20265389` - Verdict for gtkb-wi4618-non-activatable-go-scan-reconciliation

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5639`.

## Proposed Scope

- Add the current exact lifecycle-reader missing-chain message to the narrow synthetic compatibility predicate while retaining the legacy message during migration.
- Apply the same bounded predicate to the Claude and Codex managed scan-helper copies and prove their bytes remain identical.
- Preserve fail-closed blocked_non_activatable classification and exact reasons for every real malformed, unauthorized, or otherwise non-activatable GO chain.

## Cross-Harness Disposition

- **Claude managed scan helper**: Update byte-identically and exercise template parity tests.
- **Codex managed scan helper**: Update byte-identically and exercise active helper tests.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5639; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The terminal WI-4618 scan helper intentionally fails open for synthetic inline GO fixtures when no real numbered bridge chain exists. The lifecycle reader now emits 'Bridge document not found as exact numbered files', while both managed scan helpers still recognize only the retired 'not found as versioned files' phrase. As a result, five focused scan-helper regressions fail and synthetic GO fixtures are misclassified as blocked_non_activatable. Restore one structured or exact compatible missing-chain predicate across both managed helpers without weakening denial for real malformed or unauthorized GO chains.",
  "after_behavior": "Restore the intentionally narrow synthetic inline-GO compatibility fallback after the lifecycle resolver changed its missing-chain error wording, without weakening real implementation-start denial.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5639",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      ".claude/skills/bridge/helpers/scan_bridge.py",
      ".codex/skills/bridge/helpers/scan_bridge.py"
    ],
    "linked_specifications": [
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001"
    ]
  },
  "expected_result": {
    "summary": "Restore the intentionally narrow synthetic inline-GO compatibility fallback after the lifecycle resolver changed its missing-chain error wording, without weakening real implementation-start denial.",
    "scope": [
      "Add the current exact lifecycle-reader missing-chain message to the narrow synthetic compatibility predicate while retaining the legacy message during migration.",
      "Apply the same bounded predicate to the Claude and Codex managed scan-helper copies and prove their bytes remain identical.",
      "Preserve fail-closed blocked_non_activatable classification and exact reasons for every real malformed, unauthorized, or otherwise non-activatable GO chain."
    ],
    "acceptance_criteria": [
      "The five current test_scan_bridge.py synthetic-inline-GO regressions pass without changing their assertions or test fixtures.",
      "The complete platform_tests/scripts/test_scan_bridge.py suite passes for the Codex helper and its Claude managed-template parity coverage.",
      "Both managed scan-helper files are byte-identical after the change, and no implementation-authorization, resolver, dispatcher, configuration, Git, or test file is mutated."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the full scan-helper suite, including synthetic missing-chain, real blocked GO, terminal-kind GO, NO-GO, and LO actionability cases. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Hash-compare both managed helper copies and run managed-template parity tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Assert the compatibility predicate recognizes the current exact-numbered-file resolver wording and does not broad-match unrelated authorization errors. |

## Acceptance Criteria

- The five current test_scan_bridge.py synthetic-inline-GO regressions pass without changing their assertions or test fixtures.
- The complete platform_tests/scripts/test_scan_bridge.py suite passes for the Codex helper and its Claude managed-template parity coverage.
- Both managed scan-helper files are byte-identical after the change, and no implementation-authorization, resolver, dispatcher, configuration, Git, or test file is mutated.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/bridge/helpers/scan_bridge.py`

## Recommended Commit Type

`feat`
