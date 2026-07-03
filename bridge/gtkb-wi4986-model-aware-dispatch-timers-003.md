REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder session; runtime reasoning profile not exposed

# Implementation Proposal Revision - Model-aware dispatch timers

bridge_kind: prime_proposal
Document: gtkb-wi4986-model-aware-dispatch-timers
Version: 003
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4986-model-aware-dispatch-timers-002.md

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4986-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4986

target_paths: [".api-harness/routing.toml", "scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/run_with_status.py", "scripts/ollama_harness.py", "scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder revises WI-4986 after the NO-GO at `-002`. The revision keeps the original objective, but makes the load-bearing defect explicit: the implementation must not merely define larger timer values; it must prove that the resolved harness/model/config lifetime is actually passed into the live `run_with_status.py` worker wrapper for every dispatcher launch path.

This proposal also incorporates the owner's later directive that timer policy must be per harness/model/config, begin generously, collect elapsed-time telemetry, and tighten only after enough observations support high-confidence hung/failed classification.

## Requirement Sufficiency

Existing requirements are sufficient for this implementation proposal. The owner directives captured in `DELIB-202665303`, `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`, and `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` specify the timer behavior and evidence standard. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` governs dispatcher-owned spawning. No new requirement is needed before implementation.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.api-harness/routing.toml`, `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `scripts/run_with_status.py`, `scripts/ollama_harness.py`, `scripts/verify_ollama_dispatch.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`, `platform_tests/scripts/test_ollama_harness.py`, and `platform_tests/scripts/test_verify_ollama_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher is the single service that resolves recipients, composes headless commands, launches workers, and records audit evidence; the timer fix belongs in that launch/audit path.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher-owned spawn architecture; the fix must preserve daemon/control-plane ownership rather than adding harness-to-harness fallback launches.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch packet/worker metadata must stay coherent while adding elapsed-time and model-profile telemetry.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, implementation report, and eventual verification must use live bridge state and versioned bridge files.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner directives about timer behavior and hung-confidence thresholds are preserved as deliberations and tied to WI-4986.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation must maintain the artifact graph from owner directive to deliberation, work item, proposal, tests, implementation report, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the WI-4987 duplicate/supersession and eventual WI-4986 implementation lifecycle must remain explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specs and maps verification to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must be verified by tests derived from the linked specifications, not by a green status claim alone.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project id, work item id, and target paths are present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes are platform dispatcher changes under `E:\GT-KB`, not adopter-application changes.
- `GOV-STANDING-BACKLOG-001` - WI-4986 is the MemBase work item receiving the superseded WI-4987 timer directive.

## Prior Deliberations

- `DELIB-202665303` - owner directive: per-harness timers, generous first, verify the configured lifetime reaches the worker, keep storm watchdog guards, and tighten after experience.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - owner directive to start with very generous allowances until telemetry exists.
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` - owner directive to collect/analyze elapsed-time data by harness, model, and configuration before high-confidence hung/failed classification.
- `DELIB-20266203` - prior autonomous-loop clarification that introduced generous per-role worker lifetime caps, including roughly 30 minutes for Loyal Opposition review and 90 minutes for Prime Builder implementation.
- `WI-4845` / `bridge/gtkb-wi4845-daemon-worker-lifetime-override-004.md` - verified predecessor that made the 600 second `run_with_status.py` default configurable for daemon-launched workers.
- `WI-4977` - resolved dispatch-stability item covering duplicate dispatch, exact bridge-slug status lookup, and success-after-verdict handling.
- `WI-4987` - duplicate backlog capture resolved in favor of WI-4986; its status detail records the same root symptom: Claude Opus 4.8 Max was falsely timed out at the 600 second default even though a longer LO lifetime was expected.

## Owner Decisions / Input

- `DELIB-202665303` - latest governing design directive for this revision.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - owner acceptance of generous initial allowances.
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` - owner requirement for elapsed-time telemetry and confidence analysis.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4986-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering WI-4986.

## Findings Addressed

### N1 - Root cause: lifetime value not reaching worker

Response: in scope. The implementation must add a regression that inspects the exact `wrapped_command` used by `dispatcher_runtime._spawn_harness` and asserts the resolved profile lifetime is included as `--lifetime <seconds>` before the `run_with_status.py` status path and before the headless harness command. The implementation must cover at least Claude B / Opus 4.8 Max, Ollama D / DeepSeek V4 Pro cloud, and Codex A / GPT-5.5. It must also record effective lifetime/profile metadata in the run evidence so health reports can distinguish "configured value missing" from "worker exceeded configured value."

The implementation must diagnose stale-daemon/launch-path bypass explicitly. If the dispatcher daemon uses an old imported runtime, or a path bypasses `_spawn_harness`, health/status must surface that as stale runtime or launch-path drift rather than letting `run_with_status.py` silently fall back to 600 seconds.

### N2 - Prior deliberations placeholder and missing latest owner directive

Response: corrected. This revision replaces the placeholder with concrete prior deliberations and cites `DELIB-202665303`, the two Codex-captured timer deliberations, `DELIB-20266203`, WI-4845, WI-4977, and the WI-4987 duplicate/supersession evidence.

### N3/N4 - Generic verification plan and uncurated spec links

Response: corrected. The link set is limited to dispatcher, bridge, proposal, verification, placement, backlog, and artifact-governance constraints that directly govern this implementation. The verification plan below maps each spec to concrete tests or preflight evidence.

## Revised Scope

- Replace per-role-only effective lifetime selection with per-harness/model/config profile resolution for dispatched workers. Defaults must start generously: Claude B Opus 4.8 Max must have an allowance comfortably above normal 15-30 minute reviews; Ollama D DeepSeek V4 Pro cloud must have a review allowance suitable for bridge reviews; Codex A GPT-5.5 PB work must retain a generous implementation allowance.
- Keep per-role and global storm guards, work-intent claims, leases, and dispatch concurrency caps as runaway controls. Larger lifetimes must not reopen the dispatch-storm class.
- Ensure the resolved profile lifetime reaches `run_with_status.py` in the live wrapped command for dispatcher-daemon launches and any dispatcher control-plane launch path.
- Record dispatch telemetry sufficient for later threshold analysis: harness id, harness type, role, model id, model configuration/effort where available, selected bridge documents, dispatch id, start/end timestamps or elapsed seconds, configured lifetime seconds, effective timeout source, exit code, failure class, and whether a bridge verdict/report artifact was produced before process exit.
- Raise or parameterize the Ollama DeepSeek V4 Pro route/session budget so `ollama run deepseek-v4-pro:cloud` is not treated as a short 180 second fast-fail review path.
- Add health/report classification that distinguishes process death, provider failure, invalid output, configured timeout exceeded, and missing/unstamped lifetime wiring. Do not classify a live worker as hung merely because it exceeds a generic short timer.

## Pre-Filing Preflight Subsection

Candidate preflights were run against this completed revision body before live filing through `.codex/skills/bridge/helpers/revise_bridge.py file`:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4986-model-aware-dispatch-timers --content-file <candidate> --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4986-model-aware-dispatch-timers --content-file <candidate>`

Observed result before filing:

- Applicability preflight exit 0, `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:9292d6a388fed11aa68d2def6b328b0d464bcc87f2a6440afb34070fb5b77952`.
- Clause preflight exit 0; must_apply 4, evidence gaps 0, blocking gaps 0.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `platform_tests/scripts/test_dispatcher_runtime.py` and/or `test_dispatcher_runtime_work_intent.py` assert per-harness/model lifetime resolution, exact `--lifetime` placement in the wrapped command, and preserved dispatcher-owned spawn/audit behavior. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Focused tests prove no direct harness fallback path is introduced; all automated worker launches remain inside dispatcher runtime/control-plane code. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Tests assert dispatch run metadata includes role, harness id, selected documents, configured lifetime, profile source, and elapsed-time/failure fields without breaking existing packet fields. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live bridge preflights pass; implementation report must cite this proposal and preserve the bridge version chain. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report cites the timer deliberations and WI-4987 supersession so the owner directives remain durable and traceable. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation report demonstrates the artifact graph from owner directive to deliberation, WI-4986, tests, report, and verification remains intact. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation report preserves the WI-4987 duplicate/supersession lifecycle and does not create parallel backlog authority. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight passes with no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must map each linked spec to executed test evidence before requesting VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal metadata lines and `target_paths` remain present and pass bridge compliance. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests and changed-file list show all implementation paths remain under the GT-KB platform root and outside adopter app scope. |
| `GOV-STANDING-BACKLOG-001` | Implementation report references WI-4986 as the active work item and explains WI-4987 as resolved duplicate provenance, without creating a second backlog authority. |

## Acceptance Criteria

- A unit test proves the effective lifetime for Claude B / Opus 4.8 Max reaches `run_with_status.py` as the configured value, not the 600 second default.
- A unit test proves the effective lifetime for Ollama D / DeepSeek V4 Pro cloud reaches `run_with_status.py` and its route/session budget is not the short 180 second review budget.
- A unit test proves Codex A / GPT-5.5 PB dispatch keeps a generous PB implementation allowance.
- Dispatcher run metadata records elapsed time and configured lifetime by harness/model/config and role.
- Health/report output does not declare a worker hung before its profile allowance expires unless there is explicit process death, provider failure, invalid output, or missing lifetime-wiring evidence.
- Existing dispatcher storm controls remain active: global cap, per-role cap, work-intent/lease controls, and provider-failure backoff still prevent runaway launches.

## Risk And Rollback

Risk is moderate because this touches worker launch lifetimes, dispatch health classification, route budgets, and telemetry. The main failure mode is accidentally making worker lifetimes generous without retaining concurrency and lease controls; the implementation must preserve those guards and test them.

Rollback is a revert of the source/config/test changes. Bridge files, deliberations, work-item history, and PAUTH records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/run_with_status.py`
- `scripts/ollama_harness.py`
- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

## Recommended Commit Type

`feat`
