NEW

# WI-5060 Follow-On: OpenRouter direct timeout retry

bridge_kind: prime_proposal
Document: gtkb-wi5060-openrouter-direct-timeout-retry
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

target_paths: ["scripts/openrouter_harness.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: source | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal repairs a fresh OpenRouter/F Prime Builder transport failure observed after the prior OpenRouter connection-reset retry fix was verified. A real F dispatch for the separate no-window helper GO thread reached OpenRouter, then exited with a raw Python `TimeoutError: The read operation timed out` from the `urllib.request.urlopen` response path. That timeout escaped `call_openrouter_chat()` instead of using the existing bounded retry/fail-closed OpenRouter transport path.

The proposed fix is intentionally narrow: classify direct `TimeoutError` exceptions from the OpenRouter request/response path as retryable transport failures alongside `urllib.error.URLError` and `ConnectionError`. Add focused tests proving a first direct timeout can retry to success and repeated direct timeouts fail closed as `OpenRouterHarnessError` rather than leaking a raw traceback.

## Current Evidence

- `bridge/gtkb-wi5060-openrouter-connection-reset-retry-004.md` is VERIFIED and records the prior OpenRouter/F direct `ConnectionResetError` retry repair.
- A later real F Prime Builder worker for `gtkb-wi5060-no-window-helper-force-windows-compat` failed: dispatch run `2026-07-07T07-53-19Z-prime-builder-F-66a110`, exit code `1`.
- `.gtkb-state/bridge-poller/dispatch-runs/2026-07-07T07-53-19Z-prime-builder-F-66a110.stderr.log` shows a raw `TimeoutError: The read operation timed out` escaping from `scripts/openrouter_harness.py` at the `urllib.request.urlopen` call inside `call_openrouter_chat()`.
- The failed F worker command line used `scripts/openrouter_harness.py` with a dispatch prompt, implementation skill, `--max-turns 80`, and `--session-timeout 5400`; the failure was provider transport timeout, not a model-default, no-window-helper, or max-turn exhaustion failure.
- `scripts/openrouter_harness.py` currently catches `urllib.error.URLError` and `ConnectionError` in the retry branch. It does not catch direct built-in `TimeoutError`.
- `platform_tests/scripts/test_openrouter_harness.py` already has adjacent WI-5060 tests proving direct `ConnectionResetError` retry and bounded exhaustion; there is no direct `TimeoutError` coverage.
- Active PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` covers bounded source/test/governance repair for WI-5060 harness readiness. This proposal does not require credential lifecycle, registry, dispatcher ranking, model, or route changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require a live bridge GO, matching target paths, and append-only bridge evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay inside active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO, implementation-start gates, post-implementation reporting, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must link work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation proposals require Project Authorization, Project, Work Item, and target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map behavior claims to concrete tests/evidence before VERIFIED.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned harnesses must fail predictably and remain process-supervisable during transient provider failures.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/health/report commands are the authoritative topology and readiness evidence surface.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, provider credential mutation, or key rotation is in scope.
- `GOV-STANDING-BACKLOG-001` - this follow-on is tied to WI-5060 harness-readiness evidence and does not mutate unrelated backlog state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner goal, PAUTH, proposal, implementation report, verification, and runtime evidence remain durable linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change is handled through a small artifact graph rather than an untracked local patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fresh F runtime timeout is preserved as follow-on bridge evidence rather than being folded silently into a different thread.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - Loyal Opposition GO authorizing the bounded PAUTH path, while requiring separate implementation proposal and GO before source/config mutation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - active bounded WI-5060 source/test/config/governance authorization.
- `bridge/gtkb-wi5060-harness-readiness-repair-004.md` - VERIFIED original shim/readiness repair.
- `bridge/gtkb-wi5060-headless-dispatch-window-hardening-004.md` - VERIFIED headless dispatch window hardening.
- `bridge/gtkb-wi5060-openrouter-connection-reset-retry-004.md` - VERIFIED OpenRouter/F direct connection-reset retry repair.
- `bridge/gtkb-wi5060-no-window-helper-force-windows-compat-002.md` - separate GO thread whose F implementation attempt exposed the direct timeout leakage. This proposal does not implement or alter the no-window helper logic.

## Owner Decisions / Input

No additional owner decision is needed for this filing. Mike already directed the A/C/D/F harness repair goal and authorized the headless fix in this session, and the active WI-5060 PAUTH covers bounded harness-readiness source, test, configuration, and governance-evidence repair. This proposal does not request or perform credential lifecycle, deployment, destructive cleanup, broad bulk status mutation, untracked file deletion, secret disclosure, or D/F re-enable operations.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5060, the active WI-5060 PAUTH, the verified OpenRouter bridge history, the fresh F dispatch failure, and the dispatcher service/control specifications provide enough authority to repair direct OpenRouter timeout handling without creating a new specification.

## Proposed Scope

1. Update `scripts/openrouter_harness.py` so direct built-in `TimeoutError` exceptions raised during the OpenRouter request/response path use the same bounded retry/fail-closed branch as `urllib.error.URLError` and `ConnectionError`.
2. Preserve existing `CHAT_MAX_ATTEMPTS`, retry backoff, 401/403 fail-fast behavior, 429 retry-after handling, endpoint/payload handling, cloud-default OpenRouter model routing, and response parsing behavior.
3. Add `platform_tests/scripts/test_openrouter_harness.py` coverage proving first-attempt direct timeout followed by a valid OpenRouter response succeeds after retry.
4. Add coverage proving repeated direct timeouts exhaust the existing attempt budget and raise `OpenRouterHarnessError` rather than leaking a raw `TimeoutError`.

## Out Of Scope

- No model, provider, route, credential, environment, OpenRouter account, or key lifecycle changes.
- No changes to `.api-harness/routing.toml`, dispatcher registry, dispatcher ranking, harness role assignment, or dispatch eligibility.
- No implementation of the separate no-window helper GO thread.
- No D/Ollama changes; the D route max-turn slice is tracked separately by `gtkb-wi5060-ollama-route-max-turn-budget`.
- No broad backlog/status mutation, deployment, push, force-push, destructive cleanup, or untracked file deletion.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt bridge show gtkb-wi5060-openrouter-direct-timeout-retry --json --compact`; `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5060-openrouter-direct-timeout-retry` after GO | Latest status is `GO` before protected edits; implementation-start packet authorizes only the listed target paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect proposal/report headers and active PAUTH record | Proposal cites `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707`; target paths fit source/test/governance scope. |
| Direct OpenRouter timeout retry | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --tb=short --basetemp .test-tmp/pytest-openrouter-direct-timeout` | Tests pass for retry-to-success after one direct `TimeoutError`. |
| Direct OpenRouter timeout exhaustion | Same focused pytest suite | Repeated direct `TimeoutError` attempts fail closed as `OpenRouterHarnessError`; raw timeout traceback no longer escapes. |
| Existing OpenRouter retry invariants | Same focused pytest suite | Existing HTTP retry, 429 backpressure, 401/403 fail-fast, connection-reset retry, non-JSON retry, and happy-path tests continue to pass. |
| Code quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check --no-cache scripts/openrouter_harness.py platform_tests/scripts/test_openrouter_harness.py`; `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check --no-cache scripts/openrouter_harness.py platform_tests/scripts/test_openrouter_harness.py` | Python lint and format checks pass. |
| Dispatcher status truth | `gt bridge dispatch health --json`; `gt bridge dispatch status --json` | Health remains `PASS`; topology remains explicit and no registry/eligibility change is claimed by this slice. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Diff review | No env file, credential, provider secret, key, account, or model routing mutation. |

## Acceptance Criteria

- A direct `TimeoutError` raised by the OpenRouter `urlopen` request/response path is handled by the existing bounded retry/fail-closed path.
- A first-attempt direct timeout followed by a valid OpenRouter response succeeds.
- Repeated direct timeouts exhaust `CHAT_MAX_ATTEMPTS` and raise `OpenRouterHarnessError`, not a raw traceback.
- Existing OpenRouter retry/fail-fast tests continue to pass.
- Focused pytest and Ruff checks pass for the changed source/test files.
- Dispatcher health remains `PASS`; no registry, eligibility, credential, route, model, or no-window-helper mutation is part of this slice.

## Risk / Rollback

Risk is low and isolated to OpenRouter/F transport classification. Direct socket/read timeouts will now spend the existing bounded retry budget before failing closed, matching the intended behavior for other transient transport failures. Rollback is a source/test revert for `scripts/openrouter_harness.py` and `platform_tests/scripts/test_openrouter_harness.py`. Bridge files remain append-only governance records.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing bridge file for `gtkb-wi5060-openrouter-direct-timeout-retry`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
