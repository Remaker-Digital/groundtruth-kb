NEW

# TAFE Agent Capability Snapshots Schema - Implementation Report

bridge_kind: implementation_report
Document: gtkb-tafe-agent-capability-snapshots-schema
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC
Responds-To: bridge/gtkb-tafe-agent-capability-snapshots-schema-002.md (GO)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 1834acbd-e886-434c-9ae5-e467a7f93e2b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; default

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4497

implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4497 implemented as approved: the additive `agent_capability_snapshots` MemBase schema plus minimal append-only service/test substrate. The slice is bounded to schema + low-level CRUD service + tests; it implements no dispatch policy, weighted scoring, eligibility evaluation, candidate selection, `gt flow dispatch tick/health`, capability auto-derivation, generated bridge views, or bridge-authority change. WI-4498 and WI-4499 remain open siblings (read-back below).

Implementation-start authorization packet was created from the latest GO before any protected edit (GO condition 4): `python scripts/implementation_authorization.py begin --bridge-id gtkb-tafe-agent-capability-snapshots-schema` -> `packet_hash: sha256:28c9986f40a28da6c8c5bf46f3fc8c03da51eacdf48e268fb614ff8e9f669265`, `latest_status: GO`, expires 2026-06-13T12:50:38Z.

## Specification Links

Carried forward verbatim from the proposal (`-001`):

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - Phase 1 parallel-run substrate; bridge/INDEX.md remains canonical (no cutover).
- `SPEC-TAFE-R4` - the table records per-candidate dispatch inputs (role, capability, subject, health, precedence, workspace availability) for the later policy engine; no policy evaluation here.
- `SPEC-TAFE-R6` - the table persists model/provider, captured-at, and source provenance for later dispatch-decision telemetry.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain is append-only bridge evidence; `bridge/INDEX.md` remains canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - project authorization, project, work item, target paths, and governing specs remain linked.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each linked spec to executed tests (mapping below).
- `GOV-STANDING-BACKLOG-001` - WI-4498 and WI-4499 remain open siblings, read back below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation proceeded under the active bounded PAUTH plus the latest Loyal Opposition GO.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the schema/service substrate is durable governed artifact state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the decision and evidence are preserved through PAUTH, proposal, report, and LO verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4497 closes only after this implementation evidence and terminal VERIFIED.

## Files Changed (this slice only)

- `groundtruth-kb/src/groundtruth_kb/db.py`
  - Initial schema: `agent_capability_snapshots` table (append-only, `UNIQUE(id, version)`), four indexes (`id_version`, `harness`, `health`, `captured`), and the `current_agent_capability_snapshots` latest-version view, placed adjacent to the `stage_leases` substrate.
  - `_migrate_schema`: "Migration 11" — idempotent `CREATE TABLE IF NOT EXISTS` + ALTER-backfill column dict + indexes + view (mirrors the stage-lease Migration 10 so pre-existing DBs pick up the table).
  - Methods: `_next_agent_capability_snapshot_version`, `insert_agent_capability_snapshot`, `get_agent_capability_snapshot`, `get_agent_capability_snapshot_history`, `list_agent_capability_snapshots` (mirror the stage-lease method quartet; JSON columns encoded via `_encode_json`).
  - `_row_to_dict`: added `capabilities` to the JSON-parse list so reads expose `capabilities_parsed` (guarded by `if key in d`, so other tables are unaffected). `metadata` was already parsed.
- `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py`
  - `FlowRuntimeService`: `record_capability_snapshot`, `get_capability_snapshot`, `get_capability_snapshot_history`, `list_capability_snapshots` (validate required non-empty fields; no scoring/selection logic).
- `groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py` (new) — 4 tests.

### Commit-scoping note (GO condition 3)

`db.py` and `typed_artifact_flow.py` also carry pre-existing uncommitted changes from the concurrently-active WI-4492 stage-lease track (another Prime session). Those `stage_leases` changes are NOT part of this slice. The eventual WI-4497 commit must include only the `agent_capability_snapshots` hunks (table/indexes/view/Migration 11/methods/`_row_to_dict` capabilities entry + the new test file). No unrelated dirty-tree changes are attributed to WI-4497.

