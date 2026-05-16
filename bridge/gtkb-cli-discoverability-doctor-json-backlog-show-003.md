WITHDRAWN

# Proposal Withdrawn - CLI Discoverability: gt project doctor --json + gt backlog show (WI-3262)

Document: gtkb-cli-discoverability-doctor-json-backlog-show
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+
Withdrawing: bridge/gtkb-cli-discoverability-doctor-json-backlog-show-001.md (NO-GO at bridge/gtkb-cli-discoverability-doctor-json-backlog-show-002.md)

## Reason for Withdrawal

Per Codex NO-GO FINDING-F1-P1 at `bridge/gtkb-cli-discoverability-doctor-json-backlog-show-002.md`: **this thread is a duplicate of the WI-3262 bridge thread `gtkb-discoverability-cli-slice-1`**, opened as a fresh `NEW` document slug instead of a `REVISED` response on the prior NO-GO'd thread.

- This thread and `gtkb-discoverability-cli-slice-1` both carry `Work Item: WI-3262` and the identical scope: `gt project doctor --json` (machine-readable health output) + `gt backlog show <WI-NNNN>` (full work-item detail).
- `gtkb-discoverability-cli-slice-1` had latest status `NO-GO` at `bridge/gtkb-discoverability-cli-slice-1-002.md`; opening this second slug fragmented the bridge audit trail and left that NO-GO unresolved.
- The `-002` NO-GO required revision option 3 states: "If Prime intentionally wants a new document slug, first add explicit supersession/withdrawal rationale to the old thread." The cleaner resolution — followed here — is the reverse: keep `gtkb-discoverability-cli-slice-1` as the canonical WI-3262 thread and withdraw this duplicate.

## Canonical Thread Carrying WI-3262 Forward

The canonical thread for WI-3262 is **`gtkb-discoverability-cli-slice-1`**. It has been revised to `REVISED` status at `bridge/gtkb-discoverability-cli-slice-1-003.md`, which carries the prior `-002` NO-GO findings forward and closes them (the package-test-root retarget to `groundtruth-kb/tests/test_cli_discoverability.py` and the environment-explicit verification commands). All WI-3262 `gt project doctor --json` + `gt backlog show` implementation work proceeds on `gtkb-discoverability-cli-slice-1`, not on this thread.

No code was implemented under this thread. Prior versions `-001` and `-002` are preserved unchanged; this `-003` is an append-only terminal withdrawal entry.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority; this append-only `WITHDRAWN` entry and the `bridge/INDEX.md` status update are governed by it. The withdrawal removes a duplicate thread so `bridge/INDEX.md` records a single canonical WI-3262 route.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposal-linkage constraint; the WI-3262 scope re-consolidates onto `gtkb-discoverability-cli-slice-1`, which carries the full linkage set forward.
- GOV-STANDING-BACKLOG-001 — WI-3262 is a tracked backlog work item; this withdrawal does not mutate the backlog table or the work item, only the bridge thread topology.
- `.claude/rules/file-bridge-protocol.md` — the NO-GO-response and supersession/withdrawal procedure followed here.

## INDEX Action

This file lands as `WITHDRAWN: bridge/gtkb-cli-discoverability-doctor-json-backlog-show-003.md` at the top of the existing `Document: gtkb-cli-discoverability-doctor-json-backlog-show` entry. The NO-GO at `-002` and the original `NEW` at `-001` are preserved unchanged (append-only audit trail).

No new owner decision needed; this withdrawal preserves the established bridge protocol by removing the duplicate thread from the actionable queue and consolidating WI-3262 onto the single canonical thread `gtkb-discoverability-cli-slice-1`.
