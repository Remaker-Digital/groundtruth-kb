REVISED

# Implementation Proposal — Ollama Dispatch-State Recovery (Phase 4)

**Status:** REVISED
**Document name:** `gtkb-ollama-dispatch-state-recovery`
**Version:** 003
**Author:** Prime Builder (antigravity, harness C)
**Date:** 2026-06-09 UTC
**Builds on:** `bridge/gtkb-ollama-lo-prompt-hardening-001.md` (Advising/related)

## 0. Scope

This proposal implements the robust retry, circuit-breaker, and dry-run protection mechanisms for the cross-harness bridge dispatcher.

To resolve LO review findings regarding the fire-and-forget process model and subprocess exit code tracking:
1. We introduce a lightweight, cross-platform python wrapper script (`scripts/run_with_status.py`) that executes the harness process and writes its final exit code to a status file.
2. The trigger script polls this status file to deterministically resolve success/failure.
3. Dry-run signature tracking is restricted to memory/temp scopes to prevent persistent signature updates or state pollution.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — File bridge protocol governance (config/governance/gov-file-bridge-authority-001.md)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Implementation proposals must cite specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verified proposals must have spec-to-test mapping
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Placement contract for application isolation
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — Trigger-harness dispatcher co-existence rules.
- `REQ-HARNESS-REGISTRY-001` — Harness registration and metadata tracking rules.
- `DELIB-S509-B1-B5-TRIAGE` — S509 triage deliberation.

## Implementation Scope

- **Project:** `PROJECT-GTKB-PLATFORM-CORE`
- **Work Item:** `WI-4328`

## target_paths

- `scripts/cross_harness_bridge_trigger.py`
- `scripts/run_with_status.py`
- `tests/framework/test_dispatch_state_recovery.py`

## Requirement Sufficiency

Existing requirements sufficient

## Deliverables

### 4.1 Process Execution Wrapper (`scripts/run_with_status.py`) [NEW]
A lightweight wrapper invoked as:
```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts/run_with_status.py <status_file_path> <harness_cmd> <args...>
```
It runs the subprocess, intercepts its exit code, writes it to `<status_file_path>` (e.g. `<state-dir>/runs/<dispatch_id>.exit_code`), and propagates the exit code.

### 4.2 Trigger Recovery Integration (`scripts/cross_harness_bridge_trigger.py`)
- Modifies the signature update logic to check the recipient's exit status via the wrapper-generated exit code file.
- Signature for `loyal-opposition` is updated **only** if the process exited with code `0`.
- Implements a retry delay check: if a retry is pending, wait at least `OLLAMA_RETRY_DELAY_SECONDS` (default: 300) since `updated_at` before spawning again.
- Implements failure-counter increment and circuit-breaker activation after `OLLAMA_MAX_RETRIES` (default: 3).
- Implements command-line argument `--reset-recipient <name>` to clear circuit breakers.
- Prevents dry-run mode from updating the persistent `last_dispatched_signature`.

### 4.3 Test Suite (`tests/framework/test_dispatch_state_recovery.py`) [NEW]
Tests dry-runs, wrapper status recording, failure counting, retry timing constraints, and circuit breaker tripping/reset.

## Specification-Derived Verification Plan

### Automated Tests
Run the trigger recovery test suite:
```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest tests/framework/test_dispatch_state_recovery.py -v
```

### Spec-to-Test Mapping

| Spec ID | Test File | Test Case(s) |
|---------|-----------|--------------|
| SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 | `tests/framework/test_dispatch_state_recovery.py` | `test_dry_run_does_not_mutate_state`, `test_circuit_breaker_active` |
| REQ-HARNESS-REGISTRY-001 | `tests/framework/test_dispatch_state_recovery.py` | `test_wrapper_records_exit_code`, `test_retry_delay_enforcement` |
