NEW

# WI-5414: Restore the missing artifact-lifecycle package residue

bridge_kind: prime_proposal
Document: gtkb-wi5414-artifact-lifecycle-package-residue
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5414

target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt exactly the two pre-existing untracked artifact-lifecycle package files
that were omitted when WI-5347 was physically finalized. Commit `42a252ab`
already contains the corresponding deterministic checker and 24-test contract,
but HEAD cannot import `groundtruth_kb.artifact_lifecycle` without these source
carriers. The current candidate passes all 24 focused tests.

This is a byte-preserving residue closure. It does not change the package,
expand behavior, repair the later WI-5406 timeout contract, alter the project
check loader, mutate `groundtruth.db`, or perform any Git operation. A later
exact mechanical finalizer may commit only the independently VERIFIED source
bytes under separate authority.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — requires deterministic lifecycle classification and residual-reference enforcement rather than a partial checker-only landing.
- `GOV-WORK-TREE-HYGIENE-001` — requires every dirty source carrier to have explicit ownership and governed finalization without absorbing foreign dirt.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires independent GO before protected source adoption and independent verification after implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — binds this proposal to the source requirement and exact verification surface.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5414 to its active tree-stabilization project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the independent verdict to evaluate the cited requirements through the focused tests and checker.

## Prior Deliberations

- `INTAKE-eb0bbcad` — Intake: Tracked artifact list is canonical for cleanup essentiality
- `INTAKE-e0d49108` — Intake: Lifecycle events are append-only MemBase/KB authority with generated projections

The first record establishes that physical source presence is evaluated from
the tracked repository rather than inferred from terminal workflow metadata.
The second establishes append-only lifecycle evidence; this proposal therefore
adds the missing implementation instead of rewriting WI-5347 history.

## Owner Decisions / Input

The owner authorized the full modernization program at the project level and
directed every discovered flaw or omission to become an `origin=hygiene` work
item while work continues. Active authorization
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` covers source,
test, metadata, and governance evidence while retaining independent GO,
claim/start, VERIFIED, and mechanical Git gates. No additional owner decision
is required for this proposal or its independently GO-approved source adoption.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
defines the artifact lifecycle behavior, `GOV-WORK-TREE-HYGIENE-001` governs
physical residue closure, and the bridge/project-linkage specifications govern
the transaction. No requirement change is proposed.

## Spec-Derived Verification Plan

`ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` and the behavior-bearing package
surface map to the 24 deterministic lifecycle, loading-graph, and live-repository
tests. Expected result: 24 passed.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q --tb=short --timeout=600
```

`GOV-WORK-TREE-HYGIENE-001` maps to exact source hygiene and ownership checks.
Expected result: no lint, format, whitespace, or undeclared-file discrepancy
within the two target paths.

```text
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py
```

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` maps to an independent LO
review of the exact two source hashes plus the commands above. Expected result:
the next verdict is `VERIFIED` only when the candidate bytes match the reviewed
scope and all evidence passes.

## Risk / Rollback

Risk is bounded to packaging a deterministic authority/loading-graph scanner;
the principal failure mode is accidentally absorbing WI-5406 or neighboring
dirty files. Exact target paths, byte hashes, and focused tests constrain that
risk. Under separate mechanical authority, finalization should be one focused
`fix` commit containing only these two additions. Rollback, if later required,
is a separately governed revert of that exact commit; no existing history is
amended and no foreign worktree content is touched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5414-artifact-lifecycle-package-residue`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — restores source implementation omitted from an earlier independently
reviewed lifecycle slice; it is not a new feature or a test-only change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
