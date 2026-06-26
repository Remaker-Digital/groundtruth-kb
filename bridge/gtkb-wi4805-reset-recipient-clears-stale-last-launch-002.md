WITHDRAWN
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e6490e91-a7fd-489d-be63-363714e9ba47
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: prime_proposal
Document: gtkb-wi4805-reset-recipient-clears-stale-last-launch
Version: 002
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4805
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26

## Withdrawal

This proposal (-001, part-1-only: `--reset-recipient` clears the stale `last_launch` failure markers) is WITHDRAWN as a duplicate. A concurrent session (130bf9ae) had already filed a more complete WI-4805 proposal -- `bridge/gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap-001.md` (NEW) -- which covers BOTH part 1 (reset clears stale last_launch + signature) AND part 2 (reap the recipient's hung dispatch-run process), with the same target_paths. I filed -001 without seeing that thread: it was untracked and filed after this session's initial WI-4805 scan (which showed 0 threads). The concurrent superset proposal supersedes this subset; only one canonical WI-4805 thread should proceed to GO.

Carry-forward analysis for the surviving proposal's reviewer/implementer: WI-4805 part 2 (reap of live-but-stale workers before they exit) is reduced-necessity given the now-VERIFIED WI-4845 (worker-lifetime cap kills hung workers -> exit 124) plus WI-4803 (work-intent claim release on that failure). The hung-worker claim leak is already handled at the lifetime cap; an N-min-stale pid-reap is a faster-reap optimization, not a correctness gap. The surviving proposal's reviewer may wish to scope part 2 accordingly.

## Specification Links

(Carried from -001 for gate compliance; this version withdraws the thread rather than proposing implementation.)

- ADR-DISPATCHER-ARCHITECTURE-001 -- dispatcher architecture-of-record; the reset command is part of the dispatch operational contract.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 -- dispatch health must reflect real dispatchability; the stale-FAIL-after-reset defect this thread targeted.
- DCL-DISPATCH-ENVELOPE-RULES-001 -- the recipient-state envelope.
- GOV-FILE-BRIDGE-AUTHORITY-001 -- bridge protocol authority; WITHDRAWN is a terminal status in the append-only versioned chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 -- satisfied: links carried forward.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 -- not applicable to a withdrawal (no implementation proceeds).
- GOV-STANDING-BACKLOG-001 -- WI-4805 is the governing backlog item (continues under the surviving proposal).

## Owner Decisions / Input

- DELIB-20266137 (AskUserQuestion, 2026-06-26) authorizes the dispatcher-reliability Fixes-then-Phases drive including WI-4805. This withdrawal is governance hygiene -- it removes a duplicate this session filed so a single canonical WI-4805 thread (the concurrent superset proposal) proceeds. No owner decision is required to withdraw a self-authored duplicate proposal.
