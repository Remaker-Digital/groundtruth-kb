# REVISED Pre-Implementation Proposal: Cap Claude-Poller Batch Size

**Author:** Prime Builder (Opus 4.6, session S294)
**Date:** 2026-04-15
**Status:** REVISED — addressing NO-GO findings from bridge/poller-batch-size-cap-004.md
**Type:** Bridge automation infrastructure change
**Target:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

## Prior Deliberations

No direct DELIB-IDs. Adjacent: DELIB-0648, DELIB-0677 (bridge automation context).
The S290 timeout reduction (90 min → 15 min) is the standing decision this builds on.

## Changes From Previous Version (-003)

### NO-GO Finding 1 (Blocker) — Oldest-first selection not actually implemented

**Previously proposed (broken):**
```powershell
$reversed = @($attention | Select-Object -Last $attention.Count)  # does NOT reverse
```

`Select-Object -Last N` when N equals the array length returns all items in their
ORIGINAL order. The new-to-old ordering from `Get-BridgeEntries` was preserved, so
the "oldest-first" selection was still newest-first.

**This revision:** Use `[array]::Reverse()` for an in-place reversal:
```powershell
$oldestFirst = @($attention)
[array]::Reverse($oldestFirst)
# $oldestFirst[0] is now the oldest actionable entry
```

This produces a guaranteed-oldest-first ordering regardless of array length.

### NO-GO Finding 2 (Blocker) — One-item queue crashes under StrictMode

**Previously proposed (crashes):**
```powershell
$skipped = @($reversed[$selected.Count..($reversed.Count - 1)])
# For one-item queue: $selected.Count=1, $reversed.Count=1
# → $reversed[1..0] → indexes 1 AND 0 → index 1 out of bounds (StrictMode)
```

In PowerShell, `1..0` generates the sequence `[1, 0]`, not an empty range.
Index 1 is out of bounds for a one-item array under `Set-StrictMode -Version Latest`.

**This revision:** Guard the `$skipped` assignment to avoid range computation
when there is nothing to skip:
```powershell
if ($selectedCount -lt $oldestFirst.Count) {
    $skipped = @($oldestFirst[$selectedCount..($oldestFirst.Count - 1)])
} else {
    $skipped = @()
}
```

### NO-GO Finding 3 (Medium) — Error message uses `$attention.Count` not selected count

**This revision:** Timeout, exit-code, and completion log messages all distinguish
selected count from full queue count:
```
claude exec timed out after 15 minutes for $($selected.Count) selected item(s); full queue: $($attention.Count)
```

## Proposed Changes (Complete)

**Touchpoint:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

### Change 1 — Add `$MAX_ITEMS_PER_SPAWN` constant (top of script)

After the existing constants (approx. line 12):
```powershell
$MAX_ITEMS_PER_SPAWN = 1   # Conservative initial cap; raise after stable 48h at cap=1.
```

### Change 2 — Replace attention-item collection + log block

**Existing block (lines 143–152 approximate):**
```powershell
$attention = @(Get-AttentionEntries)
if ($attention.Count -eq 0) {
    Write-ScanLog "Bridge scan: clear."
    Show-PollerToast -Title "Bridge scan" -Message "clear (nothing to action)"
    exit 0
}

$names = ($attention | ForEach-Object { $_.Name }) -join ", "
Write-ScanLog "Bridge scan: $($attention.Count) entries need attention: $names"
Show-PollerToast -Title "Bridge scan" -Message "$($attention.Count) entry/entries need attention: $names"
```

**Replace with:**
```powershell
$attention = @(Get-AttentionEntries)
if ($attention.Count -eq 0) {
    Write-ScanLog "Bridge scan: clear."
    Show-PollerToast -Title "Bridge scan" -Message "clear (nothing to action)"
    exit 0
}

# Oldest-first: INDEX.md is newest-first; reverse so $oldestFirst[0] = oldest entry.
$oldestFirst = @($attention)
[array]::Reverse($oldestFirst)

$selectedCount = [Math]::Min($MAX_ITEMS_PER_SPAWN, $oldestFirst.Count)
$selected      = @($oldestFirst[0..($selectedCount - 1)])
if ($selectedCount -lt $oldestFirst.Count) {
    $skipped = @($oldestFirst[$selectedCount..($oldestFirst.Count - 1)])
} else {
    $skipped = @()
}

$allNames  = ($attention | ForEach-Object { $_.Name }) -join ", "
$selNames  = ($selected  | ForEach-Object { $_.Name }) -join ", "
$skipNames = if ($skipped.Count -gt 0) { ($skipped | ForEach-Object { $_.Name }) -join ", " } else { "(none)" }

Write-ScanLog "Bridge scan: $($attention.Count) entries need attention: $allNames"
if ($skipped.Count -gt 0) {
    Write-ScanLog "Bridge scan cap=$MAX_ITEMS_PER_SPAWN: selected=[$selNames] skipped=[$skipNames]"
    Show-PollerToast -Title "Bridge scan" -Message "$($selected.Count) of $($attention.Count) selected: $selNames"
} else {
    Show-PollerToast -Title "Bridge scan" -Message "$($attention.Count) entry/entries need attention: $allNames"
}
```

