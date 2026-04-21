# Post-Implementation Report — GT-KB Artifact Ownership Matrix

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, capped automated spawn via subagent delegation)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Feature branch:** `feature/ownership-matrix`
**Parent GO:** `bridge/gtkb-artifact-ownership-matrix-004.md`
**Approved proposal:** `bridge/gtkb-artifact-ownership-matrix-003.md`
**GT-KB HEAD before:** `e12aab3`
**Agent Red HEAD:** `aa6a5fe5` (unchanged)

## 1. Summary of What Was Built

Sub-bridge delivered: the Artifact Ownership Matrix — a query API over a merged
loader surface that joins the existing managed-artifact registry with a new
sibling ownership map, and a manifest-independent CLI command that produces a
classification report against any tree (including Agent Red, read-only).

Top-level pieces:

1. **Typed ownership metadata on every parsed artifact** — `FileArtifact`,
   `SettingsHookRegistration`, `GitignorePattern`, and the new
   `OwnershipGlobArtifact` each carry an `OwnershipMeta` block. Shared
   `_extract_ownership_block` validator enforces GO Condition C1
   (all-or-none default semantics) and the divergence-policy invariant.
   Satisfies GO Condition C2: resolver consumes typed dataclasses, never
   re-parses TOML.
2. **`OwnershipResolver` query API** at
   `src/groundtruth_kb/project/ownership.py` (446 LOC). Precedence:
   FILE-class exact `target_path` match → `ownership-glob` match
   (priority desc, longest-literal-prefix tiebreak, lexical id) →
   synthetic `adopter-owned + preserve` fallback. `classify_tree` is a
   read-only walker.
3. **Sibling ownership file** at `templates/scaffold-ownership.toml` with
   8 `ownership-glob` rows including the two requirement-file rows
   mandated by GO Condition C3.
4. **All 40 registry rows gained an explicit ownership block** in
   `templates/managed-artifacts.toml` (defaults still apply for rows
   where the block is entirely absent).
5. **`gt project classify-tree --dir <path> --output <report>`** CLI
   subcommand — manifest-independent, read-only, Markdown or JSON output.
6. **`plan_upgrade` consults ownership policy** and filters out
   `preserve` / `transient` / `adopter-opt-in` rows. Zero behavioral
   change for all 40 current-HEAD rows (all use `overwrite` or
   `structured-merge`).
7. **Agent Red classification report** committed at
   `docs/reports/agent-red-classification.md` (7,355 paths, 3
   owner-decision-pending rows — `groundtruth.db`,
   `requirements-local.txt`, `requirements-test.txt`).

## 2. Commits on Feature Branch

```
bfedd40 feat(ownership): Artifact Ownership Matrix (ownership-glob + resolver + classify-tree)
```

Single commit (verification-clean intermediate states were not independently
committable without synthetic test skips; all work is additive with no
regressions). `git log --oneline main..feature/ownership-matrix`:

```
bfedd40 feat(ownership): Artifact Ownership Matrix (ownership-glob + resolver + classify-tree)
```

## 3. Test Results

### New test modules (§3 of proposal + GO C1/C3 additions)

| Module | Tests | Result |
|---|---|---|
| `tests/test_ownership_loader_agreement.py` | 15 | 15 PASS |
| `tests/test_ownership_resolver.py` | 17 | 17 PASS |
| `tests/test_scaffold_consumes_resolver.py` | 4 | 4 PASS |
| `tests/test_upgrade_dispatches_by_policy.py` | 6 | 6 PASS |
| `tests/test_doctor_unchanged_without_classify_flag.py` | 1 | 1 PASS |
| `tests/test_classify_tree_cli.py` | 6 | 6 PASS |
| `tests/test_classify_tree_read_only.py` | 2 | 2 PASS |
| **Total (new)** | **51** | **51 PASS** |

### Full GT-KB test suite

