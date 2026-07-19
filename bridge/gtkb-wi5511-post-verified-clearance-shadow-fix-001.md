NEW
::init gtkb lo
::open build

# gtkb-wi5511-post-verified-clearance-shadow-fix — Restore reachability of the WI-4837 post-VERIFIED git-add finalization clearance

bridge_kind: prime_proposal
Document: gtkb-wi5511-post-verified-clearance-shadow-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-18 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 20dd407b-d159-4c05-9700-63511dadff11
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5511

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

During Loyal Opposition review follow-up on WI-5412 (`bridge/gtkb-wi5412-gap-state-capture-source-residue`, commit `64bcd521`), the reporter's proposed manual recovery for a stale post-VERIFIED git index (`git add -- <paths>`) was found to be mechanically blocked by the `GTKB-GIT-LIFECYCLE` PreToolUse check (`_direct_git_effect_from_payload`) in `scripts/implementation_start_gate.py`.

Root-cause investigation traced this to a shadowing regression. WI-4837 (commit `92c54ff4`, 2026-07-08) landed a narrow, security-reviewed, 14-version-bridge-thread-approved clearance (`_post_verified_finalization_clearance` / `_finalization_git_add_targets`) for exactly this scenario: a single-stage `git add` of explicit paths, all within a terminal-VERIFIED thread's own approved `target_paths`, gated on an active work-intent claim. Six days later, WI-5138 (commit `7ae6f769`, 2026-07-14, a ~3,000-line rewrite of the same file) added the `_direct_git_effect_from_payload` check earlier in `gate_decision()`. That check blocks any non-read-only git subcommand — including `add` — unconditionally, before the function ever reaches the WI-4837 clearance branch. The clearance has been unreachable dead code since 2026-07-14.

Confirmed empirically: `git add` on the WI-5412 paths returns the `GTKB-GIT-LIFECYCLE` block message, never the WI-4837 clearance message. The block message's suggested alternative (`python -m groundtruth_kb.git_lifecycle`) does not cover this case either — that module is a branch-lifecycle abstraction (`create`/`attach`/`preserve`/`promote`/`close`/`resume`/`recover`/`drain`) with no raw path-staging primitive.

This proposal restores the WI-4837 clearance's reachability with the minimal change needed to preserve the `GTKB-GIT-LIFECYCLE` boundary for every other git subcommand, corrects the now-misleading block message, and adds an end-to-end regression test against the full `gate_decision()` function. The existing WI-4837 tests exercise the clearance function in isolation and did not catch this shadowing when WI-5138 landed — closing that gap is part of this proposal's scope, not an afterthought.

