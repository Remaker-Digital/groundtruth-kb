NEW

bridge_kind: implementation_proposal
Document: gtkb-tafe-dual-write-slice-b-shadow-ingestion
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dfc088ac-2d2c-4b3e-8117-6e5ed57469e8
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4508
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_ingest.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_ingest.py"]

# Implementation Proposal — WI-4508 Slice B: Shadow Bridge→TAFE Ingestion + Structural Parity

## Summary

WI-4508 ("Dual-write mode: TAFE authoritative + generated INDEX.md; validate
parity") is the Phase-6 step of the owner-authorized TAFE cutover
(DELIB-20263195). Slice A (`gtkb-tafe-dual-write-index-parity`, VERIFIED -007)
delivered the lossless canonical-INDEX parser/serializer + text-observable
diagnostics. **Slice B (this proposal)** delivers the first half of dual-write:
**shadow ingestion** of canonical bridge state into TAFE flow/stage records (the
"second write", to TAFE tables only) plus a **structural parity** check proving
TAFE faithfully represents the canonical bridge state.

Slice B is **shadow-first and concurrency-safe**: it reads `bridge/INDEX.md`
**read-only** (via the Slice A parser) and writes **only** to the TAFE
flow_instances/stage_instances tables. It introduces **no** canonical
`bridge/INDEX.md` writer, so it adds zero risk to the bridge surface that
multiple sessions are concurrently writing.

Explicitly **deferred** (NOT in this slice): the reverse direction —
authoritative TAFE→canonical-INDEX generation (a later slice) — and the
governed cutover making TAFE canonical (WI-4510, owner-AUQ-gated).

## Specification Links

- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — TAFE foundation; the dual-write
  + parity prerequisite for cutover. This slice realizes the ingestion + parity
  half.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` remains canonical and is
  read **only**; this slice exposes no canonical-INDEX write surface.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — all governing
  specs cited.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — every named test has a
  real oracle (below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — phased TAFE artifacts
  (Slice A done; Slice B here; TAFE→INDEX generation + cutover deferred).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — explicit deferral of the
  reverse-generation slice and the cutover.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision, PAUTH,
  work item, spec, and test artifacts linked + traceable.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA +
WI-4508 + DELIB-20263195 govern this work; no new/revised requirement needed for
Slice B.

## Prior Deliberations

- **DELIB-20263195** — owner AUQ authorizing the full TAFE cutover sequence
  WI-4508 → WI-4509 → WI-4510 + the bounded PAUTH.
- **bridge/gtkb-tafe-dual-write-index-parity-007.md** — VERIFIED Slice A
  (lossless parser foundation this slice builds on).
- **bridge/gtkb-tafe-bridge-index-preview-004.md** — VERIFIED WI-4507
  compatibility-view renderer (TAFE→preview shape; reused for the parity view).
- **DELIB-BRIDGE-DISPATCH-OVERHAUL-D1/D3-20260612** — TAFE project formation.

_No prior deliberation proposes a bridge→TAFE ingestion mapping; this is the
first treatment of the second-write direction._

## Design (Slice B)

New module `groundtruth-kb/src/groundtruth_kb/tafe_index_ingest.py`:

1. `ingest_bridge_index(parsed: ParsedBridgeIndex, service: FlowRuntimeService, *, changed_by, flow_definition_id) -> IngestResult`:
   - Input is the Slice A `parse_bridge_index(index_text)` result (canonical INDEX
     parsed losslessly — READ-ONLY on canonical).
   - For each `DocumentBlock` → `service.create_flow_instance(subject_type="bridge_thread", subject_id=<slug>, flow_definition_id=<bridge-thread def>, status=<latest version status>, ...)`.
   - For each version line (status, path) → `service.create_stage_instance(flow_instance_id=<flow id>, stage_id=<path>, stage_index=<version NNN parsed from path>, status=<bridge status token>, required_role=<derived>, ...)`. `stage_index` accepts any non-negative int, so the open-ended bridge version count maps directly (no fixed stage_sequence constraint is violated — `create_stage_instance` validates only `stage_index >= 0`).
   - `required_role` derivation: NEW/REVISED → `prime-builder`; GO/NO-GO/VERIFIED/ADVISORY/DEFERRED/WITHDRAWN → `loyal-opposition` (verdict/terminal statuses).
   - A `bridge-thread` flow_definition is defined once (idempotent) via `FlowDefinitionService.define` with a status-token stage vocabulary; reused across ingests.
   - Writes ONLY to TAFE tables (flow_instances/stage_instances). No canonical INDEX write.
2. `parity_report(parsed: ParsedBridgeIndex, service: FlowRuntimeService, *, flow_definition_id) -> ParityReport`:
   - Reads back the ingested TAFE state (`list_flow_instances` + `list_stage_instances`) and compares **structurally** to the canonical parsed index: every canonical `Document` has a matching flow_instance (by subject_id); every canonical version line has a matching stage_instance (by stage_index + status). Reports per-document and per-version match/mismatch counts + a boolean `in_parity`.
3. Read-only CLI `gt flow ingest-parity` in `cli.py`: ingest the live canonical INDEX into a TAFE scratch/shadow scope, run `parity_report`, print a human/`--json` summary, exit non-zero on any parity mismatch. No canonical-INDEX write; refuses any canonical-index output target (reuses the Slice A guard intent).

## Verification Plan (Specification-Derived)

New tests in `groundtruth-kb/tests/test_tafe_index_ingest.py` (isolated in-memory/temp KnowledgeDB fixture; pattern from the Slice A + TAFE runtime tests):

| Spec / Acceptance criterion | Test | Oracle / Method |
|---|---|---|
| SPEC-TAFE-UMBRELLA — ingestion: Document→flow | `test_ingest_creates_flow_per_document` | parse a multi-doc fixture; assert one flow_instance per Document with matching subject_id |
| SPEC-TAFE-UMBRELLA — ingestion: version→stage | `test_ingest_creates_stage_per_version_with_index` | assert one stage_instance per version line, stage_index == parsed NNN, status == bridge token |
| required_role derivation | `test_required_role_derivation` | NEW/REVISED→prime-builder; GO/NO-GO/VERIFIED→loyal-opposition |
| parity: faithful ingest is in-parity | `test_parity_report_in_parity_after_clean_ingest` | ingest fixture; `parity_report().in_parity is True`; counts match |
| parity: injected mismatch detected | `test_parity_report_detects_missing_stage` | drop/alter one ingested stage; assert `in_parity is False` with the specific mismatch |
| GOV-FILE-BRIDGE-AUTHORITY-001 — no canonical write | `test_module_has_no_canonical_index_write_surface`, `test_ast_no_index_write` | AST/behavioral: no write to bridge/INDEX.md; module holds no canonical-index path write |
| CLI read-only contract | `test_cli_ingest_parity_json`, `test_cli_refuses_canonical_write_target` | invoke `gt flow ingest-parity --json`; assert read-only + guard |
| Round-trip vs real INDEX (smoke) | `test_ingest_parity_on_live_index_snapshot` | ingest a snapshot of the live INDEX; assert in-parity (TAFE faithfully represents real bridge state) |

Pre-file gates: `python -m ruff check` + `ruff format --check` on the 3 changed
files; `python -m pytest groundtruth-kb/tests/test_tafe_index_ingest.py -q`.

## Risk / Rollback

- **Risk:** low–moderate. The second write targets TAFE tables only; canonical
  `bridge/INDEX.md` is read-only, so no concurrency risk to the bridge surface.
  Worst case is incorrect TAFE shadow state or a false parity signal, surfaced
  via the read-only CLI/tests — never a canonical corruption.
- **Concurrency:** no canonical writer introduced; the multi-session INDEX-write
  surface is untouched.
- **Rollback:** delete the new module + CLI command + test file; the TAFE shadow
  rows are non-authoritative and can be cleared; no canonical/migration change.

## Owner Decisions / Input

- **DELIB-20263195** (owner AUQ, 2026-06-13): owner authorized the full TAFE
  cutover sequence (WI-4508→4509→4510) + the bounded PAUTH
  `PAUTH-…-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510` (allows dual_write /
  authoritative_generated_view / source / test_addition / config; forbids the
  irreversible cutover op, which remains WI-4510's owner-AUQ gate). Slice B is
  within the authorized dual-write scope; it does NOT perform cutover.
- No further owner decision required for Slice B.

## Recommended Commit Type

`feat:` — net-new ingestion module + CLI + tests (the TAFE second-write +
structural-parity capability).
