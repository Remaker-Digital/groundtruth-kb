NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T15-51-27Z-loyal-opposition-a84fc7
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex auto-dispatch; workspace-write; approval-policy never

# Loyal Opposition Verification - Phase-1 Ollama Shim And Routing Child

bridge_kind: verification_verdict
Document: gtkb-ollama-integration-phase-1-shim
Version: 010
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-ollama-integration-phase-1-shim-009.md
Verdict: NO-GO
Recommended commit type: feat

## Verdict

NO-GO.

The implementation report satisfies the bridge and clause preflight floor, and
the shim has useful guard, routing, author-metadata, and code-quality evidence.
However, the default runtime chat path constructs the Ollama URL incorrectly:
`run_tool_loop()` passes an endpoint that already includes `/api/chat` into
`call_ollama_chat()`, and `call_ollama_chat()` appends `/api/chat` again. A
real default CLI invocation would call `/api/chat/api/chat`, while the mocked
test asserts the already-appended URL and therefore does not catch the defect.

This blocks `VERIFIED` for WI-4319 because the child claims a stdlib Ollama
`/api/chat` tool loop and CLI, not only schema construction.

## Review Scope

- Read live `bridge/INDEX.md`; latest status was `NEW` at
  `bridge/gtkb-ollama-integration-phase-1-shim-009.md`.
- Read the full thread chain `-001` through `-009` via the bridge show-thread
  helper and direct reads of the operative report.
- Ran mandatory applicability and ADR/DCL clause preflights on the indexed
  operative `-009` report.
- Searched the Deliberation Archive for the Ollama Phase 1 owner decisions and
  fail-closed guard-adapter context.
- Inspected `scripts/ollama_harness.py`, `.ollama/routing.toml`, and
  `platform_tests/scripts/test_ollama_harness.py`.
- Ran ruff lint, ruff format, and CLI help checks that do not require pytest.
- Inspected the real hook output contract for allow-case JSON compatibility.

## Prior Deliberations

- `DELIB-20260663` records the 12-AUQ owner decision pass for Phase 1,
  including the Python shim, static `.ollama/routing.toml`, Qwen model, full
  six-tool subset, E2E expectations, and doctor scope.
- `DELIB-20260680` / parent umbrella NO-GO context required the fail-closed
  local guard-adapter contract before child approval.
- `DELIB-20260679` records the parent umbrella GO after the guard-adapter
  contract was added.
- `bridge/gtkb-ollama-integration-phase-1-foundation-012.md` records the
  predecessor foundation child as VERIFIED.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` remains relevant to
  the future live localhost Ollama invocation boundary, though this child did
  not run live model dispatch.

## Findings

### F1 - P1 - Default chat path double-appends `/api/chat`

Observation:
`call_ollama_chat()` builds `url = endpoint.rstrip("/") + "/api/chat"`, but
`run_tool_loop()` calls `chat(endpoint.rstrip("/") + "/api/chat", payload,
timeout)`. When `chat_func` is not injected, the default `chat` is
`call_ollama_chat`, so the live default path becomes:

```text
<endpoint>/api/chat/api/chat
```

Evidence:

- `scripts/ollama_harness.py:232` defines `call_ollama_chat(...)`.
- `scripts/ollama_harness.py:235` appends `/api/chat` inside
  `call_ollama_chat`.
- `scripts/ollama_harness.py:617` defines `run_tool_loop(...)`.
- `scripts/ollama_harness.py:637` passes
  `endpoint.rstrip("/") + "/api/chat"` into `chat(...)`.
- `platform_tests/scripts/test_ollama_harness.py:123` injects a fake `chat`
  function, and `platform_tests/scripts/test_ollama_harness.py:138` asserts the
  fake received `http://ollama.test/api/chat`. That validates the injected
  fake-call URL, not the default `call_ollama_chat` behavior.
- `bridge/gtkb-ollama-integration-phase-1-shim-009.md:34` claims a stdlib
  Ollama `/api/chat` tool loop and CLI; `-009.md:87` claims `/api/chat` payload
  construction; `-009.md:115-116` maps CLI and mocked `/api/chat` coverage to
  WI-4319.

Deficiency rationale:
The approved Child 2 scope explicitly owns the mocked chat-loop and local CLI
framework, while Child 3 owns live server round-trip and bridge-filing proof.
Even within that boundary, the default callable path must be internally
consistent. A CLI using the default `call_ollama_chat` cannot reach Ollama's
documented `/api/chat` endpoint with the current URL construction.

Impact:
The shim would fail the first real default dispatch attempt or require callers
to compensate for an internal double-append bug. The current tests can pass
while the shipped CLI path is wrong, so the implementation report's
spec-derived verification does not cover the load-bearing default behavior.

Required action:

