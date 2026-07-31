NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed fleet stabilization; reasoning high

# Implementation Report - WI-5245 Alibaba H Publisher Recovery

bridge_kind: implementation_report
Document: gtkb-wi5245-alibaba-publisher-recovery
Version: 003
Date: 2026-07-15 UTC
Responds to GO: bridge/gtkb-wi5245-alibaba-publisher-recovery-002.md
Approved proposal: bridge/gtkb-wi5245-alibaba-publisher-recovery-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5245-H-PUBLISHER-RECOVERY-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5245
target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]
Recommended commit type: fix:

## Implementation Claim

Prime Builder implemented the GO-approved shared-cloud publisher-recovery correction. Alibaba H now sends an Anthropic named-tool choice for `PublishBridgeVerdict` during publisher-only recovery while retaining adapter-side validation. If the provider still returns a non-publisher or mixed tool turn, the loop rejects the entire turn before native hooks or tool dispatch, returns protocol-compatible synthetic rejection results, and offers another bounded correction. Repeated malformed or failed publisher turns now terminate with a normalized, length-bounded diagnostic containing the attempt count and last concrete failure.

Successful completion still requires a nonblank governed `verdict_path`. OpenAI-compatible consumers do not receive the Anthropic `tool_choice` field, and successful publication clears recovery state before final prose is accepted.

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

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of every defect discovered during the active six-harness governed-proof program.
- The owner directed this session to fix Alibaba H and separately supplied an independent Codex LO review path. That LO session authored GO at `bridge/gtkb-wi5245-alibaba-publisher-recovery-002.md` from session `019f65fb-4219-7150-ac09-26f12b650337`, distinct from this implementation session.
- H remains `can_receive_dispatch=false` until this report is independently VERIFIED. The genuine post-fix H dispatcher proof is deliberately deferred until that gate is complete.

## Prior Deliberations

- `DELIB-202666173` - fleet proof and defect-correction directive.
- `DELIB-202666162` - H Stop-hook outcome preservation.
- `DELIB-202666171` - governed provider verdict-publication context.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-005.md` - VERIFIED predecessor denying false completion without a governed verdict.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-001.md` - approved defect-fix proposal.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-002.md` - independent Loyal Opposition GO.

## Implementation Details

1. Added a 500-character recovery-reason bound with whitespace/control normalization.
2. Added Anthropic Messages `tool_choice={"type":"tool","name":"PublishBridgeVerdict"}` only while publisher-only recovery is active.
3. Reject mixed/non-publisher recovery turns atomically before tool signatures, hooks, or dispatch; no call from a rejected turn executes.
4. Return one synthetic tool result per rejected provider call so both OpenAI and Anthropic conversation protocols remain valid.
5. Count malformed recovery turns and failed publisher results against the same bounded publisher-recovery failure allowance.
6. Preserve the concrete bounded result in correction prompts and exhaustion errors, including attempt count and last failure.
7. Reset the retained failure and recovery counters only after a nonblank governed `verdict_path` is returned.

## Files Changed

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`

No Alibaba adapter, dispatcher, routing, eligibility, lease, runtime-state, model, allowance, credential, deployment, release, push, or unrelated worktree path was changed.

## Specification-Derived Verification

| Governing surface | Executed evidence |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-CLOUD-HARNESS-TEMPLATE-001`, `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | Combined cloud/Alibaba/OpenRouter suite: 156 passed. Alibaba tests prove named-tool forcing, atomic mixed-turn rejection, one governed publisher dispatch, and successful completion. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_bridge_review_rejects_mixed_publisher_recovery_turn_atomically` and `test_alibaba_loop_rejects_mixed_publisher_recovery_turn_atomically` assert only the final valid `PublishBridgeVerdict` reaches dispatch; rejected `Read` and mixed publisher calls do not execute. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Five new/strengthened recovery assertions execute against the implementation; focused and shared-consumer suites pass. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Claim acquired at `2026-07-15T13:49:36Z`; implementation-start packet finalized at `2026-07-15T13:49:41Z`; PAUTH evaluator returned `allowed` for exactly one source and two test paths. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-STANDING-BACKLOG-001` | WI-5245 remains open and linked to TEST-11399, PAUTH, NEW proposal, GO, this implementation report, and pending independent verification. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All three changed paths are under `E:\GT-KB`; `git diff --check` passed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Alibaba native-hook regressions remain green; rejected turns are handled before native PreToolUse/PostToolUse and dispatch. |

## Commands Run And Observed Results

- `python -m pytest platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py -q --tb=short` - baseline before implementation: 102 passed; final focused run: 105 passed.
- `python -m pytest platform_tests\scripts\test_openrouter_harness.py -q --tb=short` - 50 passed.
- `python -m pytest platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_openrouter_harness.py -q --tb=short` - 156 passed.
- `python -m ruff check scripts\cloud_harness_base.py platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py` - all checks passed.
- `python -m ruff format --check scripts\cloud_harness_base.py platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py` - 3 files already formatted.
- `git diff --check -- scripts\cloud_harness_base.py platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py` - passed; only line-ending notices were emitted.
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5245-alibaba-publisher-recovery` - passed; no missing required or advisory specs.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5245-alibaba-publisher-recovery` - passed; zero evidence gaps and zero blocking gaps.

## Acceptance Criteria Status

- [x] Publisher-only recovery never executes a provider-returned non-publisher call.
- [x] Mixed publisher/non-publisher recovery turns are rejected atomically.
- [x] Anthropic recovery payloads expose and force only `PublishBridgeVerdict`; OpenAI payloads remain unchanged.
- [x] Recovery prompts retain a bounded, normalized concrete failure reason.
- [x] Repeated publisher failures and malformed turns terminate with attempt count and bounded last-error detail.
- [x] Completion still requires a nonblank governed `verdict_path`.
- [x] Valid H provenance, native hooks, generous runtime allowances, and the adapter contract remain unchanged.
- [x] Focused cloud/Alibaba/OpenRouter tests and both Ruff gates pass.
- [x] H remains dispatch-disabled pending independent VERIFIED and a fresh governed post-fix H run.

## Risk And Rollback

Provider `tool_choice` is guidance rather than the security boundary; the adapter-side atomic rejection remains authoritative if Alibaba violates the requested schema. The retained diagnostic is normalized and capped at 500 characters, and rejected model prose is not retained in the synthetic recovery message. Residual risk is limited to provider-specific Anthropic compatibility in a genuine H run, which is the required post-VERIFIED proof step.

Rollback reverts only the three focused source/test paths. WI-5245, TEST-11399, PAUTH, proposal, GO, report, and subsequent verification remain append-only evidence.

## Recommended Commit Type

`fix`

## Loyal Opposition Asks

1. Verify the implementation against all linked specifications and the exact command evidence above.
2. Confirm that malformed publisher-only turns cannot reach native hooks or dispatch and that Anthropic forcing is recovery-only.
3. Return `VERIFIED` with atomic focused commit finalization if the implementation satisfies the GO; otherwise return `NO-GO` with concrete findings.
