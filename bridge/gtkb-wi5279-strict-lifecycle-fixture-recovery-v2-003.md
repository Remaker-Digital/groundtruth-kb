REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# Revised Proposal - WI-5279 strict lifecycle fixture recovery v2

bridge_kind: prime_proposal
Document: gtkb-wi5279-strict-lifecycle-fixture-recovery-v2
Version: 003
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-002.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5279
target_paths: ["platform_tests/scripts/test_implementation_start_gate.py"]

## Revision Response

The version-002 NO-GO treated
`bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-004.md` as executable
implementation authority and therefore rejected the need for this clean v2
thread. That premise is mechanically false.

Prime Builder acquired a fresh implementation claim on the original thread
and ran:

```text
python scripts/implementation_authorization.py begin \
  --bridge-id gtkb-wi5279-strict-lifecycle-fixture-recovery \
  --session-id 019f863a-acd3-7320-80c0-1831f0936cc0 \
  --no-write
```

Observed result:

```json
{
  "authorized": false,
  "error": "Status GO has wrong or unreadable author role None: bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-002.md"
}
```

The strict resolver parses version 002 before it can consider the later
NO-ACTION and corrected version-004 GO. Its correction branch does not
quarantine a canonical status whose author role is unreadable. Therefore the
original thread remains incident evidence and cannot authorize this test-file
repair.

A later independent Loyal Opposition session reviewed this exact v2 proposal,
confirmed its preflights, authorship independence, PAUTH, target ownership,
five-writer defect inventory, and final-tree test scope, and concluded it was
substantively GO-worthy. That reviewer could not replace the append-only stale
version 002 and directed Prime Builder to file this corrective revision.

No implementation occurred. Both test-file and production behavior remain
unchanged.

## Claim

Repair every numbered-bridge fixture producer in
`platform_tests/scripts/test_implementation_start_gate.py` so synthetic
lifecycles satisfy the strict resolver before their authorization behavior is
tested. This remains a one-test-file correction with no production behavior
change.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5279, the active project PAUTH,
`GOV-FILE-BRIDGE-AUTHORITY-001`, and the strict lifecycle resolver define the
fixture correction. No new owner decision or production design change is
required.

## Complete Defect Inventory

1. `_proposal()` omits exact `author_identity`, `Document`, and `Version`
   metadata from numbered version-001 fixtures.
2. `_go_verdict_body()` omits role-correct LO identity, exact document/version
   metadata, and `Responds to` from version 002.
3. `_write_implementation_report()` omits PB identity, exact document/version
   metadata, and `Responds to` from version 003.
4. The direct DEFERRED writer at current line 583 emits a metadata-free
   version-003 body.
5. `_write_verified_thread()` at current line 2141 constructs invalid
   `NEW 001 -> GO 002 -> VERIFIED 003` instead of `NEW proposal 001 -> GO 002
   -> NEW implementation report 003 -> VERIFIED 004` with exact roles and
   predecessor links.

The fifth defect is masked in existing tests whose direct Git effects are
rejected before lifecycle resolution, so direct resolver assertions are
required.

## Proposed Scope

1. Add exact fixture identities, `Document`, zero-padded `Version`, and
   `Responds to` metadata to the proposal, GO, and implementation-report
   producers.
2. Make the direct DEFERRED version 003 resolver-valid while preserving its
   existing deferral assertion.
3. Rebuild `_write_verified_thread()` as the valid four-version terminal
   lifecycle.
4. Add direct assertions proving ordinary GO, DEFERRED, and terminal VERIFIED
   fixture chains resolve to their expected latest states.
5. Preserve every existing authorization assertion and status. Do not weaken,
   skip, xfail, or bypass the resolver or implementation-start gate.

