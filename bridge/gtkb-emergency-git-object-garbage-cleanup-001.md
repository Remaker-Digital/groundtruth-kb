WITHDRAWN

bridge_kind: operational_state_change
Document: gtkb-emergency-git-object-garbage-cleanup
Version: 001
Author: prime-builder (Codex GPT-5, harness A) - interactive owner emergency cleanup session
Date: 2026-07-04
Responds-To: owner emergency directive in current Codex PB session

Project: GT-KB governance emergency bootstrap
Work Item: emergency-cleanup-no-existing-wi
Project Authorization: DELIB-20260704-EMERGENCY-GIT-OBJECT-GARBAGE-CLEANUP

author_identity: prime-builder
author_harness_id: A
author_session_context_id: 019f2955-5185-7063-9b1c-de683358bf8a
author_model: gpt-5
author_model_version: 5
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".git/objects/**", "groundtruth.db", "bridge/gtkb-emergency-git-object-garbage-cleanup-001.md"]

# WITHDRAWN - Emergency Git object garbage cleanup

This entry records an emergency-bootstrap cleanup that already completed under explicit owner instruction. It is WITHDRAWN so it remains an audit-trail artifact rather than an actionable implementation proposal.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge files are the durable audit surface for bridge/governance exceptions.
- GOV-ARTIFACT-APPROVAL-001 - retroactive owner approval is captured as DELIB-20260704-EMERGENCY-GIT-OBJECT-GARBAGE-CLEANUP.
- Governance Emergency-Bootstrap Exception Protocol - permits minimal repair when a foundational governance subsystem cannot operate and the normal bridge path is blocked by that failure.

## Owner Decisions / Input

Mike explicitly directed Prime Builder: Diagnose and remove the file accumulation. He identified this as explosive re-growth of stray files after a recent 400+ GB cleanup.

The durable owner decision is captured as DELIB-20260704-EMERGENCY-GIT-OBJECT-GARBAGE-CLEANUP.

## Deadlock Rationale

The E drive had 0 free bytes. The GT-KB database could not be opened for normal claim release or bridge-governance recording, producing sqlite3 disk I/O errors. Because the work-intent claim system and bridge audit path depended on the same unavailable disk/database capacity, the normal proposal to GO to implementation-start path was blocked by the defect being repaired.

This satisfied the emergency-bootstrap conditions:

1. Foundational governance subsystem active failure: work-intent/bridge claim and DA writes could not operate while the disk was full.
2. Normal bridge path blocked: a bridge proposal and claim release could not be recorded until disk space was restored.
3. Minimal repair: cleanup was limited to confirmed Git object-store garbage/unprotected loose objects and a temporary local index bit for groundtruth.db to stop immediate regrowth.

## Scope of Cleanup

The cleanup deleted only files under .git/objects after explicit checks:

- Pass 1 deleted 1,979 files named tmp_obj_* totaling approximately 219.32 GiB. Git had reported these as garbage via git count-objects -vH.
- Pass 2 deleted 9,655 loose object files totaling approximately 218.825 GiB only after confirming they were not reachable from refs, reflogs, or the real index. All were created from 2026-07-01 through 2026-07-03.

No source files, bridge history files, working-tree files, Git refs, packs, or real index entries were deleted.

## Cause Diagnosis

The Codex desktop app spawned child Git commands against the dirty tree, including git -c core.hooksPath=NUL -c core.fsmonitor= add -u and hash-object --no-filters. The command set included groundtruth.db, a tracked SQLite DB of approximately 543 MB. Repeated helper activity produced large compressed loose Git blobs around 128 MB each, and when the helper/index path did not retain those blobs in the real index they became unprotected loose object accumulation.

A temporary local mitigation was applied:

- git update-index --assume-unchanged -- groundtruth.db

That bit stops Codex from re-hashing groundtruth.db during this emergency session. It must be cleared before an intentional commit that needs to include groundtruth.db changes:

- git update-index --no-assume-unchanged -- groundtruth.db

## Verification Evidence

Before cleanup:

- Get-PSDrive E reported 0 free bytes.
- .git measured approximately 441.58 GiB.
- .git/objects measured approximately 441.38 GiB.
- git count-objects -vH reported garbage: 1979 and size-garbage: 219.32 GiB.

After cleanup:

- Get-PSDrive E reported approximately 472.05 GB free.
- .git measured approximately 3.671 GiB.
- git count-objects -vH reported count: 1433, size: 2.32 GiB, in-pack: 60095, size-pack: 1.14 GiB, garbage: 0, size-garbage: 0 bytes.
- A 20-second stability check showed no active git.exe children and no object-count increase.
- SQLite opened groundtruth.db successfully and the previously stuck bridge claim was released.

## Counterpart Verification Note

Same-session Loyal Opposition verification is not available because this was an owner-directed Prime Builder emergency repair of a governance deadlock. The evidence above is preserved for later independent Loyal Opposition audit if needed.

## Withdrawal Rationale

This is not an implementation proposal and does not request GO. The emergency action is already complete, was explicitly owner-authorized, and restored the disk and database state needed for normal governance to resume. WITHDRAWN is the correct bridge status for an audit-only emergency-bootstrap record.