- Pre-bridge (on `main` @ `e12aab3`): **1249 tests passing.**
- Post-bridge (on `feature/ownership-matrix`): **1300 tests passing.**
- Delta: **+51 tests**. Zero regressions, zero skips, zero xfails.

### Key test behaviors covered

- C1 `test_legacy_row_with_no_ownership_keys_receives_class_default` and
  `test_partial_ownership_row_with_overwrite_but_missing_divergence_raises`.
- C2 every resolver call traces back through dataclass `ownership`
  attribute, never re-reads TOML.
- C3 `test_classify_tree_flags_requirements_files_as_owner_decision_pending`
  verifies `requirements-local.txt` and `requirements-test.txt` both
  appear with `YES` marker.

## 4. Command Evidence

### 4.1 Full `pytest` summary (final run)

```
$ python -m pytest -q
(1249 existing + 51 new = 1300 tests)
................................................................. ... [100%]
============================== warnings summary ===============================
...
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1300 passed, 1 warning in 277.15s (0:04:37)
```

### 4.2 `mypy --strict src/groundtruth_kb/`

```
$ python -m mypy --strict src/groundtruth_kb/
Success: no issues found in 41 source files
```

### 4.3 `ruff check` + `ruff format --check`

```
$ python -m ruff check src/groundtruth_kb/ tests/
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/ tests/
113 files already formatted
```

### 4.4 `git log --oneline main..feature/ownership-matrix`

```
$ git log --oneline main..feature/ownership-matrix
bfedd40 feat(ownership): Artifact Ownership Matrix (ownership-glob + resolver + classify-tree)
```

### 4.5 Agent Red zero-write proof

Captured before and after running `gt project classify-tree --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement" --output docs/reports/agent-red-classification.md` from the GT-KB root.

**Before (89 lines):**

```
 M AgentRed-Technical-Evaluation-Report.docx
 M bridge/INDEX.md
 M groundtruth.db
 M independent-progress-assessments/bridge-automation/repair-permanent-bridge-automation.ps1
 M requirements-local.txt
 M requirements-test.txt
 M widget/package-lock.json
 M widget/package.json
?? .githooks/
?? archive/
?? bridge/agent-red-cto-cleanup-010.md
...
(89 lines total)
```

**After (89 lines):**

```
(identical byte-for-byte to "before")
```

Diff output:

```
$ diff /tmp/agent_red_before_report.txt /tmp/agent_red_after_report.txt
IDENTICAL
```

### 4.6 `gt project doctor --dir <agent-red>` still fails on manifest

```
$ python -m groundtruth_kb project doctor --dir "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"
  GroundTruth Project Doctor — Profile: local-only
  ==================================================

    [OK]  Python 3.14.0
    [OK]  Git 2.51.2.
  [WARN]  ruff not found. Install: pip install ruff
    [OK]  GitHub CLI 2.83.2
  [FAIL]  groundtruth.toml not found — run `gt project init` first
    [OK]  Schema OK (22 tables)
    [OK]  6 hook(s) present
    [OK]  6 rule(s) present

  Overall: [FAIL] FAIL

  Required tools missing:
    - groundtruth.toml: groundtruth.toml not found — run `gt project init` first

EXIT=1
```

Doctor behavior is unchanged. No weakening of existing readiness gates.

### 4.7 Helper regression proof (`artifacts_for_scaffold` id-set delta)

Captured before/after feature branch across all 3 profiles:

```
$ python -c "from groundtruth_kb.project.managed_registry import artifacts_for_scaffold, ..." > helpers.txt  # pre-change
$ ... feature branch merge ...
$ python -c "..." > helpers_after.txt
$ diff helpers.txt helpers_after.txt
HELPERS IDENTICAL
```

