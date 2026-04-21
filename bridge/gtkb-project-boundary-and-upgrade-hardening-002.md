GO

# GT-KB Project Boundary and Upgrade Hardening - Codex Review

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-project-boundary-and-upgrade-hardening-001.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target HEAD:** `cf29738`
**Agent Red checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
**Observed Agent Red HEAD:** `aa6a5fe5`

## Claim

The proposed scope is correctly aimed at the current product risk: GT-KB's
scaffold/upgrade contract is not yet strong enough to prove clean upgrades for
existing adopters, and Agent Red is not yet cleanly retrofit-able as an adopter.

GO is granted for the scope, with implementation conditions below. This GO
does not authorize direct Agent Red cleanup beyond read-only dogfood commands
and a generated classification report.

## Evidence

### The proposal's core concerns are real

- Fresh scaffold defaults still ignore `groundtruth.db`: `groundtruth-kb\src\groundtruth_kb\bootstrap.py:19-28` includes `groundtruth.db` in `DEFAULT_PROJECT_GITIGNORE`, and `groundtruth-kb\.gitignore:3` ignores the product repo's own `groundtruth.db`.
- `gt project init` still requires an empty target: `groundtruth-kb\src\groundtruth_kb\project\scaffold.py:67-72` calls `_validate_target()`, and `groundtruth-kb\src\groundtruth_kb\bootstrap.py:75-79` rejects non-empty directories.
- The upgrade CLI has no rollback option: `groundtruth-kb\src\groundtruth_kb\cli.py:682-686` exposes only `--dry-run/--apply`, `--force`, and `--dir`.
- Current upgrade execution mutates files in place, uses `.bak` backups for file overwrites, appends/rewrites config files directly, and updates the manifest at the end: `groundtruth-kb\src\groundtruth_kb\project\upgrade.py:318-371`, `:374-426`, and `:429-456`.
- The registry has no ownership field and no workflow targets: `templates/managed-artifacts.toml` currently parses to 40 records, `ownership field count 0`, and `workflow targets []`.
- CI workflows and integration files are scaffolded outside the upgrade registry: `groundtruth-kb\src\groundtruth_kb\project\scaffold.py:480-493` writes `.github/workflows/*.yml`; `:842-872` writes `.github/dependabot.yml` and `.coderabbitai.yaml`.
- Docs are stale relative to the registry: `groundtruth-kb\docs\reference\templates.md:3` says 30 template files, while `templates/managed-artifacts.toml:5` and the TOML parse both show 40 current registry records.

### Agent Red remains a hard retrofit case

- Agent Red tracks `groundtruth.db`: `git ls-files groundtruth.db requirements-local.txt requirements-test.txt` returned `groundtruth.db`.
- Agent Red still pins GT-KB `v0.2.1`: `requirements-local.txt:17` and `requirements-test.txt:49` both point at `groundtruth-kb.git@v0.2.1`, while the inspected GT-KB checkout reports `__version__ = "0.6.0"` at `groundtruth-kb\src\groundtruth_kb\__init__.py:16`.
- Agent Red does not currently have `groundtruth.toml`; `rg -n "\[project\]|scaffold_version|profile|project_name|groundtruth" groundtruth.toml .gitignore` reported `groundtruth.toml` missing and only backup/chroma DB ignores at `.gitignore:109-111`.
- Current `gt project upgrade --dry-run --dir Agent Red` cannot classify adopter files. It returns only:

```text
[SKIP] groundtruth.toml - No [project] manifest found - run `gt project init` first
1 action(s). Run with --apply to execute.
```

- Current `gt project doctor --dir Agent Red` fails on the same missing manifest:

```text
[FAIL] groundtruth.toml not found - run `gt project init` first
Overall: [FAIL] FAIL
```

This supports the proposal's retrofit path. It also means the Agent Red dogfood
step must start with a retrofit/classification dry-run, not a plain current
upgrade dry-run.

## Conditions

### Condition 1 - Make rollback receipts restore-capable

**Severity if ignored:** High

The proposal's receipt shape at `bridge/gtkb-project-boundary-and-upgrade-hardening-001.md:58-63`
records `{file_path, pre_hash, post_hash, action}`. Hashes are good audit
metadata, but they are not sufficient to implement `gt project upgrade
--rollback <receipt>` by themselves.

Required implementation action:

- Store or reference restorable pre-change bytes for every changed file.
- Include structured before/after state for JSON/TOML merges such as `.claude/settings.json`.
- Include delete/add semantics, not just hashes.
- Test rollback after file copy, settings merge, gitignore append, workflow update, and manifest update.

### Condition 2 - Ownership must cover generated and non-registry artifacts

**Severity if ignored:** High

Extending `templates/managed-artifacts.toml` with `ownership` is correct for
the 40 registry records, but the requested matrix says "every file/directory"
at `bridge/gtkb-project-boundary-and-upgrade-hardening-001.md:45-54`. Current
project scaffolding also creates/generated files outside the registry:
`groundtruth.toml`, `groundtruth.db`, `.gitignore`, `pyproject-sections.toml`,
`src/tasks.py`, webapp stubs, CI workflows, integration configs, and bridge
runtime directories.

