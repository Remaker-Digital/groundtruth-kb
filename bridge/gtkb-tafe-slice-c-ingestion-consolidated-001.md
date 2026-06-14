NEW

bridge_kind: implementation_proposal
Document: gtkb-tafe-slice-c-ingestion-consolidated
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ce76da9c-67eb-4f67-b540-521aeec05550
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4508

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_bridge_ingestion.py"]

# Implementation Proposal (NEW -001) — TAFE Slice C: Bridge-Thread Second-Write Ingestion (Consolidated)

## Summary

The single consolidated implementation of TAFE Slice C, governed by the canonical
`ADR-TAFE-SLICE-C-INGESTION-001`. It replaces two WITHDRAWN duplicate proposals
(`gtkb-tafe-dual-write-slice-c` and `gtkb-tafe-dual-write-slice-c-ingestion`) that
two Prime Builder sessions filed concurrently; the owner reconciled them into one ADR
this session (see `## Prior Deliberations`).

Slice C opens TAFE's first write surface: a new module
`groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py` parses the canonical
`bridge/INDEX.md` via the VERIFIED Slice A lossless parser
(`tafe_index_sync.parse_bridge_index`) and materializes each bridge thread into the
existing `flow_instances` + `flow_artifacts` tables as a **non-authoritative SHADOW**
store, through the append-only `TypedArtifactFlowService`. A new on-demand CLI
`gt flow ingest-bridge-index` (dry-run default, `--apply`, `--json`) drives it. The
canonical `bridge/INDEX.md` is read, never written (`GOV-FILE-BRIDGE-AUTHORITY-001`);
the module holds no canonical-index path literal. No schema change (the tables and the
five seeded flow_definitions already exist).

## Specification Links

- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — Slice C is a tracked, phased
  artifact (Slices A/B VERIFIED; Slice C scoped; cutover deferred to WI-4510).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — superseded ADRs, WITHDRAWN
  duplicate proposals, and deferred scope are recorded by name, not silently.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decisions, the canonical
  ADR, WI-4508, and the derived tests are all linked.
- **ADR-TAFE-SLICE-C-INGESTION-001** — the governing, canonical Slice C design; this
  proposal implements its D1 (implementation-flow selection + bridge_kind metadata +
  advisory-as-status), D2 (`flow-bridge-<slug>` / `fa-bridge-<slug>-<NNN>` identity),
  D3 (status-token→flow status incl. the post-impl-report `NEW`→`in_verification`
  disambiguation), D4 (sha256 fingerprint idempotence), and its flow_instances +
  flow_artifacts-only scope.
- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — the umbrella spec; runtime tables +
  `implementation` flow_definition written into.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` stays authoritative; shadow-only.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — all governing specs cited.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each named test derives from an
  ADR constraint and has a real oracle (mapping below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-TAFE-SLICE-C-INGESTION-001` (owner-approved this
session) fully specifies D1–D4 and the scope/non-goals; `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`
and WI-4508 govern the dual-write program; the cutover PAUTH (`DELIB-20263195`) authorizes
the `dual_write`/`source`/`test_addition`/`config` mutation classes. No new requirement needed.

## Prior Deliberations

- **DELIB-DECISION-1219-SLICE-C-RECONCILE-CONSOLIDATE** — owner AUQ this session choosing
  to reconcile two duplicate Slice C ADRs into one canonical ADR superseding both, and
  consolidate both proposals into this one.
- **DELIB-DECISION-1219-SLICE-C-DRIVE-ADR-FIRST** and **DELIB-TAFE-SLICE-C-ADR-APPROVAL-20260613**
  — the two owner ADR approvals the reconciliation merged.
- **DELIB-20263195** — TAFE Phase 6-7 cutover authorization + the cutover PAUTH.
- `ADR-TAFE-BRIDGE-SECOND-WRITE-INGESTION-001` (superseded) and
  `ADR-TAFE-BRIDGE-THREAD-INGESTION-001` (superseded) — the two predecessor ADRs the
  canonical ADR consolidates; their proposals (`gtkb-tafe-dual-write-slice-c`,
  `gtkb-tafe-dual-write-slice-c-ingestion`) are WITHDRAWN.
- Slice A (`gtkb-tafe-dual-write-index-parity`, VERIFIED) — the parser consumed here.
- Slice B (`gtkb-tafe-dual-write-slice-b-oracle`, VERIFIED) — the completeness oracle
  the ADR required to precede ingestion (resolved the prior shadow-ingestion F2).
- `gtkb-tafe-dual-write-slice-b-shadow-ingestion` (WITHDRAWN) — the earlier attempt
  NO-GO'd for F2 (oracle-first) and F3 (idempotence); resolved by Slice B + ADR D4.

## Design (per ADR-TAFE-SLICE-C-INGESTION-001)

