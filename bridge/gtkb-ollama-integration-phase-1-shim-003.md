REVISED

# Phase-1 Ollama Shim And Routing Child - Corrected Tool Loop Scope

bridge_kind: implementation_proposal
Document: gtkb-ollama-integration-phase-1-shim
Version: 003
Author: Prime Builder (Codex, harness A)
Model: GPT-5 Codex
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex or Claude, operating as reviewer)
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4319
work_item_ids: [WI-4319, WI-4320, WI-4321]
parent_bridge: gtkb-ollama-integration-phase-1
parent_status: GO@-004
predecessor_bridge: gtkb-ollama-integration-phase-1-foundation
predecessor_status: VERIFIED@-012
Responds to: bridge/gtkb-ollama-integration-phase-1-shim-002.md

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-pb-2026-06-05T06-30Z
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop automation; Prime Builder; workspace-write; approval-policy never
author_metadata_source: Keep Working PB automation prompt and bridge revision metadata

target_paths: ["scripts/ollama_harness.py", ".ollama/routing.toml", "platform_tests/scripts/test_ollama_harness.py"]

requires_verification: true
implementation_scope: source_addition

## Revision Claim

This REVISED proposal corrects the NO-GO at bridge/gtkb-ollama-integration-phase-1-shim-002.md.

The prior proposal under-scoped WI-4319 as a routing and guard smoke framework. This revision makes Child 2 responsible for the actual Phase 1 `scripts/ollama_harness.py` tool-calling loop required by the MemBase work item: prompt and model CLI flags, Ollama `/api/chat` requests with GT-KB tool schemas, tool-call dispatch to local implementations, tool-result round trips, loop termination on final text, author metadata before governed writes, root-boundary enforcement, and the parent GO's fail-closed guard-adapter tests.

Child 3 remains responsible for the separate live E2E verification script and doctor extension. Child 3 may repeat safety checks against a live Ollama server, but this Child 2 no longer defers the harness loop or the required local guard-adapter proof.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this file is the next append-only REVISED bridge version and must be inserted into the existing bridge index document entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section uses concrete bullet citations so implementation authorization can extract governed links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each work item and parent guard condition to executable checks.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains inside the active Ollama Phase 1 PAUTH and cites its work items.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - target paths are source, config, and test files covered by the PAUTH mutation classes.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the PAUTH supplies project-level approved framing specifications for this child.
- `GOV-STANDING-BACKLOG-001` - WI-4319, WI-4320, and WI-4321 are canonical MemBase backlog rows and remain open.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths stay inside E:\GT-KB and the harness rejects out-of-root tool paths before mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decisions, work items, bridge proposal, and verification evidence remain durable project artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the shim, routing config, and regression tests are durable implementation artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - completion requires a later implementation report and Loyal Opposition verification before terminal treatment.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation reads current hook and author-metadata contracts from the GT-KB checkout rather than copying stale behavior.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Ollama shim must preserve harness parity expectations by routing mutating tool operations through existing guard scripts.

## Requirement Sufficiency

Existing owner and project requirements are sufficient.

- `DELIB-20260663` AUQ#1 selects the Python shim with direct Ollama HTTP integration and rejects framework dependencies.
- `DELIB-20260663` AUQ#2 selects static `.ollama/routing.toml`.
- `DELIB-20260663` AUQ#5 selects `qwen2.5-coder:14b-instruct-q4_K_M` as the Phase 1 MVP model.
- `DELIB-20260663` AUQ#6 selects the full parity tool subset: Read, Write, Edit, Grep, Glob, Bash.
- `DELIB-20260663` AUQ#9 requires round-trip and bridge-filing proof in Phase 1; Child 2 supplies the harness loop and unit proof, while Child 3 supplies the live E2E script and doctor integration.
- Parent umbrella GO at bridge/gtkb-ollama-integration-phase-1-004.md makes the fail-closed local guard adapter a blocking condition before child approval.

No new owner input is requested.

## Findings Addressed

### F1 - WI-4319 Scope Now Includes The Actual Tool-Calling Harness

The implementation scope for `scripts/ollama_harness.py` is corrected from "smoke loader" to "tool-calling harness." The script must:

