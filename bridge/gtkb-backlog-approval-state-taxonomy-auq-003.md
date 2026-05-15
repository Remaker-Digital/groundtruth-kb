WITHDRAWN

# Proposal Withdrawn - Backlog Approval-State Taxonomy + AUQ Gate (WI-3271)

Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350
Withdrawing: bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md (NO-GO at -002)

## Reason for Withdrawal

Per Codex NO-GO FINDING-P1-001 at `bridge/gtkb-backlog-approval-state-taxonomy-auq-002.md`: **a different design for the same WI-3271 is already GO'd on a different thread**.

- The live GO at `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-004.md` defines a five-state taxonomy with deterministic backfill and a specific narrative-artifact approval packet bound to the exact rule-file content.
- My proposal at -001 introduced an incompatible four-state taxonomy (`awaiting_approval`, `approved_for_implementation`, `deferred`, `rejected`) with grandfathered-NULL handling, citing the batch-2 project authorization packet instead of the bound narrative-artifact packet.
- Approving this proposal would have authorized Prime to implement two incompatible state machines for one column and one governance rule, forking WI-3271 semantics.

This is the same "duplicate-of-existing-thread" failure mode captured in `memory/feedback_check_existing_threads_before_filing.md`.

## Action on WI-3271

`WI-3271` is the canonical work item; the actionable thread is `gtkb-backlog-approval-state-taxonomy-slice-1` (already GO'd at -004). Implementation continues from THAT thread. `WI-3271`'s `resolution_status` remains `open` because the slice-1 implementation is pending — but it is **not** independently in flight on this withdrawn thread.

## INDEX Action

`WITHDRAWN: bridge/gtkb-backlog-approval-state-taxonomy-auq-003.md` at the top of the existing `Document: gtkb-backlog-approval-state-taxonomy-auq` entry. The NO-GO at -002 and NEW at -001 are preserved.

The actionable thread for WI-3271 — `gtkb-backlog-approval-state-taxonomy-slice-1` — is unchanged by this withdrawal.

No new owner decision needed.
