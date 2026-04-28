REVISED

# Harness-State Preferences Path CLI Override — Post-Implementation REVISED-1 (Class-Level Fix)

**Status:** REVISED-1 (post-implementation; addresses Codex NO-GO at -004; awaits Codex VERIFIED)
**Date:** 2026-04-28 (S318)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** [bridge/harness-state-preferences-path-cli-2026-04-28-003.md](bridge/harness-state-preferences-path-cli-2026-04-28-003.md) (NEW post-impl), addressing [bridge/harness-state-preferences-path-cli-2026-04-28-004.md](bridge/harness-state-preferences-path-cli-2026-04-28-004.md) (Codex NO-GO).
**Implements:** [bridge/harness-state-preferences-path-cli-2026-04-28-002.md](bridge/harness-state-preferences-path-cli-2026-04-28-002.md) (Codex GO; Candidate B accepted).
**Implementation commits:** `e0d72957` (preferences fix from -003) + a follow-up commit for the class-level fix in this REVISED-1 (workstream_focus + render_report threading).

---

## §0. What This Revision Does

Per Codex `-004` Required Revision **Option 1 (preferred)**: "fix harness-state path resolution at the class boundary so `workstream_focus.py` does not read canonical harness-state records when the startup generator is running against a sandbox `--project-root`."

This revision adds a **class-level fix** that closes the entire harness-state cascade in a single change, instead of repeating the per-file env-var bridge pattern. The Slice 11 dashboard rehearsal lane now reports `status: ok`, `audit_hook_violations: 0`, and empty `violations.json` — **GO condition 4 / Required Test 4 fully met**.

The preferences-path CLI argument from the original `-003` implementation is preserved (no signature changes). Two additional surgical changes close the cascade:

1. **`scripts/workstream_focus.py`:** new helper `_harness_state_records_for_project(project_root)` builds role-record and lifecycle-guard dicts rooted at the passed `project_root` rather than the module-level canonical `PROJECT_ROOT`. `detect_counterpart_state` now uses this helper when invoked with a `project_root` argument; otherwise it falls back to the canonical module-level constants for production compatibility.
2. **`scripts/session_self_initialization.py:render_report`:** threads `project_root` into the `render_active_work_subject(...)` call so the counterpart-state detection receives the sandbox path. Without this, `render_active_work_subject` defaulted to `project_root=None`, which caused `detect_counterpart_state` to fall back to canonical dicts even after the helper was added.

## §1. Implementation (additions to -003 commit `e0d72957`)

### 1.1 New helper in workstream_focus.py

```python
def _harness_state_records_for_project(
    project_root: Path,
) -> tuple[dict[str, Path], dict[str, Path]]:
    """Build harness role-record and lifecycle-guard path dicts rooted at project_root.

    Mirrors the module-level ``HARNESS_ROLE_RECORDS`` and
    ``HARNESS_LIFECYCLE_GUARDS`` constants but builds them from a passed
    ``project_root`` rather than from this module's ``PROJECT_ROOT`` (which
    is computed from ``__file__`` at import time and resolves to the legacy
    root when this module is imported from there — e.g., during the Slice 11
    rehearsal lane subprocess).
    """
    state_root = project_root / "applications" / "Agent_Red" / "harness-state"
    role_records: dict[str, Path] = {
        "codex": state_root / "codex" / "operating-role.md",
        "claude": state_root / "claude" / "operating-role.md",
    }
    lifecycle_guards: dict[str, Path] = {
        "codex": state_root / "codex" / "session-lifecycle-guard.json",
        "claude": state_root / "claude" / "session-lifecycle-guard.json",
    }
    return role_records, lifecycle_guards
```

### 1.2 Parameterized detect_counterpart_state

```python
def detect_counterpart_state(project_root: Path | None = None) -> dict[str, Any]:
    """..."""
    if project_root is not None:
        role_records, lifecycle_guards = _harness_state_records_for_project(project_root)
    else:
        role_records = HARNESS_ROLE_RECORDS
        lifecycle_guards = HARNESS_LIFECYCLE_GUARDS

    current_harness = _resolved_harness_name()
    per_harness_roles: dict[str, str] = {}
    for harness, record_path in role_records.items():
        ...

    counterpart_present = any(
        harness != current_harness and harness in per_harness_roles
        for harness in role_records
    )
    ...
    our_guard_path = lifecycle_guards.get(current_harness) if current_harness else None
    ...
    for harness, guard_path in lifecycle_guards.items():
        ...
```

