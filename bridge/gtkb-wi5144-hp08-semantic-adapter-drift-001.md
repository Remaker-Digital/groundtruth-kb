NEW

# Defect-Fix Proposal - Reject hash-current generated skill adapters with semantic drift

bridge_kind: prime_proposal
Document: gtkb-wi5144-hp08-semantic-adapter-drift
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5144

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity.py"]

## Claim

The harness-parity checker currently accepts a generated skill adapter when its marker metadata and registry hash match the canonical source, even if the adapter body contradicts that source. Close MOD-HP08 by deterministically re-rendering each supported generated adapter with its recorded generation timestamp and requiring exact content equality.

This proposal is filed as the next append-only numbered bridge file, `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-001.md`. No prior versioned bridge file is deleted, rewritten, or treated as replaceable state.

## Defect / Reproduction

At HEAD `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f` in the authoritative concurrent worktree, `_status_for_surface` validates adapter existence, loadability, canonical path, registry source hash, and marker source hash, then returns `PASS`. It does not validate the generated adapter body.

The frozen MOD-HP08 case constructs a canonical skill that denies protected mutation and a Codex adapter that allows protected mutation while retaining current source-path and source-hash metadata. The checker accepts the contradictory adapter, so the clause-exact case fails.

An exact byte comparison against the authoritative generator output is required. A marker-stripped canonical-body comparison is not sufficient because Codex legitimately rewrites helper paths, API harness adapters are compact pointers rather than full copies, and each generator has its own output contract.

## In-Root Placement Evidence

Both target paths are tracked, byte-clean, and inside `E:\GT-KB`:

- `scripts/check_harness_parity.py` at Git blob `70406278a745029f7f85686b90dd8d198fdc3fd7`
- `platform_tests/scripts/test_check_harness_parity.py` at Git blob `3bd4f5752c9b8cf9dde0477f4942d239e12395e4`

The dirty registry `config/agent-control/harness-capability-registry.toml`, generated adapters, canonical skills, manifests, frozen modernization tests, and all WI-5266 targets are verification inputs only and are excluded from mutation.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - MOD-HP08 requires executable semantic-drift detection, not metadata-only evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected implementation requires this proposal, an independent GO, matching claim, and implementation-start authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The false-green is durably owned by WI-5144 and this reviewable implementation packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The exact implementation scope and tests are linked to governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED must rerun the mapped focused and clause-exact tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work item, and target paths are explicit above.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner authorization is durably captured as `DELIB-202666274`; no additional owner question is inferred.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All source, tests, and runtime reads remain inside the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - WI-5144 is the durable backlog authority for MOD-HP08.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex filing uses the governed non-bypass helper and compliance audit path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The checker repair, regression tests, implementation report, and independent verdict form the durable change packet.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Implementation and verification advance only after their required lifecycle evidence exists.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Existing hash, path, loadability, waiver, applicability, and parity classifications remain enforced.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Adapter semantic equality becomes deterministic machine-evaluable evidence and fails closed on unsupported or malformed provenance.

## Requirement Sufficiency

Existing requirements sufficient.

The frozen MOD-HP08 objective and the specifications linked above already require generated-adapter semantic parity to be mechanically enforced. This repair makes the existing checker evaluate the authoritative generator contract; it introduces no new normative harness behavior and requires no specification amendment.

## Prior Deliberations

- `DELIB-202666274` - Owner authorization for all required project-level modernization blocker repairs while preserving bridge, independent review, implementation-start, and mechanical-operation gates.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the Harness Parity project at project scope. It does not bypass bridge GO, claim/start, independent VERIFIED, Git, release, routing, harness, or deployment gates.

## Proposed Scope