Explicitly excluded: production source, resolver changes, implementation-start
semantics, project authorization semantics, registry files, databases,
historical bridge rewrites, Git finalization behavior, deployment, and external
systems.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5279; bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-002.md; mechanical implementation-start refusal on the original chain",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and scripts/bridge_lifecycle_resolver.py",
  "primary_route": "Fresh role-valid v2 GO, matching claim and implementation-start packet, one-file fixture correction, implementation report, independent verification, and governed finalization.",
  "before_behavior": "Synthetic numbered bridge fixtures are structurally invalid and the original recovery carrier is mechanically unusable.",
  "after_behavior": "Every fixture lifecycle producer emits resolver-valid metadata and direct assertions prove ordinary GO, DEFERRED, and terminal VERIFIED states.",
  "self_descriptive_naming": "The v2 slug names WI-5279, strict lifecycle, and fixture recovery.",
  "obsolete_guidance_disposition": "Both invalid predecessor chains remain immutable incident evidence and are never used as implementation authority.",
  "history_preservation": "No existing bridge version, deliberation, work-item history, or frozen baseline evidence is rewritten.",
  "baseline": {
    "head": "c0c4c40e4347e4462c3eaf7b4f3b8ac6881b920a",
    "focused_result": "41 failed, 164 passed",
    "failed_node_sha256_lf": "31cd76c57a3d6070965aebda83e31ea66a4a0d2a0e9454ffd36f51db6ced3338"
  },
  "expected_result": {
    "focused_result": "all final-tree collected tests pass",
    "wi5640_governance_gate": "all final-tree collected tests pass and frozen baseline comparison is 460/460",
    "production_behavior": "unchanged"
  },
  "rollback": {
    "instructions": "Use a governed one-file follow-up; never reset or restore the shared worktree.",
    "verification": "Rerun direct lifecycle assertions, focused and combined modules, final-tree WI-5640 gate, and frozen baseline comparison."
  },
  "hard_invariants": [
    "No production source or authorization behavior changes.",
    "No assertion weakening or failure reclassification.",
    "No edits to either invalid historical bridge chain.",
    "Only the declared test file and governed evidence may enter finalization."
  ],
  "fail_closed_conditions": [
    "Missing valid v2 GO, PAUTH, claim, implementation-start packet, or target authorization.",
    "Any direct lifecycle assertion or final-tree governance test remains failing.",
    "Any production source or unrelated dirty path enters the transaction."
  ],
  "essential_context_preservation": "The recovery preserves WI-5279 owner intent, strict lifecycle semantics, the frozen failure fingerprint, and WI-5640's governance prerequisite."
}
```

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Verification Plan

| Requirement | Command / evidence | Required result |
| --- | --- | --- |
| Strict fixture lifecycle | Direct resolver assertions for ordinary GO, DEFERRED, and terminal VERIFIED chains | Each chain resolves with the expected latest state |
| Focused behavior | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` | Every final-tree collected test passes; frozen 41-node failure set is eliminated, not reclassified |
| WI-5279 combined behavior | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` | Every final-tree collected test passes |
| WI-5640 governance gate | Run the eight-module command from `bridge/gtkb-file-move-rename-canonicalization-v4-007.md` plus the frozen baseline comparison | Every final-tree test passes and frozen baseline reaches 460/460 |
| Quality and scope | Ruff check/format on the target and a diff audit | Both Ruff gates pass; only the declared test and governed evidence change |

## Acceptance Criteria

- All five lifecycle producers emit internally consistent strict metadata.
- Ordinary GO, DEFERRED, and terminal VERIFIED fixture chains are directly
  accepted by the strict resolver.
- Every focused, combined, and eight-module test collected from the final tree
  passes; the separate frozen baseline comparison reaches 460/460.
- The frozen 41-node fingerprint disappears because those tests pass, not
  because they are renamed, skipped, or reclassified.
- No production source, resolver, registry, database, or historical bridge
  artifact is modified.

## Owner Decisions / Input

`DELIB-202666274` retains exact bridge GO, target-path, claim,
implementation-start, independent-verification, and focused-commit gates. No
additional owner input is required.

## Prior Deliberations

- `DELIB-202666274` - project-level implementation authorization and retained
  bridge/claim/verification gates.
- `DELIB-202666944` - historical WI-5279 verification context preserved as
  audit evidence.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-004.md` - role-correct
  verdict that remains non-executable because the resolver first rejects its
  predecessor.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-002.md` - stale
  NO-GO corrected by the mechanical evidence in this revision.

## Risks / Rollback

Risk: fixture repair could expose another strict requirement or accidentally
alter authorization assertions. Mitigation: direct resolver assertions and
complete final-tree focused, combined, and WI-5640 governance suites.

Rollback: use a separately governed one-file follow-up. Do not reset, restore,
or clean the shared worktree.

## Files Expected To Change

- `platform_tests/scripts/test_implementation_start_gate.py`

## Recommended Commit Type

`fix`
