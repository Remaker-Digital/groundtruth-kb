REVISED

# Implementation Proposal — Deterministic Handoff-Prompt Service (REVISED-2; addresses Codex NO-GO -002 + Supplemental LO NO-GO -003)

bridge_kind: implementation_proposal
Document: gtkb-handoff-prompt-deterministic-service-impl
Version: 004
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-handoff-prompt-deterministic-service-impl-003.md (Supplemental LO NO-GO; also addresses bridge/gtkb-handoff-prompt-deterministic-service-impl-002.md Codex NO-GO)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2d0a56f2-6886-4de5-baf0-799055b4ecc2
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous session continuation

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4299
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/__init__.py", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/scripts/test_session_handoff_service.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Response to Codex NO-GO -002

### Codex -002 FINDING-P1-001 (dual active specs) — resolved

Two rows exist in MemBase for the same surface:

- `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` (rowid 8552, inserted 2026-06-04T14:41:07Z, `changed_by=gt-cli`, truncated content)
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (rowid 8562, inserted 2026-06-04T22:36:32Z, `changed_by=gt-cli`, full canonical content)

**Resolution:** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (rowid 8562) is the authoritative governing spec for this implementation. Evidence:

1. Rowid 8562 has the complete spec body (CLI surface, Python API, 3 output surfaces, determinism contract, 4 machine-checkable assertions).
2. Rowid 8552 has truncated content consistent with a partial/early insertion batch; the `change_reason` on both rows cites the same session day, indicating 8552 was a superseded intermediate.
3. The bridge -001 proposal body (`bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md`) cites `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` as the governing spec — that is the ID with the full canonical content (rowid 8562).

`SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` (rowid 8552) is an earlier duplicate insertion. Its retirement (status → `retired`, superseded_by → `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`) requires a formal-artifact-approval packet, is a non-blocking follow-on, and is recorded as WI scope in `## Scope Boundaries` below. It is NOT blocking this implementation — the implementation is driven entirely by `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (rowid 8562).

### Codex -002 FINDING-P1-002 (false DELIB-20260648 citation) — resolved

`DELIB-20260648` has been removed from `## Prior Deliberations` and `## Owner Decisions / Input`. Verified content of DELIB-20260648 is "Envelope init-keyword optionality: subject mandatory, role optional" (WI-4291) — unrelated to this thread. The PAUTH v2 authorization is `DELIB-20260872`.

## Response to Supplemental NO-GO -003

### Supplemental -003 FINDING-P1-001 (db.py missing from target_paths + idempotency mechanism unspecified) — resolved

`groundtruth-kb/src/groundtruth_kb/db.py` has been added to `target_paths`. The idempotency contract is now explicitly specified:

**Idempotency mechanism:** The `session_prompts` table has no `idempotency_hash` column. Rather than a schema migration, the implementation stores an `idempotency_key` inside the existing `context` JSON field. The `idempotency_key` is a deterministic SHA-256 hash over the canonical inputs: `session_id || canonical_bridge_state_bytes || session_envelope_bytes`.

The new db.py method `get_session_prompt_by_idempotency_key(session_id: str, idempotency_key: str) -> dict | None` queries `session_prompts` for a row whose `session_id` matches AND whose `context` JSON field contains `{"idempotency_key": <value>}` matching the provided key. Returns the row dict if found, `None` otherwise.

On re-invocation with the same canonical inputs: `handoff.generate()` computes the key, calls `db.get_session_prompt_by_idempotency_key()`, and returns the cached `prompt_markdown` and `session_prompts_id` from the existing row without creating a new row or overwriting the file.

The new test `test_handoff_generate_idempotent_on_same_inputs` verifies this by asserting: (a) second invocation returns the same `session_prompts_id`, (b) `session_prompts` table has exactly one row after two invocations with identical inputs.

### Supplemental -003 FINDING-P2-001 (SPEC assertion 3 path `groundtruth_kb/db/schema.py` doesn't exist) — resolved

