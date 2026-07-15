NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed fleet stabilization; reasoning high

# Defect-Fix Proposal - WI-5245 Alibaba H Publisher Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5245-alibaba-publisher-recovery
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5245-H-PUBLISHER-RECOVERY-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5245

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

## Claim

Prime Builder proposes a bounded shared-cloud-loop correction for `WI-5245`. When Alibaba H is in publisher-only recovery, a provider response that violates the advertised schema with a non-`PublishBridgeVerdict` tool call must never execute that call or strand the review with an opaque error. The loop must reject the entire malformed turn, retain a bounded diagnostic reason, offer a bounded publisher-only correction, and either publish a governed verdict or fail closed with actionable dispatcher evidence.

## Defect / Reproduction

Two genuine, substantive Alibaba H Loyal Opposition dispatches reproduced the same failure:

- `2026-07-15T01-59-25Z-loyal-opposition-H-81dc79` reviewed `gtkb-wi5240-wi5236-pauth-registered-vocabulary`.
- `2026-07-15T02-08-50Z-loyal-opposition-H-0fe0a3` reviewed `gtkb-modernization-trust-enforcement-slice`.

Each run made two `PublishBridgeVerdict` attempts, then exited 1 with `stop_reason=no_progress_loop`, no stdout, and `alibaba_cloud_studio_harness: bridge verdict publisher recovery received non-publisher tool call`. The latter run spent 595 seconds, 21 turns, and 33 tool calls before failing. Its retained telemetry correctly identifies H, the dispatch, and the failed outcome, but the final diagnostic omits the rejected tool name, publisher attempt count, and last governed publisher error.

Current source inspection isolates the defect to `scripts/cloud_harness_base.py`:

1. `run_tool_loop` correctly narrows `active_tools` to `PublishBridgeVerdict` during recovery.
2. If the provider nevertheless returns any other tool, the loop immediately raises the generic non-publisher error before appending protocol-compatible rejection results or offering another bounded correction.
3. Failed publisher results increment `publisher_failures`, but exhaustion raises `repeated bridge verdict publisher failures before completion` and discards the concrete governed result.
4. The next recovery prompt replaces the concrete failure with only `PublishBridgeVerdict did not return a verdict_path`.
5. Existing tests prove successful missing-path recovery and generic fail-closed exhaustion, but do not cover schema-violating recovery calls or diagnostic fidelity. Alibaba coverage proves inheritance only for the successful path.

WI-5224 remains authoritative for denying false completion without a governed verdict. WI-5253 is the separate D/Ollama follow-on for the equivalent provider-specific loop. WI-5245 changes only the shared cloud-provider loop and its H inheritance tests.

## Requirement Sufficiency

Existing requirements are sufficient. The cloud-harness adoption and onboarding contracts already require governed bridge publication, truthful fail-closed completion, preserved dispatcher/session provenance, bounded diagnostic behavior, and independent verification. This is an implementation gap; no new specification or specification amendment is required.

## In-Root Placement Evidence

All proposed targets are inside `E:\GT-KB`:

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - active H must complete governed LO work or leave actionable, attributed failure evidence.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - the shared cloud loop is the authoritative implementation surface for publisher recovery inherited by H.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - requires H to satisfy the governed cloud-harness capability floor.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - only the governed publisher may append H verdict artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before source mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires deterministic cloud and Alibaba regressions in final verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires exact PAUTH, project, WI, and target-path linkage.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires the three target paths and source/test classes to be enforced at implementation start.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace independent GO, a matching claim, or implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the observed H failure as a durable governed correction.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links the live defect, WI, test, PAUTH, bridge chain, implementation, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the observed fleet failure to advance through the governed lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and evidence in the GT-KB platform root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to file through its governed non-bypass helper path.
- `GOV-STANDING-BACKLOG-001` - keeps this unresolved H viability defect visible until independently verified.

## Prior Deliberations

- `DELIB-202666173` - owner directive to verify A/B/C/D/F/H, correct every discovered fleet defect, finish parity, and restore healthy eligibility.
- `DELIB-202666162` - prior H Stop-hook outcome-preservation verification; establishes that terminal H outcomes must survive adapter wrapping.
- `DELIB-202666171` - governed provider verdict-publication context for cloud/provider LO lanes.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-005.md` - VERIFIED predecessor that correctly denies completion without a governed verdict.
- `bridge/gtkb-wi5253-ollama-publisher-recovery-002.md` - D-specific sibling proposal; it does not authorize shared-cloud-loop changes.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of every defect discovered during the active six-harness governed-proof program.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5245-H-PUBLISHER-RECOVERY-20260715` is active at version 1 for WI-5245, includes the complete known 15-spec set, and limits implementation to source/test changes in the three declared paths.

## Proposed Scope

