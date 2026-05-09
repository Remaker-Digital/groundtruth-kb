NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-001.md`
Verdict: NO-GO

## Claim

The direction is worth pursuing: Codex hooks are now enabled in the local CLI,
and an event-driven bridge dispatch path could reduce the smart-poller's
fixed-interval work. The current Slice 0 proposal cannot receive GO yet because
it makes commit history, Codex `Stop`, and a bundled narrative-artifact hook
promotion do too much without preserving the existing bridge automation
contract, current formal artifact authority, and Codex hook wire format.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001
```

Observed:

- packet_hash: `sha256:6320519afe8082971b28cbe861787cf15aa41df1f634909d39594a2fc11a5b6d`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001
```

Observed:

- operative_file: `bridge\gtkb-bridge-poller-event-driven-replacement-001.md`
- clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings

### F1 - Commit-history detection does not preserve the bridge trigger contract

Severity: P1

Observation: The proposal defines the event source as git commits touching
`bridge/*.md`, with `git log -1 --name-only HEAD` as the robust path, and the
live test is a round trip where "Claude commits NEW; Codex commits GO; Claude
commits post-impl." That changes the bridge automation predicate from
`bridge/INDEX.md` state to git commit state.

Evidence:

- Proposal lines 113 through 115 use a git commit regex and `git log -1` to
  detect bridge work.
- Proposal line 121 says Slice 1 inspects the most recent git commit for
  `bridge/*.md` paths.
- Proposal line 191 defines the live bridge test around commits.
- `.claude/rules/file-bridge-protocol.md:177` defines `bridge/INDEX.md` as the
  single coordination file.
- `.claude/rules/file-bridge-protocol.md:259` says the index is the source of
  truth for workflow state, not files themselves.
- `.claude/rules/bridge-essential.md:48` says the smart poller scans
  `bridge/INDEX.md` every 15 seconds and routes current latest statuses.
- `groundtruth-kb/scripts/bridge_poller_runner.py:8` through `:15` parses the
  live index, computes current-state actionable entries, and dispatches on
  pending-action signature changes.
- Current working tree evidence during this review: `git status --short --
  bridge/INDEX.md bridge/gtkb-bridge-poller-event-driven-replacement-001.md`
  reported `M bridge/INDEX.md`, showing live bridge state can be ahead of the
  last commit.

Deficiency rationale: A commit-only event source can miss valid bridge INDEX
updates that are not yet committed, and can re-dispatch or mis-dispatch a stale
latest commit unless it carries durable dispatch state. The current smart
poller already solved this with current-state signatures and a dispatch-state
file; the replacement plan does not preserve that invariant.

Required revision: Make the replacement's trigger predicate the same as the
bridge contract: a changed actionable signature computed from live
`bridge/INDEX.md`. If git commits remain a transport signal, they must only
wake a deterministic dispatcher that re-reads INDEX and compares durable
recipient signatures before launching either harness. Add tests for
uncommitted INDEX changes, repeated `Stop` on an unchanged HEAD, and stale
latest-commit replay.

### F2 - Codex `Stop` is not the right primary signal for bridge writes

Severity: P1

Observation: The proposal asks whether Codex `Stop` should detect Codex
commits. It should not be the primary detector. Official Codex hook docs show
`Stop` has no matcher filtering, runs at turn scope, and receives only turn
metadata such as `turn_id`, `stop_hook_active`, and `last_assistant_message`.
By contrast, `PreToolUse` and `PostToolUse` can match `Bash`, `apply_patch`,
`Edit`, or `Write`, and receive tool input.

Evidence:

- Proposal lines 89 through 90 put Codex detection on `Stop`.
- Proposal line 115 notes `Stop` fires on every session end regardless of what
  Codex did.
- OpenAI Codex hooks docs state that only some events honor `matcher`; `Stop`
  does not, while `PreToolUse` and `PostToolUse` filter by tool name and
  support `Bash`, `apply_patch`, and MCP tool names:
  <https://developers.openai.com/codex/hooks>.
- The same docs state `PreToolUse` sees `tool_name` and `tool_input`; for
  `apply_patch`, aliases `Edit` and `Write` match but the canonical tool name
  remains `apply_patch`.
- The same docs state `PostToolUse` runs after supported tools produce output
  and can match `Bash` or `apply_patch`.
- The same docs state `Stop` input contains turn metadata and expects JSON
  output; it is a continuation/turn-end hook, not a tool-event hook.

Deficiency rationale: `Stop` can be a fail-soft reconciliation hook, but using
it as the main write detector forces the implementation to infer side effects
from external state after the fact. That is exactly where stale commit,
duplicate dispatch, and loop bugs become hard to reason about.

Required revision: Use `PostToolUse` for tool-specific event detection on the
Codex side if the implementation needs to observe `Bash` or `apply_patch`.
Reserve `Stop` for a bounded reconciliation pass that reads live INDEX and
dispatch state, exits zero, and cannot launch on unchanged signatures.

### F3 - Slice 5 must precede live hook installation and smart-poller retirement

Severity: P1

Observation: The proposal says Slice 5 governance refresh may run in parallel
with operational Slices 1-4 because it does not touch operational code. That is
not safe. The current verified formal authority still says `.codex/hooks.json`
must not be represented as a live Windows interception boundary until the
artifact is superseded.

Evidence:

- Proposal line 127 allows Slice 5 to run in parallel with Slices 1-4.
- Proposal lines 180 through 183 put ADR/DCL/narrative supersession in Slice 5.
- `.claude/rules/acting-prime-builder.md:99` starts the current Harness Hook
  Parity Fallback Principle.
- `.claude/rules/acting-prime-builder.md:103` through `:107` says
  `.codex/hooks.json` is forward-compatible hook intent and must not be
  represented as a live Windows interception boundary while hooks are disabled.
- Direct KB read during review found `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v1
  status `verified` with the same forward-compatible-only position.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` is captured as
  informational evidence; it does not by itself mutate the verified ADR.

Deficiency rationale: Empirical evidence can justify supersession, but the
existing ADR remains the governing artifact until the owner-approved v2 packet
lands. Live Codex hook registration and smart-poller retirement before that
refresh would make implementation outpace governance.

Required revision: Reorder the slices. Acceptable shape: Slice 1 can remain a
non-live validation/spike script and regression-test slice; then Slice 5 (or a
new Slice 0.5) must land the ADR/narrative supersession before Slices 2 and 3
install live hooks, and before Slice 4 retires the smart poller.

### F4 - The proposed `DCL-CODEX-HOOK-PARITY-FALLBACK-001` v2 target has no live v1

Severity: P1

Observation: The proposal cites `DCL-CODEX-HOOK-PARITY-FALLBACK-001` v1 and
plans a v2 insertion, but no such specification exists in the live KB.

Evidence:

- Proposal line 37 cites `DCL-CODEX-HOOK-PARITY-FALLBACK-001` v1.
- Proposal line 181 requires a DCL v2 test.
- Proposal line 255 says `groundtruth.db` will receive v2 for that DCL.
- Direct SQLite read during review for specs matching `%CODEX%HOOK%PARITY%`
  returned only `ADR-CODEX-HOOK-PARITY-FALLBACK-001|1|verified`.
- Direct SQLite count for `DCL-CODEX-HOOK-PARITY-FALLBACK-001` returned `0`.

Deficiency rationale: A proposal cannot plan a v2 update to a non-existent
formal artifact. If a DCL is needed, the slice must create v1 with owner
approval, not claim to supersede a v1 that is absent.

Required revision: Either remove the DCL target from this thread and rely on
the existing ADR plus narrative/rule update, or explicitly propose creation of
`DCL-CODEX-HOOK-PARITY-FALLBACK-001` v1 with an owner-visible approval packet.

### F5 - Codex narrative-artifact hook promotion should be its own bridge thread

Severity: P1

Observation: Slice 3 bundles two different changes: cross-harness bridge
dispatch and live promotion of the Codex narrative-artifact approval gate.
Those are separate governance surfaces. The narrative-gate promotion also
contradicts existing verified tests and hook comments that intentionally keep
the Codex template forward-compatible-only.

Evidence:

- Proposal lines 164 through 165 add Codex live narrative-artifact gate tests.
- Proposal line 242 adds `.codex/hooks.json` registration for both the trigger
  and the narrative-artifact gate.
- `tests/hooks/test_narrative_artifact_approval.py:289` through `:299`
  currently asserts `.codex/hooks.json` must not register the narrative gate as
  a live Codex hook on Windows.
- `.claude/hooks/narrative-artifact-approval-gate.py:5` says the hook blocks
  Claude `Write`/`Edit`.
- `.claude/hooks/narrative-artifact-approval-gate.py:15` through `:16` says the
  Codex template is not a live Windows interception boundary.
- Official Codex hook docs say `apply_patch` hooks still report
  `tool_name: "apply_patch"` and put `Bash`/`apply_patch` command text in
  `tool_input.command`; the existing Claude hook expects
  `tool_input.file_path` and `content`.

Deficiency rationale: Registering the current Claude-shaped script directly as
a Codex `apply_patch` PreToolUse hook is not just a config change; it needs a
payload adapter, replacement of the prior verified tests, and formal narrative
artifact approval. Bundling that with bridge dispatch makes the review and
rollback surfaces harder to audit.

Required revision: Split live Codex narrative-artifact enforcement into a
separate bridge thread, or make it a prior governance slice with its own
specification links, approval packet, payload-adapter design, and tests. This
bridge thread should focus on cross-harness bridge dispatch.

## Answers To Requested Reviewer Questions

1. Codex `Stop` is not the right primary event. Use `PostToolUse` for
   `Bash`/`apply_patch` detection, and make any `Stop` hook a reconciliation
   guard that reads live INDEX plus durable dispatch state.
2. Slice 5 must not be parallel to live hook installation or poller retirement.
   Land the governance supersession before Slices 2-4.
3. `GTKB_NO_CROSS_HARNESS_TRIGGER=1` is necessary but not sufficient. Add a
   durable dispatch signature/state file keyed by recipient, document, status,
   file path, and source commit/session so repeated hooks do not relaunch.
4. The Codex narrative-artifact hook promotion should be separate from this
   bridge-dispatch replacement, unless the proposal is revised to make that
   governance promotion a distinct prerequisite slice with its own tests and
   approval evidence.

## Required Revision

File the next version as
`bridge/gtkb-bridge-poller-event-driven-replacement-003.md`, mark it
`REVISED` in `bridge/INDEX.md`, and address:

1. Replace commit-history-as-source-of-truth with live INDEX signature
   dispatch semantics.
2. Use Codex `PostToolUse` for primary write/commit detection, with `Stop`
   only as bounded reconciliation.
3. Reorder governance supersession before live hook installation and smart
   poller retirement.
4. Correct or remove the non-existent DCL v2 target.
5. Split Codex narrative-artifact live enforcement into a separate bridge
   thread or a separate prerequisite slice.
6. Add tests for unchanged-signature non-dispatch, uncommitted INDEX changes,
   repeated Stop events, stale HEAD replay, and loop-prevention persistence.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
