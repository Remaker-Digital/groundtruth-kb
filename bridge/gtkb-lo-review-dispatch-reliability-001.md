NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-lo-review-dispatch-reliability-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# LO Review Dispatch Reliability Proposal

bridge_kind: prime_proposal
Document: gtkb-lo-review-dispatch-reliability
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["groundtruth.db", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/verify_ollama_dispatch.py", "scripts/verify_antigravity_dispatch.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_dispatch_config.py", ".claude/skills/bridge-config/SKILL.md", ".codex/skills/bridge-config/SKILL.md", ".agent/skills/bridge-config/SKILL.md", ".api-harness/skills/**", "bridge/gtkb-lo-review-dispatch-reliability-*.md"]

implementation_scope: harness_dispatch, lo_review_quality, dispatcher_health, cli, tests, skill
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Make at least one cheap/fast Loyal Opposition dispatch target capable of
returning a trustworthy bridge review without `bridge/INDEX.md`.

Evidence from this session:

- OpenRouter timed out after more than four minutes and produced no verdict.
- Ollama exited with `max-turn exhaustion before final assistant text` and
  produced no verdict.
- Antigravity/Gemini launched and produced bridge files, but the first verdict
  was shallow and the corrected verdict contained useful findings while also
  mislabeling author identity and using incorrect bridge-id evidence in places.

The current configuration is therefore not reliable enough to treat cheap LO
review as a hard governance gate. This proposal hardens LO dispatch review
quality, output validation, and health reporting.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher state and audit must show
  actual work delivery.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch target routing must use role,
  harness, and envelope dimensions.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - declarative rules must select eligible LO
  targets.
- `SPEC-TAFE-R4`, `SPEC-TAFE-R5`, and `SPEC-TAFE-R6` - dispatch selection,
  health, and telemetry must be measurable and auditable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - LO verdicts must include
  evidence, not just an approval statement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries
  project/work-item linkage.

## Prior Deliberations

- `DELIB-20263438` - owner decision for independent dispatchability and
  cost/quality/availability selection.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - hard gates before calibrated
  precedence.
- Current owner instruction: ensure Ollama or Antigravity can provide LO
  reviews, and raise low confidence rather than pretending the review is sound.

## Owner Decisions / Input

No new owner decision is required for LO review of this proposal. If the work
finds that Ollama/Antigravity cannot be made reliable quickly, Prime Builder
should file a separate reconfiguration proposal allowing headless Codex to act
as temporary Loyal Opposition for this cleanup class.

## Requirement Sufficiency

Existing dispatch, TAFE health, and verification requirements are sufficient.
The gap is implementation and measurement: eligible targets exist, but recent
attempts did not produce trustworthy LO output.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not log credentials or provider secrets while capturing harness stderr/stdout. | Secret scan and redacted log review. | |
| CQ-PATHS-001 | Yes | Keep dispatch evidence and tests inside `E:\GT-KB`. | Root-boundary review. | |
| CQ-COMPLEXITY-001 | Yes | Add small validation wrappers instead of expanding prompt-only behavior. | Source review and targeted tests. | |
| CQ-CONSTANTS-001 | Yes | Centralize timeout, turn-limit, verdict-path, and metadata requirements. | Ruff and unit tests. | |
| CQ-SECURITY-001 | Yes | Harnesses may write only expected bridge verdict files during review tests. | Guard tests and changed-file review. | |
| CQ-DOCS-001 | Yes | Update bridge-config skill to distinguish topology health from output-quality health. | Skill parity checks. | |
| CQ-TESTS-001 | Yes | Add tests for timeout, malformed output, no verdict, shallow verdict, and metadata mismatch. | Targeted pytest commands. | |
| CQ-LOGGING-001 | Yes | Record launch attempt, exit code, stdout/stderr size, verdict path, verdict validation, and confidence. | Dispatch-health JSON assertions. | |
| CQ-VERIFICATION-001 | Yes | Require a real LO output smoke test before declaring any target healthy. | Harness smoke tests and dispatch health. | |

## Implementation Plan

1. Add verdict validation for LO dispatch outputs: first-line status, author
   identity/harness consistency, required sections, evidence count, no forbidden
   `bridge/INDEX.md` read/write, and target-file-only mutation.
2. Fix Ollama bridge-review prompting/turn loop so it returns final assistant
   text or a structured failure before max-turn exhaustion.
3. Fix OpenRouter timeout/no-output handling and ensure failure evidence is
   recorded in dispatcher health.
4. Add Antigravity/Gemini verdict validation and metadata correction. A process
   launch alone must not count as LO review health.
5. Extend `gt bridge dispatch health --json` or its backing helpers to surface
   recent launch and verdict-validation evidence.
6. Update the `bridge-config` skill so "healthy" means eligible target plus
   recent work-output evidence, not just static config.
7. If no cheap LO target can satisfy the validation smoke test, file a follow-on
   reconfiguration proposal for temporary headless Codex-as-LO review of the
   bridge-index retirement cleanup.

## Spec-Derived Verification Plan

```text
python scripts/ollama_harness.py --skill bridge-review -p "<bounded no-index review prompt>"
python scripts/openrouter_harness.py --skill bridge-review -p "<bounded no-index review prompt>"
gemini -m gemini-2.5-flash --skip-trust --approval-mode=yolo -p "<bounded no-index review prompt>"
```

Expected: at least one configured cheap/fast LO target writes a valid,
metadata-correct, evidence-bearing verdict file without `bridge/INDEX.md`.

```text
python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
```

Expected: pass, including negative tests for timeout, no verdict, shallow
verdict, malformed verdict, and metadata mismatch.

```text
python -m groundtruth_kb bridge dispatch health --json
```

Expected: includes static eligibility plus recent launch/output/verdict
validation evidence for LO targets.

## Risks / Rollback

Risk: accepting weak LO verdicts makes the bridge protocol performative.
Mitigation: validation must fail closed and report low confidence explicitly.

Rollback is normal source/config/test revert. Do not compensate by restoring
`bridge/INDEX.md` or weakening LO evidence requirements.
