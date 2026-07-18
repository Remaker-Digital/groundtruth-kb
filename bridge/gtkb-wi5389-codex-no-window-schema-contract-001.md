NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; governed WI-5389 proposal


bridge_kind: prime_proposal
Document: gtkb-wi5389-codex-no-window-schema-contract
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5389-CODEX-SCHEMA-SOT-20260717
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5389
Test: TEST-11562
target_paths: ["groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py", "scripts/dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py"]
mutation_classes: ["source", "test", "bridge", "governance_evidence"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Implementation Proposal - WI-5389 Codex No-Window Schema Contract

## Summary

Restore Codex A Prime Builder dispatch readiness by removing the divergent
Codex private-desktop proof contracts currently embedded in
`scripts/dispatcher_runtime.py` and `scripts/verify_codex_dispatch.py`.

Current HEAD requires schema version 2 in the dispatcher runtime and schema
version 3 in the standalone verifier. A fresh private-desktop proof reports
schema version 3, two successful runs, a complete write/read/remove sentinel
lifecycle, the requested and observed workspace-write profile, successful
wrapper execution, and zero visible windows. The verifier accepts that proof;
the dispatcher rejects the same proof as
`codex_no_window_verification_legacy_schema`, so no A worker can launch.

The historical project identifier is metadata only. There is no Goose or G
harness, and this proposal introduces no such harness, route, role, registry
entry, or behavior.

## Requirement Sufficiency

The linked work item, test, active bounded PAUTH, and existing dispatcher and
harness requirements are sufficient for this reliability repair. No new public
API, dispatch policy, role assignment, eligibility state, routing rule, TAFE
state, provider credential, or owner decision is required.

WI-5389 records a captured dependency on WI-5310, while WI-5310's current
NO-GO requires a fresh successful A dispatch. The active bounded PAUTH
explicitly resolves that circular proof dependency by making WI-5389 the
prerequisite closure for WI-5310 D4. This proposal does not otherwise weaken
or bypass WI-5310's independent requirements.

## Proposed Scope

1. Add one package-canonical module that owns the Codex no-window evidence
   schema version and structural validation contract.
2. Make the dispatcher runtime and standalone Codex verifier consume that
   shared contract while preserving their caller-specific timestamp,
   readiness, failure-class, and report assembly.
3. Preserve every fail-closed check for malformed schema, insufficient runs or
   command steps, missing marker proof, wrapper failure, missing private
   desktop containment, permission-profile mismatch, incomplete sentinel
   lifecycle, sentinel residue, visible-window evidence, non-passing result,
   missing timestamp, expiry, and staleness.
4. Add focused package, dispatcher-runtime, and standalone-verifier regression
   coverage proving both consumers accept and reject the same structural
   evidence.
5. After independent verification, focused finalization, and a quiescent
   governed daemon-generation handoff, require one genuine dispatcher-produced
   A/PB worker to complete substantive governed bridge work without visible
   windows.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5389; TEST-11562; current HEAD dispatcher schema version 2; current HEAD verifier schema version 3; fresh canonical dispatcher report classifying A as codex_dispatch_not_ready",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001; GOV-HARNESS-ONBOARDING-CONTRACT-001; ADR-DISPATCHER-ARCHITECTURE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "One package-canonical Codex no-window evidence contract is consumed by both the dispatcher runtime and standalone verifier",
  "before_behavior": "The standalone verifier accepts the fresh schema-v3 private-desktop proof while the dispatcher runtime rejects the identical proof as legacy schema and cannot launch A",
  "after_behavior": "Both consumers apply one strict structural contract, accept the same valid schema-v3 evidence, reject the same malformed evidence, and retain caller-specific timestamp and reporting behavior",
  "self_descriptive_naming": "codex_no_window_verification, schema_failure_reason, and TEST-11562 identify the evidence contract, validation result, and integration boundary directly",
  "obsolete_guidance_disposition": "The duplicated schema constants and structural validators are replaced by one package contract; no historical bridge or MemBase evidence is rewritten",
  "history_preservation": "Numbered bridge files, MemBase rows, prior no-window evidence, WI-5227 ownership, exact source history, and unrelated worktree bytes remain preserved",
  "baseline": "Current valid schema-v3 evidence passes the standalone verifier but the live dispatcher repeatedly records codex_no_window_verification_legacy_schema and launches no A worker",
  "expected_result": "Focused tests prove identical structural outcomes, read-only dispatcher readiness accepts current schema-v3 evidence after governed landing, and one substantive dispatcher-produced A/PB artifact completes with zero visible windows",
  "rollback": "A separately governed focused revert removes only the shared contract, its tests, and the two consumer delegations after preserving append-only bridge and MemBase evidence",
  "hard_invariants": "No eligibility, role, cap, route, TAFE, lease, runtime-state, credential, live-worker, push, deployment, release, foreign-hunk, or historical-evidence mutation",
  "fail_closed_conditions": "Any exact-target owner is nonterminal, target attribution is ambiguous, PAUTH or GO is stale, the shared validator weakens a current schema-v3 check, consumers disagree, focused tests fail, a visible window appears, effective permissions differ, or a genuine A worker cannot complete governed work",
  "essential_context_preservation": "Verification retains exact reason codes, schema version, run and command cardinality, marker proof, wrapper and private-desktop evidence, requested and effective profiles, sentinel lifecycle, visible-window result, timestamps, target hashes, and independent bridge/start/finalization evidence"
}
```

## Exact-Target Sequencing

`scripts/dispatcher_runtime.py` and
`platform_tests/scripts/test_dispatcher_runtime.py` currently contain
unfinalized WI-5227 implementation hunks awaiting independent Loyal Opposition
verification. No WI-5389 implementation may start until WI-5227 and every
other current exact-target owner are terminal, the exact target set is
reconciled against current HEAD, a matching claim is acquired, and a fresh
schema-v3 implementation-start packet authorizes all target bytes.

The current `scripts/verify_codex_dispatch.py` schema-v3 behavior is preserved
as candidate evidence only. It is not independently sufficient authority for
the shared-contract implementation.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes
  governed repair of fleet defects while preserving dispatchability and the
  normal bridge, claim, implementation-start, verification, and focused-commit
  gates.
- `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` records the
  current independent dependency hold and the requirement for a fresh
  substantive dispatcher-produced A/PB artifact.
- `bridge/gtkb-wi5227-ollama-abrupt-exit-diagnostics-007.md` records the current
  exact-target owner whose runtime and test hunks must reach terminal
  disposition before WI-5389 implementation starts.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-015.md` records the separate
  current ACL-remediation blocker and does not authorize this source repair.

