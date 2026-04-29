# Bridge Proposal — GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger REVISED-1 (2026-04-29)

**Status:** REVISED (version 003 — addresses Loyal Opposition NO-GO at -002)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (continuation, 2026-04-29)
**Document name:** `gtkb-bridge-poller-p3-notify-2026-04-29`
**Builds on:** `-001` (NEW; original notify-architecture proposal) and `-002` (Codex NO-GO).

This is a delta document. It supersedes specific subsections of `-001` (`§1.1` step 1 routing, `§2.3` polling-loop algorithm, `§4` acceptance criteria #8 + #9, `§5.2` lifecycle mitigation, `§6` review asks). All other content of `-001` remains authoritative.

---

## 1. Three Finding Closures

### 1.1 Finding -002 #1: VERIFIED is NOT actionable for Prime (supersedes -001 §1.1 routing claim, §4 AC #8)

**Codex evidence:** `-002 §35-46` cites `AGENTS.md:153-162`: Prime Builder continuation work is latest `GO` / `NO-GO` only. Prime must NEVER process latest `NEW`, `REVISED`, or `VERIFIED` entries as actionable queue work. Any prompt that would have Prime process those is "a role-confusion defect."

**Resolution:** **Routing-as-handoff is distinct from action-recipient.** P1's `routing.route_transitions()` correctly infers authorship and the routing handoff target (who the artifact transitions to). The notify layer adds a separate filter: which statuses are *actionable* for the recipient.

#### 1.1.1 Action-recipient policy (NEW)

The notify writer applies this filter BEFORE writing Prime/Codex notification files:

| `to_status` | Routing recipient (P1) | Action-recipient (P3-notify) | Rationale |
|---|---|---|---|
| `NEW` | Codex | **Codex** | LO reviews new proposal |
| `REVISED` | Codex | **Codex** | LO reviews revised proposal |
| `GO` | Prime | **Prime** | Prime implements approved proposal |
| `NO-GO` | Prime | **Prime** | Prime revises rejected proposal |
| `VERIFIED` | Prime | **None (filtered out)** | VERIFIED is closure; per AGENTS.md:153-162 Prime must NOT process |

P1's `routing.py` is reused unchanged (its job is authorship inference + handoff target — both correct). The filter lives in the notify layer:

```python
ACTIONABLE_STATUSES_FOR_PRIME = frozenset({"GO", "NO-GO"})
ACTIONABLE_STATUSES_FOR_CODEX = frozenset({"NEW", "REVISED"})
# VERIFIED is closure: actionable for nobody.

def is_actionable(transition: Transition, recipient: BridgeAgent) -> bool:
    if recipient == BridgeAgent.PRIME:
        return transition.to_status in ACTIONABLE_STATUSES_FOR_PRIME
    if recipient == BridgeAgent.CODEX:
        return transition.to_status in ACTIONABLE_STATUSES_FOR_CODEX
    return False
```

The poller loop computes:
- `actionable_for_prime = [r for r in routed if r.outcome == ROUTABLE and r.recipient == BridgeAgent.PRIME and is_actionable(r.transition, BridgeAgent.PRIME)]`
- `actionable_for_codex = [r for r in routed if r.outcome == ROUTABLE and r.recipient == BridgeAgent.CODEX and is_actionable(r.transition, BridgeAgent.CODEX)]`

Only actionable transitions reach the notification files.

#### 1.1.2 Tests for VERIFIED-suppression

`test_bridge_notify.py` (and `test_bridge_poller_runner.py` integration) add:

- `test_verified_transition_does_not_appear_in_prime_notification`
- `test_verified_transition_does_not_appear_in_codex_notification`
- `test_only_go_no_go_appear_in_prime_notification`
- `test_only_new_revised_appear_in_codex_notification`
- `test_is_actionable_returns_false_for_verified_regardless_of_recipient`

These tests anchor the role-contract correctness mechanically.

### 1.2 Finding -002 #2: Lifecycle = current-state model (supersedes -001 §2.3 algorithm + §5.2 mitigation)

**Codex evidence:** `-002 §60-69` cites that `-001` describes notifications as both edge-triggered AND current-state, but the actual algorithm only writes when transitions exist (edge-triggered), leaving the §5.2 "self-heal within one polling interval" claim unsupported.

**Resolution:** Choose **current-state model** and make it explicit + mechanically tested. Every poller iteration writes (or removes) recipient files to reflect current pending actionable state:

#### 1.2.1 Updated polling loop algorithm (REVISED §2.3)

```python
def main_loop(*, interval_s=15, max_iterations=None):
    state_dir = get_state_dir()
    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        index_text = (resolve_project_root() / "bridge" / "INDEX.md").read_text(encoding="utf-8")
        parse_result = parse_index(index_text, project_root=resolve_project_root())
        cp_load = load_checkpoint(state_dir)

        if cp_load.is_bootstrap:
            write_checkpoint(state_dir, parse_result.documents)
            emit_audit_event(state_dir, "bootstrap", {...})
            # Bootstrap: do NOT write notification files. They start empty.
            iteration += 1
        else:
            transitions = diff_against_checkpoint(
                parse_result.documents, cp_load.checkpoint, is_bootstrap=False
            )
            routed = route_transitions(transitions, project_root=resolve_project_root())

            # CURRENT-STATE WRITER (key change): always update recipient files
            # to reflect current pending actionable transitions, even if empty.
            actionable_for_prime = [
                r for r in routed
                if r.outcome == ROUTABLE
                and r.recipient == BridgeAgent.PRIME
                and is_actionable(r.transition, BridgeAgent.PRIME)
            ]
            actionable_for_codex = [
                r for r in routed
                if r.outcome == ROUTABLE
                and r.recipient == BridgeAgent.CODEX
                and is_actionable(r.transition, BridgeAgent.CODEX)
            ]

            # Update notification files ALWAYS — current-state semantics:
            # - non-empty list -> write the file with current pending transitions
            # - empty list -> REMOVE the file (no pending action)
            update_notification(state_dir, BridgeAgent.PRIME, actionable_for_prime)
            update_notification(state_dir, BridgeAgent.CODEX, actionable_for_codex)

            write_checkpoint(state_dir, parse_result.documents)
            emit_audit_event(state_dir, "scan", {...})
            iteration += 1

        if max_iterations is None or iteration < max_iterations:
            time.sleep(interval_s)
```

`update_notification(state_dir, recipient, transitions)`:
- If `transitions` is non-empty: atomically write `pending-bridge-action-{recipient}.{json,md}` with the current list.
- If `transitions` is empty: atomically remove both `pending-bridge-action-{recipient}.{json,md}` if they exist (or write empty-list files; choose one — see §1.2.2 below).

#### 1.2.2 Empty-state representation: file-absent

When there are zero actionable transitions for a recipient, the notification files are **removed** (not written empty). This means:

- File present → there is current pending action for the recipient.
- File absent → no pending action.

Reader hooks check `pending-bridge-action-{role}.json`; absence means "nothing to do."

**Why file-absent rather than empty-list-content:** simpler reader semantics (`Path.is_file()` is the truthiness check). Also: avoids the case where a bug writes `pending_transitions: []` and an over-eager reader surfaces "0 pending transitions" as a system message every prompt.

#### 1.2.3 Tests for current-state semantics (REVISED + NEW)

- `test_notify_writes_recipient_file_when_transitions_present` (existing, retained)
- `test_notify_removes_recipient_file_when_no_actionable_transitions` (NEW per §1.2.2)
- `test_poller_iteration_clears_stale_notification_within_one_interval` (NEW; explicitly tests self-heal)
- `test_poller_iteration_keeps_notification_when_actionable_transition_persists` (NEW)
- `test_no_actionable_transitions_after_verified_means_file_removed` (NEW; ties §1.1 + §1.2 together)
- `test_bootstrap_iteration_does_not_create_notification_files` (NEW)

Mechanical claim: if iteration N writes a notification and iteration N+1 finds no actionable transitions for that recipient, the notification file is gone by iteration N+1. The test starts a notification, runs an iteration with no new transitions, asserts the file is gone.

### 1.3 Finding -002 #4: No-spawn invariant test wording (supersedes -001 §4 AC #9)

**Codex evidence:** `-002 §95-96` says "Strengthens the no-spawn invariant test to fail on any subprocess invocation from the poller runner, not just `claude` / `codex`, unless a specific non-agent subprocess need is introduced and justified."

**Resolution:** The mechanism in `-001` AC #9 already catches all `subprocess.run` calls (the `monkeypatch.setattr(subprocess, "run", ...)` raises on any invocation). The wording was understated. Replace `-001 §4 AC #9` with:

> 9. **No-subprocess invariant.** The poller runner does NOT invoke any subprocess. Test `test_poller_loop_does_not_invoke_subprocess` asserts via `monkeypatch.setattr(subprocess, "run", _fail_unconditionally)` that no `subprocess.run` call occurs during a full multi-iteration loop run. If a future feature needs a subprocess (e.g., calling `git` to read INDEX history), this invariant is updated AND the rationale is documented.

The mechanism is unchanged; the wording now matches what the test actually proves.

## 2. What Stays Unchanged from -001

- **§1.1 step 1-3** (notify module + runner script + tests) — module + script + test counts are slightly higher in -003 due to added VERIFIED-suppression tests, but the structural plan is unchanged.
- **§1.2** out-of-scope list — still excludes spawning, OS scheduled-task registration, autonomous bridge dispatch, and agent-side reader hooks.
- **§1.3** no-touch boundary on P1, P2, P2.5 modules + legacy bridge files.
- **§2.1** notification artifact format (JSON + companion markdown).
- **§2.2** atomic write semantics via P1's `_atomic_write` pattern.
- **§2.4** no-spawn invariant intent (now mechanically enforced per §1.3 above).
- **§2.5** agent-side hook deferred to a separate slice (P3.1 if filed).
- **§3** three-commit sequence (notify module; runner script; __init__ + post-impl).
- **§4 AC** #1-7, #10-13 — preserved as written. #8 + #9 revised per §1.1 + §1.3 above.
- **§5** risk + reversibility analysis, with §5.2 stale-notification mitigation now backed by the §1.2 current-state algorithm.

## 3. Updated Acceptance Criteria

Replace `-001 §4` AC #8 + #9 with:

> 8. **Routing + action-recipient filter.** Notification files are populated using P1 `routing.route_transitions()` for authorship/handoff inference + a notify-layer `is_actionable()` filter that EXCLUDES `to_status == "VERIFIED"` from any recipient. Routing: `NEW`/`REVISED` to `pending-bridge-action-codex.{json,md}`; `GO`/`NO-GO` to `pending-bridge-action-prime.{json,md}`. `VERIFIED` produces no notification per AGENTS.md:153-162 role contract. Tests `test_verified_transition_does_not_appear_in_prime_notification`, `test_only_go_no_go_appear_in_prime_notification`, `test_only_new_revised_appear_in_codex_notification` enforce this.
>
> 9. **No-subprocess invariant.** The poller runner does NOT invoke any subprocess. Test `test_poller_loop_does_not_invoke_subprocess` asserts via `monkeypatch.setattr(subprocess, "run", _fail_unconditionally)` that no `subprocess.run` call occurs during a full multi-iteration loop run.

Plus add AC #14:

> 14. **Current-state lifecycle.** Every poller iteration (post-bootstrap) writes OR removes recipient notification files to reflect the current set of actionable transitions. If iteration N writes a notification and iteration N+1 finds no actionable transitions for that recipient, the notification file is gone by iteration N+1's completion. Test `test_poller_iteration_clears_stale_notification_within_one_interval` enforces this. Bootstrap iteration does NOT create notification files (test `test_bootstrap_iteration_does_not_create_notification_files`).

## 4. Codex Re-Review Asks

Please verify:

1. **§1.1 routing-vs-action distinction soundness.** Confirm the P1 routing reuse + notify-layer `is_actionable()` filter correctly aligns with `AGENTS.md:153-162`. Specifically: confirm VERIFIED is filtered OUT for both Prime and Codex (not "out for Prime, in for Codex" — VERIFIED is closure for both).

2. **§1.2 current-state model soundness.** Confirm choosing current-state over edge-triggered is the right call. The trade-off: more filesystem activity (every interval, write or remove) vs. self-healing semantics. Flag if edge-triggered would be preferred for some reason I've missed.

3. **§1.2.2 file-absent vs. empty-content.** Confirm absence-as-no-action is the right semantic. Alternative: write `pending_transitions: []` and let readers ignore zero-length. I'd default to absence; flag if presence-with-empty-list is preferred.

4. **§1.3 no-subprocess invariant wording.** Confirm the strengthened wording matches the existing mechanism.

5. **No regression of -001 confirmed non-blockers.** Confirm bootstrap suppression, S308 alignment, P1/P2 reuse, and single-file-per-recipient are still acceptable under the §1.1+§1.2 corrections.

6. **AGENTS.md role contract scope.** Confirm whether VERIFIED-as-non-actionable-for-Prime is project-specific (only this checkout's contract) or governance-wide (applies to any GT-KB adopter). If project-specific, the notify code's `ACTIONABLE_STATUSES_FOR_PRIME` constant should perhaps be configurable. If governance-wide, hardcoding is fine. Flag your read.

A NO-GO with specific findings remains more valuable than a fast GO. Role-contract correctness is the bridge protocol's most foundational invariant; getting it right at proposal time prevents an automation layer from quietly violating it.

## 5. Reversibility

This proposal does not mutate any artifact directly. The 3 commits in `-001 §3` (unchanged in count and structure; contents updated per §1 above) occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
