# GT-KB Managed Artifact Registry (Tier 1 / C1)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (Tier 1 kickoff per prioritization plan VERIFIED at `post-phase-a-prioritization-006`)
**Target repo:** `groundtruth-kb` main (current HEAD `33f1c5a`)
**Authority:** Plan-of-record `post-phase-a-prioritization-003` Tier 1 C1 (VERIFIED)
**Investigation source:** `docs/reports/non-disruptive-upgrade-audit.md` §"Managed-Artifact Registry Strategy" (lines 764-907), recommending Option B (single declarative registry).

## Purpose

Introduce a single declarative registry that names every scaffold-
created managed artifact, its class, profile applicability,
template source, and target path. Consumed by `scaffold.py`,
`upgrade.py`, and `doctor.py` so that all three modules read from
one authority instead of parallel lists drifting out of lockstep.

Closes the live defect **Gap 2.8** identified in the investigation:
three rule templates (`bridge-essential.md`,
`deliberation-protocol.md`, `file-bridge-protocol.md`) are copied
by `scaffold.py:273-274` but absent from `_MANAGED_RULES` at
`upgrade.py:45-51`. The doctor requires them
(`doctor.py:483-486`), so an adopter who deletes one gets a
failing doctor check with no `gt project upgrade --apply`
remediation path.

Additionally consolidates five parallel manifests that already
exist and drift separately:

- `_MANAGED_HOOKS` (upgrade.py:36)
- `_MANAGED_RULES` (upgrade.py:45)
- `_MANAGED_SKILLS` (upgrade.py:56)
- `_MANAGED_SKILLS_INITIAL` (scaffold.py:28) — already in
  "lockstep" with `_MANAGED_SKILLS` via prose convention but
  machine-checked lockstep is missing
- `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` (upgrade.py:68)

## Prior Deliberations

- `post-phase-a-prioritization-006` (VERIFIED — plan authorizes
  C1 as Tier 1)
- `gtkb-non-disruptive-upgrade-investigation-006` (VERIFIED —
  investigation recommending Option B single registry)
- `gtkb-skill-decision-capture-010` Condition 5 (Codex previously
  warned about split-manifest drift for future skills)
- All Phase A Tier A VERIFIEDs (each added a managed-artifact
  class; the registry generalizes the pattern)

## Scope

### In scope

1. **Registry file format.** Single declarative file at
   `templates/managed-artifacts.toml`. TOML chosen because:
   - Human-readable
   - Stdlib `tomllib` parses it (no new runtime dependency)
   - Tracked in git (observable in PRs, reviewable in commits)
   - Reads identically in scaffold/upgrade/doctor

   Schema (exact):

   ```toml
   [[artifact]]
   id = "hook.scanner-safe-writer"
   class = "hook"
   template_path = "templates/hooks/scanner-safe-writer.py"
   target_path  = ".claude/hooks/scanner-safe-writer.py"
   profiles = ["dual-agent", "dual-agent-webapp"]
   managed = true       # hash-drift + missing-file repair
   initial = true       # copied at scaffold time
   settings_pretooluse_hook = true   # also register in settings.json PreToolUse

   [[artifact]]
   id = "rule.bridge-essential"
   class = "rule"
   template_path = "templates/rules/bridge-essential.md"
   target_path  = ".claude/rules/bridge-essential.md"
   profiles = ["dual-agent", "dual-agent-webapp"]
   managed = true
   initial = true
   ```

   Class discriminator enumerations: `hook`, `rule`, `skill`,
   `settings-hook-registration`, `gitignore-pattern`. Extensible by
   adding new classes to the parser.

2. **Migration of existing lists.** Populate the registry from:
   - `_MANAGED_HOOKS` (7 entries)
   - `_MANAGED_RULES` (5 entries — PLUS the 3 previously-missed
     rules that closed Gap 2.8)
   - `_MANAGED_SKILLS` (6 entries from Phase A Tier A)
   - `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` (1 entry:
     `scanner-safe-writer.py`)
   - `_MANAGED_GITIGNORE_PATTERNS` (1 entry: `.claude/hooks/*.log`)
   - `_MANAGED_SKILLS_INITIAL` (6 entries — for the "initial"
     lockstep)

   Result: single source of truth. The five parallel Python lists
   are **deleted**. Gap 2.8 closes because the 3 missing rule
   entries are present in the registry.

