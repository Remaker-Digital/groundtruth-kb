GO

# Loyal Opposition Review - Ollama-D Dispatch Reliability

**Document:** `gtkb-wi4962-ollama-d-dispatch-reliability`
**Reviewed version:** `bridge/gtkb-wi4962-ollama-d-dispatch-reliability-001.md`
**Verdict:** GO
**Date:** 2026-07-06
**Reviewer:** Antigravity (harness ID C)

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 7dbb24dc-6cfd-4976-a7b7-2ac2938b3da9
author_model: Gemini 3.5 Flash (High)
author_model_version: gemini-3.5-flash-high
author_model_configuration: interactive Loyal Opposition session; review_mode=strict; validation=pytest

## Verdict

GO.

The proposal is well-scoped and targets the real launch failure and session budget timeout issues associated with the Ollama-D harness in the Loyal Opposition role.

The implementation is authorized to proceed, subject to the conditions and findings below.

## Prior Deliberations

Deliberation search was performed before review:

- `DELIB-202665303` - Owner decision: WI-4987 fix = per-harness worker timers, generous first, dial in with experience. The timer design should set per-harness (not per-role) worker timers with generous initial allowances so no harness+model+config is falsely worker_timeout'd; also ensure the configured lifetime actually reaches the worker.
- `DELIB-ENABLE-OLLAMA-OPENROUTER-DISPATCH-20260705` - Enabled D and F for bridge dispatch; F capped at dispatch_max_items=1.
- `DELIB-20260704-OLLAMA-DISPATCH-DISABLE-CREDITS` - Bounded credits exhaustion.
- `DELIB-20261065` - Loyal Opposition Report - Ollama Harness Parity Gaps and role-realignment context.
- `DELIB-20261064` - Decision Memo - Ollama Harness Integration & Task-to-Model Routing.

## Findings And Conditions

### F1 - Circuit Breaker Reset Sequencing

**Claim:** The circuit breaker for Ollama-D must not be reset or validated prior to confirming the reliability of the subprocess launch path and timeout handling.

**Evidence:** Work Item WI-4962 description requires: "reset/validate the circuit breaker only AFTER the launch+timeout faults are fixed". The proposal correctly reflects this under "Spec-Derived Verification Plan".

**Risk / impact:** Resetting the circuit breaker early or validating it before testing launch path improvements can mask lingering faults, leading to immediate recurrence of tripped states.

**Required action:** The implementation report must show verification evidence (passing tests) for the launch path and timeouts before resetting the circuit breaker.

### F2 - Timeout Alignment and Derivation

**Claim:** There is a mismatch between `DEFAULT_SESSION_TIMEOUT_SECONDS = 540.0` defined in `scripts/ollama_harness.py` and the 3600s configuration `routing.ollama.timeout_seconds` in `.api-harness/routing.toml`.

**Evidence:** `scripts/ollama_harness.py` defines `DEFAULT_SESSION_TIMEOUT_SECONDS = 540.0` at line 40. `.api-harness/routing.toml` defines `timeout_seconds = 3600` at line 47.

**Risk / impact:** If the session timeout is not derived properly from the routing TOML config, slow cloud models (like `deepseek-v4-pro:cloud` or `kimi-k2.7-code:cloud`) will hit the hard 540s session-budget timeout limit before completing a chat turn, resulting in worker_timeout failures.

**Required action:** The implementation must ensure that `resolve_runtime_timeouts` correctly resolves the operation and session timeouts using the values configured in the routing TOML when CLI overrides are not supplied, and that these timeouts are successfully applied to the tool loop execution.

### F3 - Subprocess Launch Safety under Windows

**Claim:** Subprocess launches must preserve Windows-safe flags and normalize relative paths using backslashes to avoid `WinError 2` failures.

**Evidence:** `scripts/dispatcher_runtime.py` implements `_normalize_argv_head` to handle relative forward-slash paths and command name resolution under Windows.

**Risk / impact:** On Windows runtimes, relative paths with forward slashes (e.g. `groundtruth-kb/.venv/Scripts/python.exe`) fail to resolve under `CreateProcess` if not converted to backslashes, leading to `subprocess_execution_failed`.

**Required action:** Any modifications to the harness spawn flow must preserve this normalization path and ensure Windows compatibility.

## Applicability Preflight

- packet_hash: `sha256:fe4e859dbe70202b741cef92516394a0153de0610079d30c68e00dca5ce4c1ee`
- bridge_document_name: `gtkb-wi4962-ollama-d-dispatch-reliability`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4962-ollama-d-dispatch-reliability-001.md`
- operative_file: `bridge/gtkb-wi4962-ollama-d-dispatch-reliability-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
