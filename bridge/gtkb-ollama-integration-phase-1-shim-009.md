NEW

# Prime Implementation Report - Phase-1 Ollama Shim And Routing Child

bridge_kind: implementation_report
Document: gtkb-ollama-integration-phase-1-shim
Version: 009
Author: Prime Builder (Codex, harness A)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-ollama-integration-phase-1-shim-008.md

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

implementation_authorization_packet: sha256:31cfe8dba48aad83d20ac9291642f2531a9e7882cf567edaf91e1d1721c5ee33
target_paths: ["scripts/ollama_harness.py", ".ollama/routing.toml", "platform_tests/scripts/test_ollama_harness.py"]

## Summary

Implemented the Child 2 Ollama Phase 1 shim approved by `GO:
bridge/gtkb-ollama-integration-phase-1-shim-008.md`.

The implemented scope is limited to:

- `scripts/ollama_harness.py` - stdlib-only Ollama `/api/chat` tool loop, routing loader, six-tool schema, local tool dispatch, root-boundary enforcement, guard adapter, and CLI.
- `.ollama/routing.toml` - static Phase 1 route for `qwen2.5-coder:14b-instruct-q4_K_M`.
- `platform_tests/scripts/test_ollama_harness.py` - focused mocked tests for routing, schemas, chat loop, guard ordering, root-boundary rejects, author metadata, and CLI help.

Child 3 remains responsible for live Ollama server round-trip / bridge-filing
E2E proof and doctor integration. This report does not claim those out-of-scope
items.

## Owner Decisions / Input

No new owner input was requested during implementation. The implementation uses
the already-recorded `DELIB-20260663` owner decisions carried by the GO'd
proposal:

- AUQ#1 selected a Python shim with direct Ollama HTTP integration.
- AUQ#2 selected static `.ollama/routing.toml`.
- AUQ#5 selected `qwen2.5-coder:14b-instruct-q4_K_M` as the Phase 1 MVP model.
- AUQ#6 selected the full parity tool subset: Read, Write, Edit, Grep, Glob, Bash.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is an append-only bridge entry and will be inserted into `bridge/INDEX.md` by the helper path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governed specs are carried forward from the GO'd proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report includes spec-to-test mapping and executed command evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation used the live implementation authorization packet named above.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - changed paths are source, config, and test files covered by the active project PAUTH.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the project PAUTH cites approved framing specs and includes WI-4319/WI-4320/WI-4321.
- `GOV-STANDING-BACKLOG-001` - WI-4319, WI-4320, and WI-4321 are canonical MemBase backlog rows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files stay inside `E:\GT-KB`; tool paths are rejected before mutation when they resolve outside the project root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the shim, routing config, tests, and bridge report are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation turns owner decisions and GO'd proposal scope into durable code/config/test artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal state still requires Loyal Opposition verification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - guard adapter invokes current hook scripts from `.claude/hooks/` instead of copying stale guard behavior.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - mutating model tools delegate to the existing GT-KB guard surfaces rather than bypassing harness parity expectations.

## Files Changed

- Added `scripts/ollama_harness.py`.
- Added `.ollama/routing.toml`.
- Added `platform_tests/scripts/test_ollama_harness.py`.

Unrelated dirty worktree state was left untouched, including
`applications/Agent_Red/CLAUDE.md` and untracked
`bridge/gtkb-isolation-018-agent-red-cutover-009.md`.

## Implementation Details

### WI-4319 - `scripts/ollama_harness.py`

Implemented a stdlib-only Python shim with:

- CLI flags `-p/--prompt`, `--model`, `--endpoint`, `--max-turns`, and `--timeout`.
- `load_routing_config()` and `resolve_model()` for `.ollama/routing.toml`.
- `/api/chat` payload construction with `model`, `messages`, `tools`, and `stream: false`.
- Ollama-compatible schemas for exactly Read, Write, Edit, Grep, Glob, and Bash.
- Tool-call loop that appends tool-result messages and repeats until final assistant text.
- Fail-closed handling for malformed responses, unknown tools, bad arguments, max-turn exhaustion, missing guard scripts, malformed guard output, nonzero guard exit, guard timeout, and guard denial/ask/checkpoint decisions.
- Root-boundary enforcement before guard invocation and before filesystem side effects.
- Local tool implementations for Read, Write, Edit, Grep, Glob, and Bash.

### WI-4320 - `.ollama/routing.toml`

