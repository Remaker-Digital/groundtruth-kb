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

# Implementation Proposal - Resolve exact historical Responds-to-GO implementation-report linkage without weakening strict denial

bridge_kind: prime_proposal
Document: gtkb-wi5636-exact-responds-to-go-history-compatibility
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5636

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Bound the exact historical Responds-to-GO implementation-report linkage in WI-5627 to a strict, role-correct, adjacent compatibility rule after terminal WI-5629, without weakening ordinary unlinked-history denial.

Work item description: WI-5627 version 003 is a strict NEW implementation report that links to its exact approved GO with the historical metadata key 'Responds to GO:' instead of canonical 'Responds to:'. Versions 004, 005, and 006 are strict and adjacent, but schema-v3 implementation authorization fails closed at v003 with Responds-to=None before the fresh v006 GO can authorize the two-file repair. Preserve this as a separate exact-history compatibility correction after terminal WI-5629. Accept only a bounded, role-correct, document-correct, adjacent implementation-report-to-exact-GO link proven by the historical key and later strict chain; retain fail-closed denial for missing, wrong, cross-thread, ambiguous, duplicated, non-adjacent, wrong-role, or arbitrary alternative metadata. Do not rewrite historical bridge artifacts or weaken ordinary unlinked-history denial.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5636` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

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
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666479` - Loyal Opposition Corrected Verdict - NO-GO - WI-5307 Shared Enforcement Baseline Disposition
- `DELIB-20263302` - Reconciler WI→Bridge Linkage Derivation Proposal Review
- `DELIB-20264286` - Loyal Opposition Review - LO Bridge History Backfill Slice 1 Blocker Acknowledgement
- `DELIB-2774` - Loyal Opposition Review - LO Bridge History Backfill Slice 1 Blocker Acknowledgement
- `DELIB-202666976` - Loyal Opposition Review — WI-5353 Implementation-Start Harness Selector

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5636`.

## Proposed Scope

- Hard-depend on WI-5629 terminal VERIFIED and an absent WI-5629 claim; consume its public exact-thread lifecycle resolver contract only after that boundary is satisfied.
- Recognize the historical 'Responds to GO:' key only on a strict Prime Builder implementation_report whose exact value names the immediately preceding strict GO in the same exact numbered thread, with no canonical 'Responds to:' field or conflicting alternative metadata.
- Require the complete WI-5627 v001-v006 chain to remain contiguous, document-correct, version-correct, role-correct, and transition-correct; retain fail-closed rejection for missing, wrong, cross-thread, duplicate, non-adjacent, wrong-role, ambiguous, or arbitrary alternative linkage.
- Add resolver unit coverage plus implementation-authorization schema-v3 no-write integration coverage for the exact historical shape and its negative boundary.
- Do not rewrite historical bridge artifacts or mutate scripts/implementation_authorization.py, dispatcher configuration/runtime, claims/leases, MemBase, credentials, Git/index/refs, deployment, release, push, or unrelated bytes.

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
  "provenance": "WI-5636; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5627 version 003 is a strict NEW implementation report that links to its exact approved GO with the historical metadata key 'Responds to GO:' instead of canonical 'Responds to:'. Versions 004, 005, and 006 are strict and adjacent, but schema-v3 implementation authorization fails closed at v003 with Responds-to=None before the fresh v006 GO can authorize the two-file repair. Preserve this as a separate exact-history compatibility correction after terminal WI-5629. Accept only a bounded, role-correct, document-correct, adjacent implementation-report-to-exact-GO link proven by the historical key and later strict chain; retain fail-closed denial for missing, wrong, cross-thread, ambiguous, duplicated, non-adjacent, wrong-role, or arbitrary alternative metadata. Do not rewrite historical bridge artifacts or weaken ordinary unlinked-history denial.",
  "after_behavior": "Bound the exact historical Responds-to-GO implementation-report linkage in WI-5627 to a strict, role-correct, adjacent compatibility rule after terminal WI-5629, without weakening ordinary unlinked-history denial.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5636",
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-PROJECT-DEPENDENCY-ORDERING-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Bound the exact historical Responds-to-GO implementation-report linkage in WI-5627 to a strict, role-correct, adjacent compatibility rule after terminal WI-5629, without weakening ordinary unlinked-history denial.",
    "scope": [
      "Hard-depend on WI-5629 terminal VERIFIED and an absent WI-5629 claim; consume its public exact-thread lifecycle resolver contract only after that boundary is satisfied.",
      "Recognize the historical 'Responds to GO:' key only on a strict Prime Builder implementation_report whose exact value names the immediately preceding strict GO in the same exact numbered thread, with no canonical 'Responds to:' field or conflicting alternative metadata.",
      "Require the complete WI-5627 v001-v006 chain to remain contiguous, document-correct, version-correct, role-correct, and transition-correct; retain fail-closed rejection for missing, wrong, cross-thread, duplicate, non-adjacent, wrong-role, ambiguous, or arbitrary alternative linkage.",
      "Add resolver unit coverage plus implementation-authorization schema-v3 no-write integration coverage for the exact historical shape and its negative boundary.",
      "Do not rewrite historical bridge artifacts or mutate scripts/implementation_authorization.py, dispatcher configuration/runtime, claims/leases, MemBase, credentials, Git/index/refs, deployment, release, push, or unrelated bytes."
    ],
    "acceptance_criteria": [
      "After WI-5629 is terminal VERIFIED and unclaimed, the exact live WI-5627 v001-v006 chain resolves v005 as the implementation artifact and v006 as its GO, and schema-v3 implementation authorization begin --no-write succeeds under a fresh exact WI-5627 claim without writing a packet.",
      "TEST-11681 proves absent, wrong, cross-thread, duplicate, non-adjacent, wrong-role, ambiguous, conflicting canonical-plus-historical, and arbitrary alternative metadata fail closed before packet creation or protected mutation.",
      "Ordinary strict Responds-to chains and the WI-5629 corrected malformed-verdict chain remain green; the compatibility path is operation-neutral and exact-history bounded.",
      "Only the three declared source/test targets may change after independent GO, exact claim, and implementation-start authorization; all foreign dirty bytes remain quarantined."
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
| `DCL-VERIFIED-BRIDGE-HISTORY-001` | Run TEST-11681 unit and schema-v3 integration coverage against exact WI-5627 v001-v006 bytes and all negative linkage fixtures. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Prove exact independent GO, matching claim, schema-v3 implementation-start authorization, no-write denial ordering, and append-only bridge history. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete resolver and implementation-authorization regression modules, Ruff, format check, compile, and exact live no-write acceptance before independent VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Re-read the live numbered WI-5627 and WI-5629 chains, exact target hashes, active PAUTH, claim state, and resolver bytes immediately before implementation and verification. |
| `GOV-WORK-TREE-HYGIENE-001` | Use a new canonical hunk patch and hash ledger to isolate only WI-5636 changes from commingled foreign bytes; perform no whole-file staging. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- After WI-5629 is terminal VERIFIED and unclaimed, the exact live WI-5627 v001-v006 chain resolves v005 as the implementation artifact and v006 as its GO, and schema-v3 implementation authorization begin --no-write succeeds under a fresh exact WI-5627 claim without writing a packet.
- TEST-11681 proves absent, wrong, cross-thread, duplicate, non-adjacent, wrong-role, ambiguous, conflicting canonical-plus-historical, and arbitrary alternative metadata fail closed before packet creation or protected mutation.
- Ordinary strict Responds-to chains and the WI-5629 corrected malformed-verdict chain remain green; the compatibility path is operation-neutral and exact-history bounded.
- Only the three declared source/test targets may change after independent GO, exact claim, and implementation-start authorization; all foreign dirty bytes remain quarantined.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`feat`
