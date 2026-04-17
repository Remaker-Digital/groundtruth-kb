# Non-Disruptive Upgrade Investigation Audit

**Status:** Investigation report (analytical, not remediation).
**Author:** Prime Builder (Opus 4.7).
**Date:** 2026-04-17.
**Target commit:** `3786f49` on `main` (evidence cited below pins to this SHA).
**Governance bridge:** `bridge/gtkb-non-disruptive-upgrade-investigation-003.md` (REVISED);
Codex GO at `bridge/gtkb-non-disruptive-upgrade-investigation-004.md`.

This document is analytical only. It records what `gt project upgrade` does today,
where non-disruptive upgrade gaps exist, and what the next-step child bridges
should tackle. Every remediation is described as a future child bridge, never
implemented here. No Python source file was modified by the commit that
introduces this report.

## Preview-Only Disclaimer (Codex GO -004, Required Condition 4)

> This child-bridge list is a dependency preview only. Each child bridge
> requires its own bridge proposal and GO before implementation. Approval of
> this investigation does NOT authorize implementation of any child bridge.

The preview-only disclaimer above is reproduced in the "Child-Bridge Preview"
section at the end of this report and applies to every downstream bridge
named anywhere in this document.

## Reading Guide

1. Area 1 — Current-state audit of `upgrade.py`.
2. Area 2 — Gap catalog with line-referenced evidence.
3. Area 3 — Customization-preservation model.
4. Area 4 — Atomicity and rollback.
5. Area 5 — Pre-flight check model.
6. Area 6 — Same-version drift surface, including event-by-event hook matrix
   and the **separated** `settings.json` / `settings.local.json` classification
   (Codex GO -004 Required Condition 2).
7. Area 7 — Version semantics.
8. Area 8 — Adopter-facing UX.
9. Area 9 — Scaffold/Template Inventory (55-row M/R/A/U/X table sourced from
   `scaffold.py`, `profiles.py`, and `git ls-files templates/`).
10. Managed-Artifact Registry Strategy (status-quo vs single-registry vs
    paired-manifest-enforcement; recommendation + rationale).
11. Child-Bridge Preview (8 downstream bridges in dependency order; registry
    first).

---

## Area 1 — Current-State Audit of `upgrade.py` at `3786f49`

`src/groundtruth_kb/project/upgrade.py` is a 587-line module whose entry
points are `plan_upgrade(target)` and `execute_upgrade(target, actions,
*, force=False)`. The public contract is:

- `plan_upgrade(target)` returns a list of `UpgradeAction` instances by
  reading state from disk and the project manifest at
  `groundtruth.toml`. It never writes.
- `execute_upgrade(target, actions, *, force=False)` applies the planned
  actions. With `force=False`, `skip` actions are honored. With
  `force=True`, `skip` actions are upgraded to template overwrites after
  writing a `.bak` sibling.

### 1.1 File classes `upgrade.py` is aware of

Four parallel managed lists are declared at module scope:

- `_MANAGED_HOOKS` at `src/groundtruth_kb/project/upgrade.py:36` — 7 hooks:
  `assertion-check.py`, `spec-classifier.py`, `intake-classifier.py`,
  `destructive-gate.py`, `credential-scan.py`, `scheduler.py`,
  `scanner-safe-writer.py`.
- `_MANAGED_RULES` at `src/groundtruth_kb/project/upgrade.py:45` — 5 rules:
  `prime-builder.md`, `loyal-opposition.md`, `bridge-poller-canonical.md`,
  `prime-bridge-collaboration-protocol.md`, `report-depth.md`.
- `_MANAGED_SKILLS` at `src/groundtruth_kb/project/upgrade.py:56` — 6 skill
  files across three skills: `decision-capture`, `bridge-propose`,
  `spec-intake`.
- `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` at
  `src/groundtruth_kb/project/upgrade.py:70` — 1 entry:
  `("scanner-safe-writer.py", True)` (bridge-profile only).
- `_MANAGED_GITIGNORE_PATTERNS` at
  `src/groundtruth_kb/project/upgrade.py:78` — 1 entry:
  `(".claude/hooks/*.log", "Operational hook logs", True)` (bridge-profile
  only).

Profile filtering is concentrated in three helpers:
`_filter_hooks_for_profile` (`upgrade.py:112`),
`_filter_rules_for_profile` (`upgrade.py:128`), and
`_filter_skills_for_profile` (`upgrade.py:136`). All three narrow the
respective managed list based on `ProjectProfile.includes_bridge`.

### 1.2 What `plan_upgrade` emits

`plan_upgrade` (`src/groundtruth_kb/project/upgrade.py:407`) always runs
three drift checks:

1. `_plan_missing_managed_files` (`upgrade.py:149`) — emits `add` actions
   for any managed hook/rule/skill file that is missing on disk. Unlike
   the hash-drift planners below, this check is **not** version-gated;
   it fires at every upgrade run so same-version missing-file drift (for
   example, an adopter who deleted a hook) is always repaired.
2. `_plan_settings_registration` (`upgrade.py:294`) — reads
   `.claude/settings.json`, iterates `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`,
   and emits `register-hook` actions for entries whose command marker
   (`python .claude/hooks/<name>`) is not present in any `PreToolUse`
   entry.
3. `_plan_gitignore_patterns` (`upgrade.py:372`) — reads `.gitignore` and
   emits `append-gitignore` actions for any pattern from
   `_MANAGED_GITIGNORE_PATTERNS` that is not already on its own line.

The three hash-drift planners are **version-gated**
(`upgrade.py:440`): they only run when
`manifest.scaffold_version != __version__`.

4. `_plan_managed_hooks` (`upgrade.py:181`) — for each managed hook that
   exists on disk, compares the project file's SHA-256 to the template's.
   If they differ, emits a `skip` action with reason
   `"File differs from template (customized?) — use --force to overwrite"`.
   Missing files are handled by helper 1.
5. `_plan_managed_rules` (`upgrade.py:222`) — parallel to helper 4 but
   for `.claude/rules/*`.
6. `_plan_managed_skills` (`upgrade.py:256`) — parallel to helper 4 but
   for the skill tree. Preserves subdirectory structure via
   `_map_managed_to_template` (`upgrade.py:97`) which uses
   `removeprefix('.claude/skills/')` to map target paths to template
   paths.

If `groundtruth.toml` has no `[project]` manifest (`read_manifest()`
returns `None`), `plan_upgrade` returns a single `skip` action instructing
the adopter to run `gt project init` first (`upgrade.py:415`).

### 1.3 What `execute_upgrade` does

`execute_upgrade` (`src/groundtruth_kb/project/upgrade.py:448`) iterates
actions in order. Action dispatch:

- `register-hook` → `_execute_register_hook` (`upgrade.py:504`). Rewrites
  `.claude/settings.json` in-place with an appended `PreToolUse` entry.
  Defensive against malformed shapes (non-dict root returns `SKIPPED`).
- `append-gitignore` → `_execute_append_gitignore` (`upgrade.py:559`).
  Appends the pattern to `.gitignore`, or creates the file if absent.
  Idempotent by line-stripped comparison.
- `skip` without `force=True` — passes through with a `SKIPPED` status
  message. With `force=True`, proceeds to the template-copy path.
