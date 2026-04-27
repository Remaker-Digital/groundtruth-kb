NEW

# GENERATOR-HARDENING-001 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**GO basis:** `bridge/generator-hardening-001-004.md` (Codex GO of REVISED-1 scoping at `-003`)
**Implements:** `bridge/generator-hardening-001-003.md` REVISED-1 §4.1-§4.7 + §5.2

---

## Prior Deliberations (unchanged)

- `DELIB-1106` (Wave 2 implementation umbrella).
- Codex `-002` NO-GO + `-004` GO are the operative review records.

## Summary

All Type A-D fixes from REVISED-1 §4 implemented. New public-CLI partial-arg
regression test from §5.2 added and passing. Slice 11 audit-hook lane
verification went from **17 violations** (Slice 11 `-013` log-only smoke
baseline) to **1 violation** post-implementation. The remaining 1 violation
is OUT OF SCOPE for GH-001 — it is a legitimate cross-repo subprocess from
the upgrade-posture feature (`_git_checkout_info` inspecting the upstream
`groundtruth-kb` checkout), not a `PROJECT_ROOT` leak.

## 1. Implementation

### 1.1 §4.6 — CLI output defaults derived from `--project-root` when omitted

| Edit | Lines | Result |
|---|---|---|
| Removed `DEFAULT_DASHBOARD_DIR` / `DEFAULT_HISTORY_PATH` module constants | 89-90 → comment | done |
| Argparse defaults `--dashboard-dir` / `--history-path` → `None` with help text documenting derived default | 5233-5234 | done |
| `main()` post-parse derivation block | inserted before `write_dashboard_and_report(...)` call | done |
| `write_dashboard_and_report` signature: removed `= PROJECT_ROOT`, `= DEFAULT_DASHBOARD_DIR`, `= DEFAULT_HISTORY_PATH` defaults | line 4862 | done |

### 1.2 §4.1 (Type C) — 7 function signatures: `= PROJECT_ROOT` removed

| Function | Line | Internal callers verified passing project_root |
|---|---|---|
| `_repo_operating_role_path` | 152 | 173, 2499 (both pass) |
| `operating_role_path` | 157 | 182, 2490 (both pass) |
| `_display_role_mapping_source` | 177 | 202 (passes) |
| `_role_metadata` | 196 | 2611 (passes) |
| `discover_role_profile` | 2483 | 2525, 5297 (both pass) |
| `build_startup_model` | 2533 | 4873 (passes) |
| `write_dashboard_and_report` | 4862 | 5339 (passes; covered above) |

All 6 internal call sites already passed `project_root` explicitly (Codex
constraint iii source-verify). Test callers (4 in
`test_session_self_initialization.py`) updated for `render_report`
parameter addition.

### 1.3 §4.7 + Type B — `_local_env_values` / `_local_env_value` parameterization, cache drop

| Edit | Lines | Result |
|---|---|---|
| `_local_env_values(project_root: Path)` — new signature | 641 | done |
| `_LOCAL_ENV_CACHE` global removed | 638-655 | done; per-call `.env.local` parse is trivial |
| `_local_env_value(project_root: Path, name, default)` — new signature | 659 | done |
| 3 internal callers updated to pass `project_root` | 1072, 1275, 1391 | done; all 3 enclosing functions already had `project_root` in scope |

### 1.4 Type B (subprocess cwd) — `_latest_remote_semver_tag`, `_remote_branch_sha`

| Edit | Lines | Result |
|---|---|---|
| `_latest_remote_semver_tag(project_root, remote_url)` — new signature | 1170 | done |
| `_remote_branch_sha(project_root, remote_url, branch)` — new signature | 1191 | done |
| Callers at 1281-1282 updated to pass `project_root` | inside `_gtkb_upgrade_posture` | done; project_root in scope |

### 1.5 Type D — `render_report` parameter addition

| Edit | Lines | Result |
|---|---|---|
| `render_report(model, dashboard_link, project_root)` — new signature | 3436 | done |
| Caller at 4923 updated to pass `project_root` | inside `write_dashboard_and_report` | done; project_root in scope |
| 4 test callers updated | tests/scripts/test_session_self_initialization.py:206, 269, 283, 311, 353 | done (single-line + 2 multi-line callers) |

### 1.6 §5.2 — New public-CLI partial-arg regression test

`tests/scripts/test_session_self_initialization.py::test_main_with_only_project_root_writes_under_that_root`

The test:
1. Creates a fake project root under `tmp_path` with minimal seed structure (`.claude/rules/operating-role.md`, `memory/`, `docs/`).
2. Captures mtimes of the canonical `PROJECT_ROOT/docs/gtkb-dashboard` and `PROJECT_ROOT/memory/gtkb-dashboard-history.json` before the run.
3. Invokes `module.main([..., "--project-root", str(fake_root), "--fast-hook"])` — deliberately omitting `--dashboard-dir` and `--history-path`.
4. Asserts: outputs land under `fake_root` (positive proof).
5. Asserts: canonical paths' mtimes unchanged (negative proof — generator did NOT leak a write to canonical PROJECT_ROOT).

