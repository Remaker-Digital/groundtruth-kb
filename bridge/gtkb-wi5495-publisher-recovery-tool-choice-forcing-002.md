GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 9e57c1e3-8af4-4d1a-864c-9c9748238789
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# LO Review - Proposal GO (gtkb-wi5495-publisher-recovery-tool-choice-forcing)

bridge_kind: lo_verdict
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 002
Reviewed: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

## Verdict

GO.

## Rationale

The root-cause diagnosis is independently confirmed against the actual current
source, not just the proposal prose. In scripts/cloud_harness_base.py the
publisher-only-recovery tool_choice forcing block (around line 2392) is
gated behind profile.dialect == DIALECT_ANTHROPIC_MESSAGES only; there is no
DIALECT_OPENAI_CHAT branch anywhere in that function, and _openai_build_payload
(line 1008) never sets tool_choice under any condition. In
scripts/ollama_harness.py the payload dict built at line 1277 is unconditional
and also never sets tool_choice, confirming this is a genuinely separate,
duplicated implementation with zero forcing, not a shared code path. The
proposal's quoted reproduction stderr ("bridge verdict publisher recovery
exhausted after 4 attempts; last failure: publisher-only recovery rejected
non-publisher tool call(s): Read") matches the exact raise in
cloud_harness_base.py's publisher_recovery_failures branch (around line 2512)
verbatim, including the off-by-one arithmetic (4 = MAX_BRIDGE_VERDICT_RECOVERY_TURNS
plus one).

The proposed fix -- adding the standard OpenAI Chat Completions forced-function
tool_choice directive {type: function, function: {name: PublishBridgeVerdict}}
-- is the correct mechanism for this API family and directly mirrors the
existing, already-shipped Anthropic-dialect pattern at the exact analogous
code point in both files. Existing test infrastructure directly supports the
planned new tests: test_anthropic_publisher_only_recovery_forces_tool_choice_by_default
in test_cloud_harness_base.py is a complete, realistic template (mocked chat
function asserting per-turn payload contents) the new openai-chat-dialect test
can mirror one for one.

GOV-RELIABILITY-FAST-LANE-001 eligibility independently checked against all
four criteria: (1) WI-5495's MemBase record has origin=defect; (2) the fix
adds mechanical enforcement of an already-existing tool-offering restriction,
introducing no new public API or CLI surface; (3) Requirement Sufficiency
correctly states no new specification is needed, since this is pure dialect-
parity enforcement of already-shipped Anthropic behavior; (4) scope is 2
source files with a small, single-concern, few-line change per file, well
under the ~3-file/~150-line guide. All four hold.

PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING independently confirmed active
(status=active, expires_at=None), covers PROJECT-GTKB-RELIABILITY-FIXES with
allowed_mutation_classes including source and test_addition, and forbidden
operations (deploy, force-push, spec-deletion) are not implicated by this
scope. WI-5495 is confirmed linked to that project in MemBase.

Backlog conflict check: searched open work items referencing tool_choice,
cloud_harness_base, and ollama_harness; the only overlapping-topic items
(WI-5400, WI-5199) target different, non-duplicate defects in the same
general cloud-harness-reliability area. No conflict or duplication.

All five cited Prior Deliberations (DELIB-202666257, DELIB-202666266,
DELIB-202666227, DELIB-202666174, DELIB-202666256) independently confirmed to
exist in the Deliberation Archive with GO/VERIFIED outcomes on related
publisher-recovery reliability work. No fabricated citations.

## Specification-Derived Verification

| Requirement | Verification | Observed Result |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | Applicability preflight | PASS. preflight_passed=true; missing_required_specs=[]. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Applicability preflight | PASS; matched via doc:*, Specification Links content. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Clause preflight | PASS; zero blocking gaps, exit 0. |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Target inventory | scripts/cloud_harness_base.py, scripts/ollama_harness.py, platform_tests/scripts/test_cloud_harness_base.py, platform_tests/scripts/test_ollama_harness.py -- all resolve inside E:\GT-KB. |
| GOV-RELIABILITY-FAST-LANE-001 | Manual eligibility check against the four documented criteria | PASS -- all four criteria independently verified above. |

## Applicability Preflight

- packet_hash: sha256:c1686acfa00c4fc24cb6043062a717a0e37e7cab4279c62111dd2d04580bf9b2
- operative_file: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: 0 (pass)

## Conditions

- Acquire a fresh go_implementation claim and implementation-start
  authorization packet before mutation, per the live GO recorded here.
- Stay within the exact four declared target paths; no foreign-hunk adoption
  unless expressly authorized.
- New unit tests must assert the exact tool_choice payload shape
  ({type: function, function: {name: PublishBridgeVerdict}}) is present only
  during publisher-only recovery and absent on ordinary turns, mirroring the
  existing Anthropic-dialect test's negative-control assertions
  ("tool_choice" not in payload) at turns before and after recovery.
- The Acceptance Criteria's live direct-invocation smoke test should be run
  and its result reported concretely (pass/fail, not just "attempted") in the
  implementation report.
- Independent LO VERIFIED and focused finalization required after the
  implementation report, through the mandatory commit-finalization helper.
- No Git push, release, deployment, credential lifecycle, or destructive
  cleanup under this GO unless expressly in scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
