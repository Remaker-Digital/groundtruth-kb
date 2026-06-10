NO-GO

# Loyal Opposition Review - gt generate-approval-packet CLI

bridge_kind: lo_verdict
Document: gtkb-generate-approval-packet-cli
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-generate-approval-packet-cli-001.md`
Verdict: NO-GO

## Claim

The proposal is directionally aligned with the owner-approved deterministic-services principle and the batch-4 project authorization. It cannot receive GO yet because the proposed target path set cannot register the claimed `gt generate-approval-packet` command, and the proposal narrows the operative WI from narrative-artifact approval-packet ergonomics to only the formal-artifact packet validator surface.

## Prior Deliberations

Deliberation searches and lookups run:

```text
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "approval packet ergonomics WI-3279 generate approval packet" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS approval packet ergonomics" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-0835 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-1901 --json
```

Relevant results:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` authorizes `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` and includes WI-3279.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports the goal of replacing repeated approval-packet ceremony with deterministic services.
- `DELIB-0835` is the owner decision requiring full native-format artifact presentation and approval evidence.
- `DELIB-1901` records the verified `gtkb-narrative-artifact-approval-extension-001` thread, which is relevant because WI-3279's live description is about narrative-artifact approval-packet friction.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:daf4c070f8b72c3b9ab86548ddb4a34262b2d4e7d5a72f75458388fd4e2ef844`
- bridge_document_name: `gtkb-generate-approval-packet-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-generate-approval-packet-cli-001.md`
- operative_file: `bridge/gtkb-generate-approval-packet-cli-001.md`
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
- Operative file: `bridge\gtkb-generate-approval-packet-cli-001.md`
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

### F1 - P1 - The claimed `gt` command cannot be registered inside the authorized target paths

Observation: The proposal claims a new top-level CLI command, `gt generate-approval-packet`, but authorizes only a new module and its tests.

Evidence:

- Proposal `target_paths` are only `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` and `groundtruth-kb/tests/test_cli_approval_packet.py` (`bridge/gtkb-generate-approval-packet-cli-001.md:16`).
- The proposal explicitly claims "CLI: `gt generate-approval-packet ...`" (`bridge/gtkb-generate-approval-packet-cli-001.md:22`) and "Click group registered as `gt generate-approval-packet`" (`bridge/gtkb-generate-approval-packet-cli-001.md:65`).
- The installed console entry point is `gt = "groundtruth_kb.cli:main"` (`groundtruth-kb/pyproject.toml:55`).
- The live CLI surface is registered inside `groundtruth-kb/src/groundtruth_kb/cli.py` through `@click.group()`, `def main(...)`, and `@main.command` / `@main.group` decorators (`groundtruth-kb/src/groundtruth_kb/cli.py:88`, `:92`, `:104`, `:137`, `:206`, and following command registrations).

Deficiency rationale: A new module can contain helper functions, but it does not become `gt generate-approval-packet` unless `groundtruth_kb.cli:main` imports/registers it or another entry-point/plugin mechanism exists. The proposal neither authorizes `groundtruth-kb/src/groundtruth_kb/cli.py` in `target_paths` nor describes an alternate registration mechanism.

Impact: If Prime implements within the approved target paths, the claimed command is likely unreachable. If Prime edits `cli.py` to make the command reachable, the implementation would exceed the proposal's authorization envelope and can fail the implementation-start scope gate.

Required action: Revise the proposal to add `groundtruth-kb/src/groundtruth_kb/cli.py` to `target_paths` and to the implementation/test plan, or revise the claim to a non-top-level module invocation that does not require CLI registration. Add a test that exercises the actual `groundtruth_kb.cli:main` command surface, not only module-level functions.

### F2 - P1 - The proposal does not satisfy the operative WI's narrative-artifact approval-packet scope

Observation: The proposal says WI-3279 is the operative requirement, but the proposed command is framed around the formal-artifact approval-packet validator and omits the narrative-artifact packet fields and enforcement surface that WI-3279 exists to reduce.

Evidence:

- The proposal states: "Existing requirements sufficient. WI-3279 description is the operative spec" (`bridge/gtkb-generate-approval-packet-cli-001.md:50`).
- Live MemBase readback for `WI-3279` describes the problem as "Generating a narrative-artifact approval packet on Windows requires manual handling" and calls for `gt generate-approval-packet --target <path> --action update --explicit-change-request ...`.
- The proposal's command synopsis is instead `--artifact-type`, `--artifact-id`, `--action insert`, `--content-file`, `--change-reason`, and `--source-ref`, and says it emits JSON matching the formal-artifact-approval schema (`bridge/gtkb-generate-approval-packet-cli-001.md:22`).
- The implementation plan says `--validate-after` re-validates through `groundtruth_kb.governance.approval_packet.validate_packet` (`bridge/gtkb-generate-approval-packet-cli-001.md:72`).
- That shared validator is explicitly a formal-artifact approval packet validator (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:1`, `:52`) and its valid artifact types do not include `narrative_artifact` (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:25`, `:65-67`).
- The live narrative-artifact schema requires `target_path`, `presented_to_user`, `transcript_captured`, `explicit_change_request`, and `artifact_type_value = "narrative_artifact"` (`config/governance/narrative-artifact-approval.toml:151-167`), and the narrative gate tells authors to generate packets with `artifact_type='narrative_artifact'` (`.claude/hooks/narrative-artifact-approval-gate.py:215`).

Deficiency rationale: The proposal's stated CLI may be useful for formal artifacts, but it does not cover the narrative-artifact approval-packet workflow that the live WI identifies as the friction point. The proposal also omits `config/governance/narrative-artifact-approval.toml`, `scripts/check_narrative_artifact_evidence.py`, and the verified narrative-artifact bridge thread from its specification/test mapping.

Impact: A GO here could produce a command that passes the formal packet validator while still leaving the protected narrative-artifact workflow manual or invalid. That would not implement WI-3279 as described.

Required action: Revise the proposal to specify whether `gt generate-approval-packet` supports formal packets, narrative-artifact packets, or both. For WI-3279, the revision must include the narrative-artifact packet fields, cite `config/governance/narrative-artifact-approval.toml` and `DELIB-1901` / `gtkb-narrative-artifact-approval-extension-001`, and add tests that validate a generated narrative packet against the narrative gate or `scripts/check_narrative_artifact_evidence.py`.

## Positive Confirmations

- The live bridge entry was latest `NEW` before review and had no show-thread drift.
- The batch-4 owner authorization exists as `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`.
- Live MemBase includes active project authorization `PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH` with `WI-3279` included, and active project membership `PWM-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-WI-3279`.
- Mandatory applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

Prime Builder should file `bridge/gtkb-generate-approval-packet-cli-003.md` as `REVISED` after:

1. Adding the actual CLI registration surface or changing the command claim.
2. Aligning the packet schema with WI-3279's narrative-artifact scope, or explicitly splitting formal and narrative packet generation into separately named commands.
3. Extending the specification links and tests to cover the narrative-artifact packet registry/gate when narrative packets remain in scope.
4. Re-running and citing the mandatory preflights.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
