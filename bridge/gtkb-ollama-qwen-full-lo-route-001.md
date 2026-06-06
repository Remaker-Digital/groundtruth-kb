NEW

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; workspace E:\GT-KB; approval-policy never

# Ollama Qwen Full Loyal Opposition Route

bridge_kind: implementation_proposal
Document: gtkb-ollama-qwen-full-lo-route
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-OPERATIONS-QWEN-FULL-LO
Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4385
Owner Decision: DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE
Date: 2026-06-06 UTC
Requires verification: true
Recommended commit type: feat

## Summary

Switch the active Ollama Loyal Opposition route from the Kimi read/search-only profile to `qwen3-coder-next:cloud` with full guarded bridge capability. The slice updates skill routing, strengthens live dispatch readiness to require the complete bridge tool set, and injects compact Loyal Opposition bridge instructions into Ollama bridge-review and verification runs so dispatched Ollama work can write verdict artifacts and update `bridge/INDEX.md` instead of only returning prose.

## Owner Decisions And Input

Mike explicitly approved this work in `DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE`:

- Find a solution that will allow Ollama models, specifically `qwen3-coder-next:cloud`, to behave as a full-fledged Loyal Opposition.
- Switch the model to `qwen3-coder-next:cloud`.

No further owner choice is required for this implementation slice.

## Prior Deliberations

- `DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE` - owner directive to make Ollama Qwen the active full-capability LO target.
- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` - owner directive to complete Ollama bridge integration.
- `DELIB-20260895` - owner selected Codex Prime Builder and Ollama Loyal Opposition for the single-harness replacement operating mode while Claude Code and Antigravity were offline.
- `DELIB-20260898` - owner clarified that suspended harnesses are not default-role targets but may still participate in GT-KB work.
- `DELIB-20260679` - owner clarified Ollama should be the target for LO work dispatched via the bridge.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files remain the role handoff and verdict authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposal links governing specs before work begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports and verification must map claims to spec-derived tests.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation occurs under an active project authorization envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH scopes allowed mutations and forbidden actions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner directive and route change are preserved as durable artifacts.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` - Ollama is an adopted GT-KB harness target.
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - `.ollama/routing.toml` is the routing authority for Ollama models and skills.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - dispatch readiness must ensure the route exposes tools required for the assigned work.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - Ollama-authored bridge artifacts require author metadata.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - adopted harnesses must advertise identity, routing, and tool behavior.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - roles attach to harness IDs rather than vendors or transient sessions.
- `GOV-SESSION-ROLE-AUTHORITY-001` - durable role assignment remains the authority for session role resolution.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation stays inside the GT-KB root boundary.

## Target Paths

- `.ollama/routing.toml`
- `scripts/ollama_harness.py`
- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_ollama_routing_config.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `bridge/gtkb-ollama-qwen-full-lo-route-*.md`
- `bridge/INDEX.md` entry for this thread only

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add secrets or credential-bearing values; retain model identifiers and local relative paths only. | Bridge helper credential scan plus review of `.ollama/routing.toml` and Python diffs for token or key literals. |  |
| CQ-PATHS-001 | Yes | Keep all mutations under `E:\GT-KB` and use existing project-relative path handling. | Bridge preflights plus focused tests that load repo-local routing and harness paths. |  |
| CQ-COMPLEXITY-001 | Yes | Keep the change to route selection, one compact prompt builder, and readiness constants without adding a new dispatcher layer. | Focused code review and unit tests for prompt injection and routing behavior. |  |
| CQ-CONSTANTS-001 | Yes | Centralize the required full LO tool set and route names in the existing routing and readiness surfaces. | Tests assert active bridge-review and verification routes use `qwen3-coder-next-cloud` and expose the expected tool names. |  |
| CQ-SECURITY-001 | Yes | Preserve the guard adapter for Write, Edit, and Bash and avoid credential lifecycle or production actions. | Existing and added harness tests cover guard adapter behavior; live readiness validates configured tool exposure. |  |
| CQ-DOCS-001 | Yes | Record rationale and evidence in the bridge proposal and implementation report; keep runtime prompt text compact and role-specific. | Loyal Opposition review plus implementation report inspection. |  |
| CQ-TESTS-001 | Yes | Add or update focused pytest coverage for routing, prompt injection, readiness, and dispatch validation. | Run targeted pytest for Ollama harness, routing config, and dispatch verifier tests. |  |
| CQ-LOGGING-001 | N/A | No logging behavior is changed by this slice. | Review confirms no new log sink or log format is introduced. | Existing stdout and stderr behavior is retained. |
| CQ-VERIFICATION-001 | Yes | Run bridge preflights, focused pytest, ruff check, ruff format check, and live readiness verification. | Capture exact commands and results in the post-implementation report. |  |

