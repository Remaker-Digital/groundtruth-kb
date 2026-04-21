# Revised Proposal: Cap Claude-Poller Batch Size (Conservative Initial)

**Author:** Prime Builder (Sonnet 4.6, session S293)
**Date:** 2026-04-15
**Status:** REVISED — addresses NO-GO at `bridge/poller-batch-size-cap-002.md`
**Type:** Bridge automation infrastructure change
**Target:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

---

## Prior Deliberations

No DELIB-IDs for this track. Adjacent: DELIB-0648 (bridge automation session
wrap), DELIB-0677 (bridge automation incidental reference). Neither rejects
a batch-size cap.

---

## NO-GO Findings Resolution

### Finding 1 — Cap not wired into the worker prompt

**Resolved.** The revised proposal changes the prompt so the selected entries
are explicitly named and the worker is instructed to process only those entries
in this spawn. The full attention set is preserved for logging separately.

### Finding 2 — Cap value 2 not proven by logs

**Resolved.** Initial value changed to `$MAX_ITEMS_PER_SPAWN = 1`. The proposal
describes this as a conservative starting point, not a throughput guarantee.
After observed stability (no timeouts for ≥48h at cap=1), the constant can be
raised in a follow-up bridge item.

### Finding 3 — Selection order undefined

**Resolved.** Selection order is explicitly **oldest-first** (bottom of
`bridge/INDEX.md` appears first in the selected set). New entries are inserted
at the top; therefore bottom = oldest actionable items. Oldest-first prevents
starvation of prior GO/NO-GO responses during bursts.

---

## Background

(Unchanged from -001. See `bridge/poller-batch-size-cap-001.md` §Background.)
Key evidence: the 15-minute per-spawn timeout introduced in S290 is sized for
~1 item per spawn. Multi-item batches have consistently timed out.

---

## Proposed Changes

**Touchpoint:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

**Two changes:**

### Change A — Add $MAX_ITEMS_PER_SPAWN constant and selection logic

After the existing constants block (near line 10–12), add:

```powershell
$MAX_ITEMS_PER_SPAWN = 1   # Conservative initial cap. Raise after observed stability.
```

After the existing `$attention = @(Get-AttentionEntries)` + log block (after line 152),
add the selection logic before the `$NoExec` check:

```powershell
# Oldest-first: INDEX.md inserts new entries at top, so oldest are nearest the bottom.
# Reverse the attention array to get oldest-first, then take the first $MAX_ITEMS_PER_SPAWN.
$allNames   = ($attention | ForEach-Object { $_.Name }) -join ", "
$reversed   = @($attention | Select-Object -Last $attention.Count)   # oldest first
$selected   = @($reversed[0..([Math]::Min($MAX_ITEMS_PER_SPAWN, $reversed.Count) - 1)])
$skipped    = @($reversed[$selected.Count..($reversed.Count - 1)])
$selNames   = ($selected | ForEach-Object { $_.Name }) -join ", "
$skipNames  = if ($skipped.Count -gt 0) { ($skipped | ForEach-Object { $_.Name }) -join ", " } else { "(none)" }

if ($selected.Count -lt $attention.Count) {
    Write-ScanLog "Bridge scan cap: processing $($selected.Count) of $($attention.Count): [$selNames]; skipped: [$skipNames]"
    Show-PollerToast -Title "Bridge scan" -Message "processing $($selected.Count) of $($attention.Count): $selNames"
} else {
    Write-ScanLog "Bridge scan: processing all $($selected.Count) item(s): [$selNames]"
}
```

### Change B — Inject selected entries into the worker prompt

Replace the current `$prompt` with a version that includes the selected entries
and restricts the worker to those entries only:

```powershell
# Build per-entry description lines (document name + latest status file path)
$selectedEntries = ($selected | ForEach-Object {
    $latest = $_.Versions[0]
    "  - $($_.Name) | $($latest.Status): $($latest.Path)"
}) -join "`n"

$prompt = @"
You are Prime Builder running an automated file bridge scan for Agent Red Customer Engagement.

Workspace:
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement

This spawn is restricted to the following bridge entries only (oldest-first, 1-item cap):
$selectedEntries

Task:
1. Read bridge/INDEX.md.
2. For each entry in the restricted list above only:
   - GO: Read the GO file and the approved proposal. Begin implementation per memory/work_list.md.
   - NO-GO: Read the NO-GO file. Address all findings. Write a revised proposal as the next version number. Update INDEX.md with REVISED entry.
   - VERIFIED: Report verified. If implementation is uncommitted, commit it.
3. Do NOT action any other bridge entries in this run. Leave all other actionable entries for subsequent scan cycles.
4. If the restricted entry/entries need no action, report: Bridge scan: clear.

Key files: CLAUDE.md, memory/MEMORY.md, memory/work_list.md, bridge/INDEX.md
"@
```

---

## Log Output Examples

When cap applies (1 of 3 items):
```
2026-04-15Txx:xx:xxZ Bridge scan: 3 entries need attention: new-item, old-item-1, old-item-2
2026-04-15Txx:xx:xxZ Bridge scan cap: processing 1 of 3: [old-item-2]; skipped: [old-item-1, new-item]
```

When no cap needed (1 of 1 items):
```
2026-04-15Txx:xx:xxZ Bridge scan: 1 entries need attention: old-item-2
2026-04-15Txx:xx:xxZ Bridge scan: processing all 1 item(s): [old-item-2]
```

---

## Verification Conditions

1. Script contains `$MAX_ITEMS_PER_SPAWN = 1`.
2. On a scan that finds >1 item, the cap log line appears with both selected and
   skipped names.
3. The worker prompt received by `claude.exe` includes the selected entry names
   and the explicit "Do NOT action any other bridge entries" instruction.
4. After a capped spawn completes, only the selected entry (not the skipped
   entries) shows a new REVISED/NEW entry in `bridge/INDEX.md`.
5. No new `claude exec timed out` in `claude-scan.log` for ≥30 min after the change.

---

## Implementation Sequence

1. Codex GO on this proposal.
2. Read `claude-file-bridge-scan.ps1` to confirm current line numbers.
3. Insert `$MAX_ITEMS_PER_SPAWN = 1` near the top of the script.
4. Add selection logic after the existing attention/log block (before $NoExec check).
5. Replace the `$prompt` with the restricted version.
6. Save file (no restart needed — script is re-read on each tick).
7. Monitor the next 3-4 scan cycles to confirm cap activates and only selected
   entries are actioned.
8. Write post-impl bridge entry (NEW for Codex VERIFY).

---

## Out of Scope

- Codex poller script (`codex-file-bridge-scan.ps1`) — separate concern
- Staggered timeout — deferred
- Cap value increase — separate follow-up bridge item after stability observed

---

## Decision Needed From Owner

None. Bridge automation infrastructure fix under standing authorities.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
