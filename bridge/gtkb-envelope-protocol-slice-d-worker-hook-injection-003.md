REVISED
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-17T10-20-39Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never; session_id=A-2026-07-17T10-20-39Z


Document: gtkb-envelope-protocol-slice-d-worker-hook-injection
Version: 003
Responds to: bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-002.md
bridge_kind: prime_proposal
implementation_scope: envelope-protocol-slice-d-worker-hook-injection
kb_mutation_in_scope: false
target_paths: ["scripts/session_start_dispatch_core.py", "scripts/dispatcher_runtime.py", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_check_harness_parity.py"]
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5376

# Revised Implementation Proposal: Envelope Protocol Slice D Worker Hook Injection

## Revision Claim

This revision addresses the single P1 NO-GO in `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-002.md`. The implementation scope remains Slice D worker hook injection, but the proposal now explicitly discloses the current collision with `gtkb-wi5400-cloud-verdict-claim-lifecycle` and makes WI-5400 independent VERIFIED/commit finalization plus a clean shared-file baseline a hard precondition before any Slice D implementation-start packet or source edit.

No implementation is requested or authorized by this revised filing. Prime Builder will still wait for independent LO `GO`, and will then perform the additional sequencing check below before creating the implementation-start packet.

## Requirement Sufficiency

Existing requirements remain sufficient. Slice A inserted the canonical envelope-protocol authority set, Slices B and C are independently VERIFIED, WI-5376 defines this slice, and the owner-ratified B5/B6 records plus the 2026-07-17 weak-hook fallback decision define the worker hook injection and fallback-disclosure requirements. This revision adds only a sequencing constraint needed to preserve scoped commits and non-impairment while the unrelated WI-5400 thread is not yet independently VERIFIED.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5376; bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-002.md; bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-001.md; bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-002.md; bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE",
  "canonical_authority": "SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001, DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001, DCL-ACTIVITY-DISPOSITION-PROFILE-001, DCL-ACTIVITY-CONTEXT-MANIFEST-001, DCL-SESSION-STARTUP-TOKEN-BUDGET-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.",
  "primary_route": "REVISED proposal, independent LO review, WI-5400 VERIFIED/committed precondition, Slice D implementation-start packet, scoped implementation, spec-derived tests, post-implementation report, and independent LO VERIFIED.",
  "before_behavior": "Slice D proposal version 001 correctly scoped worker hook injection but did not disclose that two target paths were already dirty with unrelated WI-5400 verdict-claim lifecycle work.",
  "after_behavior": "Slice D remains functionally unchanged but cannot begin implementation until WI-5400 is independently VERIFIED/committed and the two shared target files are clean relative to HEAD.",
  "self_descriptive_naming": "The revision names the shared-file collision, WI-5400 precondition, session-envelope packet, activity-packet, weak-hook fallback receipt, and not-parity semantics directly.",
  "obsolete_guidance_disposition": "No loading paths, dispatcher prompt surfaces, scope enforcement paths, startup-index surfaces, role overlays, glossary entries, system-interface-map rows, or historical bridge files are retired by this revision.",
  "history_preservation": "All bridge versions remain append-only. WI-5400 remains independently reviewed and verified through its own bridge thread instead of being bundled into Slice D.",
  "baseline": {
    "slice_d_latest_before_revision": "NO-GO at bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-002.md",
    "wi5400_latest_before_revision": "NEW at bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md",
    "shared_file_diff": "2 files changed, 400 insertions(+), 2 deletions(-) across scripts/dispatcher_runtime.py and platform_tests/scripts/test_dispatcher_runtime.py"
  },
  "expected_result": {
    "revision": "LO can evaluate Slice D with explicit collision disclosure and sequencing controls.",
    "pre_start_gate": "Prime does not run implementation-start until WI-5400 is VERIFIED/committed and shared files are clean.",
    "scoped_commit": "Slice D VERIFIED finalization cannot accidentally commit WI-5400 work.",
    "native_injection": "After the gate, SessionStart context includes a bounded session-envelope packet before role-specific startup specialization.",
    "weak_hook_fallback": "After the gate, weak-hook dispatch context carries a disclosed fallback receipt or pointer and explicitly states that fallback is not parity."
  },
  "rollback": {
    "instructions": "Before live filing, discard only this draft. After live filing, correct through the next bridge version rather than rewriting prior bridge history.",
    "verification": "Re-run bridge applicability preflight, ADR/DCL clause preflight, and the shared-file baseline checks before implementation-start."
  },
  "hard_invariants": [
    "No implementation before independent GO and implementation-start packet",
    "No implementation-start packet before WI-5400 is VERIFIED/committed and shared files are clean",
    "No unrelated WI-5400 code in a Slice D VERIFIED commit",
    "No dispatcher selection/ranking policy in worker context",
    "No subject-scope audit/warn or hard-block behavior in Slice D",
    "No historical bridge rewrite",
    "No credential, release, deployment, external-system, or destructive cleanup mutation",
    "Fallback receipt or pointer is not a parity claim",
    "Packet cache cannot authorize current-state claims"
  ],
  "fail_closed_conditions": [
    "Missing latest Slice D GO",
    "WI-5400 latest status is not VERIFIED",
    "Shared files are dirty immediately before Slice D implementation-start",
    "Native SessionStart output places packet context after role-specific startup text",
    "Weak-hook dispatch context omits a fallback receipt or pointer",
    "Weak-hook fallback is described as equivalent to native parity",
    "Session packet exceeds 900 estimated tokens without pointer-only fallback",
    "Activity packet exceeds 500 estimated tokens without pointer-only fallback"
  ],
  "essential_context_preservation": "Preserve owner AUQ decision IDs, PAUTH, WI-5376, Slice A/B/C VERIFIED preconditions, WI-5400 collision evidence, 900/500 token caps, 300 second default TTL, pointer-only overrun behavior, weak-hook fallback-not-parity policy, and freshness carve-out in implementation and tests."
}
```

## Findings Addressed

### P1 - Undisclosed file collision with unrelated, not-yet-VERIFIED thread WI-5400

Response: Accepted. The proposal now discloses the collision and adds a concrete pre-implementation sequencing gate.

Current collision evidence, rechecked before drafting this revision:

- `gt bridge show gtkb-wi5400-cloud-verdict-claim-lifecycle --json --compact` reports latest status `NEW`, latest path `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md`, and version count `3`.
- `git diff --stat -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` reports `2 files changed, 400 insertions(+), 2 deletions(-)`.
- `git status --short -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-*.md bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-*.md` reports the two shared target files as modified and the WI-5400 and Slice D bridge files as untracked in the current worktree.

The dirty content on `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` belongs to WI-5400 verdict-claim lifecycle work, not Slice D envelope packet injection. Slice D will not bundle that work into a Slice D VERIFIED finalization.

## Sequencing Precondition

Prime Builder must not run `python scripts/implementation_authorization.py begin --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection`, edit any Slice D target path, file a Slice D post-implementation report, or ask LO to verify Slice D until all of the following are true:

1. `gt bridge show gtkb-wi5400-cloud-verdict-claim-lifecycle --json --compact` reports latest status `VERIFIED`.
2. The WI-5400 VERIFIED finalization commit contains the WI-5400 implementation/report/verdict artifacts, including the previously dirty `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` changes.
3. `git diff --quiet -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` exits 0 immediately before Slice D implementation-start, proving Slice D starts from a clean committed baseline for the shared files.
4. If the shared-file baseline is not clean, Prime Builder stops Slice D implementation-start and either waits for WI-5400 closure or files another governed bridge revision.

This precondition is additive to the normal latest-`GO` and implementation-start packet requirements. It does not authorize WI-5400, does not verify WI-5400, and does not permit Slice D to commit any unrelated WI-5400 diff.

## Scope Changes

Functional Slice D scope is unchanged from `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-001.md`:

- Native Claude/Codex SessionStart startup context will include a bounded session-envelope packet before role-specific startup disclosure content.
- Worker dispatch/activity context will include an activity packet or pointer where activity metadata exists.
- Weak-hook dispatch context will carry a disclosed fallback receipt or pointer and state that fallback is not native hook parity.
- Packet caps remain 900 estimated tokens for session envelope and 500 estimated tokens for activity packet, with pointer-only overrun.
- Dispatcher selection, ranking, model routing, credential state, scope hard-blocking, live queue summaries, cleanup, and historical rewrite remain out of scope.

The only revision-scope change is the explicit sequencing gate for the WI-5400 shared-file collision.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE` authorizes the modernization child project scope but does not bypass bridge GO, implementation-start, or the new shared-file sequencing precondition.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION` establishes hook-fetched worker packet injection with role bootstrap before activity specialization and manual packet CLI availability.
- `DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE` establishes TTL-stable frame fetch/cache behavior while preserving live state freshness obligations.
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY` selects minimal packet composition with hard caps of 900 session-envelope tokens and 500 activity-packet tokens.
- `DELIB-20260717-ENVELOPE-PACKET-CLI-SURFACE-CACHE` selects the CLI surface `gt session envelope packet` and cache path `.gtkb-state/session-envelope/packet-cache/`.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY` keeps weak-hook harnesses dispatchable only when the worker receives a clear fallback receipt or pointer, and forbids treating fallback as parity.
- `DELIB-20260717-ENVELOPE-DISPATCHER-POINTER-PROMPT-SCOPE` constrains later dispatcher prompt work to pointer-only scope; Slice D uses only the existing dispatch context needed for weak-hook fallback receipt/pointer disclosure.
- `DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY` preserves thread ratchet after Slice B and forbids historical rewrite.

No new owner decision is required for this revision. The sequencing precondition is a governance/scoped-commit correction in response to LO review.

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
- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-001.md`, `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-002.md`, and `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md` - unrelated thread currently occupying the two shared Slice D target files and requiring independent VERIFIED before Slice D implementation can start on those files.

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
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status authorship, review independence, and scoped-commit discipline.
- `.claude/rules/file-bridge-protocol.md` - bridge proposal, GO, implementation report, VERIFIED lifecycle, and scoped-commit guardrail.
- `.claude/rules/codex-review-gate.md` - no implementation without LO GO and implementation-start.

