NEW

bridge_kind: implementation_proposal
Document: gtkb-tafe-dual-write-slice-c-ingestion
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

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_bridge_thread_ingest.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_bridge_thread_ingest.py"]

# Implementation Proposal (NEW -001) — TAFE Slice C: Bridge-Thread Second-Write Ingestion

## Summary

WI-4508 Slice C is the **second write** of the TAFE dual-write program. Slice A
(`tafe_index_sync.py`, VERIFIED) made the canonical `bridge/INDEX.md` losslessly
parseable; Slice B (`tafe_index_completeness.py`, VERIFIED) added a read-only
completeness oracle. Both are read-only. Slice C adds a **pure-derivation,
idempotent ingestion path** that materializes each standard bridge thread's
current state into the *existing* TAFE runtime tables (`flow_instances` +
current `stage_instances`) as a **shadow / non-authoritative** view. The
canonical `bridge/INDEX.md` remains authoritative per
`GOV-FILE-BRIDGE-AUTHORITY-001`; the new module performs **no INDEX write** and
holds **no canonical-index path literal**.

This is pre-cutover work: it enables WI-4509 (cutover evidence — diff the shadow
view against INDEX) and de-risks the eventual WI-4510 governed cutover. It does
not perform the cutover, does not change any dispatch substrate, and requires no
schema change (the runtime tables and the five seeded `flow_definitions` already
exist). The design is fully specified by the owner-approved
`ADR-TAFE-BRIDGE-THREAD-INGESTION-001`.

## Specification Links

- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — Slice C is a tracked,
  phased artifact (Slice A/B verified; Slice C scoped; cutover deferred to
  WI-4510), advancing durable runtime artifacts rather than transient state.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — explicit lifecycle states:
  skipped (advisory/report threads), deferred (history backfill, cutover), and
  shadow/non-authoritative are handled by name, not silently.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision
  (`DELIB-DECISION-1219-SLICE-C-DRIVE-ADR-FIRST`), the cutover authorization
  (`DELIB-20263195`), the ADR, WI-4508, and the derived tests are all linked.
- **ADR-TAFE-BRIDGE-THREAD-INGESTION-001** — the governing design: D1
  flow_definition selection, D2 subject_id derivation, D3 status-token→stage
  semantics, D4 replay/idempotency under concurrent INDEX writers, plus the
  scope/non-goals this proposal implements verbatim.
- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — the TAFE umbrella spec; the
  runtime tables and `implementation` flow_definition this proposal writes into.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` stays authoritative;
  Slice C is shadow-only and never writes the index.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal
  cites every governing specification it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — every named test below
  derives from a linked spec/ADR clause and has a real oracle.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-TAFE-BRIDGE-THREAD-INGESTION-001`
(owner-approved this session) fully specifies the four design decisions and the
scope/non-goals; `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` and WI-4508 govern
the dual-write program; the cutover PAUTH (`DELIB-20263195`) authorizes
`dual_write`/`source`/`test_addition`/`config` mutation classes. No new or
revised requirement is needed before implementation.

## Prior Deliberations

- **DELIB-DECISION-1219-SLICE-C-DRIVE-ADR-FIRST** — owner AUQ this session
  authorizing driving Slice C ADR-first (and the subsequent ADR-approval AUQ).
- **DELIB-20263195** — TAFE Phase 6-7 cutover authorization and the cutover
  PAUTH (allows `dual_write`/`source`/`test_addition`/`config`; forbids
  `cutover`/`live_dispatch_substrate`/`kb_schema_change`/`deployment`/
  `production_release`/`formal_spec_promotion`). This proposal stays inside the
  allowed classes.
- `bridge/gtkb-tafe-dual-write-index-parity-*` (Slice A, VERIFIED) — the lossless
  parser this proposal consumes (`parse_bridge_index`).
- `bridge/gtkb-tafe-dual-write-slice-b-oracle-*` (Slice B, VERIFIED) — the
  completeness oracle; Slice C is the write half that complements it.
- `bridge/gtkb-tafe-dual-write-slice-b-shadow-ingestion-*` (**WITHDRAWN**) — an
  earlier ingestion attempt was NO-GO'd as a duplicate *Slice B*; the literal
  second-write was deferred to *Slice C* pending an ADR. This proposal is that
  Slice C, now backed by `ADR-TAFE-BRIDGE-THREAD-INGESTION-001`. It does **not**
  refile ingestion as Slice B.

## Design

Per `ADR-TAFE-BRIDGE-THREAD-INGESTION-001`. New module
`groundtruth-kb/src/groundtruth_kb/tafe_bridge_thread_ingest.py`:

1. **Read** the caller-supplied INDEX text (the read-only CLI passes
   `bridge/INDEX.md` contents); parse via Slice A `parse_bridge_index`. The
   module itself performs no file I/O on the canonical index and embeds no index
   path literal (parity with Slice A/B purity).
2. **D1 — selection.** For each `DocumentBlock`, ingest only standard
   implementation-protocol threads (version chain uses `NEW/REVISED/GO/NO-GO/
   VERIFIED`). Threads whose latest token is `ADVISORY` (or otherwise
   advisory/report-shaped) are **skipped and reported**, not errored. All
   ingested threads map to the seeded `implementation` flow_definition.
