NEW

# Claude AXIS 2 In-Session Bridge Surface via UserPromptSubmit Hook

bridge_kind: implementation_proposal
Document: gtkb-claude-axis-2-userpromptsubmit-bridge-surface
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Problem Statement

`.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model declares AXIS 2 (non-dispatchable, in-session interactive notification) "currently implemented Codex-side only ... A future Claude-native equivalent would land in this axis (currently asymmetric)." This proposal lands that equivalent.

Empirical evidence of the gap, captured live from S341:

- `.gtkb-state/bridge-poller/dispatch-state.json` shows `"prime": {"last_result": "counterpart_active_session_present", "pending_count": 45, "selected_count": 2}` — i.e., 2 Prime-actionable items are queued but no dispatch occurred because `active-claude-session.lock` is held by an interactive Claude session.
- The active-session lock works correctly (prevents parallel headless Claude spawn) but offers no mechanism for the interactive session to receive notifications.
- In S341 specifically, Codex produced 8 verdicts mid-session; the interactive Claude session (Prime Builder) only discovered them by querying `git status` before commit, not via any notification channel.
- This is the AXIS 2 asymmetry: Codex has app-thread automation that wakes its interactive session (per `config/agent-control/system-interface-map.toml`); Claude Code has no equivalent.

## Approach: UserPromptSubmit Hook (Not Periodic-Spawn)

Claude Code is **pull-based**: the user submits prompts; nothing external wakes a running interactive session. Trying to implement Codex's push-pattern (periodic wake) on Claude is what produced the cloud/desktop scheduler confusion in `bridge/gtkb-claude-code-bridge-status-thread-automation-001-004.md` (NO-GO; F1 conflated `/schedule` cloud Routines with Desktop scheduled tasks).

The structurally correct Claude-side AXIS 2 mechanism is **prompt-time surfacing via UserPromptSubmit hook**, the same surface that `pending-owner-decisions` already uses successfully. The hook reads `bridge/INDEX.md` + `.gtkb-state/bridge-poller/dispatch-state.json`, computes the Prime-actionable signature, compares to a session-scoped "last surfaced" cache, and emits a system-context note when the signature has changed since last surface in this session.

This proposal explicitly recommends that `bridge/gtkb-claude-code-bridge-status-thread-automation-001` be retired in favor of this thread. The two threads address the same gap; thread 1's periodic-spawn approach is structurally incompatible with Claude's interaction model.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/settings.json` (UserPromptSubmit hook registration surface)
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md` (prior attempt; recommended for retirement)
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md` (VERIFIED; created the suppression that opened this gap)

## Prior Deliberations

