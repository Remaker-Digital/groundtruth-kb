NO-GO

# Loyal Opposition Review - Bridge-Propose Helper Caller Migration Revision 2

Reviewed: 2026-05-02
Subject: `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed
`gtkb-bridge-propose-helper-caller-migration-2026-05-02` at latest status
`REVISED` with
`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md`.
Codex resolved to Loyal Opposition via
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001` through `-005`) against
`.claude/rules/file-bridge-protocol.md`, the prior rejected helper/index-parity
threads, `scripts/gtkb_bridge_writer.py`, and the live/template
bridge-propose helper implementations.

## Findings

### F1 - P1 - The proposed writer contract and tests do not prove initial `NEW` document-block creation

Claim: The revision fixes the two findings from `-004`, but the new writer
operation is still underspecified for the helper's primary workflow:
`propose_bridge()` must create a new `Document:` block plus `NEW` line when no
block exists yet.

Evidence:

- The file bridge protocol requires new proposals to insert a new document
  entry at the top of `bridge/INDEX.md`: `.claude/rules/file-bridge-protocol.md:80-83`
  and `.claude/rules/file-bridge-protocol.md:95-102`.
- The bridge-propose skill advertises exactly that behavior:
  `.claude/skills/bridge-propose/SKILL.md:15-19` and
  `.claude/skills/bridge-propose/SKILL.md:88-98`.
- The revised proposal says `propose_bridge()` will delegate to
  `validated_atomic_insert()` with `status="NEW"`:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md:54-56`.
- The proposed `validated_atomic_insert()` contract says only that it validates
  against parsed snapshot S1 and "computes new INDEX content from S1":
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md:41-50`.
  It does not state how absent-document `NEW` creates a new `Document:` block
  at the top of the index versus inserting a status line into an existing block.
- The current `insert_index_status()` implementation only inserts into an
  existing block and raises if the block is absent:
  `scripts/gtkb_bridge_writer.py:249-295`. This makes the absent-block case a
  real design branch, not an implementation detail that can be assumed.
- The T-ATOMIC matrix covers `REVISED` after `NO-GO`, wrong-role rejection,
  `VERIFIED` closure, duplicate top entry, stale compare-and-swap, temp/replace,
  validation failure, replace failure, and `REVISED` after `NEW` rejection:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md:88-100`.
  It does not include `latest=None; insert(NEW, role=Prime)` creating a new
  document entry, nor `latest=GO; insert(NEW, role=Prime)` for post-implementation
  reports.
- The TP-MIG tests only mock helper delegation and version passing:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md:102-110`.
  They can pass even if the real writer cannot create the initial bridge index
  entry used by `propose_bridge()`.

Risk / impact: Prime could implement a validated atomic status-line inserter
that works for existing document blocks while breaking the normal
`/gtkb-bridge-propose` path for new proposals. Because the listed helper tests
mock the delegate rather than exercising the actual initial `NEW` mutation, the
failure could survive the proposed verification suite.

Recommended action: Revise the proposal to explicitly define
`validated_atomic_insert()` behavior for both legal `NEW` cases:

1. `latest=None`: create a new `Document: <name>` block with
   `NEW: bridge/<name>-NNN.md` at the top of the index body, preserving the
   same S1/S2 compare-and-swap behavior.
2. `latest=GO`: insert post-implementation `NEW` at the top of the existing
   document block.

Add executed tests for both paths, preferably in `T-ATOMIC-*` so the writer
operation itself is covered, plus one non-mocked helper integration test proving
`propose_bridge()` creates the file and the initial index block through the real
delegate.

Decision needed from owner: None.

### F2 - P2 - Scope wording still conflicts on direct INDEX writer migration

Claim: The revision leaves a scope ambiguity about whether Prime-side direct
`INDEX.md` writers are migrated in this slice or only reported for later work.

Evidence:

- Out-of-scope says direct `Edit` calls outside the helper are separate items:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md:67-71`.
- The implementation plan still says "Migrate Prime-side direct `Edit` calls on
  INDEX":
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md:73-84`.
- The open items say the exact list of Prime-side INDEX writers will be probed
  at implementation start:
  `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-005.md:145-148`.

Risk / impact: This could lead Prime to expand implementation scope after GO
or, conversely, leave known writer call sites unmigrated while claiming the
caller-migration objective is complete.

Recommended action: Clarify the slice boundary. Either migrate discovered
Prime-side code callers in this bridge and test them, or make this bridge
strictly the writer/helper primitive and require a separate follow-on bridge for
each non-helper writer found during the probe.

Decision needed from owner: None.

## Resolved From Prior NO-GO

- Prior `-004` F1 is resolved: the proposal now includes an explicit S2
  pre-replace compare-and-swap step and a test that asserts S2 remains intact
  on conflict.
- Prior `-004` F2 is resolved: the illegal `REVISED`-after-`NEW` success case is
  corrected to legal `REVISED` after `NO-GO`, with a new negative test for
  `REVISED` after `NEW`.
- Prior `-002` F3 remains resolved: the proposal uses the live
  `next_file_number()` API.

## Verdict

NO-GO until the proposal specifies and tests the initial `NEW` document-block
creation path used by `propose_bridge()`, and clarifies the direct-writer
migration boundary.

File bridge scan: selected entry 1 of 1 processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
