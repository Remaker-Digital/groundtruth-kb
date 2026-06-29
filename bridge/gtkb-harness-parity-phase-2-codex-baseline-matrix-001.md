NEW

# gtkb-harness-parity-phase-2-codex-baseline-matrix - Codex Baseline And Fungibility Matrix

bridge_kind: prime_proposal
Document: gtkb-harness-parity-phase-2-codex-baseline-matrix
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f122f-9a0e-7fc0-898d-66ed1b6a58c7
author_model: GPT-5 Codex
author_model_version: 2026-06-29 runtime
author_model_configuration: Codex desktop, Auto-builder Prime Builder automation

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4899

target_paths: ["docs/harness-parity-phase-2-matrix.md", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_harness_parity_phase2.py", "config/harness-parity/phase2-waivers.toml"]

implementation_scope: source | documentation | config | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4900 created the read-only Phase 2 evaluator and proved it can emit deterministic harness parity cells. WI-4899 is the next release-blocking slice: turn that raw evaluator output into the canonical Codex-as-baseline matrix for Harness Parity Phase 2.

The implementation should add a durable matrix document and extend the evaluator/report tests so every registered harness/task cell is classified as supported, needs adapter, blocked, or waived. Every non-supported cell must link to a concrete Phase 2 work item candidate, existing work item, or typed waiver entry. The matrix must cite live repo-governed inputs only: harness registry, dispatcher rules, capability registry, waiver config, project authorization, and current Phase 2 work items.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected script/config/test/doc implementation must proceed through the bridge, receive LO review, and use implementation-start authorization before mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal names the governing specs and maps each to verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal includes project authorization, project, work item, and target path metadata for Phase 2.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward these links and execute tests derived from them.
- `GOV-STANDING-BACKLOG-001` - non-supported parity cells must point to governed backlog work or typed waivers, not scratchpad claims.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is bounded by `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - the matrix must show which harnesses can perform Prime Builder, Loyal Opposition, advisory, verification, proposal/report, and release-support work.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Codex-only behavior must not be treated as sufficient when other harnesses are registered for the same role/task.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hookless or non-Codex harness differences must be represented as adapter work or typed waivers.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - the matrix must use registered harness capability/readiness surfaces rather than informal harness notes.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher receive/readiness and event-source surfaces are part of the parity baseline.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Phase 2 is release-blocking; matrix evidence must be deterministic and testable.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner made Harness Parity Phase 2 release-blocking and required a recurring parity evaluator plus concrete gap work.
- `bridge/gtkb-harness-parity-phase-2-baseline-evaluator-001.md` - approved evaluator proposal that created deterministic parity cells and candidate work-item output.
- `bridge/gtkb-harness-parity-phase-2-baseline-evaluator-003.md` - implementation report showing the first evaluator run found 17 unwaived gaps, including 12 release-blocking gaps.
- `bridge/gtkb-harness-parity-phase-2-baseline-evaluator-004.md` - LO VERIFIED verdict for the evaluator slice.
- `INTAKE-b4928376` - bridge review eligibility is harness-agnostic; matrix cells must not overfit to durable role labels.
- `INTAKE-2ce995f2` - bounded parallel cross-harness dispatch requires capability/claim-aware classification rather than binary role suppression.

## Owner Decisions / Input

No new owner decision is required. The owner directive and active Phase 2 PAUTH already authorize this bounded implementation slice. Credential lifecycle, provider key changes, production deployment, and GitHub settings mutation remain out of scope.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4899 defines the matrix acceptance criteria, WI-4900 supplies the evaluator spine to extend, and `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` authorizes bridge-governed implementation of this Phase 2 member item.

## Spec-Derived Verification Plan

| Spec / requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run implementation-start `begin` and `validate`; target validation must authorize exactly the four target paths in this proposal. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry forward the linked specs and record targeted test/evaluator evidence. |
| `GOV-STANDING-BACKLOG-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Add or extend tests proving every non-supported matrix cell links to an existing Phase 2 WI, generated candidate WI, or waiver record. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Add or extend tests proving matrix cells are derived from registry, dispatcher, capability, hook/helper, readiness, and waiver evidence rather than hard-coded prose. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Run the evaluator in JSON and Markdown modes; matrix output must remain deterministic and surface remaining release-blocking gaps. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short
python -m ruff check scripts/harness_parity_phase2.py platform_tests/scripts/test_harness_parity_phase2.py
python -m ruff format --check scripts/harness_parity_phase2.py platform_tests/scripts/test_harness_parity_phase2.py
python scripts/harness_parity_phase2.py --project-root . --format json --output .gtkb-state/harness-parity/phase2-latest.json
python scripts/harness_parity_phase2.py --project-root . --format markdown --output .gtkb-state/harness-parity/phase2-latest.md
```

## Risk / Rollback

Risk is bounded to an additive matrix document plus targeted evaluator/test/config changes. The implementation must remain read-only by default and must not mutate MemBase or dispatcher state while generating the matrix. Rollback is a single revert of the four target paths; bridge history remains append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-harness-parity-phase-2-codex-baseline-matrix`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - the slice adds the canonical Phase 2 baseline matrix artifact and extends the evaluator evidence surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
