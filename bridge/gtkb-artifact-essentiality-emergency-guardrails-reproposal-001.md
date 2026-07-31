NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder session; replacement proposal for malformed artifact-essentiality GO

# NEW: Replacement emergency registry-first cleanup essentiality guardrails

bridge_kind: prime_proposal
Document: gtkb-artifact-essentiality-emergency-guardrails-reproposal
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-97538B
Related Work Item: WI-AUTO-SPEC-INTAKE-99A602
Supersedes malformed GO thread: bridge/gtkb-artifact-essentiality-emergency-guardrails-002.md

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/hygiene/strays.py", "scripts/hygiene/stray_detector.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_work_tree_stray_detector.py", "groundtruth.db"]
implementation_scope: emergency_guardrail
recommended_commit_type: fix

## Claim

Replace the original `gtkb-artifact-essentiality-emergency-guardrails` GO handoff with a mechanically startable proposal for the same emergency registry-first cleanup essentiality guardrail work. The original thread reached GO at `bridge/gtkb-artifact-essentiality-emergency-guardrails-002.md`, but implementation-start now refuses it because the approved proposal lacks the mandatory `## Requirement Sufficiency` section. This replacement preserves the original scope, owner authorization, target paths, and verification expectations while adding the missing mandatory authorization metadata.

## Owner Decisions / Input

- Owner decision captured as `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY`: implement immediately that the GT-KB tracked artifact list is the canonical authority for cleanup essentiality, and that Git tracked/ignored/untracked state must not decide whether a file is essential.
- Owner emergency input in that session: `.env.local` was deleted during cleanup, an older backup was manually restored, recent backups are unreliable because of directory-size bloat, and this remediation must be done now rather than deferred.
- Bounded authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701` permits config/source/test registry guardrails and registry projection sync only; it forbids credential lifecycle, deployment, force-push, destructive bulk cleanup, broad file deletion, and secret-value disclosure.

## Problem Statement

The cleanup/inventory stack failed to protect an essential local artifact because registry authority was not enforced as the first source of truth. The GT-KB tracked artifact list exists, but `.env.local` was not registered there, and at least one inventory-backed scan filtered registry-declared files through Git tracking. That makes Git tracking or ignore state an accidental essentiality gate.

Closed hygiene work did not solve this invariant: the stray CLI was verified as read-only and candidate-action-only, while the broader work-tree hygiene governance spec remained owner-blocked. This emergency proposal is intentionally narrower: preserve registered artifacts and make registry authority visible without exposing or changing credential values.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-97538b` already states that the tracked artifact list is canonical for cleanup essentiality and Git state cannot exclude registered artifacts. `SPEC-INTAKE-99a602` already requires fail-closed cleanup assumptions while reliable backup state is absent. The missing work is implementation of those existing requirements in the registry, inventory/string-scan, and stray-classification surfaces listed in `target_paths`.

## Proposed Implementation

1. Register `.env.local` as an active owner-managed local artifact in `config/registry/sot-artifacts.toml`, with preservation semantics that make path presence and essentiality visible without serializing credential values.
2. Remove Git tracking as an inclusion filter from registry-backed inventory/string scans. The registry must decide which artifact paths are in scope; Git may remain diagnostic metadata, but it must not exclude registered artifacts.
3. Teach stray/cleanup classification to preserve registered artifacts before applying tracked/untracked/stale heuristics. Registered artifacts must not be emitted as deletion candidates solely because they are ignored, untracked, large, or old.
4. Add focused regression coverage proving a gitignored, registry-declared local artifact is included/preserved and that Git status is not used as essentiality authority.
5. Run registry projection sync so `groundtruth.db` matches `config/registry/sot-artifacts.toml`, then verify registry validation and focused tests.

## Explicit Non-Goals

