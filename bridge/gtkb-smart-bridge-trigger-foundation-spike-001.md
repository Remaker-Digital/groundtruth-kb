# Bridge Proposal — Smart Bridge Trigger: Foundation Stabilization + P2.5 Verification Spike

**Status:** NEW (implementation proposal derived from program GO)  
**Author:** Prime Builder (Goose / interactive override)  
**Date:** 2026-06-08  
**Document name:** `gtkb-smart-bridge-trigger-foundation-spike`  
**Supersedes:** None (first implementation slice from program GO)  
**Derives from:** `bridge/gtkb-bridge-poller-001-smart-poller-007.md` (GO), `-006` (contract)

---

## 0. Scope

This proposal covers the **foundation stabilization + P2.5 verification spike** from the smart bridge trigger program per -006 §3:

- **Foundation:** Stabilize the existing event-driven trigger infrastructure (`scripts/cross_harness_bridge_trigger.py`), including the dispatch-state recovery defect identified in S397
- **P2.5 Verification Spike:** Empirical evidence gathering on whether `claude -p` / `codex exec` can preserve the same governance envelope as interactive sessions

**Out of scope (explicitly gated):**
- **P1 detector/parser:** Has its own bridge thread (`gtkb-smart-poller-p1-detector`); this GO does not approve it and it needs revision
- **P3 invoker design:** Gated on P2.5 spike evidence per -006 §3.3 ("P3 invoker design on spike evidence, including the specific `--bare` governance-context risk")
- **Autonomous invocation:** Gated behind empirical spike results

**Why foundation stabilization is needed:** The S397 diagnosis (2026-06-08) revealed a dispatch-state signature lock-in defect that prevents re-dispatch after fatal worker errors. This must be fixed before the P2.5 spike can produce meaningful evidence.

---

## 1. Specification Links

| Specification | Status | Relevance |
|---|---|---|
| `SPEC-BRIDGE-TRIGGER-EVENT-DRIVEN-001` | active | Defines event-driven trigger architecture, hook registration, dispatch state machine |
| `SPEC-BRIDGE-TRIGGER-DISPATCH-STATE-001` | active | Defines dispatch state schema, signature dedup, recipient tracking |
| `SPEC-BRIDGE-TRIGGER-CONCURRENCY-001` | active | Defines spawn locking, stale-transition checks, dirty-worktree checks |
| `REQ-BRIDGE-TRIGGER-EVENT-DRIVEN-001` | active | FR1-FR8 (trigger architecture, dispatch, state management) |
| `REQ-BRIDGE-TRIGGER-CONCURRENCY-001` | active | FR1-FR5 (spawn locking, worktree isolation, dirty checks) |

**Requirement sufficiency:** Existing specifications are sufficient for foundation stabilization. The P2.5 spike may produce evidence that requires new specifications for P3 invoker design, but that is out of scope for this proposal.

---

## 2. Prior Deliberations

- `DELIB-1121`: Records the halt of the OS pollers and the token-regression baseline
- `DELIB-1104`: Records the prior bridge-poller thread state
- `DELIB-0101`: Predecessor discussion of bridge automation
- `DELIB-0486`: Predecessor discussion of bridge automation
- `DELIB-S397-OLLAMA-DISPATCH-FAILURE-2026-06-08`: S397 diagnosis of Ollama LO dispatch failure, dispatch-state signature lock-in defect

**No prior deliberation contradicts the event-driven trigger architecture or the P2.5 spike requirement.**

---

## 3. Implementation Plan

### 3.1 Foundation Stabilization: Dispatch-State Recovery

**File:** `scripts/cross_harness_bridge_trigger.py`

**Defect:** The trigger writes `last_dispatched_signature` even in dry-run mode and after fatal worker errors, preventing re-dispatch. Per S397 diagnosis (2026-06-08), this caused 14 bridge entries to be stranded in NEW/REVISED state for 24+ hours.

**Fix (per -006 §5 branch/worktree isolation + spawn locking):**

1. **Dry-run must not update signature:** Modify the dispatch logic at line 2157 to only update `last_dispatched_signature` when `dry_run=False` and launch succeeded:

```python
# Only record signature if launch succeeded (not dry-run, not failed)
if recipient == "prime-builder" and not dry_run:
    if launch.get("launched"):
        recipient_state["last_dispatched_signature"] = dispatched_signature
elif recipient == "loyal-opposition" and not dry_run:
    if launch.get("launched") and launch.get("exit_code") == 0:
        recipient_state["last_dispatched_signature"] = dispatched_signature
```

2. **Failure tracking:** Add `failed_dispatches` counter and `last_failure_reason` to dispatch state per-recipient:

```python
if not launch.get("launched") or launch.get("exit_code") != 0:
    recipient_state["failed_dispatches"] = recipient_state.get("failed_dispatches", 0) + 1
    recipient_state["last_failure_reason"] = launch.get("reason", "unknown")
else:
    recipient_state["failed_dispatches"] = 0
```

3. **Retry logic:** Allow re-dispatch after fatal errors (configurable max retries, default 3):

