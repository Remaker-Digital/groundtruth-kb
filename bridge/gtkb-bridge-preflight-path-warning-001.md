NEW

# Implementation Proposal - Bridge Preflight: Missing Parent Directory Warning (WI-3272)

bridge_kind: implementation_proposal
Document: gtkb-bridge-preflight-path-warning
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH
Project: PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS
Work Item: WI-3272

target_paths: ["scripts/bridge_applicability_preflight.py", "tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

This NEW proposal extends `scripts/bridge_applicability_preflight.py` with a warning when a bridge proposal cites `Files Changed` or `target_paths` paths whose parent directory does not exist. Observed defect during S341 (bridge `gtkb-peer-solution-workflow-contract-adr` REVISED-3): a test path was cited that pointed to a non-existent directory, surfaced only at implementation time.

## Claim

Add a non-blocking advisory warning to the preflight output listing cited paths whose parent directory does not exist relative to the project root. Existing pass/fail semantics preserved; warning surfaces in the `Applicability Preflight` section text and as a stderr line for tooling.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-bridge-preflight-path-warning-001.md`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` - preflight is part of the policy engine surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - preflight enforces this; this enhancement is a quality-of-output improvement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3272 tracked.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization 2026-05-14.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" - explicit authorization for this NEW.

## Requirement Sufficiency

Existing requirements sufficient. WI-3272 description is the operative spec; no new spec needed.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3272) targeted; member of PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 scoped to one thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-bridge-preflight-path-warning-001.md`; new top entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Add parent-directory check to preflight

In `scripts/bridge_applicability_preflight.py`, after parsing the bridge content's `target_paths` array and any `Files Changed` table:

1. For each cited path, compute its parent directory relative to project root.
2. If the parent directory does not exist (and the path itself doesn't exist as a target), add the path to a `warnings.missing_parent_dirs` list in the output JSON and the markdown section.
3. Render in the `Applicability Preflight` markdown section as `- warnings.missing_parent_dirs: [...]` line beneath `preflight_passed`.
4. Non-blocking: does not change exit code; preflight_passed semantics unchanged.

### IP-2: Tests + spec promotion

Tests cover: cited path with valid parent (no warning), cited path with missing parent (warning emitted), mixed valid+invalid (only invalid in warning list). No spec to promote (no source spec).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Cited path with existing parent | `test_preflight_no_warning_when_parent_exists` |
| Cited path with missing parent | `test_preflight_warns_when_parent_missing` |
| Mixed valid+invalid | `test_preflight_warns_only_invalid_paths` |
| Existing path itself | `test_preflight_no_warning_when_path_exists` |
| Output schema preserved | `test_preflight_output_passes_existing_schema_test` |

Run: `python -m pytest tests/scripts/test_bridge_applicability_preflight.py -v`.

## Acceptance Criteria

- IP-1 landed; 5 tests PASS.
- preflight_passed unchanged for existing inputs.
- Both preflights PASS for this bridge ID.

## Risks / Rollback

- Risk: false-positive when paths exist but in a worktree branch not yet merged. Mitigation: check both git ls-tree HEAD and filesystem.
- Rollback: revert single function addition.

## Recommended Commit Type

`feat` - non-blocking warning enhancement. ~20 LOC.