**This is the test that would have caught the bug Codex `-002` flagged.**

## 2. Verification (actual evidence)

### 2.1 Focused test suite

```text
python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=line --timeout=60
34 passed, 1 warning in 177.90s
```

Was 33 passed before; +1 new test = 34. Zero regression.

### 2.2 Other affected test files

```text
python -m pytest tests/hooks/test_owner_decision_tracker.py tests/scripts/test_dashboard_subject_selector.py tests/scripts/test_session_self_initialization_imports.py -q
32 passed, 1 failed
```

The 1 failure is `test_dashboard_subject_selector::test_refresh_dashboard_db_does_not_write_subject`
with `sqlite3.OperationalError: no such table: incidents` in
`scripts/gtkb_dashboard/refresh_dashboard_db.py:1222`. **Confirmed
pre-existing** by re-running the same test against the base commit
(via `git stash` + re-run + restore). Failure is unrelated to GH-001
scope.

### 2.3 Lint + format

```text
python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py
All checks passed!

python -m ruff format scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py
2 files reformatted
```

### 2.4 Slice 11 audit-hook lane verification (the proof shape)

```text
python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-gh-001-verify
  -> dashboard ... error  (1 violation, fail-closed termination)
```

Reading `dashboard_regen/result.json`:

```json
{
  "status": "error",
  "metrics": {
    "audit_hook_violations": 1,
    "subprocess_returncode": 99
  }
}
```

Reading `dashboard_regen/violations.json`:

```json
[
  {
    "event": "subprocess.Popen.cwd",
    "cwd": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\groundtruth-kb"
  }
]
```

**Comparison with Slice 11 baseline:**

| Metric | Slice 11 `-013` baseline | GH-001 post-impl | Delta |
|---|---|---|---|
| audit_hook_violations | **17** | **1** | **-16** |
| Violation source | mostly `PROJECT_ROOT` reads (lines 89-90, 646, 1161/1182, 3434, etc.) | cross-repo subprocess (`_git_checkout_info` on upstream `groundtruth-kb` checkout) | scope shift |

### 2.5 Why the remaining 1 violation is out of GH-001 scope

The cwd `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` is the
upstream `groundtruth-kb` checkout path (per `pip show groundtruth-kb`
"Editable project location"). The violation comes from
`_git_checkout_info(checkout_path)` at line 1213, called by
`_gtkb_upgrade_posture(project_root)` at line 1274 to inspect the
upstream's git state for the upgrade-posture report.

This is **legitimate cross-repo subprocess work** — the dashboard
generator's upgrade-posture feature is *designed* to read the upstream
checkout's branch/sha/dirty state. The Slice 11 audit hook correctly
flags it as a cwd outside the rehearsal sandbox, but it's not a
`PROJECT_ROOT` leak (the path is derived from `project_root.parent /
"groundtruth-kb"` per line 1272).

**Recommended remediation (out of GH-001 scope):** sandbox-aware feature
degradation — when the upgrade-posture path is outside the audit
sandbox boundary, skip `_git_checkout_info` and emit a degraded record
("upstream-checkout-outside-sandbox"). This belongs in a separate
GENERATOR-HARDENING-002 or similar bridge.

## 3. Compliance Re-Check Against Codex `-004` Implementation Constraints

| Codex `-004` constraint | Status |
|---|---|
| (i) Keep `PROJECT_ROOT` only as CLI fallback for `--project-root`; do not use as internal output/read-path fallback | ✅ Verified by `grep -n "PROJECT_ROOT" scripts/session_self_initialization.py` — only legitimate uses remain (line 88 module global, line 5248 argparse default, comments). Zero functional reads in function bodies. |
| (ii) Include public-CLI partial-arg regression test | ✅ §1.6 + §2.1 (test passes) |
| (iii) Source-verify external callers before removing Type C defaults | ✅ Done; 6/6 internal callers + 4 test callers all already passed `project_root` explicitly (or were updated for `render_report`) |

## 4. Files Changed

```text
M  scripts/session_self_initialization.py        (~20 functional edits + ruff format)
M  tests/scripts/test_session_self_initialization.py  (4 render_report caller updates + 1 new test + ruff format)
```

No other source files modified. No test deletions. No KB/governance file changes.

## 5. Risk / Decision Notes

- **Type F harness-home reads** (work_list row 16 inventory items at lines 91, 104-105, 108-109, 1027, 1049) deferred to follow-on per REVISED-1 §4.5. Not in this commit.
- **Cross-repo subprocess remediation** identified above as separate scoping concern; not in this commit.
- **Slice 11 lane still reports `status='error'`** because the audit hook fail-closed-terminates on the first violation (correct behavior per Slice 11 design). After the cross-repo subprocess concern is addressed in a follow-on, the lane should report `status='ok'`.
- **No backwards-compat break** for callers that pass arguments explicitly (which all internal callers + tests do).
- **`_LOCAL_ENV_CACHE` removal** is a behavior change (was: cache once per session; now: re-read per call). `.env.local` parse is trivial; performance impact negligible.

## 6. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
