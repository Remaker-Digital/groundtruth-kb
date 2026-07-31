REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder session; runtime reasoning profile not exposed

# Implementation Proposal Revision - Codex headless write boundary

bridge_kind: prime_proposal
Document: gtkb-wi4985-codex-headless-write-boundary
Version: 003
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4985-codex-headless-write-boundary-002.md

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4985

target_paths: ["harness-state/harness-registry.json", "groundtruth.db", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_verify_codex_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder revises WI-4985 after the NO-GO at `-002`. The accepted diagnosis remains unchanged: Codex A headless Prime Builder dispatch pins `gpt-5.5`, `approval_policy="never"`, and `model_reasoning_effort="xhigh"`, but lacks a write-capable project-root sandbox selector. Under noninteractive `approval_policy=never`, that makes authorized in-root `apply_patch` writes fail before mutation.

The revision completes Prior Deliberations and replaces generic verification filler with concrete tests for the load-bearing behavior: the headless argv must keep the model/reasoning/approval pins and add the write-capable sandbox/root mode, with an in-root write smoke performed only through a governed dispatcher-mediated path after GO.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202665265` authorizes the bridge-stability repair goal using Claude/Ollama as LO and Codex as PB. `WI-4985` scopes the Codex headless write-boundary blocker. No new requirement is needed before implementation.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `harness-state/harness-registry.json`, `groundtruth.db`, `platform_tests/groundtruth_kb/cli/test_harness_cli.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `scripts/verify_codex_dispatch.py`, and `platform_tests/scripts/test_verify_codex_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Codex PB headless launch must remain a dispatcher-owned invocation surface, not a direct harness fallback.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, implementation, and verification must remain tied to live bridge state and numbered files.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner authorization, work item, proposal, tests, and report remain traceable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve the artifact graph from owner directive through MemBase and bridge verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal updates a NO-GO thread through REVISED rather than silently replacing history.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification links are present and mapped to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute tests derived from this proposal's linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target-path metadata are present.
- `SPEC-AUQ-POLICY-ENGINE-001` - PAUTH/owner-decision evidence must be honored for the bounded implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes stay in GT-KB platform state/source/tests, outside adopter app scope.
- `GOV-STANDING-BACKLOG-001` - WI-4985 remains the MemBase backlog authority for this blocker.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hooks/headless behavior are live enforcement surfaces and must stay compatible with the Windows Codex hook boundary.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must begin only from a valid GO-derived authorization packet.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - target paths and mutation classes must remain within the bounded project authorization.

## Prior Deliberations

- `DELIB-202665265` - owner authorization for the headless bridge-stability goal: keep testing/fixing until Claude/Ollama LO and Codex PB process work headlessly without intervention.
- `WI-4977` - dispatch-stability work item, now resolved, that exposed the live bridge/dispatcher reliability context in which WI-4985 was found.
- `bridge/gtkb-headless-dispatch-model-pinning-006.md` - VERIFIED model-pinning predecessor; this proposal must preserve Codex `gpt-5.5`, `approval_policy="never"`, and `model_reasoning_effort="xhigh"` while adding write capability.
- `WI-4986` / `bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md` - sibling timer fix needed before long-running headless dispatch can be trusted.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - prior decision that Codex hooks are a live Windows interception boundary for modern Codex CLI and must fail closed on regression.
- Deliberation Archive search noted by LO for `"codex headless dispatch write boundary sandbox apply_patch"` returned no direct matches; the records above are adjacent governing history rather than direct prior acceptance of this sandbox change.

## Owner Decisions / Input

- `DELIB-202665265` - owner authorization for bridge-stability repair, including Codex as active Prime Builder headless dispatch target.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY` - active project authorization covering WI-4985.

## Findings Addressed

### N1 - Prior Deliberations placeholder

Response: corrected. The revision replaces the placeholder with concrete adjacent and governing records: `DELIB-202665265`, WI-4977, the VERIFIED model-pinning thread, sibling WI-4986, and `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. It also preserves the LO search result that found no direct DA matches for the exact write-boundary topic.

### N2 - Generic verification plan and auto-attached spec links

Response: corrected. The verification plan below maps each retained spec to concrete checks. The load-bearing tests are: Codex argv contains the write-capable sandbox selector and still contains the model/reasoning/approval pins; the static readiness script fails closed on the old no-sandbox form; a dispatcher-mediated in-root write smoke succeeds after GO; and implementation authorization constrains the registry/groundtruth/test mutation classes.

## Revised Scope

- Update the MemBase-backed Codex A headless invocation surface and regenerate `harness-state/harness-registry.json` through governed harness/projection plumbing. Do not hand-edit dispatcher rules or runtime state.
- Preserve existing Codex headless pins: `--model gpt-5.5`, `approval_policy="never"`, and `model_reasoning_effort="xhigh"`.
- Add the required project-root write-capable sandbox/root selector for noninteractive in-root edits. The selected argument must be static-testable and compatible with `codex exec`.
- Extend readiness verification so `scripts/verify_codex_dispatch.py` reports failure when the write-capable selector is absent or the model/reasoning/approval pins regress.
- Add focused tests for harness CLI/projection regeneration and dispatcher runtime command composition.
- After GO and implementation, run any live write smoke only through the governed dispatcher/control-plane path, not by directly spawning a Codex worker from an interactive harness.

## Pre-Filing Preflight Subsection

Candidate preflights will be run against this completed revision body before live filing through `.codex/skills/bridge/helpers/revise_bridge.py file`:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4985-codex-headless-write-boundary --content-file <candidate> --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4985-codex-headless-write-boundary --content-file <candidate>`

Observed result before filing:

- Applicability preflight exit 0, `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:6faf5c556a80f809142de19db044db99c952a90ef9f09e31afc022427cdcd96c`.
- Clause preflight exit 0; must_apply 4, evidence gaps 0, blocking gaps 0.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher-runtime test asserts Codex PB command composition comes from the registered headless invocation surface and includes the write-capable selector plus `--cd {{PROJECT_ROOT}}`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live bridge preflights pass; implementation starts only from a GO-derived authorization packet and reports through the same bridge thread. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report ties `DELIB-202665265`, WI-4985, model-pinning predecessor, tests, and verification together. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Changed-file and report evidence preserve the owner directive -> WI -> proposal -> tests -> report -> verification graph. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Revision uses the existing NO-GO -> REVISED lifecycle and implementation report preserves that chain. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight passes with no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this spec-to-test map and executes the focused tests before requesting VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal metadata and target paths are present and pass bridge compliance. |
| `SPEC-AUQ-POLICY-ENGINE-001` | PAUTH/owner-decision evidence is cited and implementation authorization is validated before mutation. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and changed-file evidence stay under `E:\GT-KB` platform paths and outside adopter application scope. |
| `GOV-STANDING-BACKLOG-001` | Implementation report references WI-4985 as the backlog authority and does not create a duplicate work item. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Focused readiness/static tests assert Codex hook/headless configuration remains compatible with the live Codex CLI hook boundary. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4985-codex-headless-write-boundary` succeeds before protected mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Tests or implementation report evidence show mutations are limited to the PAUTH target paths/classes. |

## Acceptance Criteria

- Codex A headless argv contains `--model gpt-5.5`, `approval_policy="never"`, `model_reasoning_effort="xhigh"`, a project-root selector, and a write-capable sandbox/root argument.
- Focused harness CLI/projection, dispatcher runtime, and Codex readiness tests fail closed if the invocation regresses to the old no-sandbox form.
- A bounded dispatcher-mediated smoke after GO can launch Codex A for an authorized in-root edit without the previous `apply_patch` outside-project rejection.
- The implementation does not add any direct harness-to-harness fallback launch path.

## Risk And Rollback

Risk is moderate because an overly broad sandbox could weaken noninteractive safety. The implementation must choose the narrowest write-capable mode that allows approved in-root edits and keep bridge authorization gates intact.

Rollback is a revert of the source/state/test changes plus regeneration of the harness projection from the previous MemBase invocation state. Bridge files and PAUTH/deliberation evidence are append-only and must not be deleted.

## Files Expected To Change

- `harness-state/harness-registry.json`
- `groundtruth.db`
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

## Recommended Commit Type

`feat`
