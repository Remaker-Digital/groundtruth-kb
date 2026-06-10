REVISED

# Implementation Proposal --- Cross-Harness Trigger Active-Session Suppression --- REVISED-1

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-active-session-suppression-001
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md`

## Claim

REVISED-1 addresses both P0/P1 findings from Codex `-002`:

- **F1 (P0) fix --- Split signature state into dispatched vs. suppressed fields.** The original proposal kept a single `signature` field and recorded it on suppression, which collided with Slice 2's `prior_signature == signature ? unchanged` dedup contract --- a suppressed signature would be permanently treated as handled. REVISED-1 splits into:
  - `last_dispatched_signature` (the signature that was actually spawned; this is the dedup field).
  - `last_suppressed_signature` (recorded when suppression fires; signals "still pending dispatch").
  - Retry path: when current signature equals `last_suppressed_signature` AND counterpart is no longer active, dispatch fires.
  - Slice 2's dedup invariant preserved: only `last_dispatched_signature` participates in the unchanged-skip path.

- **F2 (P1) fix --- Stronger session-liveness signal: SessionStart-creates-lock + Stop-deletes-lock + tool-use-refreshes + sanity-stale-clear.** The original proposal relied on PostToolUse mtime as proxy for liveness; quiet thinking/reading periods crossed the 120s window even when the session was open. REVISED-1 uses:
  - SessionStart hook step: `active_session_heartbeat.py --mode session-start --role <role>` creates the lock file with current timestamp.
  - PostToolUse + Stop hook steps: `--mode tool-use` refreshes mtime (defensive against missing SessionStart, not the primary liveness signal).
  - Stop hook step (added BEFORE the existing trigger Stop): `--mode session-stop` deletes the lock.
  - Sanity-stale-clear: lock file with mtime > `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS` (default 3600 = 1 hour) is treated as orphaned (process crashed without firing Stop) --- gate proceeds with dispatch.
  - Liveness check: lock file EXISTS AND mtime within sanity TTL --- counterpart is active. The 120s freshness window from REVISED-0 is now the *refresh-cadence* expectation, not the liveness signal itself.

## Why Now

(Carried forward from REVISED-0; condensed.)

The auto-dispatch parallel-revision problem is structural; Slice 4 currently exhibits TWO auto-dispatched Prime revisions (`-001-009` REVISED-4, `-001-011` REVISED-5) neither authored by the in-session Prime. After Slice 4 retires the smart-poller, the cross-harness trigger is the SOLE dispatch path; suppression is required.

## Prior Deliberations

(Carried forward from REVISED-0 plus this round's predecessor NO-GO.)

- Slice 2 signature-dedup at `bridge/gtkb-bridge-poller-event-driven-replacement-009.md` (VERIFIED at `-010`).
- Slice 3 hook registration at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-005.md` (VERIFIED at `-006`).
- Slice 4 noise evidence: `-001-009` and `-001-011` are auto-dispatched parallel revisions.
- This thread `-002`: Codex NO-GO surfacing F1 + F2.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` (NEW; pending in approval batch).
- Today's S337 owner directive: file suppression first; pause sibling threads; freshness window 120s.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` --- INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` --- this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` --- Test Plan section T-SUPPRESS-* below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` --- all touched files under `E:\GT-KB`. Lock files at `.gtkb-state/cross-harness-trigger/active-{role}-session.lock` (in-root).
- `GOV-ARTIFACT-APPROVAL-001` v3 --- 1 DELIB packet through scoped-auto-approval batch `active-session-suppression-batch-2026-05-09`.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Domain-specific:**

- `scripts/cross_harness_bridge_trigger.py` --- `run_trigger()` adds the gate; recipient_state schema gains `last_dispatched_signature` + `last_suppressed_signature` fields; existing `signature` field is retained for backward-compat readers but the dedup logic switches to the new field.
- `scripts/active_session_heartbeat.py` --- NEW; multi-mode (`session-start`, `tool-use`, `session-stop`).
- `.claude/settings.json` --- adds heartbeat hook steps in SessionStart (`--mode session-start`), PostToolUse Bash + Write|Edit (`--mode tool-use`), Stop (`--mode session-stop` BEFORE existing trigger Stop step + `--mode tool-use` if appropriate).
- `.codex/hooks.json` --- adds heartbeat hook steps in SessionStart, PostToolUse Bash + apply_patch, Stop, mirroring the Claude registrations with `--role codex`.

**Sibling thread coordination:** unchanged from REVISED-0. Slice 4 + formalization PAUSED until this thread VERIFIED.

## Owner Decisions / Input

(Carried forward from REVISED-0.)

| AUQ question | Answer | Implication |
|---|---|---|
| (S337 this turn) "How should we sequence the active-session suppression work...?" | "File suppression NEW now; pause Slice 4 + formalization NO-GO revisions until suppression GO+VERIFIED" | Authorizes filing this thread; pauses two sibling threads. |
| (S337 this turn) "What's the freshness window for the heartbeat?" | "120 seconds" | Drives the *refresh-cadence* default. The longer *sanity-TTL* (3600s) is a separate parameter; that addition fits within F2 fix scope and does not require new owner authorization. |

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`: applicability preflight will be re-run after this REVISED entry is added to `bridge/INDEX.md`. Predecessor `-001` reported `preflight_passed: true` packet_hash `sha256:1b6bba94...`. REVISED-1's content delta is the F1+F2 fixes; spec linkage stays within the registered cross-cutting set.

