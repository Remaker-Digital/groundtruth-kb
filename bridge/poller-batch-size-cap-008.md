# Verification Review: Cap Claude-Poller Batch Size Implementation

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/poller-batch-size-cap-001.md`
- `bridge/poller-batch-size-cap-002.md`
- `bridge/poller-batch-size-cap-003.md`
- `bridge/poller-batch-size-cap-004.md`
- `bridge/poller-batch-size-cap-005.md`
- `bridge/poller-batch-size-cap-006.md`
- `bridge/poller-batch-size-cap-007.md`
Target inspected:
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
- `independent-progress-assessments/bridge-automation/logs/claude-scan.log`

## Claim

The implementation cannot be verified because the modified PowerShell script
does not parse. The selected/skipped logic shape is otherwise close to the
approved design, but the scanner will fail before execution in its current form.

## Evidence

PowerShell parser check:

```text
170:40:$MAX_ITEMS_PER_SPAWN:
Variable reference is not valid. ':' was not followed by a valid variable name character.
Consider using ${} to delimit the name.
```

The failing line is:

```powershell
Write-ScanLog "Bridge scan cap=$MAX_ITEMS_PER_SPAWN: selected=[$selNames] skipped=[$skipNames]"
```

In a double-quoted PowerShell string, `$MAX_ITEMS_PER_SPAWN:` is parsed as a
scoped variable reference. Because the scope name is invalid here, the script
has a parse error.

Positive checks:

- `$MAX_ITEMS_PER_SPAWN = 1` exists at
  `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:13`.
- The implementation clones before reversing at lines 151-154.
- The selected-only prompt is present at lines 195-216.
- Timeout, exit-code, and completion messages now distinguish selected/full
  counts at lines 285-286, 309, and 341-344.
- Inline reproduction of the selection block under `Set-StrictMode -Version
  Latest` selected oldest-first for one, two, and three items and preserved
  `$attention` order.

Log observation:

- The script was last modified at 2026-04-15T07:30:27Z.
- The latest scan-log completion at 2026-04-15T07:32:31Z still uses the old
  wording, `claude exec completed for 2 attention item(s)`, from a process
  spawned before the implementation.
- No post-change capped scan with the new `selected item(s) (full queue: N)`
  wording has been observed yet.

## Findings

### 1. Scanner script has a parse error

Severity: Blocker

The scheduled poller cannot execute a script that fails PowerShell parsing. This
is more severe than a failed verification condition: future scan invocations may
fail before acquiring the intended behavior or writing normal diagnostics.

Required action:

Change the cap log line to delimit the variable before the colon, for example:

```powershell
Write-ScanLog "Bridge scan cap=${MAX_ITEMS_PER_SPAWN}: selected=[$selNames] skipped=[$skipNames]"
```

or:

```powershell
Write-ScanLog "Bridge scan cap=$($MAX_ITEMS_PER_SPAWN): selected=[$selNames] skipped=[$skipNames]"
```

Then rerun a parser check before resubmitting.

### 2. The 30-minute observation window is not yet satisfied

Severity: High

`bridge/poller-batch-size-cap-007.md` marks the no-timeout condition as pending.
That remains true. The current log window after the file modification is only a
few minutes old, and no successful post-change capped run has been observed.

Required action:

After the parse fix, observe at least one capped run and then a 30-minute window
with no `claude exec timed out` entries. The post-implementation report should
include the exact log timestamps for the capped run and the observation window.

## Required Conditions For VERIFIED

1. PowerShell parser check returns no errors for
   `claude-file-bridge-scan.ps1`.
2. The cap log line uses `${MAX_ITEMS_PER_SPAWN}` or `$($MAX_ITEMS_PER_SPAWN)`
   before the colon.
3. A live scan with more than one actionable item logs the selected/skipped
   split and processes only the selected oldest entry.
4. Completion, timeout, and non-zero exit logs use selected/full queue counts.
5. No `claude exec timed out` entries occur during a 30-minute observation
   window after the parse-fixed implementation is active.

## Decision Needed From Owner

None. This is a mechanical verification NO-GO.
