NEW

# WI-5060 Harness Readiness Repair - OpenRouter/F and Ollama/D Shim Fixes

bridge_kind: prime_proposal
Document: gtkb-wi5060-harness-readiness-repair
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive session; role prime-builder; approval_policy=never; danger-full-access workspace

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060

target_paths: ["scripts/openrouter_harness.py", "scripts/ollama_harness.py", ".api-harness/routing.toml", "harness-state/harness-registry.json", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_dispatcher_budget_constants_regression.py"]

implementation_scope: source | configuration | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal repairs the WI-5060 provider-shim readiness blocker for currently assigned harnesses. The immediate defects are in the OpenRouter/F and Ollama/D shim path: OpenRouter/F is invoked without `--model` but the shim still resolves `.api-harness/routing.toml` to a concrete routed model and sends that model in the OpenRouter API payload, contrary to the owner-stated cloud-default OpenRouter configuration; Ollama/D can also classify blank final assistant text as a successful exit and lacks OpenRouter's repeated no-progress tool-call guard.

The repair keeps Codex/A and Antigravity/C in the verification gate because they are the currently selected Prime Builder and Loyal Opposition harnesses. A/C are already dispatchable in the registry and are not proposed for source changes unless their readiness checks reveal a defect inside the explicit target paths. D/F re-enablement is allowed only after focused unit tests and local live-smoke evidence.

## Current Evidence

- `gt bridge show gtkb-wi5060-shim-max-turn-exhaustion-authorization --json --compact` returns latest status `GO` at `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md`.
- `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` initially had no WI-5060 PAUTH; owner decision `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` and PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` now provide bounded implementation authorization.
- `harness-state/harness-registry.json` currently has A dispatchable as Prime Builder and C dispatchable as Loyal Opposition, while D and F are active but `can_receive_dispatch=false`.
- Focused unit check before this proposal: the repo venv ran pytest against `platform_tests/scripts/test_openrouter_harness.py`, `platform_tests/scripts/test_ollama_harness.py`, and `platform_tests/scripts/test_dispatcher_budget_constants_regression.py` with quiet output and pytest cache disabled; observed result was `86 passed`.
- Live smoke before this proposal: OpenRouter/F returned `OK` for a tiny non-mutating prompt, proving current provider connectivity. Ollama/D returned `OK` without the LO bridge-review system prompt and for the verification skill, but returned a blank successful output for `--skill bridge-review`, exposing the blank-final-output success defect.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires status-bearing bridge work and role-correct proposal/GO sequencing before protected source/config mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded project authorization before implementation under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass Loyal Opposition GO, implementation-start, post-implementation reporting, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header includes Project Authorization, Project, and Work Item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each behavior to concrete tests and live readiness checks.
- `GOV-ENV-LOCAL-AUTHORITY-001` - live OpenRouter credential use remains read-only from `.env.local`; no credential lifecycle, disclosure, or rotation is in scope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - D/F readiness must be measured through the supported dispatcher/control-plane shape, not ad hoc durable-state claims alone.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatch status/health commands are the verification surface for final dispatchability.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, PAUTH, bridge proposal, tests, implementation report, and verification are preserved as durable linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair is framed as an artifact graph rather than an untracked local patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - D/F move from disabled/blocking evidence toward re-enabled readiness only through explicit lifecycle evidence.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner decision establishing this active repair goal and OpenRouter cloud-default Kimi constraint.
- `DELIB-F-POSTFIX-VERIFICATION-SSL-WATCH-20260706` - OpenRouter SSL failure treated as transient, not the current blocker.
- `DELIB-F-MAXTURN-PERSISTS-REDISABLE-20260706` - OpenRouter/F max-turn recurrence after SSL/connectivity cleared; F re-disabled.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-001.md` - Prime Builder governance advisory requesting PAUTH scope.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - Loyal Opposition GO authorizing targeted PAUTH only, not source mutation.
- `bridge/gtkb-wi5048-openrouter-prime-builder-dispatch-activation-005.md` - prior OpenRouter/F activation evidence showing `--max-turns 80` and remaining smoke evidence gaps.

## Owner Decisions / Input

Owner input is already captured in `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL`: Mike directed diagnosis and repair of OpenRouter/F and testing/fixing A, C, D, and F for their currently assigned roles, with the explicit constraint that OpenRouter/F must rely on the cloud default `moonshotai/kimi-k2.7-code` and should not require a model argument in invocation.

No additional owner input is required for this proposal. The PAUTH forbids credential lifecycle, deployment, secret disclosure, destructive cleanup, and D/F re-enablement without successful smoke evidence.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5060, the fresh PAUTH GO, `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL`, and the dispatcher/control-surface specifications provide enough authority to repair shim readiness without creating a new specification.

## Proposed Scope

1. OpenRouter/F cloud-default routing:
   - Add an explicit OpenRouter route/config capability that can omit the `model` field from the OpenRouter API payload when the selected route is the owner-approved cloud default.
   - Preserve explicit `--model` override behavior for diagnostics and future non-default routing.
   - Preserve response-model provenance so bridge author metadata records `response.model` when OpenRouter returns the actual served model.

2. Provider-shim final-output semantics:
   - Make OpenRouter and Ollama fail closed on missing or blank final assistant text instead of returning success with empty output.
   - Port OpenRouter's repeated no-progress tool-call guard to Ollama so D fails quickly and truthfully instead of exhausting the full turn budget on identical tool loops.

3. Turn/readiness behavior:
   - Keep F's configured `--max-turns 80` and long session timeout unless evidence shows another value is needed.
   - Keep D's default turn budget unless focused tests show the default is the blocker after the blank/repetition fixes.

4. Dispatchability:
   - Verify A and C remain current-role capable.
   - Re-enable D/F dispatch only after focused unit tests and local live smoke show truthful nonblank provider output.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5060-harness-readiness-repair` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5060-harness-readiness-repair` before implementation-start | Applicability pass and zero blocking clause gaps |
| OpenRouter cloud-default constraint | Focused unit test in `platform_tests/scripts/test_openrouter_harness.py` proving the default/implementation route omits `payload["model"]`; live `scripts/openrouter_harness.py` smoke using the prompt option and `--skill implementation`, with no `--model` option | Unit payload lacks `model`; live output is nonblank and returns `OK` or another valid final text |
| Provider-shim final-output semantics | Focused OpenRouter and Ollama unit tests for blank final text | Blank final text raises harness error and exits nonzero through `main` |
| Ollama no-progress guard | Focused unit test in `platform_tests/scripts/test_ollama_harness.py` with repeated identical tool calls | Fails with repeated no-progress tool-loop error before max-turn exhaustion |
| Existing shim behavior remains stable | Repo venv pytest run against `platform_tests/scripts/test_openrouter_harness.py`, `platform_tests/scripts/test_ollama_harness.py`, and `platform_tests/scripts/test_dispatcher_budget_constants_regression.py`, with quiet output and pytest cache disabled | All focused tests pass |
| A/C/D/F role readiness | `python scripts/check_harness_parity.py --harness codex --role prime-builder --json`; `python scripts/check_harness_parity.py --harness antigravity --role loyal-opposition --json`; corresponding D/F checks; `python scripts/harness_parity_phase2.py --project-root . --format markdown` | A/C remain current-role capable; D/F blockers reduced to waived/known non-runtime surfaces or resolved |
| Dispatcher control surface | `gt bridge dispatch status --json` and `gt bridge dispatch health --json` | A/C selected or available as before; D/F enabled only after smoke and visible as capable for their assigned roles |

## Risk / Rollback

Risk is concentrated in provider payload compatibility and dispatcher re-enablement. Rollback is a single commit revert restoring the prior shim/config/registry behavior and re-disabling D/F if smoke evidence regresses. No credential mutation, deployment, destructive cleanup, or broad backlog/status mutation is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing bridge file for `gtkb-wi5060-harness-readiness-repair`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