- `scaffold local-only`: 15 ids (unchanged)
- `scaffold dual-agent`: 40 ids (unchanged)
- `scaffold dual-agent-webapp`: 40 ids (unchanged)
- `upgrade local-only`: 3 ids (unchanged)
- `upgrade dual-agent`: 29 ids (unchanged)
- `upgrade dual-agent-webapp`: 29 ids (unchanged)
- `doctor local-only`: 3 ids (unchanged)
- `doctor dual-agent`: 6 ids (unchanged)
- `doctor dual-agent-webapp`: 6 ids (unchanged)

## 5. Satisfaction of GO Conditions

### C1 — All-or-none default ownership semantics

**Implementation evidence:**
- `_extract_ownership_block` at `src/groundtruth_kb/project/managed_registry.py:307-365`
  checks `_OWNERSHIP_BLOCK_KEYS & record.keys()`. If empty → apply class default
  from `_CLASS_OWNERSHIP_DEFAULTS`. Else → every key validated.
- `_CLASS_OWNERSHIP_DEFAULTS` at `src/groundtruth_kb/project/managed_registry.py:112-118`:
  file-classes get `gt-kb-managed + overwrite + warn`, settings-hook-registration
  and gitignore-pattern get `gt-kb-managed + structured-merge + warn`.

**Test evidence:**
- `test_legacy_row_with_no_ownership_keys_receives_class_default`
  (`tests/test_ownership_loader_agreement.py:135-152`) asserts a legacy row
  with zero ownership keys receives the class default triple.
- `test_partial_ownership_row_with_overwrite_but_missing_divergence_raises`
  (`tests/test_ownership_loader_agreement.py:155-175`) asserts a row with
  `upgrade_policy="overwrite"` but no `adopter_divergence_policy` raises
  `InvalidArtifactRecord`.

### C2 — Typed loader output carries ownership metadata

**Implementation evidence:**
- `FileArtifact.ownership`, `SettingsHookRegistration.ownership`,
  `GitignorePattern.ownership`, `OwnershipGlobArtifact.ownership` fields at
  `src/groundtruth_kb/project/managed_registry.py:149/164/178/198`.
- `_extract_ownership_block` is the single validator, called from
  `_build_file_artifact`, `_build_settings_registration`,
  `_build_gitignore_pattern`, and `_build_ownership_glob`
  (`managed_registry.py:420/451/482/507`).
- `OwnershipResolver.__init__` at `ownership.py:132-148` calls
  `_load_all_artifacts()` and reads `artifact.ownership` via
  `_to_ownership_record`; `ownership.py` does not import `tomllib`.

**Test evidence:**
- `test_resolver_sees_every_loader_record` asserts resolver's
  `all_records()` is 1:1 with the loader's output.
- `test_resolver_classify_path_matches_registry_target_path` enumerates
  all 40 FILE-class registry rows and verifies resolver reaches them by
  their loader-derived `target_path`.

### C3 — Deterministic owner-decision-pending rows for requirements files

**Implementation evidence:**
- `templates/scaffold-ownership.toml` rows `adopter-requirements-local-txt`
  and `adopter-requirements-test-txt` (both `legacy-exception + preserve`
  with `priority = 100`).
- Owner-decision-pending heuristic at `ownership.py:230`:
  `owner_decision_pending=(record.ownership == "legacy-exception")`.
  Documented in the module docstring at `ownership.py:15-19`.

**Test evidence:**
- `test_classify_tree_flags_requirements_files_as_owner_decision_pending`
  asserts both requirement-file rows appear with `YES` marker.
- The generated `docs/reports/agent-red-classification.md` shows all 3
  owner-decision-pending rows: `groundtruth.db`, `requirements-local.txt`,
  `requirements-test.txt`.

## 6. Generated Classification Report Stats

Report path: `docs/reports/agent-red-classification.md`

- **Total paths classified:** 7,355
- **Ownership distribution:**
  - adopter-owned: 6,492
  - shared-structured: 851
  - gt-kb-managed: 9
  - legacy-exception: 3
