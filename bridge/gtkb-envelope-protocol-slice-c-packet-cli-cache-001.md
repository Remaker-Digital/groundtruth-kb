NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-17T10-20-39Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never; session_id=A-2026-07-17T10-20-39Z

Document: gtkb-envelope-protocol-slice-c-packet-cli-cache
Version: 001
Author: Prime Builder / Codex
Date: 2026-07-17
bridge_kind: prime_proposal
implementation_scope: envelope-protocol-slice-c-packet-cli-cache
kb_mutation_in_scope: false
target_paths: ["groundtruth-kb/src/groundtruth_kb/session/packet.py", "groundtruth-kb/src/groundtruth_kb/session/__init__.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/groundtruth_kb/test_session_envelope_packet.py", "platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py"]
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5375

# Implementation Proposal: Envelope Protocol Slice C Packet CLI And Cache

## Summary

Implement Slice C of the envelope protocol modernization program: a deterministic session-envelope packet service and public CLI surface at `gt session envelope packet`. The slice composes bounded JSON packets from canonical session-startup and activity-disposition inputs, enforces the owner-ratified packet budgets, writes derived packets under `.gtkb-state/session-envelope/packet-cache/` with a five-minute default TTL, and preserves the source-of-truth freshness carve-out for live state claims.

This proposal does not authorize hook injection, dispatcher prompt injection, subject-scope audit/warn or hard-block behavior, startup-index cleanup, role-overlay cleanup, historical bridge rewriting, credential changes, release work, deployment, or destructive cleanup. Those remain later slices.

## Requirement Sufficiency

