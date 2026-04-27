NO-GO

# Loyal Opposition Review - GENERATOR-HARDENING-001 Scoping Proposal

Reviewed: 2026-04-27
Subject: `bridge/generator-hardening-001-001.md`
Scope: scoping proposal for hardening `scripts/session_self_initialization.py` project-root threading
Verdict: NO-GO

## Prior Deliberations

Relevant deliberation search was performed against `groundtruth.db` before review.

- No exact prior deliberation was found for `GENERATOR-HARDENING-001`, `generator hardening`, `dashboard generator`, or `session_self_initialization.py` project-root threading.
- Relevant context exists in `DELIB-1106` for the Wave 2 implementation umbrella and in the Slice 11 bridge thread, especially `bridge/gtkb-isolation-016-phase8-wave2-slice11-016.md`, which verified the audit-hook lane and recorded the first live generator-hardening signal.
- The proposal's cited work-list row is present at `memory/work_list.md:31`.

## Claim

NO-GO. The proposal correctly identifies the main `PROJECT_ROOT` leak surface and proposes the right broad direction: thread `project_root` through internal consumers, keep harness-home paths separate, and verify with the Slice 11 dashboard audit lane. However, the proposed fix explicitly keeps the CLI dashboard/history defaults unchanged, which leaves a project-root bypass in the normal generator entry point.

## Finding 1 - CLI output defaults still target the canonical root when `--project-root` is overridden

Severity: P1

### Evidence

- `scripts/session_self_initialization.py:89` binds `DEFAULT_DASHBOARD_DIR = PROJECT_ROOT / "docs" / "gtkb-dashboard"`.
- `scripts/session_self_initialization.py:90` binds `DEFAULT_HISTORY_PATH = PROJECT_ROOT / "memory" / "gtkb-dashboard-history.json"`.
- `scripts/session_self_initialization.py:5232` accepts `--project-root`.
- `scripts/session_self_initialization.py:5233` sets `--dashboard-dir` default to `DEFAULT_DASHBOARD_DIR`.
- `scripts/session_self_initialization.py:5234` sets `--history-path` default to `DEFAULT_HISTORY_PATH`.
- `scripts/session_self_initialization.py:5339` to `:5342` passes `args.dashboard_dir.resolve()` and `args.history_path.resolve()` into `write_dashboard_and_report(...)`.
- The proposal's section 4.4 says to keep Type A and Type E unchanged: `PROJECT_ROOT` remains the fallback origin, and `DEFAULT_DASHBOARD_DIR` / `DEFAULT_HISTORY_PATH` remain argparse defaults.

### Risk / Impact

If a caller invokes the generator with only `--project-root <child-root>`, the model reads may be routed to the child root after the Type B/C/D fixes, but dashboard and history output paths still default to the canonical `E:/GT-KB/docs/gtkb-dashboard` and `E:/GT-KB/memory/gtkb-dashboard-history.json`. That contradicts the stated cutover goal: operate cleanly inside `applications/Agent_Red/` or a sandbox when `--project-root` is provided.

The Slice 11 dashboard lane currently masks this gap because `_dashboard_regen.py` passes explicit sandbox paths:

- `scripts/rehearse/_dashboard_regen.py:333` to `:341` builds `--project-root`, `--dashboard-dir`, and `--history-path` together.

That is useful verification for the lane, but it is not sufficient for the generator's public CLI contract.

### Recommended Action

Revise the scope so `--dashboard-dir` and `--history-path` default to `None` at argparse level and are derived from the resolved `project_root` after parsing when omitted:

```python
dashboard_dir = args.dashboard_dir.resolve() if args.dashboard_dir else project_root / "docs" / "gtkb-dashboard"
history_path = args.history_path.resolve() if args.history_path else project_root / "memory" / "gtkb-dashboard-history.json"
```

Likewise, remove `DEFAULT_DASHBOARD_DIR` / `DEFAULT_HISTORY_PATH` defaults from `write_dashboard_and_report(...)`, or make them explicit CLI-only compatibility constants that are not used when a caller provides a non-default `project_root`.

Add a regression test that calls the generator entry path with a temporary `--project-root` and no explicit `--dashboard-dir` / `--history-path`, then asserts all output paths are under that temporary root and no canonical dashboard/history paths are touched. This can be a unit-level argument-resolution test if a full render is too expensive.

## Finding 2 - `_local_env_value()` also needs project-root threading, not only `_local_env_values()`

Severity: P2

### Evidence

- `scripts/session_self_initialization.py:638` defines `_local_env_values()` with no project-root parameter and reads `PROJECT_ROOT` at `:646`.
- `scripts/session_self_initialization.py:659` defines `_local_env_value(...)` and calls `_local_env_values()` without a project-root parameter.
- The proposal's section 4.2 names `_local_env_values(project_root: Path)` but does not explicitly name `_local_env_value(...)` or its callers.

### Risk / Impact

Updating only `_local_env_values()` is not enough if `_local_env_value()` remains parameterless. Every caller of `_local_env_value()` would still lack the project-root context needed to choose the correct `.env.local` / `env.local` file, or the implementation would be forced back toward a global cache.

### Recommended Action

Include `_local_env_value(project_root: Path, name: str, default: str = "")` in the scope, and convert `_LOCAL_ENV_CACHE` to either no cache or a cache keyed by resolved project root.

## Required Revision

1. Add CLI output-path default derivation to the scope: `--dashboard-dir` and `--history-path` must derive from the resolved `--project-root` when omitted.
2. Add verification that `--project-root <tmp-root>` without explicit output-path arguments writes dashboard/history/report artifacts under `<tmp-root>`, not under canonical `PROJECT_ROOT`.
3. Explicitly include `_local_env_value(...)` and its callers in the environment-file threading plan.
4. Keep the current good parts: Type B/C/D project-root threading, source-verification of external import callers, Type F harness-home paths as a follow-on bridge, and Slice 11 audit-lane verification.

## Decision Needed From Owner

None. This is a technical scoping correction for Prime Builder.

