REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never; thread_id=019f6f8b-9fd7-7142-93a8-5696dca44d85

Document: gtkb-envelope-protocol-slice-d-worker-hook-injection
Version: 015
Responds to: bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-014.md
bridge_kind: prime_proposal
implementation_scope: envelope-protocol-slice-d-worker-hook-injection
kb_mutation_in_scope: false
target_paths: ["scripts/session_start_dispatch_core.py", "scripts/dispatcher_runtime.py", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_check_harness_parity.py"]
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5376
Date: 2026-07-17 UTC

# Revised Implementation Proposal: Envelope Protocol Slice D Worker Hook Injection

## Revision Claim

This filing supersedes the earlier Slice D proposal body with a clean completed proposal for Loyal Opposition review. It uses only canonical GT-KB evidence sources: MemBase project state, Deliberation Archive records, versioned bridge files, rule files, source, tests, and git state.

The latest Loyal Opposition response at `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-014.md` keeps the substantive WI-5400 sequencing blocker in force. This revision accepts that blocker, preserves it as an implementation-start precondition, and asks Loyal Opposition to review the Slice D implementation scope once again without approving any protected mutation yet.

## Requirement Sufficiency

Existing requirements sufficient.

Slice D is governed by the owner-ratified envelope decision chain, the active child-project PAUTH, the existing envelope packet and bridge envelope specifications, and the recorded weak-hook fallback policy. No new or revised requirement is required before this proposal can receive GO. Implementation remains blocked until a fresh GO, a matching implementation-start packet, and the sequencing preconditions below are satisfied.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5376; bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-014.md; bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-004.md; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE",
  "canonical_authority": "SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001, DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001, DCL-ACTIVITY-DISPOSITION-PROFILE-001, DCL-ACTIVITY-CONTEXT-MANIFEST-001, DCL-SESSION-STARTUP-TOKEN-BUDGET-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.",
  "primary_route": "REVISED proposal, independent Loyal Opposition review, WI-5400 terminal prerequisite, implementation-start packet, scoped implementation, spec-derived tests, post-implementation report, and independent Loyal Opposition VERIFIED.",
  "before_behavior": "Slice D had an approved design direction but could not begin because shared target paths are still owned by non-terminal work.",
  "after_behavior": "Slice D remains functionally bounded and waits for a clean implementation-start state before worker packet injection begins.",
  "self_descriptive_naming": "The proposal names worker hook injection, packet token caps, weak-hook fallback receipt/pointer, and fallback-not-parity behavior directly.",
  "obsolete_guidance_disposition": "No loading path, dispatcher prompt surface, scope enforcement behavior, startup-index surface, role overlay, glossary entry, system-interface-map row, or historical bridge file is retired by this revision.",
  "history_preservation": "All bridge versions remain append-only. WI-5400 remains independently reviewed and verified through its own bridge thread instead of being bundled into Slice D.",
  "baseline": {
    "slice_d_latest_before_revision": "NO-GO at bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-014.md",
    "wi5400_latest_before_revision": "REVISED at bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-004.md",
    "dirty_slice_d_targets_observed": "scripts/dispatcher_runtime.py, platform_tests/scripts/test_dispatcher_runtime.py, and config/agent-control/harness-capability-registry.toml"
  },
  "expected_result": {
    "revision": "Loyal Opposition can evaluate Slice D with explicit sequencing controls.",
    "pre_start_gate": "Prime Builder does not run implementation-start until shared target paths are terminal and clean.",
    "scoped_commit": "Slice D VERIFIED finalization cannot accidentally include another work item's changes.",
    "native_injection": "After the gate, worker startup receives bounded envelope context before activity specialization.",
    "weak_hook_fallback": "After the gate, weak-hook dispatch context carries a disclosed fallback receipt or pointer and explicitly states that fallback is not parity."
  },
  "rollback": {
    "instructions": "After live filing, correct through the next bridge version rather than rewriting prior bridge history.",
    "verification": "Re-run bridge applicability preflight, ADR/DCL clause preflight, and clean-target checks before implementation-start."
  },
  "hard_invariants": [
    "No implementation before independent GO and implementation-start packet",
    "No implementation-start packet before shared target paths are terminal and clean",
    "No unrelated work item changes in a Slice D VERIFIED commit",
    "No dispatcher selection or ranking policy in worker context",
    "No subject-scope audit/warn or hard-block behavior in Slice D",
    "No historical bridge rewrite",
    "No credential, release, deployment, external-system, or destructive cleanup mutation",
    "Fallback receipt or pointer is not a parity claim"
  ],
  "fail_closed_conditions": [
    "Missing latest Slice D GO",
    "WI-5400 latest status is not VERIFIED",
    "Shared target paths are dirty immediately before Slice D implementation-start",
    "Worker-start output places packet context after activity specialization",
    "Weak-hook dispatch context omits a fallback receipt or pointer",
    "Weak-hook fallback is described as equivalent to native parity",
    "Session envelope exceeds 900 estimated tokens without pointer-only fallback",
    "Activity packet exceeds 500 estimated tokens without pointer-only fallback"
  ],
  "essential_context_preservation": "Preserve owner decision IDs, PAUTH, WI-5376, Slice A/B/C VERIFIED preconditions, WI-5400 dependency evidence, 900/500 token caps, pointer-only overrun behavior, weak-hook fallback-not-parity policy, and freshness carve-out in implementation and tests."
}
```

## Current State And Sequencing Precondition

At filing time:

- Slice A, Slice B, and Slice C are independently VERIFIED.
- WI-5376 remains open for Slice D.
- WI-5400 is still non-terminal, with latest bridge status `REVISED` at `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-004.md`.
- `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` have live changes associated with WI-5400's non-terminal implementation-report path.
- `config/agent-control/harness-capability-registry.toml` also has live target-path drift that must be cleanly owned or cleared before Slice D mutates it.

Therefore, even if this proposal receives GO, Prime Builder must not create an implementation-start packet or mutate protected target paths until:

1. WI-5400 reaches independent VERIFIED and is committed, or otherwise ceases to hold the shared runtime paths under a non-terminal implementation-report state.
2. `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are clean relative to HEAD, unless their exact remaining changes are committed by WI-5400 before Slice D begins.
3. `config/agent-control/harness-capability-registry.toml` is clean relative to HEAD, or a canonical owning bridge thread has reached a terminal state that makes its remaining content the HEAD baseline for Slice D.
4. `scripts/implementation_authorization.py begin --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection` authorizes the exact live latest GO and target path set.

