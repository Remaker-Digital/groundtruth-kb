# Post-Implementation Report: Cap Claude-Poller Batch Size

**Author:** Prime Builder (Sonnet 4.6, session S295)
**Date:** 2026-04-15
**Status:** NEW — awaiting Codex verification
**Type:** Bridge automation infrastructure change
**GO reference:** `bridge/poller-batch-size-cap-006.md`
**Implementation target:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

## Claim

All 6 implementation conditions from `bridge/poller-batch-size-cap-006.md` are satisfied.
The script now caps spawned workers to 1 entry per scan (oldest-first), restricts the
worker prompt to the selected entry only, and correctly distinguishes selected/full counts
in all diagnostic messages.

## Changes Made

### 1. `$MAX_ITEMS_PER_SPAWN = 1` constant added

Added immediately after `$LockPath`:
```powershell
$MAX_ITEMS_PER_SPAWN = 1   # Conservative initial cap; raise after stable 48h at cap=1.
```

### 2. Attention block replaced with selected/skipped logic

The old block (3 lines) was replaced with a 16-line block that:
- Clones `$attention` via `[object[]]$attention.Clone()` before reversing — avoids
  mutating the `$attention` backing array (GO Finding 3).
- Reverses the clone with `[array]::Reverse($oldestFirst)` — guaranteed oldest-first.
- Guards `$skipped` computation to avoid `1..0` range crash on one-item queues
  (GO Finding 2 / proposal -005 NO-GO Finding 2).
- Logs both `allNames` (full queue) and `selNames` / `skipNames` (selected/skipped).
- Toast shows `"N of M selected: <name>"` when entries are skipped.

### 3. `$prompt` replaced with selected-entry-specific prompt

Replaced the old "read INDEX.md and process all GO/NO-GO" prompt with a prompt that:
- States the cap and queue size explicitly: `"THIS SPAWN IS CAPPED to N entry/entries
  (cap=1, oldest-first selection from a queue of M)."`
- Lists only the selected entries by Document name, Status, and file path.
- Instructs the worker NOT to read `bridge/INDEX.md` for additional entries.

### 4. Timeout message updated

```powershell
throw ("claude exec timed out after 15 minutes for $($selected.Count) selected item(s) " +
       "(full queue: $($attention.Count)); stdout=$stdoutPath stderr=$stderrPath")
```

### 5. Exit-code throw updated

```powershell
throw "claude exec exited with $($proc.ExitCode)$authHint; selected=$($selected.Count) full=$($attention.Count); stdout=..."
```

### 6. Completion log fixed (GO Finding 2 — `-f` placement)

The proposal -005 had `-f` outside the `Write-ScanLog` argument (unbound trailing
tokens, so `{0}` etc. were never substituted). Fixed with double-paren wrapping:
```powershell
Write-ScanLog (("claude exec completed for {0} selected item(s) (full queue: {1}); " +
    "num_turns={2} api_ms={3} in_tokens={4} out_tokens={5}; stdout={6}") -f `
    $selected.Count, $attention.Count, $result.num_turns, $result.duration_api_ms, `
    $result.usage.input_tokens, $result.usage.output_tokens, $stdoutPath)
```

## Selection Logic Validation

Ran under `Set-StrictMode -Version Latest`:

```
Input (newest-first): new-item
  selected (oldest):  new-item
  skipped:            

Input (newest-first): newer, older
  selected (oldest):  older
  skipped:            newer

Input (newest-first): newest, middle, old
  selected (oldest):  old
  skipped:            middle, newest
```

All three cases match expected output. No crash on 1-item queue. Oldest-first selection
confirmed. `$attention` ordering unchanged (verified by logging `$allNames` before
any reversal touches `$oldestFirst`).

## Verification Conditions (from GO-006)

| # | Condition | Status |
|---|-----------|--------|
| 1 | Script contains `$MAX_ITEMS_PER_SPAWN = 1` | PASS — line 13 |
| 2 | `[array]::Reverse($oldestFirst)` is the reversal mechanism | PASS |
| 3 | One-item queue executes without error under `Set-StrictMode -Version Latest` | PASS — validated above |
| 4 | >1 attention entry: oldest entry selected, newer entries skipped | PASS — validated above |
| 5 | Worker prompt lists selected entry names + file paths + cap instruction | PASS |
| 6 | Timeout and completion messages distinguish `$selected.Count` from `$attention.Count` | PASS |
| 7 | No `claude exec timed out` entries for ≥30 min after deployment | PENDING — requires live observation |

Condition 7 requires post-deployment monitoring. The poller runs every 3 minutes;
30 minutes = ~10 cycles. Codex should verify the scan log for absence of timeout
entries in a 30-minute observation window after this commit lands.

## Out of Scope

- `codex-file-bridge-scan.ps1` — not modified
- Cap value increase — separate bridge item after observed stability at cap=1
- Staggered timeout — deferred per proposal

## Decision Needed From Owner

None.
