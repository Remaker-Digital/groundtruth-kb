NEW

# Defect-Fix Proposal - WI-5257 Compact Live Dispatch Attribution

bridge_kind: prime_proposal
Document: gtkb-wi5257-compact-live-dispatch-attribution
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: Codex Desktop 2026-07-15
author_model_configuration: Interactive Codex Prime Builder; transcript override ::init gtkb pb; governed fleet stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5257-COMPACT-ATTRIBUTION-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5257

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Restore bridge-document and work-item attribution in the bounded compact dispatcher report. During genuine H dispatch `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0`, canonical launch state and `document_lease_handles` identified `gtkb-modernization-wi5163-shadow-evaluation`, but `gt bridge dispatch report --json --compact` emitted `bridge_document: null` and `work_item_id: null` for the live run.

The full report already loads the canonical dispatch state into `live_state.recipients`, including per-recipient launch ledgers, last-launch compatibility records, selected documents, selected top files, primary bridge IDs, and document lease handles. The compact projection currently ignores that evidence and constructs in-flight records from run files alone. This forces operators to inspect runtime JSON directly to identify substantive work, making collision detection, proof attribution, and cost estimation harder.

The repair will correlate each bounded live/stale/unknown run with its launch record, derive one deterministic primary bridge document from canonical launch/lease metadata, and resolve its `Work Item` through the existing numbered-bridge metadata reader. The report remains read-only, bounded, and null-preserving when attribution is genuinely unavailable.

## Defect Evidence And Causal Boundary

- Genuine dispatch: `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0`.
- Canonical launch evidence: the matching launch record carried a document lease whose `doc_slug` was `gtkb-modernization-wi5163-shadow-evaluation`.
- Compact output: the in-flight row identified the dispatch and recipient but emitted null document and work-item fields.
- `build_bridge_dispatch_report` already returns canonical recipient state under `live_state.recipients`.
- `_workflow_in_flight` iterates `history.recent_runs` and hardcodes both attribution fields to `None`; it does not consult the recipient launch ledger or last-launch record.
- `_read_workflow_bridge_metadata` already resolves `Work Item`, project, and PAUTH metadata across the numbered bridge chain and can be reused without a second parser.

This proposal changes only the compact read projection. It does not change launch recording, leases, queue actionability, dispatch selection, worker lifecycle, telemetry, or bridge status.

## Proposed Implementation

1. Pass the resolved project root into `_workflow_in_flight` so attribution can reuse the existing bridge metadata reader without global state or a second filesystem authority.
2. Build a bounded lookup from `report["live_state"]["recipients"]` that indexes canonical launch-ledger records by nonblank `dispatch_id`. Include the compatibility `last_launch` record only when its dispatch ID is not already represented by the ledger.
3. For each live/stale/unknown recent run, find the exact launch record by dispatch ID. Do not match by timestamp prefix, recipient alone, PID alone, or current `last_launch` when IDs differ.
4. Derive the primary bridge document deterministically. Prefer the launch's explicit `primary_bridge_id` when it is among the launch's lease-backed or selected documents; otherwise prefer the first valid `document_lease_handles[].doc_slug`; then fall back to the first valid `selected_documents` or legacy `document_names` entry. Normalize only surrounding whitespace and reject non-string/blank values.
5. Preserve multi-document truth without pretending the run is singularly attributed to an unrelated document. The compact schema remains singular and reports the launch's declared primary document; when no declared primary exists, it uses the first canonical lease/selection order already recorded by the dispatcher.
6. Resolve `work_item_id` by feeding the selected document into `_read_workflow_bridge_metadata`, which scans the current numbered chain and extracts the governed `Work Item` header. Do not infer a WI from slug text.
7. Emit `bridge_document` even when work-item metadata is absent, and emit `work_item_id: null` only when the numbered bridge chain has no resolvable governed Work Item header.
8. Retain nulls for missing/malformed launch metadata, unmatched dispatch IDs, or genuinely unavailable bridge metadata. Reporting must not synthesize ownership or mutate runtime state to fill gaps.
9. Preserve `WORKFLOW_RECORD_LIMIT`, ordering, truncation flags, recipient derivation, recent-run state classification, queue categories, metrics, and human-readable formatting.

## Explicit Exclusions

