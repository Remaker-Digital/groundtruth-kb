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

# Implementation Proposal - Repair malformed provider model-provenance normalization literals

bridge_kind: prime_proposal
Document: gtkb-wi5605-provider-model-provenance-literal-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5605

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the malformed newline string literals in the current WI-5422 provider model-provenance normalization hunk so the governed provider writer imports again, without adopting or changing any unrelated shared dirty bytes.

Work item description: Current shared source scripts/gtkb_bridge_writer.py contains an unterminated string literal inside the uncommitted WI-5422 provider runtime model-metadata normalization block: intended newline escape sequences were materialized as physical newlines inside quoted Python strings. Python compilation and provider publisher imports fail, blocking both OpenRouter F and Ollama D governed verdict publication. Repair only the malformed newline literals while preserving the approved WI-5422 model-field normalization semantics, strict identity/harness/session conflict checks, bridge guards, concurrent foreign hunks, current dispatcher topology, and live worker state.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5605` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py`, `platform_tests/scripts/test_gtkb_bridge_writer.py`.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
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
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265375` - Verdict
- `DELIB-202666128` - gtkb-wi5181-report-metrics-enrichment — Loyal Opposition Verdict (VERIFIED)
- `DELIB-202666472` - Verdict
- `DELIB-202666708` - LO Review - WI-5383 Require Implementation and Commit Evidence Before VERIFIED Backlog Closure
- `DELIB-202666063` - Verification Verdict - WI-5107 bridge-helper no-window subprocess (NO-GO)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5605`.

## Proposed Scope

- After all live workers release the exact targets, repair only the malformed newline literals and preserve the intended split, strip, and join semantics.
- Preserve every concurrent foreign hunk byte-for-byte; do not format, refactor, or adopt unrelated writer or test changes.
- Add or adjust only the minimum focused regression necessary to prove the exact literal repair.
- Do not mutate dispatcher or TAFE configuration/runtime, roles, eligibility, caps, leases, credentials, Git state, deployment, release, or external systems.

## Cross-Harness Disposition

- **A**: Prime Builder only; implementation requires independent GO, matching claim, and implementation-start authorization.
- **D**: Operative Ollama LO consumer; verify import and governed publication compatibility without topology changes.
- **F**: Operative OpenRouter LO consumer; verify import and governed publication compatibility without topology changes.
- **B**: Parity consumer only; no dispatcher or runtime change.
- **C**: Parity consumer only; no dispatcher or runtime change.
- **E**: Parity consumer only; no dispatcher or runtime change.
- **H**: Parity consumer only; no dispatcher or runtime change.
- **G**: No installed harness; retired registry residue only and no implementation target.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5605; PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Current shared source scripts/gtkb_bridge_writer.py contains an unterminated string literal inside the uncommitted WI-5422 provider runtime model-metadata normalization block: intended newline escape sequences were materialized as physical newlines inside quoted Python strings. Python compilation and provider publisher imports fail, blocking both OpenRouter F and Ollama D governed verdict publication. Repair only the malformed newline literals while preserving the approved WI-5422 model-field normalization semantics, strict identity/harness/session conflict checks, bridge guards, concurrent foreign hunks, current dispatcher topology, and live worker state.",
  "after_behavior": "Repair the malformed newline string literals in the current WI-5422 provider model-provenance normalization hunk so the governed provider writer imports again, without adopting or changing any unrelated shared dirty bytes.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5605",
    "project": "PROJECT-GTKB-GOOSE-HARNESS-ADOPTION",
    "target_paths": [
      "scripts/gtkb_bridge_writer.py",
      "platform_tests/scripts/test_gtkb_bridge_writer.py"
    ],
    "linked_specifications": [
      "GOV-DOCUMENT-AUTHOR-PROVENANCE-001",
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
      "GOV-HARNESS-ONBOARDING-CONTRACT-001"
    ]
  },
  "expected_result": {
    "summary": "Repair the malformed newline string literals in the current WI-5422 provider model-provenance normalization hunk so the governed provider writer imports again, without adopting or changing any unrelated shared dirty bytes.",
    "scope": [
      "After all live workers release the exact targets, repair only the malformed newline literals and preserve the intended split, strip, and join semantics.",
      "Preserve every concurrent foreign hunk byte-for-byte; do not format, refactor, or adopt unrelated writer or test changes.",
      "Add or adjust only the minimum focused regression necessary to prove the exact literal repair.",
      "Do not mutate dispatcher or TAFE configuration/runtime, roles, eligibility, caps, leases, credentials, Git state, deployment, release, or external systems."
    ],
    "acceptance_criteria": [
      "TEST-11651: scripts/gtkb_bridge_writer.py compiles and platform_tests/scripts/test_gtkb_bridge_writer.py passes.",
      "Trusted author_model, author_model_version, and author_model_configuration fields normalize while identity, harness, and session conflicts remain denied.",
      "Focused cloud and Ollama provider import/publication tests pass without changing dispatcher topology.",
      "The attributable implementation diff contains only the exact malformed-literal repair and its minimum regression; all foreign dirty bytes remain excluded."
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
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Run the focused bridge-writer normalization tests proving trusted runtime model metadata replacement and strict identity, harness, and session conflict denial. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Compile the writer and run its focused publication suite to prove governed verdict publication remains importable and authorization guards remain enforced. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute linked TEST-11651 and report exact commands and observed results before independent verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run focused cloud and Ollama provider suites to prove both operative provider adapters retain governed publication compatibility. |

## Acceptance Criteria

- TEST-11651: scripts/gtkb_bridge_writer.py compiles and platform_tests/scripts/test_gtkb_bridge_writer.py passes.
- Trusted author_model, author_model_version, and author_model_configuration fields normalize while identity, harness, and session conflicts remain denied.
- Focused cloud and Ollama provider import/publication tests pass without changing dispatcher topology.
- The attributable implementation diff contains only the exact malformed-literal repair and its minimum regression; all foreign dirty bytes remain excluded.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Recommended Commit Type

`feat`
