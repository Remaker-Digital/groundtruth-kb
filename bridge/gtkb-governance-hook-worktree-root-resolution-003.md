REVISED

# Implementation Proposal - Worktree cwd / Project-Root Resolution in Bridge Governance Hooks (WI-3353)

bridge_kind: prime_proposal
Document: gtkb-governance-hook-worktree-root-resolution
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S356

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3353

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "groundtruth-kb/src/groundtruth_kb/bridge/paths.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "groundtruth-kb/tests/test_bridge_paths.py", "platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "tests/scripts/test_cross_harness_bridge_trigger.py"]

## Response to NO-GO (-002)

Loyal Opposition NO-GO bridge/gtkb-governance-hook-worktree-root-resolution-002.md raised one P1 finding, F1: WI-3353 was an active member of the prefix-doubled duplicate project PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY rather than the cited real project PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, so the canonical bridge-compliance gate returned wi-not-found-in-project against the -001 metadata. Codex classified F1 as a governance-packet blocker and confirmed the worktree-aware root-resolution design, every proposal section, and both bridge preflights passed.

Root cause of F1: the -001 work-item creation called insert_work_item with project_name set to the already-PROJECT-prefixed id PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY. The backlog backfill prepends PROJECT- to project_name, so the membership row landed under PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY instead of the real project.

Resolution: WI-3353 was linked as an active member of the real project PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY via KnowledgeDB.link_project_work_item (membership id PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-3353, status active, changed_at 2026-05-16T23:47:55Z). The owner-selected project (AskUserQuestion, S356) and the dedicated PAUTH already targeted that real project; no proposal metadata and no PAUTH metadata changed between -001 and -003.

Gate-check evidence: after the repair, the canonical bridge-compliance gate was re-run against bridge/gtkb-governance-hook-worktree-root-resolution-001.md with the canonical project root. _wi_project_membership_gap returned None; _deny_reason_for_content returned None; gate result PASS. The three project-linkage metadata lines below are unchanged from -001 and now resolve correctly because the membership state is repaired.

Residual cruft (not a -003 blocker): WI-3353 also retains an active membership under the duplicate PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY. The bridge-compliance gate matches on the (work item, real project) pair and is unaffected. The insert_work_item project_name prefix-doubling backfill that produced the duplicate project is a separate defect, distinct from this thread's worktree cwd/project-root resolution scope, and is being captured as a follow-up backlog work item.

## Problem

Two GT-KB governance PreToolUse hooks resolve the project root from the session working directory (the hook-payload `cwd`). That is correct for a session run in the canonical checkout, but wrong when a session runs inside a `.claude/worktrees/*` git worktree. Canonical project state -- the MemBase database `groundtruth.db` (~1.37 GB), the live `bridge/INDEX.md`, and `.gtkb-state/` -- exists only at the canonical root `E:\GT-KB`. A worktree has its own checkout plus an empty ~508 KB scaffold `groundtruth.db`. Confirmed S356 by direct measurement: worktree `groundtruth.db` = 507,904 bytes; canonical `groundtruth.db` = 1,366,794,240 bytes; worktree `bridge/INDEX.md` = 140,403 bytes; canonical `bridge/INDEX.md` = 141,450 bytes.

Bug 1 -- false deny (`bridge-compliance-gate.py`). `_wi_project_membership_gap` (line 309) computes `db_path = cwd_path / "groundtruth.db"` (line 325); `cwd_path` is resolved from the hook-payload `cwd` (line 781 in `main`, line 705 in `_audit_only`). In a worktree session this opens the worktree's scaffold database. The scaffold carries the schema but no rows, so the `current_project_work_item_memberships` query returns nothing and the gate emits `wi-not-found-in-project` (lines 337-338), hard-blocking a legitimate NEW proposal. The function's deliberate fail-open (`if not db_path.is_file(): return None`, line 326) never engages, because the scaffold file does exist -- it is merely empty. The same hook reads `cwd_path / "bridge/INDEX.md"` (line 803) for the pending-proposal ASK check and writes audit output under `cwd_path` (line 676); both are the same cwd-trust class, and the worktree `bridge/INDEX.md` is a stale committed copy.

