NO-GO

# Proposal Review: External Poller Liveness Watcher

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/external-poller-liveness-watcher-001.md`

## Claim

The liveness-watcher problem is real, but the proposed `stderr` mtime signal is
not valid for the current poller implementation. Both pollers buffer child
stderr in memory and write the stderr log file only after the child process
exits. During a legitimate long-running `codex exec` or `claude.exe` run, the
watcher would see a stale or missing stderr file and could still misclassify the
run as `warn` or `dead`.

## Evidence

Codex poller status schema has no process id and records only paths:

```text
independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:24
Write-ScanStatus(...)

independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:36-48
payload fields: updatedAtUtc, state, message, attentionNames, runStamp,
stdoutPath, stderrPath, lastMessagePath, scanLogPath, indexPath
```

Codex stderr is not streamed to the file:

```text
independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:172
$proc = [System.Diagnostics.Process]::Start($psi)

independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:176-178
$stdoutTask = $proc.StandardOutput.ReadToEndAsync()
$stderrTask = $proc.StandardError.ReadToEndAsync()
$completed = $proc.WaitForExit(5400000)

independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:184-187
$stdoutTask.Wait()
$stderrTask.Wait()
Set-Content -LiteralPath $stdoutPath -Value $stdoutTask.Result
Set-Content -LiteralPath $stderrPath -Value $stderrTask.Result
```

Claude poller follows the same buffered pattern:

```text
independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:327
$proc = [System.Diagnostics.Process]::Start($psi)

independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:330-341
$stdoutTask = $proc.StandardOutput.ReadToEndAsync()
$stderrTask = $proc.StandardError.ReadToEndAsync()
$completed = $proc.WaitForExit($claudeTimeoutMs)

independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:348-351
$stdoutTask.Wait()
$stderrTask.Wait()
Set-Content -LiteralPath $stdoutPath -Value $stdoutTask.Result
Set-Content -LiteralPath $stderrPath -Value $stderrTask.Result
```

Current status-file example also confirms no child pid is available for the
watcher to inspect:

```text
codex-scan-status.json fields: updatedAtUtc, updatedAtLocal, state, message,
attentionCount, attentionNames, runStamp, stdoutPath, stderrPath,
lastMessagePath, scanLogPath, indexPath
```

## Blocking Finding

The proposed dual-signal design still relies on a non-live fine signal. Stderr
mtime is only updated after process exit, so it cannot distinguish "alive but
working" from "stale/hung" under the current wrappers. That was the exact class
of S292 failure the watcher is supposed to prevent.

## Required Revision

Revise the design before implementation. A viable watcher needs at least one
live signal that exists while the subprocess is still running:

1. Add `processId` and child start time to the poller status file immediately
   after `Process.Start(...)`, then have the watcher verify the process still
   exists and matches expected executable/path context.

2. Alternatively, change the pollers to stream stdout/stderr to disk during the
   run, then use mtime or size deltas. This is a larger behavior change and must
   be verified against both wrappers.

3. Include scheduled-task state as a coarse signal, but do not use task state
   alone as proof of child health.

4. Keep the watcher output external, but include enough fields to explain the
   verdict: status age, task state, pid presence, child age, last live-signal
   timestamp, and reason.

## Answers To Prime Questions

The current dual-signal approach is not sufficient. Process existence by pid is
needed unless stderr is changed to stream during execution.

Mtime is simpler than size deltas, but only after the pollers actually stream to
the file. With the current wrappers, neither mtime nor size is a valid liveness
signal during a run.

The watcher's own liveness can reasonably be trusted to Windows Task Scheduler
for v1, but its output should include `updatedAtUtc` so humans can notice if the
watcher itself stops ticking.

## Recommended Action

Submit a revised proposal that uses pid/process verification or first changes
the pollers to stream logs. Do not implement the current stderr-mtime watcher.

