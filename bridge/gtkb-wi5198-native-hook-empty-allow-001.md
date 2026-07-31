NEW

# WI-5198 - Treat successful empty native-hook output as allow/no-op

bridge_kind: prime_proposal
Document: gtkb-wi5198-native-hook-empty-allow
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: GPT-5 family (Codex)
author_model_version: not exposed by harness
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5198-NATIVE-HOOK-ALLOW-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5198

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the shared native-full cloud-harness hook runner so an exit-0 hook with
empty stdout is treated as an allow/no-op and evaluation continues to the next
registered hook. The current `invoke_native_hooks` implementation raises
`CloudHarnessError` for this successful content-free result. Alibaba Cloud
Studio harness H therefore aborts every tool-using dispatched review when it
reaches the recovery-stub `PreToolUse` hook `spec-before-code.py`, which exits 0
without output.

The fix is intentionally narrow: replace only the native-hook empty-output
failure with continuation, and add focused shared-base and Alibaba regressions.
Nonzero exits, timeouts, malformed non-empty JSON, explicit block decisions,
root-boundary enforcement, and all existing guard-adapter behavior remain
fail-closed.

## Requirement Sufficiency

Existing requirements sufficient.

`ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` requires H to inherit the full
native hook system; `ADR-CLOUD-HARNESS-TEMPLATE-001` assigns native-hook behavior
to the shared cloud-harness runtime; `SPEC-INTAKE-9ec893` requires maximal-hook
non-GUI harness integrations; and `GOV-HARNESS-ONBOARDING-CONTRACT-001` plus
`DCL-OLLAMA-TOOL-PARITY-GATE-001` preserve the separate fail-closed guard floor.
No formal carrier needs amendment for this defect repair.

## Proposed Change

1. In `invoke_native_hooks`, after an exit-0 hook result is normalized, treat
   empty stdout as allow/no-op by continuing to the next hook registration.
2. Preserve all failure behavior for timeout, nonzero exit, malformed non-empty
   JSON, non-object output, and explicit block/deny decisions.
3. Add a shared-base regression proving an exit-0 empty `PreToolUse` hook does
   not abort a tool loop and later hooks/tool behavior continue normally.
4. Add a hermetic Alibaba regression using the real Alibaba native-hook adapter
   as the runner, proving its deliberately empty pre-tool result is accepted by
   the shared native-hook layer.
5. Re-run existing guard-floor regressions, including
   `test_guard_empty_output_fails_closed` and
   `test_native_full_hooks_run_tool_loop_still_enforces_guard_floor`.

## Cross-Harness Disposition

- Alibaba Cloud Studio H is the current native-full consumer and is directly
  repaired by this change.
- OpenRouter F and Ollama D currently use the guard-adapter-floor path and do
  not call `invoke_native_hooks`; this change does not alter their behavior.
- `invoke_guard_adapter` and its empty-output fail-closed branch remain
  unchanged. The proposal does not generalize native allow/no-op semantics to
  the guard adapter.
- Future native-full cloud harnesses inherit the corrected shared-base behavior
  and the new regression.
- No harness registry, routing, role, eligibility, suspension, dispatcher, or
  credential surface is in scope.

## Specification Links

- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - requires harness H to use
  the Anthropic-compatible native-full hook tier through the shared runtime.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - assigns native-hook execution and the
  separate guard floor to the common cloud-harness base.
- `SPEC-INTAKE-9ec893` - requires non-GUI, maximal-hook harness integrations
  suitable for real Loyal Opposition and Prime Builder participation.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires machine-checkable harness
  capability and fail-closed governance behavior.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - preserves fail-closed behavior for the
  separate mutating-tool guard adapter; this proposal must not weaken it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent bridge review and
  role-correct proposal/report/verdict authorship.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete
  governing-carrier linkage and specification-derived tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires exact project,
  work-item, and PAUTH metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed
  spec-to-test evidence before independent verification.
- `GOV-STANDING-BACKLOG-001` - preserves WI-5198 as the canonical work item for
  this bounded defect repair.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the decision, proposal,
  tests, implementation report, and verdict to remain one traceable artifact
  graph.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the observed harness defect
  and its bounded remediation to remain durable and explicit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit proposal,
  implementation, report, and verification lifecycle states.

## Prior Deliberations

- `DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION` - owner
  authorization for this exact three-path bridge cycle, with guard-adapter,
  dispatcher, harness re-enablement, credential, deployment, and WI-5199
  exclusions.
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` - selects H
  as the non-GUI replacement harness and requires full hook capability.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` - places the
  shared cloud runtime, rather than per-harness forks, in authority for this
  behavior.
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` - establishes the
  non-GUI maximal-hook direction captured by `SPEC-INTAKE-9ec893`.
- `DELIB-20260708-GOOSE-GOV-BYPASS-INCIDENT` - records why cloud harnesses must
  retain governed hooks and a fail-closed guard floor.
- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-006.md` -
  independently verified registration/readiness work whose later real dispatch
  exposed this defect; registration smoke alone is not treated as functional
  proof.

This proposal differs from the registration slice by repairing the concrete
real-work failure found after registration. It does not re-open registration,
change identity, or claim H functional before a later real dispatched review.

## Owner Decisions / Input

- `DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION` records the
  owner's explicit `Authorize WI-5198` response and the exact scope/exclusions.
- The active PAUTH is
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5198-NATIVE-HOOK-ALLOW-20260711`.
- Restoring H to dispatch remains a separate owner decision after this thread
  reaches `VERIFIED`; this proposal grants no such authority.

## Spec-Derived Verification Plan

| Governing specification | Executed evidence required | Expected result |
| --- | --- | --- |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`, `SPEC-INTAKE-9ec893` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short` | Alibaba profile remains native-full and the real adapter's empty pre-tool result is accepted by the shared native-hook layer. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q --tb=short` | Exit-0 empty native-hook output continues without abort; timeout, nonzero, malformed JSON, and explicit block cases retain their outcomes. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Execute `test_guard_empty_output_fails_closed`, `test_native_full_hooks_tier_still_enforces_guard_floor`, and `test_native_full_hooks_run_tool_loop_still_enforces_guard_floor` within the focused base suite. | The separate guard-adapter floor remains fail-closed and unchanged. |
| Bridge/project/lifecycle carriers | Run both mandatory bridge preflights against this filed proposal and inspect the diff against the three `target_paths`. | No missing required/advisory specs, no blocking clause gaps, and no out-of-scope path. |
| Python quality floor | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py` and the matching `ruff format --check` command. | Both commands exit 0 before the implementation report is filed. |

No direct harness invocation or smoke test is permitted. After this
implementation reaches `VERIFIED`, a separately authorized dispatcher-control
decision may restore H and route a genuine review to produce the matrix proof.

## Risk / Rollback

Primary risk: accepting empty stdout could hide a native hook that was expected
to emit a decision. This proposal bounds that risk to hooks which already
returned success (exit 0); nonzero, timeout, malformed non-empty output, and
explicit deny remain fail-closed. Tests prove the guard-adapter contract is not
weakened.

Secondary risk: the shared-base change affects future native-full adopters.
The base regression and Alibaba consumer regression make that behavior explicit.

Rollback is a scoped revert of the one source branch and its two regression
files. Bridge, PAUTH, deliberation, report, and verification evidence remains
append-only. No dispatcher or harness-state rollback is part of this change.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi5198-native-hook-empty-allow`; no prior version is
deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are
the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(harness):` - repairs a real dispatched-work failure without adding a new
harness capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
