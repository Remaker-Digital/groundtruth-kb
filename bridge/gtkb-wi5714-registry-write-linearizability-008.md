GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# WI-5714 Registry Write Linearizability — GO

bridge_kind: lo_verdict
Document: gtkb-wi5714-registry-write-linearizability
Version: 008
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5714-registry-write-linearizability-007.md
Reviewed proposal: bridge/gtkb-wi5714-registry-write-linearizability-007.md

## Verdict Summary

**GO.** Version 007 closes both version-006 findings without changing the
approved generation-CAS mechanism, two-file scope, retry budget, or residual
work boundary. It correctly distinguishes durable operation-time proof from
controls that are expected to expire as the bridge moves from GO to NEW.

## Finding Closure

| Finding | Result | Evidence |
| --- | --- | --- |
| Version-006 F1: terminal verifier requires expired controls to remain live | Closed | The report must capture live claim/start-packet validity at mutation/report time; terminal review validates that durable evidence and freshly rechecks mutable canonical state without demanding current liveness of expired controls. |
| Version-006 F2: stale chain references | Closed | Lifecycle verification now names v001–v005 plus v006 and v007, and accurately identifies v007 as the REVISED proposal awaiting independent GO. |

The deterministic four-process barrier test, exact conflict subclass,
eight-attempt bound, retry taxonomy, coherent parity checks, and WI-5736 /
TEST-11748 residual boundary all remain intact.

## Implementation Conditions

This GO is limited to:

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`

Before protected edits, acquire a fresh exact-session claim and matching
implementation-start packet. The implementation report must preserve durable
operation-time authorization evidence and rerun the specified tests; terminal
verification must independently validate that evidence and rerun live mutable
state/parity checks. Do not retry non-conflict exceptions or widen into
registration/bootstrap writers assigned to WI-5736.

## Prior Deliberations

- `DELIB-202667517` — owner requirement for linearizable or
  conflict-detected shared-control-plane writes.
- `DELIB-202667522` — exact WI-5714 authorization for the generation-CAS
  repair, bounded retries, and deterministic Windows-spawn coverage.
- `DELIB-2521` — freshness authority distinguishing current reads from dated
  observations.

No deliberation contradicts the bounded design.

## Review Independence

Version 007 declares author session
`019f9329-a174-7763-8f7e-29679f39e6bd`; this Loyal Opposition review uses
`019fac54-c55c-75c0-8332-d7fdaf03b20a`. Metadata is readable and the contexts
are distinct.

## Methodology Trail

Read the numbered bridge chain through version 007, including the controlling
NO-GO-006. Reviewed the revised lifecycle evidence rules, ran both mandatory
preflights, and searched the Deliberation Archive for linearizability and
freshness decisions. No protected source, configuration, dispatcher, or
external system was changed.

## Applicability Preflight

- packet_hash: `sha256:416d139df9d582afb4f07a8f850b95813dd4e43b17fc5efe249b060653aa6510`
- bridge_document_name: `gtkb-wi5714-registry-write-linearizability`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5714-registry-write-linearizability-007.md`
- operative_file: `bridge/gtkb-wi5714-registry-write-linearizability-007.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:9f07de3aa47caabecd40a64a9f0abea213b3ba8d532158a78698d59143324dd9`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5714-registry-write-linearizability`
- Operative file: `bridge/gtkb-wi5714-registry-write-linearizability-007.md`
- Clauses evaluated: 5
- must_apply: 4; may_apply: 1; not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory clause preflight exit: `0`

| Clause | Applicability | Evidence |
| --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |

## Owner Decision / Input

No owner action is required for this verdict. The recorded owner decisions and
active exact WI-5714 authorization remain sufficient; implementation stays
subject to fresh claim and implementation-start gates.
