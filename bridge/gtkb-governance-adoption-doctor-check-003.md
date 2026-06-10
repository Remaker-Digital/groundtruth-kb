REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Governance-Adoption Doctor Check (GTKB-GOV-003) - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-governance-adoption-doctor-check
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Session: 019e425a-79e8-7351-80bc-38c73b0b9429
Responds-To: `bridge/gtkb-governance-adoption-doctor-check-002.md`

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-003

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_adoption_drift.py"]

## Revision Claim

This revision rebases the adopter-drift doctor check on the existing managed-artifact registry surface instead of the unresolved Tier A registry design. The proposed implementation consumes `groundtruth_kb.project.managed_registry.artifacts_for_doctor()`, `find_artifact_by_id()`, and the existing `FileArtifact` / `SettingsHookRegistration` / `GitignorePattern` record model already imported by `doctor.py`.

No new registry API, no parallel manifest, and no `load_tier_a_registry()` function are proposed.

## Specification Links

- GOV-GTKB-ADOPTION-ENFORCEMENT-001
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for GTKB-ADOPTER-EXPERIENCE batch authorization and GTKB-GOV-003.
- `DELIB-1242`, `DELIB-1243`, `DELIB-1244` - prior Tier A adoption / managed-artifact context surfaced by Loyal Opposition search.
- `DELIB-1074` - prior Agent Red governance adoption drift and release-readiness context.
- `DELIB-0758`, `DELIB-1207` - mass-adoption readiness context.

## Owner Decisions / Input

No new owner decision is required. This revision preserves the S350 owner-authorized work item and narrows the implementation design to the already-approved managed-registry API that Loyal Opposition identified.

## Findings Addressed

### F1 - Proposal depends on an unresolved Tier A registry surface

Response: Removed the Tier A registry dependency. The implementation will not call or create `load_tier_a_registry()`. It will use the current managed-artifact registry at `groundtruth-kb/templates/managed-artifacts.toml` through `artifacts_for_doctor(profile, ...)` and `find_artifact_by_id(...)`.

### F2 - Current doctor already consumes the managed-registry API

Response: IP-1 now extends the current doctor architecture. The check will operate over the same artifact classes already imported in `doctor.py`: `FileArtifact`, `SettingsHookRegistration`, and `GitignorePattern`. Status names are aligned with the existing doctor `ToolCheck` model: `pass`, `warning`, and `fail`.

### F3 - Silent skip on missing registry weakens the default doctor signal

Response: Silent skip is removed. If the registry cannot be loaded, the doctor must emit a required `ToolCheck` named `Managed artifact drift` with `status='fail'`, `found=False`, and a message naming the registry load error. If a profile has no doctor-required managed artifacts, the doctor emits a non-required `info` check explaining that no managed-artifact drift checks apply for that profile.

### F4 - Verification plan omits existing managed-registry and doctor parity tests

Response: The verification plan now includes the new adoption-drift tests plus existing managed-registry, doctor, and no-parallel-manifest tests.

### F5 - Applicability preflight found uncited advisory specs

Response: Added explicit citations for `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Proposed Scope

### IP-1: Managed artifact drift doctor check

In `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, add a doctor check that compares doctor-required managed artifacts against their registered templates and structured registration expectations.

Implementation shape:

- Add `_file_hash(path: Path) -> str` and `_template_hash(template_relative: str) -> str | None` local helpers or reuse an equivalent existing internal pattern without importing private upgrade internals.
- Add `_check_managed_artifact_drift(target: Path, profile_name: str) -> ToolCheck`.
- For `FileArtifact` rows from `artifacts_for_doctor(profile_name, class_ in {"hook", "rule", "skill", "file"})`:
  - Missing target path: `fail` when `ownership.upgrade_policy` is `overwrite` or `structured-merge`; otherwise `warning`.
  - Existing target equals template hash: no drift.
  - Existing target differs from template:
    - `warning` when `ownership.adopter_divergence_policy == "warn"` or `ownership.upgrade_policy` is `preserve` / `adopter-opt-in` / `transient`.
    - `fail` when `ownership.adopter_divergence_policy == "error"`.
