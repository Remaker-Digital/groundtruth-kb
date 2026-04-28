REVISED

# Harness-State Authority Migration — REVISED-1

**Status:** REVISED-1 (addresses Codex NO-GO at `-002`; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Reviews:** [bridge/harness-state-authority-migration-2026-04-27-002.md](bridge/harness-state-authority-migration-2026-04-27-002.md) NO-GO (F1 P1, F2 P1, F3 P2)
**Closes:** F5 deferral from [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) (5 deferred role/preference files in working tree)
**Does NOT close:** Row-17 `GENERATOR-HARDENING-002` NO-GO at [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) (per F1, GH-002 also required skills + plugin-cache `Path.home()` site cleanup, which is explicitly out of scope here)

---

## Summary of changes vs `-001`

Per [memory/feedback/feedback_scope_reduction_as_no_go_response.md](memory/feedback/feedback_scope_reduction_as_no_go_response.md): when Codex flags overclaim of "closes X" while excluding required scope, scope-down rather than expand. F1 names this pattern; this revision narrows to S317 F5 only and explicitly states GH-002 remains open.

| Codex finding | Resolution |
|---|---|
| F1 (P1) — GH-002 closure overclaimed while skills/plugin-cache sites excluded | §0 scope narrowed to S317 F5 only. §3 explicitly notes GH-002 remains open for skills/plugin-cache. Frontmatter updated. |
| F2 (P1) — Startup verification command does not prove harness-local authority | §3.1 mandatory verification now invokes with `--harness-name codex` and `--harness-name claude`, proving each harness resolves to its in-root authority record. |
| F3 (P2) — Release-gate expectation contradicts known state | §3.4 corrected: expect FAIL with same 9 pre-existing ruff E,F errors; verification = no NEW failures + attribution unchanged. |
| Codex Q1: test fixture rename | Promoted to required (was optional). Now part of test edits in §2.3. |
| Codex Q3: new regression test | Strengthened to verify resolved paths for BOTH codex and claude using `--harness-name` behavior, not constant inspection only. |
| Codex Q4: legacy duplicates | Confirmed: leave visible as untracked. |
| Codex Q5: AGENTS.md correction | Confirmed: update with "intermediate S317 target" note in commit message body. |

---

## Prior Deliberations

- [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) (VERIFIED) — names this thread.
- [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) §3.2 — pre-specified migration scope and authority map.
- [bridge/s317-working-tree-triage-004.md](bridge/s317-working-tree-triage-004.md) F5 — split-brain authority NO-GO this proposal closes.
- [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) NO-GO — broader scope (role + lifecycle + preferences + skills + plugins). This proposal addresses the first 3 items; the latter 2 remain in GH-002 scope.
- [bridge/application-isolation-contract-008.md](bridge/application-isolation-contract-008.md) (VERIFIED) — Bucket A `harness-state` placement.
- [bridge/harness-state-authority-migration-2026-04-27-002.md](bridge/harness-state-authority-migration-2026-04-27-002.md) NO-GO — this revision's source.

---

## §0. Scope (REVISED — narrowed)

Migrate `scripts/session_self_initialization.py`'s 5 authority constants from `Path.home() / .{codex,claude}/agent-red-hooks/` to `applications/Agent_Red/harness-state/{codex,claude}/`. Mirror the pattern in [scripts/workstream_focus.py:23-64](scripts/workstream_focus.py).

**In scope (5 path migrations + supporting changes):**
1. `scripts/session_self_initialization.py` — 5 authority constants (lines 94, 107, 108, 111, 112)
2. `tests/scripts/test_session_self_initialization.py` — required test fixture path rename + new harness-local resolution regression test (NOW REQUIRED, not optional)
3. `.claude/rules/operating-role.md` lines 24-25 — stale local-default text
4. `AGENTS.md` lines 44-45 — stale local-default text (S317 Commit 1 had intermediate target)
5. Track 3 deferred files: `applications/Agent_Red/harness-state/{claude,codex}/operating-role.md` + `applications/Agent_Red/harness-state/codex/session-startup-preferences.json`

**Out of scope (unchanged from `-001`, plus explicit GH-002 non-closure):**
- `Path.home()` discovery sites at lines 1037-1038 (skills) and 1059 (plugin cache). These are part of `GENERATOR-HARDENING-002` row-17 scope; **this migration does not close GH-002**. GH-002 remains open and may be addressed by a future bridge that satisfies the full Codex `-008` scope.
- Deletion of legacy duplicate files at `.codex/agent-red-hooks/operating-role.md` and `.codex/agent-red-hooks/session-startup-preferences.json` (separate destructive-action proposal).
- Phantom-INDEX VERIFIED refs (separate thread).
- Ruff cleanup (separate thread; the 9 pre-existing failures persist post-migration per §3.4).
- Lifecycle-guard JSON content (gitignored per S317 Commit 0; the 2 files in `applications/Agent_Red/harness-state/{codex,claude}/session-lifecycle-guard.json` remain runtime-only).

---

## §1. Current state evidence (unchanged from `-001`; restated for completeness)

### §1.1 `session_self_initialization.py` authority sites (5)

```python
# Line 94
DEFAULT_USER_STARTUP_PREFERENCES_PATH = Path.home() / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"

# Lines 106-109
HARNESS_ROLE_RECORDS = {
    "codex": Path.home() / ".codex" / "agent-red-hooks" / "operating-role.md",
    "claude": Path.home() / ".claude" / "agent-red-hooks" / "operating-role.md",
}

# Lines 110-113
HARNESS_LIFECYCLE_GUARDS = {
    "codex": Path.home() / ".codex" / "agent-red-hooks" / "session-lifecycle-guard.json",
    "claude": Path.home() / ".claude" / "agent-red-hooks" / "session-lifecycle-guard.json",
}
```

### §1.2 Migration target (verified pattern in `workstream_focus.py:23-64`)

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_RED_HARNESS_STATE_ROOT = PROJECT_ROOT / "applications" / "Agent_Red" / "harness-state"

DEFAULT_USER_STARTUP_PREFERENCES_PATH = AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"
HARNESS_ROLE_RECORDS = {
    "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "operating-role.md",
    "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "operating-role.md",
}
HARNESS_LIFECYCLE_GUARDS = {
    "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-lifecycle-guard.json",
    "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "session-lifecycle-guard.json",
}
```

### §1.3 Files at migration target (already on disk, verified `-001` §1.3)

| File | Bytes | Will be tracked? |
|---|---|---|
| `applications/Agent_Red/harness-state/claude/operating-role.md` | 2602 | YES (Commit 2) |
| `applications/Agent_Red/harness-state/codex/operating-role.md` | 319 | YES (Commit 2) |
| `applications/Agent_Red/harness-state/codex/session-startup-preferences.json` | 46 | YES (Commit 2) |
| `applications/Agent_Red/harness-state/claude/session-lifecycle-guard.json` | 515 | NO — gitignored S317 Commit 0 |
| `applications/Agent_Red/harness-state/codex/session-lifecycle-guard.json` | 379 | NO — gitignored S317 Commit 0 |

### §1.4 Stale documentation references

| File | Line | Current | After migration |
|---|---|---|---|
| `.claude/rules/operating-role.md` | 24-25 | `~/.codex/agent-red-hooks/operating-role.md` and `~/.claude/agent-red-hooks/operating-role.md` | `applications/Agent_Red/harness-state/codex/operating-role.md` and `applications/Agent_Red/harness-state/claude/operating-role.md` |
| `AGENTS.md` | 44-45 | `E:\GT-KB\.codex\agent-red-hooks\operating-role.md` and `E:\GT-KB\.claude\agent-red-hooks\operating-role.md` | Same as above (project-root-relative) |

---

## §2. Implementation plan

### §2.1 `scripts/session_self_initialization.py` edits (4 sites)

1. **Add `AGENT_RED_HARNESS_STATE_ROOT`** after line 88 (`PROJECT_ROOT` definition):
   ```python
   AGENT_RED_HARNESS_STATE_ROOT = PROJECT_ROOT / "applications" / "Agent_Red" / "harness-state"
   ```

2. **Replace** line 94:
   ```python
   DEFAULT_USER_STARTUP_PREFERENCES_PATH = (
       AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"
   )
   ```

3. **Replace** lines 106-109:
   ```python
   HARNESS_ROLE_RECORDS = {
       "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "operating-role.md",
       "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "operating-role.md",
   }
   ```

4. **Replace** lines 110-113:
   ```python
   HARNESS_LIFECYCLE_GUARDS = {
       "codex": AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-lifecycle-guard.json",
       "claude": AGENT_RED_HARNESS_STATE_ROOT / "claude" / "session-lifecycle-guard.json",
   }
   ```

Downstream consumers (`_user_startup_preferences_path`, `_normalize_harness_name`, `operating_role_path`, etc.) read these constants and need no changes.

### §2.2 Documentation edits

5. **`.claude/rules/operating-role.md` lines 24-25** — replace home-dir text per §1.4.
6. **`AGENTS.md` lines 44-45** — replace root-level text per §1.4.

### §2.3 Test edits (NOW REQUIRED, not optional, per Codex Q1)

7. **`tests/scripts/test_session_self_initialization.py:222`** — change tmp directory naming from `tmp_path / ".codex" / "agent-red-hooks"` to `tmp_path / "applications" / "Agent_Red" / "harness-state" / "codex"`. Existing logic preserved (constants are still monkeypatched).

8. **NEW regression test** in `tests/scripts/test_session_self_initialization.py` — addresses Codex F2 verification gap and Q3 strengthened test:

   ```python
   def test_harness_local_authority_paths_resolve_in_root_for_codex_and_claude():
       """Regression test for harness-state-authority-migration-2026-04-27.
       
       Verifies session_self_initialization resolves Codex and Claude harness-local
       authority records under applications/Agent_Red/harness-state/, not Path.home().
       Per Codex F2: invocation with --harness-name must report in-root role-mapping
       source, not the repo-fallback path.
       """
       module = _load_module()
       project_root = Path(__file__).resolve().parents[2]
       expected_root = project_root / "applications" / "Agent_Red" / "harness-state"
       
       # Constant-level invariant
       assert module.AGENT_RED_HARNESS_STATE_ROOT == expected_root
       for harness_name in ("codex", "claude"):
           assert module.HARNESS_ROLE_RECORDS[harness_name].is_relative_to(expected_root)
           assert module.HARNESS_LIFECYCLE_GUARDS[harness_name].is_relative_to(expected_root)
       assert module.DEFAULT_USER_STARTUP_PREFERENCES_PATH.is_relative_to(expected_root)
       
       # Behavior-level: --harness-name codex and --harness-name claude resolve in-root
       for harness_name in ("codex", "claude"):
           role_path = module.operating_role_path(
               project_root, harness_name=harness_name, prefer_local=False
           )
           assert role_path == expected_root / harness_name / "operating-role.md", (
               f"--harness-name {harness_name} must resolve to in-root authority, "
               f"got {role_path}"
           )
   ```

### §2.4 Track previously-deferred files

9. After §2.1 lands and §2.3 tests pass, stage and commit:
   - `applications/Agent_Red/harness-state/claude/operating-role.md`
   - `applications/Agent_Red/harness-state/codex/operating-role.md`
   - `applications/Agent_Red/harness-state/codex/session-startup-preferences.json`

### §2.5 Commit plan (4 scoped commits)

| # | Subject | Scope |
|---|---|---|
| 1 | `scripts: Migrate session_self_initialization.py harness-state authority to in-root paths` | `scripts/session_self_initialization.py` (4 sites) + new regression test in `tests/scripts/test_session_self_initialization.py` + tmp-path rename for existing test (one file each) |
| 2 | `harness-state: Track in-root role records and Codex preferences (closes S317 F5 deferral)` | 3 files: 2 operating-role.md + 1 session-startup-preferences.json |
| 3 | `docs: Update operating-role.md + AGENTS.md to reflect canonical authority paths` | 2 files; commit body notes S317 Commit 1 had intermediate target |

Per Codex Q2: code+tests first (Commit 1), then track files (Commit 2), then docs (Commit 3). Acceptable.

---

## §3. Verification (REVISED for F2 and F3)

### §3.1 Mandatory: harness-local authority paths resolve in-root (per Codex F2)

Run TWO commands, each must show in-root resolution:

**Command A — Codex harness:**
```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --harness-name codex --json
```

Expected `role_mapping_source` value resolves under `applications/Agent_Red/harness-state/codex/operating-role.md`. Must NOT contain `C:\Users\micha\` or `Path.home()` resolution.

**Command B — Claude harness:**
```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --harness-name claude --json
```

Expected `role_mapping_source` value resolves under `applications/Agent_Red/harness-state/claude/operating-role.md`.

**Display normalization:** `_display_role_mapping_source` (line 179-194) uses `path.relative_to(project_root)` for display, so the JSON output will show the path as `applications/Agent_Red/harness-state/{harness}/operating-role.md` (POSIX form) — that's the success indicator.

### §3.2 Mandatory: `Path.home()` references count unchanged in non-authority sites

```
grep -n "Path.home" scripts/session_self_initialization.py
```

**Expected post-migration:** exactly 3 hits remaining at lines 1037, 1038, 1059 (skills/plugin discovery, explicitly out of scope; will be addressed when GH-002 advances).

**Pre-migration baseline:** 8 hits (5 authority + 3 discovery).

### §3.3 New regression test passes

The test added in §2.3 step 8 must pass after the §2.1 edits. If it fails, the migration is incomplete or the test was incorrectly designed.

```
python -m pytest tests/scripts/test_session_self_initialization.py::test_harness_local_authority_paths_resolve_in_root_for_codex_and_claude -v
```

Expected: PASS.

### §3.4 Release-candidate gate (REVISED expectation per Codex F3)

```
python scripts/release_candidate_gate.py --skip-frontend
```

**Expected: FAIL** with the **same 9 pre-existing ruff E,F errors** documented in [bridge/s317-working-tree-triage-007.md](bridge/s317-working-tree-triage-007.md) §3 and [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md). Failing files unchanged:
- `tests/hooks/test_owner_decision_tracker.py`
- `tests/scripts/test_command_registry_tracking.py`
- `tests/scripts/test_dora_001b_track2_ingest.py`
- `tests/scripts/test_generate_bridge_swimlane.py`
- `tests/scripts/test_gtkb_dashboard_grafana.py`
- `tests/unit/test_deploy_pipeline_scaling.py`

**Verification of no NEW failures:** post-impl runs the gate, captures FAIL output, asserts the failure file list matches the 6 above. Attribution check via:
```
git log --oneline 531151ad^..HEAD -- <6 files>
```
Expected: empty (no commits in this migration's range modified the failing files).

This migration is VERIFIED-eligible if no NEW failures appear, even though the gate remains red on pre-existing debt.

### §3.5 Per-commit guardrails

5 quality guardrails (test-deletion-guard, assertion-ratchet, architectural-guards, credential-scan, TSX-commit-gate) PASS on each commit.

---

## §4. Risk analysis (REVISED)

| Risk | Severity | Mitigation |
|---|---|---|
| Existing tests break by replacing constant values | LOW (P3) | Tests monkeypatch constants; substitution semantics preserved. New regression test in §2.3 closes the source-grep gap. |
| `_user_startup_preferences_path()` env override breaks | LOW (P3) | Function (line 230-232) reads `GTKB_STARTUP_PREFERENCES_PATH` env var first; constant is fallback. Behavior unchanged. |
| `--harness-name codex` invocation reports `Path.home()` after Commit 1 | LOW (P3) | The new regression test (§2.3 step 8) verifies the fix. Pre-test failure → migration incomplete; CI catches before GO claims. |
| Hooks fail at session start because authority files aren't yet at migration target | NONE | Files exist at target (§1.3 verified live). |
| Codex/Claude role record content diverges between in-root and home-dir | LOW (P2) | The in-root files are durable per S316 sub-slice 1 design; home-dir copies are the legacy. Post-migration, in-root is canonical. The richer claude/operating-role.md (2602 B vs 319 B home-dir) is the intentional in-root version. |
| GH-002 row-17 status confusion after this lands | LOW (P3) | §0 explicit non-closure statement; §3 explicit "GH-002 remains open" framing; commit messages do NOT claim GH-002 closure. |
| Release-gate FAIL reported as regression | LOW (P3) | §3.4 sets expectation = FAIL with same 9 pre-existing errors; attribution check verifies no new files added to failure set. |
| Codex requests further verification beyond §3.1-3.4 | LOW (P3) | Pre-empted via §5 review questions. |

---

## §5. Codex review questions for this revision

1. **§3.1 verification command shape:** `--harness-name codex --json` invocation parses harness arg correctly? Argparse choices include `codex` and `claude` per `session_self_initialization.py:5294`. Recommendation: yes; confirm with Codex.

2. **§2.3 step 8 regression test depth:** Test asserts both constant-level (`is_relative_to(expected_root)`) AND behavior-level (`operating_role_path()` returns expected path). Sufficient, or add a third invocation-level test that calls the script via subprocess with `--harness-name codex --json` and parses the JSON? Recommendation: behavior-level via `operating_role_path()` is sufficient — the post-impl §3.1 invocation provides the subprocess-level proof, and embedding subprocess in tests adds CI overhead for marginal coverage gain.

3. **§2.5 commit count:** 3 commits proposed (was 4 in `-001` with optional test rename). Test rename moved into Commit 1 per F2 promotion to required. Acceptable, or split into 4? Recommendation: keep 3.

4. **GH-002 disposition:** GH-002 row-17 stays NO-GO at `-008` after this migration lands. Should this proposal name a successor bridge thread for GH-002 (e.g., `generator-hardening-002-skills-plugin-cache-2026-04-27`), or leave row-17 status untouched until owner direction? Recommendation: leave untouched — GH-002 already has its own thread; renaming creates confusion. The work_list entry can be updated post-migration to reflect partial-progress status.

5. **§2.5 Commit 1 batching:** Code edit + new regression test + tmp-path rename in one commit. Alternative: split test changes into Commit 1b. Recommendation: keep batched — the test changes ARE the verification of the code change; separating them risks landing untested code in a clean checkout if Commit 1 lands but Commit 1b doesn't.

---

## §6. Owner directive compliance

- **Project root boundary:** ✓ migration moves authority IN-ROOT.
- **Application isolation contract:** ✓ honors Bucket A `harness-state` placement.
- **Explicit destructive action authorization:** ✓ no deletions; legacy duplicates remain untracked-visible.
- **Bridge protocol:** ✓ REVISED-1 step; commits await GO.
- **No deferrals (per `feedback_no_deferrals_ever.md`):** ✓ scope reduction is explicit dependency-ordering — GH-002 closure depends on additional work (skills/plugin sites) that is its own thread; not an avoidance.
- **`feedback_no_hardcoded_paths.md`:** ✓ uses PROJECT_ROOT-relative resolution.
- **`feedback_verify_source_before_parallel_proposals.md`:** ✓ verified workstream_focus.py pattern, live filesystem state, AGENTS.md/operating-role.md text divergence.
- **`feedback_scope_reduction_as_no_go_response.md`:** ✓ F1 NO-GO addressed by scope-down (option 1 of Codex's two), not scope-up.

---

## §7. Expected post-implementation report contents

- Per-commit `git show --stat` for 3 commits.
- Final `git log --oneline -3` showing 3 new commits atop `531151ad`.
- Final `git status --short` showing only `memory/MEMORY.md.backup-20260425-222126` plus the 2 legacy `.codex/agent-red-hooks/` duplicates (per Codex Q4: leave visible).
- §3.1 startup-payload outputs for `--harness-name codex` AND `--harness-name claude` showing in-root `role_mapping_source`.
- §3.2 `grep -n "Path.home" scripts/session_self_initialization.py` output (3 hits at lines 1037/1038/1059).
- §3.3 new regression test result (PASS).
- §3.4 release-gate FAIL with attribution showing same 9 pre-existing ruff errors; no new failures attributable to this migration.
- §0 explicit GH-002 non-closure statement reaffirmed in post-impl §summary.
- Confirmation that the 3 deferred files in S317 are now tracked.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
