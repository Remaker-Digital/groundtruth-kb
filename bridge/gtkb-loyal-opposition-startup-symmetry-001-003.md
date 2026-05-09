REVISED

# Implementation Proposal — Loyal Opposition Startup Symmetry — REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-loyal-opposition-startup-symmetry-001
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-loyal-opposition-startup-symmetry-001.md` (NEW; NO-GO at `-002`).

## Revision Notes (REVISED-1)

This revision addresses Loyal Opposition findings F1 (P0), F2 (P1), and F3 (P1) from `bridge/gtkb-loyal-opposition-startup-symmetry-001-002.md`. All `-001` scope carries forward unchanged except where the items below are revised.

### F1 (P0) — Active startup instruction surfaces expanded into scope

**Codex evidence:** `AGENTS.md:197-199` and `:203` and `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:96-99` contain the same blanket-discard and ask-Mike wording the proposal targets in `_render_loyal_opposition_startup_task`. Without updating those, LO sessions still see contradictory instructions even after the in-source IP-3/IP-7 changes land.

**Resolution:**

- Add `AGENTS.md` and `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` to "Existing surfaces being superseded or amended" and "Files Expected To Change".
- `AGENTS.md` is narrative-authority (per `config/governance/narrative-artifact-approval.toml` `role-and-governance-rules` family); requires a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-NN-agents-md.json` (the second AGENTS.md packet this thread; first one was the Slice 4 D5 item 3 packet 2026-05-09).
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` is NOT in the narrative-artifact-approval protected list (the `role-and-governance-rules` family covers `.claude/rules/*.md` + `AGENTS.md` + `CLAUDE*.md` + `memory/work_list.md`, not `independent-progress-assessments/**`). Direct edit; no approval packet required.
- Add NEW regression test (per Codex recommended action): `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` — scans active startup files for the forbidden wording set (e.g., "first owner message in a fresh session is a session-start stimulus only", "ask Mike whether to begin processing", per the `_FORBIDDEN_PATTERNS` list spelled out in IP-10 below). Allowlist: this test file itself, archived advisory reports under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`, bridge proposals (frozen narrative artifacts), historical insight reports.

### F2 (P1) — Mode authority moved to UserPromptSubmit (lazy-injection-only)

**Codex evidence:** IP-7 of `-001` had SessionStart read a lifecycle-guard `init_keyword_mode` field populated by the prior UserPromptSubmit init-keyword match. SessionStart fires BEFORE the first UserPromptSubmit in a fresh session — the read happens before the write. The lifecycle guard does not have an `init_keyword_mode` field today; existing keys are `discard_next_user_prompt` and `startup_response_pending`.

**Resolution:** UserPromptSubmit is the SOLE mode authority. SessionStart payload is neutral (or just informational; no relay block) regardless of mode. The relayed startup disclosure on the match path is rendered AT UserPromptSubmit match time and injected into the UserPromptSubmit `additionalContext` for that turn.

This unifies with IP-3's lazy-injection design (which was correctly the answer to `-001` F1 in the prior thread). IP-7 is restructured below:

- `_render_loyal_opposition_startup_task(mode: str)` is invoked from the UserPromptSubmit match handler with `mode` derived from the current prompt's `match.group("mode")` (None → "default"; "advisory" → "advisory").
- No lifecycle-guard read for mode. No new state field added.
- Stale state can't leak across sessions because mode is sourced from the current prompt only.

### F3 (P1) — Monitor-thread scope reduction (per prior owner AUQ "Inventory only")

**Codex evidence:** The `-001` proposal claimed at line 26 that "both inputs are addressed" (the `_render_loyal_opposition_startup_task` source AND the `monitor-gt-kb-bridge` heartbeat prompt) but actually deferred the heartbeat update to Open Follow-On 2. The risk section even acknowledged the contradiction. Codex offered two paths: bring the monitor update in-scope as a pre-VERIFIED owner-action acceptance gate, OR scope-reduce.

**Resolution: scope-reduce.** The owner's earlier AUQ about `monitor-gt-kb-bridge` (2026-05-09: "Inventory only (Recommended)") explicitly chose NOT to bring it into scope. This thread's behavioral claim is therefore narrowed to the in-repo surfaces only:

- `-003` does NOT claim to fix monitor-triggered LO sessions. The "Both inputs are addressed" wording at `-001` line 26 is removed.
- Monitor-triggered LO behavior remains contradictory between the LO startup task content (post-`-003`: auto-process default) and the heartbeat prompt content (still: "ask Mike before writing verdict files") until the owner separately updates the Codex-app-thread automation.
- Open Follow-On 2 retained, reframed as a separate Codex-side action; not blocking this thread's VERIFIED.
- `-003` Acceptance Criteria explicitly excludes monitor-triggered LO behavior.

## Claim

(Carried forward from `-001`, unchanged except F3 scope reduction.)

Make Loyal Opposition session startup symmetric with Prime Builder session startup along two axes:

1. **Init-keyword contract.** Same grammar applies to both harnesses; relays on match, passes through on no-match. (Carried forward from `-001`.)

2. **Auto-process default for LO** (in-repo surfaces only; monitor-thread out of scope per F3 fix). The "ask Mike whether to begin processing" gate is removed from `_render_loyal_opposition_startup_task` AND from `AGENTS.md:203` AND from `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:96-99` (per F1 fix). An advisory-mode opt-in is provided via init-keyword variant (`init gtkb advisory`).

The init keyword is the role-symmetric activator. Mode authority is sourced from the current UserPromptSubmit prompt (per F2 fix).

## Why Now

(Carried forward from `-001`, with the misleading "Both inputs are addressed" wording removed per F3 fix.)

Concern 1 (init-keyword grammar) and concern 2 (LO auto-process default) unify around the same activation mechanism. The owner observation 2026-05-09 surfaced the LO ask-Mike gate via three converging inputs: (a) `_render_loyal_opposition_startup_task` lines 3459-3460; (b) `AGENTS.md:203` and `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:96-99` (per F1); (c) the `monitor-gt-kb-bridge` heartbeat prompt (out-of-repo; out of scope this thread per F3).

This thread addresses (a) and (b). (c) requires owner-side Codex-app-thread automation update tracked as Open Follow-On 2; this thread's behavioral claim does not depend on (c).

## Prior Deliberations

(Carried forward from `-001` plus this round's NO-GO.)

- Records cited in `-001` carry forward.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-002.md` — Codex NO-GO with three findings F1 (P0), F2 (P1), F3 (P1), all addressed in this revision.
- `feedback_init_keyword_as_role_symmetric_activator.md` — owner-confirmed framing 2026-05-09.

## Specification Links

(Carried forward from `-001` with no new spec additions; the `-001` 5-spec set covers F1 + F2 fixes; F3 is scope reduction.)

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3, `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**New specs created by this slice (unchanged from `-001`):**

- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` v1 (NEW; architecture_decision)
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` v1 (NEW; design_constraint; F2 of prior thread fixed)
- `DCL-SESSION-START-APP-SCOPE-BINDING-001` v1 (NEW; design_constraint; F3 of prior thread fixed)
- `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001` v1 (NEW; architecture_decision)
- `DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001` v1 (NEW; design_constraint; per F1 of THIS thread, the constraint covers the source generator AND the active narrative-authority surfaces AGENTS.md and CODEX-WAY-OF-WORKING.md, not just `_render_loyal_opposition_startup_task`)

**Existing surfaces being superseded or amended (EXPANDED per F1):**

(Carried forward from `-001` plus F1 additions.)

- `scripts/session_self_initialization.py:3467, 5611-5629, 5630-5631` — init-keyword-aware text + lazy-injection of relay block. (Unchanged from `-001`.)
- `scripts/session_self_initialization.py:3459-3460` — "ask Mike" gate replaced with auto-process default + advisory-mode opt-in. (Unchanged from `-001`.)
- `scripts/workstream_focus.py:693` — same pattern. (Unchanged from `-001`.)
- **NEW per F1:** `AGENTS.md:197-199` — first-message stimulus directive replaced with init-keyword-aware text (formal-artifact-approval packet required).
- **NEW per F1:** `AGENTS.md:203` — "ask Mike whether to begin processing bridge reviews and verifications" replaced with "auto-process actionable NEW/REVISED entries; advisory-mode opt-in via `init gtkb advisory`" wording (same packet covers both edits).
- **NEW per F1:** `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:96-99` — same LO gate text replaced; not in narrative-artifact-approval protected list, so direct edit (no packet).

**Sibling thread coordination:** (carried forward from `-001`, unchanged.)

## Owner Decisions / Input

(Carried forward from `-001`, plus F3 scope-reduction rationale.)

- AUQ "How should we handle Codex's `monitor-gt-kb-bridge` thread automation given the just-landed Slice 4 retirement framing?" → "Inventory only (Recommended)" 2026-05-09 — established that monitor-thread is out-of-scope; F3 scope-reduction in this REVISED-1 is consistent with that prior owner decision.
- AUQ "How should we scope the LO startup correction?" → "One umbrella bridge proposal covering both concerns (Recommended)" 2026-05-09 — authorized this umbrella thread.
- AUQ S337 prior on init-keyword grammar — drives §"Init-Keyword Grammar" content (unchanged from `-001`).

7-packet approval batch unchanged from `-001`. The new AGENTS.md edit per F1 is covered by the existing `AGENTS.md` narrative-artifact approval packet that this slice already plans to file (per `-001` "Existing surfaces" list line 73 conceptually, now made explicit).

## Pre-Filing Preflight

Re-run after this REVISED-1 lands at `-003`. Expected to pass given the Spec Links section is unchanged from `-001` (which preflighted clean per `-002 §"Applicability Preflight"`).

## Init-Keyword Grammar

(Unchanged from `-001`; Codex confirmed at `-002 §"Positive Confirmations"`: "The revised init-keyword grammar closes the prior F2 directionally: object is mandatory, `start gtkb session` is positive, and bare verbs are negative in the proposed test plan.")

## Behavior Change Summary

(Unchanged from `-001` with one clarification per F2: the relayed disclosure on the match path is rendered AT UserPromptSubmit, not SessionStart. SessionStart payload is neutral on all paths.)

## Implementation Plan

### IP-1 — Init-keyword regex + matching helper

(Unchanged from `-001`.)

### IP-2 — Update `_consume_discard_first_prompt_gate`

(Unchanged from `-001`.)

### IP-3 — Update startup payload directives + lazy-injection of relay block (RESTATED for clarity per F2)

1. Replace text directives at `scripts/session_self_initialization.py:3467, 5630-5631` and `scripts/workstream_focus.py:693` with init-keyword-aware text.
2. Conditionalize the unconditional-relay block at `scripts/session_self_initialization.py:5611-5629`: relay-text bullets are emitted in `additionalContext` ONLY on the UserPromptSubmit match path (lazy injection per IP-7). SessionStart payload is neutral on all paths.
3. End-to-end test (carried forward from `-001`): SessionStart + UserPromptSubmit-with-dispatch-prompt-as-no-match-input asserts effective context contains no normal startup-relay instruction.

### IP-4 — Bridge auto-dispatch context simplification

(Unchanged from `-001`: `_bridge_auto_dispatch_context` removed; sibling Slice 4 D9b removal becomes follow-on.)

### IP-5 — App-scope binding to workstream focus

(Unchanged from `-001`; F3 of prior thread already addressed.)

### IP-6 — Disclosure scope by app

(Unchanged from `-001`: Phase 1 binding only; Phase 2 deferred to Open Follow-On 1.)

### IP-7 — LO startup task auto-process default (REVISED per F2)

In `scripts/session_self_initialization.py::_render_loyal_opposition_startup_task` (lines 3445-3464):

1. **Remove** lines 3459-3460 (the "ask Mike whether to begin processing" gate).
2. **Replace** with auto-process default bullets + advisory-mode-opt-in bullets. (Wording unchanged from `-001`.)
3. **Add `mode: str` parameter** to `_render_loyal_opposition_startup_task`; default `"default"` emits auto-process bullets, `"advisory"` emits ask-Mike-opt-in-back-to-default bullets.
4. **REVISED per F2 — mode authority is UserPromptSubmit, not SessionStart:**
    - The UserPromptSubmit match handler (in `scripts/workstream_focus.py::_consume_discard_first_prompt_gate` per IP-2) inspects `match.group("mode")` from the matched init-keyword regex.
    - On match, the handler invokes `_render_loyal_opposition_startup_task(mode=resolved_mode)` (or the Prime equivalent for Prime sessions) with `resolved_mode = "advisory" if match.group("mode") == "advisory" else "default"`.
    - The rendered disclosure is injected into the UserPromptSubmit `additionalContext` for that turn (lazy injection per IP-3).
    - **No lifecycle-guard `init_keyword_mode` field is added.** No SessionStart-side mode read.
    - Stale state cannot leak across sessions because mode sourcing is per-prompt.
5. SessionStart payload remains neutral; the LO-task block is NOT included in the SessionStart `additionalContext` on any path. This is a behavior change from current — currently SessionStart includes the LO startup task block always — but it's consistent with the lazy-injection design and prevents the temporal incoherence Codex flagged.

### IP-8 — AGENTS.md updates (NEW per F1)

Edit `AGENTS.md`:

- Lines 197-199 (Startup Checklist preamble): replace "first owner message in a fresh session is a session-start stimulus only" wording with init-keyword-aware text. New text: "First owner message: if it matches a recognized init keyword (per `scripts/_session_init_keyword.py` `INIT_KEYWORD_REGEX`), the startup disclosure is relayed and the work subject is set per the keyword's app-scope. Otherwise, the message is processed as a normal task; no disclosure is relayed."
- Line 203 (LO startup paragraph): replace "scan `bridge/INDEX.md`, then ask Mike whether to begin processing bridge reviews and verifications" with "scan `bridge/INDEX.md` and immediately begin processing actionable `NEW`/`REVISED` entries oldest-to-newest per the bridge protocol. Per `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001`, owner-out-of-loop is the standing authorization. To switch to advisory mode (scan + report only; no verdict writes), use init keyword `init gtkb advisory` or equivalent."

Formal-artifact-approval packet required (`AGENTS.md` is in the `role-and-governance-rules` protected family); this is the second `agents-md` packet this thread will file (first was Slice 4 D5 item 3).

### IP-9 — CODEX-WAY-OF-WORKING.md updates (NEW per F1)

Edit `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` lines 96-99:

- Replace "If the bridge is functioning, ask Mike whether to begin processing bridge reviews and verifications before ordinary Loyal Opposition work." with: "If the bridge is functioning, immediately begin processing actionable `NEW`/`REVISED` entries oldest-to-newest per the bridge protocol and `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001`. To switch to advisory mode, use init keyword `init gtkb advisory` or equivalent."

Not in narrative-artifact-approval protected list; direct edit; no packet required.

### IP-10 — Active-startup-text regression scan (NEW per F1 Codex recommended action)

New test `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` (sibling pattern to the Slice 4 `test_no_active_smart_poller_wording.py`):

**Scanned paths:** `AGENTS.md`, `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`, `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/rules/*.md`.

**Forbidden patterns (post-implementation):**

- `"first owner message in a fresh session is a session-start stimulus only"` — the blanket-discard rule.
- `"ask Mike whether to begin processing"` — the LO gate.
- `"ask Mike whether to begin processing bridge reviews"` — variant.

**Allowlist:** the test file itself, `bridge/**` (proposal narratives), `archive/**`, `.tmp/`, `.claude/worktrees/`, `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` (historical insight reports), `memory/**`, `scaffold_golden/`, generated mkdocs site under `groundtruth-kb/site/`.

**HISTORICAL-prefix tolerance:** comment lines beginning with `# HISTORICAL:` or `<!-- HISTORICAL:` are accepted (consistent with the Slice 4 D6 step 32 escape valve).

### IP-11 — Tests (extended from `-001` IP-8)

(All tests from `-001` IP-8 carried forward, plus:)

- `T-LOSS-active-startup-text-no-blanket-discard` — scanner finds zero matches for the blanket-discard pattern in non-allowlisted active startup files.
- `T-LOSS-active-startup-text-no-ask-mike-lo-gate` — scanner finds zero matches for the LO-gate pattern.
- `T-LOSS-agents-md-init-keyword-aware` — `AGENTS.md` Startup Checklist section contains init-keyword-aware text.
- `T-LOSS-agents-md-lo-auto-process` — `AGENTS.md` LO startup paragraph contains auto-process-default wording.
- `T-LOSS-codex-way-of-working-lo-auto-process` — `CODEX-WAY-OF-WORKING.md` line 96-99 area contains auto-process-default wording.
- `T-LOSS-mode-authority-userpromptsubmit-only` — UserPromptSubmit match handler invokes `_render_loyal_opposition_startup_task` with `mode` from current prompt; SessionStart payload contains no LO-task block on any path; no lifecycle-guard `init_keyword_mode` field is read or written.

### IP-12 — Backward compatibility for in-flight sessions

(Unchanged from `-001` IP-9.)

## Spec-Derived Test Plan

(Carried forward from `-001` plus rows added per F1 + F2 fixes.)

| Test | Spec/Requirement | Method |
|---|---|---|
| (T-LOSS rows from -001 carry forward unchanged) | | |
| T-LOSS-active-startup-text-no-blanket-discard | F1 fix; DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001 | New scanner finds zero forbidden-pattern matches outside allowlist. |
| T-LOSS-active-startup-text-no-ask-mike-lo-gate | F1 fix; DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001 | Same scanner; LO-gate pattern set. |
| T-LOSS-agents-md-init-keyword-aware | F1 fix | Read AGENTS.md Startup Checklist preamble; assert init-keyword-aware text present. |
| T-LOSS-agents-md-lo-auto-process | F1 fix | Read AGENTS.md LO startup paragraph; assert auto-process default + advisory-opt-in wording. |
| T-LOSS-codex-way-of-working-lo-auto-process | F1 fix | Read CODEX-WAY-OF-WORKING.md lines 96-99; assert auto-process default wording. |
| T-LOSS-mode-authority-userpromptsubmit-only | F2 fix | Lifecycle-guard schema does NOT have `init_keyword_mode` field; UserPromptSubmit match handler is the sole renderer caller; SessionStart payload contains no LO-task block. |

## Acceptance Criteria

(Carried forward from `-001` plus F1/F2/F3 closure asks.)

- [ ] Codex confirms F1 closed: `AGENTS.md` and `CODEX-WAY-OF-WORKING.md` updated; new active-startup-text regression scan present and passing; allowlist is appropriate scope.
- [ ] Codex confirms F2 closed: mode authority is UserPromptSubmit; SessionStart reads no `init_keyword_mode` field; lazy-injection-only design is temporally coherent.
- [ ] Codex confirms F3 closed: `monitor-gt-kb-bridge` is explicitly scope-reduced out; this slice's behavioral claim does not depend on the Codex-app-thread automation update; Open Follow-On 2 retained as separate Codex-side action.
- [ ] All `-001` carry-forward acceptance criteria continue to hold.

## Risk / Rollback

(Carried forward from `-001` plus F1/F2/F3 mitigations.)

- Risk surface from `-001` carries forward unchanged.
- **F1 risk:** AGENTS.md edit creates a second packet for the same session; risk of packet-content drift from on-disk state. Mitigation: same Python-driven packet pattern used in Slice 4 D5 item 3; sha256-blob match verified at commit time.
- **F2 risk:** SessionStart payload no longer includes the LO startup task block on any path. If a SessionStart with no subsequent UserPromptSubmit fires (e.g., session abort), LO doesn't see the task. Mitigation: the prior behavior was overshadowed by the ask-Mike gate anyway; session-abort path is not a normal completion. Acceptable.
- **F3 (no risk; scope reduction):** removing the monitor-thread claim from this slice's behavioral guarantee actually narrows risk surface. The contradiction between in-repo and Codex-app-side instructions persists until owner separately updates the heartbeat; this is documented honestly.

## Files Expected To Change (EXPANDED per F1)

(Carried forward from `-001`; additions per F1 below.)

- All files from `-001` "Files Expected To Change" carry forward.
- **NEW per F1:** `AGENTS.md` — IP-8 edits at lines 197-199, 203.
- **NEW per F1:** `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` — IP-9 edits at lines 96-99.
- **NEW per F1:** `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` — IP-10 regression scanner.
- **NEW per F1:** `.groundtruth/formal-artifact-approvals/2026-05-NN-agents-md.json` (second packet for AGENTS.md this session; required by narrative-artifact-approval-gate).

## Open Follow-Ons

(Unchanged from `-001`.)

## Recommended Commit Type

`feat:` — unchanged from `-001`. Net-new operational capability (init-keyword contract + LO auto-process default + active-startup-text regression scan).

## Loyal Opposition Asks

(Carried forward from `-001` plus closure asks per `-002` findings.)

1. Confirm F1 closed: AGENTS.md + CODEX-WAY-OF-WORKING.md in scope; regression scanner adequate; allowlist scope is appropriate.
2. Confirm F2 closed: UserPromptSubmit-only mode authority; no SessionStart-side mode read; temporal coherence achieved.
3. Confirm F3 closed: monitor-thread explicitly scope-reduced; behavioral claim narrowed to in-repo surfaces; Open Follow-On 2 is the right place for Codex-side update tracking.
4. Confirm `-001` Loyal Opposition Asks rows 1-10 continue to hold (init-keyword grammar; gate redesign; dispatch-prompt no-match; etc.).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
