REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T16-30-55Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default;thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5668 Deterministic Dual-Authority Baseline Prerequisite

bridge_kind: prime_proposal
Document: gtkb-wi5668-skill-rename-sweep-completion-gate
Version: 011
Responds to: bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-010.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668
target_paths: ["config/file-reference-migration/wi5640.toml", "scripts/gtkb_file_reference_migration.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py"]
implementation_scope: configuration | source | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Resolve the v010 baseline-contract contradictions without implementing the WI-5668 doctor or release gate. This prerequisite retains the three-path boundary, makes the policy preflight's shared full-observation publication retry deterministically on transient Windows `PermissionError`, adds focused regression coverage, and captures the final post-format SHA-256 values for all three tracked files.

The later completion-gate proposal must consume two distinct authorities: artifact membership from `config/registry/sot-artifacts.toml` through `groundtruth_kb.project.sot_registry`, and mapping/alias/disposition policy from `config/file-reference-migration/wi5640.toml`. It must use `config/agent-control/gtkb-skill-rename-map.toml` if rename mapping is needed. It must not use `git ls-files` as its universe or retained `config/agent-control/skill-rename-map.toml` as authority.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE`, WI-5668, v010's two findings, and the three declared paths bound this prerequisite. A separate proposal remains required for doctor WARN and release-gate FAIL implementation.

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

- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE` - binds the future evaluator to separate SoT registry and WI-5640 policy authorities, canonical rename-map input, WARN doctor, and FAIL release-gate semantics.

## Owner Decisions / Input

- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE` is the owner decision for this prerequisite and the later evaluator's authority boundary.

## Findings Addressed

### P1 - Exact recorded bytes conflicted with formatter success

Response: formatting is explicitly authorized for the two Python targets. The proposal no longer claims their pre-format bytes are immutable. After formatting, the implementation report must record final SHA-256 values for all three paths and commit exactly those bytes. `wi5640.toml` must retain its semantic mapping, alias, and disposition policy; its final hash is recorded rather than assumed.

### P1 - Shared full-observation replacement was not reproducible

Response: within `scripts/gtkb_file_reference_migration.py`, replace the single `os.replace(observation_temp, observation_path)` with a bounded deterministic retry helper. It retries only `PermissionError` from that final publication step using a documented fixed attempt schedule, preserves the same source/destination paths and content bytes, and raises a named migration error with attempts and path after exhaustion. It must not retry policy interpretation, alter artifact enumeration, silently discard a successful observation, or mutate any tracked registry/policy authority beyond this declared capture.

The focused test module must prove both transient recovery (one or more simulated `PermissionError` calls followed by success) and exhausted-retry failure with the named diagnostic. A fresh successful command must then publish the real observation without concurrent state contention.

## Scope And Explicit Exclusions

- Include exactly the three declared paths. No doctor, release-gate, registry reader, generated adapter, template, fixture, bridge detector, or canonical rename-map file may change.
- Do not alter `config/registry/sot-artifacts.toml` or `groundtruth_kb.project.sot_registry`; they are read-only future evaluator authority.
- Do not change WI-5640 policy semantics, policy-authorized migration mappings, or intentional negative fixture literals merely to obtain a zero future gate count.
- Do not add `git ls-files` enumeration, retained `skill-rename-map.toml` input, or a zero condition that treats policy-authorized aliases/fixtures as violations.
- Do not implement doctor WARN or release-gate FAIL code in this prerequisite.

## Specification-Derived Verification Plan

| Spec / governing surface | Command / assertion | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Acquire claim and current implementation authorization before edits; verify exact three-path commit. | No protected change without live authorization; no extra path staged. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5668-skill-rename-sweep-completion-gate` | No missing required/advisory specification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short` plus new transient/exhausted publication selectors. | Existing policy coverage and new retry regressions pass. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run policy preflight, record final hashes, and preserve distinct authority roles in implementation report. | Fresh preflight succeeds and evidence remains traceable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation report distinguishes this deterministic baseline from later doctor/release evaluator work. | No false gate-completion or terminal claim. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --check -- config/file-reference-migration/wi5640.toml scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py` | All changed paths are in-root and clean. |

## Commands To Run Before Reporting

    python scripts/gtkb_file_reference_migration.py preflight --project-root . --policy config/file-reference-migration/wi5640.toml
    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py
    git diff --check -- config/file-reference-migration/wi5640.toml scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5668-skill-rename-sweep-completion-gate
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5668-skill-rename-sweep-completion-gate

## Acceptance Criteria

- Only the three declared paths change and commit; their final post-format SHA-256 values are recorded in the implementation report.
- The policy preflight succeeds freshly after a simulated transient `PermissionError` retry is covered by a focused regression and exhausted retries produce a deterministic named failure.
- The focused migration-policy test suite, Ruff check/format, scoped diff check, and both bridge preflights pass.
- The implementation report explicitly preserves the two-authority design, canonical `gtkb-skill-rename-map.toml` correction, and later WARN-doctor/FAIL-release contract without claiming those gates are implemented.

## Risks And Rollback

Retrying the final publication can mask a persistent file lock if it is unbounded. The helper therefore uses a fixed, short attempt schedule and raises a named error when exhausted. Rollback is a governed revert limited to the three-file commit; it does not roll back policy mappings, registry authority, or a later evaluator proposal.

## Files Expected To Change

- `config/file-reference-migration/wi5640.toml`
- `scripts/gtkb_file_reference_migration.py`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`

## Recommended Commit Type

`fix`
