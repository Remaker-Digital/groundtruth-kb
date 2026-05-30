NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s365-work-intent-integration
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Implementation Proposal - Bridge Work-Intent Registry Integration into Prime-Side Write Paths

bridge_kind: implementation_proposal
Document: gtkb-work-intent-registry-prime-write-integration
Version: 001 (NEW)
Implements: WI-3414
Work Item: WI-3414
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
target_paths: [".claude/hooks/bridge-compliance-gate.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py"]
Recommended commit type: feat:
Date: 2026-05-28 UTC

## Implementation Claim

This proposal integrates the existing `scripts/bridge_work_intent_registry.py` foundation module (VERIFIED via WI-3274 at `bridge/gtkb-bridge-parallel-session-collision-006.md`) into three Prime-side write paths so concurrent Prime sessions cannot independently draft and file the same bridge thread version. The work closes the "deferred integration risk" explicitly noted in the registry foundation's `-006` VERIFIED verdict.

The integration consumes the registry's existing `acquire`, `release`, `current_holder`, and `revalidate_thread_version` API; it does NOT modify the registry module itself. Each integration point is independently revertable.

This work attaches to the **standing reliability fast lane** per `feedback_reliability_fast_lane.md` and the `GOV-RELIABILITY-FAST-LANE-001`-cited PAUTH coverage: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-3414 by active project membership (no per-fix authorization required). The closely-related earlier work (`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, `PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS` (retired)) is cited as historical context only.

## Race Scenario This Closes (S365 observed evidence)

During S365, the AXIS-1 cross-harness event-driven trigger detected an actionable signature change on `gtkb-git-repo-broken-blob-investigation` after Codex filed `-008` NO-GO. A fresh headless Prime spawn was dispatched at 02:54 UTC. The interactive Prime session (this one) also was active at 02:54 UTC. Both Prime instances independently decided to address the same NO-GO finding. The spawn filed `-009` at 02:59 UTC; the interactive session attempted to write `-009` ~3 hours later and was caught by the Write tool's incidental "must read before write" check.

The race wasted ~30 minutes of interactive-session token budget on a redundant draft. If Write-tool timing had been reversed (interactive write first, then spawn write), the existing accidental safety net would not have triggered and the bridge thread could have lost the in-flight draft work to overwrite.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal extends the bridge protocol's coordination guarantees by integrating the work-intent registry at the Prime-side write boundary. `bridge/INDEX.md` remains canonical workflow state; the registry adds a per-thread holder record at `.gtkb-state/work-intent/<slug>.json` consulted by Prime-side write paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal carries forward applicable governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each integration point to a focused test surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched files reside under `E:\GT-KB`. The state directory `.gtkb-state/work-intent/` is also in-root.
- `GOV-STANDING-BACKLOG-001` - WI-3414 is recorded in MemBase and an active member of `PROJECT-GTKB-RELIABILITY-FIXES` via `project_work_item_memberships`.
- `GOV-RELIABILITY-FAST-LANE-001` - this work meets the standing reliability fast-lane eligibility criteria (small defect/reliability fix closing a deferred-integration race observed during S365).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the integration treats the bridge writer as a governed deterministic service; the registry's existing state files form an audit trail.

## Prior Deliberations

- `bridge/gtkb-bridge-parallel-session-collision-006.md` (VERIFIED 2026-05-27, WI-3274): the registry foundation module was approved as foundation-only with explicit deferred integration: "no bridge writer, AXIS-2, startup payload, compliance gate, or hook integration was changed... does not close the deferred integration risk prematurely." This proposal closes that deferred integration risk. WI-3274 is cited as historical context only; WI-3414 is the declared implementation work item for this proposal.
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md` (VERIFIED 2026-05-27, WI-3280): added a quiesce window to the cross-harness trigger to coalesce close-spaced PostToolUse fires for the same INDEX edit. That work addressed a different race (multiple trigger fires per edit); the current proposal addresses a complementary race (multiple Prime spawns drafting in parallel after legitimate separate fires). WI-3280 is cited as historical context only.
- `DELIB-2217` (Bridge thread record for parallel-session-collision; 6 versions, VERIFIED).
- `DELIB-2348` through `DELIB-2351` (Cross-Harness Trigger INDEX Edit Race + Quiesce Window reviews).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (S312 owner directive): repetitive AI plumbing is a defect; the work-intent registry is the canonical deterministic service for coordinating Prime-side bridge writes.

## Requirement Sufficiency

Existing requirements sufficient. The deferred-integration risk language in `GOV-FILE-BRIDGE-AUTHORITY-001`-cited VERIFIED records (`bridge/gtkb-bridge-parallel-session-collision-006.md`) already authorizes the integration class. No new specifications are required. The integration consumes existing API; it adds no new public interfaces.

## Owner Decisions / Input

- AUQ S365 #1 ("Codex side is idle..."): owner selected "Unstick a multi-round NO-GO" as session direction.
- AUQ S365 #2 (multi-round NO-GO candidate selection): Prime selected `gtkb-git-repo-broken-blob-investigation` as the more tractable of two 8-round NO-GOs; owner directive stood.
- AUQ S365 #3 ("Original directive fulfilled by parallel spawn..."): owner selected "Investigate the AXIS-1 race pattern" with stated goal of filing a small bridge proposal for a Prime-side pre-write guard.
- AUQ S365 #4 ("Integration scope..."): owner selected "A + B + C - full integration" (hook + helper + trigger).

No additional owner approval is required to file this NEW proposal. The standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers `source`, `test_addition`, `hook_upgrade` mutation classes by active project membership, which together cover all three integration points (hook upgrade for `.claude/hooks/`, source for `.claude/skills/` and `scripts/`, test_addition for `platform_tests/`).

## Implementation Plan

### Integration Point A - PreToolUse Write hook (`.claude/hooks/bridge-compliance-gate.py`)

Add a new check function that fires when the hook receives a PreToolUse Write/Edit event whose `tool_input.file_path` matches `^bridge/(?P<slug>[a-z0-9][a-z0-9-]+)-\d{3,}\.md$`:

1. Extract the bridge thread slug from the path.
2. Read the current session's `session_id` from the hook payload's `session_id` field (Claude Code provides this in stdin per the SessionStart / PreToolUse hook protocol).
3. Call `bridge_work_intent_registry.current_holder(slug)`.
4. If `current_holder` returns a record whose `session_id` does NOT match this session's `session_id`, emit `{"decision": "block", "reason": "..."}` with a message including the holder's `session_id`, `acquired_at`, and `ttl_expires_at`.
5. If `current_holder` returns `None` or matches this session, allow Write through.

The hook's existing structure (PreToolUse handler with input-event parsing) is extended; no architectural change. Self-acquired records do not block (per the registry's `acquire` semantic). Expired records do not block (per `current_holder`'s expiry check).

### Integration Point B - bridge-propose helper (`.claude/skills/bridge-propose/helpers/write_bridge.py`)

Before any draft work begins in the helper:

1. Extract the thread slug from the caller-provided bridge filename.
2. Read the session_id from the helper's environment context (the bridge-propose skill is invoked under a Claude session; `session_id` is available from the SessionStart cache or via a passed parameter).
3. Call `bridge_work_intent_registry.acquire(slug, session_id, ttl_seconds=300)` (5-minute TTL covers a typical drafting window).
4. If `acquire` returns `False`, report the current holder via `current_holder(slug)` and refuse to start drafting. Exit non-zero with a clear message.
5. If `acquire` returns `True`, proceed with the existing helper logic.
6. On successful Write (or on caller cleanup), call `release(slug, session_id)` to free the slot.
7. The TTL ensures stale records auto-expire if a session is killed mid-draft.

### Integration Point C - cross-harness trigger (`scripts/cross_harness_bridge_trigger.py`)

Before spawning a counterpart Prime session for a newly-actionable thread:

1. Parse the actionable bridge thread slug from the INDEX entry being dispatched.
2. Call `bridge_work_intent_registry.current_holder(slug)`.
3. If `current_holder` returns a non-`None` record (any session holds it), defer the spawn. Log to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` with reason `work_intent_already_held` and the holder's `session_id` / `acquired_at`. Do NOT consume the dispatch budget for this signature change yet.
4. If `current_holder` returns `None`, proceed with the existing spawn logic. The spawned Prime session, on starting work, will itself call `acquire` via Integration Point B's helper integration.

The trigger's existing actionable-signature change detection, quiesce window, and dispatch-state persistence are NOT modified. This integration adds one consultation step before the spawn syscall.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] Integration Point A: `.claude/hooks/bridge-compliance-gate.py` modified to call `bridge_work_intent_registry.current_holder()` and block Write when a different session is the holder.
- [ ] Integration Point B: `.claude/skills/bridge-propose/helpers/write_bridge.py` modified to `acquire`/`release` work-intent records around draft work.
- [ ] Integration Point C: `scripts/cross_harness_bridge_trigger.py` modified to defer spawn when a holder exists.
- [ ] Tests at `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py` verify hook denial when a different session holds the work-intent and pass-through when the same session or no holder exists.
- [ ] Tests at `platform_tests/skills/test_bridge_propose_helper_work_intent.py` verify helper refuses to draft when another session holds; acquires and releases correctly on success.
- [ ] Tests at `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py` verify trigger defers spawn when a holder exists; proceeds when none.
- [ ] All three integration points stay within the standing PAUTH's `source` / `hook_upgrade` / `test_addition` mutation classes.
- [ ] Test runs with workspace-local `--basetemp` per the standard PowerShell pattern observed in prior verdicts.
- [ ] No modification to `scripts/bridge_work_intent_registry.py` itself (consumption only).
- [ ] `bridge/INDEX.md` updated with `REVISED` lines for any post-impl report cycles; the bridge thread proceeds through standard GO -> implement -> NEW -> VERIFIED flow.
- [ ] Post-implementation report demonstrates the race scenario reproduces, then is blocked by the integration.
- [ ] Loyal Opposition returns VERIFIED on the eventual post-implementation report.

## Spec-to-Test Mapping

| Specification | Verification Command | Expected | Test Path |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge protocol; coordination of Prime-side writes) | Integration tests run pytest on the 3 new test files: hook denies, helper refuses, trigger defers. | All 3 deny-paths exercised; PASS | `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py`, `platform_tests/skills/test_bridge_propose_helper_work_intent.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-intent-registry-prime-write-integration` | `preflight_passed: true`; no missing required specs | preflight invocation |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This Spec-to-Test Mapping table populated in the post-impl report with executed pytest evidence. | mapped + observed PASS for each row | post-impl REVISED |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Source files inspected by `git check-ignore -v <file>` on each target_paths entry; all under `E:\GT-KB`. | No ignore match; all in-root | direct file paths |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-3414 --json`. | WI-3414 active in `PROJECT-GTKB-RELIABILITY-FIXES` | live MemBase |
| `GOV-RELIABILITY-FAST-LANE-001` | PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-3414 by membership. | active PAUTH; WI-3414 covered | live MemBase |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge thread + tests + state files form a durable governed graph (this NEW, eventual GO, post-impl, VERIFIED) | append-only bridge versions | bridge thread |

## Risks

1. **session_id availability across all 3 integration points.** Claude Code's hook payloads include `session_id` per the standard hook contract; the bridge-propose helper has access via the SessionStart cache or env. The cross-harness trigger does NOT have its own session_id (it's a spawning mechanism, not a session itself). For Integration Point C, the trigger uses `current_holder` (read-only consultation, no `acquire`), so no session_id is required for the trigger itself. The spawned counterpart Prime session is what calls `acquire` later.

