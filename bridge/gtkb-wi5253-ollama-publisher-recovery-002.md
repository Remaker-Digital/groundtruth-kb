REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed bridge proposal filing; reasoning high

# Revised Defect-Fix Proposal - WI-5253 Ollama D Publisher Failure Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5253-ollama-publisher-recovery
Version: 002
Responds to: bridge/gtkb-wi5253-ollama-publisher-recovery-001.md
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5253-OLLAMA-PUBLISHER-RECOVERY-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5253

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

## Claim

Prime Builder proposes a bounded D-only follow-on to the GO-approved WI-5216 semantic recovery design. WI-5253 repairs the post-invocation failure state now exposed by WI-5224: Ollama D invokes `PublishBridgeVerdict`, the governed publisher returns an error or an incomplete result, and the tool loop retries but discards the concrete publisher error when it finally exits.

## Revision Summary

This revision narrows the relationship to predecessor work and adds the missing diagnostic contract:

- WI-5216 remains authoritative for detecting denied raw Write/Edit/Bash bridge-publication intent and entering equivalent F/D semantic recovery. WI-5253 does not reimplement that trigger or modify the cloud loop.
- WI-5224 remains authoritative for preventing a provider completion without a governed verdict.
- WI-5253 begins only after D has invoked `PublishBridgeVerdict` and publication failed or returned no usable `verdict_path`, or after a provider violates the publisher-only recovery schema with a non-publisher call.
- Final failure evidence must preserve a bounded form of the last concrete publisher error, the attempt count, and the recovery reason in the raised diagnostic consumed by dispatcher telemetry.

## Defect / Reproduction

Genuine dispatcher run `2026-07-15T08-05-49Z-loyal-opposition-D-48dcd4` reviewed `gtkb-wi5229-binary-verified-finalizer-hunk-patch` for 326 seconds and 41 turns. It made 60 tool calls, including four `PublishBridgeVerdict` calls, then exited 1 with `stop_reason=no_progress_loop`, zero stdout, and only:

`ollama_harness: repeated bridge verdict publisher failures before completion`

The generic final error omitted the governed publisher's actual result even though `scripts/ollama_harness.py` had already converted it to a model-visible string such as `ERROR: governed bridge verdict publication failed: <reason>`. Earlier genuine D runs also exited on `bridge verdict publisher recovery received non-publisher tool call` without a governed verdict.

Current source evidence:

- `run_tool_loop` catches `OllamaHarnessError` from `dispatch_tool_call` and stores `ERROR: <reason>` in `result`.
- Failed publisher results increment `publisher_failures`, but the exhaustion error contains neither `result` nor the failure count.
- The recovery prompt replaces the concrete result with `PublishBridgeVerdict did not return a verdict_path`.
- A non-publisher call during publisher-only recovery raises immediately, without a bounded corrective turn and without recording the rejected tool name in the final diagnostic.
- Existing repeated-failure coverage asserts only the generic error, so it does not protect diagnostic fidelity.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001`, `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` require governed publication, fail-closed completion, preserved provenance, diagnostic failure evidence, and exact implementation authorization. No new specification is required.

## In-Root Placement Evidence

Both target paths are under `E:\GT-KB`:

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - D must complete governed LO work or produce actionable failure evidence.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - governs D's guarded tool loop and fail-closed publisher path.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - recovered publication must preserve dispatcher session and model provenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - only the governed publisher may append LO verdicts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires mapped deterministic verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires exact scope enforcement at implementation start.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace GO, claim, or implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the live failure through WI, test, proposal, implementation, and verification.

## Prior Deliberations

- `DELIB-202666204` - owner authorization for the WI-5253 governed correction path.
- `DELIB-202666173` - owner directive to correct proof-blocking fleet defects.
- `DELIB-202666171` - governed provider verdict publication context.
- `DELIB-20264376` - prior Ollama dispatch-failure hardening context.
- `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-002.md` - GO-approved parent semantic recovery design.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-005.md` - VERIFIED fail-closed completion predecessor.

## Owner Decisions / Input

