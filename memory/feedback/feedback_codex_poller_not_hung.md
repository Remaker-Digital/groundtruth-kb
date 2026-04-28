---
name: Codex poller long-running reviews are normal — check stderr, not stdout
description: codex exec buffers stdout and can legitimately run 20-30+ min during empirical observation reviews; never diagnose "hung" from missing stdout alone
type: feedback
originSessionId: 12953966-5fb1-486d-abf4-94fa82fdb93a
---
When triaging the Codex poller, **do not treat a missing or empty stdout file as evidence
the run is hung**. `codex exec` buffers stdout until process exit, but streams reasoning
text to stderr in real-time. Long reviews can legitimately run 20-30+ minutes when Codex
is doing empirical observation work (e.g., tailing logs across a 30-minute window with
Start-Sleep subprocesses to validate a live fix).

**Why:** S292 session start incident. I observed:
- `codex-scan-status.json` state=running, 22 min stale
- Claimed `codex-NNNN.stdout.log` path missing or 2 bytes
- Codex process CPU only 2 seconds in 22 minutes

...and concluded the Codex poller was stuck, analogous to the S291 Claude-poller outage.
I recommended kill + resume and the owner authorized it. I killed PID 18528 at 14:11:36Z.
Reading stderr afterward revealed 151 KB of active Codex reasoning including the literal
line "The final cutoff is about 72 seconds away." Codex was running a legitimate 30-min
empirical observation window on `poller-batch-size-cap-009.md` and was ~72 seconds from
completing its review. I destroyed ~25 min of review work for nothing.

**How to apply:** Before recommending kill of any Codex exec subprocess:

1. **Check if the child process is still alive** via `Get-Process -Id <pid>` — this
   is the ONLY reliable live signal under the current wrappers. The status file does
   not record the child pid today, so you must discover it via
   `Get-Process | Where-Object { $_.ProcessName -like '*codex*' }` and cross-reference
   with the recorded `runStamp`. (Once the external-poller-liveness-watcher proposal
   lands, the status file will include `childPid` and `childStartUtc` directly.)
2. Check process CPU growth over 2-3 minutes. If CPU is increasing, the process is
   doing work even if stdout/stderr files look empty.
3. **Do NOT check stderr file size or mtime during an active run.** Both poller
   wrappers use `$proc.StandardError.ReadToEndAsync()` and only `Set-Content` the
   buffered bytes AFTER `WaitForExit()` returns. During a live run, the stderr file
   is either missing or zero bytes. The 151 KB stderr I saw in S292 was written on
   process exit from the kill signal, NOT during the run — a misreading that
   shaped my original post-incident guidance.
4. Only if the child process is gone OR CPU is flat over 5+ minutes is "hung" a
   defensible diagnosis.

**Corrected S292 understanding:** My original version of this memory recommended
"check stderr size/recency" as the primary liveness signal. That was wrong under the
current wrapper architecture. Codex's NO-GO on
`bridge/external-poller-liveness-watcher-001.md` caught the error by citing the
wrapper source code (lines 176-187 in codex-file-bridge-scan.ps1). The correct
primary signal is child pid presence, not file activity.

**Also:** The Codex observability mirror (`codex-scan-status.json`) only ticks on scan
loop transitions (start/end of a codex exec dispatch), not within a single long run. A
stale `updatedAtUtc` during an active codex exec is expected, not a failure signal. The
Claude-side mirror is different — it ticks at every scan interval because the Claude
poller uses a different architecture (Get-AttentionEntries fires independently of the
exec dispatch).
