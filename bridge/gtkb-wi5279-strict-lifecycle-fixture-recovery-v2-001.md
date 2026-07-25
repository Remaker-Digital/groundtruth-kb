NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# Defect-Fix Proposal - WI-5279 strict lifecycle fixture recovery v2

bridge_kind: prime_proposal
Document: gtkb-wi5279-strict-lifecycle-fixture-recovery-v2
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5279
target_paths: ["platform_tests/scripts/test_implementation_start_gate.py"]

## Claim

Repair every numbered-bridge fixture producer in
`platform_tests/scripts/test_implementation_start_gate.py` so synthetic
lifecycles satisfy the strict resolver before their authorization behavior is
tested. This remains a one-test-file correction with no production behavior
change.

The predecessor recovery thread is preserved as incident evidence. Its
version 002 `GO` used `author_identity: codex`, which does not resolve to Loyal
Opposition; implementation authorization rejected it. Version 003 correctly
routed `NO-ACTION`, but the current strict resolver raises on the wrong-role
verdict before reaching its malformed-verdict correction branch. This fresh
thread avoids changing production bridge machinery merely to authorize the
bounded fixture repair.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5279, the active project PAUTH,
`GOV-FILE-BRIDGE-AUTHORITY-001`, and the strict lifecycle resolver define the
fixture correction. No new owner decision or production design change is
required.

## Defect Inventory

The complete AST/manual writer inventory in the approved target is:

1. `_proposal()` emits numbered version 001 bodies without exact
   `author_identity`, `Document`, and `Version` metadata.
2. `_go_verdict_body()` emits version 002 without role-correct LO identity,
   exact document/version metadata, or `Responds to`.
3. `_write_implementation_report()` emits version 003 without PB identity,
   exact document/version metadata, or `Responds to`.
4. The direct writer at current line 583 emits a metadata-free version 003
   `DEFERRED` body.
5. `_write_verified_thread()` at current line 2141 constructs the invalid
   terminal sequence `NEW 001 -> GO 002 -> VERIFIED 003`; it must construct
   `NEW proposal 001 -> GO 002 -> NEW implementation report 003 -> VERIFIED
   004`, with exact PB/LO roles and predecessor links.

The fifth defect is masked in several existing tests because direct Git
effects are rejected before lifecycle resolution. Passing the existing
assertions alone is therefore insufficient; the repaired fixture chains need
direct strict-resolver assertions.

## Baseline Evidence

At frozen baseline `c0c4c40e4347e4462c3eaf7b4f3b8ac6881b920a`:

- the focused module collected 205 tests and produced `41 failed, 164 passed`;
- the sorted 41-node failure list with trailing LF has SHA-256
  `31cd76c57a3d6070965aebda83e31ea66a4a0d2a0e9454ffd36f51db6ced3338`;
- the historical eight-module WI-5640 gate collected 460 tests.

Concurrent work has since added tests elsewhere, so final verification must
run every test collected from the final tree in addition to reproducing the
frozen baseline comparison. A fixed `460 passed` claim cannot exclude newly
collected tests.

## Proposed Scope

1. Add exact fixture identities, `Document`, zero-padded `Version`, and
   `Responds to` metadata to `_proposal()`, `_go_verdict_body()`, and
   `_write_implementation_report()`.
2. Replace the direct metadata-free DEFERRED write with a resolver-valid owner
   version 003 body responding to version 002.
3. Rebuild `_write_verified_thread()` as a valid four-version terminal chain
   with a version 003 implementation report and role-correct version 004 LO
   verdict.
4. Add focused assertions proving ordinary GO, DEFERRED, and terminal VERIFIED
   fixture chains are accepted by `resolve_bridge_lifecycle()` with the
   expected latest state.
5. Preserve all existing test assertions and statuses. Do not weaken, skip,
   xfail, or bypass the strict resolver or implementation-start gate.

Explicitly excluded: production source, resolver changes, implementation-start
semantics, project authorization semantics, registry files, databases,
historical bridge rewrites, Git finalization behavior, deployment, and external
systems.

## In-Root And Nonimpairment Evidence

