NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - WI-5332 WI-5113 Invalid Terminal VERIFIED Verdict Reissue Repair

bridge_kind: prime_proposal
Document: gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5332
Intent: bounded terminal-verdict finalization repair

target_paths: ["bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md", "independent-progress-assessments/WI-5332-wi5113-verdict-006.invalid-finalizer.md"]

implementation_scope: bridge | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

## Proposal Summary

Repair one malformed file-only terminal `VERIFIED` artifact in the WI-5113
bridge chain without touching source, tests, database state, dispatcher state,
or unrelated bridge threads.

The current `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md`
file is untracked, starts with `VERIFIED`, cites the owner hunk-scoped waiver,
and correctly affirms WI-5113 substance, but it was written as a file-only
verdict rather than through the canonical atomic finalizer. The stricter current
finalizer rejects its body because it lacks `Recommended commit type` evidence,
a helper-compatible `## Spec-to-Test Mapping` table, and `## Commands Executed`.
It also lacks helper-generated `## Commit Finalization Evidence`.

This proposal applies the established failed-terminal-verdict repair pattern:
copy the exact failed 006 bytes to a durable in-root archive, verify byte/hash
identity, remove only the untracked failed bridge copy, and let independent
Loyal Opposition reissue WI-5113 version 006 through
`.claude/skills/verify/helpers/write_verdict.py --finalize-verified` using a
modern body that passes `validate_verified_body()` and receives helper-generated
commit-finalization evidence.

## First-Line Role Eligibility Check

- Active transcript-defined role: Prime Builder via `::init gtkb pb`.
- Status authored here: `NEW`, a Prime Builder proposal status.
- This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, does not mutate the
  invalid verdict, and does not run the finalizer.

## Current Evidence

- Failed verdict path:
  `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md`.
- Git status: untracked (`??`).
- Size: `2458` bytes.
- SHA-256:
  `097D7BEDEDA4CE255AB77EB39763C37F2FFF87E0DCE0F634DB9ACA9E6B89001D`.
- Git blob hash: `8bc934d88727d2bbd24db2eea4dabe5ede66f33e`.
- First status: `VERIFIED`.
- Responds to:
  `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-005.md`.
- Helper body validation failure observed:
  `VERIFIED verdict body must include Recommended commit type evidence.`
- Current WI-5113 implementation target paths are clean in the worktree; the
  no-window source/test substance is already present in `HEAD` commit
  `42a252ab`.
- Existing staged unrelated path detected and must be preserved:
  `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER` - owner approved the
  hunk-scoped finalization waiver for the WI-5113 no-window hunks.
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - precedent for
  hunk-scoped finalization under a commingled worktree.
- `DELIB-20260711-WI5118-BY-REFERENCE-FINALIZATION-WAIVER` - precedent for
  owner-approved by-reference finalization.
- `bridge/gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue-001.md` - current
  invalid-terminal-verdict reissue proposal pattern that names modern body
  validation explicitly.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-*` - archive,
  remove, and atomic reissue precedent for a file-only terminal `VERIFIED`
  artifact.
- `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-001.md` through
  `-006.md` - original WI-5113 proposal, GO, reports, finalization blocker, and
  invalid file-only terminal verdict.

## Owner Decisions / Input

- `DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER` records the owner's
  explicit waiver reply: `APPROVE WI5113 HUNK-SCOPED FINALIZATION WAIVER`.
- The owner repeated the approval in the current Prime Builder session:
  `APPROVE WI5113 HUNK-SCOPED FINALIZATION WAIVER`.

This proposal does not broaden that waiver. It preserves the invalid file-only
verdict as evidence and restores the original WI-5113 thread to a state where
Loyal Opposition can reissue a valid terminal verdict through the required
atomic finalizer. It does not authorize broad staging, source mutation, Git
history rewrite, push, release, deployment, credential lifecycle, dispatcher
mutation, or unrelated cleanup.

## Requirement Sufficiency

Existing requirements are sufficient. The mandatory VERIFIED finalization gate,
worktree hygiene requirements, project authorization requirements, and
spec-derived verification gate define the repair. No new GOV, ADR, DCL, PB,
SPEC, or product requirement is introduced by this proposal.

## Proposed Implementation Steps

1. Reconfirm that
   `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md` is
   still untracked, terminal `VERIFIED`, and matches the recorded size, SHA-256,
   and Git blob hash, or record any fresh replacement evidence before mutation.
2. Copy that exact file to
   `independent-progress-assessments/WI-5332-wi5113-verdict-006.invalid-finalizer.md`.
3. Verify source and archive byte length, SHA-256, Git blob hash, and byte
   sequence match exactly.
4. Remove only the untracked failed terminal verdict file.
5. Confirm the original WI-5113 PAUTH-v2 thread returns to latest `REVISED` at
   version `005`, making it eligible for independent Loyal Opposition reissue.
6. File an implementation report with before/after status, archive integrity
   evidence, scoped status output, and confirmation that the unrelated staged
   `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` index entry
   was preserved.
7. Independent Loyal Opposition must then reissue WI-5113 version `006` through
   `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`, using a
   modern `VERIFIED` body that includes `Recommended commit type`,
   `## Spec-to-Test Mapping`, `## Commands Executed`, and helper-generated
   `## Commit Finalization Evidence`.

## Explicit Non-Goals

- Do not stage, commit, modify, or delete any WI-5113 source/test target path.
- Do not author or edit a replacement `VERIFIED` verdict from Prime Builder.
- Do not bypass hooks, use `--no-verify`, run a broad sweep commit, reset the
  index, unstage unrelated paths, or capture unrelated dirty work.
- Do not mutate dispatcher, TAFE, harness state, project configuration,
  database rows, credentials, deployments, releases, or external systems.
- Do not alter the original WI-5113 versions `001` through `005`.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Before/after `git status --short --untracked-files=all --` on the failed verdict and archive target; prove no unrelated staged or unstaged path was touched. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show this repair proposal/report are Prime-authored `NEW` entries and that any replacement WI-5113 terminal verdict is LO-authored only. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Preserve the failed terminal verdict bytes in the in-root archive before removal, with size, SHA-256, Git blob hash, and byte-equality evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Require the replacement WI-5113 verdict to pass `validate_verified_body()` and be written by `write_verdict.py --finalize-verified`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal and report retain the exact two target paths and complete governing spec links. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and report retain PAUTH, project, work item, and `target_paths` metadata. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `implementation_authorization.py begin` must authorize exactly the two declared repair paths after independent GO. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The archive, repair report, and reissued verdict preserve the incident rationale and exact recovery route as durable governed evidence. |

## Acceptance Criteria

1. The invalid WI-5113 version `006` bytes are preserved exactly at the declared
   archive path.
2. Only the failed untracked
   `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md` file is
   removed by this repair.
3. The original WI-5113 PAUTH-v2 thread becomes latest `REVISED` at version
   `005`.
4. A later valid finalization transaction can write and commit a replacement
   version `006` through the canonical helper with same-transaction evidence.
5. The unrelated staged `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md`
   entry and every unrelated dirty worktree path are preserved.

## Risk And Rollback

Risk is low but provenance-sensitive. Until the replacement verdict is finalized,
rollback is a byte-for-byte copy from the archive back to
`bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md`. After
successful helper finalization, the committed replacement verdict and its
helper-generated finalization evidence become authoritative. No Git history
rewrite, hook bypass, dispatcher mutation, direct harness-to-harness action,
push, deployment, release, credential action, or unrelated cleanup is allowed.

## Recommended Commit Type

`chore:` - this is governance-evidence recovery and atomic-finalization repair,
not product behavior change.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
