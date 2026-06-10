REVISED

# Implementation Proposal --- Cross-Harness Trigger Active-Session Suppression --- REVISED-2

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-active-session-suppression-001
Version: 005 (REVISED-2 post NO-GO at `-001-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-003.md`

## Claim

REVISED-2 addresses Codex NO-GO at `-001-004`:

- **F1 (P1) fix --- Heartbeat lock path aligned with trigger state-dir.** REVISED-1 documented heartbeat locks at `.gtkb-state/cross-harness-trigger/active-{role}-session.lock`, but Slice 3's hook registrations already pass `--state-dir .gtkb-state/bridge-poller` to the trigger. If implemented literally, the heartbeat writer and trigger's `check_counterpart_active` reader would use different directories and the gate would fail open silently. REVISED-2 explicitly aligns heartbeat to the same `.gtkb-state/bridge-poller` path the trigger uses. New integration test `T-SUPPRESS-heartbeat-trigger-shared-lock-dir` pins the contract by parsing both hook configs and asserting heartbeat + trigger `--state-dir` arguments match.
- **F2 (P2) fix --- Sanity TTL default aligned to owner-stated 120s.** REVISED-1 introduced a 3600s sanity TTL default without owner authorization; the prior owner AUQ specified 120s. REVISED-2 sets the default sanity TTL to 120s. Documented tradeoff: a crashed harness without graceful Stop fires up to 120s of dispatch suppression. New acceptance criterion records this as intentional. Configurable via `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS` for operators who need a different value.

The state-machine F1 fix from REVISED-1 (split `last_dispatched_signature` + `last_suppressed_signature`) is preserved unchanged. The session-liveness F2 fix from REVISED-1 (SessionStart-creates + Stop-deletes + per-tool-use-refresh) is preserved unchanged.

## Why Now

(Carried forward from REVISED-1; condensed.)

The auto-dispatch parallel-revision problem is structural; Slice 4 currently exhibits TWO auto-dispatched Prime revisions (`-001-009` REVISED-4, `-001-011` REVISED-5) neither authored by the in-session Prime. Suppression unblocks Slice 4 + formalization revisions per S337 owner directive.

## Prior Deliberations

(Carried forward from REVISED-1 plus this round's predecessor NO-GO.)

- Slice 2 signature-dedup at `bridge/gtkb-bridge-poller-event-driven-replacement-009.md` (VERIFIED at `-010`).
- Slice 3 hook registration at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-005.md` (VERIFIED at `-006`) --- pinned `.gtkb-state/bridge-poller` as the shared dispatch-state path.
- This thread `-002` and `-001-004`: two prior NO-GOs surfacing the path + state-machine + liveness issues.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` (NEW; pending in approval batch).

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` --- INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` --- this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` --- Test Plan section T-SUPPRESS-* below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` --- all touched files under `E:\GT-KB`. Lock files at `.gtkb-state/bridge-poller/active-{role}-session.lock` (in-root; same directory as trigger dispatch-state.json per Slice 3 Option A coordination).
- `GOV-ARTIFACT-APPROVAL-001` v3 --- 1 DELIB packet through scoped-auto-approval batch `active-session-suppression-batch-2026-05-09`.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Domain-specific:**

- `scripts/cross_harness_bridge_trigger.py` --- gate added; recipient_state schema gains `last_dispatched_signature` + `last_suppressed_signature`; legacy `signature` retained for back-compat.
- `scripts/active_session_heartbeat.py` --- NEW; multi-mode (`session-start`, `tool-use`, `session-stop`); writes/refreshes/deletes lock at `<state-dir>/active-{role}-session.lock` where `<state-dir>` is supplied by the hook command and MUST match the trigger's `--state-dir`.
- `.claude/settings.json` --- adds heartbeat steps in SessionStart, PostToolUse Bash, PostToolUse Write|Edit, Stop. All steps pass `--state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` matching the existing trigger registration.
- `.codex/hooks.json` --- mirrors with `--role codex` and `--state-dir E:\GT-KB\.gtkb-state\bridge-poller`.

**Sibling thread coordination:** unchanged. Slice 4 + formalization remain PAUSED per S337 owner directive.

## Owner Decisions / Input

(Carried forward from REVISED-1 with F2 alignment.)

| AUQ question | Answer | Implication |
|---|---|---|
| (S337 this turn) "How should we sequence the active-session suppression work...?" | "File suppression NEW now; pause Slice 4 + formalization NO-GO revisions until suppression GO+VERIFIED" | Authorizes filing this thread; pauses two sibling threads. |
| (S337 this turn) "What's the freshness window for the heartbeat?" | "120 seconds" | Drives BOTH the refresh-cadence (PostToolUse refresh interval expectation) AND the sanity TTL default per REVISED-2 F2 fix. The 3600s sanity TTL from REVISED-1 was an unauthorized expansion; aligned back to 120s in this revision. |

The 1 new DELIB packet flows through `GOV-ARTIFACT-APPROVAL-001` v3 scoped-auto-approval batch `active-session-suppression-batch-2026-05-09`. No new owner decisions required by REVISED-2; the F1 path alignment and F2 default alignment are corrections within the previously-authorized scope.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`: applicability preflight will be re-run after this REVISED entry is added to `bridge/INDEX.md`. Predecessor `-001-003` reported `preflight_passed: true` packet_hash `sha256:886e8e93...`. REVISED-2 content delta is the F1+F2 path/default fixes; spec linkage stays within the registered cross-cutting set.

## Design (REVISED-2)

### Heartbeat hook script (UNCHANGED from REVISED-1 except --state-dir contract)

`scripts/active_session_heartbeat.py`:

- argparse: `--mode {session-start|tool-use|session-stop}`, `--role {claude|codex}`, `--state-dir <path>`. **`--state-dir` is REQUIRED** (no default). The hook registration MUST pass the same path the trigger uses. This makes the path coupling explicit at config time rather than hidden in script defaults.
- Lock file: `<state-dir>/active-{role}-session.lock`.
- Mode behaviors unchanged from REVISED-1.

### Trigger gate (UNCHANGED from REVISED-1)

`run_trigger()` state-machine logic from REVISED-1 preserved verbatim:

- `last_dispatched_signature` is the dedup field.
- `last_suppressed_signature` is the retry-pending marker.
- Three-way branch: counterpart_active --- record-suppressed; prior_dispatched == current --- "unchanged"; else --- dispatch.
- Slice 2 invariant preserved.

### Counterpart liveness check (UNCHANGED from REVISED-1; default value updated per F2)

```
def check_counterpart_active(recipient: str, state_dir: Path) -> bool:
    counterpart_role = "claude" if recipient == "prime" else "codex"
    lock_path = state_dir / f"active-{counterpart_role}-session.lock"
    if not lock_path.exists():
        return False
    try:
        mtime = lock_path.stat().st_mtime
    except OSError:
        return False
    age_seconds = time.time() - mtime
    sanity_ttl = int(os.environ.get("GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS", "120"))
    if age_seconds > sanity_ttl:
        return False  # treat as orphaned
    return True
```

The default sanity TTL is now 120 seconds (was 3600s in REVISED-1; aligned to owner-stated input).

### Path coupling (NEW per F1)

The heartbeat lock directory and trigger state directory MUST be the same path. This is enforced at three layers:

1. **Hook config**: each hook command passes the same `--state-dir` argument to both the heartbeat script and the trigger script.
2. **Script contract**: `active_session_heartbeat.py` REQUIRES `--state-dir` (no default), forcing the caller to supply it.
3. **Test**: `T-SUPPRESS-heartbeat-trigger-shared-lock-dir` parses `.claude/settings.json` and `.codex/hooks.json`; extracts `--state-dir` from heartbeat and trigger commands; asserts they match exactly.

This eliminates the silent failure mode where heartbeat writes one path and the trigger reads another.

### Crashed-harness-suppression-window tradeoff (NEW per F2 acceptance criterion)

With sanity TTL = 120s default:

- Graceful exit (Stop hook fires): lock deleted immediately. Counterpart trigger sees stale (lock absent) on next fire; dispatches normally. No suppression delay.
- Crash (Stop does not fire): lock remains on disk. For up to 120 seconds after the crash, the counterpart trigger sees lock-present + mtime-fresh; suppresses dispatch. After 120 seconds, mtime > sanity_ttl; lock is treated as orphaned; dispatch fires.
- Long quiet legitimate session (no tool use for >120s): lock present + mtime older than 120s; treated as orphaned. False-positive dispatch fires while a real session is still open. **This is a known tradeoff at the owner-stated 120s value**; documented as acceptance criterion.

If operators encounter the long-quiet-session false-positive in practice, two mitigations exist without code changes: (a) set `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS` to a larger value; (b) ensure tool use occurs at least every 120s. Codex's prior `-001-004` F2 framing accepted this as a recent-activity heuristic.

## Implementation Plan (REVISED-2)

(Carried forward from REVISED-1 with F1+F2 corrections.)

### IP-1 (REVISED) --- Heartbeat hook script

Same as REVISED-1 except `--state-dir` is now REQUIRED (no default).

### IP-2 (REVISED) --- Hook registration with explicit shared --state-dir

**Claude (`.claude/settings.json`):**

- SessionStart: heartbeat `--mode session-start --role claude --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` BEFORE existing session_start_dispatch.py.
- PostToolUse Bash: heartbeat `--mode tool-use --role claude --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` BEFORE existing trigger.
- PostToolUse Write|Edit: heartbeat `--mode tool-use --role claude --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` BEFORE existing trigger.
- Stop: heartbeat `--mode tool-use --role claude --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` BEFORE existing trigger Stop step; heartbeat `--mode session-stop --role claude --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` AFTER existing trigger Stop step.

**Codex (`.codex/hooks.json`):**

Mirror with `--role codex` and `--state-dir E:\GT-KB\.gtkb-state\bridge-poller`.

The shared `--state-dir` is identical to what Slice 3 already passes to the trigger script. Heartbeat and trigger therefore read/write the same directory by construction.

### IP-3 (REVISED) --- Trigger gate

Same as REVISED-1 except sanity TTL default = 120s (was 3600s).

### IP-4 (REVISED) --- Tests

NEW `tests/scripts/test_active_session_heartbeat.py` (~6-8 tests). Same as REVISED-1.

UPDATES to `tests/scripts/test_cross_harness_bridge_trigger.py`. Same as REVISED-1 plus:

- T-SUPPRESS-sanity-ttl-default-is-120s: assert default `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS` is 120 (matches owner directive).
- Existing T-SUPPRESS-counterpart-stale-overrides-via-sanity-ttl: stale boundary updated to 120s.

UPDATES to `tests/scripts/test_slice_3_hook_registrations.py`. Same as REVISED-1 plus:

- **T-SUPPRESS-heartbeat-trigger-shared-lock-dir** (NEW per F1): parse `.claude/settings.json`; extract `--state-dir` from each heartbeat command and from the trigger command; assert they all match exactly. Repeat for `.codex/hooks.json`. The test fails if any heartbeat or trigger command has a different `--state-dir` value.

### IP-5 --- Stop hook ordering

Same as REVISED-1: tool-use heartbeat refresh --- trigger Stop reconciliation --- session-stop heartbeat lock removal.

### IP-6 --- Documentation

Add inline doc comment in `scripts/cross_harness_bridge_trigger.py` describing:

- The three signature fields (`signature`, `last_dispatched_signature`, `last_suppressed_signature`) and their semantics.
- The shared-state-dir contract with `active_session_heartbeat.py`.
- The 120s sanity TTL default and the crashed-harness-suppression tradeoff.

## Spec-Derived Test Plan (REVISED-2)

Carries forward all rows from REVISED-1. New/updated rows:

| Test | Spec/Requirement | Method |
|---|---|---|
| **T-SUPPRESS-heartbeat-trigger-shared-lock-dir** (NEW per F1) | IP-2 + IP-3 | Parse `.claude/settings.json` and `.codex/hooks.json`. Extract `--state-dir <value>` from every heartbeat command and from every trigger command. Assert all values match within each harness side (Claude side: all `$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller`; Codex side: all `E:\GT-KB\.gtkb-state\bridge-poller`). |
| T-SUPPRESS-sanity-ttl-default-is-120s (NEW per F2) | IP-3 | `python -c "import os; from cross_harness_bridge_trigger import check_counterpart_active; ..."` exercises the default; assert default int parsed is 120. Or simpler: import the constant if exposed. |
| T-SUPPRESS-counterpart-stale-overrides-via-sanity-ttl (UPDATED per F2) | IP-3 | Counterpart lock present but mtime > 120s ago (not 3600). Trigger dispatches. |
| T-SUPPRESS-heartbeat-script-requires-state-dir (NEW per F1) | IP-1 | `python active_session_heartbeat.py --mode tool-use --role claude` (no `--state-dir`) returns argparse error / non-zero exit. |
| T-SUPPRESS-heartbeat-script-respects-state-dir (NEW per F1) | IP-1 | Heartbeat with `--state-dir <synthetic>` writes to `<synthetic>/active-{role}-session.lock`, NOT to any default path. |

All other test rows from REVISED-1 unchanged.

## Acceptance Criteria

- [ ] Codex confirms F1 fix: heartbeat path aligned with trigger state-dir; integration test pins the shared-path contract.
- [ ] Codex confirms F2 fix: sanity TTL default = 120s matches owner-stated value; crashed-harness-suppression-window tradeoff documented as intentional.
- [ ] Codex confirms F1 (REVISED-1) state-machine repair preserved: split state fields enable retry after counterpart exit while preserving Slice 2 dedup.
- [ ] Codex confirms F2 (REVISED-1) liveness model preserved: SessionStart-creates + Stop-deletes + sanity-TTL is the active-session signal.
- [ ] Codex confirms backward-compat: legacy `signature` field updated only on real dispatch.
- [ ] Codex confirms 1-packet approval batch is sufficient.
- [ ] Codex confirms scope is now complete --- no further hidden surfaces.

## Risk / Rollback

(Carried forward from REVISED-1 with F2 acceptance criterion documented as intentional tradeoff.)

**Risk surface:**

- **Risk: Crashed harness suppresses dispatch for up to 120 seconds.** Documented and accepted per F2 owner-stated value. If operators need a different window, override via `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS` env var.
- **Risk: Long quiet legitimate session (no tool use for >120s) gets false-cleared as orphan.** Documented; mitigations available without code changes (env-var override; tool-use cadence).
- (Other risks unchanged from REVISED-1.)

**Rollback:** unchanged from REVISED-1.

## Files Expected To Change (REVISED-2)

(Identical to REVISED-1 file list; only path values and default values change.)

- `scripts/active_session_heartbeat.py` (NEW; ~80 lines).
- `scripts/cross_harness_bridge_trigger.py` --- gate added; state schema extended; sanity TTL default = 120s.
- `.claude/settings.json` --- 4 heartbeat hook step additions (SessionStart, PostToolUse Bash, PostToolUse Write|Edit, Stop with 2 entries for ordering); all use `--state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` matching the trigger.
- `.codex/hooks.json` --- mirrors with `--role codex` and `E:\GT-KB\.gtkb-state\bridge-poller`.
- `tests/scripts/test_active_session_heartbeat.py` (NEW; ~120 lines, 6-8 tests).
- `tests/scripts/test_cross_harness_bridge_trigger.py` --- ~14 new T-SUPPRESS-* tests (13 from REVISED-1 + T-SUPPRESS-sanity-ttl-default-is-120s).
- `tests/scripts/test_slice_3_hook_registrations.py` --- updated with T-SUPPRESS-heartbeat-trigger-shared-lock-dir and heartbeat-presence assertions.
- `groundtruth.db` --- 1 new DELIB row.
- `.groundtruth/formal-artifact-approvals/2026-05-NN-DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09.json` (1 packet).
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-005.md` (this REVISED).
- `bridge/INDEX.md` (REVISED line for this thread).

## Open Follow-Ons

(Unchanged from REVISED-1.)

## Recommended Commit Type

`feat:` --- unchanged.

## Loyal Opposition Asks

1. Confirm F1 fix: heartbeat lock path aligned with trigger state-dir; integration test pins the shared-path contract.
2. Confirm F2 fix: sanity TTL default = 120s aligns with owner directive; crashed-harness-suppression tradeoff documented as intentional.
3. Confirm REVISED-1 state-machine + liveness fixes are preserved unchanged.
4. Confirm scope is now complete; no further hidden surfaces.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
