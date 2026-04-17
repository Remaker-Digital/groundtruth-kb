# GT-KB Managed Artifact Registry Review

**Verdict: NO-GO**
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-managed-artifact-registry-003.md`
**Prior review:** `bridge/gtkb-managed-artifact-registry-002.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target HEAD:** `82c5a85`

## Claim

The revision fixes the original high-risk count and schema problems in the
right direction: the registry now distinguishes `initial` from `managed`,
uses class-specific schemas, includes `tests/test_intake.py`, and expands
Gap 2.8 coverage to all three required bridge rules.

It is still not safe to implement as written because the proposed single
`profiles` field cannot represent current profile-specific lifecycle
semantics. Several artifacts are scaffolded for `local-only` but upgrade-
managed only for bridge profiles. Some artifacts are both scaffolded and
managed for `local-only`. The revised proposal's sample inventories omit
that distinction and would either drop local-only scaffold files or over-
manage local-only projects.

## Finding 1 - `profiles` is too coarse for current initial-vs-managed behavior

**Severity:** High

The revised proposal adds `initial: bool` and `managed: bool`, but keeps one
shared `profiles` list per artifact. Current behavior has profile asymmetry
between scaffold-time copying and upgrade-time repair.

Evidence in the checkout:

- `src/groundtruth_kb/project/scaffold.py:100-105` calls
  `_copy_base_templates(target)` for every profile before the bridge-profile
  branch.
- `src/groundtruth_kb/project/scaffold.py:184-187` copies every
  `templates/hooks/*.py` into `.claude/hooks/` in that base layer.
- `src/groundtruth_kb/project/upgrade.py:112-125` narrows local-only managed
  hooks to only `assertion-check.py` and `spec-classifier.py`.
- `src/groundtruth_kb/project/upgrade.py:128-133` narrows local-only managed
  rules to only `prime-builder.md`.

Source-backed runtime verification, run with `PYTHONPATH=src` against
HEAD `82c5a85`, confirms current scaffold behavior:

```text
local-only
hooks 14 ['assertion-check.py', 'bridge-compliance-gate.py', 'credential-scan.py', 'delib-search-gate.py', 'delib-search-tracker.py', 'destructive-gate.py', 'intake-classifier.py', 'kb-not-markdown.py', 'scanner-safe-writer.py', 'scheduler.py', 'session-health.py', 'session-start-governance.py', 'spec-before-code.py', 'spec-classifier.py']
rules 1 ['prime-builder.md']
settings.json False
dual-agent
hooks 14 [...]
rules 8 [...]
settings.json True
dual-agent-webapp
hooks 14 [...]
rules 8 [...]
settings.json True
```

Current local-only upgrade planning also repairs three files:

```text
local-only ['.claude/hooks/assertion-check.py', '.claude/hooks/spec-classifier.py', '.claude/rules/prime-builder.md']
```

The revised proposal's hook rows show
`profiles = ["dual-agent", "dual-agent-webapp"]` for both the 7 managed hooks
and the 7 initial-only hooks. If scaffold reads those records, local-only no
longer receives the hook files currently copied by the base scaffold. If the
rows are broadened to include `local-only`, then the single `managed=true`
flag would incorrectly make local-only repair bridge-only managed hooks such
as `intake-classifier.py`, `destructive-gate.py`,
`credential-scan.py`, `scheduler.py`, and `scanner-safe-writer.py`.

Rules have the same issue in smaller form. The proposal says all 8 rule
records have `profiles = ["dual-agent", "dual-agent-webapp"]`, but
`prime-builder.md` is currently scaffolded and upgrade-managed for
`local-only` (`scaffold.py:191-194`, `upgrade.py:128-133`).

**Risk/impact:** Implementing the registry as proposed breaks the stated
backward-compatibility intent. It either changes local-only scaffold output,
changes local-only upgrade behavior, or forces consumer-specific hardcoding
that recreates the split-manifest drift the registry is meant to eliminate.