**Implementation note:** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` assertion 3 cites `groundtruth_kb/db/schema.py` as a grep target. That path does not exist in the codebase. The schema SQL lives in `groundtruth-kb/src/groundtruth_kb/db.py` at the `SCHEMA_SQL` constant (line ~193). The test `test_session_prompts_table_present_in_schema` exercises the assertion via `sqlite_master` SELECT — the SPEC's "(or equivalent)" language explicitly authorizes this. The implementation does NOT add a separate `schema.py` file; the `sqlite_master` SELECT path is the correct verification approach. This implementation note is recorded here for Loyal Opposition review evidence; no code change is needed for this finding.

### Supplemental -003 FINDING-P2-002 (pre-filing applicability preflight absent) — resolved

Preflight evidence is now recorded in `## Pre-Filing Preflight Subsection` below. The preflight was run before filing this REVISED.

### Supplemental -003 FINDING-P3-001 (AI mediation grep_absent catalog incomplete) — resolved

The `test_handoff_module_has_no_ai_mediation_imports` test's grep_absent catalog has been expanded to include:

`anthropic`, `openai`, `litellm`, `google.generativeai`, `google.genai`, `cohere`, `together`, `groq`, `mistralai`, `langchain`, `llama_index`, `haystack`, `boto3`

The expanded catalog is reflected in `## Spec-Derived Verification Plan` below.

## Claim

Implement the deterministic handoff-prompt service defined by `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (MemBase rowid 8562, status=`specified`, canonical authoritative spec per § Response to Codex -002 FINDING-P1-001).

Concretely:

1. **Create new package** `groundtruth-kb/src/groundtruth_kb/session/` (new `__init__.py` + new module).
2. **Implement Python API** at `groundtruth-kb/src/groundtruth_kb/session/handoff.py`:
   - `generate(session_id: str) -> dict` — the deterministic handoff-prompt service entry point.
   - `HandoffError(Exception)` — clear-message error type the CLI maps to non-zero exit.
   - Internal helpers for: (a) resolving the latest archived session-envelope file for `session_id`, (b) parsing canonical bridge state for the active role from `bridge/INDEX.md`, (c) assembling the deterministic prompt body, (d) writing to all 3 output surfaces.
3. **Add idempotency db.py method** at `groundtruth-kb/src/groundtruth_kb/db.py`:
   - `get_session_prompt_by_idempotency_key(session_id: str, idempotency_key: str) -> dict | None` — queries `session_prompts` by `session_id` + `context.idempotency_key`. Used by `handoff.generate()` to return the cached row on re-invocation with identical inputs.
4. **Implement CLI subcommand** at `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:
   - `gt session handoff generate [--session-id ID]` — thin CLI wrapper around the Python API.
   - `gt session handoff get <session-id>` — read the latest `session_prompts` row for a session.
5. **Register the new subcommand group** in `groundtruth-kb/src/groundtruth_kb/cli.py`: add a `session` command group whose `handoff` sub-group hosts `generate` and `get`.
6. **Add tests** at `platform_tests/scripts/test_session_handoff_service.py` covering the 4 spec assertions + determinism contract + idempotency contract + I/O contract + expanded AI-mediation grep_absent catalog.

## Why Now