- Do not print, copy, normalize, rotate, validate, or otherwise mutate credential values.
- Do not perform destructive cleanup or broad file deletion.
- Do not resolve the entire historical work-tree hygiene governance thread beyond this emergency guardrail.
- Do not treat Git ignored, untracked, or tracked status as artifact essentiality authority.

## Specification Links

- `SPEC-INTAKE-97538b` - tracked artifact list is canonical for cleanup essentiality; Git state cannot exclude registered artifacts.
- `SPEC-INTAKE-99a602` - cleanup must fail closed while no reliable GT-KB backup exists.
- `GOV-ENV-LOCAL-AUTHORITY-001` - `.env.local` is owner-managed local credential/config state; this proposal preserves path authority without exposing values.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation report must cite fresh registry, projection, and test reads.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - no protected implementation starts until this replacement receives GO and a matching work-intent claim.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner emergency input that crosses into a requirement/plan is preserved as governed bridge state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact correction is routed through bridge/spec/test evidence rather than scratch memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - cleanup-risk findings trigger durable artifact lifecycle handling.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal carries concrete project authorization, project, work item, target paths, and spec links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation-targeting proposal includes PAUTH/project/WI metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map each blocking spec to executed verification evidence.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| `SPEC-INTAKE-97538b` | Tests prove the tracked artifact list is canonical for cleanup essentiality and Git state cannot exclude registered artifacts. |
| `SPEC-INTAKE-99a602` | Tests and report evidence prove cleanup assumptions fail closed; no destructive cleanup runs. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Registry/list evidence shows `.env.local` path authority without credential values. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Registry projection sync and validation evidence are captured in the implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this mapping plus exact command results. |

Planned verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry list --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry validate --json
```

Manual credential-safety check: no test output, report, or bridge artifact may contain credential values from `.env.local`.

## Prior Deliberations

- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner emergency decision authorizing immediate registry-first cleanup essentiality remediation.
- `INTAKE-eb0bbcad` / `SPEC-INTAKE-97538b` - tracked artifact list is canonical for cleanup essentiality.
- `INTAKE-b44907bd` / `SPEC-INTAKE-99a602` - no reliable GT-KB backup before destructive cleanup.
- `DELIB-20260809` - approved the five-slice WI-4356 work-tree hygiene plan.
- `DELIB-20260867` - owner AUQ approval for WI-4356 implementation authorization.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` - VERIFIED read-only stray CLI; destructive cleanup deferred.
- `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-044.md` - latest blocker record for the unresolved cleanup governance spec.
- `bridge/gtkb-artifact-essentiality-emergency-guardrails-002.md` - original GO now superseded because mandatory Requirement Sufficiency metadata is absent.

## Risk And Rollback

Risk is low to moderate: the change narrows cleanup behavior and broadens inventory inclusion to registered artifacts. Rollback is to revert the source/config/test changes and rerun registry projection sync, but rollback would restore the known failure mode that allowed essential gitignored local state to be treated as disposable.


## Pre-Filing Preflights

Applicability preflight (candidate content before filing):

- exit_code: 0
- preflight_passed: True
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:a1e3cccb078096640341144838113a780ddcf00b3c54e8fe9be973bf25e7b100

Clause preflight (candidate content before filing):

- exit_code: 0
- blocking_gaps: 0

## Acceptance Criteria

- The replacement proposal receives a fresh independent GO or NO-GO verdict with current mandatory bridge metadata.
- Implementation starts only from the replacement GO and a matching work-intent claim.
- `.env.local` path authority is represented without disclosing or mutating credential values.
- Focused registry, inventory, and stray-classification tests pass.

## Files Expected To Change

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py`
- `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`
- `scripts/hygiene/stray_detector.py`
- `groundtruth-kb/tests/test_inventory_string_scan.py`
- `platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py`
- `platform_tests/scripts/test_hygiene_strays_cli.py`
- `platform_tests/scripts/test_work_tree_stray_detector.py`
- `groundtruth.db`

## Recommended Commit Type

`fix`
