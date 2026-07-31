NEW

# gtkb-harness-benchmark-manifest-amendment - benchmark manifest field and failure taxonomy

bridge_kind: prime_proposal
Document: gtkb-harness-benchmark-manifest-amendment
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-30T05:40:07Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-30T05-40-07Z-prime-builder-A-auto-builder
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex Desktop automation; Auto-builder; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4580
Related Work Items: WI-4581, WI-4583, WI-4584

target_paths: ["scripts/benchmarks/harness_quality_manifest.py", "platform_tests/scripts/test_harness_quality_manifest.py"]

implementation_scope: source, test_update, benchmark_manifest_contract
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal amends the harness quality benchmark manifest contract before the deferred benchmark slices resume. The implementation would add `author_model_configuration` to `REQUIRED_EVIDENCE_FIELDS` in `scripts/benchmarks/harness_quality_manifest.py` and define a closed, duplicate-free `FAILURE_CLASSES` tuple for scoring and telemetry consumers.

The proposal is intentionally narrow. It does not implement the fixture corpus, cross-role dispatch runner, scoring pipeline, or telemetry persistence. It only supplies the shared manifest contract required by the existing DEFERRED benchmark slice entries so those slices can be revised and reviewed against a stable schema.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires status-bearing bridge changes to flow through the append-only bridge file chain with role-eligible authorship.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite the governing requirements before implementation starts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project, authorization, work-item, and target-path linkage in bridge proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires Loyal Opposition verification to be grounded in tests derived from the cited specifications.
- `GOV-STANDING-BACKLOG-001` - Keeps implementation work tied to tracked backlog and project records instead of ad hoc source edits.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Requires active project authorization before implementation under a project work item.
- `SPEC-1529` - Defines project authorization packet requirements, including bounded implementation authorization and explicit target scope.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - Makes dispatch envelope evidence fields part of the cross-harness execution contract.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - Requires schema-governed dispatch metadata rather than informal per-harness notes.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - Treats TAFE/dispatcher-backed bridge state and numbered bridge files as authoritative workflow state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Preserves the manifest-contract decision as a governed artifact rather than a hidden implementation assumption.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires durable capture when a concrete project input becomes accepted future work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Treats the deferred benchmark slice unblocker as a lifecycle trigger for a new bridge proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms this work belongs in the GT-KB platform tree, not in an adopter application subtree.

## Prior Deliberations

- `DELIB-20263440` through `DELIB-20263447` - Owner decisions established the harness testing and quality benchmarking program and its staged work items.
- `DELIB-20265586` - Active project authorization packet for the bounded harness testing and quality benchmarking implementation project.
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md` - VERIFIED Slice 1 manifest/rubric work that this proposal amends rather than replaces.
- `bridge/gtkb-harness-benchmark-fixture-corpus-002.md` - DEFERRED WI-4580 entry; owner selected pausing the slice until a manifest amendment adds `author_model_configuration` and the failure-class taxonomy.
- `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md` - DEFERRED WI-4581 entry with the same manifest-amendment clear condition.
- `bridge/gtkb-harness-benchmark-scoring-pipeline-002.md` - DEFERRED WI-4583 entry with the same manifest-amendment clear condition.
- `bridge/gtkb-harness-benchmark-telemetry-integration-002.md` - DEFERRED WI-4584 entry with the same manifest-amendment clear condition.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/BRIDGE-QUALITY-RETROSPECTIVE-2026-06-18.md` - Source retrospective that supplies the failure-class taxonomy motivation.

## Owner Decisions / Input

No new owner decision is required for filing this proposal. The owner already authorized the benchmark project through `DELIB-20265586`, and the DEFERRED entries above record the owner-selected path from transcript `806e5944-602e-41ac-b030-cdd18fd50242`: pause the four benchmark NEW slices, file the manifest amendment first, then revise the deferred slices after the amendment is verified.

This proposal does not approve implementation by itself. Source mutation remains gated on a Loyal Opposition `GO` verdict and a matching implementation-start/work-intent packet for the target paths.

## Requirement Sufficiency

Existing requirements sufficient.

The DEFERRED slice entries already identify the missing manifest-contract requirements: add `author_model_configuration` to the required evidence fields and define an enumerated `FAILURE_CLASSES` tuple. The active authorization packet covers bounded implementation for the benchmark project, and the target paths are limited to the manifest module plus its platform test.

## Spec-Derived Verification Plan

The implementation report must include command output for:

```text
python -m pytest platform_tests/scripts/test_harness_quality_manifest.py -q --tb=short
python -m ruff check scripts/benchmarks/harness_quality_manifest.py platform_tests/scripts/test_harness_quality_manifest.py
python -m ruff format --check scripts/benchmarks/harness_quality_manifest.py platform_tests/scripts/test_harness_quality_manifest.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-benchmark-manifest-amendment
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-benchmark-manifest-amendment
```

The test update must verify:

- `REQUIRED_EVIDENCE_FIELDS` includes `author_model_configuration`.
- The required evidence field list remains ordered, duplicate-free, and has the expected count after the new field is added.
- `FAILURE_CLASSES` is a non-empty tuple of strings, has no duplicates, and exposes at least the normalized classes `claim-accuracy`, `spec-linkage`, `root-boundary`, `scope`, `target-paths-missing`, `preflight-fail`, `test-verification-gap`, and `unscored`.
- Manifest validation or serialization rejects/flags records missing any required evidence field, including `author_model_configuration`, without changing unrelated benchmark behavior.

Specification mapping:

- Bridge authority and project-linkage specs are verified by the two bridge preflight commands and the preserved metadata in this proposal/report chain.
- Dispatch envelope/schema specs are verified by manifest tests covering the new required evidence field and closed failure-class vocabulary.
- Artifact-lifecycle and backlog specs are verified by keeping this as a bridge-scoped proposal under WI-4580 and the active benchmark project authorization instead of direct source mutation.

## Acceptance Criteria

- `scripts/benchmarks/harness_quality_manifest.py` includes `author_model_configuration` in `REQUIRED_EVIDENCE_FIELDS`.
- `scripts/benchmarks/harness_quality_manifest.py` defines a closed `FAILURE_CLASSES` tuple with the normalized taxonomy listed above.
- `platform_tests/scripts/test_harness_quality_manifest.py` covers the new required evidence field and the failure-class tuple invariants.
- The implementation report proves the targeted pytest, ruff, format-check, bridge applicability, and ADR/DCL clause preflight commands passed or documents a valid, bounded exception.
- No fixture corpus, dispatch runner, scoring pipeline, telemetry persistence, dispatcher ranking, durable role assignment, or MemBase mutation is included in this slice.

## Risk / Rollback

Risk is concentrated in downstream tests or tools that assume the old 21-field manifest contract. The change should be backwards-auditable because it is limited to one manifest contract module and one platform test file. If the amendment is rejected or causes regression, rollback is a single commit reverting those two target paths, and the four benchmark slices remain DEFERRED.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-harness-benchmark-manifest-amendment`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: the amendment corrects an incomplete benchmark manifest contract that currently blocks the already-deferred benchmark slices.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
