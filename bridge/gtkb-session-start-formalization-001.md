NEW

# Implementation Proposal --- SessionStart Formalization (Init-Keyword Contract with Application Scope)

bridge_kind: implementation_proposal
Document: gtkb-session-start-formalization-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Sibling thread: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` (currently REVISED-3 at `-001-007` awaiting Codex review). This formalization, if VERIFIED, eliminates the need for that thread's D9b (env-var marker passing); a Slice 4 REVISED-4 will drop D9b after this thread reaches GO.

## Claim

Replace the blanket "first owner message in a fresh session is discarded session-start stimulus" rule with an **explicit init-keyword contract**: the startup disclosure is relayed only when the owner's first message matches a defined init-keyword grammar; otherwise the first message is processed as a normal task. The init keyword optionally accepts an **application-scope argument** that simultaneously sets the active work subject for the session.

Owner directive (S337 AskUserQuestion): "Perhaps we can formalize the session start and eliminate this blanket restriction. If the hook were targeted at 'init session', 'initialize session' or 'start gtkb session', then this problem is eliminated." Plus extension: "Is this an appropriate opportunity to allow users to specify the application as well... `init gtkb`/`start gtkb`/`begin gtkb` would all start a GT-KB-scoped session, while `init agent_red`/`start agent_red`/`begin agent_red` would all start the session with an explicit agent_red scope."

## Why Now

The current blanket-discard rule has produced subtle bugs whenever auto-dispatched sessions interact with the rule. Most recently:

- Slice 4 REVISED-2 NO-GO at `-001-006` F1 (P0) flagged that the cross-harness trigger does not set `GTKB_BRIDGE_POLLER_RUN_ID`, so trigger-spawned children would have their dispatch prompt discarded as "session-start stimulus."
- The fix proposed in Slice 4 REVISED-3 (D9b: trigger sets the env var) preserves the marker but does not address the root cause. The env-var-as-marker design is fragile --- variable names misalign with current architecture (the marker is named POLLER but no poller will exist post-Slice-4); inheritance semantics are subtle (parent env can leak); and the SessionStart hook code reads a string env var that any subprocess can spoof or fail to set.
- Replacing the implicit env-var contract with an explicit textual contract (init keyword that the owner types or a dispatching mechanism inserts) eliminates an entire class of subtle bugs.

Plus the application-scope extension addresses a long-standing UX gap: today a user who wants to scope a session to "Agent Red mode" must (a) wait for the disclosure, (b) type a separate `agent red mode` command. With the proposal, `init agent_red` does both in one step.

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` --- event-driven trigger empirical foundation.
- Slice 4 sibling thread predecessor NO-GOs: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-{002,004,006}.md` --- surfaced the env-var marker fragility that motivates this redesign.
- `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` (NEW; to be inserted as part of this slice's approval batch) --- captures the owner directive that triggered this proposal.
- Existing wrap-up trigger keyword set per `scripts/session_self_initialization.py` Wrap-Up Trigger Commands (relayed in startup payload) --- symmetric counterpart to the new init-keyword set.
- Existing workstream-focus state machine per `scripts/workstream_focus.py` --- manages `current_subject` (work subject) which the init keyword's app-scope argument writes to.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` --- INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` --- this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` --- Test Plan section T-FORM-* below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` --- all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 --- new specs + narrative edits gate through scoped-auto-approval batch `session-start-formalization-batch-2026-05-09`.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` --- owner directive captured via AskUserQuestion provides the candidate-requirement to spec promotion path.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**New specs created by this slice:**

- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` v1 (NEW; architecture_decision) --- formalizes the init-keyword grammar, app-scope semantics, and contract that disclosure is keyword-gated. Approval-packet-gated.
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` v1 (NEW; design_constraint) --- machine-checkable constraint: `_consume_discard_first_prompt_gate` MUST relay the disclosure ONLY when prompt matches the init-keyword regex; otherwise pass through. Approval-packet-gated.
- `DCL-SESSION-START-APP-SCOPE-BINDING-001` v1 (NEW; design_constraint) --- machine-checkable constraint: when init keyword carries an app-scope argument, the active work subject is set atomically with disclosure relay. Approval-packet-gated.

**Existing surfaces being superseded or amended (text-only directives):**

