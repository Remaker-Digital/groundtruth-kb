NEW

# Bridge work-intent session-id live-env precedence repair (WI-4377)

bridge_kind: implementation_proposal
Document: gtkb-bridge-work-intent-session-id-live-env-precedence
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-05 UTC
Session: keep-working automation

author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: codex-keep-working-20260605-bridge-session-id-proposal
author_model: GPT-5 Codex
author_model_version: 2026-06 runtime
author_model_configuration: Codex desktop automation; high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4377

target_paths: ["scripts/gtkb_session_id.py", "scripts/bridge_claim_cli.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py"]

## Summary

Interactive bridge filing can still resolve a stale legacy Claude session id before the live Claude Code session id. The verified WI-4267/WI-4270 work fixed membership drift and centralized the resolver, but deliberately preserved `CLAUDE_SESSION_ID` before `CLAUDE_CODE_SESSION_ID`. That preserved policy is now a live bridge blocker: an interactive session can hold or file work under a phantom legacy UUID while the actual Write payload and current harness context identify a different live `CLAUDE_CODE_SESSION_ID`.

This proposal changes the bridge work-intent precedence policy from legacy-Claude-first to live-Claude-Code-first, while keeping explicit CLI `--session-id` values first. It also changes hook payload handling so live environment session ids win over stale stdin payload session ids, with payload used only as fallback when no live env session id is available.

This does not change the marker-continuity policy. `MARKER_CONTINUITY_ORDER` stays `GTKB_SESSION_ID` first and remains outside this scope.

## Problem Evidence

- Current shared bridge order in `scripts/gtkb_session_id.py` is `CLAUDE_SESSION_ID`, then `CLAUDE_CODE_SESSION_ID`.
- Reproduction from this triage: calling the shared resolver with stale legacy env plus live Claude Code env returns the stale legacy value.
- Reproduction from this triage: `.claude/hooks/bridge-compliance-gate.py` returns a stale payload or stale legacy env session before considering the live `CLAUDE_CODE_SESSION_ID`.
- Owner-reported symptom on 2026-06-05: bridge work-intent session resolution produced phantom UUID `5719749f` instead of the live `CLAUDE_CODE_SESSION_ID`, requiring manual claim-state alignment and blocking interactive bridge filing.

## In-Root Placement Evidence

All target paths are under `E:\GT-KB`. No target path is under `applications/`, and no Agent Red repository path is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge filing and work-intent claims are bridge protocol platform plumbing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge, project, testing, and placement specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries `Project Authorization`, `Project`, and `Work Item` metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - WI-4377 is an active member of PROJECT-GTKB-RELIABILITY-FIXES and the standing PAUTH covers active project members.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - test plan maps each behavior change to focused regression tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes are in-root platform files, not application files.
- `GOV-STANDING-BACKLOG-001` - WI-4377 was captured in MemBase as a P1 defect before this proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner-reported hygiene moved from candidate observation to active work item and bridge proposal state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-reported bridge defect is preserved as a durable work item and bridge proposal.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation remains additive and audited through proposal, GO, implementation report, and verification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - source and hook edits must wait for a live GO packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start packet must be minted from the GO'd proposal before protected edits.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - standing reliability PAUTH bounds this defect repair to source, tests, and hook upgrades.

## Prior Deliberations

- `DELIB-20260645` - archived verified bridge thread `gtkb-claude-code-session-id-env-var-gap`; predecessor fixed the membership omission by adding `CLAUDE_CODE_SESSION_ID`.
- `DELIB-20260748` and `DELIB-20260749` - verified shared resolver unification for WI-4270; established one shared membership set plus per-surface order constants.
- `DELIB-2707` - work-intent registry review requiring earlier acquisition boundaries to prevent duplicate drafting/token burn; related to the separate WI-4378 guard but not implemented in this P1 repair.
- `DELIB-20260673` - parallel-session fragmentation evidence; supports the separate WI-4378 follow-up for same-role loop coordination.

## Owner Decisions / Input

- 2026-06-05 owner hygiene directive: bridge session resolution resolved a phantom UUID (`5719749f`) instead of the live `CLAUDE_CODE_SESSION_ID`, requiring manual claim-state alignment and blocking interactive bridge filing.
- 2026-06-05 owner follow-up directive: "Please keep working on these until they are resolved."
- This work is filed through the reliability fast-lane: WI-4377 is a P1 defect in PROJECT-GTKB-RELIABILITY-FIXES and is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for active project members.

## Requirement Sufficiency

Existing requirements are sufficient. The bridge protocol already requires session-consistent work-intent claims and implementation-start authorization. The defect is in the resolver policy and hook fallback order, not in a missing governance requirement. No new GOV, ADR, or DCL is needed for this P1 fix.

## Clause Scope Clarification

This is not a bulk operation. It updates one resolver policy and its direct bridge work-intent consumers for one P1 work item. It does not migrate bridge state, change the bridge status model, alter marker-continuity session role resolution, or modify any application runtime. Bulk-operation evidence: no inventory sweep, review-packet batch, Phase-deferred decision marker, or multi-item backlog mutation is proposed.

