NO-GO

# Loyal Opposition Review - SessionStart Formalization (Init-Keyword Contract with Application Scope)

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-session-start-formalization-001.md`
Verdict: NO-GO

## Claim

The proposal is directionally correct: replacing the blanket first-message discard rule with an explicit init-keyword contract is the right class of fix for bridge auto-dispatch sessions. The mandatory applicability and ADR/DCL clause preflights pass.

It is not ready for implementation because the proposal has three contract defects: it leaves the unconditional SessionStart relay path unresolved, the canonical regex does not actually match one owner-specified phrase while overmatching bare verbs, and the app-scope binding writes values that do not fit the current `workstream_focus` state schema.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "session start init keyword first owner message workstream focus Agent Red bridge auto dispatch" --limit 10`

Relevant records surfaced:

- `DELIB-1079` - SessionStart acceptance-check context.
- `DELIB-1076` and `DELIB-1082` - prior startup-sequence and session-focus implementation context.
- `DELIB-1092` - Prime Builder bridge handoff context.
- `DELIB-1063` - Codex poller visibility session-wrap context.
- `DELIB-0859` / `DELIB-1152` - Agent Red session-wrap automation bridge-thread history.

The reviewed proposal also cites the S337 owner directive as `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09`, to be inserted as part of the proposed approval batch.

## Applicability Preflight

