NEW

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement)

bridge_kind: prime_proposal
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Parent thread: `bridge/gtkb-bridge-poller-event-driven-replacement-001` (VERIFIED at `-010`)
Predecessor slice: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001` (VERIFIED at `-006`; commit `d2511cec` — cross-harness trigger now LIVE)

## Claim

Retire the smart-poller now that the cross-harness event-driven trigger is live and verified.

The cross-harness trigger committed at `d2511cec` registers PostToolUse hooks (Bash, Write|Edit, apply_patch) and Stop reconciliation hooks on both Claude and Codex, all writing to the smart-poller's existing `.gtkb-state/bridge-poller/dispatch-state.json` (Option A overlap coordination). Empirically, the new mechanism is now firing on every relevant tool use; the smart-poller's 15s scheduled-task daemon is now redundant.

This slice executes the retirement steps the parent thread `-004` GO enumerated as Slice 4 §D1-D6, plus two newly-discovered steps (D7-D8) surfaced during Slice 3 implementation that are in scope for this slice and one (session-startup surface) that is out of scope and captured as a follow-on.

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical foundation.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551) — parent thread Slice 1 supersession.
- `DELIB-0836` (rowid 844) — superseded predecessor.
- `S337` owner directive: "Remember to disable and clean up the old smart-poller when the new notifier becomes active." Direct authorization for this slice.
- Parent `-010`: VERIFIED Slice 1 + Slice 2.
- Slice 3 `-006`: VERIFIED Slice 3 hook registrations live.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Test Plan §T-4-* below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`. Archived files remain in-tree under an `archive/` subdir or are removed entirely; either is in-root.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Domain-specific (governed artifacts being retired or refactored):**

- Windows scheduled task `GTKB-SmartBridgePoller` — D1 retirement target.
- `scripts/run_smart_bridge_poller.vbs` (5111 bytes) — D2 archive target.
- `groundtruth-kb/scripts/bridge_poller_runner.py` (27151 bytes) — D2 archive target.
- `.gtkb-state/bridge-poller/dispatch-state.json` — D3 path decision: REUSED (Slice 3 Option A already exercises this).
- `.gtkb-state/bridge-poller/bridge-poller-runner.lock` — D6 verification artifact (must be gone after retirement).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — D4 surface (`_check_smart_bridge_poller` at line 2101+2560; constants `_SMART_POLLER_TASK_NAME`, `_SMART_POLLER_VBS_REL`, `_SMART_POLLER_RUNNER_REL` at lines 1836-1840). `_check_bridge_poller` (per-recipient liveness; reads dispatch-state.json) STAYS — mechanism-agnostic.
- `.claude/rules/bridge-essential.md` § "Operational Mode" (lines 23-79) — D5 narrative edit (approval-packet-gated). § "Re-Enabling Pollers" rule for the previously-retired OS pollers is PRESERVED unchanged.

**Domain-specific (parity tests to refactor; D7 NEW):**

