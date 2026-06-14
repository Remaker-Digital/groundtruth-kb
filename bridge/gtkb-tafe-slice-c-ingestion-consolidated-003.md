NEW

bridge_kind: implementation_report
Document: gtkb-tafe-slice-c-ingestion-consolidated
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4886e722-ded0-4913-b8d9-e603dccf98c9
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4508
Responds to: bridge/gtkb-tafe-slice-c-ingestion-consolidated-002.md (LO GO)

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_bridge_ingestion.py"]

# Implementation Report (NEW -003) — TAFE Slice C: Bridge-Thread Second-Write Ingestion (Consolidated)

## Summary

Implemented the GO'd consolidated TAFE Slice C second-write ingestion within the
three declared `target_paths` and the GO's shadow-only scope. TAFE's first write
surface is now live as a **non-authoritative SHADOW**: a new module
`groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py` parses a single
canonical `bridge/INDEX.md` snapshot via the VERIFIED Slice A lossless parser
(`tafe_index_sync.parse_bridge_index`) and materializes each bridge thread into
the existing append-only `flow_instances` + `flow_artifacts` tables through
`TypedArtifactFlowService`. A new on-demand CLI `gt flow ingest-bridge-index`
(dry-run default, `--apply`, `--json`) drives it. The canonical `bridge/INDEX.md`
is read, never written (`GOV-FILE-BRIDGE-AUTHORITY-001`); the module holds no
canonical-index path literal (it receives `index_text` as a string and the
read-only CLI owns the guarded read). No schema change. No `stage_instances` /
`flow_events` rows (deferred per ADR scope).

## Files Changed

- **NEW** `groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py` (~330 lines)
  — the ingestion module implementing ADR D1–D4 (`ingest_bridge_index`,
  `derive_flow_status`, `derive_bridge_kind`, `compute_thread_fingerprint`, plus
  `IngestionResult` / `ThreadResult` / `ArtifactResult` JSON-serializable views).
- **MODIFIED** `groundtruth-kb/src/groundtruth_kb/cli.py` — added the additive
  `gt flow ingest-bridge-index` command on the existing `flow` group (dry-run
  default; `--apply`; `--json`; `--index-path`). Read-only canonical-index
  resolution mirrors the existing `flow index-parity` / `index-completeness`
  pattern; the command has no `--out` and never writes the canonical index.
- **NEW** `groundtruth-kb/tests/test_tafe_bridge_ingestion.py` (20 tests) —
  spec-derived suite (mapping below).

## Specification Links

