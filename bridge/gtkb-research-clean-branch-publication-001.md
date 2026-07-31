NEW

# Research Branch — Clean-Branch Publication to origin/develop

bridge_kind: prime_proposal
Document: gtkb-research-clean-branch-publication
Version: 001
Author: Prime Builder (Antigravity, harness C, interactive pb transcript-override)
Date: 2026-07-17 UTC

author_identity: prime-builder/antigravity/C
author_harness_id: C
author_session_context_id: cb17fdc1-27d0-4083-babf-6200cfdc0d6e
author_model: Gemini 3.5 Flash (High)
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity interactive Prime Builder; transcript role-override via ::init gtkb pb; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-RESEARCH-PUBLISH-20260717
Project: PROJECT-GTKB-TREE-STABILIZATION-WORKTREE-FINALIZATION
Work Item: WI-5403

target_paths: ["bridge/gtkb-research-clean-branch-publication-001.md"]

# Note: The implementation git operation targets the remote branch origin/codex/publish-20260717-clean-branch.
# This is a git-push-only operation with no local file mutations beyond the bridge artifact already filed.
# The target_paths above lists the sole local artifact produced; the push range is verified blob-free before execution.

implementation_scope: Create clean publication branch from origin/develop; overlay committed content at 42a252ab; verify zero oversized blobs in push range; push to origin
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

The local `research` branch stands 1,256 commits ahead of `origin/HEAD` (main)
and 485 commits ahead of `origin/develop`. The `research` object graph contains
multiple 694 MB `groundtruth.db` binary blobs from historical snapshots; a
direct push would be rejected by GitHub's 100 MB file-size limit and would
pollute the remote object store permanently.

The safe publication path is:

1. Create a new clean branch `codex/publish-20260717-clean-branch` from
   `origin/develop` (no local object reuse).
2. Use `git checkout 42a252ab -- <paths>` to overlay the committed file content
   at the current HEAD onto the clean branch, **excluding** `groundtruth.db`
   and any other blob exceeding 50 MB.
3. Commit the overlaid content on the clean branch with a scoped commit message
   referencing this bridge thread.
4. Run `git rev-list origin/develop..codex/publish-20260717-clean-branch | xargs -I{} git cat-file -s {}` (or equivalent PowerShell pipeline) to verify that
   every object in the push range is ≤ 50 MB. Gate: zero objects above threshold.
5. Push `codex/publish-20260717-clean-branch` to `origin`. Do **not** push
   `research` directly or force-push any remote branch.

This proposal also registers a bounded PAUTH (`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-RESEARCH-PUBLISH-20260717`) that explicitly permits `git_push` and `database_write` (for the PAUTH registration transaction itself) while forbidding all other mutation classes.

