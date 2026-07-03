NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder session; runtime reasoning profile not exposed

# Implementation Proposal - Mechanically block direct harness-to-harness launches

bridge_kind: prime_proposal
Document: gtkb-wi4988-direct-harness-launch-guard
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4988-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4988

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Mechanically enforce the owner prohibition on direct harness-to-harness invocation while preserving dispatcher-owned headless dispatch.

Work item description: Owner prohibited direct harness-to-harness interaction after Codex directly launched a Claude Code headless LO fallback. Implement mechanical enforcement so interactive harness commands cannot directly launch, trigger, command, or supervise another AI harness (claude, codex exec, ollama/cursor/openrouter/antigravity shims, etc.) as a standby or backup path. Allowed cross-harness work must flow through the governed dispatcher/control plane or independent owner/manual harness operation. Dispatcher-mediated launches need an explicit internal exemption/marker so the dispatcher remains the only automation path.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4988` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`, `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`, `platform_tests/scripts/test_fab14_directive_hook_coverage.py`, `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`.

## Specification Links

- `SPEC-INTAKE-21c5b3` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4988-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4988`.

## Proposed Scope

- Add a shared directive-enforcement command classifier that blocks interactive harness commands from invoking another AI harness directly.
- Cover Claude Code, Codex, Ollama, Cursor, OpenRouter, and Antigravity/Gemini launch signatures, including Windows executable suffixes and PowerShell wrappers.
- Preserve dispatcher-mediated launches by keeping the allowed spawn path inside scripts/dispatcher_runtime.py and making that path explicit in tests and metadata.
- Return remediation text that directs the agent to bridge and dispatcher control-plane surfaces instead of direct fallback spawning.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-21c5b3` | Unit tests exercise direct harness-launch command signatures across Bash and PowerShell syntax and assert denial plus remediation text. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Hook coverage tests confirm the existing shared directive-enforcement adapters apply to Claude, Codex, and Cursor command surfaces. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher-runtime tests assert mediated dispatch remains allowed and records/labels dispatcher-owned worker launches. |

## Acceptance Criteria

- Direct shell/PowerShell commands for claude, codex exec, ollama, cursor, openrouter, and antigravity/agy/gemini launch signatures are denied by the shared directive-enforcement gate.
- Non-harness status/read commands and normal in-root development commands continue to pass the existing false-positive corpus.
- Dispatcher runtime remains the only automated harness-spawn path and its tests prove the mediated path still constructs/launches workers without using interactive shell hooks.
- Denial output names the no-direct-harness rule and points to governed bridge/dispatcher control surfaces.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`

## Recommended Commit Type

`feat`
