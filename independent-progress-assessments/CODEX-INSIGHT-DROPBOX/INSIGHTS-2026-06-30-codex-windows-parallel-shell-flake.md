# Codex Windows Parallel Shell Launch Flake

## Claim

The observed `CreateProcessWithLogonW failed: 1056` failure is most consistent
with a Codex Desktop / Windows process-launch race around concurrent shell
startup, not with a deterministic GT-KB hook or PowerShell command failure.

This run did not reproduce the failing condition. The practical GT-KB-side
response is to treat this as an upstream/runtime flake unless recurrence
evidence shows a project wrapper or hook participates before PowerShell starts.

## Evidence

- Bridge authorization: `bridge/gtkb-wi4248-codex-windows-parallel-shell-flake-002.md`
  issued GO for an additive investigation report only.
- Implementation-start packet:
  `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4248-codex-windows-parallel-shell-flake`
  passed at `2026-06-30T05:19:54Z` with the sole target path
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-codex-windows-parallel-shell-flake.md`.
- Local Windows service state during this run:
  `Get-CimInstance Win32_Service -Filter "Name='seclogon'"` returned
  `State=Running`, `StartMode=Manual`, `StartName=LocalSystem`, `Status=OK`.
- Local PowerShell host path during this run:
  `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe`,
  version `10.0.26100.8737`.
- A five-job PowerShell subprocess fan-out at `2026-06-30T05:18:50Z` completed
  successfully with five result objects and no process-launch failures.
- The original failure class, as captured in WI-4248 and the approved proposal,
  occurred before ordinary command execution: a child process could not be
  created and returned Windows error `1056`.

## Interpretation

Windows error `1056` maps to "an instance of the service is already running".
For `CreateProcessWithLogonW`, the relevant service dependency is commonly the
Secondary Logon service (`seclogon`). The current machine has that service
running, which explains why later parallel launches can succeed after an
initial collision or warm-up completes.

Because the failure occurs at process creation time, ordinary GT-KB PreToolUse
hooks, PowerShell parsing, repo-local scripts, and command bodies may never be
reached. That boundary makes a project-level code fix premature without a
captured recurrence that shows GT-KB code executing before the failure.

## Risk / Impact

- Automation runs that start with wide shell fan-out may intermittently lose
  several parallel reads even when the commands are harmless.
- Retrying individually after the first failure is likely to succeed once the
  service is running.
- A GT-KB source mitigation would be speculative unless recurrence evidence
  shows a project-owned launch wrapper, hook, or environment setup step is in
  the path before `CreateProcessWithLogonW` fails.

## Recommended Action

1. Keep Codex Windows startup and live-discovery probes conservative when the
   session is cold: prefer one initial shell command before broad
   `multi_tool_use.parallel` fan-out.
2. On recurrence, capture the exact failed command envelope, whether any
   PowerShell output was produced, `seclogon` state, and whether an immediate
   sequential retry succeeds.
3. Do not add a GT-KB retry/serialization wrapper yet. Reopen implementation
   only if recurrence evidence shows the failure is reproducible from a
   GT-KB-owned launch surface or hook.

## Owner Decision Needed

None for this report. If the failure recurs often enough to affect automation
reliability, the next decision is whether to prefer a GT-KB local warm-up probe
or to treat it as a Codex Desktop runtime issue for upstream reporting.
