NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Proposal - Ollama dispatch timeout is bounded and classified without tracebacks

bridge_kind: prime_proposal
Document: gtkb-wi4933-ollama-timeout-classification
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Live dispatcher testing on 2026-06-30 launched `loyal-opposition:D` for `gtkb-wi4933-dispatch-backpressure-health` and produced no visible console windows, but the worker exited nonzero after a long silent wait. The dispatch sidecars show exit code `1`, empty stdout, and a raw Python traceback ending in `TimeoutError: timed out` from `urllib.request.urlopen` inside `scripts/ollama_harness.py::call_ollama_chat`.

That is not release-healthy. Provider/network timeouts must be bounded, converted to `OllamaHarnessError`, and surfaced as actionable provider timeout/backpressure diagnostics rather than raw tracebacks. This proposal narrows the next fix to the Ollama harness timeout path and focused regression coverage.

## Claim

Prime Builder proposes a bounded `WI-4933` implementation slice for the newly observed Ollama provider-timeout dispatch failure. This is an extension of the active provider backpressure/health classification work, not a topology change and not a revival of retired trigger paths.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4933` covers provider backpressure/health classification repair; the active PAUTH covers source and test changes for provider retry/backpressure handling. The live dispatch failure supplies the concrete acceptance gap.

## In-Root Placement Evidence

All target paths are relative in-root paths: `scripts/ollama_harness.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned harness execution must be bounded, observable, and release-health visible.
- `ADR-DISPATCHER-ARCHITECTURE-001` - fixes must keep the daemon as the dispatch path and avoid retired trigger fallbacks.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - health/report surfaces must classify runtime outcomes accurately.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatch must remain headless/no-window while surfacing failures through logs/status.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.

## Prior Deliberations

- `DELIB-20266507` - Authorize WI-4933 dispatcher backpressure health classification repair.
- `DELIB-20266276` - Authorize daemon-resilience program implementation and release-health hardening.
- `DELIB-20266505` - Authorize dispatcher diagnostic health release fix.

## Owner Decisions / Input

- `DELIB-20266507` - active owner-decision evidence for `WI-4933` provider backpressure/health classification repair.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH` - active project authorization covering `WI-4933` source/test changes.

## Evidence From Live Test

- Command: `python scripts/gtkb_dispatcher_daemon.py tick --max-items 1`.
- Spawned dispatch: `2026-06-30T08-44-14Z-loyal-opposition-D-7e1e80` for `loyal-opposition:D`.
- Sidecars: `.gtkb-state/bridge-poller/dispatch-runs/2026-06-30T08-44-14Z-loyal-opposition-D-7e1e80.*`.
- Result: `exit_code=1`, `stdout.log` length `0`, `stderr.log` contains a raw traceback ending in `TimeoutError: timed out` from `call_ollama_chat`.
- Dispatcher health after completion: WARN with `dispatch runtime failure: loyal-opposition:D latest_run=2026-06-30T08-44-14Z-loyal-opposition-D-7e1e80 failure_class=subprocess_execution_failed exit_code=1`.

## Proposed Scope

- Catch socket/request timeout exceptions in `scripts/ollama_harness.py::call_ollama_chat` and convert them to `OllamaHarnessError` with a concise timeout diagnostic.
- Preserve bounded retry behavior for retryable HTTP and URL transport failures.
- Ensure timeout diagnostics do not emit raw Python tracebacks for normal provider timeout/backpressure cases.
- Add focused tests in `platform_tests/scripts/test_ollama_harness.py` proving timeout exceptions are converted to `OllamaHarnessError` and existing retry behavior is preserved.

## Out Of Scope

- Dispatcher topology changes.
- Scheduler/watchdog task enablement.
- Any cross-harness trigger fallback.
- Broad health taxonomy changes outside the existing `WI-4933` target if not required by the Ollama timeout fix.
- Live provider credential changes.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused Ollama harness tests proving provider timeouts are bounded and reported without raw traceback behavior. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Confirm no retired trigger files or topology config are modified. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run `gt bridge dispatch health --json` after the fix; any remaining warning must be actionable and not caused by raw Ollama timeout traceback behavior. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Confirm the live dispatch path remains `pythonw.exe`/no-window-safe and does not add shell-wrapper launches. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability preflight before implementation report/verdict filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include focused pytest and ruff evidence for touched files. |

## Acceptance Criteria

- A socket/request timeout from `urllib.request.urlopen` in `call_ollama_chat` raises `OllamaHarnessError` with a concise timeout/provider diagnostic, not a raw traceback from the urllib stack.
- Existing HTTP retry/backoff and URL transport retry tests continue to pass.
- Focused tests for `scripts/ollama_harness.py` pass.
- Ruff check and format-check pass for touched files.
- Dispatcher live health no longer records the observed Ollama timeout defect as an unexplained raw subprocess crash after a bounded retest, or the remaining classification is explicitly actionable as provider timeout/backpressure.

## Risks / Rollback

Risk is low to moderate. The change is in a provider harness used by dispatcher LO work, so behavior must remain fail-closed and bounded. Rollback is a revert of the two target files. Bridge files remain append-only audit evidence.

## Files Expected To Change

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`fix`
