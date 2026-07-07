NEW

# WI-5060 Follow-On: Ollama route max-turn budget

bridge_kind: prime_proposal
Document: gtkb-wi5060-ollama-route-max-turn-budget
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive session; role prime-builder; approval_policy=never; danger-full-access workspace

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060

target_paths: [".api-harness/routing.toml", "scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_dispatcher_budget_constants_regression.py"]

implementation_scope: source | configuration | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal repairs the remaining Ollama/D turn-budget defect observed after the verified WI-5060 shim-readiness work. The earlier VERIFIED chain fixed blank final output and repeated identical no-progress tool calls, but a later real Loyal Opposition bridge verification on D consumed the ordinary `80` turn budget and failed with `ollama_harness: max-turn exhaustion before final assistant text`.

The proposed fix is intentionally narrow: add an optional route-configured `max_turns` value for `[routing.ollama]`, use it when the dispatcher invocation omits `--max-turns`, preserve explicit CLI overrides, and raise D's configured bridge-review budget without changing model routes, credentials, dispatcher eligibility, ranking, or OpenRouter behavior.

## Current Evidence

- `bridge/gtkb-wi5060-harness-readiness-repair-004.md` is VERIFIED and records the earlier fix for blank final output plus repeated identical tool loops.
- `bridge/gtkb-wi5060-openrouter-connection-reset-retry-004.md` is VERIFIED and records the later OpenRouter connection-reset retry repair, committed at `4c520122343ce7cef0de549d8adb04f09cd97087`.
- The later D dispatch run `2026-07-07T07-35-47Z-loyal-opposition-D-6f0bf7` exited `1`; stderr is exactly `ollama_harness: max-turn exhaustion before final assistant text`.
- A subsequent Antigravity/C run `2026-07-07T07-41-37Z-loyal-opposition-C-f20d1a` verified the same OpenRouter report and exited `0`, proving the bridge item was reviewable by a functioning LO harness and that D's failure is a D budget/runtime concern rather than a bad report.
- `gt bridge dispatch health --json` currently reports `health_status: PASS`, with daemon, supervisor, and watchdog healthy, hidden, and using `pythonw.exe` where scheduled tasks launch Python.
- `gt bridge dispatch status --json` reports D and C selected for Loyal Opposition and F selected for Prime Builder. D's prior `max_turn_exhaustion` evidence is stale only because the referenced bridge document is now terminal, not because the D turn-budget behavior was corrected.
- `.api-harness/routing.toml` has `[routing.ollama] timeout_seconds = 3600` but no route-level `max_turns`.
- `scripts/ollama_harness.py` defines `DEFAULT_MAX_TURNS = 80`, the CLI parser defaults `--max-turns` to that constant, and `main()` passes `args.max_turns` directly into `run_tool_loop()`.
- `scripts/ollama_harness.py` already has `resolve_runtime_timeouts(args, config, argv)`, which reads route-configured `timeout_seconds` unless the CLI supplies an explicit timeout. There is no analogous route-aware max-turn resolver.
- `WI-5060` is resolved, but active PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` remains active and includes `WI-5060` for bounded harness-readiness source, test, configuration, and governance-evidence repair.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test/config changes require a live bridge GO, matching target paths, and append-only bridge evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the proposal cites the active WI-5060 PAUTH and stays inside its bounded source, test, configuration, and governance-evidence classes.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the active PAUTH does not bypass Loyal Opposition review, implementation-start authorization, post-implementation reporting, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal links work item, project, PAUTH, target paths, governing specs, and spec-derived verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header carries Project Authorization, Project, Work Item, and parseable inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation must add or identify tests that prove route-configured max turns apply and CLI overrides remain authoritative.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - D is a dispatcher-selected Loyal Opposition harness, so route/runtime budgets must support real bridge dispatch work rather than only tiny smoke prompts.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status and health commands are the live topology and reliability evidence surfaces after the change.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, provider secret mutation, or key rotation is in scope.
- `GOV-STANDING-BACKLOG-001` - this follow-on is tied to resolved `WI-5060` evidence and must not silently create or mutate unrelated backlog status.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner goal, PAUTH, proposal, implementation report, verification, and runtime evidence remain durable linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change is handled through a small artifact graph rather than an untracked local patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fresh D runtime failure is preserved as follow-on bridge evidence despite the earlier WI terminal state.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - Loyal Opposition GO authorizing the PAUTH path, while explicitly requiring a separate implementation proposal and GO before source/config mutation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - active bounded WI-5060 source/test/config/governance authorization.
- `bridge/gtkb-wi5060-harness-readiness-repair-004.md` - VERIFIED prior shim readiness repair, including blank-final-output and repeated identical tool-loop termination.
- `bridge/gtkb-wi5060-openrouter-connection-reset-retry-004.md` - VERIFIED later OpenRouter/F retry fix, which exposed that D still needs enough turn budget to complete real LO bridge verification work.
- `bridge/gtkb-wi5060-no-window-helper-force-windows-compat-002.md` - GO for a separate no-window helper compatibility slice; this proposal does not overlap those target paths.

## Owner Decisions / Input

No additional owner decision is needed for this filing. Mike already authorized the active A/C/D/F harness repair goal and the headless fix in this session, and the active WI-5060 PAUTH covers bounded source, test, configuration, and governance-evidence repair while forbidding credential lifecycle, deployment, destructive cleanup, broad bulk status mutation, untracked file deletion, secret disclosure, and D/F reenablement without successful smoke evidence.

## Requirement Sufficiency

Existing requirements sufficient. WI-5060, the active WI-5060 PAUTH, the verified WI-5060 bridge history, the fresh D dispatch evidence, and the dispatcher service/control specifications provide enough authority to repair D's route-level turn budget without creating a new specification.

## Proposed Scope

1. Add optional `max_turns: int | None` to `scripts/ollama_harness.py` `RoutingConfig`.
2. Parse optional `[routing.ollama] max_turns` from `.api-harness/routing.toml` with fail-closed positive-integer validation.
3. Add `resolve_runtime_max_turns(args, config, argv)` mirroring the existing route-aware timeout resolver: use `config.max_turns` when present and `--max-turns` was not supplied; preserve explicit CLI `--max-turns` overrides.
4. Update `main()` to pass the resolved max-turn value to `run_tool_loop()`.
5. Set `.api-harness/routing.toml` `[routing.ollama] max_turns = 200` so D bridge-review dispatch has more budget than the exhausted `80` turns while staying below the existing 3600-second route timeout.
6. Add focused tests in `platform_tests/scripts/test_ollama_harness.py` for config parsing, invalid values, config-default resolution, and CLI override precedence.
7. Update or preserve `platform_tests/scripts/test_dispatcher_budget_constants_regression.py` so parser defaults remain stable and the new route-config resolver behavior is explicitly covered where appropriate.

## Out Of Scope

- No OpenRouter/F code, routing, credential, model, or retry changes.
- No dispatcher eligibility, ranking, role assignment, recipient selection, or budget-pricing changes.
- No D/F reenablement operation; D and F are already selected/active according to the current dispatcher status surface, and this proposal does not mutate harness registry state.
- No `groundtruth.db`, backlog resolution, PAUTH, formal-artifact, or broad governance mutation.
- No deployment, push, force-push, credential lifecycle, destructive cleanup, or untracked file deletion.
- No attempt to hide real infinite loops by disabling the existing fail-closed repeated-tool-loop guard.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt bridge show gtkb-wi5060-ollama-route-max-turn-budget --json --compact`; `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5060-ollama-route-max-turn-budget` after GO | Latest status is `GO` before protected edits; implementation-start packet authorizes only the listed target paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect proposal/report headers and active PAUTH record | Proposal cites `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707`; target paths fit source/test/config/governance scope. |
| Route-config max-turn parsing | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short --basetemp .test-tmp/pytest-ollama-route-max-turns` | Tests pass for positive config parsing and fail-closed invalid or non-positive values. |
| CLI override precedence | Focused pytest in `platform_tests/scripts/test_ollama_harness.py` for `resolve_runtime_max_turns()` | Route `max_turns` is used only when `--max-turns` is absent; explicit CLI values win. |
| Existing budget invariants | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_budget_constants_regression.py -q --tb=short --basetemp .test-tmp/pytest-budget-regression` | Parser default remains `DEFAULT_MAX_TURNS`; per-invocation overrides still parse correctly. |
| Code quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check .api-harness/routing.toml scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_dispatcher_budget_constants_regression.py`; `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_dispatcher_budget_constants_regression.py` | Python lint and format checks pass; TOML path is included only if the local ruff invocation accepts it, otherwise the report states the Python-only ruff scope. |
| Dispatcher status truth | `gt bridge dispatch health --json`; `gt bridge dispatch status --json` | Health remains `PASS`; topology remains explicit and no registry/eligibility change is claimed by this slice. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Diff review | No credential values, environment files, provider secret lifecycle actions, or rotation instructions. |

## Acceptance Criteria

- `[routing.ollama] max_turns` is optional, positive-integer validated, and loaded into `RoutingConfig`.
- Dispatcher/default invocations that omit `--max-turns` use the route-configured max-turn budget.
- Explicit CLI `--max-turns` continues to override route configuration for focused diagnostics and small smoke tests.
- `.api-harness/routing.toml` sets D's Ollama route max-turn budget to `200`.
- Focused pytest and ruff checks pass for the changed files.
- Dispatcher health/status remain PASS after the implementation, without claiming a D full-review success until a subsequent real dispatch or smoke evidence proves it.

## Risk / Rollback

Risk is moderate and isolated to D runtime duration: raising the turn budget may let legitimately complex bridge reviews complete, but it can also keep an unproductive non-identical loop alive longer. The existing repeated identical no-progress guard, HTTP timeout, and session timeout remain in place. Rollback is a single source/config/test commit revert restoring the parser-only `DEFAULT_MAX_TURNS` behavior and removing `[routing.ollama] max_turns`.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing bridge file for `gtkb-wi5060-ollama-route-max-turn-budget`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
