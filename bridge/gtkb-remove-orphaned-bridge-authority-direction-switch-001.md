NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Orphaned switch file harness-state/bridge-authority-direction.json (authority_direction=tafe_canonical) after no-index migration deleted its consumer

bridge_kind: prime_proposal
Document: gtkb-remove-orphaned-bridge-authority-direction-switch
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4629

target_paths: ["harness-state/bridge-authority-direction.json", "groundtruth-kb/tests/test_bridge_authority_direction.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The WI-4510 Phase-3 bridge authority-direction cutover left two orphaned remnants after the no-index migration deleted their only consumer. The git-tracked switch file `harness-state/bridge-authority-direction.json` still reads `authority_direction=tafe_canonical` (updated `2026-06-15T15:47:39Z`), but the module that read it — `scripts/bridge_authority_cutover.py` — was deleted in commit `0f96c4e6e` ("chore(gtkb): sweep no-index bridge closeout"). The only remaining `.py` reference to that deleted module is its now-dangling test `groundtruth-kb/tests/test_bridge_authority_direction.py`, whose `_load_module()` asserts `MODULE_PATH.is_file()` against the deleted path and therefore fails. The orphaned switch file is dead state that misrepresents a live authority toggle, and the dangling test is a broken test for deleted code. The minimal, audit-trail-complete fix is to delete both remnants of the retired cutover feature.

## Defect / Reproduction

Root cause: commit `0f96c4e6e` (no-index bridge closeout, `Tue Jun 16 13:21:23 2026`) deleted the consumer of the switch file — `scripts/bridge_authority_cutover.py` (the module exporting `read_authority_direction`, `write_authority_direction`, `direction_state_path`, `flip_to_tafe_canonical`, `revert_to_index_canonical`) — along with siblings `groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py` and `groundtruth-kb/tests/test_tafe_cutover_evidence.py`. The closeout did NOT delete (a) the git-tracked state file `harness-state/bridge-authority-direction.json`, nor (b) the test module `groundtruth-kb/tests/test_bridge_authority_direction.py` that imports the deleted consumer.

Evidence:
- `git show 0f96c4e6e --name-status` lists `D scripts/bridge_authority_cutover.py`.
- `harness-state/bridge-authority-direction.json` is present and git-tracked (`git ls-files` confirms), contents `{"authority_direction": "tafe_canonical", "updated_at": "2026-06-15T15:47:39Z", ...}`.
- A repo-wide `*.py` grep for `read_authority_direction|bridge_authority_cutover|direction_state_path|bridge-authority-direction` matches exactly ONE file: `groundtruth-kb/tests/test_bridge_authority_direction.py`. The post-migration authority modules `groundtruth-kb/src/groundtruth_kb/authority.py` and `groundtruth-kb/src/groundtruth_kb/mcp_surface/authority.py` no longer reference the switch file. No reader exists in `scripts/`, `.claude/hooks/`, or `config/`.

Reproduction (test breakage): run `python -m pytest groundtruth-kb/tests/test_bridge_authority_direction.py`. `_load_module()` (lines 31-43) executes `assert MODULE_PATH.is_file()` where `MODULE_PATH = PROJECT_ROOT / "scripts" / "bridge_authority_cutover.py"`; that path no longer exists, so module load fails and every test in the file errors. This is the source-code consequence of the orphan: a broken test referencing deleted code.

Scope note on `.pyc` cache (per the WI's secondary "sweep stale `__pycache__/*.pyc`" item): the stale `.pyc` files for the deleted `tafe_index_*` / `tafe_bridge_ingestion` / `bridge_authority_cutover` / `tafe_cutover_evidence` modules are git-IGNORED (`git check-ignore` confirms `__pycache__/*.pyc` is ignored; `git ls-files "*.pyc"` returns 0). They are regenerable byte-compilation cache, not committed project state, so they are out of scope for `target_paths` and the committed fix. Deleting them is a local cache-clean operation (`find . -path '*/__pycache__/*' -name '*.pyc' -delete` for the named modules) that may be performed during implementation but produces no tracked diff and requires no bridge/test surface.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `harness-state/bridge-authority-direction.json`, `groundtruth-kb/tests/test_bridge_authority_direction.py`. No path outside the GT-KB root is read, written, verified, or depended upon. No `applications/` or adopter surface is touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs the bridge authority model; the orphaned switch file is a stale WI-4510 Phase-3 authority-direction toggle whose consumer was deleted, so removing it keeps the bridge-authority surface consistent with the post-no-index-migration reality and removes a misleading authority artifact. This proposal is itself bridge-mediated and honors the GO/VERIFIED discipline: it is filed as the next numbered bridge file `bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-001.md` in the append-only versioned bridge file chain, and no prior bridge version is deleted or rewritten (the bridge audit trail is append-only).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The fix advances the durable artifact lifecycle by retiring a dead state artifact (the orphaned switch) and its dangling test rather than letting stale remnants accumulate; the deletion is captured as a tracked, reviewable bridge change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites every relevant governing specification for the change (mandatory spec linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The Specification-Derived Verification Plan below derives the verification steps from the cited specs (full test-suite green after the dangling test is removed, plus targeted absence assertions), as required.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal carries the mandatory Project Authorization / Project / Work Item linkage lines (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / PROJECT-GTKB-RELIABILITY-FIXES / WI-4629).
- `SPEC-AUQ-POLICY-ENGINE-001` - Not directly exercised: this fast-lane defect fix introduces no owner-decision/AUQ surface and changes no AUQ policy; cited here only because the scaffold seeded it. The change is authorized by standing reliability-fast-lane authorization (see Owner Decisions / Input), so no new AUQ is required.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The change is confined to the GT-KB platform (`harness-state/` runtime state and `groundtruth-kb/tests/`); no application/adopter placement boundary is crossed and no `applications/` surface is touched, so the isolation contract is preserved.
- `GOV-STANDING-BACKLOG-001` - WI-4629 is a standing-backlog work item (origin=defect, P3) under PROJECT-GTKB-RELIABILITY-FIXES; this proposal addresses that tracked backlog item.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Not directly exercised: the change touches no Codex/Claude hook-parity surface (no `.codex/hooks.json` / `.claude/settings.json` hook registration changes); cited only because the scaffold seeded it. Harness hook parity is unaffected by deleting a dead state file and a dangling test.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The retirement of the orphaned switch and its test remains artifact-backed and traceable: the change is recorded via the bridge thread and a reviewable commit rather than an untracked manual cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The switch file and its test reach the "retired" lifecycle state once their consumer was deleted; this fix realizes that transition by removing the dead artifacts rather than leaving them in an ambiguous live-looking state.

## Prior Deliberations

- `DELIB-20264698` - Loyal Opposition Verdict, Retired Bridge Artifact Runtime Source Cleanout Revised Proposal - directly on point: the verdict context for the runtime source cleanout that retired the bridge-index/cutover machinery whose orphaned state file this WI removes.
- `DELIB-20263786` - Bridge Index Retirement Cleanout Packet Correction Review - prior reconciliation of the bridge-index retirement cleanout; establishes the pattern of removing remnants of the retired index/authority machinery.
- `DELIB-20263285` - TAFE Live Implementation-Flow Pilot Proposal Review - origin context for the TAFE authority-direction work whose Phase-3 cutover left this switch file behind.
- `DELIB-20263275` - Loyal Opposition GO Verdict: TAFE Slice C Bridge-Thread Ingestion - sibling TAFE cutover context for the deleted `tafe_*` modules whose stale `.pyc` cache the WI also notes.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - Standing reliability fast-lane authorization. WI-4629 is origin=defect, single-concern, deletes only dead state + a dangling test, introduces no new public API/CLI/behavior, and adds no new/revised requirement or spec, so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - Owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-4629 (P3, orphaned switch-file cleanup) is in scope of that batch.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes the bridge authority model and that authority state must reflect live, consumed configuration; the orphaned switch file violates that intent by presenting a live-looking authority toggle with no consumer. Removing the dead artifact and its dangling test enforces the existing contract. No new or revised requirement/specification is introduced.

## Proposed Scope

1. Delete the orphaned, consumer-less switch file `harness-state/bridge-authority-direction.json` (git-tracked dead state; its only consumer `scripts/bridge_authority_cutover.py` was deleted in `0f96c4e6e`). Use `git rm` so the deletion is staged as a tracked change.
2. Delete the now-dangling test `groundtruth-kb/tests/test_bridge_authority_direction.py` (its `_load_module()` asserts `is_file()` on the deleted `scripts/bridge_authority_cutover.py`; the test exercises only deleted behavior and cannot pass). Use `git rm`.
3. (Local, untracked cache-clean — not part of the committed diff) remove the stale `__pycache__/*.pyc` byte-cache for the deleted `bridge_authority_cutover`, `tafe_cutover_evidence`, `tafe_bridge_ingestion`, and `tafe_index_*` modules. These are git-ignored and regenerable; no tracked path changes.

This is the defect-removal path: both remnants belong to a retired feature whose live code was already deleted. The WI's alternative framing ("document the orphaned switch file") would re-establish a live-looking authority artifact for code that no longer exists and is rejected as contrary to `GOV-FILE-BRIDGE-AUTHORITY-001`; it is out of scope for this fast-lane defect fix.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (authority state must reflect a live consumer) | absence check: `test -f harness-state/bridge-authority-direction.json` returns non-zero | The orphaned switch file no longer exists in the working tree, so no consumer-less authority toggle remains. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (retired artifacts are removed, not left live-looking) | absence check: `test -f groundtruth-kb/tests/test_bridge_authority_direction.py` returns non-zero AND a repo-wide grep for `bridge_authority_cutover` / `read_authority_direction` over `*.py` returns no matches | The dangling test is removed and no `.py` reference to the deleted consumer module remains. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (no regression; suite stays green) | full test-suite run after deletion | `python -m pytest groundtruth-kb/tests -q --tb=short` collects and passes with no errors caused by the removed module/test (the previously-erroring `test_bridge_authority_direction.py` is gone; no other test imports it). |

Execution commands:
- `python -m pytest groundtruth-kb/tests/test_bridge_authority_direction.py -q --tb=short` (pre-fix: expect collection/load ERROR proving the defect; post-fix: file is gone, "no tests ran" / deselected)
- `python -m pytest groundtruth-kb/tests -q --tb=short` (post-fix regression: full GT-KB test directory green, no import errors)
- `python -m ruff check harness-state/bridge-authority-direction.json groundtruth-kb/tests/test_bridge_authority_direction.py` (post-deletion: ruff reports no remaining files to lint for the removed paths; run against any residual changed `.py`)
- `python -m ruff format --check harness-state/bridge-authority-direction.json groundtruth-kb/tests/test_bridge_authority_direction.py` (post-deletion: format-clean / no remaining target files)

Note: because both target files are deleted, the ruff commands above will report the paths as missing post-implementation; the load-bearing verification is the absence checks plus the green full-suite pytest run. The ruff commands are retained per the mandatory pre-file code-quality gate and confirm no surviving `.py` in scope is left unformatted/lint-dirty.

## Acceptance Criteria

1. `harness-state/bridge-authority-direction.json` is deleted from the working tree and staged for commit (`git rm`).
2. `groundtruth-kb/tests/test_bridge_authority_direction.py` is deleted and staged; a repo-wide `*.py` grep for `bridge_authority_cutover` / `read_authority_direction` / `direction_state_path` returns no matches.
3. `python -m pytest groundtruth-kb/tests -q --tb=short` is green (the prior load ERROR from the dangling test is gone and no other test breaks).
4. No live consumer of the switch file remains in `groundtruth-kb/src`, `scripts/`, `.claude/hooks/`, or `config/` (confirmed unchanged from investigation).

## Risks / Rollback

- Risk: an undiscovered runtime reader of `harness-state/bridge-authority-direction.json` exists. Mitigation: investigation grep over `*.py`, `*.toml`, `*.json`, `*.md` across `groundtruth-kb/src`, `scripts/`, `.claude/hooks/`, and `config/` found zero live readers; the only match is the test being removed. The post-migration `authority.py` modules already do not read it.
- Risk: the dangling test was the last coverage for the deleted cutover behavior, so deleting it removes a test. Mitigation: the behavior under test (`scripts/bridge_authority_cutover.py`) was itself deleted in `0f96c4e6e`; there is no production surface left to cover, so the test is vestigial, not load-bearing.
- Risk: re-running tooling regenerates the stale `.pyc` cache. Mitigation: `.pyc` files are git-ignored and never enter the committed diff; the cache-clean step is cosmetic/local only.
- Rollback: `git restore --staged --worktree harness-state/bridge-authority-direction.json groundtruth-kb/tests/test_bridge_authority_direction.py` (or `git revert` the commit). The change is two file deletions with no migration and is fully reversible.

## Files Expected To Change

- `harness-state/bridge-authority-direction.json` (deleted)
- `groundtruth-kb/tests/test_bridge_authority_direction.py` (deleted)

## Recommended Commit Type

`fix`
