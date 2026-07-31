NEW

# WI-5298 Codex Snapshot Git Window Containment - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5298-codex-snapshot-git-window-containment
Version: 003
Responds to GO: bridge/gtkb-wi5298-codex-snapshot-git-window-containment-002.md
Approved proposal: bridge/gtkb-wi5298-codex-snapshot-git-window-containment-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5298
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "scripts/ops/harness_storm_watchdog_launcher.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]
Recommended commit type: fix:

author_identity: Codex A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5.5
author_model_version: 5.5
author_model_configuration: Prime Builder

## Implementation Claim

Implemented a Windows-only, event-driven monitor that hides only a top-level
window-show event whose process provenance is exactly `conhost.exe` parented by
Codex Desktop's snapshot Git command and descended from `ChatGPT.exe`. The only
target-window action is `ShowWindowAsync(SW_HIDE)`. Process-inspection and
Windows-API ambiguity fail open and leave the window and process untouched.

The existing hidden storm-watchdog launcher now ensures the monitor through
`pythonw.exe`, canonical no-window flags, detached process flags, and a named
mutex. Monitor startup is fail-soft and cannot prevent the watchdog or a
harness from running. No process was killed, suspended, reprioritized, or
intercepted; no Git command, dispatcher, TAFE, bridge route, scheduled task,
harness role, or eligibility setting was changed. A, B, and C remained active
and dispatchable throughout the live proof.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

`DELIB-202666274` authorizes the modernization project while preserving the
bridge, implementation-start, independent verification, and mechanical gates.
The owner's 2026-07-15 correction requires the console defect to be fixed
without making any harness non-dispatchable. The implementation follows that
only acceptable resolution. No new owner decision is required for independent
verification; staging, commit, push, release, and deployment remain outside
this report.

## Prior Deliberations

- `DELIB-202666274` - project-level modernization implementation authority.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - background automation must not
  surface visible consoles.
- `DELIB-202666320` - WI-5113 covers no-window finalizer subprocesses, not this
  separate Codex Desktop snapshot path.
- Owner directive, 2026-07-15 - console visibility is never a harness
  dispatchability-withhold reason.
- `bridge/gtkb-wi5298-codex-snapshot-git-window-containment-001.md` - approved
  exact four-target proposal.
- `bridge/gtkb-wi5298-codex-snapshot-git-window-containment-002.md` - independent
  Loyal Opposition GO.

## Specification-Derived Verification Plan

| Specification | Executed evidence and result |
| --- | --- |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | A 120.037-second live observer sampled 2,709 times, saw 40 exact snapshot Git processes and 20 matching conhosts, found zero visible qualifying windows, and confirmed the two cutoff Git PIDs exited naturally. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The monitor is root-bound and Windows-only; 27 focused tests pass for exact/near-miss provenance, event filtering, hide-only behavior, launcher flags, and fail-soft startup. |
| `ADR-CROSS-HARNESS-PARITY-001` | Read-only `gt bridge status --json` after the live proof showed A, B, and C `active` with `can_receive_dispatch=true`; no eligibility mutation command was run. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Static source assertions reject process termination and dispatch-control APIs; live process telemetry proved snapshot execution continued while only window visibility changed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The implementation followed proposal `-001`, independent GO `-002`, and the governed WI-5298 claim/start packet for exactly four targets. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward all eleven linked specifications from the approved proposal. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The header records the Harness Parity PAUTH, project, WI-5298, and exact target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Every linked specification maps to executed evidence in this table; pytest, Ruff, formatting, diff, process, window, Git-index, singleton, and dispatch checks all passed. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | WI-5298, owner correction, proposal, GO, source, tests, this report, and the requested verdict form one traceable chain. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This `NEW` implementation report advances the implemented GO to independent verification without prematurely resolving or committing WI-5298. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The defect and nonimpairment invariant are preserved in WI-5298 and the numbered bridge chain rather than remaining transcript-only. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check` against all four targets.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check` against all four targets.
- `git diff --check --` against all four targets.
- Hidden launcher invocation through `ensure_snapshot_window_hider()` followed
  by a 120-second `psutil` plus Win32 `EnumWindows` observer.
- Read-only process-environment sampling of the exact outer/inner snapshot Git
  pair and five-second natural-exit follow-up.
- A second `ensure_snapshot_window_hider()` invocation with before/after
  process census.
- `gt bridge status --json` read-only topology check after the live proof.

## Observed Results

- Pytest: `27 passed`; one pre-existing unknown `asyncio_mode` warning.
- Ruff check: `All checks passed!`; Ruff format: all four files formatted.
- Diff check: exit 0; only the existing Windows LF/CRLF warning appeared.
- Live observer: 120.037 seconds, 2,709 samples, 40 exact Git processes, 20
  qualifying conhosts, zero visible qualifying conhost events.
- Every observed snapshot Git process had a `ChatGPT.exe` ancestor. The two
  snapshot PIDs alive exactly at the observation cutoff both exited naturally.
- The sampled outer/inner Git pair used
  `GIT_INDEX_FILE=C:\Users\micha\AppData\Local\Temp\codex-index-...\index`.
  A transient real-index lock from concurrent workspace activity appeared
  during sampling, but the exact snapshot processes used the temporary index;
  `.git/index.lock` was absent at both follow-up checks and no residue remained.
- The initial monitor launch produced one venv interpreter chain. Re-launch
  returned successfully and the persistent process count remained `2 -> 2`,
  demonstrating mutex-guarded singleton operation without process termination.
- After acceptance, A/Codex, B/Claude, and C/Antigravity were all `active` and
  `can_receive_dispatch=true`.

## Files Changed

- `scripts/ops/codex_snapshot_window_hider.py`
- `scripts/ops/harness_storm_watchdog_launcher.py`
- `platform_tests/scripts/test_codex_snapshot_window_hider.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`

## Acceptance Criteria Status

- PASS: the snapshot Git mechanism remained operational and exited naturally.
- PASS: no qualifying console was visible during the two-minute observation.
- PASS: exact argv, process ancestry, event shape, and near-miss rejection have
  focused regression coverage.
- PASS: monitor startup is hidden, detached, singleton, and fail-soft while the
  existing watchdog path remains operational.
- PASS: no target-process lifecycle action or Git interception exists.
- PASS: no harness was disabled or impaired; A, B, and C remained dispatchable.
- PASS: no dispatcher, TAFE, bridge-route, task, Git staging/commit/push,
  deployment, release, credential, or destructive-cleanup mutation occurred.

## Risk And Rollback

Residual risk is an unrelated console matching every provenance predicate. The
exact argv, immediate parent, `ChatGPT.exe` ancestry, top-level show-event
filter, and fail-open error handling constrain that risk. Rollback is the exact
four-path finalization reversal after VERIFIED; the monitor performs no durable
external-system or dispatcher mutation, and the current singleton process will
end with its hosting Windows session or an authorized maintenance action.

## Loyal Opposition Asks

1. Independently verify the exact four-path implementation and evidence.
2. Return VERIFIED only if snapshot completion, hide-only behavior, singleton
   operation, fail-soft launcher behavior, and unchanged dispatchability hold.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
