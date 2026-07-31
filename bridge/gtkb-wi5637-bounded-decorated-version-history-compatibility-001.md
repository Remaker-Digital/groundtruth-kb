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

# Implementation Proposal - Accept bounded historical decorated Version metadata without weakening strict bridge history

bridge_kind: prime_proposal
Document: gtkb-wi5637-bounded-decorated-version-history-compatibility
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5637

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Accept only bounded historical decorated Version metadata after terminal WI-5629 and WI-5636 while preserving strict bridge-history denial and exact modern authoring.

Work item description: Historical canonical bridge artifacts such as WI-5554 v005, WI-5438 v005, WI-5474 v002, and research-clean-branch-publication carry a numeric Version value followed by a parenthetical status or report annotation. The public bridge lifecycle resolver currently requires exact digits and fails schema-v3 implementation authorization before a later strict GO can be evaluated. Add a bounded compatibility rule only after terminal WI-5629 and WI-5636: accept a filename-matching three-digit prefix followed by one historical parenthetical annotation when document identity, role/status, adjacency, and linkage remain valid; reject wrong numeric prefixes, arbitrary suffixes, duplicate Version fields, non-parenthetical text, cross-thread or malformed chains, and all ambiguity. Do not rewrite historical artifacts or weaken strict current-authoring requirements.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5637` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_lifecycle_resolver.py`, `platform_tests/scripts/test_bridge_lifecycle_resolver.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `DCL-VERIFIED-BRIDGE-HISTORY-001` - auto-linked governing or work-item specification.
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

- `DELIB-202667075` - Loyal Opposition Proposal Review - NO-GO - WI-5443 Bounded Fresh-Worker Timeout (wrong prerequisite identified; target file not clean; duplicates live WI-5336 thread)
- `DELIB-20265787` - Loyal Opposition NO-GO Verification Verdict: gtkb-wi4761-restore-ci-testing-integration-health
- `DELIB-20265747` - Loyal Opposition GO verdict: WI-4716 bridge-propose semantic-search doc sync
- `DELIB-20265740` - Loyal Opposition GO verdict - WI-4701 Codex adapter CRLF whitespace fix
- `DELIB-202666479` - Loyal Opposition Corrected Verdict - NO-GO - WI-5307 Shared Enforcement Baseline Disposition

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5637`.

## Proposed Scope

- Hard-depend on WI-5629 and WI-5636 reaching terminal VERIFIED with no live implementation claims; consume their public resolver contract without broadening either predecessor.
- Recognize one historical Version form only when the three-digit numeric prefix matches the filename version, one balanced parenthetical annotation follows, and the annotation leading lifecycle token matches the artifact status; preserve exact modern Version: NNN authoring as the only current writer form.
- Retain fail-closed rejection for wrong numeric prefixes, missing or multiple Version fields, multiple or nested parentheticals, non-parenthetical or trailing text, annotation/status disagreement, malformed roles or statuses, gaps, cross-thread links, wrong-document links, non-adjacent links, ambiguity, and multiply malformed chains.
- Add resolver unit coverage and schema-v3 implementation-authorization no-write coverage for WI-5554, WI-5438, WI-5474, research-clean-branch-publication, strict modern chains, and negative boundary fixtures.
- Do not rewrite historical bridge files or mutate scripts/implementation_authorization.py, dispatcher configuration/runtime, claims or leases except the exact future implementation claim/start path, MemBase, credentials, Git/index/refs, push, deployment, release, or unrelated bytes.

## Cross-Harness Disposition

