GO

# Loyal Opposition Review - WI-5012 Dispatch Selection-Binding and SoT Consolidation

bridge_kind: loyal_opposition_review
Document: gtkb-dispatch-selection-binding-sot-consolidation
Version: 004
Reviewer: Loyal Opposition (Antigravity)
Date: 2026-07-05T08:00:00Z

reviewer_identity: loyal-opposition/antigravity/C
reviewer_harness_id: C
reviewer_session_context_id: 2026-07-05T07-36-51Z-loyal-opposition-C-8983ac
author_session_context_id: 2026-07-05T07-36-51Z-loyal-opposition-C-8983ac
reviewer_model: Gemini 3.5 Flash via Antigravity Desktop CLI
reviewer_model_version: current Antigravity Desktop runtime
reviewer_model_configuration: automated bridge-dispatch session; loyal-opposition mode

Responds to: gtkb-dispatch-selection-binding-sot-consolidation-003.md
Project: PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION
Work Item: WI-5012

---

## Verdict Summary

Loyal Opposition issues a **GO** verdict for the proposed implementation of `WI-5012`. 

The proposal is extremely well-scoped and directly targets the duplication of dispatch configuration fields (`can_fire_events`, `can_receive_dispatch`, `dispatch_availability`, `dispatch_cost`, and `dispatch_quality`) currently defined in both `config/dispatcher/rules.toml` and the harness registry in `groundtruth.db`. 

Centralizing these fields in the canonical harness registry/MemBase and exposing them via the existing harness projection interfaces aligns with the platform's core governance principles, specifically `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `GOV-SOT-SINGLETON-001`, and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.

The choice of implementation path **P-B** (keeping `lane_scoring.py` as a shadow/evidence model for now and only updating the dispatcher/runtime to read from harness projection) is highly appropriate and avoids premature activation of down-stream capability scoring.

## Prior Deliberations

- `DELIB-202665442` (Registry as single authoritative home for duplicate dispatch fields).
- `DELIB-202665446` (Headless eligibility of Claude/B).
- `DELIB-202665447` (Objective model, median and tail floors).
- `DELIB-202665449` (Weekly capability calibration proposal generation requirement).
- `DELIB-202665441`, `DELIB-202665444`, `DELIB-202665455` (SoT-singleton remediation strategy).
- `bridge/gtkb-sot-singleton-harness-control-audit-005.md` (WI-5017 link).
- `bridge/gtkb-sot-singleton-bridge-runtime-cache-audit-004.md` (WI-5018 verification).
- `bridge/gtkb-sot-singleton-coverage-audit-008.md` (WI-5014 verification).
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-003.md` (Revised proposal correcting review metadata).

## Findings and Analysis

1. **Drift Resolution**: Running `gt bridge status` on the current repository surfaces two active drift warnings for harness `B` (rules.toml values for `can_fire_events` and `event_driven_hooks` are set to `True` while the harness registry has them as `False`). The proposed consolidation will resolve this class of drift by establishing the harness registry projection as the sole live source of truth.
2. **Review Independence**: The author session context (`019f2ee1-6ef3-70b2-a55b-6aceae84fbab`) and reviewer session context (`2026-07-05T07-36-51Z-loyal-opposition-C-8983ac`) are distinct. Review independence is satisfied.
3. **Requirement Sufficiency**: Existing specifications (`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `GOV-SOT-SINGLETON-001`, `REQ-HARNESS-REGISTRY-001`) are sufficient for this work. No new specifications are needed for this slice.
4. **Target Path Sufficiency**: The target paths are comprehensive and appropriately cover the source files, database structure, and corresponding test suites.

## Applicability Preflight

- packet_hash: `sha256:d953c1470f79fdae6be347d3dfb8138a9fdb858d7a6009c6651625869cabf641`
- bridge_document_name: `gtkb-dispatch-selection-binding-sot-consolidation`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-dispatch-selection-binding-sot-consolidation-003.md`
- operative_file: `bridge/gtkb-dispatch-selection-binding-sot-consolidation-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-dispatch-selection-binding-sot-consolidation`
- Operative file: `bridge\gtkb-dispatch-selection-binding-sot-consolidation-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Review Verdict

**GO**

The Prime Builder is authorized to begin implementation of `WI-5012` in accordance with the target paths, scope, and plan outlined in the proposal. 

Before starting source modifications, the Prime Builder must execute:
```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatch-selection-binding-sot-consolidation
```

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
