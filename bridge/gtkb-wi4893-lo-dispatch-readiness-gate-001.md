NEW

# gtkb-wi4893-lo-dispatch-readiness-gate - Dispatcher LO completion health hardening

bridge_kind: prime_proposal
Document: gtkb-wi4893-lo-dispatch-readiness-gate
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-28 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop default; reasoning effort not exposed

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893

target_paths: ["scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "scripts/cursor_harness.py", "scripts/openrouter_harness.py", "scripts/_env.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal closes the remaining WI-4893 dispatcher release-readiness gap discovered after the first PID-provenance implementation reports were filed. The dispatcher restarted and selected all three Loyal Opposition dispatch targets, but none produced a verdict: Ollama/D exited with `max-turn exhaustion before final assistant text`, Cursor/E exited `0` after launching the GUI/Electron path and emitted only unsupported-flag warnings, and OpenRouter/F exited because `OPENROUTER_API_KEY` was unavailable to the release-worktree process even though the owner-maintained primary `.env.local` contains it. Despite those outcomes, `gt bridge dispatch status --json`, `health --json`, and `report --json` still reported `health_status: PASS`, `runtime_failure_count: 0`, and empty findings.

The implementation will make LO dispatch readiness fail visibly when selected targets cannot complete bridge work. It will add OpenRouter credential forwarding to the dispatcher allowlist, make Cursor fail closed before launching the GUI when no supported headless agent executable is present, and tighten dispatch report/status health so recent non-completing worker outcomes cannot be summarized as PASS. It will not copy, print, or commit credential values.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require this GO plus an implementation-start authorization packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the dispatcher and release-readiness specifications constraining the repair.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the work is tied to the active WI-4893 project authorization and exact target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the three observed dispatch failure classes become visible and actionable.
- `GOV-STANDING-BACKLOG-001` - WI-4893 is the controlling MemBase work item for release-blocking dispatcher readiness.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher health must reflect operational completion, not just spawn attempts.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the centralized dispatcher must surface failed and non-completing LO routes before release.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - `gt bridge dispatch status|health|report` must expose warnings/errors that match runtime outcomes.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatched worker envelopes and credential forwarding must be deterministic and auditable without leaking secrets.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - process cleanup remains limited to explicit dispatcher worker sidecars; this proposal does not broaden kill behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the release-blocking runtime findings are preserved as a bridge proposal instead of being left as transient scratch diagnosis.

## Prior Deliberations

- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues must be diagnosed and resolved before release and that the dispatcher needs a readiness test plan.
- `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-001.md` and `-002.md` - original WI-4893 source/test GO scope.
- `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-003.md` - filed implementation report that disclosed the stale/not-running daemon caveat.
- `bridge/gtkb-wi4893-daemon-test-provenance-scope-amendment-001.md` through `-003.md` - companion daemon test target and report.
- `bridge/gtkb-wi4884-daemon-resilience-formalization-006.md` - daemon resilience GO context supplied by the owner.
- `bridge/gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap-004.md` - create-time provenance precedent.
- `bridge/gtkb-wi4861-soft-reset-prune-stale-dispatch-runs-004.md` - stale dispatch-run pruning precedent.
- `bridge/gtkb-wi4765-dispatch-report-cli-004.md` - dispatch report baseline.

## Owner Decisions / Input

The owner explicitly made dispatcher release readiness the top priority and stated that all dispatcher issues must be diagnosed and resolved before release. No additional owner decision is required for this bounded implementation because it stays inside WI-4893's release-readiness authorization and does not require credential disclosure, credential rotation, production deployment, or formal artifact mutation.

## Requirement Sufficiency

Existing requirements sufficient - the linked dispatcher architecture, centralized dispatch service, dispatcher control-surface, dispatch envelope, release-readiness, and bridge authority requirements already require selected LO routes and health surfaces to represent real dispatch readiness. No new requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / governing surface | Required verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4893-lo-dispatch-readiness-gate` succeeds and target validation covers every targeted path. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` proves `OPENROUTER_API_KEY` is allowlisted for dispatch env forwarding without logging values. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` / `ADR-DISPATCHER-ARCHITECTURE-001` | `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short` proves recent max-turn, missing-key, and GUI-warning dispatch outcomes produce WARN/FAIL findings instead of PASS/runtime_failure_count 0. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Synthetic recent-run fixtures for D, E, and F show that selected LO targets with no verdict-producing completion remain release-blocking until cleared or corrected. |
| Cursor headless dispatch readiness | `python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short` proves the shim fails closed when only the Cursor GUI launcher is present and no supported `agent` executable is available. |
| OpenRouter dispatch readiness | `python -m pytest platform_tests/scripts/test_openrouter_harness.py -q --tb=short` preserves local `.env.local` loading behavior and key-present/key-absent failure semantics without printing secrets. |
| Code quality | `python -m ruff check <changed files>` and `python -m ruff format --check <changed files>` both pass. |
| Live readiness smoke | After implementation and verification, `gt bridge dispatch health --json`, `gt bridge dispatch status --json`, `gt bridge dispatch report --json`, and `gt bridge dispatch daemon status --json` must not claim PASS when selected LO routes are currently unable to produce bridge verdicts. |

## Risk / Rollback

Risk is that stricter health classification may surface more WARN/FAIL states during release work. That is intentional: a green dashboard that hides failed LO routes is more dangerous than a noisy but truthful one. Rollback is a single revert of the implementation commit plus its VERIFIED verdict; it restores the previous permissive health semantics and Cursor/OpenRouter dispatch behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4893-lo-dispatch-readiness-gate`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: this repairs release-blocking dispatcher readiness and health-reporting defects without adding a new user-facing capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
