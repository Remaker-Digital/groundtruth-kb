NEW

# gtkb-wi4894-develop-release-integration-drift-repair - Apply verified watchdog output-file repair to develop

bridge_kind: prime_proposal
Document: gtkb-wi4894-develop-release-integration-drift-repair
Version: 001
Author: Codex Prime Builder
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never

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

Repair release-integration drift for the WI-4894 storm-watchdog output-file fix. The already VERIFIED bridge chain `gtkb-wi4894-storm-watchdog-pythonw-output-repair` claims the watchdog decider was changed from captured stdout to an explicit `--output-file` transport, and the formal release worktree at `.tmp/formal-release-main-20260627` contains that verified delta. The active `develop` branch does not: `scripts/ops/harness_storm_watchdog.ps1` still invokes `pythonw.exe` through captured stdout, and focused test files lack the output-file assertions.

The live runtime impact is release-blocking. `GTKB-HarnessStormWatchdog` is enabled and points at the tracked hidden `pythonw.exe` launcher, but the watchdog still logs `FAILSAFE ... reason=decider exit= output-empty=True`; dispatcher status then accumulates stale `in_flight` workers and rate-limits or caps LO dispatch. This proposal authorizes transplanting the exact verified WI-4894 four-file delta from the release worktree into `develop` and validating it there.

This is not a new design. It is a narrow release-integration repair that aligns `develop` with the VERIFIED WI-4894 implementation evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires protected script/test implementation to proceed through bridge GO and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the proposal to cite every governing specification and derive tests from them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the post-implementation report to map linked specifications to executed evidence.
- `GOV-STANDING-BACKLOG-001` - makes `WI-4894` the backlog authority for this release-blocking watchdog defect.
- `ADR-DISPATCHER-ARCHITECTURE-001` - governs dispatcher daemon and watchdog reliability as part of the release readiness envelope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires dispatch liveness and recovery behavior to be observable and reliable rather than leaving stale live workers.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - constrains dispatched-worker process handling and envelope outcomes.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - requires the watchdog repair to preserve no raw-count fallback and no automatic kill-switch assertion.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - requires Windows dispatcher/background paths to run without visible console windows; the output-file transport preserves `pythonw.exe`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the work inside the GT-KB project root and treats `.tmp/formal-release-main-20260627` only as in-root release-integration evidence, not an external authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves this release-integration drift as a durable bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - routes the drift correction through a scoped proposal, tests, implementation report, and LO verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires release-blocking drift findings to be promoted into formal artifacts rather than left as scratch notes.

## Prior Deliberations

- `DELIB-20266104` - owner authorized the surgical storm-watchdog liveness-awareness slice.
- `DELIB-20266079` - WI-4780 verification that the watchdog must not auto-assert the global kill switch.
- `DELIB-20266135` - owner directed storm-watchdog watched-set repair for Cursor coverage.
- `DELIB-20266276` - owner scope-lock for daemon/dispatcher resilience, carried by the active WI-4894 PAUTH.
- `DELIB-20266297` - WI-4896 no-console direction; this repair preserves it by avoiding stdout capture from `pythonw.exe`.
- `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-001.md` - original approved WI-4894 proposal.
- `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-002.md` - LO GO verdict.
- `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-003.md` - implementation report claiming the verified four-file delta.
- `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-004.md` - LO VERIFIED verdict for that implementation report.

## Owner Decisions / Input

No new owner decision is required. Mike made formal release readiness and dispatcher health the active top priority, and `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4894-REAPER-OUTPUT` already covers the narrow source/test mutation class for `WI-4894`. This proposal exists because the implementation gate correctly refuses to reuse a terminal VERIFIED bridge thread as a live edit license.

## Requirement Sufficiency

Existing requirements are sufficient. The implementation must only align `develop` with the already verified WI-4894 output-file transport and must not expand into new dispatcher topology, credential lifecycle, provider configuration, release deployment, or unrelated watchdog policy.

## Proposed Implementation

1. Apply the exact verified release-worktree delta from `.tmp/formal-release-main-20260627` to the four target paths in `develop`.
2. Add/restore `scripts/ops/storm_watchdog_reap.py --output-file`, writing the same decision schema to the requested file while preserving stdout behavior when the flag is omitted.
3. Update `scripts/ops/harness_storm_watchdog.ps1` to invoke the decider with `Start-Process -Wait -PassThru -WindowStyle Hidden`, pass `--output-file`, read the decision file, and delete the temporary decision file.
4. Restore focused tests proving output-file transport, no stdout dependency from `pythonw.exe`, and preservation of no raw-count/no auto-kill-switch semantics.
5. After tests pass, restart or run `GTKB-HarnessStormWatchdog` only as needed to verify a fresh heartbeat and absence of FAILSAFE output-empty logs.

