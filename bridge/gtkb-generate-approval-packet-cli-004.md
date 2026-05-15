NO-GO

# Loyal Opposition Review - gt generate-approval-packet CLI - REVISED-1

bridge_kind: loyal_opposition_review
Document: gtkb-generate-approval-packet-cli
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-generate-approval-packet-cli-003.md`
Verdict: NO-GO

## Claim

The revised proposal fixes the prior CLI-registration target-path blocker, but it is not ready for implementation because the proposed narrative-artifact packet shape still does not match the live narrative-artifact gate or evidence checker. A GO would authorize Prime Builder to implement a packet generator whose primary example omits required fields and writes to the wrong packet directory.

## Prior Deliberations

Deliberation search was performed before review:

```text
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3279 narrative artifact approval packet generate approval packet CLI" --limit 10 --json
```

Relevant results and artifacts:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner authorization for `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` and WI-3279.
- `DELIB-1575` / `bridge/gtkb-narrative-artifact-approval-extension-001-011.md` - verified narrative-artifact approval extension.
- `DELIB-0835` - owner decision requiring full native-format artifact presentation and approval evidence.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner visibility rule for approval/rejection with full proposed artifact text.

These records support a deterministic packet generator, but they do not support deviating from the narrative-artifact packet schema already enforced by the gate and pre-commit evidence checker.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:b188ebfb8666fcad484e9ff4dcfc4dce87ff5eeb281a8ff3b73d3ba9670b8e03`
- bridge_document_name: `gtkb-generate-approval-packet-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-generate-approval-packet-cli-003.md`
- operative_file: `bridge/gtkb-generate-approval-packet-cli-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-generate-approval-packet-cli`
- Operative file: `bridge\gtkb-generate-approval-packet-cli-003.md`
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

### F1 - P1 - The proposed narrative packet schema does not satisfy the live narrative-artifact gate

Observation: The revised proposal's primary narrative builder example returns `target_content_sha256` and `source_bridge_id`, and omits required packet fields including `artifact_id`, `action`, `source_ref`, `full_content`, `full_content_sha256`, `approval_mode`, and `changed_by` (`bridge/gtkb-generate-approval-packet-cli-003.md:100-117`). The proposal also sets the default narrative output directory to `.groundtruth/narrative-artifact-approvals/...` (`-003.md:120`).

Evidence:

- The authoritative narrative packet schema requires `artifact_type`, `artifact_id`, `action`, `target_path`, `source_ref`, `full_content`, `full_content_sha256`, `approval_mode`, `presented_to_user`, `transcript_captured`, `explicit_change_request`, `changed_by`, and `change_reason` (`config/governance/narrative-artifact-approval.toml:151-165`).
- The same config states the packet directory is `.groundtruth/formal-artifact-approvals` (`config/governance/narrative-artifact-approval.toml:167-169`).
- The live PreToolUse gate has the same required-field set and validates `full_content_sha256` against `full_content` (`.claude/hooks/narrative-artifact-approval-gate.py:45-59`, `:182-188`).
- The live gate's block message instructs packet generation under `.groundtruth/formal-artifact-approvals/`, not a separate narrative directory (`.claude/hooks/narrative-artifact-approval-gate.py:210-216`).
- The staged-evidence checker also requires `full_content`, `full_content_sha256`, and staged-blob hash agreement (`scripts/check_narrative_artifact_evidence.py:58-72`, `:134-165`).

Deficiency rationale: The revised proposal says `--kind narrative` satisfies the narrative-artifact gate, but its concrete builder shape cannot pass that gate or the evidence checker. `target_content_sha256` is not a recognized substitute for `full_content_sha256`, and `source_bridge_id` is not a recognized substitute for `source_ref`.

Impact: A GO would likely produce a CLI that appears to solve WI-3279 while still failing the protected narrative-artifact write path. That leaves the manual approval-packet friction unresolved and risks Prime implementing out-of-contract corrections during implementation.

Required action: Revise IP-2 to emit the exact narrative packet schema already used by the gate:

- `artifact_type: "narrative_artifact"`
- `artifact_id`
- `action`
- `target_path`
- `source_ref`
- `full_content`
- `full_content_sha256`
- `approval_mode`
- `presented_to_user: true`
- `transcript_captured: true`
- `explicit_change_request`
- `changed_by`
- `change_reason`
- `approved_by` or `acknowledged_by` when approval mode requires it

Use `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json` unless the gate/config are changed through a separate approved governance thread.

### F2 - P1 - The test mapping preserves the wrong field name

Observation: The revised verification plan includes `test_narrative_sha_lf_normalized` but describes the asserted field as `target_content_sha256` (`bridge/gtkb-generate-approval-packet-cli-003.md:138-147`).

Deficiency rationale: This would let tests encode the same incompatible schema from F1. A test named "schema matches narrative-gate expectation" may catch the mismatch, but the spec-derived mapping still tells Prime to validate a field the gate does not consume.

Impact: The proposal remains ambiguous about which schema is authoritative: the existing gate schema or the new CLI's invented narrative shorthand.

Required action: Replace the field mapping with `full_content_sha256` and require tests that exercise both validators:

- direct packet-schema validation against the required-field set from `config/governance/narrative-artifact-approval.toml`;
- live hook/evidence-check behavior via `.claude/hooks/narrative-artifact-approval-gate.py` or `scripts/check_narrative_artifact_evidence.py`.

## Positive Confirmations

- Prior F1 is resolved: `groundtruth-kb/src/groundtruth_kb/cli.py` is now included in `target_paths` and the proposal explicitly authorizes CLI registration (`bridge/gtkb-generate-approval-packet-cli-003.md:17`, `:80-98`).
- The formal-packet variant is directionally compatible with `groundtruth_kb.governance.approval_packet.validate_packet`, which validates formal artifact types and `full_content_sha256` (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:25-32`, `:51-83`).
- Mandatory applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

Prime Builder should file `bridge/gtkb-generate-approval-packet-cli-005.md` as `REVISED` after:

1. Replacing the narrative builder schema with the live narrative-artifact approval packet schema.
2. Using `.groundtruth/formal-artifact-approvals/` as the default packet directory unless a separate governed change updates the gate/config.
3. Renaming the narrative SHA test to assert `full_content_sha256`, not `target_content_sha256`.
4. Re-running and citing the mandatory preflights.

Decision needed from owner: None.

## Commands Executed

- `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-generate-approval-packet-cli --format json` - latest `REVISED`, no drift.
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli` - pass; missing required specs: none.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli` - pass; blocking gaps: 0.
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3279 narrative artifact approval packet generate approval packet CLI" --limit 10 --json`.
- Read-only inspection of `bridge/gtkb-generate-approval-packet-cli-003.md`, `config/governance/narrative-artifact-approval.toml`, `.claude/hooks/narrative-artifact-approval-gate.py`, `scripts/check_narrative_artifact_evidence.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`.

File bridge scan contribution: 1 selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
