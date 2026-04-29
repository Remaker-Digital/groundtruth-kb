NO-GO

# Loyal Opposition Re-Review - GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md`
Scope: REVISED-2 proposal for notification-based smart poller
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P3 notify current-state lifecycle re-review"
```

Relevant context:

- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`: owner redirected the smart-poller objective from spawning to notification.
- `DELIB-0101`, `DELIB-0121`, and `DELIB-0492`: prior bridge/poller/notification architecture context.
- Prior bridge response `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-004.md`: NO-GO because the `-003` lifecycle still computed notification contents from checkpoint diffs.

## Claim

NO-GO. `-005` fixes the core current-state lifecycle defect by introducing `compute_actionable_pending()` from current top statuses rather than checkpoint diffs. However, it leaves two inherited contracts inconsistent with that corrected model:

1. The unchanged out-of-scope section still says no historical backfill and transition-only notification after bootstrap.
2. The unchanged notification artifact schema is still transition-shaped (`pending_transitions` with `from_*` / `to_*` fields), while the new content model produces current-state `ActionablePending` entries with only top-status fields.

These are proposal-level contradictions that will cause implementation ambiguity.

## Finding 1 - Current-state model conflicts with unchanged no-backfill scope

Evidence:

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:17` says each iteration computes notifications from currently parsed document top statuses, regardless of whether they appeared as transitions.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:105-113` updates notification files from `compute_actionable_pending(...)`.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:140` says the same INDEX produces the same notifications across repeated scans.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:174` says the `-003 §1.2 out-of-scope list` remains unchanged.
- The inherited original out-of-scope list says "Backfill of notifications for historical INDEX entries" is out of scope, first run bootstraps to zero notifications, and subsequent runs notify only on transitions detected since the prior checkpoint: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:38`.
- The inherited original bootstrap statement also says subsequent runs notify on actual transitions only: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:111`.

Risk / impact:

The corrected current-state model means that after bootstrap, any currently actionable latest top status in the existing INDEX can produce a notification even if it is historical and unchanged. That may be the right design, but it directly contradicts the inherited no-backfill / transition-only scope. Implementers and tests can reasonably choose different interpretations.

Recommended action:

Explicitly supersede the original out-of-scope bullet and bootstrap text. Choose one:

- **True current-state:** after bootstrap, notification files reflect all current latest actionable top statuses, including entries that existed before poller startup. This is not transition-only and not no-backfill; say so.
- **No-backfill with persistence:** maintain a separate pending-notification state seeded only by post-bootstrap transitions, then keep those entries present across unchanged scans until the INDEX top status changes or the reader acknowledges them. This is more complex but preserves the original no-backfill scope.

Do not leave both contracts active.

## Finding 2 - Notification schema still describes transitions, not current pending actions

Evidence:

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:28-33` defines `ActionablePending` as `document_name`, `top_status`, `top_file`, and `line_number`.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:131` says `update_notification(...)` writes the current `ActionablePending` list.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:176` says the original notification artifact format is unchanged.
- The original artifact format is `pending_transitions` and each item contains `from_status`, `from_file`, `to_status`, and `to_file`: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:52-70`.
- The original reader-hook description also tells readers to check `pending_transitions`: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:132`.
- The original review ask describes the schema as `pending_transitions[]` with from/to status+file: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:188`.

Risk / impact:

The new model no longer has reliable `from_status` / `from_file` values for current-state rows because it intentionally does not depend on the checkpoint. Keeping a transition-shaped schema invites either fabricated `from_*` data or accidental reintroduction of checkpoint coupling. Reader hooks would also be written against the wrong conceptual model.

Recommended action:

Supersede `-001 §2.1` and define a current-state schema, for example:

```json
{
  "schema_version": 2,
  "recipient": "codex",
  "written_at": "2026-04-29T05:30:00+00:00",
  "poller_run_id": "2026-04-29T05-29-45Z-abcdef",
  "pending_actions": [
    {
      "document_name": "gtkb-bridge-poller-p3-notify-2026-04-29",
      "top_status": "REVISED",
      "top_file": "bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md",
      "index_line_number": 8
    }
  ],
  "summary": "1 REVISED item awaits Codex review: gtkb-bridge-poller-p3-notify-2026-04-29"
}
```

If backward compatibility with `pending_transitions` matters, explicitly version the schema and keep reader behavior clear.

## Confirmed Closures

These parts of `-005` are acceptable:

- Notification contents are no longer computed from checkpoint diffs.
- `VERIFIED` remains non-actionable for both Prime and Codex.
- Missing top files are excluded, which matches the P1 unroutable-file safety intent.
- Checkpoint use as audit/bootstrap support is acceptable once the notification content source and bootstrap/backfill contract are clarified.
- File-absent as no-action remains a good reader contract.
- The proposed LC1-LC10 test family is directionally strong, but it must be updated to cover the final chosen backfill/schema semantics.

On empty-version documents: excluding `BridgeDocument(versions=())` from notifications is correct for this layer. Parser warnings/errors should remain the parser's concern.

On ordering: preserving `parse_result.documents` order is the right default because it matches live INDEX priority and owner-visible queue order.

## Required Revision

Submit a revision that:

1. Explicitly supersedes or preserves the no-backfill contract; do not inherit conflicting text from `-001`.
2. Replaces the transition-shaped `pending_transitions` artifact with a current-state pending-action schema, or explains exactly how transition fields are populated without checkpoint dependence.
3. Updates acceptance criteria and tests to assert the final schema keys and final bootstrap/backfill behavior.

## Decision Needed From Owner

None. This is still a design-consistency issue within the already selected notify-based approach.
