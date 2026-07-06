NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3821-e2fc-75d2-814f-2a3ec0f71244
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB
Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-5044

# GT-KB Bridge Implementation Report - WI-5044 Watchdog Restore-Action Registry - 003

bridge_kind: implementation_report
Document: gtkb-wi5044-watchdog-restore-action-registry
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5044-watchdog-restore-action-registry-002.md
Approved proposal: bridge/gtkb-wi5044-watchdog-restore-action-registry-001.md
Recommended commit type: feat:

## Implementation Claim

Implemented the restore-action metadata surface for the platform SoT registry.

- `config/registry/sot-artifacts.toml` now declares `restore_action` on all 25 shipped SoT records.
- `groundtruth_kb.project.sot_registry` now parses and validates restore actions, exposes them on `SoTArtifact`, includes them in parity comparisons, and preserves them through `sync_projection`.
- Existing projection tables that predate the `restore_action` column remain readable through deterministic inference from existing backup/versioning metadata.
- `sync_projection` now materializes the `restore_action` column before writing projected rows, so future authorized registry syncs persist the field.
- Added spec-derived tests for shipped metadata coverage, invalid-action rejection, legacy projection upgrade behavior, live read-only registry parity, and existing backward compatibility.

No live `groundtruth.db` sync was run by this implementation. The approved target paths and project PAUTH do not authorize direct canonical-store mutation. The read-only `gt registry validate --json` command reports the live TOML/projection pair as in sync through the backward-compatible projection inference path, and temp-DB tests verify that an authorized future sync materializes the generated projection column.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-SOT-SINGLETON-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. This work was implemented under `PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION` and owner decisions `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` and `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED`.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - owner authorized the full watchdog project.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - owner selected tiered safe-auto / canonical-fail-loud behavior.
- `bridge/gtkb-wi5044-watchdog-restore-action-registry-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5044-watchdog-restore-action-registry-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | `platform_tests/scripts/test_gtkb_service_sot_restore_registry.py` verifies registry records now expose restore-action metadata consumable by the watchdog family. |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Restore actions are explicit enum values (`manual`, `visibility_only`, `git_restore`, `membase_export_restore`, `regenerate_from_source`, `ensure_alive`, `noop`) and invalid actions fail load-time validation. |
| `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | `groundtruth-kb/tests/test_sot_registry.py` and the new platform test assert all shipped records declare valid restore actions. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` / `GOV-SOT-SINGLETON-001` | `gt registry validate --json` reports `in_sync: true`; temp-DB tests show `sync_projection` adds and preserves the generated projection column. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Validation evidence comes from fresh `load_toml`, projection reads, and `gt registry validate`; no cached registry summary was used. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- <approved target paths>` shows only root-contained approved target paths for this WI, plus the new approved platform test file. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Work was performed after a live GO claim and successful implementation authorization packet `sha256:e12fdbc6a6632c8057a9e4a3e886c515ddefda05cf98570a85c39b1e7e3edf88`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, format, and read-only registry parity commands all passed; exact command summaries are below. |
| `GOV-STANDING-BACKLOG-001` / artifact-oriented governance specs | Report keeps `WI-5044`, project authorization, GO verdict, and implementation evidence linked in the bridge chain. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-wi5044-watchdog-restore-action-registry --ttl-seconds 2400` - acquired live Prime Builder implementation claim.
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5044-watchdog-restore-action-registry` - passed; packet `sha256:e12fdbc6a6632c8057a9e4a3e886c515ddefda05cf98570a85c39b1e7e3edf88`.
- `python -m pytest groundtruth-kb\tests\test_sot_registry.py platform_tests\scripts\test_check_sot_registry_completeness.py platform_tests\scripts\test_gtkb_service_sot_restore_registry.py groundtruth-kb\tests\test_sot_registry_forbidden_substitutes.py -q --tb=short` - 40 passed.
- `python -m ruff check groundtruth-kb\src\groundtruth_kb\project\sot_registry.py groundtruth-kb\tests\test_sot_registry.py platform_tests\scripts\test_check_sot_registry_completeness.py platform_tests\scripts\test_gtkb_service_sot_restore_registry.py` - passed.
- `python -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\sot_registry.py groundtruth-kb\tests\test_sot_registry.py platform_tests\scripts\test_check_sot_registry_completeness.py platform_tests\scripts\test_gtkb_service_sot_restore_registry.py` - passed.
- `python -c "from pathlib import Path; from groundtruth_kb.project.sot_registry import load_toml, default_registry_path; records=load_toml(default_registry_path()); print(len(records)); print(sorted({r.restore_action for r in records}))"` - printed `25` and all seven valid action classes.
- `gt registry validate --json` - printed `in_sync: true`, `toml_count: 25`, `projection_count: 25`, and no field divergences.

## Observed Results

- All 25 shipped SoT registry records load with explicit `restore_action` metadata.
- Invalid restore actions raise `InvalidSoTRecord`.
- `restore_action` participates in `validate_projection_parity`.
- Existing old-schema projection fixtures remain readable.
- `sync_projection` materializes and preserves the generated `restore_action` projection column in temp DB verification.
- Live registry validation is read-only clean without mutating `groundtruth.db`.

## Files Changed

Files changed by this WI:

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`
- `groundtruth-kb/tests/test_sot_registry.py`
- `platform_tests/scripts/test_check_sot_registry_completeness.py`
- `platform_tests/scripts/test_gtkb_service_sot_restore_registry.py`

Other dirty worktree files pre-existed or belong to concurrent bridge or project work and were not edited for this WI.

## Acceptance Criteria Status

- [x] `restore_action` is schema-validated for every active shipped registry record.
- [x] The registry can express manual, visibility-only, git restore, MemBase-export restore, regenerate-from-source, ensure-alive, and no-op actions without executing them.
- [x] TOML/projection parity behavior includes `restore_action`.
- [x] Legacy projections remain readable until a governed sync materializes the column.
- [x] Focused spec-derived tests, ruff check, ruff format check, and read-only registry validation pass.

## Risk And Rollback

Residual risk is low-to-moderate: this introduces a new metadata field but does not execute restore actions. Execution policy and resource-bounded restoration remain in later WIs. Rollback is a single revert of the five WI files above; bridge audit files remain append-only and must not be removed.

## Loyal Opposition Asks

1. Verify that the backward-compatible projection inference is acceptable until the generated projection column is materialized by an authorized registry sync.
2. Return `VERIFIED` if the implementation satisfies the approved proposal, otherwise return `NO-GO` with concrete target-path findings.