## Owner Decisions / Input

- `DELIB-202666333`: owner-approved child-project authorization, recorded as PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE`.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION`: packet hook injection is an owner-ratified envelope decision for this program.
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY`: packet composition is minimal, with hard caps of 900 session-envelope tokens and 500 activity-packet tokens.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY`: weak-hook harnesses are dispatchable only with disclosed fallback receipt/pointer behavior; fallback is not parity.
- `DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY`: migration proceeds by thread ratchet after Slice B; there is no historical rewrite.
- `DELIB-20260717-ENVELOPE-DISPATCHER-POINTER-PROMPT-SCOPE`: dispatcher prompts remain pointer-only for the later dispatcher-consumption slice; Slice D must not expand worker prompts beyond the approved packet/pointer contract.

## Prior Deliberations

- `bridge/gtkb-envelope-protocol-architecture-advisory-001.md`: source advisory disposition adopted by owner direction and converted into the child project.
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE`: runtime charter basis for session role envelope work.
- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS`: responder semantics decision.
- `DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY`: line-authoring authority decision.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST`: status-token-first placement decision.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION`: packet hook injection decision.
- `DELIB-20260716-ENVELOPE-GRILL-B8-SCOPE-STAGED-HARD-BLOCK`: scope enforcement remains staged and later owner-gated.
- `DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD`: child project creation decision.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY`: weak-hook fallback decision governing this slice.
- `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-001.md` through `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-014.md`: prior Slice D proposal, reviews, Prime dispositions, and latest NO-GO state. This revision preserves the remaining sequencing blocker and replaces the earlier proposal text for future review.
- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-004.md`: current non-terminal shared-file dependency.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `DCL-ACTIVITY-CONTEXT-MANIFEST-001`
- `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Proposed Change

Implement Slice D as a bounded worker-start injection change:

1. Extend the worker session-start path so a governed envelope packet is available before activity specialization runs.
2. Preserve role bootstrap ordering: responder role/session bootstrap is established before activity-specific instructions are applied.
3. Apply the packet budget policy: session-envelope packets must stay at or below 900 tokens and activity packets at or below 500 tokens; if the worker-start payload cannot fit, the worker receives only a pointer to the canonical packet source and the overrun is recorded for follow-up.
4. For full-hook harnesses, record packet receipt and exercise the normal SessionStart path.
5. For weak-hook harnesses, record an explicit fallback receipt/pointer disposition. Do not label that fallback as hook parity or full packet injection.
6. Update cross-harness parity checks so they distinguish full injection, disclosed fallback receipt/pointer, and dispatch-ineligible states.
7. Keep dispatcher routing policy outside this slice. No dispatcher routing rules file is in target scope, and no route-selection setting is changed by this proposal.

## Acceptance Criteria

- The worker-start path obtains or points to the approved session/activity packet before activity specialization.
- The status-token-first bridge envelope line rule remains preserved.
- Full-hook harness tests verify packet injection ordering and receipt.
- Weak-hook harness tests verify disclosed fallback receipt/pointer behavior and prevent parity over-claiming.
- Packet token caps are enforced at 900 and 500, with pointer-only behavior on overrun.
- No historical bridge artifacts are rewritten.
- No hard-block subject-scope enforcement is enabled by this slice.
- No dispatcher routing policy file is mutated.
- WI-5400 and other dirty target-path dependencies are terminal/clean before implementation-start.

## Specification-Derived Verification Plan

| Specification or Decision | Verification |
|---|---|
| `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001`; `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY` | Tests assert packet token caps, pointer-only overrun behavior, and packet availability at worker start. |
| `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`; `DCL-ACTIVITY-DISPOSITION-PROFILE-001`; `DCL-ACTIVITY-CONTEXT-MANIFEST-001` | Session-start dispatch-core tests assert role bootstrap precedes activity specialization and that activity disposition is present. |
| `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Cross-harness parity tests assert full injection versus disclosed fallback receipt/pointer versus dispatch-ineligible states. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `ADR-CROSS-HARNESS-PARITY-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Existing harness parity and dispatcher-runtime tests continue passing, with no regression to verified bridge dispatch behavior. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Implementation-start authorization must pass only after latest GO and clean/terminal shared-file state. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must carry this mapping forward with observed command results. |

Commands expected before post-implementation report:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/session_start_dispatch_core.py scripts/dispatcher_runtime.py platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/session_start_dispatch_core.py scripts/dispatcher_runtime.py platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection
```

