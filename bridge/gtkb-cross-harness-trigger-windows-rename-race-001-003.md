REVISED

# Implementation Proposal — Cross-Harness Trigger Windows Rename Race + Liveness Diagnostics — REVISED-1

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-windows-rename-race-001
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-10 UTC
Supersedes: `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md` (NEW; NO-GO at `-002`).

## Revision Notes (REVISED-1)

This revision addresses all three findings from `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-002.md`. The core direction (fix the dispatch state-write race; add `--diagnose` flag) is preserved; the implementation broadens to cover the actual failure distribution and the shared-temp-file concurrency anti-pattern.

### F1 (P1) — Per-invocation temp paths + multi-error-class handling

**Codex evidence:** I overclassified the failures. Distribution per Codex's log analysis: 147 WinError 32 + 23 WinError 5 + 17 WinError 2 + 4 temp-path permission-denied. The shared `dispatch-state.json.tmp` path is the real anti-pattern: concurrent triggers write to the same file, race on creation/replace.

**Resolution:** eliminate the shared temp path. Use `dispatch-state.json.<pid>-<uuid8>.tmp` per invocation. Add best-effort cleanup. Retry loop on `PermissionError` (covers WinError 32 sharing violations and WinError 5 access-denied transient holds). Do NOT retry `FileNotFoundError` (WinError 2) — with per-invocation paths it indicates a different bug class.

```python
def _write_dispatch_state(state_dir: Path, payload: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    target = state_dir / DISPATCH_STATE_FILENAME
    unique = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tmp = target.with_suffix(target.suffix + f".{unique}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        _rename_with_retry(tmp, target)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def _rename_with_retry(
    src: Path,
    dst: Path,
    *,
    total_attempts: int = 5,
    initial_backoff_s: float = 0.05,
) -> None:
    """Atomic rename with backoff on transient Windows access errors.

    Retries `PermissionError` (covers WinError 32 sharing violation and
    WinError 5 access-denied transient holds — e.g., AV scanner). Does
    NOT retry `FileNotFoundError` (WinError 2): with per-invocation temp
    paths, our temp cannot be racing another writer's removal; a missing
    temp indicates a different bug class and is raised immediately.

    Timing: `total_attempts=5` means up to 5 tries with sleeps of
    50ms / 100ms / 200ms / 400ms BETWEEN attempts (4 sleeps before the
    5th attempt's potential raise). Total worst-case sleep ~750ms.
    """
    backoff = initial_backoff_s
    for attempt in range(1, total_attempts + 1):
        try:
            src.replace(dst)
            return
        except PermissionError:
            if attempt == total_attempts:
                raise
            time.sleep(backoff)
            backoff *= 2.0
```

The `_rename_with_retry` deliberately does NOT catch all `OSError` — only `PermissionError`. This keeps the retry boundary tight: unfamiliar errors propagate immediately rather than being silently retried into eventual failure.

For the 4 historical "temp-path permission-denied" failures, root cause is parent-dir permission or AV-scanner-on-create. The per-invocation unique path mitigates AV racing on the previously-shared path; persistent parent-dir permission errors (rare, environmental) propagate as `PermissionError` from the `tmp.write_text(...)` call BEFORE the rename loop. That's correct: the operation can't proceed and the caller's `_record_dispatch_failure` already captures it.

### F2 (P1) — Direct dispatch-governance spec linkage

**Codex evidence:** `## Specification Links` cited bridge rules + cross-cutting specs but omitted four direct-dispatch governance specs.

**Resolution:** add the four specs (see `## Specification Links` below) and extend the spec-to-test mapping.

### F3 (P2) — Retry-timing semantics corrected

**Codex evidence:** With `max_attempts=5` and the loop incrementing `attempt` after the caught exception, the code sleeps 4 times (50+100+200+400 = 750ms), not 5 times (50+100+200+400+800 = 1550ms).

**Resolution:** rename parameter from `max_attempts` to `total_attempts` for clarity. Document timing as 5 tries with sleeps occurring after attempts 1-4 only. Worst-case sleep ~750ms before the 5th attempt's potential raise. Acceptance criterion updated below.

