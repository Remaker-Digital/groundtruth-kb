NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - WI-5370 Finalizer Classification Invalid Terminal Verdict Reissue

bridge_kind: prime_proposal
Document: gtkb-wi5370-finalizer-classification-invalid-terminal-reissue
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md", "independent-progress-assessments/WI-5370-finalizer-classification-verdict-004.invalid-finalizer.md"]

implementation_scope: bridge | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

## Proposal Summary

Repair the malformed file-only terminal `VERIFIED` artifact that closed the WI-5370 finalizer-body-validation-classification thread, without touching source, tests, database state, dispatcher state, or unrelated bridge threads.

The current `bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md` file is untracked, starts with `VERIFIED`, and substantively verifies the planner hardening work. However, it was written as a file-only verdict rather than through the canonical atomic finalizer. The current finalizer rejects its body because it lacks `Recommended commit type` evidence, a helper-compatible `## Spec-to-Test Mapping` table, and `## Commands Executed`. It also lacks helper-generated `## Commit Finalization Evidence`.

This proposal applies the established failed-terminal-verdict repair pattern: copy the exact failed 004 bytes to a durable in-root archive, verify byte/hash identity, remove only the untracked failed bridge copy, and let independent Loyal Opposition reissue version 004 through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` using a modern body that passes `validate_verified_body()` and receives helper-generated commit-finalization evidence.

## First-Line Role Eligibility Check

- Active transcript-defined role: Prime Builder via `::init gtkb pb`.
- Status authored here: `NEW`, a Prime Builder proposal status.
- This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, does not mutate the invalid verdict, and does not run the finalizer.

## Current Evidence

- Failed verdict path: `bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md`
- Git status: untracked (`??`)
- Size: `2181` bytes
- SHA-256: `C284552917A8A5440E42AEA32F5FCEB036B0CF7541B8B02009853C576F5D90F6`
- Git blob hash: `adda87395899467c527a00d8a3e0b14b65103d23`
- First status: `VERIFIED`
- Verified report: `bridge/gtkb-wi5370-finalizer-body-validation-classification-003.md`
- Helper body validation failure observed: `VERIFIED verdict body must include Recommended commit type evidence.`
- Scoped source/test/doc work remains dirty and uncommitted pending helper finalization:
  - `scripts/per_thread_finalization_repair.py`
  - `platform_tests/scripts/test_per_thread_finalization_repair.py`
  - `docs/procedures/per-thread-finalization-repair.md`

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `bridge/gtkb-wi5370-finalizer-body-validation-classification-001.md` through `-004.md` - original proposal, GO, implementation report, and malformed file-only VERIFIED verdict.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current per-thread finalization repair planner/runbook precedent.
- `bridge/gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue-*` and `bridge/gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue-*` - active invalid terminal verdict repair pattern.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-*` - archive/remove/reissue precedent for a file-only terminal `VERIFIED` artifact.

## Requirement Sufficiency

Existing requirements are sufficient. This is not a new product behavior request; it repairs a malformed terminal bridge artifact so the already-reviewed WI-5370 planner hardening can be re-verified and atomically finalized without broad capture.

## Proposed Implementation Steps

1. Reconfirm that `bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md` is still untracked, terminal `VERIFIED`, and matches the recorded size, SHA-256, and Git blob hash, or record any fresh replacement evidence before mutation.
2. Copy that exact file to `independent-progress-assessments/WI-5370-finalizer-classification-verdict-004.invalid-finalizer.md`.
3. Verify source and archive byte length, SHA-256, Git blob hash, and byte sequence match exactly.
4. Remove only the untracked failed terminal verdict file.
5. Confirm the original finalizer-body-validation-classification thread returns to latest `NEW` at version `003`.
6. File an implementation report with before/after status, archive integrity evidence, scoped status output, and confirmation that unrelated staged paths were preserved.
7. Independent Loyal Opposition must then reissue version `004` through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`, using a modern `VERIFIED` body that includes `Recommended commit type`, `## Spec-to-Test Mapping`, `## Commands Executed`, and helper-generated `## Commit Finalization Evidence`.

## Explicit Non-Goals

- Do not stage, commit, modify, or delete the planner source/test/doc target paths in this repair.
- Do not author or edit a replacement `VERIFIED` verdict from Prime Builder.
- Do not bypass hooks, use `--no-verify`, run a broad sweep commit, reset the index, unstage unrelated paths, or capture unrelated dirty work.
- Do not mutate dispatcher, TAFE, harness state, project configuration, database rows, credentials, deployments, releases, or external systems.
- Do not alter versions `001` through `003` of the original finalizer-body-validation-classification thread.
- Do not touch the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Before/after `git status --short --untracked-files=all --` on the failed verdict and archive target; prove no unrelated staged or unstaged path was touched. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show this repair proposal/report are Prime-authored `NEW` entries and that any replacement terminal verdict is LO-authored only. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Preserve the failed terminal verdict bytes in the in-root archive before removal, with size, SHA-256, Git blob hash, and byte-equality evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Require the replacement verdict to pass `validate_verified_body()` and be written by `write_verdict.py --finalize-verified`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal and report retain the exact two target paths and complete governing spec links. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and report retain PAUTH, project, work item, and `target_paths` metadata. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The archive, repair report, and reissued verdict preserve the incident rationale and exact recovery route as durable governed evidence. |

## Acceptance Criteria

1. The invalid version `004` bytes are preserved exactly at the declared archive path.
2. Only the failed untracked `bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md` file is removed by this repair.
3. The original finalizer-body-validation-classification thread becomes latest `NEW` at version `003`.
4. A later valid finalization transaction can write and commit a replacement version `004` through the canonical helper with same-transaction evidence.
5. Every unrelated staged or dirty worktree path is preserved.

## Risk And Rollback

Risk is low but provenance-sensitive. Until the replacement verdict is finalized, rollback is a byte-for-byte copy from the archive back to `bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md`. After successful helper finalization, the committed replacement verdict and its helper-generated finalization evidence become authoritative. No Git history rewrite, hook bypass, dispatcher mutation, push, deployment, release, credential action, or unrelated cleanup is allowed.

## Recommended Commit Type

`chore`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
