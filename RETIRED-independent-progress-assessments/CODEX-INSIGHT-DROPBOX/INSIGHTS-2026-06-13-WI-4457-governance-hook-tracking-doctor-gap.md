Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001
WIs: WI-4457, WI-4449

# WI-4457 Governance Hook Tracking Doctor Gap

Role: Loyal Opposition
Harness: Codex A
Date: 2026-06-13

## Claim

WI-4457 remains a valid P0 doctor-gap follow-up. The current workspace has no
untracked `.claude/hooks/*.py` files, and every hook path registered in
`.claude/settings.json` currently exists and is tracked. The residual risk is
that `gt project doctor` still does not directly test the git-index tracking
invariant for registered governance hook scripts, so a recurrence of the
WI-4449 class can be missed until a fresh clone or another session hits it.

## Evidence

- `bridge/gtkb-commit-untracked-governance-hooks-002.md:43` and
  `bridge/gtkb-commit-untracked-governance-hooks-002.md:86` record the emergency
  repair evidence for WI-4449: missing registered hook targets became zero and
  `git ls-files '.claude/hooks/*.py'` increased by six tracked files.
- `.gitignore:265` through `.gitignore:269` explicitly re-include
  `.claude/hooks/*.py`, so untracked hook scripts are meant to be visible to
  git rather than silently ignored.
- `.claude/settings.json:10`, `:14`, `:18`, `:22`, `:26`, `:30`, `:40`, and
  `:50` show representative registered governance hook commands.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1219` through `:1254`
  implement `_check_hooks()` as a presence check over `hooks_dir.glob("*.py")`
  plus managed required-hook filenames. It does not ask git whether those files
  are tracked.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2008` through `:2115`
  check the scanner-safe-writer file, registration, and log-ignore pattern.
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2118` through `:2142`
  check only two safety-gate registrations.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2663` through `:2727`
  generalize hook registration drift as "paired hook file exists and command is
  registered"; it still does not validate `git ls-files` tracking.
- Live census command returned every registered `.claude/hooks/*.py` path as
  `exists: true` and `tracked: true`; `git status --porcelain=v1
  --untracked-files=all -- .claude/hooks` returned no rows.
- `python -m groundtruth_kb.cli project doctor --json` does surface hook
  presence, managed-artifact drift, registration drift, and safety-gate
  registration findings, but there is no check named for registered-hook git
  tracking or untracked governance hooks.
- Deliberation search for `WI-4457 untracked governance hook scripts doctor`
  returned no relevant prior deliberations.

## Finding

Severity: P1 governance drift, under a P0 backlog row because the defect class
can remove governance hooks from fresh clones while leaving the local workspace
apparently functional.

The current checks are necessary but not sufficient. A hook can exist on disk
and be registered in `.claude/settings.json` while still being absent from the
git index. That was the WI-4449 incident class. `_check_hooks()` would pass the
presence side, and `_check_settings_hook_registration_drift()` would pass the
registration side, because neither check verifies the tracked side. The
`.gitignore` negation makes this mechanically testable without guessing:
registered hook files should appear in `git ls-files`.

## Recommended Action

Prime Builder should file a narrow bridge proposal for an additive doctor check:

1. Parse `.claude/settings.json` hook command strings for in-root
   `.claude/hooks/*.py` script references.
2. For each referenced hook script, verify file existence and membership in
   `git ls-files`.
3. Warn for any registered hook that exists but is not tracked.
4. Warn for any untracked `.claude/hooks/*.py` path, even if not registered,
   because `.gitignore` intends those files to be visible tracking candidates.
5. Add focused tests with temporary git repositories that exercise:
   registered+tracked pass, registered+untracked warning, unregistered+untracked
   warning, missing registered hook fail or warning matching existing doctor
   severity conventions.

Rejected alternative: relying on managed-artifact drift is not enough. That
path detects managed template drift and selected registration records, but
WI-4449 was a git-index publication failure. The doctor needs a git-index
predicate, not only an artifact-registry predicate.

## Prime Builder Context

Objective: make `gt project doctor` surface untracked registered governance
hook scripts before they become fresh-clone or cross-session failures.

Preconditions: preserve the existing hook-presence, managed-artifact, and
registration checks; this should be an additive WARN-level check unless a
proposal justifies fail severity.

Evidence paths:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_fab07_doctor_false_signals.py`
- `platform_tests/scripts/test_single_harness_doctor_check_upgrade.py`
- `.claude/settings.json`
- `.gitignore`
- `bridge/gtkb-commit-untracked-governance-hooks-002.md`

File touchpoints expected:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- a focused doctor test module under `platform_tests/scripts/`

Verification steps:

- Existing targeted doctor tests should keep passing.
- New tests should fail before the implementation and pass after it.
- A live `gt project doctor --json` run should include a clean PASS message for
  registered hook tracking when all current hook scripts are tracked.

Rollback notes: the new check can be removed cleanly from `run_doctor()` and
its tests if it produces excessive false positives; it should not alter hook
runtime behavior.

Open decisions: none for the advisory. Formal implementation still requires a
normal Prime Builder proposal, Loyal Opposition GO, and implementation-start
authorization.

## Verification Performed

- `python -m groundtruth_kb.cli harness roles` confirmed Codex A is currently
  Loyal Opposition.
- `python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition
  --format json` reported `actionable: []`.
- `python -m groundtruth_kb.cli backlog show WI-4457 --json` confirmed the live
  backlog row is open, P0, unapproved, and depends on WI-4449.
- `python -m pytest platform_tests\scripts\test_fab07_doctor_false_signals.py
  platform_tests\scripts\test_single_harness_doctor_check_upgrade.py
  platform_tests\scripts\test_check_canonical_terminology_doctor_integration.py
  -q --tb=short` passed: 24 tests passed.
- `git status --short` returned no source changes before this report was
  authored.