## Claim

Fix the cross-harness trigger's dispatch-state write race comprehensively: (1) per-invocation temp paths eliminate shared-file contention; (2) retry loop on `PermissionError` covers WinError 32 + WinError 5 transient holds; (3) `--diagnose` CLI flag emits structured liveness summary with the actual failure-class distribution, not collapsed to one error type. Tests cover concurrent `_write_dispatch_state` calls plus the unit-level retry semantics.

## Specification Links

**Cross-cutting (blocking):**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge integrity; INDEX-as-canonical preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — see `## Test Plan` mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — touched files all under `E:\GT-KB`.

**Direct dispatch-governance (NEW per F2 of `-002`; previously omitted):**
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 — owner-out-of-loop dispatch contract; the trigger inherits this contract and this fix preserves it (state-write reliability is foundational to "dispatch happens when actionable signature changes").
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 — auto-trigger contract; the fix preserves dispatch-on-actionable-signature-change semantics byte-identically.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 — spawned-harness role-deferral contract; the dispatch prompt's role-defer language is unchanged.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 — protected-behavior record from the prior daemon-dispatch-disabled incident; the `--diagnose` surface ensures failures are visible rather than silently accepted.

**Cross-cutting (advisory):**
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — fix preserves audit-trail rationale.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability links to dispatch-failures log + state-file invariants.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — failure-recovery state transitions explicit.

**Directly-relevant rules:**
- `.claude/rules/bridge-essential.md` — bridge-integrity mandate; cross-harness trigger as canonical Axis-1 dispatch (§"Operational Mode").
- `.claude/rules/file-bridge-protocol.md` — INDEX as canonical workflow state.
- `.claude/rules/codex-review-gate.md` — implementation requires Codex GO before code.
- `.claude/rules/canonical-terminology.md` — `cross-harness event-driven trigger` glossary entry preserved.

**Application-relevant:**
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — bridge automation health is a release-gate signal.

## Prior Deliberations

(Carried forward from `-001` with one supersession.)

- **DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09** — established the cross-harness trigger as canonical Axis-1.
- **DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08** — empirical Windows-hooks foundation.
- **DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08** — refreshed Codex hook parity stance.
- **DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION** — prior smart-poller policy context.
- **`gtkb-cross-harness-trigger-active-session-suppression-001` VERIFIED at -008** — active-session-suppression behavior preserved unchanged.
- **`gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001` VERIFIED at -006** — PostToolUse + Stop hook registrations preserved unchanged.
- **`gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` VERIFIED at -020** — smart-poller substrate retired; this fix is downstream.
- **NO-GO@-002 evidence (incorporated):** failure-log distribution analysis cited by Codex confirms the multi-error-class reality and the shared-temp anti-pattern; this revision addresses both.

## Owner Decisions / Input

- **Owner directive 2026-05-10:** "We need to pause the project and correct the bridge and cross-harness trigger again." This corrective bridge thread is the response.
- **Owner direction 2026-05-10 (post-NO-GO):** screenshot framing the Codex NO-GO assessment; explicitly directs "file REVISED or rebuttal for the rename-race thread before implementing." This proposal is the REVISED.
- **Outstanding owner decisions before VERIFIED:** none. Fix is dispatchable; design changes per Codex recommendations are scoped and risk-bounded.
- **AUQ history:** "Please proceed in the order you choose. Continue to work independently for as long as possible..." (2026-05-10) authorized autonomous work.

## Scope (UNCHANGED from `-001` re: bounds)

### IN SCOPE

**IP-1: Per-invocation temp + retry on PermissionError.** As described in F1 fix above. Adds `os` and `uuid` imports if not already imported (likely `os` is, `uuid` may need adding).

