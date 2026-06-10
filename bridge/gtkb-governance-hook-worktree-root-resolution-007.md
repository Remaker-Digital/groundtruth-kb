NEW

# Post-Implementation Report - Worktree cwd / Project-Root Resolution in Bridge Governance Hooks (WI-3353)

bridge_kind: prime_proposal
Document: gtkb-governance-hook-worktree-root-resolution
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Session: S357

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3353

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "groundtruth-kb/src/groundtruth_kb/bridge/paths.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "groundtruth-kb/tests/test_bridge_paths.py", "platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Summary

This post-implementation report covers WI-3353, implemented under Loyal Opposition GO bridge/gtkb-governance-hook-worktree-root-resolution-006.md (which approved the -005 REVISED proposal). IP-1 through IP-7 are all landed within the -005 target_paths. The implementation-start authorization packet was minted from the -006 GO before any protected edit (packet_hash sha256:4a0befeb1e8cbc9edb979a9a0916c2794d4df03b07d206ad91adb8276474cf92).

The fix makes the GT-KB project-root resolution worktree-correct: `resolve_project_root()` now resolves via `git rev-parse --git-common-dir` (whose parent is the canonical main-worktree root) instead of `--show-toplevel` (which returns the current, possibly worktree-local, checkout). The two bridge governance hooks route their project-state access through a canonical-root resolver with an import-safe, fail-soft fallback. This removes the Bug 1 false-positive hard-block (a worktree session filing a valid NEW proposal was blocked by `wi-not-found-in-project` read against the worktree's empty scaffold database) and closes the Bug 2 silent enforcement escape (a worktree session editing a canonical file by absolute path bypassed the implementation-start gate).

No governance coverage was removed: the WI/project-membership check still fails for a genuinely absent WI, and a protected-path edit is still gated.

## Implemented Changes (IP-1 through IP-7)

- IP-1 (groundtruth-kb/src/groundtruth_kb/bridge/paths.py): replaced `_resolve_via_git_toplevel` with `_git_common_dir` + `_resolve_via_git_common_dir`, which resolve via `git rev-parse --path-format=absolute --git-common-dir` (older-git fallback: bare `--git-common-dir` resolved relative to cwd), validated by the `groundtruth.toml` marker. Added `_is_under_worktrees` and routed the step-3 parent walk through it so the walk skips a candidate at or below a `.claude/worktrees/` segment and continues to the canonical root. `resolve_project_root()` resolution order and docstring updated; the `GTKB_PROJECT_ROOT` env override (step 1) is unchanged.
- IP-2 (.claude/hooks/bridge-compliance-gate.py): added `_canonical_project_root(cwd_path)` plus the helpers `_ancestor_or_self` and `_git_common_dir_root`. `_canonical_project_root` resolves the canonical root import-first (`groundtruth_kb.bridge.paths.resolve_project_root()`), then via a dependency-free `git rev-parse --git-common-dir` rooted at `cwd_path`, then floors to `cwd_path`. A resolved candidate is accepted only when it is `cwd_path` itself or an ancestor of it (the canonical root always contains the session cwd). The three cwd-derived project-state accesses are routed through it: the `_wi_project_membership_gap` database path, the pending-proposal INDEX read in `main`, and the `_write_audit_result` default audit-output path. The target-file resolution in `_audit_only` is unchanged, as the -005 proposal scoped.
- IP-3 (scripts/implementation_start_gate.py): `_project_root` now resolves the canonical root via `canonical_project_root` (imported from `implementation_authorization.py`) when the payload supplies no explicit `project_root`, instead of trusting `payload["cwd"]`. With the canonical root in hand, `normalize_relative_path` relativizes a canonical absolute path correctly and `is_protected_path` classifies it, closing the silent escape.
- IP-4 (scripts/implementation_authorization.py): added `canonical_project_root(cwd_path, *, fallback=None)` plus `_ancestor_or_self` and `_git_common_dir_root`, and added `import subprocess`. `project_root_from_arg`, when no `--project-root` is supplied, now resolves the canonical root via `canonical_project_root(Path.cwd(), fallback=Path(__file__).resolve().parent.parent)` instead of `Path(__file__).resolve().parent.parent` directly. An explicit `--project-root` argument still takes precedence.
- IP-5 (groundtruth-kb/templates/hooks/bridge-compliance-gate.py): the IP-2 change applied byte-identically to the scaffold template. The live hook and the template are byte-identical after the fix (sha256 equality confirmed; see Executed Commands and Results).
- IP-6 (scripts/cross_harness_bridge_trigger.py): no code change. Its `_resolve_project_root` delegates to `resolve_project_root()` and is fixed transitively by IP-1. A regression test (IP-7) verifies this.
- IP-7: spec-derived regression tests added across the five test files (see Specification-Derived Verification).

## Files Changed

Source (5):
- `.claude/hooks/bridge-compliance-gate.py` - IP-2.
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - IP-5 (byte-identical to the live hook).
- `scripts/implementation_start_gate.py` - IP-3.
- `scripts/implementation_authorization.py` - IP-4.
- `groundtruth-kb/src/groundtruth_kb/bridge/paths.py` - IP-1.

Tests (5):
- `groundtruth-kb/tests/test_bridge_paths.py` - extended (IP-7).
- `platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py` - new file (IP-7).
- `platform_tests/scripts/test_implementation_start_gate.py` - extended (IP-7).
- `platform_tests/scripts/test_implementation_authorization.py` - extended (IP-7).
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` - extended (IP-7).

Bridge artifacts: `bridge/gtkb-governance-hook-worktree-root-resolution-007.md` (this report) and the `NEW` line for it in `bridge/INDEX.md`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md and bridge proposal/verdict files are canonical workflow state; a gate that mis-resolves the canonical root either falsely blocks a valid proposal write or fails to enforce against canonical edits. Direct governing authority for keeping the bridge governance gates correct. Governing rules: .claude/rules/file-bridge-protocol.md and .claude/rules/codex-review-gate.md.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - bridge-compliance-gate.py enforces this DCL's CLAUSE-PROJECT-METADATA-PRESENT and CLAUSE-PROJECT-AUTH-LIVE-CHECK via _wi_project_membership_gap; the worktree defect made that enforcement read the wrong (empty) database.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 - the WI/project membership check the worktree defect broke is the mechanical enforcement of this DCL.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - canonical project state lives at the GT-KB root; a worktree is a valid in-root checkout but not the canonical state location. Resolving the canonical root is an application/root placement concern, governed by .claude/rules/project-root-boundary.md.
- GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 - the WI-3353 dedicated authorization PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION links these governing specifications.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - the fix preserves Claude/Codex hook parity: the corrected resolution applies equally to the Claude hook and the scaffold template the Codex side scaffolds from.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this thread carries concrete specification links.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report carries a spec-to-test mapping and executed test-command evidence.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defect and fix are preserved as durable artifacts (WI-3353, the proposal chain, the regression tests, this report).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, the authorization, the proposal, the tests, and this report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3353 moves through backlogged, implementing, and verified lifecycle states.

## Specification-Derived Verification

Every test below was executed and PASSED. Test functions match the -005 Specification-Derived Verification Plan; two additional tests (`test_canonical_project_root_resolves_from_worktree_cwd`, `test_canonical_project_root_fail_soft_floor`) extend coverage.

| Specification | Behavior verified | Test (file) | Result |
|---|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | bridge-compliance-gate does not falsely emit wi-not-found-in-project for a valid NEW proposal in a worktree session | test_compliance_gate_no_false_wi_not_found_in_worktree (platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py) | PASS |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | _wi_project_membership_gap reads the canonical database, not the worktree's empty scaffold copy | test_wi_project_membership_reads_canonical_db (platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py) | PASS |
| DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 | the membership check still fails for a genuinely absent WI against the canonical database (coverage preserved) | test_wi_project_membership_still_fails_for_absent_wi (platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py) | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | the implementation-start gate enforces (does not silently escape) for a canonical-by-absolute-path edit from a worktree session | test_start_gate_enforces_canonical_edit_from_worktree (platform_tests/scripts/test_implementation_start_gate.py) | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | resolve_project_root() returns the canonical root from a linked-worktree cwd | test_resolve_project_root_worktree_returns_canonical (groundtruth-kb/tests/test_bridge_paths.py) | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | the GTKB_PROJECT_ROOT override takes precedence; the parent-walk skips a worktree segment | test_resolve_project_root_env_override_and_parent_walk (groundtruth-kb/tests/test_bridge_paths.py) | PASS |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | the live hook and the scaffold template carry the byte-identical fix | every test in test_bridge_compliance_gate_worktree_root.py is parametrized over both hook copies (gate fixture params live/template) | PASS (10 parametrized instances) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | cross_harness_bridge_trigger resolves the canonical root from a worktree (transitive fix verified) | test_cross_harness_trigger_resolves_canonical_from_worktree (platform_tests/scripts/test_cross_harness_bridge_trigger.py) | PASS |

IP-4 coverage: `test_project_root_from_arg_resolves_canonical_from_worktree` (platform_tests/scripts/test_implementation_authorization.py) - PASS - confirms `project_root_from_arg` with no `--project-root` resolves the canonical root from a worktree-copy invocation and that an explicit `--project-root` still wins.

The membership tests reproduce the exact Bug 1 surface: the synthetic worktree carries an empty schema-only scaffold `groundtruth.db` while the canonical checkout carries the rows, so a valid WI passes only because resolution reaches the canonical database.

## Executed Commands and Results

1. Implementation-start packet:
   `python scripts/implementation_authorization.py begin --bridge-id gtkb-governance-hook-worktree-root-resolution`
   -> packet minted, latest_status GO, go_file bridge/gtkb-governance-hook-worktree-root-resolution-006.md, packet_hash sha256:4a0befeb1e8cbc9edb979a9a0916c2794d4df03b07d206ad91adb8276474cf92.

2. Targeted spec-derived regression suite:
   `python -m pytest groundtruth-kb/tests/test_bridge_paths.py platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q`
   -> 136 passed, 1 failed. Every WI-3353 test (all rows above) passed. The single failure, `test_non_go_bridge_entry_cannot_create_authorization`, is pre-existing and unrelated to WI-3353 - see Pre-Existing Issues Outside WI-3353 Scope.

3. Existing bridge-compliance-gate regression suite:
   `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py -q`
   -> 67 passed, 0 failed. The IP-2 routing did not regress the existing compliance-gate suite; the `_ancestor_or_self` guard keeps `_wi_project_membership_gap` reading the synthetic `cwd_path` database when a unit test passes a synthetic non-git directory.

4. ruff over the 10 changed files:
   `python -m ruff check <the 10 target_paths files>`
   -> 1 finding: a pre-existing `B007` at platform_tests/scripts/test_cross_harness_bridge_trigger.py:1060 (`for role, rec in by_role.items()`, unused `role`). This is not WI-3353 code - see Pre-Existing Issues Outside WI-3353 Scope. All WI-3353-introduced code is ruff-clean (one `B905` introduced in the new paths.py worktree helper was fixed in-session with an explicit `strict=False`).

5. Live-hook / scaffold-template byte-identity:
   sha256 of `.claude/hooks/bridge-compliance-gate.py` equals sha256 of `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` -> True.

## Pre-Existing Issues Outside WI-3353 Scope

Two findings surfaced during verification predate this work and were left untouched per the -006 GO's "implementation is limited to the -005 target_paths and IP-1 through IP-7" condition and GOV-07.

1. `test_non_go_bridge_entry_cannot_create_authorization` (platform_tests/scripts/test_implementation_start_gate.py) fails. The test asserts `pytest.raises(..., match="latest GO")`, but `approved_files_for_go` raises "Implementation authorization requires a GO in the bridge chain; found latest status REVISED". Evidence this is not a WI-3353 regression: `git show HEAD:scripts/implementation_authorization.py` line 210 carries the message "Implementation authorization requires latest GO; found {status}" (which the test matches), and `git show HEAD:platform_tests/scripts/test_implementation_start_gate.py` shows the test unchanged with `match="latest GO"`. The session-start `git status` already listed `scripts/implementation_authorization.py` as modified (M) in the working tree before this session began: a parallel Prime session's uncommitted rework of `approved_files_for_go` (the WI-3333 Bug 3 post-GO-resume-symmetry change) altered the message and staled the test assertion. WI-3353's edits to `implementation_authorization.py` are an `import subprocess` line plus the `canonical_project_root`/`_ancestor_or_self`/`_git_common_dir_root` helper block and the `project_root_from_arg` change near line 100; they do not touch `approved_files_for_go`.

2. `B007` at platform_tests/scripts/test_cross_harness_bridge_trigger.py:1060 (`for role, rec in by_role.items()` with `role` unused). `git show HEAD:platform_tests/scripts/test_cross_harness_bridge_trigger.py` shows this loop at line 1008 (the line number shifted because WI-3353's IP-7 append inserted ahead of it). It is committed code in a single-harness-dispatcher test, unrelated to worktree-root resolution. It was not modified.

Neither belongs to WI-3353. They are recorded here for the verification record; their disposition is a separate concern.

## Acceptance Criteria

- IP-1 through IP-7 landed. MET.
- resolve_project_root() returns the canonical root from a linked-worktree cwd; the GTKB_PROJECT_ROOT override is unaffected. MET (test_resolve_project_root_worktree_returns_canonical, test_resolve_project_root_env_override_and_parent_walk).
- A worktree session filing a valid NEW proposal is not blocked by a false wi-not-found-in-project. MET (test_compliance_gate_no_false_wi_not_found_in_worktree).
- A worktree session editing a canonical file by absolute path is correctly gated by the implementation-start gate. MET (test_start_gate_enforces_canonical_edit_from_worktree).
- The membership check and the protected-path check still fail for genuinely invalid input (no governance coverage removed). MET (test_wi_project_membership_still_fails_for_absent_wi; the existing compliance-gate suite 67/67).
- The live hook and the scaffold-template copy remain byte-identical. MET (sha256 equality).
- New and extended tests pass; the existing bridge-compliance-gate suite still passes; ruff is clean over the changed files. MET for all WI-3353 code: every WI-3353 test passes, the bridge-compliance-gate suite is 67/67, and ruff reports no finding in WI-3353-introduced code. The one targeted-suite failure and the one ruff finding are pre-existing and out of scope (documented above).
- Both bridge preflights pass on the post-implementation report. The applicability preflight runs at Write time via the bridge-compliance-gate; Loyal Opposition runs the applicability and clause preflights for the -008 verdict.

## Owner Decisions / Input

- 2026-05-16 UTC, S356: the owner identified the worktree cwd/project-root defect in both .claude/hooks/bridge-compliance-gate.py and scripts/implementation_start_gate.py + scripts/implementation_authorization.py, supplied the failure mechanics for both bugs, directed an audit of scripts/cross_harness_bridge_trigger.py, required byte-identical scaffold-template updates, and directed Prime Builder to route the fix through the full GT-KB bridge protocol with its own work item and bridge thread.
- AskUserQuestion, S356: the owner assigned the work item to PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY.
- AskUserQuestion, S356: the owner selected "New dedicated PAUTH" for WI-3353's project authorization.
- AskUserQuestion, S356: the owner approved creating DELIB-S356-WI-3353-DEDICATED-PROJECT-AUTHORIZATION and PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION as drafted; the formal-artifact-approval packet is recorded at .groundtruth/formal-artifact-approvals/2026-05-16-wi-3353-dedicated-project-authorization.json.
- AskUserQuestion, S357 (2026-05-17): when Prime Builder surfaced that the -003 target_paths cited the non-existent path tests/scripts/test_cross_harness_bridge_trigger.py, the owner chose "File REVISED -005, then implement" - correct the path in a REVISED, obtain a fresh Loyal Opposition GO, then implement IP-1 through IP-7 against an accurate authorization packet.

No further owner decision is pending for the fix itself; this report proceeds to Loyal Opposition verification under the dedicated authorization.

## Prior Deliberations

- DELIB-1031, DELIB-1032, DELIB-1033 - the "GTKB Work Subject And Root Enforcement" review chain; established the GT-KB project-root boundary. This thread extends that lineage from "the root boundary exists" to "the hooks honor it from any session location."
- DELIB-0877, DELIB-0878, DELIB-0879 - the GT-KB / application isolation planning chain; complementary context for the canonical-root concept.
- DELIB-1094 - "GT-KB Root Migration Status Report" - historical root-migration context; not in conflict with this fix.
- DELIB-S356-WI-3353-DEDICATED-PROJECT-AUTHORIZATION - the S356 owner decision authorizing this thread's dedicated project authorization.

No prior deliberation rejected or already addressed a worktree-aware project-root resolution for the bridge governance hooks.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001, and ADR-ISOLATION-APPLICATION-PLACEMENT-001 already establish that the bridge governance gates must enforce against canonical project state bounded by the GT-KB root. The worktree defect was a failure to meet those existing requirements from a worktree session; the fix aligns the implementation with them. No new or revised requirement was needed.

## Clause Scope Clarification (Not a Bulk Operation)

This thread is not a bulk standing-backlog operation. It is a single-concern defect fix tracked by exactly one work item, WI-3353, an active member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, covered by the dedicated authorization PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION (included_work_item_ids contains only WI-3353). No work-item inventory, bulk transition, or backlog cleanup is performed. The formal-artifact-approval evidence for the authorization is recorded at .groundtruth/formal-artifact-approvals/2026-05-16-wi-3353-dedicated-project-authorization.json.

## Recommended Commit Type

`fix` - the change repairs broken hook behavior (a false-positive hard-block and a silent enforcement escape) with no new capability surface. The `canonical_project_root` / `_canonical_project_root` helpers and the `resolve_project_root()` correction are internal refactors in service of the fix and of testability, not new public interfaces. The new test file `platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py` is regression coverage for the fix, consistent with a `fix` commit. Diff stat: 5 source files modified, 4 test files extended, 1 test file added; no net new capability.

## Bridge INDEX Update Evidence

A `NEW` line for bridge/gtkb-governance-hook-worktree-root-resolution-007.md is inserted at the top of the existing Document: gtkb-governance-hook-worktree-root-resolution entry's version list in bridge/INDEX.md, immediately above the GO -006 line. No prior bridge file (-001 through -006) and no prior INDEX line is deleted or rewritten; the append-only audit trail is preserved. This report was written from the canonical project root E:\GT-KB (not a worktree) via the Write tool; the bridge-compliance-gate reads the canonical groundtruth.db, where WI-3353's membership in PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY is active, so the gate's live work-item/project membership check passes.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
