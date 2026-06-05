NEW

# Implementation Proposal — Deterministic Handoff-Prompt Service (WI-4299 impl)

bridge_kind: implementation_proposal
Document: gtkb-handoff-prompt-deterministic-service-impl
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 316b9ea4-8e82-4441-8b8d-cda2197c6f28
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous session continuation

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4299
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/__init__.py", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_session_handoff_service.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Implement the deterministic handoff-prompt service defined by `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (MemBase, status=`specified`, inserted 2026-06-04 under PAUTH v2 approval_packet_creation per AUQ-2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001-INSERT).

Concretely:

1. **Create new package** `groundtruth-kb/src/groundtruth_kb/session/` (new `__init__.py` + new module).
2. **Implement Python API** at `groundtruth-kb/src/groundtruth_kb/session/handoff.py`:
   - `generate(session_id: str) -> dict` — the deterministic handoff-prompt service entry point.
   - `HandoffError(Exception)` — clear-message error type the CLI maps to non-zero exit.
   - Internal helpers for: (a) resolving the latest archived session-envelope file for `session_id`, (b) parsing canonical bridge state for the active role from `bridge/INDEX.md`, (c) assembling the deterministic prompt body, (d) writing to all 3 output surfaces.
3. **Implement CLI subcommand** at `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:
   - `gt session handoff generate [--session-id ID]` — thin CLI wrapper around the Python API.
   - `gt session handoff get <session-id>` — read the latest `session_prompts` row for a session.
4. **Register the new subcommand group** in `groundtruth-kb/src/groundtruth_kb/cli.py`: add a `session` command group whose `handoff` sub-group hosts `generate` and `get`. The `session` group is open for future extension (e.g., `gt session help wrap` per the WI-4298 § Discoverability Fallback handoff).
5. **Add tests** at `platform_tests/scripts/test_session_handoff_service.py` covering the 4 spec assertions + determinism contract + I/O contract.

## Why Now

`SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` was just inserted into MemBase (2026-06-04, this session, AUQ-approved). PAUTH v2 covers WI-4299 with `source` + `test_addition` mutation classes. The service is independently testable today (the `session_prompts` MemBase table already exists; the `bridge/INDEX.md` parsing path is reusable from `scripts/bridge_applicability_preflight.py`).

The one missing input source — the per-harness `harness-state/<harness_name>/session-envelope-archive/` directory defined by WI-4293 — does not block service shipping. The service's archive-resolution path raises `HandoffError` with a clear message when the directory or file is missing; this error path is spec-compliant and lets the service ship now with a well-defined failure mode that gets resolved automatically when WI-4293 lands the archive infrastructure.

## Why Not (alternatives considered)

- **Wait for WI-4301 capstone to land the impl** (rejected): the spec assertions reference "WI-4301 Slice B impl time" but that framing was from the design phase before PAUTH v2 added WI-4299 with `source`/`test_addition` classes. The PAUTH v2 amendment supersedes the deferral.
- **Wait for WI-4293 archive directory to exist before implementing** (rejected): the service's input contract is well-defined; a missing archive directory raises `HandoffError` with a clear message. This is spec-compliant ("Errors raise HandoffError with a clear message"). Once WI-4293 ships, the service works end-to-end without service-side changes.
- **Implement only the API, skip the CLI** (rejected): the SPEC explicitly requires both surfaces; the CLI is a thin wrapper around the API.
- **Implement only as a private module inside scripts/** (rejected): the SPEC's surface contract is `groundtruth_kb.session.handoff.generate(...)` — a public Python API in the platform package. Placing it under `scripts/` would be a different surface than the spec defines.
- **Include WI-4301 capstone work (wrap procedure integration call-site) in this thread** (rejected): the call-site integration (wrap procedure invokes the handoff service after archive step #12a) is a wrap-procedure responsibility, not a handoff-service responsibility. The service exposes itself as a callable; the wrap procedure becomes the caller when WI-4301 ships it.

## Prior Deliberations

- `DELIB-20260872` (2026-06-04, owner_conversation/owner_decision) — PAUTH v2 mint adding `source`/`test_addition` for WI-4299.
- AUQ-2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001-INSERT (2026-06-04, this session) — owner approved MemBase insertion of `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` verbatim from bridge -001 body.
- `DELIB-20260648` (2026-06-04, owner_conversation/owner_decision) — envelope-program PAUTH v1 mint.
- `DELIB-20260636` (2026-06-04, owner_conversation/owner_decision) — envelope-program grilling + WI-4299 service-surface AUQ.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — owner directive that repetitive AI work belongs in deterministic services.
- `DELIB-2500` (2026-05-05, owner_conversation/owner_decision) — terminology lock to "handoff prompt".
- `DELIB-2238` (2026-05-01, owner_conversation/owner_decision) — session envelope foundation.
- Bridge `gtkb-handoff-prompt-deterministic-service-001.md` + Codex GO at `-002.md` — design authority for the spec body inserted as `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`.

## Specification Links

**Primary spec being implemented (MemBase, status=`specified`):**

- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` — GroundTruth-KB Session Handoff-Prompt Service Deterministic Surface Contract. Inserted 2026-06-04 under PAUTH v2 approval_packet_creation. This impl realizes the spec's service-surface, input, output-surface, determinism, terminology, and assertion clauses in full. The call-site coupling to WI-4294 wrap procedure is exposed as a callable but not invoked from a wrap procedure (no wrap procedure exists yet); see § Scope Boundaries.

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

