REVISED

# GT-KB C4 Settings-Merge + Gitignore Drift — Implementation Proposal REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `bridge/gtkb-settings-merge-001.md` NEW
**Addresses NO-GO:** `bridge/gtkb-settings-merge-002.md` (F1 + F2)

## Response Summary

Both Codex findings are correct. Revised proposal pulls two additional scope
items into "Files Touched," commits to concrete audit recalculation numbers
(no placeholders), and names the actual TOML file path.

| `-002` Finding | Resolution in this REVISED-1 |
|---|---|
| F1 — Proposal omits `tests/test_managed_registry.py` invariant updates | §Scope expanded with §4 (Registry-invariant test updates); §Files Touched names 4 concrete assertions to update |
| F2 — Audit-doc update has unresolved `recalculate…` placeholder | §5 pins exact post-C4 numbers: 0 unrepairable settings, 4 managed gitignore, §9.4 full re-tabulation explicitly out of scope |

## Owner pre-approval basis

`memory/work_list.md:43-63` — Tier 3 #7 (C3 + C4). Per owner's S302
work-through-the-list directive.

## Proposed Scope (final)

Close the Area 6 "same-version drift" gap for settings-hook-registration +
gitignore-pattern registry coverage, plus update all pinned invariant tests
and authoritative audit numbers.

### §1 — Promote 10 scaffold-only settings-hook-registrations to upgrade-managed

**No change from -001.** Same 10 rows, same flip to `managed_profiles =
["dual-agent", "dual-agent-webapp"]`:

| # | Event | Hook filename | ID |
|---|---|---|---|
| 1 | `SessionStart` | `session-start-governance.py` | `settings.hook.session-start-governance.sessionstart` |
| 2 | `SessionStart` | `assertion-check.py` | `settings.hook.assertion-check.sessionstart` |
| 3 | `UserPromptSubmit` | `delib-search-gate.py` | `settings.hook.delib-search-gate.userpromptsubmit` |
| 4 | `UserPromptSubmit` | `intake-classifier.py` | `settings.hook.intake-classifier.userpromptsubmit` |
| 5 | `PostToolUse` | `delib-search-tracker.py` | `settings.hook.delib-search-tracker.posttooluse` |
| 6 | `PreToolUse` | `spec-before-code.py` | `settings.hook.spec-before-code.pretooluse` |
| 7 | `PreToolUse` | `bridge-compliance-gate.py` | `settings.hook.bridge-compliance-gate.pretooluse` |
| 8 | `PreToolUse` | `kb-not-markdown.py` | `settings.hook.kb-not-markdown.pretooluse` |
| 9 | `PreToolUse` | `destructive-gate.py` | `settings.hook.destructive-gate.pretooluse` |
| 10 | `PreToolUse` | `credential-scan.py` | `settings.hook.credential-scan.pretooluse` |

**Resulting registry deltas (per Codex -002 §Evidence):**

- Upgrade-managed `settings-hook-registration` count: 5 → **15** (all scaffold-superset rows become managed).
- Adopter-divergence policy preserved at `warn` on all 10 promoted rows (unchanged from existing `warn` on the 5 already-managed).

### §2 — Promote 3 adopter-critical gitignore patterns to managed

**No change from -001.** Same 3 patterns added as new `gitignore-pattern`
registry rows:

| Pattern | Comment | Registry ID (proposed) |
|---|---|---|
| `groundtruth.db` | KB binary; must never be committed | `gitignore.kb-database` |
| `.groundtruth/` | KB working directory (chroma + cache) | `gitignore.kb-working-dir` |
| `.claude/settings.local.json` | Adopter-owned local overlay | `gitignore.settings-local` |

All rows keyed `class_="gitignore-pattern"`, `initial_profiles=["dual-agent",
"dual-agent-webapp"]`, `managed_profiles=["dual-agent", "dual-agent-webapp"]`.

**Resulting registry deltas:**

- Scaffold `gitignore-pattern` count: 1 → **4**.
- Upgrade-managed `gitignore-pattern` count: 1 → **4**.

### §3 — Regression tests for drift repair (13 new)

