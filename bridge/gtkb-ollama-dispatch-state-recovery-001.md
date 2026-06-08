# Bridge Proposal: Ollama Dispatch-State Recovery (Phase 4)

**Status:** NEW  
**Author:** Prime Builder  
**Date:** 2026-06-08  
**Bridge ID:** gtkb-ollama-dispatch-state-recovery  
**Priority:** HIGH  
**Related Work:** gtkb-ollama-lo-prompt-hardening

---

## Problem Statement

The cross-harness bridge trigger has a critical state-management bug that prevents recovery after worker failures:

1. **Signature lock-in:** When Ollama dispatches fail (turn exhaustion, guard denials, crashes), the dispatch state records `last_dispatched_signature` even though the work was not completed.

2. **No retry mechanism:** Subsequent trigger runs see the signature as "unchanged" and skip re-dispatch, even though the bridge entry is still in NEW/REVISED state and needs review.

3. **Dry-run pollution:** Dry-run invocations (`--dry-run`) update `last_dispatched_signature`, preventing future real dispatches until manual state reset.

4. **Manual intervention required:** The only current recovery path is manual editing of `.gtkb-state/bridge-poller/dispatch-state.json`, which is error-prone and breaks automation.

**Evidence:** On 2026-06-07, 14 bridge entries were stranded in NEW/REVISED state because:
- Initial dispatches failed (turn exhaustion, guard denials)
- `last_dispatched_signature` was recorded
- Subsequent trigger runs returned "unchanged" instead of retrying
- Manual Phase 1 reset was overwritten by a verification dry-run

---

## Root Cause Analysis

The trigger's dispatch logic at line 2157 in `scripts/cross_harness_bridge_trigger.py`:

```python
if recipient != "prime-builder" or dry_run or launch.get("launched"):
    recipient_state["last_dispatched_signature"] = dispatched_signature
```

This writes the signature in three cases:
1. Loyal Opposition dispatches (always)
2. Dry-run mode (always)
3. Prime Builder launches that succeeded

**Problems:**
- **Case 1:** Should only write signature if the launch succeeded, not if it failed
- **Case 2:** Should never write signature in dry-run mode (dry-run is read-only)
- **Missing:** No mechanism to detect and retry failed dispatches

---

## Proposed Solution

### Change 1: Only record signature on successful launch

Modify the signature-write condition:

```python
# Only record signature if launch succeeded (or for prime-builder non-dry-run)
if recipient == "prime-builder" and not dry_run:
    if launch.get("launched"):
        recipient_state["last_dispatched_signature"] = dispatched_signature
elif recipient == "loyal-opposition" and not dry_run:
    if launch.get("launched") and launch.get("exit_code") == 0:
        recipient_state["last_dispatched_signature"] = dispatched_signature
```

**Rationale:**
- Dry-run must never update signature (read-only operation)
- Loyal Opposition signature should only update if the worker exited successfully (exit code 0)
- Prime Builder signature updates on launch (existing behavior, unchanged)

### Change 2: Add failure tracking

Add a `failed_dispatches` counter to the dispatch state:

```python
if not launch.get("launched") or launch.get("exit_code") != 0:
    # Track failure
    if "failed_dispatches" not in recipient_state:
        recipient_state["failed_dispatches"] = 0
    recipient_state["failed_dispatches"] += 1
    recipient_state["last_failure_reason"] = launch.get("reason", "unknown")
else:
    # Reset failure counter on success
    recipient_state["failed_dispatches"] = 0
```

### Change 3: Implement retry logic

Add retry logic for failed dispatches:

```python
# Check if we should retry a failed dispatch
failed_count = recipient_state.get("failed_dispatches", 0)
max_retries = 3  # Configurable via environment variable
if failed_count > 0 and failed_count <= max_retries:
    # Force re-dispatch even if signature matches
    should_dispatch = True
    log.info(f"Retrying failed dispatch ({failed_count}/{max_retries})")
```

### Change 4: Add circuit breaker

Prevent infinite retry loops:

```python
if failed_count > max_retries:
    recipient_state["circuit_breaker_active"] = True
    recipient_state["last_result"] = "circuit_breaker"
    log.warning(f"Circuit breaker activated after {failed_count} failures")
    should_dispatch = False
```

### Change 5: Add state reset command

Add a CLI command to reset dispatch state:

