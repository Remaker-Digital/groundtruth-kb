# Implementation Proposal — Cross-Harness Trigger Windows Rename Race + Liveness Diagnostics

bridge_kind: implementation_proposal
Document: gtkb-cross-harness-trigger-windows-rename-race-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-10 UTC
Trigger: Owner-directed pause + correction request after Codex assessment that "the cross-harness trigger is working partially, but not correctly enough to call the bridge fully functional."

## Claim

Fix the single substantive defect in `scripts/cross_harness_bridge_trigger.py`: the `tmp.replace(target)` atomic-rename in `_write_dispatch_state` has no retry loop, causing 191 documented `WinError 32: The process cannot access the file because it is being used by another process` failures (from 2026-05-08 to 2026-05-09) when concurrent trigger invocations race on the same target file. Add a Windows-aware retry loop with exponential backoff. Add a `--diagnose` CLI flag that emits a structured liveness assessment so future health probes don't require manually composing the assessment.

The owner-cited symptoms ("stale for hours earlier today", "Prime dispatch path not demonstrably functional") are downstream consequences of this single race: when the rename fails, the trigger logs to `dispatch-failures.jsonl` and exits without updating state. Subsequent triggers see stale state until the concurrency window clears.

The other findings in the owner's assessment are NOT defects:
- "Prime side `unchanged` and `counterpart_active_session_present`" is correct behavior — active-session-suppression is by design (per `gtkb-cross-harness-trigger-active-session-suppression-001` VERIFIED).
- "Selected_count: 2" is the `--max-items` cap, not a bug.
- "Codex auto-dispatch still running for -005" is the expected post-dispatch state; nothing to repair.

## Why Now

Per `bridge-essential.md`: "Bridge integrity is the top-priority task. Always." The owner explicitly paused other work-front items to correct this. The race is latent and will recur under load (e.g., when multiple bridge edits happen close together, which is the normal session pattern).

Diagnostic gap: the owner had to compose the assessment manually from raw `dispatch-state.json` + `dispatch-failures.jsonl` content. A `--diagnose` flag emitting a structured summary closes that diagnostic gap.

## Specification Links

**Cross-cutting (blocking):**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge integrity is the canonical workflow state machine.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — see `## Test Plan` mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — touched files all under `E:\GT-KB`; no `applications/` paths.

**Cross-cutting (advisory):**
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the fix preserves audit-trail rationale + verification evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability links the fix to the dispatch-failures log + state file invariants.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — failure-recovery state transitions are explicit.

**Directly-relevant rules and protocols:**
- `.claude/rules/bridge-essential.md` — bridge-integrity mandate; cross-harness event-driven trigger is the canonical Axis-1 dispatch (preserved unchanged).
- `.claude/rules/file-bridge-protocol.md` — INDEX.md as canonical workflow state.
- `.claude/rules/codex-review-gate.md` — implementation requires Codex GO before any code change.
- `.claude/rules/canonical-terminology.md` — glossary entries for `cross-harness event-driven trigger`, `smart poller` (retired), `OS poller` (retired) preserved.

**Application-relevant:**
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — bridge automation health is a release-gate-visible signal.

## Prior Deliberations

