REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-54-35Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5668 dual-authority baseline before completion gate

bridge_kind: prime_proposal
Document: gtkb-wi5668-skill-rename-sweep-completion-gate
Version: 009
Responds to: bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-008.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668

target_paths: ["config/file-reference-migration/wi5640.toml", "scripts/gtkb_file_reference_migration.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py"]

implementation_scope: configuration | source | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Establish the governed, tracked baseline required for the owner-selected
dual-authority WI-5668 completion design. This prerequisite captures the
existing WI-5640 migration policy, interpreter, and focused test suite at their
observed bytes. It does not alter doctor.py, release_candidate_gate.py, any
release-gate test, or the superseded version-006 GO target set.

## Claim

Prime Builder proposes a baseline-and-scope-binding transaction only. The
tracked config/registry/sot-artifacts.toml and its tracked reader
groundtruth-kb/src/groundtruth_kb/project/sot_registry.py remain read-only
authorities. The three declared untracked files are captured without semantic
change so a later reviewed gate can consume both authorities safely.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE
binds WI-5668 to the SoT artifact universe plus WI-5640
alias/disposition policy, with WARN doctor and failing release gate semantics.
The former skill-rename-map-only evaluator is expressly superseded.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Authority And Ownership Matrix

| Role | Path | Tracking state and SHA-256 | Direction / disposition |
| --- | --- | --- | --- |
| Artifact universe | config/registry/sot-artifacts.toml via groundtruth_kb.project.sot_registry | tracked; reader SHA-256 611d03002a0729c6933ef822d2afb5ed47f8a34a61815678b0a8dc55d567943d | Stable read-only source of truth; no mutation in this prerequisite. |
| Mapping, alias forms, dispositions | config/file-reference-migration/wi5640.toml | untracked; b468b7b61085b346af3cbdd7e4981b0a1bd3222ab5f33c55724d046404d3a231 | Capture unchanged as the second authority. It is not an artifact registry. |
| Policy interpreter | scripts/gtkb_file_reference_migration.py | untracked; 76e74c4891ec10f029fe78802222f82311a0014a4dc30fb9eba8a245c598c3e1 | Capture unchanged; its preflight is the executable policy parse/coverage check. |
| Focused regression suite | platform_tests/scripts/test_gtkb_file_reference_migration.py | untracked; c7ea894298994163b27f89ae76f58c89767a0590a2f4603df718c7a1532a84cf | Capture unchanged; it covers direct, absolute, URI, segmented, structured, glob, regex, and SQLite policy forms. |

No retained config/agent-control/skill-rename-map.toml input is allowed in the
future evaluator. When a rename map is needed, it must use the canonical
config/agent-control/gtkb-skill-rename-map.toml.

## Observed Baseline Evidence

    python scripts/gtkb_file_reference_migration.py preflight --project-root . --policy config/file-reference-migration/wi5640.toml
    exit 0

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short
    52 passed, 1 warning

These observations establish the existing bytes and behavior only. They do not
claim that WI-5668's eventual doctor or release gate has been implemented.

## Scope And Explicit Exclusions

- Include exactly the three declared baseline files in a dedicated governed
  commit after fresh GO and implementation claim.
- Do not modify the tracked SoT registry or reader.
- Do not modify doctor, release gate, generated adapters, templates, fixtures,
  scratch captures, or unrelated migration consumers.
- Do not use raw git ls-files as the future evaluator's artifact universe.
- Do not make a zero-hit condition fail on policy-authorized mappings or
  intentional negative-fixture literals.

## Specification-Derived Verification Plan

    python scripts/gtkb_file_reference_migration.py preflight --project-root . --policy config/file-reference-migration/wi5640.toml
    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py
    git diff --check -- config/file-reference-migration/wi5640.toml scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5668-skill-rename-sweep-completion-gate
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5668-skill-rename-sweep-completion-gate

## Acceptance Criteria

- Exactly the three declared untracked files are captured, byte-identical to the
  recorded hashes, with no unrelated path staged.
- The policy preflight, all 52 focused tests, Ruff lint/format, and diff check
  pass.
- The subsequent completion-gate proposal may cite both authorities by their
  distinct roles, but this baseline does not authorize gate code.
- Doctor WARN and release-gate FAIL semantics remain the owner-selected
  completion contract for that later proposal.

## Cross-Harness Disposition

The baseline is repository policy, interpreter, and tests. It does not alter
any harness adapter, hook, generated template, dispatcher route, or runtime
behavior. A later evaluator proposal must cover registry-declared artifacts
across all included harness and physical roots.

## Risks And Rollback

The risk is wrongly treating a migration policy as a sole registry or changing
its semantics during capture. Hash equality, read-only SoT authority, and the
focused policy suite fail closed. Rollback is a later governed revert of only
the dedicated three-file baseline commit.

## Owner Decisions / Input

- DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE records the owner
  binding, authority separation, canonical map correction, and WARN/FAIL
  severity contract.

## Recommended Commit Type

chore