The only protected target is
`E:\GT-KB\platform_tests\scripts\test_implementation_start_gate.py`. The
change repairs synthetic test data and adds direct lifecycle assertions; it
does not change runtime authorization decisions. Rollback is a governed
one-file revert after independent review, never a shared-worktree reset.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5279; bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-003.md; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and scripts/bridge_lifecycle_resolver.py",
  "primary_route": "Fresh valid GO, matching claim and implementation-start packet, one-file fixture correction, implementation report, independent verification, and governed finalization.",
  "before_behavior": "Synthetic numbered bridge fixtures are structurally invalid, causing 41 focused failures and allowing terminal helper defects to be masked by earlier gate decisions.",
  "after_behavior": "All synthetic lifecycle producers emit resolver-valid chains and direct resolver assertions prove ordinary GO, DEFERRED, and terminal VERIFIED states before authorization behavior is tested.",
  "self_descriptive_naming": "The v2 slug names WI-5279, strict lifecycle, and fixture recovery; the only target is the affected implementation-start test module.",
  "obsolete_guidance_disposition": "The invalid predecessor recovery thread and historical WI-5279 chain remain immutable audit evidence and are not implementation authority.",
  "history_preservation": "All existing bridge files, deliberations, work-item history, and frozen baseline evidence remain unchanged.",
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
    "instructions": "Use a governed one-file follow-up to revert the fixture patch; never reset or restore the shared worktree.",
    "verification": "Rerun direct lifecycle assertions, the focused and combined modules, the final-tree WI-5640 gate, and the frozen baseline comparison."
  },
  "hard_invariants": [
    "No production source or authorization behavior changes.",
    "No assertion weakening, skipping, xfail conversion, or failure reclassification.",
    "No edits to either historical invalid bridge chain.",
    "Only the declared test file and governed bridge evidence may enter finalization."
  ],
  "fail_closed_conditions": [
    "Missing valid GO, PAUTH, claim, implementation-start packet, or target authorization.",
    "Any direct lifecycle assertion or final-tree governance test remains failing.",
    "Any production source or unrelated dirty path enters the patch or transaction.",
    "The frozen failure set is hidden or reclassified instead of passing."
  ],
  "essential_context_preservation": "The recovery preserves WI-5279 owner intent, strict bridge lifecycle semantics, carrier-only authorization assertions, the frozen failure fingerprint, and WI-5640's governance prerequisite."
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
| Strict fixture lifecycle | Direct resolver assertions for ordinary GO, DEFERRED, and terminal VERIFIED chains in the target module | Each complete chain resolves with the expected latest state and no structural error |
| Focused implementation-start behavior | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` | Every test collected from the final tree passes; the frozen 41-node failure set is eliminated, not reclassified |
| WI-5279 combined behavior | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` | Every final-tree collected test passes |
| WI-5640 governance gate | Run the eight-module command recorded in `bridge/gtkb-file-move-rename-canonicalization-v4-007.md` against the patch and separately reproduce the frozen 460-test baseline comparison | Every final-tree collected test passes and the frozen baseline reaches 460/460 |
| Quality and scope | `python -m ruff check platform_tests/scripts/test_implementation_start_gate.py`; `python -m ruff format --check platform_tests/scripts/test_implementation_start_gate.py`; diff audit | Both Ruff checks pass; only the declared test file and governed bridge/report evidence change |

## Acceptance Criteria

- All five lifecycle producers emit internally consistent strict metadata.
- Ordinary GO, DEFERRED, and terminal VERIFIED fixture chains are directly
  accepted by the strict resolver.
- Every focused, combined, and eight-module test collected from the final tree
  passes; the separate frozen baseline comparison reaches 460/460.
- The frozen 41-node failure fingerprint disappears because those tests pass,
  not because they are renamed, skipped, or reclassified.
- No production source, resolver, registry, database, or historical bridge
  artifact is modified.

## Owner Decisions / Input

The WI-5279 owner directive and `DELIB-202666274` retain exact bridge GO,
target-path, claim, implementation-start, independent-verification, and focused
commit gates. No additional owner input is required for this test-only
recovery.

## Prior Deliberations

- `DELIB-202666274` - project-level implementation authorization and retained
  bridge/claim/verification gates.
- `DELIB-202666944` - historical WI-5279 verification context, preserved as
  audit evidence.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-003.md` - current
  invalid-GO incident and NO-ACTION evidence.

## Risks / Rollback

Risk: fixture repair could expose a second strict requirement or accidentally
alter authorization assertions. Mitigation: direct resolver assertions plus
the complete final-tree focused, combined, and WI-5640 governance suites.

Rollback: use a separately governed one-file follow-up to revert the fixture
patch. Do not reset, restore, or clean the shared worktree.

## Files Expected To Change

- `platform_tests/scripts/test_implementation_start_gate.py`

## Recommended Commit Type

`fix`