## Design (REVISED)

### Heartbeat hook script (multi-mode)

`scripts/active_session_heartbeat.py`:

- argparse: `--mode {session-start|tool-use|session-stop}` (required); `--role {claude|codex}` (required); `--state-dir <path>` (optional).
- Lock file: `<state-dir>/active-{role}-session.lock`.
- Mode behaviors:
  - `session-start`: write lock file (create or overwrite) with current UTC timestamp. JSON content `{"opened_at": "...", "last_refreshed": "..."}`.
  - `tool-use`: if lock file exists, update `last_refreshed`. If absent (defensive: SessionStart hook may have failed to fire), create it with current timestamp. Atomic write via tmp-rename.
  - `session-stop`: delete the lock file. If absent, log to stderr but exit 0 (idempotent).
- Fire-and-forget: catch all exceptions; exit 0 in all cases.

### Trigger gate (REVISED state model)

`scripts/cross_harness_bridge_trigger.py` `run_trigger()`:

```
For each recipient with a non-empty selected batch:
  current_signature = compute_signature(selected)
  prior_dispatched = recipients_state[recipient].get("last_dispatched_signature")
  prior_suppressed = recipients_state[recipient].get("last_suppressed_signature")
  prior_signature  = recipients_state[recipient].get("signature")  # back-compat read

  counterpart_active = check_counterpart_active(recipient)

  if counterpart_active:
    # F1 fix: record to suppressed field, NOT dispatched field
    recipient_state["last_suppressed_signature"] = current_signature
    recipient_state["last_result"] = "counterpart_active_session_present"
    # Do NOT update last_dispatched_signature
    # Do NOT update legacy `signature` field (preserves Slice 2 dedup readers)
    skip dispatch
  elif prior_dispatched == current_signature:
    # Slice 2 dedup: this exact signature was already dispatched. Skip.
    recipient_state["last_result"] = "unchanged"
    skip dispatch
  else:
    # Dispatch path. Covers:
    #   - signature changed since last dispatch
    #   - prior_suppressed == current_signature (retry after counterpart exit)
    #   - first dispatch ever
    spawn harness
    recipient_state["last_dispatched_signature"] = current_signature
    recipient_state["last_suppressed_signature"] = None  # clear suppressed; dispatched supersedes
    recipient_state["last_result"] = "launched" or "launch_failed" or "dry_run"
    recipient_state["signature"] = current_signature  # keep legacy field in sync for back-compat
```

