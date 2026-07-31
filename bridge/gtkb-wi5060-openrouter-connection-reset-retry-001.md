NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex interactive Prime Builder

bridge_kind: prime_proposal
Document: gtkb-wi5060-openrouter-connection-reset-retry
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060

target_paths: ["scripts/openrouter_harness.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: source | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# WI-5060 Follow-On: OpenRouter connection reset retry hardening

## Summary

This proposal requests a narrow OpenRouter/F harness repair. After the earlier WI-5060 readiness and headless fixes, the dispatcher successfully selected OpenRouter/F for Prime Builder work without a model argument, proving the cloud-default route is active. The live F run then failed before producing work because a provider-side socket reset escaped `scripts/openrouter_harness.py` as a raw `ConnectionResetError` traceback from `urllib.request.urlopen`.

The OpenRouter harness already has bounded retry behavior for transient HTTP statuses, `urllib.error.URLError`, and transient non-JSON bodies. The observed failure is the same reliability class but travels through Python's direct socket exception path instead of `URLError`. The proposed repair is to classify direct `ConnectionError`/socket reset failures from the `urlopen` call as retryable transient transport failures inside the existing `call_openrouter_chat` retry loop, then fail closed as `OpenRouterHarnessError` after the existing attempt budget instead of crashing with an uncaught traceback.

## Current Evidence

- Live dispatch evidence: `.gtkb-state/bridge-poller/dispatch-runs/2026-07-07T07-20-24Z-prime-builder-F-4c4b7e.exit_code` contains `1`.
- Live stderr evidence: `.gtkb-state/bridge-poller/dispatch-runs/2026-07-07T07-20-24Z-prime-builder-F-4c4b7e.stderr.log` shows `ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host` bubbling out of `scripts/openrouter_harness.py` `call_openrouter_chat` at the `urllib.request.urlopen` call.
- `gt bridge dispatch status --json` reports OpenRouter/F as active and selected for Prime Builder dispatch, with `last_result=work_intent_already_held` after the failed implementation claim.
- The F invocation surface does not require a model argument; OpenRouter model selection remains the cloud/default route and is not part of this proposal.
- `scripts/openrouter_harness.py` `call_openrouter_chat` catches `urllib.error.HTTPError` and `urllib.error.URLError`, but not direct `ConnectionError` from the socket/SSL stack.
- `platform_tests/scripts/test_openrouter_harness.py` already contains WI-4817 retry tests for HTTP 502, HTTP 429, HTTP 500 exhaustion, non-transient HTTP 401/403, and non-JSON transient responses, but no regression for direct `ConnectionResetError`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require a live bridge GO with matching target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay inside active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO or implementation-start gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must link work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation proposals require Project Authorization, Project, Work Item, and target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map behavior claims to concrete tests/evidence before VERIFIED.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned harnesses must fail predictably and remain process-supervisable during transient provider failures.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/health/report commands are the authoritative topology and readiness evidence surface.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, provider credential mutation, or key rotation is in scope.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5060 and the active WI-5060 PAUTH authorize bounded source/test harness readiness repair for OpenRouter/F. This is not a model-routing or credential change; it is a retry/fail-closed repair for an observed live transport failure that currently crashes the F harness process.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - GO authorizing the targeted WI-5060 PAUTH path before implementation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - active bounded WI-5060 source/test/config/governance authorization.
- `bridge/gtkb-wi5060-harness-readiness-repair-004.md` - VERIFIED original shim/readiness repair.
- `bridge/gtkb-wi5060-headless-dispatch-window-hardening-004.md` - VERIFIED headless dispatch window hardening.
- `bridge/gtkb-wi5060-no-window-helper-force-windows-compat-002.md` - GO for the current no-window helper compatibility follow-on.
- `.gtkb-state/bridge-poller/dispatch-runs/2026-07-07T07-20-24Z-prime-builder-F-4c4b7e.stderr.log` - fresh live evidence of the direct connection reset escape.

## Owner Decisions / Input

No additional owner decision is needed for this bridge filing. Mike already authorized the A/C/D/F harness repair goal and the headless fix. This proposal is the next bounded F repair exposed by live dispatch evidence.

## Proposed Scope

1. Extend `scripts/openrouter_harness.py` `call_openrouter_chat` to catch direct `ConnectionError` from `urllib.request.urlopen` as a transient transport failure inside the existing bounded retry loop.
2. Preserve fail-fast behavior for non-transient HTTP 401/403 and preserve existing rate-limit/backpressure messaging.
3. Preserve the existing `CHAT_MAX_ATTEMPTS`, backoff budget, timeout budget, endpoint, payload shape, OpenRouter cloud-default model behavior, and response parsing semantics.
4. Add a focused regression test in `platform_tests/scripts/test_openrouter_harness.py` proving a first-attempt `ConnectionResetError` retries and then succeeds.
5. Add or preserve exhaustion coverage so repeated direct connection resets fail as `OpenRouterHarnessError` after the bounded attempt count, without leaking a raw traceback.

## Out Of Scope

- No changes to OpenRouter credentials, provider account settings, env.local, API keys, or model configuration.
- No changes to `.api-harness/routing.toml`, harness registry, dispatcher ranking, role assignment, cost budgets, or max-turn budgets.
- No change to the no-window helper proposal target paths.
- No broad retry policy redesign beyond direct socket connection reset classification.
- No deployment, push, force-push, destructive cleanup, or untracked file deletion.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt bridge show gtkb-wi5060-openrouter-connection-reset-retry --json --compact`; implementation claim after GO | Latest status is `GO` before protected source/test edits; target paths match proposal. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect proposal header and active PAUTH record | Proposal cites `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707`; target paths fit source/test harness repair scope. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --tb=short --basetemp .test-tmp/pytest-openrouter-connection-reset` | Direct `ConnectionResetError` is retried or fails closed as `OpenRouterHarnessError`; no raw traceback escapes the harness function. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch health --json`; `gt bridge dispatch status --json` | Dispatcher health remains `PASS`; no registry/eligibility mutation is included. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps each claim above to focused pytest, ruff, and dispatcher health/status evidence | Loyal Opposition can verify behavior from tests and live dispatch evidence. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Diff review | No credential values, provider secrets, env.local mutation, credential upload, or rotation instructions. |

## Acceptance Criteria

- A direct `ConnectionResetError` raised by `urllib.request.urlopen` is handled by the existing bounded retry/fail-closed path.
- A first-attempt connection reset followed by a valid OpenRouter response succeeds.
- Repeated direct connection resets exhaust the existing attempt budget and raise `OpenRouterHarnessError`, not a raw traceback.
- Existing HTTP retry, 429 backpressure, non-transient HTTP 401/403 fail-fast, and non-JSON retry tests continue to pass.
- Ruff check and format check pass for `scripts/openrouter_harness.py` and `platform_tests/scripts/test_openrouter_harness.py`.
- Dispatcher health remains `PASS`; no registry or dispatch eligibility mutation is part of this slice.

## Risk / Rollback

Risk is low and isolated to exception classification in the OpenRouter chat transport wrapper plus focused tests. Rollback is a source/test revert for the two listed target paths. Bridge files are append-only governance records and are not deleted by rollback.

## Recommended Commit Type

`fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