- The "first owner message in a fresh session is a session-start stimulus only" directive currently lives in three text locations: `scripts/session_self_initialization.py:3467, 5630`, `scripts/workstream_focus.py:693`. These are narrative directives embedded in payload-generation code, not formal MemBase records. After this slice, those directives are replaced with init-keyword-aware text. Formal spec supersession is not required because the prior text was never promoted to a `SPEC`/`GOV`/`ADR`/`DCL`/`PB` artifact.

**Sibling thread coordination:**

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-007.md` (REVISED-3) currently includes D9b (trigger sets `GTKB_BRIDGE_POLLER_RUN_ID`). After this thread reaches GO, the sibling files REVISED-4 dropping D9b. The env-var marker becomes obsolete.

## Owner Decisions / Input

This proposal is directly owner-driven:

| AUQ question | Answer | Implication |
|---|---|---|
| (S337 this turn) "How should we handle the SessionStart redesign relative to Slice 4?" | "Redesign as prerequisite (file separately)" | Authorizes filing this thread; sibling Slice 4 REVISED-3 holds and gets REVISED-4 after this thread's GO. |
| (S337 this turn) "What init-keyword set should trigger the startup disclosure?" | Multi-select: "init session / initialize session / start gtkb session"; "Plus: start session / begin session / open session"; "Plus: GT-KB startup / GroundTruth-KB startup"; PLUS owner extension via Other field: "init gtkb/start gtkb/begin gtkb would all start a GT-KB-scoped session, while init agent_red/start agent_red/begin agent_red would all start the session with an explicit agent_red scope" | Drives the keyword grammar in section "Init-Keyword Grammar" below. |

The 3 new spec inserts (ADR + 2 DCLs) plus the new DELIB capturing the directive flow through `GOV-ARTIFACT-APPROVAL-001` v3 scoped-auto-approval batch `session-start-formalization-batch-2026-05-09`. Owner activates the batch on first packet acknowledgement.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`: applicability preflight will be run after this NEW entry is added to `bridge/INDEX.md`. Expected to pass given the Spec Links section above.

## Init-Keyword Grammar

### Verb forms

`init`, `initialize`, `start`, `begin`, `open`

### Object forms (optional; default = current default work subject)

| Object | Resolves to |
|---|---|
| `session` (literal) | Default work subject (currently GT-KB) |
| `gtkb`, `gt-kb`, `groundtruth-kb` | GT-KB Infrastructure Focus |
| `agent_red`, `agent-red`, `agent red` | Agent Red demo adopter |
| (omitted) | Default work subject |

### Standalone forms

`GT-KB startup`, `GroundTruth-KB startup` (legacy phrasings retained per S337 owner choice)

### Regex (canonical reference)

```
^\s*(?:
   (?:init|initialize|start|begin|open)
   (?:\s+(?P<app>session|gtkb|gt-kb|groundtruth-kb|agent_red|agent-red|agent\s+red))?
 |
   (?:gt-kb|groundtruth-kb)\s+startup
)\s*[.?!]?\s*$
```

(Case-insensitive. Optional leading/trailing punctuation. Implementation will use `re.IGNORECASE` and accept Unicode whitespace.)

### Examples

| Owner types | Behavior |
|---|---|
| `init session` | Disclosure relayed for default work subject |
| `init gtkb` | Disclosure relayed; work subject set to GT-KB |
| `start agent_red` | Disclosure relayed; work subject set to Agent Red |
| `GT-KB startup` | Disclosure relayed; work subject set to GT-KB |
| `Hello, what is the status?` | Does not match; treated as normal task; disclosure is not relayed |
| (empty / harness boilerplate) | Does not match; treated as normal task |

## Behavior Change Summary

**Before (current):**

1. SessionStart hook arms `discard_next_user_prompt: True`.
2. Owner's first message arrives; UserPromptSubmit hook consumes the gate, injects "this is session-start stimulus" context.
3. Harness follows directive: relays the startup disclosure regardless of what owner typed.
4. Subsequent messages are normal tasks.

**After (this slice):**

1. SessionStart hook arms `discard_next_user_prompt: True` (state-machine layer preserved for compatibility; the gate fires conditionally).
2. Owner's first message arrives; UserPromptSubmit hook consumes the gate. The gate now checks the prompt against the init-keyword regex:
   - **Match**: harness relays the (app-scoped) startup disclosure. If app-scope argument present, work subject is set atomically.
   - **Does not match**: gate is consumed silently (state cleared); harness processes prompt as normal task; disclosure is not relayed.
3. Subsequent messages are normal tasks (unchanged).

**For cross-harness-trigger-spawned sessions:**

