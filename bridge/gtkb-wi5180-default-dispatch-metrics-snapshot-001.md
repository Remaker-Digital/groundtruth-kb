NEW

# Canonical default dispatch metrics events and deterministic bounded snapshots

bridge_kind: prime_proposal
Document: gtkb-wi5180-default-dispatch-metrics-snapshot
Version: 001
Author: Prime Builder / Codex
Date: 2026-07-11 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated session document
author_metadata_source: validated harness-state/codex/session-envelopes session document plus Codex runtime context

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5180-DEFAULT-METRICS-20260711
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5180

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/groundtruth_kb/test_dispatch_default_metrics.py"]

implementation_scope: source | test_addition | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the approved `gtkb.dispatch_default_metric_event.v1` and `gtkb.dispatch_default_metrics_snapshot.v1` substrates as one canonical MemBase-backed event/snapshot authority. The new projection module will normalize only allowlisted observational fields from approved WI-5173 telemetry and existing benchmark evidence, then construct deterministic, source-window-bounded snapshots with explicit provenance, freshness, and coverage.

This slice is intentionally not a report command and does not modify dispatch behavior. It provides the canonical snapshot data later consumed by WI-5181 and evaluated by WI-5182, without creating a competing metrics store or silently tuning production dispatch.

## Specification Links

- `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` - controls event/snapshot schemas, MemBase authority, null semantics, privacy, bounded deterministic aggregation, and acceptance tests.
- `SPEC-HARNESS-OBSERVABILITY-SELF-TUNING-PROGRAM-001` - keeps this child observational, independent, and separate from later report enrichment and advisory tuning.
- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - constrains the safe WI-5173 telemetry fields that may be read as an evidence source.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - require PAUTH, independent GO, a matching claim, and implementation-start evidence before protected edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed, spec-derived verification before independent VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve evidence lineage without conflating metrics capture with approval to alter dispatch.

## Prior Deliberations

- `DELIB-202666085` - owner approval of the bounded WI-5180 PAUTH.
- `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` - owner-approved child specification defining this exact data contract.
- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` and terminal WI-5173 evidence - the permissible telemetry input is privacy-bounded and nullable by contract.

## Owner Decisions / Input

- `DELIB-202666085` records `Approve WI-5180 PAUTH`.
- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5180-DEFAULT-METRICS-20260711` authorizes only this proposal and, after ordinary gates, the three declared source/test paths.
- Protected implementation remains blocked until an independent Loyal Opposition GO, matching work-intent claim, and implementation-start packet are live.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` fully specifies canonical authority, schema behavior, coverage/null semantics, privacy exclusions, source bounds, cost-label separation, and acceptance criteria. The PAUTH excludes provider calls, sensitive-content capture, dispatcher/role/claim/production mutation, report enrichment, advisory tuning, automatic tuning, configuration, deployment, destructive operations, and competing stores.

## Spec-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Event schema and idempotency | Validate allowlisted event input, immutable provenance, schema ID, and repeated event handling without a competing write path. |
| Canonical persistence | Assert events and snapshots reside in the one versioned MemBase authority and derived payloads do not become a second store. |
| Bounded deterministic snapshots | Feed stable source records in different insertion orders; assert identical bounded snapshots, source windows, record counts, distributions, freshness, and coverage. |
| Null and cost semantics | Assert unknown usage/cost remains `null`, observed zero remains zero, and provider-reported versus benchmark-estimated cost remains separately labeled. |
| WI-5173 and benchmark integration | Project only safe telemetry and evidence references; verify absent, partial, or stale inputs yield explicit coverage/unavailable metadata. |
| Privacy and safety | Scan event/snapshot serializations for prohibited prompt/message/tool/provider/credential/environment content; assert no provider call, dispatcher config mutation, or production-state mutation. |

Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_dispatch_default_metrics.py -q --tb=short`. Run `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check` over the three declared Python paths.

## Risk / Rollback

- Risk: raw source evidence leaks through a generic serializer. Mitigation: build events and snapshots from an explicit primitive allowlist and run prohibited-content tests.
- Risk: a missing measurement becomes a false zero or mixed cost number. Mitigation: normalize unknown values to `null`, retain coverage/unavailable reasons, and label cost sources separately.
- Risk: a second metrics store or report surface emerges. Mitigation: persist only canonical MemBase rows; exports remain derived and report enrichment is excluded by PAUTH.
- Risk: metrics alter production dispatch. Mitigation: no dispatcher/configuration mutation API is called or exposed; assert the relevant state is unchanged in tests.
- Rollback: revert the single implementation commit; no selection, ranking, routing, role, claim, configuration, or production transition requires reversal.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5180-default-dispatch-metrics-snapshot`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` - adds the approved canonical observational metrics and snapshot substrate without operational actuation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
