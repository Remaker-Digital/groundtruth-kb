NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-17T10-20-39Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never; session_id=A-2026-07-17T10-20-39Z


Document: gtkb-envelope-protocol-slice-d-worker-hook-injection
Version: 001
Author: Prime Builder / Codex
Date: 2026-07-17
bridge_kind: prime_proposal
implementation_scope: envelope-protocol-slice-d-worker-hook-injection
kb_mutation_in_scope: false
target_paths: ["scripts/session_start_dispatch_core.py", "scripts/dispatcher_runtime.py", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_check_harness_parity.py"]
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5376

# Implementation Proposal: Envelope Protocol Slice D Worker Hook Injection

## Summary

Implement Slice D of the envelope protocol modernization program. The native SessionStart hook path will fetch the deterministic Slice C session-envelope packet and inject it before role-specific startup specialization. Where an activity is available to a worker dispatch, the worker context will also receive a bounded activity-packet pointer or packet before activity specialization. Weak-hook harnesses remain dispatchable only with a disclosed fallback receipt or packet pointer, and that fallback is explicitly not treated as parity with native hook injection.

This proposal does not authorize dispatcher selection/ranking changes, retirement of init-keyword prompt composition, subject-scope enforcement, hard-block rollout, startup-index cleanup, role-overlay cleanup, historical bridge rewriting, credential changes, release work, deployment, or destructive cleanup. Those remain later slices.

## Requirement Sufficiency

Existing requirements sufficient. Slice A inserted the canonical envelope-protocol authority set, Slices B and C are independently VERIFIED, WI-5376 defines this slice, and the owner-ratified B5/B6 records plus the 2026-07-17 weak-hook fallback decision define the worker hook injection and fallback-disclosure requirements. No new or revised requirement is needed before implementation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5376; bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md; bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md; bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-006.md; DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION; DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE; DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE",
  "canonical_authority": "SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001, DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001, DCL-ACTIVITY-DISPOSITION-PROFILE-001, DCL-ACTIVITY-CONTEXT-MANIFEST-001, DCL-SESSION-STARTUP-TOKEN-BUDGET-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.",
  "primary_route": "Bridge GO, implementation-start packet, scoped worker hook injection and fallback-disposition implementation, spec-derived tests, post-implementation report, and independent Loyal Opposition VERIFIED.",
  "before_behavior": "The packet service and CLI exist, and SessionStart hooks already centralize through scripts/session_start_dispatch_core.py, but worker startup does not fetch and inject the Slice C packet. Weak-hook harnesses have envelope projection/fallback notes but no explicit packet fallback receipt or pointer in the worker context.",
  "after_behavior": "Native Claude/Codex SessionStart startup context includes a bounded session-envelope packet before role-specific startup text. Dispatch contexts for weak-hook harnesses disclose a fallback receipt or pointer instead of claiming native parity.",
  "self_descriptive_naming": "Functions, registry entries, tests, and emitted context use envelope packet, session-envelope, activity-packet, native injection, fallback receipt, and pointer names tied directly to Slice D.",
  "obsolete_guidance_disposition": "No loading paths or historical bridge files are retired in Slice D. Later Slice E owns dispatcher prompt simplification, Slice F owns scope enforcement, and Slice G owns cleanup and documentation retirement.",
  "history_preservation": "Slice A, B, and C bridge histories, Deliberation Archive records, MemBase records, and existing runtime packet caches remain append-only. Fallback receipts are runtime evidence and not canonical authority.",
  "baseline": {
    "slice_a": "bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md VERIFIED",
    "slice_b": "bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md VERIFIED",
    "slice_c": "bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-006.md VERIFIED",
    "work_item": "WI-5376 open/backlogged before this proposal",
    "native_hook_surface": "scripts/session_start_dispatch_core.py emits startup context but does not include the packet service output",
    "weak_hook_surface": "Weak-hook harnesses rely on prompt or adapter fallback without a packet fallback receipt/pointer"
  },
  "expected_result": {
    "native_injection": "SessionStart context includes a bounded session-envelope packet before role-specific startup specialization",
    "activity_packet": "Dispatch/activity context includes an activity packet or pointer where the selected bridge artifact carries ::open activity metadata",
    "weak_hook_fallback": "Weak-hook dispatch context carries a disclosed fallback receipt or pointer and explicitly states that fallback is not parity",
    "packet_caps": "Session-envelope remains capped at 900 estimated tokens and activity-packet remains capped at 500 estimated tokens",
    "ttl_seconds": 300,
    "freshness": "Live state claims remain fresh-read only"
  },
  "rollback": {
    "instructions": "Before VERIFIED, revert only the scoped SessionStart injection, dispatcher fallback receipt/pointer, registry, and test edits and file a revised bridge report. After VERIFIED, correct through a governed follow-on bridge thread instead of rewriting bridge history.",
    "verification": "Rerun focused SessionStart, dispatcher prompt, packet, harness-parity, ruff, bridge applicability, and ADR/DCL clause preflights after rollback or correction."
  },
  "hard_invariants": [
    "No implementation before independent GO and implementation-start packet",
    "No dispatcher selection/ranking policy in worker context",
    "No subject-scope audit/warn or hard-block behavior in Slice D",
    "No historical bridge rewrite",
    "No credential, release, deployment, external-system, or destructive cleanup mutation",
    "Fallback receipt or pointer is not a parity claim",
    "Packet cache cannot authorize current-state claims",
    "Over-budget packet output must remain pointer-only",
    "Role bootstrap remains before activity specialization"
  ],
  "fail_closed_conditions": [
    "Missing latest GO or implementation-start packet",
    "Native SessionStart output places packet context after role-specific startup text",
    "Weak-hook dispatch context omits a fallback receipt or pointer",
    "Weak-hook fallback is described as equivalent to native parity",
    "Session packet exceeds 900 estimated tokens without pointer-only fallback",
    "Activity packet exceeds 500 estimated tokens without pointer-only fallback",
    "Packet embeds forbidden dispatcher ranking policy, model-selection policy, credentials, or unrelated live queue summaries",
    "Tests weaken the source-of-truth freshness carve-out"
  ],
  "essential_context_preservation": "Preserve owner AUQ decision IDs, PAUTH, WI-5376, Slice A/B/C VERIFIED preconditions, 900/500 token caps, 300 second default TTL, pointer-only overrun behavior, weak-hook fallback-not-parity policy, and freshness carve-out in implementation and tests."
}
```

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE` authorizes the modernization child project scope but does not bypass bridge GO or implementation-start.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION` establishes that envelope packets are hook-fetched and injected at worker session start, with role bootstrap before activity specialization and manual packet CLI availability.
- `DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE` establishes TTL-stable frame fetch/cache behavior while preserving live state freshness obligations.
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY` selects minimal packet composition with hard caps of 900 session-envelope tokens and 500 activity-packet tokens.
- `DELIB-20260717-ENVELOPE-PACKET-CLI-SURFACE-CACHE` selects the CLI surface `gt session envelope packet` and cache path `.gtkb-state/session-envelope/packet-cache/`.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY` keeps weak-hook harnesses dispatchable only when the worker receives a clear fallback receipt or pointer, and forbids treating fallback as parity.
- `DELIB-20260717-ENVELOPE-DISPATCHER-POINTER-PROMPT-SCOPE` constrains later dispatcher prompt work to pointer-only scope; Slice D uses only the existing dispatch context needed for weak-hook fallback receipt/pointer disclosure.
- `DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY` preserves thread ratchet after Slice B and forbids historical rewrite.

## Prior Deliberations

- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - worker role comes from the explicit session envelope carried by the dispatched bridge item; dispatcher policy remains excluded from worker context.
- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS` - responder-role semantics for envelope lines.
- `DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY` - governed writers own line authoring and validation.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` - Body Status-Token Rule preservation.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION` - hook-fetched worker packet injection authority.
- `DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE` - TTL-stable fetch/cache authority for packets.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY` - weak-hook fallback receipt/pointer requirement and no-parity constraint.
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY` - minimal packet composition and 900/500 token hard caps.
- `DELIB-20260717-ENVELOPE-PACKET-CLI-SURFACE-CACHE` - public CLI and cache path decision.
- `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md` - Slice A canonical authority insertion VERIFIED.
- `bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md` - Slice B bridge writer envelope-head implementation VERIFIED.
- `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-006.md` - Slice C packet CLI/cache implementation VERIFIED.

