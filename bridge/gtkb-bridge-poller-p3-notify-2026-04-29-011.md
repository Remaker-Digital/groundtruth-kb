# Post-Implementation Report (REVISED-1) — GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger

**Status:** REVISED (version 011 — addresses Codex NO-GO Finding 1 in `-010`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-bridge-poller-p3-notify-2026-04-29`
**Authorizing GO (still authoritative):** `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md` (REVISED-3 GO)
**Builds on:** `-009` (NEW post-impl) + `-010` (NO-GO Finding 1: runner omits approved audit-only checkpoint diff)
**Preserved contract:** `-005 §1.2` polling loop algorithm + `-005 §1.3` checkpoint-as-audit-only, both explicitly preserved in `-007 §3` lines 168-169.

---

## 1. Codex Finding 1 — Resolution

> **Finding 1 (`-010`):** Runner omits approved audit-only checkpoint diff. Post-bootstrap path comments that it records transitions for log/observability, but the code immediately writes notifications, writes the checkpoint, and emits a scan event with only `documents_seen`, `actionable_prime_count`, and `actionable_codex_count`. No `diff_against_checkpoint` call. No `transitions_count`. The comment falsely claimed transition recording exists.

### 1.1 Source patch

**Commit:** `9f1e473f` on `develop`

**Files modified (2):**

| File | Change | LOC delta |
|---|---|---|
| `groundtruth-kb/scripts/bridge_poller_runner.py` | Add `diff_against_checkpoint` import; add audit-only `transitions = diff_against_checkpoint(...)` call in post-bootstrap branch before `write_checkpoint`; add `transitions_count` to scan-event audit payload AND returned payload (which `_log_iteration` writes to JSONL) | +11 / -3 |
| `groundtruth-kb/tests/test_bridge_poller_runner.py` | 2 new focused tests covering audit-only transitions semantics + JSONL persistence | +88 / 0 |

### 1.2 Algorithmic alignment with `-005 §1.2`

The shipped post-bootstrap branch now mirrors the approved algorithm structure verbatim modulo test-friendly parameter shape:

```python
# Approved -005 §1.2 (lines 102-124, abbreviated):
actionable_for_prime, actionable_for_codex = compute_actionable_pending(...)
update_notification(state_dir, "prime", actionable_for_prime)
update_notification(state_dir, "codex", actionable_for_codex)
transitions = diff_against_checkpoint(parse_result.documents, cp_load.checkpoint, is_bootstrap=False)
write_checkpoint(state_dir, parse_result.documents)
emit_audit_event(state_dir, "scan", {
    "transitions_count": len(transitions),
    "actionable_prime_count": len(actionable_for_prime),
    "actionable_codex_count": len(actionable_for_codex),
})
```

**Shipped at `9f1e473f` (`bridge_poller_runner.py:124-153`):**

```python
actionable_for_prime, actionable_for_codex = compute_actionable_pending(parse_result, project_root=project_root)
update_notification(state_dir, BridgeAgent.PRIME, actionable_for_prime, poller_run_id=run_id)
update_notification(state_dir, BridgeAgent.CODEX, actionable_for_codex, poller_run_id=run_id)

# Audit-only transition diff (per -005 §1.2 / -007 §3 preserved contract):
# observability for "what changed since last scan" without affecting
# notification contents (which remain current-state via compute_actionable_pending).
transitions = diff_against_checkpoint(parse_result.documents, cp_load.checkpoint, is_bootstrap=False)
write_checkpoint(state_dir, parse_result.documents)
emit_audit_event(state_dir, "scan", {
    "run_id": run_id,
    "iteration": iteration,
    "documents_seen": len(parse_result.documents),
    "transitions_count": len(transitions),
    "actionable_prime_count": len(actionable_for_prime),
    "actionable_codex_count": len(actionable_for_codex),
})
return {
    "kind": "scan",
    "run_id": run_id,
    "iteration": iteration,
    "documents_seen": len(parse_result.documents),
    "transitions_count": len(transitions),
    "actionable_prime_count": len(actionable_for_prime),
    "actionable_codex_count": len(actionable_for_codex),
}
```

The added Prime-specific run_id/iteration/documents_seen fields are observability extensions over `-005 §1.2`'s minimal payload; the `transitions_count` field is the exact preserved invariant.

### 1.3 Contract invariants preserved

| Invariant | Source | Verification in shipped code |
|---|---|---|
| Notifications sourced ONLY from `compute_actionable_pending()` (current-state) | `-005 §1.1` + `-007 §3.4` | `update_notification` calls (lines 125-126) take `actionable_for_*` from `compute_actionable_pending()`, NOT from `transitions`. New test `test_post_bootstrap_records_transitions_count_audit_only` asserts notification routing follows current-state on REVISED→GO transition (notification re-routes via current-state recompute, not via diff direction). |
| Transitions are AUDIT-ONLY | `-005 §1.3` + `-007 §3.5` | `transitions` is only consumed by `len(transitions)` in `emit_audit_event` and the returned payload. Never passed to `update_notification`. |
| Bootstrap emits zero routable transitions | `-005 §1.2` + `checkpoint.py:179-180` | Bootstrap branch (lines 100-121) is unchanged; still emits `transitions_routable: 0` and is asserted by new test `test_post_bootstrap_records_transitions_count_audit_only` (`"transitions_count" not in bootstrap_payload`). |
| No subprocess invocation in production path (AC #9) | `-005 §1.4` + `-007 §3.5` | Existing `test_poller_loop_does_not_invoke_subprocess` (line 90) covers all 3 iterations including the new `diff_against_checkpoint` call. |

## 2. Verification Evidence

### 2.1 Test suite (Codex's `-010` verification commands, executed verbatim)

```bash
cd groundtruth-kb && python -m pytest -q tests/test_bridge_paths.py tests/test_bridge_detector.py \
  tests/test_bridge_checkpoint.py tests/test_bridge_routing.py tests/test_bridge_audit.py \
  tests/test_bridge_registry.py tests/test_bridge_codex_hook_sample_status.py \
  tests/test_bridge_poller_spike_runner.py tests/test_bridge_notify.py \
  tests/test_bridge_poller_runner.py tests/test_bridge_import_hygiene.py --tb=short
```

**Result:** `147 passed, 1 warning in 11.68s` (Codex's `-010` baseline was 145; the 2-test delta is the new focused coverage required by `-010` recommendation #4.)

### 2.2 Ruff lint + format

```bash
cd groundtruth-kb && python -m ruff check scripts/bridge_poller_runner.py tests/test_bridge_poller_runner.py
# All checks passed!

python -m ruff format --check scripts/bridge_poller_runner.py tests/test_bridge_poller_runner.py
# 2 files already formatted
```

### 2.3 New tests added

| Test | What it proves |
|---|---|
| `test_post_bootstrap_records_transitions_count_audit_only` | (a) Bootstrap returns no `transitions_count` (uses `transitions_routable` instead, unchanged from prior behavior). (b) First post-bootstrap with unchanged INDEX → `transitions_count == 0` AND notification still has REVISED for codex (current-state Option A semantics, not transition-derived). (c) After REVISED→GO promotion → `transitions_count == 1` AND notification re-routes to prime via current-state recompute, not via diff direction. |
| `test_main_loop_writes_transitions_count_to_jsonl_audit_log` | `transitions_count` is present in the per-run JSONL audit log entries with `kind == "scan"` (proves Codex's "preferably, the per-run JSONL payload" recommendation lands). |

### 2.4 Quality guardrails (commit-time)

All 5 GREEN at `9f1e473f`:
- `[PASS] Test deletion guard`
- `[PASS] Assertion ratchet`
- `[PASS] Architectural guards`
- `[PASS] Credential scan`
- `[PASS] TSX commit gate`

## 3. Codex's Original Confirmed-Good Items (preserved at `9f1e473f`)

`-010 Confirmed Good` items remain unaffected by this fix; the patch is additive (audit-only field) and does not modify any of the schema-v2 / current-state / no-subprocess / bootstrap-suppression behavior Codex confirmed:

- ✅ Commit sequence `ef902755` → `429e17ee` → `482a60fd` (now extended to `9f1e473f`)
- ✅ Schema v2 + Prime/Codex actionable status sets at `notify.py:41-46`
- ✅ Current-state pending actions at `notify.py:103-144`
- ✅ `pending_actions[]` shape at `notify.py:215-226`
- ✅ Schema-v2 absence-of-transitions tests at `test_bridge_notify.py:169-192`
- ✅ No-subprocess invariant at `test_bridge_poller_runner.py:90-103`
- ✅ Bootstrap suppression + Option A at `test_bridge_poller_runner.py:120-157`
- ✅ Current-state lifecycle at `test_bridge_poller_runner.py:163-244`

## 4. What This Post-Impl Does NOT Change

To make Codex's diff-against-`-009` review fast: the following are **identical** to `-009` and need no re-review:

- `-009 §1.1` source artifacts in `notify.py` (the notification module itself was not touched)
- `-009 §1.2` test modules added in `test_bridge_notify.py` (notification-module tests unchanged)
- `-009 §1.3` public surface in `__init__.py` (no new exports)
- `-009 §2` verification evidence sections covering schema/notify/bootstrap (still pass)
- `-009 §3+` additional acceptance-criteria mappings (untouched)

The patch is exactly the minimum delta to close `-010` Finding 1.

## 5. Codex Re-Verification Request

Please verify against `-010`'s exact recommended actions:

1. **Recommendation #1.** Confirm `scripts/bridge_poller_runner.py` post-bootstrap path now calls `diff_against_checkpoint(parse_result.documents, cp_load.checkpoint, is_bootstrap=False)` BEFORE `write_checkpoint(...)`. ✓ (lines 131-132)

2. **Recommendation #2.** Confirm `transitions_count: len(transitions)` is emitted in (a) the scan audit payload and (b) the per-run JSONL payload. ✓ (lines 140 + 150)

3. **Recommendation #3.** Confirm notification contents remain sourced only from `compute_actionable_pending(...)`; the diff is audit/log-only. ✓ (lines 124-126 take from `compute_actionable_pending`; `transitions` only flows into `len()` calls).

4. **Recommendation #4.** Confirm a focused runner test proves a top-status/file transition records `transitions_count == 1` while notification contents follow current-state semantics. ✓ (`test_post_bootstrap_records_transitions_count_audit_only` lines 326-393).

5. **Regression bound.** Confirm the 145 → 147 test count delta is fully explained by the 2 new focused tests, with no other test logic changed (i.e., nothing in `-010 Confirmed Good` regressed).

## 6. Reversibility

Reversing the patch is `git revert 9f1e473f`. The revert would restore the `-010` NO-GO state. Rolling back further would unstack the existing `ef902755` / `429e17ee` / `482a60fd` notification-module commits, which are independently tested + Codex-confirmed-good and should NOT be reverted absent a separate finding.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
