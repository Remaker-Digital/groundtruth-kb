NEW

# WI-5321: Repair WI-5299 failed VERIFIED finalization by archive and atomic reissue

bridge_kind: prime_proposal
Document: gtkb-wi5321-wi5299-failed-verified-finalization-repair
Version: 001

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5299-VERIFIED-FINALIZATION-20260715
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5321

target_paths: ["bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md", "independent-progress-assessments/WI-5321-wi5299-verdict-004.failed-finalizer.md"]

implementation_scope: governance_evidence | bridge failed-transaction rollback
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5299 received a substantively independent `VERIFIED` verdict at version 004,
but the reviewer wrote the verdict as a file-only operation instead of using
the mandatory atomic finalizer. The untracked 004 file therefore lacks
`Commit Finalization Evidence`, and
`scripts/check_protected_commit_authorization.py` correctly refuses to commit
it. Broad staging or a manual hook bypass would convert an audit defect into a
repository-integrity defect.

Perform the same rollback the atomic helper performs after a failed
finalization: first copy the exact untracked 004 bytes to the declared durable
incident path, verify both byte and SHA-256 identity, then remove only the
untracked bridge copy. This returns the original WI-5299 thread to latest 003
`NEW`, allowing independent LO to reissue version 004 through
`write_verdict.py --finalize-verified`. The corrected helper transaction must
commit only the independently VERIFIED `.gitignore` and focused test hunks,
the untracked WI-5299 proposal/report predecessors, and the helper-generated
004 verdict with its same-transaction evidence.

## Exact Pre-Repair Evidence

- Failed verdict path:
  `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`
- Git status: untracked (`??`); absent from `HEAD` and all committed history.
- Git blob hash: `000b9aa061ee171a180857436b2de0777a6952df`.
- SHA-256: `DF7EE48F605F39254FBEB09EC66FA0EF8072D23B3001E2AE447E2C431E9AAA32`.
- Size: 5,260 bytes.
- First status: `VERIFIED`; independent reviewer session
  `cb17fdc1-27d0-4083-babf-6200cfdc0d6e` differs from Prime report session
  `019f5f6d-60cd-7040-b73f-c7d23757c4bc`.
- Missing required section: `## Commit Finalization Evidence`.
- Canonical checker result: fail with
  `terminal VERIFIED bridge file lacks Commit Finalization Evidence with a same-transaction path set`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666332` - owner authorizes exact local finalization of independently
  VERIFIED scopes to reach a clean worktree while forbidding broad or unrelated
  capture.
- `DELIB-202666274` - project implementation authority preserves bridge,
  implementation-start, independent verification, and mechanical gates.
- `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-001.md` through
  `-004.md` - original proposal, GO, implementation report, and failed
  file-only verdict transaction.

## Owner Decisions / Input

`DELIB-202666332` is the exact mechanical owner authority for this repair. It
permits local commits only for independently VERIFIED, path/hunk-isolated scopes
and expressly forbids broad capture. PAUTH version 2 narrows the operation to
the failed 004 archive/removal and atomic reissue path. No further owner choice
is required.

## Requirement Sufficiency

Existing requirements are sufficient. The mandatory VERIFIED finalization gate
defines the failed-transaction rollback behavior, while worktree hygiene and
project authorization require exact provenance and isolation. No new GOV, ADR,
DCL, or product requirement is introduced.

## Implementation Steps

1. Revalidate that the bridge 004 path is untracked, absent from `HEAD`, exactly
   5,260 bytes, and matches both recorded hashes.
2. Copy its bytes without transformation to
   `independent-progress-assessments/WI-5321-wi5299-verdict-004.failed-finalizer.md`.
3. Verify source and archive are byte-identical and have the same SHA-256.
4. Remove only the untracked bridge 004 file. Do not touch versions 001-003,
   the Git index, dispatcher configuration, or any harness.
5. Confirm the versioned-file chain now resolves to WI-5299 report 003 `NEW`
   and the protected-commit failure no longer exists as a staged candidate.
6. File a WI-5321 implementation report carrying the before/after evidence and
   an explicit by-reference waiver for the removed untracked path. The durable
   archive, WI-5321 proposal/report, and WI-5321 verdict are the repair commit
   surfaces.
7. Independent LO must then process the original WI-5299 report and use the
   atomic finalizer to reissue 004. The finalizer include set must contain only
   `.gitignore`, the focused test, WI-5299 versions 001 and 003, and its newly
   generated 004 verdict; version 002 is already committed.

## Specification-Derived Verification Plan

| Specification | Required executed evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Before removal, prove the file is an untracked failed transaction with no finalization section; after removal, prove versions 001-003 are unchanged and latest is report 003 `NEW`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Preserve the independent verdict body byte-for-byte in the archive and require the reissued 004 to add helper-generated finalization evidence without weakening its substantive findings. |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --short --` on both exact targets plus all WI-5299 paths must show only the declared archive addition and failed bridge-file removal; no broad stage/commit occurs during implementation. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Claim/start must name PAUTH v2, WI-5321, and exactly the two target paths before copy or removal. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | The start packet must pass for `bridge` and `governance_evidence`; all forbidden operations remain absent. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal/report headers retain the exact PAUTH, project, WI, and target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal and report carry forward every applicable specification identified by preflight. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The durable archive and implementation report preserve why the original untracked verdict was removed and how to reconstruct it exactly. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5321 is not complete until its repair is VERIFIED and the original WI-5299 004 is reissued by an atomic finalizer commit. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5321, the durable archive, report, and corrected finalization preserve the incident as governed evidence. |

## Acceptance Criteria

1. The durable archive is byte-for-byte identical to the failed untracked 004
   and records the same Git blob and SHA-256 values.
2. Only the failed untracked bridge 004 is removed; committed history and
   WI-5299 versions 001-003 remain byte-identical.
3. The original WI-5299 thread becomes LO-actionable at report 003 `NEW`.
4. The repair thread receives independent VERIFIED, and the original WI-5299
   004 is subsequently reissued through the atomic finalizer with mandatory
   same-transaction evidence.
5. The corrected WI-5299 commit contains no unrelated staged or unstaged bytes.

## Risk / Rollback

The risk is losing the only bytes of the failed verdict or allowing a reissued
verdict to drift substantively. The exact archive copy, dual hashes, size, and
byte comparison prevent that. Before atomic reissue, rollback is an exact byte
copy from the durable archive back to the bridge path. After reissue, the Git
commit and helper-generated finalization evidence are authoritative. No Git
history rewrite, hook bypass, dispatcher mutation, direct harness contact,
push, deployment, release, credential action, or unrelated cleanup is allowed.

## Recommended Commit Type

`chore:` - this is governance-evidence recovery and atomic-finalization repair,
not a product behavior change.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