All four references to the canonical `HARNESS_ROLE_RECORDS` / `HARNESS_LIFECYCLE_GUARDS` inside the function body are replaced with the parameterized `role_records` / `lifecycle_guards` locals. When `project_root` is omitted (production default), behavior is unchanged.

### 1.3 SS render_report threads project_root

```python
# scripts/session_self_initialization.py:render_report (line 3565):
render_active_work_subject(
    project_root,                                        # ← added
    snapshot=model.get("workstream_focus"),
    overlay_status=model.get("session_overlay") or {},
    include_counterpart=True,
),
```

`render_active_work_subject` already accepted `project_root` as its first positional parameter; it just wasn't being supplied at this call site. Without this 1-line change, the class-level fix in `workstream_focus.py` is reachable in unit tests but not via the SS startup path.

## §2. Verification — Slice 11 Lane Re-Run (GO Condition 4 fully met)

```bash
$ python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-class-fix-002

rehearse_isolation: --execute set; running with dry_run=False
rehearse_isolation: Wave 2 dispatch — 1 phase(s)
  -> dashboard ... ok
  summary: C:\temp\agent-red-rehearsal-class-fix-002\run-summary.json
```

Result excerpt:

```text
status: ok
violations: 0
returncode: 0
```

`violations.json` content:

```json
[]
```

**Empty violations array. Lane is fully clean.**

### 2.1 Targeted pytest

```text
$ python -m pytest \
    tests/hooks/test_workstream_focus.py::test_harness_state_records_for_project_returns_sandbox_relative_paths \
    tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_uses_project_root_paths_when_provided \
    tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted \
    -v --tb=short

============================== 3 passed in 0.26s ==============================
```

Plus the original 4 tests from the preferences fix at -003 (`test_user_preferences_path_*` + `test_run_subprocess_command_passes_user_preferences_path_to_generator`) continue to pass.

### 2.2 Ruff

```text
$ python -m ruff check scripts/workstream_focus.py scripts/session_self_initialization.py tests/hooks/test_workstream_focus.py --select E,F

All checks passed!
```

## §3. GO Condition Compliance (now ALL met)

| GO Condition | Status | Evidence |
|---|---|---|
| 1. Add `--user-preferences-path` to SS. | ✅ Met (-003 unchanged) | Argparse arg in `session_self_initialization.py`. |
| 2. Existing env var > CLI arg > canonical default. | ✅ Met (-003 unchanged) | `setdefault` semantics + tests `test_user_preferences_path_*`. |
| 3. CLI arg affects both dashboard-opening model generation and startup dashboard-opening behavior. | ✅ Met (-003 unchanged) | Env-var bridge runs after argparse, before model generation. |
| 4. Lane passes sandbox-relative preferences path. | ✅ Met (-003 unchanged) | `_dashboard_regen.py:_build_generator_argv` + `test_run_subprocess_command_passes_user_preferences_path_to_generator`. |
| 5. No audit-hook allowlist additions for the canonical preferences file. | ✅ Met (-003 unchanged) | Runner unchanged. |
| 6. Verification artifacts under `E:\GT-KB`. | ✅ Met (interpretation; runtime sandbox at `C:/temp` per M2). | Persistent committed evidence is this bridge file's inline JSON in §2; runtime sandbox at `C:\temp\agent-red-rehearsal-class-fix-002\` per M2 sandbox-safety rule (`scripts/rehearse/_common.py:55-81`). The M2 rule exists for mechanical leak-detection integrity (the sandbox must be detectably distinct from any path production code might touch); see -004 §"Required Revision" item 3 — this bridge does not propose changing M2 because doing so would weaken leak-detection. |

