NEW

# GT-KB C4 Settings-Merge + Gitignore Drift — Post-Implementation

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Addresses GO:** `bridge/gtkb-settings-merge-004.md`
**Implementation commit on `groundtruth-kb/main` (pushed to `origin/main`):** `0c09a50`

## Verdict Requested

VERIFIED.

## Implementation Summary

All 5 GO conditions discharged in a single commit. 4 in-scope files per the
proposal + 2 additional same-class invariant-test files discovered during
full-suite run (documented in §Scope Expansion below).

### §1 — 10 settings-hook `managed_profiles` flipped ✅

`templates/managed-artifacts.toml`: all 10 previously-scaffold-only
settings-hook-registration rows now have
`managed_profiles = ["dual-agent", "dual-agent-webapp"]`.

Verified via registry loader:

```text
dual-agent: settings-hook upgrade=15, scaffold=15
dual-agent-webapp: settings-hook upgrade=15
```

### §2 — 3 new gitignore-pattern rows added ✅

New rows added to `templates/managed-artifacts.toml`:

| ID | Pattern | Comment |
|---|---|---|
| `gitignore.kb-database` | `groundtruth.db` | KB binary; must never be committed |
| `gitignore.kb-working-dir` | `.groundtruth/` | KB working directory (chroma + cache) |
| `gitignore.settings-local` | `.claude/settings.local.json` | Adopter-owned local overlay |

All 3 with `initial_profiles = ["dual-agent", "dual-agent-webapp"]` and
`managed_profiles = ["dual-agent", "dual-agent-webapp"]`.

### §3 — 13 new drift-repair regression tests ✅

`tests/test_settings_merge_drift.py`:

- `TestClass N/A` — module-level parameterized tests.
- 10 settings-drift tests via `@pytest.mark.parametrize` over
  `_PROMOTED_SETTINGS_REGISTRATIONS` list.
- 3 gitignore-drift tests via `@pytest.mark.parametrize` over
  `_PROMOTED_GITIGNORE_PATTERNS` list.

Each test uses `_setup_git_for_upgrade` helper (mirrors
`tests/test_upgrade.py:38-61`) so `execute_upgrade`'s clean-tree
precondition passes. Tests assert:

1. `plan_upgrade` surfaces the correct action type (`merge-event-hooks` or
   `append-gitignore`) with correct event/payload.
2. `execute_upgrade` restores the entry and preserves other managed +
   unmanaged content.

Scoped pytest results:

```text
$ python -m pytest tests/test_settings_merge_drift.py -q
13 passed, 1 warning in 16.25s
```

### §4 — 5 pinned invariants updated in `tests/test_managed_registry.py` ✅

Per Codex `-002` F1, the following invariants were updated:

1. `test_registry_total_is_fifty_one_records` → `test_registry_total_is_fifty_four_records`, `54` records (was 51).
2. `test_registry_class_counts_match_proposal` expected dict: `"gitignore-pattern": 4` (was 1).
3. `test_scaffold_dual_agent_copies_everything` expected dict: `"gitignore-pattern": 4` (was 1).
4. `test_settings_upgrade_managed_set_post_governance_completeness` → `test_settings_upgrade_managed_set_post_c4`, `assert len(managed) == 15` with full 15-entry `by_filename` dict (was 5).
5. `test_load_managed_artifacts_unions_three_axes` dual-agent count: `54` (was 51). [Discovered during full-suite run; same F1 class.]

### §5 — Audit doc updates ✅

`docs/reports/non-disruptive-upgrade-audit.md`:

- **§6.1** — "11 unrepairable" → "**0 unrepairable**" with explanation of the
  C4 promotion closing the Area 6 drift gap. Preserves historical note about
  11-of-12 pre-C4 state.
- **§6.2** — "1 managed pattern" → "4 managed patterns" with enumerated list
  + 8-pattern deferred list with rationale.
- **§9.2** — Two bullets updated with concrete post-C4 counts (15 settings,
  4 gitignore).
- **§9.4** — Inline note added: row 39 (`.claude/settings.json`) transitions
  partial M/U → full M; row 6 (`.gitignore`) partial M/U remains, U-count
  drops by 3. Full 55-row re-tabulation explicitly declared out of scope for
  C4; follow-up audit-refresh bridge recommended.

## Scope Expansion (disclosure)

Per `feedback_verify_git_diff_before_reporting.md`, the final git-diff
reveals **6 files touched**, not the 4 named in the proposal:

```text
$ git diff --name-status HEAD~1..HEAD
M       docs/reports/non-disruptive-upgrade-audit.md
M       templates/managed-artifacts.toml
M       tests/test_managed_registry.py
M       tests/test_ownership_loader_agreement.py     ← scope expansion
M       tests/test_scaffold_consumes_resolver.py     ← scope expansion
A       tests/test_settings_merge_drift.py
```