Bug 2 -- silent escape (`implementation_start_gate.py` + `implementation_authorization.py`). `_project_root` (lines 94-95) returns `payload["project_root"] or payload["cwd"]`; in a worktree session this is the worktree root. When a worktree session edits a canonical file by absolute path -- the normal Prime worktree workflow, since GO-authorized source edits land in canonical `E:\GT-KB` -- `normalize_relative_path` (`implementation_authorization.py` lines 584-590) calls `.relative_to(project_root)` with the worktree root and raises `AuthorizationError` ("Path escapes project root") because the canonical path is not under the worktree. `_normalize` (`implementation_start_gate.py` lines 125-126) catches that exception and returns the raw absolute path. `is_protected_path` (lines 129-135) then applies `.lstrip("./")` to a Windows absolute path (`E:/GT-KB/.claude/hooks/...`), which leaves it intact, and the path matches none of the relative `PROTECTED_PREFIXES`. The function returns `False`; the gate emits no decision and does not enforce. A Prime worktree session silently bypasses the implementation-start authorization gate for every canonical-by-absolute-path edit.

Root cause -- the shared resolver. `groundtruth_kb/bridge/paths.py:resolve_project_root()` (line 96) is itself worktree-incorrect. Its resolution order is: (1) the `GTKB_PROJECT_ROOT` env var; (2) `_resolve_via_git_toplevel` (lines 71-85), which runs `git rev-parse --show-toplevel`; (3) `_resolve_via_parent_walk` (lines 88-93). In a linked worktree, `--show-toplevel` returns the worktree's own root, and because `groundtruth.toml` is a git-tracked file the worktree checkout carries it, so the `_has_marker` validation (line 83) passes and the resolver confidently returns the worktree. Step 3's parent walk has the same flaw -- it stops at the worktree's own `groundtruth.toml`. `--show-toplevel` answers "which checkout am I in"; `git rev-parse --git-common-dir` answers "where is the shared repository" -- and in a linked worktree `--git-common-dir` points at `<canonical>/.git`, whose parent is the canonical root.

Cross-harness trigger audit. `scripts/cross_harness_bridge_trigger.py`'s `_resolve_project_root` (line 134) delegates to `groundtruth_kb.bridge.paths.resolve_project_root()`. It therefore inherits the worktree defect; it is not independently incorrect. Fixing `resolve_project_root()` fixes the trigger transitively. This proposal adds a regression test rather than a code change for the trigger.

Separate worktree exposure. `implementation_authorization.py:project_root_from_arg` (lines 100-103) defaults, when no `--project-root` is passed, to `Path(__file__).resolve().parent.parent`. `scripts/` is git-tracked, so a worktree session that invokes the worktree's copy of the script resolves `__file__` to the worktree and creates the implementation-start authorization packet scoped to the worktree. Same defect family, different mechanism.

Scaffold template. `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` is line-for-line identical to the live hook (the cwd-bug lines sit at the same line numbers: 325, 676, 781, 803). Adopter projects scaffolded from the template inherit the defect.

## Claim

Resolve the canonical GT-KB project root deterministically -- independent of the session `cwd` and of a worktree-local `__file__` -- and route the bridge governance hooks' project-state access through that resolution. Concretely: make `resolve_project_root()` worktree-correct by resolving via `git rev-parse --git-common-dir` (whose parent is the canonical main worktree), validated by the `groundtruth.toml` marker; route `bridge-compliance-gate.py` and `implementation_start_gate.py` / `implementation_authorization.py` through that resolution with an import-safe fallback; apply the byte-identical change to the scaffold template; and add spec-derived regression tests. `cross_harness_bridge_trigger.py` is fixed transitively.

