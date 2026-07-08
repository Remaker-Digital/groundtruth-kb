NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Codex desktop session; role override ::init gtkb pb; WI-5033 dispatcher/bridge auto-build goal
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - WI-5067 Active Dispatcher/Test INDEX.md Purge

bridge_kind: prime_proposal
Document: gtkb-wi5067-active-dispatcher-index-purge
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5067

target_paths: ["platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_show_thread_bridge.py", "platform_tests/governance/test_index_md_classification_contract.py", "config/registry/sot-artifacts.toml", "groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Purge the active dispatcher, bridge-helper, and registry test residue that still writes, reads, or asserts the retired `bridge/INDEX.md` aggregate as live bridge state. The current bridge authority is dispatcher/TAFE state plus status-bearing numbered `bridge/*.md` files. Guard and quarantine references remain out of scope unless they are explicitly reclassified by the contract test.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5067`. No protected implementation files are changed by this proposal. Actual edits require Loyal Opposition GO plus implementation-start authorization.

## Requirement Sufficiency

Existing requirements are sufficient. The owner restated on 2026-07-07 that `INDEX.md` is obsolete and all references to it must be purged from GT-KB. This proposal is the next active-test tranche under the existing obsolete-reference purge project and its classification contract.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - significant retirements require stale load-bearing references to be stripped or quarantined with justification.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` - purge work must carry explicit STRIP / KEEP / QUARANTINE classification and verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - current bridge state is status-bearing numbered bridge files plus dispatcher/TAFE state, not the retired aggregate.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - active tests and registry surfaces must not route agents to stale bridge authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage is required for implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must verify the proposal against the cited requirements.
- `GOV-STANDING-BACKLOG-001` - `WI-5067` is the MemBase work item created for this owner-directed tranche.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains inside the GT-KB root and does not touch Agent Red application files.

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` - original owner directive authorizing the obsolete-reference purge project and STRIP / KEEP / QUARANTINE method.
- `DELIB-20260704-WITHDRAW-GTKB-OBSOLETE-REFERENCE-PURGE-METHODOLOGY-ADR-DCL-GO` - confirms the methodology ADR/DCL already exist and stale GO handling must not leave obsolete work active.
- `bridge/gtkb-index-md-classified-inventory-001.md` - reviewed classification contract for `bridge/INDEX.md` retirement.
- `bridge/gtkb-index-md-strip-tests-004.md` and `bridge/gtkb-index-md-strip-skill-docs-004.md` - prior VERIFIED purge tranches.
- `bridge/gtkb-wi4800-in-root-memory-index-purge-003.md` - in-root memory tranche implementation report awaiting LO verification.

## Owner Decisions / Input

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` - owner authorized residue-only stripping while keeping guard machinery and audit/history quarantines.
- 2026-07-07 owner directive in this session: "INDEX.md is obsolete and we have a standing directive to purge all references to it from GT-KB."
- Active project authorization used by the filing helper: `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30`.

No new owner decision is required before LO review. Implementation remains bridge-gated.

## Proposed Scope

- Replace active dispatcher/daemon/config test fixtures that still synthesize or read `bridge/INDEX.md` with fixtures built from numbered bridge files and dispatcher/TAFE state-compatible setup.
- Replace active bridge-helper tests that still seed `INDEX.md` compatibility text when the helper under test now discovers status-bearing numbered files.
- Update the active SoT registry/adopter test expectation that still presents `bridge/INDEX.md` as a scaffolded or authoritative artifact.
- Extend `platform_tests/governance/test_index_md_classification_contract.py` with a `WI-5067` STRIP set so this active-test residue cannot reappear silently.
- Preserve guard/enforcement references whose purpose is to block or detect retired aggregate writes; those remain KEEP and are not target paths for this tranche.

## Out of Scope

- Historical bridge files, independent-progress assessment reports, archives, generated dashboard snapshots, and session transcripts.
- Broad repo-wide string rewriting outside the declared target paths.
- The separate `NO-ACTION` scan-helper parser drift discovered during this session; that should be a separate bridge item because it is not an `INDEX.md` purge.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | Run `python -m pytest platform_tests/governance/test_index_md_classification_contract.py -q --tb=short` after adding the WI-5067 STRIP contract. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | Run `rg -n "bridge/INDEX\.md|bridge\\INDEX\.md|INDEX\.md"` over the target paths and confirm no surviving target reference is active operational guidance. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run targeted dispatcher and bridge-helper tests: `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_show_thread_bridge.py -q --tb=short`. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Run the touched registry/adopter test or an equivalent targeted check proving `bridge/INDEX.md` is no longer declared as current SoT/scaffold output. |
| Code quality | Run `python -m ruff check` and `python -m ruff format --check` on the touched Python test files. |

## Acceptance Criteria

- No target path in the WI-5067 STRIP set uses `bridge/INDEX.md` as live bridge authority after implementation.
- Dispatcher/runtime and bridge-helper tests continue to exercise current numbered bridge file behavior without recreating the retired aggregate as an input fixture.
- The registry/adopter expectation no longer treats `bridge/INDEX.md` as a current scaffolded artifact.
- KEEP guard machinery is not weakened.

## Risks / Rollback

Risk is moderate: stale tests can hide real dispatcher regressions, but over-stripping could remove useful guard coverage. The scoped target list and classification-contract update are the main mitigation.

Rollback is a revert of the implementation edits. Bridge files remain append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_scan_bridge.py`
- `platform_tests/scripts/test_show_thread_bridge.py`
- `platform_tests/governance/test_index_md_classification_contract.py`
- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py`

## Recommended Commit Type

`test`
