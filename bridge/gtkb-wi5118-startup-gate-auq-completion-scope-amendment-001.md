NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved via validated session document
author_metadata_source: validated harness-state/codex/session-envelopes session document plus Codex runtime context

# WI-5118 AUQ Completion Scope Amendment

bridge_kind: prime_proposal
Document: gtkb-wi5118-startup-gate-auq-completion-scope-amendment
Version: 001
Date: 2026-07-11 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5118-STARTUP-GATE-SCOPE-AMENDMENT-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5118

target_paths: ["scripts/session_start_dispatch_core.py", ".claude/hooks/owner-decision-capture.py", "groundtruth-kb/templates/hooks/owner-decision-capture.py", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/hooks/test_owner_decision_capture.py"]

implementation_scope: scope-amendment-only
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Claim

Approve the exact five additional paths required to make a completed
AskUserQuestion clear a satisfied startup-input gate in the same interactive
session. This amendment responds to the original WI-5118 GO's binding condition:
AUQ-completion detection must occur within authorized target paths or a fresh
scope-review GO is required before implementation.

The amendment adds session-context propagation, the existing Claude
PostToolUse owner-decision capture hook, its standard-template counterpart, and
their focused regression coverage. The original GO retains authority for the
existing state-model, wrapper, and parity paths. This proposal adds no new
product behavior beyond the approved fresh-session, AUQ, repeated-AUQ,
continuation, parity, and privacy requirements.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-STARTUP-GATE-FRESH-START-ONLY-001`
already requires that an AUQ answer satisfy the gate without a second plain
prompt, that satisfaction stay monotonic during the same interactive context,
that genuinely fresh contexts re-arm, and that lifecycle state omit prompt or
AUQ-answer content. The owner approved only the target-path expansion needed to
implement those existing requirements.

## Parent Implementation Thread

The parent implementation thread is
`bridge/gtkb-wi5118-startup-gate-fresh-start-only-001.md` with its independent
GO at `bridge/gtkb-wi5118-startup-gate-fresh-start-only-002.md`. Its LO
verification condition 3 requires a fresh scope-review route when AUQ
completion needs an event surface outside the original seven target paths.

This companion thread is scope-amendment-only. It requires an independent GO
before the added targets are touched, but it has no separate implementation
report. The eventual parent WI-5118 report must cite this amendment GO and
carry all original binding verification conditions forward.

## Defect / Reproduction

The original state transition clears `startup_response_pending` through a normal
UserPromptSubmit follow-up. An AskUserQuestion answer is a tool round-trip, not
a new plain prompt, so it can leave the gate pending and wedge protected tool
use until another owner message arrives. The existing PostToolUse
`owner-decision-capture.py` sees confirmed AskUserQuestion completion, but it
and the stable SessionStart context carrier are outside the original target set.

No source, hook, or test path in this amendment has been mutated for WI-5118.
The amendment is filed before implementation precisely to preserve the bridge
and target-path gates.

## In-Root Placement Evidence

All five target paths are inside `E:\GT-KB`. They are limited to the
SessionStart context carrier, owner-decision capture parity, and focused tests.
They do not include dispatcher configuration, role registry, routing, ranking,
provider calls, credentials, application source, or external files.

## Specification Links

- `DCL-STARTUP-GATE-FRESH-START-ONLY-001` - fresh-only arming, monotonic
  satisfaction, AUQ completion, continuation, and content-free lifecycle state.
- `GOV-SESSION-SELF-INITIALIZATION-001`,
  `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, and
  `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` - preserve the required startup
  disclosure and genuinely fresh-session protection.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` - preserve continuation and role behavior
  without a new gate arm during a contiguous context.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - require shared-core behavior and
  template parity rather than a Claude-only contract drift.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - preserve PAUTH,
  scoped review, and target-path authority.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - binds final parent-thread
  verification to executed AUQ, repeated-AUQ, resume/compact, and fresh-reset
  coverage.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, and
  `GOV-STANDING-BACKLOG-001` - preserve durable in-root lineage without a
  duplicate defect or competing backlog authority.

## Prior Deliberations

- `bridge/gtkb-wi5118-startup-gate-fresh-start-only-001.md` - original defect
  proposal with its seven existing implementation targets.
- `bridge/gtkb-wi5118-startup-gate-fresh-start-only-002.md` - independent GO
  that makes scope expansion and fresh review mandatory for AUQ event capture.
- `DELIB-202666076` - original owner approval for bounded WI-5118 work.
- `DELIB-20260710-WI5118-PAUTH-SCOPE-AMENDMENT-APPROVAL` - owner approval of
  this exact session-context and AUQ-capture target-path expansion.
- `DELIB-202666019` - WI-5083 verification; continuation handling is preserved
  while the AUQ-completion defect is repaired.
- `DELIB-202665704` - mid-session init/role evidence relevant to no-rearm
  behavior.

## Owner Decisions / Input

- `DELIB-20260710-WI5118-PAUTH-SCOPE-AMENDMENT-APPROVAL` - owner approved the
  five-path expansion after being shown that the original target set cannot
  observe AUQ completion safely.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5118-STARTUP-GATE-SCOPE-AMENDMENT-20260710`
  - active bounded authorization for this companion scope amendment.
- `DELIB-202666076` and
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5118-STARTUP-GATE-20260710` remain
  the original parent-thread approval evidence and are not rewritten.

## Proposed Scope

1. Extend the shared SessionStart core to extract a stable SessionStart context
   identifier when provided and pass it to the existing startup service as the
   content-free guard identifier. Absence remains fail-safe and uses the existing
   fresh-session behavior.
2. Add a bounded owner-decision-capture acknowledgement after a confirmed
   AskUserQuestion result. It supplies only the matching session identifier to
   the shared gate state transition; it does not pass, store, log, or render the
   prompt, answer, tool arguments, or tool result in lifecycle state.
3. Keep the generated template hook behaviorally identical to the canonical
   Claude hook so future scaffolds retain the same acknowledgement contract.
4. Add focused tests for SessionStart context extraction/propagation and for
   confirmed AUQ acknowledgement, including mismatched or missing context and
   no-content persistence. The parent-thread tests retain full state-transition
   and cross-harness coverage.
5. Do not edit dispatcher configuration, dispatcher role maps, ranking, routing,
   selection, claims, production state, credentials, or the startup disclosure.

## Cross-Harness Disposition

- Shared SessionStart core: required parity. The Claude and Codex thin wrappers
  continue to consume the same context-carrier behavior through the shared core.
- Claude owner-decision capture: required parity with its standard template. The
  PostToolUse callback supplies only session identity to the gate acknowledgement.
- Codex startup behavior: remains covered by the original common-state and
  wrapper parity tests; this amendment adds no Codex-specific PostTool hook.
- Other harnesses: no native hook registration is changed. A discovered
  cross-harness mismatch remains a final parent-thread NO-GO unless an
  owner-approved typed waiver is obtained.

## Specification-Derived Verification Plan

| Requirement | Planned evidence |
| --- | --- |
| Stable context identifier reaches startup guard | `platform_tests/scripts/test_session_start_dispatch_core.py` tests valid, absent, malformed, and continuation input without consuming prompt content. |
| Confirmed AUQ clears only its matching pending guard | `platform_tests/hooks/test_owner_decision_capture.py` tests acknowledged matching context, ignored absent/mismatched context, and no prompt/answer fields in lifecycle state. |
| Template parity | The hook-template regression proves `groundtruth-kb/templates/hooks/owner-decision-capture.py` carries the same acknowledgement behavior as `.claude/hooks/owner-decision-capture.py`. |
| Full fresh-only behavior | Parent WI-5118 suites cover fresh arm, normal follow-up, AUQ, repeated AUQ, resume, compact, mid-session init/role, and distinct fresh reset. |
| Privacy | Parent and amendment tests assert no `startup_prompt_preview`, prompt body, or AUQ-answer content is persisted in lifecycle state. |

## Acceptance Criteria

- Independent LO GO authorizes the five new exact paths before source mutation.
- A completed AUQ can clear only the matching session guard without a second
  owner prompt and without exposing owner content to gate state.
- A missing or mismatched context cannot clear another session's guard.
- Claude hook and template behavior stay equivalent.
- The final parent WI-5118 report executes all original and amendment-focused
  regression evidence before requesting VERIFIED.

## Risks / Rollback

The primary risk is clearing a gate for the wrong session. The context identifier
is therefore treated as a required match, while missing/malformed identifiers
fall back to the existing fail-safe fresh-session behavior. A second risk is
leaking owner content through a convenience payload; the interface passes only
the session identity and tests assert lifecycle state contains no content-bearing
field. Rollback restores only the state transition and acknowledgement code; it
must never restore `startup_prompt_preview` retention. Bridge and PAUTH evidence
remain append-only.

## Pre-Filing Preflight Subsection

Candidate preflights completed before filing against this completed draft:

- Applicability preflight: `preflight_passed: true`; packet hash
  `sha256:5a91d74b953b536c8a608a775076248a0b06229e9a9d0fcda8a9933a46ea7352`;
  `missing_required_specs: []`; `missing_advisory_specs: []`.
- Clause applicability preflight: mandatory mode; 5 clauses evaluated, 4
  must-apply, 0 evidence gaps, 0 blocking gaps, exit 0.

## Files Expected To Change

- `scripts/session_start_dispatch_core.py`
- `.claude/hooks/owner-decision-capture.py`
- `groundtruth-kb/templates/hooks/owner-decision-capture.py`
- `platform_tests/scripts/test_session_start_dispatch_core.py`
- `platform_tests/hooks/test_owner_decision_capture.py`

## Recommended Commit Type

`fix`