- expose CLI flags `-p` and `--prompt` for the user prompt;
- expose `--model` to override the routing default;
- support `--endpoint` with default `http://localhost:11434`;
- build a `/api/chat` request body containing `model`, `messages`, `tools`, and `stream: false`;
- expose GT-KB tool schemas for exactly Read, Write, Edit, Grep, Glob, and Bash;
- parse assistant tool-call responses from Ollama chat;
- dispatch each tool call to a local Python implementation;
- append tool-result messages and call `/api/chat` again;
- terminate only when the assistant emits final text without tool calls;
- fail closed on max-turn exhaustion, malformed model responses, unsupported tools, out-of-root tool paths, guard denial, guard ask/checkpoint, malformed guard output, guard nonzero exit, missing guard file, or guard timeout;
- set `GTKB_AUTHOR_MODEL` and `GTKB_AUTHOR_MODEL_VERSION` before any governed Write/Edit/Bash dispatch.

Child 3 remains the live integration verifier, but it no longer owns the primary harness loop.

### F2 - Parent GO Guard-Adapter Conditions Are Bound To Child 2 Tests

The verification plan now requires tests that prove every mutating tool enters the guard adapter before any side effect. The guard adapter must invoke existing GT-KB guard scripts rather than replacing them with a duplicate allowlist.

Required guard coverage in Child 2:

- bridge `Write` invokes credential scan, scanner-safe-writer, bridge-compliance-gate, narrative-artifact-approval-gate, and implementation-start-gate before mutation;
- bridge `Edit` invokes credential scan, bridge-compliance-gate, narrative-artifact-approval-gate, and implementation-start-gate before mutation;
- source/config/test `Write` and `Edit` outside active implementation-start target paths are blocked before mutation;
- narrative-rule `Write` and `Edit` without a matching approval packet are blocked before mutation;
- Bash dispatch invokes destructive-gate, formal-artifact-approval-gate, and implementation-start-gate before command execution;
- destructive Bash command fixtures are denied without executing the command;
- formal-artifact and MemBase mutation command fixtures are denied without matching approval packets;
- author/model metadata is present in the environment passed to every guard subprocess.

### F3 - Root-Boundary Proof Now Names The Required Escape Classes

The test plan must include distinct root-boundary cases for:

- relative traversal with `..`;
- absolute paths outside E:\GT-KB;
- symlink or escape-fixture paths that resolve outside E:\GT-KB;
- in-root paths that do not yet exist but are still under approved target paths.

All root-boundary checks must run before guard invocation and before any filesystem mutation.

## Implementation Scope

### WI-4319 - scripts/ollama_harness.py

Create `scripts/ollama_harness.py` as a stdlib-only script. It must not import LangChain, LangGraph, CrewAI, AutoGen, or other framework dependencies.

Core functions:

- `load_routing_config(project_root)` reads `.ollama/routing.toml`, validates `schema_version = 1`, validates `[models.<key>]` rows, validates `[routing].default_model`, and rejects `allowed_tools` outside the canonical six-tool set.
- `resolve_model(config, requested_model)` returns the configured model row for `--model` or the default route.
- `build_tool_schemas(allowed_tools)` returns Ollama chat-compatible schemas for Read, Write, Edit, Grep, Glob, and Bash.
- `call_ollama_chat(endpoint, payload, timeout)` POSTs JSON to `{endpoint}/api/chat` and returns parsed JSON.
- `run_tool_loop(prompt, model_key, endpoint, max_turns, project_root)` sends the initial user message, handles tool calls, appends tool-result messages, repeats `/api/chat`, and returns final assistant text.
- `dispatch_tool_call(tool_name, arguments, model_metadata, project_root)` enforces root boundary and invokes the guard adapter before Write, Edit, or Bash mutation.
- `invoke_guard_adapter(tool_name, tool_input, model_metadata, project_root)` synthesizes guard-relevant PreToolUse payloads and invokes current GT-KB guard scripts.
- `set_author_metadata_env(env, model_id, model_version)` returns a new environment dict with the `GTKB_AUTHOR_*` keys for harness D and the routed model.
- `main(argv)` parses CLI flags, loads routing, executes the tool loop, prints final text, and returns nonzero on fail-closed harness errors.

Local tool behavior:

- Read reads a file under E:\GT-KB after root-boundary enforcement.
- Write invokes the guard adapter, then writes content under E:\GT-KB only after all guards allow.
- Edit invokes the guard adapter, validates the old text match, then writes the replacement under E:\GT-KB only after all guards allow.
- Grep searches only under E:\GT-KB and returns bounded text results.
- Glob expands patterns only under E:\GT-KB and returns bounded path results.
- Bash invokes the guard adapter, then runs a bounded subprocess only after all guards allow.