2. **TTL choice in Integration Point B.** A 5-minute TTL covers most drafting windows but could expire mid-draft for very long sessions. Mitigation: the helper can extend the TTL by re-`acquire`-ing periodically, or the post-impl session can extend the TTL on the same session_id (per `acquire`'s same-session passthrough). For Slice 1, 5 minutes is the conservative starting point; future telemetry on actual drafting windows can inform a tuning REVISED.

3. **Coordination with existing AXIS-1 quiesce window.** The quiesce window (from the cited cross-harness-trigger-index-edit-race-quiesce thread) and the work-intent integration are complementary: quiesce coalesces close-spaced trigger fires; work-intent coordinates concurrent drafts. They operate on different time scales and don't conflict. The post-impl test plan includes a coexistence verification.

4. **State directory permissions on Windows.** The registry creates `.gtkb-state/work-intent/<slug>.json` and `.lock` files. The Windows ACL on `E:\GT-KB\.gtkb-state\` may need to permit the running user. Existing usage by other GT-KB tooling suggests this is fine; the post-impl test plan includes a write permission probe.

5. **Hook integration with `hook_upgrade` PAUTH mutation class.** The PreToolUse hook modification falls under `hook_upgrade`; the trigger and helper modifications fall under `source`. These are explicitly in the standing PAUTH's `allowed_mutation_classes`.

## Rollback

Each integration point is independently revertable:
- A: revert the `.claude/hooks/bridge-compliance-gate.py` diff; the hook returns to pre-integration behavior.
- B: revert the helper diff; bridge-propose returns to pre-integration drafting (no `acquire`).
- C: revert the trigger diff; spawn proceeds unconditionally on actionable signature change.

A partial rollback (e.g., A+B retained, C reverted) is consistent — the hook and helper provide the primary race-prevention surface even without trigger pre-checks.

No `groundtruth.db` mutations are made by this proposal. WI-3414 was created via the `python -m groundtruth_kb backlog add` CLI prior to filing this proposal; project membership was set via `db.link_project_work_item('PROJECT-GTKB-RELIABILITY-FIXES', 'WI-3414', ...)` as a one-shot governance-hygiene operation outside this proposal's target_paths scope.

## Loyal Opposition Asks

1. Verify the integration scope is appropriately bounded — three consumption points, no registry-module modification, no new public interfaces.
2. Confirm the standing PAUTH (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) covers `hook_upgrade` + `source` + `test_addition` for the proposed work via WI-3414's active project membership.
3. Confirm the spec linkage carries forward correctly from the parent thread (`gtkb-bridge-parallel-session-collision`) and the sibling thread (`gtkb-cross-harness-trigger-index-edit-race-quiesce`); cited WI-3274 / WI-3280 are historical context, not declared implementation targets (per the soft collision-check warning).
4. Consider whether the TTL default in Integration Point B (300 seconds) should be configurable via env var (`GTKB_WORK_INTENT_TTL_SECONDS`) similar to `GTKB_TRIGGER_QUIESCE_SECONDS`.
5. Issue GO if findings 1-3 hold; or NO-GO with specific revision asks.

## Opportunity Radar

A future Slice 2 could:
- Add `acquire` / `release` to the bridge-stop-drain hook (legacy, retired in S350+ but pattern could recur).
- Add a `gt bridge holders` CLI command surfacing all currently-held bridge work-intent records for owner visibility.
- Extend the registry to track NOT just thread slugs but also `(slug, version)` tuples so two sessions could legitimately work on different versions of the same thread (one revising `-009`, another reviewing `-008`).

These are out of scope for this Slice 1 proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
