REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive; approval_policy=never; reasoning_effort not exported by local environment

# Implementation Proposal REVISED - Phase 3 gap 02: harness and model configuration truth

bridge_kind: prime_proposal
Document: gtkb-headless-dispatch-model-pinning
Version: 003
Date: 2026-07-02 UTC
Responds to: bridge/gtkb-headless-dispatch-model-pinning-002.md (NO-GO)

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING-ABD
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4964

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth.db", "harness-state/harness-registry.json", ".api-harness/routing.toml", "config/dispatcher/rules.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Revise the WI-4964 proposal after LO NO-GO `bridge/gtkb-headless-dispatch-model-pinning-002.md` by replacing the Prior Deliberations placeholder with concrete decision citations and expanding the model-pinning scope to include Ollama/D. Headless dispatch identity must be explicit and truthful for Claude Code/B, Codex/A, and Ollama/D:

- Claude Code/B headless Loyal Opposition dispatch uses `claude-opus-4-8` with max effort.
- Codex/A headless Prime Builder dispatch uses `gpt-5.5` with `model_reasoning_effort="xhigh"`.
- Ollama/D headless Loyal Opposition dispatch explicitly selects the Ollama cloud model `deepseek-v4-pro:cloud`, equivalent to `ollama run deepseek-v4-pro:cloud` and the owner-supplied Ollama Python API example.

No separate work item is needed: `WI-4964` already covers UI model labels, headless dispatch routes, provider shim routing, harness registry entries, and owner-visible model identity drift.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4964` and keeps the bridge, expanded project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Requirements are sufficient for filing this revised proposal. The original owner decision and PAUTH covered A/B; the owner then provided an Ollama-specific model directive and authorized creating additional WI scope if necessary. Because `WI-4964` already includes provider-shim routing and harness/model configuration truth, the correct governance move is not a new WI but an expanded A/B/D project authorization: `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING-ABD`.

## Current State Evidence

- Claude Code/B registry headless argv currently contains the Claude CLI, prompt argument placeholder, project-root add-dir, and JSON output, with no explicit model or effort selector.
- Codex/A registry headless argv currently contains `codex exec`, `approval_policy="never"`, prompt placeholder, and project-root working directory, with no explicit model or reasoning effort override.
- Ollama/D registry headless argv currently invokes `scripts/ollama_harness.py` with prompt placeholder and `--skill bridge-review`, with no explicit model route selector.
- `.api-harness/routing.toml` currently has `routing.ollama.default_model = "kimi-k2-7-code-cloud"` and `routing.ollama.skills.bridge-review = "kimi-k2-7-code-cloud"`.
- A resolver check of `scripts.ollama_harness.load_routing_config` plus `resolve_model(..., skill="bridge-review")` returned route key `kimi-k2-7-code-cloud` and model id `kimi-k2.7-code:cloud`.
- `.api-harness/routing.toml` also contains an OpenRouter route `deepseek-v4-pro` with model id `deepseek/deepseek-v4-pro`; that is not the Ollama D route selector required by the owner.
- Dispatcher budget/status metadata currently reports A as `gpt-5-codex`, B as `claude-code`, and D as `kimi-k2-7-code-cloud`.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/harness_ops.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/tests/test_harness_ops.py`, `platform_tests/groundtruth_kb/cli/test_harness_cli.py`, `platform_tests/scripts/test_verify_ollama_dispatch.py`, `groundtruth.db`, `harness-state/harness-registry.json`, `.api-harness/routing.toml`, and `config/dispatcher/rules.toml`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - requires semantically equivalent and truthful harness behavior across dispatch surfaces.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs centralized headless bridge dispatch and selected target behavior.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires dispatcher state/config to be read through governed control surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - keeps Codex-side hook/dispatch parity evidence explicit where Codex uses helper-mediated paths.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform dispatch configuration work out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - preserves tracked work-item and project linkage for future follow-through.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - captures owner decisions and implementation intent as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - classifies owner model-selection directives and proposal revisions as durable artifact triggers.

## Prior Deliberations

- `DELIB-202665197` - owner authorization for the HARNESS-EQUIVALENCE-PHASE-3 umbrella planning and child work-item creation, including `WI-4964` as gap 02.
- `DELIB-20260702-HEADLESS-DISPATCH-MODEL-PINNING` - owner directive for Prime Builder to determine headless model-selection mechanisms, file implementation proposals, and update Claude Code/B and Codex/A headless dispatch model/effort settings.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - owner directive that Ollama harness dispatch should use `deepseek-v4-pro:cloud`, equivalent to `ollama run deepseek-v4-pro:cloud` and the owner-supplied Ollama Python API example.
- `bridge/harness-equivalence-phase-3-umbrella-002.md` - GO verdict for the Phase 3 umbrella that created `WI-4964` as the harness/model configuration truth gap.
- `bridge/gtkb-headless-dispatch-model-pinning-002.md` - LO NO-GO requiring concrete Prior Deliberations citations before approval.

## Owner Decisions / Input

