WITHDRAWN

# Withdrawn - Duplicate of gtkb-bridge-thread-read-cli (WI-4634)

bridge_kind: prime_proposal
Document: gtkb-bridge-thread-read-cli-commands
Version: 002
Responds-To: bridge/gtkb-bridge-thread-read-cli-commands-001.md
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4634

## Withdrawal

This proposal is WITHDRAWN as a concurrent duplicate of `gtkb-bridge-thread-read-cli`
(filed ~19 minutes later, 2026-06-18T03:43Z) for the same work item WI-4634. Both
proposals add `gt bridge show` and `gt bridge threads --wi` read commands and overlap
on `groundtruth-kb/src/groundtruth_kb/cli.py`.

Per owner decision (AskUserQuestion 2026-06-18, recorded as
`DELIB-20260618-WI4634-DUP-KEEP-MINE-WITHDRAW-CODEX`), the surviving proposal is
`gtkb-bridge-thread-read-cli`. It carries a metadata-precise WI->thread mapping
(matches the `Work Item:` metadata line rather than body-text substring, avoiding
false positives), an honest thread-level coverage caveat, and
adversarial-verification-derived edge-case tests. This withdrawal is owner-directed
and is the terminal version of this thread; WI-4634 is covered by the surviving
thread. No code from this proposal was implemented.

## Owner Decisions / Input

- AskUserQuestion 2026-06-18: "Keep mine, withdraw Codex's" -> withdraw this thread
  as the duplicate. Recorded as `DELIB-20260618-WI4634-DUP-KEEP-MINE-WITHDRAW-CODEX`.

## Root Cause (concurrency)

Two Prime Builder sessions (Codex keep-working automation, harness A; interactive
Claude, harness B) independently selected WI-4634 and filed under DIFFERENT slugs,
so the slug-keyed work-intent claim could not prevent the duplicate. Evidence for
WI-4378 (guard duplicate same-role loops on one project). The surviving
`gt bridge threads --wi` command would itself have surfaced this cross-slug
duplicate by work item.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
