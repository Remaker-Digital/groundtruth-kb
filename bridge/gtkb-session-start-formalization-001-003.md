REVISED

# Revised Implementation Proposal - SessionStart Formalization

bridge_kind: prime_proposal
Document: gtkb-session-start-formalization-001
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Supersedes: `bridge/gtkb-session-start-formalization-001.md`
Responds-To: `bridge/gtkb-session-start-formalization-001-002.md`
Recommended commit type: `feat:`

## Claim

This revision keeps the init-keyword contract from the original proposal but
closes the three `-002` NO-GO findings before implementation:

1. SessionStart may no longer carry unconditional "first durable answer must be
   the startup disclosure" instructions on non-init paths.
2. The init grammar must match owner-selected phrases such as
   `start gtkb session` while rejecting bare verbs such as `start`.
3. Application scope must write the current workstream schema values
   (`application` or `gtkb_infrastructure`), not user-visible labels as
   `current_subject`.

No implementation is performed in this revision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`
- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` (new spec proposed by this slice)
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` (new spec proposed by this slice)
- `DCL-SESSION-START-APP-SCOPE-BINDING-001` (new spec proposed by this slice)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Owner Decisions / Input

This proposal remains bound to the owner directive quoted in `-001`: formalize
session start around explicit owner init phrases such as `init session`,
`initialize session`, and `start gtkb session`, and support app-scope phrases
such as `init gtkb` and `init agent_red`.

No new owner decision is required for this revision. Bare verbs are treated as
out of scope because the owner-selected phrases all include an init object.

## Revision Response To NO-GO `-002`

### F1 - SessionStart Relay Becomes Conditional

Implementation must revise the SessionStart payload contract before removing
any existing auto-dispatch special context.

Acceptable implementation shape for this slice:

- SessionStart may emit startup state, freshness metadata, and hook diagnostics.
- SessionStart must not instruct the harness that the first durable assistant
  answer is always the startup disclosure.
- The startup disclosure is injected or relayed only after UserPromptSubmit
  matches the init-keyword grammar.
- Non-matching first prompts receive no normal startup-relay instruction and
  are processed as normal task input.
- `_bridge_auto_dispatch_context` remains in place until an end-to-end test
  proves that a dispatch prompt with no environment marker is not displaced by
  the normal startup payload.

Required regression:

`test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task`
simulates SessionStart followed by a bridge auto-dispatch prompt, with no
`GTKB_BRIDGE_POLLER_RUN_ID` or successor marker, and asserts the effective
context contains no unconditional startup-relay directive.

### F2 - Grammar Matches Owner Phrases And Rejects Bare Verbs

Canonical matching rule:

```text
^\s*(?:
  (?P<verb>init|initialize|start|begin|open)
  \s+
  (?:
    (?P<session>session)
    |
    (?P<gtkb>gtkb|gt-kb|groundtruth-kb)(?:\s+session)?
    |
    (?P<agent>agent_red|agent-red|agent\s+red)(?:\s+session)?
  )
  |
  (?P<startup>gt-kb|groundtruth-kb)\s+startup
)\s*[.?!]?\s*$
```

Implementation may factor this into a readable verbose regex, but it must
preserve the behavioral contract:

- positive: `init session`, `initialize session`, `start session`,
  `begin session`, `open session`
- positive: `init gtkb`, `start gtkb`, `begin gtkb`,
  `start gtkb session`, `GroundTruth-KB startup`, `GT-KB startup`
- positive: `init agent_red`, `start agent-red`, `begin agent red`,
  and app-scope `... session` variants
- negative: bare `init`, `initialize`, `start`, `begin`, `open`
- negative: bridge dispatch prompts such as `Bridge auto-dispatch notification`

### F3 - App Scope Writes Internal Workstream Values

Application-scope binding must use the current workstream state schema:

- GT-KB aliases write `current_subject = "gtkb_infrastructure"`.
- Agent Red aliases write `current_subject = "application"`.
- The user-visible label `Agent Red demo adopter` remains a label, not the
  `current_subject` value.
- If specific app identity must be persisted later, that is a follow-on schema
  extension such as `application_id` or `application_label`, with its own
  migration and tests.

Required tests:

- `init agent_red` updates durable state to `current_subject == "application"`.
- `init gtkb` updates durable state to
  `current_subject == "gtkb_infrastructure"`.
- User-visible disclosure may render `Agent Red demo adopter` separately, but
  tests must not expect that label in `current_subject`.

## Updated Implementation Plan

1. Add or update an init-keyword helper module with the corrected grammar and
   explicit normalization output.
2. Update `_consume_discard_first_prompt_gate` so a match relays the startup
   disclosure and an app-scope update, while a non-match clears the gate and
   returns no additional context.
3. Revise `scripts/session_self_initialization.py` and `scripts/workstream_focus.py`
   text so they no longer state the blanket first-message discard rule.
4. Keep the bridge auto-dispatch context until the new end-to-end dispatch
   regression is green; remove it only in a later revision or implementation
   report if the regression proves it unnecessary.
5. Leave app-specific disclosure content as a Phase 2 follow-on.

## Specification-Derived Verification Plan

| Test | Requirement |
| --- | --- |
| `test_match_start_gtkb_session` | Owner-selected phrase is accepted. |
| `test_bare_verbs_do_not_match` | Bare `init`, `initialize`, `start`, `begin`, and `open` pass through as normal prompts. |
| `test_dispatch_prompt_does_not_match` | Auto-dispatch prompts are not consumed as init requests. |
| `test_gate_non_match_returns_no_context` | Non-init first prompt clears the gate and injects no startup disclosure. |
| `test_gate_match_relays_disclosure` | Init first prompt receives startup disclosure handling. |
| `test_gate_app_scope_sets_internal_subject_application` | `init agent_red` writes `current_subject = "application"`. |
| `test_gate_gtkb_scope_sets_internal_subject` | `init gtkb` writes `current_subject = "gtkb_infrastructure"`. |
| `test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task` | F1 end-to-end guard: no unconditional SessionStart relay displaces bridge work. |
| `test_startup_payload_has_no_blanket_discard_rule` | Startup payload text is init-keyword-aware. |

## Acceptance Criteria

- The canonical grammar accepts the owner-selected init phrases and rejects
  bare verbs.
- Non-init first prompts are processed as ordinary work and are not displaced
  by SessionStart instructions.
- App-scope binding persists only schema-valid workstream subjects.
- Any removal of `_bridge_auto_dispatch_context` is backed by the explicit
  SessionStart plus dispatch-prompt regression.
- No implementation starts before this revised proposal receives GO.

## Requested Loyal Opposition Review

Review this revision for GO. It is intended to resolve all three `-002` findings
without changing the implementation scope beyond the required corrective tests.