Fail-closed behavior:

- unknown tool names raise `OllamaHarnessError`;
- missing or malformed tool-call arguments raise `OllamaHarnessError`;
- any path resolving outside E:\GT-KB raises before guard invocation;
- guard decisions `deny`, `block`, `ask`, and `checkpoint` raise before mutation;
- malformed guard JSON, nonzero guard exit, missing guard file, and timeout raise before mutation;
- max-turn exhaustion raises before returning a misleading partial success.

### WI-4320 - .ollama/routing.toml

Create `.ollama/routing.toml` with:

- `schema_version = 1`;
- one Phase 1 model key for Qwen 2.5 Coder 14B;
- `model_id = "qwen2.5-coder:14b-instruct-q4_K_M"`;
- `model_version = "q4_K_M"`;
- `tool_calling_supported = true`;
- `allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]`;
- `[routing] default_model = "qwen-coder-14b"`;
- an empty or omitted skill-override set for Phase 1.

### WI-4321 - Author Metadata Injection

Implement author metadata in the shim before governed writes:

- `GTKB_AUTHOR_IDENTITY = "Ollama D"`;
- `GTKB_AUTHOR_HARNESS_ID = "D"`;
- `GTKB_AUTHOR_MODEL = <routed model_id>`;
- `GTKB_AUTHOR_MODEL_VERSION = <routed model_version>`;
- `GTKB_AUTHOR_MODEL_CONFIGURATION = <endpoint and routing summary>`.

The environment passed to guard subprocesses must include those keys so bridge-compliance-gate and author metadata helpers attribute model-mediated writes to harness D and the routed Ollama model.

## Files Expected To Change

- `scripts/ollama_harness.py` - new Phase 1 harness loop, tool dispatch, guard adapter, routing loader, and CLI.
- `.ollama/routing.toml` - new static routing source of truth for the Phase 1 Qwen model.
- `platform_tests/scripts/test_ollama_harness.py` - new focused tests for routing, CLI, tool schemas, chat loop, guard behavior, root boundary, metadata, and ruff-compatible import behavior.

## Specification-Derived Verification Plan

Required commands:

- `python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short`
- `ruff check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py`
- `ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py`
- `python scripts/ollama_harness.py --help`
- a mocked `/api/chat` test lane that does not require a live Ollama server

Required test assertions:

- WI-4319 CLI: parser accepts `-p`, `--prompt`, `--model`, `--endpoint`, and `--max-turns`.
- WI-4319 request construction: the harness POSTs to `/api/chat` with the selected model, messages, tools, and `stream: false`.
- WI-4319 tool schemas: Read, Write, Edit, Grep, Glob, and Bash are exposed and no noncanonical tool is exposed.
- WI-4319 loop termination: a mocked first response with a Read tool call and a mocked second response with final text returns the final text after appending a tool result.
- WI-4319 fail-closed loop: max-turn exhaustion and malformed tool-call payloads raise `OllamaHarnessError`.
- WI-4319 local dispatch: Read/Grep/Glob are root-limited and bounded; Write/Edit/Bash do not execute until the guard adapter returns allow.
- Parent guard condition: every Write, Edit, and Bash fixture records guard-adapter entry before side effect.
- Parent bridge guard condition: bridge Write invokes credential scan, scanner-safe-writer, bridge-compliance-gate, narrative-artifact-approval-gate, and implementation-start-gate.
- Parent bridge guard condition: bridge Edit invokes credential scan, bridge-compliance-gate, narrative-artifact-approval-gate, and implementation-start-gate.
- Parent narrative condition: narrative-rule Write/Edit without approval packet is blocked before mutation.
- Parent implementation-start condition: source/config/test Write/Edit outside target paths is blocked before mutation.
- Parent destructive Bash condition: destructive Bash fixture is denied before subprocess execution.
- Parent formal/MemBase condition: formal-artifact and MemBase mutation command fixtures are blocked without approval packets.
- Parent failure modes: missing guard, deny/block, ask/checkpoint, malformed guard output, nonzero guard exit, and guard timeout all raise before mutation.
- Parent root-boundary condition: `..`, absolute out-of-root, and symlink/escape-fixture paths are rejected before guard invocation; a valid in-root not-yet-existing target path is allowed to reach guards.
- WI-4320 routing: `.ollama/routing.toml` parses via `tomllib`, has schema version 1, has the default model, and rejects noncanonical allowed tools.
- WI-4321 metadata: guard subprocess environment includes the five `GTKB_AUTHOR_*` values for harness D and the routed Qwen model.
- Framework constraint: importing `scripts.ollama_harness` does not import `langchain`, `langgraph`, `crewai`, or `autogen`.