1. Choose a single URL-ownership contract:
   - Preferred: `run_tool_loop()` passes the base endpoint to `chat(...)`, and
     `call_ollama_chat()` remains responsible for appending `/api/chat`.
   - Acceptable alternative: `call_ollama_chat()` accepts a complete chat URL,
     is renamed or documented accordingly, and the CLI constructs that URL once.
2. Add a regression test that exercises the default `call_ollama_chat` path,
   not only an injected fake. A small monkeypatch around `urllib.request.urlopen`
   or a local fake HTTP handler is enough; assert exactly one `/api/chat`.
3. Rerun and report the focused pytest, ruff check, ruff format, and CLI help
   commands after the fix.

Option rationale:
Fixing `run_tool_loop()` to pass the base endpoint is the smaller and clearer
change because `call_ollama_chat()` already owns URL construction.

## Required Revisions

1. Fix the `/api/chat/api/chat` URL composition defect in
   `scripts/ollama_harness.py`.
2. Add a regression test that exercises the default `call_ollama_chat()` path,
   not only an injected fake callback.
3. Rerun and report the focused pytest, ruff check, ruff format, CLI help, and
   bridge preflight commands after the fix.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `uv run --with pytest --with pytest-timeout pytest platform_tests\scripts\test_ollama_harness.py -q --tb=short` | yes | PASS: 26 passed, but coverage misses F1 |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Direct monkeypatch probe of `call_ollama_chat("http://localhost:11434/api/chat", ...)` URL construction | yes | FAIL: captured `http://localhost:11434/api/chat/api/chat` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` read before writing this verdict; show-thread drift check after write | yes | PASS: latest `NO-GO`, `drift: []` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path inspection for `scripts/ollama_harness.py`, `.ollama/routing.toml`, and `platform_tests/scripts/test_ollama_harness.py` | yes | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Guard output contract inspection and existing guard-adapter tests | yes | PASS for inspected guard behavior; not the blocking issue |

## Positive Confirmations

- Applicability preflight on the operative report passes with
  `missing_required_specs: []` and `missing_advisory_specs: []`.
- ADR/DCL clause preflight reports zero must-apply evidence gaps and zero
  blocking gaps.
- `.ollama/routing.toml` has `schema_version = 1`, default route
  `qwen-coder-14b`, model id `qwen2.5-coder:14b-instruct-q4_K_M`, and the full
  canonical six-tool `allowed_tools` list.
- `groundtruth-kb\.venv\Scripts\ruff.exe check scripts\ollama_harness.py
  platform_tests\scripts\test_ollama_harness.py ...` returned
  `All checks passed!`.
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check ...` returned
  `4 files already formatted`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --help`
  exited 0 and lists `--prompt`, `--model`, `--endpoint`, `--max-turns`, and
  `--timeout`.
- Real hook inspection confirms allow-case guard scripts emit JSON `{}` or a
  structured deny object, matching the shim's expected guard output contract.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:25e655d54f5dd7eb74a892a2ab714033afb6d7dca243519e19f30353d9feb346`
- bridge_document_name: `gtkb-ollama-integration-phase-1-shim`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-shim-009.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-shim-009.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-shim`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-shim-009.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Verification Limits

- The report's venv pytest command could not be rerun verbatim because
  `groundtruth-kb\.venv\Scripts\python.exe -m pytest` resolves to a malformed
  pytest installation (`pytest.__file__` and `pytest.__version__` are `None`)
  and no `pytest.exe` exists in either checked venv.
- Focused pytest was rerun through `uv run --with pytest --with
  pytest-timeout` and passed with 26 tests. This does not clear F1 because the
  passing suite does not cover the default production URL-composition path.
- No live Ollama server round-trip was run; that remains Child 3 scope as
  stated in the approved GO and the implementation report.

## Commands Executed

```powershell
Get-Content .\bridge\INDEX.md
$env:PYTHONIOENCODING='utf-8'; python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-ollama-integration-phase-1-shim --format json --preview-lines 0
$env:PYTHONIOENCODING='utf-8'; python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
$env:PYTHONIOENCODING='utf-8'; python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness.py -q --tb=short
uv run --with pytest --with pytest-timeout pytest platform_tests\scripts\test_ollama_harness.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py
groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --help
```

Observed results: bridge helper drift check passed; preflights passed; venv
pytest command failed before collection; `uv` pytest passed with 26 tests; ruff
passed; CLI help passed. The direct monkeypatch probe captured the blocking
`/api/chat/api/chat` URL.

## Opportunity Radar

The material deterministic-service cue is a narrow regression-test gap, not a
new automation project: the default chat URL path needs a test that exercises
the production callable rather than an injected fake. No separate advisory is
filed from this selected-entry dispatch.

## Owner Action Required

None. Prime Builder can file a REVISED implementation report after fixing F1
and rerunning the focused verification gates.

File bridge scan contribution: 1 selected actionable entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
