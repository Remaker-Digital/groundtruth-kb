REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912-wi5172
author_model: GPT-5 Codex
author_model_version: 2026-07-16 runtime
author_model_configuration: Codex Desktop Prime Builder worker context for user-directed PB bridge auto-process

# Revised Implementation Proposal - WI-5172 Adopt Canonical-Carrier Evaluator With Bounded Formatting

bridge_kind: prime_proposal
Document: gtkb-wi5172-canonical-carrier-nonauthority-evaluator
Version: 005
Responds to: bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-004.md
Revises: bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-001.md
Superseded verdict: bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-002.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5172
target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "scripts/check_artifact_decontamination.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py"]

## Revision Claim

Select the NO-GO's preferred adopt-with-formatting path. Preserve `__init__.py` and `decontamination.py` exactly, run Ruff formatting only on the checker and focused test, then bind implementation and independent verification to fresh post-format hashes for all four files. This removes the prior mutually exclusive byte-preservation/format-check contract without broadening functional scope.

## Requirement Sufficiency

Existing requirements and PAUTH are sufficient. Formatting the two named source/test targets is a mechanical, semantic-preserving mutation inside the approved four-file envelope and needs no new owner decision.

## In-Root Placement Evidence

All four targets are inside `E:\GT-KB`; no external, cleanup, retirement, or adopter path is introduced.

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666274`
- `DELIB-20260710-GTKB-MODERNIZATION-CARRIER-EVALUABILITY-AUTHORITY-PAIR-RESULT`
- `DELIB-20260710-GTKB-MODERNIZATION-CANONICAL-CARRIER-DCL-FORMALIZATION-RESULT`
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT`
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-002.md`
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-003.md`
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-004.md`

## Owner Decisions / Input

No new owner decision is required for the preferred path. No Ruff waiver is requested or relied upon.

## Findings Addressed

### Byte-preservation versus format-gate contradiction

Accepted. The two already formatted files remain bound to their unchanged pre-start hashes. The checker and focused test are explicitly authorized for target-only `ruff format`, and preservation begins from fresh independently recorded post-format SHA-256 values. Both Ruff gates are mandatory after formatting.

## Scope Changes

1. Preserve exact bytes of `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py` and `decontamination.py`.
2. Authorize `ruff format` only on `scripts/check_artifact_decontamination.py` and `platform_tests/scripts/test_modernization_artifact_decontamination.py`.
3. Record fresh SHA-256 for all four files after formatting; these become the independent adoption baseline.
4. Keep canonical-carrier evaluator behavior, exact four-target envelope, no-regeneration intent, and non-scope unchanged.

## Pre-Filing Preflight Subsection

- Preliminary completed-content applicability passed with no missing specs or blocking errors.
- Preliminary mandatory clause gate exited 0 with 4 must-apply clauses satisfied and 0 blocking gaps.
- The governed revision helper must rerun both gates against the final bytes before filing.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Canonical-carrier semantics | Run all 24 tests in `platform_tests/scripts/test_modernization_artifact_decontamination.py`. |
| Deterministic live audit | Run `scripts/check_artifact_decontamination.py` against the live governed fixture/registry route and record the result. |
| Mechanical formatting | Run Ruff format only on the checker and focused test, then `ruff format --check` on all four targets. |
| Lint quality | Run `ruff check` on all four targets. |
| Byte-preservation contract | Prove unchanged hashes for `__init__.py` and `decontamination.py`; record and independently verify fresh post-format hashes for checker/test. |
| Governed lifecycle | Implementation starts only after a new independent GO, matching claim, and start packet; report then awaits independent VERIFIED. |

## Acceptance Criteria

- `__init__.py` and `decontamination.py` remain byte-identical to their independently reviewed inputs.
- Only checker and focused test receive Ruff formatting.
- Fresh post-format hashes for all four targets are recorded before adoption and remain unchanged through the report.
- All 24 tests, the live deterministic audit, Ruff lint, and Ruff format-check pass.
- The evaluator proves exact-one operative carrier closure and non-authoritative classification without mutating governed artifacts.
- No cleanup, retirement, unrelated regeneration, bridge rewrite, Git finalization, push, deployment, or release occurs.

## Risk And Rollback

Formatting could conceal semantic drift if scope expands beyond the two named files. Exact path restriction, before/after diff review, 24 tests, live audit, and fresh hashes constrain that risk. Rollback reverts only the four-file candidate after independent review; bridge history remains append-only.

## Recommended Commit Type

`feat`