- No read or write of dispatcher runtime JSON outside the existing full-report reader.
- No dispatcher config, launch ledger, lease, lock, eligibility, role, model, routing, allowance, or telemetry mutation.
- No bridge artifact creation, rewrite, status change, or WI inference from filenames.
- No direct harness/provider contact and no worker disturbance.
- No schema expansion to unbounded prompt, tool, stdout, stderr, or cost payloads.
- No source changes outside the two declared paths.
- No staging, commit, push, deployment, release, destructive cleanup, or unrelated worktree mutation by this proposal.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the central service must expose auditable per-dispatch recipient and work attribution.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - canonical status/report controls must expose sufficient bounded operational state without direct runtime-file inspection.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch envelope identity and selected work must remain correlated in reporting.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Work Item attribution comes from the numbered bridge chain, not a parallel queue or filename inference.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before protected implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires deterministic report regressions before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to its PAUTH, project, WI, and exact targets.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires live authorization checks at claim and implementation start.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace independent GO, claim, start authorization, report, or verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the observed reporting defect as a durable correction chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links incident evidence, WI/test, PAUTH, proposal, implementation, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the observed defect to advance through the governed lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and evidence in-root under `E:/GT-KB`; the filed bridge artifact remains under `E:/GT-KB/bridge`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to file through the governed non-bypass helper.
- `GOV-STANDING-BACKLOG-001` - keeps compact-report attribution visible until independently verified.

## Prior Deliberations

- `DELIB-202666173` - owner directive to verify A/B/C/D/F/H through genuine governed dispatcher work and correct every discovered defect.
- `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-004.md` - independently VERIFIED predecessor establishing the per-dispatch launch ledger as concurrent runtime evidence.
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md` - independently VERIFIED predecessor establishing selected-document and lease-backed per-document semantics.
- `bridge/gtkb-wi5181-report-metrics-enrichment-004.md` - compact-report predecessor establishing bounded operator-facing workflow reporting.

These records govern the existing data source and report boundary; unrelated harness recovery threads were excluded.

## Owner Decisions / Input

`DELIB-202666173` authorizes correction of dispatcher defects discovered during the active fleet proof program. Mike has directed that manual interactive PB/LO work continue despite automated bridge health, so this read-only reporting proposal does not reconfigure or pause any lane.

## Requirement Sufficiency

Existing requirements are sufficient. The centralized dispatcher, control-surface, dispatch-envelope, and bridge-authority specifications already require bounded auditable attribution. The defect is a projection omission, not a missing requirement.

## Spec-Derived Verification Plan

| Requirement | Deterministic verification |
| --- | --- |
| Exact launch correlation | Seed two launch-ledger records for the same recipient and a live run matching only one dispatch ID; assert attribution comes from the exact matching launch. |
| Lease-backed document | Seed a matching launch with `document_lease_handles=[{"doc_slug":"live-thread"}]`; assert compact JSON emits `bridge_document="live-thread"`. |
| Work Item resolution | Seed the numbered `live-thread` bridge chain with `Work Item: WI-7001`; assert compact JSON emits `work_item_id="WI-7001"`. |
| Metadata-null preservation | Omit the Work Item header while retaining a valid lease document; assert the document is present and only the WI remains null. |
| Launch-null preservation | Provide a live run with no exact ledger/last-launch match; assert both attribution fields remain null. |
| Compatibility fallback | Seed only a matching legacy `last_launch` with selected-document metadata; assert bounded attribution still resolves. |
| Primary multi-document semantics | Seed multiple lease/selected documents and an explicit valid primary; assert the declared primary is emitted. When primary is absent, assert first canonical order is used. |
| No slug inference | Use a document slug containing a WI-like token but no governed Work Item header; assert `work_item_id` remains null. |
| Bounds and ordering | Re-run compact workflow limit/truncation tests and assert no additional unbounded records or fields are introduced. |
| Focused suite | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short` passes. |
| Static quality | Targeted Ruff lint/format and `git diff --check` pass on the two declared paths. |
| Governance | Applicability, clause, and target-coverage preflights pass; implementation begins only after independent GO plus matching claim/start authorization. |

## Risk / Rollback

Risk is limited to compact report attribution and fixture expectations. Exact dispatch-ID matching and null-preserving fallbacks prevent cross-launch contamination. The report remains read-only and bounded. If the focused change regresses compact output, revert the focused commit through a separately governed change; do not restore direct runtime-file inspection as an operator requirement.

## Bridge Filing

This proposal is filed as the first status-bearing numbered file for `gtkb-wi5257-compact-live-dispatch-attribution`. It does not overwrite another thread. Dispatcher/TAFE state plus the append-only numbered bridge chain remain the live workflow surfaces.

## Recommended Commit Type

`fix` - restores truthful bounded dispatcher reporting.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
