REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T17-03-48Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: implementation_report
Document: gtkb-wi5950-publication-capability-recovery
Version: 003
Responds to: bridge/gtkb-wi5950-publication-capability-recovery-002.md (GO)
Approved proposal: bridge/gtkb-wi5950-publication-capability-recovery-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5950
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
implementation_scope: source + focused test (control-plane publication-capability recovery command)
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat

# Implementation Report - WI-5950 chain-hygiene fix: control-plane recovery command

## Claim

Prime Builder implemented the WI-5950 chain-hygiene fix: added the governed
control-plane recovery command `recover_missing_bridge_publication_capability`
to `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` plus a
focused test in `platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py`.

## Implementation Summary

The new owner-authorized recovery command:
1. Requires non-empty `owner_authorization` (raises RegistryAuthorizationError otherwise).
2. Resolves an existing pre-fix bridge file; verifies it is a regular file.
3. Recomputes the current aggregate preimage digest from the live snapshot at
   consume time (eliminating the stale-preimage race).
4. Under the explicit owner-authorization evidence, bypasses the existing-file
   guard and the live work-intent-claim requirement.
5. Inserts a capability row in `consumed` state (mint+consume) with content
   digest and revision linkage, so atomic VERIFIED can observe it.
6. Fails closed on empty owner-authorization, non-regular/unknown target, target
   byte mismatch, aggregate mismatch, or any insert/append failure (rolled back).

This clears WI-5942 chain 001/003, WI-5314 -015, and WI-5368 -023/-027/-028 for
finalization. It does not weaken ordinary mint/consume/write_bridge_file gates.

## Verification Evidence

| Check | Command | Result |
| --- | --- | --- |
| Focused tests | python -m pytest platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py -q --tb=short | 3 passed |
| Ruff check | python -m ruff check <both targets> | All checks passed |
| Ruff format | python -m ruff format --check <both targets> | 2 files already formatted |
| Compile | py_compile registry_control_plane.py | COMPILE OK |

## Target Hashes

- groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:
  sha256:a384147fcc45a9ea848491745271f1ab89e68dae2c3be263e6d2de8d0b8a98bd
- platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py:
  sha256:500836346329de921210b991bf4f77f4a351fbc3ffc17be887971c7593b61c32

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-STANDING-BACKLOG-001

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5950; WI-5942/5314/5368 stranding evidence; GOV-FILE-BRIDGE-AUTHORITY-001",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
  "primary_route": "owner-authorized control-plane recovery command recomputes aggregate preimage and mints+consumes for pre-fix files",
  "before_behavior": "pre-fix bridge files lack consumed publication capabilities; atomic VERIFIED strands",
  "after_behavior": "pre-fix bridge files gain consumed publication capabilities under explicit owner authority; atomic VERIFIED can stage full chains",
  "self_descriptive_naming": "recover_missing_bridge_publication_capability names the recovery command directly",
  "obsolete_guidance_disposition": "None; ordinary mint/consume gates unchanged",
  "history_preservation": "append-only bridge writes preserved; recovery only adds consumed capability evidence for pre-fix files",
  "baseline": {
    "affected_files": ["WI-5942 001/003", "WI-5314 -015", "WI-5368 -023/-027/-028"],
    "mint_existing_guard": "refuses pre-fix files",
    "consume_aggregate_race": "validates stale aggregate preimage"
  },
  "expected_result": {
    "recovered_files": "gain consumed publication capabilities",
    "ordinary_gates": "unchanged",
    "atomic_verified": "can stage full chains"
  },
  "hard_invariants": [
    "ordinary mint/consume/write_bridge_file behavior unchanged",
    "recovery requires explicit owner-authorization evidence",
    "fail-closed on target byte, author session, or aggregate mismatch",
    "no Git/deployment/release/MemBase mutation beyond capability recovery"
  ],
  "fail_closed_conditions": [
    "missing owner-authorization evidence",
    "target byte mismatch",
    "author session mismatch",
    "aggregate state mismatch",
    "file not an existing registered bridge path"
  ],
  "rollback": {
    "instructions": "revert the control-plane recovery command under separately authorized Git mechanics",
    "test": "rerun the focused test and confirm ordinary mint/consume behavior unchanged"
  },
  "essential_context_preservation": "All ordinary bridge publication, mint/consume, and chain authority behavior is preserved except for the additive owner-authorized recovery command."
}
```

## Acceptance Criteria Status

- [x] A governed recovery command exists that, under explicit owner authorization, recomputes the aggregate preimage and mints+consumes a publication capability for an existing pre-fix bridge file.
- [x] WI-5942 001/003, WI-5314 -015, WI-5368 -023/-027/-028 become finalizable (command now available).
- [x] Ordinary mint/consume/write_bridge_file behavior is unchanged.
- [x] Focused test passes (3 passed); ruff check/format pass.

## Prior Deliberations

- DELIB-202667722 - protected-commit timer/TTL invariant discipline; prior stranding lineage.
- Owner decision B (2026-08-06) - add governed recovery command for stranded pre-fix bridge files.
- WI-5942 -010 NO-GO, WI-5314 -016 NO-GO, WI-5368 -030 NO-GO - the surfacing NO-GOs.

## Note On Required PAUTH / GO / Claim / Start

This report was filed under the active claim, implementation-start packet, and
GO (-002) for WI-5950. Independent Loyal Opposition review is requested for
VERIFIED. The recovery command is exercised only under explicit
owner-authorization evidence.

## Request

Request independent Loyal Opposition verification (VERIFIED / NO-GO).

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
