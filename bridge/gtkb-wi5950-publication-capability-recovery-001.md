NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T17-03-48Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi5950-publication-capability-recovery
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5950
Related Work Items: ["WI-5942", "WI-5314", "WI-5368"]

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]

implementation_scope: source + focused test (control-plane publication-capability recovery command)
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: feat

# Implementation Proposal - Systemic chain-hygiene fix: control-plane recovery command for pre-fix bridge files

## Problem Statement

WI-5950 (P0, defect) is a systemic chain-hygiene defect. Pre-fix bridge filings
filed via the helper before WI-5942's mint/consume integration lack consumed
publication-capability receipts. This blocks atomic VERIFIED finalization
(WI-5825-class stranding) because the protected-commit gate requires an exact
consumed publication capability for every staged registered bridge path.

Confirmed affected (missing capability rows): WI-5942 chain versions 001 and
003; WI-5314 version 015; WI-5368 versions 023, 027, 028.

Root cause: `mint_bridge_publication_capability` refuses already-existing files
(the "candidate bridge version already exists" guard in
`_bridge_publication_transition_digest`) and requires a live work-intent claim;
`consume_bridge_publication_capability` validates `aggregate_preimage_digest`
against the live latest aggregate revision (which changes on every write). There
is no clean control-plane recovery path for an already-existing, no-capability
pre-fix bridge file.

## Proposed Fix

Add a governed control-plane recovery command to
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, e.g.
`recover_missing_bridge_publication_capability`, that under explicit owner
authority (an owner-authorization token/deliberation id):

1. Resolves an existing pre-fix bridge file (document_name, version, target_path).
2. Recomputes the current aggregate preimage digest from the live snapshot at
   consume time (so the stale-preimage race is eliminated).
3. Bypasses the existing-file guard and the live work-intent-claim requirement
   (both only under the explicit owner-authorization evidence).
4. Mints and consumes a publication capability for the file (content digest,
   revision linkage), making it a consumed capability.
5. Fails closed on any mismatch (target bytes, author session, aggregate state).

Add a focused test covering the recovery of a pre-fix no-capability file and the
fail-closed conditions.

This clears WI-5942 001/003, WI-5314 -015, and WI-5368 -023/-027/-028 so atomic
VERIFIED can stage the full chains. It is a controlled, owner-authorized
capability; it does not weaken the normal mint/consume gates for ordinary writes.

## Scope

- Add `recover_missing_bridge_publication_capability` (or equivalent) to
  `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`.
- Add focused tests in
  `platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py`.

## Out Of Scope

- No change to ordinary `mint`/`consume`/`write_bridge_file` behavior.
- No change to the WI-5942 helper fix.
- No Git mutation, deployment, release, or MemBase mutation beyond the
  publication-capability recovery.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` requires
numbered-file chain authority and publication-capability evidence;
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` govern the recovery. The recovery is
owner-authority-scoped and does not expand ordinary write authority. No new
owner decision is needed beyond the already-recorded decision B.

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

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Recovery of a pre-fix file yields a consumed capability accepted by check_protected_commit_authorization. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Focused test passes; python -m pytest platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py -q --tb=short. |
| GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 | Ordinary mint/consume/write_bridge_file behavior unchanged; recovery fail-closed on mismatch. |

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

## Acceptance Criteria

- A governed recovery command exists that, under explicit owner authorization,
  recomputes the aggregate preimage and mints+consumes a publication capability
  for an existing pre-fix bridge file.
- WI-5942 001/003, WI-5314 -015, WI-5368 -023/-027/-028 become finalizable.
- Ordinary mint/consume/write_bridge_file behavior is unchanged.
- Focused test passes; ruff check/format pass.

## Prior Deliberations

- DELIB-202667722 - protected-commit timer/TTL invariant discipline; prior stranding lineage.
- Owner decision B (2026-08-06) - add governed recovery command for stranded pre-fix bridge files.
- WI-5942 -010 NO-GO, WI-5314 -016 NO-GO, WI-5368 -030 NO-GO - the surfacing NO-GOs.

## Note On Required PAUTH / GO / Claim / Start

This proposal is filed under the active project-scope PAUTH
PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE. No
implementation may begin until an independent bridge GO, a matching work-intent
claim, and a successful implementation-start packet exist. The recovery command
itself is exercised only under explicit owner-authorization evidence.

## Request

Request independent Loyal Opposition review (GO/NO-GO). If GO, Prime Builder
will implement the recovery command + focused test, run spec-derived
verification, and file an implementation report requesting VERIFIED.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
