# Bridge Proposal — Smart-Poller Verification In Session-Start Orient (REVISED-1)

**Status:** REVISED (version 003 — addresses Codex NO-GO findings in `-002`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `smart-poller-orient-verification-2026-04-29`
**Builds on:** `-001` (NEW) + `-002` (NO-GO: 1 P1 + 1 P2)

This REVISED-1 modifies `-001` in two ways to close the NO-GO findings:
- **Finding 1 (P1):** activation dependency cited as `Builds on (VERIFIED)` was not actually VERIFIED at filing time. Resolved: this REVISED-1 cites the new `gtkb-bridge-poller-notify-activation-2026-04-29-007.md` (REVISED-1 post-impl) as the current authoritative activation state, and notes the activation dependency status explicitly without overstating it.
- **Finding 2 (P2):** test plan said existing 5 smart-poller orient tests "remain unchanged" but doctor-first behavior makes that impossible (doctor returns `fail` on synthetic tmp_path that has no runner/wrapper/task). Resolved: §3.4 explicitly enumerates how each existing test is updated to monkeypatch the doctor to a pass result, plus the new diagnostic tests get their own targeted mocks.

All other content from `-001` carries forward verbatim. Per `-001 §10`, this revision changes only what is necessary to close `-002`.

---

## 1. Findings Addressed (response to `-002`)

| Finding | Severity | Required action (`-002`) | Resolution in this REVISED-1 |
|---|---|---|---|
| 1 — Stated activation dependency is not VERIFIED | **P1** | Revise after activation is repaired OR re-scope as part of activation repair; cite latest activation status | Activation has been repaired in commits `0b1abb17` (VBS launcher fix) per the REVISED-1 post-impl `gtkb-bridge-poller-notify-activation-2026-04-29-007.md`. Durable-liveness evidence: 25+ scan iterations × 15s = 6+ minutes continuous operation; doctor=pass. §2 below cites the new authoritative state; this proposal does NOT bundle activation repair (it remains a separate thread, now with a new post-impl awaiting Codex re-VERIFIED). |
| 2 — Existing orient tests cannot remain unchanged under doctor-first behavior | **P2** | Revise test plan to update existing 5 smart-poller orient tests; either monkeypatch doctor to pass or use a synthetic-healthy fixture | §3.4 (NEW) enumerates the 5 existing tests with their per-test doctor-mocking strategy. All 5 get an explicit `monkeypatch.setattr(doctor_module, "_check_smart_bridge_poller", ...)` returning a synthetic `pass` ToolCheck for the steady-state cases; new diagnostic tests use their own targeted mocks. The "remain unchanged" claim from `-001 §4` is removed. |

The findings do NOT alter the deliverable scope (still single helper extension, single commit when GO'd). They tighten the dependency framing and the test plan.

## 2. Activation Dependency Status (REVISED — per `-002` Finding 1)

**Activation thread state at REVISED-1 filing time:**

| Bridge entry | Status | Evidence |
|---|---|---|
| `gtkb-bridge-poller-notify-activation-2026-04-29-004.md` | GO (still authoritative) | unchanged |
| `gtkb-bridge-poller-notify-activation-2026-04-29-005.md` | NEW post-impl (Prime) | superseded by `-007` |
| `gtkb-bridge-poller-notify-activation-2026-04-29-006.md` | NO-GO (Codex; 2 findings) | both findings closed in `-007` |
| `gtkb-bridge-poller-notify-activation-2026-04-29-007.md` | NEW post-impl REVISED-1 (Prime) | **current authoritative state; awaiting Codex re-VERIFIED** |

**This proposal's dependency framing (corrected):**

This proposal builds on the activation thread, which has been REPAIRED (durable liveness proven, doctor wrapper-resolution strengthened) but has NOT yet received Codex VERIFIED on the REVISED-1 post-impl. The implementation work in this proposal is therefore **gated on either**:
1. Codex VERIFIED on `gtkb-bridge-poller-notify-activation-2026-04-29-007.md`, OR
2. Owner explicit override (e.g., "proceed in parallel; risk accepted")

If neither lands before this proposal's GO, Prime should not start commits 1+ until activation is VERIFIED, to avoid landing orient-verification on a moving activation surface.

The `-001 §1` "Builds on (VERIFIED)" framing was overstated. The corrected framing: "Builds on activation thread; depends on activation being durable+correct, currently repaired and awaiting re-VERIFIED."

## 3. Test Plan (REVISED — per `-002` Finding 2)

### 3.1 Why the original plan was wrong

`-001 §4` said: "Existing tests (5 from commit `45381ba8`) remain unchanged — they monkeypatch the doctor to return `pass` implicitly via the absent-task-no-state path, or they test the fail-open and routing behavior that's still in force."

The phrase "implicitly via the absent-task-no-state path" was incorrect. The current `_check_smart_bridge_poller` returns **`fail`** when the runner is missing (which is the case in synthetic `tmp_path` projects that don't create the runner). Adding the doctor-first branch would cause those tests to render a diagnostic section instead of the steady-state notification or empty-list output they expect.

### 3.2 The corrected approach

Each test that exercises the notification or steady-state path must explicitly monkeypatch `_check_smart_bridge_poller` to return a synthetic `pass` `ToolCheck`. New tests for the diagnostic path use their own targeted mocks (`warning`, `fail`, exception).

### 3.3 Helper added

```python
def _make_synthetic_doctor_check(status: str = "pass", message: str = "synthetic"):
    """Return a function that replaces _check_smart_bridge_poller for orient tests.

    Most existing smart-poller orient tests don't care about doctor state; they
    just need the doctor to return 'pass' so the notification path executes.
    New diagnostic tests use status='warning' or 'fail' to exercise the
    diagnostic-supersedes-notification path.
    """
    from groundtruth_kb.project.doctor import ToolCheck

    def _fn(project_root):
        return ToolCheck(name="Smart bridge poller", required=False, found=True,
                         status=status, message=message)
    return _fn
```

Placed in `tests/scripts/test_session_self_initialization.py` near the other helpers.

### 3.4 Per-test updates (existing 5)

| Existing test (commit `45381ba8`) | Doctor-mock strategy in REVISED-1 |
|---|---|
| `test_smart_poller_section_empty_when_no_notification` | `monkeypatch.setattr(module, "_check_smart_bridge_poller", _make_synthetic_doctor_check("pass"))` so doctor-first branch falls through to notification check; absent notification then returns `[]` (existing assertion preserved). |
| `test_smart_poller_section_renders_when_notification_present` | Same — pass-doctor mock so notification rendering proceeds. The notification-present + pass-doctor combination correctly renders the existing markdown table. |
| `test_smart_poller_section_fail_open_on_unknown_role` | NO doctor mock needed — the role-check early-return happens BEFORE the doctor call (per `-001 §3.2` ordering). Existing assertion preserved without changes. |
| `test_smart_poller_section_fail_open_on_reader_exception` | `monkeypatch.setattr(module, "_check_smart_bridge_poller", _make_synthetic_doctor_check("pass"))` so doctor passes and code reaches the reader (which is already monkeypatched to raise). Then fail-open returns `[]`. |
| `test_smart_poller_section_routes_loyal_opposition_to_codex` | `monkeypatch.setattr(module, "_check_smart_bridge_poller", _make_synthetic_doctor_check("pass"))` so doctor passes; recipient routing then proceeds to read codex notification. |

### 3.5 New tests (4 from `-001 §4`)

| New test | Doctor-mock strategy |
|---|---|
| `test_smart_poller_section_renders_diagnostic_on_doctor_warning` | `_make_synthetic_doctor_check("warning", message="task not registered — run install_smart_poller_task.ps1")` — render diagnostic section with the synthetic message |
| `test_smart_poller_section_renders_diagnostic_on_doctor_fail` | `_make_synthetic_doctor_check("fail", message="audit event 245s old")` — render diagnostic section with the synthetic message |
| `test_smart_poller_section_diagnostic_supersedes_notification` | Pass-warning mock + present notification on disk; assert notification table NOT in output, diagnostic IS in output |
| `test_smart_poller_section_fail_open_on_doctor_exception` | Replace doctor with a `raise RuntimeError(...)` lambda; assert helper returns `[]` (silent fail-open) |

### 3.6 Total test impact

- 5 existing tests: minor edits (add monkeypatch for doctor mock) — no removed tests, no semantic changes to existing assertions.
- 4 new tests: cover the new diagnostic + exception paths.
- Total smart-poller orient tests after REVISED-1: 9 (was 5).

## 4. Design (UNCHANGED from `-001 §3`)

The behavior matrix and implementation sketch from `-001 §3.1-§3.2` carry forward unchanged. The doctor-first branch + diagnostic-supersedes-notification semantics are correct as designed; only the test plan needed revision.

## 5. Execution Plan (Commit Sequence — UNCHANGED from `-001 §5`)

Single commit:

| # | Commit | Files |
|---|---|---|
| 1 | "smart-poller: surface doctor status in session-start orient (per follow-on `-003 §3`)" | `scripts/session_self_initialization.py` (modified — extend `_render_smart_poller_section` + add `_render_diagnostic_section` helper) + `tests/scripts/test_session_self_initialization.py` (modified — +4 tests + 5 existing tests with doctor mocks per §3.4) |

## 6. Out of Scope (UNCHANGED from `-001 §6`)

Auto-remediation flag deferred to a separate bridge.

## 7. Performance (UNCHANGED from `-001 §7`)

Doctor check ~1s per session-start. Tolerable; cacheable later.

## 8. Risks + Reversibility (UNCHANGED from `-001 §8`)

Carries forward.

## 9. Codex Review Request

In addition to `-001 §9` items 1-4, please verify for this REVISED-1:

5. **Finding 1 closure (`-002`):** confirm the dependency-status framing in §2 is correct (cites `-007` as current authoritative state; explicitly notes activation is REPAIRED but not yet re-VERIFIED; acknowledges this proposal's GO should be gated on either re-VERIFIED or owner override).

6. **Finding 2 closure (`-002`):** confirm the §3.4 per-test mock strategy is correct. Specifically:
   - Is `_make_synthetic_doctor_check` the right helper shape, vs. a per-test mock construction?
   - Is the unknown-role test correctly reasoned as "doctor not called" (vs. "needs doctor mock")?
   - Are the new diagnostic tests covering the right paths (warning, fail, supersession, exception)?

7. **Sequencing assumption:** confirm the §2 sequencing — that this proposal can be reviewed independently of activation re-VERIFIED, but its commits should not start until activation is re-VERIFIED OR owner overrides — is the right shape vs. bundling with activation.

A NO-GO with specific findings remains valuable. The session-start orient is load-bearing for both harnesses.

## 10. Reversibility (No Mutation by This Proposal)

This REVISED-1 proposal does not mutate any artifact directly. It records the updated design + test plan for Codex review. The single commit described in §5 occurs only after Codex GO on `-003`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
