NO-GO

# Loyal Opposition Review - GTKB MemBase Effective Use Recovery Slice A Event Surfacer

**Status:** NO-GO
**Date:** 2026-04-29
**Reviewed proposal:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-001.md`
**Reviewer:** Codex Loyal Opposition

## Verdict

NO-GO.

The proposal has the right high-level objective and links the primary
specification, but it does not yet satisfy the prior Slice A approval condition
to specify a mechanically valid hook-registration path, per-session start
timestamp source, ledger location, and duplicate-suppression behavior. The
current plan depends on upstream files and session-start state that do not exist
in this checkout, and the proposed tests would not catch the most important
upgrade/registration failures.

## Findings

### F1 - Blocking: upstream hook registration path is not the current managed registration surface

**Claim:** The proposed `gt project upgrade` routing is not mechanically valid.

**Evidence:**

- The proposal says the upstream registration work is
  `groundtruth-kb/templates/settings/post_tool_use.json` plus
  `groundtruth-kb/src/groundtruth_kb/hooks_registry.py`
  (`-001` lines 99-102 and 194-198).
- Filesystem checks showed all three proposed new/existing registration targets
  are absent before implementation:
  `groundtruth-kb/src/groundtruth_kb/hooks_registry.py`,
  `groundtruth-kb/templates/settings/post_tool_use.json`, and
  `groundtruth-kb/templates/settings/stop.json`.
- The current managed-artifact source of truth is
  `groundtruth-kb/templates/managed-artifacts.toml`, documented at lines 3-10
  as the registry for scaffold, upgrade, and doctor.
- The current runtime registry loader is
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`, whose
  `SettingsEvent` and `_VALID_SETTINGS_EVENTS` contain only `SessionStart`,
  `UserPromptSubmit`, `PostToolUse`, and `PreToolUse`
  (`managed_registry.py` lines 45-50 and 86).
- Existing registry parity tests assert the exact 15-row event matrix and only
  include `PostToolUse` for `delib-search-tracker.py` and
  `owner-decision-capture.py`; there is no Stop row in the managed registry
  contract (`groundtruth-kb/tests/test_managed_registry.py` lines 383-425 and
  428-460).

**Risk / impact:** A Prime implementation following the proposal could edit
ad-hoc settings files or invent a parallel settings template while bypassing the
managed artifact registry that `gt project upgrade`, scaffold, and doctor
actually use. That would fail the umbrella GO condition requiring exact hook
registration files, and it risks creating a live-only hook that does not survive
upgrade or conformance checks.

**Required action:** Revise the proposal to use the actual managed-artifact
path:

- Add the hook file to `groundtruth-kb/templates/hooks/spec-event-surfacer.py`.
- Add settings-hook-registration rows to
  `groundtruth-kb/templates/managed-artifacts.toml`.
- Update `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` only if
  `Stop` is intentionally becoming a managed event, and include the supporting
  tests that prove `Stop` is accepted by scaffold, upgrade, doctor, and registry
  validation.
- Update the exact matrix tests, upgrade merge tests, and scaffold/doctor tests
  that currently encode the managed registration contract.

If the revised slice keeps `Stop`, the proposal must explicitly make `Stop` a
first-class managed settings event. If it drops `Stop`, it must explain how the
remaining `PostToolUse` path still satisfies the chat-visibility and coverage
requirement.

### F2 - Blocking: the session-start timestamp and ledger initialization source is asserted but not present

**Claim:** The proposed per-session lower bound is not currently available, and
the fallback can suppress the very events Slice A is meant to surface.

**Evidence:**

- The proposal states that existing `scripts/session_self_initialization.py`
  writes `.claude/session/session-start.json` with `session_started_at`
  (`-001` lines 104-120), and that the existing SessionStart hook initializes
  `.claude/session/spec-events-seen.jsonl` (`-001` lines 122-140).
- Repository search found no current `session_started_at`,
  `.claude/session/session-start.json`, or `spec-events-seen` implementation in
  `scripts/session_self_initialization.py`, `.claude/hooks`, `.codex`,
  `groundtruth-kb/src`, `groundtruth-kb/templates`, or the relevant tests.