Additionally, the staged foreign bridge artifact
`bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` (staged by
another harness in the shared dirty workspace) is included as a passive carry
into the clean branch only if it was already committed into `42a252ab`. If it
is only staged (not committed), it is **not** included; the staging index is
not carried through the clean branch overlay.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is the status-bearing bridge artifact that authorizes the publication work; only the role-authorized next verdict may be filed after LO review.
- `GOV-WORK-TREE-HYGIENE-001` — the working tree must not accumulate committed large-blob objects; clean-branch publication is the governed hygiene path.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — project commits must not include out-of-scope or unauthorized content; the clean branch preserves that invariant.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the observed blob-size pathology, the proposal, implementation report, and verification remain a traceable artifact graph.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` — governed branch promotion requires a scoped commit and no unrelated file carryover.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, work item, and exact targets are machine-readable above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every applicable governing requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent VERIFIED requires the spec-mapped verification checks in the Spec-Derived Verification Plan section below.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — filing, PAUTH registration, implementation, and verification are distinct lifecycle transitions; this proposal covers only the filing transition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the blob-size pathology, owner decision option A, and this proposal are captured as durable artifacts before any implementation.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — governed Git lifecycle requires bounded dispatcher coordination; this push does not trigger dispatcher or TAFE mutation.

## Prior Deliberations

- No prior deliberation directly addresses clean-branch publication strategy.
  The general prohibition on pushing `research` directly is established by the
  continuous pattern of blob-size enforcement observations since the first
  `groundtruth.db` carrier commit.
- `DELIB-20260717-TREE-STABILIZATION-PUBLICATION-A` (to be created by Loyal
  Opposition if a prior-deliberation record is required by gate review) — owner
  directed option A (new bounded bridge proposal) for publication gate.

## Owner Decisions / Input

The owner directed option A: file a new bounded bridge proposal for the
clean-branch publication operation rather than relying on an existing GO scope.
This direction was given in the interactive Prime Builder session `cb17fdc1`
at 2026-07-17T01:14Z.

The owner also stated:
- Do not push `research` directly.
- Publication must use a clean branch from the remote target.
- Verify the push-range object list has no huge blobs before pushing.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001` and
`ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` jointly require that only clean,
blob-safe content reaches the remote. `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
requires scoped commits. No new formal artifact is required beyond the PAUTH
registration that this proposal packages.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "Owner directive 2026-07-17 ::init gtkb pb session; research branch blob-size enforcement; WI-5403",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001; ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001; DCL-GIT-BRANCH-BINDING-PROMOTION-001",
  "primary_route": "Create clean branch from origin/develop; overlay 42a252ab committed content excluding blobs >50 MB; blob-size-verify push range; push clean branch",
  "before_behavior": "Local research branch 1256 commits ahead, unreachable from remote due to 694 MB historical blobs; no governed publication path active.",
  "after_behavior": "Remote origin/develop is 485 commits closer to the research HEAD; a clean publication branch carries exactly the committed content without large-blob contamination.",
  "self_descriptive_naming": "Clean branch name includes date and 'clean-branch' suffix; commit message references WI-5403 and this bridge thread.",
  "obsolete_guidance_disposition": "No existing guidance is retired; this is an additive one-time publication operation.",
  "history_preservation": "research branch, its full history, all local commits, and groundtruth.db remain in the local worktree unchanged; remote receives only the clean overlay.",
  "baseline": {
    "research_commits_ahead_of_develop": 485,
    "largest_blob_in_push_range_bytes": 694726656,
    "remote_publish_path": "none active"
  },
  "expected_result": {
    "research_commits_ahead_of_develop": 485,
    "clean_branch_max_blob_bytes": 52428800,
    "remote_publish_path": "origin/codex/publish-20260717-clean-branch"
  },
  "rollback": {
    "instructions": "Delete the remote branch: git push origin --delete codex/publish-20260717-clean-branch. No local branch, commit, or database state is altered by the rollback.",
    "verification": "Confirm git ls-remote origin codex/publish-20260717-clean-branch returns empty."
  },
  "hard_invariants": [
    "research branch is never pushed directly.",
    "No object exceeding 50 MB enters the push range.",
    "groundtruth.db is never overlaid onto the clean branch.",
    "No remote branch is force-pushed.",
    "No local commit history, staged files, or database state is mutated by this operation.",
    "No dispatcher, TAFE, harness registry, or deployment state is changed."
  ],
  "fail_closed_conditions": [
    "Independent GO verdict is absent.",
    "Blob-size verification finds any object above 50 MB in the push range.",
    "The PAUTH registration transaction fails.",
    "The clean branch already exists at origin (name collision).",
    "The overlay produces merge conflicts or missing content relative to 42a252ab."
  ],
  "essential_context_preservation": "Complete local research history, all bridge threads, harness-state, and groundtruth.db binary carrier remain in the local worktree. Only the file content delta reaches the remote."
}
```

## PAUTH Registration Step

Before any git operation, register the bounded PAUTH via the governed CLI:

