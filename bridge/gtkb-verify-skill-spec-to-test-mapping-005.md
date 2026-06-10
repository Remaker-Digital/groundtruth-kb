REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-verify-skill-spec-to-test-mapping-revised-2
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Implementation Proposal - Spec-to-Test Mapping Helper Slice 2 (WI-3261) - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-verify-skill-spec-to-test-mapping
Version: 005 (REVISED)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Responds-To: `bridge/gtkb-verify-skill-spec-to-test-mapping-004.md` (GO) + implementation-start authorization-gate finding

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3261

target_paths: ["scripts/spec_to_test_mapper.py", "platform_tests/scripts/test_spec_to_test_mapper.py"]

Recommended commit type: feat

## Revision Claim

This REVISED-2 carries forward the GO'd `-003` scope **unchanged** and adds the mandatory `## Requirement Sufficiency` subsection required by the implementation-start authorization gate. The GO at `-004` approved `-003`, but `-003` omitted `## Requirement Sufficiency`, so `python scripts/implementation_authorization.py begin --bridge-id gtkb-verify-skill-spec-to-test-mapping` fails closed with `"Approved proposal is missing ## Requirement Sufficiency"` and implementation cannot start.

Changes vs `-003`, both additive and non-scope-altering:

1. Added the `## Requirement Sufficiency` subsection (single operative state).
2. Added a `## Schema Reconciliation Note` recording the exact live `current_tests` / `assertion_runs` column names so the implementation is faithful to the database and does not earn a column-mismatch NO-GO.

`target_paths`, the helper data contract, the scope, and the verification plan are otherwise identical to `-003`. Re-GO requested.

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
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- DELIB-S350-BATCH3-DETERMINISTIC-SERVICES

## Prior Deliberations

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner authorization for the deterministic-services batch containing WI-3261.
- `bridge/gtkb-verify-verdict-author-skill-slice-1-004.md` - VERIFIED Slice 1; this thread implements only the deferred helper and does not modify the skill files Slice 1 installed.
- `bridge/gtkb-verify-skill-spec-to-test-mapping-003.md` (REVISED) and `-004.md` (GO) - the prior GO'd proposal this REVISED-2 carries forward; the GO is the controlling approval, this revision only adds the gate-mandatory section.
- `DELIB-1461`, `DELIB-1463`, `DELIB-1475`, `DELIB-1476` - prior spec-derived verification and Deliberation Archive governance context surfaced during Loyal Opposition review.

## Owner Decisions / Input

No new owner decision is required. This revision adds a mandatory proposal subsection that the implementation-start gate requires; it does not change the S350-authorized WI-3261 scope, target paths, or data contract. WI-3261 is covered by the active `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH` per project membership.

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

## Schema Reconciliation Note (live column names)

Recorded from the live `groundtruth.db` schema (read-only `PRAGMA table_info`) so the implementation maps the data contract to real columns:

- `current_tests` is a SQL VIEW (latest version per test). Columns: `rowid, id, version, title, spec_id, test_type, test_file, test_class, test_function, description, expected_outcome, last_result, last_executed_at, changed_by, changed_at, change_reason`.
- The contract's per-test `Test ID` maps to `current_tests.id`; the contract's `Test Path` / JSON `test_path` maps to `current_tests.test_file` (there is **no** `test_path` column). Per-test status maps to `last_result`; last-run maps to `last_executed_at` (both present as contracted).
- `assertion_runs` is a TABLE. Columns: `rowid, spec_id, spec_version, run_at, overall_passed, results, triggered_by`. There is **no** `run_id` column; the JSON `latest_assertion_run.run_id` is optional and may be sourced from `rowid` or omitted.
- `KnowledgeDB.get_tests_for_spec(spec_id)` returns `current_tests` rows for a spec and is the preferred accessor for per-test rows. Latest assertion run = newest `assertion_runs` row for the spec ordered by `run_at` (tie-break `rowid`).

This note is informational reconciliation; it does not change the contract's intended output, only the source-column mapping used to produce it.

## Proposed Scope

### IP-1: `scripts/spec_to_test_mapper.py`

Add a read-only CLI helper that:

1. Parses explicit spec IDs or extracts spec IDs from a bridge thread.
2. Queries `groundtruth.db` using the data contract above.
3. Emits a markdown table by default.
4. Emits the JSON shape above with `--json`.
5. Exits non-zero only for invalid inputs, missing database, or missing bridge thread; absence of linked tests is reported in output and is not a CLI error.

### IP-2: Platform tests

Add `platform_tests/scripts/test_spec_to_test_mapper.py`. Tests use a temporary SQLite database or a minimal `KnowledgeDB` fixture, not the live `groundtruth.db`.

## Explicitly Not Authorized

- Changes to `.claude/skills/verify/SKILL.md`.
- Changes to `.codex/skills/verify/SKILL.md`.
- Changes to root `tests/` tree.
- Spec promotion or status mutation.
- Database mutation.

## Requirement Sufficiency

Existing requirements sufficient. WI-3261 is authorized under the active `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH` (no expiry; WI-3261 in the included work-item set; allowed mutation classes include `test_addition` and `cli_extension`). The helper data contract, the Schema Reconciliation Note, and the acceptance criteria fully specify a read-only CLI over the existing `current_tests` / `assertion_runs` schema. No new or revised requirement is required before implementation.

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
3. Markdown and JSON output follow the data contract, sourced from the columns in the Schema Reconciliation Note.
4. No skill files are modified.
5. Focused platform tests pass (observed output in the post-implementation report).
6. Applicability and clause preflights pass before and after filing.
7. (Pending Codex) Re-GO on this REVISED-2 at `-006`.

## Risk And Rollback

Risk: bridge spec extraction may miss unusual citation styles. Mitigation: explicit `--spec-id` remains the deterministic path, and bridge extraction is tested against representative bridge content.

Risk: consumers may overread assertion-run status as per-test proof. Mitigation: assertion-run status is intentionally separate from per-test status in both markdown and JSON.

Rollback: delete `scripts/spec_to_test_mapper.py` and `platform_tests/scripts/test_spec_to_test_mapper.py`. Slice 1 `/verify` skill files remain intact.

## Pre-Filing Preflight Subsection

Run after INDEX update (operative resolves to `-005`):

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping`

Expected `preflight_passed: true`; `missing_required_specs: []`; clause preflight exit 0.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