- `DELIB-202666204` authorizes the WI-5253 governed proposal and implementation lifecycle.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5253-OLLAMA-PUBLISHER-RECOVERY-20260715` is active for WI-5253 and limits implementation to source/test changes in the two declared paths.

## Proposed Scope

1. Preserve the latest failed publisher result as a bounded diagnostic value. Do not retain unbounded model output or expose credentials.
2. Feed the concrete bounded failure reason, rather than only `did not return a verdict_path`, into the next governed publisher recovery prompt.
3. On publisher-attempt exhaustion, raise a deterministic error containing the attempt count and bounded last failure reason so dispatcher stderr/telemetry explains the failure.
4. If the provider emits a non-publisher call while only `PublishBridgeVerdict` is exposed, do not execute that call. Record its tool name, count it as a bounded recovery failure, issue another publisher-only correction while budget remains, and fail closed with the same diagnostic contract on exhaustion.
5. Preserve success only when the publisher returns a nonblank `verdict_path`; clear retained failure state after success.
6. Keep the implementation D/Ollama-only. Do not add WI-5216 raw-denial detection, alter the shared cloud loop, or absorb WI-5245.

## Explicit Exclusions

- No cloud-provider or H recovery changes; WI-5245 remains separate.
- No implementation of WI-5216 raw Write/Edit/Bash denial detection.
- No direct bridge Write/Edit/Bash mutation or alternate verdict writer.
- No dispatcher eligibility, routing, runtime JSON, lease, lock, credential, deployment, release, push, or history mutation.
- No source/test changes outside the two target paths.
- No reduction of D/F/H turn, operation, session, worker, or lease allowances.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Actionable final diagnostic | Make the publisher raise a stable sentinel such as `claim contention`; after bounded exhaustion assert the raised `OllamaHarnessError` contains the attempt count and sentinel. |
| Concrete recovery prompt | After one failed publisher call, assert the next provider payload contains the bounded concrete failure reason and exposes only `PublishBridgeVerdict`. |
| Non-publisher schema violation | During recovery return a `Read` or `Bash` call; assert it is not dispatched, its name is retained diagnostically, and recovery remains bounded. |
| Governed success | After an initial failure, return a successful publisher result and assert completion requires a nonblank `verdict_path`, retained failure state clears, and canonical publisher delegation is unchanged. |
| Fail-closed behavior | Assert repeated publisher failures and repeated non-publisher recovery calls terminate before the ordinary turn budget and never report a successful final response. |
| Provenance and regression | Run the full focused Ollama harness suite, including existing dispatcher session-id propagation and successful recovery tests. |
| Governance lifecycle | Require GO, matching claim, implementation-start authorization, NEW implementation report, independent LO verification, and focused commit. |

Minimum command set:

- `python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5253-ollama-publisher-recovery --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5253-ollama-publisher-recovery`

## Acceptance Criteria

1. Publisher exhaustion includes the exact bounded attempt count and a bounded form of the last concrete publisher error in the raised diagnostic observed by dispatcher stderr/telemetry.
2. A non-publisher call during publisher-only recovery is never executed and receives at most the configured bounded corrective opportunities before diagnostic failure.
3. A provider completion is never accepted until `PublishBridgeVerdict` returns a nonblank `verdict_path`.
4. Recovery prompts expose only `PublishBridgeVerdict` and include the concrete bounded reason for the previous failure.
5. Successful recovery preserves trusted author/session metadata and clears retained failure state.
6. Existing completion, publisher, guard, timeout, and allowance tests remain green.
7. Changes remain limited to the two declared paths and do not duplicate WI-5216 or WI-5245 scope.

## Risks / Rollback

The main risk is leaking excessive publisher output into prompts or telemetry. Bound and normalize the retained diagnostic and rely on the existing credential-safe governed publisher; do not serialize full exception objects or model content. Another risk is turning malformed non-publisher calls into extra work, so they must never be dispatched and must consume the same small recovery budget.

Rollback reverts only the focused source/test commit. Bridge, PAUTH, work-item, test, dispatch, and verification records remain append-only evidence.

## Files Expected To Change

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`fix`
