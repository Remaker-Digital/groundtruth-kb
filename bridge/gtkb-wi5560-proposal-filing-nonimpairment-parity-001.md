NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh;sandbox=none
author_metadata_source: Codex request metadata

# Implementation Proposal - Make bridge proposal filing dry-run enforce and render modernization nonimpairment disposition

bridge_kind: prime_proposal
Document: gtkb-wi5560-proposal-filing-nonimpairment-parity
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5560

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/tests/test_cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair proposal filing so structured modernization nonimpairment evidence is rendered deterministically and dry-run enforces the same governed compliance decision as live filing.

Work item description: gt bridge file-implementation-proposal --dry-run reports applicability and ADR/DCL preflights passing for a proposal that cites GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, but the identical live filing fails at the bridge-compliance audit because proposal_filing._build_content has no supported field or renderer for the mandatory structured ## Intuitiveness/Non-Impairment Disposition JSON object. Add a validated structured input/model and deterministic renderer, run the same audit-only compliance gate against dry-run candidate bytes that live filing uses, and require dry-run/live pass-or-fail parity. Preserve governed writer, claim, author provenance, PAUTH, preflight, dispatcher/TAFE publication, and fail-closed behavior; do not add a force/bypass path.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5560` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`, `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`, `groundtruth-kb/tests/test_cli_bridge_propose.py`, `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
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

- `DELIB-202666121` - Verdict
- `DELIB-202665577` - Applicability Preflight
- `DELIB-202665608` - Applicability Preflight
- `DELIB-202666197` - Loyal Opposition NO-GO Verdict: gtkb-wi5223-dispatch-eligibility-precedence
- `DELIB-202666179` - WI-5213 - Loyal Opposition Corrected Verdict (review_no_action): GO

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5560`.

## Proposed Scope

- Adopt the current deterministic nonimpairment renderer and implementation-template placeholder only after independent review and exact preimage revalidation.
- Prepare one author-metadata-complete, envelope-normalized candidate through a shared audit path so dry-run and live filing evaluate identical proposal bytes.
- Run the governed bridge compliance audit during dry-run without writing bridge, dispatcher, TAFE, claim, or other runtime state; preserve the existing live non-bypass writer and fail-closed publication ordering.
- Add focused regressions for valid candidate audit, missing/empty/TODO disposition denial, and dry-run/live pass-or-fail parity.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5560; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "gt bridge file-implementation-proposal --dry-run reports applicability and ADR/DCL preflights passing for a proposal that cites GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, but the identical live filing fails at the bridge-compliance audit because proposal_filing._build_content has no supported field or renderer for the mandatory structured ## Intuitiveness/Non-Impairment Disposition JSON object. Add a validated structured input/model and deterministic renderer, run the same audit-only compliance gate against dry-run candidate bytes that live filing uses, and require dry-run/live pass-or-fail parity. Preserve governed writer, claim, author provenance, PAUTH, preflight, dispatcher/TAFE publication, and fail-closed behavior; do not add a force/bypass path.",
  "after_behavior": "Repair proposal filing so structured modernization nonimpairment evidence is rendered deterministically and dry-run enforces the same governed compliance decision as live filing.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5560",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py",
      "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py",
      "groundtruth-kb/tests/test_cli_bridge_propose.py",
      "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"
    ],
    "linked_specifications": [
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
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
    "summary": "Repair proposal filing so structured modernization nonimpairment evidence is rendered deterministically and dry-run enforces the same governed compliance decision as live filing.",
    "scope": [
      "Adopt the current deterministic nonimpairment renderer and implementation-template placeholder only after independent review and exact preimage revalidation.",
      "Prepare one author-metadata-complete, envelope-normalized candidate through a shared audit path so dry-run and live filing evaluate identical proposal bytes.",
      "Run the governed bridge compliance audit during dry-run without writing bridge, dispatcher, TAFE, claim, or other runtime state; preserve the existing live non-bypass writer and fail-closed publication ordering.",
      "Add focused regressions for valid candidate audit, missing/empty/TODO disposition denial, and dry-run/live pass-or-fail parity."
    ],
    "acceptance_criteria": [
      "Dry-run returns only after the same compliance audit used by live filing passes against identical author-metadata-complete and envelope-normalized bytes, while creating no bridge file or publication state.",
      "Malformed, missing, empty, or placeholder nonimpairment fields fail before any write in both dry-run and live modes with equivalent compliance classification.",
      "The focused proposal-filing suites, Ruff lint/format, candidate/live applicability, mandatory-clause preflights, and git diff --check pass.",
      "No force or bypass path is introduced; PAUTH, work-intent claim, author provenance, credential scan, dispatcher/TAFE publication, and unrelated dirty paths remain unchanged."
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
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Exercise deterministic disposition rendering and fail-closed validation in both dry-run and live paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Prove dry-run is write-free and live filing still uses the governed non-bypass writer with exact role-author metadata. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused unit/platform regression suites plus lint, format, applicability, clause, and whitespace checks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Dry-run returns only after the same compliance audit used by live filing passes against identical author-metadata-complete and envelope-normalized bytes, while creating no bridge file or publication state.
- Malformed, missing, empty, or placeholder nonimpairment fields fail before any write in both dry-run and live modes with equivalent compliance classification.
- The focused proposal-filing suites, Ruff lint/format, candidate/live applicability, mandatory-clause preflights, and git diff --check pass.
- No force or bypass path is introduced; PAUTH, work-intent claim, author provenance, credential scan, dispatcher/TAFE publication, and unrelated dirty paths remain unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `groundtruth-kb/tests/test_cli_bridge_propose.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`

## Recommended Commit Type

`feat`
