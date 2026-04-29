GO

# Loyal Opposition Re-Review - GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md`
Scope: REVISED-3 proposal for notification-based smart poller
Verdict: GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P3 notify current-state schema no-backfill review"
```

Relevant context:

- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`: owner redirected the smart-poller objective from spawning to notification.
- `DELIB-0492`: bridge architecture audit context.
- `DELIB-0121`: bridge ops / reporting proposal using Codex automations.
- `DELIB-0101`: bridge poller staleness and wake churn review.
- Prior bridge response `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-006.md`: NO-GO because `-005` fixed the current-state algorithm but left inherited no-backfill / transition-shaped contracts active.

## Claim

GO. `-007` resolves the two proposal-level contradictions that blocked `-005`:

1. It explicitly selects Option A, true current-state notification semantics.
2. It replaces the transition-shaped v1 artifact with schema v2 `pending_actions[]`.

The combined `-001 + -003 + -005 + -007` proposal is coherent enough for Prime Builder implementation.

## Evidence

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md:9-14` explicitly supersedes the inherited `-001` subsections that conflicted with the corrected `-005` algorithm.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md:26-40` defines bootstrap as silent on iteration 1, then current-state notification computation on iteration 2 onward, including pre-existing actionable entries.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md:48-56` makes the Option A over Option B decision explicit and gives a reasonable operational rationale.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md:64-128` defines schema v2, `pending_actions[]`, `top_status`, `top_file`, `index_line_number`, reader expectations, and no v1 compatibility shim.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md:136-150` updates LC1-LC10 field assertions and adds LC11-LC15 for schema v2 plus bootstrap/current-state behavior.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md:157-170` preserves the previously confirmed closures: VERIFIED suppression, file-absent empty-state semantics, missing-file exclusion, no-subprocess/no-spawn/no-OS-scheduled-task invariants, and hardcoded routing sets.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:38`, `:111`, `:132`, `:168`, and `:188` show the original no-backfill / transition-shaped statements that caused the `-006` NO-GO. `-007` now directly supersedes those statements.

## Review Answers

1. Option A explicitness: acceptable. The iteration-1 bootstrap / iteration-2 current-state split is clear and handles first install on a populated INDEX without silently losing pending work.
2. Option A vs Option B: acceptable. Option B would add recipient-specific persistence state without a demonstrated benefit for the owner-facing "pending bridge action" model.
3. Schema v2 shape: acceptable. `pending_actions[]` with `document_name`, `top_status`, `top_file`, and `index_line_number` is the right shape for current-state notification consumption. Transition history belongs in audit logs, not in the pending-action artifact.
4. Test coverage: acceptable for proposal approval. LC11-LC15 directly pin schema v2 and bootstrap/current-state behavior. LC1-LC4 continue to cover persistence, routing, and VERIFIED/file-absent clearing.
5. Prior closures: no regression found in the proposal text. The implementation still needs to prove these with tests and code inspection.
6. Internal contradictions: the supersession list and section 1.2 remove the inherited inconsistencies that caused `-006`.

## Implementation Watchpoints

- Do not compute notification contents from checkpoint diffs. The checkpoint is audit/bootstrap support only.
- Do not emit or read `pending_transitions`, `from_status`, or `from_file`.
- Preserve file-absent semantics for no pending action; avoid writing empty pending-action artifacts unless a test explicitly requires that behavior.
- Keep `VERIFIED` non-actionable for both Prime and Codex. Prime-actionable top statuses remain `GO` and `NO-GO`; Codex-actionable top statuses remain `NEW` and `REVISED`.
- Preserve INDEX order in notification payloads unless a later proposal explicitly changes queue ordering.

## Risk / Impact

The main implementation risk is accidental reintroduction of transition semantics through old variable names, stale tests, or reader assumptions. The revised acceptance criteria are strong enough to catch that if implemented literally.

## Recommended Action

Prime Builder may implement P3 notify using the combined proposal:

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md`
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-003.md`
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md`
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md`

## Decision Needed From Owner

None.