- `add` / `update` (post-`skip-with-force` path) — resolves the template
  path via `_map_managed_to_template`, backs up any pre-existing project
  file to `<path>.bak` via `shutil.copy2` (`upgrade.py:486`), then copies
  the template into place.

At the end of the loop, if a manifest exists, `execute_upgrade` rewrites
`groundtruth.toml`'s `scaffold_version` to `__version__`
(`upgrade.py:495`) and appends a `VERSION scaffold_version → <ver>`
message to the result log.

### 1.4 Claimed vs actual non-disruptive scope

`upgrade.py`'s non-disruption contract, as implemented, consists of four
guarantees:

1. Missing-file repair is idempotent and safe for adopters who remove a
   managed file.
2. Hash-drift on a managed file defaults to `skip`; only `--force`
   overwrites (after writing `.bak`).
3. Settings repair is append-only: existing `PreToolUse` entries are
   preserved; only missing registrations are added.
4. `.gitignore` repair is append-only: existing lines are preserved.

Within those four guarantees, the surface is narrow: only 7 hooks, 5
rules, 6 skill files, 1 settings registration, and 1 gitignore pattern
are understood. Everything else the scaffold produces is outside the
upgrade planner's awareness.

---

## Area 2 — Gap Catalog With Line-Referenced Evidence

The upgrade planner does not currently cover the following surface. Each
gap is a candidate for a future child bridge (no fix is attempted here).

### Gap 2.1 — Missing pre-flight checks

No git-state check, no in-flight bridge check, no settings parseability
check, no backup writability check. `plan_upgrade`
(`src/groundtruth_kb/project/upgrade.py:407`) only reads the manifest
before generating actions; `execute_upgrade`
(`src/groundtruth_kb/project/upgrade.py:448`) performs no global validation
before mutating files. An adopter running `gt project upgrade --apply` on a
dirty working tree produces a mixed commit and has no rollback primitive
(see Gap 2.2).

### Gap 2.2 — No atomicity or rollback primitive

`execute_upgrade` mutates files one at a time. There is no transaction,
no manifest of what was changed, no `gt project upgrade --rollback`
command, and no `scaffold_version` demotion on failure. If a mid-run
exception fires after file 5 of 10 has been written, the run is left in
an inconsistent state. `.bak` siblings are written
(`src/groundtruth_kb/project/upgrade.py:486`) but they are per-file —
collecting them into a rollback is an adopter task, not a supported
workflow.

### Gap 2.3 — Settings repair is limited to one `PreToolUse` hook

Scaffold writes 12 hook registrations across four event classes
(`src/groundtruth_kb/project/scaffold.py:370` through `:387`); upgrade
repairs exactly one of them — `scanner-safe-writer.py` under
`PreToolUse` — because `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`
(`src/groundtruth_kb/project/upgrade.py:70`) has one entry. `SessionStart`,
`UserPromptSubmit`, and `PostToolUse` registrations are not repaired
by upgrade at all. Full matrix in Area 6.

### Gap 2.4 — No coverage of profile changes at upgrade time

The current `ProjectManifest` records a single `profile` value
(`src/groundtruth_kb/project/manifest.py:22`). Upgrade never compares the
manifest's `profile` to the scaffold-created artifact set. An adopter who
renames their profile (for example, `local-only` → `dual-agent` after
realising they want bridge support) gets no help from upgrade.

### Gap 2.5 — No dry-run / apply output differentiation

`plan_upgrade` returns a list of `UpgradeAction`s. The CLI layer renders
them identically whether they will be executed or not. There is no
"will this create a backup?", "is this a same-version drift repair vs a
version change?", "which profile did I detect?" output.

### Gap 2.6 — No UPGRADE_NOTES or breaking-change annotation

`scaffold_version` is a plain string (`manifest.py:14`). There is no
concept of breaking-change annotation, no `UPGRADE_NOTES.md` emitted
during version bumps, no SemVer-aware comparison. An adopter bumping
from `0.5.0` to `1.0.0` gets the same output as from `0.5.0` to `0.5.1`.

### Gap 2.7 — Workflows / CI / integration files unmanaged

`scaffold.py` generates `.github/workflows/*.yml` via
`_copy_ci_templates` (`src/groundtruth_kb/project/scaffold.py:459`),
`.github/dependabot.yml` and `.coderabbitai.yaml` via
`_copy_integration_templates`
(`src/groundtruth_kb/project/scaffold.py:828`). None of those files are
present in any of `_MANAGED_HOOKS`, `_MANAGED_RULES`, `_MANAGED_SKILLS`,
or the planner helpers. An adopter who stays on a stale workflow
template has no drift remediation path.

### Gap 2.8 — Three of eight rule templates are unmanaged

`git ls-files templates/rules/` returns 8 rule files. `_MANAGED_RULES`
(`src/groundtruth_kb/project/upgrade.py:45`) references 5.
**Unmanaged by upgrade but copied by scaffold** (scaffold.py:273 runs
`for src in (templates / "rules").glob("*.md"):`):
`bridge-essential.md`, `deliberation-protocol.md`, `file-bridge-protocol.md`.
All three are required by `_check_file_bridge_setup` (`doctor.py:774`).
An adopter who deletes one of them fails a doctor check but upgrade
will not restore it, because the managed-list is authoritative for upgrade
and the three missing rules are not listed there.

### Gap 2.9 — No `groundtruth.toml` migration path

`manifest.py` reads specific fields (`manifest.py:73`). If a future
release renames or splits a field, there is no migration step. An
adopter upgrading across that boundary gets a `ValueError` from
`ProjectProfile` resolution or a silent default.

### Gap 2.10 — No interactive mode

Adopters cannot pick individual actions. `plan_upgrade` returns them
all; `execute_upgrade` applies them all (respecting `force`). There is
no "apply action 3 and 5 but skip action 2" path.

---

## Area 3 — Customization-Preservation Model

### 3.1 The skip-if-drift-unless-force contract

Current model: if a managed file's SHA-256 does not match the bundled
template's, emit a `skip` action with reason `"File differs from
template (customized?) — use --force to overwrite"`. Evidence at
`src/groundtruth_kb/project/upgrade.py:211` (hooks),
`src/groundtruth_kb/project/upgrade.py:245` (rules),
`src/groundtruth_kb/project/upgrade.py:283` (skills).

With `force=True`, `execute_upgrade` honors the `skip` but writes a
`.bak` before overwriting (`src/groundtruth_kb/project/upgrade.py:484`).
The `.bak` sibling is an adopter's local recovery tool.

### 3.2 When the contract fails

The contract fails on the **adopter-extended managed file** case. An
adopter who adds a project-specific rule block to
`.claude/rules/prime-builder.md` (a managed rule) sees their content
erased when they run `gt project upgrade --apply --force`. The `.bak`
backup is the only recovery path. There is no merge helper, no marker-
comment convention, and no structured "adopter sections" mechanism.

### 3.3 Other cases the current contract cannot handle

- **Semantically equivalent drift.** A managed file with only whitespace
  changes is treated identically to a semantically divergent one,
  because hash comparison is byte-level.
