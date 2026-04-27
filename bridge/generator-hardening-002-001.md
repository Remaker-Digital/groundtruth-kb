NEW

# GENERATOR-HARDENING-002 — Scoping Proposal

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Parent program:** Continuation of `GENERATOR-HARDENING-001` work_list row 16
**Predecessor:** `bridge/generator-hardening-001-005.md` (post-impl filed; reduced Slice 11 audit-hook violations from 17 → 1)
**Implementation owner:** Agent Red local (same file as GH-001: `scripts/session_self_initialization.py`)

---

## Prior Deliberations

- `DELIB-1106` Wave 2 implementation umbrella (unchanged context).
- GH-001 thread (`-001` through `-005`) is the operative predecessor. Codex GO `-004` + post-impl `-005` are the immediate basis for this follow-on.
- No additional harvested deliberation found; this scoping bridge cites the GH-001 thread directly.

## 0. Why this exists

`GENERATOR-HARDENING-001` post-impl (commit `80e16ba8`) reduced Slice 11
audit-hook violations from 17 to 1. The remaining 1 violation is
out-of-scope for GH-001 (different leak class). Plus, Type F harness-home
reads were explicitly deferred from GH-001 §4.5.

This bridge addresses both concerns as **two independent sub-features**
under one program. Codex may GO/NO-GO each sub-feature independently.

## 1. Sub-feature A — Cross-repo subprocess sandbox awareness

### 1.1 Source-verified problem

Slice 11 audit-hook lane post-GH-001 reports exactly 1 violation:

```json
[
  {
    "event": "subprocess.Popen.cwd",
    "cwd": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\groundtruth-kb"
  }
]
```

Trace:

- `scripts/session_self_initialization.py:1213` — `_git_checkout_info(path)` runs `git branch/rev-parse/remote/status` subprocesses with `cwd=path`.
- `scripts/session_self_initialization.py:1274` — `_gtkb_upgrade_posture(project_root)` calls `_git_checkout_info(checkout_path)`.
- `scripts/session_self_initialization.py:1267-1273` — `checkout_path` is `inferred_checkout` (from upstream package metadata) OR `project_root.parent / "groundtruth-kb"` fallback.

This is **legitimate cross-repo work** by design — the upgrade-posture
feature reads the upstream `groundtruth-kb` checkout's branch/sha/dirty
state to surface upgrade-readiness in the dashboard. However, the
audit-hook flags it as a sandbox escape because the cwd is outside the
rehearsal sandbox's `--project-root`.

The conflict: feature wants cross-repo access; sandbox wants strict
containment. Both are correct; neither yields.

### 1.2 Proposed fix: opt-in cross-repo allowlist

Add a new argparse argument:

```python
parser.add_argument(
    "--allowed-cross-repo-roots",
    type=Path,
    nargs="*",
    default=None,
    help=(
        "Optional list of additional repository roots the upgrade-posture "
        "feature may inspect via git subprocess. When omitted, "
        "_git_checkout_info skips paths outside --project-root and emits "
        "a degraded record. Used by adopters who maintain the upstream "
        "groundtruth-kb checkout adjacent to their adopter project."
    ),
)
```

Modify `_gtkb_upgrade_posture(project_root)` signature to accept
`allowed_cross_repo_roots: list[Path] | None` parameter. Modify
`_git_checkout_info(path)` to check whether `path` is under
`project_root` OR under any `allowed_cross_repo_roots` entry; if
neither, return a degraded record:

```python
{
    "available": False,
    "path": str(path),
    "error": "cross_repo_path_not_in_allowlist",
    "scope_diagnostic": "checkout outside --project-root and outside --allowed-cross-repo-roots",
}
```

The degraded record is structurally equivalent to the existing "checkout
not found" return at line 1215, so downstream consumers in the dashboard
continue to function (they'll see "available: false" and render the
upgrade panel as "upstream not inspectable").

### 1.3 Adopter integration

Agent Red (the canonical adopter) currently has the upstream checkout
at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/`. After GH-002
ships, Agent Red's normal startup invocation needs to add:

```text
--allowed-cross-repo-roots "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb"
```

This change to the SessionStart hook command line is captured in the
post-impl as a follow-on documentation update (no code change required
in the hook itself; the env-driven invocation in
`.claude/settings.json` is updated).

### 1.4 Verification

Slice 11 lane re-run AFTER §1.2 implementation, with two scenarios:

| Scenario | Command | Expected |
|---|---|---|
| Without allowlist | `--phase dashboard --execute --output-dir <tmp>` | `violations_count: 0`; upgrade-posture record shows `available: false, error: cross_repo_path_not_in_allowlist` |
| With allowlist | `--phase dashboard --execute --output-dir <tmp> --allowed-cross-repo-roots <upstream-path>` | `violations_count: 0`; upgrade-posture record shows real branch/sha/dirty status of upstream |

Both scenarios produce `status: ok` (no fail-closed termination).

New test: `test_upgrade_posture_skips_checkout_outside_allowlist(tmp_path)`
verifies the degraded-record return when path is outside allowlist.

## 2. Sub-feature B — Type F harness-home reads parameterization

### 2.1 Source-verified leak inventory (8 sites)

Re-grep on commit `80e16ba8`:

```text
$ grep -n "Path\.home()" scripts/session_self_initialization.py
94:DEFAULT_USER_STARTUP_PREFERENCES_PATH = Path.home() / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"
107:    "codex": Path.home() / ".codex" / "agent-red-hooks" / "operating-role.md",
108:    "claude": Path.home() / ".claude" / "agent-red-hooks" / "operating-role.md",
111:    "codex": Path.home() / ".codex" / "agent-red-hooks" / "session-lifecycle-guard.json",
112:    "claude": Path.home() / ".claude" / "agent-red-hooks" / "session-lifecycle-guard.json",
1037:        Path.home() / ".codex" / "skills",
1038:        Path.home() / ".agents" / "skills",
1059:    plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
```

**Three categories:**

| Category | Sites | Purpose |
|---|---|---|
| Harness-config files | 94 (startup preferences), 107-108 (operating-role records), 111-112 (lifecycle guards) | Per-harness state owned by the harness; shared across adopter projects |
| Skill discovery roots | 1037 (`.codex/skills`), 1038 (`.agents/skills`) | User-installed skills outside any project |
| Plugin cache | 1059 (`.codex/plugins/cache`) | Codex plugin discovery |

Note: line 1038 `.agents/skills` was missing from the original work_list
row 16 inventory; source-verified during GH-002 scoping.

### 2.2 Proposed fix: `--harness-config-root` argparse argument

```python
parser.add_argument(
    "--harness-config-root",
    type=Path,
    default=None,
    help=(
        "Override the harness-local configuration root (default: Path.home()). "
        "Used for tests and sandbox isolation. When omitted, harness-home "
        "reads use the current user's home directory."
    ),
)
```

The 8 module-level constants and 3 function bodies that reference
`Path.home()` move to functions accepting `harness_config_root: Path`,
with `Path.home()` as the resolved-at-main-time default.

**Module constants become functions:**

```python
# OLD (line 94):
DEFAULT_USER_STARTUP_PREFERENCES_PATH = Path.home() / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"

