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

# Implementation Proposal - Batch Git range secret scanning for large pre-push updates

bridge_kind: prime_proposal
Document: gtkb-wi5613-large-range-secret-scan-batching
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5613

target_paths: ["groundtruth-kb/src/groundtruth_kb/secrets/scanner.py", "platform_tests/groundtruth_kb/test_secrets_scanner.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the canonical pre-push secret scanner's large-range timeout by batching Git object reads without weakening redaction, allowlisting, or fail-closed behavior.

Work item description: The canonical pre-push gate invokes a redacted range secret scan with a fixed 300-second wrapper. Pushing local main over origin/main currently covers 1,314 commits and approximately 6,900 changed paths; scan_range launches one git show subprocess per path, exceeds the wrapper timeout, and returns hard-inconclusive. Replace per-path blob reads with deterministic batched Git object reads while preserving exact head-side content, skip, redaction, allowlist, and fail-closed behavior. Bound implementation to groundtruth-kb/src/groundtruth_kb/secrets/scanner.py and focused scanner/preflight tests; do not alter dispatcher configuration, runtime state, credentials, remote refs, or push during implementation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5613` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/secrets/scanner.py`, `platform_tests/groundtruth_kb/test_secrets_scanner.py`.

## Specification Links

- `SPEC-SEC-SCANNER-CLI-001` - auto-linked governing or work-item specification.
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
- `SPEC-SEC-SCAN-REDACTION-001` - auto-linked governing or work-item specification.
- `SPEC-SEC-ALLOWLIST-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-1658` - Loyal Opposition Review - GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT Slice 1 Proposal
- `DELIB-202666141` - Loyal Opposition Verdict — WI-5189 Document-Authoritative GO-Implementation Claim Eligibility (REVISED-005 second scope expansion to eight paths)
- `DELIB-20266530` - Review Independence
- `DELIB-202666104` - Loyal Opposition VERIFIED verdict — WI-5132 tolerate genuine version gaps in VERIFIED finalization
- `DELIB-20263114` - FAB-04 Storage Reclamation - Verification Verdict

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5613`.

## Proposed Scope

- Replace scan_range per-path git show subprocesses with one deterministic head-tree enumeration and one git cat-file --batch stream.
- Preserve head-side blob semantics, per-path allowlist checks, redacted-only findings, excluded path handling, binary skipping, deleted-path skipping, duplicate-blob path attribution, and fail-closed Git errors.
- Add focused unit/integration coverage only in platform_tests/groundtruth_kb/test_secrets_scanner.py; do not modify the 300-second preflight timeout unless evidence shows batching alone is insufficient.
- Do not alter dispatcher configuration, TAFE/runtime state, harness roles or eligibility, credentials, remote refs, Git history, deployment, or release.

## Cross-Harness Disposition

- **A**: Shared Python scanner behavior; no Codex-specific adapter change.
- **B**: Shared Python scanner behavior; no Claude-specific adapter change.
- **C**: Shared Python scanner behavior; no Antigravity-specific adapter change.
- **D**: Shared Python scanner behavior; no Ollama-specific adapter change.
- **E**: Shared Python scanner behavior; no Cursor-specific adapter change.
- **F**: Shared Python scanner behavior; no OpenRouter-specific adapter change.
- **H**: Shared Python scanner behavior; no Alibaba-specific adapter change.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5613; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The canonical pre-push gate invokes a redacted range secret scan with a fixed 300-second wrapper. Pushing local main over origin/main currently covers 1,314 commits and approximately 6,900 changed paths; scan_range launches one git show subprocess per path, exceeds the wrapper timeout, and returns hard-inconclusive. Replace per-path blob reads with deterministic batched Git object reads while preserving exact head-side content, skip, redaction, allowlist, and fail-closed behavior. Bound implementation to groundtruth-kb/src/groundtruth_kb/secrets/scanner.py and focused scanner/preflight tests; do not alter dispatcher configuration, runtime state, credentials, remote refs, or push during implementation.",
  "after_behavior": "Repair the canonical pre-push secret scanner's large-range timeout by batching Git object reads without weakening redaction, allowlisting, or fail-closed behavior.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5613",
    "project": "PROJECT-GTKB-RELIABILITY-FIXES",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/secrets/scanner.py",
      "platform_tests/groundtruth_kb/test_secrets_scanner.py"
    ],
    "linked_specifications": [
      "SPEC-SEC-SCANNER-CLI-001",
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
      "SPEC-SEC-SCAN-REDACTION-001",
      "SPEC-SEC-ALLOWLIST-001"
    ]
  },
  "expected_result": {
    "summary": "Repair the canonical pre-push secret scanner's large-range timeout by batching Git object reads without weakening redaction, allowlisting, or fail-closed behavior.",
    "scope": [
      "Replace scan_range per-path git show subprocesses with one deterministic head-tree enumeration and one git cat-file --batch stream.",
      "Preserve head-side blob semantics, per-path allowlist checks, redacted-only findings, excluded path handling, binary skipping, deleted-path skipping, duplicate-blob path attribution, and fail-closed Git errors.",
      "Add focused unit/integration coverage only in platform_tests/groundtruth_kb/test_secrets_scanner.py; do not modify the 300-second preflight timeout unless evidence shows batching alone is insufficient.",
      "Do not alter dispatcher configuration, TAFE/runtime state, harness roles or eligibility, credentials, remote refs, Git history, deployment, or release."
    ],
    "acceptance_criteria": [
      "A many-path range uses one tree enumeration and one batch blob-reader process, with no per-path git show calls.",
      "Every eligible changed head-side text path is scanned exactly once even when multiple paths share one blob; deleted, excluded, binary, and non-blob entries are skipped.",
      "Redacted finding content, provider class, path, line, severity, fingerprint, and path-sensitive allowlist behavior remain unchanged.",
      "Focused scanner tests and push-preflight tests pass, and the real origin/main..main redacted scan completes within the canonical 300-second pre-push envelope."
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
| `SPEC-SEC-SCANNER-CLI-001` | Run platform_tests/groundtruth_kb/test_secrets_scanner.py and the real origin/main..main CLI range scan; require bounded subprocess count and completion below 300 seconds. |
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
| `SPEC-SEC-SCAN-REDACTION-001` | Assert findings expose only provider metadata and short fingerprints, never matched values, for batched range content. |
| `SPEC-SEC-ALLOWLIST-001` | Assert a shared blob at two paths is evaluated independently so path-specific allowlist behavior remains exact. |

## Acceptance Criteria

- A many-path range uses one tree enumeration and one batch blob-reader process, with no per-path git show calls.
- Every eligible changed head-side text path is scanned exactly once even when multiple paths share one blob; deleted, excluded, binary, and non-blob entries are skipped.
- Redacted finding content, provider class, path, line, severity, fingerprint, and path-sensitive allowlist behavior remain unchanged.
- Focused scanner tests and push-preflight tests pass, and the real origin/main..main redacted scan completes within the canonical 300-second pre-push envelope.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/secrets/scanner.py`
- `platform_tests/groundtruth_kb/test_secrets_scanner.py`

## Recommended Commit Type

`feat`
