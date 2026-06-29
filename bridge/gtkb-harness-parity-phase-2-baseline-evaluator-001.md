NEW

# gtkb-harness-parity-phase-2-baseline-evaluator (Slice 0) - Harness Parity Phase 2 Baseline Evaluator

bridge_kind: prime_proposal
Document: gtkb-harness-parity-phase-2-baseline-evaluator
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06-29 runtime
author_model_configuration: Codex desktop, Prime Builder session, governed bridge proposal

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4900

target_paths: ["scripts/harness_parity_phase2.py", "config/harness-parity/phase2-waivers.toml", "docs/harness-parity-phase-2.md", "platform_tests/scripts/test_harness_parity_phase2.py"]

implementation_scope: source | config | documentation | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Harness Parity Phase 2 is now the release-blocking umbrella for making the registered harness fleet fungible with Codex wherever each harness permits. This Slice 0 implements the deterministic baseline evaluator needed before deeper adapter edits: a repo-local CLI that inventories the Codex baseline, evaluates every registered harness against that baseline, reads typed waiver records for impossible gaps, emits machine-readable and human-readable parity reports, and proposes concrete work-item language for unwaived gaps without mutating MemBase.

This slice intentionally does not close every harness gap. It creates the measurement and waiver spine that lets the rest of Phase 2 proceed without subjective or scratchpad-based parity claims. Follow-on slices will use the evaluator output to close Antigravity, Cursor, Ollama, OpenRouter, skill/hook/command projection, no-window, and full release-smoke gaps tracked by `PROJECT-HARNESS-PARITY-PHASE-2`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - This implementation changes script, config, test, and documentation surfaces and therefore must proceed through the bridge, preserve append-only bridge state, and receive independent LO review and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The proposal cites the governance and parity requirements that constrain the work and maps them to tests below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal includes `Project Authorization`, `Project`, and `Work Item` metadata for the active Phase 2 project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must carry forward these links and execute tests derived from the linked requirements.
- `GOV-STANDING-BACKLOG-001` - Phase 2 work items live in MemBase; the evaluator may propose backlog language but must not create, resolve, or mutate work items unless invoked through governed CLI surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The implementation is bounded by `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` and does not bypass per-slice bridge GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Phase 2 parity findings that cross the threshold into future work must become durable backlog or waiver artifacts instead of staying in scratchpads.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The evaluator must preserve traceability between harness gaps, work items, waivers, tests, reports, and owner decisions as an artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The evaluator must distinguish open, blocked, waived, verified, retired, and candidate parity states rather than flattening them into generic warnings.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - Harness parity means roles attach to capable harnesses rather than a fixed vendor/runtime; the evaluator must classify feasible role/task fungibility per harness.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - The evaluator must detect silent single-harness drift and report unwaived parity gaps rather than assuming Codex-only behavior is enough.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex is the baseline for current hook capability; other harnesses must either match feasible hook behavior or use explicit helper/waiver paths.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - Registered harnesses must have readiness/capability surfaces that can be inspected by the evaluator.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Dispatcher selection/readiness and headless worker behavior are part of harness parity and release readiness.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Phase 2 is a release blocker; release health must be supported by deterministic test/report evidence rather than prose assertions.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - Owner made Phase 2 a release blocker and required full feasible harness parity plus recurring parity evaluation/proposal tooling.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - Prior cross-harness parity program authorization established bridge-governed parity implementation discipline; this slice extends that posture into Phase 2 release readiness.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` - Phase 1 parity work established bidirectional, applicability-scoped parity as the governing frame; Phase 2 broadens that from artifact parity to operational fungibility.
- `DELIB-20266276` - Daemon-resilience scope lock required full-harness topology and real-harness smoke evidence; the evaluator will surface this as a release-health parity dimension.
- `DELIB-20263447` - Harness benchmarking must be exposed through Dispatcher/Bridge CLI surfaces and must treat CLI-governed mutation as a first-class use case; the evaluator follows that CLI-first pattern.
- `INTAKE-b4928376` - Bridge review eligibility is harness-agnostic; the evaluator must not confuse durable role labels with actual review/verdict capability.
- `INTAKE-2ce995f2` - Bounded parallel cross-harness dispatch changed the operating model from binary same-role suppression to capability/claim-aware concurrency; the evaluator must inspect dispatchability without assuming one active session blocks another.

## Owner Decisions / Input

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` captures the owner directive to create and execute Harness Parity Phase 2 as a release blocker.
- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` is the active snapshot-scoped project authorization for the current 40 Phase 2 member work items.
- The proposal does not request credential lifecycle changes, production deployment, GitHub settings mutation, or any bypass of bridge GO / implementation-start / LO verification.

## Requirement Sufficiency

Existing requirements sufficient - the owner directive, active project authorization, linked parity/governance specifications, and accepted Phase 2 work items (`WI-4899`, `WI-4900`, `WI-4901`, `WI-4907`) are sufficient for this bounded evaluator/baseline slice. New formal GOV/ADR/DCL/SPEC records may be proposed by later slices if the evaluator exposes an ungoverned policy gap, but this slice can implement the measurement/waiver/reporting tool without creating new formal requirements.

## Spec-Derived Verification Plan

The implementation report must execute and report:

```text
python -m pytest platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short
python scripts/harness_parity_phase2.py --project-root . --format json --output .gtkb-state/harness-parity/phase2-latest.json
python scripts/harness_parity_phase2.py --project-root . --format markdown --output .gtkb-state/harness-parity/phase2-latest.md
```

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` are covered by the bridge filing preflights plus a test that the evaluator report includes project/work-item/authorization provenance and never claims implementation authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` are covered by this proposal's spec-to-test mapping and by tests asserting the evaluator emits deterministic evidence for each checked parity dimension.
- `GOV-STANDING-BACKLOG-001` is covered by tests that gap-to-work-item output is advisory text/commands only and does not mutate MemBase in normal report mode.
- `GOV-HARNESS-ROLE-PORTABILITY-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, and `GOV-HARNESS-ONBOARDING-CONTRACT-001` are covered by fixture tests for supported/blocked/waived role-task cells, harness root discovery, skill/hook/command projection checks, and readiness-probe discovery.
- `ADR-DISPATCHER-ARCHITECTURE-001` is covered by tests that dispatcher eligibility/readiness dimensions are represented without changing live dispatcher config.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` is covered by strict-mode behavior: unwaived release-blocking gaps produce a non-zero result and name owning WIs or candidate WI text.

## Risk / Rollback

Risk is bounded to a new reporting script, one waiver config file, one documentation page, and focused tests. The evaluator must be read-only by default and must not change dispatcher config, MemBase records, bridge state, credentials, or provider settings. Generated latest reports under `.gtkb-state/harness-parity/` are runtime evidence and are not part of this proposal's target paths.

Rollback is a single commit revert of the four target paths. Because the evaluator is additive and read-only by default, rollback does not require data migration.

## Bridge Filing

This proposal is filed in the bridge directory as the next status-bearing numbered
bridge file for `gtkb-harness-parity-phase-2-baseline-evaluator`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - this adds a new Phase 2 harness parity evaluation capability, waiver config, documentation, and tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
