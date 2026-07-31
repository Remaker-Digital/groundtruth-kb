REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5667 Author-Provenance-Safe Scaffold Rename Recovery — Complete Quality Plan

bridge_kind: prime_proposal
Document: gtkb-wi5667-author-provenance-safe-recovery
Version: 005
Responds to: bridge/gtkb-wi5667-author-provenance-safe-recovery-004.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]

## Revision Disposition

This revision resolves version 004’s sole finding. The exact 17-target scope,
six-substitution doctor boundary, operation-time authorization mapping, fresh
provenance-safe chain, and scaffold-golden quarantine remain unchanged. Both
Ruff commands now cover every one of the 12 Python targets, and the focused
pytest plan names every node ID.

No implementation target or staging area was changed through this revision.
The real index still contains the unrelated staged WI-5661 bridge evidence
carrier, so WI-5667 implementation must not start until that transaction has
been independently finalized and the real index is empty.

## Claim

After a fresh independent GO, empty-index proof, exact Prime claim, and
successful current-session implementation-start packet, this chain may adopt
only the existing 17-path managed-scaffold candidate. The historical
`gtkb-wi5667-scaffold-managed-skill-rename-recovery` GO remains unusable: its
immutable v001 has unreadable bare author provenance, and a later valid version
cannot repair that append-only chain.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667193` authorizes the
gtkb-prefixed managed scaffold outcome; `DELIB-202667194` requires exact
skill-rename isolation and exclusion of commingled foreign work. Version 004
requires no new owner decision.

## Specification Links

- GOV-DOCUMENT-AUTHOR-PROVENANCE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Prior Deliberations And Evidence

- `DELIB-202667193` — owner-directed gtkb-prefixed managed templates.
- `DELIB-202667194` — exact isolation and foreign-hunk exclusion.
- Versions 001–004 of this fresh chain — complete recovery scope, PAUTH/spec
  linkage, and the quality-coverage correction resolved here.
- `bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-004.md` —
  historical accepted design only; never implementation authority.

## Owner Decisions / Input

No new owner decision is required. This revision adds reproducible quality
evidence without changing the owner-approved outcome or implementation scope.

## Exact Doctor Hunk Ownership

Only six rename substitutions against doctor index blob `7087c8e47` are owned:

1. `_check_skill_present`: `decision-capture` paths/diagnostic become
   `gtkb-decision-capture`.
2. `_check_bridge_propose_skill_present`: `bridge-propose` paths/diagnostic
   become `gtkb-bridge-propose`.
3. `_check_spec_intake_skill_present`: `spec-intake` paths/diagnostic become
   `gtkb-spec-intake`.

The separate `_check_skill_rename_reference_sweep` definition and
`run_doctor()` registration are WI-5668 evidence and remain unstaged.

## Complete Python Quality Set

Both `ruff check` and `ruff format --check` use this exact 12-file set:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py`
- `groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py`
- `groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py`
- `groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py`
- `groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py`
- `groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py`
- `groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py`
- `groundtruth-kb/tests/test_scaffold_skills.py`
- `groundtruth-kb/tests/test_upgrade_skills.py`
- `groundtruth-kb/tests/test_managed_registry.py`
- `groundtruth-kb/tests/test_doctor.py`

Pre-filing results on the current candidate: Ruff check `All checks passed!`;
Ruff format-check `12 files already formatted`.

## Exact Focused Test Set

- Whole `groundtruth-kb/tests/test_scaffold_skills.py`.
- `test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_propose_skill_at_same_version`
- `test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_skill_at_same_version`
- `test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_helper_at_same_version`
- `test_upgrade_skills.py::test_execute_creates_missing_spec_intake_files_at_same_version`
- `test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version`
- `test_upgrade_skills.py::test_execute_creates_missing_bridge_skill_files_at_same_version`
- `test_managed_registry.py::test_bridge_skill_records_are_managed_for_dual_agent_profiles`
- `test_managed_registry.py::test_scaffold_dual_agent_copies_everything`
- `test_managed_registry.py::test_upgrade_dual_agent_manages_full_set_including_gap_28_rules`
- `test_doctor.py::test_check_rules_with_files`

Pre-filing result on the current candidate: `17 passed in 25.58s`.

## Implementation And Verification Plan

1. Require an empty real index. After fresh GO, acquire the exact claim and run
   `implementation_authorization.py begin --no-write`, verifying PAUTH,
   project/WI, proposal/GO provenance, all 17 classifications, and allowed
   operation-time decision. Then run normal `begin` and verify its schema-v3
   packet against the same facts.
2. Build an index-only patch against doctor blob `7087c8e47` containing only
   the six substitutions. Run `git apply --cached --check`, apply to the index,
   and prove the WI-5668 evaluator remains only in the unstaged diff.
3. Stage only the other declared template/test paths after exact review. Abort
   on either scaffold-golden root, any undeclared path, or generator spillover.
4. Re-run the exact 17-test set and both Ruff commands over the complete
   12-file Python set. Run `git diff --cached --check` and exact cached-path and
   hunk assertions.
5. Commit only the 17-path transaction. Before terminal finalization, use a
   separately scoped WI-5667 bridge/evidence carrier if the current PAUTH’s
   explicit bridge-audit exclusion would otherwise block report finalization.

## Quarantine And Explicit Exclusions

- Never read, modify, stage, restore, rebaseline, attribute, or commit either
  `groundtruth-kb/tests/fixtures/scaffold_golden/` root.
- Never invoke `scripts/_capture_scaffold_golden.py`, including help/dry-run.
- Never stage the WI-5668 doctor evaluator/registration, retained bare
  templates, WI-5640 policy, generated adapters, or canonical runtime skills.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Project authorization | Active PAUTH/WI membership and exact classification audit | All 17 targets covered without widening. |
| Operation-time enforcement | Fresh claim, `begin --no-write`, then normal `begin` | Current-session allowed schema-v3 packet. |
| Author/bridge provenance | Fresh proposal and independent GO | Historical chain is never reused. |
| Managed scaffold consistency | Exact 17-test node set | All focused regressions pass. |
| Python quality | Ruff check + format-check on exact 12-file set | All checks pass; 12 formatted. |
| Foreign ownership | Cached/unstaged doctor assertions | Six substitutions cached; WI-5668 excluded. |
| Quarantine | Exact staged-path scan | Neither scaffold-golden root is accessed or committed. |

## Acceptance Criteria

- Fresh operation-time evidence permits exactly the 17 paths before protected
  mutation or staging.
- The exact focused set passes and both Ruff gates cover all 12 Python targets.
- The commit contains only six doctor substitutions plus the other declared
  paths; WI-5668 and all foreign hunks remain excluded.
- Scaffold-golden roots are never accessed.
- A committed report receives independent LO terminal review under a valid
  bridge/evidence finalization carrier.

## Pre-Filing Preflight Subsection

The governed helper must run applicability and mandatory ADR/DCL clause
preflights against this completed candidate. Any missing required spec or
blocking clause gap prohibits filing.

## Risk And Rollback

Risks are invalid authorization assumptions, historical-chain reuse,
whole-file doctor staging, incomplete Python quality coverage, and quarantined
golden contamination. The complete gates, clean-index prerequisite, index-only
patch, and exact exclusions fail closed. Rollback is a separately governed
revert of only a later scoped commit.

## Recommended Commit Type

fix