**Forward references (informational only):**

- WI-4293 (session-envelope durability) — archive directory the service reads; absence raises clear HandoffError.
- WI-4294 (wrap procedure) — future caller of the service.
- WI-4301 (impl umbrella) — wrap procedure + capstone integration.

## Owner Decisions / Input

1. **DELIB-20260872** (2026-06-04, owner AUQ) — PAUTH v2 mint adding source/test_addition for WI-4299.
2. **AUQ-2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001-INSERT** (2026-06-04, this session) — owner approved MemBase insertion of the spec body verbatim from bridge -001.
3. **DELIB-20260648** (2026-06-04, owner AUQ) — envelope-program PAUTH v1 mint authorizing the program.
4. **DELIB-20260636** (2026-06-04, owner AUQ) — service-surface design captured in WI-4299 status_detail (CLI + API + inputs + 3 output surfaces + determinism + terminology lock).

No fresh AUQ is required at this impl layer because PAUTH v2 covers the work and the spec defines what success looks like.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (MemBase, status=`specified`) defines the canonical service contract this impl realizes (CLI + Python API + 2 inputs + 3 output surfaces + determinism + WI-4294 coupling + terminology lock + 4 assertions). No new spec is required.

## Scope Boundaries (explicit)

**In scope (this impl):**

- Create `groundtruth-kb/src/groundtruth_kb/session/` package with `__init__.py` + `handoff.py`.
- Implement `generate(session_id) -> dict` Python API + `HandoffError`.
- Implement bridge-state parser (reuse `scripts/bridge_applicability_preflight.py` canonical-status-set logic where possible).
- Implement archive-file resolver (raises `HandoffError` if missing, per spec).
- Implement deterministic prompt-body templating (no randomness, no AI mediation, no fresh timestamps).
- Implement all 3 output surfaces: `session_prompts` MemBase row, `.claude/session/handoff-<session-id>.md` file, terminal stdout echo.
- Implement idempotency: re-invocation on same canonical inputs returns the existing row's prompt unchanged.
- Implement CLI subcommand `gt session handoff generate` + `get`.
- Register `session` command group in `cli.py`.
- Add 12+ tests covering 4 spec assertions, determinism contract, I/O contract, error paths.

**Out of scope (deferred):**

- Wrap-procedure call-site integration. The wrap procedure does not yet exist as a Python entry point (`SPEC-WRAP-PROCEDURE-001` design-only). When WI-4301 capstone ships the wrap procedure, it will invoke this service per the spec's coupling contract; no service-side change is needed.
- Per-harness archive directory creation. The service consumes the directory if it exists; creation is WI-4293 scope.
- `gt session help wrap` CLI subcommand (the WI-4298 § Discoverability Fallback handoff target). Reasonable next-WI scope under the same `session` command group.

