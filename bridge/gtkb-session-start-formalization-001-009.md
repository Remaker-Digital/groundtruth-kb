REVISED

# Corrective Implementation Proposal Revision - SessionStart Formalization

bridge_kind: prime_proposal
Document: gtkb-session-start-formalization-001
Version: 009
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds-To: `bridge/gtkb-session-start-formalization-001-008.md`
Supersedes corrective report: `bridge/gtkb-session-start-formalization-001-007.md`
Recommended commit type: `fix:`
target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/hooks/test_workstream_focus.py"]

## Claim

This revision reopens only the corrective implementation scope needed to close
the `-008` verification NO-GO. It does not claim that the source fix has been
performed. The live implementation-start gate blocks protected source and test
edits while this thread's latest bridge status is `NO-GO`, so Prime Builder
needs a fresh Loyal Opposition `GO` on this corrective scope before producing a
new implementation report.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`
- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001`
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`
- `DCL-SESSION-START-APP-SCOPE-BINDING-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`

## Prior Deliberations

- `DELIB-1536` - prior Loyal Opposition NO-GO context for this SessionStart
  formalization thread.
- `DELIB-1515` - canonical init-keyword syntax review context.
- `DELIB-1079` and `DELIB-1076` - earlier startup acceptance and session-focus
  implementation context.
- `DELIB-1529`, `DELIB-1530`, and `DELIB-1531` - related startup-symmetry review
  context.
- `bridge/gtkb-session-start-formalization-001-008.md` - current verification
  NO-GO identifying the remaining source/test defects.

## Owner Decisions / Input

No new owner decision is required. The correction remains bound to the owner
directive carried through the approved proposal chain: startup disclosure must
be triggered by explicit init phrases such as `init session`, `initialize
session`, and `start gtkb session`, with app-scope phrases such as `init gtkb`
and `init agent_red`.

## Requirement Sufficiency

Existing requirements sufficient. The corrective work is directly constrained
by the linked SessionStart init-keyword ADR/DCL records, the approved proposal
chain, and the `-008` verification findings. No new or revised requirement is
required before this corrective source/test edit.

## Findings Addressed Plan

### F1 - SessionStart still emits unconditional first-answer startup relay directives

Planned correction: remove active SessionStart payload instructions that say
the harness must relay the generated startup message as the first durable
assistant answer. Replace them with neutral cache-only instructions: SessionStart
may include the generated user-visible disclosure as cached context, but only
the UserPromptSubmit init-keyword match response may instruct the harness to
render it.

### F2 - Dispatch/no-unconditional regression is absent or inverted

Planned correction: add an end-to-end regression that composes an armed
SessionStart lifecycle gate with a bridge dispatcher-style first prompt that
does not have an environment marker. The expected result is no startup relay
gate response, no startup disclosure additionalContext, and guard state marking
the prompt as a no-match pass-through.

### F3 - Ruff scope omitted the new test file

Planned correction: include every changed startup/init file in the targeted
ruff check and format-check lane, including
`platform_tests/scripts/test_session_init_keyword_matching.py`.

## Scope Changes

The corrective target path set is narrower than the original implementation
proposal. It is limited to the live SessionStart payload text and the tests
needed to prove the `-008` findings are closed. This revision does not remove
`_bridge_auto_dispatch_context` and does not change app-scoped disclosure
content.

## Pre-Filing Preflight Subsection

Prime Builder will run the helper-enforced content preflights before filing
this revision:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-start-formalization-001 --content-file <candidate>
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-start-formalization-001 --content-file <candidate>
```

Expected result: applicability preflight passes with empty missing required and
advisory spec lists; clause preflight exits 0 with no blocking gaps.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| SessionStart does not carry unconditional first-answer relay instructions | `platform_tests/scripts/test_session_self_initialization.py::test_emit_startup_service_payload_returns_full_codex_session_start_contract` asserts the startup payload contains cache-only and init-keyword-gated language and omits `first durable assistant answer` and `relay the generated startup message`. |
| Dispatch prompt without marker remains ordinary task input | `platform_tests/hooks/test_workstream_focus.py::test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task` simulates an armed first-prompt gate and a multi-line single-harness bridge dispatcher prompt, then asserts no startup gate response is returned. |
| Init grammar and app-scope bindings remain green | `platform_tests/scripts/test_session_init_keyword_matching.py` and selected `platform_tests/hooks/test_workstream_focus.py` startup-gate tests. |
| All touched files are formatted and lint-clean | Targeted `python -m ruff check` and `python -m ruff format --check` over the touched startup/init files, including the new init-keyword matcher test file. |

## Risk And Rollback

Risk: making SessionStart cache-only could hide startup disclosure when the
UserPromptSubmit init-keyword hook fails. Mitigation: the init-match hook still
injects cached disclosure and has tests covering that path; fallback text points
to the dashboard startup report.

Rollback: revert only the SessionStart payload wording and the associated tests,
then file a superseding bridge revision. Do not delete prior bridge files.
