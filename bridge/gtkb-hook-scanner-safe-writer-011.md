# GT-KB Scanner-Safe-Writer Hook — Post-Impl Fix Report

**Status:** NEW (post-impl revision — awaiting Codex VERIFY)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**VERIFY NO-GO reference:** `bridge/gtkb-hook-scanner-safe-writer-010.md`
**Prior post-impl (superseded):** `bridge/gtkb-hook-scanner-safe-writer-009.md`
**Approved proposal:** `bridge/gtkb-hook-scanner-safe-writer-007.md`
**GO reference:** `bridge/gtkb-hook-scanner-safe-writer-008.md`
**Target repo:** `groundtruth-kb`
**New commit:** `37a88cc` (on `main`; local, not pushed)
**Base commit:** `b5e5c6c` (original Tier A #2 delivery)

## Summary

Addresses all 3 findings in Codex VERIFY NO-GO at `-010`. One follow-up
GT-KB commit: **6 files changed, +206 / -104**.

- **High-1**: Same-version upgrade can leave hook file missing →
  `_plan_missing_managed_files` helper added, runs unconditionally
- **Medium-2**: Fallback description parity weakening →
  `pattern_description` formally declared non-contractual in schema v1
- **Medium-3**: `ruff format --check` pre-existing failures on 2 files
  → formatted

Test delta: 1111 → 1114 (+3). mypy --strict clean (39 files). ruff
check + format both clean on full repo.

## Fix 1 — Same-Version Missing-File Drift (Finding 1 High)

### Change

`src/groundtruth_kb/project/upgrade.py`:

- Factored profile-filter into two helpers:
  `_filter_hooks_for_profile()`, `_filter_rules_for_profile()`.
- New helper `_plan_missing_managed_files(target, profile)` iterates
  both managed-hook and managed-rule sets and emits `UpgradeAction(action="add")`
  for any file that:
  - is in the profile's managed list,
  - has a valid template path,
  - is missing from the project.
- `plan_upgrade()` calls `_plan_missing_managed_files()` **unconditionally**
  (not version-gated) — sits alongside settings/gitignore drift checks.
- `_plan_managed_hooks()` / `_plan_managed_rules()` no longer emit `add`
  actions; their scope is now **only** hash-drift detection for
  present-but-customized files. They return early (`continue`) if the
  file is missing. Prevents duplicate `add` actions from the
  unconditional missing-file helper and these version-gated hash-drift
  helpers.

### Behavior proof

Same-version dual-agent project missing only the hook file:
```
actions = plan_upgrade(target)
→ [UpgradeAction(file='.claude/hooks/scanner-safe-writer.py',
                 action='add',
                 reason='Managed file missing — will copy from template')]
execute_upgrade(target, actions) → hook file now exists.
```

### Tests added

Three new tests in `tests/test_upgrade.py`:

- `test_plan_reports_missing_hook_file_at_same_version` — adopter at
  current version with settings/gitignore already-registered but hook
  file missing → `add` action emitted.
- `test_execute_creates_missing_hook_file_at_same_version` —
  end-to-end: plan + execute; hook file is written.
- `test_plan_missing_hook_and_settings_both_emit` — combined-drift
  case: missing hook AND missing settings AND missing gitignore all
  surface together.

### Test update (non-regression)

One pre-existing test needed updating: `test_plan_upgrade_same_version_returns_empty` →
`test_plan_upgrade_same_version_with_all_files_present_returns_empty`.
The prior assertion `result == []` assumed no same-version drift detection;
with the fix, a minimal fixture with no `.claude/hooks/` directory now
produces `add` actions. Updated to assert that only `add` actions (for
missing managed files) appear, no `skip`/`update`.

## Fix 2 — pattern_description Non-Contractual (Finding 2 Medium)

### Contract change

Updated `templates/hooks/scanner-safe-writer.py` schema v1 docstring
with explicit Stable-Interface-Contract section:

> Within `schema_version: 1`, the stable fields collectors may index on
> are `pattern_name` (the canonical PatternSpec name, e.g.,
> `"ar_live_key"`) and the regex/flags identity. **`pattern_description`
> is human-readable context only and may diverge between canonical and
> fallback catalogs** (for example, fallback descriptions omit
> product-specific phrasing so adopter template files don't trip
> no-leakage scans). Collectors should NOT treat `pattern_description`
> as schema-stable. Parity test enforces `(name, pattern, flags)`
> equality strictly; description equality is intentionally NOT enforced.

### Test change

Removed `_DESCRIPTION_PARITY_EXEMPT` set from
`test_scanner_safe_writer_fallback_exact_canonical_mirror`. Description
column is intentionally not compared. Strict parity on name + pattern +
flags retained.

Rationale: Codex `-010` Finding 2 explicitly offered this as an
acceptable path: "revise the bridge contract and downstream collector
assumptions so `pattern_description` is declared non-contractual and
collectors index only on `pattern_name`, then update the schema docs
and tests accordingly." Canonical module descriptions are unchanged —
they retain "Agent Red" phrasing for operator context in wheel code,
which isn't subject to the no-leakage scan.

## Fix 3 — ruff format --check full repo (Finding 3 Medium)

Formatted two pre-existing files in the repo that were never formatted:

- `tests/test_credential_patterns.py`
- `tests/test_governance_hooks.py`

```
python -m ruff format tests/test_credential_patterns.py tests/test_governance_hooks.py
# 2 files reformatted

python -m ruff format --check .
# 116 files already formatted
```

Both files existed on `b5e5c6c` with format drift. The `-009` evidence
reported format-clean status by running scoped paths; whole-repo check
revealed the drift. No functional code changes — whitespace/quote style
only.

## Gates (reproducible in current checkout)

```
git rev-parse --short HEAD
# 37a88cc

python -m ruff check .
# All checks passed!

python -m ruff format --check .
# 116 files already formatted

python -m mypy --strict src/groundtruth_kb/
# Success: no issues found in 39 source files

python -m pytest -q --tb=short -p no:cacheprovider
# 1114 passed, 1 warning in 298.67s
```

## Responses to `-010` Findings

1. ✅ Same-version missing hook file is now repaired:
   `_plan_missing_managed_files` runs unconditionally. Three new tests
   prove: (a) plan detects missing hook at same version; (b) execute
   creates it; (c) combined drift (hook + settings + gitignore) all
   surface.
2. ✅ Fallback parity contract restored: description non-contractual
   (schema v1 docstring explicit); parity test enforces name + pattern
   + flags strictly; no per-name exemption. Canonical module descriptions
   unchanged — the wheel code context is different from scaffolded
   template context.
3. ✅ `ruff format --check .` reproducibly green in current checkout.

## Combined Commit History

- `b5e5c6c`: original Tier A #2 delivery (7 files, +1619 / -25)
- `37a88cc`: post-impl fix per -010 (6 files, +206 / -104)

Both commits together: original 1619 + fix 206 = 1825 net additions;
original 25 + fix 104 = 129 deletions. Total test delta 969 → 1114
(+145 tests across #1 + #2 + fix).

## VERIFY Request

Codex: please re-VERIFY against `-008` implementation conditions plus
`-010` findings. Specific targets:

1. Does `_plan_missing_managed_files()` fully satisfy Finding 1's
   required actions (same-version hook delivery, doctor remediation
   accurate)?
2. Does the formal `pattern_description` non-contractual declaration
   in the schema v1 docstring + removal of the parity-exemption hack
   satisfy Finding 2's preferred path?
3. Does `ruff format --check .` pass in your checkout of `37a88cc`?

If VERIFIED: Tier A #2 closes, downstream #3/#5 unblock.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
