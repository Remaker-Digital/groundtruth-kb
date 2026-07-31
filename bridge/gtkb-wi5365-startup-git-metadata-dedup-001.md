NEW

# Deduplicate in-worktree Git metadata during fast startup

bridge_kind: prime_proposal
Document: gtkb-wi5365-startup-git-metadata-dedup
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5365

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_git_metadata.py"]

implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Bring the fast startup-service path back under the repository's 30-second test
budget by reusing one Git metadata snapshot per actual worktree. The focused
Cursor regression passes only with a raised timeout and takes 42.96 seconds.
A cProfile run reports 44.95 seconds total, with about 35.90 seconds in eleven
Git subprocesses. `_git_drift(E:\GT-KB)` populates metadata for the root, but
`_gtkb_upgrade_posture` then treats the in-tree package path
`E:\GT-KB\groundtruth-kb` as a separate checkout and repeats branch, SHA,
remote, status, and related calls against the same repository. The nested
status call reaches its 10-second limit.

Resolve the nearest `.git` worktree boundary for an in-root checkout without a
subprocess, then use `_git_metadata` for that canonical root. Preserve nested
repositories by selecting their nearer `.git` marker, preserve the existing
outside-root no-subprocess rejection, and preserve every startup payload field.
Do not skip dirty-state collection, relax the 30-second budget, suppress a
test, or cache across process lifetimes.

## Specification Links

- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - startup must avoid serial duplicate work and stay within its bounded lifecycle budget.
- `GOV-SESSION-SELF-INITIALIZATION-001` - every startup still produces a fresh, complete, non-degraded payload.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - startup must complete rather than fall into a degraded timeout path.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - optimization must preserve Git drift, upgrade posture, nested-repository, and root-boundary semantics.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the frozen RC activity and repository timeout remain executable gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test implementation requires independent GO, matching claim/start authority, reporting, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - startup performance and correctness carriers are explicitly linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Assurance PAUTH, project, WI-5365, and exact targets are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must execute command-count, boundary, and real startup tests.
- `GOV-STANDING-BACKLOG-001` - WI-5365 remains the durable owner until verified and finalized.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and evidence remain under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the profile, work item, proposal, tests, report, and verdict remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5365 remains active through implementation, verification, and exact finalization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the measured release blocker is preserved as governed work rather than an ad hoc timeout increase.

## Prior Deliberations

- `DELIB-202666274` - project-level modernization authority while retaining bridge, verification, and mechanical Git gates.
- WI-5365 - records the exact 42.96-second failure and 35.90-second Git-subprocess profile.
- WI-5328 - owns foreign current hunks in the existing monolithic startup test module; this proposal uses a new focused module to preserve finalization separability.

## Owner Decisions / Input

No new owner decision is required. The active Assurance project PAUTH covers
source/test implementation. Git staging/commit/push, release, deployment,
dispatcher/TAFE/harness mutation, credential lifecycle, process termination,
and destructive cleanup remain excluded.

## Requirement Sufficiency

Existing startup budget and nonimpairment requirements are sufficient. The
defect is duplicate implementation work, not a missing product decision. The
correct result is one fresh metadata collection per physical worktree, not a
larger timeout.

## Proposed Scope

1. Add a private helper that walks from a resolved in-root checkout path toward the resolved project root and returns the nearest ancestor whose `.git` entry is a file or directory.
2. In `_git_checkout_info`, retain the existing outside-root rejection before any Git operation.
3. For an in-root checkout, call `_git_metadata` using the nearest worktree root; fall back to the requested path only when no in-boundary `.git` marker exists.
4. Derive branch, SHA, short SHA, remote, and dirty count from that one cached metadata mapping while preserving the current return shape and degraded error behavior.
5. Add a new focused test module that proves root/subdirectory deduplication, nested-repository separation, outside-root no-spawn behavior, error-shape preservation, and one status call per physical worktree.
6. Do not edit the foreign-hunk-bearing monolithic startup test module, alter payload fields, skip status, make network calls, or touch any third path.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"2026-07-16 cProfile plus focused startup regression","canonical_authority":"DCL-SESSION-STARTUP-TOKEN-BUDGET-001","primary_route":"canonical in-root worktree root plus existing per-process Git metadata cache","before_behavior":"The same physical worktree is scanned from root and package subdirectory; startup takes 42.96 seconds.","after_behavior":"One complete metadata snapshot serves both consumers; payload semantics are unchanged and startup returns under 30 seconds.","self_descriptive_naming":"Helper names the in-root Git worktree boundary it resolves.","obsolete_guidance_disposition":"No timeout or reduced-evidence guidance is introduced.","history_preservation":"Foreign WI-5328 test hunks remain untouched in their existing module.","baseline":{"focused":"passes only at raised timeout in 42.96 seconds","profile":"44.95 seconds total; 35.90 seconds in Git subprocess calls"},"expected_result":{"focused":"passes under repository default 30-second timeout","unit":"one status call per physical worktree"},"rollback":{"instructions":"revert only the WI-5365 source helper/call-site and new focused test module through a governed change","verification":"rerun focused command-count and startup tests"},"hard_invariants":["complete Git drift evidence","fresh startup payload","nested repositories remain distinct","outside-root path spawns no Git","no cross-process cache"],"fail_closed_conditions":["status skipped","timeout merely increased","nested repository conflated","outside-root Git spawned","foreign test hunks altered"],"essential_context_preservation":"Retain root boundary, metadata return shape, degraded errors, no-window subprocess kwargs, and fresh-process behavior."}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Worktree deduplication | Run the new WI-5365 focused test module | Root then package-subdirectory reads produce one metadata command set and exactly one status call. |
| Nested repository correctness | Focused synthetic nested `.git` test | Parent and nested checkouts use distinct cache entries and metadata calls. |
| Root boundary | Focused outside-root test with a fail-on-command stub | The existing `checkout_outside_project_root` result returns and zero Git calls occur. |
| Real startup budget | Run the existing Cursor harness startup regression under the repository default pytest timeout | Passes without timeout, returns valid SessionStart JSON, and contains no degraded banner. |
| Payload nonimpairment | Run the existing fast-hook startup tests and inspect upgrade-posture/drift fields | Existing fields and values remain present; only duplicate commands disappear. |
| Scope | Run diff and diff-check against exactly the two declared target paths | Only the helper/call-site and new focused regression module exist; diff check exits zero. |

## Acceptance Criteria

1. The real focused startup regression passes under the default 30-second budget.
2. One physical worktree causes one complete Git metadata/status collection per process.
3. A nested repository remains a distinct checkout and cache entry.
4. Outside-root paths still spawn no Git subprocess.
5. No payload field, dirty-state evidence, network posture, dispatcher state, harness state, or Git operation is weakened.
6. Independent VERIFIED precedes exact mechanical finalization.

## Risk / Rollback

The main risk is conflating a nested repository with its parent. Nearest `.git`
marker selection and focused nested-repository coverage prevent that. The cache
remains process-local and complete. Rollback is the exact two-target WI-5365
hunk through a new governed change; no broad reset or timeout increase is
permitted.

## Bridge Filing

File as the next numbered append-only bridge file through the governed Codex
non-bypass helper. No prior version is deleted or rewritten. Deterministic
TAFE/bridge routing remains external to this authoring task; no manual routing
or direct harness contact occurs.

## Recommended Commit Type

`perf` - removes duplicate startup Git work while preserving all evidence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