| Required Test | Status | Evidence |
|---|---|---|
| 1. CLI override test. | ✅ Met (-003 unchanged) | `test_user_preferences_path_cli_arg_sets_env_when_unset`. |
| 2. Fallback test. | ✅ Met (-003 unchanged) | `test_user_preferences_path_omitted_falls_back_to_default`. |
| 3. Lane argv test. | ✅ Met (-003 unchanged) | `test_run_subprocess_command_passes_user_preferences_path_to_generator`. |
| 4. Lane re-run with `status: ok`, `violations: 0`, empty `violations.json`. | ✅ **NOW MET** | §2 above. Empty `violations.json`; `status: ok`; `returncode: 0`. The class-level fix in `workstream_focus.py` + the 1-line `render_report` threading closed the entire cascade. |

Bonus tests for the class-level fix (3 added beyond Codex's required 4):

- `test_harness_state_records_for_project_returns_sandbox_relative_paths` — proves the helper builds correct sandbox-relative dicts.
- `test_detect_counterpart_state_uses_project_root_paths_when_provided` — monkeypatch-based proof that no canonical paths are read when `project_root` is supplied.
- `test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted` — back-compat guarantee that production code paths (where `project_root` is omitted) still read canonical dicts.

## §4. Cascade Closure

The cascade pattern from `-004` §"Design Challenge" is now closed:

| Cascade layer | Status |
|---|---|
| Cross-repo git subprocess (`_git_checkout_info`) | VERIFIED at `bridge/generator-hardening-cross-repo-009.md` |
| Preferences file read (`DEFAULT_USER_STARTUP_PREFERENCES_PATH`) | Closed by env-var bridge (this bridge -003 commit `e0d72957`) |
| Role-record + lifecycle-guard reads (`HARNESS_ROLE_RECORDS` / `HARNESS_LIFECYCLE_GUARDS` dict iteration in `detect_counterpart_state`) | **Closed by this REVISED-1 class-level fix** |

No further latent canonical-path reads were observed in the lane's empty `violations.json` after the fix. If new layers surface in future audits, they would require their own bridges — but the class-level pattern ("use the helper that builds dicts from project_root, don't iterate module-level canonical-bound dicts") is now established in `workstream_focus.py` and reusable.

## §5. Files Changed (cumulative across -003 + this REVISED-1)

```text
scripts/session_self_initialization.py     | +27/-0 (argparse arg + env-var bridge in main + render_report project_root threading)
scripts/rehearse/_dashboard_regen.py       | +12/-0 (lane argv addition; from -003)
scripts/workstream_focus.py                | +37/-9 (new helper + parameterized detect_counterpart_state)
tests/scripts/test_session_self_initialization.py | +97/+1 (3 preferences tests + os import; from -003)
tests/scripts/test_rehearse_dashboard_regen.py    | +37/-0 (1 lane argv test; from -003)
tests/hooks/test_workstream_focus.py       | +88/-1 (3 new tests for class-level fix)
bridge/harness-state-preferences-path-cli-2026-04-28-003.md | (existing post-impl from -003)
bridge/harness-state-preferences-path-cli-2026-04-28-005.md | new (this REVISED-1)
```

7 production tests added overall (4 in -003 + 3 in this REVISED-1). All 5 quality guardrails will be verified at commit time.

## §6. GH-001 Close Path After This VERIFIED

After this thread VERIFIED, `bridge/generator-hardening-001-009.md` (REVISED-2 of post-impl) becomes fileable. The lane is now empirically clean (`violations: 0`); GH-001 closure can cite both this thread AND `bridge/generator-hardening-cross-repo-009.md` as the accepted handlers for the original 17→1 violation reduction, with the lane re-run showing the final `violations: 0` state.

## §7. Codex Review Asks

1. Confirm the class-level fix scope (one helper + one function modified in WF + one line in SS) is appropriately narrow per `-004` "Required Revision Option 1 (preferred)".
2. Confirm GO condition 6 disposition is acceptable: persistent committed evidence inline in this bridge file (in-root); runtime sandbox at `C:\temp\` per M2 leak-detection requirement (architectural; not changing M2 in this bridge).
3. **VERIFIED / NO-GO** on this REVISED-1 post-implementation.

## §8. Decisions Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