```
python scripts/project_authorization.py register \
  --pauth-id PAUTH-PROJECT-GTKB-TREE-STABILIZATION-RESEARCH-PUBLISH-20260717 \
  --project-id PROJECT-GTKB-TREE-STABILIZATION-WORKTREE-FINALIZATION \
  --work-item-id WI-5403 \
  --allowed-mutation-classes '["git_push", "database_write", "bridge", "governance_evidence"]' \
  --forbidden-operations '["credential_lifecycle","destructive_cleanup","git_history_rewrite","git_push_force","production_deployment","release","dispatcher_mutation","external_system_mutation","raw_database_mutation","committing_unrelated_dirty_files","staging_groundtruth_db"]' \
  --scope-summary "Bounded authorization for WI-5403: one-time clean-branch publication overlaying 42a252ab committed content onto a branch from origin/develop, blob-size verification, and push. Excludes groundtruth.db, force-push, and all mutation classes not listed."
```

This PAUTH registration is itself a `database_write` mutation; it is the first
step of the implementation and must be recorded in the implementation-start
packet before any git operation begins.

## Implementation Steps (post-GO)

1. Register PAUTH as above.
2. Run `python scripts/implementation_authorization.py begin --bridge-document gtkb-research-clean-branch-publication --work-item WI-5403` to emit the implementation-start packet.
3. Fetch remote state: `git fetch origin`.
4. Create clean branch: `git checkout -b codex/publish-20260717-clean-branch origin/develop`.
5. Identify committed paths at 42a252ab that are not `groundtruth.db` and not binary blobs >50 MB:
   ```powershell
   git diff --name-only origin/develop..42a252ab | Where-Object { $_ -ne 'groundtruth.db' }
   ```
6. Overlay committed content: `git checkout 42a252ab -- <each path>`.
7. Verify: `git diff --name-only HEAD` matches the overlay set.
8. Commit: `git commit -m "chore(publish): WI-5403 clean-branch overlay from research@42a252ab (no blobs >50 MB)"`.
9. Blob-size gate — must pass before any push:
   ```powershell
   git rev-list origin/develop..HEAD | ForEach-Object {
     git cat-file -s $_
   } | Where-Object { $_ -gt 52428800 }
   # Must produce zero lines
   ```
10. If gate passes: `git push origin codex/publish-20260717-clean-branch`.
11. Return to `research` branch: `git checkout research`.
12. File implementation report.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `git rev-list origin/develop..codex/publish-20260717-clean-branch \| xargs git cat-file -s \| sort -rn \| head -5` | All sizes ≤ 52,428,800 bytes; groundtruth.db absent from diff |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` | `git diff --name-only origin/develop..codex/publish-20260717-clean-branch \| grep groundtruth.db` | Returns empty — groundtruth.db not in push range |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | `git log --oneline origin/develop..codex/publish-20260717-clean-branch` | Exactly one commit; message references WI-5403 and this bridge thread |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | `python scripts/implementation_authorization.py check --bridge-document gtkb-research-clean-branch-publication` | Active claim with matching work-intent before any push |
| PAUTH registration | `python scripts/project_authorization.py get --pauth-id PAUTH-PROJECT-GTKB-TREE-STABILIZATION-RESEARCH-PUBLISH-20260717` | Status = active; allowed_mutation_classes includes git_push |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short -k "test_preflight"` | Bridge applicability suite passes; confirms bridge artifact and project-linkage compliance for this thread |

## Risk / Rollback

Primary risk: overlay accidentally includes a file whose blob exceeds 50 MB
(e.g., a cached binary). The blob-size gate (step 9) is mandatory and
unconditional; if it fails, the push does not occur, the clean branch is
deleted locally, and a revised proposal is filed.

Secondary risk: name collision at origin. Resolved by checking
`git ls-remote origin codex/publish-20260717-clean-branch` before creating
the local branch; if it exists, the implementation halts and a revised name is
proposed.

Rollback is trivially reversible: `git push origin --delete codex/publish-20260717-clean-branch`. No local state changes.

## Bridge Filing

This proposal is filed as the first status-bearing numbered file for thread
`gtkb-research-clean-branch-publication`; no prior version exists.
Dispatcher/TAFE state plus the numbered file chain are the live workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore(publish)` — this is a one-time publication/sync operation, not a feature
or fix.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