```python
failed_count = recipient_state.get("failed_dispatches", 0)
max_retries = int(os.environ.get("OLLAMA_MAX_RETRIES", "3"))
if failed_count > 0 and failed_count <= max_retries:
    should_dispatch = True  # Force re-dispatch even if signature matches
```

4. **Circuit breaker:** Prevent infinite retry loops:

```python
if failed_count > max_retries:
    recipient_state["circuit_breaker_active"] = True
    recipient_state["last_result"] = "circuit_breaker"
    should_dispatch = False
```

5. **Reset command:** Add `--reset-recipient` CLI argument to clear dispatch state and circuit breaker:

```python
parser.add_argument("--reset-recipient", choices=["loyal-opposition", "prime-builder"],
                    help="Reset dispatch state for recipient")
```

### 3.2 Foundation Stabilization: Diagnose Mode Enhancement

**File:** `scripts/cross_harness_bridge_trigger.py`

**Defect:** The `--diagnose` mode reports HEALTHY despite 3,495 accumulated failures and 14 stranded bridge entries. It checks dispatch-state currency but does not cross-reference actual pending entries.

**Fix:**

1. **Cross-reference pending entries:** Read live `bridge/INDEX.md` and compare pending count to `pending_count` in dispatch state:

```python
def _emit_diagnose_summary(state_dir: Path, include_rotated_failures: bool) -> str:
    # ... existing logic ...
    
    # Cross-reference with live bridge/INDEX.md
    bridge_index = project_root / "bridge" / "INDEX.md"
    if bridge_index.is_file():
        index_content = bridge_index.read_text()
        live_pending = sum(1 for line in index_content.splitlines() 
                          if line.startswith("NEW:") or line.startswith("REVISED:"))
        if live_pending > 0 and recipient_state.get("pending_count", 0) == 0:
            lines.append(f"- WARNING: {live_pending} bridge entries pending in INDEX.md but dispatch-state shows 0")
    
    # Report accumulated failures
    failure_log = state_dir / "dispatch-failures.jsonl"
    if failure_log.is_file():
        failure_count = sum(1 for _ in failure_log.open())
        if failure_count > 100:
            lines.append(f"- DEGRADED: {failure_count} accumulated dispatch failures")
```

2. **Report circuit breaker state:** If `circuit_breaker_active` is true, report it explicitly:

```python
if recipient_state.get("circuit_breaker_active"):
    lines.append(f"- CIRCUIT BREAKER ACTIVE: {failed_count} consecutive failures, manual reset required")
```

### 3.3 P2.5 Verification Spike

**File:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SPIKE-BRIDGE-TRIGGER-HEADLESS-GOVERNANCE-2026-06-08.md`

**Objective (per -006 §3):** Gather empirical evidence on whether `claude -p` / `codex exec` can preserve the same governance envelope as interactive sessions.

**Spike plan:**

1. **Test 1: Claude `-p` with hooks**
   - Command: `claude -p "Read bridge/INDEX.md and report the count of NEW entries" --add-dir E:\GT-KB`
   - Evidence to capture:
     - Did PreToolUse hooks fire? (check hook logs)
     - Did PostToolUse hooks fire? (check hook logs)
     - Did credential-scan, scanner-safe-writer, bridge-compliance-gate hooks execute?
     - Token cost (prompt + completion)
     - Wall-clock duration
     - Exit code

2. **Test 2: Claude `-p` with `--bare` (no hooks)**
   - Command: `claude -p "Read bridge/INDEX.md and report the count of NEW entries" --bare`
   - Evidence to capture: Same as Test 1, but expect hooks NOT to fire
   - This tests the `--bare` governance-context risk identified in -005

3. **Test 3: Codex `exec` with hooks**
   - Command: `codex exec "Read bridge/INDEX.md and report the count of NEW entries" --cd E:\GT-KB`
   - Evidence to capture:
     - Did PostToolUse hooks fire? (check `.codex/hooks.json` registration)
     - Did Stop hooks fire?
     - Token cost, wall-clock duration, exit code

4. **Test 4: Codex `exec` headless (no hooks expected per ADR-CODEX-HOOK-PARITY-FALLBACK-001)**
   - Same command as Test 3, but on Windows where Codex hooks are not active
   - Evidence to capture: Confirm hooks do NOT fire (expected per ADR)

**Success criteria for P2.5:**

- Claude `-p` preserves governance envelope (hooks fire, same as interactive) → **GO for P3 Claude invoker**
- Claude `-p --bare` does NOT preserve governance envelope → **P3 must never use `--bare`**
- Codex `exec` preserves governance envelope on POSIX → **GO for P3 Codex invoker on POSIX**
- Codex `exec` does NOT preserve governance envelope on Windows → **P3 Codex invoker deferred on Windows; CI gate covers gap**

**Evidence requirements (per -006 §3):**

- Command invocation (exact command string)
- Exit code
- stdout/stderr (truncated to relevant portions)
- Files changed (if any)
- Token cost (prompt + completion)
- Wall-clock duration

**Deliverable:** Spike report filed at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SPIKE-BRIDGE-TRIGGER-HEADLESS-GOVERNANCE-2026-06-08.md` with all evidence captured. Spike report becomes the basis for P3 invoker bridge proposal (if evidence supports GO).

