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


# Implementation Proposal — WI-5667 scaffold rename with doctor hunk isolation

bridge_kind: prime_proposal
Document: gtkb-wi5667-scaffold-managed-skill-rename-recovery
Version: 003
Responds to: bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-002.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]

## Summary

This revision preserves the clean-recovery scope from v001 and adds the required
foreign-hunk isolation for `doctor.py`. It does not treat the pre-GO candidate
contents as implementation evidence and does not rewrite the historical chain.

## Claim

After a fresh independent GO and implementation-start packet, the recovery will
commit only the declared 17 paths. In `doctor.py`, it will stage exactly the six
rename hunks listed below; the separate WI-5668 detector hunk remains an
unstaged, unowned worktree change throughout this transaction.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202667193` and the active WI-5667
authorization cover the renamed managed scaffold outcome; this revision only
makes its ownership boundary executable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667193` — owner-directed gtkb-prefixed managed templates.
- `DELIB-202667194` — recovery must preserve foreign-hunk ownership.

## Owner Decisions / Input

No new owner decision is required. The owner-approved renamed-template outcome
is unchanged; the added staging protocol prevents accidental attribution of an
unrelated evaluator.

## Exact Doctor Hunk Ownership

The only `doctor.py` content owned by this recovery is the following six
existing rename hunks from `7087c8e47`:

1. `_check_skill_present`: `decision-capture` paths and diagnostic string become `gtkb-decision-capture`.
2. `_check_bridge_propose_skill_present`: `bridge-propose` paths and diagnostic string become `gtkb-bridge-propose`.
3. `_check_spec_intake_skill_present`: `spec-intake` paths and diagnostic string become `gtkb-spec-intake`.

The unrelated, explicitly excluded hunk is the insertion of
`_check_skill_rename_reference_sweep` at original line 2529 plus its
`run_doctor()` registration. It is 108 added lines in the current worktree,
belongs to WI-5668, and must remain absent from the staged diff and any commit
for this bridge.

## Implementation And Verification Plan

1. Acquire a claim and issue `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5667-scaffold-managed-skill-rename-recovery`; stop before staging if it does not issue a current packet.
2. Create an exact, reviewed index-only patch against blob `7087c8e47` that contains only the six `doctor.py` substitutions above. Run `git apply --cached --check` and then `git apply --cached` on that patch; never use `git add` on the whole doctor file.
3. Prove the staged doctor diff contains the six expected substitutions and no definition, string, or registration named `_check_skill_rename_reference_sweep`; prove the unstaged diff retains that excluded hunk.
4. Stage the remaining declared template and test paths only after the same exact-scope check. Abort if the staged set contains any other path or either scaffold-golden root.
5. Run:

```text
python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_scaffold_skills.py groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_propose_skill_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_skill_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_helper_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_execute_creates_missing_spec_intake_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_execute_creates_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_managed_registry.py::test_bridge_skill_records_are_managed_for_dual_agent_profiles groundtruth-kb/tests/test_managed_registry.py::test_scaffold_dual_agent_copies_everything groundtruth-kb/tests/test_managed_registry.py::test_upgrade_dual_agent_manages_full_set_including_gap_28_rules groundtruth-kb/tests/test_doctor.py::test_check_rules_with_files -q --tb=short
```

6. Run Ruff check and format-check on the doctor module and four tests, then scoped `git diff --check`, staged-set, applicability, and clause preflights. Commit only the packet-authorized index; file a committed report for LO.

## Quarantine And Explicit Exclusions

- Never read, modify, stage, restore, rebaseline, attribute, or commit either `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**` or `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**`.
- Do not invoke `scripts/_capture_scaffold_golden.py`, including help or dry-run modes.
- Do not modify, stage, format, or commit the WI-5668 evaluator function or its `run_doctor()` registration.
- Do not modify retained bare templates, file-reference migration policy, generated adapters, or canonical runtime skills.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh GO, claim, packet, and exact staged index inspection | No protected content is adopted before authority; only declared hunk/path set is staged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused selector plus Ruff and diff checks | Managed templates, registry, doctor, and tests agree on gtkb-prefixed names. |
| Foreign ownership | `git diff --cached` and unstaged `git diff` assertions | Staged doctor diff has only six rename substitutions; the 108-line evaluator remains unstaged. |
| Artifact lifecycle controls | Bridge/clause preflights and commit report | Historical and quarantined evidence remains unmodified. |

## Acceptance Criteria

- A fresh dual-agent scaffold/upgrade emits the declared gtkb-prefixed managed artifacts.
- Registry, templates, doctor checks, and declared tests agree on canonical names.
- `doctor.py` commit evidence contains only the six specified rename hunks; no WI-5668 evaluator content is attributed.
- Only the declared 17 paths are committed and both scaffold-golden roots remain excluded.
- Independent LO review remains required for terminal verification.

## Risks And Rollback

The material risk is staging the mixed doctor file wholesale. The index-only
patch and dual staged/unstaged assertions fail closed. Rollback is a separately
governed revert of only a later scoped commit; historical bridge artifacts and
foreign hunks are never rollback targets.

## Recommended Commit Type

fix
