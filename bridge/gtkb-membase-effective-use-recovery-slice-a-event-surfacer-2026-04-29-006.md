GO

# Loyal Opposition Review - GTKB MemBase Effective Use Recovery Slice A Event Surfacer REVISED-2

**Status:** GO
**Date:** 2026-04-30
**Reviewed proposal:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-005.md`
**Reviewer:** Codex Loyal Opposition

## Verdict

GO.

The REVISED-2 proposal corrects the prior blocking defects. It now routes the
hook file and settings registration through the actual managed-artifact surface,
makes both lifecycle axes match for upgrade and doctor enforcement, and maps the
verification plan to real existing regression surfaces or explicitly new test
files.

This approval is for the Slice A implementation as scoped in `-005`; it does
not verify a completed implementation. Post-implementation verification must
carry forward the linked specifications, the spec-to-test mapping, exact
commands, and observed results per `.claude/rules/file-bridge-protocol.md`.

## Evidence Checked

1. **Live bridge state was actionable.**
   - `bridge/INDEX.md` showed latest status `REVISED` for
     `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-005.md`.
   - The full thread history `-001` through `-005` was read before this verdict.

2. **Specification linkage is present and relevant.**
   - `-005` carries the primary spec `SPEC-INTAKE-2485e9` plus the parent
     scoping bridge and prior NO-GO record.
   - The live KB contains `SPEC-INTAKE-2485e9` v1 with title
     `Surface spec creation/update events in owner chat view`,
     `type='requirement'`, `status='specified'`, and
     `section='membase-effective-use'`.

3. **F1 is resolved: hook file and settings registration now share upgrade axes.**
   - `-005` proposes the hook artifact with
     `managed_profiles=["dual-agent","dual-agent-webapp"]`.
   - `-005` proposes the paired `settings-hook-registration` with the same
     `managed_profiles`.
   - The live registry code documents `managed_profiles` as the upgrade
     drift/missing-file axis and `artifacts_for_upgrade()` filters by that
     field (`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`).
   - The proposed upgrade tests now cover both an `add` action for
     `.claude/hooks/spec-event-surfacer.py` and a `merge-event-hooks` action for
     `PostToolUse`, including the applied tree.

4. **F2 is resolved: doctor/conformance coverage is no longer contradictory.**
   - `-005` makes both hook and settings-registration artifacts
     `doctor_required_profiles=["dual-agent","dual-agent-webapp"]`.
   - The live doctor path filters required checks through
     `doctor_required_profiles`, so this policy is mechanically meaningful.
   - The proposed doctor tests now cover missing hook file, missing
     registration, orphaned registration, and both-present pass behavior.

5. **F3 is resolved: existing test surfaces are real, and new files are marked as new.**
   - Existing paths checked present:
     `groundtruth-kb/tests/test_managed_registry.py`,
     `groundtruth-kb/tests/test_scaffold_settings.py`,
     `groundtruth-kb/tests/test_scaffold_project.py`,
     `groundtruth-kb/tests/test_upgrade.py`,
     `groundtruth-kb/tests/test_settings_merge_drift.py`,
     `groundtruth-kb/tests/test_doctor.py`,
     `tests/scripts/test_session_self_initialization.py`,
     `tests/scripts/test_codex_hook_parity.py`,
     `scripts/session_self_initialization.py`, and
     `scripts/release_candidate_gate.py`.
   - The two absent test files are explicitly scoped as new files:
     `groundtruth-kb/tests/test_spec_event_surfacer.py` and
     `tests/hooks/test_spec_event_surfacer_integration.py`.

6. **Root-boundary posture is acceptable.**
   - All proposed active files are under `E:\GT-KB`.
   - Upstream work is routed to in-root `groundtruth-kb/`; live consumer work is
     in the in-root GT-KB/Agent Red operating surface. No external checkout or
     `E:\Claude-Playground` dependency is proposed.

## Responses To Open Questions

1. **F1 fix selection:** Accept Path A. Make the hook upgrade-managed. There is
   no need to introduce a separate live-file delivery channel for this slice.

2. **F2 fix selection:** Accept Path A. Doctor-required hook plus registration
   is the correct conservative policy for a hook whose absence can make the
   owner-visible event path inert.

3. **F3 additional tests:** No additional blocking test file is required beyond
   the revised list. If implementation touches resolver-specific scaffold code,
   add focused coverage in `test_scaffold_consumes_resolver.py`, but that is not
   a GO condition from this proposal alone.

4. **Record-count correction:** It is acceptable to correct the
   `managed-artifacts.toml` header count in this slice. The count change is
   directly coupled to adding one hook artifact and one settings registration.

5. **Doctor fail-state granularity:** Separate tests for missing hook, missing
   registration, orphaned registration, and both-present pass are clear and
   acceptable. A parametrized implementation is also acceptable if the failure
   messages remain readable.

## Non-Blocking Notes

- `-005` still contains wording that says all pytest paths were verified to
  exist at proposal-drafting time. Prime should interpret that as: all modified
  existing paths were verified, and the two explicitly new test files must be
  created during implementation.
- The post-implementation report must show that `python scripts/release_candidate_gate.py --skip-frontend`
  actually executes the new coverage, not merely that the standalone test
  commands pass.

## Required Next Prime Builder Actions

1. Implement Slice A exactly through the managed-artifact, session-start writer,
   hook, live consumer, and test surfaces listed in `-005`.
2. Preserve PostToolUse-only scope unless a separate bridge expands the managed
   settings-event contract to `Stop`.
3. Return with a post-implementation bridge report that includes linked specs,
   spec-to-test mapping, exact commands, observed results, and manual
   chat-visibility evidence or an explicit documented waiver request.

## Decision Needed From Owner

None.

## Verification Performed

- Read live `bridge/INDEX.md` before acting.
- Read `.claude/rules/file-bridge-protocol.md` and
  `.claude/rules/project-root-boundary.md`.
- Read the full bridge chain for this thread: `-001`, `-002`, `-003`, `-004`,
  and `-005`.
- Read the parent scoping proposal and GO:
  `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` and `-002.md`.
- Queried live `groundtruth.db` read-only for `SPEC-INTAKE-2485e9`.
- Inspected existence of the cited test and implementation surfaces.
- Inspected the live managed registry, upgrade, and doctor surfaces relevant to
  `managed_profiles`, `doctor_required_profiles`, and `merge-event-hooks`.

## Scan Result

File bridge scan: 1 entry processed.
