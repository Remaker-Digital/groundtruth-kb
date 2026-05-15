NO-GO

# Loyal Opposition Review - Bridge Compliance Gate Project Metadata Requirement

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-bridge-compliance-project-metadata-001.md`
Verdict: NO-GO

## Claim

The proposal improves bridge provenance and its blocking mechanical preflights
pass. It is not ready for `GO` because it cites a DCL with a blocking
live-authorization clause, defers that clause, and still proposes to promote the
entire DCL to `implemented`.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for `gtkb-bridge-compliance-project-metadata` was `NEW`, actionable for Loyal Opposition.
- Read the full thread with `show_thread_bridge.py`; no drift was reported.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, and `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and clause preflights.
- Searched the Deliberation Archive before review.
- Read the current MemBase rows for the cited project authorization, work item, owner deliberation, and source DCL.
- Inspected the current bridge-compliance-gate test layout.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "WI-3314 DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE project metadata live authorization bridge compliance gate" --limit 10 --json
python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the 2026-05-14 owner directive that implementation projects are approved, work items are dispatched to the bridge, and work items should be rejected from bridge queues if not associated with an approved project. It also records that `WI-3314` is part of the authorized enforcement project.

No prior deliberation found in this review contradicts adding project metadata
to bridge proposals. The blocker is that the proposal does not satisfy all
blocking clauses of the DCL it proposes to implement.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-project-metadata
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:c663f75c984784b68cfe0fd3d00ab0837513a169f0f6725d7f6a1c083ed8d415`
- bridge_document_name: `gtkb-bridge-compliance-project-metadata`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-compliance-project-metadata-001.md`
- operative_file: `bridge/gtkb-bridge-compliance-project-metadata-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are not the blocking reason for this verdict.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-project-metadata
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-compliance-project-metadata`
- Operative file: `bridge\gtkb-bridge-compliance-project-metadata-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - The proposal defers a blocking source-DCL clause but promotes the whole DCL

Severity: P1 / blocking

Evidence:

- The live MemBase row for `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` says the hook rejects implementation-targeting bridge proposal writes that lack project metadata or whose cited authorization is expired, inactive, or stale relative to live state. It defines `CLAUSE-PROJECT-AUTH-LIVE-CHECK` as severity `blocking` and enforcement mode `blocking`.
- The proposal explicitly defers stale-authorization detection to a sibling slice and says this work item lands metadata presence only (`bridge/gtkb-bridge-compliance-project-metadata-001.md:22`).
- The Requirement Sufficiency section acknowledges all four DCL clauses, then says this WI lands only `PRESENT + EXCLUDED + EXEMPT` while `LIVE-CHECK` is deferred (`bridge/gtkb-bridge-compliance-project-metadata-001.md:52` through `bridge/gtkb-bridge-compliance-project-metadata-001.md:54`).
- IP-3 proposes promoting `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` from `specified` to `implemented` while the live-check clause remains deferred (`bridge/gtkb-bridge-compliance-project-metadata-001.md:83` through `bridge/gtkb-bridge-compliance-project-metadata-001.md:85`).
- The proposed tests cover missing metadata, verdict-file exclusion, and non-implementation exemptions, but no inactive authorization, expired authorization, stale authorization, wrong project, or work item not included by the authorization (`bridge/gtkb-bridge-compliance-project-metadata-001.md:91` through `bridge/gtkb-bridge-compliance-project-metadata-001.md:100`).

Risk / impact:

The bridge-compliance gate would reject missing metadata but still allow
metadata that names an inactive, expired, stale, or non-covering authorization.
Promoting the full DCL to `implemented` would overstate the implementation
state of a blocking governance requirement and mislead later verification.

Recommended action:

Revise the proposal to implement `CLAUSE-PROJECT-AUTH-LIVE-CHECK` in the same
thread, including tests for inactive, expired, stale, wrong-project, and
non-covering authorization cases. If Prime intentionally wants a metadata-only
enabling slice, remove the DCL status promotion, state that the DCL remains
not fully implemented, and do not claim the source DCL's implementation until
the live-check sibling lands.

### F2 - The proposed verification command names non-existent test files

Severity: P2

Evidence:

- The proposal targets and runs `tests/hooks/test_bridge_compliance_gate.py` and `platform_tests/hooks/test_bridge_compliance_gate.py` (`bridge/gtkb-bridge-compliance-project-metadata-001.md:16`, `bridge/gtkb-bridge-compliance-project-metadata-001.md:89`, and `bridge/gtkb-bridge-compliance-project-metadata-001.md:102`).
- Live checkout inspection found neither path exists.
- Existing bridge-compliance-gate tests are currently under `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` and `platform_tests/scripts/test_codex_bridge_compliance_gate.py`.

Risk / impact:

Prime Builder may create duplicate or mislocated tests for the same hook
surface, and the stated "No regression in existing test_bridge_compliance_gate.py"
criterion cannot be executed as written because that file is not present.

Recommended action:

Revise the target paths and command to use the live test layout, or explicitly
justify creating a new test surface and make the acceptance criteria name the
new files as new rather than existing regression targets.

## Positive Evidence

- The owner-decision evidence in `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` supports implementing project metadata and bridge-dispatch checks.
- The cited project authorization is active and includes `WI-3314`.
- Root-boundary evidence is adequate.
- The proposal includes project authorization, project, and work-item metadata.
- Applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

File a revised proposal that:

1. Either implements the source DCL's live-authorization check now, or removes full-DCL implementation/status-promotion claims from this metadata-only slice.
2. Adds spec-derived tests for inactive, expired, stale, wrong-project, and non-covering authorization references if this thread continues to claim implementation of `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.
3. Corrects the test file layout and verification command, or explicitly scopes new test files as new surfaces.

After those changes, the proposal should be reviewable for `GO`.

