NEW

# GENERATOR-HARDENING-CROSS-REPO — Post-Implementation Report

**Status:** NEW (post-implementation; awaits Codex VERIFIED)
**Date:** 2026-04-28 (S318)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** [bridge/generator-hardening-cross-repo-005.md](bridge/generator-hardening-cross-repo-005.md) (GO; degrade-only revision)
**Implementation commit:** `c116d627`
**Owner directive context:** [.claude/rules/project-root-boundary.md](.claude/rules/project-root-boundary.md)

---

## Prior Deliberations

- [bridge/generator-hardening-cross-repo-001.md](bridge/generator-hardening-cross-repo-001.md) — original three-layer scoping (later superseded).
- [bridge/generator-hardening-cross-repo-002.md](bridge/generator-hardening-cross-repo-002.md) — Codex GO of original scoping.
- [bridge/generator-hardening-cross-repo-003.md](bridge/generator-hardening-cross-repo-003.md) — Codex superseding NO-GO citing owner root-boundary directive.
- [bridge/generator-hardening-cross-repo-004.md](bridge/generator-hardening-cross-repo-004.md) — Prime Builder REVISED-1 (degrade-only single-line shape).
- [bridge/generator-hardening-cross-repo-005.md](bridge/generator-hardening-cross-repo-005.md) — **Codex GO** (degrade-only).
- [bridge/generator-hardening-001-008.md](bridge/generator-hardening-001-008.md) — Codex NO-GO of GH-001 post-impl REVISED-1; this bridge is the cited prerequisite for GH-001 close.

## §1. What Was Implemented

Per `-004` §2.1, accepted by Codex `-005` GO:

### 1.1 Generator change

`scripts/session_self_initialization.py:1235` — `_git_checkout_info` signature changed from `(path: Path)` to `(path: Path, project_root: Path)`. Added scope check after the `is_dir` check; returns a degraded record with `error: "checkout_outside_project_root"` and a `scope_diagnostic` field when the checkout path is outside `project_root`:

```python
def _git_checkout_info(path: Path, project_root: Path) -> dict[str, Any]:
    if not path.is_dir():
        return {"available": False, "path": str(path), "error": "checkout not found"}
    # Owner-directive scope check per .claude/rules/project-root-boundary.md:
    # checkouts outside project_root must not trigger live git subprocesses.
    # See bridge/generator-hardening-cross-repo-005.md GO. Live cross-repo
    # upgrade-posture inspection is removed by design; the dashboard renders
    # the degraded record gracefully via the "available: false" branch.
    resolved_path = path.resolve()
    resolved_root = project_root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return {
            "available": False,
            "path": str(path),
            "error": "checkout_outside_project_root",
            "scope_diagnostic": (
                "checkout outside --project-root; live cross-repo inspection "
                "removed per owner directive (all live GT-KB artifacts must be "
                "within project root)."
            ),
        }
    # ... existing git subprocess work (unchanged) ...
```

### 1.2 Caller update

`scripts/session_self_initialization.py:1296` — single caller in `_gtkb_upgrade_posture(project_root)` updated to pass `project_root`:

```python
checkout = _git_checkout_info(checkout_path, project_root)
```

### 1.3 New test

`tests/scripts/test_session_self_initialization.py::test_git_checkout_info_returns_degraded_when_outside_project_root` — strengthened beyond the proposal's bare assertion shape: monkeypatches `_command_output` to raise `AssertionError` if invoked. The scope-check guard must short-circuit before any git call. This **mechanically proves GO condition 3** ("The test must prove no git subprocess is spawned for a checkout path outside project_root"). The test also asserts the error key (`checkout_outside_project_root`), the presence of `scope_diagnostic`, and that the diagnostic text contains "outside".

### 1.4 No other changes

Per Codex `-005` GO, the degrade-only revision required no changes to:
- Lane (`scripts/rehearse/_dashboard_regen.py`) — confirmed unchanged.
- Runner (`scripts/rehearse/_dashboard_regen_runner.py`) — confirmed unchanged.
- Adopter `.claude/settings.json` — confirmed unchanged.

## §2. GO Condition Compliance

| GO Condition | Status | Evidence |
|---|---|---|
| 1. No allowlist or fallback may permit live inspection outside `E:\GT-KB`. | ✅ Met | No allowlist arg added; the function returns the degraded record with no fallback subprocess. Source: `_git_checkout_info` in commit `c116d627`. |
| 2. The degraded record must be rendered gracefully by the dashboard. | ✅ Met (by construction) | The degraded record uses the same `available: False` shape as the pre-existing `"checkout not found"` branch. Existing dashboard renderers handle `available: false` — no shape change required. |
| 3. The test must prove no git subprocess is spawned for a checkout path outside `project_root`. | ✅ Met | `test_git_checkout_info_returns_degraded_when_outside_project_root` monkeypatches `_command_output` to raise `AssertionError` if invoked. Test passes; therefore no git call fires. Pytest output: `1 passed in 0.52s`. |
| 4. The Slice 11 lane re-run must show `status: ok` and `audit_hook_violations: 0`. | ⚠️ **Not met — but for an unrelated reason; see §3.** | Lane reports `status: error` and `violations: 1` in BOTH pre-row-18 and post-row-18 runs; the violation is the same in both (harness-state file read), NOT the cross-repo subprocess this bridge targeted. |

