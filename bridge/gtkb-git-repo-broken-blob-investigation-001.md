NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-broken-blob-investigation
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Git Repo Broken-Blob Investigation: diagnose missing blob 01448913 referenced by tree aec44289

bridge_kind: implementation_proposal
Document: gtkb-git-repo-broken-blob-investigation
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-27 UTC
Implements: WI-3394 (Investigate and repair local git repo broken-blob)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3394
target_paths: [".gtkb-state/repo-integrity/broken-blob-investigation/"]
Recommended commit type: chore:

## Summary

This proposal scopes a read-only investigation slice for the broken-blob defect surfaced incidentally during WI-3392's inventory-regen commit on 2026-05-27. `git fsck --no-dangling` confirms a broken link from tree `aec442890b8085c24f6d663e228521d21a3ec56e` to missing blob `01448913b70ba97f8e16fe4e10a3359d4aaec637`. The blob is not present locally, and `git fetch origin --quiet` (which succeeded for fetch) did not retrieve the missing blob from upstream — its post-fetch auto-gc/repack fails on the same blob.

The investigation slice does NOT execute any repair operation. It produces a structured diagnostic report identifying:

1. Which commit(s) and tree path reference the missing blob (via `git log --all` + tree walks).
2. Whether the broken tree is reachable from any branch, tag, or stash (orphan diagnosis).
3. Whether the missing blob exists on upstream origin (`Remaker-Digital/groundtruth-kb`) via a remote object query.
4. Whether the broken link affects normal git operations (commit, push, fetch already known to succeed; clone/repack/gc affected).
5. Recommended repair approach with risk/blast-radius analysis.

Repair execution is intentionally out of scope for this slice. After investigation completes, a follow-on proposal (a SLICE-2 thread under WI-3394, or a new WI-3396 if scope expands) will propose the specific repair operation and request owner approval through the standard bridge protocol.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - investigation evidence is written to in-root `.gtkb-state/repo-integrity/broken-blob-investigation/`; no out-of-root paths touched.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites the governing specification surfaces and concrete target paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each governing surface to an executed verification step.
- GOV-STANDING-BACKLOG-001 - WI-3394 was captured via the gate-clean backlog-add CLI and is an active member of PROJECT-GTKB-RELIABILITY-FIXES.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - investigation produces a durable diagnostic artifact under change control, not transient session output.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability preserved between WI-3394, this thread, the diagnostic report, and the post-impl record.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3394 advances from `backlogged` to lifecycle-tracked investigation scope.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification is needed for a read-only diagnostic investigation; existing GOV-FILE-BRIDGE-AUTHORITY-001 governance plus the standing reliability project authorization cover the scope.

## KB Mutation Scope

This proposal performs no MemBase mutation. The implementation does not write to groundtruth.db. The investigation uses git plumbing commands (read-only) and writes evidence only to the runtime tree at `.gtkb-state/repo-integrity/broken-blob-investigation/`. WI-3394's lifecycle transition will happen downstream via lifecycle-automation hooks consuming bridge VERIFIED status. `groundtruth.db` is therefore intentionally excluded from target_paths.

## WI Citation Disclosure

The proposal declares implementation work for WI-3394 only. References to WI-3392 in the Summary and Prior Deliberations sections are originating-context citations: WI-3392 (inventory-regen chore commit) was the work whose post-implementation Anomalies Observed section surfaced this broken-blob defect; WI-3392 itself is not being implemented or modified by this proposal. The reference to a hypothetical WI-3396 in the Summary refers to a possible future scope-expansion proposal not yet captured in MemBase. Neither citation broadens the implementation scope of this proposal; `Work Item: WI-3394` in the header is the sole implementation target.

## Prior Deliberations

- bridge/gtkb-inventory-regen-chore-commit-2026-05-27-003.md (NEW, this session): WI-3392 post-impl report Anomalies Observed section surfaced the broken-blob defect during the inventory-regen commit. The repo-integrity issue was incidental to that work and out of scope for the chore commit; this proposal formally tracks it.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: Establishes that small reliability/defect investigations route through PROJECT-GTKB-RELIABILITY-FIXES via PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE: Diagnostic outputs from this investigation will be deterministic git-plumbing reports, suitable for codifying as a reusable diagnostic if the broken-blob pattern recurs.

## Owner Decisions / Input

This proposal depends on the following owner decision:

- Owner direction 2026-05-27 (this session): "Please proceed: ... and/or file a separate proposal for the broken-blob repair" authorized the investigation-scoping proposal in direct response to my status summary surfacing the WI-3392 anomaly.

The proposal intentionally defers the repair operation to a follow-on proposal. No additional owner decision is required at this scoping stage. The post-implementation report will surface the recommended repair shape and request owner approval for SLICE 2 (repair) at that time.

## Implementation Plan

1. Identify the broken tree's location in repo history:
   - `git rev-list --all --objects | grep "^aec442890b"` to find which commits reference the broken tree.
   - For each referencing commit, `git ls-tree -r <commit>` to identify the file path the broken tree corresponds to (likely a directory listing).
   - Record findings as `.gtkb-state/repo-integrity/broken-blob-investigation/<UTC-timestamp>/tree-references.json`.
2. Identify the broken blob's likely content:
   - For each referencing commit, identify which child blob entries the broken tree contains via `git ls-tree <tree-sha>`.
   - Note: this may fail for the missing blob entry itself; the entry name (file path) should still be readable.
   - Record findings as `tree-contents.json`.