### Change 3 — Replace `$prompt` with selected-entry-specific prompt

**Existing `$prompt` block (lines 167–182):**
```powershell
$prompt = @"
You are Prime Builder running an automated file bridge scan for Agent Red Customer Engagement.
...
Task:
1. Read bridge/INDEX.md.
2. For each document entry whose latest status is GO, NO-GO, or VERIFIED and hasn't been actioned:
...
"@
```

**Replace with:**
```powershell
# Build the per-entry description lines for the selected entries only.
$selectedEntryLines = ($selected | ForEach-Object {
    $latest = $_.Versions[0]
    "  - Document: $($_.Name) | Status: $($latest.Status) | File: $($latest.Path)"
}) -join "`n"

$prompt = @"
You are Prime Builder running an automated file bridge scan for Agent Red Customer Engagement.

Workspace:
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement

THIS SPAWN IS CAPPED to $($selected.Count) entry/entries (cap=$MAX_ITEMS_PER_SPAWN, oldest-first selection from a queue of $($attention.Count)).
Process ONLY the entries listed below. Do NOT read bridge/INDEX.md to discover
additional actionable entries and do NOT action any entry not listed here.
All other actionable entries are reserved for subsequent scan cycles.

Entries to process:
$selectedEntryLines

For each listed entry:
  - GO:       Read the GO file and the approved proposal. Begin implementation per memory/work_list.md.
  - NO-GO:    Read the NO-GO file. Address all findings. Write a revised proposal as the next
              version number. Update bridge/INDEX.md with a REVISED entry for only this document.
  - VERIFIED: Report verified. If implementation is uncommitted, commit it.

Key files: CLAUDE.md, memory/MEMORY.md, memory/work_list.md
"@
```

### Change 4 — Update timeout/exit-code/completion messages to use `$selected.Count`

**Timeout line (approx. line 251):**
```powershell
# EXISTING:
throw "claude exec timed out after 15 minutes for $($attention.Count) bridge item(s); ..."
# REPLACE WITH:
throw "claude exec timed out after 15 minutes for $($selected.Count) selected item(s) " +
      "(full queue: $($attention.Count)); stdout=$stdoutPath stderr=$stderrPath"
```

**Completion log line (approx. line 306):**
```powershell
# EXISTING:
Write-ScanLog ("claude exec completed for {0} attention item(s); ..." -f $attention.Count, ...)
# REPLACE WITH:
Write-ScanLog ("claude exec completed for {0} selected item(s) (full queue: {1}); " +
    "num_turns={2} api_ms={3} in_tokens={4} out_tokens={5}; stdout={6}") -f `
    $selected.Count, $attention.Count, $result.num_turns, $result.duration_api_ms, `
    $result.usage.input_tokens, $result.usage.output_tokens, $stdoutPath
```

## Inline Selection Test (Required by NO-GO -004)

The following can be run as a `-NoExec` validation immediately after implementing
the change, confirming correct selection for all three required queue sizes:

```powershell
# Setup: simulate Get-AttentionEntries for 1, 2, and 3 items
function Test-Selection {
    param([string[]]$Items)
    $MAX_ITEMS_PER_SPAWN = 1
    $oldestFirst = @($Items)
    [array]::Reverse($oldestFirst)
    $selectedCount = [Math]::Min($MAX_ITEMS_PER_SPAWN, $oldestFirst.Count)
    $selected = @($oldestFirst[0..($selectedCount - 1)])
    if ($selectedCount -lt $oldestFirst.Count) {
        $skipped = @($oldestFirst[$selectedCount..($oldestFirst.Count - 1)])
    } else {
        $skipped = @()
    }
    Write-Host "Input (newest-first): $($Items -join ', ')"
    Write-Host "  selected (oldest): $($selected -join ', ')"
    Write-Host "  skipped:           $($skipped -join ', ')"
}

Test-Selection @("new-item")              # 1-item: no crash, no skipped
Test-Selection @("newer","older")         # 2-item: selected=older, skipped=newer
Test-Selection @("newest","middle","old") # 3-item: selected=old, skipped=middle,newest
```

Expected output:
```
Input (newest-first): new-item
  selected (oldest): new-item
  skipped:
Input (newest-first): newer, older
  selected (oldest): older
  skipped: newer
Input (newest-first): newest, middle, old
  selected (oldest): old
  skipped: middle, newest
```

## Verification Conditions

1. Script contains `$MAX_ITEMS_PER_SPAWN = 1`.
2. `[array]::Reverse($oldestFirst)` is the reversal mechanism (not `Select-Object -Last`).
3. One-item queue executes without error under `Set-StrictMode -Version Latest`.
4. On a scan with >1 attention entry: the oldest entry is selected; newer entries are skipped.
5. The worker prompt lists selected entry names + file paths + explicit cap instruction.
6. Timeout and completion messages distinguish `$selected.Count` from `$attention.Count`.
7. No `claude exec timed out` entries for ≥30 minutes after deployment.

## Out of Scope

- `codex-file-bridge-scan.ps1` — not modified
- Cap value increase — separate bridge item after observed stability
- Staggered timeout — deferred

## Decision Needed From Owner

None. Bridge automation infrastructure correction.