## Spec-Derived Verification Plan

| Spec assertion / requirement | Test |
|---|---|
| `groundtruth_kb.session.handoff.generate(session_id) -> dict` exports the right symbol with the right signature | `test_handoff_module_exports_generate_function_with_correct_signature` — assert import + signature inspection |
| `gt session handoff generate` is a registered CLI subcommand | `test_cli_session_handoff_generate_subcommand_registered` — invoke `--help` via Click `CliRunner`, assert exit code 0 + expected option `--session-id` present |
| `gt session handoff get` is a registered CLI subcommand | `test_cli_session_handoff_get_subcommand_registered` — same pattern |
| `session_prompts` MemBase table schema is present | `test_session_prompts_table_present_in_schema` — assert table exists via SELECT on `sqlite_master` |
| No AI-mediated prompt-assembly path | `test_handoff_module_has_no_ai_mediation_imports` — assert `handoff.py` does NOT import `anthropic`, `openai`, `litellm`, or similar AI client libraries; `grep_absent` style check |
| Service raises `HandoffError` with clear message when archive directory missing | `test_handoff_raises_handoff_error_on_missing_archive_dir` |
| Service raises `HandoffError` with clear message when session_id has no archived envelope | `test_handoff_raises_handoff_error_on_missing_session_envelope` |
| Determinism: same inputs → same `prompt_markdown` bytes | `test_handoff_generate_deterministic_byte_stability` — invoke twice with mocked fixed inputs, assert byte-equal results |
| Idempotency: re-invocation returns existing row unchanged | `test_handoff_generate_idempotent_on_same_inputs` — assert second invocation returns row with original `session_prompts_id` |
| Output surface 1: `session_prompts` row created | `test_handoff_writes_session_prompts_row` |
| Output surface 2: `.claude/session/handoff-<session-id>.md` file created | `test_handoff_writes_handoff_markdown_file` |
| Output surface 3: terminal echo via CLI | `test_cli_session_handoff_generate_echoes_prompt_to_stdout` |
| Inputs deliberately excluded (DA harvest, backlog rollup, source-tree state) | `test_handoff_prompt_body_excludes_deliberation_harvest_and_backlog_rollup` — assert known marker substrings absent from generated prompt |
| Terminology lock: "handoff prompt" used, "continuation prompt" not used | `test_handoff_prompt_uses_handoff_terminology_not_continuation` |

**Verification commands (Pre-File Code-Quality Gates per `.claude/rules/file-bridge-protocol.md`):**

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_handoff_service.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_session_handoff_service.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_session_handoff_service.py
```

Plus existing test surfaces touched by the cli.py edit must remain green:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/ -q --no-header -p no:cacheprovider -k "cli"
```

## Risk / Rollback

**Risk:** the new `session` command group registration in `cli.py` is a touch on the central CLI entry point; a defect there could break other `gt` subcommands.

**Mitigations:**
- The cli.py edit is a single `cli.add_command(session_group)`-style line, minimal blast radius.
- Existing cli.py tests (under `groundtruth-kb/tests/`) catch registration regressions.
- The new `session/` package is isolated; nothing else in the platform depends on it (until the future wrap-procedure caller exists).

**Rollback:** single-commit `git revert <impl-commit>` removes the new package and unregisters the subcommand. No MemBase mutation, no schema change (the `session_prompts` table already exists), no narrative-artifact mutation.

## Bridge Filing (INDEX-Canonical)

This proposal is filed as a fresh document under `bridge/` with a `NEW` entry inserted at the top of a new `gtkb-handoff-prompt-deterministic-service-impl` document list in `bridge/INDEX.md`. The originating design thread `gtkb-handoff-prompt-deterministic-service` is preserved as historical evidence and remains GO-terminal at -002.

## Pre-Filing Preflight Subsection

Applicability and clause preflights will be run after INDEX entry insertion. Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking clause gaps.

## Recommended Commit Type

`feat` — net-new capability (deterministic handoff-prompt service surface: new package + Python API + CLI subcommand + tests). Not `refactor` (no pre-existing implementation to refactor); not `chore` (substantial new functional surface).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
