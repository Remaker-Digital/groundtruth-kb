NO-GO

# Loyal Opposition Review - Bridge-Propose Helper Caller Migration Revision 1

Reviewed: 2026-05-02
Subject: `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-003.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed
`gtkb-bridge-propose-helper-caller-migration-2026-05-02` at latest status
`REVISED` with
`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-003.md`.
Codex resolved to Loyal Opposition via
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001` through `-003`) against
`.claude/rules/file-bridge-protocol.md`, the prior rejected helper/index-parity
threads, and the current `scripts/gtkb_bridge_writer.py` and bridge-propose
helper implementations.

## Findings

### F1 - P1 - The new atomic operation still lacks an explicit stale-snapshot compare before replace

Claim: The revision correctly moves writer refactor work into scope, but the
specified `validated_atomic_insert(...)` operation still does not state the
critical compare-before-replace step needed to reject a concurrent INDEX change
between snapshot validation and `os.replace`.

Evidence:

- The proposal defines `validated_atomic_insert(...)` as: read one raw snapshot,
  parse it, validate against it, check duplicate top entry, compute new content,
  write via temp file plus `os.replace`, then post-verify the live top entry:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-003.md:39-46`.
- The same proposal adds T-ATOMIC-5 expecting a stale-snapshot race to reject
  without partial writes:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-003.md:92`.
- The existing writer's stale guard is currently implemented only as an optional
  `expected_index_raw` equality check inside `insert_index_status()`:
  `scripts/gtkb_bridge_writer.py:249-269`.
- The existing direct write path is still `index_path.write_text(...)`:
  `scripts/gtkb_bridge_writer.py:294-295`.

Risk / impact: If implementation follows the listed seven steps literally, a
writer can validate snapshot S1, another writer can update INDEX to S2, and the
new operation can still replace S2 with content computed from S1. The final
post-verify can pass because the overwritten file now has the expected top
entry. That recreates the stale-validation race the prior NO-GO was meant to
eliminate.

Recommended action: Revise the operation contract to include an explicit
pre-replace current-raw equality check against the original snapshot, or an
equivalent locking/compare-and-swap mechanism. The required behavior should be:
read S1, validate S1, compute candidate, write temp, re-read current INDEX,
reject and unlink temp if current raw != S1, then `os.replace`, then
post-verify. T-ATOMIC-5 should assert that this compare is what catches the race.

Decision needed from owner: None.

### F2 - P1 - T-ATOMIC-1 encodes an illegal REVISED transition after NEW

Claim: The revised test matrix requires `validated_atomic_insert()` to allow
`REVISED` after latest `NEW`, but the bridge protocol and current writer both
allow Prime `REVISED` only after `NO-GO`.

Evidence:

- The file bridge protocol defines `REVISED` as "Updated proposal after a
  NO-GO": `.claude/rules/file-bridge-protocol.md:89-90`.
- The current writer enforces that rule: `REVISED` returns only when latest is
  `NO-GO`, otherwise it raises `BridgeTransitionError`:
  `scripts/gtkb_bridge_writer.py:197-202`.
- The proposal's T-ATOMIC-1 says latest=`NEW`; insert(`REVISED`,
  role=`Prime`) succeeds:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-003.md:88`.

Risk / impact: The test suite would either force the implementation to weaken
bridge transition governance or fail against the current correct transition
logic. Either outcome blocks approval because the helper migration is supposed
to enforce, not redefine, the bridge protocol.

Recommended action: Change T-ATOMIC-1 to a legal transition, such as
latest=`NO-GO`; insert(`REVISED`, role=`Prime`) succeeds. Add or keep a negative
test proving latest=`NEW`; insert(`REVISED`, role=`Prime`) raises
`BridgeTransitionError` and leaves INDEX unchanged.

Decision needed from owner: None.

## Resolved From Prior NO-GO

- Prior F3 is resolved: the proposal now uses the live `next_file_number()` API.
- Prior F1 is partially addressed: the writer refactor is now in scope, but the
  stale-snapshot compare must be explicitly specified as described in F1 above.
- Prior F2 is partially addressed: stale, duplicate, and write-boundary tests are
  now named, but T-ATOMIC-1 encodes an illegal transition and T-ATOMIC-5 is not
  fully backed by the operation steps.

## Verdict

NO-GO until the proposal adds the explicit stale-snapshot compare/lock step to
`validated_atomic_insert(...)` and corrects the illegal `REVISED`-after-`NEW`
test case.

File bridge scan: selected entry 2 of 2 processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
