NO-GO

# Loyal Opposition Review - Project Authorize Spec-Linkage Gate

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-project-authorize-spec-linkage-gate-001.md`
Verdict: NO-GO

## Claim

The proposal implements an important governance gate, and the blocking
mechanical preflights pass. It is not ready for `GO` because the proposed
implementation and test plan enforce only a non-empty `included_spec_ids` list,
not the governing requirement that an active project authorization cite at
least one approved/current specification.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for `gtkb-project-authorize-spec-linkage-gate` was `NEW`, actionable for Loyal Opposition.
- Read the full thread via `show_thread_bridge.py`; no drift was reported.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, and `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and clause preflights.
- Searched the Deliberation Archive before review.
- Inspected current `KnowledgeDB.insert_project_authorization()`, `ProjectLifecycleService.authorize_project()`, and the `projects authorize` CLI path.
- Read the current MemBase row for `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "WI-3312 GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS project authorization" --limit 5 --json
python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant results:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the 2026-05-14 owner directive that projects cannot be approved without specifications and that the approved project includes the relevant implementation work.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` reinforces that implementation proposals must cite applicable specifications and that tests and verification must remain coupled to the cited specifications.
- `DELIB-S321-SPEC-CREATION-STANDING-AUTH` is older context now clarified by S346; it does not contradict the stricter S350 chain.

No prior deliberation found in this review contradicts the proposed gate. The blocker is that the proposed implementation is too shallow for the approved-specification requirement.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:ec1348457e0ea76897cec402e03d2c20caedc04dbb46258873dcce8bc265fbe4`
- bridge_document_name: `gtkb-project-authorize-spec-linkage-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-authorize-spec-linkage-gate-001.md`
- operative_file: `bridge/gtkb-project-authorize-spec-linkage-gate-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are not the blocking reason for this verdict.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-project-authorize-spec-linkage-gate`
- Operative file: `bridge\gtkb-project-authorize-spec-linkage-gate-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Findings

### F1 - Non-empty spec IDs are not the same as linked approved specifications

Severity: P1 / blocking

Evidence:

- The live `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` description says a project authorization "cannot reach active status without citing at least one approved specification (GOV/SPEC/REQ/ADR/DCL/PB)" and that every authorized project has at least one "citable governance anchor."
- The proposal's IP-1 validation blocks only `included_spec_ids is None OR len(included_spec_ids) == 0`.
- The proposed tests cover `None`, `[]`, draft-without-specs, active-with-one-spec, CLI missing specs, and grandfathering. They do not cover an unknown spec ID, retired/unapproved spec ID, or non-spec arbitrary string.
- Current `KnowledgeDB.insert_project_authorization()` simply JSON-encodes `included_spec_ids`; implementing IP-1 literally would still allow `included_spec_ids=["NOT-A-SPEC"]`.

Risk / impact:

This would preserve the exact governance-chain failure the new spec is meant to close: a project could be active with a syntactically non-empty but non-citable "spec" value. Work items could then appear project-authorized while still lacking a real governing specification anchor.

Recommended action:

Revise the proposal to validate the cited specification IDs, not only list cardinality. At minimum, active authorization should require at least one `included_spec_id` that resolves through `KnowledgeDB.get_spec()` to a current MemBase specification row of an allowed subtype (`GOV`, `SPEC`, `REQ`, `ADR`, `DCL`, or `PB`) with an approved/current lifecycle state. Add negative tests for unknown IDs and any disallowed lifecycle state the repo treats as not approved.

### F2 - CLI error mapping is underspecified against the live service layer

Severity: P2

Evidence:

- Live `projects_authorize()` calls `ProjectLifecycleService.authorize_project()`.
- Live `ProjectLifecycleService.authorize_project()` catches DB `ValueError` and raises `ProjectLifecycleError`.
- The proposal says `groundtruth-kb/src/groundtruth_kb/cli.py` should convert the `ValueError` from IP-1 to `click.UsageError`, but the CLI will normally see `ProjectLifecycleError`, not the original DB `ValueError`.
- The proposal's `target_paths` do not include `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, so any typed service-layer exception change would currently be outside the authorized implementation scope.

Risk / impact:

The CLI acceptance criterion can be implemented only by either pattern-matching a wrapped `ProjectLifecycleError` in `cli.py` or modifying the service exception path. The proposal does not choose one, so Prime may either miss the intended CLI behavior or need to edit a file outside `target_paths`.

Recommended action:

Revise IP-2 to match the live call path. Either specify `cli.py` converts the relevant `ProjectLifecycleError` into `click.UsageError`, or include `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` in `target_paths` and define a typed exception path for this validation failure.

## Positive Evidence

- The owner-decision evidence in `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` supports implementing this gate.
- The proposal includes project authorization, project, and work-item metadata.
- Root-boundary evidence is adequate.
- The proposal includes a substantive `Owner Decisions / Input` section.
- Applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

File a revised proposal that:

1. Validates at least one cited spec ID resolves to an approved/current specification row, rather than only checking that the list is non-empty.
2. Adds negative tests for fake or otherwise non-approved spec IDs.
3. Clarifies the live CLI/service exception path and updates `target_paths` if the implementation needs lifecycle-service edits.

After those changes, the proposal should be reviewable for `GO`.
