# Post-Implementation Report: Emergency Poller Repair + Observability Mirror (S291)

**Author:** Prime Builder (Opus 4.6, foreground session S291)
**Date:** 2026-04-15
**Status:** NEW — retroactive audit-trail entry for direct out-of-band repair
**Type:** Emergency infrastructure repair (direct edit, not bridge-mediated)

## Why This Entry Is Retroactive

The Claude-side bridge poller was broken from 2026-04-15 ~07:30 UTC until 2026-04-15 ~13:41 UTC — a **6-hour silent outage**. The root cause was a one-character PowerShell syntax error introduced by the autonomous Prime worker's own implementation of `poller-batch-size-cap-007`, which Codex correctly NO-GO'd at `-008` but the fix could not land via the bridge because the poller was the thing that needed to run the fix.

This created a **circular dependency** that the bridge protocol cannot resolve on its own: the autonomous loop cannot self-heal a broken poller using the broken poller. Direct foreground intervention was required.

Owner (Mike) explicitly authorized direct out-of-band action at 13:38 UTC with: "I need to emphasize that fixing the poller is extremely important. It is my top priority." After the initial fix landed at 13:41 UTC, Owner requested Option 3 (direct observability fix + retroactive bridge entry) at 13:48 UTC.

This bridge entry documents the work for audit trail compliance and to capture the lessons that informed it.

## Scope of Direct Edits

Two files were modified via direct foreground edit (not bridge-mediated):

### Edit 1 — `claude-file-bridge-scan.ps1` line 170 syntax fix

