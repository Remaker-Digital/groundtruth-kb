# Bridge Automation

Windows scheduled-task scripts that drive the Prime ↔ Codex file-bridge
protocol. The two scanners poll `bridge/INDEX.md` every three minutes
and spawn a headless review or implementation agent when a bridge entry
needs attention. See `.claude/rules/file-bridge-protocol.md` and
`.claude/rules/bridge-essential.md` for the contract these scripts
implement.

## Source scripts (tracked in git)

| Script | Role |
|--------|------|
| `codex-file-bridge-scan.ps1` | Codex-side scanner. Looks for `NEW`/`REVISED` entries and spawns `codex exec` to review. |
| `claude-file-bridge-scan.ps1` | Prime-side scanner. Looks for `GO`/`NO-GO` entries and spawns headless `claude.exe` to implement or revise. |
| `bridge-scan-common.ps1` | Shared helper module: `Get-IndexEntryTopVersion`, `Test-SnapshotStillFresh`, `Invoke-GuardedLaunch`. Dot-sourced by both scanners and by the test file. Side-effect free at load. |
| `run-bridge-scan-noconsole.ps1` | Wrapper generator. Reads one scanner source and writes a no-console copy that hides the console window and uses `taskkill /T /F` on timeout. |
| `tests/test-spawn-revalidation.ps1` | Seven-case integration test for the `Invoke-GuardedLaunch` TOCTOU guard. |

## Generated wrappers (ignored)

The VBS launchers and scheduled tasks invoke the no-console wrappers,
not the sources:

| Generated | Source | Invoked by |
|-----------|--------|-----------|
| `codex-file-bridge-scan-noconsole.generated.ps1` | `codex-file-bridge-scan.ps1` | `run-file-bridge-scan-noconsole.vbs` |
| `claude-file-bridge-scan-noconsole.generated.ps1` | `claude-file-bridge-scan.ps1` | `run-claude-bridge-scan-noconsole.vbs` |

Both `*.generated.ps1` files are excluded from git via
`.gitignore` line 217 (`*.generated.ps1`). Treat them as ephemeral
build output. Never edit them directly; every scheduled-task spawn
calls `run-bridge-scan-noconsole.ps1` which regenerates the wrapper
in-place if the source has changed.

## Regenerating wrappers

The scheduled tasks regenerate on every run, but you can force a local
regeneration (for example after editing a source scanner) with:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass `
    -File independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 `
    -Scanner Codex -NoExec

powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass `
    -File independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 `
    -Scanner Claude -NoExec
```

`-NoExec` causes the source scanner to exit before launching the child
agent. If there are actionable entries, the source scanners exit with
code `2` under `-NoExec` (that is the convention used to distinguish
"attention entries present but no spawn" from "clear" (`0`) and error
(`1`)). When there are no actionable entries, exit is `0`.

After regeneration, confirm the guard propagated into both wrappers:

```powershell
Select-String `
    -Path independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1, `
          independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1 `
    -Pattern 'Test-SnapshotStillFresh|Invoke-GuardedLaunch'
```

Both files should produce matches for `Invoke-GuardedLaunch` at the
guarded-launch call site.

## Snapshot revalidation guard

Both scanners capture the selected entry's top `status:file` line as a
snapshot immediately after parsing `bridge/INDEX.md`, then call
`Invoke-GuardedLaunch` with a scriptblock that owns the full child-agent
lifecycle. The guard re-reads `INDEX.md` immediately before invoking the
scriptblock and aborts if any of:

- the document entry has been removed;
- the top status has changed (e.g., the other scanner appended a verdict); or
- the top file path has changed.

On a stale snapshot the guard appends a JSON record to
`logs/bridge-snapshot-stale.log`:

```json
{"event":"SNAPSHOT-STALE","document":"...","expected_status":"...","expected_file":"...","timestamp_utc":"..."}
```

The scanners log a `SNAPSHOT-STALE` line to their scan log, write a
`stale` state to their `*-scan-status.json`, and exit `0`. The next
3-minute poll re-reads `INDEX.md` and dispatches on whatever the current
top entry is.

## Test matrix

`tests/test-spawn-revalidation.ps1` runs seven deterministic cases
against per-test temp `INDEX.md` fixtures. No live bridge files are
read or mutated.

Run locally:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass `
    -File independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1
```

Exits `0` on all-pass, `1` on any failure. Prints one line per case.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
