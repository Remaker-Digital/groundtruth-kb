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

bridge_kind: prime_proposal
Document: gtkb-wi5667-author-provenance-safe-recovery
Version: 003
Responds to: bridge/gtkb-wi5667-author-provenance-safe-recovery-002.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667
target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]

# WI-5667 Author-Provenance-Safe Scaffold Rename Recovery — PAUTH-Complete Revision

## Revision Disposition

This revision resolves the sole version-002 finding by adding
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` to the governing
links and mapping their exact claim/packet checks below. The 17-path scope,
six-substitution doctor boundary, quarantine, tests, and owner outcome are
unchanged from version 001.

No implementation target is changed or staged through this revision. The
currently staged WI-5661 bridge-only report is unrelated evidence and prevents
any WI-5667 implementation start until its index transaction is complete.

## Claim

Use this fresh provenance-valid chain to adopt only the existing 17-path
WI-5667 managed scaffold candidate after an independent GO, exact claim, and
successful operation-time packet. The historical
`gtkb-wi5667-scaffold-managed-skill-rename-recovery` GO remains non-executable
because its operative proposal provenance is unreadable and supplies no
authority here.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667193` authorizes the
gtkb-prefixed managed scaffold outcome; `DELIB-202667194` requires exact
foreign-hunk isolation. No new owner decision is needed.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations And Bridge Evidence

- `DELIB-202667193` — owner-directed gtkb-prefixed managed templates.
- `DELIB-202667194` — exact isolation and foreign-hunk exclusion.
- `bridge/gtkb-wi5667-author-provenance-safe-recovery-001.md` — complete
  17-path recovery proposal.
- `bridge/gtkb-wi5667-author-provenance-safe-recovery-002.md` — NO-GO whose
  sole P1 specification-link finding is corrected here.
- `bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-004.md` —
  historical accepted design but unusable implementation authority.

## Owner Decisions / Input

No new owner decision is required. This revision changes no approved outcome
or target; it completes the governing linkage demanded by version 002.

## Exact Doctor Hunk Ownership

Only six rename substitutions against doctor index blob `7087c8e47` are
owned:

1. `_check_skill_present`: `decision-capture` paths/diagnostic become
   `gtkb-decision-capture`.
2. `_check_bridge_propose_skill_present`: `bridge-propose` paths/diagnostic
   become `gtkb-bridge-propose`.
3. `_check_spec_intake_skill_present`: `spec-intake` paths/diagnostic become
   `gtkb-spec-intake`.

The separate `_check_skill_rename_reference_sweep` definition and
`run_doctor()` registration are WI-5668 evidence and remain unstaged.

## Implementation And Verification Plan

1. Require an empty index before WI-5667 work. After a fresh GO, acquire the
   exact claim and run `implementation_authorization.py begin --no-write` to
   verify PAUTH ID/project/WI, proposal/GO provenance, all 17 target
   classifications, and allowed operation-time decision. Then run normal
   `begin` and verify the written schema-v3 packet matches those facts.
2. Build an index-only patch against blob `7087c8e47` for only the six doctor
   substitutions. Run `git apply --cached --check`, apply it to the index, and
   prove the WI-5668 evaluator remains only in the unstaged diff.
3. Stage only the other declared template/test paths after exact-scope review.
   Abort on either scaffold-golden root or any undeclared path.
4. Run all `test_scaffold_skills.py`, the six bridge/spec-intake upgrade
   selectors, three managed-registry selectors, and
   `test_doctor.py::test_check_rules_with_files` under the groundtruth-kb
   rootdir/testpaths configuration.
5. Run Ruff check/format-check on doctor and the four tests; run scoped diff,
   cached-set, applicability, and clause gates; commit only the 17-path index
   and file a strict committed implementation report.

## Quarantine And Explicit Exclusions

- Never read, modify, stage, restore, rebaseline, attribute, or commit either
  `groundtruth-kb/tests/fixtures/scaffold_golden/` root.
- Never invoke `scripts/_capture_scaffold_golden.py`, including help/dry-run.
- Never stage the WI-5668 doctor evaluator/registration, retained bare
  templates, WI-5640 policy, generated adapters, or canonical runtime skills.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Project authorization (`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`) | `gt projects show-authorization <PAUTH> --json`, active WI membership, and exact target-class audit | Active PAUTH covers WI-5667 and every classified target without widening scope |
| Operation-time enforcement (`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`) | Post-GO claim plus `begin --no-write`, then normal `begin` | Current-session claim/provenance and all 17 targets yield allowed schema-v3 packet |
| Author/bridge provenance | Fresh proposal, independent GO, claim, packet | No reuse of the unreadable historical chain |
| Managed scaffold consistency | Focused scaffold, upgrade, registry, doctor selectors | Declared gtkb-prefixed artifacts agree |
| Foreign ownership | Cached/unstaged doctor assertions | Six rename substitutions committed; WI-5668 evaluator excluded |
| Quarantine | Exact staged-path scan | Neither scaffold-golden root is accessed or committed |

## Acceptance Criteria

- Fresh operation-time evidence proves the active PAUTH permits the exact
  17-path implementation before any protected mutation or staging.
- Scaffold/upgrade emits the declared gtkb-prefixed managed artifacts and all
  focused selectors pass.
- Commit contains only the six doctor substitutions plus other declared paths.
- Scaffold-golden roots and WI-5668 evaluator bytes remain excluded.
- A committed report receives independent LO terminal review.

## Risks / Rollback

Risks are invalid PAUTH assumptions, reuse of unreadable historical authority,
whole-file doctor staging, and quarantined-golden contamination. The explicit
operation-time mapping, clean-index prerequisite, index-only patch, and exact
exclusions fail closed. Rollback is a separately governed revert of only a
later scoped commit.

## Recommended Commit Type

`fix`
