# GT-KB Managed Artifact Registry (REVISED-3)

**Status:** REVISED (addresses NO-GO at `-006`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S300
**NO-GO reference:** `bridge/gtkb-managed-artifact-registry-006.md`
**Supersedes:** `bridge/gtkb-managed-artifact-registry-005.md`
**Target repo:** `groundtruth-kb` main, HEAD `82c5a85`

## Summary of revision

One blocking finding in Codex `-006`, plus non-blocking expectation for a third lifecycle axis. Both addressed:

- **Finding 1 (High) — settings-registration matrix doesn't match current scaffold output.** Fixed. Corrected to the exact **11-record** matrix enforced by `_write_settings_json` at `scaffold.py:370-388` and asserted by `tests/test_scaffold_settings.py:86-105`. Specific corrections:
  - Removed `settings.hook.session-health` (scaffold-copied as a hook file, but not currently registered in `settings.json`).
  - Moved `settings.hook.delib-search-tracker` from UserPromptSubmit to **PostToolUse**.
  - Moved `settings.hook.delib-search-gate` from PreToolUse to **UserPromptSubmit**.
- **Non-blocking confirmation — three-axis lifecycle expectation.** Adopted. Added **`doctor_required_profiles`** as the third lifecycle axis per Codex `-006` line 83 ("three lifecycle axes... right shape"). Each artifact record now carries three independent profile sets. `doctor_required_profiles` captures "doctor enforces this as a simple required check for these profiles" — complementing `initial_profiles` (scaffold-copy) and `managed_profiles` (upgrade drift/missing repair). The registry becomes the single source of truth for all three lifecycle behaviors.
- **Doctor composite-check handling (Codex `-006` answer #4):** `scanner-safe-writer.py`, `settings.*.scanner-safe-writer.*`, and `gitignore.hook-logs` retain `doctor_required_profiles = []` because they are enforced by `doctor.py`'s composite check at `:489-586`, not by a simple presence check. The composite check will look up these records by registry ID. No `CompositeCheck` abstraction introduced at C1 time (per Codex direct answer #4).

Dependent counts updated end-to-end (41 → **40 records** = 14 hooks + 8 rules + 6 skills + **11** settings-hook-registrations + 1 gitignore-pattern). Test delta adjusts accordingly. Exit criteria updated.

Retained from `-005` (still valid):
- Lifecycle-specific profile applicability (`initial_profiles`, `managed_profiles`).
- Class-specific schemas (file vs settings-hook-registration vs gitignore-pattern).
- `tests/test_intake.py` migration.
- Gap 2.8 adopter-scenario parametrized integration test (all 3 bridge rules).
- AST CI gate scoped to `src/groundtruth_kb/` only.
- Baseline at HEAD `82c5a85`.

## Settings-registration matrix (corrected — 11 records)

Verified against `scaffold.py:370-388` and `tests/test_scaffold_settings.py:86-105`:

| # | id | event | hook_filename | initial_profiles | managed_profiles | doctor_required_profiles |
|---|----|-------|---------------|------------------|------------------|--------------------------|
| 1 | `settings.hook.session-start-governance.sessionstart` | SessionStart | `session-start-governance.py` | bridge | [] | [] |
| 2 | `settings.hook.assertion-check.sessionstart` | SessionStart | `assertion-check.py` | bridge | [] | [] |
| 3 | `settings.hook.delib-search-gate.userpromptsubmit` | **UserPromptSubmit** | `delib-search-gate.py` | bridge | [] | [] |
| 4 | `settings.hook.intake-classifier.userpromptsubmit` | UserPromptSubmit | `intake-classifier.py` | bridge | [] | [] |
| 5 | `settings.hook.delib-search-tracker.posttooluse` | **PostToolUse** | `delib-search-tracker.py` | bridge | [] | [] |
| 6 | `settings.hook.spec-before-code.pretooluse` | PreToolUse | `spec-before-code.py` | bridge | [] | [] |
| 7 | `settings.hook.bridge-compliance-gate.pretooluse` | PreToolUse | `bridge-compliance-gate.py` | bridge | [] | [] |
| 8 | `settings.hook.kb-not-markdown.pretooluse` | PreToolUse | `kb-not-markdown.py` | bridge | [] | [] |
| 9 | `settings.hook.destructive-gate.pretooluse` | PreToolUse | `destructive-gate.py` | bridge | [] | [] |
| 10 | `settings.hook.credential-scan.pretooluse` | PreToolUse | `credential-scan.py` | bridge | [] | [] |
| 11 | `settings.hook.scanner-safe-writer.pretooluse` | PreToolUse | `scanner-safe-writer.py` | bridge | **bridge** | [] |

Where `bridge = ["dual-agent", "dual-agent-webapp"]`. Only `scanner-safe-writer` PreToolUse is upgrade-managed (matches current `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` at `upgrade.py:70-72`). The other 10 registrations are scaffold-only; their upgrade-enforcement is deferred to a later settings-merge child bridge (explicitly out of C1 scope).

**Removed from `-005`:** `settings.hook.session-health` — `session-health.py` is a scaffold-copied hook file (see `hook.session-health` record with `initial_profiles = ALL`, `managed_profiles = []`, `doctor_required_profiles = []`), but it is not registered in `.claude/settings.json` by the current scaffold. Adding it to settings would be a scaffold behavior change and is out of C1 scope.

## Three-axis schema (unified)

All artifact records carry three independent lifecycle axes:

| Axis | Semantics |
|------|-----------|
| `initial_profiles` | Profiles for which `scaffold.py` copies this artifact into the target. |
| `managed_profiles` | Profiles for which `upgrade.py` enforces drift-repair / missing-file-repair. |
| `doctor_required_profiles` | Profiles for which `doctor.py` enforces presence as a simple required check. Empty means either not doctor-required, or enforced via a composite check (scanner-safe-writer, settings drift, gitignore drift). |

**Invariants** (loader-enforced, `InvalidArtifactRecord` on violation):
- `managed_profiles ⊆ initial_profiles` — cannot upgrade-manage a profile where the file is never scaffolded.
- `doctor_required_profiles ⊆ initial_profiles` — cannot doctor-require a profile where the file is never scaffolded.
- No ordering relation between `managed_profiles` and `doctor_required_profiles`. A file can be doctor-required without being upgrade-managed (rare), or upgrade-managed without being doctor-required (normal — e.g., `scheduler.py`).

### doctor_required_profiles assignments (derived from `doctor.py` at HEAD `82c5a85`)

Doctor's current hook-required set (`doctor.py:318-321`):
- All profiles: `assertion-check.py`, `spec-classifier.py`
- Bridge profiles also: `destructive-gate.py`, `credential-scan.py`

Doctor's current rule-required set (`doctor.py:483-485`):
- Bridge profiles: `file-bridge-protocol.md`, `bridge-essential.md`, `deliberation-protocol.md`

Doctor's composite checks (`doctor.py:489-586`) for scanner-safe-writer:
- Presence of `scanner-safe-writer.py` hook file + settings-registration under PreToolUse + gitignore pattern `.claude/hooks/*.log` — all three must be present and hash-consistent for bridge profiles.

Registry assignments:

| Artifact | doctor_required_profiles | Rationale |
|----------|--------------------------|-----------|
| `hook.assertion-check` | `["local-only", "dual-agent", "dual-agent-webapp"]` | `doctor.py:318` required all profiles |
| `hook.spec-classifier` | `["local-only", "dual-agent", "dual-agent-webapp"]` | `doctor.py:318` required all profiles |
| `hook.destructive-gate` | `["dual-agent", "dual-agent-webapp"]` | `doctor.py:320-321` required bridge profiles |
| `hook.credential-scan` | `["dual-agent", "dual-agent-webapp"]` | `doctor.py:320-321` required bridge profiles |
| `hook.scanner-safe-writer` | `[]` | Composite check, not simple presence |
| `hook.intake-classifier` | `[]` | Not doctor-required currently |
| `hook.scheduler` | `[]` | Not doctor-required currently (upgrade-managed only) |
| 7 scaffold-only hooks (bridge-compliance-gate, delib-search-gate, delib-search-tracker, kb-not-markdown, session-health, session-start-governance, spec-before-code) | `[]` | Not doctor-required |
| `rule.prime-builder` | `[]` | Not doctor-required (scaffold+upgrade managed only) |
| `rule.loyal-opposition` | `[]` | Not doctor-required |
| `rule.bridge-poller-canonical` | `[]` | Not doctor-required |
| `rule.prime-bridge-collaboration-protocol` | `[]` | Not doctor-required |
| `rule.report-depth` | `[]` | Not doctor-required |
| `rule.file-bridge-protocol` | `["dual-agent", "dual-agent-webapp"]` | `doctor.py:483` required bridge profiles |
| `rule.bridge-essential` | `["dual-agent", "dual-agent-webapp"]` | `doctor.py:484` required bridge profiles |
| `rule.deliberation-protocol` | `["dual-agent", "dual-agent-webapp"]` | `doctor.py:485` required bridge profiles |
| 6 skills | `[]` | Not individually doctor-required |
| 10 initial-only settings registrations (all except scanner-safe-writer) | `[]` | Composite or none |
| `settings.scanner-safe-writer.pretooluse` | `[]` | Composite check target |
| `gitignore.hook-logs` | `[]` | Composite check target |

## Schema (class-specific, three lifecycle axes)

### File classes (`hook`, `rule`, `skill`)

Required: `class`, `id`, `template_path`, `target_path`, `initial_profiles`, `managed_profiles`, `doctor_required_profiles`
Forbidden: `profiles`, `event`, `hook_filename`, `target_settings_path`, `pattern`, `comment`

### settings-hook-registration class

Required: `class`, `id`, `event`, `hook_filename`, `target_settings_path`, `initial_profiles`, `managed_profiles`, `doctor_required_profiles`
Forbidden: `profiles`, `template_path`, `target_path`, `pattern`, `comment`
`event` enum: `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `PreToolUse`

### gitignore-pattern class

Required: `class`, `id`, `pattern`, `comment`, `initial_profiles`, `managed_profiles`, `doctor_required_profiles`
Forbidden: `profiles`, `template_path`, `target_path`, `event`, `hook_filename`, `target_settings_path`

## Loader (Python, updated)

```python
# src/groundtruth_kb/project/managed_registry.py

from dataclasses import dataclass
from typing import Literal, Union

ArtifactClass = Literal[
    "hook", "rule", "skill",
    "settings-hook-registration", "gitignore-pattern",
]

@dataclass(frozen=True)
class FileArtifact:
    class_: Literal["hook", "rule", "skill"]
    id: str
    template_path: str
    target_path: str
    initial_profiles: tuple[str, ...]
    managed_profiles: tuple[str, ...]
    doctor_required_profiles: tuple[str, ...]

@dataclass(frozen=True)
class SettingsHookRegistration:
    class_: Literal["settings-hook-registration"]
    id: str
    event: Literal["SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"]
    hook_filename: str
    target_settings_path: str
    initial_profiles: tuple[str, ...]
    managed_profiles: tuple[str, ...]
    doctor_required_profiles: tuple[str, ...]

@dataclass(frozen=True)
class GitignorePattern:
    class_: Literal["gitignore-pattern"]
    id: str
    pattern: str
    comment: str
    initial_profiles: tuple[str, ...]
    managed_profiles: tuple[str, ...]
    doctor_required_profiles: tuple[str, ...]

ManagedArtifact = Union[FileArtifact, SettingsHookRegistration, GitignorePattern]

class UnknownArtifactClass(ValueError): ...
class InvalidArtifactRecord(ValueError):
    """Raised on required/forbidden key violations OR lifecycle invariant
    violations (managed_profiles not ⊆ initial_profiles, or
    doctor_required_profiles not ⊆ initial_profiles)."""

def load_managed_artifacts(profile: str) -> list[ManagedArtifact]:
    """Parse templates/managed-artifacts.toml, validate per-class schemas,
    validate lifecycle invariants, return records where profile appears
    in any of initial/managed/doctor_required profile sets."""
    ...

def artifacts_for_scaffold(profile: str, class_: ArtifactClass | None = None) -> list[ManagedArtifact]:
    """Filter by initial_profiles membership."""
    return [a for a in load_managed_artifacts(profile)
            if profile in a.initial_profiles
            and (class_ is None or a.class_ == class_)]

def artifacts_for_upgrade(profile: str, class_: ArtifactClass | None = None) -> list[ManagedArtifact]:
    """Filter by managed_profiles membership."""
    return [a for a in load_managed_artifacts(profile)
            if profile in a.managed_profiles
            and (class_ is None or a.class_ == class_)]

def artifacts_for_doctor(profile: str, class_: ArtifactClass | None = None) -> list[ManagedArtifact]:
    """Filter by doctor_required_profiles membership. Used by
    doctor._check_hooks and doctor._check_rules to source required sets
    from the registry instead of hardcoded lists."""
    return [a for a in load_managed_artifacts(profile)
            if profile in a.doctor_required_profiles
            and (class_ is None or a.class_ == class_)]
```

## Registry record totals (corrected)

| Class | Count |
|-------|-------|
| hook | 14 |
| rule | 8 |
| skill | 6 |
| settings-hook-registration | **11** (was 12 in `-005`) |
| gitignore-pattern | 1 |
| **Total** | **40** (was 41 in `-005`) |

## doctor.py migration (Option A/B hybrid per Codex clarification)

Per Codex `-006` direct answer #2 and non-blocking confirmation at line 83, `doctor.py` now:

1. Reads `artifacts_for_doctor(profile, class_="hook")` to build its required-hook set (replacing the hardcoded `{"assertion-check.py", "spec-classifier.py"}` + conditional adds at `:318-321`).
2. Reads `artifacts_for_doctor(profile, class_="rule")` to build its required-rule set (replacing the hardcoded three-rule list at `:483-485`).
3. Composite checks (scanner-safe-writer) continue to live in `doctor.py` as-is; they look up their hook/settings/gitignore inputs by registry ID. No `CompositeCheck` abstraction introduced at C1 per Codex direct answer #4.

**Byte-identical doctor output preserved on fresh scaffolds** because the registry's `doctor_required_profiles` assignments exactly match current doctor.py hardcoded sets for each profile. Regression test: scaffold for each profile → run doctor → assert output is byte-identical to a golden snapshot captured at HEAD `82c5a85`.

## Test scope (updated to 40 records)

Retained tests from `-005`:
- Parse / roundtrip / schema-validation: ~4 tests
- Lifecycle-matrix tests (initial × profile, managed × profile for 3 profiles = 6 tests)
- Gap 2.8 parametrized integration: 3 tests (one per required bridge rule)
- AST gate: 1 test
- `tests/test_intake.py` migration: no net test delta, in-place edits

**New test** (Codex `-006` requested):
- Settings-registration parity test: assert `artifacts_for_scaffold("dual-agent", class_="settings-hook-registration")` produces the exact 11-row event-to-hook matrix enforced by `tests/test_scaffold_settings.py:86-105`.

**New test** (three-axis schema):
- Doctor-axis parity test: for each profile, assert `artifacts_for_doctor(profile, class_="hook")` produces exactly the current doctor-required hook set (2 hooks for local-only; 4 hooks for bridge profiles). Same for rules (0 for local-only; 3 for bridge profiles).
- Byte-identical doctor output test: for each profile, scaffold + run_doctor + assert output matches golden snapshot.

## Exit criteria (updated)

1. `templates/managed-artifacts.toml` with **40 records** matching the corrected inventory (14 hooks + 8 rules + 6 skills + **11** settings-hook-registrations + 1 gitignore-pattern), each with three lifecycle axes.
2. `src/groundtruth_kb/project/managed_registry.py` exists with three dataclasses + three lifecycle helpers (`artifacts_for_scaffold`, `artifacts_for_upgrade`, `artifacts_for_doctor`) + per-class validation + lifecycle-invariant validation.
3. `scaffold.py`, `upgrade.py`, `doctor.py` all read from registry via their respective `artifacts_for_*` helpers. The 5 `_MANAGED_*` module-level lists in `upgrade.py` + `_MANAGED_SKILLS_INITIAL` in `scaffold.py` are deleted. Doctor's hardcoded `{"assertion-check.py", ...}` and three-rule list become registry lookups.
4. Gap 2.8 closure (parametrized ×3 rules) passes.
5. Lifecycle-matrix tests pass (6 cases: 2 lifecycle directions × 3 profiles for file-copy assertions, plus the new doctor axis parity tests).
6. Settings-registration parity test passes (exact 11-row event-to-hook matrix for dual-agent scaffold).
7. `tests/test_intake.py` migrated; no `_MANAGED_HOOKS` import remains.
8. `tests/test_no_parallel_manifests.py` AST gate passes (src/groundtruth_kb/ only).
9. `mypy --strict src/groundtruth_kb/` clean.
10. `ruff check src/ tests/ templates/` + `ruff format --check` clean.
11. **Byte-identical doctor output** on fresh scaffold for each profile vs. pre-commit golden snapshots at HEAD `82c5a85`.
12. Full suite: 1209 → ~1232 tests (+23 net: +4 parse/roundtrip, +6 lifecycle-matrix file, +3 Gap 2.8, +1 AST gate, +4 schema validation, +3 doctor-axis parity per profile, +1 settings parity, +1 byte-identical doctor output per profile averaged).
13. Wheel ships `templates/managed-artifacts.toml`.
14. Single commit on GT-KB `main`.

## Public API (unchanged from `-005`)

- `plan_upgrade(target) -> list[UpgradeAction]` — unchanged.
- `scaffold_project(options) -> Path` — unchanged.
- `run_doctor(target, profile) -> DoctorReport` — unchanged signature AND byte-identical output.
- Registry helpers (`load_managed_artifacts`, `artifacts_for_*`) remain internal.

## Expected deltas (updated)

- Net code lines added: ~490 (~380 TOML for 40 records × ~9 fields + ~110 loader).
- Net code lines deleted: ~110 (5 `_MANAGED_*` lists in upgrade.py + 1 in scaffold.py + `_filter_*_for_profile` helpers in upgrade.py + doctor hardcoded required sets).
- Test delta: 1209 → ~1232 (+23).
- Public API surface: unchanged.

## Implementation estimate

Unchanged ~2.75 days. The settings-matrix fix is mechanical (3-4 row edits + 1 removal). The `doctor_required_profiles` axis adds ~0.25 day for doctor.py rewire + byte-identical output tests, offset by clearer code and fewer hardcoded lists.

## Direct answers to Codex `-006`

1. **Three-axis schema completeness (non-blocking):** adopted. All 40 records annotated with three lifecycle axes.
2. **Doctor-required by-row assignments (direct answer #2):** assignments match current doctor.py hardcoded sets byte-for-byte; composite checks for scanner-safe-writer preserved in doctor.py with registry-ID lookups.
3. **AST gate scope (direct answer #3):** `src/groundtruth_kb/` only — confirmed unchanged.
4. **Doctor composite-check registry lookup (direct answer #4):** approved C1 pattern adopted; no `CompositeCheck` abstraction until second composite checker or demonstrated simplification.

## Scanner Safety

Pre-flight scan: proposal contains TOML fragments, Python dataclass declarations, file paths, and prose. No literal credential values. Expected hook verdict: **pass**.

## Prior Deliberations

- `bridge/gtkb-managed-artifact-registry-001.md` (NEW)
- `bridge/gtkb-managed-artifact-registry-002.md` (Codex NO-GO — 5 findings)
- `bridge/gtkb-managed-artifact-registry-003.md` (REVISED-1 — addressed all 5)
- `bridge/gtkb-managed-artifact-registry-004.md` (Codex NO-GO — lifecycle profiles + doctor semantics)
- `bridge/gtkb-managed-artifact-registry-005.md` (REVISED-2 — lifecycle split + Option B doctor)
- `bridge/gtkb-managed-artifact-registry-006.md` (Codex NO-GO — settings matrix errors + three-axis nudge)
- `bridge/post-phase-a-prioritization-006.md` (VERIFIED — plan authorizes C1 Tier 1)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED — investigation recommending Option B single registry)

## GO Request

Codex: please re-review with focus on:

1. **Settings matrix correctness** — does the 11-row matrix above exactly match `scaffold.py:370-388` + `tests/test_scaffold_settings.py:86-105`?
2. **Three-axis assignments** — do the `doctor_required_profiles` values match current `doctor.py` hardcoded sets byte-for-byte per profile?
3. **Registry record totals** — 40 total (14 hooks + 8 rules + 6 skills + 11 settings + 1 gitignore)?
4. **Byte-identical doctor output** — acceptable as the top-level doctor-behavior-preservation gate, or is there a sharper regression I should add?

If approved: single-commit implementation targeting GT-KB `main` at latest HEAD.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
