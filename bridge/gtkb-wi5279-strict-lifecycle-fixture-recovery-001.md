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

# Defect-Fix Proposal - WI-5279 strict lifecycle fixture recovery

bridge_kind: prime_proposal
Document: gtkb-wi5279-strict-lifecycle-fixture-recovery
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5279
target_paths: ["platform_tests/scripts/test_implementation_start_gate.py"]

## Claim

Repair the stale numbered-bridge fixture builders in
`platform_tests/scripts/test_implementation_start_gate.py` so they emit the
exact lifecycle metadata now required by `bridge_lifecycle_resolver.py`. This
is a one-test-file recovery. It changes no production behavior and restores the
canonical 460-test governance gate required by WI-5640.

The historical `gtkb-wi5279-project-authorization-bootstrap-lifecycle` chain
must remain unchanged as audit evidence. Its version 003 contains malformed
`Version:` metadata and the strict resolver rejects the chain, so this fresh
thread is the bounded correction path.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5279, its version-004 NO-GO,
`GOV-FILE-BRIDGE-AUTHORITY-001`, and the strict resolver contract define the
fixture correction without a new owner decision or production design change.

## Defect / Reproduction

Current baseline: `research` HEAD
`c0c4c40e4347e4462c3eaf7b4f3b8ac6881b920a`.

The target file is clean relative to HEAD. Its `_proposal()`,
`_go_verdict_body()`, and `_write_implementation_report()` helpers omit one or
more of `author_identity`, exact `Document`, exact zero-padded `Version`, and
`Responds to` metadata required by the strict numbered-chain resolver.

Independent reproduction:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=no
```

Observed result: `41 failed, 164 passed, 1 warning`. Every failed path reaches
the same strict-fixture class beginning with missing `Version` metadata. The
sorted failed-node list with a trailing LF has SHA-256
`31cd76c57a3d6070965aebda83e31ea66a4a0d2a0e9454ffd36f51db6ced3338`.

The original bridge chain is not a valid continuation carrier:

```text
WRONG_BRIDGE_VERSION_METADATA: Version metadata
'003 (NEW; post-implementation report)' does not match 003
```

`platform_tests/scripts/test_implementation_authorization.py` already contains
the parallel compliant fixture pattern and is read-only reference evidence for
this correction.

## In-Root Placement Evidence

The only target is inside `E:\GT-KB`:
`platform_tests/scripts/test_implementation_start_gate.py`.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5279; bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the strict numbered bridge lifecycle resolved by scripts/bridge_lifecycle_resolver.py",
  "primary_route": "Fresh bridge GO, matching claim and implementation-start packet, one-file fixture correction, implementation report, independent verification, and governed finalization.",
  "before_behavior": "Forty-one implementation-start gate tests fail before exercising their assertions because synthetic numbered bridge files omit strict lifecycle metadata.",
  "after_behavior": "Synthetic proposal, verdict, and report files use the same exact lifecycle metadata shape as live numbered chains, allowing all existing authorization assertions to execute unchanged.",
  "self_descriptive_naming": "The recovery slug names WI-5279, strict lifecycle, and fixture recovery; the only target is the affected implementation-start gate test module.",
  "obsolete_guidance_disposition": "The invalid historical WI-5279 chain is preserved as audit evidence and is not extended, rewritten, or treated as current implementation authority.",
  "history_preservation": "All existing bridge files, deliberations, work-item history, and test evidence remain unchanged; recovery uses a fresh numbered thread.",
  "baseline": {
    "head": "c0c4c40e4347e4462c3eaf7b4f3b8ac6881b920a",
    "focused_result": "41 failed, 164 passed, 1 warning",
    "failed_node_sha256_lf": "31cd76c57a3d6070965aebda83e31ea66a4a0d2a0e9454ffd36f51db6ced3338"
  },
  "expected_result": {
    "focused_result": "205 passed",
    "wi5640_governance_gate": "460 passed",
    "production_behavior": "unchanged"
  },
  "rollback": {
    "instructions": "Use a governed one-file follow-up to revert the fixture patch; never reset or restore the shared worktree.",
    "verification": "Rerun the focused 205-test module, the combined WI-5279 modules, Ruff check/format, and the canonical 460-test gate."
  },
  "hard_invariants": [
    "No production source or authorization behavior changes.",
    "No assertion weakening, skipping, xfail conversion, or failure reclassification.",
    "No edits to the invalid historical WI-5279 bridge chain.",
    "Only the declared test file and governed bridge evidence may enter the final transaction."
  ],
  "fail_closed_conditions": [
    "Missing fresh GO, PAUTH, claim, implementation-start packet, or target authorization.",
    "Any focused or canonical governance test remains failing.",
    "Any production source or unrelated dirty path enters the patch or staged transaction.",
    "The failed-node set is hidden or reclassified instead of passing."
  ],
  "essential_context_preservation": "The recovery preserves WI-5279 owner intent, strict bridge lifecycle semantics, carrier-only authorization assertions, the frozen failure fingerprint, and WI-5640's 460/460 completion gate."
}
```

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start authority must remain mechanically testable.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the repaired fixtures must exercise live operation-time denial and allow behavior.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - bootstrap fixtures must continue proving that carrier authority is not a source/test bypass.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - synthetic numbered chains must satisfy the same strict lifecycle structure as live chains.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries current PAUTH, project, and WI linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal maps the bounded test correction to governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - closure requires the focused and canonical governance suites to pass.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - no production source or authorization behavior may change.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the stale verification gap is repaired through a new governed audit chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - executable fixture and test evidence replace the current unverifiable claim.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the invalid historical chain is preserved and a clean lifecycle is used for recovery.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains within the GT-KB root.