**Recommended minimal fix shape** (final diff is Prime's to compose after GO): in `gate_decision()`, when `_direct_git_effect_from_payload` returns `"add"` specifically, consult `_post_verified_finalization_clearance` before blocking, so the WI-4837 exemption is reachable again without weakening the gate for any other subcommand. Update the block message so it no longer points `add` callers at a module with no relevant primitive.

**Out of scope (noted, not addressed here):** `_emergency_bridge_repair_applies` and `_dispatcher_config_direct_edit_targets` in the same function appear structurally shadowed the same way for raw-git-invoked mutations. This is unverified and is flagged in WI-5511's own description for a future reviewer sweep; fixing it is not part of this proposal's bounded scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal repairs a corner of the bridge/implementation-authorization audit-trail discipline the gate enforces.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied by this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project Authorization` / `Project` / `Work Item` header lines present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the spec-to-test mapping in `## Spec-Derived Verification Plan` below.
- `GOV-STANDING-BACKLOG-001` — WI-5511 is tracked in the standing backlog. This proposal is a single narrow work item, not a bulk operation: the other WI-IDs it cites (WI-4837, WI-5412, WI-5138, WI-5501) appear only as evidentiary/historical cross-references, never as additional mutation targets. A standing-backlog review packet check was completed before filing (per this spec's Backlog Conflict & Future Work Review discipline): WI-5501 was identified as related-but-distinct and cross-referenced rather than duplicated or absorbed into this proposal's scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — names the exact gate function (`gate_decision` in `scripts/implementation_start_gate.py`) this proposal modifies; the fix must not weaken its fail-closed default for any subcommand other than the narrow WI-4837 `add` case.
- `GOV-WORK-TREE-HYGIENE-001` — governs the broader worktree-finalization problem family this and sibling WI-5501 both belong to.
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` — the original owner decision this proposal restores reachability of; carried forward, not re-litigated.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — this proposal preserves the WI-4837 decision, the WI-5511 work item, and the WI-5501 cross-reference as durable artifacts rather than letting the finding live only in chat.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability preserved across the WI-4837 bridge thread, the WI-5511 work item, and this proposal's citation of both.

## Prior Deliberations

- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` — the owner decision authorizing the exact clearance this proposal restores. This proposal does not reopen that decision; it repairs a later mechanical regression against it. See `bridge/gtkb-wi4837-post-verified-finalization-recovery-014.md` (VERIFIED, with an explicit "Security Review of the Clearance Branch" section) for the original narrow-scope specification this fix must preserve exactly.
- `WI-5501` (standing backlog, not a DELIB) — sibling, currently-owned-by-a-different-session work item covering the *forward* transaction robustness (making `finalize_verified_commit` tolerant of concurrent real-index writers), filed independently and discovered to cite the same WI-5412 commit (`64bcd521`) as evidence. Cross-referenced per the mandatory backlog-conflict check (`GOV-STANDING-BACKLOG-001` / `.claude/rules/loyal-opposition.md` "Backlog Conflict & Future Work Review"); not duplicated into this proposal. WI-5511 is the *recovery-path* half of the same problem family; WI-5501 is the *prevention* half. A corroborating note with cross-reference was added to WI-5501's `status_detail` rather than filing competing scope.
- Pruned from the helper-seeded candidates as not directly relevant to this specific shadowing regression: `INTAKE-eb7f7814`, `INTAKE-9314e628`, `INTAKE-8438b8c0` (general OPS/backlog-closure intake items, not about this gate) and `DELIB-WI4723-OWNER-PROCEED-20260621` (a different finalization-gate retry fix, tangential but not on point to the `_direct_git_effect_from_payload`/`_post_verified_finalization_clearance` interaction specifically).


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

Owner selected "File only the new finding" via `AskUserQuestion` when presented with three options: (a) file only this WI-4837 shadow-regression finding, (b) also pick up the sibling WI-5501 proposal despite an apparently-active concurrent Codex session, or (c) hold off on filing anything. The owner's selection confirms this proposal's scope is intentionally narrow — WI-4837 reachability only — and that WI-5501 remains with its existing owning session rather than being absorbed here.

Separately, this session's resolved role required an explicit `::init gtkb pb` from the owner (sent and confirmed via `.claude/session/active-session-role.json`, `source: init_keyword`) before this proposal could be authored under Prime Builder attribution; that owner action is the basis for the `author_identity`/`author_harness_id` values above.

No further owner approval is required for filing itself; ordinary bridge GO/NO-GO discipline governs implementation approval from this point.

## Requirement Sufficiency

Existing requirements sufficient. This is a repair of an existing, owner-approved requirement (`DELIB-WI4837-AUTOMATIC-PARITY-20260707`) that was mechanically regressed by a later, unrelated change (WI-5138). No new specification is needed; the fix restores previously-approved, previously-security-reviewed behavior rather than introducing new authorization surface.

## Spec-Derived Verification Plan

| Specification / Decision | Test / Verification | Expected Result |
|---|---|---|
| `DELIB-WI4837-AUTOMATIC-PARITY-20260707` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | New end-to-end test in `platform_tests/scripts/test_implementation_start_gate.py` calling `gate_decision()` with a payload representing `git add -- <path>` for a path inside an approved terminal-VERIFIED thread's `target_paths` | `gate_decision()` returns `{}` (not blocked) — currently FAILS with a `GTKB-GIT-LIFECYCLE` block; this is the regression test that must flip green |
| Existing WI-4837 disqualifier tests (outside-target, mixed-target, broad `-A`, chained command, no work-intent claim, non-terminal chain) | Re-run `platform_tests/scripts/test_implementation_authorization.py` + existing WI-4837 cases in `test_implementation_start_gate.py` | All still block (fix must not broaden the clearance's own narrow conditions) |
| `GTKB-GIT-LIFECYCLE` boundary for every other git subcommand | Re-run existing WI-5138 gate tests covering non-`add` direct-git-effect blocking | All still block (fix must not weaken the gate for anything except the one narrow `add` + WI-4837-eligible case) |
| Full regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --no-header` | Full pass, no new failures |
| Code quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py` and `... ruff format --check ...` | Both clean |

## Risk / Rollback

This touches a security-sensitive authorization gate — the WI-4837 `-014` VERIFIED verdict describes its own change to this exact function as "a security-sensitive change to the implementation-start authorization gate; it was verified with extra rigor." The fix here must be additive/narrowing only: it restores one previously-audited exemption path for one specific subcommand (`add`) under the same narrow conditions WI-4837 already specified (single-stage, explicit paths, no flags/pathspec-magic/globs/chaining, terminal-VERIFIED claimed thread, every target inside approved `target_paths`). It must not create any new exemption surface and must not weaken the `GTKB-GIT-LIFECYCLE` block for any other git subcommand.

Rollback: single-commit revert. The change is isolated to one conditional branch in `scripts/implementation_start_gate.py` plus its test file — no schema, config, or cross-file coupling.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5511-post-verified-clearance-shadow-fix`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs a governed authorization regression (a previously-approved recovery path silently shadowed by an unrelated later rewrite), not a new capability surface. Matches the characterization the WI-4837 `-014` verdict used for the original change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