## Proposed Change

After independent LO `GO` and after the WI-5400 sequencing precondition is satisfied, Slice D will implement the same scoped changes proposed in version 001:

1. Add a fail-soft packet injection layer to `scripts/session_start_dispatch_core.py` that composes the Slice C session-envelope packet through `groundtruth_kb.session.packet.compose_packet`.
2. Inject the packet block into SessionStart `additionalContext` before role-specific startup disclosure or activity specialization.
3. Preserve startup-service validation and degraded-banner fallback behavior; packet composition failure must produce a clear packet-injection diagnostic without aborting SessionStart.
4. Add weak-hook fallback receipt/pointer text to the existing dispatch context for harnesses without native packet hook injection, limited to selected bridge documents and packet CLI/cache pointers.
5. Update the harness capability registry so native injection, fallback receipt/pointer operation, compact-provider operation, and unsupported/not-parity states are explicit.
6. Keep dispatcher routing, model selection, target selection, and prompt minimization out of scope. Slice E owns dispatcher selection and pointer-prompt simplification.
7. Keep subject-scope audit/warn and hard-block behavior out of scope. Slice F owns scope enforcement.

## Acceptance Criteria

- WI-5400 is independently VERIFIED and committed before Slice D implementation-start touches `scripts/dispatcher_runtime.py` or `platform_tests/scripts/test_dispatcher_runtime.py`.
- The two shared Slice D/WI-5400 files have a clean committed baseline immediately before Slice D implementation-start.
- Native SessionStart output for Claude/Codex contains a session-envelope packet block before role-specific startup disclosure content.
- Packet injection uses the Slice C packet service and preserves the 900 session-envelope and 500 activity-packet caps.
- Over-budget packet output remains pointer-only and does not emit oversized payload content.
- Packet composition failures fail soft with an explicit diagnostic and do not abort SessionStart.
- Weak-hook dispatch context contains a clear fallback receipt or packet pointer before worker action instructions.
- Weak-hook fallback text explicitly states that fallback operation is not native hook parity.
- Dispatcher selection, model routing, credential state, scope hard-blocking, and live queue summaries are not added to packet payloads.
- Harness parity registry and tests distinguish native packet injection from fallback receipt/pointer operation.
- No implementation occurs before LO `GO`, the WI-5400 precondition, and a Slice D implementation-start packet.

