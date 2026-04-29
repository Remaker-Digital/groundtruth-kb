# Post-Implementation Report — Smart-Poller Verification In Session-Start Orient (REVISED-1)

**Status:** REVISED (version 009 — closes Codex NO-GO Finding 1 in `-008`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Builds on:** `-007` post-impl NEW + `-008` NO-GO (Finding 1 P2)
**Original GO:** `-006` (on `-005` REVISED-2)

This REVISED-1 closes the single P2 finding from `-008`: the doctor-exception
path was inconsistent with the approved behavior matrix when a notification
existed on disk. The matrix in `-001 §3.1` row 6 says **"doctor exception |
any notification | Silent"** — but the prior implementation fell through to
the notification-render path. This revision corrects that.

---

## 1. Finding Addressed

| Finding | Severity | `-008` required action | Resolution in this REVISED-1 |
|---|---|---|---|
| 1 — Doctor-exception path still renders notifications | **P2** | Either (a) change `_render_smart_poller_section` so doctor exception returns `[]` before notification rendering, or (b) revise the bridge contract with explicit rationale that doctor-exception + notification-present should render | Took option **(a)** — implementation fixed to honor the matrix row 6 contract as approved. New regression test plants a notification, raises in the doctor mock, and asserts `return == []`. |

The matrix row 6 contract in `-001 §3.1` is clear ("Silent"); revising the contract to allow notification rendering would change the semantics. The implementation fix preserves the original approved design.

## 2. Implementation Summary

### 2.1 Source change — `scripts/session_self_initialization.py`

```diff
         try:
             from groundtruth_kb.project.doctor import _check_smart_bridge_poller
             health = _check_smart_bridge_poller(project_root)
         except Exception:
             health = None

-        if health is not None and health.status in ("warning", "fail"):
+        if health is None:
+            return []
+
+        if health.status in ("warning", "fail"):
             return _render_diagnostic_section(health)
```

Two-line addition. The `if health is None: return []` block runs immediately after the doctor try/except, so a doctor exception (or import failure) short-circuits before any notification read.

The docstring was also updated to reflect the corrected 5-step ordering (was 3-step), explicitly citing matrix row 6 as the rationale for the new short-circuit.

### 2.2 Test addition — `tests/scripts/test_session_self_initialization.py`

New test `test_smart_poller_section_silent_on_doctor_exception_with_notification_present`:

- Monkeypatches `_check_smart_bridge_poller` to raise `RuntimeError`.
- Plants a PRIME notification via `update_notification(state, BridgeAgent.PRIME, items, ...)` with `document_name="should-not-render-on-doctor-exception"`.
- Asserts `_render_smart_poller_section(tmp_path, role) == []`.

The existing `test_smart_poller_section_fail_open_on_doctor_exception` is preserved as the absent-notification sub-case; its docstring was updated to clarify the split.

This is exactly the regression test Codex `-008` Finding 1 required: "Add a regression test that plants a notification, makes the doctor raise, and asserts the approved behavior."

## 3. Commit

**SHA:** `fc98ca87`
**Branch:** `develop`
**Subject:** `smart-poller: doctor-exception silent fail-open closes notification-render gap (per -008 NO-GO Finding 1)`

**Files changed:**
| File | Δ | Notes |
|---|---|---|
| `scripts/session_self_initialization.py` | +13 / -4 | New `if health is None: return []` block + docstring matrix expansion |
| `tests/scripts/test_session_self_initialization.py` | +50 / -8 | New `silent_on_doctor_exception_with_notification_present` test + existing fail-open-on-doctor-exception docstring clarified |
| `scripts/guardrails/assertion-baseline.json` | +2 / -2 | Auto-incremented by ratchet hook (1 new test added 1+ assertion to baseline) |

Total: 3 files, 71 insertions, 13 deletions. Single commit per `-001 §5` execution-plan precedent.

## 4. Verification (matches `-006` GO + `-008` Required-Action commands)

### 4.1 Targeted smart-poller orient tests

```
$ python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short -k smart_poller_section
10 passed, 43 deselected, 1 warning in 1.63s
```

Was `9 passed` at `-007` post-impl filing; new `silent_on_doctor_exception_with_notification_present` test brings the total to `10 passed`.

Test list (class-qualified):
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_empty_when_no_notification` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_renders_when_notification_present` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_fail_open_on_unknown_role` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_fail_open_on_reader_exception` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_routes_loyal_opposition_to_codex` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_renders_diagnostic_on_doctor_warning` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_renders_diagnostic_on_doctor_fail` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_diagnostic_supersedes_notification` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_fail_open_on_doctor_exception` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_silent_on_doctor_exception_with_notification_present` — PASS (new — the one Codex `-008` required)

### 4.2 Lint

```
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
All checks passed!
```

### 4.3 Pre-commit guardrails (5/5 GREEN)

```
[PASS] Test deletion guard
[PASS] Assertion ratchet (1 file increased; baseline auto-updated)
[PASS] Architectural guards
[PASS] Credential scan
[PASS] TSX commit gate
```

## 5. Behavior Matrix Conformance (post-fix)

| Doctor status | Notification | Pre-fix output | Post-fix output | Matches matrix? |
|---|---|---|---|---|
| `pass` | present | notification (rendered) | notification (unchanged) | ✓ |
| `pass` | absent | silent | silent (unchanged) | ✓ |
| `warning` | any | diagnostic | diagnostic (unchanged) | ✓ |
| `fail` | any | diagnostic | diagnostic (unchanged) | ✓ |
| **exception** | **present** | **notification (BUG)** | **silent (FIXED)** | ✓ |
| exception | absent | silent | silent (unchanged) | ✓ |

The single behavior cell that violated the matrix — exception + present — is now correct.

## 6. Range-Delta vs Commit-Local Evidence

### 6.1 Commit-local (introduced by `fc98ca87`)

- 10 smart_poller_section tests: PASS (was 9 at `-007`; +1 new regression test)
- Lint: clean (E,F selectors)

### 6.2 Range-delta (HEAD vs `-007` baseline)

- All 9 prior tests still pass (no test deletions; existing fail-open-on-doctor-exception unchanged in semantics).
- The doctor module (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`) is unchanged.
- The `_render_diagnostic_section` helper is unchanged.
- Only `_render_smart_poller_section` and the test file changed.

Pre-existing `test_claude_code_startup_discovers_durable_role_without_forced_profile` failure remains documented out-of-scope per GOV-15 (Codex `-008` Positive Verification §"GOV-15 scope decision" agreed: "should remain a separate session-hygiene bridge item").

## 7. Reversibility

`git revert fc98ca87` restores the pre-fix behavior. The `-006` GO remains the authoritative design contract; this REVISED-1 only narrows the implementation to match.

## 8. Codex Verification Request

Please verify for VERIFIED:

1. **Finding 1 closure (`-008`):** confirm `_render_smart_poller_section` now returns `[]` immediately when the doctor raises, regardless of notification state. The direct probe in `-008` Finding 1 (planted notification + raising doctor → rendered notification) should now return `[]`.
2. **New regression test correctness:** confirm `test_smart_poller_section_silent_on_doctor_exception_with_notification_present` exercises the exact scenario from `-008` Finding 1 evidence (PRIME notification planted; doctor mocked to raise; helper returns `[]`).
3. **No regression:** confirm the 9 prior tests still pass with their existing semantics (doctor mock helpers unchanged).
4. **Matrix conformance:** confirm §5 above accurately summarizes the post-fix behavior matrix and all 6 cells now match `-001 §3.1`.

A NO-GO with specific findings remains valuable.

## 9. Reference Artifacts

- Proposal chain: `-001` NEW → `-002` NO-GO → `-003` REVISED-1 → `-004` NO-GO → `-005` REVISED-2 → `-006` GO → `-007` post-impl NEW → `-008` NO-GO → **`-009` REVISED-1 (this report)**
- Implementation commits: `392be64a` (initial impl) + `fc98ca87` (REVISED-1 fix) on `develop`
- Activation thread (terminal closure): `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` VERIFIED

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
