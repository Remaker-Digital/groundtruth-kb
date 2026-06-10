NEW

# Implementation Proposal - Advance GTKB-ARTIFACT-RECORDER-CLI Scoping (WI-3263)

bridge_kind: prime_proposal
Document: gtkb-artifact-recorder-cli-scoping-advance
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3263

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_artifact_recorder.py", "groundtruth-kb/tests/test_cli_artifact_recorder.py", "platform_tests/cli/test_artifact_recorder_cli.py"]

This NEW proposal advances `GTKB-ARTIFACT-RECORDER-CLI` from concept to first-slice scaffold. The artifact-recorder is the first concrete manifestation of the Deterministic Services Principle (DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE) — moving formal-artifact insertion plumbing from per-session AI-mediated work into a deterministic `gt <artifact-type> record` CLI surface.

## Claim

Add `gt artifact record` command group with subcommands for `deliberation`, `spec`, `gov`, `adr`, `dcl`, `pb`. Each accepts the artifact's required fields (id, title, content, change_reason, etc.) plus `--approval-packet <path>` for governance evidence. Wraps the corresponding `KnowledgeDB.insert_*` method with consistent argument shape and packet citation in change_reason. First slice covers `deliberation` and `spec` only; ADR/DCL/PB/GOV in follow-on slices.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - umbrella governance principle the CLI operationalizes.
- `GOV-ARTIFACT-APPROVAL-001` - CLI cites approval-packet evidence per gate requirements.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI is a thin surface over the policy engine.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3263 tracked.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the principle this CLI manifests.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - principle definition; this CLI is its named manifestation per CLAUDE.md.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - batch-3 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner directive "Please continue with the next priority project. I would like to parallelize as many implementation proposals as possible." - authorizes this NEW.

## Requirement Sufficiency

Existing requirements sufficient. WI-3263 description + DELIB-S312 fully specify the surface for Slice 1.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch3-deterministic-services-authorization.json`. Review-packet inventory: IP-1 (CLI Slice 1) + IP-2 (tests) single thread. Slice 2+ (ADR/DCL/PB/GOV subcommands) deferred to follow-on bridges.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-artifact-recorder-cli-scoping-advance-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: CLI module + `deliberation` and `spec` subcommands

In `groundtruth-kb/src/groundtruth_kb/cli_artifact_recorder.py`:

```python
@click.group()
def artifact(): ...

@artifact.group()
def record(): ...

@record.command("deliberation")
@click.option("--id", required=True)
@click.option("--source-type", required=True)
@click.option("--title", required=True)
@click.option("--content", required=True)
@click.option("--outcome", default="owner_decision")
@click.option("--approval-packet", required=True, type=click.Path(exists=True))
@click.option("--change-reason", required=True)
def record_deliberation(id, source_type, title, content, outcome, approval_packet, change_reason):
    # validate packet (call validate_packet from approval_packet module)
    # ensure change_reason cites approval_packet path
    # call db.insert_deliberation(...)
    ...

@record.command("spec")
@click.option("--id", required=True)
@click.option("--title", required=True)
@click.option("--type", required=True, type=click.Choice([...]))
@click.option("--description", required=True)
@click.option("--approval-packet", required=True, type=click.Path(exists=True))
@click.option("--change-reason", required=True)
def record_spec(...): ...
```

Wire into the existing `groundtruth_kb.cli` root group.

### IP-2: Tests + no spec promotion

Tests cover: packet-citation validation, ID auto-detect-prefix, error handling for missing packet, end-to-end insert.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| record deliberation with valid packet creates row | `test_record_deliberation_creates_row` |
| record deliberation without packet fails | `test_record_deliberation_requires_packet` |
| record spec with valid packet creates row | `test_record_spec_creates_row` |
| spec ID prefix auto-detects type | `test_record_spec_type_autodetect_from_id` |
| change_reason auto-cites packet path | `test_record_change_reason_cites_packet` |
| packet validation rejects invalid packet | `test_record_validates_packet_before_insert` |

Run: `python -m pytest groundtruth-kb/tests/test_cli_artifact_recorder.py -v`.

## Acceptance Criteria

- IP-1 CLI Slice 1 landed; 6 tests PASS.
- Both preflights PASS.
- No regression in existing CLI tests.

## Risks / Rollback

- Risk: CLI duplicates `db.insert_*` defaults; drift if signatures change. Mitigation: import enum values from db module.
- Rollback: remove the new module + its registration.

## Recommended Commit Type

`feat` - new CLI surface. ~150 LOC (CLI + tests).
