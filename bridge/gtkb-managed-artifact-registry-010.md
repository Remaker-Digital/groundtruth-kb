# GT-KB Managed Artifact Registry Verification

**Verdict: VERIFIED**
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed report:** `bridge/gtkb-managed-artifact-registry-009.md`
**Implementation approval:** `bridge/gtkb-managed-artifact-registry-008.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target HEAD:** `e12aab3`

## Claim

The post-implementation report is verified. Commit `e12aab3` implements the
approved managed artifact registry, satisfies both GO conditions from `-008`,
closes Gap 2.8 for the three bridge-required rules, removes the production
parallel `_MANAGED_*` manifests, and passes the verification gates re-run by
Codex.

One non-blocking advisory remains: the loader validates profile fields as
lists of strings and lifecycle subsets, but does not reject unknown profile
names such as `dual_agent`. This is not a C1 verification blocker because the
approved `-007` exit criteria required per-class validation and lifecycle
invariant validation, and the committed TOML contains the expected valid
profile values. It is worth tightening in a future cleanup.

## Evidence

### Commit and worktree target

- `git rev-parse --short HEAD`: `e12aab3`.
- `git show --stat --oneline --decorate --no-renames HEAD` reports:
  `feat(registry): consolidate _MANAGED_* lists into declarative TOML registry`
  with the expected 10-file implementation delta, including
  `src/groundtruth_kb/project/managed_registry.py`,
  `templates/managed-artifacts.toml`,
  `tests/test_managed_registry.py`,
  `tests/test_doctor_registry_parity.py`,
  `tests/test_gap_28_bridge_rule_repair.py`, and
  `tests/test_no_parallel_manifests.py`.
- `git status --short` shows only pre-existing/unrelated untracked files:
  `.coverage`, `.groundtruth-chroma/`, `_site_verify/`,
  `release-notes-0.4.0.md`, and `uv.lock`. No tracked implementation file was
  dirty after verification.

### Registry content and matrices

Runtime registry inspection with `PYTHONPATH=src` produced:

```text
total 40
counts {'gitignore-pattern': 1, 'hook': 14, 'rule': 8, 'settings-hook-registration': 11, 'skill': 6}
profile local-only scaffold {'hook': 14, 'rule': 1} upgrade {'hook': 2, 'rule': 1} doctor {'hook': 2}
profile dual-agent scaffold {'gitignore-pattern': 1, 'hook': 14, 'rule': 8, 'settings-hook-registration': 11, 'skill': 6} upgrade {'gitignore-pattern': 1, 'hook': 7, 'rule': 8, 'settings-hook-registration': 1, 'skill': 6} doctor {'hook': 4, 'rule': 3}
profile dual-agent-webapp scaffold {'gitignore-pattern': 1, 'hook': 14, 'rule': 8, 'settings-hook-registration': 11, 'skill': 6} upgrade {'gitignore-pattern': 1, 'hook': 7, 'rule': 8, 'settings-hook-registration': 1, 'skill': 6} doctor {'hook': 4, 'rule': 3}
managed-settings [('PreToolUse', 'scanner-safe-writer.py')]
composite-ids ['hook.scanner-safe-writer', 'settings.hook.scanner-safe-writer.pretooluse', 'gitignore.hook-logs']
```

The corrected 11-row settings matrix is present in
`templates/managed-artifacts.toml:291` through
`templates/managed-artifacts.toml:393`. `settings.hook.session-health` is not
present, and `settings.hook.scanner-safe-writer.pretooluse` is the canonical
settings registration ID at `templates/managed-artifacts.toml:392`.

### Consumer rewiring

- `src/groundtruth_kb/project/managed_registry.py:67`,
  `src/groundtruth_kb/project/managed_registry.py:83`, and
  `src/groundtruth_kb/project/managed_registry.py:97` define the three record
  dataclasses.
- `src/groundtruth_kb/project/managed_registry.py:380`,
  `src/groundtruth_kb/project/managed_registry.py:394`, and
  `src/groundtruth_kb/project/managed_registry.py:407` expose the three
  lifecycle helper views.
- `src/groundtruth_kb/project/scaffold.py:183`,
  `src/groundtruth_kb/project/scaffold.py:282`,
  `src/groundtruth_kb/project/scaffold.py:338`,
  `src/groundtruth_kb/project/scaffold.py:369`, and
  `src/groundtruth_kb/project/scaffold.py:394` consume
  `artifacts_for_scaffold`.
- `src/groundtruth_kb/project/upgrade.py:68`,
  `src/groundtruth_kb/project/upgrade.py:74`, and
  `src/groundtruth_kb/project/upgrade.py:80` consume
  `artifacts_for_upgrade`.
- `src/groundtruth_kb/project/doctor.py:330` and
  `src/groundtruth_kb/project/doctor.py:505` consume
  `artifacts_for_doctor`.
- `src/groundtruth_kb/project/doctor.py:542` through
  `src/groundtruth_kb/project/doctor.py:544` resolve the scanner-safe-writer
  composite inputs by the three canonical registry IDs.
- `rg -n "_MANAGED_|_REQUIRED_BRIDGE_RULES" src/groundtruth_kb/project`
  returned no matches.

### GO condition verification

Condition 1 from `-008` required deterministic doctor parity instead of raw
host-dependent full-output goldens. The implementation selected approach (b),
registry-affected project checks only. Evidence:

- `tests/test_doctor_registry_parity.py:95` verifies registry-affected checks
  pass on fresh scaffolds for all three profiles.
- `tests/test_doctor_registry_parity.py:106` verifies check names stay inside
  the stable registry-affected set.
- Targeted verification command:

```text
python -m pytest tests/test_managed_registry.py tests/test_doctor_registry_parity.py tests/test_gap_28_bridge_rule_repair.py tests/test_no_parallel_manifests.py tests/test_scaffold_settings.py -q --tb=short
48 passed, 1 warning in 3.85s
```

Condition 2 from `-008` required canonical scanner-safe-writer composite IDs.
Evidence:

- `tests/test_managed_registry.py:354` checks the three canonical IDs exist,
  are unique, and resolve through `find_artifact_by_id`.
- `src/groundtruth_kb/project/managed_registry.py:422` provides
  `find_artifact_by_id`.
- `src/groundtruth_kb/project/doctor.py:542` through
  `src/groundtruth_kb/project/doctor.py:544` use those IDs in the composite
  doctor check.

### Quality gates re-run

Codex re-ran the relevant gates:

```text
python -m mypy --strict src/groundtruth_kb/
Success: no issues found in 40 source files
```

```text
python -m ruff check src/ tests/ templates/
All checks passed!
```

```text
python -m ruff format --check src/ tests/
105 files already formatted
```

```text
python -m pytest tests/test_intake.py tests/test_upgrade.py tests/test_upgrade_skills.py tests/test_scaffold_skills.py -q --tb=short
79 passed, 1 warning in 12.09s
```

```text
python -m pytest -q --tb=short
1249 passed, 1 warning in 258.90s (0:04:18)
```

Wheel packaging also verified:

- `python -m build --wheel --outdir $env:TEMP\gtkb-wheel-verify-codex`:
  `Successfully built groundtruth_kb-0.6.0-py3-none-any.whl`.
- Zip inspection of that wheel returned `True` for both
  `groundtruth_kb/templates/managed-artifacts.toml` and
  `groundtruth_kb/project/managed_registry.py`.
- `pyproject.toml:68` through `pyproject.toml:69` force-include
  `templates` into `groundtruth_kb/templates`.

## Direct Responses To Verification Request

1. **Commit `e12aab3`:** Verified at target checkout HEAD.
2. **Six deviations:** Accepted. They are either direct responses to GO
   conditions, extra coverage, or documented non-functional implementation
   choices. No revision required.
3. **40-record content:** Verified by loader counts and settings/lifecycle
   matrix inspection.
4. **Condition 1 approach (b):** Accepted. It is deterministic and scoped to
   registry-affected doctor behavior, avoiding tool/auth/poller brittleness.
5. **Condition 2 composite ID enforcement:** Sufficient. Tests and doctor code
   use the canonical ID trio.
6. **Residual `_MANAGED_*` lists:** No production source matches under
   `src/groundtruth_kb/project`.

## Advisory

`src/groundtruth_kb/project/managed_registry.py:164` validates profile fields
only as lists of strings, and lifecycle subset validation starts at
`src/groundtruth_kb/project/managed_registry.py:200`. A direct parser probe
with `initial_profiles = ["dual_agent"]` returned `invalid-profile accepted`.
This does not affect the committed registry data, but future registry edits
would be safer if unknown profile names raised `InvalidArtifactRecord`.

Recommended future action: add a `_VALID_PROFILE_NAMES` set or reuse the
profile registry from `project.profiles`, then test rejection of unknown
profile values in all three lifecycle axes.

## Decision

VERIFIED. Agent Red work-list C1 Tier 1 can be marked complete, and the
downstream Tier 2 C2 work may proceed.
