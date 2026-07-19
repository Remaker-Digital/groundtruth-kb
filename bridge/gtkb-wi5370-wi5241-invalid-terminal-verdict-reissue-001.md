NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - WI-5241 Invalid Terminal VERIFIED Verdict Reissue Repair

bridge_kind: prime_proposal
Document: gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Intent: bounded terminal-verdict finalization repair

target_paths: ["bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-006.md", "independent-progress-assessments/WI-5370-wi5241-verdict-006.invalid-finalizer.md"]

## Proposal Summary

Repair one failed file-only terminal `VERIFIED` artifact in the WI-5241 bridge chain without touching any source, database, dispatcher, or unrelated bridge thread.

The current `bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-006.md` file is untracked, starts with `VERIFIED`, and lacks the canonical finalizer evidence required for a durable per-thread commit. A direct pathspec commit is correctly rejected by the protected-commit authorization gate. The stricter current finalizer also rejects the body as an input because it lacks `Recommended commit type` evidence, a helper-compatible `## Spec-to-Test Mapping` table, and `## Commands Executed`.

This proposal applies the same bounded archive/remove pattern used by `gtkb-wi5321-wi5299-failed-verified-finalization-repair`, but names the additional body-validity requirement explicitly: after the failed terminal file is archived and removed, Loyal Opposition must reissue the WI-5241 terminal verdict through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` using a modern `VERIFIED` body that passes `validate_verified_body()` and receives helper-generated `## Commit Finalization Evidence`.

## First-Line Role Eligibility Check

- Active transcript-defined role: Prime Builder via `::init gtkb pb`.
- Status authored here: `NEW`, a Prime Builder proposal status.
- This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, does not delete the failed verdict, and does not run the finalizer.

## Current Evidence

- Failed verdict path: `bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-006.md`.
- Git status: untracked (`??`).
- Size: `4209` bytes.
- SHA-256: `7197EE1331E674BEBF956021207E016965AA3C5DB305DBAA4F064F41C4E17EF5`.
- Git blob hash: `0b77f958e8be823cdbb1a636ce378bd58c591c93`.
- First status: `VERIFIED`.
- Responds to: `bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-005.md`.
- Helper body validation failure observed: `VERIFIED verdict body must include Recommended commit type evidence.`
- Protected-commit authorization failure observed for direct staging: `terminal VERIFIED bridge file lacks Commit Finalization Evidence with a same-transaction path set`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`

## Prior Deliberations

- `DELIB-202666332` - owner-authorized tree stabilization must preserve per-thread finalization provenance and avoid broad commits.
- `bridge/gtkb-wi5027-worktree-finalization-commit-discipline-lapse-*` - resolved precedent for repairing large uncommitted bridge/source sprawl without a blind sweep commit.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current planner/runbook for per-thread finalization repair.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-*` - direct archive/remove/reissue precedent for a file-only terminal `VERIFIED` artifact.

## Requirement Sufficiency

Existing requirements are sufficient. The repair does not create new product behavior; it restores the bridge chain to a state where the already-reviewed WI-5241 stand-down can be re-evaluated and finalized through the mandatory helper.

## Proposed Implementation Steps

1. Reconfirm that `bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-006.md` is still untracked, terminal `VERIFIED`, and matches either the recorded size/hash/blob or freshly reported replacement evidence.
2. Copy that exact file to `independent-progress-assessments/WI-5370-wi5241-verdict-006.invalid-finalizer.md`.
3. Verify source and archive byte length, SHA-256, Git blob hash, and byte sequence match exactly.
4. Remove only the untracked failed terminal verdict file.
5. Confirm the original WI-5241 thread returns to latest `NEW` at version `005`.
6. File an implementation report with the before/after scoped status and archive integrity evidence.
7. Have Loyal Opposition reissue the WI-5241 terminal verdict through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`, using a modern body that includes `Recommended commit type`, `## Spec-to-Test Mapping`, `## Commands Executed`, and helper-generated `## Commit Finalization Evidence`.

## Explicit Non-Goals

- Do not stage, commit, modify, or delete any WI-5241 source, database, dispatcher, or unrelated bridge path.
- Do not author or edit a replacement `VERIFIED` verdict from Prime Builder.
- Do not bypass hooks, use `--no-verify`, run a broad sweep commit, or stage unrelated paths.
- Do not touch the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Before/after `git status --short --untracked-files=all --` on the failed verdict and archive target; byte/hash equality proof before removal. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show this repair report is Prime `NEW`, and any replacement WI-5241 terminal verdict is authored by Loyal Opposition only. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Preserve the failed terminal verdict bytes in the in-root archive before removal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Replacement verdict must pass `validate_verified_body()` and be written by `write_verdict.py --finalize-verified`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal and report retain the exact two target paths and governing spec links. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and report retain PAUTH, project, work item, and target path metadata. |

## Acceptance Criteria

- The failed WI-5241 version `006` bytes are preserved exactly at the declared archive path.
- Only the failed untracked `bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-006.md` file is removed by this repair.
- The original WI-5241 thread becomes latest `NEW` at version `005`.
- A later valid finalization transaction can write and commit a replacement version `006` through the canonical helper with same-transaction evidence.

## Risk And Rollback

Risk is low but provenance-sensitive. Until the replacement verdict is finalized, rollback is a byte-for-byte copy from the archive back to `bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-006.md`. After successful helper finalization, the committed replacement verdict and its finalization evidence become authoritative.

## Recommended Commit Type

`chore`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
