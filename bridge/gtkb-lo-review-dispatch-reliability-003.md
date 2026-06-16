REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# LO Review Dispatch Reliability Proposal - Revision

bridge_kind: prime_proposal
Document: gtkb-lo-review-dispatch-reliability
Version: 003
Responds to: bridge/gtkb-lo-review-dispatch-reliability-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["groundtruth.db", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/verify_ollama_dispatch.py", "scripts/verify_antigravity_dispatch.py", "scripts/cross_harness_bridge_trigger.py", "scripts/gtkb_bridge_writer.py", "scripts/bridge_author_metadata.py", "groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_author_meets_reviewer.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "groundtruth-kb/tests/test_tafe_live_pilot.py", ".claude/skills/bridge-config/SKILL.md", ".codex/skills/bridge-config/SKILL.md", ".api-harness/skills/**", "bridge/gtkb-lo-review-dispatch-reliability-*.md"]

implementation_scope: harness_dispatch, lo_review_quality, dispatcher_health, cli, tests, skill, session_context_review_independence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Note

This revision addresses the NO-GO in
`bridge/gtkb-lo-review-dispatch-reliability-002.md` by adding the missing
required specification links and removing the unresolved
`.agent/skills/bridge-config/SKILL.md` target. It also incorporates the owner's
2026-06-16 clarification about the Codex Loyal Opposition startup failure:
formal review independence is session-context scoped, not harness scoped.

## Summary

Make cheap/fast Loyal Opposition dispatch targets capable of returning
trustworthy bridge reviews without `bridge/INDEX.md`, and correct the
self-review guard that currently blocks valid headless Codex review.

Evidence from the no-index cleanup session:

- OpenRouter timed out after more than four minutes and produced no verdict.
- Ollama exited with max-turn exhaustion before final assistant text and
  produced no verdict.
- Antigravity/Gemini launched and produced bridge files, but one verdict was
  shallow and another had metadata/evidence reliability issues.
- A fresh Codex LO attempt reported that same-harness separation blocked Codex
  A from reviewing Codex A-authored artifacts even when the intended rule is
  session-context independence.
- `scripts/cross_harness_bridge_trigger.py` implements
  `_should_refuse_self_review()` by comparing `author_harness_id` with the
  dispatched harness id.
- `platform_tests/scripts/test_dispatch_author_meets_reviewer.py` and
  `platform_tests/scripts/test_cross_harness_bridge_trigger.py` assert the
  same over-broad same-harness blocker.

The correct rule is:

- a model session context must not formally review an artifact that it created;
- `reviewer_session_context_id == author_session_context_id` is the hard
  blocker;
- matching harness id, vendor, or model family is not itself a blocker;
- a headless Codex LO session with a fresh/disjoint session context may review
  Codex-authored artifacts if it receives only the artifact and governed
  context, not the authoring session's scratchpad, hidden reasoning, or
  conversation state.

## Prior Deliberations

- `DELIB-20263438` - owner decision for independent dispatchability and
  cost/quality/availability selection.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - hard gates before calibrated
  precedence.
