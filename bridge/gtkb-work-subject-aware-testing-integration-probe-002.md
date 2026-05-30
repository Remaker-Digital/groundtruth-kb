NO-GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-05-27T20-49-03Z-loyal-opposition-d8be4f
author_model: GPT-5 Codex
author_metadata_source: bridge auto-dispatch
reviewed_document: bridge/gtkb-work-subject-aware-testing-integration-probe-001.md
reviewed_status: NEW
Date: 2026-05-27 UTC

# Loyal Opposition Review: Work-Subject-Aware Testing Integration Probe

Document: gtkb-work-subject-aware-testing-integration-probe
Version Reviewed: 001 (NEW)
Verdict: NO-GO

## Summary

NO-GO. The defect claim is credible, the proposed target paths are in-root, and the project authorization exists. The proposal still misses two review-gate requirements before implementation can be approved:

1. It relies on the reliability fast-lane standing authorization but does not cite the governing fast-lane spec, `GOV-RELIABILITY-FAST-LANE-001`, in `## Specification Links`.
2. It defines "canonical" work-subject return values as `"GT-KB"` / `"application"` / `"GT-KB+application"`, but the live canonical state file and helper constants use `gtkb_infrastructure` and `application`. The proposal must align the implementation contract to the existing canonical schema or explicitly define a translation layer.

No owner input is requested in this auto-dispatch context; Prime Builder can revise the proposal.

## Prior Deliberations

Deliberation Archive searches run:

- `$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "work subject testing integrations probe startup rollup Agent Red GT-KB WI-3409" --limit 8 --json` returned `[]`.
- `$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "DELIB 0876 work subject session startup work-subject.json" --limit 8 --json` returned `[]`.

Relevant live project authorization evidence:

- `python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` shows `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry, and allows `source`, `test_addition`, and `hook_upgrade`.
- `python -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json` shows `WI-3409` is an active member under `PROJECT-GTKB-RELIABILITY-FIXES`.

## Applicability Preflight

- packet_hash: `sha256:d0ad30844cc2223e45cff320a1006aa93c8fe26ee6ffaae79a58c7763b620968`
- bridge_document_name: `gtkb-work-subject-aware-testing-integration-probe`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-subject-aware-testing-integration-probe-001.md`
- operative_file: `bridge/gtkb-work-subject-aware-testing-integration-probe-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/scripts/test_testing_service_integrations_work_subject_aware.py"]
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-work-subject-aware-testing-integration-probe`
- Operative file: `bridge\gtkb-work-subject-aware-testing-integration-probe-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Review Findings

### Finding P1-001: Missing Governing Fast-Lane Specification

Observation: The proposal cites `Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, `Project: PROJECT-GTKB-RELIABILITY-FIXES`, and `Work Item: WI-3409`, and its Owner Decisions section says the standing authorization covers the source and test target paths. Its `## Specification Links` section does not cite `GOV-RELIABILITY-FAST-LANE-001`.

Evidence: `bridge/gtkb-work-subject-aware-testing-integration-probe-001.md` header metadata, `## Specification Links`, and `## Owner Decisions / Input`; live authorization output from `python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json`.

Deficiency rationale: The proposal uses the reliability fast-lane as implementation authority. Under `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, the implementation proposal must cite every relevant governing specification. The fast-lane spec is the governance surface that defines eligibility and the reduced approval ceremony for this standing authorization. Without it, Loyal Opposition cannot verify that the proposed defect fix qualifies for the fast-lane path.

Impact: Prime Builder could implement under a standing authorization without demonstrating that the work satisfies that authorization's governing eligibility constraints.

Recommended action: Revise `## Specification Links` and the verification mapping to include `GOV-RELIABILITY-FAST-LANE-001`. Add a short eligibility statement that this is a small, single-concern startup reliability defect fix with source and test-only target paths, no deployment, no force-push, and no spec deletion.

### Finding P1-002: Proposed Work-Subject Values Do Not Match The Canonical Schema

Observation: IP-1 says the helper should return canonical values `"GT-KB"` (default), `"application"`, or `"GT-KB+application"`. The live `.claude/session/work-subject.json` stores `"current_subject": "gtkb_infrastructure"`, and `scripts/workstream_focus.py` defines `FOCUS_GTKB_INFRASTRUCTURE = "gtkb_infrastructure"` and `FOCUS_APPLICATION = "application"`. No current code reference for `"GT-KB+application"` was found.

Evidence:

- `.claude/session/work-subject.json` currently contains `"current_subject": "gtkb_infrastructure"`.
- `scripts/workstream_focus.py` defines `FOCUS_GTKB_INFRASTRUCTURE = "gtkb_infrastructure"`, `SUBJECT_GTKB = FOCUS_GTKB_INFRASTRUCTURE`, and `FOCUS_APPLICATION = "application"`.
- `rg -n "GT-KB\+application|gtkb_infrastructure|current_subject|work-subject.json" ...` found `"GT-KB+application"` only in this proposal, while the runtime code uses `gtkb_infrastructure`.

Deficiency rationale: The proposed implementation target is specifically the work-subject boundary. Approving a proposal that calls a non-runtime string `"GT-KB"` canonical risks adding a second vocabulary to the startup path and tests. That would repair the GitHub repo selection symptom while introducing new drift between the session state schema and `_testing_service_integrations`.

Impact: Tests could pass against a newly invented helper contract while the actual startup state continues to use `gtkb_infrastructure`, or future callers could consume `queried_work_subject` and misinterpret it as a canonical state value.

Recommended action: Revise the scope to use the existing `scripts.workstream_focus` constants or `load_state(project_root)` result directly. The proposal should state branch behavior in terms of `gtkb_infrastructure` -> GT-KB repo and `application` -> Agent Red repo. If a display label such as "GT-KB" is desired, make it explicitly a display label, not the canonical work-subject value. Remove or explicitly defer `"GT-KB+application"` unless the current schema already supports it.

## Non-Blocking Note

The mechanical applicability preflight reports missing advisory spec `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. Because it is advisory, this is not a standalone blocker. Prime should still consider adding it if the revised text continues to discuss candidate/verified lifecycle transitions.

## Required Revision Response

1. Add `GOV-RELIABILITY-FAST-LANE-001` to `## Specification Links` and map it to an explicit fast-lane eligibility check.
2. Replace the proposed `"GT-KB"` / `"GT-KB+application"` canonical values with the current work-subject schema (`gtkb_infrastructure`, `application`) or document a clear internal translation layer that cannot be mistaken for the persisted canonical value.
3. Keep the target paths scoped to `scripts/session_self_initialization.py` and `tests/scripts/test_testing_service_integrations_work_subject_aware.py`.

