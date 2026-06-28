NEW

# gtkb-wi4894-storm-watchdog-pythonw-output-repair - Restore pythonw-safe reaper output

bridge_kind: prime_proposal
Document: gtkb-wi4894-storm-watchdog-pythonw-output-repair
Version: 001
Author: Codex Prime Builder
Date: 2026-06-28 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop; formal-release dispatcher reliability

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4894-REAPER-OUTPUT
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4894

target_paths: ["scripts/ops/storm_watchdog_reap.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_storm_watchdog_reap.py", "platform_tests/scripts/test_harness_storm_watchdog.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the storm-watchdog reaper path so the scheduled no-console watchdog can still receive the decider JSON from `scripts/ops/storm_watchdog_reap.py`.

Current evidence shows the pure decider works when run with `python.exe` against the saved candidate file, but `scripts/ops/harness_storm_watchdog.ps1` invokes it through `pythonw.exe` and captures stdout into `$decisionRaw`. That contract is brittle: `pythonw.exe` is the GUI-subsystem interpreter and does not provide reliable captured stdout to PowerShell. The watchdog log repeatedly records `FAILSAFE ... reason=decider exit=1 output-empty=True` or `output-empty=True` with no exit code, so the fail-safe correctly reaps nothing even when candidates exist.

The release impact is direct: stale dispatched workers accumulate, dispatcher health moves to WARN, and formal release verification can stall behind live-but-nonproductive LO worker records. This proposal keeps the no-console behavior from WI-4896 but changes the decider transport from stdout capture to an explicit output file.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this protected script/test implementation to proceed through bridge GO and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the proposal to cite every governing specification and derive tests from them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the post-implementation report to map linked specifications to executed evidence.
- `GOV-STANDING-BACKLOG-001` - makes the MemBase work item `WI-4894` the current backlog authority for this defect.
- `ADR-DISPATCHER-ARCHITECTURE-001` - governs the dispatcher as a centralized, resilient automation substrate; the watchdog/reaper is part of that reliability envelope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires dispatch liveness and recovery behavior to be observable and reliable rather than silently leaving stale workers.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - constrains dispatched-worker process handling and envelope outcomes.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - preserves the verified rule that the watchdog must not use raw count or auto-assert a kill switch; the repair keeps fail-safe semantics and liveness-based reaping only.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - constrains the Windows background task/no-console surface that WI-4896 was repairing.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms the work stays inside the GT-KB project root and does not treat Agent Red or an external checkout as the release authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governs preservation of the WI, proposal, implementation report, verification, and release evidence as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governs reducing ambiguity by routing the defect repair through a durable work item and bridge chain instead of scratch notes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs when investigation findings and release blockers become formal bridge/work-item artifacts.

## Prior Deliberations

- `DELIB-20266104` - owner authorized the surgical storm-watchdog liveness-awareness slice; this repair preserves that design and fixes its current transport break.
- `DELIB-20266079` - WI-4780 verification that the watchdog must not auto-assert the global kill switch; this proposal keeps fail-safe/no-raw-count behavior.
- `DELIB-20266135` - owner directed the storm-watchdog watched-set repair for Cursor coverage; this proposal preserves the watched-set tests and does not narrow coverage.
- `DELIB-20266276` - owner scope-lock for the daemon-resilience program; the cited PAUTH includes storm-watchdog repair under dispatcher resilience.
- `DELIB-20266297` - WI-4896 console-window suppression; this proposal repairs the stdout side effect without reverting no-console launch behavior.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-004.md` - VERIFIED predecessor that introduced no-console behavior; this proposal is a follow-on correction, not a rollback.

## Owner Decisions / Input

No new owner decision is required. Implementation authority is supplied by `DELIB-20266276` and the active narrow authorization `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4894-REAPER-OUTPUT`, which includes `WI-4894`, source/test mutation, and the governing dispatcher/watchdog specifications. The owner also made the formal release the top priority on 2026-06-27, and this defect is now blocking reliable release verification.

## Requirement Sufficiency

Existing requirements sufficient - the governing requirements are the dispatcher-resilience PAUTH, `WI-4894`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`, and `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`.

## Proposed Implementation

1. Extend `scripts/ops/storm_watchdog_reap.py` with an optional `--output-file <path>` argument. When supplied, the CLI writes the exact decision JSON to that file and still exits with the same status semantics. Stdout may remain for normal CLI use when no output file is requested.
2. Update `scripts/ops/harness_storm_watchdog.ps1` to create a per-run decision JSON path under `.gtkb-state/ops`, remove any stale file before invocation, call `pythonw.exe ... --output-file <decision-file>`, and read the decision from the file after exit.
3. Preserve fail-safe behavior: if the decider exits nonzero, the output file is missing/empty, or JSON conversion fails, reap nothing and log the failure. Do not add any raw-count fallback.
4. Update focused tests so the regression suite proves the file-output contract, the watchdog no-console path, and the no-kill-switch rule together.

## Spec-Derived Verification Plan

| Spec / requirement | Verification |
| --- | --- |
| `WI-4894`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add a regression test that the decider can write a valid decision JSON via `--output-file`; run `python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short`. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, WI-4896 no-console constraint | Update `platform_tests/scripts/test_harness_storm_watchdog.py` so the PowerShell watchdog is expected to invoke `pythonw.exe` with `--output-file` and read the output file rather than capturing stdout. |
| `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` | Keep the existing watchdog tests that assert no global kill-switch auto-assertion and no raw-count fallback; run the focused watchdog tests. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Execute the decider against `.gtkb-state/ops/storm-watchdog-candidates.json` after implementation and confirm it exits 0 with parseable decision JSON through the file-output path. |
| Python quality gate | Run `ruff check` and `ruff format --check` on the changed Python test/source files. |

Expected commands:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py -q --tb=short
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\ops\storm_watchdog_reap.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\ops\storm_watchdog_reap.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe scripts\ops\storm_watchdog_reap.py --now <epoch> --project-root E:\GT-KB --provenance-dir .gtkb-state/ops/dispatch-provenance --processes-file .gtkb-state\ops\storm-watchdog-candidates.json --output-file .tmp\wi4894-reap-decision.json
```

## Risk / Rollback

Primary risk is making the watchdog too aggressive while repairing the transport. The proposal mitigates that by preserving the existing pure decider, keeping fail-safe behavior, and changing only how the JSON decision is returned to PowerShell. Rollback is a single revert of the eventual implementation commit; the rollback restores current fail-safe/no-reap behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4894-storm-watchdog-pythonw-output-repair`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - this repairs a broken release-critical watchdog/reaper behavior without adding a new user-facing capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
