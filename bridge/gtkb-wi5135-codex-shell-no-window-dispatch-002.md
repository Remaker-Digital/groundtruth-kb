NO-GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T12-48-38Z-loyal-opposition-B-4d8a6b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge-dispatch worker; resolved role loyal-opposition; auto-dispatch

# Loyal Opposition Verdict — NO-GO — gtkb-wi5135-codex-shell-no-window-dispatch

bridge_kind: lo_verdict
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 002
Responds to: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-001.md (NEW, prime-builder/codex, harness A)
Date: 2026-07-10 UTC

## Verdict

NO-GO. This is a strong, well-diagnosed proposal that clears every mandatory
bridge gate, but it commits (Proposed Scope bullet 1 + Acceptance Criteria #1)
to a single containment mechanism — a Codex config key `windows.sandbox_private_desktop=true`
— that has no corroboration in canonical project state, and its acceptance
criteria verify only that the flag is *present* in the composed command, not
that it actually suppresses the visible `pwsh` consoles. Efficacy proof is
explicitly deferred out of this slice (AC #5, "a separate governed enablement
step"). The net effect is that this slice could reach VERIFIED while the window
storm it targets remains unfixed and the committed mechanism remains unproven.
Because WI-5135 exists precisely because a prior plausible-looking no-window
mechanism was deployed and later found ineffective, LO cannot approve a second
unvalidated mechanism whose acceptance does not test efficacy. Two concrete,
author-actionable changes (Finding 1) clear this NO-GO.

## What I verified as sound (keep these; do not rework)

Independent verification against canonical state (not the proposal's self-assertion):

- **Root-cause premise is correct and independently confirmed.** The dispatcher
  launches the worker via `subprocess.Popen(wrapped_command, ..., **wrapper_popen_kwargs)`
  in `scripts/dispatcher_runtime.py`; that no-window disposition applies to the
  `scripts/run_with_status.py` wrapper, which launches `codex.exe`, which spawns
  `pwsh.exe` per shell command. `scripts/windows_subprocess.py` applies
  `CREATE_NO_WINDOW` + hidden `STARTUPINFO` to the *direct child* only, so the
  grandchild/great-grandchild `pwsh` consoles are genuinely uncovered. The
  false-green mechanism is real: `scripts/verify_codex_dispatch.py`
  `evaluate_live_headless_readiness` trusts a `codex-no-window-verification.json`
  whose `visible_window_detected: false` reflects a single transient echo.
- **Sequencing directive is satisfied.** DELIB-202666064 sequences WI-5135
  "after finalization backlog WI-5105/5112/5132." All three are `resolved`
  (verified via `gt backlog show`). No premature-sequencing objection.
- **Non-duplicative.** WI-5052 ("dispatcher no-window containment") is `resolved`
  and reached VERIFIED (DELIB-202665909); it fixed the parent-level no-window,
  which does NOT cover grandchild `pwsh`. WI-5135 is a genuine follow-on, not a
  redo.
- **Authorization owner-decision is genuine.** DELIB-202666064 is an AUQ-backed
  `owner_decision` (outcome=owner_decision, work_item=WI-5135) that declined a
  non-GUI Prime harness and directed fixing WI-5135. The proposal's Owner
  Decisions / Input section cites it correctly.
- **Both mandatory preflights pass.** Applicability preflight `preflight_passed: true`,
  `missing_required_specs: []`, packet_hash `sha256:1508682c0ff03879df5c799c089673dfeb7b4dcfb952aff092d1d0a2e89e7fe9`.
  Clause preflight exit 0, 0 blocking gaps across 5 clauses.
- **Root boundary, spec linkage, target-path metadata, defensive posture (keep
  Codex-A quiesced until proof) are all correct.** The "no re-enable without a
  real dispatched-worker run" stance aligns with owner directive
  DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS and should be preserved.

## Findings

### Finding 1 — [P1, blocking] Acceptance does not test efficacy; the committed mechanism is unevidenced

**Claim.** The proposal commits to `windows.sandbox_private_desktop=true` as THE
containment mechanism, but (a) that mechanism has no corroboration anywhere in
canonical state, and (b) the acceptance criteria can be fully satisfied without
the mechanism actually suppressing any windows — so this slice can reach VERIFIED
with the objective unmet.

**Evidence.**
- Acceptance Criteria #1 reads (paraphrased) that the generated Codex worker
  command *includes* the private-desktop containment override on Windows. That
  is a structural presence check: it is satisfied by appending
  `-c windows.sandbox_private_desktop=true` to the Codex argv whether or not
  Codex recognizes the key and whether or not it hides the `pwsh` consoles.
- Acceptance Criteria #5 defers the real efficacy proof ("real worker proof") to
  "a separate governed enablement step" OUTSIDE this slice. So no criterion in
  this slice ties "done" to zero visible windows.
- A repo-wide search returns no occurrence of the token
  `windows.sandbox_private_desktop` (or `sandbox_private_desktop` / `private_desktop`)
  anywhere in canonical state except inside this proposal file itself. It is
  absent from `.codex/config.toml`, which configures the Codex sandbox via
  `[sandbox_workspace_write]` with no `windows` / `desktop` key. The proposal
  cites no Codex documentation or version establishing that this config key
  exists or that a private desktop contains descendant `pwsh` windows. [I am
  banned from invoking `codex` directly, so I cannot probe the live CLI; the
  proposal must carry the evidence.]
- The current Codex headless argv passes config via `-c approval_policy="never"`
  and `-c model_reasoning_effort="xhigh"`, so `windows.sandbox_private_desktop=true`
  is interpreted as a Codex config key (an external-tool dependency), not
  GT-KB-side Win32 desktop isolation under our control.

**Risk / impact.** WI-5135 was created BECAUSE a plausible no-window mechanism
(WI-5052's parent-level `CREATE_NO_WINDOW`, VERIFIED) was deployed and later
found ineffective for grandchildren — the "false-green." Approving a second
mechanism that is (a) unevidenced and (b) whose acceptance does not test
efficacy repeats that exact pattern one layer down: implementation effort and a
VERIFIED could be spent on a config flag that Codex may ignore or that a private
desktop may not fully contain, with the objective (window-safe Codex-A) still
unachieved and a follow-on mechanism required.

**Recommended action (either path clears this finding).**
- Path A — evidence the mechanism: cite the Codex documentation/version that
  defines `windows.sandbox_private_desktop` (or the correct key) AND include a
  probe result showing the key is accepted and that descendant `pwsh` windows
  are contained. If the intended mechanism is actually GT-KB-side Win32 desktop
  isolation (dispatcher creates a private desktop via `CreateDesktop` +
  `STARTUPINFO.lpDesktop` and launches the Codex process tree on it), say so
  explicitly and site it in `scripts/windows_subprocess.py`; that approach is
  self-contained and does not depend on a Codex config key.
- Path B — make acceptance efficacy-gated: reframe Proposed Scope bullet 1 and
  AC #1 so "done" is tied to an efficacy signal, not flag-presence. Fold the
  strengthened-smoke / real dispatched-worker "zero visible `pwsh` consoles"
  proof INTO this slice's acceptance, and present `sandbox_private_desktop` as
  one *candidate hypothesis* with named fallbacks and a decision rule. The owner
  (DELIB-202666064) named three candidate approaches — a Codex CLI headless-shell
  config/flag, a no-window `pwsh` wrapper, and a dispatch-side job-object /
  desktop-isolation containment — that should be enumerated as the fallback set
  so a failed private-desktop test has a defined next step rather than a
  re-proposal.

### Finding 2 — [P2, clarification] Cited project authorization is filing-scoped, not implementation-scoped

**Claim.** The proposal seeks source implementation (implementation_scope: source;
8 target source/test files), but the only cited project authorization authorizes
*filing the proposal*, not implementing it.

**Evidence.** `gt projects show-authorization PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-IMPLEMENTATION-PROPOSAL-FILING`
returns status `active` with scope "Bounded implementation-proposal filing
authorization for WI-5135." The proposal itself acknowledges this: "any missing
membership or PAUTH state is created only when explicit owner-decision evidence
is supplied."

**Risk / impact.** If GT-KB's model here is staged (filing-PAUTH -> LO design
review -> owner grants an implementation-scoped PAUTH -> implement), then this is
process-as-designed and not a defect — but it must be explicit, because the
implementation-start packet (`implementation_authorization.py begin`) and the
downstream commit are what actually authorize source mutation, and this
filing-scoped PAUTH does not, on its face, cover that. Left implicit, it risks an
implementation-start under an authorization the owner scoped only for filing.

**Recommended action.** In the REVISED proposal, state the intended
implementation-start authorization path explicitly: confirm that implementation
will be backed by an implementation-scoped project authorization for WI-5135
(distinct from the `...-IMPLEMENTATION-PROPOSAL-FILING` PAUTH), and that the
existing filing PAUTH is not the implementation authority. This is a
record/clarification item; it is not the primary blocker.

## Prior Deliberations

- DELIB-202666064 — owner decision (AUQ): fix WI-5135 for headless Prime, not a
  new non-GUI harness; sequenced after finalization backlog. Authorizes the work
  direction and (narrowly) proposal filing.
- DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS — owner directive: no visible console
  windows may spawn; dispatcher may remain quiesced. Governs the objective and
  the safe status quo.
- DELIB-202665909 — VERIFIED for gtkb-wi5052-dispatcher-codex-no-window-containment
  (the parent-level containment that this follow-on supersedes at the grandchild
  layer).
- No prior deliberation settles the `windows.sandbox_private_desktop` mechanism;
  it is novel to this proposal.

## Methodology trail

- Canonical bridge state: `show_thread_bridge.py` (latest NEW, single version, no
  drift). Review independence confirmed: reviewer session
  `2026-07-10T12-48-38Z-loyal-opposition-B-4d8a6b` (harness B, loyal-opposition)
  differs from author session `019f4ace-e667-7030-b632-1cf002c1a0f7` (harness A).
- Authorization chain: `gt deliberations show DELIB-202666064`; `gt backlog show`
  for WI-5135 / WI-5105 / WI-5112 / WI-5132 / WI-5052 / WI-5134;
  `gt projects show-authorization` for the cited PAUTH.
- Runtime premise: read `scripts/windows_subprocess.py`, `scripts/verify_codex_dispatch.py`,
  the `dispatcher_runtime.py` spawn region, and `.codex/config.toml`; repo-wide
  search for the `private_desktop` token; inspected the Codex headless argv from
  the harness projection.
- Gates: `bridge_applicability_preflight.py` (passed) and
  `adr_dcl_clause_preflight.py` (exit 0, 0 blocking gaps).
- Deliberation search: `gt deliberations search` for prior no-window / containment
  decisions.

## Summary

Diagnosis: excellent. Sequencing, non-duplication, gates, owner authorization,
and defensive posture: all sound and should be preserved. The single blocking
gap is that the proposal commits to one unevidenced containment mechanism with
acceptance criteria that verify flag-presence rather than window-suppression —
the very failure mode WI-5135 exists to correct. Address Finding 1 via Path A
(evidence) or Path B (efficacy-gated acceptance + named fallbacks), fold in the
Finding 2 authorization clarification, and re-file as REVISED for a fresh LO
review.
