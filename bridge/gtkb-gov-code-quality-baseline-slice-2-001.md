NEW

# Implementation Proposal - GTKB-GOV-CODE-QUALITY-BASELINE Slice 2 (hook + verifier + tests + formal artifacts)

bridge_kind: implementation_proposal
Document: gtkb-gov-code-quality-baseline-slice-2
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py", "scripts/check_code_quality_baseline_parity.py", "platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py", "platform_tests/scripts/test_check_code_quality_baseline_parity.py", "groundtruth.db"]

## Claim

The parent Slice 1 governance bridge `gtkb-gov-code-quality-baseline-slice1` is GO at `-006` (Slice 1 governance design approved; Slice 2 implementation proposal authorized). This Slice 2 implements the Tier-1 mechanical hook plus the Tier-3 post-implementation parity verifier per Codex's tier-separation conditions.

Tier 1 (proposal-time mechanical check) and Tier 3 (post-impl source/diff scan) are implemented in this slice. Tier 2 (Loyal Opposition review judgment) is preserved as a non-mechanical review responsibility, not implemented as a hook.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-gov-code-quality-baseline-slice-2-001.md`. Hook at `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\hooks\code_quality_baseline_proposal_check.py`. Parity script at `E:\GT-KB\scripts\check_code_quality_baseline_parity.py`. Tests under `E:\GT-KB\platform_tests\`. No `applications/` paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - one tracking work_item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - code-quality rule IDs are governance artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - hook + parity script are tracked artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - hook gates proposal lifecycle.
- `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` - parent Slice 1 operative proposal (REVISED-1 GO'd).
- `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` - Codex Slice 1 GO authorizing Slice 2.

## Prior Deliberations

- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit authorization.
- Parent Slice 1 chain `gtkb-gov-code-quality-baseline-slice1 -001 through -006` - full prior history.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner prompt "Please continue with..." authorizes this slice-2 filing.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work".

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. Operating under parent Slice 1 GO's authorization.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation; one tracking work_item; introduces Tier-1 mechanical hook + Tier-3 parity script under Slice 1's tier separation.

## Proposed Scope

### IP-1: Tier-1 mechanical proposal-time hook

In `groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py`:

- PreToolUse hook entry point for Write/Edit of `bridge/*.md` files with `bridge_kind: implementation_proposal` header.
- Tier-1 checks:
  - Table shape: any markdown table in the proposal must have well-formed rows.
  - Rule ID well-formedness: any cited `CQ-NAME-NNN` rule ID matches pattern `^CQ-[A-Z]+-\d{3}$`.
  - Row well-formedness: rule-table rows have non-empty rule ID column.
  - Waiver/N/A shape: waiver lines match `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` format.
  - Vague-phrase scan: rejects obvious vague phrases (`TBD`, `to be determined`, `pending`, `???` in rule-table rows).

Hook returns block decision on Tier-1 failure; returns `{}` (allow) on pass.

### IP-2: Tier-3 post-implementation parity verifier

In `scripts/check_code_quality_baseline_parity.py`:

- CLI: `python scripts/check_code_quality_baseline_parity.py --since <commit-sha>` runs source/diff scan against current HEAD vs cited baseline commit.
- Scans for the 9 canonical rule IDs from Slice 1: CQ-COMPLEXITY-001, CQ-CONSTANTS-001, CQ-SECRETS-001, CQ-VERIFICATION-001, etc.
- Reports violations in markdown-table form for inclusion in post-impl reports.

Exit code 0 = clean; exit 1 = violations present; exit 2 = invocation error.

### IP-3: Regression tests

`platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py`:
- Tier-1 hook allows a well-formed proposal.
- Tier-1 hook blocks on malformed table shape.
- Tier-1 hook blocks on invalid rule ID format.
- Tier-1 hook blocks on vague phrase.
- Tier-1 hook ignores non-proposal bridge files (verdicts, advisories).

`platform_tests/scripts/test_check_code_quality_baseline_parity.py`:
- Parity script returns 0 on clean diff.
- Parity script returns 1 on diff with secret-shape token.
- Parity script returns 1 on diff with hardcoded path violation.

### IP-4: Tracking work_item

One `work_items` row: origin=`new`, component=`code-quality`, source_spec_id (TBD until GOV-CODE-QUALITY-BASELINE-001 formal-artifact-approval lands in follow-on slice).

## Specification-Derived Verification Plan

1. `python -m pytest platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py platform_tests/scripts/test_check_code_quality_baseline_parity.py -v` - all tests PASS.
2. `python -m ruff check groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py scripts/check_code_quality_baseline_parity.py` - zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` - PASS.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` - exit 0.
5. End-to-end smoke: invoke Tier-1 hook against a known well-formed proposal (e.g., `bridge/gtkb-startup-payload-canonical-state-drift-001.md`) and verify allow.
6. End-to-end smoke: invoke Tier-3 parity script against current HEAD and verify exit 0.
7. MemBase tracking WI inserted.

## Risks and Rollback

- **Risk**: Tier-1 hook over-blocks legitimate proposals with non-canonical table shapes. Mitigation: tier separation explicit; only mechanical shape checks at Tier 1; substantive judgment is Tier 2 (Loyal Opposition).
- **Risk**: Tier-3 parity scan false-positives on benign source patterns. Mitigation: scan exits 1 but doesn't gate VERIFIED; review evidence in post-impl report.
- Rollback: revert hook + parity script + tests.

## Sequenced Dependencies

Slice 2 depends on Slice 1 (governance design + 9 canonical rule IDs). Future slices may add Tier-2 review template extensions or formal-artifact-approval insertion for GOV-CODE-QUALITY-BASELINE-001.

## Recommended Commit Type

`feat:` - new Tier-1 hook + Tier-3 parity script + tests.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` flat bullets.
- Non-empty `## Prior Deliberations`.
- Non-empty `## Owner Decisions / Input`.
- target_paths JSON; all in-root.
- `## Requirement Sufficiency` one state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` present.
- `## In-Root Placement Evidence` present.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
