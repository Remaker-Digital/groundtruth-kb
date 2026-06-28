NEW

# gtkb-wi4893-daemon-hook-storm-hardening - daemon and hook storm hardening

bridge_kind: prime_proposal
Document: gtkb-wi4893-daemon-hook-storm-hardening
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-28 UTC

author_identity: codex-prime-builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Prime Builder interactive session, formal release worktree

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/cross_harness_bridge_trigger.py", ".codex/hooks.json", ".claude/settings.json", ".codex/gtkb-hooks/bridge-dispatch-trigger.cmd", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source_and_configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal closes the dispatcher console-storm release blocker reproduced during the WI-4893 formal-release pass. The owner observed new Windows console windows opening every few seconds, sometimes two at once, then exiting too quickly to capture. Live process inspection confirmed multiple nested dispatcher daemon loops under `pythonw.exe`, duplicate OpenRouter dispatch worker chains, and foreground `python.exe E:\GT-KB\scripts\cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller` hook processes being launched repeatedly from the active Codex root.

The observed failure has two coupled causes. First, `scripts/gtkb_dispatcher_daemon.py` uses an age-based lock file and PID-only liveness checks, so concurrent starts and PID reuse can leave more than one live loop believing it owns the daemon. Second, `.codex/hooks.json` and `.claude/settings.json` register cross-harness dispatch hooks as foreground `python ...cross_harness_bridge_trigger.py` commands, which can flash visible Windows consoles and can continue to fan out trigger processes even after the daemon is stopped. Release readiness requires both halves to be fixed together: robust single-instance/provenance behavior for the daemon, and hidden/bounded hook launch behavior for the trigger.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this protected source/config change must enter through a Prime Builder proposal and Loyal Opposition GO before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the release-blocking defect to dispatcher and hook-governance requirements before edits begin.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds the work to WI-4893, the dispatcher reliability project, and the current PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include daemon single-instance/provenance tests, hook launch-surface tests or static assertions, and a live no-storm process check.
- `GOV-STANDING-BACKLOG-001` - WI-4893 is the MemBase work-item authority for release-blocking dispatcher readiness work.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher behavior must remain centralized, auditable, and bounded rather than devolving into duplicate ad hoc hook workers.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the daemon substrate must have one effective dispatcher owner and must not multiply active daemon loops.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - `gt bridge dispatch daemon start|stop|status` must reflect and control actual daemon state, including stale/PID-reused state.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - trigger/daemon launch envelopes must remain bounded by role, selected target, retry/backoff, and dispatch-run state.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook behavior on Windows is in scope because hook parity and hook fallback behavior are the visible failure surface.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - hook-surface changes must declare parity or a typed waiver for each affected harness.
- `ADR-CROSS-HARNESS-PARITY-001` - cross-harness hook behavior must stay aligned unless the owner explicitly approves a divergence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-visible release blocker is preserved as a bridge proposal instead of remaining transient console-storm context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposed fix turns observed operational drift into a reviewable, testable implementation slice.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the console-storm report crossed from ephemeral observation into release-blocking work and therefore requires durable artifact capture.

## Prior Deliberations

- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues are release blockers and must be diagnosed/resolved before release.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - prior empirical finding that Codex hooks fire on Windows; this proposal updates the Windows hook behavior from "fires" to "fires without visible console storm and without unbounded trigger fan-out."
- `DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION` - prior hook-health authorization establishes that hook overhead and hook failure modes are legitimate governance surfaces, not incidental UI noise.

## Owner Decisions / Input

No new owner decision is required for filing this proposal. The owner explicitly reported the Windows console storm during the active release-hardening session and previously directed that all dispatcher issues be diagnosed and resolved before release. Loyal Opposition should treat this as implementation-authorizable only if it agrees that the existing WI-4893 PAUTH covers hook launch configuration needed to make dispatcher readiness real; otherwise it should return NO-GO requesting a PAUTH amendment before implementation.

## Requirement Sufficiency

Existing requirements sufficient for proposal review. WI-4893, `DELIB-20260628-DISPATCHER-RELEASE-READINESS`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, and the Codex hook parity record define the expected behavior: one controlled daemon owner, no unbounded trigger/worker fan-out, accurate control-surface status, and no user-visible Windows console storm from routine dispatch hooks. If Loyal Opposition considers `.codex/hooks.json` or `.claude/settings.json` outside the existing PAUTH, the required next step is a PAUTH amendment rather than a new technical requirement.

## Cross-Harness Disposition

Codex/A: parity-required. The active failure is visible in Codex on Windows because `.codex/hooks.json` launches the bridge trigger as foreground `python`, and because routine tool/hook invocations can start multiple direct trigger processes. The implementation must update Codex hook registration or a Codex-specific wrapper so routine hook execution does not create visible consoles and does not bypass trigger quiesce/backoff.

Claude/B: parity-required. `.claude/settings.json` contains the same bridge-trigger command pattern, so the Claude hook surface must receive an equivalent hidden/bounded launch disposition or a tested no-op explanation if Claude's host runner already guarantees no visible Windows console. No typed waiver is requested.

Antigravity/C and Cursor/E: no direct hook-config mutation proposed. They remain covered by dispatcher recipient readiness and trigger selection rules, not by this hook-launch change, unless implementation evidence shows they consume the same hook registration files.

OpenRouter/F and Ollama/D: no harness-config mutation proposed. They are dispatch recipients only for this change and must be protected by bounded trigger/daemon selection, backoff, and worker-lifetime rules.

## Spec-Derived Verification Plan

The implementation must prove the following before reporting completion:

- `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` passes with new regression coverage for atomic/single-instance daemon lock behavior, PID create-time provenance in daemon liveness/status/start refusal, and stale/missing dispatch-run sidecars not causing loop respawn or incorrect running state.
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` passes with new regression coverage that hook-trigger invocations honor the existing `GTKB_NO_CROSS_HARNESS_TRIGGER` loop-prevention contract, respect quiesce/backoff, and do not create duplicate worker dispatches when another trigger is in flight.
- A static or unit-level hook-config assertion verifies `.codex/hooks.json` no longer launches the dispatcher trigger as foreground `python ...cross_harness_bridge_trigger.py` on Windows; the registered command must use a hidden/no-window launch path or a hook wrapper that selects `pythonw.exe` without losing audit logs.
- A matching static assertion verifies `.claude/settings.json` does not retain an equivalent Windows-foreground trigger path when the Claude hook runs on Windows.
- Live smoke after implementation: run a bounded sequence of `gt bridge dispatch daemon stop`, hook-trigger status/report commands, and process inspection; expected result is zero persistent duplicate daemon loops, zero duplicate auto-dispatch worker chains for the same selected entries, and no visible console storm during repeated benign tool/hook invocations.
- `python -m ruff check scripts/gtkb_dispatcher_daemon.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` passes.
- `python -m ruff format --check scripts/gtkb_dispatcher_daemon.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` passes.

## Risk / Rollback

Risk is moderate because this touches dispatcher process lifecycle and hook launch configuration, two surfaces that can either over-dispatch or prevent dispatch entirely. The implementation must fail closed: if hidden launch cannot be proven safe, dispatch hooks should produce a visible `WARN` in dispatcher health instead of silently spawning uncontrolled workers. Rollback is a single revert of the implementation commit and this append-only bridge chain; operationally, the daemon should remain stopped until the fix is verified.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4893-daemon-hook-storm-hardening`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
