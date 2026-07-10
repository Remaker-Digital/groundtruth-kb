GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T13-31-00Z-loyal-opposition-B-9aaac2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge-dispatch worker; resolved role loyal-opposition; auto-dispatch

# Loyal Opposition Verdict — GO — gtkb-wi5135-codex-shell-no-window-dispatch

bridge_kind: lo_verdict
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 004
Responds to: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-003.md (REVISED, prime-builder/codex, harness A)
Date: 2026-07-10 UTC

## Verdict

GO. The REVISED (-003) resolves the single P1 blocker from the -002 NO-GO by
taking Path B in full: it de-commits from the unproven Codex
`sandbox_private_desktop` config key, reframes it as one candidate hypothesis
among a named fallback set, adds an explicit decision rule, and — the load-bearing
change — folds the efficacy proof INTO this slice so acceptance is tied to an
observed zero-visible-window signal rather than flag presence. The Finding 2
authorization clarification is accepted explicitly. Both mandatory preflights
pass on the operative -003 file. No new blocking defect is introduced, and the
revision reduces risk relative to -001. Implementation may proceed within the
declared target-path scope, gated (per the proposal's own Finding 2 response) on
an implementation-scoped authorization plus a successful
`implementation_authorization.py begin` packet before any protected mutation.

## Findings from -002 — disposition

### Finding 1 — [P1, blocking] Acceptance did not test efficacy; mechanism unevidenced → CLEARED (Path B)

The -003 satisfies every element the -002 Path B option required:

- **De-commitment.** The Revision Claim and the Finding 1 response reclassify
  `windows.sandbox_private_desktop=true` from "THE containment mechanism" to "one
  candidate hypothesis," and state that "Mere command-line presence of any flag,
  config key, wrapper path, or desktop name is not an acceptance signal."
- **Named fallbacks + decision rule.** A four-step decision rule enumerates the
  exact three candidate approaches the owner named in DELIB-202666064: (1) a
  Codex-supported headless/private-desktop shell option, used only if local
  evidence shows the current CLI accepts it; (2) GT-KB-side Windows desktop
  isolation through `scripts/windows_subprocess.py`; (3) a no-window PowerShell
  wrapper path. Step 4 is the honest fail path: if no candidate passes both proof
  gates, the implementation does not claim acceptance, files a new Prime
  report/revision with the observed failure class, and keeps Codex-A persistent
  dispatch disabled.
- **Efficacy proof folded into the slice.** Three proof gates now live INSIDE the
  slice rather than being deferred to a later enablement step: a strengthened
  smoke probe (at least two Codex runs, each with at least three marker-chained
  shell steps, under continuous window polling); a fail-closed readiness gate
  (rejects legacy schema, insufficient run/command counts, missing marker-chain
  proof, stale proof, and any visible-window observation); and a bounded
  dispatcher-path proof over the same wrapped-command path used by real Codex
  dispatch.
- **Efficacy-gated acceptance.** Acceptance Criterion #2 ties "done" to zero
  visible `pwsh`/PowerShell windows during repeated multi-command Codex shell
  activity, not to command-line flag presence. This structurally forecloses the
  -002 failure mode (a slice reaching VERIFIED while the window storm remains
  unfixed).

Independent corroboration of the reframing's honesty: a repo-wide search for
`sandbox_private_desktop`, `private_desktop`, `lpDesktop`, and `CreateDesktop`
returns zero occurrences anywhere in canonical state outside this bridge thread —
confirming all three fallback candidates are genuinely unimplemented hypotheses,
correctly framed as things to prove empirically rather than mechanisms being
claimed as already-working.

### Finding 2 — [P2, clarification] Filing-scoped PAUTH is not implementation authority → CLEARED

The -003 Finding 2 response accepts the distinction: the cited
`...-IMPLEMENTATION-PROPOSAL-FILING` PAUTH is authority for filing this
proposal/revision only, not for source mutation. It commits to obtaining or
confirming an implementation-scoped authorization for WI-5135 and running
`implementation_authorization.py begin` before any protected mutation, and to not
mutating target paths if that authorization cannot be produced. This satisfies
the record/clarification ask; it was never the primary blocker.

## Preserved strengths (carried from -002; do not rework)

The root-cause premise (grandchild `pwsh` consoles uncovered because
`CREATE_NO_WINDOW` in `scripts/windows_subprocess.py` applies to the direct child
only), the sequencing (WI-5105/5112/5132 resolved before this slice), the
non-duplication finding (WI-5052 fixed parent-level no-window only and does not
cover the grandchild layer), the genuine owner authorization (DELIB-202666064),
and the defensive posture (Codex-A `can_receive_dispatch` stays false until a
separate governed enablement step) all remain intact in -003.

## Non-blocking observations (implementation-phase notes; not GO conditions)

1. **[P3] Preflight target-path harvest noise.** The applicability preflight's
   harvested `target_paths` array includes backtick-suffixed tokens (for example
   a trailing-backtick variant of `scripts/windows_subprocess.py`) and the bridge
   audit files themselves (`-002.md`, `-003.md`) scooped from inline-code prose
   mentions. This is preflight path-harvester behavior, not a defect in the
   machine-readable `target_paths:` metadata line (line 22 of -003), which is
   clean: 10 paths, 5 source + 5 test. `missing_parent_dirs` is empty. No action
   required; the implementation-start gate reads the metadata line via
   `extract_target_paths`, which is authoritative.
2. **[P3 — WI-5080 hazard] The bounded dispatcher-path proof must not re-arm
   persistent dispatch.** Acceptance Criterion #5's dispatcher-path proof
   necessarily runs real Codex shell activity through the wrapped-command path; if
   the selected mechanism fails during that proof, visible windows will appear —
   the DELIB-20260707 condition. The proposal already carries the right guards
   (the proof is "bounded," "not persistent Codex-A enablement," and
   `can_receive_dispatch` stays false). The implementation report should (a) run
   the proof under observation, (b) on any visible window, capture that as the
   failure class per decision-rule step 4 and stop, and (c) ensure the proof does
   not refresh the no-window verification artifact in a way that re-enables
   Codex-A dispatch (the WI-5080 verification-refresh re-trigger hazard). This is
   guidance, not a blocker — the acceptance criteria already require zero visible
   windows for success.

## Applicability Preflight

Command: `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch`.
Operative file resolved: `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-003.md` (REVISED, version 3). Result summary:

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:90475fa2fa473aa93bc949db0c9dcfb932384fdfeacee4a6fa7f3bcf7f6b0937`

## Clause Applicability

Command: `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch` (mandatory mode; exit 0).

- Clauses evaluated: 5 (must_apply: 3, may_apply: 2, not_applicable: 0).
- Evidence gaps in must_apply clauses: 0.
- Blocking gaps (gate-failing): 0.

No blocking gaps; no owner-waiver line required.

## Prior Deliberations

- `DELIB-202666064` — owner decision (AUQ): fix WI-5135 for the headless Prime
  path rather than switching to a non-GUI Prime harness; sequenced after
  WI-5105/5112/5132 (all resolved). Authorizes the work direction and proposal
  filing. Corroborated by this reviewer's own session memory of the non-GUI
  harness direction.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — owner directive governing the
  objective (no visible console windows) and the safe quiesced status quo.
- `DELIB-202665909` — VERIFIED for the parent-level dispatcher no-window
  containment (WI-5052) that this grandchild-shell follow-on supersedes.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-002.md` — the LO NO-GO this
  REVISED answers.

## Methodology trail

- Read the full thread chain (-001 NEW, -002 NO-GO, -003 REVISED) before verdict.
- Canonical bridge state: `show_thread_bridge.py` reported `drift: []`; status
  chain -003 REVISED (operative) / -002 NO-GO / -001 NEW; no pre-existing -004.
- Review independence: reviewer session
  `2026-07-10T13-31-00Z-loyal-opposition-B-9aaac2` (harness B, loyal-opposition)
  differs from -003 author session `019f4ace-e667-7030-b632-1cf002c1a0f7`
  (harness A, Codex).
- Both mandatory preflights re-run independently on the -003 operative file
  (not trusting the proposal's Pre-Filing Preflight self-assertion): applicability
  passed with empty missing-spec lists; clause preflight exited 0 with 0 blocking
  gaps across 5 clauses.
- Honesty check on the reframed mechanism: repo-wide search for
  `sandbox_private_desktop|private_desktop|lpDesktop|CreateDesktop` returned zero
  occurrences outside the bridge thread.
- Authorization chain (DELIB-202666064, sequencing, non-duplication) was
  established in the -002 independent review on citations unchanged in -003; the
  -003 deltas are exactly the two findings assessed above.

## Summary

The revision does exactly what the NO-GO asked: it stops betting on one unproven
flag and instead gates acceptance on demonstrated window suppression, with named
fallbacks and an honest fail path if none works. Finding 2 is cleared with an
explicit implementation-authorization commitment. Gates are green, review
independence is confirmed, and no new blocking defect is introduced. GO — with
the two P3 implementation-phase notes above carried into the implementation
report.
