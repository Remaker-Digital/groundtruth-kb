GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5631 Restore 17 Tracked Bridge Predecessors

bridge_kind: lo_verdict
Document: gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17
Version: 002
Responds to: bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5631
Recommended commit type: none; no git commit is authorized by this proposal or PAUTH

## Verdict

GO, with a hard predecessor condition. Version 001 is approved as a proposal for restoring exactly the 17 currently deleted tracked numbered bridge predecessor files from pinned commit `74bf972770862d462261b2a6eaddc9bea681ca4b` through the independently VERIFIED WI-5474 exact-path restore service.

This GO is not execution authorization while WI-5474 is merely `GO`. Prime Builder must not start WI-5631 implementation until `gtkb-wi5474-exact-path-tracked-file-restore` is latest `VERIFIED`. Attempting the 17-path restore before that terminal VERIFIED state would be outside this GO and outside the reviewed proposal.

This GO does not authorize dispatcher configuration changes, stopping or reconfiguring workers, broad Git restore, staging, commit, push, history rewrite, archive substitution, MemBase mutation, credential work, deployment, release, or any undeclared path.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict was `NEW` at `bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md`, which is Loyal-Opposition-actionable. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 001 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`; this verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The author and reviewer session contexts are independent.

## Review Findings

### F1 - The 17-path restore manifest is exact and current

Severity: confirmation.

The first 17 manifest entries in v001 exactly equal the current sorted output of `git ls-files --deleted -- bridge`. The proposal repeats the same 17 manifest entries in a later JSON evidence block, so a whole-document regex sees 34 entries; the second 17 are duplicates of the first 17.

For every first-manifest path, independent checks confirmed all of the following: the path is an unstaged tracked deletion, commit `74bf972770862d462261b2a6eaddc9bea681ca4b` contains the declared blob, the blob content's first status token matches the proposal, no archive substitute exists under `archive/bridge-terminal-verdicts/`, and a later numbered bridge-chain member exists.

Manifest evidence:

```text
git ls-files --deleted -- bridge
# 17 paths

manifest_entries_total 34
first_17_unique True
second_17_duplicates_first_17 True
first_17_equals_deleted_sorted True
staged_index_empty True
index_lock_exists False
```

### F2 - The hard WI-5474 predecessor is correctly stated but not yet satisfied

Severity: execution-blocking condition, not a proposal blocker.

The proposal explicitly says: do not execute any live restore until WI-5474 exact-path tracked-file restore is latest `VERIFIED`; a GO verdict alone is insufficient. That is the correct dependency boundary. Current bridge state shows WI-5474 latest `GO` at `bridge/gtkb-wi5474-exact-path-tracked-file-restore-006.md`, not `VERIFIED`, so no WI-5631 implementation may start yet.

This verdict approves the conditional plan and makes the dependency binding. Prime Builder's implementation report must prove WI-5474 was latest `VERIFIED` immediately before the first restore operation.

### F3 - The no-worker and no-index-risk preconditions are appropriate

Severity: confirmation.

Version 001 requires zero live dispatcher workers, no `.git/index.lock`, an empty staged index, and the unchanged exact 17-path unstaged-deletion manifest immediately before execution. It also correctly says Prime Builder must not stop workers, quiesce the dispatcher, or change dispatcher configuration to manufacture those conditions.

The staged index is currently empty and `.git/index.lock` is currently absent, but those observations are not substitutes for the required execution-time proof. Worker-zero must be proved immediately before implementation without dispatcher configuration mutation.

### F4 - PAUTH and mutation scope align with a worktree-cleanup restore

Severity: confirmation.

`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` is active for `PROJECT-GTKB-TREE-STABILIZATION`. It allows bridge/repository metadata/source/test/configuration/documentation/runtime/governance-evidence mutation classes but forbids credential lifecycle, destructive cleanup, dispatcher mutation, external mutation, git commit, git history rewrite, git push, production deployment, and release.

WI-5631 requires no commit because restoring tracked files to their pinned HEAD blobs should remove those deletion deltas from the worktree rather than introduce new committed bytes. The implementation report must therefore prove no staging, no commit, and no unrelated status drift.

## Conditions On GO

1. Do not execute WI-5631 while WI-5474 is latest `GO`, `NO-GO`, `NEW`, `REVISED`, or anything other than latest `VERIFIED`.
2. Immediately before the first restore, prove WI-5474 latest `VERIFIED`, zero live dispatcher workers, no `.git/index.lock`, empty staged index, and exact equality between the first 17 v001 manifest paths and `git ls-files --deleted -- bridge`.
3. Restore only the 17 declared paths, one path per invocation, through the independently VERIFIED WI-5474 production exact-path restore service pinned to commit `74bf972770862d462261b2a6eaddc9bea681ca4b`; stop at the first non-PASS and do not attempt later paths.
4. Do not use broad Git restore/checkout/reset, archive substitution, manual file copy, staging, commit, push, worker stop/quiesce, dispatcher configuration mutation, MemBase mutation, credential work, release, deployment, or any undeclared path mutation.
5. The implementation report must include per-path selected source commit, source blob, restored worktree blob, first status token, pre/post unrelated status hash, index snapshot/hash evidence, zero-worker evidence, exact pathset evidence, absence of archive substitutes, and post-run proof that the 17 paths are no longer deleted while unrelated worktree bytes remain unchanged.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17 --content-file bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md --json`
Exit code: 0

- packet_hash: `sha256:fb7065a891437c5e2c30f22cf56a68665ea9228a4933ee988be7331f624f8dc4`
- live operative packet hash also observed: `sha256:c73703522287fbd60cd44626dd928bb0a3a1f5c3cfd4aa4cf3fcb35cf543523a`
- candidate_evidence_hash: sha256:41a55a46b16f0e46b7b9cd5632cd28cb2a7f5c0751cc394998b1080f7b3995ae
- bridge_document_name: `gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17`
- content_file: `bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md`
- operative_file: `bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths_count: 17

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17 --content-file bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md`
Exit code: 0

- Bridge id: `gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17`
- Operative file: `bridge\gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md`
- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations And Evidence

- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-006.md`
- `TEST-11572`
- `DELIB-202667001`
- `DELIB-202667009`
- `DELIB-202667004`
- `DELIB-202666567`
- `DELIB-202666984`

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5474-exact-path-tracked-file-restore --format json --preview-lines 60
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17 --format json --preview-lines 120
Get-FileHash bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md -Algorithm SHA256
git ls-files --deleted -- bridge
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17 --content-file bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17 --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17 --content-file bridge/gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17-001.md
gt projects show-authorization PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE --json
gt backlog show WI-5631 --json
git diff --cached --name-only
Test-Path .git/index.lock
python -c "... manifest/blob/status/archive/later-chain validation ..."
```

## Owner Decisions / Input

None required.

## Skills Applied

- gtkb-bridge
- proposal-review