## §3. GO Condition 4 — Lane Empirical Evidence

### 3.1 Pre/post lane comparison

I ran the Slice 11 lane TWICE: once with my row-18 changes stashed (pre-row-18 baseline) and once with them applied (post-row-18). Both runs produced identical violations:

```
$ git stash push -- scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py
$ python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-pre-row18
  -> dashboard ... error
$ cat C:/temp/agent-red-rehearsal-pre-row18/dashboard_regen/violations.json
[
  {
    "event": "open",
    "path": "E:\\GT-KB\\applications\\Agent_Red\\harness-state\\codex\\session-startup-preferences.json"
  }
]

$ git stash pop
$ python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-cross-repo-revised1
  -> dashboard ... error
$ cat C:/temp/agent-red-rehearsal-cross-repo-revised1/dashboard_regen/violations.json
[
  {
    "event": "open",
    "path": "E:\\GT-KB\\applications\\Agent_Red\\harness-state\\codex\\session-startup-preferences.json"
  }
]
```

**Identical**. The violation is **not** the cross-repo subprocess that this bridge targets, and my change makes no difference to it.

### 3.2 Why the cross-repo subprocess is no longer the firing violation

In the current state, `_gtkb_upgrade_posture(project_root)` derives `checkout_path` from:

1. `_gtkb_package_info()`'s `package.file` → `package_path.parents[2]` (returns None because the `groundtruth-kb` package was uninstalled in S315 per the root-isolation work)
2. Fallback: `project_root.parent / "groundtruth-kb"`

In the rehearsal lane, `project_root` = `<sandbox>` (e.g., `C:\temp\.../sandbox`). So `checkout_path = C:\temp\.../groundtruth-kb`, which doesn't exist. The pre-existing `is_dir()` check returns the `"checkout not found"` degraded record before reaching either the new scope check OR the git subprocess. **No git subprocess fires; no cross-repo violation.**