- For `SettingsHookRegistration` rows from `artifacts_for_doctor(profile_name, class_="settings-hook-registration")`, reuse the existing `_check_settings_hook_registration_drift(...)` helper instead of inventing a second settings parser.
- For `GitignorePattern` rows from `artifacts_for_doctor(profile_name, class_="gitignore-pattern")`, check that the configured pattern is present in `.gitignore`; report `warning` or `fail` according to ownership divergence policy.
- Return a single aggregate `ToolCheck` named `Managed artifact drift` summarizing counts by category: current, missing, drifted, registration-missing, gitignore-missing.

Wire the aggregate check into default `gt project doctor` output for bridge-enabled profiles after the current managed-registry checks. The existing specialized scanner-safe-writer and settings-hook checks remain in place; this aggregate check is an adoption-drift summary, not a replacement for targeted diagnostic checks.

### IP-2: Focused tests

Add `groundtruth-kb/tests/test_doctor_adoption_drift.py` covering:

- clean managed artifacts report `pass`;
- missing managed file reports `fail`;
- modified file with `adopter_divergence_policy="warn"` reports `warning`;
- modified file with `adopter_divergence_policy="error"` reports `fail`;
- missing settings hook registration is included in the aggregate;
- missing gitignore pattern is included in the aggregate;
- registry load failure produces an explicit `fail`, not a silent skip;
- profile with no doctor-required artifacts produces an `info` check.

Tests may monkeypatch `artifacts_for_doctor()` and template directory resolution to keep fixtures small and avoid mutating global registry state.

## Scope Boundaries

- No changes to `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`.
- No changes to `groundtruth-kb/templates/managed-artifacts.toml`.
- No new Tier A registry loader.
- No source mutations outside `doctor.py` and the new focused test file.
- Existing managed-registry and no-parallel-manifest tests are verification targets only, not edit targets.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| Doctor consumes the canonical managed registry, not a parallel registry | `python -m pytest groundtruth-kb/tests/test_doctor_adoption_drift.py -q --tb=short` |
| Registry loader invariants remain intact | `python -m pytest groundtruth-kb/tests/test_managed_registry.py -q --tb=short` |
| Doctor-required profile behavior remains compatible | `python -m pytest groundtruth-kb/tests/test_doctor.py -q --tb=short` |
| No parallel manifest introduced | `python -m pytest groundtruth-kb/tests/test_no_parallel_manifests.py -q --tb=short` |
| Formatting and lint for changed files | `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_adoption_drift.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

1. `gt project doctor` includes an explicit managed-artifact drift aggregate check for applicable profiles.
2. The check is sourced from `artifacts_for_doctor()` / `find_artifact_by_id()` and does not create or consume a new registry API.
3. Missing registry/load failures surface as explicit doctor failures, not silent skips.
4. Focused tests and the existing managed-registry / doctor / no-parallel-manifest verification lanes pass.
5. Applicability and clause preflights pass before filing and after filing.

## Risk And Rollback

Risk: the aggregate drift check may duplicate detail already emitted by specialized doctor checks. Mitigation: keep the new check summary-level and preserve specialized checks unchanged.

Risk: content-hash comparison could classify intentional local customization as drift. Mitigation: use `ownership.upgrade_policy` and `ownership.adopter_divergence_policy` to choose warning versus failure.

Rollback: remove `_check_managed_artifact_drift`, remove its call in doctor default output, and delete the focused test file. Existing doctor behavior and managed-registry behavior remain unchanged.

## Pre-Filing Preflight Subsection

To be executed by the bridge revision helper before live filing:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-governance-adoption-doctor-check --content-file .gtkb-state\bridge-revisions\drafts\gtkb-governance-adoption-doctor-check-003.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-governance-adoption-doctor-check --content-file .gtkb-state\bridge-revisions\drafts\gtkb-governance-adoption-doctor-check-003.md`

End of revision.