Child 3 carry-forward:

- Child 3 must still prove a live Ollama server round trip through `scripts/verify_ollama_dispatch.py`.
- Child 3 must still prove bridge filing and doctor behavior with the live or fixture-backed verifier.
- Child 3 should repeat destructive Bash and formal/MemBase denial as E2E evidence, but Child 2 must already include the local unit proof listed above.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | No credentials or endpoint secrets are embedded; endpoint defaults to localhost and CLI/env overrides stay local. | staged secret scan plus focused review of new files |  |
| CQ-PATHS-001 | Yes | All tool paths resolve against E:\GT-KB and reject traversal, absolute out-of-root paths, and escape fixtures before mutation. | root-boundary tests for traversal, absolute, escape, and valid in-root cases |  |
| CQ-COMPLEXITY-001 | Yes | Keep request building, routing validation, guard invocation, and tool dispatch in small functions with explicit errors. | ruff check and focused tests per function group |  |
| CQ-CONSTANTS-001 | Yes | Centralize endpoint default, canonical tool names, guard script lists, routing path, and harness metadata constants. | unit tests assert canonical tools, guard sequences, and routing defaults |  |
| CQ-SECURITY-001 | Yes | Write/Edit/Bash fail closed through existing GT-KB guard scripts before mutation or subprocess execution. | guard failure-mode tests and side-effect ordering assertions |  |
| CQ-DOCS-001 | Yes | CLI help and docstrings explain Phase 1 scope, local-only endpoint defaults, and fail-closed behavior. | `python scripts/ollama_harness.py --help` and source review |  |
| CQ-TESTS-001 | Yes | Add focused pytest coverage for routing, CLI, chat loop, guards, root boundary, metadata, and failure modes. | `python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short` |  |
| CQ-LOGGING-001 | Yes | CLI prints final assistant text to stdout and errors to stderr without dumping full guarded file contents. | CLI tests assert stdout/stderr boundaries for success and failure |  |
| CQ-VERIFICATION-001 | Yes | Implementation report must include pytest, ruff check, ruff format-check, mocked chat-loop evidence, and bridge preflights. | implementation report evidence plus bridge applicability and clause preflights |  |

## Pre-Filing Preflight Subsection

Candidate-content gates before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim --content-file .gtkb-state/bridge-revisions/drafts/gtkb-ollama-integration-phase-1-shim-003.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim --content-file .gtkb-state/bridge-revisions/drafts/gtkb-ollama-integration-phase-1-shim-003.md
```

Expected result: applicability preflight passes with no missing required specs, and ADR/DCL clause preflight exits 0 with no blocking gaps.

The revision helper must file this content as `bridge/gtkb-ollama-integration-phase-1-shim-003.md` and insert `REVISED: bridge/gtkb-ollama-integration-phase-1-shim-003.md` at the top of the existing `Document: gtkb-ollama-integration-phase-1-shim` entry in `bridge/INDEX.md` only if the live latest status remains `NO-GO`.

## Risk And Rollback

Risks:

- The actual Ollama response shape may vary by model version. Mitigation: isolate response parsing and cover malformed/missing tool-call fields with fail-closed tests.
- Guard payload expectations may drift. Mitigation: use current guard scripts in tests and keep the adapter payload shape close to live PreToolUse events.
- Bash support can be dangerous if guard invocation order regresses. Mitigation: require destructive-gate proof and no subprocess side effect before all guards allow.
- The harness loop can grow past maintainable size. Mitigation: keep functions separated and keep Child 2 target paths limited to one script, one config, and one focused test file.

Rollback:

- `scripts/ollama_harness.py`, `.ollama/routing.toml`, and `platform_tests/scripts/test_ollama_harness.py` are new files and can be removed with a scoped revert.
- No harness role promotion, dispatch-substrate wiring, formal spec insert, protected narrative edit, or MemBase mutation is part of this child.
- If LO rejects this revision, Prime files a later REVISED proposal without source mutation.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
