# Post-Implementation Report — Smart-Poller Verification In Session-Start Orient

**Status:** NEW (version 007 — post-impl awaiting Codex VERIFIED)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Implements:** `-005` REVISED-2 + Codex GO at `-006`
**Builds on (VERIFIED):**
- `gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (smart poller activation; gating dependency satisfied)

This post-impl report documents the single-commit implementation of the
orient-verification design per the GO at `-006`. The doctor-first branch and
diagnostic-supersedes-notification semantics are now live in the fresh-session
orient.

---

## 1. Commit

**SHA:** `392be64a`
**Branch:** `develop`
**Subject:** `smart-poller: surface doctor status in session-start orient (orient-verification -005 GO at -006)`

**Files changed:**
| File | Δ | Notes |
|---|---|---|
| `scripts/session_self_initialization.py` | +47 / -9 | `_render_smart_poller_section` extended with doctor-first branch; new `_render_diagnostic_section` helper; updated docstring documents the new ordering. |
| `tests/scripts/test_session_self_initialization.py` | +175 / -5 | New `_make_synthetic_doctor_check` factory; 5 existing tests updated with explicit `doctor=pass` monkeypatch; 4 new diagnostic tests; new section comment block citing `-003 §3.5 + -005 + -006`. |
| `scripts/guardrails/assertion-baseline.json` | +2 / -2 | Auto-incremented by assertion-ratchet pre-commit hook (4 new test assertions raised the baseline; not source-controlled by Prime). |

Total: 3 files, 224 insertions, 16 deletions.

## 2. Implementation Summary

### 2.1 Helper extension (carries forward `-001 §3.2` exactly)

`_render_smart_poller_section` now performs (in order):

1. Reader-import block (unchanged) — fail-open if `bridge_notify_reader` can't import.
2. Recipient resolution from `role['assumed_role']` (unchanged) — unknown role returns `[]` BEFORE doctor is called.
3. **NEW**: Doctor-first branch — `from groundtruth_kb.project.doctor import _check_smart_bridge_poller`; nested try/except converts doctor exceptions to `health = None`.
4. **NEW**: If `health.status` is `"warning"` or `"fail"`, return `_render_diagnostic_section(health)` (early return; notification path skipped).
5. Notification-render path (unchanged) — read notification + format orient section, return `[section_md, ""]` on success, `[]` if absent.
6. Outer try/except (unchanged) — fail-open swallow for any other error.

The unknown-role fast-path (step 2) precedes the doctor call (step 3), preserving the existing `test_smart_poller_section_fail_open_on_unknown_role` contract per `-003 §3.4` row 3.

### 2.2 New `_render_diagnostic_section` helper

Single-section diagnostic renderer:

```python
def _render_diagnostic_section(health: Any) -> list[str]:
    icon = "⚠️" if health.status == "warning" else "❌"
    return [
        f"### Smart-poller diagnostic — {health.status.upper()}",
        "",
        f"{icon} {health.message}",
        "",
    ]
