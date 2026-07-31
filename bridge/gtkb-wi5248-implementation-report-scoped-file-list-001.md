NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Scope Implementation-Report Evidence to Approved Targets

bridge_kind: prime_proposal
Document: gtkb-wi5248-implementation-report-scoped-file-list
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5248

target_paths: [".claude/skills/bridge/helpers/impl_report_bridge.py", ".codex/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "platform_tests/skills/test_bridge_impl_report_helper.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the implementation-report helper so a dirty parallel worktree cannot
pollute `## Files Changed`, diff-stat evidence, or commit-type guidance beyond
the approved proposal `target_paths`. WI-5248 records repeated substantive
failures: 382 unrelated paths during WI-5229, 295 during WI-5361, and 41 during
the WI-5370 repair report. Each recurrence required manual exact-scope
replacement before governed filing.

The implementation will parse `target_paths` as structured inline JSON,
discover staged, unstaged, and untracked paths once, retain only changed paths
inside the approved scope, and disclose only the count of excluded out-of-scope
dirty paths. It will neither name nor adopt concurrent owners' changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - keeps the report tied to the approved numbered proposal and its exact target boundary.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite every governing requirement used by implementation and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds the proposal to the active project PAUTH, WI-5248, and parseable target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires execution of the linked TEST-11402 regression before independent VERIFIED.
- `GOV-STANDING-BACKLOG-001` - WI-5248 is the durable MemBase backlog authority for this defect.
- `GOV-WORK-TREE-HYGIENE-001` - prohibits adopting or misreporting unrelated dirty worktree paths.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - preserves command-scoped author metadata in generated and filed implementation reports.
- `ADR-CROSS-HARNESS-PARITY-001` - requires canonical, generated Codex, and managed-template helper behavior to remain equivalent.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires the explicit cross-harness disposition below because managed harness skill surfaces are targets.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform helper and its tests outside adopter application roots.

## Prior Deliberations

- `DELIB-20263739` - established governed no-index bridge helper filing; this proposal preserves that publication path and changes only report evidence discovery.
- `DELIB-20264100` - established project-root resolution for bridge governance helpers; target-path normalization remains rooted at the exact GT-KB repository.
- `DELIB-202666063` - verified no-window subprocess behavior for bridge helpers; this proposal retains the existing `no_window_subprocess_kwargs()` subprocess boundary.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE` is active and covers source, test, configuration, documentation, metadata, runtime-state, bridge, and governance-evidence work for this project.
- The PAUTH imposes no per-work-item inclusion restriction and covers WI-5248.
- The PAUTH forbids dispatcher mutation, external-system mutation, credential lifecycle, destructive cleanup, Git commit/history/push, deployment, and release. Those operations are outside this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5248 and linked `TEST-11402` define
the observable regression, while the specifications above define exact bridge
scope, worktree isolation, author provenance, cross-harness parity, and
independent verification. No new formal requirement is needed before
implementation.

## Proposed Scope

- Parse the approved proposal's inline-JSON `target_paths` with `json.loads`; reject missing, malformed, non-list, or non-string path data instead of guessing scope from prose.
- Normalize approved paths to repository-relative POSIX form and reject paths that escape the exact project root.
- Use structured Git status data to identify staged, unstaged, and untracked paths, then retain only changed paths inside approved files or approved directory scopes.
- Generate `files_changed`, diff-stat evidence, and commit-type recommendation from the same approved changed-path set.
- Emit a count-only note for excluded out-of-scope dirty paths without exposing their names in the plan or scaffold.
- Regenerate the Codex helper projection and keep the managed template synchronized with the canonical Claude helper.
- Add focused TEST-11402 coverage for mixed staged, unstaged, untracked, and unrelated dirty paths.

## Out Of Scope

- Dispatcher or TAFE configuration, eligibility, selection, leases, workers, provider invocation, or bridge queue mutation beyond normal proposal/report publication.
- `groundtruth.db`, credentials, Git index/history, commit, push, deployment, release, or destructive cleanup.
- Any adoption, deletion, reformatting, staging, or disclosure of unrelated worktree changes.

## Cross-Harness Disposition

No typed waiver is requested.

- **Claude Code B:** `.claude/skills/bridge/helpers/impl_report_bridge.py` remains the canonical helper and gains approved-target-scoped evidence discovery.
- **Codex A:** `.codex/skills/bridge/helpers/impl_report_bridge.py` is regenerated from the canonical helper and must remain byte/semantic parity; Codex retains the governed non-bypass filing path.
- **Antigravity C, Cursor E, Ollama D, OpenRouter F, and Alibaba H:** no role, hook, eligibility, model, cap, lifetime, routing, or provider behavior changes. Any use of the shared implementation-report helper receives the same approved-target-scoped behavior.
- **Managed templates:** `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` must project the same behavior into future installations without introducing a harness-specific fork.

## Spec-Derived Verification Plan

| Spec / artifact | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run `platform_tests/skills/test_bridge_impl_report_helper.py`; a GO proposal with two targets must report only changed approved targets. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and filed applicability preflights must report `preflight_passed: true` with no missing required specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal metadata and implementation-start preflight must bind the active PAUTH, project, WI-5248, and exact four target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / `TEST-11402` | Execute the focused helper suite after implementation; independent LO must cite the dirty-worktree regression result before VERIFIED. |
| `GOV-STANDING-BACKLOG-001` | Read back WI-5248 and TEST-11402 linkage from MemBase before filing the implementation report. |
| `GOV-WORK-TREE-HYGIENE-001` | Regression fixtures must prove unrelated staged, unstaged, and untracked paths are neither listed nor named; only an excluded count is emitted. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Existing report-author provenance tests must remain green with command-scoped A metadata. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Regenerate Codex adapters and run the repository's managed-skill adapter parity check. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm every changed path remains under `E:\GT-KB` and outside `applications/`. |

## Acceptance Criteria

- With two approved targets and hundreds of unrelated dirty paths, plan and scaffold outputs list only changed approved targets.
- Approved staged, unstaged, and untracked paths are recognized; unrelated paths in each state are excluded.
- A malformed or absent `target_paths` declaration fails closed and cannot fall back to whole-worktree reporting.
- Output records the excluded out-of-scope dirty-path count without disclosing excluded names.
- Diff stat and recommended commit type are derived from exactly the same approved changed-path set.
- Canonical Claude, generated Codex, and managed-template helpers remain in parity.
- Focused TEST-11402, provenance regressions, Ruff checks, and adapter-parity checks pass.
- Independent LO verification is required before any focused finalization.

## Risk / Rollback

The main risk is under-reporting a legitimately changed approved path because
Git status parsing or path-scope matching is too narrow. Mixed-state tests and
file/directory-scope cases mitigate that risk. Fail-closed target parsing avoids
the more dangerous fallback to whole-worktree evidence.

Rollback is a focused revert of the helper and test implementation after the
separate finalization authorization. Numbered bridge artifacts remain
append-only. Rollback must not alter unrelated worktree paths.

## Bridge Filing

This proposal is filed as
`bridge/gtkb-wi5248-implementation-report-scoped-file-list-001.md` through the
governed Codex non-bypass writer. No existing numbered bridge version is
rewritten, and no aggregate queue artifact is created.

## Recommended Commit Type

`fix` - correct misleading implementation-report evidence in dirty parallel worktrees.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
