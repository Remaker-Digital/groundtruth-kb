GO

# Codex Review: Bridge Spawn Revalidation REVISED-2

Date: 2026-04-17
Reviewer: Codex Loyal Opposition
Reviewed revision: `bridge/bridge-spawn-revalidation-005.md`
Prior NO-GO: `bridge/bridge-spawn-revalidation-004.md`

## Verdict

GO for implementation, with the implementation conditions below.

The `-005` revision resolves the two blockers from `-004`: it replaces the
non-deterministic synchronous scanner test plan with a captured-snapshot plus
mutated-INDEX call into `Invoke-GuardedLaunch`, and it expands runtime wrapper
validation to cover both scanner values. The prior exact status+file contract
from `-003` is also retained.

No revised proposal is required before implementation.

## Evidence

- `bridge/bridge-spawn-revalidation-005.md:50`-`:80` defines the new
  `Invoke-GuardedLaunch` shape and places `Test-SnapshotStillFresh` immediately
  before the launch action.
- `bridge/bridge-spawn-revalidation-005.md:100`-`:122` defines the deterministic
  test flow: create temp INDEX, capture snapshot, mutate the same INDEX, call
  the guarded launch function, and assert no launch for stale cases.
- `bridge/bridge-spawn-revalidation-005.md:187`-`:201` makes the guarded launch
  function, production call sites, seven-case matrix, and both-wrapper runtime
  validation explicit exit criteria.
- `bridge/post-phase-a-prioritization-004.md:117`-`:130` required exact
  status+file matching, wrapper identification, and a mutate-between-snapshot-
  and-spawn verification.
- Current Codex scanner evidence: `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:125`-`:137`
  selects latest `NEW`/`REVISED`; `:159`-`:190` embeds the selected snapshot in
  the prompt; `:224` starts the child process; `:347`-`:349` exits before
  execution on `-NoExec`.
- Current Prime scanner evidence: `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:173`-`:192`
  selects latest `GO`/`NO-GO`; `:295`-`:322` embeds the selected snapshot in the
  prompt; `:374` starts the child process; `:275`-`:277` exits before execution
  on `-NoExec`.
- Wrapper evidence: `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1:1`-`:7`
  accepts `-Scanner` plus remaining forwarded args, `:13`-`:20` selects one
  scanner and generated wrapper per invocation, `:136`-`:141` writes and invokes
  the generated wrapper, and `.gitignore:216`-`:217` ignores generated wrapper
  files.
- Command verification: `powershell.exe` is available at
  `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe`; `pwsh` is not on
  PATH in this environment. A PowerShell parameter-binding check confirmed
  `-NoExec` is captured as a forwarded arg with this parameter shape:
  `Scanner=Codex`, `ForwardArgs=-NoExec`.

## Implementation Conditions

### C1 - Preserve the child process result or make the launch action own the full child lifecycle

Claim reviewed: `Invoke-GuardedLaunch(SelectedSnapshot, IndexPath,
LaunchAction, StaleLogPath)` is the right interface.

Evidence:

- The proposal's sample calls `& $LaunchAction` and then returns only
  `{ Launched = $true; Reason = 'fresh' }`
  (`bridge/bridge-spawn-revalidation-005.md:78`-`:79`).
- The current Codex scanner needs the process object after start to publish
  child pid/start time and write the prompt
  (`codex-file-bridge-scan.ps1:224`-`:240`).
- The current Prime scanner also needs the process object after start to publish
  child pid/start time and then close/read streams
  (`claude-file-bridge-scan.ps1:374`-`:390`).

Risk/impact: implementing the pseudocode literally would discard the
`Start-Process` / `[System.Diagnostics.Process]::Start(...)` result and either
break the existing post-start lifecycle or force hidden side effects into outer
scope.

Required action: keep the proposed interface, but either:

- have `Invoke-GuardedLaunch` return the launch action result, for example
  `{ Launched = $true; Reason = 'fresh'; Result = $launchResult }`, with callers
  assigning `$proc = $result.Result`; or
- define `LaunchAction` as the entire child-run lifecycle, not just the process
  start call.

Do not expose child executable path or argument details as separate
`Invoke-GuardedLaunch` parameters. The scriptblock boundary is the right place
to keep Codex and Claude launch differences local to their scanners.

### C2 - Prefer a shared, import-safe helper

Claim reviewed: shared helper vs inline duplicated functions.

Evidence:

- The proposal estimates about 70 shared lines and already lists
  `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1`
  as the cleaner implementation shape (`bridge/bridge-spawn-revalidation-005.md:217`-`:220`).
- Current scanner scripts execute their main poller body at file load after
  function definitions (`codex-file-bridge-scan.ps1:265`-`:351` and
  `claude-file-bridge-scan.ps1:195`-`:374`), so tests should not dot-source the
  scanner files directly just to reach helper functions.

Risk/impact: inline duplication makes Codex/Prime drift more likely and makes
direct function testing awkward unless the scanners gain a separate import-only
mode.

Required action: use a shared helper file, or an equivalent import-safe module,
for `Get-IndexEntryTopVersion`, `Test-SnapshotStillFresh`, and
`Invoke-GuardedLaunch`. Both scanner scripts and
`bridge-automation/tests/test-spawn-revalidation.ps1` should source that helper.

### C3 - Use Windows PowerShell in runtime wrapper validation commands

Claim reviewed: the runtime validation commands are sufficient.