**Location:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:170`

**Before (broken):**
```powershell
Write-ScanLog "Bridge scan cap=$MAX_ITEMS_PER_SPAWN: selected=[$selNames] skipped=[$skipNames]"
```

**After (fixed):**
```powershell
Write-ScanLog "Bridge scan cap=${MAX_ITEMS_PER_SPAWN}: selected=[$selNames] skipped=[$skipNames]"
```

**Why broken:** PowerShell parses `$variable:` as a drive-scoped variable reference (e.g., `$env:PATH`). Without braces, `$MAX_ITEMS_PER_SPAWN:` reads as "the variable on drive MAX_ITEMS_PER_SPAWN" which is invalid. The script died at parse time with `InvalidVariableReferenceWithDrive` before it could write any log entry — which is why the outage was silent.

**Root source:** The autonomous Prime worker's implementation of `bridge/poller-batch-size-cap-007.md` introduced this line. Codex caught it on post-impl review and issued NO-GO at `-008`, but by then the broken file was on disk and the poller that would run the corrective revision was the broken one.

### Edit 2 — Observability mirror: Write-ScanStatus + 6 hook points

**Purpose:** Close the asymmetric observability gap between the Claude and Codex pollers. Before this edit, the Codex poller wrote `codex-scan-status.json` on every state transition while the Claude poller wrote nothing equivalent. The only Claude-side observability was ephemeral Windows toast notifications which demonstrably failed to surface the 6-hour outage.

**Additions to `claude-file-bridge-scan.ps1`:**

1. New constant `$StatusPath = Join-Path $LogDir "claude-scan-status.json"` (near line 13)
2. New function `Write-ScanStatus` mirroring the Codex pattern:
   - Atomic write via tmp + `Move-Item -Force`
   - UTF-8 encoding
   - Schema identical to `codex-scan-status.json` with one addition: `maxItemsPerSpawn` (useful because the Claude poller has a cap and the Codex poller does not)
   - Non-fatal fallback: if the status write fails, logs a WARN to `claude-scan.log` and continues
3. Six hook calls at state transitions:
   - `skipped` — at the lock-acquisition catch block (line ~184)
   - `clear` — when no attention items are found (line ~194)
   - `attention` — when attention items are found, before cap/spawn logic (line ~217 / ~221)
   - `running` — immediately before the claude.exe spawn, with runStamp + stdoutPath + stderrPath (line ~244)
   - `completed` — after successful spawn completion with full run metadata (line ~406)
   - `error` — in the outer catch block at script end (line ~413)

**Schema verification:** The Codex side's schema at `bridge/spec-hygiene-*` consumer tooling and at `independent-progress-assessments/bridge-automation/logs/codex-scan-status.json` uses the exact field names mirrored here.

## Verification Performed

1. **Syntax check via direct invocation:**
   ```
   powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .../claude-file-bridge-scan.ps1 -NoExec
   ```
   Result: clean parse, no errors, exit code 2 at the `-NoExec` gate (expected). Prior to edit 1 this produced `InvalidVariableReferenceWithDrive` at parse time.

2. **Live spawn end-to-end:**
   First manual run at 13:41:01 UTC hit `AUTH FAILURE` on a stale OAuth token (token file had not been refreshed in this session). Token refresh executed via:
   ```
   echo "$CLAUDE_CODE_OAUTH_TOKEN" > .../claude-oauth-token.txt
   ```
   Second manual run at 13:41:25 UTC completed successfully at 13:45:07 UTC with `num_turns=11 api_ms=209510 in_tokens=13 out_tokens=12838`. Processed `poller-batch-size-cap-008` (NO-GO) and posted `poller-batch-size-cap-009 REVISED` — the autonomous loop immediately began self-healing the proposal that originally caused the outage.

3. **Lock logic confirmation:**
   The scheduled task fired at 13:42:50 UTC while the manual run held the lock and correctly logged `"skipped: previous scan still running"`. Proves that post-fix, the lock semantics work end-to-end.

4. **Autonomous processing resumed:**
   - 13:45:50 → 13:51:57 — processed `s291-phase1.5-verified-spec-audit-006` (NO-GO), posted REVISED `-007`
   - 13:54:31 — scan found 1 remaining attention item (`test-artifact-integrity-investigation-002`)
   - Queue is draining at expected cadence

5. **Observability mirror verified:**
   `NoExec` smoke test at 13:54:31 UTC produced `claude-scan-status.json` with schema:
   ```json
   {
     "updatedAtUtc": "2026-04-15T13:54:31Z",
     "updatedAtLocal": "2026-04-15T06:54:31-07:00",
     "state": "attention",
     "message": "Bridge scan: 1 entries need attention: test-artifact-integrity-investigation",
     "attentionCount": 1,
     "attentionNames": ["test-artifact-integrity-investigation"],
     "runStamp": "",
     "stdoutPath": "",
     "stderrPath": "",
     "scanLogPath": "...",
     "indexPath": "...",
     "maxItemsPerSpawn": 1
   }
   ```

## Lessons Learned (for Codex review)

1. **The bridge protocol has a critical circular dependency when the failing component is the poller itself.** The autonomous Prime worker cannot fix the machinery it depends on. Out-of-band human-authorized foreground repair is the only escape hatch. This is a known limitation worth explicit documentation.

2. **Post-impl review is not sufficient for infrastructure proposals that land directly on disk.** Codex correctly caught the `$MAX_ITEMS_PER_SPAWN:` syntax error on `poller-batch-size-cap-008` post-impl review — but by then the broken file was already on disk and the fix could not be applied via the same loop. A **pre-commit syntax-validation hook** for PowerShell files in the bridge automation directory would have caught this before it landed. Possible follow-on proposal: `bridge/poller-infra-preflight-001.md` adding a `powershell -Command "[scriptblock]::Create((Get-Content script.ps1 -Raw))"` parse check to the implementation template.

3. **Observability must be symmetric.** The Claude poller was deployed with ephemeral toasts as its only owner-facing observability, while the Codex poller had a persistent JSON status file. The asymmetry was invisible until something broke. Going forward, any new poller or autonomous worker should ship with both forms of observability by default.

4. **Toast notifications are necessary but not sufficient for heartbeat signaling.** Windows toasts disappear from the Action Center after some time, can be blocked by Focus Assist / Do Not Disturb, and cannot be "tailed" programmatically. A persistent file on disk with a predictable schema is strictly better for liveness checks.

## Files Touched

| File | Change | Lines |
|---|---|---|
| `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` | Edit 1: fix `$MAX_ITEMS_PER_SPAWN:` syntax error | 1 line |
| `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` | Edit 2: add `$StatusPath`, `Write-ScanStatus`, 6 hook calls | ~55 lines added |
| `independent-progress-assessments/bridge-automation/.local/claude-oauth-token.txt` | Token refresh (no git tracking, .local/ is gitignored) | file content |

## Files NOT Touched

- `codex-file-bridge-scan.ps1` — no changes to the working Codex poller
- `codex-scan-status.json` schema — no changes; the Claude mirror conforms to it
- `INDEX.md` — will be updated as part of this bridge entry post; no other edits
- Any KB rows, any spec, any test, any work item
- `.claude/hooks/assertion-check.py` — untouched
- Claude Desktop binary path or token store

## Verification Conditions for Codex

To verify this post-impl entry:

1. Confirm `claude-file-bridge-scan.ps1:170` uses `${MAX_ITEMS_PER_SPAWN}:` (braces around variable name).
2. Confirm `claude-file-bridge-scan.ps1` contains a `Write-ScanStatus` function with the schema documented above.
3. Confirm 6 `Write-ScanStatus` call sites exist at skipped / clear / attention / running / completed / error state transitions.
4. Confirm `independent-progress-assessments/bridge-automation/logs/claude-scan-status.json` exists and is updated with each scan.
5. Confirm the claude poller scan log shows successful completions since 13:45:07 UTC.
6. Confirm no changes to `codex-file-bridge-scan.ps1` or `codex-scan-status.json`.
7. Confirm no KB writes occurred during this repair (verifiable by comparing `groundtruth.db` hash before/after the edits — hash drift during this window was caused by the unrelated concurrent `spec-hygiene-untested-verified-006` implementation, not by this repair).
8. Confirm the bridge backlog is now draining autonomously (see log trace in "Verification Performed" section).

## Decision Needed From Owner

**None.** This repair was performed under explicit owner authorization at 13:38 UTC. This bridge entry exists solely for audit trail compliance per the owner's Option 3 request ("direct edit now + retroactive bridge entry for audit trail after the fact").

## Recommended Follow-On Proposals

1. **Pre-commit syntax validation for poller PS1 files.** Small hook or helper that runs a `[scriptblock]::Create((Get-Content script.ps1 -Raw))` parse check before any autonomous Prime implementation of poller-affecting proposals. Prevents the `$var:` class of silent syntax error from ever landing.

2. **Poller liveness external watcher.** A tiny cron-like check (Windows scheduled task, 15-min interval) that compares `claude-scan-status.json.updatedAtUtc` against wall clock and writes a separate `poller-liveness.json` heartbeat the owner can watch. If the Claude or Codex status file is >10 min stale, the heartbeat writes a warning that surfaces via a more persistent mechanism than toast.

Both are candidate Phase 2 infrastructure improvements. This entry does not propose either — it merely flags them for future consideration.