- **A**: Prime Builder only; no role change, self-review, or direct harness contact.
- **B**: Harness-neutral lifecycle consumer; no direct routing or provider mutation.
- **C**: Harness-neutral lifecycle consumer; no direct routing or provider mutation.
- **D**: Harness-neutral lifecycle consumer; no direct routing or provider mutation.
- **E**: Harness-neutral lifecycle consumer; no direct routing or provider mutation.
- **F**: Harness-neutral lifecycle consumer; no direct routing or provider mutation.
- **H**: Harness-neutral lifecycle consumer; no direct routing or provider mutation.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5637; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Historical canonical bridge artifacts such as WI-5554 v005, WI-5438 v005, WI-5474 v002, and research-clean-branch-publication carry a numeric Version value followed by a parenthetical status or report annotation. The public bridge lifecycle resolver currently requires exact digits and fails schema-v3 implementation authorization before a later strict GO can be evaluated. Add a bounded compatibility rule only after terminal WI-5629 and WI-5636: accept a filename-matching three-digit prefix followed by one historical parenthetical annotation when document identity, role/status, adjacency, and linkage remain valid; reject wrong numeric prefixes, arbitrary suffixes, duplicate Version fields, non-parenthetical text, cross-thread or malformed chains, and all ambiguity. Do not rewrite historical artifacts or weaken strict current-authoring requirements.",
  "after_behavior": "Accept only bounded historical decorated Version metadata after terminal WI-5629 and WI-5636 while preserving strict bridge-history denial and exact modern authoring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5637",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "scripts/bridge_lifecycle_resolver.py",
      "platform_tests/scripts/test_bridge_lifecycle_resolver.py",
      "platform_tests/scripts/test_implementation_authorization.py"
    ],
    "linked_specifications": [
      "DCL-VERIFIED-BRIDGE-HISTORY-001",
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
    "summary": "Accept only bounded historical decorated Version metadata after terminal WI-5629 and WI-5636 while preserving strict bridge-history denial and exact modern authoring.",
    "scope": [
      "Hard-depend on WI-5629 and WI-5636 reaching terminal VERIFIED with no live implementation claims; consume their public resolver contract without broadening either predecessor.",
      "Recognize one historical Version form only when the three-digit numeric prefix matches the filename version, one balanced parenthetical annotation follows, and the annotation leading lifecycle token matches the artifact status; preserve exact modern Version: NNN authoring as the only current writer form.",
      "Retain fail-closed rejection for wrong numeric prefixes, missing or multiple Version fields, multiple or nested parentheticals, non-parenthetical or trailing text, annotation/status disagreement, malformed roles or statuses, gaps, cross-thread links, wrong-document links, non-adjacent links, ambiguity, and multiply malformed chains.",
      "Add resolver unit coverage and schema-v3 implementation-authorization no-write coverage for WI-5554, WI-5438, WI-5474, research-clean-branch-publication, strict modern chains, and negative boundary fixtures.",
      "Do not rewrite historical bridge files or mutate scripts/implementation_authorization.py, dispatcher configuration/runtime, claims or leases except the exact future implementation claim/start path, MemBase, credentials, Git/index/refs, push, deployment, release, or unrelated bytes."
    ],
    "acceptance_criteria": [
      "After WI-5629 and WI-5636 are terminal VERIFIED and unclaimed, exact historical decorated-Version chains resolve only when filename version, artifact status, document identity, role, transition, adjacency, and linkage all agree.",
      "TEST-11682 proves wrong prefixes, arbitrary or non-parenthetical suffixes, annotation/status disagreement, duplicate Version fields, nested or multiple annotations, malformed roles/statuses, cross-thread links, gaps, non-adjacent links, and ambiguous chains fail closed before packet creation or protected mutation.",
      "Strict modern Version: NNN chains and the WI-5629/WI-5636 compatibility cases remain green, and current bridge writers continue emitting exact modern Version metadata only.",
      "Only the three declared source/test targets may change after independent GO, exact claim, and implementation-start authorization; implementation and verification use hunk-scoped evidence and preserve all foreign dirty bytes."
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
| `DCL-VERIFIED-BRIDGE-HISTORY-001` | Run TEST-11682 resolver and schema-v3 integration coverage against exact historical and negative decorated-Version fixtures. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Prove independent GO, exact claim, implementation-start authorization, append-only bridge history, and no historical rewrite. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run complete resolver and implementation-authorization regression modules, Ruff, format check, compile, and exact live no-write acceptance before independent VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- After WI-5629 and WI-5636 are terminal VERIFIED and unclaimed, exact historical decorated-Version chains resolve only when filename version, artifact status, document identity, role, transition, adjacency, and linkage all agree.
- TEST-11682 proves wrong prefixes, arbitrary or non-parenthetical suffixes, annotation/status disagreement, duplicate Version fields, nested or multiple annotations, malformed roles/statuses, cross-thread links, gaps, non-adjacent links, and ambiguous chains fail closed before packet creation or protected mutation.
- Strict modern Version: NNN chains and the WI-5629/WI-5636 compatibility cases remain green, and current bridge writers continue emitting exact modern Version metadata only.
- Only the three declared source/test targets may change after independent GO, exact claim, and implementation-start authorization; implementation and verification use hunk-scoped evidence and preserve all foreign dirty bytes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`feat`
