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


# Deterministic Dual-Authority Baseline Recovery — WI-5668

bridge_kind: prime_proposal
Document: gtkb-wi5668-dual-authority-baseline-recovery
Version: 001
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668

target_paths: ["config/file-reference-migration/wi5640.toml", "scripts/gtkb_file_reference_migration.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py"]

## Claim

The historical WI-5668 chain cannot issue an implementation packet because its
first proposal has unreadable PB author-role metadata. This fresh recovery
reissues only the v011 baseline prerequisite: deterministic retry of the final
full-observation publication and focused regression coverage. It does not
implement the doctor WARN or release-gate FAIL evaluator.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE`, WI-5668, and the active PAUTH define this exact three-path baseline. The later evaluator requires its own separate proposal and review.

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

- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE` — SoT registry membership, WI-5640 mapping authority, canonical rename map, WARN doctor, and FAIL release gate are distinct controls.

## Owner Decisions / Input

No new owner decision is required. This recovery preserves the owner-selected
dual-authority design and does not treat migration policy/test fixture literals
as unresolved reference violations.

## Dual-Authority Boundary

- Artifact universe for the later evaluator comes from `config/registry/sot-artifacts.toml` through `groundtruth_kb.project.sot_registry`.
- Mapping, aliases, and dispositions come from `config/file-reference-migration/wi5640.toml`.
- Any rename mapping uses `config/agent-control/gtkb-skill-rename-map.toml`, never the retained obsolete `skill-rename-map.toml`.
- This baseline must not enumerate with `git ls-files`, alter registry membership, change mapping semantics, or implement a zero-count gate.

## Proposed Scope

1. In `scripts/gtkb_file_reference_migration.py`, retry only the final `os.replace(observation_temp, observation_path)` publication when it raises `PermissionError`. Use a fixed bounded schedule; preserve paths and bytes; raise a named diagnostic with attempts and path after exhaustion.
2. In the focused test module, prove transient recovery and exhausted retry. Preserve all intentional WI-5640 policy mappings, aliases, dispositions, and negative fixture literals.
3. Record final post-format SHA-256 values for all three declared files. No doctor, release workflow, registry reader, map, generated adapter, template, fixture, or bridge detector is a target.

## Explicit Exclusions

- Do not modify `groundtruth-kb/src/groundtruth_kb/project/doctor.py` or `.github/workflows/release-candidate-gate.yml`.
- Do not modify `config/registry/sot-artifacts.toml`, `groundtruth_kb.project.sot_registry`, or either skill-rename map.
- Do not change WI-5640 policy semantics or fixtures to manufacture a future zero state.
- Do not call the pre-existing detector implementation evidence or terminal closure proof.

## Implementation And Verification Plan

1. After independent GO, acquire claim and issue `implementation_authorization.py begin` for this recovery; abort before any staged change on failure.
2. Run policy preflight, focused migration tests including transient/exhausted selectors, Ruff check/format-check, scoped diff check, and bridge/clause preflights.
3. Verify the cached path set is exactly the three declared paths, record their final SHA-256 values, commit, and file a non-terminal report that repeats the dual-authority/exclusion boundary.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge authority | Fresh recovery GO, claim, and packet | No protected change begins from invalid history. |
| Publication reliability | Focused transient and exhausted `PermissionError` tests | Bounded recovery succeeds transiently and reports deterministic exhaustion. |
| Policy integrity | Existing focused migration suite and policy preflight | Authority mappings/fixtures are retained unchanged except the scoped retry support. |
| Scope isolation | Cached path list, hashes, and `git diff --check` | Exactly three paths; evaluator and authority inputs untouched. |
| Future evaluator correctness | Report records dual authorities and separate follow-on | No false completion gate is claimed. |

## Acceptance Criteria

- Only the three declared policy/source/test paths are committed.
- Final observation publication handles transient locking deterministically and fails loudly after bounded exhaustion.
- Policy preflight, focused migration suite, Ruff, scoped diff, and both bridge preflights pass.
- The implementation report preserves the dual-authority design and expressly leaves doctor WARN/release FAIL to a separate proposal.

## Risks And Rollback

Unbounded retries could hide a persistent lock; the schedule is fixed and
diagnostic. A later rollback is an exact three-file revert. It does not change
policy, registry, fixture, evaluator, or historical bridge artifacts.

## Recommended Commit Type

fix