3. **Loader** in `src/groundtruth_kb/project/managed_registry.py`
   (new): `load_managed_artifacts(profile: str) -> list[ManagedArtifact]`.
   Reads the TOML from `get_templates_dir() / "managed-artifacts.toml"`.
   Filters by profile. Returns a list of typed records.

4. **Consumer refactors** (minimal, targeted):
   - `scaffold.py`: `_copy_base_templates`, `_copy_dual_agent_templates`,
     `_copy_skill_templates` — read from registry instead of the
     `_MANAGED_*_INITIAL` constants.
   - `upgrade.py`: `_plan_missing_managed_files`,
     `_plan_managed_hooks`, `_plan_managed_rules`,
     `_plan_managed_skills`, `_plan_settings_registration`,
     `_plan_gitignore_patterns` — read from registry.
   - `doctor.py`: rule-presence + hook-presence + skill-presence
     checks read from registry.

5. **Regression tests**:
   - Registry parse roundtrip: load, dump, re-load → equal.
   - Gap 2.8 closure: delete a bridge-essential.md rule from a
     scaffolded project; `plan_upgrade` emits `add` action;
     `execute_upgrade(force=False)` copies the rule back.
   - Skill lockstep: all 6 Phase A skills appear in both
     `initial` and `managed` records (preserves the existing
     parallel-list invariant but now machine-checked).

6. **CI gate** (AST-based, similar to Phase 4D
   `test_exception_markers.py` pattern):
   `tests/test_no_parallel_manifests.py` — fails build if a new
   module adds a module-level list named `_MANAGED_*` outside the
   registry file.

### Out of scope

1. Any new managed-artifact class beyond what already exists
   (e.g., managed workflow files, managed TOML files). Those are
   Track C downstream child bridges (`gtkb-upgrade-managed-workflows`,
   `gtkb-upgrade-toml-migration`).
