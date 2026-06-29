NEW

# gtkb-wi4896-codex-desktop-antigravity-console-residual - Codex Desktop and Antigravity console residual containment

bridge_kind: prime_proposal
Document: gtkb-wi4896-codex-desktop-antigravity-console-residual
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29 UTC

author_identity: codex-prime-builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop; release-readiness incident response

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896

target_paths: [".codex/config.toml", ".codex/hooks.json", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: configuration, tests, and operational release gate
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal closes the remaining console-window release blocker after the earlier WI-4893/WI-4896 daemon and hook-storm hardening threads were marked terminal VERIFIED. Mike reported that Windows console windows still spawned in bursts after a hard Codex restart, including immediately after user input. Live process watches established three distinct launch classes:

1. GT-KB Codex hook commands from the previously loaded Codex hook table, including `.codex\gtkb-hooks\workstream-focus.cmd`, `.codex\gtkb-hooks\session_wrapup_trigger_dispatch.py`, `.claude\hooks\spec-classifier.py`, `.codex\gtkb-hooks\glossary-expansion.py`, and `.codex\gtkb-hooks\project-completion-surface.py`.
2. An Antigravity app-local `language_server.exe multicall schedule "0 * * * *" agentapi new-conversation ... GroundTruth-KB Loyal Opposition ...` child that respawned under the Antigravity parent even though dispatcher config already marks harness C retired and `can_receive_dispatch: false`.
3. Codex Desktop app-internal Windows child processes, especially `git.exe diff/status/hash-object` dirty-worktree snapshots and a direct `powershell.exe -NoProfile -NonInteractive ... Get-CimInstance Win32_Process ...` process probe. This third class matches the public OpenAI Codex Windows issue reporting visible PowerShell/conhost probes spawned directly by Codex Desktop.

Emergency containment was necessary because the console storm prevented stable owner input. The current local containment state is intentionally conservative: `.codex/hooks.json` is inert, project `.codex/config.toml` sets `features.hooks = false` and `features.shell_snapshot = false`, and the Antigravity process tree was terminated. This proposal asks Loyal Opposition to approve converting that emergency containment into a release-safe, test-backed residual fix, or to NO-GO it with a narrower acceptable path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected hook/config/test changes require bridge review, GO, implementation-start evidence, implementation report, and independent verification before release.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the residual to dispatcher, hook, parity, and release-readiness requirements before further edits.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, work item, and parseable `target_paths` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include a spec-derived process-watch test proving no GT-KB-controlled hook/scheduler launcher remains active.
- `GOV-STANDING-BACKLOG-001` - WI-4896 is the work-item authority for recurring Windows console suppression.
- `ADR-DISPATCHER-ARCHITECTURE-001` - release automation must not depend on uncontrolled duplicate or app-local background loops.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher readiness requires one bounded control surface rather than invisible app-local scheduler state.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher config/status must be the authority for dispatch eligibility; Antigravity C is not eligible and must not be relied on for release LO work.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch-run and harness envelopes must be bounded, inspectable, and free of stale app-local scheduler behavior.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook behavior on Windows is in scope, including fallback when desktop hooks cannot run without visible child consoles.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - disabling or re-enabling Codex hooks must be treated as a typed parity disposition rather than silent drift from Claude/Cursor behavior.
- `ADR-CROSS-HARNESS-PARITY-001` - cross-harness hook/dispatch behavior must remain aligned or carry an explicit waiver.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the release-blocking incident is preserved as a bridge proposal instead of remaining transient chat/process context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair must be artifact-driven: proposal, review, implementation report, verification, and scoped release evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated owner-visible console/focus-steal crossed the threshold for durable release-blocking artifact capture.

## Prior Deliberations

- `DELIB-20266297` - WI-4896 console-window suppression authorization and owner directive to stop recurring Windows console/dialog popups from dispatcher/background automation.
- `DELIB-20266276` - daemon-resilience program scope-lock; relevant because scheduled daemon/watchdog recovery and app-local background launchers were part of the observed window storm.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues are release blockers and all dispatcher issues must be diagnosed and resolved before release.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-004.md` - prior terminal VERIFIED console-window suppression thread; current evidence shows residual behavior remained.
- `bridge/gtkb-wi4896-daemon-loop-console-residual-004.md` - prior terminal VERIFIED daemon-loop residual; current evidence shows non-daemon app-local and Codex Desktop residuals remained.
- `bridge/gtkb-wi4896-startup-console-residual-006.md` - prior terminal VERIFIED startup-console residual; current evidence shows post-restart and post-input residuals remained.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-004.md` - prior terminal VERIFIED daemon/hook-storm hardening; current evidence shows the terminal state did not cover Codex Desktop internal probes or Antigravity app-local scheduler respawn.

## Owner Decisions / Input

No new owner decision is required to file this proposal. Mike reported the continuing console storm, authorized doing whatever was needed to diagnose/correct it, and made release readiness the top priority. The proposal remains inside WI-4896 console-window suppression and does not authorize production deployment, credential lifecycle action, history rewrite, retired-poller restoration, or direct dispatcher-config file edits.

## Requirement Sufficiency

Existing requirements are sufficient. The required release behavior is simple: no GT-KB-controlled automation may spawn visible Windows console windows, no retired/non-dispatchable harness may be relied upon for dispatched LO work, and the release gate must distinguish project-controlled launchers from upstream Codex Desktop app behavior. A new requirement would be needed only if the owner wants GT-KB to depend on Codex Desktop lifecycle hooks on Windows despite evidence that the desktop app itself can spawn visible PowerShell/conhost children.

## Cross-Harness Disposition

Codex/A: scoped divergence requested during incident containment. Codex Desktop lifecycle hooks on Windows are disabled because the active incident shows visible console-capable child processes after user input/tool activity. The final release path must either keep Codex hooks disabled with an explicit parity waiver or re-enable them only after a Windows no-storm process watcher proves the documented Windows launch disposition does not create visible console windows.

Claude/B: no direct mutation in this proposal. Claude remains suspended/unavailable in current dispatcher state. If Claude hook settings are later changed for parity, that must happen in a separate target list and verification pass.

Antigravity/C: no direct repo mutation in this proposal. Dispatcher config already marks C retired and `can_receive_dispatch: false`; the observed app-local scheduler is non-canonical external state and must be absent before release. C is not a release-ready dispatched LO target.

Cursor/E: no direct mutation in this proposal. Cursor remains an active dispatch-capable harness in dispatcher config but currently has a separate `cursor_headless_cli_unavailable` health failure that must be resolved before it is relied upon for release LO/PB dispatch.

Ollama/D and OpenRouter/F: no hook-surface mutation in this proposal. They remain dispatch recipients subject to their own health gates; OpenRouter F currently has a separate timeout health failure and must not be treated as healthy until that is resolved.

## Proposed Implementation

1. Preserve an incident breaker in project Codex config while the release gate is red:
   - `.codex/config.toml` keeps the existing `approval_policy = "on-request"` and `[sandbox_workspace_write] network_access = false`.
   - `.codex/config.toml` sets `[features] hooks = false` until Codex Desktop hook execution is revalidated on Windows.
   - `.codex/config.toml` sets `[features] shell_snapshot = false` to suppress the Codex Desktop process-probe feature where supported.
2. Keep `.codex/hooks.json` inert during containment. Re-enable it only through a follow-up GO if all hook entries use a documented Windows-specific launch disposition and the live process watcher proves no visible console-capable hook wrappers are created.
3. Update the Codex hook regression test to accept exactly one of two release-safe states:
   - breaker mode: project hooks disabled and `.codex/hooks.json` empty; or
   - enabled mode: every hook entry has a Windows-specific command path and the test rejects foreground `python`, `cmd /d /s /c`, `powershell.exe`, and `pwsh.exe` launchers.
4. Add or update dispatcher readiness test evidence so Antigravity C remains excluded from dispatch (`status: retired`, `can_receive_dispatch: false`) and any app-local `language_server.exe multicall schedule ... GroundTruth-KB` process is treated as an external residual that must be absent before release verification.
5. Add the release-gate process watch to the implementation report evidence:
   - no `.codex\gtkb-hooks` or `.claude\hooks` hook command children;
   - no `cross_harness_bridge_trigger.py`, `gtkb_dispatcher_daemon.py`, or `harness_storm_watchdog` children spawned by disabled hooks;
   - no Antigravity `multicall schedule` GroundTruth-KB LO child;
   - any remaining direct `Codex.exe` child `git.exe` or `powershell.exe ... Get-CimInstance` probes are explicitly classified as Codex Desktop upstream behavior and not claimed fixed by GT-KB.

## Spec-Derived Verification Plan

The implementation report must include exact command evidence for:

1. Static breaker validation:
   - `.codex/config.toml` contains `[features] hooks = false` and `shell_snapshot = false` while preserving `approval_policy = "on-request"` and `[sandbox_workspace_write] network_access = false`.
   - `.codex/hooks.json` is exactly inert or, if re-enabled, every hook has a Windows-safe disposition and no foreground launcher tokens.
2. Focused tests:
   - `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`
   - `python -m ruff check .codex/skills/bridge-propose/helpers/write_bridge.py scripts/gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
   - `python -m ruff format --check scripts/gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
3. Dispatcher-control evidence:
   - `gt bridge dispatch config --json` shows harness C not eligible to receive dispatch.
   - `gt bridge dispatch status --json` does not select harness C for LO work.
4. Live no-storm evidence:
   - A watcher spanning at least one prior storm interval after Codex reload and owner input records zero GT-KB hook/scheduler command children and zero Antigravity GroundTruth-KB `multicall schedule` children.
   - The watcher may separately record Codex Desktop internal Git or process probes; those must be classified as upstream Codex Desktop behavior and must not be represented as fixed by GT-KB.

## Acceptance Criteria

- GT-KB-controlled Codex hooks do not run while the Windows desktop console behavior remains unverified.
- Antigravity C remains non-dispatchable and is not used as a release LO target.
- Cursor E, Ollama D, and OpenRouter F remain the only non-Codex release-readiness dispatch candidates subject to their own health gates.
- Release verification includes a no-storm process-watch artifact, not only static file inspection.
- The implementation report explicitly states whether any remaining visible windows are Codex Desktop upstream behavior, project-controlled behavior, or absent.

## Risk / Rollback

The main risk is governance coverage loss while Codex hooks are disabled. The rollback is to restore the saved full hook configuration only after a Windows no-window validation passes. Until then, Prime Builder self-enforcement and non-Codex dispatcher/release gates remain mandatory. This is safer than leaving hooks enabled when the owner cannot reliably type because visible console windows steal focus.

## Bridge Filing

This proposal will be filed as `bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-001.md`, the first numbered bridge file for this residual thread. No prior numbered bridge files are deleted or rewritten; the versioned bridge file chain remains append-only.