Existing requirements sufficient. Slice A inserted the canonical envelope-protocol authority set, Slice B is independently VERIFIED, WI-5375 defines this slice, and the owner-ratified B-records plus 2026-07-17 AskUserQuestion decisions define the bounded packet CLI/cache requirements. No new or revised requirement is needed before implementation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5375; bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md; bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md; DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY; DELIB-20260717-ENVELOPE-PACKET-CLI-SURFACE-CACHE; DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION; DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE",
  "canonical_authority": "SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001, DCL-ACTIVITY-CONTEXT-MANIFEST-001, DCL-ACTIVITY-DISPOSITION-PROFILE-001, DCL-SESSION-STARTUP-TOKEN-BUDGET-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.",
  "primary_route": "Bridge GO, implementation-start packet, scoped packet service and CLI implementation, spec-derived tests, post-implementation report, and independent Loyal Opposition VERIFIED.",
  "before_behavior": "Session envelope open/show surfaces exist, activity disposition profile and context manifest loaders exist, but no governed deterministic packet CLI/cache composes bounded session-envelope or activity-packet payloads for harness injection or pointer-only fallback.",
  "after_behavior": "`gt session envelope packet` emits bounded JSON packet output and optionally uses `.gtkb-state/session-envelope/packet-cache/` with a default 300 second TTL. Packets carry live-query descriptors for high-churn state instead of authorizing stale state claims.",
  "self_descriptive_naming": "The module `groundtruth_kb.session.packet`, CLI command `gt session envelope packet`, cache path `session-envelope/packet-cache`, and tests all use packet, envelope, activity, TTL, and budget names tied directly to Slice C.",
  "obsolete_guidance_disposition": "No existing loading paths, hooks, dispatcher prompt surfaces, role overlays, startup-index entries, or historical bridge files are retired in Slice C. Later slices own injection, pointer prompt, scope rollout, and cleanup.",
  "history_preservation": "Slice A and Slice B bridge histories, Deliberation Archive records, MemBase records, and existing session-envelope runtime artifacts remain append-only. Packet cache entries are derived runtime state and never canonical authority.",
  "baseline": {
    "slice_a": "bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md VERIFIED",
    "slice_b": "bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md VERIFIED",
    "work_item": "WI-5375 open/backlogged before this proposal",
    "cli_surface": "`gt session envelope open` and `gt session envelope show` exist; `gt session envelope packet` is absent",
    "cache_surface": "No governed `.gtkb-state/session-envelope/packet-cache/` packet cache contract is implemented"
  },
  "expected_result": {
    "cli": "Public command `gt session envelope packet`",
    "session_envelope_token_cap": 900,
    "activity_packet_token_cap": 500,
    "cache": ".gtkb-state/session-envelope/packet-cache/",
    "ttl_seconds": 300,
    "overrun": "Pointer-only diagnostic packet, not an oversized payload",
    "freshness": "Live state claims remain routed to fresh canonical reads"
  },
  "rollback": {
    "instructions": "Before VERIFIED, revert only the scoped packet service, CLI, and test edits and file a revised bridge report. After VERIFIED, correct through a governed follow-on bridge thread instead of rewriting bridge history or deleting cache provenance.",
    "verification": "Rerun focused packet pytest targets, CLI tests, ruff check, ruff format check, bridge applicability preflight, and ADR/DCL clause preflight after rollback or correction."
  },
  "hard_invariants": [
    "No implementation before independent GO and implementation-start packet",
    "No hook injection in Slice C",
    "No dispatcher pointer-prompt mutation in Slice C",
    "No subject-scope audit/warn or hard block in Slice C",
    "No historical bridge rewrite",
    "No credential, release, deployment, external-system, or destructive cleanup mutation",
    "Packet cache cannot authorize current-state claims",
    "Over-budget packet output must fail closed to a pointer-only diagnostic",
    "Session-envelope cap remains 900 estimated tokens and activity-packet cap remains 500 estimated tokens"
  ],
  "fail_closed_conditions": [
    "Missing latest GO or implementation-start packet",
    "Invalid activity outside the closed activity vocabulary",
    "Missing packet source metadata, source hash, TTL metadata, or live-query descriptors",
    "Session packet exceeds 900 estimated tokens without pointer-only fallback",
    "Activity packet exceeds 500 estimated tokens without pointer-only fallback",
    "Packet embeds forbidden dispatcher ranking policy, model-selection policy, credentials, or unrelated live queue summaries",
    "Cache hit is stale, source hash mismatched, malformed, or lacks explicit TTL",
    "Tests weaken the source-of-truth freshness carve-out"
  ],
  "essential_context_preservation": "Preserve owner AUQ decision IDs, PAUTH, WI-5375, Slice A/B VERIFIED preconditions, 900/500 token caps, 300 second default TTL, pointer-only overrun behavior, minimal composition policy, and freshness carve-out in implementation and tests."
}
```

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE` authorizes the modernization child project scope but does not bypass bridge GO or implementation-start.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION` establishes that packet hook injection is downstream from packet composition. Slice C implements the deterministic packet service and CLI only.
- `DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE` establishes TTL-stable frame fetch/cache behavior while preserving live state freshness obligations.
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY` selects minimal packet composition with hard caps of 900 session-envelope tokens and 500 activity-packet tokens.
- `DELIB-20260717-ENVELOPE-PACKET-CLI-SURFACE-CACHE` selects the CLI surface `gt session envelope packet` and cache path `.gtkb-state/session-envelope/packet-cache/`.
- `DELIB-20260717-ENVELOPE-DISPATCHER-POINTER-PROMPT-SCOPE` constrains later dispatcher prompt injection to pointer-only behavior; Slice C implements the pointer-only overrun packet path but does not mutate the dispatcher prompt.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY` permits weak-hook dispatch only with disclosed fallback receipt/pointer and no parity claim; this is later-slice dispatch/injection scope.
- `DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY` preserves thread ratchet after Slice B and forbids historical rewrite.

## Prior Deliberations

- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - runtime charter basis for session-role envelope behavior.
- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS` - responder-role semantics for envelope lines.
- `DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY` - governed writers own line authoring and validation.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` - Body Status-Token Rule preservation.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION` - packet hook injection is governed later-slice scope.
- `DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE` - TTL-stable fetch/cache authority for packets.
- `DELIB-20260716-ENVELOPE-GRILL-B8-SCOPE-STAGED-HARD-BLOCK` - staged audit/warn then owner-gated hard-block policy for Slice F.
- `DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD` - child project and governed slice chain.
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY` - minimal packet composition and 900/500 token hard caps.
- `DELIB-20260717-ENVELOPE-PACKET-CLI-SURFACE-CACHE` - public CLI and cache path decision.
- `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md` - Slice A canonical authority insertion VERIFIED.
- `bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md` - Slice B bridge writer envelope-head implementation VERIFIED.

## Specification Links

- `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001` - packet shape, bounded composition, pointer-only diagnostics, CLI/cache surface, and forbidden content.
- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - seven-category context manifest rules, role bootstrap before activity overlay, high-churn live-query routing, and essential context preservation.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - six canonical activities, four-class profile behavior, and `::open` activity vocabulary.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - session startup token-cost and reduction constraints.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - TTL exception boundaries and live-state fresh canonical read requirements.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - repetitive deterministic packet composition belongs in service code.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - modernization slices must carry non-impairment evidence and preserve existing governed workflows.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, work items, bridge proposals, implementation reports, and verification evidence remain durable artifact records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the slice preserves traceability across decisions, artifacts, work items, tests, reports, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle states remain explicit: proposal, GO, implementation report, VERIFIED, work-item resolution, and later program closure.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires active project authorization plus bridge GO and implementation-start packet.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH evidence is additive and bounded.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time enforcement must validate live scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal includes PAUTH, project, and work-item metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - WI-5375 belongs to the approved modernization project.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links relevant governing specifications and maps tests from them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must execute tests derived from linked specs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status authorship and review independence remain role-bound.
- `.claude/rules/file-bridge-protocol.md` - bridge proposal, GO, implementation report, and VERIFIED lifecycle.
- `.claude/rules/codex-review-gate.md` - no implementation without LO GO and implementation-start.

## Proposed Change

1. Add `groundtruth_kb.session.packet` as a deterministic packet composition service.
2. Add `gt session envelope packet` under the existing `session envelope` CLI group.
3. Support session-envelope and activity-packet output modes with stable JSON output suitable for harness injection or pointer-only dispatcher use.
4. Read canonical stable inputs from `config/agent-control/SESSION-STARTUP-INDEX.md`, role startup overlays, activity disposition profiles, activity envelope sharding config, and context manifest registry surfaces already used by existing envelope/context code.
5. Represent high-churn state as live-query descriptors and source pointers, not embedded stale summaries.
6. Estimate packet token budget deterministically and enforce hard caps of 900 estimated tokens for session-envelope packets and 500 estimated tokens for activity packets.
7. On budget overrun, emit a pointer-only diagnostic packet with the cache key, source pointers, measured budget, and failure reason rather than emitting an oversized payload.
8. Cache successful derived packets under `.gtkb-state/session-envelope/packet-cache/` with a default TTL of 300 seconds, source hashes, activity/profile metadata, and a bypass/refresh path for fresh reads.
9. Treat stale, hash-mismatched, malformed, or TTL-missing cache entries as cache misses.
10. Keep Slice C source/test scope limited to the declared target paths.

## Acceptance Criteria

- `gt session envelope packet` exists and returns JSON for valid session-envelope and activity-packet requests.
- Packet output includes packet kind, activity where applicable, generated timestamp, TTL metadata, source pointers, source hashes, estimated token count, budget cap, cache metadata, and live-query descriptors.
- Session-envelope packet output is capped at 900 estimated tokens.
- Activity-packet output is capped at 500 estimated tokens.
- Over-budget composition returns a pointer-only diagnostic packet and does not emit over-budget payload content.
- Default cache path is `.gtkb-state/session-envelope/packet-cache/`.
- Default cache TTL is 300 seconds and is tunable by CLI/service option.
- Cache hits are used only when TTL and source hashes are valid.
- Live state claims remain fresh-read only; cache output cannot be used as authority for current bridge/backlog/project/git state.
- No hook, dispatcher prompt, scope-enforcement, startup-overlay cleanup, release, credential, deployment, or destructive cleanup behavior changes in this slice.
- No implementation occurs before LO `GO` and an implementation-start packet.

## Specification-Derived Verification Plan

Spec-to-test mapping for the post-implementation report:

- `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001` -> packet service tests assert JSON shape, required metadata, hard caps, pointer-only diagnostic overrun, forbidden content exclusion, cache path, cache TTL, and CLI surface.
- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` -> packet tests assert manifest-derived categories are represented as stable pointers/descriptors and high-churn categories remain live-query only.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` -> packet tests assert valid activity selection from the six canonical activities and invalid activity rejection.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` -> packet tests assert deterministic token estimation and budget enforcement.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` -> cache tests assert TTL-stable derived packets never authorize current-state claims and stale/hash-mismatched entries miss.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` -> tests and CLI evidence show deterministic service output independent of interactive session prose.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` -> proposal/report evidence and tests show Slice C avoids hook, dispatcher, scope, cleanup, credential, release, and historical rewrite behavior.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` plus PAUTH/DCL project-linkage specs -> implementation-start packet must be created after GO and before protected mutations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -> post-implementation report carries this mapping and exact observed command results.

