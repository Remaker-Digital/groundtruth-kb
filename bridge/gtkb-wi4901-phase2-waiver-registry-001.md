NEW

# gtkb-wi4901-phase2-waiver-registry - Typed Harness Capability Waiver Registry

bridge_kind: prime_proposal
Document: gtkb-wi4901-phase2-waiver-registry
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1266-0a9b-7f32-aa7a-b8b04db29e4d
author_model: GPT-5 Codex
author_model_version: 2026-06-29 runtime
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4901

target_paths: ["config/harness-parity/phase2-waivers.toml", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_harness_parity_phase2.py"]

implementation_scope: source | config | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4899 created the Codex baseline/fungibility matrix and made every unwaived parity gap visible. WI-4901 is the next Phase 2 registry slice: make typed harness capability waivers first-class enough that impossible or owner-accepted gaps can be recorded without hiding executable work.

The implementation should harden `config/harness-parity/phase2-waivers.toml` and `scripts/harness_parity_phase2.py` so waiver records have a stable schema, explicit reason classes, owner-decision evidence, evidence paths or commands, review triggers or expirations, and deterministic evaluator behavior. The evaluator should keep waived cells visible, distinguish active versus retired waivers, and fail closed on malformed waivers.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected config/source/test implementation must proceed through bridge review, GO, implementation-start authorization, report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing requirements and maps them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal includes project authorization, project, work item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry these links forward and execute spec-derived tests.
- `GOV-STANDING-BACKLOG-001` - waived cells must not erase backlog truth; non-waived gaps must continue to produce candidate work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is bounded by the active Phase 2 PAUTH.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - waiver records document harness capability limits without hard-coding role assumptions.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Codex parity remains the baseline; unsupported harness differences require explicit work or typed waiver evidence.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - provider and harness capability floors are registry-derived, not scratchpad-derived.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Phase 2 release readiness requires deterministic evidence for remaining gaps and accepted waivers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - waiver decisions and future parity work remain durable artifacts instead of scratchpad state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the waiver registry preserves traceability between harness limits, owner decisions, tests, and follow-on work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - active, retired, malformed, and future-review waiver states need explicit lifecycle behavior.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner made Harness Parity Phase 2 release-blocking and authorized bounded implementation for the Phase 2 member items.
- `bridge/gtkb-harness-parity-phase-2-baseline-evaluator-001.md` through `-004.md` - evaluator slice that introduced gap-to-work-item proposal output.
- `bridge/gtkb-harness-parity-phase-2-codex-baseline-matrix-001.md` through `-004.md` - WI-4899 matrix slice; current matrix shows 17 unwaived gaps and 12 release-blocking unwaived gaps.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` - OpenRouter harness registry integration model, relevant to provider-backed waiver cases.
- `DELIB-S378-SLICE1-CLI-PACKET-FORM-WAIVER` and `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` - prior examples of explicit owner-approved waiver records; relevant as precedent for recording scope, evidence, and review triggers.

## Owner Decisions / Input

No new owner decision is required before filing this proposal. The active Phase 2 project authorization covers WI-4901 implementation. Individual future waiver records still require their own owner-decision evidence; this slice builds the registry shape and evaluator behavior, not new waivers.

## Requirement Sufficiency

Existing requirements sufficient. WI-4901 requires a governed record shape for impossible parity gaps, and `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` includes WI-4901 in the authorized Phase 2 member set.

## Proposed Implementation

1. Define and document the live waiver record schema in `config/harness-parity/phase2-waivers.toml`, including `id`, `harness`, `dimension`, `reason_class`, `rationale`, `owner_decision`, `evidence`, `review_trigger` or `expires`, `evaluator_behavior`, and `status`.
2. Extend evaluator validation to reject malformed active waiver records, retired waiver records that still affect cells, unsupported reason classes, missing owner-decision evidence, and missing review triggers or expirations.
3. Keep waived cells visible in JSON and Markdown with `status: waived`, `waiver_id`, and a disposition that names the waiver.
4. Keep unwaived gaps producing candidate work-item suggestions.
5. Add focused tests for valid active waiver behavior, malformed waiver failures, retired waiver non-application, wildcard waiver behavior, and Markdown/JSON disposition output.

## Spec-Derived Verification Plan

| Spec / requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run implementation-start `begin` and target validation for exactly the three target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries forward linked specs and records executed focused tests. |
| `GOV-STANDING-BACKLOG-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Extend `platform_tests/scripts/test_harness_parity_phase2.py` to prove waived cells remain visible and unwaived cells still produce candidate work items. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Run `python scripts/harness_parity_phase2.py --format json` and Markdown generation; malformed waivers fail closed while valid waivers are counted. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests must show waiver records keep explicit lifecycle state and traceability instead of suppressing gaps silently. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short
python -m ruff check scripts/harness_parity_phase2.py platform_tests/scripts/test_harness_parity_phase2.py
python -m ruff format --check scripts/harness_parity_phase2.py platform_tests/scripts/test_harness_parity_phase2.py
python scripts/harness_parity_phase2.py --format json
python scripts/harness_parity_phase2.py --format markdown --include-supported --output docs/harness-parity-phase-2-matrix.md
```

## Acceptance Criteria

- [ ] Waiver schema is explicit and includes owner-decision evidence plus review trigger or expiration.
- [ ] Malformed active waiver records produce `invalid_waiver` release-blocking cells.
- [ ] Retired waivers do not suppress current gaps.
- [ ] Valid active waivers mark matching cells as `waived`, preserve `waiver_id`, and remain visible in JSON/Markdown output.
- [ ] Unwaived gaps still produce candidate work-item suggestions.
- [ ] Focused tests, ruff lint, and ruff format checks pass.

## Risk / Rollback

The main risk is over-waiving release-blocking gaps. The implementation must bias toward fail-closed validation and visible waiver accounting. Rollback is a single commit revert of the three target files; bridge artifacts remain append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4901-phase2-waiver-registry`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the eventual implementation adds a governed Phase 2 waiver-registry capability and evaluator behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
