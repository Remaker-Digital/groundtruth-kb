NEW

# Harness-State Authority Migration — `session_self_initialization.py` to In-Root Paths

**Status:** NEW (P1; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Closes:**
- F5 deferral from [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) (5 deferred role/preference files in working tree)
- Row-17 GENERATOR-HARDENING-002 NO-GO at [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) (Type F harness-home parameterization)

---

## Prior Deliberations

- [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) (VERIFIED) — names this thread; closes the working-tree triage that left these files deferred.
- [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) §3.2 — pre-specified migration scope and authority map.
- [bridge/s317-working-tree-triage-004.md](bridge/s317-working-tree-triage-004.md) F5 P1 — original NO-GO finding identifying `session_self_initialization.py:HARNESS_ROLE_RECORDS` etc. as `Path.home()`-resolved.
- [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) NO-GO — required GT-KB runtime defaults under `E:\GT-KB`, not `Path.home()`, and Agent Red active harness config under `E:\GT-KB\applications\Agent_Red`. This proposal satisfies both.
- [bridge/application-isolation-contract-008.md](bridge/application-isolation-contract-008.md) (VERIFIED) — Bucket A registers `harness-state` under `applications/Agent_Red/`. This migration places authority files there.
- [memory/feedback/feedback_no_hardcoded_paths.md](memory/feedback/feedback_no_hardcoded_paths.md) — relative/discovered paths preferred; PROJECT_ROOT-relative resolution is the chosen pattern.

---

## §0. Scope

Migrate the 5 authority constants in `scripts/session_self_initialization.py` from `Path.home() / .{codex,claude}/agent-red-hooks/` to `applications/Agent_Red/harness-state/{codex,claude}/`. Mirror the pattern already established in [scripts/workstream_focus.py:23-64](scripts/workstream_focus.py) (committed in S317 Commit 2 `786685d4`).

After migration, track the 3 in-root authoritative files that S317 deferred. Close GH-002 by removing the last `Path.home()` use for authority paths. Update `.claude/rules/operating-role.md` and `AGENTS.md` text to reflect canonical authority locations.

**In scope:**
1. `scripts/session_self_initialization.py` constants (5 sites: lines 94, 107, 108, 111, 112)
2. `scripts/session_self_initialization.py` `_user_startup_preferences_path` resolution (line 230-232)
3. `tests/scripts/test_session_self_initialization.py` test fixture path naming (clarity improvement; tests already pass via monkeypatch)
4. `.claude/rules/operating-role.md` lines 24-25 stale local-default text
5. `AGENTS.md` lines 44-45 stale local-default text
6. Track 3 deferred files: `applications/Agent_Red/harness-state/{claude,codex}/operating-role.md` + `applications/Agent_Red/harness-state/codex/session-startup-preferences.json`

**Out of scope:**
- `Path.home()` discovery sites at lines 1037-1038 (skills) and 1059 (plugin cache). These scan user-installed dev-environment tools; legitimate `Path.home()` use (per `feedback_no_hardcoded_paths.md` triage category: development environment discovery, not project authority).
- Deletion of legacy duplicate files at `.codex/agent-red-hooks/operating-role.md` (319 B) and `.codex/agent-red-hooks/session-startup-preferences.json` (46 B). Per `feedback_explicit_destructive_action_authorization.md`, deletion needs separate enumerated proposal. They remain untracked harmless artifacts; flag as legacy via comment in registry or a follow-up cleanup bridge.
- Phantom-INDEX VERIFIED refs (separate thread).
- Ruff cleanup (separate thread).
- KB mutations, deployment, feature work.

---

## §1. Current state evidence

### §1.1 `session_self_initialization.py` authority sites (5)

```python
# Line 94 — startup preferences default
DEFAULT_USER_STARTUP_PREFERENCES_PATH = Path.home() / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"

# Lines 106-109 — operating-role records
HARNESS_ROLE_RECORDS = {
    "codex": Path.home() / ".codex" / "agent-red-hooks" / "operating-role.md",
    "claude": Path.home() / ".claude" / "agent-red-hooks" / "operating-role.md",
}

# Lines 110-113 — lifecycle guards
HARNESS_LIFECYCLE_GUARDS = {
    "codex": Path.home() / ".codex" / "agent-red-hooks" / "session-lifecycle-guard.json",
    "claude": Path.home() / ".claude" / "agent-red-hooks" / "session-lifecycle-guard.json",
}
```

### §1.2 Migration target (already established by `workstream_focus.py`:23-64)

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_RED_HARNESS_STATE_ROOT = PROJECT_ROOT / "applications" / "Agent_Red" / "harness-state"

DEFAULT_USER_STARTUP_PREFERENCES_PATH = (
    AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"
)
HARNESS_ROLE_RECORDS = {
    "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "operating-role.md",
    "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "operating-role.md",
}
HARNESS_LIFECYCLE_GUARDS = {
    "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-lifecycle-guard.json",
    "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "session-lifecycle-guard.json",
}
```

### §1.3 Files physically present at migration target (verified by `ls -la` during S317 -005 §1.4-bis)

| File | Bytes | Will be tracked? |
|---|---|---|
| `applications/Agent_Red/harness-state/claude/operating-role.md` | 2602 | YES (post-migration) |
| `applications/Agent_Red/harness-state/codex/operating-role.md` | 319 | YES (post-migration) |
| `applications/Agent_Red/harness-state/codex/session-startup-preferences.json` | 46 | YES (post-migration) |
| `applications/Agent_Red/harness-state/claude/session-lifecycle-guard.json` | 515 | NO — gitignored per S317 Commit 0 (mutable runtime state) |
| `applications/Agent_Red/harness-state/codex/session-lifecycle-guard.json` | 379 | NO — gitignored per S317 Commit 0 |

The 3 to-be-tracked files exist and are byte-identical (or richer, in claude/operating-role.md case) to the legacy locations. No data migration is needed at runtime — just the code change to point at the new location.

### §1.4 Stale documentation references

| File | Line | Current text | Issue |
|---|---|---|---|
| [.claude/rules/operating-role.md](.claude/rules/operating-role.md) | 24-25 | `~/.codex/agent-red-hooks/operating-role.md` and `~/.claude/agent-red-hooks/operating-role.md` | Stale; pre-S315 home-dir paths |
| [AGENTS.md](AGENTS.md) | 44-45 | `E:\GT-KB\.codex\agent-red-hooks\operating-role.md` and `E:\GT-KB\.claude\agent-red-hooks\operating-role.md` | Wrong canonical location; root-level `.codex/agent-red-hooks/` instead of application-level `applications/Agent_Red/harness-state/codex/` |

Both are updated by this migration to reflect the canonical app-level locations.

---

## §2. Implementation plan

### §2.1 `scripts/session_self_initialization.py` edits

Apply 4 edits:

1. **Add `AGENT_RED_HARNESS_STATE_ROOT` constant** after `PROJECT_ROOT` definition (~line 88-89):
   ```python
   AGENT_RED_HARNESS_STATE_ROOT = PROJECT_ROOT / "applications" / "Agent_Red" / "harness-state"
   ```

2. **Replace `DEFAULT_USER_STARTUP_PREFERENCES_PATH`** at line 94:
   ```python
   DEFAULT_USER_STARTUP_PREFERENCES_PATH = (
       AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"
   )
   ```

3. **Replace `HARNESS_ROLE_RECORDS`** at lines 106-109:
   ```python
   HARNESS_ROLE_RECORDS = {
       "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "operating-role.md",
       "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "operating-role.md",
   }
   ```

4. **Replace `HARNESS_LIFECYCLE_GUARDS`** at lines 110-113:
   ```python
   HARNESS_LIFECYCLE_GUARDS = {
       "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-lifecycle-guard.json",
       "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "session-lifecycle-guard.json",
   }
   ```

The downstream consumers (`_user_startup_preferences_path`, `_normalize_harness_name`, `operating_role_path`, etc.) all read these constants and need no changes — they continue working with the new resolution.

### §2.2 Documentation edits

5. **`.claude/rules/operating-role.md` lines 24-25:** Replace the stale home-dir local-default text with:
   ```
   - Codex: `applications/Agent_Red/harness-state/codex/operating-role.md`
   - Claude Code: `applications/Agent_Red/harness-state/claude/operating-role.md`
   ```
   (Project-root-relative paths; matches the `applications/Agent_Red/` Bucket A placement under the application-isolation contract.)

6. **`AGENTS.md` lines 44-45:** Replace the wrong root-level canonical text with:
   ```
   - Codex: `applications/Agent_Red/harness-state/codex/operating-role.md`
   - Claude Code: `applications/Agent_Red/harness-state/claude/operating-role.md`
   ```

### §2.3 Test edits (clarity improvements; not correctness changes)

7. **`tests/scripts/test_session_self_initialization.py:222`** — change tmp directory naming from `tmp_path / ".codex" / "agent-red-hooks"` to `tmp_path / "applications" / "Agent_Red" / "harness-state" / "codex"`. The test already monkeypatches `module.HARNESS_ROLE_RECORDS["codex"]`, so this is a clarity-only update. Existing test logic continues working.

   (Optional. Test passes either way. Recommend including for documentation value.)

### §2.4 Track previously-deferred files

8. After §2.1 lands, the 3 files at the migration target are now resolved-by-code. Stage and commit:
   - `applications/Agent_Red/harness-state/claude/operating-role.md`
   - `applications/Agent_Red/harness-state/codex/operating-role.md`
   - `applications/Agent_Red/harness-state/codex/session-startup-preferences.json`

   The 2 lifecycle-guard JSONs at the migration target remain gitignored per S317 Commit 0 — that decision is unchanged.

### §2.5 Commit plan (3 scoped commits)

| # | Subject | Scope |
|---|---|---|
| 1 | `scripts: Migrate session_self_initialization.py harness-state authority to in-root paths` | Single-file edit to `scripts/session_self_initialization.py` (4 sites) |
| 2 | `harness-state: Track in-root role records and Codex preferences (closes S317 F5 deferral)` | 3 files: 2 operating-role.md + 1 session-startup-preferences.json |
| 3 | `docs: Update operating-role.md + AGENTS.md to reflect canonical authority paths` | 2 files: `.claude/rules/operating-role.md` + `AGENTS.md` |

Optional 4th commit if §2.3 test edits are accepted: `tests: Rename harness-state test fixture paths for post-migration clarity` (1 file).

---

## §3. Verification

### §3.1 Mandatory: fresh startup payload reports in-root role-mapping source (per Codex F5)

Run `python scripts/session_self_initialization.py --project-root E:\GT-KB --json` and confirm output contains:
- `role_mapping_source` with a path resolving under `applications/Agent_Red/harness-state/` (not `C:\Users\micha\.codex\agent-red-hooks\`)

### §3.2 Mandatory: no `Path.home()` references for the 5 authority constants

```
grep -n "Path.home" scripts/session_self_initialization.py
```

Post-migration expected: only 3 hits remain (lines 1037, 1038, 1059 — skills/plugin cache discovery, explicitly out of scope per §0).

### §3.3 Test contract (addressing Codex GH-002 -004 NO-GO requirements)

The Codex GH-002 NO-GO at `-004` flagged 3 test-quality concerns. This migration's test contract:

1. **`Path.home()` monkey-patch raises during `--harness-config-root` runs:** Existing tests at `test_session_self_initialization.py:220-228` use the safer pattern of monkeypatching the **constants**, which makes any `Path.home()` use detectable via assertion that the constant value is the patched tmp path. Adding a new test that explicitly sets `Path.home` to raise during a startup run, then verifying no exception, would be a stronger contract — proposed as Commit 1 addition.

2. **Replace fixed-line source-grep with semantic check:** Add a regression test:
   ```python
   def test_session_self_initialization_no_path_home_for_authority_constants():
       """Verify session_self_initialization.py defines authority constants via
       AGENT_RED_HARNESS_STATE_ROOT, not Path.home()."""
       from scripts import session_self_initialization as m
       project_root = Path(__file__).resolve().parents[2]
       expected_root = project_root / "applications" / "Agent_Red" / "harness-state"
       for harness_name in ("codex", "claude"):
           assert m.HARNESS_ROLE_RECORDS[harness_name].is_relative_to(expected_root)
           assert m.HARNESS_LIFECYCLE_GUARDS[harness_name].is_relative_to(expected_root)
       assert m.DEFAULT_USER_STARTUP_PREFERENCES_PATH.is_relative_to(expected_root)
   ```

3. **Positive proof asserts sentinel role-record path/content:** The above test's `is_relative_to(expected_root)` assertion satisfies this — it verifies the actual resolved path, not just the absence of `Path.home()`.

### §3.4 Release-candidate gate

```
python scripts/release_candidate_gate.py --skip-frontend
```

Expected: pass (the 9 pre-existing ruff errors from S317 close-out remain in untouched files; this migration introduces no new lint surface).

If the new test added in §3.3 fails on the current code, the test was correctly designed and the migration is incomplete.

### §3.5 Per-commit guardrails

All 5 quality guardrails (test-deletion-guard, assertion-ratchet, architectural-guards, credential-scan, TSX-commit-gate) PASS on each commit.

---

## §4. Risk analysis

| Risk | Severity | Mitigation |
|---|---|---|
| Breaking tests by replacing constant values | LOW (P3) | Existing tests monkeypatch the constants; substitution semantics preserved. New regression test added per §3.3 closes the source-grep gap. |
| `_user_startup_preferences_path()` env override breaks | LOW (P3) | The function (line 230-232) reads `GTKB_STARTUP_PREFERENCES_PATH` env var first; `DEFAULT_USER_STARTUP_PREFERENCES_PATH` is the fallback. Env-override behavior unchanged. |
| Hooks fail at session start because authority files aren't yet at migration target | NONE | The 3 files already exist at `applications/Agent_Red/harness-state/...` (verified S317 -005 §1.4-bis live filesystem). The migration just changes where the code reads from. |
| Codex harness uses different role record after migration | LOW (P3) | The new file `applications/Agent_Red/harness-state/codex/operating-role.md` (319 B) is byte-identical to the home-dir copy. Codex sessions continue resolving to the same `active_role: loyal-opposition` value. |
| Claude harness role record content differs between in-root and home-dir | LOW (P2) | The in-root `applications/Agent_Red/harness-state/claude/operating-role.md` (2602 B) is RICHER than the home-dir one (likely 319 B). After migration, Claude reads the richer record. This is the intended state — the in-root version was designed for application-isolation. Verify via S316 sub-slice 1 history. |
| Lifecycle guards remain gitignored — what about their content? | NONE | `.gitignore` pattern only affects tracking, not file presence. Hooks continue reading/writing the local lifecycle guard files; they just don't get committed. Same as `memory/pending-owner-decisions.md` pattern. |
| AGENTS.md / operating-role.md edits create cross-reference inconsistency | LOW (P3) | This migration touches the only two stale references discovered via grep. Other rule files (acting-prime-builder.md, prime-builder-role.md, loyal-opposition.md) reference these files by their own paths, not by the home-dir path. |
| Codex requires additional verification beyond §3.1 | MEDIUM (P2) | Pre-empted via §3.3 regression test + explicit §3.1 startup-payload check. If Codex requests more, REVISED-1 follows. |

---

## §5. Codex review questions

1. **§2.3 test fixture rename (Optional commit 4):** Include the test path-naming clarity update in this thread, or defer? Recommendation: include — small, same-thread context, prevents the cognitive friction from accumulating.

2. **§2.5 commit ordering:** Is the order Commit 1 (code) → Commit 2 (track files) → Commit 3 (docs) correct, or should it be reordered? Specifically: should the 3 files be tracked BEFORE the code change so that even if Commit 1's tests fail mid-CI, the files are durable? Recommendation: keep proposed order. Codex GO `-006` for S317 honored a similar ordering (gitignore first, then content); reverse order risks committing files that the code won't read until Commit 1 lands.

3. **§3.3 test addition vs existing tests:** Adding a new regression test extends test surface. Codex GH-002 `-004` requested it. Acceptable, or should the migration prefer modifying the existing `test_harness_local_role_record_overrides_repo_default_for_startup` test instead? Recommendation: ADD a new test for the source-grep replacement; existing test is unrelated (tests behavior, not constant resolution).

4. **Legacy duplicates at `.codex/agent-red-hooks/`:** After this migration, `.codex/agent-red-hooks/operating-role.md` (319 B) and `.codex/agent-red-hooks/session-startup-preferences.json` (46 B) become unused legacy files. Disposition options:
   - (a) Leave as untracked, flag follow-up cleanup bridge (proposed)
   - (b) Add to `.gitignore` to hide them
   - (c) Delete in a separate destructive-action proposal
   
   Recommendation: (a) — keep visible signal that legacy state exists; cleanup is its own discrete decision per `feedback_explicit_destructive_action_authorization.md`.

5. **§1.4 `AGENTS.md` text disposition:** The current AGENTS.md text at lines 44-45 (committed in S317 Commit 1 `66dcb196`) was an intermediate migration state — it pointed at root-level `.codex/agent-red-hooks/` rather than app-level `applications/Agent_Red/harness-state/codex/`. Updating it now is a correction. Should this migration also retroactively explain the discrepancy in the commit message? Recommendation: yes — commit message body notes "S317 Commit 1 had intermediate target; this commit completes the migration to canonical app-level location."

---

## §6. Owner directive compliance

- **Project root boundary:** ✓ migration moves authority IN-ROOT (from `Path.home()` to `applications/Agent_Red/harness-state/`).
- **Application isolation contract:** ✓ honors Bucket A `harness-state` placement.
- **Explicit destructive action authorization:** ✓ no deletions; legacy duplicates remain untracked per §4 risk mitigation.
- **Bridge protocol:** ✓ this NEW proposal awaits GO before any file edit.
- **No deferrals (per `feedback_no_deferrals_ever.md`):** ✓ closes 2 deferrals (F5 + GH-002 NO-GO at -008); legacy duplicate cleanup is dependency-ordered (needs explicit destructive-action proposal first).
- **`feedback_no_hardcoded_paths.md`:** ✓ uses PROJECT_ROOT-relative resolution, not absolute `E:\GT-KB\` literals.
- **`feedback_verify_source_before_parallel_proposals.md`:** ✓ verified `workstream_focus.py:23-64` migration pattern as the reference; verified live filesystem state for 3 to-be-tracked files; verified test fixture patterns.

---

## §7. Expected post-implementation report contents

- Per-commit `git show --stat` for 3-4 commits.
- Final `git log --oneline` showing the 3-4 new commits atop `531151ad`.
- Final `git status --short` showing only `memory/MEMORY.md.backup-20260425-222126` and the legacy `.codex/agent-red-hooks/operating-role.md` + `.codex/agent-red-hooks/session-startup-preferences.json` (per §4 risk mitigation option (a)).
- §3.1 startup-payload verification output proving in-root `role_mapping_source`.
- §3.2 `grep -n "Path.home" scripts/session_self_initialization.py` output (3 hits remaining for skills/plugin sites).
- §3.3 new regression test result (PASS).
- §3.4 release-candidate gate result (expected: same 9 pre-existing ruff errors; no new failures).
- Confirmation that GH-002 thread row-17 status moves to "ready for VERIFIED via this migration" or owner-decision on whether to formally close GH-002 with a cross-reference.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