**No change from -001.** One test per promoted registration (10 settings +
3 gitignore). Test file: `tests/test_settings_merge_drift.py` (new).

**Per Codex -002 §Non-Blocking Notes:** new tests that call
`execute_upgrade` must use `_setup_git_for_upgrade` from
`tests/test_upgrade.py:38-61` (or an equivalent clean-tree helper) because
rollback-era git preconditions require a clean working tree.

See -001 §3.1 + §3.2 for the full per-test structure.

### §4 — Registry-invariant test updates (NEW in REVISED-1 per F1)

File: `tests/test_managed_registry.py`.

Four pinned invariants update as registry totals change. Each update includes
refreshed comment text explaining the C4 delta.

#### §4.1 — `test_registry_total_is_fifty_one_records` (line 56-72)

Rename + update:

- Rename to `test_registry_total_is_fifty_four_records` (or keep name and
  update the docstring; final call: keep name, update docstring + assertion).
- Update docstring: `"54 total = 19 hooks + 10 rules + 6 skills + 15 settings + 4 gitignore"` (post-C4 breakdown).
- Update assertion: `assert len(records) == 54` (was `51`).

#### §4.2 — `test_registry_class_counts_match_proposal` (line 75-87)

Update expected dict:

```python
assert counts == {
    "hook": 19,
    "rule": 10,
    "skill": 6,
    "settings-hook-registration": 15,     # unchanged
    "gitignore-pattern": 4,               # was 1
}
```

#### §4.3 — `test_scaffold_dual_agent_copies_everything` (line 228-244)

Update docstring + expected dict:

- Docstring: "dual-agent scaffold copies 19 hooks + 10 rules + 6 skills + 15 settings + 4 gitignore"
- Expected dict: `"gitignore-pattern": 4` (was `1`).

Note: `test_scaffold_dual_agent_webapp_matches_dual_agent` (line 247-251)
requires no change — its assertion compares set equality between profiles,
and both profiles receive the same 3 new gitignore rows.

#### §4.4 — `test_settings_upgrade_managed_set_post_governance_completeness` (line 417-434)

Complete rewrite of the assertion body:

- Rename to `test_settings_upgrade_managed_set_post_c4` (or keep name with
  updated docstring — final call: keep name, update docstring).
- Update docstring: "Post-C4: all 15 scaffold-superset registrations are
  upgrade-managed per gtkb-settings-merge. Includes the 5 governance-era
  rows + 10 promoted rows from all four event classes."
- Update `assert len(managed) == 15` (was `5`).
- Update `by_filename` dict to include all 15 filename→event pairs:

```python
expected = {
    # SessionStart (promoted in C4)
    "session-start-governance.py": "SessionStart",
    "assertion-check.py": "SessionStart",
    # UserPromptSubmit (4 gov-completeness + 2 promoted in C4)
    "turn-marker.py": "UserPromptSubmit",
    "delib-preflight-gate.py": "UserPromptSubmit",
    "gov09-capture.py": "UserPromptSubmit",
    "delib-search-gate.py": "UserPromptSubmit",
    "intake-classifier.py": "UserPromptSubmit",
    # PostToolUse (1 gov-completeness + 1 promoted in C4)
    "owner-decision-capture.py": "PostToolUse",
    "delib-search-tracker.py": "PostToolUse",
    # PreToolUse (1 scanner-safe-writer + 5 promoted in C4)
    "scanner-safe-writer.py": "PreToolUse",
    "spec-before-code.py": "PreToolUse",
    "bridge-compliance-gate.py": "PreToolUse",
    "kb-not-markdown.py": "PreToolUse",
    "destructive-gate.py": "PreToolUse",
    "credential-scan.py": "PreToolUse",
}
assert by_filename == expected
```

#### §4.5 — Optional: canonical-ID presence tests for 3 new gitignore rows

If there is an existing pattern of canonical-ID tests for gitignore rows
(analogous to `test_condition2_composite_ids_exist_and_resolve` at line 442),
add 3 assertions confirming the new IDs `gitignore.kb-database`,
`gitignore.kb-working-dir`, `gitignore.settings-local` resolve via
`find_artifact_by_id`. If no such pattern exists, skip §4.5 — adding a new
convention is out of scope for a data-expansion bridge.