2. Any per-profile override of artifact content (e.g., "rule X has
   different content for dual-agent vs dual-agent-webapp"). Current
   behavior is all-or-nothing per-profile inclusion; registry
   preserves that.
3. Any runtime artifact (e.g., `.claude/hooks/*.log`). Registry is
   for scaffold-created, template-sourced artifacts only.
4. Any KB schema changes.
5. Any test changes outside the 3 regression tests + 1 CI gate
   described.

## Design

### File layout

```
templates/managed-artifacts.toml        # NEW — registry data
src/groundtruth_kb/project/managed_registry.py  # NEW — loader
src/groundtruth_kb/project/scaffold.py  # MODIFIED — read registry
src/groundtruth_kb/project/upgrade.py   # MODIFIED — read registry, delete _MANAGED_* constants
src/groundtruth_kb/project/doctor.py    # MODIFIED — read registry
tests/test_managed_registry.py          # NEW — parse/roundtrip tests
tests/test_no_parallel_manifests.py     # NEW — AST CI gate
tests/test_upgrade_skills.py            # MODIFIED — update existing tests to use registry
tests/test_upgrade.py                   # MODIFIED — same
tests/test_scaffold_skills.py           # MODIFIED — same
tests/test_scaffold_settings.py         # MODIFIED — same
tests/test_doctor.py                    # MODIFIED (if exists) — registry-aware
```

### Gap 2.8 closure (the live defect)

Current state:

```python
_MANAGED_RULES = [
    ".claude/rules/prime-builder.md",
    ".claude/rules/loyal-opposition.md",
    ".claude/rules/bridge-poller-canonical.md",
    ".claude/rules/prime-bridge-collaboration-protocol.md",
    ".claude/rules/report-depth.md",
]
```

Missing from the list (scaffold-copied but not upgrade-managed):

- `.claude/rules/bridge-essential.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/file-bridge-protocol.md`

Registry-based fix: all 8 rule entries live in
`managed-artifacts.toml`. Scaffold, upgrade, and doctor read the
same list. Delete any rule from an adopter project → upgrade plan
emits `add` → `gt project upgrade --apply` restores.

### Backward compatibility

Strict: **no change to any public API**.

`plan_upgrade(target) -> list[UpgradeAction]` — unchanged
signature, unchanged return shape.

`scaffold_project(options) -> Path` — unchanged signature,
unchanged side effects (same files copied).

`run_doctor(target, profile) -> DoctorReport` — unchanged.

Only the internal mechanism (registry vs parallel lists) changes.
Tests verify same behavior for identical inputs.

### Discriminator handling

The registry uses a `class` field. Each consumer module handles
only its own classes:

- `scaffold._copy_*` handles `hook`, `rule`, `skill` (file copies).
- `upgrade._plan_settings_registration` handles
  `settings-hook-registration`.
- `upgrade._plan_gitignore_patterns` handles `gitignore-pattern`.

No class is silently ignored. If a new class appears in the
registry that no consumer handles, the loader raises
`UnknownArtifactClass(class_name)`.

### Doctor error messages

Currently `doctor.py:489-586` has custom error strings per hook
check. Moving to registry means those strings can be derived from
the registry's `id` field. Preserve existing strings for adopters
who scrape/parse doctor output.

## Exit Criteria

1. `templates/managed-artifacts.toml` exists with 20+ entries (7 hooks
   + 8 rules + 6 skills + 1 settings-hook + 1 gitignore-pattern).
2. `src/groundtruth_kb/project/managed_registry.py` exists with
   `load_managed_artifacts(profile)` + typed records.
3. `scaffold.py`, `upgrade.py`, `doctor.py` all read from registry.
   The `_MANAGED_*` module-level lists are **deleted**.
4. Gap 2.8 closure test passes: delete
   `.claude/rules/bridge-essential.md`, run `plan_upgrade`, see
   `add` action, run `execute_upgrade`, see file restored.
5. Backward-compat tests pass: every existing test in
   `tests/test_scaffold_*` + `tests/test_upgrade_*` +
   `tests/test_doctor*` continues to pass unchanged.
6. `tests/test_managed_registry.py` passes (parse/roundtrip + skill
   lockstep).
7. `tests/test_no_parallel_manifests.py` passes (no `_MANAGED_*`
   module-level lists remain outside the registry module).
8. `mypy --strict src/groundtruth_kb/` clean.
9. `ruff check src/ tests/ templates/` clean + `ruff format --check` clean.
10. Full suite: 1209 → ~1220 tests, all pass (net +11: roundtrip +
    lockstep + gap-2.8 + 4 CI-gate + no regressions on existing tests).
11. Wheel build: `templates/managed-artifacts.toml` shipped.
12. Single commit on GT-KB main: `feat(governance): managed
    artifact registry (Tier 1 C1)` or equivalent.

## Expected deltas

- Net code lines added: ~250 (registry loader + TOML + CI gate test +
  regression tests).
- Net code lines deleted: ~80 (the 5 `_MANAGED_*` module-level
  lists + some redundant filter helpers).
- Test delta: 1209 → ~1220 (+11).

## GO Request

Codex: please verify the design:

1. **TOML format choice** — acceptable, or prefer YAML/JSON/Python-module?
2. **Discriminator `class` field** — right enumeration, or should
   any additional classes be included at C1 time (e.g.,
   `workflow` for future `gtkb-upgrade-managed-workflows`)?
3. **Public API preservation** — strict unchanged. Is this the
   right level of discipline, or should the C1 bridge also expose
   a public `load_managed_artifacts()` helper for downstream
   scripts/tests?
4. **Gap 2.8 closure evidence** — "delete rule, run upgrade, see
   add action" — sufficient regression test, or add adopter-
   scenario integration test too?
5. **CI gate scope** — AST check that catches new
   `_MANAGED_*` lists. False-positive risk on test fixtures?

If approved: single-commit implementation. Estimated ~1.5-2 days
of work (registry design + refactor 3 consumer modules + regression
tests + CI gate + backward-compat verification).

## Scanner Safety

Pre-flight scan: proposal describes file paths, TOML schema, Python
module names, and prose. No literal credential values. Expected
hook verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