(Carried forward from the GO'd proposal -001.)

- **ADR-TAFE-SLICE-C-INGESTION-001** — the governing canonical Slice C design;
  this implementation realizes D1 (implementation-flow selection + `bridge_kind`
  metadata + advisory-as-status), D2 (`flow-bridge-<slug>` /
  `fa-bridge-<slug>-<NNN>` identity), D3 (status-token→flow status incl. the
  post-impl-report `NEW`→`in_verification` disambiguation), D4 (sha256 fingerprint
  idempotence), and the flow_instances + flow_artifacts-only scope.
- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — runtime tables + `implementation`
  flow_definition written into.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` stays authoritative;
  shadow-only; no INDEX write; no path literal.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — all governing specs
  cited (carried forward).
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each named test derives
  from an ADR constraint with a real oracle (mapping below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**, **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001**,
  **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — Slice C is a tracked,
  phased artifact; superseded ADRs / WITHDRAWN duplicates recorded by name.

## Spec-to-Test Mapping (Specification-Derived Verification Gate)

| ADR constraint / spec clause | Test(s) | Oracle | Result |
|---|---|---|---|
| D1 — thread → `implementation` flow | `test_thread_maps_to_implementation_flow` | `flow_definition_id=='implementation'`, `subject_type=='bridge_thread'`, `subject_id==slug`, `metadata.shadow is True` | PASS |
| D1 — advisory-as-status | `test_advisory_thread_status_and_metadata` | advisory-latest → `status='advisory'`, `metadata.bridge_kind='advisory'`, still `implementation` | PASS |
| D2 — deterministic identity | `test_deterministic_instance_and_artifact_ids` | `flow-bridge-<slug>`; `fa-bridge-<slug>-{001,002}` with `artifact_type='bridge_version'`, `artifact_ref='bridge/<slug>-NNN.md'`, `relationship='version'`, `metadata.status_token` | PASS |
| D3 — status table (8 tokens) | `test_status_token_to_flow_status` (parametrized REVISED/GO/NO-GO/VERIFIED/WITHDRAWN/ADVISORY/DEFERRED/unknown) | written `flow_instances.status` == ADR D3 value; pure `derive_flow_status` agrees | PASS (8) |
| D3 — dual-`NEW` disambiguation | `test_new_after_go_is_in_verification`; `test_new_without_go_is_in_review` | chain with prior `GO` → `in_verification`/`implementation_report`; without → `in_review`/`implementation_proposal` | PASS |
| D4 — replay-safe no-op | `test_reingest_unchanged_index_is_noop` | 2nd `apply` over identical INDEX → 0 new instance versions / 0 new artifacts; history len 1; artifacts len 2 | PASS |
| D4 — one version on real change | `test_state_change_appends_one_version` | a status change → exactly 1 new flow_instance version + exactly 1 new artifact | PASS |
| Scope — no stage_instances/events | `test_no_stage_instances_or_events_written` | `list_stage_instances()==[]` and `list_flow_events()==[]` after apply | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 — no write | `test_ingestion_does_not_write_canonical_index` | shadow rows written; module reads no file (byte-fidelity asserted in CLI tests) | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 — no path literal | `test_ingestion_module_holds_no_canonical_index_path_literal` | AST scan: no non-docstring string constant contains `index.md` | PASS |
| CLI dry-run default writes nothing | `test_cli_ingest_dry_run_default_writes_nothing` | `--json` no `--apply` → `status='dry_run'`, `mutated=False`; no shadow rows; INDEX bytes identical | PASS |
| CLI apply writes shadow; index untouched | `test_cli_ingest_apply_writes_shadow_and_leaves_index` | `--apply` → `status='applied'`, 1 instance + 2 artifacts; INDEX bytes identical | PASS |

## Verification Evidence (exact commands + observed results)

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_bridge_ingestion.py -q --tb=short
# -> 20 passed in 4.83s

# Regression set (no regressions in adjacent TAFE surfaces):
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_bridge_ingestion.py \
  groundtruth-kb/tests/test_tafe_flow_cli.py groundtruth-kb/tests/test_tafe_index_sync.py \
  groundtruth-kb/tests/test_tafe_runtime_tables.py -q --tb=short
# -> 46 passed in 7.29s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check \
  groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py \
  groundtruth-kb/src/groundtruth_kb/cli.py \
  groundtruth-kb/tests/test_tafe_bridge_ingestion.py
# -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check \
  groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py \
  groundtruth-kb/src/groundtruth_kb/cli.py \
  groundtruth-kb/tests/test_tafe_bridge_ingestion.py
# -> 3 files already formatted

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tafe-slice-c-ingestion-consolidated
# -> preflight_passed: true ; missing_required_specs: [] ; packet_hash sha256:6262855e4c403077def7c252534237307100d91731ab5d773254c52ac7a9aa83

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tafe-slice-c-ingestion-consolidated
# -> Blocking gaps (gate-failing): 0 ; exit 0
```

### GO Required-Verification Checklist (mapped to evidence)

- dry-run mode writes nothing — `test_cli_ingest_dry_run_default_writes_nothing` + live dry-run below (no shadow rows; INDEX byte-identical). PASS
- unchanged INDEX replay writes zero new instance versions and zero new artifacts — `test_reingest_unchanged_index_is_noop`. PASS
- changed thread status writes exactly one new flow-instance version — `test_state_change_appends_one_version`. PASS
- every version line produces a deterministic `flow_artifact` row, inserted only once — `test_deterministic_instance_and_artifact_ids` + the idempotence tests. PASS
- latest `NEW` with a prior `GO` maps to `in_verification`; initial `NEW` maps to `in_review` — `test_new_after_go_is_in_verification`, `test_new_without_go_is_in_review`. PASS
- advisory-latest threads ingest as `status='advisory'` with `metadata.bridge_kind` — `test_advisory_thread_status_and_metadata`. PASS
- no `stage_instances` or `flow_events` rows written — `test_no_stage_instances_or_events_written`. PASS
- the new ingestion module does not write or hard-code the canonical index — `test_ingestion_module_holds_no_canonical_index_path_literal` (AST scan) + module signature takes `index_text` string. PASS
- any canonical-index path resolution in the CLI remains read-only and guarded — the command has no `--out`, only reads `resolved_index`, and never writes it; `test_cli_ingest_apply_writes_shadow_and_leaves_index` asserts INDEX byte-fidelity across an apply. PASS

### Live dry-run evidence (read-only against real canonical index)

```text
INDEX sha256 BEFORE: 356bbc1212a7c2322d45c67df1a0de9371924512f78c0178ebb93679f736ba36
gt flow ingest-bridge-index --json   ->  status: dry_run | applied: False | mutated: False
  threads_total: 319 | would-write instances: 319 | would-write artifacts: 1831 | skipped: 0
  distribution (flow_status, bridge_kind):
    advisory          advisory               x14
    complete          verification_verdict   x211
    in_implementation verification_verdict   x28
    withdrawn          unknown                x66
INDEX sha256 AFTER:  356bbc1212a7c2322d45c67df1a0de9371924512f78c0178ebb93679f736ba36   (byte-identical)
```

The live canonical index currently has no latest-`NEW`/`NO-GO`/`REVISED`/`DEFERRED`
threads (every thread's highest-version line is GO/VERIFIED/WITHDRAWN/ADVISORY), so
the dry-run shows no `in_review`/`in_revision`/`in_verification`/`deferred` rows; the
parser correctly takes the highest-version line as latest (e.g.
`gtkb-tafe-runtime-schema` latest = `WITHDRAWN`-002, not the `NEW`-001 below it).
The `NEW`/`NO-GO`/`REVISED`/`DEFERRED` mappings are covered by the unit suite.

## Scope Adherence

All edits are within the three GO'd `target_paths`. The change is additive and
shadow-only: no schema change, no canonical-state change, no canonical-index write,
no auto-hook/PostToolUse coupling, no cutover, no stage/event modeling — all
explicitly deferred per the ADR and the GO. No MemBase WI mutation is performed in
this report (WI-4508 resolution is a separate operational step after VERIFIED).

## Risk / Rollback

Low–moderate, as proposed. Rollback: delete `tafe_bridge_ingestion.py` + the test
and revert the additive `cli.py` command; no schema change, no migration; any
shadow rows are inert and non-authoritative.

## Owner Decisions / Input

No new owner decision is required for this report; it implements a GO'd, owner-
authorized scope. The authorizing owner evidence (carried forward):

- **DELIB-DECISION-1219-SLICE-C-RECONCILE-CONSOLIDATE** (owner AUQ): reconcile the
  two duplicate Slice C ADRs into `ADR-TAFE-SLICE-C-INGESTION-001` and file one
  consolidated proposal.
- **Merged-ADR approval AUQ** (`.groundtruth/formal-artifact-approvals/2026-06-14-ADR-TAFE-SLICE-C-INGESTION-001.json`, `approved_by=owner`): owner approved the canonical ADR.
- **DELIB-20263195** (cutover authorization) + the cutover PAUTH covering this scope. The irreversible cutover itself remains forbidden by the PAUTH, gated to the closing owner AUQ on the cutover work item.

## Prior Deliberations

- **DELIB-DECISION-1219-SLICE-C-RECONCILE-CONSOLIDATE**, **DELIB-DECISION-1219-SLICE-C-DRIVE-ADR-FIRST**, **DELIB-TAFE-SLICE-C-ADR-APPROVAL-20260613** — the reconciliation + the two ADR approvals it merged.
- **DELIB-20263195** — TAFE Phase 6-7 cutover authorization.
- `ADR-TAFE-BRIDGE-SECOND-WRITE-INGESTION-001` (superseded) and `ADR-TAFE-BRIDGE-THREAD-INGESTION-001` (superseded) — the predecessor ADRs the canonical ADR consolidates.
- Slice A (`gtkb-tafe-dual-write-index-parity`, VERIFIED) — the parser consumed here. Slice B (`gtkb-tafe-dual-write-slice-b-oracle`, VERIFIED) — the oracle the ADR required to precede ingestion. `gtkb-tafe-dual-write-slice-b-shadow-ingestion` (WITHDRAWN) — F2/F3 origin resolved by Slice B + ADR D4.

## Recommended Commit Type

`feat:` — adds a net-new ingestion module (`tafe_bridge_ingestion.py`, TAFE's
first write surface) and a net-new `gt flow ingest-bridge-index` CLI subcommand +
spec-derived tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