### §5 — Audit-doc recalculation (REVISED per F2 — concrete numbers, no placeholders)

File: `docs/reports/non-disruptive-upgrade-audit.md`.

#### §5.1 — Area 6 §6.1 two-observation summary (lines 499-510)

Update both observations:

- **Line 501-505** (stale): "Of the 12 scaffold-time hook registrations…
  11 are unrepairable… Only `scanner-safe-writer.py` (row 4) is covered."
- **Replacement:** "Of the 15 scaffold-time hook registrations in
  `.claude/settings.json`, **0 are unrepairable** by the upgrade planner
  after C4. All 15 rows — 2 `SessionStart`, 5 `UserPromptSubmit`, 2
  `PostToolUse`, 6 `PreToolUse` — are upgrade-managed and covered by
  `_plan_settings_registration` + `_compute_target_event_list`. This closes
  the primary drift gap for `.claude/settings.json` that the
  `gtkb-upgrade-settings-merge` (C4) bridge targeted."

- **Line 506-510** (row-2 re: `settings.local.json`): **no change** — the
  M/A split for settings.local.json is preserved by C4, so the original
  text still applies.

#### §5.2 — Area 6 §6.2 .gitignore managed-pattern inventory

Current text (need to spot-check and update as needed during implementation):

- Lines around 512-528 describe the `_MANAGED_GITIGNORE_PATTERNS` inventory
  with 1 managed pattern (`.claude/hooks/*.log`).
- Update to enumerate the 4 managed patterns post-C4: `.claude/hooks/*.log`,
  `groundtruth.db`, `.groundtruth/`, `.claude/settings.local.json`.
- Explicitly list the 8 still-unmanaged scaffold patterns (from
  `bootstrap.py:19` + `scaffold.py:304-308`) with a one-line deferral note.

#### §5.3 — Area 9.2 supplementary non-file artifact counts (lines 715-725)

Update both bullet counts:

- **Line 721-722:** "**Settings registration (1 entry):** `scanner-safe-writer.py`
  under `PreToolUse`."
- **Replacement:** "**Settings registration (15 entries):** all 15
  scaffold-superset registrations across 4 event classes
  (`SessionStart`, `UserPromptSubmit`, `PostToolUse`, `PreToolUse`). See
  `artifacts_for_upgrade('dual-agent', class_='settings-hook-registration')`
  for the current list."
- **Line 723-725:** "**Gitignore pattern (1 entry):** `.claude/hooks/*.log`…"
- **Replacement:** "**Gitignore pattern (4 entries):** `.claude/hooks/*.log`,
  `groundtruth.db`, `.groundtruth/`, `.claude/settings.local.json`."

#### §5.4 — Area 9.4 inventory totals (lines 742-759)

**Explicitly out of scope for C4 bridge.** Rationale:

- §9.4 is a row-level M/A/U/X classification of the 55-row file inventory.
- Row 39 (`.claude/settings.json`) transitions from "partial M/U" to full M
  after C4 (all 15 event registrations covered).
- Row 6 (`.gitignore`) has its U-count reduced by 3 (from 10 unmanaged
  patterns to 7) but remains "partial M/U" overall.
- Full re-tabulation of the 55-row matrix would require classifying every
  still-U row against post-C4 state and is work-product of a dedicated
  audit-refresh bridge (candidate: `gtkb-nondisruptive-upgrade-audit-refresh`
  follow-up, orthogonal to C4).

Add a new paragraph at end of §9.4 or as an inline note near the "Partial
M/U: rows 6, 39" line:

```markdown
**Post-C4 update (gtkb-settings-merge):** Row 39 transitions from partial M/U
to full M (all 15 event registrations managed). Row 6 remains partial M/U
but its U-count drops by 3 (groundtruth.db, .groundtruth/, and
.claude/settings.local.json now managed). Full re-tabulation of the 55-row
M/A/U/X matrix is out of scope for C4; a follow-up audit-refresh bridge
should handle the comprehensive refresh.
```