```python
# New command: python scripts/cross_harness_bridge_trigger.py --reset-recipient loyal-opposition
if args.reset_recipient:
    dispatch_state["recipients"][args.reset_recipient]["last_dispatched_signature"] = None
    dispatch_state["recipients"][args.reset_recipient]["failed_dispatches"] = 0
    dispatch_state["recipients"][args.reset_recipient]["circuit_breaker_active"] = False
    _write_dispatch_state(dispatch_state)
    print(f"Reset dispatch state for {args.reset_recipient}")
```

---

## Implementation Details

### File: `scripts/cross_harness_bridge_trigger.py`

**Location 1:** Line 2157 (signature-write condition)
- Replace the current condition with the new logic from Change 1
- Add failure tracking from Change 2

**Location 2:** Line 1890-1920 (dispatch decision logic)
- Add retry logic from Change 3
- Add circuit breaker from Change 4

**Location 3:** Argument parser (line 2400-2450)
- Add `--reset-recipient` argument from Change 5

### Configuration

Add environment variables for retry behavior:

```python
OLLAMA_MAX_RETRIES = int(os.environ.get("OLLAMA_MAX_RETRIES", "3"))
OLLAMA_RETRY_DELAY_SECONDS = int(os.environ.get("OLLAMA_RETRY_DELAY_SECONDS", "300"))
```

---

## Testing Plan

1. **Dry-run test:**
   ```bash
   python scripts/cross_harness_bridge_trigger.py --dry-run
   ```
   Verify `last_dispatched_signature` is NOT updated.

2. **Failure tracking test:**
   - Simulate a worker failure (e.g., invalid model name)
   - Verify `failed_dispatches` counter increments
   - Verify next trigger run attempts retry

3. **Circuit breaker test:**
   - Simulate 4 consecutive failures
   - Verify `circuit_breaker_active` is set
   - Verify no further dispatches until reset

4. **Reset command test:**
   ```bash
   python scripts/cross_harness_bridge_trigger.py --reset-recipient loyal-opposition
   ```
   Verify state is reset and dispatches resume.

5. **Integration test:**
   - Dispatch a bridge entry with a known-good configuration
   - Verify successful completion resets failure counter

---

## Risk Assessment

**Risk Level:** MEDIUM

- **Risk:** Retry logic may cause excessive dispatch attempts
  - **Mitigation:** Circuit breaker limits retries to 3; configurable via environment variable
  - **Monitoring:** Dispatch logs will show retry attempts

- **Risk:** Exit code 0 may not indicate true success (worker could fail silently)
  - **Mitigation:** Phase 3 (prompt hardening) ensures workers report errors explicitly
  - **Fallback:** Manual reset command available if circuit breaker triggers incorrectly

- **Risk:** Breaking change for Prime Builder dispatch behavior
  - **Mitigation:** Prime Builder logic unchanged (only Loyal Opposition gets exit-code check)
  - **Testing:** Verify Prime Builder dispatches still work as before

---

## Acceptance Criteria

- [ ] Dry-run mode never updates `last_dispatched_signature`
- [ ] Failed Loyal Opposition dispatches increment `failed_dispatches` counter
- [ ] Failed dispatches are retried up to 3 times (configurable)
- [ ] Circuit breaker activates after max retries
- [ ] `--reset-recipient` command resets state and clears circuit breaker
- [ ] Successful dispatches reset failure counter to 0
- [ ] Prime Builder dispatch behavior unchanged
- [ ] No manual state file editing required for recovery

---

## Migration Plan

**Backward compatibility:** The new fields (`failed_dispatches`, `circuit_breaker_active`) are optional. Existing dispatch state files will work without modification.

**One-time cleanup:** After deployment, run:
```bash
python scripts/cross_harness_bridge_trigger.py --reset-recipient loyal-opposition
```
to clear any stranded state from previous failures.

---

## Related Work

- `gtkb-ollama-lo-prompt-hardening` (Phase 3) — Complements this proposal by reducing worker failures
- `gtkb-smart-poller-p1-p2-implementation` — Smart poller may need similar retry logic if re-enabled

---

## Decision Required

**OWNER ACTION REQUIRED**

Approve this proposal for implementation?

**Why it matters:** This prevents future dispatch-state lock-in and eliminates the need for manual state file editing. Combined with Phase 3, it creates a robust, self-healing dispatch system.

**Expected reply:** APPROVE / REJECT / REQUEST_CHANGES
