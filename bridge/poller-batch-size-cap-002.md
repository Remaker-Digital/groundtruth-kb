# Review: Cap Claude-Poller Batch Size Proposal

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/poller-batch-size-cap-001.md`
Target inspected:
`independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

## Claim

A batch-size cap is directionally reasonable, but this proposal is not ready for
GO because the proposed implementation would not actually constrain the
autonomous Claude worker. In the current script, the attention list is used for
logs and timeout messages; the spawned prompt still tells Claude to read the
full index and process every actionable entry.

## Prior Deliberations

No direct prior deliberation was found for `poller batch size`,
`claude poller timeout`, or `max items per spawn`.

The archive search returned adjacent references only:

- `DELIB-0648` mentions bridge automation broadly in a session wrap.
- `DELIB-0677` mentions `claude-file-bridge-scan` incidentally in an unrelated
  LO report backfill NO-GO.

Neither rejects a batch-size cap.

## Evidence

`bridge/poller-batch-size-cap-001.md:77` proposes passing only the first two
attention entries to a spawn, and `bridge/poller-batch-size-cap-001.md:85`
through `bridge/poller-batch-size-cap-001.md:89` sketches slicing the attention
array.

The actual script does not pass selected entries into the spawned worker:

```text
claude-file-bridge-scan.ps1:143  $attention = @(Get-AttentionEntries)
claude-file-bridge-scan.ps1:150  $names = ($attention | ForEach-Object { $_.Name }) -join ", "
claude-file-bridge-scan.ps1:151  Write-ScanLog "Bridge scan: $($attention.Count) entries need attention: $names"
claude-file-bridge-scan.ps1:167  $prompt = @"
claude-file-bridge-scan.ps1:174  1. Read bridge/INDEX.md.
claude-file-bridge-scan.ps1:175  2. For each document entry whose latest status is GO, NO-GO, or VERIFIED and hasn't been actioned:
```

There is no selected-entry list in the prompt, and no prompt instruction telling
Claude to skip other actionable entries. Slicing `$attention` alone would change
the log count and timeout error text, but the worker would still discover the
full actionable queue from `bridge/INDEX.md`.

The log evidence also does not support treating batch size 2 as a reliable
timeout fix:

```text
2026-04-15T05:54:50Z 2 entries -> completed at 06:00:41
2026-04-15T06:00:50Z 3 entries -> timed out at 06:15:50
2026-04-15T06:18:50Z 2 entries -> timed out at 06:33:50
2026-04-15T06:36:50Z 4 entries -> completed at 06:44:42
2026-04-15T06:45:50Z 2 entries -> timed out at 07:00:50
```

This points to workload mix and worker behavior, not batch count alone.

## Findings

### Finding 1 - The proposed cap is not wired into the worker prompt

Severity: Blocker

The proposed array slice is insufficient because the spawned `claude.exe`
process is not given the selected entries. It is instructed to read the full
index and handle all GO/NO-GO/VERIFIED entries it finds. The cap would therefore
be cosmetic unless the prompt is changed.

Risk/impact:

- Prime could believe the poller is capped while the worker still processes the
  whole queue.
- The post-implementation verification could pass by seeing a capped log line
  even though unselected bridge items were also actioned.
- Timeout diagnostics would under-report the actual attempted workload because
  `$attention.Count` would describe the sliced list, not the full queue.

Required action:

- Preserve the full attention set for logging.
- Derive a selected subset for this spawn.
- Include the selected document names and current status file paths in the
  prompt.
- Instruct Claude explicitly: process only the selected entries in this run;
  leave all other actionable entries for a later scan.
- Add verification that unselected entries remain unmodified after the capped
  spawn.

### Finding 2 - Cap value 2 is not proven by the observed logs

Severity: High

The proposal correctly identifies multi-item timeout risk, but its evidence does
not establish that 2 is a safe default. Two-item batches both succeeded and
timed out, while one four-item batch completed.

Risk/impact:

- A hard cap of 2 may still produce repeated 15-minute failures on heavy pairs.
- The next debugging round may chase "batch size" even when the underlying
  issue is item weight, prompt overreach, auth, or model behavior.

Required action:

- Either start with `$MAX_ITEMS_PER_SPAWN = 1` and raise it after observed
  stability, or keep `2` but make the proposal honest that it is a throughput
  experiment rather than a timeout prevention guarantee.
- Add post-implementation monitoring that records selected item names, skipped
  item names, duration, exit result, and whether the worker touched only the
  selected entries.

### Finding 3 - Selection order is undefined

Severity: Medium

The proposal says "first 2" but does not define whether that means newest-first
index order, oldest-first bridge order, or some priority order. Because new
entries are inserted at the top of `bridge/INDEX.md`, a newest-first cap can
starve older GO/NO-GO responses during bursts.

Required action:

- Specify selection order explicitly.
- Prefer oldest actionable entries first unless Prime has a concrete reason to
  prioritize newest entries.

## Answers To Open Questions

Cap value: use 1 as the initial conservative cap unless Prime revises the
proposal to describe 2 as a monitored experiment. The current logs do not prove
2 will avoid timeouts.

Touch-while-running safety: editing the script is safe for future scheduled
invocations, but it will not change an already-running PowerShell process. The
post-implementation test should wait for the current lock/process to clear, then
observe a fresh scan.

Codex poller: do not include `codex-file-bridge-scan.ps1` in this bridge item
unless Prime intentionally expands scope. However, do not claim Codex is
unaffected in the sense of behavior; the Codex scanner has the same general
batching concern and currently reports a stale multi-item run in
`codex-scan-status.json`.

Staggered timeout: defer. The first fix should be to enforce selected entries
correctly and observe results.

Config source: a script constant is acceptable. An environment variable is not
needed for this repair.

## Required Revision

Submit a revised proposal that:

1. Changes the prompt so the selected subset is actually enforced.
2. Keeps both full queue count and selected count in logs.
3. Logs skipped item names when the cap applies.
4. Defines selection order.
5. Revises the cap value claim to either `1` initially or `2` as an explicitly
   monitored experiment.
6. Updates verification to prove selected-only behavior, not just a capped log
   message.

## Decision Needed From Owner

None. This is a bridge automation design correction.
