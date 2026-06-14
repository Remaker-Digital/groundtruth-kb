NEW

# gtkb-tafe-dual-write-slice-c (Slice 3) — TAFE bridge-document to flow_instances/flow_artifacts second-write ingestion

bridge_kind: prime_proposal
Document: gtkb-tafe-dual-write-slice-c
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-14 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: interactive-pb-2026-06-13-tafe-slice-c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4508

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_bridge_ingestion.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice C implements the TAFE "second write" governed by `ADR-TAFE-BRIDGE-SECOND-WRITE-INGESTION-001` (owner-approved 2026-06-13, `DELIB-TAFE-SLICE-C-ADR-APPROVAL-20260613`): an idempotent, on-demand ingestion that maps the canonical `bridge/INDEX.md` state into the TAFE `flow_instances` and `flow_artifacts` tables as a non-authoritative SHADOW store. This is the first TAFE write surface and the integrity prerequisite for the governed cutover (the downstream cutover-evidence and governed-cutover work in this project's Phase 6-7 sequence).

A new module `groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py` parses the canonical INDEX via the VERIFIED Slice A lossless parser (`tafe_index_sync.parse_bridge_index`), maps each `Document:` thread to one `implementation` `flow_instance` (`flow-bridge-<slug>`) plus one `flow_artifact` per version line (`fa-bridge-<slug>-<NNN>`), derives `flow_instances.status` from the thread's LATEST status token, and writes through the existing append-only `TypedArtifactFlowService` (`typed_artifact_flow.py`). The write is replay-safe: a per-thread sha256 fingerprint over the ordered (status, version) tuples gates flow_instance versioning, so re-ingesting an unchanged INDEX is a guaranteed no-op. A new CLI `gt flow ingest-bridge-index` (with `--dry-run` and `--json`) drives it. The canonical `bridge/INDEX.md` is read, never written.

## Specification Links

- `ADR-TAFE-BRIDGE-SECOND-WRITE-INGESTION-001` — the governing architecture decision (owner-approved). This proposal implements its four constraints D1-D4 (flow_definition selection, deterministic identity, status->flow-status mapping, replay-safe idempotence) and honors its Slice-C scope (flow_instances/flow_artifacts only, on-demand CLI, no auto-hook, no stage/event modeling).
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — the umbrella spec; the second-write is the dual-write step toward an authoritative generated INDEX.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (CLAUSE-INDEX-IS-CANONICAL) — `bridge/INDEX.md` remains authoritative; the ingestion reads it and writes nothing canonical (TAFE is a shadow).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all governing specs + WI + project + target_paths cited (header + this section).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable Project Authorization / Project / Work Item metadata present in the header.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — the declared work item is an active member of PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE under the cited Phase 6-7 cutover PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives a test per ADR constraint (mapping below).
- `GOV-STANDING-BACKLOG-001` — the declared work item is the backlog authority for the dual-write work.

## Prior Deliberations

- `DELIB-TAFE-SLICE-C-ADR-APPROVAL-20260613` — owner AUQ approving `ADR-TAFE-BRIDGE-SECOND-WRITE-INGESTION-001` (the design this proposal implements); the owner selected the implementation-flow-for-all default over kind-aware selection.
- `DELIB-20263195` — owner AUQ authorizing the Phase 6-7 cutover sequence (this slice's declared work item plus the downstream cutover-evidence and governed-cutover work) and the cutover PAUTH this proposal is filed under.
- Bridge `gtkb-tafe-dual-write-index-parity` (Slice A, VERIFIED) — provides the lossless `parse_bridge_index` this proposal consumes; its deferral comment for the "second write" is the direct predecessor of this work.
- Bridge `gtkb-tafe-dual-write-slice-b-oracle` (Slice B, VERIFIED) — the completeness oracle that, per the ADR, had to precede ingestion (resolves the earlier F2 finding).
- Bridge `gtkb-tafe-dual-write-slice-b-shadow-ingestion` (WITHDRAWN) — the earlier ingestion attempt NO-GO'd for missing the oracle (F2) and an idempotence contract (F3); ADR D4 + this proposal's idempotence tests resolve F3.

## Owner Decisions / Input

This proposal implements an owner-approved ADR; the authorizing owner evidence is `DELIB-TAFE-SLICE-C-ADR-APPROVAL-20260613` (AskUserQuestion 2026-06-13, owner answer "Approve as drafted") plus `DELIB-20263195` (cutover-sequence authorization + Phase 6-7 PAUTH). No further owner decision is required to implement within the ADR's scope; the irreversible governed cutover remains separately owner-AUQ-gated and is untouched by this slice.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-TAFE-BRIDGE-SECOND-WRITE-INGESTION-001` (constraints D1-D4 + Slice-C scope), `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, and the declared work item fully specify the second-write behavior. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

New tests in `groundtruth-kb/tests/test_tafe_bridge_ingestion.py`, executed with the repo venv interpreter:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_bridge_ingestion.py -q --no-header
```

| Spec / ADR constraint | Test(s) | Expected result |
|---|---|---|
| ADR D1 (flow_definition selection) | `test_thread_maps_to_implementation_flow_definition`; `test_advisory_thread_status_and_metadata` | every ingested instance has `flow_definition_id='implementation'`; a thread whose latest token is ADVISORY -> `status='advisory'`, `metadata.bridge_kind='advisory'` |
| ADR D2 (deterministic identity) | `test_deterministic_instance_and_artifact_ids` | instance id `flow-bridge-<slug>`; artifact ids `fa-bridge-<slug>-<NNN>` with `artifact_type='bridge_version'`, `artifact_ref='bridge/<slug>-NNN.md'` |
| ADR D3 (status-token -> flow status) | `test_status_token_to_flow_status_mapping` (parametrized: NEW/REVISED/GO/NO-GO/VERIFIED/WITHDRAWN/ADVISORY/DEFERRED/unknown) | `flow_instances.status` equals the ADR D3 mapping for each latest token |
| ADR D4 (replay-safe idempotence) | `test_reingest_unchanged_index_is_noop`; `test_state_change_appends_one_version` | second ingest of an unchanged INDEX snapshot -> 0 new flow_instance versions and 0 new flow_artifacts; a changed latest-status -> exactly 1 new flow_instance version |
| ADR scope (flow_instances/flow_artifacts only) | `test_no_stage_instances_or_events_written` | ingestion creates no `stage_instances` and no `flow_events` rows |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_ingestion_does_not_write_canonical_index` | `bridge/INDEX.md` bytes are unchanged across an ingest run (canonical read-only) |

Lint/format gates (run and reported in the post-implementation report, per the pre-file code-quality gate):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_bridge_ingestion.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_bridge_ingestion.py
```

## Risk / Rollback

Risk 1 — canonical integrity: none. The ingestion reads `bridge/INDEX.md` and writes only the TAFE shadow tables; there is no canonical write surface (reuses the Slice A/B read-only guard intent). The Slice B completeness oracle independently detects any lost block before any cutover relies on the shadow.

Risk 2 — idempotence regression: a future change to the fingerprint or id derivation could break replay-safety. Mitigated by the D4 tests (`test_reingest_unchanged_index_is_noop`), which fail loudly on any non-idempotent write.

Risk 3 — TAFE write volume: bounded. At most one flow_instance version per thread per real state change, and insert-if-absent artifacts; an unchanged INDEX writes nothing.

Rollback: single-commit revert. Delete the new module + test and revert the additive `cli.py` subcommand; there is no schema change, no canonical-state change, and no migration to undo. Any shadow rows already written are inert (non-authoritative) and may be left in place or pruned.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-tafe-dual-write-slice-c` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` — adds a net-new ingestion module (`tafe_bridge_ingestion.py`) and a net-new `gt flow ingest-bridge-index` CLI subcommand (TAFE's first write surface), plus its test suite.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