- `DELIB-REVIEW-INDEPENDENCE-INVARIANT-20260610` - review independence is
  session-context scoped; same model in a disjoint context may review.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - never-self-review is a
  same-session-context prohibition, not a model or harness-family prohibition.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-SELF-REVIEW-SCOPE-20260612` - artifact-only
  spawned context is independent when it does not receive creator scratchpad,
  hidden reasoning, or conversation state.
- Current owner clarification, 2026-06-16: interactive Codex PB must not issue
  an LO verdict in the same session, but separately launched headless Codex LO
  with a different session context is eligible unless another rule blocks it.

## Owner Decisions / Input

No further owner decision is needed for this revision. The owner confirmed the
session-context interpretation in the active conversation.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must still
  proceed through reviewed bridge work and live work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge proposals, reports, and verdicts
  remain the governed lifecycle even while `bridge/INDEX.md` is retired.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision
  includes concrete governing specification links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries
  project authorization, project, work item, and target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports
  must map requirements to observed test results.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher state and audit must
  show actual work delivery and not merely static eligibility.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch target routing must use role,
  harness, subject, activity, and envelope dimensions.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - declarative rules must select eligible LO
  targets.
- `SPEC-TAFE-R4`, `SPEC-TAFE-R5`, and `SPEC-TAFE-R6` - dispatch selection,
  health, and telemetry must be measurable and auditable.
- `GOV-AGENT-INSTRUCTION-SURFACE-CONSISTENCY-001` - agent-facing dispatch and
  bridge-config surfaces must not teach obsolete review or index behavior.

## Requirement Sufficiency

Existing dispatch, TAFE health, bridge-governance, and review-independence
requirements are sufficient. The implementation defect is that some dispatch
code still uses harness identity as a self-review blocker, while the canonical
rule requires session-context comparison.

## Proposed Implementation

1. Replace `_should_refuse_self_review()` in
   `scripts/cross_harness_bridge_trigger.py` with a session-context guard:
   - parse `author_session_context_id` from the latest candidate artifact;
   - compare it with the reviewer/dispatch session context id;
   - refuse only when both are present and equal;
   - record a diagnostic when metadata is missing instead of treating same
     harness identity as a blocker.
2. Make dispatch invocation metadata expose a distinct
   `reviewer_session_context_id` for headless runs. If a harness shim already
   emits `GTKB_AUTHOR_SESSION_CONTEXT_ID`, do not reuse an authoring session id
   as reviewer identity.
3. Update tests that currently expect same-harness refusal so they expect
   same-session-context refusal and permit same-harness/different-context
   review.
4. Keep the existing same-session guard in `scripts/gtkb_bridge_writer.py`
   aligned with the dispatch guard.
5. Add LO dispatch output validation:
   - first-line status;
   - author identity/harness metadata consistency;
   - reviewer session-context metadata;
   - required evidence sections;
   - no forbidden `bridge/INDEX.md` read/write dependency;
   - target-file-only mutation.
6. Fix Ollama/OpenRouter/Antigravity dispatch health so a process launch alone
   is not reported as successful review health. Health must include recent
   launch, exit code, stdout/stderr or structured error, verdict path, and
   verdict-validation result.
7. Update the `bridge-config` skill if needed so health means eligible target
   plus recent work-output/verdict-validation evidence.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
python -m pytest platform_tests\scripts\test_dispatch_author_meets_reviewer.py platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
python -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_bridge_dispatch_config.py -q --tb=short
python -m pytest groundtruth-kb\tests\test_tafe_live_pilot.py groundtruth-kb\tests\test_tafe_flow_type_lifecycle.py -q --tb=short
gt bridge dispatch config
gt bridge dispatch status --json
gt bridge dispatch health --json
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- Same session context is blocked from formal review.
- Same harness with a different/disjoint session context is allowed when role,
  dispatchability, subject/activity rules, and readiness permit it.
- LO dispatch health includes static eligibility plus recent launch/output and
  verdict-validation evidence.
- At least one configured cheap/fast LO target can produce a valid,
  metadata-correct, evidence-bearing verdict without `bridge/INDEX.md`; if not,
  the health surface must fail closed and report the reason.

Run static stale-rule checks:

```powershell
rg -n "same[-_ ]harness|author_harness_id.*dispatched|reviewer_harness|author_meets_reviewer" scripts platform_tests groundtruth-kb\src groundtruth-kb\tests
rg -n "reviewer_session_context_id|author_session_context_id|same-session review" scripts platform_tests groundtruth-kb\src groundtruth-kb\tests
```

Expected:

- No active code path blocks review solely because harness ids match.
- Active tests assert session-context independence.

## Risks / Rollback

Risk: accepting weak LO verdicts makes the bridge protocol performative.
Mitigation: verdict validation must fail closed and report low confidence.

Risk: confusing lineage with context could either over-block valid headless
Codex LO review or under-block review that received the author's scratchpad.
Mitigation: require explicit reviewer session-context metadata and artifact-only
dispatch envelopes.

Rollback is normal source/config/test revert. Do not restore `bridge/INDEX.md`
and do not reinstate same-harness self-review blocking.
