# Loyal Opposition Insight — WI-4837 Post-VERIFIED Finalization Recovery: Owner-Gated Dispatch Loop

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001
WIs: WI-4837 (also relevant: WI-4992 systemic dispatch-suppression tracker)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T23-28-44Z-loyal-opposition-B-9ae5d1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition
author_metadata_source: dispatcher-auto-dispatch
Date: 2026-07-05 UTC

---

## Summary

I was auto-dispatched to review `bridge/gtkb-wi4837-post-verified-finalization-recovery-005.md` (REVISED). After reading the full 5-version chain and verifying canonical state, I determined the correct Loyal Opposition action is **record-and-stop without filing a fresh bridge verdict**. I did NOT file a `-006` GO/NO-GO. Rationale below. The thread is blocked on an owner policy decision (F3) that no headless worker can make, and any Prime-actionable verdict would only perpetuate a token-costly, owner-gated dispatch loop.

This insight is the durable record of that determination; it does not touch the bridge chain (no loop-fuel) and does not ask the owner anything in prose (headless worker; AUQ-only + owner-decision-tracker discipline).

## Thread state (verified canonical)

`gt bridge show gtkb-wi4837-post-verified-finalization-recovery --json` version chain (latest first):

| Ver | Status | Author | Substance |
| --- | --- | --- | --- |
| 005 | REVISED | Prime (Codex A) | Re-records the F3 owner-decision blocker; explicitly NOT a corrected implementation proposal |
| 004 | NO-GO | LO (Antigravity C) | Confirms the F3 blocker; prohibits implementation |
| 003 | NO-ACTION | Prime (Codex A) | Records the F3 blocker; headless worker cannot collect owner input |
| 002 | NO-GO | LO (Claude B, different session) | Raises F3 (requirement disambiguation) + F1/F2/F4/F5 |
| 001 | NEW | Prime (Codex A) | Original proposal: post-VERIFIED finalization-recovery auth mode |

`latest_status: REVISED`, `latest_path: -005`. Confirmed live.

## Blocker liveness (verified — not trusting the artifact's assertion)

1. **F3 owner policy decision is genuinely undecided.** `gt deliberations search` returned no match for the policy question under two wordings ("...owner waiver automatic parity per-instance gate" and "post-VERIFIED finalization gate parity terminal verified target_paths git add"). The live pending-owner-decision set is also empty (UserPromptSubmit hook). F3 = choose one evidence bar and apply it symmetrically across both finalization gates:
   - `automatic parity`: allow `git add`/finalization for terminal-`VERIFIED` paths inside the approved proposal `target_paths` (matching the pre-commit gate), OR
   - `per-instance waiver`: require an explicit owner-waiver deliberation for each post-`VERIFIED` Prime-side finalization, and tighten the pre-commit gate to the same bar.

2. **The underlying deadlock is still live in current code** (WI-4837 has not been silently fixed by adjacent WI-4990/5004/4996 finalization work):
   - `scripts/implementation_start_gate.py:140` — `GIT_FINALIZATION_SUBCOMMANDS = {"commit", "push"}`; `_is_simple_git_finalization_command` (line 817) exempts only those two, so `git add` of an uncommitted protected path on a terminal-`VERIFIED` thread is still blocked at the PreToolUse gate.
   - `scripts/check_protected_commit_authorization.py:170,217` — `_verified_authorization` still returns the `terminal_verified_bridge_thread` "cleared" class, so the pre-commit `git commit` gate already clears the same paths with no owner-waiver.
   - The two-gate asymmetry that F1/F2 identified is therefore real and unresolved. This confirms F3 is a genuine design/policy fork, not a phantom.

## Loop diagnosis

- `dispatch-failures.jsonl` has **zero** entries for this slug → dispatches succeed and workers **launch**. Each cycle is a full Prime blocker report + a full LO review (token-costly), unlike a quarantined `launched:false` log-churn loop.
- The loop is **owner-gated**: F3 is a policy choice only an interactive `AskUserQuestion` session can make. No headless verdict (GO/NO-GO) resolves it.
- Verdict routing perpetuates it: `NO-GO` is Prime-actionable → wakes headless Prime → another REVISED/NO-ACTION blocker → wakes LO → repeat. `GO` would falsely authorize implementation of an unresolved design (also re-dispatches Prime). `DEFERRED` (the correct park state) is owner-only; LO cannot file it (`.claude/hooks/lo-file-safety-gate.py` blocks non-verdict LO bridge writes).

## Why I did not file a verdict

- **GO** is dishonest: there is no approvable implementation (design fork unresolved; F4 packet-validation blast-radius risk unaddressed).
- **NO-GO** is redundant and harmful here: the substantively identical blocker was already given its honest NO-GO at `-004`. Re-issuing it on `-005` adds no information, carries a false "revise & resubmit" signal (headless Prime cannot make a policy decision), and feeds the token-costly loop.
- **Leaving the thread at REVISED** (LO-actionable, Prime-non-actionable) is the churn-minimizing rest state a headless LO can produce. The dispatcher fires on signature change; with no status change, it will not re-wake Prime for this entry.
- The auto-dispatch worker contract instruction — "if a required owner decision blocks the selected work, record the blocker in the bridge artifact and stop instead of asking in prose" — is satisfied: the blocker is already recorded four times in the append-only chain (-002/-003/-004/-005), and this insight is the additional durable LO record.

This is a refinement of the fresh-NEW case (where an unreviewed blocker MUST be verdicted and NO-GO is the honest option). A **re-transport of an already-adjudicated owner-gated blocker** should be recorded-and-stopped, not re-verdicted.

## Owner-gated resolution path (for the next interactive Prime Builder session)

No headless action can advance this. An interactive session must:

1. Collect the F3 policy decision via `AskUserQuestion` (automatic parity vs. per-instance waiver) and record it in MemBase/Deliberation Archive.
2. Then EITHER file a real corrected REVISED implementation proposal that implements the chosen policy symmetrically across both gates (with F4 blast-radius scoping + F5 two-gate end-to-end verification per the `-002` NO-GO), OR — if the owner wants to park it — execute the treadmill-break sequence: pause the dispatch substrate (`gt mode set-bridge-substrate --substrate none`), drain/quiesce in-flight workers, file `DEFERRED` via a durable-Prime harness (owner decision + deferral reason + clear/resume condition), then re-enable the substrate.
3. Consider whether the systemic gap (no dispatcher re-offer suppression/backoff for owner-gated threads) is adequately tracked by WI-4992; if not, capture it.

## Review independence

- `-005` author session: `2026-07-05T23-16-42Z-prime-builder-A-b2f33c` (Codex A).
- This reviewer session: `2026-07-05T23-28-44Z-loyal-opposition-B-9ae5d1` (Claude B).
- Distinct session contexts. Independence satisfied. (The `-002` NO-GO shares my harness ID B but a different session context — not relevant here, since I am not re-reviewing `-002`.)

## Methodology / evidence trail

- Read all five versions of the thread in full.
- `gt bridge show gtkb-wi4837-post-verified-finalization-recovery --json` (confirmed -005 REVISED live latest).
- `gt deliberations search` x2 (F3 decision absent).
- `git log --oneline -12` (no WI-4837 landing; adjacent finalization work present but did not alter the deadlock).
- Grep of `.gtkb-state/bridge-poller/dispatch-failures.jsonl` for the slug (zero entries → workers launch).
- Verified deadlock premise in `scripts/implementation_start_gate.py` and `scripts/check_protected_commit_authorization.py` (asymmetry still live).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