- **Owner-decision-pending rows: 3**
  - `groundtruth.db` — `legacy-exception / preserve / —` — "Fresh scaffold gitignores; Agent Red tracks. Owner decision pending on product default (S296-S299 context)."
  - `requirements-local.txt` — `legacy-exception / preserve / —` — "GT-KB pip dependency pin location. Owner decision pending on adoption cadence (stale v0.2.1 pin as of 2026-04-17)."
  - `requirements-test.txt` — `legacy-exception / preserve / —` — "GT-KB pip test dependency pin location. Owner decision pending on adoption cadence (stale v0.2.1 pin as of 2026-04-17)."

Report header block conforms to §4 of the proposal:

```
# Agent Red Classification Report

- Generated: 2026-04-18T00:01:35+00:00
- GT-KB version: 0.6.0
- GT-KB HEAD: e12aab3
- Target tree: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
- Target HEAD: aa6a5fe5
- Total paths classified: 7355
- Owner-decision-pending rows: 3
```

Table columns match §4 contract: `path | ownership | upgrade_policy |
divergence_policy | notes | owner_decision_pending`. Ordering is by
ownership-enum index then alphabetical by path; divergence policy renders as
`—` when `None`.

## 7. Implementation Notes & Scope Deltas

- **Ignore globs tuned for Agent Red tree size.** Initial run produced
  178,209 rows (mostly `widget/node_modules/`, `.codex_pydeps/`,
  `.hypothesis/`). Default ignore set expanded to cover nested
  `**/node_modules/**`, `**/.codex_pydeps/**`, `**/.hypothesis/**`, and
  common build/cache dirs. Result: 7,355 rows — small enough to commit
  but still comprehensive.
- **`_load_all_artifacts()` now returns 48 records** (40 registry + 8
  ownership-glob). Three pre-existing tests in
  `tests/test_managed_registry.py` were updated to call a new
  `_registry_records()` helper that filters out ownership-glob rows —
  test scope was always registry-only.
- **Glob matcher rewritten** mid-implementation when an initial fnmatch-based
  implementation failed to match `bridge/**/*.md` against `bridge/foo.md`.
  New implementation in `ownership.py:_glob_to_regex` handles `/**/`,
  `prefix/**`, `**/suffix`, and `**` as a whole-pattern segment, with
  correct POSIX globstar semantics. Compiled regex is cached per-glob.
- **CHANGELOG entry added under `[Unreleased]`** per proposal §5. 0.6.0
  was already released before this sub-bridge; the next patch release
  will roll up this Unreleased section.
- **Scaffold path unchanged.** `artifacts_for_scaffold` filters out
  `ownership-glob` by class at the helper level — `scaffold.py` received
  zero changes. Verified by id-set diff pre/post across all 3 profiles.

## 8. Links to New/Modified Files (from GT-KB root)

New files:
- `src/groundtruth_kb/project/ownership.py`
- `templates/scaffold-ownership.toml`
- `tests/test_ownership_loader_agreement.py`
- `tests/test_ownership_resolver.py`
- `tests/test_scaffold_consumes_resolver.py`
- `tests/test_upgrade_dispatches_by_policy.py`
- `tests/test_doctor_unchanged_without_classify_flag.py`
- `tests/test_classify_tree_cli.py`
- `tests/test_classify_tree_read_only.py`
- `docs/reports/agent-red-classification.md`

Modified files:
- `src/groundtruth_kb/project/managed_registry.py` (new class, dataclass
  fields, validators, sibling-file loader, helper filtering)
- `src/groundtruth_kb/project/__init__.py` (new exports)
- `src/groundtruth_kb/project/upgrade.py` (ownership policy filter)
- `src/groundtruth_kb/cli.py` (new `classify-tree` subcommand)
- `templates/managed-artifacts.toml` (explicit ownership blocks on all 40 rows)
- `tests/test_managed_registry.py` (registry-scope filter helper)
- `CHANGELOG.md` (Unreleased entry)

## 9. Next Step

Codex VERIFIED review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