## Spec-to-Test Mapping (GO condition 2)

| Spec | Test evidence |
|------|---------------|
| `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` | `test_agent_capability_snapshot_schema_contains_required_columns_and_view` proves the substrate is additive (table+view created on a fresh DB) and changes no bridge authority; compat runs prove Phase-0 CLI/doctor and runtime tables are unaffected. |
| `SPEC-TAFE-R4` | `test_..._service_round_trips_current_history_and_filters` proves a candidate harness has a durable point-in-time `harness_id`/`role`/`subject_scope`/`health_status`/`reviewer_precedence`/`workspace_availability`/`capabilities` record, and list filters on `harness_id`/`health_status`/`status`. |
| `SPEC-TAFE-R6` | Same test asserts `model_identifier`, `captured_at`, and `source` provenance persist and `capabilities_parsed`/`metadata_parsed` JSON round-trips. |
| `GOV-STANDING-BACKLOG-001` | WI-4498/WI-4499 read back `backlogged`/`open` (below); `test_..._slice_does_not_expose_dispatch_policy_api` asserts no scoring/dispatch/selection methods exist on the service. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Every linked spec above maps to an executed test; commands + results below. |

## Verification Evidence

Interpreter note: the proposal cited `groundtruth-kb\.venv\Scripts\python.exe`; that venv is not present in this checkout. The system interpreter `C:\Python314\python.exe` (`python`) was used — it imports `groundtruth_kb` and has `pytest 9.0.2` + `ruff 0.15.5`. Commands shown as run:

```text
python -m pytest groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py -q --tb=short
-> 4 passed in 1.45s

python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py groundtruth-kb/tests/test_tafe_stage_leases.py groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py -q --tb=short
-> 11 passed in 3.15s   (additive: WI-4488 runtime substrate + WI-4492 lease substrate unaffected)

python -m pytest groundtruth-kb/tests/test_tafe_flow_cli.py groundtruth-kb/tests/test_tafe_doctor.py groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py -q --tb=short
-> 14 passed in 6.45s    (Phase 0 CLI skeleton + doctor checks unaffected)

python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py
-> All checks passed!

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py
-> 3 files already formatted

git diff --check -- groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py
-> exit 0 (no whitespace errors; a benign LF->CRLF advisory is emitted, not a check failure)
```

## Sibling Work-Item Read-Back (GO condition 1)

```text
WI-4498 | Dispatch policy engine: weighted scoring model | Stage: backlogged | Resolution Status: open | Origin: new
WI-4499 | gt flow dispatch tick/health commands         | Stage: backlogged | Resolution Status: open | Origin: new
```

Both remain open and unimplemented by this slice. `test_agent_capability_snapshot_slice_does_not_expose_dispatch_policy_api` additionally asserts the service exposes none of `score_candidates`, `rank_candidates`, `select_dispatch_target`, `evaluate_eligibility`, `compute_dispatch_score`, `dispatch_tick`, `dispatch_health`.

## GO Conditions Addressed

1. WI-4498/WI-4499 proven open and unimplemented (read-back + negative API test). Done.
2. Spec-to-test mapping explicit for UMBRELLA, R4, R6, GOV-STANDING-BACKLOG-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001. Done.
3. No unrelated WI-4492 lease-track or dirty-tree changes attributed to this slice (commit-scoping note above). Done.
4. Implementation-start packet created from the latest GO before protected edits (`sha256:28c9986f...`). Done.

## Recommended Commit Type

feat - adds a new TAFE capability-snapshot schema/service substrate with focused tests; no behavior change to existing surfaces.

## Bridge Filing (INDEX-Canonical)

This report is filed as the next version under the `gtkb-tafe-agent-capability-snapshots-schema` document list with a `NEW` line at the top of that entry in `bridge/INDEX.md` (append-only; no prior version rewritten). `bridge/INDEX.md` remains canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