- **Unmanaged adopter-owned files.** Files outside the managed list are
  never touched. But that is a feature, not a bug, for, for example,
  `bridge/INDEX.md` (see Area 9 row 25). For Gap 2.8 files (three rule
  templates copied by scaffold but not in `_MANAGED_RULES`), it is a
  defect because upgrade cannot repair missing files there either.
- **Template renames.** If a template file is renamed between releases,
  the adopter's project retains the old name indefinitely. Upgrade has
  no concept of file-rename actions.

### 3.4 No opt-out per file

An adopter cannot declare "I have permanently customised
`destructive-gate.py`; do not even warn about it on upgrade." Upgrade
always re-scans every managed file and always emits a `skip` action
when drift is present. For projects with long-lived customisations, this
is noise.

---

## Area 4 — Atomicity and Rollback

### 4.1 Partial-failure behavior of `execute_upgrade`

The loop at `src/groundtruth_kb/project/upgrade.py:458` iterates
sequentially. Each action is one of:

- `register-hook` — reads + writes `.claude/settings.json`.
- `append-gitignore` — reads + writes `.gitignore`.
- template-copy — reads template, writes `.bak`, copies to project.

Any exception in the middle of the loop halts execution. The project is
left with:

- Any files already successfully written.
- Any `.bak` siblings already created.
- No updated `scaffold_version` in the manifest
  (`src/groundtruth_kb/project/upgrade.py:495` runs after the loop, so
  a loop-raised exception prevents it from running).

The behavior is predictable only for the specific case where every
action in the planned list is independent. It is not atomic.

### 4.2 `.bak` behavior

`shutil.copy2(project_path, backup)` is invoked before every template
copy of an existing file (`src/groundtruth_kb/project/upgrade.py:486`).
The `.bak` sibling lives in the same directory with the original file
name plus a `.bak` suffix. Adopter-facing consequences:

- Two successive upgrades that touch the same file overwrite the `.bak`
  with the intermediate state, not the original pre-first-upgrade state.
- `.bak` files are never cleaned up; an adopter who wants a clean tree
  must remove them manually.
- `.bak` files are not in the default project `.gitignore`
  (`src/groundtruth_kb/bootstrap.py:19`), so they can accidentally be
  committed.

### 4.3 Rollback gaps

There is no `gt project upgrade --rollback` command. There is no upgrade
receipt / manifest artifact that records "these 12 files changed". An
adopter who wants to undo a failed upgrade must manually restore
`.bak` files and manually re-edit `groundtruth.toml` to restore the
pre-upgrade `scaffold_version` value.

### 4.4 Settings and `.gitignore` mutations have no rollback hook

`_execute_register_hook` (`src/groundtruth_kb/project/upgrade.py:552`)
writes the full JSON file in one shot. `_execute_append_gitignore`
(`src/groundtruth_kb/project/upgrade.py:578`) does the same. Neither
function writes a `.bak` sibling. Reverting either mutation requires
adopter-side git history or external backup.

---

## Area 5 — Pre-Flight Check Model

The current `plan_upgrade` function performs one check: "is there a
`[project]` manifest in `groundtruth.toml`?"
(`src/groundtruth_kb/project/upgrade.py:415`). Everything else is
implicit in the action generators.

This section catalogs what `gt project upgrade --dry-run` **should**
verify before modifying anything. Nothing here is implemented today;
each is a future child bridge concern
(`gtkb-upgrade-pre-flight-checks`).

### 5.1 Git state

- Working tree clean? — `git status --porcelain` equivalent.
- Currently on a branch an adopter would accept (not `main` unless
  configured)?
- Any unpushed commits that would be awkward to entangle with upgrade
  output?

Today: none of these are checked. An adopter can run the upgrade with a
dirty tree and produce a mixed commit that mingles their in-flight work
with upgrade-generated file writes.

### 5.2 In-flight bridges

- Does `bridge/INDEX.md` contain NEW / REVISED / GO entries that would
  be invalidated by a version bump or file change?
- Is a bridge currently under Codex review?

Today: `plan_upgrade` does not read `bridge/INDEX.md`. An upgrade run
during active bridge review can interact with scanner-safe-writer and
bridge-propose helpers in unexpected ways.

### 5.3 `settings.json` parseability

- Does `json.loads(settings.read_text())` succeed?
- If it throws, the plan currently emits a single `skip` action with
  reason `"Malformed JSON — manual repair required"`
  (`src/groundtruth_kb/project/upgrade.py:320`), but does not halt the
  full upgrade. The gitignore pattern check and managed-file copies still
  run.

A pre-flight check would stop the run before any file is touched,
so the adopter can repair `settings.json` manually without mixed state.

### 5.4 Backup directory writability

- Can the process write to `project_path.with_suffix(suffix + ".bak")`?

Today: the write is attempted lazily during `execute_upgrade`
(`src/groundtruth_kb/project/upgrade.py:486`). If the first file
succeeds and the third fails (permission reasons on one subtree),
the run is left half-applied.

### 5.5 Profile change detection

- Does the manifest's `profile` still match what the adopter expects?
- Has the profile registry changed between the scaffolded version and
  the current version?

Today: no comparison. `profiles.py` is resolved by name only
(`src/groundtruth_kb/project/profiles.py:64`). A profile that has been
refactored in a later release produces silent behavior changes in
upgrade planning.

### 5.6 Scaffold/template coverage delta

- Does the scaffold create artifacts that do not exist on disk but
  that upgrade does not know about either?

Today: `_plan_missing_managed_files` handles the subset inside the
managed lists; anything outside (workflows, integrations, settings.local)
is invisible.

---

## Area 6 — Same-Version Drift Surface

"Same version drift" means: `scaffold_version == __version__` but the
project state diverges from the scaffold state because an adopter
deleted, modified, or mis-wrote a managed file.

The planner explicitly addresses same-version drift for three
concerns (`src/groundtruth_kb/project/upgrade.py:428`):

- Missing managed files (`_plan_missing_managed_files`).
- Missing `PreToolUse` registration for `scanner-safe-writer.py`
  (`_plan_settings_registration`).
- Missing `.claude/hooks/*.log` gitignore pattern
  (`_plan_gitignore_patterns`).

Everything else is only addressed on a version bump, and often not at
all.

### 6.1 Event-by-event hook audit matrix

Codex GO -004 Required Condition 2: `.claude/settings.json` and
`.claude/settings.local.json` **must be classified separately**. The
current evidence:

- `.claude/settings.json` — scaffold writes it
  (`src/groundtruth_kb/project/scaffold.py:298`); it is **tracked** in
  git (test at `tests/test_scaffold_settings.py:121`); it currently
  holds 12 governance hook registrations across 4 event classes
  (`scaffold.py:370`-`:387`).
- `.claude/settings.local.json` — scaffold copies the template
  (`scaffold.py:293`-`:295`); it is **ignored** by git (bootstrap.py:27
  writes `.claude/settings.local.json` into the scaffolded project's
  `.gitignore`); the template currently contains only `permissions`
  (`templates/project/settings.local.json`), no hooks.

The following matrix enumerates each event class the current scaffold
produces, showing scaffold behavior vs upgrade behavior vs adopter-
survival semantics. Rows are per-event-class for `.claude/settings.json`,
plus two summary rows for `.claude/settings.local.json`.