## Proposed Scope

### IP-1 - Prefer live Claude Code env over stale legacy Claude env for bridge work-intent

In `scripts/gtkb_session_id.py`, change `BRIDGE_WORK_INTENT_ORDER` so `CLAUDE_CODE_SESSION_ID` precedes `CLAUDE_SESSION_ID`.

Retain explicit argument precedence in `resolve_session_id()`: a non-empty explicit value still wins over every env var. `scripts/bridge_claim_cli.py --session-id <id>` must continue to override env values.

### IP-2 - Make hook payload session id a fallback, not the first bridge work-intent authority

In `.claude/hooks/bridge-compliance-gate.py` and `.claude/hooks/bridge-axis-2-surface.py`, change work-intent session resolution to prefer live env through `WORK_INTENT_SESSION_ENV_VARS`, then fall back to `payload["session_id"]` only when no live env session id exists.

This keeps headless or stdin-only contexts working while preventing stale payload data from overriding the current interactive harness session.

### IP-3 - Keep template and helper fallback copies aligned

Update the fail-soft fallback tuples in `.claude/skills/bridge-propose/helpers/write_bridge.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, and `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`.

The helper should still import `BRIDGE_WORK_INTENT_ORDER` when available and use the fallback only for partial installs.

### IP-4 - Add focused regression coverage

Update existing focused tests to prove:

- `CLAUDE_CODE_SESSION_ID` beats stale `CLAUDE_SESSION_ID` in the bridge work-intent order.
- explicit `--session-id` still beats all env vars in the CLI.
- bridge-compliance gate and AXIS 2 surface prefer live env over stale payload.
- no live env still falls back to payload.
- fallback tuples match the canonical shared order.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not introduce credential fixtures; use synthetic session ids only. | Secret scan remains covered by bridge helper and normal hooks. | |
| CQ-PATHS-001 | Yes | Keep all target paths root-relative and under `E:\GT-KB`. | Applicability preflight and target path review. | |
| CQ-COMPLEXITY-001 | Yes | Keep resolver change to ordering and a small env-then-payload helper branch. | Ruff plus focused tests. | |
| CQ-CONSTANTS-001 | Yes | Use existing named order constants; no magic session-env lists outside tested fallback copies. | Drift-lock tests compare fallback copies to canonical order. | |
| CQ-SECURITY-001 | Yes | No subprocess, credential, deletion, or deployment behavior change. | Code review plus focused tests. | |
| CQ-DOCS-001 | Yes | Update docstrings/comments where they currently describe the old preserved order. | Source review during implementation. | |
| CQ-TESTS-001 | Yes | Add focused regressions for live-env precedence, explicit CLI override, env-first hook resolution, and payload fallback. | Focused pytest command over five target test files. | |
| CQ-LOGGING-001 | N/A | | | Resolver surfaces do not add logging. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, scoped Ruff check, scoped Ruff format-check, bridge applicability preflight, and ADR/DCL clause preflight before report. | Commands recorded in post-implementation report. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: file through the bridge and run `show_thread_bridge.py` to confirm no INDEX drift.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`: after GO, run `implementation_authorization.py begin --bridge-id gtkb-bridge-work-intent-session-id-live-env-precedence --no-write`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run focused pytest over the five target test files.
- Live-env precedence: add tests reproducing stale legacy env plus live Claude Code env and assert live env wins.
- Explicit CLI override: add or update `test_bridge_claim_cli.py` coverage proving explicit session id wins over both env values.
- Hook payload fallback: add hook tests for env-first and payload-only fallback branches.
- Code quality: run scoped `ruff check` and `ruff format --check` on changed source/test files.

## Acceptance Criteria

1. `scripts.gtkb_session_id.BRIDGE_WORK_INTENT_ORDER[:2] == ("CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID")`.
2. `scripts.bridge_claim_cli` still resolves an explicit `--session-id` before any env var.
3. Bridge compliance and AXIS 2 work-intent resolution choose live env over stale payload.
4. Template/helper fallback tuples match the canonical bridge order.
5. Focused tests and ruff checks pass.
6. Post-implementation report includes exact command evidence and spec-to-test mapping.

## Risk / Rollback

Risk is limited to bridge work-intent identity selection. The intended behavior change is narrow: stale legacy Claude session ids no longer win over live Claude Code session ids. If an environment truly has only `CLAUDE_SESSION_ID`, it still resolves through the second bridge-order slot. If a headless hook invocation has no live env but does have a payload session id, payload fallback still works.

Rollback is a single revert of the resolver order and hook fallback changes plus associated tests. No data migration or bridge state rewrite is proposed.

## Bridge INDEX Update Evidence

This proposal is filed through the bridge and inserted as `NEW: bridge/gtkb-bridge-work-intent-session-id-live-env-precedence-001.md` under `Document: gtkb-bridge-work-intent-session-id-live-env-precedence` in `bridge/INDEX.md`.
