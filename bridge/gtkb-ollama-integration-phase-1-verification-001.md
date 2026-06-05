NEW

# Implementation Proposal - Phase-1 Ollama Verification and Doctor Check (Child 3)

bridge_kind: implementation_proposal
Document: gtkb-ollama-integration-phase-1-verification
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4322
work_item_ids: [WI-4322, WI-4323]

target_paths: ["scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "tests/groundtruth_kb/test_doctor_ollama.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

## Summary

This is Child 3 of the Phase-1 Ollama integration umbrella (GO at `bridge/gtkb-ollama-integration-phase-1-004.md`). It delivers two verification surfaces:

1. **WI-4322** — `scripts/verify_ollama_dispatch.py`: an E2E verification script that proves the Ollama shim's guard-adapter pipeline correctly denies destructive Bash commands and blocks formal-artifact/MemBase mutations without matching approval packets. This is the acceptance-test evidence layer for the guard contract established in Child 2 (VERIFIED at `-012`).

2. **WI-4323** — `_check_ollama_harness` doctor check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`: a health check reporting WARN when local Ollama is unreachable, and FAIL on `.ollama/routing.toml` parse errors or harness-registry inconsistencies (e.g., harness D registered but routing config missing, or vice versa).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this append-only NEW bridge entry will be filed under `bridge/` and a `NEW: bridge/gtkb-ollama-integration-phase-1-verification-001.md` line inserted at the top of the document entry in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governed specs are cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests are enumerated in the verification plan below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the active PAUTH covers WI-4322 and WI-4323.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — all target_paths fall within the GO'd umbrella envelope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — the project PAUTH cites the approved framing specs.
- `GOV-STANDING-BACKLOG-001` — WI-4322 and WI-4323 are canonical MemBase backlog rows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target files stay under `E:\GT-KB`; the verify script tests out-of-root rejection.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the verification script and doctor check are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the E2E script turns the guard-adapter safety contract into executable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — terminal state requires Loyal Opposition verification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the doctor check reads `.ollama/routing.toml` and harness-registry state through canonical paths.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the guard-adapter delegation pattern tested by the E2E script mirrors the hook parity contract.

## Prior Deliberations

- `DELIB-20260663` — 12-AUQ owner decision pass for Phase 1. Covers the E2E verification scope ("scripts/verify_ollama_dispatch.py exercises destructive-gate and formal-artifact denial"), doctor check scope ("_check_ollama_harness: WARN when unreachable, FAIL on config inconsistency"), and the Qwen model, six-tool subset, and guard-adapter contract.
- `DELIB-20260679` — umbrella GO context after the guard-adapter contract was added.
- `DELIB-20260680` — parent umbrella NO-GO context requiring the fail-closed guard-adapter contract before child approval.
- `bridge/gtkb-ollama-integration-phase-1-foundation-012.md` — Child 1 VERIFIED (terminal).
- `bridge/gtkb-ollama-integration-phase-1-shim-012.md` — Child 2 VERIFIED (terminal).

## Owner Decisions / Input

No new owner decisions required. This proposal is scoped within the active PAUTH and the 12-AUQ owner decision pass captured in `DELIB-20260663`. The umbrella GO at `-004` explicitly authorizes child-bridge filing for this scope.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are:
- Umbrella GO `-004` §Child 3: "E2E fixture proves destructive Bash denied; E2E fixture proves formal-artifact/MemBase mutation blocked without packets; Doctor WARN when unreachable, FAIL on config/registry inconsistency."
- `DELIB-20260663` owner decisions on doctor scope and E2E verification scope.
- Guard-adapter contract from umbrella `-003` §Guard-Adapter Contract.

## Design

### WI-4322: `scripts/verify_ollama_dispatch.py`

The E2E verification script follows the established `scripts/verify_*.py` pattern (cf. `verify_antigravity_dispatch.py`). It exercises the Ollama shim's guard pipeline WITHOUT requiring a live Ollama server by mocking `call_ollama_chat` to return pre-canned tool-call responses.

**Fixture 1 — Destructive Bash denial:**
- Mocks `call_ollama_chat` to return a model response requesting execution of `rm -rf /` via the Bash tool.
- Asserts the guard adapter intercepts and denies the request (fail-closed).
- Verifies `run_tool_loop` returns the denial message, not an executed result.

**Fixture 2 — Formal-artifact mutation denial:**
- Mocks `call_ollama_chat` to return a model response requesting a Write to a `.groundtruth/formal-artifact-approvals/` path without a matching approval packet.
- Asserts the guard adapter blocks the write.
- Verifies the tool-loop response includes the guard denial.

**Fixture 3 — Out-of-root path rejection:**
- Mocks a Write tool call targeting `C:\Windows\System32\test.txt`.
- Asserts the root-boundary guard rejects the path.
- Verifies the rejection is not normalized back into scope.

**Output:** Structured JSON evidence to `.gtkb-state/ollama-verification/` with pass/fail per fixture, timestamps, and guard denial messages.

### WI-4323: `_check_ollama_harness` doctor check

Registered in `run_doctor()` within the `p.includes_bridge` block (alongside other infrastructure checks). The check performs three layers:

**Layer 1 — Routing config parse:**
- Reads `.ollama/routing.toml`. If missing and no harness D in registry → PASS (Ollama not configured). If present, validates `schema_version`, `default_route`, and at least one model entry. Parse error → FAIL.

**Layer 2 — Registry consistency:**
- If `.ollama/routing.toml` exists but no harness D in `harness-state/harness-registry.json` → WARN ("routing config present but no Ollama harness registered").
- If harness D registered but `.ollama/routing.toml` missing → FAIL ("Ollama harness registered but routing config missing").

**Layer 3 — Ollama reachability (best-effort):**
- Attempts a lightweight HTTP GET to the configured endpoint (default `http://localhost:11434`). Timeout 3s.
- Unreachable → WARN ("Ollama endpoint unreachable at {endpoint}; local model dispatch will fail"). This is informational, not blocking, per umbrella GO constraint.
- Reachable → augments the PASS message with the Ollama version if returned.

**Test file:** `tests/groundtruth_kb/test_doctor_ollama.py` — unit tests for `_check_ollama_harness` with mocked filesystem and HTTP. Tests:
- No routing config, no harness D → PASS
- Valid routing config, harness D present, endpoint unreachable → WARN
- Valid routing config, harness D present, endpoint reachable → PASS with version
- Malformed routing config → FAIL
- Routing config present, no harness D → WARN
- Harness D registered, no routing config → FAIL

**Additional test file:** `platform_tests/scripts/test_verify_ollama_dispatch.py` — unit tests for the verify script's fixture execution against mocked guard responses.

## Risk and Rollback

**Risk:** Low. The verify script is read-only (writes only evidence JSON to `.gtkb-state/`). The doctor check is additive (a new `_check_*` function + one `checks.append()` line in `run_doctor()`). Neither modifies Ollama runtime behavior, source code, or guard scripts.

**Rollback:** Remove the verify script, remove the doctor check function and its registration line, remove the test files. No schema, config, or data migration involved.

## Pre-Filing Preflight Subsection

Commands run before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification --content-file .gtkb-state/bridge-revisions/drafts/gtkb-ollama-integration-phase-1-verification-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification --content-file .gtkb-state/bridge-revisions/drafts/gtkb-ollama-integration-phase-1-verification-001.md
```

## Specification-Derived Verification Plan

| Requirement / GO constraint | Planned test or command | Expected result |
|---|---|---|
| WI-4322 E2E destructive Bash denied | `pytest platform_tests/scripts/test_verify_ollama_dispatch.py -k destructive` | PASS: guard adapter denies `rm -rf /` |
| WI-4322 E2E formal-artifact mutation blocked | `pytest platform_tests/scripts/test_verify_ollama_dispatch.py -k formal_artifact` | PASS: guard adapter blocks unapproved write |
| WI-4322 E2E out-of-root rejected | `pytest platform_tests/scripts/test_verify_ollama_dispatch.py -k out_of_root` | PASS: root-boundary guard rejects path |
| WI-4323 doctor WARN when unreachable | `pytest tests/groundtruth_kb/test_doctor_ollama.py -k unreachable` | PASS: status=warning |
| WI-4323 doctor FAIL on config error | `pytest tests/groundtruth_kb/test_doctor_ollama.py -k malformed` | PASS: status=fail |
| WI-4323 doctor PASS when not configured | `pytest tests/groundtruth_kb/test_doctor_ollama.py -k no_config` | PASS: status=pass |
| WI-4323 doctor registry inconsistency | `pytest tests/groundtruth_kb/test_doctor_ollama.py -k registry` | PASS: appropriate status per scenario |
| Code quality lint | `ruff check scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/project/doctor.py` | All checks passed |
| Code quality format | `ruff format --check scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/project/doctor.py` | Already formatted |
| Target-path scope | `python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification --candidate-paths <all-modified> --json` | verdict: in_scope |

## Files Changed

This proposal adds or modifies:

| File | Action | Purpose |
|---|---|---|
| `scripts/verify_ollama_dispatch.py` | CREATE | E2E verification script (WI-4322) |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | MODIFY | Add `_check_ollama_harness` + registration (WI-4323) |
| `tests/groundtruth_kb/test_doctor_ollama.py` | CREATE | Doctor check unit tests (WI-4323) |
| `platform_tests/scripts/test_verify_ollama_dispatch.py` | CREATE | Verify script unit tests (WI-4322) |

Recommended commit type: feat

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