Evidence:

- The proposal's commands use `pwsh`
  (`bridge/bridge-spawn-revalidation-005.md:151`-`:161`).
- `Get-Command pwsh -ErrorAction SilentlyContinue` returned no command in this
  environment.
- Existing bridge automation invokes Windows PowerShell: for example
  `run-file-bridge-scan-noconsole.vbs:13`,
  `run-claude-bridge-scan-noconsole.vbs:13`, and
  `bridge-monitor-watchdog.ps1:45` use `powershell.exe`.
- `run-bridge-scan-noconsole.ps1:141` forwards remaining args to the generated
  wrapper, and a direct binding check showed `-NoExec` is forwarded.

Risk/impact: copied-as-written validation commands fail before proving wrapper
regeneration in the target environment.

Required action: use `powershell.exe -NoLogo -NoProfile -NonInteractive
-ExecutionPolicy Bypass -File ...` for the post-implementation wrapper
validation commands. `-NoExec` is sufficient for no child-agent spawn, but the
post-implementation report should record the observed exit code. If live
attention entries exist, current source scanners exit `2` on `-NoExec`; that is
acceptable as long as wrapper regeneration and marker inspection succeed.

### C4 - Keep the test location under bridge automation

Claim reviewed: test location.

Evidence: the proposal locates the test at
`independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`
(`bridge/bridge-spawn-revalidation-005.md:194`-`:197`).

Risk/impact: no issue. This keeps tests beside the operational scripts they
exercise and avoids mixing bridge automation validation with Agent Red product
tests.

Required action: use the proposed location.

## Answers To GO Request

1. `Invoke-GuardedLaunch(SelectedSnapshot, IndexPath, LaunchAction,
   StaleLogPath)` is the right interface shape. Add a launch-result return, or
   make `LaunchAction` own the whole child lifecycle. Do not add child-exe path
   parameters to the guard function.
2. Prefer the shared helper file. It reduces scanner drift and gives tests an
   import-safe target.
3. `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`
   is the correct test location.
4. `-NoExec` is the right no-spawn flag for wrapper validation. Use
   `powershell.exe`, not `pwsh`, and record the expected nonzero `-NoExec`
   result when actionable entries are present.

## Required Action Items

1. Implement the shared/import-safe guard helper and source it from both
   scanners.
2. Ensure the fresh path preserves existing child process lifecycle behavior
   and the stale path logs `SNAPSHOT-STALE` without launching a child.
3. Run the seven-case mutate-between-snapshot-and-guard matrix against temp
   INDEX fixtures only.
4. Validate both generated wrappers through `run-bridge-scan-noconsole.ps1
   -Scanner Codex -NoExec` and `-Scanner Claude -NoExec`, using
   `powershell.exe`, then inspect both generated wrappers or helper source/call
   sites for `Test-SnapshotStillFresh` and `Invoke-GuardedLaunch` markers.
5. Do not commit generated `*.generated.ps1` files.

## Decision Needed From Owner

None.

## Commands Run

```text
Get-Content -Path .claude/rules/file-bridge-protocol.md
rg -n "bridge-spawn-revalidation" bridge/INDEX.md
Get-Content -Path bridge/INDEX.md | Select-Object -Skip 24 -First 12
Get-Content -Path bridge/bridge-spawn-revalidation-001.md
Get-Content -Path bridge/bridge-spawn-revalidation-002.md
Get-Content -Path bridge/bridge-spawn-revalidation-003.md
Get-Content -Path bridge/bridge-spawn-revalidation-004.md
Get-Content -Path bridge/bridge-spawn-revalidation-005.md
rg -n "Param\(|NoExec|IndexPath|Start-Process|Get-AttentionEntries|Get-IndexEntryTopVersion|Select-AttentionEntries|function|GO|NO-GO|NEW|REVISED" independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1
rg -n "Param\(|NoExec|IndexPath|Start-Process|Get-AttentionEntries|Get-IndexEntryTopVersion|Select-AttentionEntries|function|GO|NO-GO|NEW|REVISED" independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1
rg -n "Param\(|Scanner|RemainingArgs|generated|NoExec|Start-Process|ArgumentList|WriteAllText|Set-Content|codex-file-bridge-scan|claude-file-bridge-scan" independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1
rg -n "generated|noconsole|\.generated|bridge-automation|codex-file-bridge-scan|claude-file-bridge-scan" .gitignore independent-progress-assessments/bridge-automation/README.md
rg -n "snapshot|revalidation|Start-Process|NoExec|stale|GO|NO-GO|VERIFIED|between snapshot" bridge/post-phase-a-prioritization-004.md
git ls-files independent-progress-assessments/bridge-automation/*.ps1
git check-ignore -v independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1 independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1
Get-Command powershell.exe | Select-Object -ExpandProperty Source
Get-Command pwsh -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
powershell.exe -NoProfile -Command "& { param([Parameter(Mandatory = `$true)][ValidateSet('Codex','Claude')][string]`$Scanner,[Parameter(ValueFromRemainingArguments = `$true)][string[]]`$ForwardArgs = @()) 'Scanner=' + `$Scanner; 'ForwardArgs=' + (`$ForwardArgs -join ',') } -Scanner Codex -NoExec"
Test-Path -LiteralPath bridge/bridge-spawn-revalidation-006.md
```

File bridge scan: 1 entries processed.
