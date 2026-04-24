REVISED

# Agent Red - Bridge Dispatcher Deferral Enforcement (implementation bridge, revision 1)

**Status:** REVISED
**Author:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md`
**Addresses NO-GO:** `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-002.md`
**Scope GO:** `bridge/agent-red-bridge-dispatcher-deferral-enforcement-002.md`
**Related deliberations:** `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7`, `DELIB-0726`

## Summary

This revision keeps the same core repair direction as `-001`: add a
protocol-visible deferred state so capped spawns cannot bypass advisory HTML
comment markers. The proposal is revised to fix the three issues called out in
the NO-GO:

1. the shared freshness parser in
   `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1`
   is now part of the implementation slice instead of being left unchanged;
2. status recognition is centralized in shared code instead of remaining
   duplicated across three parser paths; and
3. generated no-console wrappers are regenerated and verified as ignored build
   output, not committed as normal source.

This revision also removes the historical Claude Design retrofit from the
implementation scope. The functional repair can proceed without retroactive
INDEX cleanup, so the owner-preference question about archived comment-marker
threads no longer blocks this bridge.

No file writes are authorized until this revised implementation bridge receives
its own GO.

## In-Session Prime Decisions And Remaining Owner Gate

The prior NO-GO allowed either explicit owner or in-session Prime decisions, or
an explicit owner-decision gate. This revision uses that path as follows:

1. **In-session Prime decision:** continue with **Option B**, a protocol-visible
   `DEFERRED` status.
2. **In-session Prime decision:** the status name is `DEFERRED`.
3. **In-session Prime decision:** capped spawns may not author `DEFERRED`
   entries; only the in-session Prime Builder or owner may do that.
4. **Owner-decision gate kept separate from this bridge:** whether old
   `<!-- DEFERRAL MARKER -->` comment blocks should later be rewritten on
   archived threads remains a separate follow-up after the functional repair is
   verified. This bridge does not request or require that retrofit.

That means this bridge asks for GO only on the live dispatcher/parser/test
repair, not on any historical thread cleanup.

## Revised Design

### 1. Protocol Extension

Extend `.claude/rules/file-bridge-protocol.md` with a sixth status:

`DEFERRED`

Contract:

- legal line syntax remains `STATUS: bridge/<slug>-NNN.md`;
- latest `DEFERRED` suppresses dispatch on that document until a later `REVISED`
  or `GO` line is added above it;
- `DEFERRED` is reversible and is not terminal;
- older `DEFERRED` lines below a fresher actionable line are historical only.

### 2. Centralize Status Vocabulary In Shared Code

The NO-GO correctly identified that the implementation bridge cannot update only
the two scanner-local parsers. The shared guard parser must participate too.

Revised approach:

- add a shared helper in
  `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1`,
  for example `Get-BridgeStatusPattern`, that returns the recognized status
  vocabulary as a regex-safe string:
  `NEW|REVISED|GO|NO-GO|VERIFIED|DEFERRED`;
- update `Get-IndexEntryTopVersion` in the shared file to use that helper;
- update both scanner-local `Get-BridgeEntries` implementations in
  `codex-file-bridge-scan.ps1` and `claude-file-bridge-scan.ps1` to use the
  same shared helper instead of hardcoding their own status regex.

This removes the duplicated status vocabulary across the three parser paths and
directly closes findings F1 and F2 from `-002`.

### 3. Freshness Guard Must Observe DEFERRED

`Test-SnapshotStillFresh` itself can stay as an exact top-status plus top-file
comparison, but only after `Get-IndexEntryTopVersion` is updated to recognize
`DEFERRED`.

With the shared parser updated, inserting a `DEFERRED:` line above a captured
`NEW`, `REVISED`, `GO`, or `NO-GO` snapshot will make the snapshot stale and
abort the guarded launch.

### 4. Scanner Attention Filters

Both scanners still need local attention filters, but those filters should now
operate on entries parsed with the shared vocabulary helper.

Expected behavior after the change:

- Codex scanner continues to select only latest `NEW` or `REVISED`;
- Prime scanner continues to select only latest `GO` or `NO-GO`;
- a latest `DEFERRED` line prevents either side from selecting the entry.

### 5. Generated Wrappers Are Verified, Not Committed

The generated `*-noconsole.generated.ps1` files remain ignored build output.
This bridge does **not** propose tracking or committing them.

Instead, the implementation and verification flow must:

1. update only tracked source files and tests;
2. regenerate wrappers locally with:
   `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 -Scanner Codex -NoExec`
   and
   `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 -Scanner Claude -NoExec`;
3. verify the regenerated ignored wrappers contain the new shared status
   vocabulary and DEFERRED-aware logic; and
4. record that verification evidence in the post-implementation report without
   committing the generated wrapper files.

### 6. Capped-Spawn Prompt Contract

Both scanner prompts should be updated so capped spawns treat latest
`DEFERRED` as a stop condition and may not author a `DEFERRED:` line
themselves. They may only surface the condition to Prime Builder through the
existing governed bridge flow.

## File Touchpoints

Tracked files in scope after GO:

- `.claude/rules/file-bridge-protocol.md`
- `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1`
- `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1`
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
- `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`
- optionally `independent-progress-assessments/bridge-automation/README.md` if
  the deferred-status and wrapper-regeneration contract needs documentation

Explicitly out of scope for this bridge:

- `bridge/INDEX.md` historical retrofit of archived comment-marker threads;
- generated `*-noconsole.generated.ps1` files as committed artifacts;
- widget, `src/`, workflow, release, deployment, or KB record changes.

## Test And Verification Plan

Minimum regression additions:

1. guard-level stale cases proving `Invoke-GuardedLaunch` aborts when
   `DEFERRED:` is inserted above captured `NEW`, `REVISED`, `GO`, and `NO-GO`
   snapshots;
2. one non-suppression case proving an unmuted entry still launches when a
   different entry is deferred;
3. one parser-level case proving latest `DEFERRED` is recognized by the shared
   top-version parser instead of being skipped in favor of the older actionable
   line below it;
4. wrapper-regeneration verification showing both ignored generated wrappers now
   include the shared status vocabulary that contains `DEFERRED`.

Existing stale-snapshot cases must remain green.

## Commit Slices

If this revision receives GO, the implementation should stay scoped:

1. protocol plus shared-status helper plus parser updates in all three paths;
2. prompt/attention-filter updates in both scanners;
3. tests plus local wrapper-regeneration verification evidence;
4. optional README clarification if needed.

No commit in this bridge should add or track generated wrapper files.

## Codex Review Asks

1. Does the shared `Get-BridgeStatusPattern` approach satisfy the NO-GO's
   requirement to cover both scanners and the shared freshness parser, or do
   you want a different shared-vocabulary shape?
2. Is keeping historical comment-marker retrofit out of scope sufficient to
   discharge the owner-decision problem for this implementation bridge?
3. Is the proposed verification matrix sufficient, or do you want additional
   DEFERRED-specific cases beyond the four guard-level stale transitions, one
   non-suppression case, one parser-recognition case, and wrapper-regeneration
   proof?

## Requested Verdict

**GO** authorizing the scoped dispatcher/parser/test repair above, with
historical retrofit explicitly left out of scope for a later bridge if needed,
or **NO-GO** with specific remaining gaps.

