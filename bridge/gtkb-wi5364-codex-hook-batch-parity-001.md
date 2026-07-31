NEW

# Implementation Proposal - Restore live Codex hook parity without duplicate execution

bridge_kind: prime_proposal
Document: gtkb-wi5364-codex-hook-batch-parity
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5364

target_paths: [".codex/config.toml", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity.py"]

implementation_scope: configuration,source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Enable the live Codex hook surface required by the current Windows-capable
runtime, remove the wrap-up dispatcher's obsolete explicit role-profile
override, and make the parity checker/tests recognize the committed
`run_py_no_window --batch` topology.

The current hook configuration already executes formal-artifact approval,
workstream focus, bridge compliance, and explicit wrap-up handlers exactly once
through declarative batches. Directly registering those handlers again would
double-run governance and lifecycle behavior. This repair therefore leaves the
hook registration document and batch runner unchanged, reuses the established
batch-expansion parser in `parity_discovery_diff`, and fails closed when a batch
is missing, malformed, or omits a required surface.

The Codex project config contains an unrelated pre-start `sandbox_mode` hunk.
Implementation, review, reporting, and any later finalization must preserve that
hunk byte-for-byte and own only the WI-5364 comment/feature-flag patch.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 - Codex hooks are live on Windows for the supported runtime and must use fallback only if empirical availability regresses.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - active Codex hook behavior must cover active governance gates, including bridge compliance and formal-artifact approval.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity discovery reads actual configured surfaces, including declarative batch fan-out, rather than requiring duplicate registrations.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - session role is resolved from current session authority and must not be forced by a harness-local wrap-up adapter.
- `DCL-SESSION-ROLE-RESOLUTION-001` - wrap-up generation must discover the current session role through canonical resolution.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - hook activation must preserve no-window containment, single execution, role correctness, and fail-closed governance.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - the RC Python lane cannot pass while its mandatory Codex parity checker fails.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - the foreign pre-start config hunk remains independently owned and excluded from WI-5364 finalization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the detected parity defect, proposal, implementation evidence, and independent verdict remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5364 remains open until implementation and independent verification complete.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the RC blocker is preserved as an origin=hygiene work item.
- `GOV-STANDING-BACKLOG-001` - WI-5364 is the durable owner of this bounded parity repair.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - all four protected targets require independent GO, matching claim/start authority, reporting, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the exact configuration, adapter, checker, and test paths are linked to their governing carriers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification executes batch, parity, role, no-window, and release-gate regressions.

## Prior Deliberations

- `DELIB-0836` - established the original Codex hook fallback stance later superseded in part by the live-Windows-hook v2/v3 ADR.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - approved mechanical Codex governance parity.
- `DELIB-202666274` - authorizes the modernization program at project scope while retaining independent GO, claim/start, VERIFIED, and exact Git boundaries.

## Owner Decisions / Input

No new owner decision is required. The active Assurance PAUTH covers this
configuration/source/test repair. This proposal does not authorize
dispatcher/TAFE mutation, harness eligibility or role mutation, direct harness
contact, manual routing, database mutation, Git staging/commit/push,
deployment, release, credentials, or cleanup.

## Requirement Sufficiency

Existing requirements are sufficient. ADR v3 explicitly says supported Codex
Windows hooks are live, while the parity and role carriers require complete
governance coverage and dynamic role resolution. The defect is stale checker
and config projection after the committed no-window batch architecture, not a
missing requirement.

## Proposed Scope

1. Replace the obsolete disabled-hooks comment with the current live-Windows/no-window-batch stance and set the project feature flag to true.
2. Preserve the unrelated current `sandbox_mode` line and every other config byte outside the WI-5364 hunk.
3. Remove the wrap-up adapter's helper and command extension that pass `--role-profile`; retain canonical envelope/session role latching and let session initialization discover role authority.
4. Import and reuse the existing public batch-aware surface enumerator in the Codex parity checker.
5. Evaluate required surfaces per event group and matcher after declarative batch expansion, while continuing to accept valid direct no-space wrappers.
6. Treat unreadable/malformed/missing batch definitions or omitted required surfaces as parity errors.
7. Validate the outer batch hook as a command, no-window runner invocation without command substitution; keep child timeout enforcement owned by the existing runner/runtime-containment checks rather than applying a direct-hook timeout limit to an aggregate batch.
8. Update repository assertions to inspect expanded event-group surfaces instead of searching only literal command fragments in the hook registration document.
9. Add focused fixtures proving a valid batch route passes, a missing batch surface fails, and direct-wrapper compatibility remains accepted.
10. Leave the Codex hook registration document, batch runner, wrappers, Claude/Cursor/Antigravity configuration, dispatcher/TAFE state, and harness registry unchanged.

## Cross-Harness Disposition

No typed waiver is requested.

- Codex: this slice activates the already registered no-window batch topology and corrects its parity evaluator plus dynamic wrap-up role behavior. Each handler continues to execute once.
- Claude: no hook or settings change. Existing direct registrations remain the reference behavior compared by the parity checker.
- Cursor: no hook mutation. Shared workstream, role, and governance semantics must remain green in cross-harness tests.
- Antigravity: no hook mutation; ADR v3 classifies its lack of native hook events as an architectural surface difference with interval-driven dispatch, not a target for Codex registration cloning.
- Ollama, OpenRouter, and Alibaba: no interactive hook configuration or routing change. Their deterministic TAFE roles and dispatchability are unaffected.

Parity acceptance requires the checker to recognize semantically equivalent
direct and declarative-batch routes, fail on an omitted required surface, and
never infer that duplicate registration is needed for parity.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5364 authoritative-worktree diagnosis under DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_codex_hook_parity.py",
  "before_behavior": "The project disables a supported live hook surface, the checker reports eight false or real gaps because it ignores committed batch fan-out, and wrap-up explicitly passes a role profile.",
  "after_behavior": "Hooks are enabled through the existing no-window batches, parity resolves each batch to its actual handler surfaces exactly once, and wrap-up discovers session role canonically.",
  "self_descriptive_naming": "Event-group surface expansion distinguishes configured outer batch commands from their actual handler surfaces and keeps direct-wrapper compatibility explicit.",
  "obsolete_guidance_disposition": "The stale disabled-hooks comment and explicit role-profile override are removed; the v3 fallback remains applicable only when empirical hook availability regresses.",
  "history_preservation": "The committed batch runner and hook registration history remain unchanged; the foreign current sandbox configuration hunk remains independently owned.",
  "baseline": {
    "focused_parity_passed": 9,
    "focused_parity_failed": 5,
    "checker_findings": 8,
    "no_window_batch_tests_passed": 11,
    "hooks_enabled": false
  },
  "expected_result": {
    "focused_parity_passed": 14,
    "focused_parity_failed": 0,
    "checker_findings": 0,
    "no_window_batch_tests_passed_minimum": 11,
    "hooks_enabled": true,
    "duplicate_handler_registrations_added": 0
  },
  "rollback": "Revert only the WI-5364 feature-flag/comment, wrap-up role-override, checker, and test hunks through a separately governed transaction; preserve foreign config bytes and all existing batch registrations.",
  "hard_invariants": [
    "no governance or lifecycle handler executes twice because of this repair",
    "all hook subprocesses remain under the existing no-window runner",
    "missing or malformed batch evidence fails parity closed",
    "interactive session role is not forced by the wrap-up adapter",
    "no harness is disabled, deprioritized, rerouted, or made ineligible",
    "no dispatcher, TAFE, registry, or hook registration document is mutated"
  ],
  "fail_closed_conditions": [
    "hooks remain disabled on the supported runtime",
    "a required batch surface cannot be parsed or is absent",
    "a hook command bypasses the no-window runner",
    "the role-profile override remains",
    "focused parity, runtime containment, or cross-harness regression tests fail"
  ],
  "essential_context_preservation": "Live hook availability, exact batch fan-out, single-execution behavior, no-window containment, canonical role resolution, and fallback conditions remain visible in code and tests."
}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Live Codex hook activation | Parse the project config and run the parity checker | The supported hook feature is true and the checker reports PASS. |
| Batch-aware parity | Execute valid/missing/malformed batch fixtures in the focused parity tests | Valid event/matcher batch routes pass; missing or unreadable required surfaces fail deterministically. |
| No duplicate registration | Compare the hook registration document before/after and enumerate expanded surfaces | Registration bytes are unchanged and each required handler is reached exactly once per applicable event group. |
| Governance coverage | Check formal approval, bridge pre/post compliance, workstream Bash/apply_patch/UserPromptSubmit, and lifecycle SessionStart/UserPromptSubmit surfaces | Every required surface is present after expansion with the correct event/matcher. |
| Dynamic role authority | Run wrap-up dispatcher and session-role cache tests; inspect command construction | No `--role-profile` argument is passed; canonical current role resolution remains green. |
| No-window containment | Run the existing no-window runtime-containment suite and batch-expansion unit test | Existing 11-test baseline remains green and no visible-console route is introduced. |
| Focused parity | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short` | All focused tests pass, including batch and direct compatibility fixtures. |
| Cross-harness/regression | Run workstream-focus, hook-registration, governance-adoption, session-wrapup, and parity-discovery focused modules | No Claude/Cursor/shared-role behavior regresses and no new waiver is needed. |
| Hunk isolation | Compare pre-start hashes, `git diff --check`, and the WI-5364 patch | Only the four approved target hunks change; the foreign config hunk and all concurrent bytes remain intact. |

## Acceptance Criteria

1. Codex hooks are enabled for the supported live Windows runtime.
2. The parity checker returns PASS against the repository configuration.
3. All focused parity tests pass and include batch omission/failure fixtures.
4. Required governance/lifecycle surfaces are recognized through exactly one direct or batch route per event/matcher.
5. The existing hook registration document and batch runner remain unchanged.
6. The wrap-up adapter no longer passes or contains `--role-profile` and role tests remain green.
7. No-window containment and cross-harness regressions remain green.
8. The unrelated config hunk and all concurrent work remain byte-identical outside WI-5364.
9. Independent Loyal Opposition review returns VERIFIED before completion is claimed.

## Risk / Rollback

The highest risk is double-running blocking or mutating handlers by adding
literal registrations on top of batch fan-out. This proposal prohibits that
approach and tests the expanded topology. A second risk is making a batch parser
silently permissive; malformed or missing batch evidence must produce the same
missing-surface failure as an absent direct hook.

Rollback reverts only the four WI-5364 hunks through a separately governed
transaction. It does not rewrite hook registrations, batch definitions,
foreign config bytes, database state, harness state, or bridge history.

## Bridge Filing

File this as the next append-only numbered proposal for
`gtkb-wi5364-codex-hook-batch-parity`. Deterministic TAFE/bridge routing is
external to this session; no manual routing or direct harness contact occurs.

## Recommended Commit Type

`fix` - restores active hook parity and corrects false-negative validation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
