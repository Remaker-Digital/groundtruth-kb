GO

# Loyal Opposition Review: Canonical Terminology Surface Implementation REVISED-3

Reviewed document: `bridge/gtkb-canonical-terminology-surface-implementation-007.md`
Verdict: GO with implementation conditions
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The post-GO revision is justified. GT-KB `main` now has the managed-artifact
registry from commit `e12aab3`, and the original `-005` Phase 4 hard-coded copy
plan would conflict with that architecture.

Option B is acceptable for implementation: add the canonical terminology
glossary and TOML config as managed `rule` file artifacts under
`.claude/rules/`. The current registry schema treats `rule` as a generic file
artifact class with `template_path` and `target_path`; it does not enforce a
Markdown-only extension. Scaffold and upgrade already copy registry file
artifacts by those fields, so no new schema class is required.

This GO is conditional because the move from `.claude/canonical-terminology.*`
to `.claude/rules/canonical-terminology.*` changes registry record counts,
breaks existing count/parity tests unless they are updated, and affects manual
template-copy documentation that currently copies only `rules/*.md`.

## Evidence

- `bridge/gtkb-canonical-terminology-surface-implementation-007.md:33`-`:44`
  evaluates Option B and recommends it.
- `bridge/gtkb-canonical-terminology-surface-implementation-007.md:50`-`:65`
  proposes two `class = "rule"` registry records:
  `rule.canonical-terminology` and `rule.canonical-terminology-config`.
- `bridge/gtkb-canonical-terminology-surface-implementation-007.md:80`-`:87`
  moves the target paths from `.claude/canonical-terminology.*` to
  `.claude/rules/canonical-terminology.*`.
- `groundtruth-kb@main:src/groundtruth_kb/project/managed_registry.py:36`-`:63`
  defines `rule` as a valid `FileArtifact` class.
- `groundtruth-kb@main:src/groundtruth_kb/project/managed_registry.py:142`
  requires only `template_path` and `target_path` for `rule` records; there is
  no `.md` extension invariant.
- `groundtruth-kb@main:src/groundtruth_kb/project/scaffold.py:196`-`:201`
  copies local-only `rule` artifacts by registry `target_path`.
- `groundtruth-kb@main:src/groundtruth_kb/project/scaffold.py:282`-`:287`
  copies dual-agent `rule` artifacts by registry `target_path`.
- `groundtruth-kb@main:src/groundtruth_kb/project/upgrade.py:97`,
  `:147`-`:157`, and `:348`-`:361` show upgrade planning and execution already
  map registry target paths back to template paths for file artifacts.
- `groundtruth-kb@main:tests/test_no_parallel_manifests.py:23`-`:30` and
  `:65`-`:81` enforce the no-parallel-`_MANAGED_*` rule, supporting the
  revision's rejection of another hard-coded list.

## Findings / Conditions

### P1 Condition - Update registry count and parity tests for the two new rule records

Option B changes the registry cardinality from 40 to 42 records and rule count
from 8 to 10. It also changes local-only scaffold/upgrade expectations because
both new records have `initial_profiles` and `managed_profiles` covering all
three profiles.

Current tests on `main` hard-code the old contract:

- `groundtruth-kb@main:tests/test_managed_registry.py:43`-`:57` expects 40
  records and 8 rules.
- `groundtruth-kb@main:tests/test_managed_registry.py:177`-`:185` expects
  local-only scaffold to have exactly one rule.
- `groundtruth-kb@main:tests/test_managed_registry.py:194`-`:202` expects
  dual-agent scaffold to have exactly 8 rules.
- `groundtruth-kb@main:tests/test_managed_registry.py:225` expects local-only
  upgrade-managed rules to equal only `.claude/rules/prime-builder.md`.
- `groundtruth-kb@main:tests/test_managed_registry.py:402` and `:407` expect
  `load_managed_artifacts()` lengths of 40 and 15.

Required action: update the registry tests to the new explicit contract:
42 total records, 10 rule records, and local-only scaffold/upgrade includes
`prime-builder.md`, `canonical-terminology.md`, and
`canonical-terminology.toml`. Keep `doctor_required_profiles = []` for both new
records unless the composite canonical-terminology doctor check intentionally
takes over simple presence enforcement.

### P1 Condition - Remove stale old-path implementation before post-implementation evidence

The inspected checkout currently contains pre-adaptation uncommitted work on
`feat/canonical-terminology-surface` that still uses the old
`.claude/canonical-terminology.*` paths and hard-coded scaffold/upgrade logic.
Examples from `git status --short --branch` and ripgrep include modified
`src/groundtruth_kb/project/scaffold.py`, `upgrade.py`, and `doctor.py`, plus
untracked `templates/canonical-terminology.md`,
`templates/canonical-terminology.toml`, and tests reading
`.claude/canonical-terminology.toml`.

Required action: the implementation branch used for the post-implementation
report must not carry those old-path artifacts forward. Post-implementation
evidence must show:

- source files live at `templates/rules/canonical-terminology.md` and
  `templates/rules/canonical-terminology.toml`;
- scaffolded files live at `.claude/rules/canonical-terminology.md` and
  `.claude/rules/canonical-terminology.toml`;
- no canonical terminology copy path remains in `scaffold.py` or `upgrade.py`
  outside the registry-driven artifact flow;
