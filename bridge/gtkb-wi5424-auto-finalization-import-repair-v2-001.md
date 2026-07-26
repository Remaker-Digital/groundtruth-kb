NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder
author_metadata_source: codex-system-runtime

# Implementation Proposal - Make auto-finalization honor canonical verdict validation and bounded Git execution

bridge_kind: prime_proposal
Document: gtkb-wi5424-auto-finalization-import-repair-v2
Version: 001
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

target_paths: ["scripts/auto_finalize_sweep.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the live P1 auto-finalization break with the smallest current-byte scope. The sweep points at a retired skill directory, so canonical verdict validation is unavailable and 97 skip events affected three unique VERIFIED verdicts. The historical WI-5424 chain is non-authorizing because its exact hashes drifted and its GO lacks mandatory Responds-to linkage. This fresh thread changes only the import root and its focused regression test.

Work item description: The live three-path auto-finalization sweep hunk has no current owner: scripts/auto_finalize_sweep.py, platform_tests/hooks/test_auto_finalize_verified_verdicts.py, and .claude/rules/auto-finalization-sweep.md. It imports the canonical VERIFIED-body validator, runs the protected-commit authorization checker before attempting a commit, skips and audits legacy/incomplete terminal verdicts that require per-thread repair, and bounds every Git subprocess with timeout-as-failure behavior so the Stop hook cannot hold the index indefinitely. Independently review and finalize only these safeguards. Exclude .claude/settings.json (WI-5391), per-thread repair paths (WI-5417), any live bridge chain, source staging/commit execution, dispatcher/harness mutation, groundtruth.db, and unrelated worktree content.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5424` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/auto_finalize_sweep.py`, `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`.

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
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666419` - Loyal Opposition NO-GO Verdict - WI-5237 WI-5229 PAUTH Configuration Coverage (stand-down disposition)
- `DELIB-202666402` - Loyal Opposition Corrected Verdict (review_no_action) - NO-GO - WI-5211 F Governed Publication Functional Proof
- `DELIB-202666599` - LO Review - WI-5370 Auto-Finalization Sweep Invalid-Body Guard
- `DELIB-202666370` - Loyal Opposition NO-GO Verdict - WI-5144 HP08 Semantic Adapter Drift (finalization-scoped)
- `DELIB-20265511` - Owner decision: pragmatic completion + retirement of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5424`.

## Proposed Scope

- Replace the absent .claude/skills/verify/helpers import root with the live .claude/skills/gtkb-verify/helpers root.
- Add a regression test that resolves and imports validate_verified_body from the canonical helper location.
- Preserve the sweep fail-soft control flow and existing bounded Git behavior; do not run the sweep or finalize any verdict.
- This proposal performs no KB or MemBase mutation and no groundtruth.db write.
- Exclude the stale rule reference, which remains owned by WI-5664, and exclude dispatcher, settings, bridge-history repair, Git, release, and deployment changes.

## Cross-Harness Disposition

- **Claude Stop hook**: Uses scripts/auto_finalize_sweep.py directly; repair applies without harness-local duplication.
- **Codex and other harnesses**: No hook registration change; shared source/test behavior only.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5424; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The live three-path auto-finalization sweep hunk has no current owner: scripts/auto_finalize_sweep.py, platform_tests/hooks/test_auto_finalize_verified_verdicts.py, and .claude/rules/auto-finalization-sweep.md. It imports the canonical VERIFIED-body validator, runs the protected-commit authorization checker before attempting a commit, skips and audits legacy/incomplete terminal verdicts that require per-thread repair, and bounds every Git subprocess with timeout-as-failure behavior so the Stop hook cannot hold the index indefinitely. Independently review and finalize only these safeguards. Exclude .claude/settings.json (WI-5391), per-thread repair paths (WI-5417), any live bridge chain, source staging/commit execution, dispatcher/harness mutation, groundtruth.db, and unrelated worktree content.",
  "after_behavior": "Repair the live P1 auto-finalization break with the smallest current-byte scope. The sweep points at a retired skill directory, so canonical verdict validation is unavailable and 97 skip events affected three unique VERIFIED verdicts. The historical WI-5424 chain is non-authorizing because its exact hashes drifted and its GO lacks mandatory Responds-to linkage. This fresh thread changes only the import root and its focused regression test.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5424",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "scripts/auto_finalize_sweep.py",
      "platform_tests/hooks/test_auto_finalize_verified_verdicts.py"
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
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "Repair the live P1 auto-finalization break with the smallest current-byte scope. The sweep points at a retired skill directory, so canonical verdict validation is unavailable and 97 skip events affected three unique VERIFIED verdicts. The historical WI-5424 chain is non-authorizing because its exact hashes drifted and its GO lacks mandatory Responds-to linkage. This fresh thread changes only the import root and its focused regression test.",
    "scope": [
      "Replace the absent .claude/skills/verify/helpers import root with the live .claude/skills/gtkb-verify/helpers root.",
      "Add a regression test that resolves and imports validate_verified_body from the canonical helper location.",
      "Preserve the sweep fail-soft control flow and existing bounded Git behavior; do not run the sweep or finalize any verdict.",
      "This proposal performs no KB or MemBase mutation and no groundtruth.db write.",
      "Exclude the stale rule reference, which remains owned by WI-5664, and exclude dispatcher, settings, bridge-history repair, Git, release, and deployment changes."
    ],
    "acceptance_criteria": [
      "The canonical validator imports from the live helper directory in production code.",
      "The focused regression test fails against the current stale path and passes after the repair.",
      "All existing focused auto-finalization tests remain green and no third implementation path changes."
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
| `DCL-VERIFIED-BRIDGE-HISTORY-001` | Run focused import and invalid-verdict skip tests; validator availability no longer causes a blanket skip. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Recompute exact target diff, lifecycle validity, current project authorization, claim, and implementation-start evidence before mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Run the complete focused test module plus ruff check and format check on the two targets. |

## Acceptance Criteria

- The canonical validator imports from the live helper directory in production code.
- The focused regression test fails against the current stale path and passes after the repair.
- All existing focused auto-finalization tests remain green and no third implementation path changes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/auto_finalize_sweep.py`
- `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`

## Recommended Commit Type

`feat`