- The live Codex SessionStart dispatcher writes diagnostics to
  `.codex/gtkb-hooks/out/last-session-start.json` and captures
  `request_started_at` as an environment-backed freshness timestamp
  (`.codex/gtkb-hooks/session_start_dispatch.py` lines 108-140), not to the
  proposed `.claude/session/session-start.json`.
- The proposal's missing-file fallback says that an empty ledger falls back to
  "the current time" and emits no events that turn (`-001` line 118). If a spec
  row is created earlier in the same turn and no session-start file exists, the
  first surfacer run can set the lower bound after the row's `changed_at`,
  causing the in-session event to be skipped.

**Risk / impact:** The first implementation could pass unit tests built around
fabricated fixtures while failing in the real session lifecycle. In the
degraded path, the surfacer would silently miss exactly the new spec writes it
is supposed to make owner-visible.

**Required action:** Revise the proposal to choose one concrete timestamp
authority and prove it exists in both Claude and Codex paths:

- Either add a real `.claude/session/session-start.json` writer to the active
  SessionStart flow and include tests for the writer, fresh-session ledger reset,
  and missing/malformed recovery; or
- Reuse an existing durable SessionStart source such as the Codex
  `startupFreshness.request_started_at` diagnostic path and define the Claude
  equivalent.

The revised fallback must not make the first surfacer invocation skip
already-created in-session rows. If the timestamp source is missing, fail soft
with an owner-visible degradation message or use a conservative lower bound;
do not use "current time" in a way that hides recent writes.

### F3 - Blocking: verification does not cover the governing upgrade path

**Claim:** The current spec-derived tests omit the upgrade/scaffold/doctor
contracts that constrain hook registration.

**Evidence:**

- The proposal's hook-registration test mapping checks only
  `.claude/settings.json`, `.codex/hooks.json`, and
  `tests/scripts/test_codex_hook_parity.py` (`-001` lines 60-64 and 250-255).
- The prior umbrella GO condition required Slice A to specify exact hook
  registration files and prove the chat-visible event path mechanically
  (`bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md` lines
  98-105).
- The active managed registry and matrix tests are the repository's upgrade
  authority for settings-hook-registration rows
  (`groundtruth-kb/templates/managed-artifacts.toml` lines 3-10 and 521-667;
  `groundtruth-kb/tests/test_managed_registry.py` lines 383-460).

**Risk / impact:** A green test suite could still leave adopters without the
surfacer after `gt project upgrade`, or could make `Stop` registration fail
registry validation after implementation.

**Required action:** Add spec-derived verification for:

- managed-artifact registry row parsing;
- scaffold settings output;
- upgrade structured-merge behavior;
- doctor or conformance detection for missing surfacer hook/registration;
- Codex parity only after the authoritative Claude/managed registration path is
  correct.

## Non-Blocking Notes

- The primary spec exists in the live KB:
  `SPEC-INTAKE-2485e9` v1, title `Surface spec creation/update events in owner
  chat view`, `type='requirement'`, `status='specified'`,
  `section='membase-effective-use'`, `changed_at='2026-04-24T14:28:54+00:00'`.
- `current_specifications.changed_at` is indexed by
  `idx_specs_changed_at` (`groundtruth-kb/src/groundtruth_kb/db.py` lines
  374-416), so the proposed query shape is reasonable once the timestamp source
  is corrected.
- The proposal's KB read-only constraint is appropriate. Keep the "zero
  INSERT/UPDATE/DELETE SQL" acceptance criterion.

## Decision Needed From Owner

None. This is a proposal correction for Prime Builder.

## Verification Performed

- Read live `bridge/INDEX.md` before acting; latest status for this document
  was `NEW`.
- Read `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-001.md`.
- Read `.claude/rules/file-bridge-protocol.md`.
- Read the parent GO at
  `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md`.
- Searched the repository for the cited spec, hook registration surfaces,
  session-start timestamp state, ledger state, and managed registry contracts.
- Queried live `groundtruth.db` read-only for `SPEC-INTAKE-2485e9`.
- Inspected `.claude/settings.json`, `.codex/hooks.json`,
  `.codex/gtkb-hooks/session_start_dispatch.py`,
  `groundtruth-kb/templates/managed-artifacts.toml`,
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`, and
  `groundtruth-kb/tests/test_managed_registry.py`.

## Scan Result

File bridge scan: 1 entry processed.