## Implementation Plan

1. Update `.ollama/routing.toml` so `bridge-review` and `verification` resolve to `qwen3-coder-next-cloud`; keep implementation on Qwen.
2. Leave the Kimi model row as non-active inventory unless focused tests show removal is cleaner; no active LO skill route should target Kimi after this slice.
3. Add a compact bridge-role system context in `scripts/ollama_harness.py` for `bridge-review` and `verification`. The context will identify Ollama harness D as Loyal Opposition, direct it to read `bridge/INDEX.md`, follow the file bridge protocol, use guarded tools to write the next bridge verdict artifact and update `bridge/INDEX.md`, and include the required author metadata values.
4. Preserve the existing guard adapter for mutating tools so full tool exposure remains governed rather than unrestricted.
5. Update `scripts/verify_ollama_dispatch.py` so readiness for Ollama LO dispatch requires `Read`, `Write`, `Edit`, `Grep`, `Glob`, and `Bash`.
6. Add focused tests for route selection, system context injection, full LO tool readiness, and preserved guard behavior.

## Spec-To-Test Mapping

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`: `platform_tests/scripts/test_ollama_routing_config.py` asserts bridge-review and verification route to `qwen3-coder-next-cloud`.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: `platform_tests/scripts/test_verify_ollama_dispatch.py` and live `scripts/verify_ollama_dispatch.py --readiness-only --json` assert the full LO tool set is present.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: `platform_tests/scripts/test_ollama_harness.py` asserts bridge context includes required Ollama author metadata guidance.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: Ollama smoke review must write a bridge verdict artifact and `bridge/INDEX.md` entry through guarded tools.
- `GOV-HARNESS-ROLE-PORTABILITY-001` and `GOV-SESSION-ROLE-AUTHORITY-001`: Registry remains Codex A Prime Builder and Ollama D Loyal Opposition; route change does not alter durable harness identity semantics.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: Preflights and git diff inspection verify target paths stay within `E:\GT-KB`.

## Acceptance Criteria

- Active Ollama `bridge-review` and `verification` skills resolve to `qwen3-coder-next-cloud`.
- The active LO route exposes all six guarded tools: `Read`, `Write`, `Edit`, `Grep`, `Glob`, and `Bash`.
- Ollama bridge-review and verification invocations receive compact Loyal Opposition bridge context before the user prompt.
- Live readiness succeeds for the active Ollama LO route.
- Focused pytest, ruff check, and ruff format check pass for changed files.
- A Qwen smoke review can use `scripts/ollama_harness.py --model qwen3-coder-next-cloud --skill bridge-review` to write a bridge verdict artifact through the governed tool path.

## Risk And Rollback

The main risk is giving a cloud Ollama model mutating tools before the prompt context is strong enough to produce compliant verdict files. The guard adapter limits filesystem writes, credential exposure, and implementation-start behavior, and the smoke review is intentionally performed before considering the route operational. Rollback is to restore `bridge-review` and `verification` to the prior Kimi read/search route and return readiness to read/search-only while preserving the failed evidence for follow-up.

## Out Of Scope

- Changing durable harness identity values.
- Restoring Claude Code or Antigravity as active role targets.
- Adding production deployment behavior.
- Changing credential lifecycle handling.
- Creating files outside `E:\GT-KB`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
