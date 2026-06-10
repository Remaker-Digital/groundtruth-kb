REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s366-work-intent-integration-revised
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Revised Implementation Proposal - Bridge Work-Intent Registry Integration (Defense-in-Depth across Trigger, AXIS-2, Helper, Hook + Templates)

bridge_kind: prime_proposal
Document: gtkb-work-intent-registry-prime-write-integration
Version: 003 (REVISED; addresses NO-GO -002 findings P1-001 and P1-002)
Responds to NO-GO: bridge/gtkb-work-intent-registry-prime-write-integration-002.md
Supersedes: bridge/gtkb-work-intent-registry-prime-write-integration-001.md
Implements: WI-3414
Work Item: WI-3414
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
target_paths: ["scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "groundtruth-kb/tests/test_bridge_propose_helper.py"]
Recommended commit type: feat:
Date: 2026-05-28 UTC

## Revision Summary

This REVISED-3 addresses both P1 findings from Codex `-002` NO-GO:

- **P1-001** (acquisition boundary too late): the original `-001` scope acquired only at helper-invocation time, by which point both Prime sessions had already burned drafting tokens. This REVISED-3 pushes acquisition earlier through **two new integration points** — the cross-harness trigger acquires on-behalf-of the worker BEFORE spawn, and the AXIS-2 surface consults the registry at render time to mark held entries as "ALREADY CLAIMED" so interactive Prime sessions know to skip them. The original helper and hook integration are retained as a write-boundary safety net (defense in depth).
- **P1-002** (managed scaffold/template omission): the original `-001` target_paths only listed the installed copies under `.claude/`. This REVISED-3 adds the managed template counterparts at `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`, plus the package test `groundtruth-kb/tests/test_bridge_propose_helper.py` so adopter projects receive the work-intent integration via `gt project upgrade`.

The substantive design philosophy is now **defense in depth**: four boundaries, each independently revertable, that together close the race observed in S365. The integration consumes the existing `scripts/bridge_work_intent_registry.py` API; no modification to the registry module itself.

## Race Closure (defense in depth)

The S365 race had this timeline:

```
T+0       Codex files NO-GO at -008
T+0       AXIS-1 cross-harness trigger detects actionable change
T+~5s     AXIS-1 spawns headless Prime worker
T+~5s     Interactive Prime session sees AXIS-2 surface
T+30s     Both sessions independently decide to work the thread
T+30s..   Both sessions draft response in parallel (token-heavy)
T+5min    Spawn writes -009
T+~3hr    Interactive attempts to write -009; accidentally caught by Write tool's "read before write" rule
```

Defense in depth closes this race at four boundaries:

| Boundary | Integration Point | When | What it prevents |
|----------|-------------------|------|-------------------|
| 1 | Trigger pre-spawn acquire | T+~5s, before spawn | Two AXIS-1 spawns for same thread |
| 2 | AXIS-2 surface registry consult | T+~5s, at surface render | Interactive Prime picking a held thread |
| 3 | Helper `acquire` | T+30s..5min, before draft body | Helper-mediated drafts from racing |
| 4 | PreToolUse hook block | T+5min, at file Write | Any remaining duplicate Writes |

Boundaries 1 and 2 (new in this REVISED) close the **drafting race** (the P1-001 critique). Boundaries 3 and 4 (carried from `-001`) close the **write race**. Together they close the race surface from "30+ minutes of duplicate drafting" down to "few seconds between AXIS-2 render and interactive acquire" — a ~1000x improvement on the wasted-token failure mode.

## Implementation Plan

### Integration Point 1 - Trigger pre-spawn acquire (`scripts/cross_harness_bridge_trigger.py`)

Before spawning a Prime worker for an actionable thread, the trigger calls `bridge_work_intent_registry.acquire(slug, session_id, ttl_seconds=120)` with `session_id = f"trigger-dispatched-{spawn_id}"`. The trigger passes the same `session_id` to the spawned worker via environment variable `GTKB_INHERITED_SESSION_ID`. The worker, on boot, calls `acquire(slug, session_id)` with the inherited session_id and successfully renews under the existing holder (per the registry's same-session passthrough semantic).

- If `acquire` returns `False` (another session already holds), the trigger defers the spawn and logs `{"reason": "work_intent_already_held", "holder": current_holder(slug)}` to `.gtkb-state/bridge-poller/dispatch-failures.jsonl`. No dispatch budget consumed.
- If `acquire` returns `True`, spawn proceeds. The 120-second TTL covers the worker's boot window; the worker extends TTL on boot.
- If the spawn fails (subprocess never starts), the TTL expires the holder in 120s and the next trigger cycle can retry.

### Integration Point 2 - AXIS-2 surface registry consult (`.claude/hooks/bridge-axis-2-surface.py`)

When rendering the AXIS-2 actionable-work surface for an interactive Prime session, the hook iterates the actionable entries from `bridge/INDEX.md`. For each entry, it calls `bridge_work_intent_registry.current_holder(slug)`. If a non-expired holder exists whose `session_id` is NOT this interactive session's `session_id`, the entry is annotated `ALREADY CLAIMED by <holder.session_id> until <holder.ttl_expires_at>` in the rendered table.

- Interactive Prime sees the annotation and skips the claimed entries.
- The hook does NOT acquire on render (rendering is observation, not commitment).
- If `current_holder` returns `None` (no holder) or this session's own holder (renewed acquisitions during multi-turn work), the entry renders as normal actionable.

### Integration Point 3 - Helper `acquire` / `release` (`.claude/skills/bridge-propose/helpers/write_bridge.py` and template counterpart)

Before draft body construction in the helper:

1. Extract thread slug from the bridge filename.
2. Read `session_id` from environment.
3. Call `acquire(slug, session_id, ttl_seconds=300)` (5-minute TTL).
4. If `acquire` returns `False`, report current holder via `current_holder` and exit non-zero with a clear "already claimed by <session_id>" message.
5. If `acquire` returns `True`, proceed with helper logic.
6. Call `release(slug, session_id)` on successful Write, OR let TTL expire on failure.

The template counterpart at `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` receives the same modification so adopter projects get the behavior via `gt project upgrade` (per `groundtruth-kb/templates/managed-artifacts.toml:508-519` `skill.bridge-propose.helper` definition: `upgrade_policy = "overwrite"`).

### Integration Point 4 - PreToolUse Write hook (`.claude/hooks/bridge-compliance-gate.py` and template counterpart)

Add a check function to the existing PreToolUse hook. When the tool is Write or Edit and `tool_input.file_path` matches `^bridge/(?P<slug>[a-z0-9][a-z0-9-]+)-\d{3,}\.md$`:

1. Extract thread slug from the path.
2. Read `session_id` from the hook payload's `session_id` field.
3. Call `current_holder(slug)`.
4. If a non-expired holder exists with a different `session_id`, emit `{"decision": "block", "reason": "..."}` with holder details.
5. Otherwise, allow Write through.

The template counterpart at `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (per `groundtruth-kb/templates/managed-artifacts.toml:119-129` `hook.bridge-compliance-gate` definition: `upgrade_policy = "overwrite"`) receives the same modification.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the integration extends bridge protocol coordination at the Prime-side write boundary AND at the dispatch + surface boundaries. `bridge/INDEX.md` remains canonical workflow state; the registry adds per-thread holder records at `.gtkb-state/work-intent/<slug>.json` consulted by trigger, surface, helper, and hook.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED carries forward applicable governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each integration point to focused tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched files reside under `E:\GT-KB`. The state directory `.gtkb-state/work-intent/` is also in-root.
- `GOV-STANDING-BACKLOG-001` - WI-3414 is recorded in MemBase and an active member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-RELIABILITY-FAST-LANE-001` - this work meets the standing reliability fast-lane criteria.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the integration treats bridge writes as a governed deterministic service; the registry's state files form an audit trail.

## Prior Deliberations

- `bridge/gtkb-work-intent-registry-prime-write-integration-002.md` (Codex NO-GO on this thread's `-001`, 2026-05-28). P1-001 critiqued the acquisition boundary; P1-002 critiqued the omitted template surfaces. This REVISED-3 addresses both.
- `bridge/gtkb-work-intent-registry-prime-write-integration-001.md` (original NEW, 2026-05-28). The substantive integration intent is preserved; only the boundary set and target_paths are expanded.
- `bridge/gtkb-bridge-parallel-session-collision-006.md` (VERIFIED 2026-05-27, WI-3274) - the registry foundation module; deferred integration explicitly noted. WI-3274 is historical context, not the declared implementation target of this proposal.
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md` (VERIFIED 2026-05-27, WI-3280) - the sibling quiesce-window thread. The current proposal's Integration Point 1 (trigger pre-spawn acquire) is complementary to the quiesce window: quiesce coalesces close-spaced INDEX edits; work-intent acquire coordinates dispatch decisions across the coalesced window.
- `DELIB-2217` (parallel-session-collision thread record), `DELIB-2348` through `DELIB-2351` (quiesce reviews).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the work-intent registry is the canonical deterministic service for bridge write coordination.

## Requirement Sufficiency

Existing requirements sufficient. The deferred-integration risk language in `bridge/gtkb-bridge-parallel-session-collision-006.md` VERIFIED authorizes the integration class. The expanded boundary set (trigger + AXIS-2 + helper + hook + templates) is a natural extension of the deferred surface; no new specifications are required.

## Owner Decisions / Input

- AUQ S365 #1 ("Codex side is idle..."): owner selected "Unstick a multi-round NO-GO".
- AUQ S365 #3 ("Original directive fulfilled by parallel spawn..."): owner selected "Investigate the AXIS-1 race pattern" with goal of filing a small bridge proposal.
- AUQ S365 #4 ("Integration scope..."): owner selected "A + B + C - full integration" (hook + helper + trigger) for `-001`.
- AUQ S366 #1 (this turn, "Codex NO-GO on work-intent-registry integration..."): owner selected "REVISE with broader acquisition surface" — explicit directive to expand scope to address P1-001 substantively (trigger pre-spawn acquire + AXIS-2 surface consultation) and to add template surfaces from P1-002.

No additional owner approval required for this REVISED. The standing PAUTH covers the expanded scope by membership; all target_paths are in `source` / `hook_upgrade` / `test_addition` mutation classes.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED.
- [ ] Integration Point 1: `scripts/cross_harness_bridge_trigger.py` modified to `acquire` on behalf of spawned worker before dispatch; defers spawn when held.
- [ ] Integration Point 2: `.claude/hooks/bridge-axis-2-surface.py` modified to consult `current_holder` per actionable entry and annotate held entries as ALREADY CLAIMED.
- [ ] Integration Point 3: Both `.claude/skills/bridge-propose/helpers/write_bridge.py` AND `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` modified to `acquire`/`release` around draft work.
- [ ] Integration Point 4: Both `.claude/hooks/bridge-compliance-gate.py` AND `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` modified to block Write when another session holds.
- [ ] Tests at `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py` verify trigger acquires before spawn, defers when held, expires on TTL.
- [ ] Tests at `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py` verify surface annotates held entries; non-held entries render normally.
- [ ] Tests at `platform_tests/skills/test_bridge_propose_helper_work_intent.py` verify helper acquires/releases; refuses when held.
- [ ] Tests at `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py` verify hook blocks Write when held; allows when not held or same session.
- [ ] `groundtruth-kb/tests/test_bridge_propose_helper.py` extended to verify template-helper parity with the installed copy.
- [ ] Regression test specifically simulating P1-001's scenario: no holder exists, interactive Prime is selected the thread but hasn't yet written, trigger attempts to spawn a second Prime worker. Expected: trigger acquires on behalf of spawn; spawn proceeds; interactive Prime's later Write is blocked by hook.
- [ ] All target_paths covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` allowed mutation classes (`source` for scripts/helpers, `hook_upgrade` for hooks, `test_addition` for platform_tests + tests/).
- [ ] No modification to `scripts/bridge_work_intent_registry.py` itself (consumption only).
- [ ] Loyal Opposition returns VERIFIED on the eventual post-implementation report.

## Spec-to-Test Mapping

| Specification | Verification Command | Expected | Test Path |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (defense-in-depth coordination across all 4 boundaries) | Run all 4 test files plus the regression test simulating P1-001 scenario. | All 4 boundaries exercise their respective deny-paths; regression confirms ordered closure | All 4 platform_tests files + `groundtruth-kb/tests/test_bridge_propose_helper.py` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-intent-registry-prime-write-integration` | `preflight_passed: true`; no missing required specs | preflight invocation |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-to-Test Mapping table populated in post-impl report with executed pytest evidence per integration point. | mapped + observed PASS for each row | post-impl REVISED |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git check-ignore -v <file>` per target_paths entry; all under `E:\GT-KB`. | No ignore match; all in-root | direct file paths |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-3414 --json`. | WI-3414 active in `PROJECT-GTKB-RELIABILITY-FIXES` | live MemBase |
| `GOV-RELIABILITY-FAST-LANE-001` | `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-3414 by membership. | active PAUTH; WI-3414 covered | live MemBase |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge thread + tests + state files form a durable governed graph | append-only bridge versions | bridge thread |

## Risks

1. **session_id availability at trigger pre-spawn time.** The trigger is invoked by PostToolUse/Stop hooks; it has a session context. The trigger generates a synthetic `session_id = "trigger-dispatched-<spawn_id>"` to mark the holder. The spawned worker reads this from the inherited env var `GTKB_INHERITED_SESSION_ID` and renews. If the worker fails to receive the env var (subprocess env injection failure), it would acquire under its own session_id, fail the same-session passthrough, and exit with a clear error. Acceptable fail-closed behavior.

2. **AXIS-2 surface render performance.** Reading per-entry `current_holder` adds N file reads to render (one per actionable entry, up to ~50 in practice). Each read is a single small JSON parse. Expected sub-100ms overhead; if this proves measurable, the surface can batch-read all `.gtkb-state/work-intent/*.json` files in one directory scan.

3. **TTL choice in helper Integration Point 3.** 5-minute TTL covers most drafting windows but could expire mid-draft for very long sessions. Same-session re-`acquire` extends TTL (per the registry's same-session passthrough). If a future telemetry pass shows actual drafting windows commonly exceed 5 min, a tuning REVISED can adjust.

4. **Coordination with quiesce window (WI-3280, VERIFIED).** The quiesce window coalesces close-spaced INDEX edits before the trigger evaluates dispatch. The new pre-spawn `acquire` happens AFTER quiesce decision-time, on the actual dispatch syscall. They compose cleanly; the post-impl test plan includes a coexistence regression.

5. **State directory permissions on Windows.** `.gtkb-state/work-intent/` requires write permission for the running user. The registry foundation (WI-3274 VERIFIED) already established this works on Windows; no new permission concerns.

6. **Template upgrade behavior for adopters.** `upgrade_policy = "overwrite"` for both managed-artifacts entries means adopters who run `gt project upgrade` after this lands receive the new behavior. Adopters with `adopter_divergence_policy = "warn"` will see a warning if they've locally modified the helper or hook; they can opt out of the upgrade per artifact.

## Rollback

Each of the 4 integration boundaries is independently revertable. Partial rollback (e.g., revert 1 and 2 but keep 3 and 4) is consistent — the system falls back to the original write-boundary safety with no regression vs `-001`'s shipped behavior.

No `groundtruth.db` mutations are made by this proposal. WI-3414 was created via the `python -m groundtruth_kb backlog add` CLI before filing `-001`; project membership and the doubled-prefix fix were applied via `db.link_project_work_item(...)` as one-shot governance-hygiene operations outside target_paths scope.

## Loyal Opposition Asks

1. Verify the defense-in-depth narrative actually closes P1-001's race surface — i.e., that boundaries 1 + 2 acting together prevent the duplicate-drafting scenario observed in S365 (not just the duplicate-Write scenario).
2. Confirm all template counterparts are correctly listed in target_paths and the corresponding managed-artifacts.toml entries match (`hook.bridge-compliance-gate` at line 119-129; `skill.bridge-propose.helper` at line 508-519).
3. Verify the trigger's synthetic `session_id = "trigger-dispatched-<spawn_id>"` semantic is compatible with the registry's same-session passthrough rule — that the worker can renew under an inherited session_id.
4. Consider whether the AXIS-2 surface should also OPTIONALLY acquire on behalf of the interactive session (e.g., via an explicit user opt-in like `claim <slug>`). If yes, that becomes Slice 2 follow-on; if not, the surface remains read-only as proposed here.
5. Issue GO if findings 1-3 hold; or NO-GO with specific revision asks.

## Opportunity Radar

Beyond the proposed Slice 1 scope, future work could:

- Add a `gt bridge holders` CLI surface for owner visibility of current work-intent records.
- Extend the registry to `(slug, version)` tuples so two sessions can legitimately work on different versions of the same thread (one revising `-009`, another reviewing `-008`).
- Add the bridge-stop-drain hook integration (currently retired in S350+ but pattern could recur).

These are out of scope for this Slice 1 proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
