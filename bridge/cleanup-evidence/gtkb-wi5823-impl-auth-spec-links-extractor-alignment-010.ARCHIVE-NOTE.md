# Archive note — orphan terminal VERIFIED, gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8038611d-3a31-49fb-ad15-9f00b0ef3d25
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope

Archived: 2026-08-07 UTC
Authority: bridge/gtkb-wi5823-stranded-finalization-verdict-reissue-004.md (GO)
Work Item: WI-5823
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730

## What was archived

`bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010.md` — a terminal
`VERIFIED` verdict that was written **without** its atomic finalization commit,
contrary to the Mandatory VERIFIED Commit-Finalization Gate.

The file was **untracked** at archive time, so it had never entered the git audit
trail and nothing is removed from history by this relocation. The tracked chain
`-001` through `-008` is untouched and byte-identical.

## Why it was archived

Terminal `VERIFIED` closed the thread's implementation phase, which made the
finalization commit that `VERIFIED` was supposed to accompany impossible:

- `scripts/check_protected_commit_authorization.py` refused the thread's
  authorization packet — *"Bridge thread is VERIFIED (terminal at
  bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010.md); the
  implementation phase for this proposal is closed."*
- `scripts/per_thread_finalization_repair.py` classified the thread
  `terminal_verified_blocked_dirty_targets` with `stop: true`.
- The transaction-local `VERIFIED` route failed on two defects in this verdict
  body: its same-transaction manifest declared all 13 chain paths including the
  already-committed `-001`..`-008`, making staged-set equality unsatisfiable; and
  its recorded applicability `packet_hash` (`sha256:b6ebd791…`) was stale against
  the gate-expected `sha256:3a80a320…`.

Archiving it returns the thread's latest status to `-009` (`NEW`, the
implementation report) — the ordinary Loyal-Opposition-actionable state — so a
helper-created finalization can proceed normally.

## What happens next

Per the GO'd sequence, ordering is load-bearing:

1. Archive `-010` (this note records that step).
2. Commit the untracked `-009` predecessor, so the chain is committed and
   `write_verdict.py --finalize-verified` does not strand at the
   predecessor-chain gate.
3. Loyal Opposition reissues `VERIFIED` through
   `write_verdict.py --finalize-verified`, creating the atomic commit containing
   the verified implementation paths plus the new verdict.

Step 2 cannot precede step 1: committing `-009` while `-010` was still terminal
would re-trigger the same "implementation phase is closed" refusal.

## Preserved, not deleted

This verdict is retained verbatim for audit. It is evidence of the stranded
state and of the two body defects above, both of which are captured as backlog
work (WI-6005 covers the unsatisfiable manifest; WI-5995 covers the
self-invalidating-authorization class this instance belongs to).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