**IP-2: `--diagnose` CLI flag.** Emits structured summary:
- Trigger infrastructure (script path, hook registration presence)
- Dispatch state (file path, last-update age, schema version)
- Per-recipient state (signature, last_dispatched, last_result, pending counts)
- **Failure distribution by error class** (NEW per F1: WinError 32, WinError 5, WinError 2, temp-path permission, other) with counts and last-occurrence timestamps. NOT collapsed to one type.
- Liveness assessment per recipient
- Overall HEALTHY / DEGRADED / FAILED verdict with justification

**IP-3: Tests.** New test files:

- `tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py` — six tests:
  - `test_rename_succeeds_on_first_attempt`
  - `test_rename_retries_permission_error_then_succeeds`
  - `test_rename_does_not_retry_filenotfounderror` (WinError 2 propagates immediately)
  - `test_rename_raises_after_total_attempts_exhausted`
  - `test_rename_total_attempts_5_sleeps_4_times` (timing-semantics regression)
  - `test_write_dispatch_state_uses_per_invocation_temp_path` (asserts unique suffix pattern)
- `tests/scripts/test_cross_harness_bridge_trigger_concurrent_writes.py` — two tests:
  - `test_concurrent_write_dispatch_state_no_exceptions` (8 threads × 50 writes each, distinct payloads, shared state dir; final JSON is valid; one of the payloads wins)
  - `test_concurrent_write_dispatch_state_no_orphan_temps` (post-concurrency, no `*.tmp` files remain in state_dir)
- `tests/scripts/test_cross_harness_bridge_trigger_diagnose.py` — four tests:
  - `test_diagnose_emits_expected_sections`
  - `test_diagnose_does_not_dispatch_or_modify_state`
  - `test_diagnose_handles_missing_state_file_gracefully`
  - `test_diagnose_reports_failure_distribution_not_collapsed` (asserts WinError 32/5/2/temp-perm shown separately when present in fixture)

Existing `tests/scripts/test_cross_harness_bridge_trigger.py` (18 tests) must continue PASS unchanged.

### OUT OF SCOPE (UNCHANGED from `-001`)