3. Check for the broken blob in upstream and stashes:
   - `git fetch origin --tags --quiet` to ensure full origin reachability (already attempted; expect post-fetch gc warning).
   - `git stash list` to enumerate stashes.
   - `for stash in $(git stash list --format=%H); do git cat-file -e 01448913... && echo "FOUND IN STASH $stash"; done`.
   - `git fsck --unreachable --lost-found --no-dangling` to surface unreachable objects.
   - Record findings as `recovery-search.json`.
4. Assess impact on normal operations:
   - `git status` (read-only) — confirm reports clean.
   - `git commit --dry-run` (read-only) — confirm would succeed.
   - `git fetch origin --dry-run` — confirm dry-fetch path.
   - `git gc --dry-run` (if available) or document `git gc` known-failure observation.
   - Record findings as `operations-impact.json`.
5. Synthesize recommended repair approach:
   - Option A: Fresh clone from origin to a sibling directory; rsync `.git/objects/` to recover the missing blob if present in the fresh clone.
   - Option B: `git fsck --lost-found` recovery of orphan objects (if the broken-blob's parent commit is reachable).
   - Option C: Accept the broken link as benign if it's only in unreachable history (e.g., from a dropped branch or rebased-away commit) and configure `git gc --prune=never` to suppress repack errors.
   - Option D: Re-create the broken tree from scratch via a synthetic commit if the blob content can be reconstructed.
   - Record the synthesis as `recommended-repair.md` with risk/blast-radius analysis and the recommended option.

The investigation uses only read-only git plumbing; no git history is rewritten, no objects are deleted, no branches/tags are moved, no commits are created. Investigation evidence lives entirely in `.gtkb-state/repo-integrity/broken-blob-investigation/` which is excluded from regression-gate canonical state.

## Spec-to-Test Mapping

| Specification | Verification Command | Expected Result |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal filed at `bridge/gtkb-git-repo-broken-blob-investigation-001.md`; INDEX entry created. | PASS - bridge protocol observed. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Investigation evidence directory is `.gtkb-state/repo-integrity/broken-blob-investigation/` — under `E:\GT-KB`. | PASS - all in-root. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation` will be run prior to Codex review. | PENDING (preflight scheduled). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This table itself records the spec-to-test mapping; post-implementation report will record observed results. | PASS - mapping present. |
| GOV-STANDING-BACKLOG-001 | `python -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES` lists WI-3394 as an active member (canonical project-id, post-repair of the doubled-prefix CLI bug). | PASS - membership confirmed at filing. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Investigation diagnostic + bridge audit trail preserve durable traceability between WI-3394, this thread, and the diagnostic outputs. | PASS - traceability preserved. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `.gtkb-state/repo-integrity/broken-blob-investigation/<UTC-timestamp>/` exists and contains the five JSON/MD evidence files.
- [ ] `tree-references.json` identifies at least one commit referencing tree `aec44289...`, OR reports "tree unreachable from any branch/tag" with supporting evidence.
- [ ] `recovery-search.json` confirms whether blob `01448913...` was recovered from any source (origin, stash, lost-found).
- [ ] `operations-impact.json` confirms which normal git operations are affected by the broken link.
- [ ] `recommended-repair.md` provides a specific repair option with risk analysis.
- [ ] No git history rewrite, branch/tag movement, object deletion, or commit creation is performed during the investigation.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before SLICE 2 (repair) is proposed.

## Risk and Rollback

Risk is very low. The investigation is read-only by design; all git plumbing commands used are non-mutating (`git rev-list`, `git ls-tree`, `git cat-file -e`, `git fsck --no-dangling`, `git fetch --dry-run`, `git stash list`).

Risks identified:
- The git auto-gc post-fetch may continue to emit warnings during routine fetches until repair lands; these are surface noise, not new defects (already observed during WI-3392).
- The investigation may fail to identify the broken tree's parent commit if it's truly unreachable from any branch/tag/stash; in that case, the recommended-repair.md will document Option C (accept benign with gc tuning) as the lowest-risk path.

Rollback: not applicable. No state changes to roll back.

## Verification Limitations Anticipated

The investigation may produce inconclusive findings if:
- The missing blob is referenced from a truly unreachable tree (e.g., a force-pushed-over branch or expired stash). In this case the diagnosis is "orphan corruption, benign", and Option C is the recommended repair.
- The git plumbing commands return ambiguous output. The post-implementation report will record the ambiguity and recommend an extended-scope SLICE 1.5 if needed.

## Files Touched (target_paths recap)

- `.gtkb-state/repo-integrity/broken-blob-investigation/` (new diagnostic evidence tree; specific timestamped subdirectory created during implementation)

Plus bridge filing artifacts (workflow infrastructure, not implementation scope):
- `bridge/gtkb-git-repo-broken-blob-investigation-001.md` (this file)
- `bridge/INDEX.md` (entry update)
- `bridge/gtkb-git-repo-broken-blob-investigation-NNN.md` (post-impl report)

## Loyal Opposition Asks

1. Verify the read-only investigation scoping is appropriate, or NO-GO with guidance on whether to scope repair into the same slice.
2. Confirm that target_paths covering only `.gtkb-state/repo-integrity/broken-blob-investigation/` (the evidence tree) is sufficient given the implementation uses only read-only git plumbing commands.
3. Flag any concerns about the deferred SLICE 2 (repair) being filed as a separate follow-on bridge rather than folded into this one.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
