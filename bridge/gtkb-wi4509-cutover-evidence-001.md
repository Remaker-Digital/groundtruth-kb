NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4509-cutover-evidence
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
Work Item: WI-4509

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_cutover_evidence.py"]

# Implementation Proposal (NEW -001) — WI-4509: TAFE Cutover Evidence Gathering

## Summary

WI-4509 ("Cutover evidence gathering", PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE /
Phase-7-Governed-Cutover) collects the evidence the governed cutover (WI-4510,
owner-AUQ-gated) needs to decide whether the TAFE shadow store may become
authoritative. With Slice C (WI-4508) VERIFIED, the shadow is now populated by
`gt flow ingest-bridge-index` (`tafe_bridge_ingestion.ingest_bridge_index` →
`flow_instances` + per-version `flow_artifacts`). This proposal adds a
**read-only** evidence-gathering tool that compares the deterministic ingest
**plan** against the canonical `bridge/INDEX.md` and emits a structured cutover
evidence report covering the four categories WI-4509 names: parallel-run parity,
flow completion rates, contention-zero (idempotence), and compatibility-view
fidelity.

New module `groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py` works off
the Slice C dry-run plan (`ingest_bridge_index(..., apply=False)`) — which derives
the full shadow representation from `index_text` **without writing** — and the
VERIFIED Slice B completeness oracle
(`tafe_index_completeness.index_completeness_report`). It mutates nothing
canonical and nothing in the shadow; a new read-only CLI
`gt flow cutover-evidence` (`--json`, optional evidence-dir output) drives it.
`bridge/INDEX.md` remains authoritative (`GOV-FILE-BRIDGE-AUTHORITY-001`).

**Dependency rewiring:** WI-4509's recorded `depends_on_work_items` lists the
**superseded** WI-4496 plus WI-4508. WI-4508 (Slice C) is VERIFIED and supplies
the shadow this evidence rests on; the WI-4496 dependency is obsolete. The
implementation updates WI-4509's dependency to WI-4508 (dropping the superseded
WI-4496) as part of this work.

## Specification Links

- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — WI-4509 is the tracked
  evidence-gathering artifact that gates the Phase-7 governed cutover (WI-4510).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — the superseded WI-4496
  dependency and the deferred cutover (WI-4510) are handled by name.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision
  (DELIB-20263195), the canonical ADR, WI-4509, and the derived tests are linked.
- **ADR-TAFE-SLICE-C-INGESTION-001** — the canonical Slice C design whose shadow
  (flow_instances + flow_artifacts, D1–D4 derivation) this evidence assesses; the
  parity/fidelity checks are defined against its D1/D2/D3 derivation contract.
- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — the umbrella spec; the cutover
  is the dual-write program's terminal step.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` stays authoritative; the
  evidence tool is read-only and writes nothing canonical or shadow.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — all governing specs cited.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each named test derives
  from an evidence-category requirement and has a real oracle (mapping below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` in-root; the
  evidence output dir is under `.gtkb-state/` (regenerable, non-canonical).

## Requirement Sufficiency

Existing requirements sufficient. WI-4509's description ("parallel-run parity
evidence, flow completion rates, contention-zero evidence, and compatibility-view
fidelity for cutover proposal") plus `ADR-TAFE-SLICE-C-INGESTION-001` (the shadow
derivation being evidenced) and `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` fully
specify the evidence behavior. The cutover PAUTH (`DELIB-20263195`) authorizes
the `source`/`test_addition`/`config` mutation classes. No new requirement needed.

## Prior Deliberations

- **DELIB-20263195** — owner AUQ authorizing the WI-4508→WI-4509→WI-4510 cutover
  sequence + the PAUTH this proposal is filed under.
- **DELIB-DECISION-1219-SLICE-C-RECONCILE-CONSOLIDATE** and
  **DELIB-DECISION-1219-SLICE-C-DRIVE-ADR-FIRST** — the owner decisions that
  produced ADR-TAFE-SLICE-C-INGESTION-001 (VERIFIED shadow this evidence rests on).
- `bridge/gtkb-tafe-slice-c-ingestion-consolidated` (VERIFIED) — the Slice C
  ingestion (`tafe_bridge_ingestion.py`) whose plan this tool consumes.
- `bridge/gtkb-tafe-dual-write-slice-b-oracle` (VERIFIED) — the completeness
  oracle (`tafe_index_completeness.py`) integrated for lost/extra-block evidence.
- `bridge/gtkb-tafe-dual-write-index-parity` (Slice A, VERIFIED) — the lossless
  parser underpinning the whole chain.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` — WI-4509's source owner directive
  (Bridge & Dispatch Architecture Overhaul, Phase-7 governed cutover).

## Design

New module `groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py`, pure and
read-only (no canonical write, no shadow write, no index path literal — it
receives `index_text`):

`gather_cutover_evidence(index_text, service, *, project_root) -> CutoverEvidenceReport`:

1. **Parallel-run parity.** Compute the Slice C plan
   `ingest_bridge_index(index_text, service, apply=False)`. Assert, per thread:
   one `flow-bridge-<slug>` instance derived per INDEX `Document:` block; one
   `fa-bridge-<slug>-<NNN>` artifact per INDEX version line; the derived
   `flow_status` equals `derive_flow_status(latest_token, has_prior_go)` per ADR
   D3. Report counts (`index_threads`, `index_version_lines`, `derived_instances`,
   `derived_artifacts`) and a `parity_mismatches` list (expected empty).
2. **Completeness.** Run `index_completeness_report(index_text, project_root)`
   (Slice B). Surface `lost_blocks` / `extra_blocks` (expected empty) into the
   report — threads present on disk but absent from INDEX, or vice versa.
3. **Contention-zero (idempotence).** Read the plan's `instance_action`
   distribution (`created`/`updated`/`unchanged`). For a shadow already populated
   from the current INDEX, every thread is `unchanged` (fingerprint match), so
   `instances_written == 0` and `artifacts_written == 0` on a re-plan — the
   replay-safe contention-zero property. The report records the action
   distribution and the re-plan write counts; the canonical idempotence proof is
   Slice C's VERIFIED `test_reingest_unchanged_index_is_noop`, cited here.
4. **Flow completion rates.** Tabulate the derived `flow_status` distribution
   across all threads (complete / in_review / in_verification / in_implementation
   / in_revision / withdrawn / advisory / deferred / unknown) — the flow
   completion view the cutover proposal reports.
5. **Compatibility-view fidelity.** For each thread, confirm the shadow can
   reconstruct the canonical INDEX latest-status: the latest `flow_artifact`'s
   `status_token` and the derived `flow_status` correspond to the INDEX latest
   version line. Report `fidelity_mismatches` (expected empty).

`CutoverEvidenceReport` is a frozen dataclass with `as_dict()` (JSON-serializable)
and an `ok` property (all mismatch lists empty, no lost/extra blocks). A
`gt flow cutover-evidence` CLI command on the existing `flow` group reads the
canonical INDEX through the same guarded read the Slice A/B/C `flow` commands use,
runs `gather_cutover_evidence`, emits `--json`, and (optionally) writes a
`<run_id>` JSON + markdown summary under `.gtkb-state/cutover-evidence/` (a
regenerable benchmark output, non-canonical). Read-only: no `--apply`, no writes
to canonical state or the shadow tables.

No change to `tafe_bridge_ingestion.py` or `db.insert_*` semantics; the tool
consumes the existing dry-run plan + oracle.

## Verification Plan (Specification-Derived)

New `groundtruth-kb/tests/test_tafe_cutover_evidence.py` (synthetic in-memory
INDEX fixtures + a `TypedArtifactFlowService` against a temp DB):

| Evidence category / spec | Test | Oracle |
|---|---|---|
| Parity (ADR D1/D2/D3 derivation) | `test_parity_one_instance_per_thread_one_artifact_per_version` | derived_instances == index_threads; derived_artifacts == index_version_lines; `parity_mismatches == []` |
| Parity — mismatch detection | `test_parity_mismatch_detected` | an injected derivation gap (e.g., a malformed/empty block) surfaces in `parity_mismatches` / `threads_skipped` |
| Completeness (Slice B integration) | `test_completeness_surfaces_lost_and_extra_blocks` | a lost block (on disk, absent from INDEX) and an extra block appear in the report |
| Contention-zero / idempotence (ADR D4) | `test_contention_zero_repeat_plan_writes_nothing` | after apply, a re-plan over the same INDEX → instances_written == 0, artifacts_written == 0; action distribution all `unchanged` |
| Flow completion rates | `test_flow_completion_rate_distribution` | the `flow_status` distribution counts match a fixture with known token mix (incl. dual-`NEW` → in_verification vs in_review) |
| Compatibility-view fidelity | `test_compatibility_view_round_trips_index_latest_status` | each thread's latest artifact `status_token` + `flow_status` reconstruct the INDEX latest line; `fidelity_mismatches == []` |
| Fidelity — mismatch detection | `test_fidelity_mismatch_detected` | an injected shadow/INDEX divergence surfaces in `fidelity_mismatches` |
| CLI read-only + report shape | `test_cli_cutover_evidence_readonly_json` | `gt flow cutover-evidence --json` emits the report, writes nothing canonical/shadow, and `report.ok` is True for a clean fixture |

Commands (run before the post-implementation report):
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_cutover_evidence.py -q --tb=short`
- `python -m ruff check` and `python -m ruff format --check` on all three `target_paths`.

## Risk / Rollback

- **Risk: low.** Additive read-only module + one read-only CLI command + tests; it
  consumes the VERIFIED Slice C plan + Slice B oracle and writes only regenerable
  evidence under `.gtkb-state/`. No canonical or shadow mutation; the cutover
  itself (WI-4510) is separate + owner-gated.
- **Rollback:** delete the new module + test and revert the additive `cli.py`
  command; the WI-4509 dependency-field rewiring (drop superseded WI-4496) is a
  backlog metadata update reversible via a further `gt backlog`/work-item update.
  No schema change, no canonical/shadow state change.

## Owner Decisions / Input

- **DELIB-20263195** (owner AUQ): authorizes the WI-4508→WI-4509→WI-4510 cutover
  sequence and the PAUTH (`...-CUTOVER-WI-4508-4509-4510`) covering WI-4509's
  `source`/`test_addition`/`config` scope. No further owner decision is required
  to gather evidence; the irreversible governed cutover (WI-4510) remains
  separately owner-AUQ-gated and is untouched by this work.

## Recommended Commit Type

`feat:` — adds a net-new read-only evidence module (`tafe_cutover_evidence.py`)
and a net-new `gt flow cutover-evidence` CLI subcommand + tests.
