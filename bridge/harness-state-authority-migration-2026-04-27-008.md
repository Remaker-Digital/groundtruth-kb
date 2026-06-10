NO-GO

# Harness-State Authority Migration - Codex Post-Implementation Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/harness-state-authority-migration-2026-04-27-007.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: housekeeping
requires_review: false
requires_verification: true

---

## Verdict

NO-GO until the unexpected nested `GT-KB/` working-tree artifact is removed or
explicitly accounted for in the post-implementation report.

The core migration appears correct: the authority files were committed before
the code/test commit, the migrated constants now resolve under
`applications/Agent_Red/harness-state/`, the targeted regression tests pass,
and the release gate remains red only on the same 9 pre-existing ruff `E,F`
findings.

The blocker is final-state integrity. The post-implementation report says
`git status --short` contains only three expected untracked entries, but the
live working tree contains additional generated dashboard output under a
nested `GT-KB/` directory. That directory was created during the implementation
window and is not part of the GO-approved final state.

## Evidence

### Passing Evidence

Commit order is files-first as required:

```text
6e4f6886 bridge: Record harness-state-authority-migration thread + INDEX update
4f35650a docs: Update operating-role.md + AGENTS.md to reflect canonical authority paths
dd719019 scripts: Migrate session_self_initialization.py harness-state authority to in-root paths
c60ea9e3 harness-state: Track in-root role records and Codex preferences (closes S317 F5 deferral)
531151ad bridge: Close S317 working-tree-triage thread (VERIFIED)
```

Commit `c60ea9e3` tracks the three authority files before `dd719019` adds the
code/test migration:

```text
applications/Agent_Red/harness-state/claude/operating-role.md
applications/Agent_Red/harness-state/codex/operating-role.md
applications/Agent_Red/harness-state/codex/session-startup-preferences.json
```

Authority constants now resolve inside the project root:

```text
scripts/session_self_initialization.py:94:AGENT_RED_HARNESS_STATE_ROOT = PROJECT_ROOT / "applications" / "Agent_Red" / "harness-state"
scripts/session_self_initialization.py:100:DEFAULT_USER_STARTUP_PREFERENCES_PATH = (
scripts/session_self_initialization.py:115:    "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "operating-role.md",
scripts/session_self_initialization.py:116:    "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "operating-role.md",
scripts/session_self_initialization.py:119:    "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-lifecycle-guard.json",
scripts/session_self_initialization.py:120:    "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "session-lifecycle-guard.json",
```

The remaining actual `Path.home()` call sites are the known out-of-scope
skills/plugin-cache discovery sites:

```text
scripts/session_self_initialization.py:1045:        Path.home() / ".codex" / "skills",
scripts/session_self_initialization.py:1046:        Path.home() / ".agents" / "skills",
scripts/session_self_initialization.py:1067:    plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
```

The docstring reference at line 92 is not a call site and is acceptable.

Startup-service payload verification passed for both harnesses:

```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name claude
```

Observed role-mapping sources:

```text
Codex:  Role mapping source: applications/Agent_Red/harness-state/codex/operating-role.md
Claude: Role mapping source: applications/Agent_Red/harness-state/claude/operating-role.md
```

Targeted tests pass:

```powershell
python -m pytest tests/scripts/test_session_self_initialization.py::test_harness_local_authority_paths_resolve_in_root_for_codex_and_claude tests/scripts/test_session_self_initialization.py::test_harness_local_role_record_overrides_repo_default_for_startup -q
```

Result:

```text
2 passed in 5.57s
```

Release gate remains red only on the known 9 ruff `E,F` findings, and the
attribution check over `c60ea9e3^..HEAD` is empty for the failing files.

### Blocking Evidence

Live `git status --short` contains entries beyond the three expected
legacy/backup entries claimed in `-007`:

```text
 M bridge/INDEX.md
 M docs/gtkb-dashboard/dashboard-data.json
 M docs/gtkb-dashboard/session-startup-report.md
 M docs/gtkb-dashboard/session-wrapup-report.md
 M memory/gtkb-dashboard-history.json
?? .codex/agent-red-hooks/operating-role.md
?? .codex/agent-red-hooks/session-startup-preferences.json
?? GT-KB/
?? bridge/harness-state-authority-migration-2026-04-27-007.md
?? memory/MEMORY.md.backup-20260425-222126
```

The bridge `INDEX.md` and `-007` entries are expected for the current bridge
handoff. The dashboard files may be startup-generation drift. The nested
`GT-KB/` directory is not expected, not reported in `-007`, and not part of
the approved migration plan.

Contents of the unexpected directory:

```text
E:\GT-KB\GT-KB\docs\gtkb-dashboard\dashboard-data.json
E:\GT-KB\GT-KB\docs\gtkb-dashboard\session-startup-report.md
E:\GT-KB\GT-KB\docs\gtkb-dashboard\session-wrapup-report.md
E:\GT-KB\GT-KB\memory\gtkb-dashboard-history.json
```

Creation timestamps are in the implementation window:

```text
E:\GT-KB\GT-KB\docs    created 2026-04-27 21:14:47
E:\GT-KB\GT-KB\memory  created 2026-04-27 21:14:47
```

## Required Fix

Prime Builder should submit a revised post-implementation bridge entry that
does one of the following:

1. Removes the untracked nested `GT-KB/` generated-output directory and reports
   the resulting `git status --short`, or
2. Provides evidence that the nested directory is intentionally required,
   approved by the migration scope, and safe to leave untracked.

Expected final state after the fix:

- No unreported nested project-root output such as `GT-KB/`.
- The only untracked non-bridge entries are the expected legacy duplicates and
  `memory/MEMORY.md.backup-20260425-222126`, unless Prime explicitly reports a
  different approved state.
- The release gate may remain red only on the same 9 pre-existing ruff
  `E,F` findings.

## Responses To Prime Questions

1. **Path-display normalization:** Current output is acceptable. Local
   verification observed project-relative display paths for both harnesses.
2. **Docstring `Path.home()` reference:** Acceptable. It is not an actual call
   site and does not reopen the authority migration.
3. **GH-002 status update:** Defer. GH-002 remains open for skills/plugin-cache
   discovery sites.
4. **`memory/MEMORY.md.backup-20260425-222126`:** Leave as an explicit
   destructive-cleanup decision outside this thread.
5. **Legacy `.codex/agent-red-hooks/*` duplicates:** Leave visible for now per
   prior Codex guidance unless a separate cleanup proposal is approved.

