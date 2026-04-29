# Bridge Proposal — Smart-Poller Verification In Session-Start Orient

**Status:** NEW (version 001 — small follow-on to activation `-005`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `smart-poller-orient-verification-2026-04-29`
**Builds on (VERIFIED):**
- `gtkb-bridge-poller-notify-activation-2026-04-29-005.md` (activation post-impl, awaiting VERIFIED)
- `gtkb-bridge-poller-p3-notify-2026-04-29-012.md` (P3-notify writer)

This proposal closes a gap surfaced by the owner immediately after activation: the session-start orient currently READS notifications when they exist, but does NOT verify that the smart poller is actually running. If the scheduled task is dead, missing, or stuck, the orient is silent and the owner only discovers the breakage by running `gt project doctor` manually or noticing notifications stop appearing.

The activation's "writer → reader" half is closed. This proposal closes the "verifier → owner" half by wiring the existing doctor check into session-start.

---

## 1. Context

After activation `-004` GO landed and was implemented through commits `d2d96f2a` → `d5a628e5`, the owner asked: *"Smart poller verification and remediation (if needed) should be a part of the session start procedure. Is it already?"*

Answer: partially. The notification reader runs at session-start (`_render_smart_poller_section` in `scripts/session_self_initialization.py`). The doctor check exists (`_check_smart_bridge_poller` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`). But they are not wired together — the verifier doesn't run at session-start, only on explicit `gt project doctor` invocation.

The gap: a dead/missing scheduled task is silent at session-start, defeating the operational value of activation.

## 2. Scope

**One deliverable:**
- Extend `_render_smart_poller_section` in `scripts/session_self_initialization.py` to call `_check_smart_bridge_poller` and emit a status-derived section in the orient block.

**Out of scope (deferred per owner direction):**
- Auto-remediation flag (e.g., `--remediate-smart-poller`) that runs the install script if doctor reports "not registered". Owner-policy-bearing; deserves a separate bridge with explicit opt-in / default-off design.
- Performance optimization of the doctor check (the PowerShell shell-out adds ~0.5-1s to session-start; tolerable today, optimizable later if it becomes a regression).

## 3. Design

### 3.1 Behavior matrix (status → orient output)

| Doctor `_check_smart_bridge_poller` status | Notification artifact | Orient output |
|---|---|---|
| `pass` | non-empty pending_actions | Existing markdown table (current behavior — unchanged) |
| `pass` | empty pending_actions | Silent (current behavior — unchanged) |
| `pass` | absent | Silent (current behavior — unchanged) |
| `warning` (e.g., task not registered, no audit yet) | any | "Smart-poller diagnostic" section: warning message + suggested action ("run `scripts/install_smart_poller_task.ps1`") |
| `fail` (e.g., wrapper missing, stuck task, stale audit, wrong target) | any | "Smart-poller diagnostic" section: failure message + remediation hint (specific command/file path from the doctor message itself) |
| Doctor itself raises an exception | any | Silent (fail-open per `-004` guardrail 1) — preserves current orient behavior; logs the exception to stderr for diagnosis but does NOT block startup |

### 3.2 Implementation sketch

The helper signature stays the same. Internal logic adds an early branch:

```python
def _render_smart_poller_section(project_root: Path, role: dict[str, Any]) -> list[str]:
    """Render the smart-poller orient section.

    Order of operations:
      1. Run doctor check; if status is warning/fail, render diagnostic +
         remediation hint and return early. (Notification rendering is
         skipped because notifications can't be trusted when the poller
         itself is unhealthy.)
      2. Otherwise (pass) proceed with existing notification-render path.
      3. All steps wrapped in fail-open try/except per -004 guardrail 1.
    """
    try:
        # Existing recipient determination from role['assumed_role']
        ...

        # NEW: doctor check first
        try:
            from groundtruth_kb.project.doctor import _check_smart_bridge_poller
            health = _check_smart_bridge_poller(project_root)
        except Exception:
            health = None  # Fail-open: silent if doctor itself errors

        if health is not None and health.status in ("warning", "fail"):
            return _render_diagnostic_section(health)

        # Existing path: read notification + format orient section
        artifact = read_for_recipient(project_root, recipient)
        section_md = format_orient_section(artifact)
        if not section_md:
            return []
        return [section_md, ""]
    except Exception:
        return []


def _render_diagnostic_section(health) -> list[str]:
    """Render a single-section diagnostic for an unhealthy smart poller."""
    icon = "⚠️" if health.status == "warning" else "❌"
    lines = [
        f"### Smart-poller diagnostic — {health.status.upper()}",
        "",
        f"{icon} {health.message}",
        "",
    ]
    return lines
```

### 3.3 Owner-experience samples

**When poller is healthy with pending work** (current state):
```
### Smart-poller notification — 15 pending action(s)

| Document | Status | File | INDEX line |
|---|---|---|---|
| ... |
```

**When task is not registered** (after fresh clone or post-uninstall):
```
### Smart-poller diagnostic — WARNING

⚠️ smart-poller task 'GTKB-SmartBridgePoller' not registered — run `scripts/install_smart_poller_task.ps1` to activate
```

**When task is registered but stuck** (audit > 60s old):
```
### Smart-poller diagnostic — FAIL

❌ smart-poller task registered but most recent audit event is 245s old (> 60s threshold). Task may be stuck — inspect Task Scheduler
```

The doctor message field is reused verbatim — it already contains specific remediation hints (file paths, command strings) per the existing `_check_smart_bridge_poller` design.

## 4. Tests

`tests/scripts/test_session_self_initialization.py` (existing file, +4 tests):

| Test | Scenario | Expected |
|---|---|---|
| `test_smart_poller_section_renders_diagnostic_on_doctor_warning` | Doctor returns `warning` status; notification absent | Output contains "Smart-poller diagnostic — WARNING" + the doctor's message text |
| `test_smart_poller_section_renders_diagnostic_on_doctor_fail` | Doctor returns `fail` status; notification absent | Output contains "Smart-poller diagnostic — FAIL" + the doctor's message |
| `test_smart_poller_section_diagnostic_supersedes_notification` | Doctor returns `warning`; notification file present with pending_actions | Output contains diagnostic; does NOT contain the notification table (notifications can't be trusted when poller is unhealthy) |
| `test_smart_poller_section_fail_open_on_doctor_exception` | Doctor itself raises an exception (monkeypatched) | Output is empty; orient continues; no startup failure |

Existing tests (5 from commit `45381ba8`) remain unchanged — they monkeypatch the doctor to return `pass` implicitly via the absent-task-no-state path, or they test the fail-open and routing behavior that's still in force.

## 5. Execution Plan (Commit Sequence)

Single commit:

| # | Commit | Files |
|---|---|---|
| 1 | "smart-poller: surface doctor status in session-start orient (per follow-on -001 §3)" | `scripts/session_self_initialization.py` (modified — extend `_render_smart_poller_section` + add `_render_diagnostic_section` helper) + `tests/scripts/test_session_self_initialization.py` (modified — +4 tests) |

Single commit because:
- Scope is bounded to one helper function + tests
- No new files
- No system-level config changes (unlike activation commit 5)
- Reversible via `git revert`

## 6. Out of Scope

Per owner direction at filing time: **auto-remediation deferred to a separate bridge.** That work would add a `--remediate-smart-poller` flag (or equivalent owner-policy mechanism) that re-runs the install script when doctor reports "not registered". Auto-remediation has system-mutation implications (it would re-register a Windows Scheduled Task without explicit per-invocation owner approval), so it deserves its own design + GO cycle with an explicit opt-in default-off contract.

If the owner wants auto-remediation included in this bridge, REVISED-1 would add a `--remediate-smart-poller-on-startup` argparse flag to `session_self_initialization.py` (default `False`), gated additionally on the doctor status being exactly `warning` (not `fail`) so genuine misconfigurations don't trigger silent reinstalls.

## 7. Performance

The doctor check shells out to `Get-ScheduledTask` via PowerShell. Measured cost on this host: ~0.5-1.0s on first invocation, typically lower on subsequent calls (Windows caches PowerShell module loading). Session-start already runs multiple expensive operations (Grafana dashboard JSON regeneration, KB queries, work-subject snapshot), so adding ~1s is not a meaningful regression.

If this becomes a concern, the doctor check could be cached (e.g., skip if last invocation < 60s ago) — but that's optimization, not in this scope.

## 8. Risks + Reversibility

### 8.1 Doctor check increases session-start latency

Mitigation: ~1s addition is below the noise floor of session-start (which already takes 5-10s). If it becomes a concern, cache the result with a short TTL.

### 8.2 Diagnostic noise when poller is intentionally uninstalled

If the owner has explicitly uninstalled the smart poller (e.g., via `uninstall_smart_poller_task.ps1` for a development pause), every fresh session would surface a "WARNING — task not registered" diagnostic. This is correct behavior: the owner WANTS to be reminded that the poller isn't running.

If the noise is unwanted in some scenarios, the same `--remediate-smart-poller` opt-in flag (out of scope here) could include a `--silence-smart-poller-diagnostic` companion flag — defer to the auto-remediation bridge.

### 8.3 Reversibility

Single-commit change; revert via `git revert` returns to the post-activation state where the orient surfaces notifications-when-present-only.

## 9. Codex Review Request

Please verify:

1. **Scope appropriateness.** Confirm the single-deliverable scope (verification only, no auto-remediation) is right for this follow-on, given the owner explicitly asked about both verification AND remediation but I'm proposing only verification with auto-remediation deferred.

2. **Behavior matrix coherence.** Confirm the §3.1 status → output mapping makes sense, particularly:
   - "pass + empty notification → silent" (no diagnostic, no notification): correct steady-state
   - "warning/fail → diagnostic supersedes notification": confirm this is the right precedence (notifications can't be trusted when poller is unhealthy) vs. showing both

3. **Doctor-check exception path.** Confirm that swallowing doctor exceptions and rendering nothing (per §3.2's nested try/except) is the right fail-open semantics. Specifically: should a doctor exception itself surface a diagnostic ("doctor unreachable — investigate") or stay silent? Current proposal is silent to preserve startup robustness; alternative is a third diagnostic class.

4. **Performance acceptance.** Confirm ~1s session-start regression is acceptable. If you'd prefer a cached check or async pre-fetch design, flag it.

A NO-GO with specific findings remains valuable. The session-start orient is a load-bearing surface for both harnesses; getting the verification semantics right matters for the durable contract.

## 10. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. It records the design contract for Codex review. The single commit described in §5 occurs only after Codex GO on `-001`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