- packet_hash: `sha256:2e11e6d752a47ab4216d31cef7d28c14970b42cad4f5d0bbec46d8803460fd6b`
- bridge_document_name: `gtkb-session-start-formalization-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-session-start-formalization-001.md`
- operative_file: `bridge/gtkb-session-start-formalization-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-session-start-formalization-001`
- Operative file: `bridge\gtkb-session-start-formalization-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P0 - The no-match pass-through contract does not address the unconditional SessionStart relay payload

Observation:

- The proposal's central contract says the startup disclosure is relayed only when the first owner message matches the init-keyword grammar, otherwise the first message is processed as a normal task at `bridge/gtkb-session-start-formalization-001.md:14`.
- Its behavior summary repeats that non-matching prompts are consumed silently and processed as normal tasks at `bridge/gtkb-session-start-formalization-001.md:132-135`.
- IP-4 recommends removing `_bridge_auto_dispatch_context`, so SessionStart returns the standard payload and "the gate handles dispatch-prompt routing" at `bridge/gtkb-session-start-formalization-001.md:172-181`.
- The current special auto-dispatch context exists specifically to replace the normal startup payload: `.claude/hooks/session_start_dispatch.py:103-120` and `.codex/gtkb-hooks/session_start_dispatch.py:90-107` tell the harness not to relay normal startup and to treat the initial prompt as the dispatch task.
- If that special context is removed, the standard startup payload still contains unconditional relay directives: `scripts/session_self_initialization.py:5611-5624` says the harness must relay the generated startup message verbatim, preserve it, and not omit sections; `scripts/session_self_initialization.py:5629` says the first durable assistant answer should be the startup disclosure itself.
- IP-3 only proposes replacing the first-message discard wording at `scripts/session_self_initialization.py:3467`, `scripts/session_self_initialization.py:5630-5631`, and `scripts/workstream_focus.py:693` (`bridge/gtkb-session-start-formalization-001.md:161-170`). It does not replace or conditionalize the unconditional relay directives at `scripts/session_self_initialization.py:5611-5629`.

Deficiency rationale:

The root bug is not only the `UserPromptSubmit` discard gate. A bridge auto-dispatch child also receives a `SessionStart` `additionalContext`. If the standard payload continues to instruct "relay startup as first durable answer," a non-matching dispatch prompt can still be displaced by startup text even though `_consume_discard_first_prompt_gate` returns null.

Impact:

This can preserve the exact auto-dispatch failure mode the proposal is meant to eliminate. Dropping Slice 4 D9b and removing `_bridge_auto_dispatch_context` would be unsafe until the SessionStart payload itself is made keyword-aware or neutral for non-init sessions.

Recommended action:

Revise the design so the SessionStart payload is not an unconditional relay instruction. Acceptable shapes include:

- keep `_bridge_auto_dispatch_context` until an end-to-end test proves it is unnecessary;
- make SessionStart emit only neutral state and have the `UserPromptSubmit` init-keyword match inject the startup disclosure;
- or make the SessionStart payload explicitly conditional on a later init-keyword match, with no "first durable assistant answer must be startup disclosure" instruction on non-match paths.

Add an end-to-end test that simulates SessionStart plus first UserPromptSubmit with a bridge dispatch prompt and no env-var marker, then asserts the effective context contains no normal startup-relay instruction and the prompt is processed as bridge work.

### F2 - P1 - The canonical regex misses an owner-specified phrase and overmatches bare verbs

Observation:

- The owner directive quoted by the proposal includes `start gtkb session` at `bridge/gtkb-session-start-formalization-001.md:16`, and the Owner Decisions table repeats that selected phrase at `bridge/gtkb-session-start-formalization-001.md:70`.
- The canonical regex only allows a verb followed by zero or one object token from `session|gtkb|gt-kb|groundtruth-kb|agent_red|agent-red|agent red` at `bridge/gtkb-session-start-formalization-001.md:101-102`.
- That grammar accepts `start gtkb` but rejects `start gtkb session` because the trailing `session` remains unmatched.
- The same optional object also accepts bare `start`, `begin`, `open`, `init`, and `initialize`, because the object group is optional at `bridge/gtkb-session-start-formalization-001.md:102`.
- I evaluated the proposed regex directly: `start gtkb session` -> no match; `start session` -> match; `start` -> match; `open` -> match; `Bridge auto-dispatch notification...` -> no match.
- The test plan covers positive examples and dispatch negative tests, but it does not require the owner-specified `start gtkb session` phrase or negative tests for bare verbs at `bridge/gtkb-session-start-formalization-001.md:225-234`.

Deficiency rationale:

The proposal asks Codex to confirm the grammar "covers the owner-specified set" and does not overmatch (`bridge/gtkb-session-start-formalization-001.md:240`). It does neither. A startup contract intended to remove implicit behavior should not introduce broad one-word triggers that were not explicitly selected.

Impact:

Owner-typed `start gtkb session` would fail to initialize the session despite being the motivating phrase. Conversely, a first prompt of `start` or `open` could unexpectedly trigger startup disclosure instead of passing through as normal task input.

Recommended action:

Revise the grammar to explicitly include the selected phrase shapes, including app/object plus optional `session` where intended. Make the object mandatory for verbs unless the owner explicitly approves bare-verb init triggers. Add tests for:

- `start gtkb session` and any app-scope `... session` variants intended to be valid;
- bare `start`, `begin`, `open`, `init`, and `initialize` as negative cases unless explicitly approved;
- every owner-selected alias listed in the AUQ table.

### F3 - P1 - App-scope binding writes values outside the current work-subject schema

Observation:

- The proposal says `agent_red` resolves to "Agent Red demo adopter" at `bridge/gtkb-session-start-formalization-001.md:88-91`.
- IP-5 says the helper updates `current_subject` to the resolved app's canonical name, including `"Agent Red demo adopter"` for `agent_red` at `bridge/gtkb-session-start-formalization-001.md:185-190`.
- The spec-derived test expects `_consume_discard_first_prompt_gate("init agent_red")` to update `current_subject` to `"Agent Red demo adopter"` at `bridge/gtkb-session-start-formalization-001.md:233`.
- The live workstream state schema uses internal subject values, not labels: `scripts/workstream_focus.py:65-75` defines `FOCUS_APPLICATION = "application"`, `FOCUS_GTKB_INFRASTRUCTURE = "gtkb_infrastructure"`, and `DEFAULT_APPLICATION_LABEL = "Agent Red demo adopter"`.
- `save_state()` rejects unknown subjects at `scripts/workstream_focus.py:470-473`.
- `_normalize_subject()` normalizes unknown values back to the GT-KB default at `scripts/workstream_focus.py:396-399`.

Deficiency rationale:

`"Agent Red demo adopter"` is currently a label, not a valid `current_subject` value. Implementing IP-5 literally would either fail validation or write a value that later loads as the GT-KB default, defeating the app-scope binding.

Impact:

`init agent_red` can appear to succeed in the immediate hook path while the durable state remains invalid or silently reverts to GT-KB on the next read. That would break the scope guarantee this proposal is adding.

Recommended action:

Revise app-scope binding to use the current schema deliberately:

- set `current_subject` to `application` for `agent_red`;
- preserve `gtkb_infrastructure` for GT-KB scope;
- if the specific app identity matters, add a separate schema field such as `application_id` or `application_label`, with migration and tests.

Then update tests to assert the internal state key and the user-visible label separately.

## Positive Confirmations

- The proposed no-match behavior is the right target behavior for bridge auto-dispatch prompts.
- The sibling-thread sequencing is sensible in principle: Slice 4 should drop D9b only after this thread has a correct, verified replacement.
- Deferring app-specific disclosure content to a Phase 2 follow-on is acceptable if Phase 1 accurately records scope and does not mislabel GT-KB-default disclosure as app-specific content.
- The proposal correctly includes spec-derived tests for regex matching, gate behavior, app-scope binding, and dispatch-prompt pass-through, but those tests need the corrections above.

## Decision

NO-GO. Revise the SessionStart payload contract, the init-keyword grammar, and the work-subject state mapping before implementation.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-session-start-formalization-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-session-start-formalization-001`
- `python -m groundtruth_kb deliberations search "session start init keyword first owner message workstream focus Agent Red bridge auto dispatch" --limit 10`
- Direct regex evaluation of the proposal's canonical pattern against representative positive and negative inputs.
- `rg` and targeted file reads over `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, and the proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
