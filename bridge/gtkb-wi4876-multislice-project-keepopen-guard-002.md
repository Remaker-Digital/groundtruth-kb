GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 846d5995-f678-4a82-bf71-a599fa4b6b2d
author_model: Gemini 3.5 Flash (High)
author_model_version: gemini-3.5-flash-high
author_model_configuration: auto-dispatched Loyal Opposition review
author_metadata_source: dispatcher-dispatch-env

# Review Verdict - Multi-slice project keep-open guard

Document: gtkb-wi4876-multislice-project-keepopen-guard
Version: 002
Date: 2026-07-06 UTC

## Verdict Summary

Loyal Opposition issues a **GO** for the proposal "Multi-slice project keep-open guard" (WI-4876).
The proposal addresses a critical catch-22/trap in the auto-retirement logic of multi-slice projects, where completing an interim slice's authorization is blocked if a completion guard is present, yet completing it without a guard leads to premature project retirement.

The proposed solution to extend `gt projects authorize` (or its underlying service layer) to record a `plan_incomplete` completion guard of type `completion_guard` for the project is sound, provided we implement the following detailed design:

1. **CLI and Service Layer Extensions**:
   - Add a `--plan-incomplete` (or `--keep-open`) option to the `gt projects authorize` command.
   - When specified, the service layer `authorize_project` will insert an active project artifact link with `relationship='plan_incomplete'`, `artifact_type='completion_guard'`, and `artifact_ref=f"{authorization_id}-keepopen"`.

2. **Refined Guard Gating in `complete_project_authorization`**:
   - Modify `complete_project_authorization` to distinguish between `bridge_thread` guards (which represent unverified work and must block completing the authorization) and general `completion_guard` type guards (which represent project-level plan incompleteness).
   - A `completion_guard` type guard must NOT raise `ProjectLifecycleError` in `complete_project_authorization`. Instead, it will allow the authorization to be completed but will prevent the project from being retired (treating the project as if there are still active guards, which overrides the retirement action).

3. **Automatic Guard Retirement**:
   - When `complete_project_authorization` successfully completes an authorization, it should automatically retire/deactivate any active `plan_incomplete` guard links associated with that authorization (i.e. where `artifact_ref == f"{authorization_id}-keepopen"`).
   - This ensures that once the final slice's authorization (which does not have the `--plan-incomplete` flag) is completed, and all prior slice guards are inactive, the project can auto-retire cleanly without manual intervention.

4. **Refinement of `auto_complete_ready_authorizations`**:
   - Ensure `auto_complete_ready_authorizations` does not skip completing an authorization for a project just because a `completion_guard` exists (only `bridge_thread` guards should block authorization auto-completion).

5. **Code Re-organization**:
   - We approve the refactoring and moving of projects CLI commands from `cli.py` to `groundtruth-kb/src/groundtruth_kb/cli_projects.py` as indicated in the target paths.

## Applicability Preflight

- packet_hash: `sha256:ac325bfbbcbfc06fe7443f93e5a8593f0730d5997c63f155f06f814596649b81`
- bridge_document_name: `gtkb-wi4876-multislice-project-keepopen-guard`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4876-multislice-project-keepopen-guard-001.md`
- operative_file: `bridge/gtkb-wi4876-multislice-project-keepopen-guard-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4876-multislice-project-keepopen-guard`
- Operative file: `bridge\gtkb-wi4876-multislice-project-keepopen-guard-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
