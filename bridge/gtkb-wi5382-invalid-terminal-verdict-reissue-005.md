REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder revision worker; transcript-defined Prime Builder role
author_metadata_source: explicit_interactive_session_metadata

# WI-5382 - Retry removal of reappeared invalid terminal verdict

bridge_kind: prime_proposal
Document: gtkb-wi5382-invalid-terminal-verdict-reissue
Version: 005
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5382-IMPLEMENTATION-START-PACKET-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5382

target_paths: ["bridge/gtkb-wi5382-implementation-start-packet-contract-004.md", "independent-progress-assessments/WI-5382-invalid-terminal-verdict-004.finalization-diagnostic.md"]

implementation_scope: preserve the existing archive and retry removal of only the reappeared untracked invalid verdict under fresh claim/start authority
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This revision responds to
`bridge/gtkb-wi5382-invalid-terminal-verdict-reissue-004.md`. Independent
review confirmed that the approved archive exists but the malformed untracked
source verdict has reappeared at
`bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`. Therefore the
version 003 implementation claim is not currently true: the source thread
still resolves to malformed `VERIFIED` version 004 instead of implementation
report `NEW` version 003.

The requested fresh GO authorizes no broad cleanup and no replacement verdict.
After a new matching claim and implementation-start packet, Prime Builder will
verify that the reappeared source bytes are byte-for-byte identical to the
preserved archive, remove only the untracked source path, prove that the source
thread returns to latest `NEW` version 003, and file a fresh implementation
report with current evidence. The archive remains intact. Independent Loyal
Opposition retains sole authority to verify the recovery report and separately
reissue a canonical source-thread `VERIFIED` through the atomic finalizer.

## NO-GO Finding Response

The NO-GO is accepted. Current evidence reproduces all three review facts:

- `Test-Path bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`
  is true.
- Git status reports the path as untracked.
- The source thread still resolves to `VERIFIED` version 004.

The archive step remains valid and must not be repeated destructively. The
retry will use the archive only as immutable comparison evidence. If source
and archive length, SHA-256, Git blob, first line, or byte content differ, the
retry fails closed and files no removal claim. If they match, only the
reappeared untracked source verdict is removed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded governed
  repair authority while preserving GO, claim, start, verification, and exact
  target gates.
- `bridge/gtkb-wi5382-invalid-terminal-verdict-reissue-001.md` - original
  byte-checked archive/remove proposal.
- `bridge/gtkb-wi5382-invalid-terminal-verdict-reissue-002.md` - original GO
  limiting removal to the malformed untracked source verdict.
- `bridge/gtkb-wi5382-invalid-terminal-verdict-reissue-003.md` - prior report
  whose removal claim is contradicted by current state.
- `bridge/gtkb-wi5382-invalid-terminal-verdict-reissue-004.md` - controlling
  NO-GO requiring the source verdict to actually be removed.
- `bridge/gtkb-wi5382-implementation-start-packet-contract-003.md` - source
  implementation report that must become latest after lawful removal.

The current deliberation search found no owner decision authorizing broader
cleanup, source mutation, or a Prime-authored replacement verdict. None is
inferred.

## Owner Decisions / Input

No new owner decision is required to request review of this exact retry. The
existing bounded repair authorization does not bypass the need for a fresh GO,
claim, and implementation-start packet. It authorizes no unrelated cleanup.

## Requirement Sufficiency

Existing requirements sufficient. The linked bridge-authority,
operation-time authorization, worktree-hygiene, artifact-lifecycle, and
spec-derived verification requirements already mandate byte-checked removal of
only the invalid untracked verdict and independent reissuance of a lawful
terminal verdict. No new or revised requirement is needed for this retry.

## Proposed Scope

1. Confirm this version 005 revision has a fresh independent GO and acquire a
   new matching `go_implementation` claim.
2. Obtain a new implementation-start packet covering exactly the malformed
   source verdict and its existing archive evidence path.
3. Confirm the source path is untracked and the archive remains in-root.
4. Compare source and archive length, SHA-256, Git blob, first line, and bytes.
5. Fail closed without mutation if any comparison differs.
6. Remove only
   `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`.
7. Prove the archive still exists with unchanged bytes and the source path is
   absent from both the filesystem and Git status.
8. Prove the source thread now resolves to `NEW` version 003 and the
   finalization planner no longer treats the malformed version 004 as live.
9. File a fresh implementation report with the current claim/start packet and
   observed evidence, then release the claim.

## Out Of Scope

- Rewriting, replacing, deleting, or moving the archive.
- Any source or test mutation, including
  `scripts/implementation_authorization.py` and its tests.
- Any Prime-authored `VERIFIED` verdict or use of the LO finalizer.
- Any broad clean, reset, restore, staging, commit, push, release, deployment,
  credential, database, dispatcher, TAFE, runtime, or harness mutation.

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Capture fresh GO, claim, and exact-target start packet before removal. | Removal occurs only under current operation-time authority. |
| `GOV-WORK-TREE-HYGIENE-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Compare source/archive bytes and root paths; inspect exact path status before and after. | Only the untracked malformed source is removed; archive and unrelated dirt remain unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run `gt bridge show gtkb-wi5382-implementation-start-packet-contract --json --compact` before and after. | Before: malformed `VERIFIED` v004; after: implementation report `NEW` v003. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Preserve source report v003 and leave replacement verification to independent LO. | Prime authors no `VERIFIED`; LO can respond to the unambiguous source report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run `python scripts/per_thread_finalization_repair.py --format json` after removal. | The reappeared invalid terminal artifact is no longer a live malformed-terminal candidate. |

## Acceptance Criteria

1. Fresh GO, matching claim, and implementation-start packet precede removal.
2. Source and archive are proven byte-for-byte identical before removal.
3. The archive remains unchanged and in-root.
4. Only the untracked malformed source verdict is removed.
5. The source thread returns to latest `NEW` version 003.
6. A fresh implementation report states current observed facts and requests
   independent verification.
7. Replacement source-thread `VERIFIED` remains independent LO work through
   the canonical atomic finalizer.
8. No unrelated worktree, index, history, source, test, DB, runtime, release,
   deployment, credential, or external state changes.

## Risks / Rollback

The main risk is deleting bytes that differ from the approved archive. Exact
byte/hash/blob comparison is therefore a hard precondition. Before independent
LO reissues a valid source verdict, rollback is a byte-for-byte copy from the
unchanged archive to the original source path under a separately governed
successor. No broad cleanup or history rewrite is permitted.

## Files Expected To Change

- Removed only:
  `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`
- Preserved without modification:
  `independent-progress-assessments/WI-5382-invalid-terminal-verdict-004.finalization-diagnostic.md`

## Recommended Commit Type

`fix`

## Pre-Filing Preflight Subsection

Before filing this revision, Prime Builder runs candidate applicability and
clause preflights against this completed content. Filing is permitted only when
`missing_required_specs: []`, `missing_advisory_specs: []`, and blocking clause
gaps are all empty. The live version is rechecked after helper filing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
