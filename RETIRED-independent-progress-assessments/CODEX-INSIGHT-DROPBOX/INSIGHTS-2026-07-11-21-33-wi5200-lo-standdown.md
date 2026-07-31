# INSIGHTS 2026-07-11 21:33 UTC — WI-5200..5202 LO stand-down + incremental findings

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-11T21-13-34Z-loyal-opposition-B-0707b3
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatch loyal-opposition; bridge-review; effort max

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, ADR-CLOUD-HARNESS-TEMPLATE-001, SPEC-CENTRALIZED-DISPATCH-SERVICE-001
WIs: WI-5200, WI-5201, WI-5202
Thread: gtkb-wi5200-5202-generous-harness-repair

## Context (why this report exists)

This auto-dispatched Loyal Opposition worker (harness B, dispatch id
`2026-07-11T21-13-34Z-loyal-opposition-B-0707b3`) was routed to review the NEW
proposal `gtkb-wi5200-5202-generous-harness-repair-001`. Before I could file my
verdict, an **independent** peer Loyal Opposition session (harness B, but a
distinct interactive session context `4c34d164-9aef-4d9e-b0c3-17a9021a90c8`,
Claude Sonnet 5, `::init gtkb lo`) had already filed a valid **GO** at
`bridge/gtkb-wi5200-5202-generous-harness-repair-002.md`. The append-only
`write_bridge_file` guard correctly refused my v003 overwrite.

**Disposition: STAND DOWN.** The thread's latest status is GO (Prime-actionable).
Filing a competing verdict would be a non-independent duplicate. My independent
review reached the **same conclusion (GO)** on the same evidence, so the
convergence strengthens confidence in the peer verdict; there is no dissent to
preserve. This report preserves only the findings my review surfaced that the
peer verdict did not, so the implementer/verifier gains them before
implementation.

## Convergence with the peer GO (v002)

My independent review confirmed the peer's core evidence and overlaps two of its
findings:
- Both premises verified in canonical code: blank no-tool terminal exit
  (`scripts/cloud_harness_base.py` no-tool branch → `_final_text_from_message`
  raising on blank content); `DEFAULT_SESSION_TIMEOUT_SECONDS = 540.0` /
  `DEFAULT_MAX_TURNS = 40`; `OPENROUTER_WORKER_LIFETIME_SECONDS = 900` (F outer
  cap < inner session).
- Peer FINDING A (commingled dirty target_paths) == my commingled-finalization
  finding. Peer FINDING B (magnitude jump; record per-harness before/after) ==
  my native-A/B/C-outer-floor finding.

## Incremental findings NOT in the peer GO v002

### Finding 3 [P2] — F effective limits could silently stay old under CLI-over-config

- Claim: Implementation Plan step 1 introduces an "explicit-CLI-over-config
  resolver used by H and F," meaning registry-argv CLI flags win over
  `routing.toml`. F's current registry argv already carries explicit
  `--timeout 60 --session-timeout 5400 --max-turns 200`, and
  `[routing.openrouter]` has **no** `max_turns`. If the implementer sets the
  generous values only in `routing.toml` for openrouter, F's explicit argv wins
  and F stays at 60 s op / 5400 s session / 200 turns — a silent no-op for the
  exact harness (F) this proposal is meant to repair.
- Evidence: `harness-state/harness-registry.json` F headless argv;
  `.api-harness/routing.toml` `[routing.openrouter]` (no `max_turns`).
- Impact: WI-5200's F-envelope repair silently does not apply unless F's
  invocation surface is also updated. This is F-specific and distinct from the
  peer's generic "dispatcher does not thread routed `max_turns`" note.
- Recommended action: implementation report must show F's EFFECTIVE resolved
  limits become the intended generous values (a resolver/output test for F, or
  an updated F invocation surface via `gt harness set-invocation-surface`), not
  merely that `routing.toml` was edited.

### Finding 1 [P3] — Superseded WI-5066 F silent-stall cap should be acknowledged

- Claim: The proposal reverses the OpenRouter-F 900 s cap that
  `scripts/dispatcher_runtime.py` documents as "the bounded WI-5066 silent-stall
  cap proven by direct headless dispatch," plus the WI-4845/WI-5003 floors,
  without citing them. The deliberation protocol asks reviewers to flag
  superseding of prior decisions.
- Recommended action: the implementation report should acknowledge the
  superseded WI-5066 cap and show, with test evidence, that the retained inner
  controls (`PROVIDER_CALL_WALL_CLOCK_GRACE_SECONDS`, no-progress dedup, turn
  cap, session timeout) cover the silent-stall mode the 900 s cap was catching.

### Finding 4 [P3] — Blank-recovery has no consecutive-blank cutoff (hardening)

- Claim: the no-progress dedup (`MAX_REPEATED_TOOL_SIGNATURE_TURNS = 4`) applies
  only to repeated tool calls, not to blank no-tool responses. Under the new
  blank-recovery branch, a provider emitting blank every turn burns the full
  600-turn budget before failing closed. Bounded + fail-closed, so this is
  hardening, not a correctness gap.
- Recommended action: consider a consecutive-blank cutoff analogous to the
  repeated-tool-signature cutoff; at minimum ensure the blank-recovery test
  asserts eventual fail-closed termination, not just happy-path recovery.

## Bridge state (no action taken)

- `bridge/gtkb-wi5200-5202-generous-harness-repair-002.md` = GO (peer,
  independent session context). Thread is Prime-actionable. No further LO action.
- Work-intent claim acquired for the attempted write was released; no bridge
  file was written by this session.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