New module `groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py`:

1. Parse a single canonical-INDEX snapshot via Slice A `parse_bridge_index` (no INDEX
   write; no path literal).
2. **D1:** map each `Document:` thread to one `implementation` flow_instance; preserve
   `bridge_kind` in `metadata.bridge_kind`; advisory-latest threads ingest with
   `status='advisory'` (not skipped).
3. **D2:** `subject_type='bridge_thread'`, `subject_id=<slug>`; deterministic ids
   `flow-bridge-<slug>` and one `flow_artifact` per version line
   `fa-bridge-<slug>-<NNN>` (`artifact_type='bridge_version'`,
   `artifact_ref='bridge/<slug>-NNN.md'`, `relationship='version'`,
   `metadata.status_token`).
4. **D3:** derive `flow_instances.status` from the latest token via the ADR table,
   with the version chain disambiguating a latest `NEW`: prior `GO` in chain →
   `in_verification` (post-impl report); else → `in_review` (initial proposal).
5. **D4:** `ingest_fingerprint = sha256(slug, ordered (status, version) tuples)` in
   `metadata.ingest_fingerprint`; append a new flow_instance version only on fingerprint
   change; flow_artifacts insert-if-absent (`UNIQUE(id)`). Re-ingest of an unchanged
   INDEX = no-op. No `stage_instances`/`flow_events` (deferred).
6. CLI `gt flow ingest-bridge-index` on the existing `flow` group: dry-run default,
   `--apply`, `--json`. Reuses the Slice A/B INDEX-read pattern.

No change to `db.insert_*` semantics (idempotence lives in the ingestion layer).

## Verification Plan (Specification-Derived)

New `groundtruth-kb/tests/test_tafe_bridge_ingestion.py`:

| ADR constraint | Test | Oracle |
|---|---|---|
| D1 selection + advisory | `test_thread_maps_to_implementation_flow`; `test_advisory_thread_status_and_metadata` | `flow_definition_id=='implementation'`; advisory-latest → `status='advisory'`, `metadata.bridge_kind='advisory'` |
| D2 identity | `test_deterministic_instance_and_artifact_ids` | `flow-bridge-<slug>`; `fa-bridge-<slug>-<NNN>` with `artifact_type='bridge_version'`, `artifact_ref='bridge/<slug>-NNN.md'` |
| D3 status map | `test_status_token_to_flow_status` (parametrized all tokens) | `flow_instances.status` == ADR D3 value per latest token |
| D3 dual-`NEW` | `test_new_after_go_is_in_verification`; `test_new_without_go_is_in_review` | chain with/without prior `GO` → `in_verification` vs `in_review` |
| D4 idempotence | `test_reingest_unchanged_index_is_noop`; `test_state_change_appends_one_version` | 2nd `--apply` over identical INDEX → 0 new versions / 0 new artifacts; a status change → exactly 1 new flow_instance version |
| Scope | `test_no_stage_instances_or_events_written` | no `stage_instances`, no `flow_events` rows created |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `test_ingestion_does_not_write_canonical_index` | `bridge/INDEX.md` bytes unchanged across an ingest; no index path literal in source |
| CLI dry-run default | `test_cli_ingest_dry_run_default_writes_nothing` | CLI without `--apply` writes nothing |

Commands (run before the post-implementation report):
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_bridge_ingestion.py -q --tb=short`
- `python -m ruff check` and `python -m ruff format --check` on all three `target_paths`.

## Risk / Rollback

- **Risk: low–moderate.** Additive module + one CLI command + tests; the write is
  fingerprint-gated and confined to existing tables; the shadow view is
  non-authoritative so a stale row never corrupts canonical state. The main correctness
  surface (D3 mapping incl. dual-`NEW`) is fully table-tested.
- **Rollback:** delete the new module + test and revert the additive `cli.py` command;
  no schema change, no canonical-state change, no migration. Any shadow rows are inert.

## Owner Decisions / Input

- **DELIB-DECISION-1219-SLICE-C-RECONCILE-CONSOLIDATE** (owner AUQ, this session):
  reconcile the two duplicate Slice C ADRs into `ADR-TAFE-SLICE-C-INGESTION-001`
  (superseding both), withdraw both duplicate proposals, and file this single
  consolidated proposal.
- **Merged-ADR approval AUQ** (this session; `2026-06-14-ADR-TAFE-SLICE-C-INGESTION-001.json`
  formal-artifact-approval packet, `approved_by=owner`): owner approved the canonical ADR.
- **DELIB-20263195** (cutover authorization): the cutover PAUTH covering this scope.

## Recommended Commit Type

`feat:` — adds a net-new ingestion module (`tafe_bridge_ingestion.py`) and a net-new
`gt flow ingest-bridge-index` CLI subcommand (TAFE's first write surface) + tests.