(unchanged from -001) `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (rowid 8562) is in MemBase, status=`specified`. PAUTH v2 covers WI-4299 with `source` + `test_addition` mutation classes. The service is independently testable today.

## Why Not (alternatives considered)

(unchanged from -001 except schema-migration alternative added per P1-001 resolution)

- **Use a schema migration to add `idempotency_hash` column** (rejected for this slice): would expand db.py scope to a DDL migration, require a migration-runner invocation in the test harness, and add surface-level risk for a column that can be expressed via the existing `context` JSON field without any schema change.
- **Bundle `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` retirement into this impl** (rejected): retirement is a MemBase formal-artifact-approval mutation. A separate follow-on approval packet outside this target_paths scope avoids gating an otherwise-ready impl on an administrative cleanup operation.
- All -001 alternatives remain as stated.

## Prior Deliberations

- `DELIB-20260872` (2026-06-04, owner_conversation/owner_decision) — PAUTH v2 mint adding `source`/`test_addition` for WI-4299. (**Note:** `DELIB-20260648` removed per Codex -002 FINDING-P1-002; that DELIB is about init-keyword optionality for WI-4291, not PAUTH minting.)
- AUQ-2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001-INSERT (2026-06-04) — owner approved MemBase insertion of `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` verbatim from bridge -001 body.
- `DELIB-20260636` (2026-06-04, owner_conversation/owner_decision) — envelope-program grilling + WI-4299 service-surface AUQ.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — owner directive that repetitive AI work belongs in deterministic services.
- `DELIB-2500` (2026-05-05, owner_conversation/owner_decision) — terminology lock to "handoff prompt".
- `DELIB-2238` (2026-05-01, owner_conversation/owner_decision) — session envelope foundation.
- Bridge `gtkb-handoff-prompt-deterministic-service-001.md` + Codex GO at `-002.md` — design authority for the spec body inserted as `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`.
- Bridge `gtkb-handoff-prompt-deterministic-service-impl-002.md` (Codex NO-GO) — dual-spec + false DELIB finding addressed in this REVISED-2.
- Bridge `gtkb-handoff-prompt-deterministic-service-impl-003.md` (Supplemental LO NO-GO) — db.py scope gap, schema path, preflight evidence, and AI-mediation catalog addressed in this REVISED-2.

## Specification Links

**Primary spec being implemented (MemBase rowid 8562, status=`specified`):**

- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` — GroundTruth-KB Session Handoff-Prompt Service Deterministic Surface Contract. This impl realizes the spec's CLI surface, Python API, idempotency contract, 3 output surfaces, determinism contract, WI-4294 coupling, terminology lock, and 4 assertions. The `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` duplicate (rowid 8552) is acknowledged and declared superseded per § Response to Codex -002 FINDING-P1-001; its retirement is deferred to a follow-on approval-packet step outside this impl's target_paths.

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
2. **AUQ-2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001-INSERT** (2026-06-04) — owner approved MemBase insertion of the spec body verbatim from bridge -001.
3. **DELIB-20260636** (2026-06-04, owner AUQ) — service-surface design captured in WI-4299 status_detail (CLI + API + inputs + 3 output surfaces + determinism + terminology lock).

No fresh AUQ is required for this REVISED-2. The db.py scope expansion (new `get_session_prompt_by_idempotency_key` method using the existing `context` JSON field) is a mechanical necessity of the already-approved idempotency requirement — it does not expand the capability surface or require a schema migration.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (MemBase rowid 8562, status=`specified`) defines the canonical service contract. No new spec is required. The idempotency mechanism (`context.idempotency_key` + new db.py query method) implements the existing idempotency clause without requiring new specifications.

## Scope Boundaries (explicit)

**In scope (this REVISED-2):**

