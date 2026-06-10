NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e95cd-bdc9-7da2-9b1d-c4cbb31e21d1
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop; interactive; Prime Builder; danger-full-access; approval-policy never
author_metadata_source: Codex explicit metadata in bridge proposal

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-COMPACT-AUTO-DISPATCH-STARTUP-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4361
Recommended commit type: feat

target_paths: ["scripts/session_self_initialization.py","scripts/session_start_dispatch_core.py","platform_tests/scripts/test_session_self_initialization.py","platform_tests/hooks/test_session_start_dispatch_role_cache.py","platform_tests/scripts/test_claude_session_start_dispatcher.py","platform_tests/scripts/test_codex_session_start_dispatcher.py",".gtkb-state/startup-payload-profiles/**"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Startup Payload Profiler + Compact SessionStart Context

bridge_kind: prime_proposal
Document: gtkb-startup-payload-profiler-compact-context
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-05 UTC

## Claim

`WI-4361` should change the startup-service/dispatcher contract so default SessionStart `additionalContext` is a compact machine summary with explicit expansion paths, while the full owner-visible startup disclosure remains complete and available through the init-keyword relay cache. The same implementation should add lightweight payload profiling as verification instrumentation for the compact path; `WI-4360` remains a paired backlog item and is not claimed complete by this proposal unless a later implementation report explicitly closes it with its own authorization evidence.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped startup-payload implementation. The approved owner decision `DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL`, `WI-4361`, `GOV-SESSION-SELF-INITIALIZATION-001`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, and `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` define enough behavior to implement compact SessionStart context, demand-loaded expansion, and regression coverage without a new or revised formal specification.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`. Source changes are limited to the startup service and shared SessionStart dispatcher. Test changes are limited to startup-service/dispatcher regression tests. Generated payload profiles are runtime state under `.gtkb-state/startup-payload-profiles/`.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup must be generated from live role, governance, bridge, dashboard, priority, and token context; this change preserves fresh generation while compacting the default model-facing payload.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - startup must surface token-cost context and reduction options; the new compact path and profile metadata make startup size measurable instead of relying on oversized repeated disclosure text.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - init-keyword disclosure relay must remain visible and cache-isolated; the dispatcher must cache the full disclosure from a separate field while emitting compact `additionalContext`.
- `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` - Codex first-prompt/session-start behavior depends on real SessionStart dispatch; the envelope shape must remain valid and not accidentally arm or bypass interactive startup handling.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role-scoped startup caches must still be written for both Prime Builder and Loyal Opposition paths regardless of durable role-set details.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authorization is required before modifying protected startup/dispatcher scripts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the implementation scope to governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work item metadata are declared in machine-readable header lines.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map cited specifications to tests and executed commands before VERIFIED.

## Prior Deliberations

- `DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL` - owner approved the full sequence from the glossary/CLI scan delta report, including startup refactor expansion and Codex skill-path hardening follow-ups.
- `DELIB-1075` - prior startup token consumption review; establishes the recurring concern that startup payloads consume too much context.
- `DELIB-2327` - Loyal Opposition verification of startup-refractor glossary-load surface; related startup refactor precedent.
- `DELIB-2328` - Loyal Opposition review of startup-refractor glossary-load surface; related review precedent.

## Owner Decisions / Input

- `DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL` records Mike's approval to convert the INSIGHTS report recommendations into backlog and governed implementation flow.
- `PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-COMPACT-AUTO-DISPATCH-STARTUP-IMPLEMENTATION-AUTHORIZATION` authorizes `WI-4361` implementation with source/test/generated-runtime-file scope and forbids formal artifact mutation without a packet.
- No additional owner decision is required before implementation if Loyal Opposition returns GO for this proposal.

## Proposed Scope

1. In `scripts/session_self_initialization.py`, split generated startup output into compact `hookSpecificOutput.additionalContext` and complete `hookSpecificOutput.startupDisclosure` fields.
2. Keep compact context focused on mandatory routing facts: contract/version, generated time, role/harness identity, work subject, bridge authority, top priority action IDs/titles, startup report/dashboard/wrap-up paths, relay-cache paths, and payload-profile path.
3. Add deterministic payload profile metadata for `additionalContext` and `startupDisclosure`, including UTF-8 bytes, line count, character count, rough token estimate, and SHA-256 digest.
4. Write the latest profile to `.gtkb-state/startup-payload-profiles/last-<harness>.json` as generated runtime state; also include the profile object in the SessionStart hook payload.
5. In `scripts/session_start_dispatch_core.py`, populate relay caches from `startupDisclosure` when that field exists and is non-empty; otherwise preserve compatibility with legacy payloads that embed `## User-Visible Startup Message` in `additionalContext`.
6. Do not change bridge auto-dispatch routing, strict-drop behavior, lifecycle guard semantics, or role-resolution authority.

## Out Of Scope

- No MemBase schema change.
- No formal GOV/SPEC/ADR/DCL mutation.
- No change to the init-keyword grammar.
- No closure claim for `WI-4360` unless a later implementation report demonstrates the profiler acceptance criteria under its own authorization basis.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credential, token, or environment-secret output; profile records only byte counts and digests of generated startup text. | Bridge credential scan plus focused startup tests inspect profile shape. |  |
| CQ-PATHS-001 | Yes | Keep all source, test, and generated runtime paths inside `E:\GT-KB`; normalize profile output under `.gtkb-state/startup-payload-profiles/`. | Bridge target-path gate and focused tests cover in-root profile path. |  |
| CQ-COMPLEXITY-001 | Yes | Use small helpers for compact context, disclosure extraction, and profile construction rather than expanding dispatcher branching. | `python -m ruff check` on touched files. |  |
| CQ-CONSTANTS-001 | Yes | Use named contract/profile strings and existing startup constants for generated payload fields. | Code review plus `ruff check` on touched files. |  |
| CQ-SECURITY-001 | Yes | Preserve fail-soft startup behavior and avoid new network, credential, auth, or shell execution paths. | Focused startup-service and dispatcher tests exercise success and compatibility paths. |  |
| CQ-DOCS-001 | N/A | Runtime payload text changes only; no durable user documentation artifact is in scope. | Review target paths and bridge report. | No documentation artifact target in this implementation slice. |
| CQ-TESTS-001 | Yes | Add/update regression tests for compact context, complete disclosure relay, profile metadata, and role-cache compatibility. | `python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_session_start_dispatch_role_cache.py -q --tb=short`. |  |
| CQ-LOGGING-001 | Yes | Emit deterministic JSON profile runtime state without noisy stdout/stderr logging. | Focused tests assert profile metadata and startup payload fields. |  |
| CQ-VERIFICATION-001 | Yes | Run focused pytest commands and `ruff check` for every source/test target touched. | Commands listed in the Specification-Derived Verification Plan. |  |

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Run `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short` and confirm fresh service payloads still pass freshness validation and contain live startup metadata. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Add assertions that compact `additionalContext` omits the full startup disclosure, includes expansion/profile paths, and exposes profile byte/token-proxy metadata. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Add/update dispatcher tests proving relay caches are populated from `startupDisclosure` and legacy embedded-disclosure payloads still work. |
| `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` | Run Codex/Claude dispatcher envelope tests and confirm emitted SessionStart envelopes retain valid `hookSpecificOutput` shape. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Run `python -m pytest platform_tests/hooks/test_session_start_dispatch_role_cache.py -q --tb=short` to confirm both role-scoped caches are still produced. |
| Bridge/proposal specs | Run focused tests plus `python -m ruff check scripts/session_self_initialization.py scripts/session_start_dispatch_core.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_session_start_dispatch_role_cache.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py`. |

## Acceptance Criteria

- Default SessionStart `additionalContext` is compact and does not embed the full `## User-Visible Startup Message` disclosure body.
- `hookSpecificOutput.startupDisclosure` contains the complete owner-visible startup disclosure needed by init-keyword relay.
- Dispatcher relay cache writing uses `startupDisclosure` when available and continues supporting legacy embedded-disclosure payloads.
- Startup payload profile metadata is deterministic, includes byte/line/character/rough-token/SHA fields, and is written to `.gtkb-state/startup-payload-profiles/`.
- Focused startup-service and dispatcher tests pass.

## Risks / Rollback

- Risk: relay cache truncation or loss if the dispatcher reads only compact context. Mitigation: write tests that assert caches contain the full startup disclosure after a compact payload.
- Risk: payload profile writes could make startup brittle. Mitigation: fail-soft profile file write while preserving in-payload profile metadata.
- Rollback: restore `additionalContext` to the previous embedded-disclosure format and remove the `startupDisclosure` field/profile writer if regression evidence appears.

## Files Expected To Change

- `scripts/session_self_initialization.py`
- `scripts/session_start_dispatch_core.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/hooks/test_session_start_dispatch_role_cache.py`
- `platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `platform_tests/scripts/test_codex_session_start_dispatcher.py`
- `.gtkb-state/startup-payload-profiles/**`