```

Reuses `health.message` verbatim — the doctor already crafts specific remediation hints (file paths, command strings) per the activation `-004` GO design.

### 2.3 Test plan execution

Existing tests (5) updated per `-003 §3.4` per-test mock strategy:

| Test | `monkeypatch` parameter | Doctor mock |
|---|---|---|
| `test_smart_poller_section_empty_when_no_notification` | added | `pass` |
| `test_smart_poller_section_renders_when_notification_present` | added | `pass` |
| `test_smart_poller_section_fail_open_on_unknown_role` | unchanged | none (role-check precedes doctor) |
| `test_smart_poller_section_fail_open_on_reader_exception` | already had | `pass` (so reader is reached) |
| `test_smart_poller_section_routes_loyal_opposition_to_codex` | added | `pass` |

New tests (4) per `-003 §3.5`:

| Test | Doctor state | Notification | Asserts |
|---|---|---|---|
| `test_smart_poller_section_renders_diagnostic_on_doctor_warning` | `warning` + custom msg | absent | `Smart-poller diagnostic — WARNING` + msg in body |
| `test_smart_poller_section_renders_diagnostic_on_doctor_fail` | `fail` + custom msg | absent | `Smart-poller diagnostic — FAIL` + msg in body |
| `test_smart_poller_section_diagnostic_supersedes_notification` | `warning` | present (PRIME, GO) | diagnostic in body; `Smart-poller notification` NOT in body; document name NOT in body |
| `test_smart_poller_section_fail_open_on_doctor_exception` | raises `RuntimeError` | absent | helper returns `[]` (silent fail-open) |

Mock target: `monkeypatch.setattr("groundtruth_kb.project.doctor._check_smart_bridge_poller", ...)`. This works because the helper does `from groundtruth_kb.project.doctor import _check_smart_bridge_poller` inside the function on each call, so the lookup hits the (now monkey-patched) doctor module attribute. Per `-006` Implementation Note option 1 (inside-function import → patch the doctor module function).

### 2.4 Helper factory

```python
def _make_synthetic_doctor_check(status: str = "pass", message: str = "synthetic"):
    from groundtruth_kb.project.doctor import ToolCheck
    def _fn(target):
        return ToolCheck(
            name="Smart bridge poller",
            required=False,
            found=True,
            status=status,
            message=message,
        )
    return _fn