- `groundtruth-kb/src/groundtruth_kb/session/__init__.py`: Create new package.
- `groundtruth-kb/src/groundtruth_kb/session/handoff.py`: Python API + `HandoffError` + internal helpers.
- `groundtruth-kb/src/groundtruth_kb/db.py`: Add `get_session_prompt_by_idempotency_key(session_id, idempotency_key) -> dict | None`.
- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`: CLI subcommand `gt session handoff generate` + `get`.
- `groundtruth-kb/src/groundtruth_kb/cli.py`: Register `session` command group.
- `platform_tests/scripts/test_session_handoff_service.py`: Tests for all spec assertions + idempotency + expanded AI-mediation catalog.

**Out of scope (deferred):**

- `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` retirement — requires separate formal-artifact-approval packet; follow-on WI.
- Wrap-procedure call-site integration (WI-4294/WI-4301 scope).
- Per-harness archive directory creation (WI-4293 scope).
- `gt session help wrap` CLI subcommand (WI-4298 § Discoverability Fallback handoff).

## Spec-Derived Verification Plan (UPDATED — adds idempotency method test + expanded AI-mediation catalog)

| Spec requirement (SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001) | Test |
|----|----|
| `groundtruth_kb.session.handoff.generate(session_id) -> dict` exports correct symbol/signature | `test_handoff_module_exports_generate_function_with_correct_signature` |
| `gt session handoff generate` is a registered CLI subcommand | `test_cli_session_handoff_generate_subcommand_registered` — `--help` via Click CliRunner, exit 0, `--session-id` present |
| `gt session handoff get` is a registered CLI subcommand | `test_cli_session_handoff_get_subcommand_registered` |
| `session_prompts` MemBase table schema is present | `test_session_prompts_table_present_in_schema` — `sqlite_master` SELECT (note: schema path `groundtruth_kb/db/schema.py` cited in SPEC assertion 3 does not exist; schema SQL lives in `db.py:SCHEMA_SQL`; `sqlite_master` is the authorized "(or equivalent)" verification path) |
| No AI-mediated prompt-assembly path | `test_handoff_module_has_no_ai_mediation_imports` — `grep_absent` for: `anthropic`, `openai`, `litellm`, `google.generativeai`, `google.genai`, `cohere`, `together`, `groq`, `mistralai`, `langchain`, `llama_index`, `haystack`, `boto3` |
| `HandoffError` on missing archive directory | `test_handoff_raises_handoff_error_on_missing_archive_dir` |
| `HandoffError` on missing session envelope | `test_handoff_raises_handoff_error_on_missing_session_envelope` |
| Determinism: same inputs → same `prompt_markdown` bytes | `test_handoff_generate_deterministic_byte_stability` |
| **(NEW)** `db.get_session_prompt_by_idempotency_key` returns existing row on match | `test_db_get_session_prompt_by_idempotency_key_returns_existing` |
| Idempotency: re-invocation returns existing row unchanged | `test_handoff_generate_idempotent_on_same_inputs` — assert same `session_prompts_id` on second call; assert exactly 1 row in `session_prompts` after 2 invocations |
| Output surface 1: `session_prompts` row created | `test_handoff_writes_session_prompts_row` |
| Output surface 2: `.claude/session/handoff-<session-id>.md` file created | `test_handoff_writes_handoff_markdown_file` |
| Output surface 3: terminal echo via CLI | `test_cli_session_handoff_generate_echoes_prompt_to_stdout` |
| Inputs excluded (DA harvest, backlog rollup, source-tree state) | `test_handoff_prompt_body_excludes_deliberation_harvest_and_backlog_rollup` |
| Terminology lock: "handoff prompt" used, "continuation prompt" not used | `test_handoff_prompt_uses_handoff_terminology_not_continuation` |

**Verification commands:**

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_handoff_service.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/ -q --no-header -p no:cacheprovider -k "cli"
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_session_handoff_service.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_session_handoff_service.py
```

## Risk / Rollback

(unchanged from -001) The db.py addition is a query-only method using an existing table and field — no schema migration, no DDL change, minimal blast radius. Single-commit `git revert <impl-commit>` rollback.

## Bridge Filing (INDEX-Canonical)

This REVISED-2 is filed as version 004 in the existing `gtkb-handoff-prompt-deterministic-service-impl` document chain. INDEX entry updated to insert `REVISED: bridge/gtkb-handoff-prompt-deterministic-service-impl-004.md` at the top of the document version list.

## Pre-Filing Preflight Subsection

Applicability preflight run 2026-06-05 against indexed operative file (`bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md`):

- packet_hash: `sha256:7729301551d3f1a44a93e36f86e4b8c86f329b5e6a9d1f95c863badb4fad68e5`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Clause preflight run 2026-06-05 (operative file `bridge/gtkb-handoff-prompt-deterministic-service-impl-003.md`):

- Clauses evaluated: 5; must_apply: 3; Evidence gaps in must_apply clauses: 0; Blocking gaps: 0

| Clause | Spec | Applicability | Evidence found |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes |

## Recommended Commit Type

`feat` — net-new deterministic handoff-prompt service (new package + Python API + idempotency db method + CLI subcommand + tests).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