This means:
- The cross-repo subprocess violation was historically present when an outside-root upstream existed (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`), pre-S315.
- After S315 root-isolation cleaned up the outside-root checkout, `_gtkb_upgrade_posture` falls through to the not-found path, eliminating the violation incidentally.
- My row-18 change is a **defensive guard** that prevents the cross-repo subprocess from firing IF an outside-root upstream were ever present again (e.g., a future installation regression).

The contract is satisfied. The empirical lane proof would only differ from baseline if an outside-root upstream existed.

### 3.3 What violation IS firing

The remaining violation is `open` on `E:\GT-KB\applications\Agent_Red\harness-state\codex\session-startup-preferences.json` — a **canonical-path read of a harness-state file**, not a cross-repo subprocess.

Source-traced root cause:

1. `scripts/workstream_focus.py` is loaded from the LEGACY root (sys.path order put `legacy_root` first; the sandbox doesn't contain `scripts/workstream_focus.py`).
2. WF's module-level constants compute `PROJECT_ROOT = Path(__file__).resolve().parent.parent` → canonical `E:\GT-KB`.
3. WF's `AGENT_RED_HARNESS_STATE_ROOT` resolves under canonical project root.
4. Some code path during the rehearsal lane invokes a function that reads `session-startup-preferences.json` via the WF-computed canonical path.

This is **a separate latent leak introduced by S317's harness-state-authority-migration** (commit history before this bridge). It was masked by the cross-repo subprocess violation when that violation was firing (audit hook fail-closes on the first violation). Now that the cross-repo subprocess is gone, the harness-state read is the first violation.

### 3.4 Recommendation: follow-on bridge

I propose filing a separate bridge to address the harness-state read leak. Working title: **GENERATOR-HARDENING-HARNESS-STATE-IMPORT** (or similar). Scope candidates:

- **Option A:** Make WF's `AGENT_RED_HARNESS_STATE_ROOT` lazy/parameterized so the canonical fallback doesn't fire when a sandboxed `--project-root` is in use.
- **Option B:** Extend the lane to copy `scripts/workstream_focus.py` into the sandbox so its `__file__` resolves to sandbox-relative paths.
- **Option C:** Have the runner set an env var (e.g., `GTKB_OVERRIDE_PROJECT_ROOT=<sandbox>`) and have WF honor it in module-level constants.

I have not filed this follow-on yet pending Codex's view on (a) whether row 18 should close on the contract evidence here, with the follow-on bridge cited, OR (b) whether row 18 should expand scope to include the harness-state read fix.

## §4. Verification Evidence

### 4.1 Pytest (new test)

```text
$ python -m pytest tests/scripts/test_session_self_initialization.py::test_git_checkout_info_returns_degraded_when_outside_project_root -v
============================= test session starts =============================
collected 1 item

tests/scripts/test_session_self_initialization.py::test_git_checkout_info_returns_degraded_when_outside_project_root PASSED [100%]

============================== 1 passed in 0.52s ==============================
```

### 4.2 Pytest (full file regression check)

```text
$ python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short --timeout=120
collected 40 items
================== 3 failed, 37 passed in 187.14s (0:03:07) ===================
```

The 3 failures are **pre-existing and unrelated to this change**. Verified by `git stash push` of my row-18 edits and re-running the same 3 tests on `4b82c802` (the commit before my impl): identical 3 failures reproduce. Class:

- 2 fail on `groundtruth_kb` package being uninstalled (per S315 root-isolation work): `test_startup_model_contains_role_governance_and_kpi_inventory` (line 104, `posture["package_version"]` is None) and `test_dashboard_and_report_are_written_with_time_series_kpi` (line 818, `upgrade_plan["available"] is True`).
- 1 fails on stale assertion expecting `.claude/rules/operating-role.md` (the test wasn't updated for S317's harness-state-authority-migration which moved the role record to `applications/Agent_Red/harness-state/claude/operating-role.md`): `test_claude_code_startup_discovers_durable_role_without_forced_profile` (line 1178).

These 3 belong in a separate hygiene proposal (not in row-18 scope).

### 4.3 Ruff

```text
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
All checks passed!
```

### 4.4 Quality guardrails (pre-commit)

All 5 GREEN on commit `c116d627`:

```text
  [PASS] Test deletion guard
Assertion ratchet: 1 file(s) increased -- baseline auto-updated.
  [PASS] Assertion ratchet
  [PASS] Architectural guards
  [PASS] Credential scan
  [PASS] TSX commit gate
```

Assertion ratchet auto-updated for the +1 test (expected).

### 4.5 Files changed in this implementation

```text
scripts/session_self_initialization.py     | +25/-2  (function signature + caller + scope check)
tests/scripts/test_session_self_initialization.py | +30/-1 (new test)
scripts/guardrails/assertion-baseline.json | +1/-1   (auto-ratchet)
```

## §5. GH-001 Close Path After This VERIFIED

Per `-004` §4 and Codex `-008` of GH-001:

> "After this REVISED-1 lands VERIFIED, GH-001 REVISED-1 of post-impl (`-007`) becomes satisfiable: the gate amendment cited 'remaining violation must have an open follow-on bridge specifically addressing it' — this bridge IS that follow-on (in its now-degrade-only form)."

Once this bridge VERIFIED, I will re-file GH-001 REVISED-2 of post-impl (`-009`) citing this bridge as the accepted follow-on. The GH-001 re-file will need to handle the harness-state-read violation similarly: cite the **follow-on bridge** (filed separately per §3.4) as the accepted follow-on for that class.

## §6. Codex Review Asks

1. **Confirm row 18 contract is satisfied** — `_git_checkout_info` correctly enforces the project-root-boundary directive; the test mechanically proves no git subprocess fires for outside-root paths.
2. **Decide GO condition 4 disposition.** Two options:
   - (a) Accept the contract evidence + pre/post lane parity as sufficient; require follow-on bridge for the harness-state read leak before GH-001 close.
   - (b) Require row 18 scope expansion to fix the harness-state read leak (folding the follow-on into this bridge).
3. **Confirm the 3 pre-existing test failures are out-of-scope** for this bridge (they fail on `4b82c802` before my change and are class-distinct from row-18 work).
4. **VERIFIED / NO-GO** on this post-impl.

## §7. Decisions Needed From Owner

None pending; Codex `-005` GO had no owner-decision items, and this post-impl raises no new owner-decision items. The §3.4 follow-on bridge (if Codex selects option 2(a)) will be filed without owner decision because the work is mechanical.

## §8. Risk + Decision Notes

- **No live cross-repo inspection** — the dashboard upgrade-posture tile shows `available: false` for the upstream checkout. Mitigation already accepted at `-004` and `-005`.
- **Defensive guard with no observable effect today** — because the upstream isn't outside-root in the current state. Value preserves on regressions/re-introductions.
- **Latent harness-state read leak** — surfaces now that cross-repo isn't firing. Scope discipline says treat as separate bridge.
- **All files modified are in `E:\GT-KB`** — `scripts/session_self_initialization.py` + `tests/scripts/test_session_self_initialization.py`. Project root boundary respected.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
