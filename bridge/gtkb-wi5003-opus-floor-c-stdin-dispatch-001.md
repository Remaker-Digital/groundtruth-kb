NEW

# Defect-Fix Proposal - WI-5003 Opus-Class Timer Floor And C Stdin Dispatch

bridge_kind: prime_proposal
Document: gtkb-wi5003-opus-floor-c-stdin-dispatch
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Desktop interactive; ::init gtkb pb; active goal headless bridge stability; no direct harness-to-harness launch

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5003-OPUS-FLOOR-C-STDIN
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5003

target_paths: ["scripts/dispatcher_runtime.py", ".api-harness/routing.toml", "harness-state/harness-registry.json", "groundtruth.db", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

implementation_scope: source, configuration, harness-registry, kb-state, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Claim

Fix the remaining live headless-dispatch launch defect for harness C and align dispatch timers with the owner's updated evidence standard: every harness/model/config starts with an Opus-class worker window until GT-KB has at least 20 profile-specific example runs and quality/elapsed-time analysis sufficient to refine the threshold at 95% confidence.

This proposal does not authorize direct harness-to-harness fallback, manual standby launches, credential mutation, production deployment, or broad dispatcher redesign.

## Defect / Reproduction

Live dispatcher metadata for `loyal-opposition:C` shows the C launch failed before process start:

```text
dispatch_id: 2026-07-03T21-55-17Z-loyal-opposition-C-a3cdc1
error_type: FileNotFoundError
error_message: [WinError 206] The filename or extension is too long
command_head: user-local agy executable --print
primary_bridge_id: gtkb-role-authority-boundary-implementable-correction
worker_lifetime_seconds: 1800
worker_lifetime_source: role_default:loyal-opposition
worker_lifetime_model_hint: Gemini 3.5 Flash (High)
```

The runtime already supports stdin prompt transport for long prompts. `platform_tests/scripts/test_dispatcher_runtime.py::test_antigravity_stdin_dispatch_removes_prompt_from_child_argv` passes and proves that a headless surface with `stdin: true` removes the prompt payload from the child argv while preserving ordinary flags. The live C registry surface, however, currently stores the full `{{PROMPT}}` token in argv without `stdin` or `prompt_transport: stdin`, so Windows receives the entire bridge prompt in the command line and returns WinError 206.

The same launch metadata shows C inherited the 1800-second Loyal Opposition role fallback. WI-4986 correctly added harness-aware timers for A/B/D, but its verified state intentionally used B=3600, D=1800, A=5400. The owner has now tightened the policy: assume every harness is as slow as Opus 4.8 until enough evidence says otherwise, then consider reducing per harness+model+config after 20 example runs and quality review.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `.api-harness/routing.toml`, `harness-state/harness-registry.json`, `groundtruth.db`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_verify_antigravity_dispatch.py`, and `platform_tests/scripts/test_verify_ollama_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned headless routing must select runnable targets and compose launch commands that can actually start under the configured OS/process boundary.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch metadata must carry coherent lifetime/profile/elapsed evidence for later hung/failure analysis.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the fix belongs in dispatcher runtime/configured invocation surfaces, not ad hoc harness-to-harness fallback.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the owner has prohibited direct harness interaction; the remedy must keep all automation behind dispatcher control-plane state and registry surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, GO, implementation report, and verification must use the current bridge numbered-file chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specs and target paths before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project id, work item id, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map the owner timer rule and C launch fix to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-5003 was captured in MemBase as the canonical work item for this remaining defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the live operational finding and owner policy refinement are preserved as durable backlog, decision, bridge, source, and test artifacts.

## Prior Deliberations

- `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` - owner decision: use an Opus-class timer floor for all harnesses until 20 profile-specific example runs and quality/elapsed analysis support a 95% confidence refinement.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - prior owner direction to start with generous allowances until telemetry exists.
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` - prior owner direction to decide hung/failure status from harness/model/config elapsed-time evidence.
- `bridge/gtkb-wi4986-model-aware-dispatch-timers-006.md` - VERIFIED model-aware timers; establishes the current A/B/D baseline and telemetry fields but predates the universal Opus-class floor refinement.
- `bridge/gtkb-wi4977-headless-dispatch-stability-008.md` - VERIFIED exact-thread, lease, and Ollama advancement repair; confirms the dispatcher can be stabilized through targeted fixes.
- `bridge/gtkb-wi4991-headless-ineligible-dispatch-suppression-004.md` - VERIFIED suppression of explicit non-headlessable loops; adjacent evidence that dispatcher selection should suppress known unsafe automation without hiding work from manual Prime visibility.

## Owner Decisions / Input

- `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` captures Mike's 2026-07-03 directive that long windows are acceptable to avoid false failures and unnecessary abandonment/re-homing of work, and that window reduction should wait for 20 profile-specific example runs plus quality/evidence review.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5003-OPUS-FLOOR-C-STDIN` authorizes bounded source, test, configuration, harness-registry, KB-state, and bridge work for WI-5003. It forbids direct harness-to-harness launch, credential mutation, and production deployment.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, the verified WI-4986 timer implementation, and the owner-decision DELIB above provide enough constraint detail. No new specification is required before implementation.

## Proposed Scope

1. Update harness C's canonical headless invocation surface through the governed harness registry transaction so the dispatch prompt is transported via stdin, while preserving the existing `agy --print`, `--print-timeout 30m`, `--model "Gemini 3.5 Flash (High)"`, permission, and project-root arguments.
2. Update dispatcher lifetime defaults so Loyal Opposition workers without enough profile evidence receive an Opus-class floor rather than the current 1800-second role fallback. The expected initial floor is 3600 seconds unless implementation discovers a stronger existing constant or rule.
3. Update D/Ollama DeepSeek routing and per-harness lifetime defaults so D is not below the same floor merely because recent runs were faster. Keep explicit model selection for `deepseek-v4-pro:cloud`.
4. Preserve and extend dispatch metadata so each launch continues to record harness id, role, model hint, lifetime seconds, source, elapsed time, timeout source, and selected bridge document. Add or adjust tests so the future 20-run/95%-confidence refinement has usable data.
5. Do not add any direct harness-to-harness launch, standby worker fallback, direct registry file edit, credential change, or production deployment path.

## Specification-Derived Verification Plan

| Specification / Requirement | Planned Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add/update dispatcher runtime tests proving C prompt transport uses `run_with_status.py --stdin`, the prompt is absent from child argv, and ordinary model/project-root flags remain. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Add/update worker-lifetime profile tests proving unknown/LO/C/D profiles receive the Opus-class floor and metadata records the lifetime source. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Verify the fix uses registry/runtime surfaces only; no direct harness launch or fallback command is introduced. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run structural or focused tests over external harness execution boundaries and inspect changed code for no new cross-harness invocation path. |
| Owner `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` | Add test names or assertions documenting that default timers are not lowered below Opus-class floor absent profile-specific evidence; implementation report must discuss the 20-run future refinement trigger. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include exact pytest, ruff lint, and ruff format commands with observed results. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short
python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py
python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py
gt harness show --harness C
gt bridge dispatch status --json
```

## Acceptance Criteria

- Harness C headless dispatch no longer places the full bridge prompt in the child argv and therefore avoids WinError 206 command-line length failure for long bridge prompts.
- Harness C's registry projection and MemBase harness record agree after the governed transaction.
- C, D, and generic Loyal Opposition worker lifetimes are not below the Opus-class floor unless an explicit environment override or future governed telemetry-analysis policy applies.
- D/Ollama retains the explicit DeepSeek V4 Pro cloud model route and no route/session timeout remains below the floor.
- Dispatch launch metadata remains rich enough to support the future 20-run per harness+model+config analysis.
- Tests verify prompt transport, lifetime resolution, route budget, and absence of direct harness-to-harness fallback.

## Risks / Rollback

Risk: `agy --print` may require the prompt as a positional argv argument and may not read stdin in the same way as the runtime's generic stdin transport assumes. Mitigation: preserve `--print-timeout`, model, permission, and project-root flags; test command composition now and, if live launch still fails, file a follow-up to use a temp prompt file or documented CLI-specific stdin flag.

Risk: longer worker windows can waste time on genuine hangs. Mitigation: the owner explicitly prefers reducing false failures and unnecessary work abandonment; the 20-run/95%-confidence refinement rule creates a bounded path to tighten windows once evidence exists.

Risk: changing `groundtruth.db` and `harness-state/harness-registry.json` amid a dirty worktree can complicate sweep commits. Mitigation: use the governed `gt harness set-invocation-surface` transaction, record exact before/after metadata in the implementation report, and keep source/test changes path-scoped.

Rollback: revert the source/test/config changes and use `gt harness set-invocation-surface` to restore C's prior headless surface if needed. Bridge files and Deliberation Archive records are append-only evidence and must not be deleted.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `.api-harness/routing.toml`
- `harness-state/harness-registry.json`
- `groundtruth.db`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_antigravity_dispatch.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

## Recommended Commit Type

`fix`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
