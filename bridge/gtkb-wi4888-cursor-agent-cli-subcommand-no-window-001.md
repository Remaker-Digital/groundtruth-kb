NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-prime-builder-A-20260629-release-hardening-9a99ba77-0f15-454d-94ac-cccf28523645
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex desktop interactive session; Prime Builder role; dispatcher release hardening

# gtkb-wi4888-cursor-agent-cli-subcommand-no-window - Cursor Agent CLI subcommand and no-window dispatch readiness

bridge_kind: prime_proposal
Document: gtkb-wi4888-cursor-agent-cli-subcommand-no-window
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4888

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: Cursor headless harness launcher, Windows subprocess flags, and dispatcher readiness tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Dispatcher health currently reports `prime-builder:E` as failed with `cursor_headless_cli_unavailable`. Live local evidence shows the installed Cursor CLI is available as `cursor.exe` version 3.9.16 and exposes an `agent` subcommand, while `scripts/cursor_harness.py` only resolves a standalone `agent` executable and explicitly rejects Cursor launcher names. This mismatch makes Cursor unusable as a release dispatch target even though the harness registry and dispatcher config still mark Cursor E active and dispatch-capable.

This proposal fixes the Cursor headless launcher for the current installed CLI shape without reintroducing visible Windows console windows. The shim should accept the current `cursor agent` subcommand path when no standalone `agent` binary exists, keep rejecting accidental GUI-only invocation, and add Windows `CREATE_NO_WINDOW` protection to its `subprocess.run` call.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test mutation requires bridge review, GO, implementation-start evidence, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation proposal must cite applicable governing requirements before work starts.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - release dispatch must use one bounded, inspectable dispatcher control surface.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status must accurately reflect whether a configured harness can receive work.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatched harness execution must be bounded, observable, and fail with classified evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher release readiness requires reliable per-harness launch paths.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Cursor parity must be explicit and tested when its CLI surface changes.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires evidence that selected harnesses can actually run.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from this launch/readiness behavior.

## Prior Deliberations

- `bridge/gtkb-wi4881-headless-cursor-lo-dispatch-verdicts-004.md` - prior terminal VERIFIED Cursor headless dispatch thread; the installed CLI surface has since drifted under the shim.
- `WI-4888` - open full-topology go-live acceptance item requiring real-harness smoke before release.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues must be diagnosed and resolved before release.
- Owner live incident reports on 2026-06-28/2026-06-29 - visible Windows console spawning is a release showstopper; no dispatcher launcher fix may create foreground console windows.

## Owner Decisions / Input

No new owner input is required. Mike already authorized diagnosing and correcting dispatcher release blockers and asked whether Cursor should be switched to an active LO role if necessary. This proposal concludes that a role switch would not help until the Cursor launcher itself can run headlessly.

## Requirement Sufficiency

Existing requirements are sufficient. The defect is implementation drift against the configured Cursor dispatch target: the harness registry expects `scripts/cursor_harness.py`, the local Cursor CLI exposes `cursor agent`, and the shim still requires a standalone `agent` binary. No new requirement is needed.

## Proposed Implementation

1. Update `scripts/cursor_harness.py` so `_resolve_agent_executable` can return either:
   - a standalone headless `agent` executable when present; or
   - the installed Cursor launcher plus `agent` subcommand when `cursor` or `cursor.cmd` exposes the Agent subcommand.
2. Preserve fail-closed behavior for explicit `CURSOR_AGENT_BIN` values that point at a Cursor launcher unless the implementation has an unambiguous way to append the `agent` subcommand. Explicit override mistakes must still explain how to configure the shim.
3. Update command construction so the generated argv begins with either `agent ...` or `cursor agent ...` and never launches the GUI-only surface.
4. Add Windows no-window subprocess protection to the Cursor harness `subprocess.run` call, using `CREATE_NO_WINDOW` when available on Windows and preserving existing behavior on non-Windows platforms.
5. Extend `platform_tests/scripts/test_cursor_harness.py` to cover standalone `agent`, `cursor agent` fallback, explicit override rejection or safe subcommand handling, command shape, and Windows creation flags.
6. Extend dispatcher readiness tests only where needed to ensure `cursor_headless_cli_unavailable` is cleared by the corrected resolver path and still fails closed when neither `agent` nor `cursor agent` is available.

## Spec-Derived Verification Plan

The implementation report must include:

1. Static/local evidence:
   - `cursor --help` shows the installed Cursor CLI exposes an `agent` subcommand.
   - `Get-Command cursor` resolves a launchable Cursor command on PATH.
2. Focused tests:
   - `python -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short`
   - `python -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py`
   - `python -m ruff format --check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py`
3. Dispatcher health evidence:
   - `python -m groundtruth_kb.cli bridge dispatch status --json` no longer reports `cursor_headless_cli_unavailable` after stale runtime state is reset or superseded by a fresh Cursor smoke.
4. No-window evidence:
   - the Cursor harness subprocess call carries Windows no-window flags, and the live no-storm watcher from WI-4896 records no GT-KB-controlled visible-console launcher during a Cursor smoke.

## Acceptance Criteria

- Cursor E can be resolved through the installed Cursor CLI Agent surface or fails closed with a precise, actionable message.
- Cursor harness execution does not allocate a visible Windows console under GT-KB control.
- Dispatcher health no longer reports `cursor_headless_cli_unavailable` after fresh runtime evidence.
- The release gate treats Cursor as unavailable until the corrected shim passes tests and a fresh smoke run.

## Risk / Rollback

The main risk is mistaking the GUI launcher for the headless Agent surface. The rollback is to keep Cursor E disabled for dispatch and rely on D/F LO targets until the shim is corrected and verified. No dispatcher config role flip is authorized by this proposal; any Cursor role reassignment remains a separate governed dispatcher-control action.
