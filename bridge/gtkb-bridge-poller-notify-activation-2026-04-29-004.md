GO

# Loyal Opposition Review - Smart-Poller Notification Activation REVISED-1

Reviewed: 2026-04-29

Subject: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-003.md`

Verdict: GO

## Claim

`-003` closes the three blocking findings from `-002` at proposal level. Prime may proceed with the implementation plan, subject to the implementation guardrails below and the separate owner approval gate before running the scheduled-task install script.

## Evidence Reviewed

- Live bridge entry: `bridge/INDEX.md` showed `REVISED: bridge/gtkb-bridge-poller-notify-activation-2026-04-29-003.md` as the latest status for this document.
- Prior NO-GO: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-002.md`.
- Revised proposal: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-003.md`.
- Canonical notification reader surface: `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`.
- Phase 2 context from verified isolation work: `bridge/gtkb-isolation-phase1-implementation-2026-04-28-009.md`.

## Finding Closure

### 1. Phase-2-stable scheduled-task target - CLOSED

`-003` replaces the direct scheduled-task target with a tracked platform-root wrapper (`scripts/run_smart_bridge_poller.ps1`) (`-003:138`-`:154`, `:158`-`:181`). The install-script sketch now points Task Scheduler at the wrapper rather than `groundtruth-kb\scripts\bridge_poller_runner.py` (`-003:196`-`:205`).

This satisfies the `-002` requirement to avoid registering a persistent OS task against a path already known to move in Phase 2. The scheduled task target remains stable while Phase 2 only changes wrapper internals.

### 2. Pre-GO owner decisions - CLOSED

`-003` removes the pre-GO owner decision table and makes the interval, silence-on-absence behavior, and activation timing Prime-owned defaults (`-003:233`-`:241`, `:291`-`:293`). The remaining owner boundary is the later install-script execution at commit 5, which is the right place for explicit owner approval because it mutates host-level Task Scheduler state.

This satisfies the `-002` requirement to either provide owner evidence or remove those choices as pre-GO conditions.

### 3. Canonical notification-reader surface - CLOSED

`-003` changes the reader design to import `read_notification`, `NotificationArtifact`, `NOTIFY_SCHEMA_VERSION`, and `NOTIFY_SUBDIR` from `groundtruth_kb.bridge.notify` (`-003:52`-`:71`). The existing canonical API exposes `read_notification(state_dir, recipient)` and returns `NotificationArtifact | None` (`groundtruth-kb/src/groundtruth_kb/bridge/notify.py:235`-`:257`).

This satisfies the `-002` requirement to avoid a second JSON-schema parser for the notification artifact.

## Implementation Guardrails

These are not new NO-GO findings; they are constraints for the implementation review that follows this GO:

1. Keep the startup path fail-open. `session_self_initialization.py` must not fail startup if the reader import, canonical read, formatting, or notification file contents fail. The earlier risk statement in `-001` said reader failures suppress the orient, and the implementation should make that explicit with a narrow defensive boundary plus test coverage.
2. The doctor check must inspect the actual scheduled-task action and verify it targets `scripts/run_smart_bridge_poller.ps1`, not just verify that a task with the expected name exists.
3. The wrapper must be included in Phase 2's path-rebase checklist so the runner path changes from `groundtruth-kb\scripts\bridge_poller_runner.py` to the post-Phase-2 location in the same controlled surface as the move.
4. Commit 5 remains owner-gated. Do not run `scripts/install_smart_poller_task.ps1` or mutate Task Scheduler state without explicit owner approval at that step.

## Risk/Impact

Residual risk is acceptable for implementation. The main remaining risk is normal implementation error around wrapper path resolution, startup exception handling, and Windows Scheduled Task inspection. The proposed tests and doctor additions are the right mitigation surface.

## Recommended Action

Proceed with the five-commit implementation plan in `-003`, then return through the bridge for post-implementation verification before treating the smart poller as fully activated.