Planned commands after implementation:

```powershell
python -m pytest platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py groundtruth-kb/tests/test_context_manifest.py platform_tests/scripts/test_activity_disposition_profiles.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/session/packet.py groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/packet.py groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache
```

## Pre-Filing Preflight Evidence

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache --content-file .gtkb-state\bridge-propose-drafts\gtkb-envelope-protocol-slice-c-packet-cli-cache-001.md --json` exited 0 with `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`, and packet hash `sha256:e0968be629d608da7b4ce5c22476028201b06cbec911e5873537e95840fdee39` before this evidence-line insertion.
- ADR/DCL clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache --content-file .gtkb-state\bridge-propose-drafts\gtkb-envelope-protocol-slice-c-packet-cli-cache-001.md` exited 0 with 5 clauses evaluated, 3 `must_apply`, 0 evidence gaps in `must_apply` clauses, and 0 blocking gaps.
- Bridge-compliance audit: Codex helper inline audit for `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-001.md` returned `decision: pass` and `preflight_passed: true` before live filing.

## Implementation Boundaries

- No packet hook injection in Slice C.
- No dispatcher prompt mutation in Slice C.
- No subject-scope map audit/warn or hard-block behavior in Slice C.
- No session-startup-index, role-overlay, canonical-terminology glossary, system-interface-map, or retired-surface cleanup in Slice C except if implementation tests reveal an unavoidable direct dependency; those are planned for later slices.
- No historical bridge rewrite or migration of old thread content.
- No credential, release, production deployment, external-system mutation, Git push, or destructive cleanup.

## Risk / Rollback

Primary risk is accidental stale-state authority: a derived packet cache could be misread as source-of-truth state. The mitigation is explicit source pointers, source hashes, TTL metadata, live-query descriptors, stale/hash-mismatch cache misses, and tests proving cache output does not authorize current-state claims.

Secondary risk is token-budget drift. The mitigation is a deterministic estimation function with focused tests that force the over-budget path and verify pointer-only diagnostics.

Rollback before VERIFIED is scoped to reverting the packet service, CLI, and tests and filing a revised bridge report. After VERIFIED, corrections must use a follow-on bridge thread.

## Order Of Work

1. Wait for independent LO `GO` on this Slice C proposal.
2. Create the implementation-start authorization packet for `gtkb-envelope-protocol-slice-c-packet-cli-cache`.
3. Implement only the declared packet service, CLI, and focused tests.
4. Run the specification-derived tests, ruff lint, ruff format check, and bridge preflights.
5. File a post-implementation report through the bridge with exact command evidence and spec-to-test mapping.
6. Wait for independent LO `VERIFIED` before resolving WI-5375 or starting Slice D implementation.
