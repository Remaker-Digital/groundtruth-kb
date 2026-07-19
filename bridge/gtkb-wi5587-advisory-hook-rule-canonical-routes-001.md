NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Retarget canonical advisory hooks and LO rules to governed carriers

bridge_kind: prime_proposal
Document: gtkb-wi5587-advisory-hook-rule-canonical-routes
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5587-ADVISORY-HOOK-RULES-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5587-ADVISORY-HOOK-RULES-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5587

target_paths: [".claude/hooks/advisory-router-scan.py", ".claude/rules/deliberation-protocol.md", ".claude/rules/codex-loyal-opposition-runbook.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Retarget canonical advisory routing and Loyal Opposition rule guidance so durable advisory capture uses numbered bridge ADVISORY entries, Advisory Proposal, the Deliberation Archive, and MemBase according to artifact purpose while preserving explicit tombstone prohibitions. This build session may file only the proposal and metadata; a separate future ops activity envelope is mandatory for configuration mutation.

Work item description: Ops activity-envelope child of WI-5582. Mutate exactly .claude/hooks/advisory-router-scan.py, .claude/rules/deliberation-protocol.md, and .claude/rules/codex-loyal-opposition-runbook.md. Retarget Stop-hook advisory collection to numbered bridge ADVISORY entries and replace rule instructions that direct reports or startup reads to the owner-retired carrier with Advisory Proposal, Deliberation Archive, MemBase, and numbered bridge routes. Preserve explicit tombstone prohibitions. Source scripts, tests, dispatcher configuration, TAFE state, runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and all other paths are excluded.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5587` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/advisory-router-scan.py`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/codex-loyal-opposition-runbook.md`.

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - auto-linked governing or work-item specification.
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
- `ADR-0001` - auto-linked governing or work-item specification.
- `SPEC-2098` - auto-linked governing or work-item specification.
- `DCL-ADVISORY-ROUTING-001` - auto-linked governing or work-item specification.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - auto-linked governing or work-item specification.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - auto-linked governing or work-item specification.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-2207` - WI-3298 disposition: monitor (bridge advisory report message type advisory adopted via 5 VERIFIED conversion threads)
- `DELIB-202665189` - NO-GO: WI-4944 -- v013 blocker report confirms unresolved topology authority gap; owner decision still required
- `DELIB-202666362` - GT-KB WI-5142 Bounded Registry Readiness Repair — Corrected Loyal Opposition Verdict (terminal-conflicting and dependency-blocked GO)
- `DELIB-20263265` - Loyal Opposition Verification: WI-4509 Cutover Evidence Gathering
- `DELIB-202665988` - Loyal Opposition Verdict - WI-4841 Parent Route-Record Completion (VERIFIED)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5587-ADVISORY-HOOK-RULES-2026-07-18` - active project authorization covering `WI-5587`.

## Proposed Scope

- In this build session, file only this governed proposal and project or MemBase linkage; do not mutate any configuration target.
- In a separate future ops activity envelope after independent GO, exact claim, and schema-v3 start, update the Stop-hook advisory router to emit or validate numbered bridge ADVISORY entries through the canonical bridge path.
- In that ops session, update the two Loyal Opposition rule documents so durable findings route to Advisory Proposal, Deliberation Archive, MemBase, or numbered bridge artifacts according to their lifecycle purpose.
- Preserve explicit tombstone prohibitions and remove no historical evidence; do not make a retired or noncanonical carrier a live dependency.
- Do not inspect or mutate dispatcher configuration, TAFE state, runtime state, source, tests, credentials, deployment, release, Git history, or any path outside the three exact targets.

## Cross-Harness Disposition

- **hook.advisory-router-scan**: Retarget the canonical Stop-hook advisory route without changing hook registration, dispatcher configuration, or runtime state.
- **Loyal Opposition surfaces**: Keep Claude, Codex, Cursor, Antigravity, Ollama, and OpenRouter guidance aligned on the same canonical carrier hierarchy and role boundary.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5587; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5587-ADVISORY-HOOK-RULES-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Ops activity-envelope child of WI-5582. Mutate exactly .claude/hooks/advisory-router-scan.py, .claude/rules/deliberation-protocol.md, and .claude/rules/codex-loyal-opposition-runbook.md. Retarget Stop-hook advisory collection to numbered bridge ADVISORY entries and replace rule instructions that direct reports or startup reads to the owner-retired carrier with Advisory Proposal, Deliberation Archive, MemBase, and numbered bridge routes. Preserve explicit tombstone prohibitions. Source scripts, tests, dispatcher configuration, TAFE state, runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and all other paths are excluded.",
  "after_behavior": "Retarget canonical advisory routing and Loyal Opposition rule guidance so durable advisory capture uses numbered bridge ADVISORY entries, Advisory Proposal, the Deliberation Archive, and MemBase according to artifact purpose while preserving explicit tombstone prohibitions. This build session may file only the proposal and metadata; a separate future ops activity envelope is mandatory for configuration mutation.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5587",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      ".claude/hooks/advisory-router-scan.py",
      ".claude/rules/deliberation-protocol.md",
      ".claude/rules/codex-loyal-opposition-runbook.md"
    ],
    "linked_specifications": [
      "DCL-CANONICAL-CARRIER-NONAUTHORITY-001",
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
      "ADR-0001",
      "SPEC-2098",
      "DCL-ADVISORY-ROUTING-001",
      "SPEC-ADVISORY-REPORT-TEMPLATE-001",
      "GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001",
      "DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001"
    ]
  },
  "expected_result": {
    "summary": "Retarget canonical advisory routing and Loyal Opposition rule guidance so durable advisory capture uses numbered bridge ADVISORY entries, Advisory Proposal, the Deliberation Archive, and MemBase according to artifact purpose while preserving explicit tombstone prohibitions. This build session may file only the proposal and metadata; a separate future ops activity envelope is mandatory for configuration mutation.",
    "scope": [
      "In this build session, file only this governed proposal and project or MemBase linkage; do not mutate any configuration target.",
      "In a separate future ops activity envelope after independent GO, exact claim, and schema-v3 start, update the Stop-hook advisory router to emit or validate numbered bridge ADVISORY entries through the canonical bridge path.",
      "In that ops session, update the two Loyal Opposition rule documents so durable findings route to Advisory Proposal, Deliberation Archive, MemBase, or numbered bridge artifacts according to their lifecycle purpose.",
      "Preserve explicit tombstone prohibitions and remove no historical evidence; do not make a retired or noncanonical carrier a live dependency.",
      "Do not inspect or mutate dispatcher configuration, TAFE state, runtime state, source, tests, credentials, deployment, release, Git history, or any path outside the three exact targets."
    ],
    "acceptance_criteria": [
      "The filed proposal changes no configuration bytes and records the build-now versus ops-later activity-envelope boundary explicitly.",
      "Future implementation changes exactly the three declared clean targets and starts only under an ops envelope with current GO, exact claim, and schema-v3 target authorization.",
      "The Stop hook routes durable advisory capture through numbered canonical ADVISORY bridge entries without creating an alternate queue or noncanonical dependency.",
      "Both rule documents direct durable information to Advisory Proposal, Deliberation Archive, MemBase, or numbered bridge artifacts according to artifact purpose.",
      "Explicit tombstone prohibitions remain, and no canonical bridge artifact cites a noncanonical carrier as authority.",
      "Existing hook-parity, cross-harness protocol, governance-adoption, scaffold-rule, and doctor-accuracy checks pass with no dispatcher or runtime mutation."
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
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Inspect the exact three-file diff and deterministic text assertions; no instruction or hook path treats a noncanonical carrier as live authority. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
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
| `ADR-0001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-2098` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ADVISORY-ROUTING-001` | Exercise the advisory router in isolated fixtures and confirm durable output is a numbered bridge ADVISORY entry through the canonical route. |
| `SPEC-ADVISORY-REPORT-TEMPLATE-001` | Inspect generated advisory content and rule guidance for the required canonical Advisory Proposal structure and lifecycle routing. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The filed proposal changes no configuration bytes and records the build-now versus ops-later activity-envelope boundary explicitly.
- Future implementation changes exactly the three declared clean targets and starts only under an ops envelope with current GO, exact claim, and schema-v3 target authorization.
- The Stop hook routes durable advisory capture through numbered canonical ADVISORY bridge entries without creating an alternate queue or noncanonical dependency.
- Both rule documents direct durable information to Advisory Proposal, Deliberation Archive, MemBase, or numbered bridge artifacts according to artifact purpose.
- Explicit tombstone prohibitions remain, and no canonical bridge artifact cites a noncanonical carrier as authority.
- Existing hook-parity, cross-harness protocol, governance-adoption, scaffold-rule, and doctor-accuracy checks pass with no dispatcher or runtime mutation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/hooks/advisory-router-scan.py`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/codex-loyal-opposition-runbook.md`

## Recommended Commit Type

`feat`