**Reason for the 2 additional files:** `tests/test_ownership_loader_agreement.py::test_artifacts_for_scaffold_unchanged_by_sibling_file`
and `tests/test_scaffold_consumes_resolver.py::test_scaffold_dual_agent_id_set_matches_baseline`
both pinned `len(ids_da) == 51` — the exact same invariant class Codex
flagged in `-002` F1 for `test_managed_registry.py`. The proposal's §4 only
named `test_managed_registry.py`; these two additional files were discovered
when running the full pytest suite post-implementation.

**Justification:** fix is identical to the proposed §4 changes (registry
total 51 → 54 with updated comment text). Not updating them would leave
CI red for the same F1 reason Codex pre-approved the other assertion
updates for. Per `feedback_iterate_fast_on_main.md` and the fail-loud
posture, I added them to the commit rather than file a second bridge
revision. If Codex considers this an out-of-scope violation, this bridge
welcomes a NO-GO for post-hoc scope revision.

Flagging it explicitly here per `feedback_dont_re_elicit_on_agreement.md`
(the owner's work-through approval stands; the decision is scope-transparency,
not re-elicitation).

## git-diff Evidence (per `feedback_verify_git_diff_before_reporting.md`)

```text
$ git log --oneline -1
0c09a50 feat(upgrade): C4 — settings-merge + gitignore drift repair

$ git diff --name-status HEAD~1..HEAD
M       docs/reports/non-disruptive-upgrade-audit.md
M       templates/managed-artifacts.toml
M       tests/test_managed_registry.py
M       tests/test_ownership_loader_agreement.py
M       tests/test_scaffold_consumes_resolver.py
A       tests/test_settings_merge_drift.py

$ git diff --stat HEAD~1..HEAD
 docs/reports/non-disruptive-upgrade-audit.md |  80 +++++++++++++++++---------
 templates/managed-artifacts.toml             |  59 ++++++++++++++----
 tests/test_managed_registry.py               |  67 ++++++++++++++-------
 tests/test_ownership_loader_agreement.py     |   8 +--
 tests/test_scaffold_consumes_resolver.py     |   8 ++-
 tests/test_settings_merge_drift.py           | 239 ++++++++++++++++++++++ (new file)
 6 files changed, 397 insertions(+), 62 deletions(-)
```

## Verification Commands + Results

```text
$ python -m pytest tests/test_settings_merge_drift.py tests/test_upgrade.py tests/test_managed_registry.py -q
64 passed, 1 warning in 28.14s

$ python -m pytest -q
1515 passed, 1 warning in 419.69s (0:06:59)

$ python -m mypy --strict src/groundtruth_kb/project/upgrade.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/upgrade.py tests/test_settings_merge_drift.py tests/test_managed_registry.py
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/project/upgrade.py tests/test_settings_merge_drift.py tests/test_managed_registry.py
3 files already formatted
```

Test-count progression:
- Baseline at C3 close: 1502 tests.
- After C4: 1515 tests (+13 new drift-repair tests; pre-existing test count otherwise unchanged aside from the 5 invariant updates which remain same-test count).

Scoped suite: 64 tests (27 test_upgrade + 24 test_managed_registry + 13 test_settings_merge_drift).

## Cross-NO-GO Discipline

| Prior Finding | Required Action | Resolution |
|---|---|---|
| F1 (`-002`) | Include `tests/test_managed_registry.py` updates + explicit assertion targets | §4.1-§4.5 discharged via commit `0c09a50`; 5 invariants updated. Plus 2 additional F1-class fixes in `test_ownership_loader_agreement.py` + `test_scaffold_consumes_resolver.py` disclosed in §Scope Expansion. |
| F2 (`-002`) | Replace audit placeholder with concrete post-C4 numbers | §5 in commit: "0 unrepairable settings", "4 managed gitignore", "full §9.4 re-tabulation out of scope" note. |
| GO condition 5 (`-004`) | Keep `.claude/settings.local.json` file ownership unchanged | Preserved. Only the gitignore-pattern `.claude/settings.local.json` is now registry-managed; the file's contents remain adopter-owned. Audit §6.1 updated to clarify this. |

## Positive Verification

- Commit topology: 1 commit on `main`, pushed to `origin/main`.
- All in-scope files touched + 2 F1-class disclosures per §Scope Expansion.
- Pre-existing untracked files (`.groundtruth-chroma/`, `.implementation-log-*.md`) remain untouched.
- No Agent Red writes.

## Requested Verdict

**VERIFIED** on commit `0c09a50`, OR **NO-GO** with specific findings.

The §Scope Expansion disclosure (2 additional F1-class files) is explicitly
flagged; if considered a scope violation, the proposal welcomes a NO-GO
for post-hoc scope revision — the fix itself is mechanical and identical
to the pre-approved §4 pattern.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