1. Retain the latest failed governed publisher result as a normalized, bounded diagnostic value. Do not retain unbounded model output, full exception objects, or unrelated tool content.
2. Include the bounded concrete failure reason in the next publisher-only correction instead of replacing it with a generic missing-`verdict_path` message.
3. When publisher attempts are exhausted, raise a deterministic error containing the bounded attempt count and last failure reason for dispatcher stderr and telemetry classification.
4. During publisher-only recovery, reject an entire provider turn if any tool call is not `PublishBridgeVerdict`. Execute none of that turn's calls, invoke no tool-side mutation for them, record the rejected tool names in bounded synthetic results, and offer another publisher-only correction while the small recovery budget remains.
5. Count malformed recovery turns against the same bounded recovery allowance and fail closed with the diagnostic contract on exhaustion.
6. Preserve success only when the governed publisher returns a nonblank `verdict_path`; clear retained failure state after successful publication.
7. Preserve native SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop semantics for valid calls, dispatcher session provenance, current model routes, and all generous turn/time/worker/lease allowances.
8. Keep the implementation in the shared cloud loop. Do not change `scripts/alibaba_cloud_studio_harness.py`; prove H inheritance in its focused test module.

## Explicit Exclusions

- No Ollama D changes; WI-5253 remains the D-specific vehicle.
- No direct bridge Write/Edit/Bash mutation or alternate verdict writer.
- No execution of provider-returned non-publisher calls during publisher-only recovery.
- No dispatcher routing, eligibility, runtime JSON, lease, lock, harness role, model, allowance, credential, deployment, release, push, history, external-system, cleanup, or unrelated worktree mutation.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Governed publisher diagnostic | Make the governed publisher return or raise a stable sentinel such as `claim contention`; after bounded exhaustion assert the error contains the exact attempt count and bounded sentinel. |
| Concrete recovery prompt | After one failed publisher call, assert the next provider payload contains the bounded failure reason and exposes only `PublishBridgeVerdict`. |
| Schema-violating recovery turn | Return `Read`, `Bash`, or a mixed publisher/non-publisher turn while recovery is active; assert none of that turn's calls are dispatched, rejected names are retained diagnostically, and recovery remains bounded. |
| Governed success | After an initial failure or malformed turn, return a successful publisher result and assert completion still requires a nonblank `verdict_path` and clears retained failure state. |
| Alibaba inheritance | Run an Anthropic-dialect H fixture through the same malformed recovery sequence and assert identical publisher-only behavior and dispatcher session propagation. |
| Native hook preservation | Existing cloud/Alibaba native-hook, Stop, and valid-tool tests continue to pass; rejected schema-violating calls do not invoke mutation-capable hooks or dispatchers. |
| Focused suites | `python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short` passes. |
| Static quality | `python -m ruff check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py` and `python -m ruff format --check` on the same paths pass. |
| Governance lifecycle | Applicability and clause preflights pass; implementation starts only after independent GO plus matching claim/start packet; final report receives independent dispatcher-produced LO verification before a focused commit. |

## Acceptance Criteria

1. A cloud/H bridge-review run in publisher-only recovery never executes a provider-returned non-publisher call.
2. A mixed publisher/non-publisher recovery turn is rejected atomically; no call from that malformed turn is dispatched.
3. Recovery prompts expose only `PublishBridgeVerdict` and include a bounded concrete reason for the prior failed or malformed turn.
4. Repeated publisher failures and repeated malformed recovery turns terminate within the configured small recovery allowance with attempt count, bridge/dispatch context already carried by telemetry, and bounded last-error detail.
5. No final provider prose is accepted until `PublishBridgeVerdict` returns a nonblank `verdict_path`.
6. Successful recovery preserves trusted H author/session/model provenance and existing native-hook completion behavior.
7. Focused cloud and Alibaba suites plus ruff checks pass with changes limited to the three target paths.
8. H is not re-enabled until the correction is independently VERIFIED and a fresh governed H run is authorized through canonical dispatcher controls.

## Risks / Rollback

The primary risk is accidentally executing a non-publisher tool while the loop is supposed to be publisher-only. Reject the whole malformed turn before PreToolUse or dispatch and cover mixed-call responses explicitly. A second risk is leaking excessive error content into prompts or telemetry; normalize whitespace and control characters, cap retained length, and retain only the governed publisher result or deterministic schema-violation reason.

Rollback reverts only the focused source/test commit. WI, TEST-11399, PAUTH, bridge, dispatch, report, and verification artifacts remain append-only audit evidence.

## Bridge Filing

This NEW artifact is filed as the next append-only numbered bridge file `bridge/gtkb-wi5245-alibaba-publisher-recovery-001.md`. Dispatcher/TAFE state plus the numbered file chain remain authoritative; no aggregate queue artifact is created.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`

## Recommended Commit Type

`fix`
