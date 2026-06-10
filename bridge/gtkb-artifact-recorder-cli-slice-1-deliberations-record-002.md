NO-GO

# Loyal Opposition Review - Artifact Recorder CLI Slice 1 Deliberations Record

bridge_kind: lo_verdict
Document: gtkb-artifact-recorder-cli-slice-1-deliberations-record
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-001.md`
Verdict: NO-GO

## Claim

`bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-001.md` cannot receive GO as written. The proposed high-level `gt deliberations record` surface is directionally useful, but the core safety claim depends on the existing formal-artifact approval PreToolUse hook validating a packet that the same CLI command only creates after that PreToolUse hook would already have run. That is not the current enforcement model.

The proposal must be revised so the approval packet is either an external pre-hook input, or the deterministic service has an explicit in-process validation path equivalent to the hook's packet validation before it mutates the Deliberation Archive.

## Prior Deliberations

Deliberation search was run before review for:

```text
artifact recorder CLI slice 1 deliberations record create-deliberation requirements trace
```

Relevant returned records included `DELIB-1575`, `DELIB-1560`, `DELIB-1577`, `DELIB-1404`, `DELIB-1526`, `DELIB-1788`, `DELIB-1477`, `DELIB-1561`, `DELIB-1522`, and `DELIB-1581`.

The proposal also cites the load-bearing parent context: `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`, `DELIB-0874`, `DELIB-0835`, `DELIB-0687`, and the Slice 0 GO at `bridge/gtkb-artifact-recorder-cli-004.md`. No retrieved deliberation waives the formal-artifact approval gate for deliberation writes.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:b4db7fc0c2cc0efb2a9150cb98ca8dfaeab56baab19bb4dec0233b8fc6ade717`
- bridge_document_name: `gtkb-artifact-recorder-cli-slice-1-deliberations-record`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-001.md`
- operative_file: `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-artifact-recorder-cli-slice-1-deliberations-record`
- Operative file: `bridge\gtkb-artifact-recorder-cli-slice-1-deliberations-record-001.md`
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

### F1 - P1 - The proposed packet-generation flow bypasses or deadlocks the PreToolUse gate

Evidence:

- Proposal claim: the new command "constructs the formal-artifact-approval packet, sets the `GTKB_FORMAL_APPROVAL_PACKET` env var, and invokes `KnowledgeDB.insert_deliberation()` such that the existing `formal-artifact-approval-gate.py` PreToolUse hook validates the packet at write time" (`-001`, Claim).
- Proposed implementation order: write packet, set `os.environ["GTKB_FORMAL_APPROVAL_PACKET"]`, then call `db.insert_deliberation()` (`-001`, IP-2 steps 4-6).
- Actual hook model: `.claude/hooks/formal-artifact-approval-gate.py` is a `PreToolUse` hook for Bash commands. It inspects the shell command string before the command executes, and only then loads a packet referenced by command text or environment.
- Actual protected patterns currently match `gt deliberations add|upsert|link` and Python code containing `insert_deliberation(...)`, but not `gt deliberations record`.
- Hook probe:
  - `python -m groundtruth_kb deliberations record --source-type owner_conversation` returned `{}`.
  - `gt deliberations record --source-type owner_conversation` returned `{}`.
  - `python -m groundtruth_kb deliberations add --source-type owner_conversation` was blocked for missing packet.
  - `gt deliberations upsert --source-type owner_conversation` was blocked for missing packet.

Impact:

The proposal's central safety invariant is not implementable as written. If `record` remains absent from the hook's formal-mutation regex, it bypasses the formal approval gate. If `record` is added to the regex, the PreToolUse hook will run before the command can create the packet internally, so it will block unless the caller supplies an external packet path up front. Setting `os.environ` inside the CLI process cannot affect a PreToolUse hook that already executed in a separate process.

Recommended action:

Revise the design around one explicit enforcement model:

1. External-packet model: `gt deliberations record` requires a caller-supplied `--formal-approval-packet` or inherited `GTKB_FORMAL_APPROVAL_PACKET`, and the hook validates before command execution; the CLI may verify the packet matches content before inserting.
2. In-process-service model: extract the hook's packet validation into a reusable library and have `gt deliberations record` call that validation before `insert_deliberation()`; still update hook coverage for raw command protection.

The revised proposal must include tests that prove both `gt deliberations record` without valid approval evidence is blocked and valid evidence is accepted at the actual enforcement boundary.

Decision needed from owner: none.

### F2 - P2 - The proposed API references `--source-ref` but does not define it

Evidence:

- IP-2 says packet `source_ref=<from --source-ref or constructed from --auq-id>`.
- The proposed argument list includes `--source-type`, `--title`, `--summary`, `--content-file`, `--change-reason`, `--auq-id`, `--auq-answer`, `--owner-presented`, `--spec-id`, `--work-item-id`, `--participants`, `--outcome`, `--session-id`, and `--dry-run`.
- It does not define `--source-ref`.
- Existing deliberation APIs use `source_ref` materially: `gt deliberations upsert` is keyed by `(source_type, source_ref, content_hash)`, and `KnowledgeDB.upsert_deliberation_source()` auto-generates DELIB IDs on that key.

Impact:

The implementation contract is ambiguous around source identity and idempotency. The live smoke expectation says re-running with the same content should match existing `add`/`upsert` dedup semantics, but the command surface does not define the source-ref input needed to make that deterministic and reviewable.

Recommended action:

Add an explicit `--source-ref` argument or define a deterministic source-ref derivation rule from `--auq-id`, `--content-file`, and session metadata. The revised proposal should state whether `record` calls `insert_deliberation()` with a preallocated ID or `upsert_deliberation_source()` for source/content idempotency, and tests should cover duplicate invocation behavior.

Decision needed from owner: none.

### F3 - P3 - Approval-mode description misstates current hook behavior

Evidence:

- The proposal says auto-mode "the gate currently rejects for `artifact_type='deliberation'`".
- The actual hook accepts `approval_mode="auto"` for any valid artifact type when `auto_approval_scope` exists and `auto_approval_activated_by == "owner"`; `platform_tests/hooks/test_formal_artifact_approval_gate.py::test_formal_write_allows_scoped_auto_approval_packet` covers auto approval.

Impact:

This is not the primary blocker, but it can lead to tests that assert the wrong safety property. The issue is not artifact type; the issue is missing required packet fields and missing owner-activated auto-approval scope.

Recommended action:

Revise the safety note and tests to match the hook's actual rules: `presented_to_user=true` and `transcript_captured=true` are always required, and `auto` additionally requires `auto_approval_scope` plus `auto_approval_activated_by="owner"`.

Decision needed from owner: none.

## Positive Confirmations

- The slice boundary is otherwise narrow: it targets the `gt deliberations record` surface and does not mix in the other artifact-recorder slices.
- The proposal cites the parent Slice 0 GO and the relevant artifact-approval governance family.
- The proposed tests correctly recognize the need to cover content-hash binding, project-root containment, dry-run non-mutation, and help-surface visibility.

## Decision

NO-GO. Revise the proposal so the formal-artifact approval enforcement path is coherent with the actual PreToolUse hook lifecycle, define source identity/idempotency explicitly, and correct the approval-mode safety note.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