- **DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09** — established the cross-harness trigger as the canonical Axis-1 substrate. The trigger inherits the smart-poller's actionable-signature scheme byte-identically; this proposal does NOT change that scheme.
- **DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08** — confirmed Codex hooks fire on Windows; the cross-harness trigger is registered in `.codex/hooks.json` and `.claude/settings.json` PostToolUse + Stop.
- **`gtkb-cross-harness-trigger-active-session-suppression-001` VERIFIED at -008** — established the active-session-suppression behavior that the owner's assessment (correctly) identifies but misclassifies as a defect.
- **`gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001` VERIFIED at -006** — established the PostToolUse + Stop hook registrations.
- **`gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` VERIFIED at -020** — retired the smart-poller substrate.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` — seed=search; owner_conversation; Slice 4 smart-poller retirement: archive smart poller in favor of cross-harness 
- DA: `DELIB-1005` — seed=search; bridge_thread; GTKB-ISOLATION-015 - Loyal Opposition Verification Review
- DA: `DELIB-1115` — seed=search; bridge_thread; Bridge thread: gtkb-startup-enhancements-p1 (6 versions, VERIFIED)
- DA: `DELIB-1046` — seed=search; bridge_thread; Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Revision 1
- DA: `DELIB-1107` — seed=search; bridge_thread; Bridge thread: gtkb-dora-001b-track1-implementation (6 versions, GO)

## Owner Decisions / Input

- **Owner directive 2026-05-10:** "We need to pause the project and correct the bridge and cross-harness trigger again." Authorizes this corrective bridge thread as top-priority work. Other work-front items paused.
- **Outstanding owner decisions before VERIFIED:** none. The fix is dispatchable; the retry-loop approach is the standard Windows-rename pattern and does not introduce new architectural surfaces.
- **AUQ history (carried forward):** "Please proceed in the order you choose. Continue to work independently for as long as possible..." (2026-05-10) authorized autonomous work, but the owner has now explicitly redirected priority.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Add Windows-aware retry loop to `_write_dispatch_state`.**

Modify `scripts/cross_harness_bridge_trigger.py:_write_dispatch_state` (currently lines ~162-167):

```python
def _write_dispatch_state(state_dir: Path, payload: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    target = state_dir / DISPATCH_STATE_FILENAME
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _rename_with_retry(tmp, target)


def _rename_with_retry(
    src: Path,
    dst: Path,
    *,
    max_attempts: int = 5,
    initial_backoff_s: float = 0.05,
) -> None:
    """Atomic rename with exponential backoff on Windows file-in-use.

    On POSIX systems the rename is atomic and can never fail with file-in-use.
    On Windows, when another process briefly holds the target open (concurrent
    trigger invocations, doctor probe, AV scanner, etc.), `os.replace` raises
    `PermissionError` (WinError 32). The fix is to retry with exponential
    backoff; each attempt is cheap and the contention window is typically
    sub-second.
    """
    attempt = 0
    backoff = initial_backoff_s
    while True:
        try:
            src.replace(dst)
            return
        except PermissionError as exc:
            attempt += 1
            if attempt >= max_attempts:
                raise
            time.sleep(backoff)
            backoff *= 2.0
```

Default `max_attempts=5` and `initial_backoff_s=0.05` give total worst-case wait of ~50+100+200+400+800ms = 1.55s before raising. The contention window in observed failures is typically <100ms.

**IP-2: Add `--diagnose` CLI flag.**

Add a new flag to `scripts/cross_harness_bridge_trigger.py` argparse setup. When `--diagnose` is set, the script does NOT perform a dispatch run; instead it prints a structured summary and exits 0.

Output format:

```text
Cross-harness trigger diagnose — 2026-05-10T15:55:00Z

== Trigger infrastructure ==
- Script: scripts/cross_harness_bridge_trigger.py present.
- Hook registrations: .claude/settings.json PostToolUse + Stop OK; .codex/hooks.json PostToolUse + Stop OK.

== Dispatch state ==
- File: .gtkb-state/bridge-poller/dispatch-state.json
- Last update: 2026-05-10T15:49:21Z (6 minutes ago).
- Schema version: 1.

== Per-recipient state ==
- codex: last_result=no_pending, pending=0, selected=0
  signature 4f53cda1... (matches empty-actionable hash).
- prime: last_result=counterpart_active_session_present, pending=36, selected=2
  signature 2045e894... last_dispatched=2045e894... (suppression active).

== Recent failures ==
- Total in dispatch-failures.jsonl: 191.
- Last 5 timestamps: 2026-05-09T22:20:18Z, 2026-05-09T22:19:33Z, ...
- Most common error: PermissionError WinError 32 (191 of 191).

== Liveness ==
- Dispatch state file age: <60s; HEALTHY.
- Per-recipient liveness:
  - codex: actionable signature == last_dispatched (no pending work to dispatch).
  - prime: actionable signature == last_suppressed_signature (waiting for counterpart session to exit).
- Failure rate today: 0 (last failure 2026-05-09T22:20:18Z).
- Overall: HEALTHY (no current dispatch failures; recipients functioning per design).
```

The output is intentionally markdown-friendly so it can be pasted into chat or rendered in a dashboard.

**IP-3: Tests.**

New test files:

- `tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py` — three tests:
  - `test_rename_succeeds_on_first_attempt`
  - `test_rename_retries_on_permission_error_then_succeeds`
  - `test_rename_raises_after_max_attempts_exhausted`
- `tests/scripts/test_cross_harness_bridge_trigger_diagnose.py` — three tests:
  - `test_diagnose_emits_expected_sections`
  - `test_diagnose_does_not_dispatch_or_modify_state`
  - `test_diagnose_handles_missing_state_file_gracefully`

Existing `tests/scripts/test_cross_harness_bridge_trigger.py` (18 tests) must continue to PASS unchanged.

### OUT OF SCOPE

- **Active-session-suppression behavior:** unchanged. The owner's assessment correctly identified this behavior; it is not a defect. The diagnose output explains it explicitly so future probes don't misclassify it.
- **`audit.jsonl` rotation/trimming:** the file is not load-bearing for the trigger and does not affect dispatch correctness. Tracked separately in `GTKB-DETERMINISTIC-SERVICES-001` discoverability sub-project.
- **Re-enabling the retired smart poller or OS poller:** explicitly forbidden by `bridge-essential.md`.
- **Migrating to file-based locking (`portalocker` or similar):** retry loop is the minimal sufficient fix. File-locking would be a more invasive change requiring its own thread.
- **`dispatch-failures.jsonl` rotation:** the file is currently 60KB / 191 entries; small enough to ignore. If retry loop reduces failure rate to ~0, the file stops growing.
- **Per-PID state files (alternative architecture):** rejected as too invasive for this scope.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py` — MODIFIED. Add `_rename_with_retry` helper; replace the `tmp.replace(target)` call in `_write_dispatch_state`. Add `--diagnose` CLI flag and `_emit_diagnose_summary` helper. Add `import time` if not already imported.
- `tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py` — NEW.
- `tests/scripts/test_cross_harness_bridge_trigger_diagnose.py` — NEW.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-windows-rename-race-001` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-windows-rename-race-001` — exit 0 expected.

### Implementation tests

3. `pytest tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py -v` — 3/3 PASS.
4. `pytest tests/scripts/test_cross_harness_bridge_trigger_diagnose.py -v` — 3/3 PASS.

### Regression tests

5. `pytest tests/scripts/test_cross_harness_bridge_trigger.py -q` — 18/18 PASS unchanged.

### End-to-end live test

6. Run `python scripts/cross_harness_bridge_trigger.py --state-dir .gtkb-state/bridge-poller --diagnose` and verify the diagnose output renders correctly against current state.
7. Force a concurrent rename race in a controlled fixture (two threads simultaneously calling `_rename_with_retry`); assert both succeed without raising.
8. After implementation lands, observe `dispatch-failures.jsonl` over the next 24 hours; expect 0 new entries (or a sharp drop) compared to the historical 191 entries.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 5 (full regression preserves trigger semantics) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion (all touched files under `E:\GT-KB`) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 8 (post-impl observation; failure rate trends to 0) |
| Bridge-essential.md trigger-as-canonical | 5 (no semantics change) |
| canonical-terminology.md `cross-harness event-driven trigger` glossary | 6 (diagnose output cites canonical name) |

## Acceptance Criteria

- [ ] `_rename_with_retry` helper added with `max_attempts=5` and exponential backoff (50ms → 100 → 200 → 400 → 800).
- [ ] `_write_dispatch_state` calls `_rename_with_retry(tmp, target)` instead of `tmp.replace(target)`.
- [ ] `--diagnose` flag added; emits the structured summary; exits 0; does NOT modify dispatch state.
- [ ] 3 new rename-retry tests PASS.
- [ ] 3 new diagnose tests PASS.
- [ ] Existing 18 trigger tests PASS unchanged (no regression).
- [ ] Live diagnose output (test 6) reports `Overall: HEALTHY` against current state.
- [ ] Concurrency race fixture (test 7) confirms two simultaneous renames both succeed.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Low): Retry loop with sleep adds up to 1.55s wall time on the hot path under contention.** Mitigation: rare event (191 failures across 2 days = ~0.1/hour); the retry path is only exercised under contention. Successful first-attempt path adds 0 latency.
- **R2 (Low): `--diagnose` flag could become a maintenance burden.** Mitigation: minimal-format output; the flag does not modify state; adding new sections is purely additive.
- **R3 (Negligible): `import time` if newly added could shadow existing imports.** Mitigation: `time` is in the standard library; if already imported the import is idempotent.
- **R4 (Negligible): The retry loop could mask a different underlying bug if the contention is something other than file-in-use (e.g., disk full, permission denied for non-temporary reasons).** Mitigation: only `PermissionError` is retried; other exceptions propagate immediately. Final attempt's exception is re-raised verbatim.

### Rollback

`git revert <impl-commit-sha>` cleanly reverts both the helper and the diagnose flag. The existing `_write_dispatch_state` semantics are preserved; revert restores the pre-fix behavior (which is operational, just race-prone).

## Recommended Commit Type

`fix:` — repairs a documented defect (191 historical WinError 32 failures), not a net-new capability. The `--diagnose` flag is a small operational addition that fits within the same fix scope as a diagnostic surface for the same defect class.

## Loyal Opposition Asks

1. Confirm IP-1's retry-loop approach is the minimal sufficient fix vs. file-locking (rejected as more invasive).
2. Confirm IP-2's `--diagnose` output sections cover the assessment dimensions used in the owner's recent classification (file bridge, codex dispatch, prime dispatch, whole automation).
3. Confirm out-of-scope items are appropriately deferred (`audit.jsonl` rotation; per-PID state files; file-locking migration).
4. Confirm tests adequately cover the rename-retry semantics including failure modes (max_attempts exhausted; non-permission exceptions propagate immediately).

## Applicability Preflight

To be filled in by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
