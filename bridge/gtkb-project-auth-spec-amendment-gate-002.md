NO-GO

# Loyal Opposition Review - Project Authorization Spec-Amendment Approval Gate

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-project-auth-spec-amendment-gate-001.md`
Verdict: NO-GO

## Claim

The proposal targets a real governance gap and its blocking mechanical
preflights pass. It is not ready for `GO` because the proposed implementation
allows any citation-shaped string to satisfy an owner-approval gate that the
governing DCL defines as packet-evidence-backed.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for `gtkb-project-auth-spec-amendment-gate` was `NEW`, actionable for Loyal Opposition.
- Read the full thread with `show_thread_bridge.py`; no drift was reported.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, and `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and clause preflights.
- Searched the Deliberation Archive before review.
- Read the current MemBase rows for the cited project authorization, work item, owner deliberation, and source DCL.
- Inspected current `KnowledgeDB.insert_project_authorization()` / `update_project_authorization()` flow.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "WI-3313 DCL-PROJECT-SPECIFICATION-AMENDMENT approval-packet project authorization" --limit 10 --json
python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the 2026-05-14 owner directive that adding a specification to an in-flight project requires approval, potentially as part of a batch approval. It also records that `WI-3313` is part of the authorized enforcement project.

No prior deliberation found in this review contradicts implementing the
spec-amendment gate. The blocker is the proposed evidence check.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:bb27647b8ae4361591f7db7c9624cc803cc69aa68f6db261744cdeb835caabb6`
- bridge_document_name: `gtkb-project-auth-spec-amendment-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-auth-spec-amendment-gate-001.md`
- operative_file: `bridge/gtkb-project-auth-spec-amendment-gate-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
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
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-project-auth-spec-amendment-gate`
- Operative file: `bridge\gtkb-project-auth-spec-amendment-gate-001.md`
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

### F1 - Citation-shaped text is not approval-packet evidence

Severity: P1 / blocking

Evidence:

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` says adding, removing, or substituting a specification on an active project authorization requires explicit owner approval via AskUserQuestion or a batch formal-artifact-approval packet covering the amendment, and that the amendment write fails closed without packet evidence.
- The proposal claim says the mutation should require a path to an existing `.groundtruth/formal-artifact-approvals/*.json` packet, but then defines reference detection as a case-insensitive substring match for `.groundtruth/formal-artifact-approvals/` and `.json` in `change_reason` (`bridge/gtkb-project-auth-spec-amendment-gate-001.md:22`).
- IP-1 repeats the substring-only check (`bridge/gtkb-project-auth-spec-amendment-gate-001.md:73` through `bridge/gtkb-project-auth-spec-amendment-gate-001.md:76`).
- The positive-path test intentionally succeeds when `change_reason` includes `.groundtruth/formal-artifact-approvals/test-packet.json` (`bridge/gtkb-project-auth-spec-amendment-gate-001.md:91`), with no proposed assertion that the packet exists, is in-root, is approved by the owner, or covers the amendment.

Risk / impact:

A caller could mutate a project's linked specification scope with
`change_reason="approved via .groundtruth/formal-artifact-approvals/fake.json"`.
That would satisfy the proposed gate while providing no approval packet and no
evidence that the owner approved the specific amendment. This preserves the
silent governance-footprint expansion risk the DCL is meant to close.

Recommended action:

Revise the proposal to validate packet evidence, not just packet-shaped text.
At minimum, parse the cited path, require it to resolve inside
`E:\GT-KB\.groundtruth\formal-artifact-approvals\`, require the JSON file to
exist, require owner approval fields such as `approved_by: owner`, and require
coverage of the relevant project authorization/spec amendment. Add negative
tests for fake paths, outside-root paths, malformed JSON, non-owner-approved
packets, and packets that do not cover the amendment.

### F2 - The spec-to-test mapping omits the key negative evidence cases

Severity: P2

Evidence:

- The verification plan tests no packet path, any packet-shaped path, batch reuse, first-version exemption, and status-only exemption (`bridge/gtkb-project-auth-spec-amendment-gate-001.md:88` through `bridge/gtkb-project-auth-spec-amendment-gate-001.md:94`).
- It does not test the behavior that distinguishes packet evidence from arbitrary text: nonexistent packet, malformed packet, packet outside `.groundtruth/formal-artifact-approvals/`, or packet that does not cover the amended authorization/specs.

Risk / impact:

Prime Builder could implement the literal plan, get all proposed tests passing,
and still leave the approval gate bypassable through a fake packet reference.

Recommended action:

Add spec-derived tests for the packet-evidence failure cases above, then promote
the DCL only after those tests and the validation logic pass.

## Positive Evidence

- The owner-decision evidence in `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` supports implementing this gate.
- The cited project authorization is active and includes `WI-3313`.
- Root-boundary evidence is adequate.
- The proposal includes project authorization, project, and work-item metadata.
- Applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

File a revised proposal that:

1. Replaces substring-only packet detection with validation of actual approval-packet evidence.
2. Adds negative tests for fake, missing, malformed, outside-root, non-owner-approved, and non-covering packet references.
3. Aligns the claim, implementation plan, tests, and acceptance criteria around the same approval-evidence standard.

After those changes, the proposal should be reviewable for `GO`.
