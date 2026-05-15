NEW

# Implementation Proposal - gt generate-approval-packet CLI (WI-3279)

bridge_kind: implementation_proposal
Document: gtkb-generate-approval-packet-cli
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3279

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/tests/test_cli_approval_packet.py"]

This NEW proposal lands `gt generate-approval-packet` CLI for deterministic packet generation with LF normalization. Currently every approval packet authoring requires manual handling of (a) text-mode LF-normalized read, (b) sha256 of UTF-8 bytes, (c) JSON serialization with consistent field ordering — the same boilerplate I wrote 4 times this session.

## Claim

CLI: `gt generate-approval-packet --artifact-type <type> --artifact-id <id> --action insert --content-file <path> --change-reason <text> --source-ref <ref> [--approved-by owner] [--out <path>]`. Reads content file with LF normalization, computes sha256, emits JSON packet matching the formal-artifact-approval schema.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - CLI emits packets matching this gate's expected schema.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - generated packet must satisfy hook validation.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI is a thin surface over the policy engine.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3279 tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-APPROVAL-PACKET-ERGONOMICS authorization including WI-3279.

## Requirement Sufficiency

Existing requirements sufficient. WI-3279 description is the operative spec.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: CLI implementation

`groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py`:
- Click group registered as `gt generate-approval-packet`.
- Required: `--artifact-type` (in valid set), `--artifact-id`, `--action`, `--change-reason`, `--source-ref`.
- Either `--content-file` or `--content-stdin` for full_content source.
- Normalization: read text mode + replace CRLF with LF (Windows-safe).
- Compute sha256 of UTF-8 bytes.
- Emit JSON with stable field order matching existing packet examples.
- `--out` writes to file; default writes to stdout.
- `--validate-after` re-validates the emitted packet against `groundtruth_kb.governance.approval_packet.validate_packet`.

### IP-2: Tests

Verify all field requirements, hash correctness, LF normalization, validation pass.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Packet schema fields all present | `test_packet_fields_complete` |
| sha256 matches LF-normalized content | `test_sha_lf_normalized` |
| --validate-after passes for emitted packet | `test_validate_after_passes` |
| CRLF input normalizes correctly | `test_crlf_input_normalizes_to_lf` |
| Invalid artifact_type rejected | `test_invalid_artifact_type_rejected` |
| Content-stdin path works | `test_content_stdin_mode` |

Run: `python -m pytest groundtruth-kb/tests/test_cli_approval_packet.py -v`.

## Acceptance Criteria

- IP-1 CLI landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: schema drift between CLI and hook validator. Mitigation: import the shared validate_packet at the end of generation.
- Rollback: remove the CLI module.

## Recommended Commit Type

`feat` - new CLI surface. ~80 LOC.