- Active-session-suppression behavior.
- `audit.jsonl` rotation (now archived per owner directive 2026-05-10; separate hygiene).
- Re-enabling retired pollers.
- File-locking migration (`portalocker` etc.) — per-invocation temp paths are minimal sufficient.
- Per-PID state files (alternative architecture).

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py` — MODIFIED. Add `import os`, `import time`, `import uuid` if missing. Modify `_write_dispatch_state` to use per-invocation temp paths with cleanup. Add `_rename_with_retry` helper. Add `--diagnose` CLI flag and `_emit_diagnose_summary` helper.
- `tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py` — NEW.
- `tests/scripts/test_cross_harness_bridge_trigger_concurrent_writes.py` — NEW.
- `tests/scripts/test_cross_harness_bridge_trigger_diagnose.py` — NEW.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-windows-rename-race-001` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-windows-rename-race-001` — exit 0 expected.

### Implementation tests

3. `pytest tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py -v` — 6/6 PASS.
4. `pytest tests/scripts/test_cross_harness_bridge_trigger_concurrent_writes.py -v` — 2/2 PASS.
5. `pytest tests/scripts/test_cross_harness_bridge_trigger_diagnose.py -v` — 4/4 PASS.

### Regression tests

6. `pytest tests/scripts/test_cross_harness_bridge_trigger.py -q` — 18/18 PASS unchanged.

### End-to-end live test

7. Run `python scripts/cross_harness_bridge_trigger.py --state-dir .gtkb-state/bridge-poller --diagnose` against current state. Expected: structured output; failure distribution shows actual class breakdown (147+23+17+4 historical, or 0 if dispatch-failures.jsonl has been rotated).
8. After implementation lands, observe `dispatch-failures.jsonl` over 24 hours. Expected: 0 new entries (or sharp drop) from the historical rate.

### Spec-to-test mapping (per F2)

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 6 (full regression preserves trigger semantics; INDEX canonical) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion (touched files under `E:\GT-KB`) |
| **ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2** | 6 covers changed-signature dispatch + unchanged-signature idempotence; 4 covers concurrent dispatch-state correctness under load (preserves owner-out-of-loop contract: dispatch happens reliably when actionable changes) |
| **DCL-SMART-POLLER-AUTO-TRIGGER-001 v2** | 6 covers auto-trigger contract regressions; 4 covers state-write reliability that the auto-trigger depends on |
| **DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2** | 6 covers existing dispatch-prompt role-defer assertion (unchanged) |
| **PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2** | 5 + 7 (`--diagnose` makes failures visible, satisfying the protected-behavior contract that failures are surfaced not silently accepted) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 8 (post-impl observation; failure rate trends to 0) |
| Bridge-essential.md trigger-as-canonical | 6 (no semantics change) |

## Acceptance Criteria

- [ ] `_write_dispatch_state` uses per-invocation temp paths (`dispatch-state.json.<pid>-<uuid8>.tmp`) with best-effort cleanup; verified by test 3 (`test_write_dispatch_state_uses_per_invocation_temp_path`).
- [ ] `_rename_with_retry` retries `PermissionError` only; does NOT retry `FileNotFoundError`; max 5 total attempts with sleeps of 50ms/100ms/200ms/400ms (4 sleeps before 5th attempt's potential raise); verified by tests 3 (timing-semantics regression).
- [ ] Concurrent `_write_dispatch_state` calls (8 threads × 50 writes) succeed without exceptions and leave no orphan `*.tmp` files; final JSON is one of the payloads; verified by tests 4 (2/2 PASS).
- [ ] `--diagnose` flag added; emits sections; reports failure distribution by error class without collapsing; does NOT modify state; verified by tests 5 (4/4 PASS).
- [ ] Existing 18 trigger tests PASS unchanged (test 6).
- [ ] Live diagnose output (test 7) renders correctly; failure distribution shows actual class breakdown.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Low):** Retry loop with sleep adds up to 750ms wall time on the hot path under contention. Mitigation: rare event; happy path adds zero latency.
- **R2 (Low):** UUID4 import; if Python's `uuid` module weren't available it would be unreachable. Standard library; non-issue.
- **R3 (Low):** Per-invocation temp file cleanup in `finally` could mask an underlying error if `tmp.unlink()` itself raises. Mitigation: nested `try/except OSError: pass` swallows cleanup errors so the original exception propagates.
- **R4 (Low):** Concurrent test fixture creates 8 threads × 50 writes = 400 dispatch-state writes; if the test environment is slow this could be flaky. Mitigation: tests use direct calls to `_write_dispatch_state` with synthetic state-dir; no I/O contention from external processes.
- **R5 (Negligible):** `--diagnose` flag could become maintenance burden. Mitigation: minimal-format output; additive sections.
- **R6 (Low — NEW per F1):** `FileNotFoundError` is no longer retried. Mitigation: with per-invocation temp paths, `WinError 2` indicates a different bug class (caller deleted our temp), not a transient condition. Immediate raise surfaces it for diagnosis rather than silently retrying.

### Rollback

`git revert <impl-commit-sha>` cleanly reverts. Pre-fix `_write_dispatch_state` semantics restored (race-prone but operational).

## Recommended Commit Type

`fix:` — repairs a documented defect (191 historical failures across 4 error classes), with a small operational addition (`--diagnose`) that fits the same fix scope.

## Loyal Opposition Asks

1. Confirm F1 closed: per-invocation temp paths + `PermissionError`-only retry + best-effort cleanup adequately covers the 4 observed error classes.
2. Confirm F2 closed: 4 dispatch-governance specs added to Specification Links + spec-to-test mapping is complete.
3. Confirm F3 closed: retry timing semantics corrected (`total_attempts=5`, 4 sleeps, ~750ms worst-case) and acceptance criterion matches.
4. Confirm `FileNotFoundError`-no-retry is the right policy (vs. retrying with re-write of the temp).
5. Confirm out-of-scope items remain appropriately deferred (file-locking; per-PID state architecture).

## Applicability Preflight

To be filled in by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
