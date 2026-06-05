REVISED

# Prime Revision - Phase-1 Ollama Shim Chat URL Ownership Fix

bridge_kind: implementation_report_revision
Document: gtkb-ollama-integration-phase-1-shim
Version: 011
Author: Prime Builder (Codex, harness A)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-ollama-integration-phase-1-shim-010.md

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e986b-9e40-77c3-8e68-3abd2796a881
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex API; Keep Working PB automation; workspace-write; approval-policy never

Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4319
work_item_ids: [WI-4319, WI-4320, WI-4321]

implementation_authorization_packet: sha256:802e186edb09f3ca1b8fb2054581125c22788b5d38ae59db6abb91b2eef35993
target_paths: ["scripts/ollama_harness.py", ".ollama/routing.toml", "platform_tests/scripts/test_ollama_harness.py"]
Recommended commit type: fix

## Revision Claim

This revision fixes the single blocking finding in `bridge/gtkb-ollama-integration-phase-1-shim-010.md`.

`run_tool_loop()` now passes the base endpoint to the chat callable. `call_ollama_chat()` remains the sole owner of appending `/api/chat`, so the default CLI path posts to exactly `<endpoint>/api/chat` instead of `<endpoint>/api/chat/api/chat`.

The revision also adds a regression test that exercises the default `call_ollama_chat()` path by monkeypatching `urllib.request.urlopen` and asserting the exact request URL.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this append-only `REVISED` bridge entry will be filed under `bridge/` and the helper will insert the `REVISED: bridge/gtkb-ollama-integration-phase-1-shim-011.md` line at the top of the document entry in `bridge/INDEX.md` without deleting or rewriting prior versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governed specs are carried forward from the GO'd proposal and implementation report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this revision includes spec-to-test mapping and executed evidence for the corrected default path.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the fix used the active implementation authorization packet named above.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - changed paths remain inside the GO'd target path envelope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the project PAUTH cites the approved framing specs and includes WI-4319/WI-4320/WI-4321.
- `GOV-STANDING-BACKLOG-001` - WI-4319, WI-4320, and WI-4321 are canonical MemBase backlog rows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files stay inside `E:\GT-KB`; path handling remains project-root bounded.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the shim, tests, and bridge revision are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the correction turns LO verification feedback into durable source/test evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal state still requires Loyal Opposition verification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the default runtime path now matches the single source of URL construction in `call_ollama_chat()`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - guard delegation and fail-closed hook behavior remain unchanged.

## Prior Deliberations

- `DELIB-20260663` records the 12-AUQ owner decision pass for Phase 1, including the Python shim, static `.ollama/routing.toml`, Qwen model, full six-tool subset, E2E expectations, and doctor scope.
- `DELIB-20260680` / parent umbrella NO-GO context required the fail-closed local guard-adapter contract before child approval.
- `DELIB-20260679` records the parent umbrella GO after the guard-adapter contract was added.
- `bridge/gtkb-ollama-integration-phase-1-foundation-012.md` records the predecessor foundation child as VERIFIED.

## Owner Decisions / Input

No new owner input was requested or required. This revision is a narrow defect correction inside the already-approved Child 2 scope and active PAUTH.

## Findings Addressed

### F1 - P1 - Default chat path double-appends `/api/chat`

Response: fixed.

Changes made:

- `scripts/ollama_harness.py`: changed `run_tool_loop()` to pass `endpoint` directly to the chat callable instead of pre-appending `/api/chat`.
- `platform_tests/scripts/test_ollama_harness.py`: updated the injected-chat assertion to expect the base endpoint and added `test_default_tool_loop_calls_single_chat_endpoint`, which monkeypatches `urllib.request.urlopen` and asserts exactly `http://ollama.test/api/chat`.

This preserves the preferred URL ownership contract named in the NO-GO: `run_tool_loop()` passes the base endpoint, and `call_ollama_chat()` appends `/api/chat` exactly once.

## Scope Changes

No scope expansion. The fix changes only:

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

The routing config remains unchanged.

## Pre-Filing Preflight Subsection

Commands run before live filing:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim --content-file .gtkb-state\bridge-revisions\drafts\gtkb-ollama-integration-phase-1-shim-011.md
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim --content-file .gtkb-state\bridge-revisions\drafts\gtkb-ollama-integration-phase-1-shim-011.md
```

Observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit 0, zero must-apply evidence gaps, zero blocking gaps.

## Specification-Derived Verification

| Requirement / GO or NO-GO condition | Executed test or command | Observed result |
|---|---|---|
| WI-4319 default runtime posts to exactly one `/api/chat` endpoint | `$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-automation'; uv run --no-project --with pytest --with pytest-timeout python -m pytest platform_tests\scripts\test_ollama_harness.py -q --tb=short` and `test_default_tool_loop_calls_single_chat_endpoint` | `27 passed, 2 warnings in 1.77s`; regression asserted `http://ollama.test/api/chat`. |
| Injected chat callable receives the base endpoint contract | `test_tool_loop_posts_chat_payload_and_returns_final_text` | Test now asserts injected callable receives `http://ollama.test` while payload still contains model, messages, tools, and `stream: false`. |
| CLI remains available after the fix | `groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --help` | Exit 0; help lists `--prompt`, `--model`, `--endpoint`, `--max-turns`, and `--timeout`. |
| Code-quality lint gate | `groundtruth-kb\.venv\Scripts\ruff.exe check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py` | `All checks passed!` |
| Code-quality format gate | `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py` | `2 files already formatted` |
| Target-path scope | `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim --candidate-paths scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py --json` | `verdict: in_scope`; all two changed candidates are in scope, `.ollama/routing.toml` unused. |

The two pytest warnings are non-blocking environment warnings: root config includes `asyncio_mode` without the asyncio plugin in the uv test environment, and the pre-existing `.pytest_cache` path reports `[WinError 183] Cannot create a file when that file already exists`.

## Risk And Rollback

Risk is low. The change narrows URL ownership to one function and adds regression coverage for the default runtime path that was previously untested.

Rollback is straightforward: revert the two changed files from this revision. No schema, config, or data migration is involved.
