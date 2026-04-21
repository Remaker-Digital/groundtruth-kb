# Post-Incident Note: S292 Codex Poller Misdiagnosis

**Author:** Prime Builder (Opus 4.6, session S292)
**Date:** 2026-04-15
**Status:** NEW (informational audit trail, no Codex action requested)
**Type:** Bridge automation incident report

## Claim

At S292 session start I misdiagnosed a legitimate long-running Codex review as a hung
poller and killed its subprocess ~72 seconds before it would have completed. The bridge
has since recovered and re-dispatched codex exec on the full backlog, but ~25 min of
review work on `poller-batch-size-cap-009.md` was destroyed in the process.

No data corruption. No bridge file modification. No KB changes. The only damage is
wasted Codex compute time and a ~30 min delay on the bridge queue while the work
re-executes.

## Timeline

| Time (UTC) | Event |
|---|---|
| 13:46:10Z | Codex scan dispatched `codex exec` for `poller-batch-size-cap` (queue length 1 at that moment) |
| 13:46:10Z → 14:11:36Z | Codex actively wrote 151 KB of reasoning to stderr, running a 30-min empirical observation window on Claude scan.log to validate the S291 batch cap fix. Multiple `powershell Start-Sleep -Seconds 30/45` subprocesses for tailing. |
| ~14:08Z | S292 session starts; Prime Builder reads bridge state |
| ~14:09Z | Prime observes: codex-scan-status.json state=running 22 min stale, stdout file 2 bytes, process CPU 2 sec, no scan.log ticks since 13:46:10Z. Prime classifies Codex poller as "stuck". |
| ~14:10Z | Prime reports findings to owner and proposes kill of PID 18528 + PID 17156 |
| 14:11:23Z | (From stderr tail) Codex writes "The 14:09:50Z scheduled scan is clear. One final check after 14:11Z will close the observation condition." — i.e. Codex is ~72 seconds from finishing. |
| 14:11:35Z | Owner authorizes kill |
| 14:11:36Z | Prime executes Stop-Process on the PIDs (they had actually already terminated via an earlier implicit signal by the time the explicit call ran — scan.log shows `exited with -1` at this timestamp) |
| 14:11:36Z | Scan loop resumes, writes `ERROR: codex exec exited with -1` to scan.log; status file goes state=error |
| 14:13:10Z | Next scheduled Codex tick fires; detects 4 in-flight items (poller-emergency-repair, test-artifact-integrity-investigation, s291-phase1.5-verified-spec-audit, poller-batch-size-cap) and dispatches fresh codex exec |
| 14:14Z | Bridge confirmed live and processing backlog |

## Root cause of the misdiagnosis

Four diagnostic signals looked consistent with a hung subprocess but were in fact all
normal for a long-running codex exec review:

1. **Empty stdout file (2 bytes).** `codex exec` buffers stdout until process exit. Empty
   stdout is not evidence of work happening or not happening — it only reflects that
   the process hasn't finished.
2. **Low process CPU (2 sec in 22 min).** Codex was sleeping inside multiple
   `Start-Sleep -Seconds 30/45` subprocesses to observe live production behavior over a
   30-minute window. Low CPU is the intended behavior of an observation window.
3. **Stale codex-scan-status.json (22 min).** The Codex side of the S291 observability
   mirror only ticks on scan-loop state transitions (start/end of a codex exec dispatch),
   not within a single long run. Staleness during an in-flight codex exec is expected.
4. **Missing scan.log entries after 13:46:10Z.** The Codex scan loop is synchronous — it
   writes a new "Bridge scan: clear/N needs attention" line only after the previous codex
   exec returns. Absence of new lines during an in-flight run is the default state, not
   a failure signal.

Prime should have read the stderr file (151 KB and recent) before recommending kill.
`tail -30 codex-<runStamp>.stderr.log` would have immediately shown Codex actively
reasoning, counting log entries, and approaching completion.

## Consequence

- `poller-batch-size-cap-009.md` review lost; re-dispatched at 14:13:10Z
- The 4-item batch on this re-dispatch is larger than the original 1-item run. The Codex
  poller has **no `maxItemsPerSpawn` cap** (the batch-size-cap proposal only gave one to
  the Claude poller). This run could easily take 60+ min at the same review depth.
- No corruption or loss beyond compute time

## Preventive actions taken in S292

1. Wrote `feedback_codex_poller_not_hung.md` and added to MEMORY.md index so future
   sessions will check stderr before diagnosing a Codex run as hung.
2. Did NOT kill the new 14:13:10Z codex exec when it also showed an empty stdout file
   — instead, I am letting it run and will check stderr if it exceeds 60 min.

## Deferred proposals (not opened as bridge items in this session)

- **Codex-side `maxItemsPerSpawn` cap**, symmetric to the Claude-side cap delivered by
  `poller-batch-size-cap`. Would reduce worst-case review latency and limit the blast
  radius of any single hang. Requires owner direction before drafting.
- **Codex scan-status heartbeat during long runs.** Current mirror only updates on scan
  transitions. A heartbeat field updated every N seconds inside Invoke-CodexBridgeScan
  (perhaps by a child ticker) would eliminate the "stale status during active run"
  diagnostic ambiguity that triggered this incident.

## Note to Codex

No review or verdict requested on this file. This is an audit-trail entry filed to keep
the bridge self-documenting. The Codex review of `poller-batch-size-cap-009.md` that was
in progress at 13:46:10Z → 14:11:36Z should be restarted as part of the normal 14:13:10Z
batch dispatch. If any of the observation work from the killed run was externally visible
(e.g. partial writes to INDEX.md or bridge/) the re-review will naturally supersede it.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
