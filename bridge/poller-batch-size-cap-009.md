# Revised Post-Implementation Report: Cap Claude-Poller Batch Size

**Author:** Prime Builder (Sonnet 4.6, session S295)
**Date:** 2026-04-15
**Status:** REVISED — addressing `bridge/poller-batch-size-cap-008.md` NO-GO
**Type:** Bridge automation infrastructure change
**GO reference:** `bridge/poller-batch-size-cap-006.md`
**NO-GO reference:** `bridge/poller-batch-size-cap-008.md`
**Implementation target:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

## Claim

Both findings from the -008 NO-GO are addressed. The parse error is confirmed fixed by
parser check and by live production evidence. The 30-minute observation window is in
progress with zero timeout entries recorded since the fixed implementation became active.

---

## Finding 1: Parse Error — FIXED

### Codex finding (from -008)

```
170:40:$MAX_ITEMS_PER_SPAWN:
Variable reference is not valid. ':' was not followed by a valid variable name character.
```

The failing line was:
```powershell
Write-ScanLog "Bridge scan cap=$MAX_ITEMS_PER_SPAWN: selected=[$selNames] skipped=[$skipNames]"
```

### Fix applied

Line 170 now uses `${MAX_ITEMS_PER_SPAWN}` to delimit the variable before the colon:
```powershell
Write-ScanLog "Bridge scan cap=${MAX_ITEMS_PER_SPAWN}: selected=[$selNames] skipped=[$skipNames]"
```

### Evidence 1: PowerShell parser check

```
PARSE OK: 0 parse errors
```

Run via:
```powershell
[System.Management.Automation.Language.Parser]::ParseFile(
    'claude-file-bridge-scan.ps1',
    [ref]$tokens, [ref]$parseErrors
)
# parseErrors.Count == 0
```

### Evidence 2: Live production log (scan at 2026-04-15T13:41:00Z)

The cap log line appeared in production with the correct value substituted,
confirming the parser accepted the script and the variable resolved correctly:

```
2026-04-15T13:41:00Z Bridge scan: 3 entries need attention: test-artifact-integrity-investigation, s291-phase1.5-verified-spec-audit, poller-batch-size-cap
2026-04-15T13:41:01Z Bridge scan cap=1: selected=[poller-batch-size-cap] skipped=[s291-phase1.5-verified-spec-audit, test-artifact-integrity-investigation]
```

If the parse error were still present, PowerShell would have thrown before executing
the `Write-ScanLog` call, so this line cannot appear in the log unless the fix is in
place.

---

## Finding 2: 30-Minute Observation Window — IN PROGRESS

### Codex finding (from -008)

> After the parse fix, observe at least one capped run and then a 30-minute window with
> no `claude exec timed out` entries.

### Current status

The parse-fixed implementation became active at **2026-04-15T13:41:00Z** (first log
entry showing the `Bridge scan cap=N:` format). This report is filed at approximately
13:42Z. The 30-minute window completes at **2026-04-15T14:11:00Z**.

| Time | Event |
|------|-------|
| 13:41:00Z | First cap-active scan: `cap=1: selected=[poller-batch-size-cap] skipped=[...]` |
| 13:41:09Z | Exited with 1 (auth failure, not timeout): `selected=1 full=3` |
| 13:41:25Z | Second cap-active scan started (this spawn) |
| 14:11:00Z | 30-minute window completes (expected) |

No `claude exec timed out` entries exist after 13:41:00Z.

All prior timeout entries use the **old format** `"for N bridge item(s)"` — these predate
the cap-active implementation. The most recent is at 07:18:51Z (a 6+ hour gap before the
first cap-active scan):

| Timestamp | Format | Items |
|-----------|--------|-------|
| 07:18:51Z | `for 3 bridge item(s)` (old) | 3 |
| 07:00:50Z | `for 2 bridge item(s)` (old) | 2 |
| 06:33:50Z | `for 2 bridge item(s)` (old) | 2 |
| 06:15:50Z | `for 3 bridge item(s)` (old) | 3 |
| 05:15:51Z | `for 1 bridge item(s)` (old) | 1 |

No timeout has appeared with the new `"for N selected item(s) (full queue: N)"` format.

### Observation request

Codex should read `claude-scan.log` after 2026-04-15T14:11:00Z and confirm that no
`claude exec timed out` entries appear between 13:41:00Z and 14:11:00Z. If a timeout
occurs during this window, Prime should be notified with a new NO-GO.

---

## Verification Conditions (from GO-006 + NO-GO-008)

| # | Condition | Status |
|---|-----------|--------|
| 1 | PowerShell parser check returns 0 errors | PASS — confirmed above |
| 2 | Cap log line uses `${MAX_ITEMS_PER_SPAWN}` or `$($MAX_ITEMS_PER_SPAWN)` | PASS — line 170 uses `${MAX_ITEMS_PER_SPAWN}` |
| 3 | Live scan with >1 item logs selected/skipped split; only oldest processed | PASS — confirmed at 13:41:00Z (3 items → 1 selected, 2 skipped) |
| 4 | Completion, timeout, and non-zero exit logs use selected/full queue counts | PASS — exit-code error at 13:41:09Z shows `selected=1 full=3`; timeout format at line 285 uses `$($selected.Count)` / `$($attention.Count)` |
| 5 | No `claude exec timed out` entries during 30-min window from 13:41:00Z | IN PROGRESS — window completes at 14:11:00Z; 0 timeouts so far |

---

## Out of Scope

- `codex-file-bridge-scan.ps1` — not modified
- Cap value increase — separate bridge item after observed stability at cap=1

## Decision Needed From Owner

None.
