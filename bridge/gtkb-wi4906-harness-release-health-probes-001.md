NEW

# gtkb-wi4906-harness-release-health-probes - Release Health Probe Alignment

bridge_kind: prime_proposal
Document: gtkb-wi4906-harness-release-health-probes
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29T09:28:13Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4906

target_paths: ["scripts/harness_parity_phase2.py", "scripts/verify_codex_dispatch.py", "scripts/verify_claude_dispatch.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_verify_claude_dispatch.py"]

implementation_scope: source | test | release-health
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4902 repaired unclassified capability-registry drift, but the Phase 2
release-health matrix still reports release-blocking gaps that are partly
evaluator blind spots: the no-window dimension only scans registry argv text,
so it misses real wrapper-level `CREATE_NO_WINDOW` evidence in the dispatcher
and harness shims. The same matrix also lacks deterministic Codex and Claude
readiness probe scripts, making release evidence rely on indirect wrapper
existence instead of explicit probe contracts.

This proposal authorizes a bounded WI-4906 slice to align the Phase 2
release-health evaluator with actual release evidence. The implementation will
add Codex and Claude readiness probe scripts, teach
`scripts/harness_parity_phase2.py` to recognize wrapper/runtime no-window
evidence rather than requiring literal no-window tokens in harness registry
argv, and add focused tests. It will not flip Cursor, Claude, or Antigravity
dispatchability, change durable role assignments, alter provider credentials,
or record typed waivers. Remaining true dispatchability gaps stay assigned to
WI-4903, WI-4904, WI-4885, and WI-4907.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires proposal, GO, implementation report, and verification for protected source/test changes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite governing requirements and define spec-derived verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the Project Authorization, Project, and Work Item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the implementation report to execute tests derived from linked specifications.
- `GOV-STANDING-BACKLOG-001` - Requires remaining parity gaps to stay in MemBase/project work items rather than scratch state.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Requires cross-harness enforcement and parity gaps to be explicitly evaluated, corrected, or waived.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Constrains dispatcher readiness evidence and release-health evaluation for harness selection.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Requires governed release-readiness evidence before treating harness parity as release-healthy.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Allows this bounded project-authorized implementation only through the normal bridge/GO/report/verification path.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires project-relevant release-health decisions and findings to remain in governed artifacts rather than scratchpads.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Supports the artifact-first approach of executable probes and matrix evidence instead of prose-only release claims.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Keeps residual harness gaps visible as work items, waivers, or release-gate findings rather than ambiguous notes.

## Prior Deliberations

- `INTAKE-b4928376` - Bridge review eligibility is harness-agnostic; durable role is a fallback, not a review/verdict gate.
- `INTAKE-97211546` - Harness registrar role assignment and independent review requirements.
- `INTAKE-2ce995f2` - Bounded parallel cross-harness auto-dispatch requires truthful per-harness readiness and capability evidence.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` - Provider harness registry integration model; relevant because OpenRouter/Ollama no-window and readiness evidence must be explicit.
- `DELIB-S422-OR-FRAMEWORK-CHOICE` - Provider harness runner framework choice; relevant because release health checks need wrapper-aware evidence.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - Owner directive creating Harness Parity Phase 2 as a release blocker.

This proposal builds on WI-4902 by moving from registry classification to
release-health evidence quality. It deliberately avoids role topology flips or
provider credential work, because those are separable dispatchability slices.

## Owner Decisions / Input

No new owner decision is required before LO review. The work is inside
`PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` and implements
the owner-directed Phase 2 release-blocking harness parity program captured in
`DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`.

## Requirement Sufficiency

Existing requirements sufficient - this slice is governed by the linked bridge,
cross-harness enforcement, dispatcher architecture, release-readiness testing,
standing backlog, and project implementation authorization records. No new or
revised formal requirement is needed before implementation.

Bulk-operation visibility evidence: this is not a bulk backlog/spec mutation
and does not require a separate inventory artifact or review-packet. Residual
work remains visible through the existing Harness Parity Phase 2 project work
items and the Phase 2 matrix candidate-work-item output.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge threads --wi WI-4906` plus implementation-start authorization before protected edits | Latest GO exists before implementation and packet validates target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4906-harness-release-health-probes` | `preflight_passed: true`, `missing_required_specs: []`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4906-harness-release-health-probes` | No blocking clause gaps for project linkage/authorization evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest targets below | New readiness/no-window evaluator behavior is exercised. |
| `GOV-STANDING-BACKLOG-001` | `python scripts/harness_parity_phase2.py --project-root . --format markdown --strict` | Residual findings stay explicit and map to existing follow-on WIs; this slice does not hide true gaps. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Phase 2 matrix and focused tests | Cross-harness readiness/no-window states are classified from deterministic evidence. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Probe tests and phase2 matrix | Dispatch readiness is represented by deterministic probe scripts rather than prose claims. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Full focused command bundle in the implementation report | Release-health gate evidence is executable and repeatable. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4906-harness-release-health-probes` | Target-path packet authorizes only this slice. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report and Phase 2 matrix output | Release-health claims are preserved as bridge/test artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | New probe scripts and tests | Harness readiness evidence is executable artifact output. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Matrix residual-gap output | Residual gaps remain routed to work-item/waiver lifecycle surfaces. |

Focused implementation verification commands:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_verify_claude_dispatch.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\harness_parity_phase2.py scripts\verify_codex_dispatch.py scripts\verify_claude_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_verify_claude_dispatch.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\harness_parity_phase2.py scripts\verify_codex_dispatch.py scripts\verify_claude_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_verify_claude_dispatch.py
groundtruth-kb\.venv\Scripts\python.exe scripts\harness_parity_phase2.py --project-root . --format markdown --strict
groundtruth-kb\.venv\Scripts\python.exe scripts\windows_no_window_spawn_audit.py --release-runtime
```

## Risk / Rollback

Primary risk is false-positive release-health confidence if wrapper-level
no-window evidence is matched too broadly. Mitigation: keep the accepted
evidence map explicit by harness/wrapper path and test both supported and
unsupported cases. Rollback is a single commit reverting the new probe scripts,
evaluator change, and focused tests.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4906-harness-release-health-probes`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `fix:`

`fix:` is appropriate because this slice repairs release-health classification
and adds missing deterministic probes for existing harnesses; it does not add a
new user-facing feature surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