Required implementation action:

- Add `ownership` to registry rows that already exist.
- Add a sibling machine-readable ownership map for generated files, globs, and
  adopter-only directories that do not belong in the managed-artifact registry.
- Ensure doctor and upgrade consume the same machine-readable ownership source
  used to generate `docs/reference/artifact-ownership-matrix.md`.
- Do not treat "GT-KB managed" as silent overwrite permission. Managed files
  still need preflight, receipt, rollback, and an explicit force/merge policy
  when local content differs.

### Condition 3 - Include or explicitly retire `bootstrap-desktop`

**Severity if ignored:** Medium

The proposal and the current docs cite bootstrap behavior as evidence, and
`docs/reference/templates.md:3-4` says templates are used by both
`gt project init` and `gt bootstrap-desktop`. But `bootstrap_desktop_project()`
still has a separate copy path: `groundtruth-kb\src\groundtruth_kb\bootstrap.py:134-164`
glob-copies hooks/rules and root CI templates rather than using the current
project registry/tier logic.

Required implementation action:

- Either bring `bootstrap-desktop` under the same ownership/registry/parity
  contract, or explicitly deprecate/document it as outside the hardened
  project lifecycle.
- Add tests for whichever decision is made.

### Condition 4 - Dogfood Agent Red as classification-only until owner approval

**Severity if ignored:** High

The proposal correctly keeps Agent Red cleanup out of scope at
`bridge/gtkb-project-boundary-and-upgrade-hardening-001.md:107-112`. Preserve
that boundary.

Required implementation action:

- The Agent Red dogfood step must not modify Agent Red files.
- Produce a report that classifies Agent Red files as GT-KB managed,
  GT-KB scaffolded/adopter-owned, shared structured data, adopter-owned, or
  legacy exception.
- Treat `groundtruth.db` as an unresolved owner decision, not as an implicit
  product default change.
- A follow-on Agent Red bridge is required before changing `groundtruth.db`
  tracking or bumping `requirements-local.txt` / `requirements-test.txt`.

### Condition 5 - Source docs parity from current registry truth

**Severity if ignored:** Medium

The proposal says the registry has 42 records at
`bridge/gtkb-project-boundary-and-upgrade-hardening-001.md:16`, but the
inspected checkout currently has 40 records:

```text
40
{'hook': 14, 'rule': 8, 'skill': 6, 'settings-hook-registration': 11, 'gitignore-pattern': 1}
```

Required implementation action:

- Generate/check docs from the live registry and ownership map, not from a
  hard-coded expected count.
- Add a CI gate for the docs parity script proposed at
  `bridge/gtkb-project-boundary-and-upgrade-hardening-001.md:87-91`.

## Direct Answers To Codex Questions

1. `.gt-upgrade-staging/` is acceptable if it is ignored/cleaned and not
   relied on as the only rollback source. Prefer filesystem staging over a git
   staging branch because not every adopter repo can be assumed to have clean
   git state or even git initialized.
2. Use both: extend `managed-artifacts.toml` for current registry records, and
   add a sibling ownership map for generated/scaffolded/adopter globs not
   represented by registry rows.
3. Extend `tests/test_upgrade.py` for planner/executor rollback and settings
   merge cases, and add a focused git/preflight test module for dirty-tree
   refusal. Keep docs parity tests separate so failures point at the right
   subsystem.
4. Agent Red retrofit is feasible only as a dry-run classification first.
   Current `doctor` and `upgrade --dry-run` cannot classify it because
   `groundtruth.toml` is absent. Do not grandfather it out of the product
   contract, but do not live-retrofit it in this bridge.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-001.md
git rev-parse --short HEAD
git ls-files groundtruth.db requirements-local.txt requirements-test.txt
git status --short -- groundtruth.db requirements-local.txt requirements-test.txt
rg -n "\[project\]|scaffold_version|profile|project_name|groundtruth" groundtruth.toml .gitignore
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short
rg -n "project init|upgrade|retrofit|dry-run|force|rollback|scaffold_version" src/groundtruth_kb/cli.py src/groundtruth_kb/project tests
python -m pytest tests/test_upgrade.py tests/test_managed_registry.py tests/test_scaffold_ci_tiers.py -q --tb=short
python -m groundtruth_kb project upgrade --dry-run --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
python -m groundtruth_kb project doctor --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
```

Test result:

```text
74 passed, 1 warning in 10.70s
```

## Decision Needed From Owner

Yes, but not before implementation starts: the `groundtruth.db` tracking default
still needs an owner decision before any Agent Red follow-on cleanup. Product
implementation can proceed by preserving the current fresh-scaffold default and
classifying Agent Red's tracked DB as a legacy/adopter exception until Mike
decides otherwise.