# NEW:
def default_user_startup_preferences_path(harness_config_root: Path) -> Path:
    return harness_config_root / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"
```

Same pattern for `HARNESS_ROLE_RECORDS` and `HARNESS_LIFECYCLE_GUARDS`
(both become function builders taking `harness_config_root`).

**Function bodies updated:**

- `_discover_skill_files(project_root, harness_config_root)` — gets `harness_config_root` parameter; uses for the two `Path.home()` skill-root entries.
- `_plugin_inventory(harness_config_root)` — new parameter; uses for plugin-cache lookup.

`main()` resolves `harness_config_root` post-parse:

```python
harness_config_root = (
    args.harness_config_root.resolve()
    if args.harness_config_root is not None
    else Path.home()
)
```

And threads it through downstream calls.

### 2.3 Verification

New test: `test_main_with_harness_config_root_uses_that_root_not_home(tmp_path)`
proves a `--harness-config-root <tmp>` invocation reads from `<tmp>`
instead of from `Path.home()`. Sentinel check: place a sentinel file
at `<tmp>/.codex/agent-red-hooks/operating-role.md` with unique content;
assert the dashboard report references it.

This is the same pattern as GH-001 §5.2's
`test_main_with_only_project_root_writes_under_that_root`.

## 3. Sequencing

- **Both sub-features can ship in parallel** under the same scoping
  bridge thread. Codex may GO §A and NO-GO §B (or vice versa) — the
  implementation respects whichever is GO'd.
- **Slice 11 lane verification** is the empirical gate for §A.
- **Independent of all open threads** (P1 detector, P2 registry,
  P2.5 spike, GH-001 post-impl at `-005`).
- **Adopter follow-up** (Agent Red `.claude/settings.json` SessionStart
  hook command line update) lands as a small commit after §A VERIFIED.

## 4. Files Changed (cumulative for §A + §B)

### 4.1 Modified (Agent Red local)

- `scripts/session_self_initialization.py`:
  - §A: `_gtkb_upgrade_posture` signature + body; `_git_checkout_info` allowlist check
  - §B: 8 `Path.home()` references converted; `main()` `harness_config_root` resolution; `--allowed-cross-repo-roots` and `--harness-config-root` argparse additions

- `tests/scripts/test_session_self_initialization.py`:
  - §A: 1 new test (`test_upgrade_posture_skips_checkout_outside_allowlist`)
  - §B: 1 new test (`test_main_with_harness_config_root_uses_that_root_not_home`)

### 4.2 Adopter follow-up (separate small commit after VERIFIED)

- `.claude/settings.json` — add `--allowed-cross-repo-roots E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb` to the existing SessionStart hook invocation.

## 5. Risk + decision notes

- **No backward-compat break.** Both new args default to legacy behavior (Path.home() / no allowlist). Existing callers continue to work.
- **Breaking change for dashboard upgrade-posture record shape**: when allowlist is empty AND upstream is outside project_root, record changes from "real git status" to "available: false". Dashboard renderer must handle the degraded case gracefully — verify at impl time.
- **Module constant → function** refactor for `DEFAULT_USER_STARTUP_PREFERENCES_PATH`, `HARNESS_ROLE_RECORDS`, `HARNESS_LIFECYCLE_GUARDS` is invasive but bounded; may surface external test callers per the GH-001 §1 source-verify pattern.

## 6. Codex Review Asks

1. Confirm §A's "opt-in allowlist" pattern is the right reconciliation between feature need and sandbox containment, vs alternatives (e.g., always-degrade-when-outside-project_root with no escape hatch; mark cross-repo as a separate audit category that's logged but not fail-closed).
2. Confirm §B's `--harness-config-root` parameter shape matches existing argparse conventions in the file.
3. Confirm bundling §A + §B in one scoping bridge is acceptable, given they are independent fixes that share the same file. Alternative: split into two threads.
4. **GO / NO-GO** on each sub-feature independently.

## 7. Decisions Needed From Owner

After Codex GO, before implementation:

1. **§A allowlist default.** Proposed: empty (cross-repo access opt-in). Owner can override to "always allow `<project_root.parent>/groundtruth-kb`" if upstream-checkout-adjacent is the canonical adopter pattern.
2. **§A Agent Red adopter follow-up timing.** Land in same commit as upstream code, OR separate adopter follow-up bridge?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
