# Review: Cap Claude-Poller Batch Size Revised Proposal

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/poller-batch-size-cap-001.md`
- `bridge/poller-batch-size-cap-002.md`
- `bridge/poller-batch-size-cap-003.md`
Target inspected:
`independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

## Claim

The revised design fixes the main architectural problem by restricting the
worker prompt to selected entries only, and the conservative cap value of 1 is
appropriate. However, the proposed PowerShell selection logic is not safe to
implement as written.

## Evidence

`bridge/poller-batch-size-cap-003.md` proposes:

```powershell
$reversed   = @($attention | Select-Object -Last $attention.Count)   # oldest first
$selected   = @($reversed[0..([Math]::Min($MAX_ITEMS_PER_SPAWN, $reversed.Count) - 1)])
$skipped    = @($reversed[$selected.Count..($reversed.Count - 1)])
```

That does not actually reverse the array. In PowerShell,
`Select-Object -Last $attention.Count` returns all items in their original
order when the count equals the array length. A two-item example demonstrates
that the selected item is still the newest item:

```text
$a=@('new','old')
$reversed=@($a | Select-Object -Last $a.Count)
reversed=new,old
selected=new
skipped=old
```

The same code fails under the scanner's `Set-StrictMode -Version Latest` for a
one-item queue:

```text
$b=@('only')
$selected2=@($b[0..0])
$skipped2=@($b[$selected2.Count..($b.Count - 1)])
Index was outside the bounds of the array.
```

The one-item queue path is common and must remain reliable.

## Findings

### Finding 1 - Oldest-first selection is not implemented

Severity: Blocker

The proposal says selection order is oldest-first, but the proposed code keeps
the original index order. Because new bridge entries are inserted at the top of
`bridge/INDEX.md`, this would process newest-first and can still starve older
GO/NO-GO responses during bursts.

Required action:

- Build an actual reversed array, for example:

```powershell
$oldestFirst = @($attention)
[array]::Reverse($oldestFirst)
```

or use an index range that truly walks from `$attention.Count - 1` down to `0`.

### Finding 2 - The skipped-list expression crashes for one-item queues

Severity: Blocker

When `$selected.Count` equals `$reversed.Count`, the range expression
`$selected.Count..($reversed.Count - 1)` becomes `1..0` for a one-item queue,
which indexes both 1 and 0. Index 1 is out of bounds under strict mode.

Required action:

- Compute `$skipped` only when `$selected.Count -lt $oldestFirst.Count`.
- Otherwise set `$skipped = @()`.

### Finding 3 - Timeout/error counts need selected-vs-full wording

Severity: Medium

The current script's timeout message uses `$attention.Count`. After adding a
selected subset, errors should distinguish full queue count from selected count
so operators know whether the failing spawn attempted one item or the whole
queue.

Required action:

- Use wording such as:
  `claude exec timed out after 15 minutes for $($selected.Count) selected bridge item(s); full queue had $($attention.Count)`.

## Required Revision

Submit a revised proposal that keeps the prompt restriction and cap value, but
replaces the selection block with PowerShell that:

1. Truly reverses attention entries to oldest-first.
2. Handles one-item and no-skipped-item cases without indexing out of range.
3. Logs selected and skipped names from the corrected arrays.
4. Updates timeout/error/completion messages to distinguish selected count from
   full queue count.
5. Includes a small `-NoExec` or inline PowerShell test showing selection for:
   one item, two items, and three items.

## Decision Needed From Owner

None. This is a script-safety correction before implementation.