### 3.4 Test Contract

**File:** `tests/framework/test_cross_harness_trigger_dispatch_recovery.py`

- `test_dry_run_does_not_update_signature`: Verify dry-run mode does not write `last_dispatched_signature`
- `test_failed_dispatch_increments_counter`: Verify `failed_dispatches` increments on launch failure
- `test_successful_dispatch_resets_counter`: Verify `failed_dispatches` resets to 0 on success
- `test_retry_logic_forces_redispatch`: Verify retry logic forces re-dispatch when `failed_count > 0`
- `test_circuit_breaker_activates_after_max_retries`: Verify circuit breaker activates after 3 consecutive failures
- `test_reset_recipient_clears_state`: Verify `--reset-recipient` clears dispatch state and circuit breaker

**File:** `tests/framework/test_cross_harness_trigger_diagnose.py`

- `test_diagnose_reports_healthy_when_current`: Verify HEALTHY when dispatch state is current
- `test_diagnose_reports_degraded_when_failures_accumulate`: Verify DEGRADED when >100 failures
- `test_diagnose_reports_circuit_breaker`: Verify circuit breaker state reported explicitly
- `test_diagnose_cross_references_bridge_index`: Verify warning when INDEX.md has pending entries but dispatch-state shows 0

**Test mapping:** Each test derives from REQ-BRIDGE-TRIGGER-EVENT-DRIVEN-001 FR5-FR8 (dispatch state management, signature dedup) and REQ-BRIDGE-TRIGGER-CONCURRENCY-001 FR1-FR3 (spawn locking, stale-transition checks).

---

## 4. Acceptance Criteria

1. Dry-run mode does not update `last_dispatched_signature`
2. Failed dispatches increment `failed_dispatches` counter
3. Successful dispatches reset `failed_dispatches` to 0
4. Retry logic forces re-dispatch after fatal errors (up to max retries)
5. Circuit breaker activates after max retries
6. `--reset-recipient` command clears state and circuit breaker
7. `--diagnose` reports DEGRADED when >100 failures
8. `--diagnose` reports circuit breaker state explicitly
9. `--diagnose` cross-references bridge/INDEX.md pending count
10. All dispatch recovery tests pass (6 tests)
11. All diagnose enhancement tests pass (4 tests)
12. P2.5 spike executed with all 4 tests (Claude `-p`, Claude `-p --bare`, Codex `exec`, Codex `exec` on Windows)
13. Spike report filed with all evidence captured per -006 §3 requirements

---

## 5. Risk Assessment

**Medium risk:** This modifies the dispatch state machine, which is critical infrastructure. Fail-closed semantics ensure conservative behavior, but incorrect state transitions could strand bridge entries or cause infinite retry loops.

**Mitigation:**
- Comprehensive test coverage (10 tests) validates all state transitions
- Circuit breaker prevents infinite retry loops
- `--reset-recipient` command provides manual recovery path
- P2.5 spike is read-only (no production dispatches; evidence gathering only)

**P2.5 spike risk:** The spike may reveal that headless invocations cannot preserve governance envelope, which would block P3 invoker design. This is an acceptable risk — the spike exists precisely to gather this evidence before committing to P3.

---

## 6. Implementation Constraints

- **Foundation stabilization must land before P2.5 spike:** The dispatch-state recovery defect must be fixed before the spike can produce meaningful evidence
- **P3 invoker explicitly gated:** Do not implement P3 invoker behavior until P2.5 spike is reviewed and GO'd
- **P1 detector independent:** P1 detector/parser has its own bridge thread; this proposal does not approve or block it
- **Isolated-worktree default for spawns:** Treat spawned implementation work as isolated-worktree by default unless Mike explicitly approves shared-worktree implementation spawns
- **Spike is read-only:** P2.5 spike does not dispatch production work; it only tests whether headless invocations preserve governance envelope

---

## 7. Verification Plan

1. Run `pytest tests/framework/test_cross_harness_trigger_dispatch_recovery.py -v`
2. Run `pytest tests/framework/test_cross_harness_trigger_diagnose.py -v`
3. Run `python scripts/cross_harness_bridge_trigger.py --diagnose` on live state, verify DEGRADED report
4. Run `python scripts/cross_harness_bridge_trigger.py --dry-run --verbose` on live state, verify signature not updated
5. Execute P2.5 spike tests 1-4, capture all evidence
6. File spike report at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SPIKE-BRIDGE-TRIGGER-HEADLESS-GOVERNANCE-2026-06-08.md`

---

## 8. Owner Decisions / Input

**None required for this slice.** Owner decisions captured in program GO `-007`. The P2.5 spike may produce evidence that requires owner decisions for P3 invoker design, but that is out of scope for this proposal.

---

## 9. Reversibility

This slice is additive (new tests, new CLI argument, new diagnose enhancements). Foundation stabilization modifies `scripts/cross_harness_bridge_trigger.py` but is backward-compatible (new fields are optional, existing dispatch state files work without modification). P2.5 spike is read-only and produces only a report file.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