- `DELIB-20260702-HEADLESS-DISPATCH-MODEL-PINNING` - direct A/B model-pinning mandate.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - direct D/Ollama model selector mandate.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING-ABD` - active project authorization covering A/B/D model route pinning under `WI-4964`.

## Proposed Scope

- Add or use a narrow canonical `gt harness` command/API path for updating an existing harness `invocation_surfaces` JSON from the MemBase harnesses table without changing role, lifecycle status, identity, reviewer precedence, dispatch eligibility, or unrelated capability fields.
- Use the canonical harness writer/projection path to pin Codex/A headless dispatch to `codex exec --model gpt-5.5 -c model_reasoning_effort="xhigh"`, preserving `approval_policy="never"`, prompt placeholder, and project-root working directory.
- Use the canonical harness writer/projection path to pin Claude Code/B headless dispatch to the Claude CLI with model `claude-opus-4-8`, max effort, prompt placeholder, project-root add-dir, and JSON output.
- Add an Ollama-provider route key, expected to be `deepseek-v4-pro-cloud`, in `.api-harness/routing.toml` whose `model_id` is exactly `deepseek-v4-pro:cloud`, `provider = "ollama"`, tool calling is supported, and bridge tools remain allowed.
- Use the canonical harness writer/projection path to make Ollama/D headless dispatch pass `--model deepseek-v4-pro-cloud` in addition to `--skill bridge-review`, so D explicitly selects the owner-required route instead of relying on the current Kimi default.
- Keep the existing OpenRouter route `deepseek-v4-pro` / `deepseek/deepseek-v4-pro` intact for OpenRouter/F unless a separate authorization changes that provider path.
- Align dispatcher budget/status model labels for A, B, and D so owner-visible dispatch status matches actual headless CLI/provider route identity: `gpt-5.5`, `claude-opus-4-8`, and `deepseek-v4-pro-cloud` or `deepseek-v4-pro:cloud` consistently documented.
- Preserve dispatcher eligibility topology: no role changes, no `can_receive_dispatch` changes, no reviewer-precedence changes, no provider credentials, no production deployment, and no external account settings.

## Cross-Harness Disposition

This proposal intentionally touches harness surfaces for Codex/A, Claude/B, and Ollama/D. Cursor/E, Antigravity/C, and OpenRouter/F are excluded except for read-only comparison evidence. OpenRouter/F already has an OpenRouter-style DeepSeek V4 Pro route; this proposal must not conflate that provider route with the owner-required Ollama cloud slug `deepseek-v4-pro:cloud`. The transient Cursor UI report observed during this session is not in this implementation scope because dispatcher state showed Cursor/E not selected, no live Cursor worker, and the active suspect was Claude Desktop's external `cursortouch.windows-mcp` extension process tree rather than GT-KB headless dispatch.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify A/B/D model identity is explicit in headless dispatch routes and owner-visible status; add focused tests for harness invocation-surface updates and Ollama route resolution. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run `gt bridge dispatch config --json` and inspect selected headless-capable A/B/D route metadata after the update. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Use `gt bridge dispatch config/status/health --json` rather than cached reports or ad hoc aggregate queue files for dispatch status evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Before implementation, acquire a live GO work-intent claim and implementation-start packet for `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING-ABD`; keep mutations within listed target paths and forbidden operations. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must cite the GO and work-intent claim. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, work item, `target_paths`, and status-bearing numbered bridge chain remain valid. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Confirm all governing specs cited here are live and relevant before implementation report filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must list focused test names and command output for harness update, projection refresh, dispatcher config, and Ollama model-route resolution. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Verify the Codex helper-mediated proposal path and Codex headless argv preserve existing no-approval dispatch behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm no `applications/` or Agent Red files are targeted. |
| `GOV-STANDING-BACKLOG-001` | Confirm no additional WI is created because `WI-4964` already covers provider-shim routing and model identity drift. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm the Ollama owner directive is preserved as `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the revised proposal cites the triggering owner decisions and NO-GO artifact. |

## Acceptance Criteria

- Harness projection output shows A headless argv containing `--model gpt-5.5` and `-c model_reasoning_effort="xhigh"` while preserving `approval_policy="never"`.
- Harness projection output shows B headless argv containing `--model claude-opus-4-8` and `--effort max` while preserving JSON output and project-root add-dir.
- Harness projection output shows D headless argv invoking `scripts/ollama_harness.py` with `--skill bridge-review` and explicit `--model deepseek-v4-pro-cloud` or the selected canonical route key for `deepseek-v4-pro:cloud`.
- `.api-harness/routing.toml` contains an Ollama-provider route whose `model_id` is exactly `deepseek-v4-pro:cloud`, and `routing.ollama.skills.bridge-review` resolves to that route unless D argv explicitly selects it and tests prove the explicit selector wins.
- A resolver check of `scripts.ollama_harness.load_routing_config` plus `resolve_model(..., requested_model=<D route>, skill="bridge-review")` returns model id `deepseek-v4-pro:cloud`.
- `gt bridge dispatch config --json` reports A/B/D budget/status model identity matching the pinned route names.
- Focused tests cover the invocation-surface update path, projection refresh, dispatcher config model labels, and Ollama route resolution without changing harness roles, status, reviewer precedence, or dispatch eligibility.

## Risks / Rollback

Risk is moderate because the implementation mutates canonical MemBase harness records, generated projections, provider route config, dispatcher metadata, and focused tests. The highest-risk confusion is provider identity: Ollama D must use `deepseek-v4-pro:cloud`, while OpenRouter F may continue to use `deepseek/deepseek-v4-pro`.

Rollback is a revert of source/config/test/projection changes plus a canonical harness-record version that restores prior A/B/D headless argv values if needed. Bridge files, project authorization records, and deliberation records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/harness_ops.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_harness_ops.py`
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `groundtruth.db`
- `harness-state/harness-registry.json`
- `.api-harness/routing.toml`
- `config/dispatcher/rules.toml`

## Recommended Commit Type

`feat`
