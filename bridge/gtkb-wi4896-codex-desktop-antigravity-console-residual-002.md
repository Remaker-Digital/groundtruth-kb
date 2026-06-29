REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-prime-builder-A-20260629-release-hardening-d89c8fbd-0516-4d49-8192-4935838448b1
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex desktop interactive session; Prime Builder role; dispatcher release hardening

# gtkb-wi4896-codex-desktop-antigravity-console-residual - Codex Desktop residual containment plus Python spawn audit

bridge_kind: prime_proposal
Document: gtkb-wi4896-codex-desktop-antigravity-console-residual
Version: 002
Author: Prime Builder (Codex harness A)
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896

target_paths: [".codex/config.toml", ".codex/hooks.json", "scripts/windows_no_window_spawn_audit.py", "platform_tests/scripts/test_windows_no_window_spawn_audit.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "scripts/cross_harness_bridge_trigger.py", "scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge/launcher.py", "groundtruth-kb/src/groundtruth_kb/bridge/poller.py", "groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py", ".codex/gtkb-hooks/", ".claude/hooks/"]

implementation_scope: Windows no-window breaker, static subprocess audit, release-runtime launcher fixes, and no-storm verification
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This revision supersedes the narrower `-001` residual containment proposal by adding Mike's stronger requirement: use a programmatic scan to find Python subprocess launch sites that could allocate visible Windows consoles, then fix or explicitly classify all release-runtime GT-KB-owned findings. The prior proposal covered the emergency Codex hook breaker, Antigravity app-local scheduler containment, and a live no-storm watcher. That remains necessary but insufficient because the first AST scan found hundreds of potential spawn surfaces, including production hook, dispatcher, bridge, and CLI launch sites.

The revised release standard is: no GT-KB-controlled background or dispatcher release-runtime Python launch may create a visible Windows console. Every such launch must use a hidden/no-window subprocess helper or an equivalent explicit Windows disposition. Interactive/foreground tools may remain foreground only when the scanner records an intentional allowlist entry with a reason.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source, hook, config, and test mutations require bridge GO, implementation-start evidence, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised implementation proposal cites governing requirements before mutation.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch automation must use bounded, inspectable launch surfaces.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher readiness must reflect actual launch health, not stale or hidden app-local behavior.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatched workers and harness envelopes must be bounded and observable.
- `ADR-DISPATCHER-ARCHITECTURE-001` - release automation must not depend on uncontrolled duplicate loops or foreground background launchers.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows desktop dispatcher tasks must be no-window where they are background tasks.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex Windows hook behavior may carry an explicit breaker or fallback when safe parity is not possible.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-surface divergence must be explicit, reviewed, and reversible.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - hook and dispatcher divergence must be explicit, tested, and reversible.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires evidence that automation does not steal focus or block owner operation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the no-window requirement.

## Prior Deliberations

- `bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-001.md` - initial residual containment proposal.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-004.md` - prior terminal VERIFIED thread; current owner reports show residual behavior remained.
- `bridge/gtkb-wi4896-daemon-loop-console-residual-004.md` - prior terminal VERIFIED daemon-loop residual.
- `bridge/gtkb-wi4896-startup-console-residual-006.md` - prior terminal VERIFIED startup-console residual.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-004.md` - prior terminal VERIFIED daemon/hook-storm hardening; current evidence requires broader launch-surface audit.
- `DELIB-20266297` - WI-4896 console-window suppression authorization.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues are release blockers.
- Owner directive on 2026-06-29 - there is no case where GT-KB should spawn a new visible console window; scan all Python code for unsuppressed spawns rather than investigating each burst manually.

## Owner Decisions / Input

No new owner decision is required. Mike already authorized doing whatever is needed to correct the console-window showstopper, and specifically asked for a programmatic scan/fix approach. This revision remains bounded to WI-4896 no-window release readiness and does not authorize production deployment, credential lifecycle action, history rewrite, retired-poller restoration, or dispatcher routing-policy changes.

## Requirement Sufficiency

Existing requirements are sufficient. The new implementation mechanism is a deterministic audit plus fixes for release-runtime surfaces; it implements the existing no-window release requirement rather than adding a new policy.

## Cross-Harness Disposition

Codex/A: scoped divergence remains approved only as incident containment. Project Codex hooks stay disabled and `.codex/hooks.json` stays inert until enabled-mode no-window validation passes. This is a typed parity waiver for Windows Codex Desktop, not a silent permanent retirement of Codex governance hooks.

Claude/B: Claude hook surfaces may be scanned and corrected for no-window helper use where the same Python hook code is shared, but no Claude settings activation change is proposed here. Any behavior change to Claude hook registration remains out of scope unless the scanner finds a shared release-runtime violation in targeted hook code.

Cursor/E: Cursor remains a separate dispatcher-readiness issue under `gtkb-wi4888-cursor-agent-cli-subcommand-no-window-001.md`. This WI-4896 revision may classify Cursor-related Python subprocess launch surfaces for no-window behavior, but it does not authorize a role flip or Cursor launcher correction.

Antigravity/C: Antigravity remains retired and non-dispatchable. The observed app-local scheduler is external noncanonical state; release verification must show it absent, but this proposal does not reactivate or depend on C.

Ollama/D and OpenRouter/F: no hook-surface mutation is proposed. They remain release LO candidates only after dispatcher health and fresh smoke evidence are green.

## Proposed Implementation

1. Keep the current incident breaker active while release readiness is red:
   - project Codex hooks remain disabled;
   - project shell snapshot remains disabled where supported;
   - `.codex/hooks.json` remains inert unless a later GO re-enables it after no-window validation.
2. Add a deterministic Python AST scanner, `scripts/windows_no_window_spawn_audit.py`, that scans tracked Python files for `subprocess.run`, `subprocess.Popen`, `os.system`, `os.popen`, `os.startfile`, and related launcher surfaces.
3. The scanner must classify every finding into one of these release states:
   - compliant no-window launch;
   - intentionally foreground/interactive with an allowlist reason;
   - test-only/archive/adopter fixture outside GT-KB release runtime;
   - violation requiring correction.
4. Add regression tests for the scanner, including false-positive protection for kwargs dictionaries and explicit violations for foreground `cmd`, `powershell`, `pwsh`, and direct Python background launches on Windows.
5. Fix all GT-KB release-runtime violations found by the scanner in dispatcher, bridge, hook, scheduler, and daemon launch paths. Prefer a small shared helper only if it reduces repeated Windows flag boilerplate without crossing package boundaries awkwardly.
6. Update existing hook and daemon tests so breaker mode and enabled no-window mode are both accepted, but foreground hook launchers are rejected.
7. Preserve separate tracking for upstream Codex Desktop internal process probes. GT-KB must not claim to fix app-owned probes, but the release report must distinguish upstream Codex behavior from GT-KB-controlled launcher behavior.

## Spec-Derived Verification Plan

The implementation report must include:

1. Static audit evidence:
   - run the new scanner over tracked Python files;
   - report zero release-runtime violations;
   - list any intentional foreground/interactive allowlist entries with reasons.
2. Focused tests:
   - `python -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`
   - `python -m ruff check scripts/windows_no_window_spawn_audit.py scripts/cross_harness_bridge_trigger.py scripts/gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
   - `python -m ruff format --check scripts/windows_no_window_spawn_audit.py scripts/cross_harness_bridge_trigger.py scripts/gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
3. Dispatcher-control evidence:
   - dispatcher config/status continues to exclude retired Antigravity C from dispatch;
   - daemon remains stopped until the no-window gate is green.
4. Live no-storm evidence:
   - a process watcher spanning at least one prior storm interval records zero GT-KB hook/scheduler/daemon/dispatcher command children that would launch visible consoles;
   - any remaining Codex Desktop internal Git or process probes are classified separately as upstream app behavior.

## Acceptance Criteria

- The scanner is tracked and tested, so future release gates can repeat the no-window audit.
- All GT-KB-owned release-runtime Python launcher violations are fixed or intentionally allowlisted with a reason.
- Codex hooks stay disabled until enabled-mode no-window validation exists.
- The owner can type in Codex without GT-KB-controlled console bursts stealing focus.
- The release report explicitly separates GT-KB-controlled behavior from upstream Codex Desktop behavior.

## Risk / Rollback

The main risk is broadening scope enough to delay release. The control is to fix only GT-KB release-runtime violations now, while recording test/archive/adopter and truly interactive findings as classified non-release-runtime entries. Rollback is to keep breaker mode active and leave daemon/hooks disabled until a narrower no-window fix is verified.