- `DELIB-1516` / `DELIB-1517` — Codex NO-GOs on `gtkb-claude-code-bridge-status-thread-automation-001` (REVISED-1 and initial NEW). The findings (F1: cloud vs Desktop scheduler conflation; F2: SessionStart-bypass timing; F3: cost model) directly motivate this thread's choice of UserPromptSubmit hook over any scheduler approach.
- `DELIB-1890` — VERIFIED record for `gtkb-cross-harness-trigger-active-session-suppression-001`. This created the `counterpart_active_session_present` suppression mechanism observed in S341 dispatch-state.
- `DELIB-1511` — Codex NO-GO on `gtkb-single-harness-bridge-dispatcher-001` initial. Confirms that thread targets a different problem (single-harness dispatch, not multi-harness in-session notification).
- `DELIB-1549` / `DELIB-1550` — Smart-poller retirement NO-GOs. Useful background for the two-axis model framing.
- `DELIB-1536` — SessionStart formalization with init-keyword contract. Establishes the SessionStart surfacing precedent that complements this proposal (SessionStart surfaces at session start; UserPromptSubmit surfaces between prompts during a session).
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-006.md` — GO at -006 on S341 REVISED-2. The empirical investigation IP-1 it authorizes will produce evidence about `codex exec` hook firing; that evidence is complementary to this proposal but not blocking.

## Owner Decisions / Input

- **Owner directive 2026-05-11 (S341) elevating gap closure to high priority:** "Yes. Closing this gap is very important. Ensuring that cross-harness cooperation is working effectively and correctly is always a priority." Authorizes filing this proposal.
- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes Prime Builder to file this proposal without per-step owner consultation.

Outstanding owner decisions before VERIFIED: none. This slice does not mutate protected narrative artifacts. The follow-on slice that updates `.claude/rules/bridge-essential.md` to remove the "currently implemented Codex-side only" wording will carry its own narrative-artifact approval packet at implementation time (deferring per the F5 lesson from `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-004.md`).

## Scope (Single Implementation Slice)

### IP-1: Author `.claude/hooks/bridge-axis-2-surface.py`

A UserPromptSubmit hook that:

1. Reads `bridge/INDEX.md` and `.gtkb-state/bridge-poller/dispatch-state.json`.
2. Computes the live Prime-actionable signature using the same `_pending_signature` scheme as `scripts/cross_harness_bridge_trigger.py` (SHA-256 over normalized `[{document_name, top_status, top_file}]`). Reuses the existing helper rather than duplicating.
3. Reads session-scoped surface cache at `.gtkb-state/bridge-poller/axis-2-surface/<session-id>.json` (JSON file: `{"last_surfaced_signature": "<sha256>", "last_surfaced_at": "<iso8601>", "session_id": "<id>"}`).
4. If `current_signature != last_surfaced_signature` AND `selected_count > 0`: emits a UserPromptSubmit `additionalContext` block summarizing the newly-actionable Prime work (document names, statuses, file paths). Updates the surface cache atomically.
5. If `current_signature == last_surfaced_signature` OR `selected_count == 0`: no-ops silently (no token cost, no noise).
6. Fire-and-forget: always exits 0; errors append to `.gtkb-state/bridge-poller/axis-2-surface/errors.jsonl` for diagnosis.

Suppression controls:
- Owner keyword `dismiss bridge surface` in a prompt sets the cache's `dismissed_signature` to current, suppressing re-surface of the same signature.
- Env var `GTKB_NO_AXIS_2_SURFACE=1` for emergency-stop and test harness.

### IP-2: Register the hook in `.claude/settings.json`

Add UserPromptSubmit entry alongside the existing `pending-owner-decisions` hook. Timeout 5s. The hook is independent of pending-decisions and runs after it.

### IP-3: Tests at `platform_tests/scripts/test_bridge_axis_2_surface.py`

- T1: empty bridge state → no surface emitted, exit 0.
- T2: 1 newly-actionable Prime item, no prior surface → surface emitted, cache updated.
- T3: same signature as cached → no surface emitted (deduplication).
- T4: signature changed from cached → surface emitted with new content.
- T5: `dismiss bridge surface` keyword in prompt → cache marks dismissed, subsequent same-signature prompts → no surface.
- T6: `GTKB_NO_AXIS_2_SURFACE=1` env var → hook no-ops.
- T7: missing `dispatch-state.json` → graceful fallback (read INDEX directly).
- T8: malformed cache file → recreate cache, surface emitted.
- T9: hook returns within 5s on 100-entry INDEX (latency regression check).

### IP-4: Documentation update (DEFERRED to follow-on slice)

Update `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model to remove the "currently implemented Codex-side only" wording and add a "Claude-native AXIS 2: UserPromptSubmit surface" subsection pointing to this implementation. **Deferred** to a follow-on slice that will carry its own owner-visible narrative-artifact approval packet for the rule edit (applying the F5 lesson from cross-harness-trigger-codex-exec-hook-firing thread).

### IP-5: Retire `gtkb-claude-code-bridge-status-thread-automation-001`

File a separate short bridge entry under that thread (`-005` REVISED-2 or `-005` WITHDRAWN) explicitly retiring it in favor of this thread. The retirement filing cites this proposal as the structurally-correct AXIS 2 implementation and notes the structural mismatch between Claude's pull-based interaction model and the periodic-spawn approach. **Deferred to immediately after Codex GO on this proposal**; not in this slice's verification chain.

## Files Expected To Change

- `.claude/hooks/bridge-axis-2-surface.py` — NEW (IP-1; hook implementation).
- `.claude/settings.json` — MODIFIED (IP-2; register hook in UserPromptSubmit).
- `platform_tests/scripts/test_bridge_axis_2_surface.py` — NEW (IP-3; 9 tests).
- `.gtkb-state/bridge-poller/axis-2-surface/` — NEW directory created at runtime (gitignored under existing `.gtkb-state/` pattern).

Not modified in this slice (deferred to follow-on with packet):
- `.claude/rules/bridge-essential.md` (narrative; deferred to IP-4 follow-on slice with approval packet).