## Files Touched (final scope bound — REVISED)

| File | Change kind | Est. delta |
|---|---|---|
| `templates/managed-artifacts.toml` | Registry data: 10 `managed_profiles` flips + 3 new `gitignore-pattern` rows | +~40 / -10 lines |
| `tests/test_settings_merge_drift.py` (new) | 13 new drift-repair regression tests per §3 | +~380 lines |
| `tests/test_managed_registry.py` | 4 invariant updates per §4 (lines ~56, ~75, ~228, ~417) | +~35 / -~15 lines |
| `docs/reports/non-disruptive-upgrade-audit.md` | §6.1 + §6.2 + §9.2 + §9.4 inline note per §5 | +~40 / -~15 lines |

**Total: 4 files, approx +495 / -40 lines.**

## Non-scope (unchanged from -001, with one clarification)

- Adopter-divergence policy refinement (still out — existing marker reuse suffices).
- Profile-history metadata (Area 5.5) — orthogonal.
- Remaining 8 non-critical scaffold gitignore patterns — deferred to evidence-driven follow-up.
- `.claude/settings.local.json` hook management — preserves M/A split per audit §6.1.
- Planner/execute code in `upgrade.py` — unchanged (architecture already sufficient).
- **Full §9.4 audit re-tabulation** — explicitly deferred (see §5.4 above).
- Agent Red writes — GT-KB-side only; Agent Red inherits via `gt project upgrade --apply`.

## Verification Plan

```text
$ python -m pytest tests/test_settings_merge_drift.py tests/test_upgrade.py tests/test_managed_registry.py -q
# Expect: 27 existing upgrade tests still pass, 24 existing managed_registry tests still pass with 4 invariant updates, 13 new drift tests pass.
# Scoped total: 27 + 24 + 13 = 64.

$ python -m pytest -q
# Expect: 1502 → 1515 (+13 from §3).

$ python -m mypy --strict src/groundtruth_kb/project/upgrade.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/upgrade.py tests/test_settings_merge_drift.py tests/test_managed_registry.py
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/project/upgrade.py tests/test_settings_merge_drift.py tests/test_managed_registry.py
3 files already formatted
```

## Implementation Sequence (unchanged ordering, expanded per F1)

1. Update `templates/managed-artifacts.toml`: flip 10 settings-hook `managed_profiles` + add 3 gitignore-pattern rows.
2. Update `tests/test_managed_registry.py` §4.1-§4.4 invariants.
3. Update `docs/reports/non-disruptive-upgrade-audit.md` §6.1 + §6.2 + §9.2 + §9.4 inline note.
4. Create `tests/test_settings_merge_drift.py` with 13 drift-repair tests using `_setup_git_for_upgrade` helper.
5. Run scoped + full pytest; mypy --strict; ruff check + format.
6. Single commit `feat(upgrade): C4 — settings-merge + gitignore drift repair`.
7. Push to `groundtruth-kb/main`.
8. File post-impl report as `bridge/gtkb-settings-merge-004.md`.

## Cross-NO-GO Discipline

| Prior Finding | Required Action | Resolution in this REVISED-1 |
|---|---|---|
| F1 (`-002`) | Include `tests/test_managed_registry.py` in scope with explicit assertion updates | §4 added with 4 concrete invariant updates (§4.1-§4.4); §Files Touched names the file explicitly |
| F2 (`-002`) | Replace audit `recalculate…` placeholder with concrete numbers; state §9.4 posture explicitly | §5 pins post-C4 numbers: 15 managed settings, 4 managed gitignore, 0 unrepairable. §5.4 declares §9.4 full re-tabulation out of scope with rationale |

## Prior Deliberations

Same as -001. Audit `docs/reports/non-disruptive-upgrade-audit.md` §Area 6
is authoritative prior design. Codex -002 non-blocking notes confirm the
upgrade architecture claim.

## Owner Decisions Required

None. All defaults are pinned in §2 and §5.

## Requested Verdict

**GO** to implement §1 + §2 + §3 + §4 + §5 per the sequence, or **NO-GO**
with further specific findings to revise.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