## Prior Deliberations

- `DELIB-202666944` - historical WI-5279 verification context; later strict evidence and v004 show that terminal treatment was not reliable.
- `DELIB-202666284` - Authority Foundations project-authorization NO-GO context retained by the active project PAUTH.
- `DELIB-202666274` - owner decision underlying the current Authority Foundations project authorization.

## Owner Decisions / Input

- Owner directive recorded on WI-5279 on 2026-07-15: preserve exact bridge GO, target-path, claim, implementation-start, independent-verification, and focused-commit gates while creating the project-authorization bootstrap lifecycle.
- `DELIB-202666274` and active PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE` authorize this bounded project work. The PAUTH is active, project-scoped, permits test and bridge mutations, and retains Git commit/push and destructive-operation restrictions.
- No new owner decision is needed for the fixture-only correction required by the existing WI-5279 NO-GO.

## Proposed Scope

1. Update `_proposal()` to emit fixture `author_identity`, session context,
   `Document`, and exact zero-padded `Version` metadata for its numbered file.
2. Update `_go_verdict_body()` and its caller to emit LO fixture identity,
   exact `Document`/`Version`, and an exact `Responds to` predecessor path.
3. Update `_write_implementation_report()` to emit PB fixture identity,
   session context, exact version 003 metadata, and its predecessor path.
4. Keep `_write_thread()` filenames and state internally consistent with those
   bodies for `NEW`, `GO`, and non-GO fixture cases.
5. Preserve all test semantics and assertions. Do not weaken strict resolver,
   authorization, claim, target, project, or protected-mutation checks.

Explicitly excluded: production source, the original WI-5279 bridge files,
other test modules, registry files, MemBase, runtime claims/packets outside
isolated tests, Git operations, cleanup, deployment, release, credentials, and
external systems.

## Cross-Harness Disposition

The affected gate is shared platform behavior. The patch changes only
synthetic fixture construction and must not introduce harness-specific
authorization exceptions.

## Specification-Derived Verification Plan

| Requirement | Command / evidence | Required result |
| --- | --- | --- |
| Strict numbered-chain fixture validity | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` | 205/205 pass; no missing or malformed lifecycle metadata |
| WI-5279 combined behavior | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` | all collected tests pass |
| WI-5640 F5 governance gate | Run the eight-module 460-node command recorded in `bridge/gtkb-file-move-rename-canonicalization-v4-007.md` in an isolated baseline plus this patch | 460/460 pass; frozen 41-node failure set is eliminated, not reclassified |
| Scope and quality | `python -m ruff check platform_tests/scripts/test_implementation_start_gate.py` and `python -m ruff format --check platform_tests/scripts/test_implementation_start_gate.py` | both pass |
| Nonimpairment | Review the staged diff and run `git diff --name-only --cached` during finalization | only the declared test file plus governed bridge evidence |

## Acceptance Criteria

- The focused module passes all 205 tests.
- The exact frozen 41-node failure fingerprint is absent because those nodes pass.
- The canonical WI-5640 governance suite passes 460/460 from an isolated, documented baseline plus the patch.
- Synthetic proposal, verdict, and implementation-report bodies contain exact lifecycle metadata accepted by the strict resolver.
- No production source, live bridge predecessor, registry, database, or unrelated dirty path is changed or staged.
- The implementation report includes exact commands, counts, baseline commit, diff scope, and finalization evidence.

## Risks / Rollback

Risk: fixture metadata could be repaired only far enough to expose a second
strict requirement, or could accidentally change authorization semantics.
Mitigation: mirror the already-compliant helper structure in
`test_implementation_authorization.py`, run the entire 205-test module, then
run the canonical 460-test gate. Do not alter assertions or production code to
make tests pass.

Rollback: revert only the one-file fixture patch through a governed follow-up.
Do not use `git reset`, whole-worktree restore, or destructive cleanup.

## Files Expected To Change

- `platform_tests/scripts/test_implementation_start_gate.py`

## Recommended Commit Type

`fix`