**Required action:** Replace the single `profiles` field for lifecycle-aware
artifact classes with profile applicability per lifecycle, for example:

```toml
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["dual-agent", "dual-agent-webapp"]
```

For records whose lifecycle applicability is identical, both fields can carry
the same set. For non-file config records, use equivalent lifecycle-specific
profile fields or explicitly justify why one profile set is sufficient for
that class.

Minimum rows that must be represented correctly:

- `assertion-check.py`: initial all profiles, managed all profiles.
- `spec-classifier.py`: initial all profiles, managed all profiles.
- `intake-classifier.py`, `destructive-gate.py`, `credential-scan.py`,
  `scheduler.py`, `scanner-safe-writer.py`: initial all profiles, managed
  bridge profiles only.
- The 7 scaffold-only hooks: initial all profiles, managed no profiles.
- `prime-builder.md`: initial all profiles, managed all profiles.
- The other 7 rules: initial bridge profiles only, managed bridge profiles
  only.

Add registry tests that assert the current local-only and bridge-profile
scaffold/upgrade applicability matrices, not just total record counts.

## Finding 2 - Doctor semantics still need their own registry dimension or preservation rule

**Severity:** Medium

The revised proposal says `doctor.py` will read from the registry and also
says doctor reads `managed=true` records for checks. Current doctor semantics
do not equal the upgrade-managed file set.

Evidence:

- `_check_hooks` requires `assertion-check.py` and `spec-classifier.py` for
  every profile, and adds only `destructive-gate.py` and
  `credential-scan.py` for bridge profiles
  (`src/groundtruth_kb/project/doctor.py:308-331`).
- `scanner-safe-writer.py` is checked separately with settings and gitignore
  drift semantics (`src/groundtruth_kb/project/doctor.py:489-586`).
- `scheduler.py` is upgrade-managed (`src/groundtruth_kb/project/upgrade.py:42`)
  but is not currently doctor-required.

**Risk/impact:** If doctor switches from its current required-hook logic to
"all managed hooks are required", it changes doctor output and may introduce
new warnings for artifacts that were not previously doctor-required. If it
keeps custom filters outside the registry, the registry is not yet the single
authority for doctor behavior.

**Required action:** Define one of these explicitly before implementation:

1. Add doctor-specific metadata such as `doctor_required_profiles` or
   `doctor_check` to registry records, with tests preserving current doctor
   output for local-only and bridge profiles; or
2. Keep doctor-required hook/rule policy outside C1 and state exactly which
   doctor checks are migrated now versus deferred.

Do not implicitly equate `managed=true` with doctor-required.

## Direct Answers To Prime Questions

1. **Per-class schema completeness:** The class split is directionally good,
   but lifecycle profile applicability is missing. A single `profiles` field
   is not complete for file artifacts or settings registrations once scaffold
   and upgrade profile scopes differ.
2. **Hook partitioning:** The 7 managed / 7 initial-only partition is correct
   for bridge-profile upgrade semantics, but not by row as written because
   local-only currently receives all 14 hooks at scaffold time and only two
   of the 7 managed hooks at upgrade time.
3. **Settings-hook-registration managed flags:** Keeping only
   `scanner-safe-writer.py` as `managed=true` is acceptable for C1 if the
   other 11 settings registrations remain explicitly deferred to the
   settings-merge child bridge. Do not upgrade-manage
   `assertion-check.py` SessionStart in C1 without a settings merge policy.
4. **AST gate scope:** `src/groundtruth_kb/` is the right initial enforcement
   scope. Existing `tests/test_intake.py` imports must be migrated, but tests
   should not be broadly forbidden from containing `_MANAGED_*` fixture names
   unless a concrete drift risk appears.

## Decision

NO-GO until the proposal defines lifecycle-specific profile applicability and
spells out how doctor-required behavior is represented or preserved. After
that change, the overall single-registry direction should be approvable with
the existing Gap 2.8, settings-registration, test-intake, and AST-gate
conditions retained.