1. Add a pure checker helper that selects an authoritative renderer only from the adapter marker's exact `Generated by` value: Codex, Antigravity, or compact API skill generator.
2. Reconstruct the renderer's immutable adapter value from the current capability, canonical source path, target surface, and already-validated source hash. For API adapters, parse the canonical frontmatter to obtain the generated description.
3. Re-render using the exact `Generated at` value already recorded in the adapter marker, preserving deterministic historical output rather than introducing the current clock.
4. Compare the current adapter text with the expected renderer output exactly after the existing path and hash checks pass.
5. Return `STALE` with a specific note when `Generated by` or `Generated at` is missing, the generator is unsupported, reconstruction or rendering fails, or rendered content differs.
6. Preserve existing `MISSING` behavior for absent surfaces, sources, or unloadable frontmatter and preserve current `STALE` behavior for path/hash drift.
7. Update the focused Codex adapter fixture to emit authoritative generator output, then add regressions proving an exact adapter passes, a hash-current body mutation is `STALE`, and missing/unsupported generation metadata fails closed.
8. Run the focused tracked suite, the MOD-HP08 clause-exact case, and the read-only live harness-parity checker. Do not regenerate adapters or mutate the concurrent registry.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_harness_parity.py --all --json",
  "before_behavior": "An adapter with current source-path and source-hash metadata passes even when its body contradicts the canonical skill.",
  "after_behavior": "A supported generated adapter passes only when its complete content exactly matches deterministic output from its declared authoritative generator and recorded timestamp.",
  "self_descriptive_naming": "Generator provenance, recorded generation timestamp, expected adapter text, and semantic drift use explicit checker concepts rather than an ambiguous body hash.",
  "obsolete_guidance_disposition": "No existing parity guidance or evidence is removed; metadata checks remain as early, specific diagnostics before semantic comparison.",
  "history_preservation": "The recorded Generated at value is reused during comparison, so historical adapter timestamps remain stable and queryable.",
  "baseline": {
    "checker_targets": 2,
    "tracked_target_blobs": [
      "70406278a745029f7f85686b90dd8d198fdc3fd7",
      "3bd4f5752c9b8cf9dde0477f4942d239e12395e4"
    ],
    "mod_hp08_clause_exact_state": "FAIL",
    "metadata_only_false_green": true
  },
  "expected_result": {
    "exact_generator_output": "PASS",
    "hash_current_semantic_tamper": "STALE",
    "missing_or_unsupported_generator_metadata": "STALE",
    "mod_hp08_clause_exact_state": "PASS"
  },
  "rollback": {
    "instructions": "Remove only the independently reviewed renderer-selection helper, exact comparison, and focused WI-5144 tests from the two tracked targets.",
    "test": "python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short"
  },
  "hard_invariants": [
    "no registry or generated adapter mutation",
    "existing path and hash diagnostics remain active",
    "existing waiver and parity classification behavior remains active",
    "renderer selection accepts only exact governed generator identities",
    "comparison does not consult the current clock",
    "all reads remain within the supplied project root"
  ],
  "fail_closed_conditions": [
    "missing Generated by metadata",
    "missing Generated at metadata",
    "unsupported generator identity",
    "canonical frontmatter reconstruction failure",
    "renderer failure",
    "complete content mismatch"
  ],
  "essential_context_preservation": "Native, fallback, unsupported, owner-action-required, manifest, role, waiver, capability-floor, and fleet-coverage behavior remains present."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Run the MOD-HP08 clause-exact case and prove the hash-current contradictory adapter is rejected. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the complete tracked harness-parity test file and verify pre-existing state classifications and diagnostics remain green. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Exercise exact output, body tamper, missing metadata, unsupported generator, and renderer failure paths with deterministic expected states. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run proposal applicability and ADR/DCL clause preflights against this complete content. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns the focused test file, MOD-HP08 exact case, and read-only checker before VERIFIED. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Use only the supplied project root and prove no renderer input resolves outside it. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify active GO, matching claim, and implementation-start authority before either target is edited. |

## Acceptance Criteria

1. A generated adapter whose complete content equals its declared authoritative renderer output remains `PASS`.
2. A generated adapter with current source-path and source-hash metadata but contradictory body content is `STALE`.
3. Missing or unsupported generator identity, missing generation timestamp, reconstruction failure, or renderer failure is `STALE` with a specific diagnostic.
4. Codex, Antigravity, and compact API adapter renderers are selected only by exact `Generated by` metadata and reuse the recorded `Generated at` value.
5. The tracked harness-parity suite and MOD-HP08 clause-exact test pass under the repository default timeout.
6. The read-only live checker completes without mutating the registry, canonical skills, adapters, manifests, bridge state beyond governed reporting, Git state, harness state, or external systems.
7. Only the two tracked, initially clean target files contain WI-5144 implementation changes.

## Risks / Rollback

- Importing generator modules could introduce script-mode path differences. Use the repository's existing guarded import pattern and test the checker both as a loaded module and direct CLI.
- Exact comparison can flag legitimately stale generated adapters that metadata-only checks previously missed. That is the intended fail-closed behavior; adapters remain unchanged and their owning generator work items receive the findings.
- API adapters intentionally differ from canonical bodies. Use the compact API renderer rather than comparing canonical text.
- Generator exceptions must not crash the whole parity report. Convert reconstruction or render failures into a scoped `STALE` result with the error class, without leaking environment details.
- Rollback removes only the reviewed checker helper, comparison branch, and focused tests, then reruns the focused suite and read-only checker.

## Files Expected To Change

- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_check_harness_parity.py`

## Recommended Commit Type

`fix`
