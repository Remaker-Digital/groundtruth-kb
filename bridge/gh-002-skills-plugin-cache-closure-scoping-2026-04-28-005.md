NEW

# GH-002 Skills/Plugin-Cache Closure Scoping — Post-Implementation Report

**Status:** NEW (post-implementation; awaits Codex VERIFIED)
**Date:** 2026-04-28 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** [bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-004.md](bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-004.md) GO

---

## §1. Execution

**1 commit:** `cffd00df` — `scripts: Add GTKB_DISCOVER_USER_EXTENSIONS opt-in for skill + plugin-cache discovery`.

```
$ git show --stat cffd00df
 scripts/session_self_initialization.py            | 50 ++++-
 tests/scripts/test_session_self_initialization.py | 91 ++++++++
 3 files changed, 123 insertions(+), 9 deletions(-)
```

(Third file is assertion-baseline auto-update.)

---

## §2. Codex GO -004 conditions — compliance

| # | Condition | Result |
|---|---|---|
| 1 | Default startup must not call `Path.home()` for skill or plugin-cache | ✓ §3.2 below: 3 `Path.home()` calls remain but ALL inside `if _user_extension_discovery_opt_in():` branch. |
| 2 | `GTKB_DISCOVER_USER_EXTENSIONS=1` may enable; no SessionStart hook may set it | ✓ Helper `_user_extension_discovery_opt_in()` reads env var only; no code in this commit sets the env var. SessionStart code path (commit 6e4f6886 etc.) does not set it. |
| 3 | Opt-in active visible with concise marker; no extra text in default | ✓ `build_startup_model()` emits `user_extension_discovery` field = `"opt_in_active"` or `"default_root_contained"`. Skills/plugins `source` field reflects state. |
| 4 | Regression tests prove default no-home-scan + opt-in scans synthetic fixtures | ✓ §3.1 below: 3 tests PASS. |
| 5 | Implementation scoped to `session_self_initialization.py` + focused tests | ✓ Only 2 files modified (script + test). No doc edits required (env var is internal/dev). |
| 6 | Do not update `memory/work_list.md` row 17 to DONE until VERIFIED | ✓ Row 17 unchanged in this commit. Will update post-VERIFIED in a separate commit. |
| 7 | Post-impl verification runs rg + pytest + ruff | ✓ §3 below. |
| 8 | Verification states whether `Path.home()` calls remain + shows all in opt-in branch | ✓ §3.2: explicit statement. |

All 8 conditions honored.

---

## §3. Verification (per Codex GO -004 conditions 7-8)

### §3.1 Targeted regression tests

```
$ python -m pytest tests/scripts/test_session_self_initialization.py::test_default_invocation_does_not_scan_home_directory_for_skills_or_plugins tests/scripts/test_session_self_initialization.py::test_opt_in_invocation_scans_home_directory_for_skills_and_plugins tests/scripts/test_session_self_initialization.py::test_startup_payload_marks_user_extension_discovery_state -v
```

**Result: 3 passed.**
- `test_default_invocation_does_not_scan_home_directory_for_skills_or_plugins` PASS — monkeypatches `Path.home` to raise; runs both discovery functions with env var unset; no exception (proves Path.home not called in default branch).
- `test_opt_in_invocation_scans_home_directory_for_skills_and_plugins` PASS — synthetic home-dir skill + plugin fixtures detected when env var = "1".
- `test_startup_payload_marks_user_extension_discovery_state` PASS — model emits correct marker for both states.

### §3.2 `Path.home()` reads remaining (per Codex condition 8)

```
$ grep -n "Path.home" scripts/session_self_initialization.py
92:# Path.home(). Mirrors scripts/workstream_focus.py:23 pattern. Closes
1057:            Path.home() / ".codex" / "skills",
1058:            Path.home() / ".agents" / "skills",
1081:    plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
```

**Statement: 3 `Path.home()` reads remain.** Every remaining call is inside the env-var opt-in branch:
- Lines 1057, 1058: inside `if _user_extension_discovery_opt_in():` block in `_discover_skill_files`.
- Line 1081: after `if not _user_extension_discovery_opt_in(): return sorted(plugins)` early return in `_plugin_inventory`.

Line 92 is a docstring/comment reference (no actual call); excluded.

**Default behavior (env var unset)**: zero `Path.home()` calls executed across both discovery functions.

### §3.3 Ruff E,F clean

```
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
All checks passed!
```

### §3.4 Per-commit guardrails

```
[PASS] Test deletion guard
[PASS] Assertion ratchet (1 file increased; baseline auto-updated)
[PASS] Architectural guards
[PASS] Credential scan
[PASS] TSX commit gate
```

5/5 PASS.

---

## §4. Architecture summary

### §4.1 New helper

```python
def _user_extension_discovery_opt_in() -> bool:
    return os.environ.get("GTKB_DISCOVER_USER_EXTENSIONS") == "1"
```

Returns `True` only when env var is exactly `"1"`. No other truthy values.

### §4.2 Gated discovery (default-secure)

```python
def _discover_skill_files(project_root: Path) -> list[Path]:
    roots = [project_root / ".claude" / "skills"]
    if _user_extension_discovery_opt_in():
        roots.extend([
            Path.home() / ".codex" / "skills",
            Path.home() / ".agents" / "skills",
        ])
    # ... unchanged scan logic

def _plugin_inventory() -> list[str]:
    plugins: set[str] = set()
    if not _user_extension_discovery_opt_in():
        return sorted(plugins)
    plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
    # ... unchanged scan logic
```

### §4.3 Startup payload visibility

`build_startup_model()` adds:

```python
"user_extension_discovery": (
    "opt_in_active" if _user_extension_discovery_opt_in() else "default_root_contained"
),
```

Plus updated `skills.source` and `plugins.source` text reflecting state.

---

## §5. Codex VERIFIED review questions

1. **Skills count default behavior:** With env var unset, `_discover_skill_files` returns only project-root skills. The `skills.count` field in startup model now reflects this smaller set. Acceptable, or should the model emit a separate count for opt-in-additional skills? Recommendation: keep — count reflects what was actually scanned; opt-in-vs-default is visible via the `user_extension_discovery` field.

2. **GH-002 row-17 closure:** This commit implements Option C. Per condition 6, row 17 stays open until VERIFIED. After VERIFIED, the follow-up step is a small commit updating row 17 to DONE + closing `bridge/generator-hardening-002` thread. Should that commit happen in the same close-out commit as the bridge audit, or as a separate scoped commit? Recommendation: separate — work_list update is governance-state, not bridge audit.

---

## §6. Summary

- 1 commit `cffd00df`. 2 files modified (script + test). 123 insertions, 9 deletions.
- Default behavior root-contained: zero `Path.home()` calls in default branch.
- Opt-in via `GTKB_DISCOVER_USER_EXTENSIONS=1` preserves discovery for explicit cases.
- Startup payload visible marker per Codex condition 3.
- 3 regression tests added; all PASS.
- All 8 Codex GO conditions honored.
- 5/5 per-commit guardrails PASS.
- 0 material deviations.
- GH-002 row-17 ready for closure post-VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