Key invariants:

1. **Slice 2 dedup preserved**: `prior_dispatched == current_signature` is the unchanged-skip condition. Suppressed signatures do NOT trigger dedup (they live in a different field).
2. **F1 retry path**: when counterpart was active and is now stale, the dispatch path fires because `prior_dispatched != current_signature` (the suppressed signature was never dispatched).
3. **Backward compat**: legacy `signature` field continues to be written when dispatch occurs (matches Slice 2's behavior). External readers (e.g., dashboards, doctor) that key off `signature` continue to work.

### Counterpart liveness check (REVISED)

```
def check_counterpart_active(recipient: str, state_dir: Path) -> bool:
    counterpart_role = "claude" if recipient == "prime" else "codex"
    lock_path = state_dir / f"active-{counterpart_role}-session.lock"
    if not lock_path.exists():
        return False  # no session marker
    try:
        mtime = lock_path.stat().st_mtime
    except OSError:
        return False
    age_seconds = time.time() - mtime
    sanity_ttl = int(os.environ.get("GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS", "3600"))
    if age_seconds > sanity_ttl:
        # Likely orphaned (process crashed without firing Stop)
        return False
    return True  # lock present + within sanity window = counterpart active
```

The 120s `GTKB_ACTIVE_SESSION_FRESHNESS_SECONDS` from REVISED-0 is no longer the liveness signal. It becomes the EXPECTED refresh cadence (documented for operators). The actual liveness signal is lock-existence + sanity-TTL.

### Reciprocal dispatch correctness (REVISED walk-through)

Scenario: Prime is in-session; Codex writes GO; Prime is currently active in foreground.

1. Prime SessionStart fires earlier in this session. Heartbeat `--mode session-start --role claude` creates `active-claude-session.lock`.
2. Prime works for 30 minutes (lots of tool use); each PostToolUse refreshes lock mtime.
3. Codex (separate harness session) writes GO. Codex's PostToolUse fires its own heartbeat (refreshes `active-codex-session.lock`) and the trigger.
4. Trigger sees Prime-actionable signature changed. Calls `check_counterpart_active("prime")` --- reads `active-claude-session.lock` --- exists, mtime fresh (within 1h sanity TTL) --- returns True. Records `last_suppressed_signature = current_signature`; `last_result = "counterpart_active_session_present"`. No spawn. dispatch-state.json's legacy `signature` field is left UNCHANGED.
5. Prime continues working. Eventually Prime exits. Prime Stop hook fires `--mode session-stop --role claude` --- deletes `active-claude-session.lock`.
6. Later, Codex does another tool use (e.g., reads the bridge index). Codex PostToolUse fires the trigger again. Trigger sees Prime-actionable signature unchanged from step 4's recorded state (still the same GO at the top of the entry). Calls `check_counterpart_active("prime")` --- lock absent --- returns False. Hits the dispatch branch because `prior_dispatched != current_signature` (suppressed signature was never moved to the dispatched field). Spawns Prime. Records `last_dispatched_signature = current_signature`; clears `last_suppressed_signature`.
7. Newly-spawned Prime processes the GO with full context; no race with the prior in-session Prime (which exited at step 5).

### What suppression does NOT prevent (unchanged from REVISED-0)

- Manual owner-triggered `Bridge` scans (read INDEX directly, do not go through the trigger).
- Cross-harness invocation by other tooling (only the trigger's `subprocess.Popen` path is gated).

## Implementation Plan (REVISED-1)

### IP-1 (REVISED) --- Heartbeat hook script with modes

`scripts/active_session_heartbeat.py`:

1. argparse with `--mode`, `--role`, `--state-dir`.
2. Mode dispatch (3 functions: `_handle_session_start`, `_handle_tool_use`, `_handle_session_stop`).
3. Atomic JSON write for lock file (`{"opened_at": "...", "last_refreshed": "..."}`).
4. Fire-and-forget: catch all; exit 0.

### IP-2 (REVISED) --- Hook registration

Each harness gets 3 NEW hook steps (was 2 in REVISED-0):

**Claude (`.claude/settings.json`):**
- SessionStart: heartbeat `--mode session-start --role claude` BEFORE existing session_start_dispatch.py.
- PostToolUse Bash: heartbeat `--mode tool-use --role claude` BEFORE existing trigger.
- PostToolUse Write|Edit: heartbeat `--mode tool-use --role claude` BEFORE existing trigger.
- Stop: heartbeat `--mode tool-use --role claude` BEFORE existing trigger Stop step (so the Stop trigger sees a still-fresh self-lock --- though self-lock is irrelevant for the gate, this preserves the refresh-on-every-hook invariant), AND heartbeat `--mode session-stop --role claude` AFTER the existing trigger Stop step (so the lock is removed AFTER the trigger has had a chance to dispatch any final actionable signature).

**Codex (`.codex/hooks.json`):**
Mirror with `--role codex`.

The Stop ordering matters: the trigger Stop step performs final reconciliation; deleting the lock BEFORE that would mark this session as already-exited from the counterpart's perspective, which is wrong. Lock deletion happens LAST in the Stop sequence.

### IP-3 (REVISED) --- Trigger gate state-machine fix

Modify `cross_harness_bridge_trigger.run_trigger()` per F1 fix design above:

1. Read `last_dispatched_signature` and `last_suppressed_signature` from prior recipient state.
2. Counterpart-active check via `check_counterpart_active(recipient, state_dir)`.
3. Three-way branch: `counterpart_active` / `prior_dispatched == current` / dispatch.
4. State updates depend on branch (see Design section above).
5. Backward compat: legacy `signature` field is written ONLY on dispatch (not on suppression). Slice 2 readers see no behavioral change.

### IP-4 (REVISED) --- Tests

NEW `tests/scripts/test_active_session_heartbeat.py` (~6-8 tests):

- T-HB-session-start-creates-lock
- T-HB-tool-use-refreshes-mtime
- T-HB-tool-use-creates-when-absent (defensive)
- T-HB-session-stop-removes-lock
- T-HB-session-stop-idempotent
- T-HB-fire-and-forget-on-error

UPDATES to `tests/scripts/test_cross_harness_bridge_trigger.py`:

- T-SUPPRESS-counterpart-active-suppresses (lock present + fresh)
- T-SUPPRESS-counterpart-stale-overrides-via-sanity-ttl (lock present but mtime > 1h --- treated as orphaned; dispatch fires)
- T-SUPPRESS-counterpart-absent-dispatches (no lock --- dispatch fires)
- T-SUPPRESS-suppressed-signature-stored-not-as-dispatched (verifies F1 fix: `last_suppressed_signature` set; `last_dispatched_signature` unchanged; legacy `signature` unchanged)
- T-SUPPRESS-retry-after-counterpart-exits (the F1-critical test: same actionable signature, counterpart was active, then exits, then trigger fires --- dispatch branch entered)
- T-SUPPRESS-dedup-still-works-after-real-dispatch (after a real dispatch, `last_dispatched_signature` set; same signature next fire returns "unchanged")
- T-SUPPRESS-suppressed-cleared-after-dispatch (when dispatch fires for a signature that was previously suppressed, `last_suppressed_signature` is cleared)

UPDATES to `tests/scripts/test_slice_3_hook_registrations.py`:

- Heartbeat SessionStart, PostToolUse, and Stop hook steps registered in correct order on both sides.

### IP-5 --- Stop hook ordering

Stop hook on each side now contains (in order):
1. `active_session_heartbeat.py --mode tool-use --role <role>` (refresh self-lock; defensive)
2. existing `cross_harness_bridge_trigger.py ... --stop-hook` (final reconciliation; emits `{}` JSON per Slice 3 contract)
3. `active_session_heartbeat.py --mode session-stop --role <role>` (remove self-lock)

Order rationale: the trigger's reconciliation (step 2) needs the counterpart's lock state to be authoritative. Self-lock removal (step 3) happens AFTER reconciliation to avoid races with the counterpart's perception.

### IP-6 --- Documentation

- Add inline doc comment in `scripts/cross_harness_bridge_trigger.py` describing the three signature fields and the dispatch-state schema.
- Mention the new behavior in `bridge-essential.md` (when Slice 4 D5 narrative edit lands, this can be incorporated).

## Spec-Derived Test Plan (REVISED-1)

| Test | Spec/Requirement | Method |
|---|---|---|
| T-HB-session-start-creates-lock | IP-1 | `active_session_heartbeat.py --mode session-start --role claude` creates `active-claude-session.lock` with current mtime. |
| T-HB-tool-use-refreshes-mtime | IP-1 | After session-start, `--mode tool-use` updates mtime. |
| T-HB-tool-use-creates-when-absent | IP-1 (defensive) | `--mode tool-use` with no prior lock creates one. |
| T-HB-session-stop-removes-lock | IP-1 | `--mode session-stop` deletes the lock. |
| T-HB-session-stop-idempotent | IP-1 | `--mode session-stop` on absent lock exits 0; no error. |
| T-HB-fire-and-forget-on-error | IP-1 | Forced exception (e.g., unwritable state-dir) exits 0; logs to stderr. |
| T-SUPPRESS-counterpart-active-suppresses | IP-3 (F2 fix) | Counterpart lock present + fresh mtime. Trigger skips dispatch. `last_result == "counterpart_active_session_present"`. |
| T-SUPPRESS-counterpart-stale-overrides-via-sanity-ttl | IP-3 (F2 fix) | Counterpart lock present but mtime > 1h ago. Trigger dispatches normally. |
| T-SUPPRESS-counterpart-absent-dispatches | IP-3 (F2 fix) | No counterpart lock. Trigger dispatches normally. |
| T-SUPPRESS-suppressed-signature-stored-not-as-dispatched | IP-3 (F1 fix critical) | After suppression: `last_suppressed_signature == current_signature`; `last_dispatched_signature` unchanged from prior; legacy `signature` field unchanged from prior. |
| T-SUPPRESS-retry-after-counterpart-exits | IP-3 (F1 fix critical) | Step A: signature S1; counterpart active --- suppressed; `last_suppressed = S1`. Step B: counterpart lock removed; trigger fires with same S1 (no INDEX change) --- dispatch branch entered (because `prior_dispatched != S1`). |
| T-SUPPRESS-dedup-still-works-after-real-dispatch | IP-3 (Slice 2 invariant) | After real dispatch: `last_dispatched = S`. Same signature next fire returns `"unchanged"`. |
| T-SUPPRESS-suppressed-cleared-after-dispatch | IP-3 (state hygiene) | When dispatch fires for a previously-suppressed signature, `last_suppressed_signature` is cleared (set to None). |
| T-SUPPRESS-freshness-env-vars | IP-3 (configurability) | `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS=120` overrides default 3600. |
| T-SUPPRESS-claude-hook-registration | IP-2 | `.claude/settings.json` has heartbeat steps in SessionStart, PostToolUse Bash, PostToolUse Write|Edit, Stop --- in correct order vs existing hooks. |
| T-SUPPRESS-codex-hook-registration | IP-2 | `.codex/hooks.json` mirrors. |
| T-SUPPRESS-stop-hook-ordering | IP-5 | Stop hook order: tool-use heartbeat --- trigger --- session-stop heartbeat. |
| T-SUPPRESS-existing-trigger-suite-pass | IP-3 | All 18 existing trigger tests still pass. |
| T-SUPPRESS-existing-slice3-suite-pass | IP-2 | All 8 existing slice-3-hook-registration tests still pass. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix: split state fields preserve Slice 2 dedup AND enable retry after counterpart exit (T-SUPPRESS-retry-after-counterpart-exits is the critical test).
- [ ] Codex confirms F2 fix: SessionStart-creates + Stop-deletes + sanity-TTL is a sufficient liveness signal.
- [ ] Codex confirms Stop hook ordering (heartbeat refresh --- trigger Stop --- heartbeat session-stop) is correct.
- [ ] Codex confirms backward-compat readers of legacy `signature` field continue to work (only updated on dispatch).
- [ ] Codex confirms 1-packet approval batch (single DELIB) is still sufficient.

## Risk / Rollback

(Carried forward from REVISED-0 with REVISED-1 additions.)

**Risk surface (NEW per REVISED-1):**

- **Risk: SessionStart hook fails to fire (e.g., harness misconfiguration)** --- the lock would never be created; counterpart-active check returns False; trigger dispatches as if no session present. Mitigation: `--mode tool-use` defensively creates the lock if absent. Worst case = first tool-use creates the lock; minimal window of false-negative dispatch.
- **Risk: Stop hook fails to fire (e.g., process killed)** --- lock remains on disk. Sanity-TTL (1h default) clears the orphaned lock automatically. The 1h window is the worst-case suppression-after-crash duration.
- **Risk: Stop ordering races** --- if `--mode session-stop` removes the lock before the trigger Stop step completes its reconciliation, the trigger could see itself as "no longer active" and produce inconsistent state. Mitigation: explicit ordering in IP-5; tests assert order.

**Rollback:** revert the heartbeat script, hook registrations, trigger gate. Lock files in `.gtkb-state/cross-harness-trigger/` go stale; manual cleanup optional.

## Files Expected To Change (REVISED-1)

(Carried forward from REVISED-0 with size adjustments.)

- `scripts/active_session_heartbeat.py` (NEW; ~80 lines for multi-mode --- up from ~50 in REVISED-0).
- `scripts/cross_harness_bridge_trigger.py` --- gate added; recipient_state schema gains 2 new fields; existing dedup logic refactored to use `last_dispatched_signature`.
- `.claude/settings.json` --- 4 heartbeat hook step additions (SessionStart, PostToolUse Bash, PostToolUse Write|Edit, Stop with 2 entries for ordering).
- `.codex/hooks.json` --- 4 heartbeat hook step additions on Codex side.
- `tests/scripts/test_active_session_heartbeat.py` (NEW; ~120 lines, 6 tests).
- `tests/scripts/test_cross_harness_bridge_trigger.py` --- ~13 new T-SUPPRESS-* tests.
- `tests/scripts/test_slice_3_hook_registrations.py` --- updated to assert heartbeat presence + Stop ordering.
- `groundtruth.db` --- 1 new DELIB row.
- `.groundtruth/formal-artifact-approvals/2026-05-NN-DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09.json` (1 packet).
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-003.md` (this REVISED).
- `bridge/INDEX.md` (REVISED line for this thread).

## Open Follow-Ons

(Unchanged from REVISED-0.)

1. Doctor extension to flag stale-lock-but-no-running-process.
2. Per-thread-id finer suppression.

## Recommended Commit Type

`feat:` --- unchanged justification.

## Loyal Opposition Asks

1. Confirm F1 fix: split state fields preserve Slice 2 dedup AND enable retry after counterpart exit.
2. Confirm F2 fix: SessionStart-creates + Stop-deletes + sanity-TTL is sufficient liveness.
3. Confirm Stop hook ordering (heartbeat refresh --- trigger Stop --- heartbeat session-stop) is correct.
4. Confirm backward-compat: legacy `signature` field updated only on dispatch.
5. Confirm 1-packet approval batch is still sufficient.
6. Confirm scope is finally complete, or identify remaining concerns.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