## Cross-Harness Disposition

- Claude Code: native SessionStart hook path delegates to `scripts/session_start_dispatch_core.py`; Slice D injects packet context through that shared path.
- Codex: native SessionStart hook path delegates to the same shared core; Slice D keeps parity by implementing shared-core behavior rather than wrapper-specific behavior.
- Cursor: fallback-capable but not a native parity claim. Dispatch remains allowed only when the worker prompt or startup fallback carries a clear packet fallback receipt or pointer.
- Antigravity: fallback-capable through existing stdin/sidecar dispatch context, not native parity. Dispatch remains allowed only with a clear packet fallback receipt or pointer.
- Ollama and OpenRouter: provider harnesses use compact-provider dispatch/result envelopes. Dispatch remains allowed only when the worker receives a packet pointer or fallback receipt in the dispatch context; this is not native hook parity.
- Alibaba Cloud Studio and other provider harnesses: this slice may record the same compact-provider fallback semantics when already covered by the registry, but it does not claim native hook parity.
- No owner-approved typed waiver is introduced by this proposal. The owner decision is a disclosed fallback policy, not a parity waiver.

## Specification Links

- `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001` - packet shape, budget caps, TTL metadata, cache behavior, pointer-only diagnostics, and forbidden content.
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` - hook-primary activity/envelope interception and agent fallback when hook events are unavailable.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - closed activity vocabulary and activity profile behavior used for activity packet selection.
- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - role bootstrap before activity overlay, context manifest inputs, live-query routing, and essential-context preservation.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - startup packet injection must preserve startup token budget constraints.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - TTL-stable packet cache cannot authorize current-state claims.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - SessionStart hooks and fallback prompts should call deterministic packet services rather than rely on hand-authored prose.
- `ADR-CROSS-HARNESS-PARITY-001` - native, adapter, provider, and fallback semantics must be explicit and behaviorally comparable without false parity claims.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface proposals must include cross-harness disposition and parity/fallback evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - modernization slices must carry non-impairment evidence and preserve existing governed workflows.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, work items, bridge proposals, implementation reports, and verification evidence remain durable artifact records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the slice preserves traceability across decisions, artifacts, work items, tests, reports, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle states remain explicit: proposal, GO, implementation report, VERIFIED, work-item resolution, and later program closure.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires active project authorization plus bridge GO and implementation-start packet.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH evidence is additive and bounded.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time enforcement must validate live scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal includes PAUTH, project, and work-item metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - WI-5376 belongs to the approved modernization project.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links relevant governing specifications and maps tests from them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must execute tests derived from linked specs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status authorship and review independence remain role-bound.
- `.claude/rules/file-bridge-protocol.md` - bridge proposal, GO, implementation report, and VERIFIED lifecycle.
- `.claude/rules/codex-review-gate.md` - no implementation without LO GO and implementation-start.

## Proposed Change

1. Add a fail-soft packet injection layer to `scripts/session_start_dispatch_core.py` that composes the Slice C session-envelope packet through `groundtruth_kb.session.packet.compose_packet`.
2. Inject the packet block into SessionStart `additionalContext` before role-specific startup disclosure or activity specialization.
3. Preserve startup-service validation and degraded-banner fallback behavior; packet composition failure must produce a clear packet-injection diagnostic without aborting SessionStart.
4. Add weak-hook fallback receipt/pointer text to the existing dispatch context for harnesses without native packet hook injection, limited to selected bridge documents and packet CLI/cache pointers.
5. Update the harness capability registry so native injection, fallback receipt/pointer operation, compact-provider operation, and unsupported/not-parity states are explicit.
6. Keep dispatcher routing, model selection, target selection, and prompt minimization out of scope. Slice E owns dispatcher selection and pointer-prompt simplification.
7. Keep subject-scope audit/warn and hard-block behavior out of scope. Slice F owns scope enforcement.

## Acceptance Criteria

- Native SessionStart output for Claude/Codex contains a session-envelope packet block before role-specific startup disclosure content.
- Packet injection uses the Slice C packet service and preserves the 900 session-envelope and 500 activity-packet caps.
- Over-budget packet output remains pointer-only and does not emit oversized payload content.
- Packet composition failures fail soft with an explicit diagnostic and do not abort SessionStart.
- Weak-hook dispatch context contains a clear fallback receipt or packet pointer before worker action instructions.
- Weak-hook fallback text explicitly states that fallback operation is not native hook parity.
- Dispatcher selection, model routing, credential state, scope hard-blocking, and live queue summaries are not added to packet payloads.
- Harness parity registry and tests distinguish native packet injection from fallback receipt/pointer operation.
- No implementation occurs before LO `GO` and an implementation-start packet.

## Specification-Derived Verification Plan

Spec-to-test mapping for the post-implementation report:

- `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001` -> packet and SessionStart tests assert JSON shape, metadata, hard caps, pointer-only diagnostic overrun, TTL/cache metadata, and forbidden content exclusion.
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` -> SessionStart and dispatcher tests assert hook-primary injection plus explicit fallback when hook events are unavailable.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` and `DCL-ACTIVITY-CONTEXT-MANIFEST-001` -> dispatcher/activity tests assert selected activity packet or pointer is derived from `::open` activity metadata and role bootstrap ordering is preserved.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` -> tests assert injection remains bounded and overrun becomes pointer-only.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` -> packet injection tests assert live state remains represented as live-query descriptors, not stale embedded state.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` -> harness parity tests assert native/fallback/provider dispositions and no false parity claim.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` -> proposal/report evidence and focused tests show Slice D avoids dispatcher routing, scope enforcement, cleanup, credential, release, and historical rewrite behavior.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` plus PAUTH/DCL project-linkage specs -> implementation-start packet must be created after GO and before protected mutations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -> post-implementation report carries this mapping and exact observed command results.