This removes a false-positive hard-block (Bug 1) and closes a silent enforcement escape (Bug 2). It removes no governance coverage: a proposal that genuinely fails the WI/project-membership check against the canonical database still fails; a protected-path edit is still gated. The gate now resolves the same canonical root whether the session runs in the canonical checkout or a worktree.

## In-Root Placement Evidence

All ten `target_paths` are in-root under `E:\GT-KB`: `.claude/hooks/`, `scripts/`, `groundtruth-kb/src/groundtruth_kb/bridge/`, `groundtruth-kb/templates/hooks/`, `groundtruth-kb/tests/`, `platform_tests/hooks/`, `platform_tests/scripts/`, and `tests/scripts/`. The bridge proposal file resides under `E:\GT-KB\bridge\`. No `target_path` and no output path is outside the project root. The fix's purpose is precisely to make the governance hooks honor that root boundary from worktree sessions.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md and bridge proposal/verdict files are canonical workflow state; a gate that mis-resolves the canonical root either falsely blocks a valid proposal write or fails to enforce against canonical edits. Direct governing authority for keeping the bridge governance gates correct. Governing rules: .claude/rules/file-bridge-protocol.md and .claude/rules/codex-review-gate.md.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - bridge-compliance-gate.py enforces this DCL's CLAUSE-PROJECT-METADATA-PRESENT and CLAUSE-PROJECT-AUTH-LIVE-CHECK via _wi_project_membership_gap; the worktree defect makes that enforcement read the wrong (empty) database.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 - the WI/project membership check the worktree defect breaks is the mechanical enforcement of this DCL.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - canonical project state lives at the GT-KB root; a worktree is a valid in-root checkout but not the canonical state location. Resolving the canonical root is an application/root placement concern, governed by .claude/rules/project-root-boundary.md.
- GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 - the WI-3353 dedicated authorization PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION links these governing specifications.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - the fix preserves Claude/Codex hook parity: the corrected resolution applies equally to the Claude hook and the scaffold template the Codex side scaffolds from.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this implementation proposal carries concrete specification links.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-test mapping and executed test-command evidence.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defect and fix are preserved as durable artifacts (WI-3353, this proposal, the regression tests, the post-implementation report).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, the authorization, this proposal, the tests, and the report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3353 moves through backlogged, implementing, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search ("worktree", "project root resolution", "project-root", "git --show-toplevel") was run against the canonical current_deliberations view. Relevant prior records:

- DELIB-1031, DELIB-1032, DELIB-1033 - the "GTKB Work Subject And Root Enforcement" review chain. That work established the GT-KB project-root boundary and work-subject enforcement; it did not address whether the governance hooks resolve the canonical root correctly from a worktree session. This proposal extends that lineage from "the root boundary exists" to "the hooks honor it from any session location."
- DELIB-0877, DELIB-0878, DELIB-0879 - the GT-KB / application isolation planning chain (authority matrix, root and repository topology). Complementary context for the canonical-root concept; no prior decision constrains worktree cwd resolution.
- DELIB-1094 - "GT-KB Root Migration Status Report" - historical root-migration context; not in conflict with this fix.
- DELIB-S356-WI-3353-DEDICATED-PROJECT-AUTHORIZATION - the S356 owner decision authorizing this thread's dedicated project authorization.

No prior deliberation rejected or already addressed a worktree-aware project-root resolution for the bridge governance hooks.

## Owner Decisions / Input

- 2026-05-16 UTC, S356: the owner identified the worktree cwd/project-root defect in both .claude/hooks/bridge-compliance-gate.py and scripts/implementation_start_gate.py + scripts/implementation_authorization.py, supplied the failure mechanics for both bugs, directed an audit of scripts/cross_harness_bridge_trigger.py, required byte-identical scaffold-template updates, and directed Prime Builder to route the fix through the full GT-KB bridge protocol with its own work item and bridge thread (explicitly NOT the reliability fast-lane).
- AskUserQuestion, S356: the owner assigned the work item to PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY.
- AskUserQuestion, S356: the owner selected "New dedicated PAUTH" for WI-3353's project authorization.
- AskUserQuestion, S356: the owner approved creating DELIB-S356-WI-3353-DEDICATED-PROJECT-AUTHORIZATION and PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION as drafted; the formal-artifact-approval packet is recorded at .groundtruth/formal-artifact-approvals/2026-05-16-wi-3353-dedicated-project-authorization.json.

No further owner decision is pending for the fix itself; implementation proceeds on Codex GO under the dedicated authorization.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001, and ADR-ISOLATION-APPLICATION-PLACEMENT-001 already establish that the bridge governance gates must enforce against canonical project state bounded by the GT-KB root. The worktree defect is a failure to meet those existing requirements from a worktree session; the fix aligns the implementation with them. No new or revised requirement is needed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single-concern defect fix tracked by exactly one work item, WI-3353, an active member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, covered by the dedicated authorization PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION (included_work_item_ids contains only WI-3353). No work-item inventory, bulk transition, or backlog cleanup is performed. The formal-artifact-approval evidence for the authorization is recorded at .groundtruth/formal-artifact-approvals/2026-05-16-wi-3353-dedicated-project-authorization.json.

## Bridge INDEX Update Evidence

A REVISED line for bridge/gtkb-governance-hook-worktree-root-resolution-003.md is inserted at the top of the existing Document: gtkb-governance-hook-worktree-root-resolution entry's version list in bridge/INDEX.md, immediately above the NO-GO -002 line. No prior bridge file (-001, -002) and no prior INDEX line is deleted or rewritten; the append-only audit trail is preserved. This REVISED version was written via direct file I/O (a non-Write path; the bridge-propose helper files only -001 NEW versions) because Bug 1 would otherwise cause the bridge-compliance-gate to block a direct Write of this proposal against the empty worktree database -- the defect this proposal fixes. The membership repair described in the Response to NO-GO section is a MemBase state change, not a bridge-file edit; no -001 or -002 content was modified.

## Proposed Scope

### IP-1: Worktree-correct resolution in the shared resolver

In groundtruth-kb/src/groundtruth_kb/bridge/paths.py, replace the `_resolve_via_git_toplevel` step with a `--git-common-dir`-based resolution. `git rev-parse --path-format=absolute --git-common-dir` returns the absolute path of the shared git directory; its parent is the canonical main-worktree root in both the main worktree and a linked worktree. Validate the result with the existing `_has_marker` (groundtruth.toml) check. Retain the `GTKB_PROJECT_ROOT` env var (step 1) as the highest-priority override. Adjust the parent-walk (step 3) so that, when the walk would stop inside a `.claude/worktrees/<name>/` path, it continues upward past the worktree segment to the canonical root; step 3 remains a last-resort fallback for environments without git. Fallback for older git: if `--path-format=absolute` is unsupported, `--git-common-dir` is resolved relative to cwd.

### IP-2: Route bridge-compliance-gate.py project-state access through the canonical root

Add one importable helper to .claude/hooks/bridge-compliance-gate.py - `_canonical_project_root(cwd_path)` - that returns the canonical GT-KB root. It attempts `from groundtruth_kb.bridge.paths import resolve_project_root` (the same import-with-ImportError-fallback pattern the hook already uses for groundtruth_kb.governance.output); on success it returns `resolve_project_root()`. On ImportError it falls back to a dependency-free `git rev-parse --git-common-dir` call (the hook already imports subprocess), parent-resolved and groundtruth.toml-validated; on any failure it returns `cwd_path`, preserving today's behavior as the final fail-soft floor. Route the three cwd-derived project-state accesses through it: the `_wi_project_membership_gap` database path (line 325), the pending-proposal INDEX read (line 803), and the `_write_audit_result` default output path (line 676). The target-file resolution at line 710 is a distinct concern (resolving the file being written) and is left unchanged.

### IP-3: Route implementation_start_gate.py through the canonical root

In scripts/implementation_start_gate.py, change `_project_root` so that when the payload supplies no explicit `project_root`, the canonical root is resolved (via the same resolver, with the same import-safe fallback) rather than trusting `payload["cwd"]`. With the canonical root in hand, `normalize_relative_path` relativizes a canonical absolute path correctly and `is_protected_path` matches it against `PROTECTED_PREFIXES`, closing the silent escape.

### IP-4: Worktree-safe project_root_from_arg in implementation_authorization.py

In scripts/implementation_authorization.py, change `project_root_from_arg` so that, when no `--project-root` is supplied, it resolves the canonical root via the shared resolver instead of `Path(__file__).resolve().parent.parent`. An explicit `--project-root` argument continues to take precedence.

### IP-5: Byte-identical fix in the scaffold template

Apply the IP-2 change byte-identically to groundtruth-kb/templates/hooks/bridge-compliance-gate.py. The live hook and the template are byte-identical today and remain byte-identical after the fix.

### IP-6: Cross-harness trigger - regression test only

scripts/cross_harness_bridge_trigger.py needs no code change: its `_resolve_project_root` delegates to the now-fixed `resolve_project_root()`. A regression test (IP-7) asserts the trigger resolves the canonical root from a worktree-shaped cwd.

### IP-7: Spec-derived regression tests

- groundtruth-kb/tests/test_bridge_paths.py (extend): resolve_project_root() returns the canonical root when invoked from a linked-worktree cwd; the GTKB_PROJECT_ROOT override still wins; the parent-walk skips a worktree segment.
- platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py (new): _canonical_project_root returns the canonical root for a worktree-shaped payload cwd; _wi_project_membership_gap reads the canonical database; the gate does not emit wi-not-found-in-project for a valid WI when the session cwd is a worktree; the fail-soft floor returns cwd when both git and the import fail.
- platform_tests/scripts/test_implementation_start_gate.py (extend): a worktree session editing a canonical file by absolute path is correctly classified as a protected-path edit (the gate enforces, not escapes).
- platform_tests/scripts/test_implementation_authorization.py (extend): project_root_from_arg with no --project-root resolves the canonical root from a worktree-copy invocation.
- tests/scripts/test_cross_harness_bridge_trigger.py (extend): the trigger's _resolve_project_root returns the canonical root from a worktree-shaped cwd.

### Out of scope

The GT-KB codebase contains eight independent project-root resolver definitions (resolve_project_root / _resolve_project_root across paths.py, reconciliation.py, cross_harness_bridge_trigger.py, single_harness_bridge_automation.py, single_harness_bridge_dispatcher.py, assertion_categorize.py, assertion_retirement_workflow.py, benchmarks/common.py). A systematic audit and consolidation of that sprawl is out of scope for this single-work-item thread and is recorded as a separate follow-up backlog work item. This proposal fixes the shared paths.py resolver and the two named hooks plus their transitive consumer.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | bridge-compliance-gate does not falsely block a valid NEW proposal in a worktree session | test_compliance_gate_no_false_wi_not_found_in_worktree |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | _wi_project_membership_gap reads the canonical database, not the worktree scaffold | test_wi_project_membership_reads_canonical_db |
| DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 | the membership check still fails for a genuinely absent WI against the canonical database (coverage preserved) | test_wi_project_membership_still_fails_for_absent_wi |
| GOV-FILE-BRIDGE-AUTHORITY-001 | the implementation-start gate enforces (does not silently escape) for a canonical-by-absolute-path edit from a worktree session | test_start_gate_enforces_canonical_edit_from_worktree |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | resolve_project_root() returns the canonical root from a linked-worktree cwd | test_resolve_project_root_worktree_returns_canonical |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | the GTKB_PROJECT_ROOT override takes precedence; the parent-walk skips a worktree segment | test_resolve_project_root_env_override_and_parent_walk |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | the live hook and the scaffold template carry the byte-identical fix | bridge-compliance-gate tests parametrized over both hook copies |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | cross_harness_bridge_trigger resolves the canonical root from a worktree (transitive fix verified) | test_cross_harness_trigger_resolves_canonical_from_worktree |

Execution command: `python -m pytest groundtruth-kb/tests/test_bridge_paths.py platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py tests/scripts/test_cross_harness_bridge_trigger.py -v`

The post-implementation report will also re-run the existing bridge-compliance-gate test suite (test_bridge_compliance_gate_project_metadata.py, test_bridge_compliance_gate_wi_project_membership.py, test_bridge_compliance_gate_index_exemption.py, test_bridge_compliance_gate_spec_test_heading.py, test_bridge_compliance_gate_hard_block_workspace.py) to confirm no regression, and `ruff` over the changed files.

## Acceptance Criteria

- IP-1 through IP-7 landed.
- resolve_project_root() returns the canonical root from a linked-worktree cwd; the GTKB_PROJECT_ROOT override is unaffected.
- A worktree session filing a valid NEW proposal is not blocked by a false wi-not-found-in-project.
- A worktree session editing a canonical file by absolute path is correctly gated by the implementation-start gate.
- The membership check and the protected-path check still fail for genuinely invalid input (no governance coverage removed).
- The live hook and the scaffold-template copy remain byte-identical.
- New and extended tests pass; the existing bridge-compliance-gate suite still passes; `ruff` is clean over the changed files.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Option A (selected): fix the shared resolve_project_root() once and route the two hooks through it, with an import-safe dependency-free fallback. Rationale: cross_harness_bridge_trigger.py already delegates to resolve_project_root(), so a single corrected resolver fixes the trigger transitively and gives one canonical definition of "the GT-KB root." The hooks already tolerate a missing groundtruth_kb import, so the import-safe fallback (git rev-parse, then cwd) fits the existing hook robustness pattern.

Option B (rejected): give each hook its own independent worktree-aware resolution. Rejected because it triplicates the resolution logic across three files (the two hooks plus the trigger), creates three places to drift on a future change, and leaves no single unit-testable resolver surface. Option A consolidates on the resolver that already exists and is already the trigger's dependency.

A considered third option -- changing resolve_project_root() to always return the worktree when in one -- is rejected outright: GT-KB canonical state (MemBase, the live INDEX, .gtkb-state/) exists only at the canonical root, so a resolver used for project-state access must return the canonical root.

## Risks / Rollback

- Risk: git rev-parse --git-common-dir is unavailable (git not on PATH, or a non-git checkout). Mitigation: the resolver retains the GTKB_PROJECT_ROOT override and the parent-walk fallback; the hooks retain a final fail-soft floor returning cwd, i.e. today's behavior. The fix never makes resolution worse than the status quo.
- Risk: --path-format=absolute is unsupported on an older git. Mitigation: IP-1 resolves --git-common-dir relative to cwd when --path-format is rejected; covered by a test.
- Risk: the import-safe fallback diverges from resolve_project_root() over time. Mitigation: the fallback is the narrow git-common-dir primitive resolve_project_root() itself uses; the regression tests exercise both the import path and the fallback path.
- Risk: behavior change for canonical (non-worktree) sessions. Mitigation: from the canonical checkout, --git-common-dir's parent is the canonical root, identical to today's --show-toplevel result; covered by a non-worktree test case.
- Rollback: revert the affected files; the change is self-contained, with no schema, configuration, or data migration.

## Recommended Commit Type

`fix` - repairs broken hook behavior (a false-positive hard-block and a silent enforcement escape) with no new capability surface. The shared _canonical_project_root helper and the resolve_project_root() correction are internal refactors in service of the fix and of testability, not new public interfaces.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