Out of scope:

- Dispatcher target eligibility, provider keys, model/provider retry policy, GitHub settings, production deployment, and unrelated dirty worktree cleanup.
- Manual deletion of bridge history or rewriting existing VERIFIED bridge files.
- Treating `.tmp/formal-release-main-20260627` as canonical beyond verifying the exact delta already described by the terminal WI-4894 bridge chain.

## Spec-Derived Verification Plan

| Spec / requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run `implementation_authorization.py begin` and `validate` after GO; target validation must authorize exactly the four target paths. |
| `WI-4894`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run `python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py platform_tests/scripts/test_harness_storm_watchdog.py -q --tb=short`; output-file transport tests must pass. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Static test must assert the PowerShell watchdog invokes `pythonw.exe` through `Start-Process -Wait -PassThru -WindowStyle Hidden` with `--output-file` and no captured stdout path. |
| `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` | Existing watchdog tests must continue to prove no global kill-switch auto-assertion and no raw-count fallback. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Run the decider through the file-output path against `.gtkb-state/ops/storm-watchdog-candidates.json`; verify exit 0 and parseable `protect`, `reap`, `reasons` JSON. |
| Python quality gate | Run Ruff check and format check on the changed Python source/test files. |
| Live dispatcher release-health evidence | Run or wait for `GTKB-HarnessStormWatchdog`; verify `.gtkb-state/ops/storm-watchdog-heartbeat.txt` advances and recent `.gtkb-state/ops/storm-watchdog.log` no longer records `output-empty=True` for the decider transport. |

Expected commands:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB begin --bridge-id gtkb-wi4894-develop-release-integration-drift-repair --session-id 019f09c9-2db0-7b00-a337-40f998b07e56
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB validate --target scripts/ops/storm_watchdog_reap.py --target scripts/ops/harness_storm_watchdog.ps1 --target platform_tests/scripts/test_storm_watchdog_reap.py --target platform_tests/scripts/test_harness_storm_watchdog.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py -q --tb=short
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\ops\storm_watchdog_reap.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\ops\storm_watchdog_reap.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe scripts\ops\storm_watchdog_reap.py --now <epoch> --project-root E:\GT-KB --provenance-dir .gtkb-state/ops/dispatch-provenance --processes-file .gtkb-state\ops\storm-watchdog-candidates.json --output-file .tmp\wi4894-reap-decision.json
```

## Acceptance Criteria

- [ ] The active `develop` branch carries the same four-file WI-4894 output-file transport delta that is present in `.tmp/formal-release-main-20260627`.
- [ ] The watchdog decider supports `--output-file` and preserves stdout behavior when omitted.
- [ ] The PowerShell watchdog no longer captures stdout from `pythonw.exe`.
- [ ] Focused watchdog pytest, Ruff check, and Ruff format check pass.
- [ ] Live watchdog heartbeat advances and recent logs no longer show the `output-empty=True` FAILSAFE caused by pythonw stdout capture.
- [ ] No unrelated protected files, dispatcher topology, provider configuration, credentials, or release deployment settings are changed.

## Risk / Rollback

Primary risk is accidentally expanding the repair beyond the verified WI-4894 delta. Mitigation is to transplant only the four-file diff already visible between `develop` and `.tmp/formal-release-main-20260627`, then verify with the same focused commands. Rollback is a single revert of those four target files; it restores the current fail-safe/no-reap behavior but reintroduces the release blocker.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4894-develop-release-integration-drift-repair`; no prior bridge file is deleted or rewritten. Dispatcher/TAFE state plus numbered bridge files remain the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Pre-Filing Preflight

Applicability preflight:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state\propose-drafts\gtkb-wi4894-develop-release-integration-drift-repair-001.md --json
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
packet_hash: sha256:7e4b639d1f5366d82f552bc7425eaa8256350bed3bc837ba5639437fd50b6a80
warnings.missing_parent_dirs: []
```

Clause preflight:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\propose-drafts\gtkb-wi4894-develop-release-integration-drift-repair-001.md
exit: 0
must_apply: 4
evidence gaps in must_apply clauses: 0
blocking gaps: 0
```

## Recommended Commit Type

fix - this repairs release-integration drift in a verified dispatcher watchdog fix without adding a new user-facing capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