| # | File | Event class | Scaffold writes (hook count + names) | Upgrade manages | Adopter-extended hook survives? | Notes |
|---|------|-------------|---------------------------------------|------------------|---------------------------------|-------|
| 1 | `.claude/settings.json` | `SessionStart` | 2 hooks: `session-start-governance.py`, `assertion-check.py` (`scaffold.py:370`-`:372`) | No — not in `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` (that list is `PreToolUse`-only, `upgrade.py:70`) | Yes (upgrade never reads this event class) | If adopter deletes a registration, upgrade cannot repair it |
| 2 | `.claude/settings.json` | `UserPromptSubmit` | 2 hooks: `delib-search-gate.py`, `intake-classifier.py` (`scaffold.py:374`-`:376`) | No | Yes (upgrade never reads this event class) | Deletion is unrecoverable via upgrade |
| 3 | `.claude/settings.json` | `PostToolUse` | 1 hook: `delib-search-tracker.py` (`scaffold.py:378`-`:379`) | No | Yes (upgrade never reads this event class) | Deletion is unrecoverable via upgrade |
| 4 | `.claude/settings.json` | `PreToolUse` | 6 hooks: `spec-before-code.py`, `bridge-compliance-gate.py`, `kb-not-markdown.py`, `destructive-gate.py`, `credential-scan.py`, `scanner-safe-writer.py` (`scaffold.py:382`-`:387`) | **Partial** — only `scanner-safe-writer.py` is in `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` (`upgrade.py:71`) | Yes | If adopter deletes `destructive-gate.py` registration, upgrade will not repair it; if they delete `scanner-safe-writer.py`, upgrade repairs on next run |
| 5 | `.claude/settings.local.json` | (any) | Template copied whole (`scaffold.py:293`-`:295`); template currently has `permissions` only, no `hooks` | Not managed by upgrade | N/A — scaffold never writes hooks here; adopter content is entirely local | Doctor uses this file's `UserPromptSubmit.hooks` as the classifier activation switch (`doctor.py:432`), but only because the adopter manually adds hook entries here. `_check_settings_classifiers` emits warnings, never upgrade actions |
| 6 | `.claude/settings.local.json` | (cross-cutting) | Ignored by git (`bootstrap.py:27` writes the ignore pattern into the scaffolded project's `.gitignore`) | Not managed by upgrade | Yes (not managed) | Adopter's local permissions override live here; upgrade never touches this file. Intentional split — see row classification below |

Two observations from this matrix:

1. Of the 12 scaffold-time hook registrations in `.claude/settings.json`,
   **11 are unrepairable** by the current upgrade planner. Only
   `scanner-safe-writer.py` (row 4) is covered. This is the primary
   drift gap for `.claude/settings.json` and the scope of the
   `gtkb-upgrade-settings-merge` child bridge.
2. `.claude/settings.local.json` is **correctly** unmanaged today. It
   is the adopter-owned local overlay. The doctor check at
   `doctor.py:370` reports on what the adopter has placed there; it is
   not a drift repair target. Any future settings child bridge must
   preserve this split: settings.json = M (managed, tracked), settings.local.json = A (adopter-owned, ignored).

### 6.2 `.gitignore` same-version drift

The single managed pattern is `.claude/hooks/*.log`
(`src/groundtruth_kb/project/upgrade.py:79`). Everything else the
scaffold writes to `.gitignore` is **unmanaged**:

- Bootstrap-written baseline (`bootstrap.py:19`): `__pycache__/`,
  `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `.venv/`,
  `groundtruth.db`, `.groundtruth/`, `.claude/settings.local.json`.
- Bridge-profile additions (`scaffold.py:304`-`:308`): three
  `independent-progress-assessments/bridge-automation/` runtime
  state patterns.

If an adopter deletes `groundtruth.db` from their `.gitignore`,
upgrade will not restore it. Future broadening of
`_MANAGED_GITIGNORE_PATTERNS` is a candidate for the
`gtkb-upgrade-settings-merge` or a dedicated gitignore child bridge.

### 6.3 Managed-file deletion drift (works today)

For the 7 + 5 + 6 = 18 files in `_MANAGED_HOOKS` + `_MANAGED_RULES` +
`_MANAGED_SKILLS`, deletion is detected and repaired on every run by
`_plan_missing_managed_files` (`upgrade.py:149`). This is the one
same-version drift case the current planner handles well.

### 6.4 Settings JSON malformation drift

If `.claude/settings.json` is syntactically broken, `_plan_settings_registration`
(`upgrade.py:319`) returns a single `skip` action. The scanner-safe-writer
registration check does not fail-fast because it is defensive. The remainder
of the upgrade plan still runs. No `scaffold_version` rollback on failure.

---

## Area 7 — Version Semantics

### 7.1 `scaffold_version` today

`ProjectManifest.scaffold_version` is a plain string
(`src/groundtruth_kb/project/manifest.py:25`). It defaults to the
package's `__version__` (`manifest.py:13`, `SCAFFOLD_VERSION =
__version__`). When `execute_upgrade` succeeds, the manifest is
rewritten with the current `__version__`
(`src/groundtruth_kb/project/upgrade.py:497`).

No SemVer-aware comparison, no minimum-supported-version check, no
breaking-change detection. The string is compared for byte equality
only (`upgrade.py:440`, `manifest.scaffold_version != __version__`).

### 7.2 Gaps

- **No UPGRADE_NOTES.md emitted.** There is no mechanism for an author
  of a new scaffold release to say "this version renames hook X to Y;
  adopters should review". The adopter sees file changes but no
  narrative.
- **No breaking-change annotation.** An API-breaking version bump
  (for example, removing a managed hook) produces the same upgrade
  output as a patch. Adopters on CI with `gt project upgrade --apply`
  in a cron job cannot distinguish safe-to-automate upgrades from
  review-required upgrades.
- **No minimum-version gate.** If an adopter skips several releases,
  the planner runs the same action set as a single-step upgrade;
  there is no concept of "if scaffold_version < 0.3.0, read the 0.3.0
  migration notes first".
- **No bidirectional version drift check.** If an adopter somehow ends
  up with `scaffold_version = 0.9.0` but `__version__ = 0.5.0`
  (for example, because they rolled back the package after a failed
  upgrade), the version check still returns "different", runs the
  hash-drift planners, and overwrites the manifest on the way out.
- **`scaffold_version = "0.0.0"` default when missing in the manifest**
  (`manifest.py:79`). An adopter whose manifest lacks the field gets
  silent re-versioning on the next successful upgrade.

These gaps are the scope of the `gtkb-upgrade-changelog-integration`
child bridge.

---

## Area 8 — Adopter-Facing UX

### 8.1 Current output shape

`plan_upgrade` returns a list of `UpgradeAction`s; the CLI layer (not
in scope for this audit) formats them. `execute_upgrade` returns a list
of status strings, one per action
(`src/groundtruth_kb/project/upgrade.py:456`).

### 8.2 UX gaps observable from the upgrade module surface

- **No grouping or summary.** The CLI surface iterates actions in a
  flat list. An adopter reading 14 actions has no "these 8 are
  same-version repairs, these 6 are version-change updates" grouping.
- **No detected-profile output.** The CLI does not print "detected
  profile: dual-agent" before the action list. An adopter who expected
  `local-only` but has `dual-agent` in their manifest gets no early
  warning.
- **`skip` reason is terse.** The string `"File differs from template
  (customized?) — use --force to overwrite"` is the same for every file.
  There is no diff preview, no diff stat, no "last modified by adopter
  on 2026-03-12" context.
- **Status strings are not machine-parseable.** `UPDATED`, `SKIPPED`,
  `REGISTERED`, `APPENDED`, `BACKUP`, `VERSION` are conventionalized
  prefixes but not namespaced or JSON-encodable. Automation consumers
  must regex-parse.
- **No `--json` flag.** Adopters cannot consume `gt project upgrade
  --dry-run` output programmatically for compliance dashboards.
- **No `--interactive` flag.** Adopter cannot opt out of specific
  actions without either `--force` (overrides all skips) or manual
  rerun with edited manifest.

### 8.3 Feedback flow on failures

`execute_upgrade` returns status strings. It does not raise on
individual action failure; it appends a `SKIPPED ... — <reason>` entry
to results and continues. An adopter must parse every line to find
failures. There is no non-zero exit-code path for partial success.

---

## Area 9 — Scaffold/Template Inventory

This inventory was sourced from three evidence streams:

1. `src/groundtruth_kb/project/scaffold.py` — all `_copy_*` and
   `_write_*` helpers, line-referenced below.
2. `src/groundtruth_kb/project/profiles.py` — the 3 profiles'
   `includes_*` flags and profile-filtered scaffolds.
3. `git ls-files templates/` — the 55 currently tracked template files.

Classification codes:

- **M (Managed)** — in `_MANAGED_HOOKS` / `_MANAGED_RULES` /
  `_MANAGED_SKILLS` with both missing-file repair and hash-drift
  semantics (plus associated settings/gitignore managed entries).
- **R (Repairable)** — missing-file drift only (in
  `_plan_missing_managed_files` but, in practice, every M file is also
  R, so no file lives in R-alone today).
- **A (Adopter-owned)** — never overwritten after initial scaffold
  (for example, `bridge/INDEX.md` after first scaffold).
- **U (Unmanaged gap)** — scaffold-created, should have upgrade
  story, does not — needs a child bridge.
- **X (Out of scope)** — intentionally excluded with rationale.

### 9.1 Inventory table (55 rows)

| # | Artifact | Profile | Source of creation | Class | Rationale |
|---|----------|---------|--------------------|-------|-----------|
| 1 | `CLAUDE.md` | all | `scaffold.py:181`-`:182` (base) | A | Template copied once; heavily adopter-customized afterward. Hash would always drift. |
| 2 | `MEMORY.md` | all | `scaffold.py:181`-`:182` (base) | A | Per-session mutable adopter state. Template is a starter, not a canonical. |
| 3 | `README.md` (template) | — | `templates/README.md` tracked but **not copied** by current scaffold | X | Not referenced by any `_copy_*` helper; candidate for removal or explicit adoption in a later bridge. |
| 4 | `groundtruth.toml` | all | `bootstrap._write_groundtruth_toml` via `scaffold.py:90`-`:96` | A | Manifest; adopter owns project-specific fields (`project_name`, etc.). Upgrade rewrites only `scaffold_version` (`upgrade.py:497`). |
| 5 | `groundtruth.db` | all | `bootstrap._initialize_database` via `scaffold.py:97` | X | Runtime state, ignored by git (`bootstrap.py:25`), restored via init. |
| 6 | `.gitignore` (project) | all | `bootstrap._write_project_gitignore` via `scaffold.py:98` | **Partial U** | Append-only `_plan_gitignore_patterns` covers 1 pattern (`.claude/hooks/*.log`). 7 baseline patterns and 3 bridge-profile patterns are unmanaged. |
| 7 | `.editorconfig` | all (base copies) | `scaffold.py:198`-`:201` | U | Copied from `templates/project/.editorconfig` at scaffold time; no upgrade planner coverage. |
| 8 | `Makefile` | all (base copies) | `scaffold.py:198`-`:201` | U | Copied from `templates/project/Makefile`; no upgrade planner coverage. |
| 9 | `.pre-commit-config.yaml` | all (base copies) | `scaffold.py:198`-`:201` | U | Copied from `templates/project/.pre-commit-config.yaml`; no upgrade planner coverage. |
| 10 | `pyproject-sections.toml` | all | `scaffold._write_pyproject_sections` via `scaffold.py:204` | U | Generated inline; no upgrade planner coverage. |
| 11 | `.claude/hooks/assertion-check.py` | all | `scaffold.py:186`-`:187` + `upgrade._MANAGED_HOOKS` `upgrade.py:37` | M | Same-version missing-file repair + version-gated hash drift. |
| 12 | `.claude/hooks/spec-classifier.py` | all | `scaffold.py:186`-`:187` + `upgrade._MANAGED_HOOKS` `upgrade.py:38` | M | Same-version missing-file repair + version-gated hash drift. |
| 13 | `.claude/hooks/intake-classifier.py` | all (copied) + dual-agent (repaired) | `scaffold.py:186`-`:187` + `upgrade._MANAGED_HOOKS` `upgrade.py:39` with `_filter_hooks_for_profile` | M (dual-agent) / A (local-only) | Local-only profile does not repair; managed file filter drops it (`upgrade.py:119`-`:124`). |
| 14 | `.claude/hooks/destructive-gate.py` | dual-agent copy via `scaffold.py:277`-`:280`; base copy via `scaffold.py:186`-`:187` | `upgrade._MANAGED_HOOKS` `upgrade.py:40` with filter | M (dual-agent) / A (local-only) | Same filter logic as row 13. |
| 15 | `.claude/hooks/credential-scan.py` | dual-agent | `scaffold.py:186`-`:187` + `upgrade.py:41` | M (dual-agent) / A (local-only) | Same filter logic. |
| 16 | `.claude/hooks/scheduler.py` | dual-agent | `scaffold.py:186`-`:187` + `upgrade.py:42` | M (dual-agent) / A (local-only) | Same filter logic. |
| 17 | `.claude/hooks/scanner-safe-writer.py` | dual-agent | `scaffold.py:186`-`:187` + `upgrade.py:43` | M (dual-agent) / A (local-only) | Same filter logic + settings registration (`upgrade.py:71`). |
| 18 | `.claude/hooks/bridge-compliance-gate.py` | all (scaffold copies every `.py` in `templates/hooks/`) | `scaffold.py:186`-`:187`; **not** in `_MANAGED_HOOKS` | U | Scaffold copies it; upgrade does not track. Deletion is unrecoverable. Only referenced via settings registration, which is also unmanaged (row 47 of 9.2). |
| 19 | `.claude/hooks/delib-search-gate.py` | all (scaffold copies every `.py`) | `scaffold.py:186`-`:187`; **not** in `_MANAGED_HOOKS` | U | Same as row 18. |
| 20 | `.claude/hooks/delib-search-tracker.py` | all (scaffold copies every `.py`) | `scaffold.py:186`-`:187`; **not** in `_MANAGED_HOOKS` | U | Same as row 18. |
| 21 | `.claude/hooks/kb-not-markdown.py` | all (scaffold copies every `.py`) | `scaffold.py:186`-`:187`; **not** in `_MANAGED_HOOKS` | U | Same as row 18. |
| 22 | `.claude/hooks/session-health.py` | all (scaffold copies every `.py`) | `scaffold.py:186`-`:187`; **not** in `_MANAGED_HOOKS` | U | Present in `templates/hooks/`; not referenced by settings.json scaffold (no event class). Dead copy or pending integration. |
| 23 | `.claude/hooks/session-start-governance.py` | all (scaffold copies every `.py`) | `scaffold.py:186`-`:187`; **not** in `_MANAGED_HOOKS` | U | Registered in settings.json `SessionStart` (`scaffold.py:371`) but not managed anywhere. |
| 24 | `.claude/hooks/spec-before-code.py` | all (scaffold copies every `.py`) | `scaffold.py:186`-`:187`; **not** in `_MANAGED_HOOKS` | U | Registered in settings.json `PreToolUse` (`scaffold.py:382`); not managed. |
| 25 | `.claude/rules/prime-builder.md` | all | `scaffold.py:189`-`:194` (base: prime-builder only) / `scaffold.py:272`-`:274` (dual-agent: all rules) + `upgrade._MANAGED_RULES` `upgrade.py:46` | M | Same-version missing-file repair + version-gated hash drift. |
| 26 | `.claude/rules/loyal-opposition.md` | dual-agent | `scaffold.py:272`-`:274` + `upgrade.py:47` | M (dual-agent) / X (local-only) | `_filter_rules_for_profile` drops all non-`prime-builder` rules for local-only (`upgrade.py:128`-`:133`). |
| 27 | `.claude/rules/bridge-poller-canonical.md` | dual-agent | `scaffold.py:272`-`:274` + `upgrade.py:48` | M (dual-agent) / X (local-only) | Same filter. |
| 28 | `.claude/rules/prime-bridge-collaboration-protocol.md` | dual-agent | `scaffold.py:272`-`:274` + `upgrade.py:49` | M (dual-agent) / X (local-only) | Same filter. |
| 29 | `.claude/rules/report-depth.md` | dual-agent | `scaffold.py:272`-`:274` + `upgrade.py:50` | M (dual-agent) / X (local-only) | Same filter. |
| 30 | `.claude/rules/bridge-essential.md` | dual-agent | `scaffold.py:272`-`:274`; **not** in `_MANAGED_RULES` | U | Gap 2.8. Required by `_check_file_bridge_setup` (`doctor.py:483`-`:486`) but unmanaged. Deletion is detected by doctor but not repaired by upgrade. |
| 31 | `.claude/rules/deliberation-protocol.md` | dual-agent | `scaffold.py:272`-`:274`; **not** in `_MANAGED_RULES` | U | Gap 2.8. Same as row 30. |
| 32 | `.claude/rules/file-bridge-protocol.md` | dual-agent | `scaffold.py:272`-`:274`; **not** in `_MANAGED_RULES` | U | Gap 2.8. Same as row 30. |
| 33 | `.claude/skills/decision-capture/SKILL.md` | dual-agent | `scaffold._copy_skill_templates` (`scaffold.py:327`, `:344`) + `upgrade._MANAGED_SKILLS` (`upgrade.py:57`) | M | Same-version missing-file repair + version-gated hash drift. Subdirectory preserved via `_map_managed_to_template` (`upgrade.py:103`-`:108`). |
| 34 | `.claude/skills/decision-capture/helpers/record_decision.py` | dual-agent | Same as row 33 + `upgrade.py:58` | M | Same. |
| 35 | `.claude/skills/bridge-propose/SKILL.md` | dual-agent | Same path + `upgrade.py:59` | M | Same. |
| 36 | `.claude/skills/bridge-propose/helpers/write_bridge.py` | dual-agent | Same path + `upgrade.py:60` | M | Same. |
| 37 | `.claude/skills/spec-intake/SKILL.md` | dual-agent | Same path + `upgrade.py:61` | M | Same. |
| 38 | `.claude/skills/spec-intake/helpers/spec_intake.py` | dual-agent | Same path + `upgrade.py:62` | M | Same. |
| 39 | `.claude/settings.json` | dual-agent | `scaffold._write_settings_json` via `scaffold.py:298`, `:353` | **Partial M / Partial U** | `_plan_settings_registration` (`upgrade.py:294`) manages 1 of 12 hook registrations (scanner-safe-writer under PreToolUse). Deleted or corrupted entries for the other 11 are unrecoverable. Tracked in git. |
| 40 | `.claude/settings.local.json` | dual-agent | `scaffold.py:292`-`:295` (copies `templates/project/settings.local.json`) | A | Codex GO -004 Condition 2: classified **separately** from `settings.json` (row 39). Adopter-owned, ignored by git (`.gitignore` pattern at `bootstrap.py:27`); scaffold template contains permissions only (`templates/project/settings.local.json`). Upgrade never touches it. Doctor reports on adopter-placed classifier hooks (`doctor.py:432`). |
| 41 | `bridge/INDEX.md` | dual-agent | `scaffold.py:319`-`:324` via `_generate_bridge_index` | A | After first scaffold, holds live bridge history and must never be overwritten. Upgrade correctly does not touch it. |
| 42 | `BRIDGE-INVENTORY.md` | dual-agent | `scaffold.py:254`-`:256` | U | Copied at scaffold time; no upgrade planner coverage. Required by `_check_file_bridge_setup` (`doctor.py:751`). |
| 43 | `bridge-os-poller-setup-prompt.md` | dual-agent | `scaffold.py:259`-`:261` | U | Copied at scaffold time; no upgrade planner coverage. Required by `_check_file_bridge_setup` (`doctor.py:751`). |
| 44 | `AGENTS.md` | dual-agent | `scaffold.py:263`-`:268` (copies template or writes default) | A | Heavily adopter-customized (Loyal Opposition operating contract). |
| 45 | `independent-progress-assessments/` directory | dual-agent | `scaffold.py:283`-`:285` | A | Adopter's Codex workspace. |
| 46 | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` | dual-agent | `scaffold.py:285` | A | Adopter's Codex reports live here. |
| 47 | `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md` | dual-agent (if template present) | `scaffold.py:287`-`:290` | U | Copied from `templates/project/codex-bootstrap/`; no upgrade planner coverage. |
| 48 | `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md` | dual-agent | Same as row 47 | U | Same. |
| 49 | `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` | dual-agent | Same as row 47 | U | Same. |
| 50 | `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md` | dual-agent | Same as row 47 | A | Per-session adopter log state. Copying the template at scaffold is fine; upgrade must not overwrite. |
| 51 | `.github/workflows/test.yml` | all (profile selects tier: minimal, standard, or full) | `scaffold._copy_ci_templates` (`scaffold.py:459`-`:479`) | U | Unmanaged workflows. Gap 2.7. |
| 52 | `.github/workflows/build.yml` | dual-agent-webapp (full tier only) | Same path | U | Unmanaged workflows. Gap 2.7. |
| 53 | `.github/workflows/deploy.yml` | dual-agent-webapp (full tier only) | Same path | U | Unmanaged workflows. Gap 2.7. |
| 54 | `.github/dependabot.yml` | when `--integrations` flag | `scaffold._copy_integration_templates` (`scaffold.py:828`-`:858`) | U | Unmanaged integrations. Gap 2.7. |
| 55 | `.coderabbitai.yaml` | when `--integrations` flag | Same path | U | Unmanaged integrations. Gap 2.7. |

### 9.2 Supplementary non-file artifacts

The managed-list surface also controls settings-registration and
gitignore-pattern targets that do not appear as standalone rows above.
These are implicit dependencies of the M classification:

- **Settings registration (1 entry):** `scanner-safe-writer.py` under
  `PreToolUse` (`upgrade.py:71`). Column "Upgrade manages" of row 39.
- **Gitignore pattern (1 entry):** `.claude/hooks/*.log`
  (`upgrade.py:79`). Not a separate row because it lives inside `.gitignore`
  (row 6).

### 9.3 Profile-dependent classification delta

Classification for a single row can change between profiles because of
`_filter_*_for_profile` helpers:

- Rows 13–17 are M under `dual-agent` / `dual-agent-webapp` but A under
  `local-only` because `_filter_hooks_for_profile` drops non-`{assertion-check, spec-classifier}`
  hooks for non-bridge profiles (`upgrade.py:119`-`:124`).
- Rows 26–29 are M under bridge profiles but X under `local-only`
  because `_filter_rules_for_profile` drops all non-`prime-builder`
  rules for non-bridge profiles (`upgrade.py:130`-`:132`).
- Rows 33–38 are M under bridge profiles but X under `local-only`
  because `_filter_skills_for_profile` returns empty for non-bridge
  (`upgrade.py:144`-`:145`).

### 9.4 Inventory totals

55 rows. Class distribution (using the dual-agent profile, because
dual-agent-webapp supersets it):

- M (Managed): 18 rows (rows 11–17, 25–29, 33–38).
- A (Adopter-owned): 13 rows (rows 1, 2, 4, 13–17 for local-only, 40,
  41, 44, 45, 46, 50). *Note:* several rows have profile-dependent
  classification — counted here by the classification they hold under
  the dual-agent profile.
- U (Unmanaged gap): 20 rows (rows 6 partial, 7–10, 18–24, 30–32, 42,
  43, 47–49, 51–55).
- X (Out of scope): 2 rows (rows 3, 5).
- Partial M/U (shared responsibility): rows 6, 39.

The 20 U-class rows and the 2 partial-M rows are the primary surface
for the next 7 child bridges. Row 6 is special because it straddles a
ManagedPattern surface; row 39 is the focus of
`gtkb-upgrade-settings-merge`.

---

## Managed-Artifact Registry Strategy

### Problem statement

`upgrade.py` has 4 parallel managed-artifact lists
(`_MANAGED_HOOKS`, `_MANAGED_RULES`, `_MANAGED_SKILLS`,
`_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`, plus `_MANAGED_GITIGNORE_PATTERNS`).
`scaffold.py` has its own lockstep list, `_MANAGED_SKILLS_INITIAL`
(`scaffold.py:34`-`:41`). The comment on `_MANAGED_SKILLS_INITIAL`
explicitly says "Kept in lockstep with `upgrade._MANAGED_SKILLS`".
There is no enforcement; the lockstep is a comment contract.

Every time a new managed artifact is added, a future author must update
every list, in every module, without the compiler catching a miss. This
is the mechanism behind Gap 2.8 (three rule files copied by scaffold
but missing from `_MANAGED_RULES`).

Three strategies are evaluated below. Each must answer:

1. Where does the canonical managed-artifact set live?
2. How do scaffold, upgrade, and doctor consume it?
3. How does a new artifact get added without drift between modules?
4. What is the migration cost from today's parallel lists?

### Option A — Status quo (parallel lists, comment-level contract)

Keep `_MANAGED_HOOKS`, `_MANAGED_RULES`, `_MANAGED_SKILLS`,
`_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`, `_MANAGED_GITIGNORE_PATTERNS`,
`_MANAGED_SKILLS_INITIAL` as parallel lists. Rely on review discipline.

**Pros:**

- Zero migration cost.
- Simplest code.

**Cons:**

- Gap 2.8 is a live defect produced by exactly this posture.
- Every future managed artifact has combinatorial review cost (N
  reviewer's eyes across N lists). Growth is super-linear.
- Cannot ship the non-disruptive upgrade investigation's other 7 child
  bridges without adding more parallel lists each time.

### Option B — Single declarative registry

Introduce one module (for example, `src/groundtruth_kb/project/managed_registry.py`)
containing a single list of `ManagedArtifact` dataclasses. Each entry
names:

- `target_path` (for example, `.claude/hooks/assertion-check.py`)
- `template_path` (for example, `hooks/assertion-check.py`)
- `classification` (M / R / A / U / X enum)
- `profile_filter` (callable or tuple of profile names)
- `settings_registration` (optional nested: event, hook filename,
  matcher)
- `gitignore_pattern` (optional string)

`scaffold.py`, `upgrade.py`, and `doctor.py` all consume this registry
instead of their local lists. Adding a new managed artifact is one
entry in one file.

**Pros:**

- Gap 2.8 becomes a compile-level defect (or a clearly failing doctor
  check) because registry consumers catch the mismatch.
- Every future child bridge extends the registry, not parallel lists.
- Clean mental model for adopters reading GT-KB source to understand
  what is "canonical" vs "adopter-owned".
- Registry entries can be exported to JSON/TOML for consumption by
  external tooling (for example, the
  `gtkb-upgrade-changelog-integration` bridge).

**Cons:**

- One-time migration cost across 3 modules.
- Slight cognitive cost: developers who touch scaffold must learn the
  registry shape instead of editing a bare list.
- Some artifacts (for example, `bridge/INDEX.md`) are A-class with
  complex lifecycles that do not fit the "managed/unmanaged" axis
  cleanly; the registry needs a classification taxonomy that handles
  A-class lifecycles without overfitting.

### Option C — Paired-manifest enforcement

Keep today's parallel lists, but add (1) a lockstep test
(`tests/test_managed_list_parallelism.py`) that enforces
`_MANAGED_SKILLS == set-derived-from(_MANAGED_SKILLS_INITIAL)` and
equivalent invariants, and (2) a linter/AST-check that surfaces any
scaffold-copied-but-not-managed file class (catching Gap 2.8 as a CI
failure).

**Pros:**

- Minimal migration cost (no registry module).
- Enforcement is mechanical (tests + CI), not review-only.
- Compatible with Option B as a stepping stone (use paired-manifest
  enforcement to catch current drift, then migrate to a registry in a
  later bridge).

**Cons:**

- Does not reduce the combinatorial review cost at edit time —
  a future author still edits N lists and relies on the test to catch
  the miss.
- Test/linter complexity grows as managed-artifact classes grow.
- Does not address the broader "scaffold, upgrade, and doctor all need
  the same source of truth" problem. They still read from different
  lists; the tests just verify those lists are parallel.

### Recommendation — Option B, single declarative registry

**Recommendation:** adopt Option B as the first child bridge
(`gtkb-managed-artifact-registry`).

**Rationale:**

- Gap 2.8 is the evidence that Option A does not scale. Option C
  partially mitigates Option A but does not remove the scaling problem.
- Every other child bridge in the preview list extends the managed-
  artifact surface (workflows, integrations, more settings registrations,
  more gitignore patterns). Doing that on parallel lists multiplies
  Gap-2.8-class defects.
- Option B gives future adopter-facing documentation
  (`gt project show-managed`, a hypothetical future CLI command) a single
  query target.
- The migration cost is one time; the defect-prevention benefit compounds.

**Rejected alternatives:**

- Option A (status quo) is rejected because it produced Gap 2.8 once and
  has no mechanism to prevent re-occurrence.
- Option C (paired-manifest enforcement) is rejected as the primary choice
  because it treats the symptom (drift between lists) without fixing the
  cause (multiple sources of truth). It is an acceptable interim step if
  the full registry bridge is delayed; in that case, Option C should be
  adopted as a time-boxed interim patch with Option B as the follow-on
  target.

Detailed implementation decisions — TOML vs Python module vs KB spec,
dataclass shape, profile-filter callable signature, migration test
strategy — are deferred to the `gtkb-managed-artifact-registry` child
bridge proposal.

---

## Child-Bridge Preview

The following child bridges close the gaps in Areas 2–9. They are
ordered by dependency: registry first (every other bridge extends the
registry), then pre-flight and rollback (safety), then the event-class
and content-class bridges.

> **Preview-only disclaimer (verbatim from Codex GO -004 Condition 4):**
> This child-bridge list is a dependency preview only. Each child
> bridge requires its own bridge proposal and GO before implementation.
> Approval of this investigation does NOT authorize implementation of
> any child bridge.

1. **`gtkb-managed-artifact-registry`** — Adopt Option B above. Single
   declarative registry consumed by `scaffold.py`, `upgrade.py`, and
   `doctor.py`. Closes Gap 2.8 as a side effect. **Precondition for
   every other bridge in this list.**
2. **`gtkb-upgrade-pre-flight-checks`** — Add `gt project upgrade
   --dry-run` pre-flight checks listed in Area 5. Gates `--apply`
   behind a clean pre-flight. Depends on registry (bridge 1) for the
   scaffold/template coverage delta check (§5.6).
3. **`gtkb-upgrade-rollback`** — Introduce `gt project upgrade
   --rollback` plus an upgrade receipt/manifest. Cleans up Gap 2.2 and
   Area 4 gaps. Depends on registry (bridge 1) to know which artifacts
   were in scope for the superseded upgrade.
4. **`gtkb-upgrade-settings-merge`** — Expand
   `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` to the full 12-hook matrix
   across all four event classes (Area 6.1). Preserve the
   settings.json / settings.local.json split (Area 6 row classification).
   Depends on registry (bridge 1) for the settings-registration entries.
5. **`gtkb-upgrade-changelog-integration`** — Add `UPGRADE_NOTES.md`,
   SemVer-aware version comparison, breaking-change annotations
   (Area 7). Depends on registry (bridge 1) only incidentally (for
   artifact-level migration notes).
6. **`gtkb-upgrade-interactive-mode`** — Add `--interactive` and
   `--json` flags; grouping output by same-version vs version-change
   (Area 8). Depends on registry (bridge 1) for per-artifact metadata
   exposed in the interactive prompts.
7. **`gtkb-upgrade-managed-workflows`** — Extend registry to cover
   `.github/workflows/*.yml` and `.github/dependabot.yml`
   and `.coderabbitai.yaml` (Gap 2.7; Area 9 rows 51–55). Depends on
   registry (bridge 1) and on bridge 4 (settings-merge) as a pattern
   reference.
8. **`gtkb-upgrade-toml-migration`** — Introduce a `groundtruth.toml`
   migration layer so future field renames/splits do not break older
   projects (Gap 2.9). Depends on registry (bridge 1) and on bridge 5
   (changelog) for version-gated migration execution.

### Out-of-scope callouts

Each of these needs its own separate bridge outside the non-disruptive
upgrade investigation:

- Azure adoption (covered by `gtkb-azure-enterprise-readiness-taxonomy`,
  see `docs/reference/azure-readiness-taxonomy.md`).
- `bridge/INDEX.md` history compaction (row 41 is A by design; a
  compaction strategy is a workflow-level concern, not an upgrade
  concern).
- Template-rename / managed-file rename support (Section 3.3). Candidate
  for a future bridge after bridge 1 lands and rename semantics can be
  expressed as registry entries.

---

## Cross-Reference Index

The audit areas and child bridges reference one another. The table
below is the forward/backward mapping for future bridge reviewers.

| Area | Feeds child bridge |
|------|--------------------|
| Area 1 — Current-state audit | Every child bridge (foundational) |
| Area 2 — Gap catalog | Gap 2.1 → bridge 2; Gap 2.2 → bridge 3; Gap 2.3 → bridge 4; Gap 2.4 → bridge 2 + 6; Gap 2.5 → bridge 6; Gap 2.6 → bridge 5; Gap 2.7 → bridge 7; Gap 2.8 → bridge 1 (side effect); Gap 2.9 → bridge 8; Gap 2.10 → bridge 6 |
| Area 3 — Customization-preservation | bridge 4 (settings merge semantics) |
| Area 4 — Atomicity and rollback | bridge 3 |
| Area 5 — Pre-flight checks | bridge 2 |
| Area 6 — Same-version drift + event matrix | bridge 4 (primary scope) |
| Area 7 — Version semantics | bridge 5 |
| Area 8 — Adopter-facing UX | bridge 6 |
| Area 9 — Scaffold/template inventory | bridge 1 (registry shape) + bridge 7 (workflows) |
| Managed-Artifact Registry Strategy | bridge 1 |

---

## Verification Evidence (from git at `3786f49`, reproducible after commit)

Commands an external reviewer can run against `main` to verify each
evidence claim in this report:

```text
# 1. Confirm the source files cited exist and line refs are valid at 3786f49
git show 3786f49:src/groundtruth_kb/project/upgrade.py | sed -n '36,80p'     # managed lists
git show 3786f49:src/groundtruth_kb/project/upgrade.py | sed -n '407,445p'   # plan_upgrade
git show 3786f49:src/groundtruth_kb/project/upgrade.py | sed -n '446,501p'   # execute_upgrade
git show 3786f49:src/groundtruth_kb/project/scaffold.py | sed -n '353,393p'  # _write_settings_json (12 hooks)
git show 3786f49:src/groundtruth_kb/project/scaffold.py | sed -n '292,298p'  # settings.local vs settings.json
git show 3786f49:src/groundtruth_kb/project/bootstrap.py | sed -n '19,28p'   # DEFAULT_PROJECT_GITIGNORE

# 2. Confirm template inventory count
git ls-files templates/ | wc -l
# expected: 55

# 3. Confirm rules gap 2.8
git ls-files templates/rules/
# expected: 8 files; _MANAGED_RULES has 5 of the 8
git show 3786f49:src/groundtruth_kb/project/upgrade.py | sed -n '45,51p'
```

The post-implementation report associated with this investigation
bridge verifies these same claims from git after the single commit
lands.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
