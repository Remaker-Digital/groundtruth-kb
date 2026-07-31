REVISED
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
Version: 002
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5067

target_paths: ["platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_show_thread_bridge.py", "platform_tests/governance/test_index_md_classification_contract.py", "config/registry/sot-artifacts.toml", "groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note

This revision replaces the initial proposal body with authorization-clean prose. The target path declaration above is the only place this packet names implementation paths.

## Summary

Purge active dispatcher, bridge-helper, and registry test residue that still treats the retired bridge aggregate as live state. The current bridge authority is dispatcher/TAFE state plus status-bearing numbered bridge files. Guard and quarantine references remain out of scope unless the classification contract explicitly reclassifies them.

## Claim

Prime Builder proposes a bounded implementation slice for WI-5067. This proposal changes no protected implementation file. Actual edits require Loyal Opposition GO plus implementation-start authorization.

## Requirement Sufficiency

Existing requirements are sufficient. The owner restated on 2026-07-07 that INDEX.md is obsolete and all references to it must be purged from GT-KB. This proposal is the next active-test tranche under the existing obsolete-reference purge project and its classification contract.

## In-Root Placement Evidence

All declared target paths are inside the GT-KB root.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - significant retirements require stale load-bearing references to be stripped or quarantined with justification.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` - purge work must carry explicit STRIP / KEEP / QUARANTINE classification and verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - current bridge state is numbered bridge files plus dispatcher/TAFE state, not the retired aggregate.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - active tests and registry surfaces must not route agents to stale bridge authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage is required for implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must verify the proposal against the cited requirements.
- `GOV-STANDING-BACKLOG-001` - WI-5067 is the MemBase work item created for this owner-directed tranche.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains inside the GT-KB root and does not touch Agent Red application files.

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` - original owner directive authorizing the obsolete-reference purge project and STRIP / KEEP / QUARANTINE method.
- `DELIB-20260704-WITHDRAW-GTKB-OBSOLETE-REFERENCE-PURGE-METHODOLOGY-ADR-DCL-GO` - confirms the methodology ADR/DCL already exist and stale GO handling must not leave obsolete work active.
- `gtkb-index-md-classified-inventory` - reviewed classification contract for the retired aggregate.
- `gtkb-index-md-strip-tests` and `gtkb-index-md-strip-skill-docs` - prior VERIFIED purge tranches.
- `gtkb-wi4800-in-root-memory-index-purge` - in-root memory tranche implementation report awaiting Loyal Opposition verification.

## Owner Decisions / Input

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` - owner authorized residue-only stripping while keeping guard machinery and audit/history quarantines.
- 2026-07-07 owner directive in this session: INDEX.md is obsolete and references to it should be purged from GT-KB.
- Active project authorization used by this filing: `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30`.

No new owner decision is required before LO review. Implementation remains bridge-gated.

## Proposed Scope

- Replace active dispatcher/daemon/config test fixtures that still synthesize or read the retired aggregate with fixtures built from numbered bridge files and dispatcher/TAFE-compatible setup.
- Replace active bridge-helper tests that still seed compatibility text when the helper under test now discovers status-bearing numbered files.
- Update the active SoT registry/adopter test expectation that still presents the retired aggregate as a scaffolded or authoritative artifact.
- Extend the classification contract with a WI-5067 STRIP set so this active-test residue cannot reappear silently.
- Preserve guard/enforcement references whose purpose is to block or detect retired aggregate writes; those remain KEEP and are not target paths for this tranche.

## Out of Scope

- Historical bridge files, independent-progress assessment reports, archives, generated dashboard snapshots, and session transcripts.
- Broad repo-wide string rewriting outside the declared target paths.
- The separate NO-ACTION scan-helper parser drift discovered during this session; that should be a separate bridge item because it is not an INDEX.md purge.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | Run the classification contract test after adding the WI-5067 STRIP contract. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | Run a fixed-string scan over the declared target paths and confirm no surviving retired-aggregate reference is active operational guidance. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the touched dispatcher and bridge-helper test modules and confirm they exercise numbered-file and dispatcher/TAFE authority. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Run the touched registry/adopter test or equivalent targeted check proving the retired aggregate is no longer declared as current SoT/scaffold output. |
| Code quality | Run lint and format checks over the touched Python test modules. |

## Acceptance Criteria

- No declared target path uses the retired aggregate as live bridge authority after implementation.
- Dispatcher/runtime and bridge-helper tests continue to exercise current numbered bridge file behavior without recreating the retired aggregate as an input fixture.
- The registry/adopter expectation no longer treats the retired aggregate as a current scaffolded artifact.
- KEEP guard machinery is not weakened.

## Risks / Rollback

Risk is moderate: stale tests can hide real dispatcher regressions, but over-stripping could remove useful guard coverage. The scoped target list and classification-contract update are the main mitigation.

Rollback is a revert of the implementation edits. Bridge files remain append-only audit artifacts and must not be deleted.

## Files Expected To Change

The implementation files are exactly the paths declared in `target_paths` above.

## Recommended Commit Type

`test`
