NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T13-33-47Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Implementation Proposal — WI-5667 managed scaffold skill-name migration

bridge_kind: prime_proposal
Document: gtkb-wi5667-scaffold-managed-skill-rename
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667

target_paths: ["config/file-reference-migration/wi5640.toml", "groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/gtkb-bridge/helpers/show_thread_bridge.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

WI-5667 corrects the adopter-facing half of the completed canonical skill rename. The managed artifact registry will emit `gtkb-*` paths for exactly the eleven registered skill artifacts: two decision-capture files, two bridge-propose files, two spec-intake files, and five bridge files. The matching templates and dual-agent golden output are materialized at the corresponding `gtkb-*` locations. The existing bare template paths are retained inertly under the WI-5640 retention policy; they are not deleted, moved, or used by scaffold or upgrade after the registry update.

`baseline-audit` is explicitly outside this slice because it has no corresponding canonical `gtkb-baseline-audit` skill. The standalone release-candidate template is not a registry-managed dual-agent scaffold artifact and is outside this owner-directed managed cluster.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667193` directs the scaffold/template/managed-artifacts cluster to adopt `gtkb-*`; the active PAUTH authorizes this bounded reference correction. No new behavior, deployment, credential, or formal-artifact mutation is proposed.

## In-Root Placement Evidence

All declared paths are under `E:\GT-KB`. The golden files are in-root package test fixtures; no adopter checkout or Agent Red dependency is required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires the numbered proposal, independent review, and later implementation-start gate.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve registry, migration policy, golden fixture, and test evidence as governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this concrete source and test scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the registry/scaffold/upgrade/doctor/migration verification below before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds the PAUTH, project, work item, and target paths.
- `GOV-STANDING-BACKLOG-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — retain WI-5667 as an independently reviewed backlog slice.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keeps the work within the GT-KB platform template and test boundary.

## Prior Deliberations

- `DELIB-202667193` — owner decision requiring scaffold names to be renamed to `gtkb-*`, while retaining normal bridge review and verification gates.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — owner direction to process WI-5667 under its existing project authorization.
- `config/file-reference-migration/wi5640.toml` — the governed retention and physical-alias policy: materialize canonical destinations while retaining old source paths inertly.

## Owner Decisions / Input

- `DELIB-202667193` supplies the owner-selected outcome: adopters receive `gtkb-*` managed skills rather than bare-name skills.
- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION` explicitly includes WI-5667. A fresh independent manual Loyal Opposition review is required; no further owner decision is asserted.

## Source-of-Record and Migration Map

| Artifact family | Current managed records | Canonical destination | Owner / parity route |
| --- | --- | --- | --- |
| decision-capture | `skill.decision-capture.skill-md`, `skill.decision-capture.helper` | `templates/skills/gtkb-decision-capture/**` → `.claude/skills/gtkb-decision-capture/**` | `managed-artifacts.toml`; registry-driven scaffold and upgrade; scaffold/upgrade/doctor tests |
| bridge-propose | `skill.bridge-propose.skill-md`, `skill.bridge-propose.helper` | `templates/skills/gtkb-bridge-propose/**` → `.claude/skills/gtkb-bridge-propose/**` | `managed-artifacts.toml`; WI-5640 physical alias policy; golden fixture regeneration |
| spec-intake | `skill.spec-intake.skill-md`, `skill.spec-intake.helper` | `templates/skills/gtkb-spec-intake/**` → `.claude/skills/gtkb-spec-intake/**` | `managed-artifacts.toml`; registry-driven scaffold and upgrade; scaffold/upgrade/doctor tests |
| bridge | `skill.bridge.skill-md`, `skill.bridge.scan-helper`, `skill.bridge.revise-helper`, `skill.bridge.impl-report-helper`, `skill.bridge.show-thread-helper` | `templates/skills/gtkb-bridge/**` → `.claude/skills/gtkb-bridge/**` | `managed-artifacts.toml`; WI-5640 physical alias policy; golden fixture regeneration |

`scaffold.py` and `upgrade.py` consume this registry generically and therefore require no direct behavior change. `doctor.py` has three explicit presence checks that must update their names and required lists. The fixture capture route is `scripts/_capture_scaffold_golden.py`; it produces the declared dual-agent snapshot paths only after scaffold output is verified.

## Proposed Implementation

1. Extend `config/file-reference-migration/wi5640.toml` with the physical-alias rows required for the four managed families and their dual-agent golden snapshots. Each row uses materialize-copy or generator-regenerate and keeps the bare source path retained; this slice never deletes or moves a legacy template.
2. Materialize the thirteen canonical `gtkb-*` template files from their existing corresponding template content. Update the eleven managed-artifact rows so both `template_path` and emitted `.claude/skills` `target_path` use the canonical names.
3. Update doctor’s decision-capture, bridge-propose, and spec-intake presence checks to require and name their `gtkb-*` emitted paths. The bridge managed artifact is verified through registry/scaffold/upgrade coverage rather than a new redundant doctor check.
4. Update scaffold, upgrade, registry, doctor, migration-policy, and dual-agent golden-fixture tests to assert the new emitted paths and retain legacy paths only as inert migration sources.

## Explicit Non-Scope

- Canonical `.claude/skills/**` content repairs (WI-5662), generated adapter regeneration (WI-5663), rules/config mirrors (WI-5664), and broad test-reference repair (WI-5665).
- `baseline-audit`, the unregistered release-candidate template, bridge audit history, archive/RETIRED/BARRED material, and any adopter project.
- Deleting, moving, or renaming retained legacy paths; WI-5640 policy requires retention and this proposal uses new canonical materializations instead.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| registry authority and scaffold/upgrade lifecycle | `groundtruth-kb/.venv/Scripts/python.exe -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_scaffold_skills.py groundtruth-kb/tests/test_upgrade_skills.py groundtruth-kb/tests/test_managed_registry.py -q --tb=short` | Fresh dual-agent scaffold and upgrade output only `gtkb-*` managed paths. |
| doctor path presence | `groundtruth-kb/.venv/Scripts/python.exe -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_doctor.py -q --tb=short` | Presence checks demand the renamed paths and provide actionable messages. |
| WI-5640 retention/materialization policy | `python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short` plus `python scripts/gtkb_file_reference_migration.py verify` | Physical aliases and golden regeneration route are valid; legacy sources remain retained. |
| deterministic fixture output | rerun `scripts/_capture_scaffold_golden.py` by its documented scoped fixture route, then inspect only the eleven declared golden paths | Golden files match the renamed scaffold output with no undeclared fixture changes. |
| bridge linkage and verification gate | candidate and live applicability/clause preflights | No required/advisory specification gaps and no blocking clause gap. |

Before the implementation report, run `ruff check` and `ruff format --check` on every changed Python source and test file.

## Acceptance Criteria

1. A fresh dual-agent scaffold and `gt project upgrade --apply` materialize all eleven managed skill artifacts under `gtkb-*` names.
2. Registry template paths, emitted paths, doctor presence checks, and the dual-agent golden fixture agree on the canonical names.
3. Retained bare templates are not used by the managed registry and are preserved only under explicit WI-5640 retention rows.
4. The exact source, test, fixture, and policy paths declared above are the only paths attributed to this slice.

## Risk and Rollback

The primary risk is accidentally deleting retained legacy templates or leaving a registry/template/golden mismatch that causes new adopters to receive old names. Materialize-copy retention, registry-driven checks, and the golden fixture bound that risk. If rollback is needed, revert only the declared registry, policy, canonical-template, doctor, test, and fixture paths under separate governed authority, then rerun the same lifecycle checks. Bridge artifacts and the owner decision remain append-only.

## Files Expected To Change

The exact `target_paths` declaration is the complete implementation boundary.

## Recommended Commit Type

`fix`