- Trigger spawns child harness with the dispatch prompt.
- Child SessionStart hook fires; arms the gate (state-machine-layer-only; behavioral effect is null because the dispatch prompt will not match init keywords).
- Child UserPromptSubmit hook consumes the gate; checks dispatch prompt against init regex; **does not match** (dispatch prompts start with "Bridge auto-dispatch notification..."); harness processes the prompt as task.
- **Env-var marker is not required.** D9b of the sibling thread becomes unnecessary.

## Implementation Plan

### IP-1 --- Init-keyword regex + matching helper

1. Add `INIT_KEYWORD_REGEX` constant + `match_init_keyword(prompt: str) -> InitKeywordMatch | None` function in a new module (e.g., `scripts/_session_init_keyword.py`) or directly in `workstream_focus.py`.
2. `InitKeywordMatch` is a dataclass with `app_scope: str | None` (resolved app ID; e.g., `"gtkb"`, `"agent_red"`, or `None` for default).
3. App-scope normalization: `gt-kb`, `groundtruth-kb` to canonical `gtkb`; `agent-red`, `agent red` to canonical `agent_red`.

### IP-2 --- Update `_consume_discard_first_prompt_gate`

In `scripts/workstream_focus.py:1009`:

1. After reading state and confirming `discard_next_user_prompt: True`:
2. Match prompt against `INIT_KEYWORD_REGEX`.
3. **If match**: existing behavior + if `app_scope` is set, atomically update `current_subject` in workstream-focus state to the resolved app's canonical work subject.
4. **If does not match**: clear the discard flag (state machine update) but return null so the harness sees the prompt as a normal task. Inject NO additional context.

### IP-3 --- Update startup payload directives

Replace the textual directives that say "first owner message is discarded stimulus":

- `scripts/session_self_initialization.py:3467` --- replace with: "First owner message: if it matches an init keyword (`init session`, `start gtkb`, `begin agent_red`, etc.), the startup disclosure is relayed and the work subject is set; otherwise, treated as a normal task."
- `scripts/session_self_initialization.py:5630-5631` --- same pattern.
- `scripts/workstream_focus.py:693` --- same pattern.

The relevant text in the SessionStart additionalContext (current lines listing the discard rule) becomes init-keyword-aware.

### IP-4 --- Bridge auto-dispatch context simplification

`_bridge_auto_dispatch_context` in both SessionStart hooks (`.claude/hooks/session_start_dispatch.py:103-119`, `.codex/gtkb-hooks/session_start_dispatch.py:90-107`) currently checks for `GTKB_BRIDGE_POLLER_RUN_ID` and returns a special context.

Post-formalization: the env-var marker is no longer load-bearing (the dispatch prompt itself will not match init-keywords, so the gate falls through naturally). The function can be simplified to:

- Either: keep the env-var check as a soft signal (informational only; additionalContext text says "auto-dispatched session"), but remove the "do not treat initial prompt as discarded stimulus" line because the gate is now keyword-aware.
- Or: remove the function entirely. SessionStart returns the standard payload; the gate handles dispatch-prompt routing.

Slice recommends the second (remove). Sibling thread Slice 4 D9b can then be dropped entirely.

### IP-5 --- App-scope binding to workstream focus

Add a helper `set_work_subject_from_init_match(match: InitKeywordMatch) -> None` that:

1. Reads the workstream-focus state file.
2. Updates `current_subject` to the resolved app's canonical name (e.g., `"GT-KB Infrastructure Focus"` for `gtkb`, `"Agent Red demo adopter"` for `agent_red`).
3. Writes the state atomically.
4. Logs the transition (audit trail).

### IP-6 --- Disclosure scope by app

The startup disclosure currently surfaces GT-KB-specific content (release blockers, MemBase work items, etc.). When app-scope is `agent_red`, the disclosure should surface Agent-Red-specific content. Slice scope:

- **Phase 1 (this slice)**: app-scope binding is recognized and recorded; the disclosure text remains GT-KB-default. Owner sees "scope: agent_red" line in disclosure but the content is still GT-KB.
- **Phase 2 (Open Follow-On)**: app-scope-conditional disclosure content (Agent Red dashboard, Agent Red work items, etc.). Filed as `gtkb-session-start-app-scoped-disclosure-001`.

Phase 1 is sufficient to satisfy the formalization contract; Phase 2 is a UX enhancement.

### IP-7 --- Tests

New test module `tests/scripts/test_session_init_keyword.py`:

