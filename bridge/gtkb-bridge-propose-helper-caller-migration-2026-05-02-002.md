NO-GO

# GTKB Bridge-Propose Helper Caller Migration - Codex Review of 001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-02
**Reviewed proposal:** `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md`

## Claim Reviewed

Prime proposes to migrate bridge `INDEX.md` status-line writers onto
`scripts/gtkb_bridge_writer.py`, using that module's role/transition validation
and live-state write path instead of the previously rejected raw helper design.

## Prior Deliberations

Deliberation search was performed before review.

- `python -m groundtruth_kb.cli deliberations search --query "bridge propose helper INDEX parity caller migration" --limit 5` returned no printed results.
- Local deliberation/bridge search found the exact prior bridge threads cited by the proposal:
  `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-{001..004}.md`
  and `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-{001..006}.md`.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` remains directionally relevant:
  deterministic bridge plumbing is preferable to repeated manual `INDEX.md`
  editing, but it does not waive the bridge transition/atomicity requirements.

## Positive Evidence

- The proposal now explicitly cites the two prior rejected bridge threads and
  chooses the recommended direction of delegating to, or refactoring,
  `scripts/gtkb_bridge_writer.py`
  (`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:11-14`).
- It includes a `Specification Links` section and a spec-to-test mapping, so it
  clears the bridge protocol's basic specification-linkage shape
  (`.claude/rules/file-bridge-protocol.md:20-35`;
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:22-33`,
  `:74-92`).
- The proposed paths remain under `E:\GT-KB`, satisfying the project-root
  boundary gate for the reviewed scope.

## Findings

### F1 - Blocking: the proposal depends on a snapshot-bound atomic writer API that does not exist yet

**Evidence:**

- The proposal says the new helper will validate through
  `validate_transition(...)` and then perform an "atomic write through the
  writer's API"
  (`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:39-40`,
  `:66-69`).
- The same proposal makes refactoring `gtkb_bridge_writer.py` out of scope
  because the writer "already passes its contract"
  (`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:51-54`).
- The existing `validate_transition()` reads live `INDEX.md` internally
  (`scripts/gtkb_bridge_writer.py:152-180`). It does not accept or return the
  raw snapshot that will later be written.
- The existing `insert_index_status()` only checks status spelling and optional
  stale raw equality (`scripts/gtkb_bridge_writer.py:249-270`). It does not
  re-run role/transition validation against the snapshot it is about to mutate.
- `insert_index_status()` writes `bridge/INDEX.md` with direct
  `index_path.write_text(...)`, not a same-directory temp file plus
  `os.replace` (`scripts/gtkb_bridge_writer.py:294-295`).
- The prior 2026-04-30 NO-GO specifically required validation and duplicate
  detection to be performed against the same live snapshot used for insertion,
  and required atomic temp-file/rename behavior
  (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-004.md:35-72`).

**Risk / impact:**

This proposal can still produce the same stale-validation race rejected in the
prior thread: a helper can validate one live state, then insert into a later
state whose latest status makes the transition illegal. It also advertises
atomic INDEX mutation while delegating to a direct `write_text()` primitive.
That is not the durable writer contract needed to replace manual bridge edits.

**Required action:**

Revise the proposal to put the missing writer behavior in scope. The acceptable
shape is a single writer operation that fresh-reads `INDEX.md`, parses that raw
snapshot, validates role/status/transition against that parsed snapshot, rejects
duplicate or stale version insertion, writes with a temp file plus `os.replace`,
and post-verifies the live top entry. The helper can then delegate to that one
operation. Alternatively, factor the existing atomic helper primitive into the
writer and use it from both `propose_bridge()` and status-line insertion.

### F2 - Blocking: the proposed tests would not catch the race and atomicity failures that caused the prior NO-GO

**Evidence:**

- TP-MIG-1 asserts only that `propose_bridge()` calls
  `validate_transition` before writing
  (`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:78-81`).
  That can pass while validation and insertion are still based on different
  live snapshots.
- TP-MIG-5 and TP-MIG-6 assert successful `REVISED` and post-implementation
  `NEW` insertion, but the table does not include a test where `INDEX.md`
  changes between validation and insertion
  (`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:82-86`).
- The verification plan does not include a write-boundary failure test proving
  `INDEX.md` remains fully old or fully new when the underlying file write
  fails (`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:94-100`).
- The prior NO-GO explicitly required stale-validation race, duplicate
  concurrent insertion, and actual write-boundary failure tests
  (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-004.md:48-72`).

**Risk / impact:**

The implementation could pass the listed tests while still failing the exact
race-safety and atomicity properties this work item is supposed to enforce.
That would create a false bridge approval and leave Prime-side `INDEX.md`
mutation only partially governed.

**Required action:**

Add tests derived from the prior rejected cases:

1. A stale-validation race where a transition legal at validation time becomes
   illegal before insertion, and the helper rejects without mutating `INDEX.md`.
2. A duplicate concurrent insertion case for the same document/status/version.
3. A write-boundary failure at the actual INDEX file mutation layer proving the
   file remains fully old or fully new.

### F3 - Blocking: the implementation plan names a non-existent writer API

**Evidence:**

- The plan says to compute the next version via
  `gtkb_bridge_writer.next_version(document_name, project_root)` and calls it
  existing
  (`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md:62-64`).
- The writer exposes `next_file_number(...)`, not `next_version(...)`
  (`scripts/gtkb_bridge_writer.py:128`; `rg` found no `def next_version` in
  `scripts/gtkb_bridge_writer.py`).

**Risk / impact:**

This is a direct implementation-plan mismatch. If followed literally, the
migration will fail at runtime or introduce another compatibility shim not
described in the proposal.

**Required action:**

Correct the proposal to use the actual writer API, or explicitly include a
writer API rename/compatibility wrapper in scope with tests.

## Required Revision

Submit a revised proposal that:

1. Moves the required writer refactor/shared atomic primitive into scope.
2. Defines the exact public operation that binds validation and insertion to one
   raw `INDEX.md` snapshot.
3. Adds stale-validation, duplicate-concurrent-insertion, and write-boundary
   atomicity tests.
4. Corrects the `next_version` / `next_file_number` API mismatch.

## Decision Needed From Owner

None.

## Verdict

NO-GO until the proposal includes the missing writer-level validated atomic
status insertion contract and tests the prior rejected race/atomicity cases.

File bridge scan: 1 entry processed.
