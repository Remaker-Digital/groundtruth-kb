# INSIGHTS — WI-5199 H-functional-proof: dispatched B worker STAND-DOWN (FINDING-A race materialized)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-11T20-38-23Z-loyal-opposition-B-390d3b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless dispatched Loyal Opposition worker (harness B); bridge auto-dispatch; full GT-KB governance

Specs: SPEC-CENTRALIZED-DISPATCH-SERVICE-001, SPEC-DISPATCHER-CONTROL-SURFACE-001, GOV-HARNESS-ONBOARDING-CONTRACT-001, ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001, GOV-FILE-BRIDGE-AUTHORITY-001
WIs: WI-5199
Bridge thread: gtkb-wi5199-fd-evidence-h-functional-proof (001 NEW, 002 GO, 003 NEW/report)
Dispatch id: 2026-07-11T20-38-23Z-loyal-opposition-B-390d3b

## Claim

I am a headless-dispatched **B (Claude) Loyal Opposition** worker that the
dispatcher routed to review report `-003` of
`gtkb-wi5199-fd-evidence-h-functional-proof`. **I am standing down without
authoring any GO/NO-GO/VERIFIED verdict.** The bridge chain explicitly reserves
this proof verdict for harness **H (Alibaba Cloud Studio)**, and a B-authored
verdict would defeat the entire purpose of WI-5199. No bridge mutation was
performed by this session.

## Why standing down is the only correct B action (evidence)

1. **Report 003 reserves the verdict for H.** `bridge/gtkb-wi5199-fd-evidence-h-functional-proof-003.md`:
   "Any B worker that nevertheless sees this report should stand down because the
   bridge chain explicitly reserves this proof verdict for H." Loyal Opposition
   Ask #5: "Publish a canonical verdict with `author_harness_id: H`."
2. **The GO verdict (002) pre-authorized exactly this stand-down.** FINDING A
   [P3]: "any future auto-dispatched B session handed this report should stand
   down in favor of H per this thread's stated intent so H is the harness that
   produces the committed verdict."
3. **Owner authorization scopes the proof to H.** `DELIB-202666172`
   ("Authorize WI-5199 + H proof") authorizes *one genuine H proof dispatch,
   with B routing restored afterward*. The acceptance criteria in 003 require
   "H publishes a substantive canonical committed verdict" with
   `author_harness_id: H`. A B verdict would falsely satisfy / destroy that
   criterion.

## The FINDING-A race predicted in 002 has materialized (live evidence)

- `gt bridge dispatch status --json` → `selected_by_role.loyal-opposition = [B]`
  only (`can_receive_dispatch: true`); **H is not in the selected LO set**
  (H currently ineligible).
- `.gtkb-state/bridge-poller/dispatch-state.json` → `loyal-opposition:B`
  `circuit_breaker_tripped: true` at `2026-07-11T20:28:37Z`, `failure_count: 1`.
- No `-004` H verdict exists; the whole thread (`-001`, `-002`, `-003`) is still
  untracked/uncommitted.

Interpretation: the proof's restoration step ("restore B eligible once H is
*in-flight*") fired while report 003 was still a live `NEW`. The dispatcher
therefore re-selected **B** for the still-actionable NEW report, and H — now
ineligible — can no longer pick up 003 under current routing. The timing
assumption `in-flight != verdict-committed` is the root cause, exactly as
FINDING A warned.

## Why B cannot resolve this itself

- Re-flipping dispatcher eligibility (enable H, disable B) so 003 routes to H is
  a **Prime Builder**, PAUTH-scoped governed-CLI action
  (`gt bridge dispatch config set-eligibility`), not a Loyal Opposition action.
  B holds no implementation-start packet for `target_paths`
  `["groundtruth.db","harness-state/harness-registry.json"]` and this is outside
  the LO role.
- This is a headless worker; it cannot ask the owner in prose.

## Risk / impact

- Report 003 remains `NEW` with **only B selected**, so absent intervention the
  dispatcher will keep re-routing 003 to B (re-dispatch loop). B's circuit
  breaker already tripped once. Record-and-stop by a single B worker does not by
  itself hold this loop across the LO pool.
- The automated H functional-proof handoff **failed** due to the FINDING-A race;
  the proof is not yet obtained and must be re-attempted.

## Recommended action (Prime Builder / owner)

1. **Prime re-attempt the H handoff** under the same live GO (`-002`), the same
   `go_implementation` work-intent claim (row 31197), and the same
   implementation-start packet
   (`sha256:2136d11f…`): re-run `set-eligibility H --can-receive-dispatch`, then
   `set-eligibility B --no-can-receive-dispatch`, confirm
   `selected_by_role.loyal-opposition = [H]`, and leave that state in place until
   **H commits its `-004` verdict** — not merely until H is "in-flight" — before
   restoring B. Delaying B restoration to *after H's verdict commit* closes the
   FINDING-A window.
2. Consider clearing / accounting for B's tripped circuit breaker for this
   document so it does not mask the re-attempt.
3. If H again fails to launch or exits unsuccessfully, follow proposal 001 §5:
   restore B first, preserve failure telemetry, and route the thread back to
   Prime for NO-GO/defect remediation — **not** to a B substitute verdict.

## Owner decision needed

Yes — the H functional proof cannot be completed by a headless B worker. It needs
a Prime Builder re-attempt of the governed eligibility handoff (or explicit owner
guidance to change the proof approach). A B-authored verdict must not be used to
close this thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
