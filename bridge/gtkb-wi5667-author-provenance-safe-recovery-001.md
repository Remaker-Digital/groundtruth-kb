NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5667 Author-Provenance-Safe Scaffold Rename Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5667-author-provenance-safe-recovery
Version: 001
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]

## Claim

This fresh thread carries forward the independently accepted WI-5667 scope
without relying on the unusable historical chain. The prior thread
`gtkb-wi5667-scaffold-managed-skill-rename-recovery` reached GO v004, but a
fresh implementation-start attempt failed closed before mutation with:
`Status NEW has wrong or unreadable author role None` for its v001. This
proposal requests a new independently reviewed authority chain whose operative
proposal and future verdict have complete provenance.

After GO, a fresh PB claim, and a successful implementation-start packet, the
implementation may adopt only the declared 17-path scaffold/template slice.
The candidate bytes already present in the dirty worktree are evidence only
until those gates succeed.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667193` authorizes the renamed
managed scaffold outcome; `DELIB-202667194` requires exact isolation from
commingled work. No new owner decision is required.

## Specification Links

- GOV-DOCUMENT-AUTHOR-PROVENANCE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Prior Deliberations And Bridge Evidence

- `DELIB-202667193` — owner-directed gtkb-prefixed managed templates.
- `DELIB-202667194` — foreign hunks require exact isolation and ownership.
- `bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-003.md` — the
  prior complete proposal whose scope and hunk protocol are carried forward.
- `bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-004.md` — the
  independent GO that accepted that design but cannot itself pass the current
  implementation-start resolver because of v001 provenance.

## Owner Decisions / Input

No new owner decision is required. This proposal changes no approved outcome;
it restores executable provenance for the same bounded WI-5667 slice.

## Exact Doctor Hunk Ownership

The only `doctor.py` content owned by this recovery is six existing rename
substitutions from index blob `7087c8e47`:

1. `_check_skill_present`: `decision-capture` paths and diagnostic become
   `gtkb-decision-capture`.
2. `_check_bridge_propose_skill_present`: `bridge-propose` paths and diagnostic
   become `gtkb-bridge-propose`.
3. `_check_spec_intake_skill_present`: `spec-intake` paths and diagnostic
   become `gtkb-spec-intake`.

The separate `_check_skill_rename_reference_sweep` definition and its
`run_doctor()` registration are excluded WI-5668 evidence. They must remain
unstaged and uncommitted in this transaction.

## Implementation And Verification Plan

1. After independent GO, acquire the thread claim and require a successful
   `implementation_authorization.py begin` packet before protected mutation or
   staging. The exact gate failure that blocked the old chain must not recur.
2. Build and review an index-only patch against blob `7087c8e47` for only the
   six `doctor.py` substitutions. Run `git apply --cached --check`, then apply
   it to the index. Never stage the whole doctor file.
3. Prove the cached doctor diff contains the six rename substitutions and no
   `_check_skill_rename_reference_sweep` definition, text, or registration;
   prove the excluded evaluator remains in the unstaged diff.
4. Stage only the other declared template/test paths after exact-scope review.
   Abort if either scaffold-golden root or any undeclared path appears.
5. Run the focused scaffold/upgrade selectors named in the prior v003 proposal:
   all of `test_scaffold_skills.py`, the six bridge/spec-intake upgrade tests,
   the three managed-registry tests, and
   `test_doctor.py::test_check_rules_with_files` under the groundtruth-kb
   rootdir/testpaths configuration.
6. Run Ruff check and format-check on `doctor.py` and the four declared tests,
   plus scoped diff, staged-set, applicability, and clause preflights. Commit
   only the authorized index and file a strict committed implementation report.

## Quarantine And Explicit Exclusions

- Never read, modify, stage, restore, rebaseline, attribute, or commit
  `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**` or
  `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**`.
- Never invoke `scripts/_capture_scaffold_golden.py`, including help or dry-run.
- Do not modify, stage, format, or commit the WI-5668 evaluator or registration.
- Do not modify retained bare templates, WI-5640 migration policy, generated
  adapters, or canonical runtime skills.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Provenance and bridge authority | Fresh-chain GO, PB claim, successful packet | Operative proposal/verdict provenance is readable and implementation authority is issued. |
| Managed scaffold consistency | Focused scaffold, upgrade, registry, and doctor tests | Declared gtkb-prefixed managed artifacts agree. |
| Foreign ownership | Cached/unstaged doctor assertions | Only six rename substitutions are committed; WI-5668 evaluator remains unstaged. |
| Quarantine boundary | Exact staged path scan | Neither scaffold-golden root is read, changed, staged, or committed. |

## Acceptance Criteria

- A fresh dual-agent scaffold/upgrade emits the declared gtkb-prefixed managed
  artifacts.
- Registry, templates, doctor checks, and declared tests agree on canonical
  names.
- Commit evidence contains only the six specified doctor substitutions plus
  the other declared target paths.
- Both scaffold-golden roots and all WI-5668 evaluator bytes remain excluded.
- A committed report receives independent LO terminal review.

## Risks And Rollback

The main risks are reusing non-executable historical authority and staging the
mixed doctor file wholesale. The fresh chain, start packet, index-only patch,
and dual staged/unstaged assertions fail closed. Rollback is a separately
governed revert of only a later scoped commit.

## Recommended Commit Type

fix
