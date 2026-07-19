REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb

# WI-5370 Finalizer Classification Repair Retry

bridge_kind: prime_proposal
Document: gtkb-wi5370-finalizer-classification-invalid-terminal-reissue
Version: 007
Responds to: bridge/gtkb-wi5370-finalizer-classification-invalid-terminal-reissue-006.md
Date: 2026-07-17 UTC
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
target_paths: ["bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md", "independent-progress-assessments/WI-5370-finalizer-classification-verdict-004.invalid-finalizer.md"]
implementation_scope: bridge | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

## Revision Claim

Prime Builder accepts version 006. The malformed untracked verdict was absent
when report 005 was filed but is present again at the original bridge path.
Because latest status is now NO-GO, the prior claim/start authority cannot be
reused. This revision requests a fresh bounded retry under the same exact two
targets and preserves the existing archive.

## Findings Addressed

- Reconfirm the reappeared source is untracked, 2,181 bytes, SHA-256
  `C284552917A8A5440E42AEA32F5FCEB036B0CF7541B8B02009853C576F5D90F6`,
  and Git blob `adda87395899467c527a00d8a3e0b14b65103d23`.
- Reconfirm the archive is byte-identical before any removal.
- Under a fresh GO, claim, and implementation-start packet, remove only the
  original bridge path and immediately confirm the thread is latest NEW 003.
- File fresh post-removal evidence. Prime Builder will not author the
  replacement VERIFIED.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- Versions 001-006 of this thread record the original archive/remove plan,
  corrected GO, execution report, and independent observation that the source
  path reappeared.
- `bridge/gtkb-wi5370-finalizer-body-validation-classification-001.md` through
  `-004.md` are the original proposal/report/malformed-verdict chain.

## Owner Decisions / Input

No new owner decision is required. The active project PAUTH covers the exact
governance-evidence retry, but a fresh independent GO and implementation-start
packet remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. This revision retries the already-approved
exact archive/remove repair and introduces no new product, policy, or target
requirement.

## Scope Changes

No target or mutation scope changes. The archive already exists and must not
be overwritten; it is now a precondition comparison source. Only the reappeared
untracked bridge version 004 may be removed.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Provenance and archive integrity | Compare both paths by byte count, SHA-256, Git blob, and byte equality before removal. |
| Worktree hygiene | Scoped Git status before/after; remove only the original untracked bridge path. |
| Bridge authority | Show original thread becomes latest NEW 003; replacement VERIFIED remains independent LO work. |
| Authorization | Fresh GO, `go_implementation` claim, and exact two-target implementation-start packet before removal. |
| Durable lifecycle | File a new implementation report with immediate post-removal evidence and no claim of terminal closure. |

## Acceptance Criteria

1. Archive remains byte-identical to the reappeared malformed verdict.
2. Only the original untracked bridge path is removed.
3. Original thread immediately resolves to latest NEW version 003.
4. Planner source/test/runbook and unrelated worktree paths remain untouched.
5. Independent LO later publishes any replacement VERIFIED through the atomic finalizer.

## Risk And Rollback

The reappearance indicates concurrent or automated restoration risk. The retry
must capture immediate post-removal state; it cannot promise the path will not
be recreated later by another actor. Rollback is a separately governed exact
copy from the preserved archive. No stage, commit, push, release, deployment,
credential, database, dispatcher, or external-system action is authorized.

## Pre-Filing Preflight Subsection

The governed revision helper will run candidate applicability and clause
preflights before filing. Filing is forbidden if either gate blocks.
