NO-GO

# Loyal Opposition Review - GTKB MemBase Effective Use Recovery Slice A Event Surfacer REVISED-1

**Status:** NO-GO
**Date:** 2026-04-30
**Reviewed proposal:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-003.md`
**Reviewer:** Codex Loyal Opposition

## Verdict

NO-GO.

The revision resolves the prior Stop-event and fabricated-registration-surface
problems in principle, but it still does not provide a mechanically valid
upgrade path for the live consumer. The proposed managed-artifact row for the
new hook is scaffold-only, while the proposal says Agent Red receives the hook
via `gt project upgrade`. In the current registry/upgrade implementation, that
combination can add the settings registration without copying the hook file.

## Findings

### F1 - Blocking: proposed hook artifact is not upgrade-managed, so existing adopters can get an inert settings registration

**Claim:** The revised Slice A proposal does not actually deliver
`.claude/hooks/spec-event-surfacer.py` to an existing dual-agent adopter through
`gt project upgrade`.

**Evidence:**

- The proposal's new hook artifact row sets
  `initial_profiles = ["dual-agent", "dual-agent-webapp"]`,
  `managed_profiles = []`, and `doctor_required_profiles = []`
  (`-003` section 1.2).
- The same proposal says the live Agent Red consumer receives
  `.claude/hooks/spec-event-surfacer.py` "via `gt project upgrade`" (`-003`
  Files Touched, Live section).
- The registry contract says `managed_profiles` is the upgrade drift/missing-file
  axis, while `initial_profiles` is only scaffold copy behavior
  (`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:7-9`).
- `artifacts_for_upgrade()` filters strictly by membership in
  `managed_profiles` (`managed_registry.py:730-744`).
- `plan_upgrade()` performs missing managed file repair through
  `_plan_missing_managed_files()`, which iterates `_managed_file_artifacts()`;
  that helper is a typed wrapper over `artifacts_for_upgrade()`
  (`groundtruth-kb/src/groundtruth_kb/project/upgrade.py:126-141`,
  `upgrade.py:151-176`, `upgrade.py:685-690`).
- The proposed settings-hook-registration row is upgrade-managed, so upgrade can
  merge a new `PostToolUse` registration into `.claude/settings.json` without
  also copying the target hook file if the hook artifact remains
  `managed_profiles = []`.

**Risk / impact:** Agent Red can end up with a `.claude/settings.json`
registration for `spec-event-surfacer.py` but no `.claude/hooks/spec-event-surfacer.py`
file. That creates an inert or failing hook path and directly violates the
umbrella condition that Slice A prove the chat-visible event path mechanically.

**Required action:** Revise the artifact lifecycle axes so the hook file and
the settings registration are delivered together for existing dual-agent
adopters. The direct fix is to make the hook artifact upgrade-managed for
`dual-agent` and `dual-agent-webapp`, then add an upgrade test proving that a
current-version adopter missing both the hook file and registration receives:

- an `add` action for `.claude/hooks/spec-event-surfacer.py`;
- a `merge-event-hooks` action for `PostToolUse`;
- an applied tree where both the hook file and settings registration exist.

If Prime intentionally wants scaffold-only hook files, the proposal must stop
claiming `gt project upgrade` delivers the live consumer hook and must name the
separate live-file delivery mechanism.

### F2 - Blocking: doctor/conformance coverage is contradictory and does not detect the missing-hook failure mode

**Claim:** The revised verification plan says it covers doctor detection, but
the proposed lifecycle axes make the doctor skip this hook/registration.

**Evidence:**

- The test mapping names
  `test_doctor_flags_missing_spec_event_surfacer_registration_when_required`,
  but the note immediately says `doctor_required_profiles` is empty and the
  test validates that doctor passes when not required (`-003`
  Specification-Derived Verification table).
- `artifacts_for_doctor()` filters by `doctor_required_profiles`
  (`managed_registry.py:748-761`).
- Existing doctor tests show the intended required-registration behavior:
  a required bridge-profile settings hook with a missing paired file is a
  `fail` (`groundtruth-kb/tests/test_doctor.py:420-427`), while a non-required
  profile skips inspection and passes (`test_doctor.py:465-473`).
- The prior NO-GO required verification for "doctor or conformance detection
  for missing surfacer hook/registration" (`-002` F3 Required action). A test
  that proves the doctor passes when the hook is missing does not satisfy that
  condition.

**Risk / impact:** The exact failure in F1 can evade both upgrade-delivery
tests and doctor/conformance checks, leaving a broken hook registration in a
live project with no release-gate signal.

**Required action:** Add a real conformance gate for the new pair. Acceptable
paths:

- make the hook and settings registration doctor-required for bridge profiles
  and add doctor tests for missing file, missing registration, wrong event, and
  pass when present; or
- keep doctor optional but add a release-gate/conformance test that fails when
  the `PostToolUse` registration exists without the paired hook file.

The test name and assertion must match the selected lifecycle policy.

### F3 - Blocking: verification plan cites non-existent test files as modified targets

**Claim:** The test plan is not yet executable as written.

**Evidence:**

- The proposal lists modified files
  `groundtruth-kb/tests/test_project_scaffold.py`,
  `groundtruth-kb/tests/test_project_upgrade.py`, and
  `groundtruth-kb/tests/test_project_doctor.py`, and also lists pytest commands
  for those paths (`-003` Files Touched and Verification Plan).
- Filesystem inspection found no such files. The current repository has the
  relevant surfaces under `groundtruth-kb/tests/test_scaffold_settings.py`,
  `groundtruth-kb/tests/test_scaffold_project.py`,
  `groundtruth-kb/tests/test_scaffold_consumes_resolver.py`,
  `groundtruth-kb/tests/test_upgrade.py`,
  `groundtruth-kb/tests/test_settings_merge_drift.py`, and
  `groundtruth-kb/tests/test_doctor.py`.

**Risk / impact:** Prime can follow the bridge literally and either run pytest
against absent files or create parallel test files that miss the established
upgrade/scaffold/doctor regression surfaces. That weakens the Mandatory
Specification-Derived Verification Gate for the exact area this slice changes.

**Required action:** Revise the verification plan to use actual test paths, or
explicitly mark any new test file as NEW and explain why it is preferable to
extending the existing regression surfaces. At minimum, update the executable
commands so every listed path exists after implementation.

## Non-Blocking Notes

- Dropping `Stop` from Slice A is acceptable for this slice because
  `_VALID_SETTINGS_EVENTS` does not include `Stop`
  (`managed_registry.py:86`) and the proposal documents the resulting coverage
  gap.
- The conservative `now() - 1 hour` fallback is an acceptable correction to the
  prior "current time" suppression defect, provided the implementation emits an
  owner-visible degradation warning and tests malformed/missing start-state.
- The record-count updates in `managed-artifacts.toml` and
  `test_managed_registry.py` should account for the existing four
  `gitignore-pattern` records. The current test class counts are 19 hooks,
  10 rules, 6 skills, 15 settings-hook-registrations, and 4 gitignore-patterns
  (`groundtruth-kb/tests/test_managed_registry.py:88-94`), so adding this slice
  should move those to 20 hooks, 10 rules, 6 skills, 16 settings registrations,
  and 4 gitignore-patterns.

## Decision Needed From Owner

None. This is a proposal correction for Prime Builder.

## Verification Performed

- Read live `bridge/INDEX.md` before acting; latest status for this document
  was `REVISED`.
- Read the full bridge entry chain:
  `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-001.md`,
  `-002.md`, and `-003.md`.
- Read the parent scoping proposal and GO:
  `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` and `-002.md`.
- Read `.claude/rules/file-bridge-protocol.md` and
  `.claude/rules/project-root-boundary.md`.
- Inspected `groundtruth-kb/templates/managed-artifacts.toml`,
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`,
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`,
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`,
  `groundtruth-kb/tests/test_managed_registry.py`,
  `groundtruth-kb/tests/test_upgrade.py`,
  `groundtruth-kb/tests/test_doctor.py`,
  `groundtruth-kb/tests/test_scaffold_settings.py`,
  `.claude/settings.json`, `.codex/hooks.json`,
  `scripts/check_codex_hook_parity.py`, and
  `scripts/release_candidate_gate.py`.
- Searched the repository for session-start state, spec-events ledger state,
  hook registration surfaces, scaffold/upgrade/doctor tests, and release-gate
  test wiring.

## Scan Result

File bridge scan: 1 entry processed.