- references in `templates/CLAUDE.md`, `templates/MEMORY.md`,
  `templates/project/AGENTS.md`,
  `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`, and
  `templates/rules/deliberation-protocol.md` point to the new `.claude/rules/`
  paths.

### P2 Condition - Update manual template-copy documentation for the TOML file

The revision correctly carries forward the `-006` condition to update
`docs/reference/templates.md` and `templates/README.md`
(`bridge/gtkb-canonical-terminology-surface-implementation-007.md:103`).
However, the public bootstrap guide has a manual process-template copy command
that copies only Markdown rule files:

- `groundtruth-kb@main:docs/bootstrap.md:179` introduces manual template copy.
- `groundtruth-kb@main:docs/bootstrap.md:191` creates `.claude/rules/`.
- `groundtruth-kb@main:docs/bootstrap.md:193` copies
  `"$TEMPLATES/rules/"*.md` into `.claude/rules/`.

Under Option B, that command would omit
`templates/rules/canonical-terminology.toml`, so a manually bootstrapped project
could receive the glossary without the doctor config.

Required action: update `docs/bootstrap.md` or replace the manual copy snippet
with the registry/profile scaffold path. If the manual snippet remains, it must
copy the canonical terminology TOML as well as Markdown rule files.

### P2 Condition - Keep class-taxonomy documentation explicit

Using `class = "rule"` for a TOML config is a pragmatic registry reuse, but it
is semantically broader than the historical "rule markdown" wording in several
places. Current doctor `_check_rules()` enumerates only `*.md`
(`groundtruth-kb@main:src/groundtruth_kb/project/doctor.py:353`-`:363`), while
registry doctor-required rules come from `artifacts_for_doctor()`
(`groundtruth-kb@main:src/groundtruth_kb/project/doctor.py:505`). Because the
new TOML records set `doctor_required_profiles = []`, this is acceptable if the
new composite check owns their presence and validity.

Required action: make the implementation docs and tests state this explicitly:
the TOML is a managed `rule` artifact for lifecycle purposes, but canonical
terminology presence/validity is enforced by `_check_canonical_terminology()`,
not by generic `_check_rules()` Markdown enumeration.

## Carried-Forward Conditions From `-006`

These remain mandatory, with paths adjusted to Option B:

- Update generated `AGENTS.md` startup wording from `memory/MEMORY.md` to root
  `MEMORY.md`, with a scaffold test.
- Use real pytest paths in post-implementation evidence.
- File the post-implementation report as
  `bridge/gtkb-canonical-terminology-surface-implementation-009.md`.
- Add `.claude/rules/canonical-terminology.md` and
  `.claude/rules/canonical-terminology.toml` to template inventory docs.

## Required Post-Implementation Evidence

At minimum:

```text
python -m pytest tests/test_managed_registry.py -q --tb=short
python -m pytest tests/test_doctor_registry_parity.py -q --tb=short
python -m pytest tests/test_no_parallel_manifests.py -q --tb=short
python -m pytest tests/test_scaffold_project.py -q --tb=short
python -m pytest tests/test_upgrade.py -q --tb=short
python -m pytest tests/test_scaffold_smoke.py -q --tb=short
python -m pytest tests/test_doctor_canonical_terminology.py -q --tb=short
python -m mkdocs build --strict
python scripts/check_docs_cli_coverage.py
```

Also include grep evidence that no stale `.claude/canonical-terminology` path
remains outside explicit migration/history notes, and that scaffolded local-only,
dual-agent, and dual-agent-webapp projects receive the new `.claude/rules/`
artifacts.

## Verification Commands Run

```text
Get-Content -Path .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-canonical-terminology-surface-implementation' -Context 0,40
Get-Content -Path bridge/gtkb-canonical-terminology-surface-implementation-001.md
Get-Content -Path bridge/gtkb-canonical-terminology-surface-implementation-002.md
Get-Content -Path bridge/gtkb-canonical-terminology-surface-implementation-003.md
Get-Content -Path bridge/gtkb-canonical-terminology-surface-implementation-004.md
Get-Content -Path bridge/gtkb-canonical-terminology-surface-implementation-005.md
Get-Content -Path bridge/gtkb-canonical-terminology-surface-implementation-006.md
Get-Content -Path bridge/gtkb-canonical-terminology-surface-implementation-007.md
git status --short --branch
git log --oneline --decorate -n 8 --all
git branch --contains e12aab3 --all
git show --stat --oneline --decorate e12aab3
git show main:templates/managed-artifacts.toml
git show main:src/groundtruth_kb/project/managed_registry.py
git show main:src/groundtruth_kb/project/scaffold.py
git show main:src/groundtruth_kb/project/upgrade.py
git show main:src/groundtruth_kb/project/doctor.py
git show main:tests/test_managed_registry.py
git show main:tests/test_doctor_registry_parity.py
git show main:tests/test_no_parallel_manifests.py
git show main:docs/bootstrap.md
rg -n "class|ManagedArtifact|artifacts_for_scaffold|doctor_required_profiles|rule|canonical-terminology|_MANAGED_" src/groundtruth_kb/project templates tests docs mkdocs.yml -S
```

No product test suite was run because this is a proposal re-review, not
post-implementation verification.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
