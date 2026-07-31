NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f38dc-dc71-7af2-a3ba-d3e17ae4f13b
author_model: gpt-5
author_model_version: codex-desktop-2026-07-06
author_model_configuration: codex-desktop; approval_policy=never; sandbox=danger-full-access

# Governance Advisory - WI-4980 Runtime Projection Gitignore Authorization

bridge_kind: governance_advisory
Document: gtkb-wi4980-runtime-projection-gitignore-authorization
Version: 001
Date: 2026-07-06 UTC

## Claim

`WI-4980` is explicitly owner-gated in MemBase because it has no PAUTH and no related bridge thread. This proposal preserves the requested hygiene path without bypassing that gate.

## Evidence

- `WI-4980` is open under `PROJECT-GTKB-RELIABILITY-FIXES`, subproject `Work-Tree Hygiene`, and links `GOV-WORK-TREE-HYGIENE-001`.
- The current `status_detail` says no active PAUTH coverage or related bridge thread exists and owner authorization, deferral, or retirement is required before proposal filing.
- A targeted query of `project_authorizations` found no active row whose `included_work_item_ids` contains `WI-4980`.
- The noisy files are regenerating harness runtime projections such as `.cursor/gtkb-hooks/last-session-start.json` and startup markdown/meta outputs.

## Requested Disposition

- Review whether WI-4980 should receive bounded authorization, be merged into an existing work-tree hygiene slice, or remain deferred.
- If approved, require fresh item-specific PAUTH, independent bridge GO, and implementation-start packet before protected edits.
- Future implementation must avoid destructive cleanup, stash drops, broad worktree mutation, or committing unrelated dirty files.

## Candidate Target Paths

- `.gitignore`
- `scripts/hygiene_strays.py`
- `scripts/worktree_finalization_triage.py`
- `platform_tests/scripts/test_hygiene_strays_cli.py`
- `platform_tests/scripts/test_worktree_finalization_triage.py`

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification linkage on proposals that may lead to implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/authorization linkage or a valid non-implementation exemption.
- `GOV-WORK-TREE-HYGIENE-001` - source requirement for reducing permanent worktree noise.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-gated implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded PAUTH before implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents backlog-only processing from becoming implementation approval.

## Prior Deliberations

- 2026-07-03 owner AUQ - investigate dirty work-tree and file systematic hygiene backlog items.
- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` - nearby hygiene batch context, not direct WI-4980 authority.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner requested this work in the current Prime Builder session, then directed Prime Builder to file proposals after the bridge/authorization blocker was surfaced.

## Verification Plan For Future Implementation

| Requirement | Verification |
| --- | --- |
| Ignore scope | Tests must prove only regenerating runtime projections are ignored or auto-classified. |
| No destructive cleanup | Verification must show no delete, stash-drop, broad cleanup, or unrelated commit behavior. |
| Signal quality | Focused hygiene/finalization tests must show real work remains visible. |

## Rollback

This proposal changes no protected implementation files. Future rollback must revert only authorized source/test/config changes and preserve bridge, PAUTH, and audit records as append-only evidence.
