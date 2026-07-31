NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c57a453e-dccb-4ca1-afb7-1d23dfa8444a
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Post-Implementation Report - WI-5471 Tool-call argument parse resilience in dispatch worker shims

bridge_kind: prime_proposal
Document: gtkb-wi5471-toolcall-arg-parse-resilience
Version: 003
Responds to: bridge/gtkb-wi5471-toolcall-arg-parse-resilience-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5471

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_shim_toolcall_arg_resilience.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implemented per the -002 GO verdict's approved scope. In both `scripts/cloud_harness_base.py` (`run_tool_loop`) and `scripts/ollama_harness.py` (`run_tool_loop`), the per-tool-call `_tool_call_parts(call, index)` invocation is now wrapped in a try/except that catches the shim's own error class (`CloudHarnessError` / `OllamaHarnessError` respectively). On a parse failure, the loop constructs a best-effort `tool_call_id` (from `call.get("id")` when `call` is a dict, else `f"tool_call_{index}"`) and `tool_name` (from any partially-parsed function name, else the literal `"<malformed_tool_call>"`), appends a `{"role": "tool", "content": "ERROR: ..."}` message correlated to that call id, and `continue`s the per-call loop instead of propagating the exception. This exactly mirrors the existing recoverable-error pattern already used for `dispatch_tool_call` failures in both shims.

**Scope decision (per -002 Non-Blocking Observation #2):** the fix covers **all** of `_tool_call_parts`'s raise points (non-dict call, missing/non-dict function, missing/invalid function name, invalid-JSON arguments string, non-object arguments), not only the JSON-decode case named in the proposal's Acceptance Criteria. All raise points are the same class of "malformed tool call from the model" and the fix mechanism (catch-and-recover at the call site) is identical for all of them; narrowing to only the JSON-decode case would have left the other four raise points still fatal for no added safety benefit. Test coverage matches this broader scope (see below).

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification was needed to implement this fix; it is an internal error-handling correction within the scope described and GO'd in -001/-002.

## Specification Links (carried forward from -001/-002)

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-RELIABILITY-FAST-LANE-001`

## Spec-to-Test Mapping

| Specification | Test(s) | Result |
| --- | --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | `test_shim_toolcall_arg_resilience.py` (all 4 tests) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_shim_toolcall_arg_resilience.py::test_cloud_harness_malformed_json_arguments_is_recoverable`, `::test_cloud_harness_missing_function_name_is_recoverable`, `::test_ollama_harness_malformed_json_arguments_is_recoverable`, `::test_ollama_harness_missing_function_name_is_recoverable` | PASS (4/4) |

Each test drives `run_tool_loop` with a mocked `chat_func` that returns one malformed tool call on turn 1, asserts the turn-2 payload's last message is `{"role": "tool", "tool_call_id": <matching id>, "content": "ERROR: ..."}` (not an uncaught exception), and asserts the loop completes normally once the model's next response is well-formed.

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_shim_toolcall_arg_resilience.py -v
# 4 passed

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_ollama_harness.py -q
# 1 failed (test_ollama_harness.py::test_tool_loop_rejects_malformed_tool_arguments -- see Known Out-of-Scope Test Regression below), 179 passed

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py scripts/ollama_harness.py platform_tests/scripts/test_shim_toolcall_arg_resilience.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cloud_harness_base.py scripts/ollama_harness.py platform_tests/scripts/test_shim_toolcall_arg_resilience.py
# 3 files already formatted (after one ruff format pass to fix initial line-length)
```

## Known Out-of-Scope Test Regression (disclosed, not silently left)

`platform_tests/scripts/test_ollama_harness.py::test_tool_loop_rejects_malformed_tool_arguments` asserts the **pre-fix** behavior (a malformed call immediately raises `OllamaHarnessError` matching `"arguments string must be JSON"`). This is now factually wrong: the same input now recovers, and since the test's mock repeats the identical malformed call every turn with `max_turns=2`, the loop instead exhausts on `"max-turn exhaustion before final assistant text"`.

This file is **not** in this proposal's `target_paths`. Attempting to edit it was correctly blocked by the implementation-start gate (`GTKB-IMPLEMENTATION-START-GATE`, target outside authorization scope) when I tried during implementation -- the gate is functioning as intended and I did not attempt to route around it. Filed `WI-5550` (P3, `PROJECT-GTKB-RELIABILITY-FIXES`) to fix this single stale assertion under its own properly-scoped proposal. `test_shim_toolcall_arg_resilience.py` (in this proposal's scope) already independently covers the corrected single-call-recovers behavior for both shims, so the defect this proposal fixes is fully test-covered; only the *stale expectation* in the older file is outstanding, tracked separately.

## Acceptance Criteria Verification

- "A tool_call whose arguments string is not valid JSON yields a recoverable ERROR tool-result and the worker continues, in both the cloud worker-shim base and the local worker shim." -- VERIFIED (`test_cloud_harness_malformed_json_arguments_is_recoverable`, `test_ollama_harness_malformed_json_arguments_is_recoverable`).
- "Well-formed tool calls are unaffected, and ruff check plus ruff format --check pass on changed files." -- VERIFIED (179 - 1 known/disclosed = 178 pre-existing tests still pass across both full suites; ruff clean).

## Files Changed

- `scripts/cloud_harness_base.py` -- wrapped `_tool_call_parts` call site in `run_tool_loop`'s per-call loop.
- `scripts/ollama_harness.py` -- same fix at the equivalent call site.
- `platform_tests/scripts/test_shim_toolcall_arg_resilience.py` -- new, 4 tests covering both shims.

## Recommended Commit Type

`fix`

## Owner Decisions / Input

No new owner decision required; implemented under the standing fast-lane authorization per the -002 GO's "Owner Action Required: None."

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
