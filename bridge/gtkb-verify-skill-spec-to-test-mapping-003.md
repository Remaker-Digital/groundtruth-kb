REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Spec-to-Test Mapping Helper Slice 2 (WI-3261) - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-verify-skill-spec-to-test-mapping
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Session: 019e425a-79e8-7351-80bc-38c73b0b9429
Responds-To: `bridge/gtkb-verify-skill-spec-to-test-mapping-002.md`

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3261

target_paths: ["scripts/spec_to_test_mapper.py", "platform_tests/scripts/test_spec_to_test_mapper.py"]

## Revision Claim

This revision removes the duplicate `/verify` skill scaffold scope and makes this thread the Slice 2 helper-only proposal. Slice 1 is already terminal: `gtkb-verify-verdict-author-skill-slice-1` is latest `VERIFIED` at `bridge/gtkb-verify-verdict-author-skill-slice-1-004.md`.

The only implementation target now is `scripts/spec_to_test_mapper.py` plus its platform test file.

## Specification Links

- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- DELIB-S350-BATCH3-DETERMINISTIC-SERVICES

## Prior Deliberations

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner authorization for the deterministic-services batch containing WI-3261.
- `bridge/gtkb-verify-verdict-author-skill-slice-1-004.md` - VERIFIED Slice 1. This revision depends on it and does not modify the skill files it installed.
- `DELIB-1461`, `DELIB-1463`, `DELIB-1475`, `DELIB-1476` - prior spec-derived verification and Deliberation Archive governance context surfaced during Loyal Opposition review.

## Owner Decisions / Input

No new owner decision is required. This revision narrows the existing S350-authorized WI-3261 work to the deferred helper slice after Slice 1 reached VERIFIED.

## Findings Addressed

### F1 - P1 - The proposal duplicates and conflicts with an existing latest-GO WI-3261 slice

Response: Removed `.claude/skills/verify/SKILL.md` and `.codex/skills/verify/SKILL.md` from `target_paths` and implementation scope. The revised proposal cites the existing Slice 1 VERIFIED thread and implements only the deferred helper.

### F2 - P1 - The verification command targets a non-existent test tree

Response: Removed `tests/scripts/test_spec_to_test_mapper.py`. The test target is now `platform_tests/scripts/test_spec_to_test_mapper.py`, matching the live repository test layout.

### F3 - P2 - The helper data contract is under-specified

Response: Added a concrete data-source and precedence contract below.

## Helper Data Contract

Input modes:

- `--bridge-id <slug>`: read the latest NEW/REVISED/implementation report/proposal file for the bridge thread and extract cited spec IDs.
- `--spec-id <SPEC-ID>`: repeatable explicit spec input.
- `--json`: emit JSON instead of markdown.

Data sources:

- Per-test rows come from `current_tests` filtered by exact `spec_id`.
- Per-test status comes from `current_tests.last_result`.
- Per-test last-run timestamp comes from `current_tests.last_executed_at`.
- Latest per-spec assertion status is a separate summary from the newest `assertion_runs` row for that `spec_id`, ordered by `run_at`.

Precedence:

- `current_tests.last_result` is never overwritten by `assertion_runs`.
- `assertion_runs.overall_passed` appears only in a separate `Latest assertion run` / `assertion_status` column or JSON field.
- If a spec has no `current_tests` rows, markdown emits a row with `Test ID` set to `(none)` and per-test status `no linked tests`.
- If a test row has no `last_result`, status is `not_run`.
- If a spec has no assertion runs, assertion status is `unknown`.

Markdown columns:

`Spec`, `Test ID`, `Test Path`, `Test Status`, `Last Test Run`, `Latest Assertion Run`, `Assertion Status`.

JSON shape:

- `specs`: list of objects with `spec_id`, `tests`, and `latest_assertion_run`.
- `tests`: list of objects with `test_id`, `test_path`, `last_result`, `last_executed_at`.
- `latest_assertion_run`: null or object with `run_at`, `overall_passed`, and `run_id` when available.

## Proposed Scope

### IP-1: `scripts/spec_to_test_mapper.py`

Add a read-only CLI helper that:

1. Parses explicit spec IDs or extracts spec IDs from a bridge thread.
2. Queries `groundtruth.db` using the data contract above.
3. Emits a markdown table by default.
4. Emits the JSON shape above with `--json`.
5. Exits non-zero only for invalid inputs, missing database, or missing bridge thread; absence of linked tests is reported in output and is not a CLI error.

### IP-2: Platform tests

Add `platform_tests/scripts/test_spec_to_test_mapper.py`.

Tests use a temporary SQLite database or a minimal `KnowledgeDB` fixture, not the live `groundtruth.db`.

## Explicitly Not Authorized

- Changes to `.claude/skills/verify/SKILL.md`.
- Changes to `.codex/skills/verify/SKILL.md`.
- Changes to root `tests/` tree.
- Spec promotion or status mutation.
- Database mutation.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| Mapper emits markdown table | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short` |
| Mapper emits JSON variant | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short` |
| Spec with no linked tests reports `(none)` and `no linked tests` | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short` |
| Per-test status comes from `current_tests.last_result` | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short` |
| Assertion-run status is separate and does not overwrite per-test status | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short` |
| Bridge-id extraction from proposal/report content works | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short` |
| Changed files lint and format cleanly | `python -m ruff check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

1. `scripts/spec_to_test_mapper.py` exists and is read-only.
2. The helper supports `--bridge-id`, repeated `--spec-id`, and `--json`.
3. Markdown and JSON output follow the data contract.
4. No skill files are modified.
5. Focused platform tests pass.
6. Applicability and clause preflights pass before and after filing.

## Risk And Rollback

Risk: bridge spec extraction may miss unusual citation styles. Mitigation: explicit `--spec-id` remains the deterministic path, and bridge extraction should be tested against representative bridge content.

Risk: consumers may overread assertion-run status as per-test proof. Mitigation: assertion-run status is intentionally separate from per-test status in both markdown and JSON.

Rollback: delete `scripts/spec_to_test_mapper.py` and `platform_tests/scripts/test_spec_to_test_mapper.py`. Slice 1 `/verify` skill files remain intact.

## Pre-Filing Preflight Subsection

To be executed by the bridge revision helper before live filing:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping --content-file .gtkb-state\bridge-revisions\drafts\gtkb-verify-skill-spec-to-test-mapping-003.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping --content-file .gtkb-state\bridge-revisions\drafts\gtkb-verify-skill-spec-to-test-mapping-003.md`

End of revision.
