NEW

# Implementation Proposal - Active-Workspace Declaration Slice 1 (specs + resolver + validator)

bridge_kind: implementation_proposal
Document: active-workspace-declaration-slice-1
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["groundtruth-kb/src/groundtruth_kb/active_workspace.py", "scripts/check_workspace_boundary.py", ".claude/rules/active-workspace.md", "harness-state/claude/active-workspace.md", "harness-state/codex/active-workspace.md", "platform_tests/groundtruth_kb/test_active_workspace_resolver.py", "platform_tests/scripts/test_check_workspace_boundary.py", "groundtruth.db"]

## Claim

The parent scoping bridge `active-workspace-declaration-architecture-2026-04-29` is GO at `-004` (architecture/scoping approval; implementation slices must each file their own bridge). This Slice 1 implements the foundational layer that subsequent slices depend on:

1. Resolver module `groundtruth_kb.active_workspace` returning `(active_workspace, hosted_application_id)` from durable records OR a blocking diagnostic.
2. Durable record file `.claude/rules/active-workspace.md` (project default `gt-kb`) plus per-harness records under `harness-state/<harness>/active-workspace.md`.
3. Repo-native validator `scripts/check_workspace_boundary.py` invoked by `python scripts/check_workspace_boundary.py` for shell/script coverage.

Slice 2 will add the hook layer (UserPromptSubmit + PreToolUse) and write-boundary gates. Slice 3+ covers application-tree integration.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\active-workspace-declaration-slice-1-001.md`. Source at `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\active_workspace.py`. Validator at `E:\GT-KB\scripts\check_workspace_boundary.py`. Durable records at `E:\GT-KB\.claude\rules\active-workspace.md` and `E:\GT-KB\harness-state\<harness>\active-workspace.md`. Tests under `E:\GT-KB\platform_tests\`. No `applications/` paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - per-harness records align with role-portability principles.
- `GOV-STANDING-BACKLOG-001` - one tracking work_item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable records are governance artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - resolver output is a tracked artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - active-workspace transitions trigger lifecycle events.
- `.claude/rules/project-root-boundary.md` - workspace boundary aligns with project-root-boundary.
- `bridge/active-workspace-declaration-architecture-2026-04-29-003.md` - parent operative proposal (REVISED-1 GO'd).
- `bridge/active-workspace-declaration-architecture-2026-04-29-004.md` - Codex GO authorizing follow-on slices.

## Prior Deliberations

- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit authorization.
- Parent thread chain `active-workspace-declaration-architecture-2026-04-29 -001 through -004` - full prior deliberation history carried forward.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner prompt "Please continue with..." authorizes this slice-1 filing.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work".

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. Operating under parent GO's scoping authority.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation; one tracking work_item; foundational implementation layer for Slice 2+ work.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This proposal is filed at `bridge/active-workspace-declaration-slice-1-001.md` with a `Document: active-workspace-declaration-slice-1` + `NEW:` entry inserted at the top of `bridge/INDEX.md`. The INDEX update is additive; no prior INDEX entry or bridge file is deleted or rewritten. The append-only audit trail at `bridge/INDEX.md` preserves the full version sequence for this thread.

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

This implementation is NOT a bulk operation against the standing backlog. It creates exactly one tracking `work_item` per IP-5. The inventory for this slice is the IP-1 resolver module + IP-2 durable record files + IP-3 validator + IP-4 regression tests + IP-5 tracking WI packet enumeration. The review-packet is this proposal plus the parent thread chain `bridge/active-workspace-declaration-architecture-2026-04-29 -001 through -004`. No formal-artifact-approval packet is required because no protected narrative artifact is edited (the new `.claude/rules/active-workspace.md` and per-harness durable records are new files, not edits to existing protected artifacts; the protected-narrative-artifact registry covers existing files, not new file creation in the canonical-rules tree).

## Proposed Scope

### IP-1: `groundtruth_kb.active_workspace` resolver module

New module at `groundtruth-kb/src/groundtruth_kb/active_workspace.py`. Public API:

```python
class WorkspaceResolution(NamedTuple):
    active_workspace: Literal["gt-kb", "hosted-application"]
    hosted_application_id: str | None
    source: Literal["project_default", "harness_record", "owner_confirmed"]

