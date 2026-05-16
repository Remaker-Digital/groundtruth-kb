WITHDRAWN

# Bridge Thread Withdrawal — Startup Disclosure Relay Truncation Fix

Document: gtkb-startup-disclosure-relay-truncation-fix
Version: 003
Withdraws: bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md (GO at bridge/gtkb-startup-disclosure-relay-truncation-fix-002.md)
Author: Prime Builder (claude / harness B)
Date: 2026-05-15 (S353)

## Withdrawal

This thread is withdrawn by Prime Builder.

The `-001` implementation proposal received a valid Codex GO at `-002`, but its
`target_paths` were written as a human-readable `### target_paths` subsection
that `scripts/implementation_authorization.py` cannot parse — no
implementation-start authorization packet could be created from the GO. Bridge
files are append-only and `REVISED` is a post-`NO-GO` state, so the GO'd thread
could not be corrected in place.

The work is re-filed, with machine-readable `target_paths:` JSON metadata, as
the thread `gtkb-startup-relay-truncation-fix-refile`. The technical scope and
every `-002` GO implementation condition carry forward unchanged to that
thread.

Per owner decision (AskUserQuestion, 2026-05-15) this withdrawal closes the
original thread so a single same-work-item implementation route remains.
`WI-3323`'s `related_bridge_threads` field points to
`gtkb-startup-relay-truncation-fix-refile`.

No code was implemented under this thread. Prior versions `-001` and `-002`
are preserved unchanged; this `-003` is an append-only terminal withdrawal
entry.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority; this append-only `WITHDRAWN` entry and the `bridge/INDEX.md` status update are governed by it.
- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 — the governing constraint for the withdrawn thread's subject; the work re-files under `gtkb-startup-relay-truncation-fix-refile`, which carries this linkage forward.

## Prior Deliberations

- DELIB-2078 — owner approval for the init-keyword startup-disclosure-relay specification; the withdrawn thread and its re-file both implement that approved relay constraint.

## Owner Decisions / Input

This withdrawal is authorized by the AskUserQuestion decision captured this
session (2026-05-15, S353): the owner selected "Re-file as a new bridge thread"
for the blocked relay fix, which entails closing the original thread. The
re-file thread `gtkb-startup-relay-truncation-fix-refile` carries the work
forward.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
