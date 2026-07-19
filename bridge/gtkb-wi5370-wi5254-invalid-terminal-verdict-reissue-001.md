NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - WI-5254 Invalid Terminal VERIFIED Verdict Reissue Repair

bridge_kind: prime_proposal
Document: gtkb-wi5370-wi5254-invalid-terminal-verdict-reissue
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Intent: bounded terminal-verdict finalization repair

target_paths: ["bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md", "independent-progress-assessments/WI-5370-wi5254-verdict-008.invalid-finalizer.md"]

implementation_scope: bridge | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

## Proposal Summary

Repair one malformed file-only terminal `VERIFIED` artifact in the `gtkb-wi5254-pauth-amendment-packet-preflight` bridge chain without touching source, tests, database state, dispatcher state, or unrelated bridge threads.

The current `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` file is untracked, starts with `VERIFIED`, and substantively records Loyal Opposition terminal review, but it was written as a file-only verdict rather than through the canonical atomic finalizer. The current finalizer rejects its body because it lacks `Recommended commit type` evidence. It also lacks helper-generated `## Commit Finalization Evidence`, so it must not be swept into a direct pathspec commit.

This proposal applies the established invalid-terminal-verdict repair pattern: copy the exact failed verdict bytes to a durable in-root archive, verify byte/hash identity, remove only the untracked failed bridge copy, and let independent Loyal Opposition reissue `gtkb-wi5254-pauth-amendment-packet-preflight` version `008` through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` using a modern body that passes `validate_verified_body()` and receives helper-generated commit-finalization evidence.

## First-Line Role Eligibility Check

- Active transcript-defined role: Prime Builder via `::init gtkb pb`.
- Status authored here: `NEW`, a Prime Builder proposal status.
- This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, does not mutate the invalid verdict, and does not run the finalizer.

## Current Evidence

- Failed verdict path: `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md`.
- Git status: untracked (`??`).
- Size: `8142` bytes.
- SHA-256: `2C013E46521B6D79A7F803ACBBD00CCAD9153ACC8DCBEA4051A349C072AAEF7A`.
- Git blob hash: `f59e6350ae259dcaf147f827f03b47af894b26ab`.
- First status: `VERIFIED`.
- Responds to: `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-007.md`.
- Helper body validation failure observed: `VERIFIED verdict body must include Recommended commit type evidence.`
- Active staged-index hazard remains outside this proposal: `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` is currently staged and must be preserved unless a separate GO authorizes index containment.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666332` - owner-authorized tree stabilization must preserve per-thread finalization provenance and avoid broad commits.
- `bridge/gtkb-wi5027-worktree-finalization-triage-001.md` through `-004.md` - resolved precedent for read-only classification before any cleanup, with terminal verdicts blocked without item-specific evidence.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current planner/runbook for per-thread finalization repair.
- `bridge/gtkb-wi5370-finalizer-body-validation-classification-001.md` through `-004.md` - current planner hardening that classifies invalid terminal VERIFIED bodies as blocked until archive/remove/reissue repair.
- `bridge/gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue-*` and `bridge/gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue-*` - active invalid terminal verdict reissue pattern examples.

## Requirement Sufficiency

Existing requirements are sufficient. The repair does not create new product behavior; it restores the bridge chain to a state where the already-reviewed terminal disposition can be re-evaluated and finalized through the mandatory helper.

## Proposed Implementation Steps

1. Reconfirm that `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` is still untracked, terminal `VERIFIED`, and matches the recorded size, SHA-256, and Git blob hash, or record fresh replacement evidence before mutation.
2. Copy that exact file to `independent-progress-assessments/WI-5370-wi5254-verdict-008.invalid-finalizer.md`.
3. Verify source and archive byte length, SHA-256, Git blob hash, and byte sequence match exactly.
4. Remove only the untracked failed terminal verdict file.
5. Confirm the original `gtkb-wi5254-pauth-amendment-packet-preflight` thread returns to latest `REVISED` at version `007`.
6. File an implementation report with before/after status, archive integrity evidence, scoped status output, and confirmation that the staged index and unrelated dirty paths were preserved.
7. Independent Loyal Opposition must then reissue `gtkb-wi5254-pauth-amendment-packet-preflight` version `008` through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`, using a modern `VERIFIED` body that includes `Recommended commit type`, `## Spec-to-Test Mapping`, `## Commands Executed`, and helper-generated `## Commit Finalization Evidence`.

## Explicit Non-Goals

- Do not stage, commit, modify, or delete any source/test target path from the original thread.
- Do not author or edit a replacement `VERIFIED` verdict from Prime Builder.
- Do not bypass hooks, use `--no-verify`, run a broad sweep commit, reset the index, unstage unrelated paths, or capture unrelated dirty work.
- Do not touch the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.
- Do not mutate dispatcher, harness state, project configuration, database rows, credentials, deployments, releases, or external systems.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Before/after `git status --short --untracked-files=all --` on the failed verdict and archive target; prove no unrelated staged or unstaged path was touched. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show this repair proposal/report are Prime-authored `NEW` entries and that any replacement terminal verdict is LO-authored only. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Preserve the failed terminal verdict bytes in the in-root archive before removal, with size, SHA-256, Git blob hash, and byte-equality evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Require the replacement verdict to pass `validate_verified_body()` and be written by `write_verdict.py --finalize-verified`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal and report retain the exact two target paths and complete governing spec links. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and report retain PAUTH, project, work item, and `target_paths` metadata. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `implementation_authorization.py begin` must authorize exactly the two declared repair paths after independent GO. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The archive, repair report, and reissued verdict preserve the incident rationale and exact recovery route as durable governed evidence. |

## Acceptance Criteria

- The invalid version `008` bytes are preserved exactly at `independent-progress-assessments/WI-5370-wi5254-verdict-008.invalid-finalizer.md`.
- Only the failed untracked `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` file is removed by this repair.
- The original `gtkb-wi5254-pauth-amendment-packet-preflight` thread becomes latest `REVISED` at version `007` until LO reissues the terminal verdict.
- A later valid finalization transaction can write and commit a replacement version `008` through the canonical helper with same-transaction evidence.
- The staged `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` entry and every unrelated dirty worktree path are preserved.

## Risk And Rollback

Risk is low but provenance-sensitive. Until the replacement verdict is finalized, rollback is a byte-for-byte copy from the archive back to `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md`. After successful helper finalization, the committed replacement verdict and its helper-generated finalization evidence become authoritative. No Git history rewrite, hook bypass, dispatcher mutation, push, deployment, release, credential action, or unrelated cleanup is allowed.

## Recommended Commit Type

`chore`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
