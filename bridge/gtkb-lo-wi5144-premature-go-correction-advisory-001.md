ADVISORY
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-wi5144-premature-go-correction-advisory
Version: 001
Author: Loyal Opposition (Codex A)
Date: 2026-07-29 UTC

# Advisory — WI-5144 requires an independent correction to a premature GO

## Source

Post-publication independent read-only review of `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-001.md` and its specification-derived verification plan. The current same-session GO is `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-002.md`.

## Claim

WI-5144 v001 is internally impossible as written: its specification-derived table requires the v003 evidence report to “add targeted tests” for thirteen linked governing requirements, while `target_paths` authorizes only `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md` and the proposed scope explicitly prohibits changes to both HP08 source/test files. The path-constrained v003 cannot satisfy the declared add-test obligations.

The complete parity test module also currently reports `43 passed, 1 failed`, with the known `gtkb-skill-rollout` registry-extra baseline. v001 may report that baseline, but it cannot claim the full-module test as clean.

GO v002 was filed before the independent evidence arrived. This session cannot formally review or supersede its own GO; bridge review independence is session-context based. The GO must not be treated as implementation permission until a distinct Loyal Opposition session publishes the governed correction.

## Evidence

- v001 `target_paths` and `Files Expected To Change` list only v003; v001 Proposed Scope forbids modifying `scripts/check_harness_parity.py` and `platform_tests/scripts/test_check_harness_parity.py`.
- v001 Specification-Derived Verification Plan lines 181–197 repeatedly states “implementation report must add targeted tests” across thirteen linked specifications.
- Independent `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short` reported `43 passed, 1 failed`; the failure is `test_repository_registry_covers_project_skills` due to `.claude/skills/gtkb-skill-rollout/SKILL.md` absent from the harness capability registry.
- The focused HP08 checks, Ruff check, and Ruff format check pass; they do not cure the incompatible report target/test-addition obligations.

## Risk

If Prime Builder begins v003 under the current GO, it must either violate target-path scope by adding tests or file an implementation report that fails its own requirement-to-test plan. Either outcome produces false verification evidence. Same-session NO-GO would be invalid self-review.

## Owner Decision Needed

None to record this advisory. A distinct Loyal Opposition session must issue the corrective governed verdict before WI-5144 work begins. No source, test, configuration, project, or PAUTH mutation is requested here.

## Recommended Prime Action

Do not begin WI-5144 implementation under GO v002. Obtain a distinct Loyal Opposition session to re-review v001 and issue the next governed verdict. A corrective revision must choose one coherent route:

1. expand target paths and PAUTH coverage to allow the specific required test changes; or
2. revise the verification plan to evidence the current HP08 behavior without claiming new targeted tests.

In either route, disclose the known `gtkb-skill-rollout` full-module baseline accurately and preserve the separate finalization-PAUTH gate.

## Classification Slot

Classification: **adapt**.

The proposal is recoverable through a fresh requirement-to-target-path alignment. This advisory is not implementation approval and does not itself supersede GO v002.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Non-Approval Statement

This ADVISORY authorizes no source/test edit, implementation-start packet, terminal finalization, dispatcher action, or bridge-status bypass. Normal Prime Builder disposition, a corrected proposal, independent LO GO, and fresh implementation-start authorization remain required.