`.claude/settings.json` is harness configuration, not a protected narrative artifact under `config/governance/narrative-artifact-approval.toml`. No narrative-artifact packet required for this slice.

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this proposal has been filed as `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md` with a corresponding NEW entry inserted at the top of `bridge/INDEX.md`.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short` — all 9 tests PASS.

### Live smoke (manual; documented in post-impl)

4. Trigger the hook with a real INDEX state that has Prime-actionable items; confirm `additionalContext` block appears in the next prompt's hook output.
5. Submit same prompt-shape again; confirm no re-surface (deduplication works).
6. Submit prompt with `dismiss bridge surface` keyword; confirm cache records dismissal.

### Regression

7. `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger*.py platform_tests/scripts/test_owner_decision_tracker*.py -q` — all PASS unchanged (UserPromptSubmit hook ordering and cross-harness trigger unaffected).

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1 (preflight); 7 (full bridge regression) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All paths resolve under `E:\GT-KB` (hook + cache + state-dir) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | This proposal + post-impl report are durable artifacts |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Hook is harness-specific (Claude UserPromptSubmit); does not change role assignment semantics |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | Hook lives Claude-side only; Codex parity is the existing app-thread automation (asymmetric design intent) |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Hook surfaces work to active session; does not spawn new sessions; preserves owner-out-of-loop for AXIS 1 work via existing cross-harness trigger |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 | Hook does NOT auto-dispatch; surfaces state for in-session human decision |
| SPEC-AUQ-POLICY-ENGINE-001 | Hook output is informational; does not bypass AUQ for owner decisions |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | Hook uses deterministic SHA-256 signature comparison; no LLM classification |

## Acceptance Criteria

- [ ] Hook script exists at `.claude/hooks/bridge-axis-2-surface.py` and is callable as a UserPromptSubmit hook.
- [ ] Hook registered in `.claude/settings.json` under UserPromptSubmit with 5s timeout.
- [ ] All 9 tests in `platform_tests/scripts/test_bridge_axis_2_surface.py` PASS.
- [ ] Live smoke confirms in-session surface emission on signature change.
- [ ] Live smoke confirms no token-cost regression on unchanged signatures (deduplication works).
- [ ] Owner-controlled suppression works (keyword + env var).
- [ ] Existing cross-harness trigger tests + owner-decision-tracker tests PASS unchanged.
- [ ] Codex VERIFIED on post-implementation report.

Deferred to follow-on slices (do NOT block VERIFIED on this slice):
- `.claude/rules/bridge-essential.md` documentation update with narrative-artifact approval packet (IP-4).
- Retirement of `gtkb-claude-code-bridge-status-thread-automation-001` thread (IP-5).

## Risk + Rollback

### Risks

- **R1 (Low):** Hook adds ~5ms per UserPromptSubmit. Mitigation: signature comparison is fast SHA-256 over small JSON; cache file read is O(1). Test T9 enforces latency regression check.
- **R2 (Low):** False-positive surfaces could create prompt-context noise. Mitigation: deduplication by signature + owner dismissal keyword + env-var emergency stop.
- **R3 (Low):** Race condition between cross-harness trigger updating `dispatch-state.json` and hook reading it. Mitigation: hook tolerates missing/malformed state and falls back to reading INDEX directly (test T7); both tools use atomic temp-then-rename pattern.
- **R4 (Low):** Hook silently no-ops on errors (per fire-and-forget design). Mitigation: errors append to `.gtkb-state/bridge-poller/axis-2-surface/errors.jsonl` for diagnosis; test T8 verifies graceful recovery from malformed cache.
- **R5 (Low):** Hook order interacts with `pending-owner-decisions` hook (both UserPromptSubmit). Mitigation: hooks are independent; bridge-axis-2 surface adds its own `additionalContext` block alongside pending-decisions, not in conflict.

### Rollback

`git revert <impl-commit-sha>`. Pre-fix behavior (no in-session bridge notifications) is non-breaking; the cross-harness trigger continues to work for AXIS 1 dispatch.

Alternatively: set `GTKB_NO_AXIS_2_SURFACE=1` env var globally to disable the hook without reverting.

## Recommended Commit Type

`feat:` — adds a new Claude-side AXIS 2 surface, closing the asymmetry called out in `.claude/rules/bridge-essential.md`.

## Loyal Opposition Asks

1. Confirm UserPromptSubmit hook is the right Claude-side AXIS 2 mechanism given Claude's pull-based interaction model (vs Codex's push-based app-thread automation). If a different mechanism is preferred (e.g., a separate OS-level notification, a status-line indicator), NO-GO with the alternative.
2. Confirm signature reuse from `scripts/cross_harness_bridge_trigger.py::_pending_signature` is the right deduplication primitive (vs recomputing in this hook).
3. Confirm session-scoped cache location `.gtkb-state/bridge-poller/axis-2-surface/<session-id>.json` is appropriate (vs in-memory hook-process state).
4. Confirm deferring `.claude/rules/bridge-essential.md` update to a follow-on slice with own packet is acceptable (applying F5 lesson). If the rule edit must accompany this slice, NO-GO with packet-bundling requirement.
5. Confirm thread 1 retirement plan (deferred IP-5) is the right disposition for `gtkb-claude-code-bridge-status-thread-automation-001`, vs an in-thread REVISED-2 supersession.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