Planned commands after implementation:

```powershell
python -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py -q --tb=short
python -m ruff check scripts/session_start_dispatch_core.py scripts/dispatcher_runtime.py platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py
python -m ruff format --check scripts/session_start_dispatch_core.py scripts/dispatcher_runtime.py platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection
python scripts/check_harness_parity.py --harness all --all --validate-schema
```

## Pre-Filing Preflight Evidence

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection --content-file .gtkb-state\bridge-propose-drafts\gtkb-envelope-protocol-slice-d-worker-hook-injection-001.md --json` exited 0 with `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`, and packet hash `sha256:f6dcfff08ba2b48ba77b0912bb087ca48d85cebfe7219fa95bb8957575dd5bb0` before this evidence-line insertion.
- ADR/DCL clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection --content-file .gtkb-state\bridge-propose-drafts\gtkb-envelope-protocol-slice-d-worker-hook-injection-001.md` exited 0 with 5 clauses evaluated, 3 `must_apply`, 0 evidence gaps in `must_apply` clauses, and 0 blocking gaps.
- Bridge-compliance audit: a standalone Codex helper audit over this completed draft returned `decision: pass`; the live helper write repeats the same audit before publishing `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-001.md`.

## Implementation Boundaries

- No dispatcher selection, ranking, model-choice, or target-eligibility logic change in Slice D.
- No retirement of dispatcher init-keyword prompt composition in Slice D.
- No subject-scope map, audit/warn, hard-block, or owner-gated hard-block flip in Slice D.
- No session-startup-index, role-overlay, canonical-terminology glossary, system-interface-map, or retired-surface cleanup in Slice D except if implementation tests reveal an unavoidable direct dependency; those are planned for later slices.
- No historical bridge rewrite or migration of old thread content.
- No credential, release, production deployment, external-system mutation, Git push, or destructive cleanup.

## Risk / Rollback

Primary risk is accidental startup breakage. The mitigation is fail-soft packet composition, preservation of the existing startup-service degraded-banner path, and wrapper tests for Claude and Codex.

Secondary risk is false parity: weak-hook fallback could be mistaken for native hook injection. The mitigation is explicit registry disposition, worker-visible fallback receipt/pointer text, and parity tests asserting fallback remains degraded/not-parity.

Rollback before VERIFIED is scoped to reverting the shared SessionStart injection, dispatcher fallback receipt/pointer, registry, and tests, then filing a revised bridge report. After VERIFIED, corrections must use a follow-on bridge thread.

## Order Of Work

1. Wait for independent LO `GO` on this Slice D proposal.
2. Create the implementation-start authorization packet for `gtkb-envelope-protocol-slice-d-worker-hook-injection`.
3. Implement only the declared SessionStart injection, weak-hook fallback receipt/pointer, registry disposition, and focused tests.
4. Run the specification-derived tests, ruff lint, ruff format check, harness parity validation, and bridge preflights.
5. File a post-implementation report through the bridge with exact command evidence and spec-to-test mapping.
6. Wait for independent LO `VERIFIED` before resolving WI-5376 or starting Slice E implementation.
