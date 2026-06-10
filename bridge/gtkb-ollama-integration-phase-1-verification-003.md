REVISED

# Implementation Proposal - Phase-1 Ollama Verification and Doctor Check (Child 3, REVISED)

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-1-verification
Version: 003 (REVISED; addresses NO-GO at -002)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-05 UTC

author_identity: Claude Code
author_harness_id: B
author_session_context_id: cb8d1960-2984-4042-b76d-6a869cd0e16a
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4322
work_item_ids: [WI-4322, WI-4323]

target_paths: ["scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

## Summary

This is Child 3 of the Phase-1 Ollama integration umbrella (GO at
`bridge/gtkb-ollama-integration-phase-1-004.md`). It delivers two verification
surfaces preserving the owner-approved acceptance scope from DELIB-20260663 and
the active PAUTH.

REVISED to address Codex NO-GO at -002:
- **F1 (P1):** WI-4322 now includes live Ollama E2E round-trip when the server
  is available, bridge filing proof, author metadata verification, and
  ruff/pytest sanity — matching the owner-approved scope from AUQ#9.
- **F2 (P1):** WI-4323 now includes advertised-model verification against local
  Ollama's model list — matching the owner-approved scope from AUQ#10.
- **F3 (P2):** Doctor test path corrected from `tests/groundtruth_kb/` to
  `groundtruth-kb/tests/` (the package-native test tree).

1. **WI-4322** — `scripts/verify_ollama_dispatch.py`: an E2E verification
   script with two operational modes:
   - **Live mode** (default when Ollama is reachable): performs a round-trip
     dispatch through `call_ollama_chat`, verifies bridge filing evidence,
     validates author metadata, and runs ruff check + pytest sanity.
   - **Guard-only mode** (fallback when Ollama is unreachable): exercises the
     guard-adapter pipeline with mocked model responses to verify destructive
     Bash denial, formal-artifact mutation denial, and out-of-root rejection.
   Guard-only fixtures are additive evidence, not replacements for live E2E.

2. **WI-4323** — `_check_ollama_harness` doctor check in
   `groundtruth-kb/src/groundtruth_kb/project/doctor.py`: a health check with
   four layers: routing config parse, registry consistency,
   reachability (WARN when unreachable), and advertised-model verification.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this REVISED bridge entry filed under `bridge/` per protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governed specs cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests enumerated in verification plan.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active PAUTH covers WI-4322 and WI-4323.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — all target_paths fall within the GO'd umbrella envelope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — project PAUTH cites approved framing specs.
- `GOV-STANDING-BACKLOG-001` — WI-4322 and WI-4323 are canonical MemBase backlog rows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target files under `E:\GT-KB`; verify script tests out-of-root rejection.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — verification script and doctor check are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — E2E script turns guard-adapter safety contract into executable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — terminal state requires Loyal Opposition verification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — doctor check reads routing config and harness-registry state through canonical paths.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — guard-adapter delegation pattern tested by E2E script mirrors hook parity contract.

## Prior Deliberations

- `DELIB-20260663` — 12-AUQ owner decision pass. AUQ#9 selected "round-trip +
  bridge filing + ruff/pytest" for Phase 1 E2E scope. AUQ#10 selected "doctor
  reachability, advertised-model, and registry checks."
- `DELIB-20260679` — umbrella GO context after the guard-adapter contract.
- `DELIB-20260680` — parent umbrella NO-GO requiring fail-closed guard-adapter.
- `bridge/gtkb-ollama-integration-phase-1-shim-012.md` — Child 2 VERIFIED.
  Explicitly states "no live Ollama server round-trip was run because it remains
  Child 3 scope."
- `bridge/gtkb-ollama-integration-phase-1-verification-002.md` — NO-GO with
  three findings: scope narrowing away from live E2E (P1), omitted
  advertised-model doctor check (P1), wrong test tree path (P2).

## NO-GO -002 Response

### F1 (P1): WI-4322 E2E scope restored to live dispatch evidence

**Before:** The proposal described only mocked guard-adapter fixtures without
live Ollama round-trip, bridge filing proof, or author metadata verification.

**After:** The verify script now operates in two modes:

- **Live mode** (triggered when Ollama endpoint responds at configured URL):
  1. Sends a `call_ollama_chat` round-trip with a simple prompt ("What is 2+2?")
     through the full shim pipeline.
  2. Asserts the response contains a non-empty model reply.
  3. Verifies author metadata (`GTKB_AUTHOR_*` env vars) are set correctly
     during the dispatch.
  4. Proves bridge filing capability by calling the bridge-propose helper's
     dry-run path (no actual INDEX mutation).
  5. Runs `ruff check` and `ruff format --check` on `scripts/ollama_harness.py`.
  6. Runs `pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short`.

- **Guard-only mode** (fallback when endpoint is unreachable):
  1. Mocked guard-adapter denial fixtures (destructive Bash, formal-artifact
     mutation, out-of-root) — preserved as additive evidence.
  2. Outputs a clear `"mode": "guard_only"` vs `"mode": "live"` field in the
     evidence JSON.
  3. The skip reason is logged so verification reviewers can distinguish
     "no Ollama installed" from "E2E passed."

### F2 (P1): WI-4323 doctor check now includes advertised-model verification

**Before:** Doctor check had 3 layers (routing parse, registry consistency,
reachability) but omitted model availability.

**After:** Layer 4 added:

**Layer 4 — Advertised-model verification (best-effort, gated on reachability):**
- If Layer 3 reports the Ollama endpoint is reachable, queries
  `GET /api/tags` to retrieve the list of locally available models.
- Reads the configured routing model(s) from `.ollama/routing.toml`
  `[routes.*.model]` entries.
- If any configured model is NOT in the local Ollama model list → WARN
  ("Model '{model}' configured in routing.toml but not available locally;
  run `ollama pull {model}` to install").
- If all configured models are available → enhances PASS message with
  model count.
- If the `/api/tags` endpoint is unreachable (Layer 3 already WARN'd) →
  model check is skipped with no additional severity escalation.

### F3 (P2): Doctor test path corrected

**Before:** `tests/groundtruth_kb/test_doctor_ollama.py` — non-existent
root `tests/` tree.

**After:** `groundtruth-kb/tests/test_doctor_ollama.py` — the package-native
test tree where existing doctor tests live.

## Owner Decisions / Input

No new owner decisions required. This REVISED proposal preserves the active
PAUTH and the 12-AUQ owner decision pass. The scope corrections restore the
owner-approved E2E and doctor acceptance scopes rather than narrowing them.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are:
- Umbrella GO `-004` §Child 3: "E2E fixture proves destructive Bash denied;
  E2E fixture proves formal-artifact/MemBase mutation blocked without packets;
  Doctor WARN when unreachable, FAIL on config/registry inconsistency."
- `DELIB-20260663` AUQ#9: "round-trip + bridge filing + ruff/pytest."
- `DELIB-20260663` AUQ#10: "doctor reachability, advertised-model, and registry
  checks."
- Guard-adapter contract from umbrella `-003` §Guard-Adapter Contract.

## Design

### WI-4322: `scripts/verify_ollama_dispatch.py`

The E2E verification script follows the established `scripts/verify_*.py`
pattern. It supports two operational modes determined at runtime:

**Startup probe:** Before any fixture, the script sends a lightweight HTTP GET
to the configured Ollama endpoint (default `http://localhost:11434`, override
via `--endpoint`). If the endpoint responds, live mode activates; otherwise
guard-only mode activates.

#### Live Mode (Ollama available)

**Fixture L1 — Round-trip dispatch:**
- Calls `call_ollama_chat` from `scripts/ollama_harness.py` with a simple
  prompt, the configured model, and no tool definitions.
- Asserts the response contains a non-empty `message.content` field.
- Records the model name, response length, and latency in evidence JSON.

**Fixture L2 — Author metadata verification:**
- During the dispatch, captures the `GTKB_AUTHOR_*` environment variables
  that the shim sets (`GTKB_AUTHOR_HARNESS_ID`, `GTKB_AUTHOR_SESSION_ID`,
  `GTKB_AUTHOR_MODEL`, `GTKB_AUTHOR_HARNESS_TYPE`, `GTKB_AUTHOR_HARNESS_NAME`).
- Asserts all five are non-empty and `GTKB_AUTHOR_HARNESS_TYPE == "ollama"`.

**Fixture L3 — Bridge filing proof (dry-run):**
- Invokes the bridge-propose helper's draft-assembly path to verify the
  Ollama harness can produce a well-formed bridge proposal body without
  actually mutating `bridge/INDEX.md`.
- Alternatively, if the helper has no dry-run mode, creates a temp file
  following the bridge naming convention and validates its structure.
- Records the draft path in evidence.

**Fixture L4 — Code quality sanity:**
- Runs `ruff check scripts/ollama_harness.py` (exit 0 expected).
- Runs `ruff format --check scripts/ollama_harness.py` (exit 0 expected).
- Runs `pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short`
  (all pass expected).
- Records pass/fail and output snippets in evidence.

#### Guard-Only Mode (Ollama unreachable)

**Fixture G1 — Destructive Bash denial:**
- Mocks `call_ollama_chat` to return a model response requesting `rm -rf /`.
- Asserts the guard adapter intercepts and denies.

**Fixture G2 — Formal-artifact mutation denial:**
- Mocks a Write to `.groundtruth/formal-artifact-approvals/` without packet.
- Asserts the guard adapter blocks the write.

**Fixture G3 — Out-of-root path rejection:**
- Mocks a Write targeting `C:\Windows\System32\test.txt`.
- Asserts root-boundary guard rejects.

**Output:** Structured JSON evidence to `.gtkb-state/ollama-verification/`
with `mode`, per-fixture pass/fail, timestamps, and diagnostic messages.

### WI-4323: `_check_ollama_harness` doctor check

Registered in `run_doctor()` within the `p.includes_bridge` block. Four layers:

**Layer 1 — Routing config parse:**
- Reads `.ollama/routing.toml`. If missing and no harness D in registry →
  PASS (Ollama not configured). If present, validates `schema_version`,
  `default_route`, and at least one model entry. Parse error → FAIL.

**Layer 2 — Registry consistency:**
- Routing TOML exists but no harness D → WARN.
- Harness D registered but routing TOML missing → FAIL.

**Layer 3 — Ollama reachability (best-effort):**
- HTTP GET to configured endpoint (default `http://localhost:11434`). Timeout 3s.
- Unreachable → WARN. Reachable → augments PASS with Ollama version.

**Layer 4 — Advertised-model verification (gated on Layer 3 reachability):**
- Queries `GET /api/tags` to retrieve locally available models.
- Reads configured model(s) from `.ollama/routing.toml` route entries.
- Any configured model absent from local Ollama → WARN with install guidance.
- All configured models available → enhances PASS with model count.
- Layer 3 unreachable → skip model check (no additional severity).

**Test file:** `groundtruth-kb/tests/test_doctor_ollama.py` — unit tests with
mocked filesystem and HTTP:
- No routing config, no harness D → PASS
- Valid config, harness D, endpoint unreachable → WARN
- Valid config, harness D, endpoint reachable, model present → PASS+model
- Valid config, harness D, endpoint reachable, model absent → WARN+install
- Malformed routing config → FAIL
- Routing config present, no harness D → WARN
- Harness D registered, no routing config → FAIL

**Additional test file:** `platform_tests/scripts/test_verify_ollama_dispatch.py`
— tests for both live mode (mocked HTTP responses) and guard-only mode (mocked
`call_ollama_chat`).

## Risk and Rollback

**Risk:** Low. The verify script writes only evidence JSON to `.gtkb-state/`.
The doctor check is additive (one `_check_*` function + registration). Neither
modifies Ollama runtime behavior, source code, or guard scripts.

**Rollback:** Remove the verify script, remove the doctor check function and
its registration line, remove the test files. No schema, config, or data
migration.

## Pre-Filing Preflight Subsection

Commands run before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification
```

## Specification-Derived Verification Plan

| Requirement / GO constraint | Planned test or command | Expected result |
|---|---|---|
| WI-4322 E2E live round-trip (AUQ#9) | `python scripts/verify_ollama_dispatch.py --json` (live mode when available) | PASS: model response received, evidence JSON written |
| WI-4322 E2E author metadata | `python scripts/verify_ollama_dispatch.py --json` live L2 fixture | PASS: all 5 GTKB_AUTHOR vars non-empty, harness_type=ollama |
| WI-4322 E2E bridge filing proof | `python scripts/verify_ollama_dispatch.py --json` live L3 fixture | PASS: draft bridge body well-formed |
| WI-4322 E2E ruff/pytest sanity | `python scripts/verify_ollama_dispatch.py --json` live L4 fixture | PASS: ruff clean, tests pass |
| WI-4322 guard destructive Bash denied | `pytest platform_tests/scripts/test_verify_ollama_dispatch.py -k destructive` | PASS: guard denies rm -rf |
| WI-4322 guard formal-artifact blocked | `pytest platform_tests/scripts/test_verify_ollama_dispatch.py -k formal_artifact` | PASS: guard blocks unapproved write |
| WI-4322 guard out-of-root rejected | `pytest platform_tests/scripts/test_verify_ollama_dispatch.py -k out_of_root` | PASS: root-boundary rejects |
| WI-4323 doctor WARN when unreachable | `pytest groundtruth-kb/tests/test_doctor_ollama.py -k unreachable` | PASS: status=warning |
| WI-4323 doctor FAIL on config error | `pytest groundtruth-kb/tests/test_doctor_ollama.py -k malformed` | PASS: status=fail |
| WI-4323 doctor PASS when not configured | `pytest groundtruth-kb/tests/test_doctor_ollama.py -k no_config` | PASS: status=pass |
| WI-4323 doctor registry inconsistency | `pytest groundtruth-kb/tests/test_doctor_ollama.py -k registry` | PASS: appropriate status |
| WI-4323 doctor advertised-model present | `pytest groundtruth-kb/tests/test_doctor_ollama.py -k model_present` | PASS: status=pass with model info |
| WI-4323 doctor advertised-model absent | `pytest groundtruth-kb/tests/test_doctor_ollama.py -k model_absent` | PASS: status=warning with install guidance |
| Code quality lint | `ruff check scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/project/doctor.py` | All checks passed |
| Code quality format | `ruff format --check scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/project/doctor.py` | Already formatted |

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `scripts/verify_ollama_dispatch.py` | CREATE | E2E verification (live + guard-only modes) (WI-4322) |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | MODIFY | Add `_check_ollama_harness` 4-layer check (WI-4323) |
| `groundtruth-kb/tests/test_doctor_ollama.py` | CREATE | Doctor check unit tests including model verification (WI-4323) |
| `platform_tests/scripts/test_verify_ollama_dispatch.py` | CREATE | Verify script tests for both live and guard-only modes (WI-4322) |

Recommended commit type: feat

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