def resolve(project_root: Path, harness_id: str | None = None) -> WorkspaceResolution | str:
    """Return WorkspaceResolution or a blocking-diagnostic string."""
```

Behavior:
- Read `.claude/rules/active-workspace.md` first (project default).
- If `harness_id` provided, read `harness-state/<harness>/active-workspace.md` overlay.
- Missing project record → default to `gt-kb`.
- Malformed records → blocking diagnostic.
- Divergent per-harness records without owner-confirmation evidence → blocking diagnostic.

### IP-2: Durable record files

Create `.claude/rules/active-workspace.md` with header `active_workspace: gt-kb` (project default). Create `harness-state/claude/active-workspace.md` and `harness-state/codex/active-workspace.md` as empty per-harness records (gt-kb effective).

### IP-3: Repo-native validator

New script at `scripts/check_workspace_boundary.py`. Invocation: `python scripts/check_workspace_boundary.py [--workspace gt-kb|hosted-application] [--harness <id>]`. Returns:
- Exit 0: workspace resolution consistent + boundary satisfied for current writes.
- Exit 1: blocking-diagnostic resolution failure.
- Exit 2: write outside allowed boundary detected.

### IP-4: Regression tests

In `platform_tests/groundtruth_kb/test_active_workspace_resolver.py`:
- `test_resolve_returns_gt_kb_default_when_no_records` - missing project record → `gt-kb`.
- `test_resolve_reads_project_default_record` - reads `.claude/rules/active-workspace.md`.
- `test_resolve_blocks_on_malformed_record` - malformed → blocking diagnostic.
- `test_resolve_blocks_on_divergent_harness_record_without_evidence` - per-harness divergence without owner evidence → blocking.
- `test_resolve_rejects_canonical_value_agent_red` - `active_workspace: agent-red` rejected (canonical values limited to `gt-kb` and `hosted-application`).

In `platform_tests/scripts/test_check_workspace_boundary.py`:
- `test_validator_exit_0_when_consistent` - clean state.
- `test_validator_exit_1_on_blocking_diagnostic` - malformed record.
- `test_validator_allows_bridge_writes_during_hosted_application_state` - bridge writes must remain allowed.

### IP-5: Tracking work_item

One `work_items` row: origin=`new`, component=`active-workspace`, source_spec_id (TBD when DCL/ADR insertion proposal lands).

## Specification-Derived Verification Plan

1. `python -m pytest platform_tests/groundtruth_kb/test_active_workspace_resolver.py platform_tests/scripts/test_check_workspace_boundary.py -v` - all tests PASS.
2. `python -m ruff check groundtruth-kb/src/groundtruth_kb/active_workspace.py scripts/check_workspace_boundary.py` - zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id active-workspace-declaration-slice-1` - PASS.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id active-workspace-declaration-slice-1` - exit 0.
5. End-to-end smoke: `python scripts/check_workspace_boundary.py` returns exit 0 against current GT-KB state.
6. MemBase tracking WI inserted.

## Risks and Rollback

- **Risk**: per-harness records cause confusion when harness IDs change. Mitigation: harness-identity stability already enforced by `harness-state/harness-identities.json`. Rollback: revert resolver + records.
- **Risk**: validator over-blocks legitimate bridge writes. Mitigation: explicit test for `bridge/**` write-allowance during hosted-application state.

## Sequenced Dependencies

Slice 1 is foundation for Slice 2 (hook layer + write-boundary gates). Sister thread `gtkb-spec-lifecycle-schema-slice-1` (parallel filing this session) is referenced for vocabulary alignment; verify status before downstream slice sequencing.

## Recommended Commit Type

`feat:` - new resolver module + durable records + validator + tests.

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