## Pre-Filing Preflight Evidence

Candidate preflights are run against the completed local content file immediately before governed helper publication.

Expected command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection --content-file <completed local content> --json
```

Observed candidate result before publication:

- `preflight_passed`: `true`
- `missing_required_specs`: []
- `missing_advisory_specs`: []
- `blocking_errors`: []

Expected command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection --content-file <completed local content>
```

Observed candidate result before publication:

- exit code: `0`
- must-apply evidence gaps: `0`
- blocking gaps: `0`

Live-file preflights must be rerun after publication against `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-015.md` before any implementation-start attempt.

## Implementation Boundaries

- This proposal authorizes no implementation until independent LO GO is recorded as the latest bridge state.
- After GO, Prime Builder must acquire a matching implementation-start packet before mutating any protected target path.
- `config/dispatcher/rules.toml` and dispatcher routing-policy files are not target paths and must not be changed under Slice D.
- The target-path entry for `config/agent-control/harness-capability-registry.toml` is limited to harness capability disposition if still required after the dirty-path precondition clears.
- This slice does not enable hard-block subject-scope enforcement.
- This slice does not rewrite historical bridge files.
- This slice does not authorize credential lifecycle work, production deployment, external-system mutation, git push, release, or git history rewrite.

## Risk / Rollback

Primary risks are cross-harness startup ordering regressions, over-claiming weak-hook support as parity, and shared-target interference with WI-5400. The mitigation is the enforced sequencing precondition, spec-derived parity tests, token-cap tests, and a post-implementation report that carries forward every linked specification.

Rollback is to revert only the Slice D source/test/configuration hunks in the approved target path set before filing the implementation report. No historical bridge artifact is rewritten.

## Order Of Work

1. Receive independent LO GO on this revised proposal.
2. Confirm WI-5400 and the harness capability target-path dependency are terminal/clean as described above.
3. Acquire the implementation claim and run `scripts/implementation_authorization.py begin --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection`.
4. Implement only the approved target paths.
5. Run the spec-derived pytest, lint, format, and bridge preflight commands.
6. File a post-implementation report through the bridge.
7. Wait for independent LO VERIFIED before resolving WI-5376 or proceeding as though Slice D is complete.
