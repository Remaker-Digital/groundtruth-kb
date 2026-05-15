NEW

# Implementation Proposal - Proposal-Standards Work-Item-ID Collision Gate (Slice 3)

bridge_kind: implementation_proposal
Document: gtkb-proposal-standards-wi-id-collision-gate
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE3

target_paths: ["scripts/bridge_proposal_wi_id_collision_check.py", "tests/scripts/test_bridge_proposal_wi_id_collision_check.py", "platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py"]

This NEW proposal lands GTKB-GOV-PROPOSAL-STANDARDS Slice 3: a pre-review hook that cross-references any `GTKB-ISOLATION-NNN`/`GTKB-DASHBOARD-NNN`/`GTKB-GOV-NNN` or `WI-NNNN` IDs cited in a bridge proposal against MemBase, flagging ID collisions (cited ID already used by another WI than the one declared in metadata).

## Claim

CLI: `python scripts/bridge_proposal_wi_id_collision_check.py --bridge-id <id>`. Scans bridge content for any pattern matching `(?:GTKB-[A-Z]+-\d+|WI-\d+)`, looks up each in MemBase `current_work_items`, and flags entries where the cited ID exists but does NOT match the `Work Item:` metadata declaration. Non-blocking by default; `--strict` returns non-zero on collisions.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; this check supports the review packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must cite specs; this enforces internal consistency on WI IDs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `GOV-STANDING-BACKLOG-001` - GTKB-GOV-PROPOSAL-STANDARDS-SLICE3 tracked.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)".

## Requirement Sufficiency

Existing requirements sufficient. GTKB-GOV-PROPOSAL-STANDARDS-SLICE3 description is the operative spec.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (Slice 3); member of PROJECT-GTKB-GOV-PROPOSAL-STANDARDS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. Review-packet inventory: IP-1 (collision check) + IP-2 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: Collision-detection CLI

`scripts/bridge_proposal_wi_id_collision_check.py`:

1. Read bridge proposal `bridge/<bridge-id>-NNN.md`.
2. Parse `Work Item:` metadata line for declared WI.
3. Extract all `(?:GTKB-[A-Z]+-\d+|WI-\d+)` patterns from the document.
4. For each unique ID, query `current_work_items` for the row.
5. If the ID exists as a different WI than declared in metadata, flag as collision in the output JSON.
6. Emit `Collision Check` markdown section with table: cited_id, exists_in_membase, matches_declared.
7. Exit 0 unless `--strict` AND collisions present.

### IP-2: Tests + (no spec promotion - new tool)

Tests cover: collision detection, no-collision case, multiple-collision case, strict-mode exit code.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| No collisions when only declared WI cited | `test_no_collision_when_only_declared_wi` |
| Collision detected on alien WI cited | `test_collision_detected_on_alien_wi` |
| Multiple collisions enumerated | `test_multiple_collisions_listed` |
| Strict mode non-zero exit | `test_strict_mode_exits_nonzero_on_collision` |
| Non-strict default exit zero | `test_default_exit_zero_on_collision` |
| Output JSON schema | `test_output_json_schema` |
| Ignore IDs in code-fence blocks | `test_ignore_ids_in_fenced_code_blocks` |

Run: `python -m pytest tests/scripts/test_bridge_proposal_wi_id_collision_check.py -v`.

## Acceptance Criteria

- IP-1 collision-check landed; 7 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: legitimate cross-references to other WIs (e.g., dependency listings) get flagged. Mitigation: report-only by default; --strict only when invoked explicitly.
- Rollback: remove script.

## Recommended Commit Type

`feat` - new check tool. ~70 LOC.
