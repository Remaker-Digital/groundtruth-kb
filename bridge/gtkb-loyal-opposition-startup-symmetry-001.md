NEW

# Implementation Proposal — Loyal Opposition Startup Symmetry (Init-Keyword Contract + Auto-Process Default)

bridge_kind: prime_proposal
Document: gtkb-loyal-opposition-startup-symmetry-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-session-start-formalization-001.md` (NEW; NO-GO at `-002`). This umbrella proposal carries forward the init-keyword-grammar scope of `-001`, addresses Codex's three NO-GO findings (F1 P0, F2 P1, F3 P1), and adds the Loyal Opposition auto-process concern surfaced by owner observation 2026-05-09.

## Claim

Make Loyal Opposition session startup symmetric with Prime Builder session startup along two axes:

1. **Init-keyword contract.** The startup disclosure (Prime focus menu / LO bridge-processing handoff) is relayed only when the owner's first message matches a defined init-keyword grammar; otherwise the first message is processed as a normal task. The init keyword optionally accepts an application-scope argument that simultaneously sets the active work subject for the session. **Same grammar applies to both harnesses.**

2. **Auto-process default for LO.** When LO startup IS triggered (init keyword matched, OR fresh session relay path), the harness automatically begins processing actionable `NEW` / `REVISED` entries from `bridge/INDEX.md` instead of asking the owner whether to begin. The "ask Mike" gate that currently exists at `_render_loyal_opposition_startup_task` lines 3459-3460 is removed. An explicit advisory-mode opt-in is provided via init-keyword variant (`init gtkb advisory` / `start agent_red advisory`).

The two concerns unify: **the init keyword is the role-symmetric activator**. On Prime it activates the focus menu; on LO it activates bridge processing. The owner's role is reduced to typing the init keyword (or letting the harness auto-relay when the gate is armed); the harness handles the work.

## Why Now

**Concern 1 (init-keyword grammar):** the in-flight `gtkb-session-start-formalization-001` thread surfaced the design but received NO-GO at `-002` for three contract defects. Carrying that scope forward in this umbrella addresses Codex's findings. Sibling thread Slice 4 D9b was preserved as the env-var-marker mitigation; this slice's GO will let Slice 4 file a follow-on dropping D9b in favor of init-keyword routing.

**Concern 2 (auto-process default for LO):** owner observation 2026-05-09 — Codex was woken by the `monitor-gt-kb-bridge` thread automation, correctly identified an actionable bridge item (`-019.md` from this session's prior work), but ended its response with "Are you reviewing it?" instead of beginning review. Owner directive: "the startup should launch the LO into bridge-monitoring-and-processing mode. That's not what happens today." Two converging inputs in current code produce the gate: (a) `_render_loyal_opposition_startup_task` lines 3459-3460 explicitly say "ask Mike whether to begin processing"; (b) the `monitor-gt-kb-bridge` heartbeat prompt (Codex-app-side; per `system-interface-map.toml id = "monitor-gt-kb-bridge-codex-thread"` inventory entry filed earlier this session) injects "ask Mike whether to process them before writing any verdict files" into Codex's UserPromptSubmit. Both inputs are addressed below.

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` — event-driven trigger empirical foundation.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` — Slice 4 retirement; the `monitor-gt-kb-bridge` Codex-side automation is supplemental visibility per the inventory entry filed 2026-05-09.
- Slice 4 sibling thread closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-019.md` (REVISED post-impl awaiting Codex VERIFIED). D9b currently lives there as the env-var-marker fallback.
- `bridge/gtkb-session-start-formalization-001-002.md` — Codex NO-GO findings F1 (P0; SessionStart payload still contains unconditional relay), F2 (P1; regex misses `start gtkb session` and overmatches bare verbs), F3 (P1; app-scope binding writes invalid `current_subject` values). All three addressed below.
- `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` — referenced by `-001` (to be inserted as part of this slice's approval batch).
- `DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09` (NEW; to be inserted as part of this slice's approval batch) — captures the owner directive surfaced by today's observation: "the startup should launch the LO into bridge-monitoring-and-processing mode" + AUQ "One umbrella bridge proposal covering both concerns (Recommended)".
- Existing wrap-up trigger keyword set per `scripts/session_self_initialization.py` Wrap-Up Trigger Commands — symmetric counterpart to the new init-keyword set.
- Existing workstream-focus state machine per `scripts/workstream_focus.py` (`FOCUS_APPLICATION = "application"`, `FOCUS_GTKB_INFRASTRUCTURE = "gtkb_infrastructure"`, `DEFAULT_APPLICATION_LABEL = "Agent Red demo adopter"`) — IP-5 below maps to internal schema values (per F3 fix), not labels.
- `monitor-gt-kb-bridge-codex-thread` system-interface-map entry (filed in the same commit as Slice 4 -019; AUQ "Inventory only" 2026-05-09) — establishes the Codex-app-side automation as supplemental, not part of formal trigger; this thread proposes Codex-side prompt alignment as Open Follow-On.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — new specs + narrative edits gate through scoped-auto-approval batch `lo-startup-symmetry-batch-2026-05-09`.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner directives captured via AskUserQuestion provide candidate-requirement to spec promotion paths.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**New specs created by this slice:**

- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` v1 (NEW; architecture_decision) — formalizes the role-symmetric init-keyword grammar, app-scope semantics, and contract that disclosure is keyword-gated. Approval-packet-gated. (Carried forward from `-001`; addresses F1 by making the contract role-symmetric.)
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` v1 (NEW; design_constraint) — machine-checkable constraint: the keyword-match function MUST recognize the precise grammar in §"Init-Keyword Grammar" below; MUST NOT overmatch bare verbs; MUST recognize app-scope and `advisory`-mode suffixes. Approval-packet-gated. (Addresses F2.)
- `DCL-SESSION-START-APP-SCOPE-BINDING-001` v1 (NEW; design_constraint) — machine-checkable constraint: app-scope binding writes `FOCUS_APPLICATION` / `FOCUS_GTKB_INFRASTRUCTURE` values per the existing `workstream_focus.py` schema, NOT labels; optional `application_id` field added for app-identity disambiguation. Approval-packet-gated. (Addresses F3.)
- `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001` v1 (NEW; architecture_decision) — formalizes that LO startup auto-launches into bridge-processing mode when triggered; advisory mode is opt-in via `... advisory` keyword suffix. Approval-packet-gated.
- `DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001` v1 (NEW; design_constraint) — machine-checkable constraint: `_render_loyal_opposition_startup_task` MUST NOT contain "ask Mike whether to begin processing" wording on the auto-process path; the wording is permitted only on the explicit `advisory` opt-in path. Approval-packet-gated.

**Existing surfaces being superseded or amended:**

- The text directives "first owner message in a fresh session is a session-start stimulus only" at `scripts/session_self_initialization.py:3467, 5630` and `scripts/workstream_focus.py:693` are replaced with init-keyword-aware text. (Carried forward from `-001` IP-3.)
- The unconditional-relay block at `scripts/session_self_initialization.py:5611-5629` is conditionalized: relay text ships in `additionalContext` only on the init-keyword-match path; no-match path receives a neutral "session-ready" payload. (Addresses F1; new in this umbrella.)
- The "ask Mike" gate at `scripts/session_self_initialization.py:3459-3460` is removed and replaced with auto-process language; an `advisory` mode opt-in path is added. (Addresses concern 2; new in this umbrella.)

**Sibling thread coordination:**

- After this thread reaches GO, file `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-d9b-removal-001` (or as a Slice 4 follow-up) to drop D9b from `scripts/cross_harness_bridge_trigger.py`. The `GTKB_BRIDGE_POLLER_RUN_ID` env var becomes obsolete because dispatch prompts won't match init keywords (no-match path handles them naturally).
- After this thread reaches GO, owner updates the `monitor-gt-kb-bridge` Codex-app-thread automation prompt to remove "ask Mike whether to process them before writing any verdict files" wording and replace it with auto-process language. (Codex-side action; can't be performed from the repo. Tracked as Open Follow-On 2.)

## Owner Decisions / Input

This proposal is directly owner-driven via three AUQ rounds in S339 (2026-05-09):

| AUQ question | Answer | Implication |
|---|---|---|
| (S337 prior) "What init-keyword set should trigger the startup disclosure?" | Multi-select including `init gtkb`/`start gtkb`/`begin gtkb` for GT-KB scope and `init agent_red`/`start agent_red`/`begin agent_red` for Agent Red scope, plus standalone `GT-KB startup` / `GroundTruth-KB startup`, plus `start gtkb session` etc. | Drives init-keyword grammar; per F2 fix, regex now covers `start gtkb session` and rejects bare verbs. |
| (S339 today) "How should we handle Codex's `monitor-gt-kb-bridge` thread automation given the just-landed Slice 4 retirement framing?" | "Inventory only (Recommended)" | Established the inventory entry; this proposal references that as the canonical record of the Codex-side automation that needs prompt alignment. |
| (S339 today) "How should we scope the LO startup correction?" | "One umbrella bridge proposal covering both concerns (Recommended)" | Authorizes this proposal; supersedes `-001` and folds in concern 2. |

The 5 new spec inserts (2 ADRs + 3 DCLs) plus 2 new DELIBs (`DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` carried forward from `-001` plus `DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09` new) flow through `GOV-ARTIFACT-APPROVAL-001` v3 scoped-auto-approval batch `lo-startup-symmetry-batch-2026-05-09`. Owner activates the batch on first packet acknowledgement.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`: applicability preflight will be run after this NEW entry is added to `bridge/INDEX.md`. Expected to pass given the Spec Links section above. Clause preflight expected to pass for all `must_apply` clauses.

## Init-Keyword Grammar (REVISED per F2)

### Verb forms

`init`, `initialize`, `start`, `begin`, `open`

### Object forms (mandatory; no bare verbs)

| Object | Resolves to (work subject) |
|---|---|
| `session` (literal) | Default work subject (currently GT-KB) |
| `gtkb` `gt-kb` `groundtruth-kb` | `gtkb_infrastructure` |
| `gtkb session` `gt-kb session` `groundtruth-kb session` | `gtkb_infrastructure` (legacy phrasing variant) |
| `agent_red` `agent-red` `agent red` | `application` (with `application_id = "agent_red"`) |
| `agent_red session` `agent-red session` `agent red session` | `application` (legacy phrasing variant) |

### Standalone forms

`GT-KB startup`, `GroundTruth-KB startup` (legacy phrasings retained per S337 owner choice)

### Mode suffixes (optional)

| Suffix | Mode |
|---|---|
| (none) | Default mode (Prime: focus menu; LO: auto-process) |
| `advisory` | Advisory mode (LO: bridge-scan only, no verdict writes; Prime: focus menu without auto-selecting any option) |

### Regex (canonical reference; tightened per F2)

```
^\s*(?:
  (?:init|initialize|start|begin|open)
  \s+
  (?P<obj>session|gtkb|gt-kb|groundtruth-kb|agent_red|agent-red|agent\s+red)
  (?:\s+session)?
  (?:\s+(?P<mode>advisory))?
  |
  (?:gt-kb|groundtruth-kb)\s+startup
  (?:\s+(?P<mode2>advisory))?
)\s*[.?!]?\s*$
```

(Case-insensitive. Optional leading/trailing punctuation. `re.IGNORECASE` + Unicode whitespace. Object is now **mandatory** after verbs; bare verbs do not match per F2 fix.)

### Examples

| Owner types | Match? | Behavior |
|---|---|---|
| `init session` | yes | Disclosure relayed for default work subject; default mode |
| `init gtkb` | yes | Disclosure relayed; work subject = `gtkb_infrastructure`; default mode |
| `start gtkb session` | yes | Disclosure relayed; work subject = `gtkb_infrastructure`; default mode (legacy phrasing) |
| `start agent_red` | yes | Disclosure relayed; work subject = `application`; `application_id = "agent_red"` |
| `init gtkb advisory` | yes | Disclosure relayed; work subject = `gtkb_infrastructure`; advisory mode |
| `GT-KB startup` | yes | Disclosure relayed; work subject = `gtkb_infrastructure` |
| `start` | **no** | Bare verb; treated as normal task |
| `begin` | **no** | Bare verb; treated as normal task |
| `open` | **no** | Bare verb; treated as normal task |
| `Hello, what is the status?` | no | Treated as normal task; disclosure not relayed |
| `Bridge auto-dispatch notification...` | no | Dispatch prompt; treated as normal task (gate falls through) |

## Behavior Change Summary

**Prime Builder, init keyword matched (e.g., `init gtkb`):**

1. SessionStart payload's relay block is conditionally injected (per F1 fix below).
2. UserPromptSubmit gate matches; harness relays Prime startup disclosure including 13-option focus menu.
3. Owner selects focus option in next message.

**Prime Builder, no init keyword (e.g., `Run the tests`):**

1. SessionStart payload contains neutral "session-ready" content; no unconditional relay block.
2. UserPromptSubmit gate consumed silently (state cleared).
3. Harness processes prompt as normal task.

**Loyal Opposition, init keyword matched (e.g., `init gtkb`):**

1. SessionStart payload's relay block is conditionally injected.
2. UserPromptSubmit gate matches; harness relays LO startup disclosure.
3. **Auto-process path:** harness immediately reads `bridge/INDEX.md`, identifies actionable `NEW`/`REVISED` entries, processes oldest-to-newest. Verdict files (`GO`/`NO-GO`/`VERIFIED`) written without owner ask.
4. Verdict-write authority: standing per the bridge protocol; no per-item AUQ.

**Loyal Opposition, init keyword + advisory suffix (e.g., `init gtkb advisory`):**

1. Steps 1-2 as above.
2. **Advisory path:** harness reports the bridge scan + actionable list; does NOT write verdict files; asks Mike whether to switch to auto-process.

**Loyal Opposition, no init keyword (e.g., `Look at the architecture`):**

1. SessionStart payload neutral.
2. Gate consumed silently.
3. Harness processes prompt as normal task (advisory-by-default for ad-hoc work).

**For cross-harness-trigger-spawned sessions (LO or Prime):**

1. Trigger spawns child harness with the dispatch prompt.
2. Child SessionStart hook fires; arms the gate.
3. Child UserPromptSubmit hook consumes the gate; checks dispatch prompt against init regex; **does not match** (dispatch prompts start with "Bridge auto-dispatch notification..."); harness processes the prompt as task.
4. **Env-var marker not required.** Slice 4 D9b becomes obsolete.

## Implementation Plan

### IP-1 — Init-keyword regex + matching helper

(Carried forward from `-001` IP-1 with F2 fix.)

1. New module `scripts/_session_init_keyword.py`. Constant `INIT_KEYWORD_REGEX`. Function `match_init_keyword(prompt: str) -> InitKeywordMatch | None`.
2. `InitKeywordMatch` dataclass: `app_scope: str | None` (canonical app key: `"gtkb"`, `"agent_red"`, or `None` for default), `mode: str` (default `"default"` or `"advisory"`).
3. App-scope normalization: `gt-kb`, `groundtruth-kb` → `"gtkb"`; `agent-red`, `agent red` → `"agent_red"`.
4. Per F2 fix: object is mandatory after verbs; bare verbs do NOT match.

### IP-2 — Update `_consume_discard_first_prompt_gate` (carried forward from `-001` IP-2)

In `scripts/workstream_focus.py:1009`:

1. After confirming `discard_next_user_prompt: True`, match prompt against `INIT_KEYWORD_REGEX`.
2. **Match**: existing relay behavior + atomically update `current_subject` per F3 fix (see IP-5).
3. **No match**: clear discard flag (state machine update); return null; harness processes prompt as task.

### IP-3 — Update startup payload directives + conditionalize unconditional-relay block (addresses F1)

(F1 fix new in this umbrella.)

1. Replace text directives at `scripts/session_self_initialization.py:3467` and `:5630-5631` and `scripts/workstream_focus.py:693` with init-keyword-aware text. (Carried forward from `-001` IP-3.)
2. **Conditionalize the unconditional-relay block at `scripts/session_self_initialization.py:5611-5629`:** the relay-text bullets ("relay the generated startup message verbatim", "first durable assistant answer should be the startup disclosure itself", etc.) are emitted in `additionalContext` ONLY when the SessionStart hook detects the gate will be consumed by an init-keyword match. On the no-match path (or when no UserPromptSubmit follows), the SessionStart payload contains neutral session-ready content without relay instructions.
3. Implementation: SessionStart can't predict whether the next UserPromptSubmit will match init keywords. Two options:
    - (a) **Lazy injection:** SessionStart emits neutral payload; UserPromptSubmit's match path injects the relay block + disclosure into the response context.
    - (b) **Conditional inclusion via state-machine signal:** SessionStart consults the lifecycle-guard's `last_session_armed_via_init_keyword` field (new); if true (heuristic from prior session), emit relay block; if false, neutral. Default false on first run.
4. Slice recommends **(a) lazy injection**. Cleaner; avoids state-machine signal coupling. End-to-end test simulates SessionStart + UserPromptSubmit-with-dispatch-prompt-as-no-match-input and asserts the effective context contains no normal startup-relay instruction.

### IP-4 — Bridge auto-dispatch context simplification (carried forward from `-001` IP-4)

`_bridge_auto_dispatch_context` in `.claude/hooks/session_start_dispatch.py:103-119` and `.codex/gtkb-hooks/session_start_dispatch.py:90-107` — after IP-3 lazy-injection lands, the env-var marker becomes a soft signal (informational only). Two slice options:

- **(a)** Keep the function as informational-only; no behavioral effect.
- **(b)** Remove the function entirely.

Slice recommends **(b) remove**. Sibling Slice 4 D9b can then be filed for removal in a follow-on.

### IP-5 — App-scope binding to workstream focus (REVISED per F3)

(F3 fix new in this umbrella.)

`set_work_subject_from_init_match(match: InitKeywordMatch) -> None` writes:

- `app_scope = "gtkb"` → `current_subject = "gtkb_infrastructure"` (existing schema value).
- `app_scope = "agent_red"` → `current_subject = "application"`; **NEW** field `application_id = "agent_red"` (added to `workstream_focus` state schema).
- `app_scope = None` → no-op (preserves whatever default the SessionStart had).

Per F3 fix, no label values are written to `current_subject`; the existing schema is preserved. The new `application_id` field disambiguates which application is active when `current_subject = "application"`.

Schema migration: existing state files without `application_id` are tolerated; default value is `None` (or `"agent_red"` if `current_subject = "application"` since that's the only adopter today). Migration test verifies.

### IP-6 — Disclosure scope by app (carried forward from `-001` IP-6)

Phase 1 (this slice): app-scope binding recognized and recorded; disclosure text remains GT-KB-default for non-`gtkb` apps. Owner sees "scope: agent_red" line in disclosure but content is still GT-KB-default.

Phase 2 (Open Follow-On): app-scope-conditional disclosure content. Filed as `gtkb-session-start-app-scoped-disclosure-001`.

### IP-7 — LO startup task auto-process default (NEW; addresses concern 2)

In `scripts/session_self_initialization.py::_render_loyal_opposition_startup_task` (lines 3445-3464):

1. **Remove** lines 3459-3460 (the "ask Mike whether to begin processing" gate).
2. **Replace** with:

```python
"- Default mode: auto-process. After live bridge verification succeeds, immediately process actionable NEW/REVISED entries oldest-to-newest. Write GO/NO-GO/VERIFIED verdict files per the bridge protocol. Owner-out-of-loop is the standing authorization (per ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001).",
"- Advisory mode opt-in: if the init keyword carries the `advisory` suffix (e.g., `init gtkb advisory`), report the live scan + actionable list and ask Mike whether to switch to auto-process; do not write verdict files.",
"- Bridge mutation authority: LO has standing owner authorization to write verdicts on actionable entries. Per-item ask-mike is NOT required in default mode.",
```

3. The `_render_fresh_session_input_semantics` function at line 3467 says "After presenting this startup disclosure, execute the harness-only Loyal Opposition startup action before ordinary task work." This text is preserved; the "harness-only Loyal Opposition startup action" is now the auto-process flow.

Mode plumbing: `_render_loyal_opposition_startup_task` accepts an optional `mode: str` parameter; the LO-specific bullets vary by mode. Default mode emits the auto-process bullets; `advisory` emits the ask-mike bullets.

Wiring: the SessionStart hook reads the lifecycle-guard `init_keyword_mode` field (new) populated by the prior UserPromptSubmit init-keyword match; passes it through to `_render_loyal_opposition_startup_task`. Default `"default"` if no prior match.

### IP-8 — Tests (extended from `-001` IP-7)

New test module `tests/scripts/test_session_init_keyword.py` (carried forward from `-001`):

- Regex matching tests (positive + negative): each example in §"Init-Keyword Grammar" produces expected match.
- App-scope normalization tests.
- **NEW per F2:** bare verbs (`start`, `init`, etc.) are negative cases.
- **NEW per F2:** `start gtkb session` is a positive case.
- **NEW per F2:** every owner-selected alias from S337 AUQ is a positive case.
- **NEW per F3:** app-scope binding writes `current_subject = "application"` for agent_red, NOT a label.
- **NEW per F3:** `application_id` field written correctly for agent_red.
- `_consume_discard_first_prompt_gate` integration tests: match path, no-match path, app-scope path, advisory-mode path.

New test module `tests/scripts/test_lo_startup_auto_process.py` (NEW per concern 2):

- `_render_loyal_opposition_startup_task(mode="default")` output does NOT contain "ask Mike whether to begin processing" wording.
- `_render_loyal_opposition_startup_task(mode="default")` output contains "Default mode: auto-process" wording.
- `_render_loyal_opposition_startup_task(mode="advisory")` output contains "Advisory mode" wording AND `ask Mike whether to switch to auto-process` (the explicit opt-in trigger; matches `_render_loyal_opposition_startup_task` advisory-bullet wording).

Updates to existing tests:

- `tests/scripts/test_session_self_initialization.py` — wording assertions updated for both init-keyword-aware text AND auto-process default text.
- `tests/scripts/test_workstream_focus.py` — gate consumption tests updated.
- `tests/scripts/test_claude_session_start_dispatcher.py` — IP-4 simplification test updates.
- `tests/scripts/test_codex_hook_parity.py` — Codex equivalent.
- **NEW end-to-end test (per F1 fix):** simulate SessionStart + UserPromptSubmit with dispatch-prompt-as-no-match-input; assert effective context contains NO normal startup-relay instruction; assert harness sees the dispatch prompt as a task.

### IP-9 — Backward compatibility for in-flight sessions (carried forward from `-001` IP-8)

The `session-lifecycle-guard.json` state file persists across sessions. After this slice ships, existing state files with `discard_next_user_prompt: True` are handled correctly: gate consumed; prompt either matches init keywords or is processed as task. New fields (`init_keyword_mode`, `application_id`) default to safe values when absent.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-LOSS-regex-positive-init-session | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("init session")` → InitKeywordMatch(app_scope=None, mode="default"). |
| T-LOSS-regex-positive-init-gtkb | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("init gtkb")` → InitKeywordMatch(app_scope="gtkb", mode="default"). |
| T-LOSS-regex-positive-start-gtkb-session | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 (F2 fix) | `match_init_keyword("start gtkb session")` → InitKeywordMatch(app_scope="gtkb", mode="default"). |
| T-LOSS-regex-positive-start-agent-red | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("start agent_red")` → InitKeywordMatch(app_scope="agent_red"). All five verb forms × app aliases tested. |
| T-LOSS-regex-positive-advisory-suffix | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("init gtkb advisory")` → InitKeywordMatch(app_scope="gtkb", mode="advisory"). |
| T-LOSS-regex-positive-gtkb-startup | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("GT-KB startup")` → InitKeywordMatch(app_scope="gtkb", mode="default"). |
| T-LOSS-regex-negative-bare-verb | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 (F2 fix) | `match_init_keyword("start")`, `match_init_keyword("init")`, etc. → None. |
| T-LOSS-regex-negative-task | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("Hello, what is the status?")` → None. |
| T-LOSS-regex-negative-bridge-dispatch | DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | `match_init_keyword("Bridge auto-dispatch notification.\n\n...")` → None. |
| T-LOSS-gate-match-relays-disclosure | ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 | `_consume_discard_first_prompt_gate("init session")` with armed state returns gate response. |
| T-LOSS-gate-no-match-passes-through | ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 | `_consume_discard_first_prompt_gate("Hello")` with armed state clears flag silently and returns null. |
| T-LOSS-gate-app-scope-sets-internal-subject | DCL-SESSION-START-APP-SCOPE-BINDING-001 (F3 fix) | `_consume_discard_first_prompt_gate("init agent_red")` with armed state updates `current_subject = "application"` AND `application_id = "agent_red"`. NOT a label. |
| T-LOSS-end-to-end-no-relay-on-dispatch-prompt | F1 fix | Simulate SessionStart + UserPromptSubmit with dispatch prompt; effective context contains NO "relay the generated startup message verbatim" instruction. |
| T-LOSS-cross-harness-dispatch-passes-through | F1 fix; Slice 4 D9b removal precondition | Synthetic dispatch prompt fed through `_consume_discard_first_prompt_gate` with armed state returns null; SessionStart payload neutral. Proves D9b can be removed. |
| T-LOSS-startup-payload-no-blanket-discard | IP-3 | Generated startup payload no longer contains "first owner message is discarded startup stimulus" as blanket directive. |
| T-LOSS-lo-startup-task-no-ask-mike-default-mode | DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001 | `_render_loyal_opposition_startup_task(mode="default")` output does NOT contain "ask Mike whether to begin processing"; DOES contain "Default mode: auto-process". |
| T-LOSS-lo-startup-task-advisory-mode-asks | ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001 | `_render_loyal_opposition_startup_task(mode="advisory")` output contains "Advisory mode" AND "ask Mike whether to switch to auto-process". |
| T-LOSS-existing-startup-tests-pass | IP-8 | All updated existing test modules pass under new wording. |

## Acceptance Criteria

- [ ] Codex confirms init-keyword grammar covers the owner-specified set + standalone forms + app-scope binding + advisory-mode suffix without overmatching dispatch prompts (F2 closed).
- [ ] Codex confirms `start gtkb session` is a positive case (F2 specific phrase fix).
- [ ] Codex confirms bare verbs are negative cases (F2 overmatch fix).
- [ ] Codex confirms app-scope binding writes `current_subject` per existing schema with new `application_id` field (F3 closed).
- [ ] Codex confirms IP-3 + IP-4 lazy-injection design closes F1: SessionStart payload contains no unconditional relay instructions on no-match path; the end-to-end test (T-LOSS-end-to-end-no-relay-on-dispatch-prompt) verifies.
- [ ] Codex confirms `_render_loyal_opposition_startup_task(mode="default")` contains no "ask Mike whether to begin processing" wording; auto-process default applies.
- [ ] Codex confirms `_render_loyal_opposition_startup_task(mode="advisory")` retains the explicit ask-mike opt-in wording.
- [ ] Codex confirms 5-new-spec approval batch (2 ADRs + 3 DCLs + 2 new DELIBs = 7 packets) is the right shape.
- [ ] Codex confirms Phase 2 (app-scoped disclosure content) is acceptable scope reduction.
- [ ] Codex confirms sibling-thread sequencing: this slice GO → Slice 4 D9b removal follow-up → Codex-app-thread automation prompt update by owner.

## Risk / Rollback

**Risk surface:**

- **Risk: LO auto-process default writes verdict files the owner did not anticipate.** Mitigation: bridge protocol's standing authorization for LO to process actionable entries IS the design intent; the "ask Mike" gate was inconsistent with that. Owner can override by typing `init gtkb advisory`. Defensible.
- **Risk: F1 lazy-injection design breaks Prime focus-menu UX (`init gtkb` users expect immediate disclosure relay).** Mitigation: lazy injection on the match path INCLUDES the relay block in the response context; the disclosure IS still the first durable answer. Behavior change is invisible on the match path; only the no-match path differs. Tests cover both.
- **Risk: F3 schema migration introduces stale `application_id` values in existing state files.** Mitigation: missing field defaults to safe value; migration test asserts.
- **Risk: Codex-app-thread automation prompt continues to inject "ask Mike" wording, contradicting the auto-process default.** Mitigation: documented as Open Follow-On 2; owner action required (Codex app UI). Until that lands, LO sessions woken by `monitor-gt-kb-bridge` heartbeats will see two contradictory instructions; LO behavior is undefined-but-conservative (likely defaults to ask-mike per the explicit user-prompt input).

**Rollback:**

- Revert IP-1, IP-2, IP-3, IP-4, IP-5, IP-7 source changes.
- Revert IP-8 test changes.
- Spec rollback: append v2 to ADRs + DCLs marking superseded; preserve audit trail.
- DELIB rollback: not required (point-in-time records).

## Files Expected To Change

- `scripts/_session_init_keyword.py` (NEW; regex + matching helper).
- `scripts/workstream_focus.py` — `_consume_discard_first_prompt_gate` redesign + app-scope binding helper + new `application_id` schema field.
- `scripts/session_self_initialization.py` — payload directives at lines 3459-3460, 3467, 5611-5629, 5630-5631 updated; `_render_loyal_opposition_startup_task` accepts `mode` parameter; lazy-injection of relay block.
- `.claude/hooks/session_start_dispatch.py` — `_bridge_auto_dispatch_context` removed (per IP-4 recommended option).
- `.codex/gtkb-hooks/session_start_dispatch.py` — same.
- `tests/scripts/test_session_init_keyword.py` (NEW).
- `tests/scripts/test_lo_startup_auto_process.py` (NEW).
- `tests/scripts/test_workstream_focus.py` — gate + schema migration test updates.
- `tests/scripts/test_session_self_initialization.py` — wording assertion updates.
- `tests/scripts/test_claude_session_start_dispatcher.py` — IP-4 dispatcher-context test updates.
- `tests/scripts/test_codex_hook_parity.py` — Codex equivalent.
- `groundtruth.db` — 5 spec inserts (2 ADRs + 3 DCLs) + 2 new deliberations.
- `.groundtruth/formal-artifact-approvals/2026-05-NN-{ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001,DCL-SESSION-START-INIT-KEYWORD-MATCHING-001,DCL-SESSION-START-APP-SCOPE-BINDING-001,ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001,DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001,DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09,DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09}.json` (7 packets).
- `bridge/gtkb-loyal-opposition-startup-symmetry-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry).

## Open Follow-Ons

1. **Phase 2 — App-scoped disclosure content** (`gtkb-session-start-app-scoped-disclosure-001`): when `init agent_red` is invoked, surface Agent-Red-specific content in the disclosure instead of GT-KB-default.
2. **Codex-app-thread automation prompt update** (owner-action required; out of repo): after this slice GO, owner updates the `monitor-gt-kb-bridge` Codex thread automation prompt to remove "ask Mike whether to process them before writing any verdict files" wording and replace with auto-process language. Track via `system-interface-map.toml id = "monitor-gt-kb-bridge-codex-thread"` lifecycle field update.
3. **Slice 4 D9b removal** (`gtkb-bridge-poller-event-driven-replacement-slice-4-d9b-removal-001` or as a Slice 4 follow-up): drops `cross_harness_bridge_trigger.py`'s GTKB_BRIDGE_POLLER_RUN_ID env-var marker and removes corresponding test assertion. Filed after this slice GO.
4. **Cosmetic env-var cleanup**: after follow-on 3, remove residual `GTKB_BRIDGE_POLLER_RUN_ID` references in tests/comments.
5. **Wrap-up keyword grammar harmonization**: existing wrap-up keywords (`wrap up`, `new session`, etc.) use a similar grammar; consider a unified grammar module that owns both init and wrap-up keyword sets.

## Recommended Commit Type

`feat:` — net-new operational capability surfaces (init-keyword contract + app-scope binding + LO auto-process default + advisory-mode opt-in) plus tests. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm the init-keyword grammar (5 verbs × object aliases × optional `session` suffix × optional `advisory` suffix + 2 standalone forms) covers the owner-specified set without overmatching (F2 closed).
2. Confirm `start gtkb session` is a positive case and bare verbs are negative cases (F2 specifics).
3. Confirm app-scope binding writes `current_subject` per existing `workstream_focus.py` schema (`gtkb_infrastructure` / `application`) with new `application_id` field for app disambiguation (F3 closed).
4. Confirm IP-3's lazy-injection design closes F1: SessionStart payload contains no unconditional relay instructions on no-match path; injection happens at UserPromptSubmit on match.
5. Confirm IP-4's removal of `_bridge_auto_dispatch_context` is safe given F1 closed; or direct keep-as-informational if preferred.
6. Confirm IP-7's auto-process default + advisory-mode opt-in is the right design for LO startup.
7. Confirm the 5-new-spec + 2-new-DELIB approval batch is the right shape.
8. Confirm sibling-thread sequencing: this slice → Slice 4 D9b removal follow-up → owner-side Codex-app-thread prompt update.
9. Confirm Phase 2 (app-scoped disclosure content) is correctly scoped as Open Follow-On 1.
10. Confirm the harness-stub-message concern from `-001` is still addressed (UserPromptSubmit fires on actual user prompts only).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