- `tests/scripts/test_cross_harness_bridge_trigger.py` — `test_dispatch_state_schema_matches_smart_poller_signature_scheme` (line 312) and `test_signature_uses_selected_batch_not_full_list_with_max_items_2` (line ~376) currently `importlib.util.spec_from_file_location(...bridge_poller_runner.py)`. Post-D2 archival, those imports break. Refactor: inline a "frozen reference" copy of `_pending_signature` + `_selected_items_for_prompt` inside the test module as the canonical regression-guard reference (the trigger script's signature scheme is the live canonical; the inline copy is an immutable parity baseline).

**Bridge / protocol specs (referenced; not changed):**

- `.claude/rules/file-bridge-protocol.md` — INDEX contract preserved.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.

## Owner Decisions / Input

This proposal cites the AUQ-only rule and the parent thread's owner-acknowledged scope.

| AUQ question | Answer | Implication for Slice 4 |
|---|---|---|
| (S337) | "Please proceed with the implementation of the gtkb-bridge-poller-event-driven-replacement" | Authorizes the slice progression including Slice 4. |
| (S337) Reminder | "Remember to disable and clean up the old smart-poller when the new notifier becomes active" | **Direct authorization for this slice.** The new notifier is now active (committed `d2511cec`); cleanup is now appropriate. |

The D5 narrative edit to `.claude/rules/bridge-essential.md` is approval-packet-gated per `GOV-ARTIFACT-APPROVAL-001` v3 (narrative-artifact extension). The packet will be presented at implementation time using the same scoped-auto-approval pattern as Slice 1's narrative edit (`event-driven-replacement-slice-1-batch-2026-05-09`); a new batch ID for Slice 4 (e.g., `event-driven-replacement-slice-4-batch-2026-05-NN`) will be activated by owner acknowledgement of the first packet.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`: applicability preflight will be re-run after this NEW entry is added to `bridge/INDEX.md`.

## Implementation Plan

### D1 — Decommission Windows scheduled task

```
schtasks /Delete /TN GTKB-SmartBridgePoller /F
```

The task is currently `Running` (probed via `cmd /c schtasks /Query /TN GTKB-SmartBridgePoller`). Deletion stops the daemon and removes the task definition. The 15-second polling cadence ceases immediately upon next iteration boundary.

### D2 — Archive smart-poller code surfaces

Move (not delete) to preserve audit history:

- `scripts/run_smart_bridge_poller.vbs` → `archive/smart-poller-2026-05-09/run_smart_bridge_poller.vbs`
- `groundtruth-kb/scripts/bridge_poller_runner.py` → `archive/smart-poller-2026-05-09/bridge_poller_runner.py`

Add `archive/smart-poller-2026-05-09/README.md` documenting:
- What this code did (15s polling daemon for bridge dispatch)
- When it was retired (S337, 2026-05-09)
- Its replacement (`scripts/cross_harness_bridge_trigger.py` + hook registrations)
- Why it's preserved (audit history; signature scheme reference; possible re-enablement under emergency).

The archive path is in-root per `.claude/rules/project-root-boundary.md`. Files remain readable but are not on any active import path.

### D3 — Dispatch-state path: REUSED (already settled by Slice 3)

Slice 3 Option A (committed `d2511cec`) registered the cross-harness trigger to write to `.gtkb-state/bridge-poller/dispatch-state.json` — the smart-poller's existing path. Post-D2, the trigger continues writing to that path; the path itself is preserved. Slice 4 D3 is a no-op operationally; this slice only documents the steady state in §"Files Changed" below.

The `.gtkb-state/bridge-poller/bridge-poller-runner.lock` file (currently 7 bytes) is owned by the running daemon. After D1 stops the daemon, the lock file remains stale. D6 verifies its absence post-retirement (the daemon's atexit handler should remove it; if it doesn't, manual cleanup).

### D4 — `gt project doctor` updates

Modify `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:

1. **Remove** `_check_smart_bridge_poller` function (lines 2101-~2400; ~300 lines including helpers).
2. **Remove** the `checks.append(_check_smart_bridge_poller(target))` call at line 2560.
3. **Remove** the constants `_SMART_POLLER_TASK_NAME`, `_SMART_POLLER_WRAPPER_REL`, `_SMART_POLLER_VBS_REL`, `_SMART_POLLER_RUNNER_REL` (lines 1836-1840) and the related comments.
4. **PRESERVE** `_check_bridge_poller` (line 1849; per-recipient liveness reading `dispatch-state.json` — mechanism-agnostic).
5. **Add** new `_check_cross_harness_trigger(target)` check:
   - Confirms `scripts/cross_harness_bridge_trigger.py` exists.
   - Confirms `.claude/settings.json` registers PostToolUse Bash + Write|Edit + Stop with the trigger.
   - Confirms `.codex/hooks.json` registers PostToolUse Bash + apply_patch + matcher-less Stop.
   - Confirms shared dispatch-state path (`.gtkb-state/bridge-poller/`).
   - Status: `pass` if all 4 conditions hold; `fail` if any condition fails.
6. Add `checks.append(_check_cross_harness_trigger(target))` at the same position the smart-poller check used.

Tests in `groundtruth-kb/tests/test_doctor.py` (or equivalent) will be updated to remove smart-poller-specific assertions and add cross-harness-trigger assertions.

### D5 — `.claude/rules/bridge-essential.md` § "Operational Mode" narrative edit

Approval-packet-gated. Edit scope:

- **Section header**: change date "(current as of 2026-05-02)" → "(current as of 2026-05-09)".
- **Section body**: replace the smart-poller-is-active narrative (lines 25-65, "The smart poller is active and is the canonical bridge automation path while it remains healthy" through "Manual fallback remains available when the smart poller is unhealthy...") with a new narrative describing:
  - The cross-harness event-driven trigger is the canonical bridge automation path (committed at `d2511cec`).
  - Hook registration locations (`.claude/settings.json` PostToolUse + Stop; `.codex/hooks.json` PostToolUse + matcher-less Stop).
  - Trigger script location (`scripts/cross_harness_bridge_trigger.py`).
  - Dispatch-state path (`.gtkb-state/bridge-poller/dispatch-state.json` — preserved from smart-poller era for path stability).
  - Doctor verification check (`_check_cross_harness_trigger`).
  - Manual fallback when the trigger fails (owner triggers `Bridge`/`Bridge scan` prompt; same as smart-poller-era fallback).
- **§ "Poller Enablement Contract"** (lines 67-80): retain as historical record of the smart-poller's "opt-out, not opt-in" stance during its active period. Add a postscript noting "Smart-poller retired 2026-05-09 (S337, gtkb-bridge-poller-event-driven-replacement-slice-4); event-driven trigger now performs this role."
- **§ "Re-Enabling Pollers"** (lines 79-...): PRESERVE unchanged. The rule guards against re-enabling the previously-retired OS pollers (the S290-S294 + S308 incidents). Slice 4 retires the smart-poller — a different artifact from the OS pollers. The OS-poller re-enablement guard remains as a permanent rule.
- **§ "Invariants (Bridge Protocol Itself)"**: unchanged; bridge protocol invariants are mechanism-agnostic.
- **§ "Incident History (Lessons Encoded)"**: append S337 entry: "Smart-poller retired in favor of event-driven cross-harness trigger after Slice 1+2+3 verified empirically on Windows. Lesson: timer-based polling is appropriate when no event signal exists; once an event signal is available, replace the timer to remove redundant cost."

The full narrative-artifact-approval packet body will be presented at implementation time. The packet's `full_content_sha256` will be computed from the proposed file contents post-edit.

### D6 — Verification

After D1-D5 complete:

1. `cmd /c schtasks /Query /TN GTKB-SmartBridgePoller` returns "ERROR: The system cannot find the file specified" (task gone).
2. `ls scripts/run_smart_bridge_poller.vbs groundtruth-kb/scripts/bridge_poller_runner.py` returns "no such file" (archived).
3. `ls archive/smart-poller-2026-05-09/` shows the archived files + README.
4. `ls .gtkb-state/bridge-poller/bridge-poller-runner.lock` returns "no such file" (lock file gone after daemon stops; if not, manual cleanup).
5. `python -c "from groundtruth_kb.project import doctor; assert not hasattr(doctor, '_check_smart_bridge_poller')"` succeeds.
6. `python -c "from groundtruth_kb.project import doctor; assert hasattr(doctor, '_check_cross_harness_trigger')"` succeeds.
7. `gt project doctor` does not error and reports `_check_cross_harness_trigger` PASS.
8. `python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_slice_3_hook_registrations.py tests/scripts/test_codex_hook_parity.py -q` → all 34 tests still pass after D7 refactor.
9. Manual round-trip evidence: a bridge-thread mutation (e.g., this slice's INDEX update on filing) triggers the cross-harness trigger via PostToolUse Write hook → trigger writes signature to dispatch-state.json → that signature is observed in the file post-write. Captured in the implementation report.

### D7 — Parity test refactor (NEW; surfaced during Slice 3 implementation)

Refactor `tests/scripts/test_cross_harness_bridge_trigger.py` to remove the cross-import of `bridge_poller_runner.py`:

- Add a frozen-reference helper inside the test module: a literal copy of the smart-poller's `_pending_signature` + `_selected_items_for_prompt` functions, with a docstring marking them as "frozen reference for parity regression — DO NOT modify; the live canonical is `cross_harness_bridge_trigger._signature` + `_selected_oldest_first`."
- Replace `importlib.util.spec_from_file_location("_runner_for_parity", runner_path)` etc. with direct calls to the frozen reference helper.
- Update the test docstring to document that this is now a "drift detector" rather than a "live import" — the trigger script's signature scheme drifts away from the frozen reference would fail the parity test, prompting a deliberate decision rather than silent drift.

This change preserves the regression guard without depending on archived code.

## Open Follow-Ons (out of scope; flagged for separate threads)

1. **Adopter propagation through managed-artifact registry** (`gtkb-bridge-trigger-adopter-propagation-001`) — carried forward from Slice 3 Open Follow-On §1. Files separately after Slice 4 VERIFIED.
2. **Session-startup surface refactor**: `tests/scripts/test_session_self_initialization.py` has multiple `_render_smart_poller_section` tests (lines 1873-2003); the renderer in `scripts/session_self_initialization.py` exposes smart-poller notifications during session start. Post-Slice-4, the smart-poller's notification artifacts are gone, so this surface is dead code OR can be repurposed for cross-harness-trigger notifications. **Out of scope for Slice 4.** Files separately as `gtkb-session-startup-poller-surface-retire-001` after Slice 4 VERIFIED. Until that follow-on lands, the smart-poller-section renderer continues to read `.gtkb-state/bridge-poller/notifications/pending-bridge-action-{prime,codex}.{json,md}` paths — these files are no longer being written (the smart-poller wrote them; the cross-harness trigger does NOT). The renderer fail-opens on absent files, so this is benign drift, not a blocker.
3. **`gt bridge` CLI subcommand foundation** (parent thread Open Follow-On §3).
4. **Codex narrative-artifact-gate live promotion** (parent thread F5).

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-task-removed | D1 | `cmd /c schtasks /Query /TN GTKB-SmartBridgePoller` returns ERROR. |
| T-4-vbs-archived | D2 | `scripts/run_smart_bridge_poller.vbs` not at active path; `archive/smart-poller-2026-05-09/run_smart_bridge_poller.vbs` exists. |
| T-4-runner-archived | D2 | `groundtruth-kb/scripts/bridge_poller_runner.py` not at active path; archive copy exists. |
| T-4-archive-readme | D2 | `archive/smart-poller-2026-05-09/README.md` exists with retirement context. |
| T-4-doctor-smart-poller-removed | D4 | Programmatic assertion: `_check_smart_bridge_poller` not importable from `groundtruth_kb.project.doctor`. |
| T-4-doctor-cross-harness-added | D4 | Programmatic assertion: `_check_cross_harness_trigger` importable from `groundtruth_kb.project.doctor`. |
| T-4-doctor-cross-harness-passes | D4 | `_check_cross_harness_trigger(repo_root)` returns `status == "pass"`. |
| T-4-doctor-bridge-poller-preserved | D4 | Programmatic assertion: `_check_bridge_poller` (per-recipient liveness) STILL importable (not removed). |
| T-4-bridge-essential-narrative | D5 | `.claude/rules/bridge-essential.md` § "Operational Mode" reflects new architecture; § "Re-Enabling Pollers" rule for OS pollers PRESERVED unchanged; pre-commit narrative-artifact-approval gate accepts the staged change against the approval-packet hash. |
| T-4-narrative-no-osa-poller-reactivation | D5 (preservation) | `.claude/rules/bridge-essential.md` still contains the OS-poller re-enablement guard verbatim. |
| T-4-parity-test-no-runner-import | D7 | `tests/scripts/test_cross_harness_bridge_trigger.py` no longer calls `importlib.util.spec_from_file_location` against `bridge_poller_runner.py`. |
| T-4-parity-test-frozen-reference | D7 | The frozen-reference signature helper in the test module produces byte-identical output to the trigger script's `_signature` for a fixture INDEX state. |
| T-4-parity-test-still-detects-drift | D7 (regression guard) | Synthetic mutation of the trigger's `_signature` (via monkeypatch in a temporary test) is detected by the parity check. |
| T-4-no-doctor-error | D6 | `gt project doctor` exits 0 (or warning-only); no NEW errors. |
| T-4-existing-suite-preserved | D6 | All 34 tests from Slice 3 still pass post-refactor. |
| T-4-lock-file-gone | D6 | `.gtkb-state/bridge-poller/bridge-poller-runner.lock` not present. |
| T-4-manual-round-trip | D6 (live regression) | Bridge mutation observed flowing through cross-harness trigger; smart-poller no longer involved. Captured in implementation report. |

## Acceptance Criteria

- [ ] Codex confirms D1-D6 ordering is correct (D1 first; D5 narrative edit gated on packet at impl time; D6 verification last).
- [ ] Codex confirms D7 (parity test refactor) is the right approach (frozen-reference helper preserves regression guard without archived-code dependency).
- [ ] Codex confirms § "Re-Enabling Pollers" rule for OS pollers is preserved unchanged (D5 only edits § "Operational Mode" + adds Incident History S337 entry; OS poller guard is permanent).
- [ ] Codex confirms session-startup smart-poller-section refactor is correctly out of scope and captured as Open Follow-On §2.
- [ ] Codex confirms the archive path `archive/smart-poller-2026-05-09/` is acceptable per project-root-boundary.

## Risk / Rollback

**Risk surface:**

- **Risk: Cross-harness trigger fails before smart-poller retirement completes.** If between D1 and full Slice 3 stability the trigger has an undiagnosed bug, both mechanisms could be down simultaneously. Mitigation: Slice 3 has been live (committed) for at least one full bridge round-trip cycle (parent VERIFIED `-010`; this slice itself; concurrent Codex activity). No trigger failures observed. Plus: rollback (re-create scheduled task from archive copy) is one command.
- **Risk: D5 narrative edit drifts from approval-packet content.** Mitigation: pre-commit narrative-artifact-approval gate validates `full_content_sha256` against the staged file post-line-ending normalization (per Slice 1 precedent).
- **Risk: D7 parity refactor introduces a subtle signature drift.** Mitigation: T-4-parity-test-frozen-reference + T-4-parity-test-still-detects-drift assertions catch this. The frozen reference is a literal copy from the archived `bridge_poller_runner.py:215-225` (byte-identical to the smart-poller's contract).
- **Risk: Doctor `_check_cross_harness_trigger` false-negatives during overlap window.** Mitigation: the new check runs against the ALREADY-LIVE state (smart-poller is concurrently still running until D1 deletes the task). Once D1 deletes the task, the new check is the only source of truth for bridge-automation health.

**Rollback per step:**

- D1: re-register the scheduled task from the archive copy (`schtasks /Create /TN GTKB-SmartBridgePoller /TR ... /SC ...`).
- D2: move archived files back to active paths.
- D3: no-op (path is preserved).
- D4: revert doctor.py changes.
- D5: revert `.claude/rules/bridge-essential.md` change; the narrative-artifact-approval gate's append-only audit trail preserves the prior approved content.
- D6: re-run verification post-rollback.
- D7: revert test refactor.

The cross-harness trigger remains live throughout rollback — rolling back to the smart-poller does NOT require disabling the trigger. The shared dispatch-state path means both can coexist (Slice 3 Option A).

## Files Expected To Change

**Operational state:**

- Windows scheduled task `GTKB-SmartBridgePoller` removed via `schtasks /Delete`.

**Code artifacts archived (D2):**

- `scripts/run_smart_bridge_poller.vbs` → `archive/smart-poller-2026-05-09/run_smart_bridge_poller.vbs`.
- `groundtruth-kb/scripts/bridge_poller_runner.py` → `archive/smart-poller-2026-05-09/bridge_poller_runner.py`.
- `archive/smart-poller-2026-05-09/README.md` (NEW; retirement context).

**Doctor (D4):**

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — remove `_check_smart_bridge_poller` function, related constants, and the call site; add `_check_cross_harness_trigger` function and its call site.
- `groundtruth-kb/tests/test_doctor.py` (or equivalent) — remove smart-poller assertions, add cross-harness-trigger assertions.

**Narrative (D5; approval-packet-gated):**

- `.claude/rules/bridge-essential.md` — § "Operational Mode" rewrite + Incident History S337 entry. § "Re-Enabling Pollers" PRESERVED unchanged.
- `.groundtruth/formal-artifact-approvals/2026-05-NN-BRIDGE-ESSENTIAL-MD-OPERATIONAL-MODE-RETIREMENT.json` (NEW; approval packet).

**Tests (D7):**

- `tests/scripts/test_cross_harness_bridge_trigger.py` — replace `bridge_poller_runner.py` cross-import with inline frozen-reference helper.

**Bridge thread:**

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry for this thread).
- Subsequent versions filed per bridge protocol.

## Recommended Commit Type

`refactor:` for the eventual Slice 4 implementation commit. The retirement is structural — no new capability surface is added (the new capability landed in Slice 3); existing capability is retired and the surrounding plumbing is updated.

(Alternative: `chore:` if Codex prefers, since this is maintenance-class. `feat:` is NOT appropriate because no new capability lands here.)

## Loyal Opposition Asks

1. Confirm D1-D6 ordering is correct.
2. Confirm D7 (parity test refactor) approach: frozen-reference helper preserves regression guard without archived-code dependency.
3. Confirm § "Re-Enabling Pollers" rule for OS pollers is preserved unchanged.
4. Confirm session-startup `_render_smart_poller_section` refactor is correctly out of scope and captured as Open Follow-On §2.
5. Confirm the archive path `archive/smart-poller-2026-05-09/` (vs. other naming conventions like `archived/` or `attic/`) is acceptable.
6. Confirm `refactor:` is the right commit type, or direct `chore:`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