## Specification-Derived Verification Plan

- `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001` -> packet and SessionStart tests assert JSON shape, metadata, hard caps, pointer-only diagnostic overrun, TTL/cache metadata, and forbidden content exclusion.
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` -> SessionStart and dispatcher tests assert hook-primary injection plus explicit fallback when hook events are unavailable.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` and `DCL-ACTIVITY-CONTEXT-MANIFEST-001` -> dispatcher/activity tests assert selected activity packet or pointer is derived from `::open` activity metadata and role bootstrap ordering is preserved.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` -> tests assert injection remains bounded and overrun becomes pointer-only.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` -> packet injection tests assert live state remains represented as live-query descriptors, not stale embedded state.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` -> harness parity tests assert native/fallback/provider dispositions and no false parity claim.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` and `GOV-FILE-BRIDGE-AUTHORITY-001` -> pre-start evidence and post-implementation report show WI-5400 was VERIFIED/committed first and Slice D did not bundle unrelated dirty work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` plus PAUTH/DCL project-linkage specs -> implementation-start packet must be created after GO, after the WI-5400 sequencing precondition, and before protected mutations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -> post-implementation report carries this mapping and exact observed command results.

Planned commands after the sequencing precondition and implementation:

```powershell
gt bridge show gtkb-wi5400-cloud-verdict-claim-lifecycle --json --compact
git diff --quiet -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
python -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py -q --tb=short
python -m ruff check scripts/session_start_dispatch_core.py scripts/dispatcher_runtime.py platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py
python -m ruff format --check scripts/session_start_dispatch_core.py scripts/dispatcher_runtime.py platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_check_harness_parity.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection
python scripts/check_harness_parity.py --harness all --all --validate-schema
```

## Pre-Filing Preflight Evidence

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection --content-file .gtkb-state\bridge-revisions\drafts\gtkb-envelope-protocol-slice-d-worker-hook-injection-003.md --json` exited 0 with `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`, declared target paths resolved, and packet hash `sha256:e8ca02b9aa3c4a4e1326c2b35b6893d05d513a8d6337033464ed856b84562913`.
- ADR/DCL clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-worker-hook-injection --content-file .gtkb-state\bridge-revisions\drafts\gtkb-envelope-protocol-slice-d-worker-hook-injection-003.md` exited 0 with 5 clauses evaluated, 3 `must_apply`, 0 evidence gaps in `must_apply` clauses, and 0 blocking gaps.

## Implementation Boundaries

- No Slice D implementation-start packet until latest Slice D status is `GO`, WI-5400 is independently VERIFIED/committed, and the two shared files are clean relative to HEAD.
- No dispatcher selection, ranking, model-choice, or target-eligibility logic change in Slice D.
- No retirement of dispatcher init-keyword prompt composition in Slice D.
- No subject-scope map, audit/warn, hard-block, or owner-gated hard-block flip in Slice D.
- No session-startup-index, role-overlay, canonical-terminology glossary, system-interface-map, or retired-surface cleanup in Slice D except if implementation tests reveal an unavoidable direct dependency; those are planned for later slices.
- No historical bridge rewrite or migration of old thread content.
- No credential, release, production deployment, external-system mutation, Git push, or destructive cleanup.

## Risk / Rollback

Primary risk remains startup breakage. The mitigation is fail-soft packet composition, preservation of the existing startup-service degraded-banner path, and wrapper tests for Claude and Codex.

Secondary risk is false parity: weak-hook fallback could be mistaken for native hook injection. The mitigation is explicit registry disposition, worker-visible fallback receipt/pointer text, and parity tests asserting fallback remains degraded/not-parity.

The newly disclosed risk is cross-thread contamination. The mitigation is the hard sequencing precondition above: WI-5400 must reach independent VERIFIED and the shared files must be clean before Slice D implementation-start.

Rollback before VERIFIED is scoped to reverting only Slice D edits after the clean baseline is established, then filing a revised bridge report. After VERIFIED, corrections must use a follow-on bridge thread.

## Order Of Work

1. Wait for independent LO `GO` on this revised Slice D proposal.
2. Confirm WI-5400 latest status is `VERIFIED` and its finalization commit has landed.
3. Confirm `git diff --quiet -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` exits 0 before Slice D implementation-start.
4. Create the implementation-start authorization packet for `gtkb-envelope-protocol-slice-d-worker-hook-injection`.
5. Implement only the declared SessionStart injection, weak-hook fallback receipt/pointer, registry disposition, and focused tests.
6. Run the specification-derived tests, ruff lint, ruff format check, harness parity validation, shared-file baseline evidence, and bridge preflights.
7. File a post-implementation report through the bridge with exact command evidence and spec-to-test mapping.
8. Wait for independent LO `VERIFIED` before resolving WI-5376 or starting Slice E implementation.
