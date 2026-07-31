NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope active; WI-5275 implementation requires ops envelope for configuration-like hook/registration mutation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Black-box enforcement parity gates

bridge_kind: prime_proposal
Document: gtkb-wi5275-black-box-enforcement-parity-gates
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5275-ENFORCEMENT-PARITY-GATES-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5275

target_paths: [".claude/settings.json", ".codex/hooks.json", ".cursor/hooks.json", "config/agent-control/harness-capability-registry.toml", ".claude/hooks/sot-read-discipline.py", "scripts/dispatch_blackbox_gate.py", "scripts/cursor_hook_adapter.py", "scripts/sdk_bridge_bash_guard.py", "scripts/protected_mutation_guard.py", "scripts/check_codex_hook_parity.py", "scripts/check_harness_parity.py", "platform_tests/scripts/test_dispatch_blackbox_gate.py", "platform_tests/scripts/test_dispatch_blackbox_gate_activation.py", "platform_tests/scripts/test_sot_read_discipline_hook.py", "platform_tests/scripts/test_cursor_hook_headless_parity.py", "platform_tests/scripts/test_check_codex_hook_parity.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_parity_coverage_complete.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py", "platform_tests/scripts/test_protected_mutation_guard.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py"]

implementation_scope: configuration/source/test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5275 proposes phased black-box enforcement across supported read, search, shell, apply_patch, and write surfaces. It hardens only where worker-safe packet surfaces and harness parity are present; unsupported surfaces receive tracked typed waivers plus compensating scans.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5275` and keeps the bridge, PAUTH, ops-envelope, parity-waiver, and verification gates intact.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved phased hardening decision and active PAUTH are sufficient to propose enforcement. Implementation that mutates hook registrations, harness config, or parity registry files must occur only after LO GO, work-intent claim, implementation-start authorization, and an ops activity envelope for configuration-like mutations.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB` and no adopter application path is targeted.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher remains a GT-KB-owned black-box service surface.
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - protected access requires activity-envelope/case authority.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - ordinary workers must not directly inspect or mutate protected internals.
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` - enforcement is safe only after worker-safe packet surfaces exist.
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` - ordinary work should route through worker-context/mediated packet facades.
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` - child enforcement remains tied to the approved foundation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms this platform enforcement work stays outside adopter application scope.
- `ADR-CROSS-HARNESS-PARITY-001` - cross-harness behavior changes require parity or typed waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface proposals require cross-harness disposition.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses explicit compliance/fallback evidence when native hook parity differs.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` - owner selected safe surfaces first, then audit/soft-deny, then hard gates after parity.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE` - strict operational black-box boundary for ordinary workers.
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT` - protected direct access requires recorded scoped maintenance capability.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - ops controls black-box configuration mutation; build controls direct internals mutation only with case authorization.
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE` - raw bridge files and bridge index are protected ordinary-worker surfaces.

## Owner Decisions / Input

- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` - owner-decision evidence for phased enforcement sequencing.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - owner correction requiring ops envelope for black-box configuration mutation and case-specific build authorization for internals.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5275-ENFORCEMENT-PARITY-GATES-20260717` - active project authorization covering `WI-5275`.

## Cross-Harness Disposition

| Harness | Disposition | Evidence / Required Follow-up |
| --- | --- | --- |
| Claude Code | In scope for read/search/write/shell hook registration and shared hook code. | `.claude/settings.json`, `.claude/hooks/sot-read-discipline.py`, and shared guard scripts must enforce or soft-deny according to parity phase. |
| Codex | In scope for Bash/apply_patch hook registration and fallback evidence. | `.codex/hooks.json`, `scripts/check_codex_hook_parity.py`, and shared guards must prove equivalent coverage or explicit fallback. |
| Cursor | In scope for shell/write adapter registration and parity tests. | `.cursor/hooks.json`, `scripts/cursor_hook_adapter.py`, and `test_cursor_hook_headless_parity.py` must either enforce supported surfaces or record typed waiver for unsupported ones. |
| Antigravity | Waiver/compensating-scan disposition in scope through the parity registry, not direct hook registration. | `config/agent-control/harness-capability-registry.toml` must record any unsupported Antigravity enforcement surface with typed waiver and compensating scan. |
| Ollama / OpenRouter SDK harnesses | Guard/compensating-scan disposition in scope through shell guard and parity registry. | `scripts/sdk_bridge_bash_guard.py` and parity tests must continue denying bridge mutation/self-invocation and record unsupported read/apply_patch surfaces as waivers if not enforceable. |

## Proposed Scope

- Extend black-box enforcement from narrow direct write/edit mutation gates toward supported read/search/shell/apply_patch/file-mutation surfaces across active harnesses.
- Implement audit/soft-deny first where hard deny is not yet parity-safe; hard-deny only surfaces with proven worker-safe replacement paths and harness parity.
- Add typed parity waivers and compensating scans for unsupported surfaces instead of silently claiming full enforcement.
- Keep hook/config mutations ops-envelope-only after GO; this proposal does not authorize dispatcher/TAFE runtime/config mutation, harness registry mutation, credentials, release, deployment, Git push, or destructive cleanup.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run black-box gate, protected mutation, read-discipline, shell guard, and hook parity tests proving dispatcher internals remain protected. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Verify enforcement distinguishes ordinary, ops, build, and case-authorized internals access. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Verify ordinary read/search/shell/write/apply_patch attempts against protected raw bridge/dispatcher/TAFE/harness internals are denied, soft-denied, or waiver-scanned as specified. |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Verify hard-denied surfaces have worker-safe packet replacement paths and denial messages name them. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Verify enforcement routes ordinary workers to worker-context/mediated packet commands rather than raw internals. |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | Verify implementation remains covered by the active WI-5275 PAUTH and foundation specs. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify target paths remain GT-KB platform/harness enforcement files and do not touch adopter application files. |
| `ADR-CROSS-HARNESS-PARITY-001` | Run harness parity checks showing supported surfaces are equivalent and unsupported surfaces carry typed waivers. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run proposal compliance plus parity coverage tests proving this Cross-Harness Disposition remains accurate. |

## Acceptance Criteria

- Supported Claude, Codex, and Cursor surfaces deny or soft-deny ordinary protected raw bridge/dispatcher/TAFE/harness internals access according to the phased hardening plan.
- Unsupported or not-yet-hard-deniable Antigravity/Ollama/OpenRouter surfaces have typed parity waivers and compensating scan coverage in the parity registry/tests.
- Denial messages point ordinary workers to worker-context or mediated bridge packet commands and do not leak protected runtime/config/ranking internals.
- Hook registration tests, parity tests, black-box gate tests, read-discipline tests, and shell guard tests cover both positive operator/capability cases and ordinary-worker negative cases.
- Implementation report proves ops-envelope context for configuration-like hook/registration/parity-registry mutations.

## Risks / Rollback

Risk is high because this can block developer tools if a matcher is too broad. Rollout must preserve audit/soft-deny staging and typed waivers where parity is incomplete.

Rollback is a revert of hook/config/source/test changes under the approved target paths. Bridge files and PAUTH records remain append-only audit artifacts.

## Files Expected To Change

- `.claude/settings.json`
- `.codex/hooks.json`
- `.cursor/hooks.json`
- `config/agent-control/harness-capability-registry.toml`
- `.claude/hooks/sot-read-discipline.py`
- `scripts/dispatch_blackbox_gate.py`
- `scripts/cursor_hook_adapter.py`
- `scripts/sdk_bridge_bash_guard.py`
- `scripts/protected_mutation_guard.py`
- `scripts/check_codex_hook_parity.py`
- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_dispatch_blackbox_gate.py`
- `platform_tests/scripts/test_dispatch_blackbox_gate_activation.py`
- `platform_tests/scripts/test_sot_read_discipline_hook.py`
- `platform_tests/scripts/test_cursor_hook_headless_parity.py`
- `platform_tests/scripts/test_check_codex_hook_parity.py`
- `platform_tests/scripts/test_check_harness_parity.py`
- `platform_tests/scripts/test_parity_coverage_complete.py`
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`
- `platform_tests/scripts/test_workstream_focus_hook_parity.py`

## Recommended Commit Type

`feat`