3. **D2 — subject.** `subject_type="bridge_thread"`, `subject_id=<slug>` (the
   `DocumentBlock.name`), `flow_instance.id="FLOW-BRIDGE-<slug>"` (deterministic).
4. **D3 — status→stage.** A single in-module mapping table from
   `(latest_token, has_prior_GO_in_chain)` → `(flow_status, current_stage_id,
   stage_index, stage_status)`, exactly the ADR D3 table, including the dual-`NEW`
   disambiguation (a `NEW` with a prior `GO` in chain is a post-impl report →
   `verify` pending; otherwise initial proposal → `review` pending).
5. **D4 — idempotent upsert.** Compute `derived_state_hash` over the canonical
   derived tuple `(flow_definition_id, subject_id, flow_status, current_stage_id,
   stage_index, latest_token, latest_version)`; store it in
   `flow_instance.metadata`. Upsert writes a new `flow_instance` version (via
   `insert_flow_instance`) **only when the hash differs** from the latest stored
   version (read via `get`/list helper) — else no-op. The matching current
   `stage_instance` is written under the same gate. No lock/lease is taken
   (shadow-view eventual convergence; strict serialization is WI-4510-era).
6. **CLI.** Add `gt flow ingest-bridge-threads` to the existing `flow` group in
   `cli.py`: **dry-run by default** (derive + report per-thread planned actions
   without writing), `--apply` to perform the idempotent upsert, `--json` for a
   machine-readable summary (`ingested`, `skipped`, `unchanged`, `written`).
   Reuses the existing `_flow_service`/INDEX-read pattern from the Slice A/B
   commands.

No change to `db.insert_*` semantics (idempotency lives in the ingestion layer
per ADR Alternative A4). No new table or column (ADR: no `kb_schema_change`).

## Verification Plan (Specification-Derived)

New test module `groundtruth-kb/tests/test_tafe_bridge_thread_ingest.py`.

| Spec / ADR clause | Test | Oracle |
|---|---|---|
| ADR D3 status→stage table | `test_status_token_maps_to_expected_stage` (parametrized over every token incl. both `NEW` cases) | each token derives the ADR-tabulated `(flow_status, stage, stage_status)` |
| ADR D3 dual-`NEW` disambiguation | `test_new_with_prior_go_is_post_impl_report` / `test_new_without_prior_go_is_initial_proposal` | chain with/without prior `GO` → `verify` vs `review` pending |
| ADR D2 subject derivation | `test_subject_and_flow_id_derived_from_slug` | `subject_type=="bridge_thread"`, `subject_id==slug`, `id=="FLOW-BRIDGE-<slug>"` |
| ADR D4 idempotency / replay | `test_reingest_unchanged_index_writes_zero_new_versions` | second `--apply` over identical INDEX text writes 0 new `flow_instance` versions |
| ADR D4 change detection | `test_changed_thread_status_writes_one_new_version` | a thread advancing `NEW`→`GO` writes exactly one new version with updated hash |
| ADR D1 advisory skip | `test_advisory_thread_skipped_and_reported` | an `ADVISORY`-latest thread is not ingested and appears in the `skipped` report |
| GOV-FILE-BRIDGE-AUTHORITY-001 / ADR scope | `test_module_never_writes_index_and_has_no_index_path_literal` | AST/source assertion: no `bridge/INDEX.md` literal, no write to the index path |
| CLI dry-run default | `test_cli_ingest_dry_run_default_writes_nothing` | `gt flow ingest-bridge-threads` (no `--apply`) leaves runtime tables unchanged |

Verification commands (run before the post-implementation report):
- `python -m pytest groundtruth-kb/tests/test_tafe_bridge_thread_ingest.py -q --tb=short`
- `python -m ruff check` and `python -m ruff format --check` on all three `target_paths` files.

## Risk / Rollback

- **Risk: low–moderate.** Additive module + one CLI command + tests; the write is
  gated by content-hash and confined to existing tables. The runtime view is
  explicitly shadow/non-authoritative, so a transiently stale row never corrupts
  canonical state (INDEX remains authoritative). The main correctness surface is
  the D3 mapping, which is fully table-tested including the dual-`NEW` case.
- **Rollback:** delete the new module + test and revert the `cli.py` command
  addition; no migration, no schema change, no canonical-state mutation. Any
  shadow `flow_instance` rows already written are non-authoritative and inert.

## Owner Decisions / Input

- **DELIB-DECISION-1219-SLICE-C-DRIVE-ADR-FIRST** (owner AUQ, this session):
  authorized driving Slice C ADR-first.
- **ADR approval AUQ** (this session, recorded in the
  `2026-06-14-ADR-TAFE-BRIDGE-THREAD-INGESTION-001.json` formal-artifact-approval
  packet, `approved_by=owner`): owner approved
  `ADR-TAFE-BRIDGE-THREAD-INGESTION-001` for insertion and authorized filing this
  implementation proposal under the cutover PAUTH for Loyal Opposition review.
- **DELIB-20263195** (cutover authorization): the cutover PAUTH whose allowed
  mutation classes (`dual_write`/`source`/`test_addition`/`config`) cover this
  proposal's scope.

## Recommended Commit Type

`feat:` — adds a new capability surface (the bridge-thread ingestion module and
the `gt flow ingest-bridge-threads` CLI command). Net-new modules + CLI, not a
repair of existing behavior.