- Regex matching tests (positive + negative): each example in the Init-Keyword Grammar section produces the expected match.
- App-scope normalization tests.
- `_consume_discard_first_prompt_gate` integration tests:
  - Match path: gate fires, returns gate response.
  - No-match path: gate consumed silently, returns null.
  - App-scope path: workstream-focus state updated.

Updates to existing tests:

- `tests/scripts/test_session_self_initialization.py` lines that assert "first owner message is stimulus" wording (multiple) updated to assert init-keyword-aware wording.
- `tests/scripts/test_workstream_focus.py` (or equivalent) gate consumption tests updated.

### IP-8 --- Backward compatibility for in-flight sessions

The `session-lifecycle-guard.json` state file persists across sessions. After this slice ships, existing state files may have `discard_next_user_prompt: True` from a prior SessionStart. The new `_consume_discard_first_prompt_gate` handles this correctly: the gate is consumed; the prompt either matches init keywords or is processed as a task. Data migration is not required.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-FORM-regex-positive-init-session | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("init session")` returns InitKeywordMatch(app_scope=null). |
| T-FORM-regex-positive-init-gtkb | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("init gtkb")` returns InitKeywordMatch(app_scope="gtkb"). |
| T-FORM-regex-positive-start-agent-red | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("start agent_red")` returns InitKeywordMatch(app_scope="agent_red"). All five verb forms x app aliases tested. |
| T-FORM-regex-positive-gtkb-startup | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("GT-KB startup")` returns InitKeywordMatch(app_scope="gtkb"). |
| T-FORM-regex-negative-task | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("Hello, what is the status?")` returns null. |
| T-FORM-regex-negative-bridge-dispatch | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("Bridge auto-dispatch notification.\n\nThis is...")` returns null (dispatch prompts MUST NOT match). |
| T-FORM-gate-match-relays-disclosure | ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 | `_consume_discard_first_prompt_gate("init session")` with armed state returns the gate response (relays disclosure). |
| T-FORM-gate-no-match-passes-through | ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 | `_consume_discard_first_prompt_gate("Hello")` with armed state clears the flag silently and returns null. |
| T-FORM-gate-app-scope-sets-subject | DCL-SESSION-START-APP-SCOPE-BINDING-001 | `_consume_discard_first_prompt_gate("init agent_red")` with armed state updates workstream-focus `current_subject` to "Agent Red demo adopter". |
| T-FORM-cross-harness-dispatch-passes-through | Sibling thread Slice 4 D9b removal | Synthetic dispatch prompt fed through `_consume_discard_first_prompt_gate` with armed state returns null --- proves trigger-spawned children process dispatch prompts as tasks without env-var marker. |
| T-FORM-startup-payload-no-blanket-discard | IP-3 | Generated startup payload no longer contains "first owner message is discarded startup stimulus" as a blanket directive; instead contains init-keyword-aware text. |
| T-FORM-existing-startup-tests-pass | IP-7 | All `tests/scripts/test_session_self_initialization.py` assertions updated to new wording; pytest passes. |

## Acceptance Criteria

- [ ] Codex confirms init-keyword grammar covers the owner-specified set + standalone forms + app-scope binding without overmatching dispatch prompts.
- [ ] Codex confirms `_consume_discard_first_prompt_gate` redesign is correct: match gives relay; no-match gives pass-through silently.
- [ ] Codex confirms 3-new-spec approval batch (ADR + 2 DCLs + new DELIB) is the right shape.
- [ ] Codex confirms Phase 2 deferral (app-scoped disclosure content) is acceptable scope reduction; Phase 1 contract is sufficient for VERIFIED.
- [ ] Codex confirms sibling thread Slice 4 REVISED-3 D9b should be DROPPED in REVISED-4 once this thread is GO.
- [ ] Codex confirms harness-stub-message concern is addressed: the "first owner message" is verifiably the user's typed message, not harness boilerplate (or, if it IS sometimes boilerplate, the no-match path handles it correctly by treating it as a task).

## Risk / Rollback

**Risk surface:**

