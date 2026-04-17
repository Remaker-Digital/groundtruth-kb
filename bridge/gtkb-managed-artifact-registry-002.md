# GT-KB Managed Artifact Registry Review

**Verdict: NO-GO**
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-managed-artifact-registry-001.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target HEAD:** `82c5a85`

## Claim

The single-registry direction is sound, and TOML is acceptable for C1 because
`groundtruth-kb` requires Python `>=3.11` and can use stdlib `tomllib`
(`pyproject.toml:11`, `pyproject.toml:76`). However, the proposal is not yet
safe to implement as written. It under-specifies scaffold-only artifacts and
non-file registry classes, and it conflicts with the current test suite.

## Finding 1 - Scaffold-only hook artifacts are not represented

**Severity:** High

The proposal says the registry will be populated from `_MANAGED_HOOKS` (7
entries) and that `scaffold.py` will read from the registry instead of its
current copy behavior. Current `scaffold.py` does not copy only managed hooks:
it copies every `templates/hooks/*.py` into `.claude/hooks/`
(`src/groundtruth_kb/project/scaffold.py:186`) and the dual-agent path also
copies missing hook templates (`src/groundtruth_kb/project/scaffold.py:278`).

Runtime verification against the checkout:

```text
scaffolded hook count: 14
managed hook count: 7
scaffolded-not-managed: bridge-compliance-gate.py, delib-search-gate.py, delib-search-tracker.py, kb-not-markdown.py, session-health.py, session-start-governance.py, spec-before-code.py
```

Several of those scaffolded-but-not-managed hooks are registered in
`.claude/settings.json` by `_write_settings_json`
(`src/groundtruth_kb/project/scaffold.py:370`-`381`). Runtime verification:

```text
bridge-compliance-gate.py registered: True exists: True
delib-search-gate.py registered: True exists: True
delib-search-tracker.py registered: True exists: True
kb-not-markdown.py registered: True exists: True
session-start-governance.py registered: True exists: True
spec-before-code.py registered: True exists: True
```

If implementation literally refactors scaffold hook copying to a registry
populated only from `_MANAGED_HOOKS`, fresh scaffolds can lose registered hook
files. That violates the proposal's strict backward-compatibility claim.

**Required action:** Define the registry as covering both `initial` scaffold
copies and `managed` upgrade-repaired files, including `initial=true,
managed=false` records for scaffold-only hook files; or explicitly keep the
current scaffold glob copy out of the C1 refactor. Add a regression test that
every hook command registered by a fresh dual-agent scaffold has a
corresponding hook file on disk.

## Finding 2 - Non-file artifact schema is internally inconsistent

**Severity:** High

The proposal's "exact" TOML schema requires `template_path` and `target_path`,
but the proposed class enum includes `settings-hook-registration` and
`gitignore-pattern`. Those current records are not template-file copies:
`_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` stores `(hook_filename,
bridge_profile_only)` (`src/groundtruth_kb/project/upgrade.py:70`), and
`_MANAGED_GITIGNORE_PATTERNS` stores `(pattern, comment, bridge_profile_only)`
(`src/groundtruth_kb/project/upgrade.py:78`). Their planners consume payloads
and comments, not template paths (`src/groundtruth_kb/project/upgrade.py:355`,
`src/groundtruth_kb/project/upgrade.py:391`).

There is also a modeling conflict: the example hook record uses
`settings_pretooluse_hook = true`, while the class enum says
`settings-hook-registration` is its own class. That distinction matters
because current settings registration has event-class semantics in scaffold
(`SessionStart`, `UserPromptSubmit`, `PostToolUse`, `PreToolUse` at
`src/groundtruth_kb/project/scaffold.py:370`-`381`) and only one
upgrade-managed `PreToolUse` registration today.

**Required action:** Replace the single "exact" schema with class-specific
schemas and validation. File artifacts should require `template_path` and
`target_path`; settings-registration artifacts should require event, hook
filename or command, target settings path, and profiles; gitignore artifacts
should require pattern, comment, and profiles. The registry tests must validate
required/forbidden keys by class.

## Finding 3 - Deleting `_MANAGED_*` constants conflicts with the current tests

**Severity:** Medium

The proposal requires deleting the five `_MANAGED_*` module-level lists and
adds a CI gate to prevent new `_MANAGED_*` lists. The current suite still
imports `_MANAGED_HOOKS` from `groundtruth_kb.project.upgrade` in
`tests/test_intake.py:27`, with assertions at `tests/test_intake.py:535`,
`tests/test_intake.py:542`, and `tests/test_intake.py:549`.

That conflicts with the exit criteria that the full suite remains clean. It
also conflicts with the stated "test changes outside the 3 regression tests +
1 CI gate" scope unless `tests/test_intake.py` is explicitly included.

**Required action:** Add `tests/test_intake.py` to the expected test updates
and migrate those assertions to the registry query API, or provide a clearly
derived compatibility view that does not trip the new AST gate. The latter is
less preferable because it keeps the old private import surface alive.

## Finding 4 - Gap 2.8 regression coverage is too narrow

**Severity:** Medium

The live defect is real. Current runtime verification shows that deleting
`bridge-essential.md` from a fresh dual-agent scaffold produces no
`plan_upgrade` add action and `execute_upgrade` does not restore it:

```text
scaffolded bridge-essential exists: True
bridge-essential actions: []
restored after execute: False
```

The proposal's single delete-and-repair test is necessary, but it should cover
all three missing required bridge rules because doctor requires all three:
`file-bridge-protocol.md`, `bridge-essential.md`, and
`deliberation-protocol.md` (`src/groundtruth_kb/project/doctor.py:482`,
`src/groundtruth_kb/project/doctor.py:774`).

**Required action:** Add an adopter-scenario regression that scaffolds a
dual-agent project, deletes each of the three required bridge rules, verifies
doctor reports the missing rule, verifies `plan_upgrade` emits an `add`, runs
`execute_upgrade`, and verifies doctor no longer reports that rule missing.

## Finding 5 - Proposal baseline is stale

**Severity:** Low

The proposal cites target HEAD `33f1c5a`, but the inspected checkout is
`82c5a85`. The core defect still reproduces at `82c5a85`, so this does not
invalidate the direction, but it does make the implementation estimate and
line references stale.

**Required action:** Re-anchor the revised proposal to the current
`groundtruth-kb` HEAD before implementation.

## Direct answers to GO request

1. **TOML format:** Acceptable, provided the implementation uses `tomllib` for
   parsing and does not introduce a new runtime dependency. Do not require a
   generic TOML dump dependency just for a roundtrip test.
2. **Discriminator `class`:** The enum is close, but the schema must be
   class-specific. Do not add future `workflow` at C1 unless C1 actually
   manages workflow artifacts.
3. **Public API preservation:** Keep `load_managed_artifacts()` internal under
   `groundtruth_kb.project.managed_registry` for C1. A public API can be a
   later proposal once there is a demonstrated downstream consumer.
4. **Gap 2.8 evidence:** Single-file delete/repair is not sufficient; cover
   all three doctor-required bridge rules and doctor-before/after behavior.
5. **CI gate scope:** Good idea, but it should scan `src/` for module-level
   `Assign`/`AnnAssign` constants named `_MANAGED_*` whose values are list,
   tuple, set, or dict literals outside `managed_registry.py`. Tests should be
   updated away from old private constants rather than exempted broadly.

## Decision

NO-GO until the revised proposal resolves the scaffold-only artifact model,
the class-specific TOML schema, and the current test-suite conflict.
