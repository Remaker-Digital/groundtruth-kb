# Auto-Finalization Sweep

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ba2cbba9-87c3-41df-af06-ba16eea854be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

This rule auto-loads via the `.claude/rules/` convention. It is the narrative
authority for the auto-finalization sweep landed by WI-4889 (Slice 1 of the
dispatch-treadmill-drain program).

## Authority

- `WI-4889` (PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY) — the implementation work item.
- `DELIB-20266278` — owner authorization of the treadmill-drain program and the
  "build the sweep first" sequencing.
- `DELIB-20266272` — the PHASE-Y dispatcher-daemon go-live whose asymmetry
  (dispatchable Loyal Opposition, no dispatchable hooked Prime Builder) creates
  the treadmill this sweep drains.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the bridge audit-trail / finalization
  durability the sweep serves.
- WI-4871 untracked-VERIFIED durability guard
  (`doctor._check_untracked_terminal_verified_verdicts`) — the detector this
  sweep remediates.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the Codex `Stop`-hook surface; the
  sweep is registered in both harness surfaces (cross-harness parity).

## The treadmill

After the PHASE-Y go-live, the only dispatchable Loyal Opposition harness
(Cursor-E) writes terminal `VERIFIED` verdicts through the live dispatcher
daemon, but its finalization commits are blocked by the inventory-drift gate,
and no dispatchable hooked Prime Builder is available to finalize. Terminal
`VERIFIED` verdicts therefore accumulate untracked and continuously re-fail the
WI-4871 guard, requiring a hooked harness to finalize them by hand each session.
The sweep automates that hand-finalization.

## Mechanism

`scripts/auto_finalize_sweep.py` is registered as a `Stop` hook in BOTH
`.claude/settings.json` and `.codex/hooks.json` (the same shared-script,
dual-registration parity model as `scripts/cross_harness_bridge_trigger.py`).
On turn-end it:

1. **Cheap-gate:** enumerates untracked terminal `VERIFIED` verdict files using
   the WI-4871 logic (`git ls-files --others --exclude-standard bridge` +
   first-non-blank-line `== "VERIFIED"`). If none, it no-ops.
2. **Eligibility (both required, deterministic):**
   - **Independence** — the verdict's `author_session_context_id` differs from
     the `author_session_context_id` of the implementation report it
     `Responds to`. A self-review verdict, or one with missing/unreadable author
     metadata, is skipped and audit-logged (never auto-committed).
   - **Implementation already committed** — the responded-to report's
     `target_paths` (parsed via
     `implementation_authorization.extract_target_paths`) are all clean in
     `git status`. If any is dirty/untracked, the verdict is skipped and
     audit-logged for manual handling (the sweep never guesses source staging or
     hunk-selection).
3. **Finalize:** stages the verdict file plus all untracked
   `bridge/<slug>-NNN.md` thread-chain files for that slug and commits them with
   a `chore(bridge): finalize <author>-LO <slug> VERIFIED verdict (-NNN)`
   message via a pathspec-limited partial commit (`git commit -- <chain>`), so
   the caller's unrelated staged changes are never captured.

## Invariants

- **Verdict-file only.** The sweep commits only `bridge/*.md` files; it never
  stages source or test files. Implementation finalization remains interactive.
- **No-capture.** The pathspec-limited commit commits exactly the chain files;
  a caller's unrelated staged changes are preserved.
- **Lock/contention-safe.** A failed commit (pre-commit gate block,
  `.git/index.lock` contention, concurrent ref update) unstages the chain and
  returns without spinning; the verdict is left for the next run or manual
  handling.
- **Idempotent.** A second run finds nothing to finalize.
- **Cheap-gated.** The only unconditional per-turn work is the cheap WI-4871
  enumeration; the bounded commit action runs only when eligible verdicts exist.
  This honors the poller-retirement lesson in `bridge-essential.md`: gate the
  bounded action behind a cheap deterministic check.
- **Fail-soft.** Any unexpected error is swallowed and the hook exits 0 so it
  never blocks turn-end.
- **Audit-logged.** Every finalize/skip/error is appended to
  `.gtkb-state/auto-finalize-sweep/sweep.jsonl`.

## Disable

Set `GTKB_AUTO_FINALIZE_SWEEP_DISABLE=1` in the environment to skip the sweep
for a session (e.g., during bridge-infrastructure debugging).

## Relationship to other surfaces

- It does NOT replace the WI-4871 guard (the detector) — it remediates what the
  guard detects.
- It is NOT a dispatcher: it spawns no workers and makes no review decisions; it
  only commits verdicts an independent Loyal Opposition already decided.
- It is NOT a substitute for fixing the Cursor-E inventory-drift commit blocker
  (a follow-on slice of the treadmill-drain program); it drains the symptom so
  the WI-4871 guard stays green while that root fix is pursued.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
