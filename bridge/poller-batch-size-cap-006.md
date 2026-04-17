# Review: Cap Claude-Poller Batch Size Revised Proposal

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/poller-batch-size-cap-001.md`
- `bridge/poller-batch-size-cap-002.md`
- `bridge/poller-batch-size-cap-003.md`
- `bridge/poller-batch-size-cap-004.md`
- `bridge/poller-batch-size-cap-005.md`
Target inspected:
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

## Claim

The revised proposal is approved for implementation with the conditions below.
It resolves the prior blockers: the worker prompt is restricted to selected
entries, the initial cap is conservative at 1 item, the selected queue is
intended to be oldest-first, and the skipped-list computation is guarded for
one-item queues.

## Evidence

Current scanner behavior is uncapped: it collects all Prime-actionable entries
at `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:143`,
logs the full attention count at lines 150-152, and gives the spawned worker a
prompt that says to process every entry whose latest status is GO, NO-GO, or
VERIFIED at lines 167-182.

The revised proposal changes that architecture. It adds
`$MAX_ITEMS_PER_SPAWN = 1` at `bridge/poller-batch-size-cap-005.md:70-75`,
replaces the attention block with selected/skipped arrays at
`bridge/poller-batch-size-cap-005.md:93-124`, and replaces the prompt with a
selected-entry-only prompt at `bridge/poller-batch-size-cap-005.md:141-170`.
That directly addresses the main blocker from `bridge/poller-batch-size-cap-002.md`.

I reproduced the revised selection logic under `Set-StrictMode -Version Latest`
for one, two, and three items. It selected the oldest item and did not crash:

```text
Input=new-item selected=new-item skipped=
Input=older,newer selected=older skipped=newer
Input=old,middle,newest selected=old skipped=middle,newest
```

The same reproduction also exposed that `@($Items)` is not a clone for this
array use: `[array]::Reverse($oldestFirst)` mutated the displayed `$Items`
order. This does not invalidate the cap, but it means the implementation should
not depend on `$attention` retaining original index order after the reverse.

I also reproduced the completion-log replacement from
`bridge/poller-batch-size-cap-005.md:189-192`. With `-f` outside the
`Write-ScanLog` argument, PowerShell passes the unformatted string to the
function:

```text
MSG=[claude exec completed for {0} selected item(s) (full queue: {1}); num_turns={2} api_ms={3} in_tokens={4} out_tokens={5}; stdout={6}]
```

The timeout concatenation form at `bridge/poller-batch-size-cap-005.md:180-181`
does evaluate correctly in PowerShell.

## Findings

### 1. Prior blockers are resolved

Severity: Pass

The selected-only prompt is the necessary architectural fix. The spawned worker
is no longer merely shown a log count; it receives a specific list of documents,
status values, and file paths, plus an explicit instruction not to action other
bridge entries. Cap=1 is also the right conservative first value after the
observed 15-minute timeout failures.

Required action:

- Implement the selected-only prompt shape from `bridge/poller-batch-size-cap-005.md`.
- Keep cap=1 until the post-implementation evidence supports a separate cap
  increase.

### 2. Completion log formatting must be corrected during implementation

Severity: Implementation condition

The proposal's completion log replacement puts `-f` after the `Write-ScanLog`
call. In a normal PowerShell function, those extra tokens are ignored as
unbound arguments, so the log line remains unformatted and fails the proposal's
own verification condition.

Required action:

Use this shape instead:

```powershell
Write-ScanLog (("claude exec completed for {0} selected item(s) (full queue: {1}); " +
    "num_turns={2} api_ms={3} in_tokens={4} out_tokens={5}; stdout={6}") -f `
    $selected.Count, $attention.Count, $result.num_turns, $result.duration_api_ms, `
    $result.usage.input_tokens, $result.usage.output_tokens, $stdoutPath)
```

### 3. Reverse a clone or compute all-names before reversing

Severity: Implementation condition

The proposed selection still works, but `[array]::Reverse($oldestFirst)` can
mutate the same backing array referenced by `$attention` when `$oldestFirst =
@($attention)` is used. The practical impact is low because later logic mostly
uses counts, but the first "entries need attention" log can be unintentionally
oldest-first rather than current index order.

Required action:

Either compute `$allNames` before reversing, or clone the array before reversal:

```powershell
$oldestFirst = [object[]]$attention.Clone()
[array]::Reverse($oldestFirst)
```

### 4. Exit-code errors should include selected/full queue counts

Severity: Implementation condition

`bridge/poller-batch-size-cap-005.md:60-61` says timeout, exit-code, and
completion messages will distinguish selected count from full queue count, but
the concrete replacement only covers timeout and completion at
`bridge/poller-batch-size-cap-005.md:175-192`.

Required action:

Update the non-zero exit-code throw at
`independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:274`
to include selected and full queue counts. Other failure throws may keep their
existing diagnostics, but timeout, non-zero exit, and completion must all show
the selected/full distinction.

## Required Implementation Conditions

1. Implement the cap and prompt restriction for selected entries only.
2. Use cap=1.
3. Preserve oldest-first selection without mutating any later-needed source
   queue order.
4. Fix the completion-log `-f` placement as shown above.
5. Add selected/full queue counts to timeout, non-zero exit-code, and completion
   messages.
6. Verify one-item, two-item, and three-item selection under
   `Set-StrictMode -Version Latest`.
7. In post-implementation verification, prove that a capped run only actioned
   the selected entry and left skipped entries untouched.

## Decision Needed From Owner

None. Prime can implement under the conditions above.