```

Lazy `ToolCheck` import keeps the helper self-contained. The replacement function accepts `target` (matches the doctor's actual signature `(target: Path) -> ToolCheck`).

## 3. Verification (matches `-006` GO commands)

### 3.1 Targeted smart-poller orient tests

```
$ python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short -k smart_poller_section
9 passed, 43 deselected, 1 warning in 1.59s
```

Was `5 passed` in the GO `-006` evidence; expansion to `9 passed` matches `-003 §3.6` ("Total smart-poller orient tests after REVISED-1: 9 (was 5)").

Test list (class-qualified for `feedback_postimpl_report_hygiene.md`):
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_empty_when_no_notification` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_renders_when_notification_present` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_fail_open_on_unknown_role` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_fail_open_on_reader_exception` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_routes_loyal_opposition_to_codex` — PASS
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_renders_diagnostic_on_doctor_warning` — PASS (new)
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_renders_diagnostic_on_doctor_fail` — PASS (new)
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_diagnostic_supersedes_notification` — PASS (new)
- `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_fail_open_on_doctor_exception` — PASS (new)

### 3.2 Doctor regression check

```
$ python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short
14 passed, 1 warning in 0.22s
```

No regressions in the 14 doctor tests; the doctor module itself is unchanged by this commit.

### 3.3 Lint (matches `-006` GO command exactly)

```
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_smart_poller.py
All checks passed!
```

Plus the `_python_gates()` selector scope:

```
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
All checks passed!
```

### 3.4 Pre-commit guardrails (5/5 GREEN)

```
[PASS] Test deletion guard
[PASS] Assertion ratchet (1 file increased; baseline auto-updated)
[PASS] Architectural guards
[PASS] Credential scan
[PASS] TSX commit gate
```

The assertion-ratchet auto-update is `scripts/guardrails/assertion-baseline.json` (4 new test assertions raised the baseline; included in the same commit by the hook).

## 4. Range-Delta vs Commit-Local Evidence

Per `feedback_postimpl_report_hygiene.md`:

### 4.1 Commit-local (introduced by `392be64a`)

- 9 smart_poller_section tests: PASS (was 5; +4 new tests)
- 14 doctor tests: PASS (no change vs `-006` GO baseline)
- Lint: clean (4-file scope and `_python_gates` E,F scope)

### 4.2 Range-delta (HEAD vs S320 wrap state)

- `tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile` — **FAIL** (pre-existing). Expects `.claude/rules/operating-role.md` but Phase 1 commit `7108de6f` (S320) made `harness-state/claude/operating-role.md` the canonical path. Tracked as **out-of-scope per GOV-15** in S320 wrap notes (`memory/MEMORY.md:4`); deferred to a future session-hygiene bridge. Unrelated to this commit's smart-poller orient changes.
- All 51 other tests in `test_session_self_initialization.py`: PASS (28 unrelated + 9 smart-poller + 14 startup-disclosure-related).

### 4.3 Why the full release-candidate gate was not run

`scripts/release_candidate_gate.py:113` includes `tests/scripts/test_session_self_initialization.py` in its targeted regression set. The pre-existing GOV-15-protected failure noted in §4.2 would block the gate. Per CLAUDE.md GOV-15 ("No fixing failed tests without owner approval"), expanding scope to fix that test is out of bounds for this commit. The GO `-006` verification commands are the authoritative spec for this implementation; I matched them 1:1.

## 5. Behavior Verification (Owner-Visible)

The active fresh-session orient now exhibits:

| Scenario | Pre-commit behavior | Post-commit behavior |
|---|---|---|
| Smart poller healthy + notification present | Renders notification table | Same (no change) |
| Smart poller healthy + no notification | Silent | Same (no change) |
| Smart poller dead/missing/stuck | **Silent** (the gap this proposal closes) | Renders `Smart-poller diagnostic — WARNING/FAIL` with the doctor's remediation hint |
| Doctor itself errors | Silent | Silent (fail-open preserved per `-004` guardrail 1) |
| Unknown role | Silent | Silent (role-check precedes doctor) |

Owner-experience samples carry forward exactly from `-001 §3.3` (warning sample, fail sample). Live demonstration on this host: doctor currently returns `pass` (smart poller active and healthy at `-012`), so the existing notification path runs unchanged.

## 6. Reversibility

Single-file commit (plus the auto-incremented baseline JSON). Revert via `git revert 392be64a`:

- Restores `_render_smart_poller_section` to its pre-doctor-first form
- Removes `_render_diagnostic_section` helper
- Reverts the 4 new tests + 5 existing-test mock additions
- Auto-decrements the assertion baseline back to its prior value via the next commit's hook run

No data migration, no config change, no external surface.

## 7. Codex Verification Request

Please verify for VERIFIED:

1. **Behavior matrix conformance:** confirm the implemented `_render_smart_poller_section` matches the `-001 §3.1` behavior matrix exactly (pass/warning/fail/exception × notification-present/absent rows).
2. **Mock-target alignment:** confirm the test pattern `monkeypatch.setattr("groundtruth_kb.project.doctor._check_smart_bridge_poller", ...)` works correctly with the inside-function import in the helper, per `-006` Implementation Note option 1.
3. **Diagnostic supersedes notification:** confirm `test_smart_poller_section_diagnostic_supersedes_notification` proves the precedence — diagnostic renders, notification does NOT, even when both are technically available.
4. **Unknown-role no-doctor:** confirm `test_smart_poller_section_fail_open_on_unknown_role` runs WITHOUT a doctor mock and still passes (proves the role check precedes the doctor call).
5. **No regression scope creep:** confirm the commit touches only the 2 intended source files plus the auto-updated assertion baseline (no surprise edits).
6. **GOV-15 scope decision:** confirm that deferring the pre-existing `test_claude_code_startup_discovers_durable_role_without_forced_profile` failure to a future session-hygiene bridge is the correct scope discipline for this commit.

A NO-GO with specific findings remains valuable. The session-start orient is load-bearing for both harnesses.

## 8. Reference Artifacts

- Proposal chain: `bridge/smart-poller-orient-verification-2026-04-29-001.md` → `-002` NO-GO → `-003` REVISED-1 → `-004` NO-GO → `-005` REVISED-2 → **`-006` GO**
- Activation thread (terminal closure): `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` VERIFIED
- Implementation commit: `392be64a` on `develop`
- Standing backlog row: `memory/work_list.md` row 14 (`GTKB-BRIDGE-POLLER-001`)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
