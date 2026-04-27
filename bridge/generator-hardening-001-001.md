NEW

# GENERATOR-HARDENING-001 — Scoping Proposal

**Status:** NEW (scoping bridge; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Discovered by:** `bridge/gtkb-isolation-016-phase8-wave2-slice11-016.md` (Slice 11 audit-hook lane VERIFIED)
**Backlog row:** `memory/work_list.md` row 16 (filed 2026-04-27 S314)
**Implementation owner:** **Agent Red local** (source-verified — see §3)

---

## Prior Deliberations

Searched `groundtruth.db` for prior decisions on `PROJECT_ROOT`/project-root threading and the `session_self_initialization.py` generator. Closest hits:

- `DELIB-0879` (GTKB-ISOLATION-002 Phase 2 root and repository topology plan, 2026-04-?? owner_conversation): broader GT-KB/application separation context — supports parameterization in principle but does not mandate the per-call-site fix shape.
- `DELIB-1106` (Wave 2 implementation umbrella): Slice 11's audit-hook lane is the surfacing instrument; its VERIFIED status is the empirical baseline this proposal builds from.

**No prior deliberation directly addresses the project-root threading pattern in `session_self_initialization.py`.** The work_list row 16 entry (filed S314) is the canonical record of the discovery; this proposal is the first scoping artifact.

## 1. Problem statement

`scripts/session_self_initialization.py` (5,385 lines) generates the
session-startup dashboard, startup report, and proactive wrap-up report
per `GOV-SESSION-SELF-INITIALIZATION-001`. The generator accepts a
`--project-root` CLI argument (line 5232) but a meaningful number of
internal call sites bypass it by reading the module-level `PROJECT_ROOT`
global directly.

This is a latent correctness defect. When the generator is invoked from a
sandbox or a temporary directory (as Slice 11's audit-hook lane does for
its sample-render verification), it reaches outside the sandbox into the
canonical project tree. The audit-hook fail-closed mechanism reports
this as a violation; absent the fail-closed wrapper, the generator would
silently leak project state across the boundary.

Slice 11's `-013` log-only smoke captured **17 distinct violations**
across one render. Slice 11's `-015` fail-closed smoke captured **1
violation** (the first read; subsequent 16 were prevented by
`os._exit(99)` termination). Both numbers are reproducible.

ISOLATION-018 cutover (the next Phase 8 program) requires the generator
to operate cleanly inside the new `applications/Agent_Red/` namespace.
Either (a) the cutover skips dashboard regen on first run and hardens
later, or (b) the cutover prepares dashboards manually until hardening
ships. Neither is fatal, but both leave operational debt; this proposal
is option (c) — fix the generator.

## 2. Source-verified leak inventory

Verified by `grep -n PROJECT_ROOT scripts/session_self_initialization.py`
on commit `e5b17bc0`. The leak surface is larger than the work_list row
16 inventory suggested; categorizing by leak type:

### Type A — Module-level constants bound to `PROJECT_ROOT` (3 sites)

Used elsewhere in the module without a parameterized override path.

| Line | Symbol | Current binding |
|---|---|---|
| 88 | `PROJECT_ROOT` | `Path(__file__).resolve().parent.parent` (the global itself; intentional but consumed downstream) |
| 89 | `DEFAULT_DASHBOARD_DIR` | `PROJECT_ROOT / "docs" / "gtkb-dashboard"` |
| 90 | `DEFAULT_HISTORY_PATH` | `PROJECT_ROOT / "memory" / "gtkb-dashboard-history.json"` |

### Type B — Direct `PROJECT_ROOT` use in function bodies (3 sites)

Function does not accept a `project_root` parameter; reads the global directly.

| Line | Function | Read |
|---|---|---|
| 646 | `_local_env_values()` | `PROJECT_ROOT / ".env.local"`, `PROJECT_ROOT / "env.local"` |
| 1161 | (release-tag enumeration) | `_command_output(["git", "ls-remote", ...], PROJECT_ROOT, ...)` |
| 1182 | (branch-head probe) | `_command_output(["git", "ls-remote", ...], PROJECT_ROOT, ...)` |

### Type C — Function signature `project_root: Path = PROJECT_ROOT` defaults (7 sites)

Parameter exists but defaults to the global, so a caller that omits the kwarg silently leaks. Easy to miss because the function *looks* parameterized.

| Line | Function |
|---|---|
| 152 | `_repo_operating_role_path` |
| 157 | `operating_role_path` |
| 177 | `_display_role_mapping_source` |
| 196 | `_role_metadata` |
| 2483 | (mid-module helper) |
| 2533 | (mid-module helper) |
| 4862 | (late-module helper) |

### Type D — Passing `PROJECT_ROOT` global instead of received parameter (1 site)

Caller has access to a `model` containing project info but ignores it.

| Line | Function | Leak |
|---|---|---|
| 3434 | `render_report(model, dashboard_link)` | calls `_load_pending_owner_decisions(PROJECT_ROOT)` |

### Type E — Argparse default (1 site, NOT a leak)

| Line | Symbol | Status |
|---|---|---|
| 5232 | `parser.add_argument("--project-root", ..., default=PROJECT_ROOT)` | This IS the right pattern. `PROJECT_ROOT` as the CLI default is correct; the leak is in *internal* call sites that bypass the parsed argument. |

### Type F — User-home harness-config reads (8+ sites; SEPARATE concern)

These are `Path.home()`-rooted, not `PROJECT_ROOT`-rooted. They legitimately
point at the current user's harness config (Codex / Claude Code) and are
not project-root leaks. They become a problem only in test/sandbox contexts
where the user-home should be redirectable. Per work_list row 16: "harness-config
paths use a `--harness-config-root` arg with default to current home".

| Line | Symbol | Read |
|---|---|---|
| 91 | `DEFAULT_USER_STARTUP_PREFERENCES_PATH` | `Path.home() / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"` |
| 104 | `HARNESS_ROLE_RECORDS["codex"]` | `Path.home() / ".codex" / "agent-red-hooks" / "operating-role.md"` |
| 105 | `HARNESS_ROLE_RECORDS["claude"]` | `Path.home() / ".claude" / "agent-red-hooks" / "operating-role.md"` |
| 108-109 | session-lifecycle-guard | (matching `Path.home()` pattern) |
| 1027 | skill scan | `Path.home() / ".codex" / "skills"` |
| 1049 | plugin cache | `Path.home() / ".codex" / "plugins" / "cache"` |

### Total leak count

- **Type A + B + C + D = 14 distinct call sites** (matches Slice 11 `-013`'s "17 distinct violations" within ±3, attributable to per-render multi-call paths and at least one subprocess-CWD leak not captured by static grep).
- **Type F = 8+ harness-config sites** (separate sub-feature).

## 3. Implementation owner determination

**Agent Red local.** Source-verified:

```text
$ ls groundtruth_kb 2>&1
ls: cannot access 'groundtruth_kb': No such file or directory

$ wc -l scripts/session_self_initialization.py
5385 scripts/session_self_initialization.py
```

The local `E:/GT-KB/` tree contains `scripts/session_self_initialization.py`
but no `groundtruth_kb/` framework package. The generator is therefore an
adopter-local artifact, not a framework artifact, regardless of whether
`GOV-SESSION-SELF-INITIALIZATION-001` is framework-class governance.

If a future framework refactor lifts the generator into `groundtruth_kb/`
(e.g., as part of the IDP-style multi-application support beyond
ISOLATION-018), this hardening work moves with it. The fix shape is
identical either way: parameterize the leak sites.

## 4. Proposed fix design

Three coordinated changes. All are local to `scripts/session_self_initialization.py`
and its callers; no upstream framework changes required.

### 4.1 Eliminate Type C defaults (the highest-volume class)

Change function signatures from:

```python
def operating_role_path(project_root: Path = PROJECT_ROOT, *, ...) -> Path:
```

to:

```python
def operating_role_path(project_root: Path, *, ...) -> Path:
```

Every caller becomes responsible for passing `project_root` explicitly.
The single legitimate "I have no project root context" entry point is
the CLI in `main()`, which already has `args.project_root` from the
parsed `--project-root`. All internal callers within `main()`'s call
graph will be threaded.

This is mechanical: 7 functions × ~3-15 caller sites each ≈ ~40-50
edited lines, primarily in the function-call argument list.

### 4.2 Add `project_root` parameter to Type B functions

Three functions currently have no `project_root` parameter:

- `_local_env_values()` → `_local_env_values(project_root: Path)`
- The two `_command_output(["git", "ls-remote", ...], PROJECT_ROOT, ...)` call sites are inside helper functions (need to read those signatures and thread `project_root` through)

The `_LOCAL_ENV_CACHE` global at line ~641 (cache for `_local_env_values()`)
becomes a per-`project_root` cache or is dropped entirely (re-reading
`.env.local` once per session is cheap; the cache likely exists for
lower-overhead repeated calls within one render).

### 4.3 Fix the Type D site

`render_report(model, dashboard_link)` at line 3426 → either thread
`project_root` as a third positional arg, or pull it from `model` if
the model already carries the project_root (likely; model is built by
upstream code that has `project_root` in scope).

### 4.4 Keep Type A and Type E unchanged

`PROJECT_ROOT` global stays as the canonical default origin — it's the
fallback when no `--project-root` is passed. `DEFAULT_DASHBOARD_DIR` /
`DEFAULT_HISTORY_PATH` stay as module constants for use as argparse
defaults. The remediation is in *consumers*, not in the constants
themselves.

### 4.5 Type F (harness-config leaks): file as sub-bridge if owner agrees

Add a `--harness-config-root` argparse argument defaulting to `Path.home()`.
Thread it through the harness-config call sites (Type F inventory above).
Lower priority than Type A-D because Type F doesn't break ISOLATION-018
cutover — only test/sandbox isolation. **Recommendation:** ship as a
follow-on bridge after Type A-D land, not bundled.

## 5. Verification gate

The verification gate is empirical and reuses Slice 11's audit-hook lane:

```text
python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-generator-hardening-verify
```

**Expected post-hardening evidence in the lane's output `dashboard-regen-result.json`:**

- `status: ok` (was: `error` per Slice 11 `-015` fail-closed evidence)
- `violations_count: 0` (was: 1 fail-closed first violation, with 16 prevented)
- No quarantine artifacts under `<output_dir>/dashboard_regen/quarantine/`
- Sample-render directory `C:/temp/<sample_render>` contains the rendered
  dashboard with all paths resolved relative to the `--project-root`,
  not `PROJECT_ROOT`.

**Pre-impl baseline measurement** (capture before edit so we can quantify
delta in the post-impl report):

```text
# Run Slice 11 dashboard lane in log-only mode (set GTKB_AUDIT_HOOK_MODE=log
# or equivalent — needs verification at impl time) to enumerate every
# violation without short-circuiting at the first.
```

If log-only mode is not available, capture the count by running the
fail-closed mode iteratively (each run prevents one new violation; count
= number of runs to reach `violations_count: 0`).

## 6. Risk + decision notes

- **Single-file change.** All edits land in `scripts/session_self_initialization.py`
  (and possibly its tests). No multi-file coordination required.
- **Cross-file caller updates may be needed** if any external script imports
  these functions. Source-verify at impl time:
  `grep -rn "from session_self_initialization import\|from scripts.session_self_initialization import"`.
- **Tests already exist** (`tests/scripts/test_session_self_initialization.py` per `GTKB-GOV-011 - DONE`).
  The hardening should add at least one test that asserts the generator
  honors a non-default `project_root` (e.g., a tmp-path render produces
  no reads of `PROJECT_ROOT`-bound paths).
- **No KB schema or assertion changes.** Quality dashboard, MemBase exports,
  release-readiness lanes are untouched.
- **Backwards-compatibility.** Removing `= PROJECT_ROOT` defaults from
  functions is a *breaking* internal API change. If any external caller
  invokes these functions without `project_root`, that caller errors at
  edit time. This is the desired behavior — failures are explicit, not
  silent.

## 7. Sequencing

- **Non-blocking parallel program.** Can ship before, alongside, or after
  ISOLATION-018 cutover. Cutover does not require this fix (cutover can
  use option (a) skip-dashboard-regen-first-run, or option (b) manual
  dashboard prep, per §1).
- **Recommended order:** Type A-D in the next implementation bridge (one
  bridge thread), Type F as a follow-on if owner approves expanded scope.
- **No dependency on bridge-poller NO-GO at `-005`** (work_list row 14)
  or any other open thread.

## 8. Decision needed from owner

1. **Scope boundary.** Confirm Type A-D in scope, Type F deferred to
   follow-on bridge. (Default per this proposal: yes.)
2. **Caller-update strategy.** If `grep` at impl time finds external
   callers of any Type C function, prefer (a) update all callers, or
   (b) keep `PROJECT_ROOT` default with a deprecation marker for one
   release cycle? (Default per this proposal: (a) update all callers
   immediately — no deprecation cycle for internal-only modules.)
3. **Pre-impl baseline.** Should the implementation bridge include a
   pre-edit log-only run that enumerates every leak before touching
   code, so the post-impl report can show "17 → 0" delta? (Default
   per this proposal: yes; cheap evidence.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
