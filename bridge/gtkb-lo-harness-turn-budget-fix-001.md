NEW

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Raise LO Reviewer Turn Budget (openrouter, ollama) - Reliability Fast-Lane

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4734
target_paths: ["scripts/openrouter_harness.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_lo_harness_turn_budget.py"]

Document: gtkb-lo-harness-turn-budget-fix

## Summary

Raise `DEFAULT_MAX_TURNS` from 24 to 80 in the two Python LO reviewer shims
(`scripts/openrouter_harness.py:38`, `scripts/ollama_harness.py:39`). The
harness-registry headless argv for openrouter (F) and ollama (D) passes no
`--max-turns` override and there is no env knob, so dispatched LO reviews run at
the 24-turn default. A full bridge verification (read all versions + applicability
preflight + clause preflight + read source + write verdict + finalize commit)
exceeds 24 tool-loop turns, so workers exit 1 with "max-turn exhaustion before
final assistant text" before writing a verdict - LO verifications never complete,
nothing reaches VERIFIED, and the backlog does not drain (observed flat at 58
total across 23:21-23:45Z while Prime drained 44->42 and LO grew 14->16). The
registry argv is unchanged, so dispatched workers pick up the new default
immediately; the capable models (deepseek-v4 / kimi-k2.7-code) were making
tool-call progress and simply ran out of steps.

## Reliability Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

- origin = defect (WI-4734).
- No new public API / CLI surface / behavior beyond removing the defect (a
  constant value change; the `--max-turns` CLI arg already exists).
- No new or revised requirement/specification.
- Small, single-concern: 2 source files + 1 test, ~6 net lines.
- Covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` via active membership
  of WI-4734 in PROJECT-GTKB-RELIABILITY-FIXES (verified). No per-fix
  deliberation, project authorization, or formal-artifact packet required.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - governs this fast-lane defect fix.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this fix restores
  LO reviewer function (bridge integrity is the top-priority subsystem).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites
  all relevant governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification
  is in the Spec-Derived Verification section.
- `.claude/rules/bridge-essential.md` - LO reviewer reliability is bridge function.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement is required; this
removes a defect (an under-budgeted reviewer loop) without changing intended
behavior. The reviewers are already required to complete verifications; this fix
lets them.

## Prior Deliberations

_No prior deliberations: novel reliability defect (LO reviewer turn budget),
discovered 2026-06-21 during live dispatch monitoring after the dispatch
kill-switch removal. No prior DA record on LO-harness turn budgets._

## Change Detail

- `scripts/openrouter_harness.py`: `DEFAULT_MAX_TURNS = 24` -> `DEFAULT_MAX_TURNS = 80`.
- `scripts/ollama_harness.py`: `DEFAULT_MAX_TURNS = 24` -> `DEFAULT_MAX_TURNS = 80`.
- `platform_tests/scripts/test_lo_harness_turn_budget.py` (new): assert both shims
  expose `DEFAULT_MAX_TURNS >= 80` and that each argparse `--max-turns` default
  equals its module `DEFAULT_MAX_TURNS`.
- Rationale for 80: a verification needs ~40-80 turns; 80 gives headroom.
  `max_turns` is a ceiling (the loop exits as soon as the model emits final text),
  so reviews that finish early are unaffected; only reviews that were hitting the
  limit benefit. Tunable later if 80 proves tight.

## Spec-Derived Verification

Derived from WI-4734 acceptance (reviewers complete verifications without
max-turn exhaustion) and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

- `python -m pytest platform_tests/scripts/test_lo_harness_turn_budget.py -q` -
  asserts `DEFAULT_MAX_TURNS >= 80` in both shims and argparse-default parity.
- Import + value smoke check of both modules' `DEFAULT_MAX_TURNS`.
- `ruff check` and `ruff format --check` on the three changed files.
- Post-impl operational confirmation: an LO review dispatched to openrouter or
  ollama completes and writes a verdict (no "max-turn exhaustion").

## Risk / Rollback

- Risk: a higher ceiling lets a pathologically-looping review run longer before
  bailing (more tokens). Low - `max_turns` is a ceiling only; productive reviews
  exit early; bounded at 80.
- Risk: 80 still insufficient for the largest verifications. Mitigation: tune up
  in a follow-up; the test asserts `>= 80` so raising further stays compliant.
- Rollback: revert the two constants to 24 and remove the test - single-commit revert.

## Owner Decisions / Input

- AUQ 2026-06-21 "dig into the LO-harness turn-budget config now" -> investigation
  completed; root cause = 24-turn default with no override.
- AUQ 2026-06-21 "LO fix approach" -> **Fast-lane fix, gemini reviews**: file a
  reliability-fast-lane proposal raising openrouter+ollama to `--max-turns 80`
  (implemented here as the `DEFAULT_MAX_TURNS` default the registry argv falls
  back to), and route the LO review to antigravity (gemini), the reviewer not
  subject to the 24-turn shim.

## Recommended Commit Type

`fix:` - repairs broken LO reviewer behavior (under-budgeted tool loop) with no
new capability surface.