## Owner Decisions / Input

No new owner input is required. The active fleet objective requires Codex A to
remain PB-only and fully dispatchable, prohibits eligibility/configuration
changes as a repair, and requires every implementation to proceed through the
normal governed bridge lifecycle.

## Cross-Harness Disposition

| Harness | Disposition |
| --- | --- |
| A / Codex | Direct repair target. Preserve PB-only assignment and max-items 1; prove one fresh substantive governed PB dispatch after VERIFIED landing. |
| D / Ollama | No behavior or configuration change. Preserve its Loyal Opposition lane and do not disturb current backoff or future workers. |
| F / OpenRouter | No behavior or configuration change. Preserve current Loyal Opposition routing and all live workers. |
| B, C, E, H | No behavior, role, eligibility, cap, or configuration change; outside this Codex-specific repair. |

## Specification-Derived Verification

| Spec / requirement | Required verification |
| --- | --- |
| `TEST-11562`; `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused package, dispatcher-runtime, and standalone-verifier tests prove one shared schema/version/validator and identical structural pass/fail outcomes. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | Full affected runtime and verifier modules pass; read-only dispatcher report/status/health show the current schema-v3 proof is accepted after governed generation handoff. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | A genuine dispatcher-produced A/PB worker uses private-desktop containment, observes the required workspace-write profile, completes its sentinel lifecycle, emits no visible window, and produces substantive governed bridge work. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Independent GO, active exact PAUTH, terminal peer ownership, matching claim, operation-time applicability, and schema-v3 implementation-start authorization all pass before mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-WORK-TREE-HYGIENE-001` | Ruff check/format, Python compilation, exact diff checks, focused tests, independent verification, and a focused commit cover only authorized hunks. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Before/after read-only topology evidence proves no eligibility, role, cap, route, TAFE, lease, credential, live-worker, push, deployment, or release mutation. |

## Acceptance Criteria

- The dispatcher runtime and standalone verifier import one package-canonical
  schema version and structural validator.
- Current valid schema-v3 evidence receives the same successful structural
  classification from both consumers.
- Every malformed containment, wrapper, profile, sentinel, marker, run-count,
  command-count, and visible-window case fails closed in both consumers with
  stable reason codes.
- Existing timestamp, expiry, result-state, failure-class, and caller-specific
  report behavior remains covered.
- A remains PB-only with max-items 1 and remains dispatchable throughout the
  repair; no harness eligibility or dispatcher configuration changes.
- No live worker is interrupted, terminated, recovered, reoffered, or deprived
  of its full allowance by this work.
- The implementation reaches independent VERIFIED and a focused commit before
  a governed generation handoff.
- A fresh dispatcher-produced A/PB worker completes substantive governed bridge
  work with zero visible windows.

## Risks And Rollback

The main risk is accidentally weakening the stricter schema-v3 contract while
deduplicating it. The focused test matrix must lock every current strict check
before either caller delegates to the shared validator.

Another risk is absorbing WI-5227 or other foreign dirty hunks from the shared
runtime/test targets. Operation-time authorization must fail closed unless
exact ownership is terminal and candidate hunks are attributable.

Rollback is a focused revert of the shared module, its tests, and the two
consumer delegations. Append-only work-item, proposal, implementation-report,
and verdict evidence remains historical.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py`
- `groundtruth-kb/tests/test_codex_no_window_verification.py`
- `scripts/dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

## Recommended Commit Type

`fix(dispatch):`