Added `schema_version = 1`, one `models.qwen-coder-14b` entry with
`model_id = "qwen2.5-coder:14b-instruct-q4_K_M"`, full six-tool
`allowed_tools`, and `[routing].default_model = "qwen-coder-14b"`.

### WI-4321 - Author Metadata Injection

Implemented `set_author_metadata_env()` and uses it for guard subprocesses and
Bash execution. The injected metadata is:

- `GTKB_AUTHOR_IDENTITY = "Ollama D"`
- `GTKB_AUTHOR_HARNESS_ID = "D"`
- `GTKB_AUTHOR_MODEL = <routed model_id>`
- `GTKB_AUTHOR_MODEL_VERSION = <routed model_version>`
- `GTKB_AUTHOR_MODEL_CONFIGURATION = <endpoint, model, route, Phase 1 summary>`

## Specification-Derived Verification

| Requirement / GO condition | Executed test or command | Observed result |
|---|---|---|
| WI-4319 CLI accepts prompt/model/endpoint/max-turns flags | `groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --help` and `test_cli_help_executes` | Exit 0; help lists `--prompt`, `--model`, `--endpoint`, `--max-turns`, `--timeout`. |
| WI-4319 builds `/api/chat` payload with model/messages/tools/stream false | `test_run_tool_loop_posts_chat_payload_and_returns_final_text` | Mocked chat captured payload with selected model, messages, full six-tool schemas, and `stream is False`; loop returned final text. |
| WI-4319 exposes exactly canonical six-tool schema | `test_build_tool_schemas_exposes_only_allowed_tool_names` plus mocked chat-loop assertion | Tool names are canonical and schemas are function objects with `additionalProperties = False`. |
| WI-4319 fail-closed guard adapter before side effects | `test_write_invokes_guard_before_side_effect`; `test_guard_denial_blocks_write_side_effect`; `test_invoke_guard_adapter_passes_author_metadata_and_denies_block` | Guard called before file exists; denial prevents file creation; hook `decision: block` raises `OllamaHarnessError`. |
| WI-4319 root-boundary escape classes | `test_root_boundary_rejects_relative_absolute_and_symlink_escapes` | Relative traversal, absolute outside-root path, and symlink escape are rejected before guard invocation. |
| WI-4320 routing TOML schema | `test_load_routing_config_and_resolve_default_model`; `test_load_routing_config_rejects_noncanonical_tools` | Valid routing loads and resolves Qwen route; noncanonical tool name is rejected. |
| WI-4321 author metadata injection | `test_invoke_guard_adapter_passes_author_metadata_and_denies_block` | Guard subprocess env includes `GTKB_AUTHOR_IDENTITY`, `GTKB_AUTHOR_HARNESS_ID`, `GTKB_AUTHOR_MODEL`, and `GTKB_AUTHOR_MODEL_VERSION`. |
| Code-quality lint gate | `groundtruth-kb\.venv\Scripts\ruff.exe check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py` | `All checks passed!` |
| Code-quality format gate | `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py` | `2 files already formatted` |

## Commands Executed

```powershell
python scripts\bridge_claim_cli.py claim gtkb-ollama-integration-phase-1-shim
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-ollama-integration-phase-1-shim
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-automation'; uv run --no-project --with pytest --with pytest-timeout python -m pytest platform_tests\scripts\test_ollama_harness.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py
groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --help
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
```

Observed results:

- `pytest`: `26 passed, 2 warnings in 0.71s`. Warnings were a pytest config warning for `asyncio_mode` in the root config and a pre-existing `.pytest_cache` creation warning: `[WinError 183] Cannot create a file when that file already exists`.
- `ruff check`: `All checks passed!`
- `ruff format --check`: `2 files already formatted`
- `ollama_harness.py --help`: exit 0 and printed the CLI options.
- Bridge applicability preflight on the GO'd operative proposal: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit 0, zero must-apply evidence gaps, zero blocking gaps.

## Verification Limits

No live Ollama server invocation was run in this child. That is intentional:
`bridge/gtkb-ollama-integration-phase-1-shim-008.md` says Child 2 owns mocked
chat-loop and local guard proof, while Child 3 owns live server round-trip,
bridge filing proof, and doctor integration.

## Acceptance Status

All Child 2 acceptance criteria in the GO'd proposal are satisfied. The thread
now awaits Loyal Opposition verification.

## Recommended Commit Type

Recommended commit type: `feat:`

`feat:` - adds a new Ollama harness capability surface, routing config, and
focused regression tests.