- **Risk: Harness emits a stub first message that we would misinterpret as a task.** Probed: the current code's `_consume_discard_first_prompt_gate` is wired to UserPromptSubmit, which fires only on actual user prompts. UserPromptSubmit is the user's first typed message. So the stub-boilerplate concern does not apply.
- **Risk: Owner-initiated sessions break for users who expect immediate disclosure.** Mitigation: the disclosure is opt-in via init keyword; users who do not type one see a session that is ready for normal tasks. Slightly different UX but not regressive --- the disclosure was always informational, never blocking.
- **Risk: App-scope normalization gets a new alias wrong.** Mitigation: T-FORM-regex-positive-* tests cover each documented alias; new aliases trigger explicit grammar update.
- **Risk: Existing sessions with stale `discard_next_user_prompt: True` see unexpected behavior.** Mitigation: IP-8 documents the migration path; the new gate handles existing flag state correctly.

**Rollback:**

- Revert IP-1 (regex helper module).
- Revert IP-2 changes to `_consume_discard_first_prompt_gate`; the function returns to always-relay-disclosure behavior.
- Revert IP-3 startup payload directives.
- Revert IP-4 bridge auto-dispatch context changes; sibling thread Slice 4 D9b becomes load-bearing again.
- Spec rollback: append v2 to ADR + DCLs marking superseded if rolling back; preserve audit trail.

## Files Expected To Change

- `scripts/_session_init_keyword.py` (NEW; regex + matching helper).
- `scripts/workstream_focus.py` --- `_consume_discard_first_prompt_gate` redesign + app-scope binding helper.
- `scripts/session_self_initialization.py` --- payload directives at lines 3467, 5630-5631 updated; `_arm_startup_lifecycle_guard` may simplify.
- `.claude/hooks/session_start_dispatch.py` --- `_bridge_auto_dispatch_context` simplified or removed.
- `.codex/gtkb-hooks/session_start_dispatch.py` --- same.
- `tests/scripts/test_session_init_keyword.py` (NEW).
- `tests/scripts/test_workstream_focus.py` --- gate consumption test updates.
- `tests/scripts/test_session_self_initialization.py` --- wording assertion updates.
- `tests/scripts/test_claude_session_start_dispatcher.py` --- dispatch-context test updates.
- `tests/scripts/test_codex_hook_parity.py` --- Codex equivalent.
- `groundtruth.db` --- 3 spec inserts (ADR + 2 DCLs) + 1 new deliberation.
- `.groundtruth/formal-artifact-approvals/2026-05-NN-{ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001,DCL-SESSION-START-INIT-KEYWORD-MATCHING-001,DCL-SESSION-START-APP-SCOPE-BINDING-001,DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09}.json` (4 packets).
- `bridge/gtkb-session-start-formalization-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry).

## Open Follow-Ons

1. **Phase 2 --- App-scoped disclosure content** (`gtkb-session-start-app-scoped-disclosure-001`): when `init agent_red` is invoked, surface Agent-Red-specific content in the disclosure (Agent Red dashboard, Agent Red work items, etc.) instead of GT-KB-default content. Filed after this slice VERIFIED.
2. **Sibling thread Slice 4 REVISED-4**: drops D9b in favor of this slice's solution. Filed after this slice GO.
3. **Cosmetic env-var rename**: after both this slice and Slice 4 land, `GTKB_BRIDGE_POLLER_RUN_ID` (currently set by smart-poller and trigger; both retired) is fully unused. File `gtkb-bridge-trigger-env-var-cleanup-001` to remove residual references in tests/comments.
4. **Wrap-up keyword grammar harmonization**: existing wrap-up keywords (`wrap up`, `new session`, etc.) use a similar grammar; consider a unified grammar module that owns both init and wrap-up keyword sets. Filed as enhancement when convenient.

## Recommended Commit Type

`feat:` --- net-new operational capability surface (init-keyword contract + app-scope binding) plus tests. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm the init-keyword grammar set (5 verbs x app aliases plus 2 standalone forms) is appropriate and will not overmatch.
2. Confirm `_consume_discard_first_prompt_gate` redesign is correct: match gives relay; no-match gives pass-through silently.
3. Confirm dispatch prompts (current shape: "Bridge auto-dispatch notification...") will reliably NOT match the init regex --- i.e., the no-match path is the right behavior for trigger-spawned children.
4. Confirm 3-new-spec approval batch + 1 DELIB packet (4 total) is the right shape.
5. Confirm Phase 2 (app-scoped disclosure content) is correctly scoped as Open Follow-On 1 vs. needed in this slice.
6. Confirm the proposed Slice 4 REVISED-4 (drop D9b after this slice GO) is the right sequencing --- or direct alternate sequencing.
7. Confirm the harness-stub-message concern is addressed: UserPromptSubmit fires only on actual user prompts, so harness boilerplate is not an issue.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
