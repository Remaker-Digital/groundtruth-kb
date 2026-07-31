NO-GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T20-49-09Z-loyal-opposition-B-a23808
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# WI-4837 Post-VERIFIED Prime-Side Finalization Recovery — Loyal Opposition Review

bridge_kind: lo_verdict
Document: gtkb-wi4837-post-verified-finalization-recovery
Version: 002
Responds to: bridge/gtkb-wi4837-post-verified-finalization-recovery-001.md
Reviewer: Loyal Opposition (Claude harness B; headless dispatcher-spawned session)
Date: 2026-07-05 UTC

---

## Verdict: NO-GO

The proposal targets a real surface and a real deadlock, is well-structured, links its
specifications cleanly (both preflights pass), and carries valid owner authorization. It is
NO-GO not because the work is unnecessary, but because its stated premise is factually
overstated and its design is unreconciled with an adjacent gate that already implements part
of the "missing" behavior. Left unresolved, the proposed design would cement an
authorization asymmetry between the two finalization gates rather than close it, and it may be
materially over-engineered for the requirement. These are pre-implementation design questions
that determine the entire shape of the code, so they should be settled before GO.

## What is strong (carry forward)

- Correct surface. The deadlock is real and is confirmed by inspection: a `git add` of an
  uncommitted protected path on a terminal-`VERIFIED` thread is blocked by
  `scripts/implementation_start_gate.py` (`gate_decision` -> `validate_targets`), because
  `_validate_packet` in `scripts/implementation_authorization.py` invalidates any packet once
  the thread is terminal `VERIFIED`. `git commit`/`git push` are exempt
  (`GIT_FINALIZATION_SUBCOMMANDS = {"commit", "push"}`, implementation_start_gate.py:140) but
  `git add` is NOT — it is explicitly a mutating command (`MUTATING_COMMAND_RE`,
  implementation_start_gate.py:157). So staging new/untracked verified files is genuinely
  blocked.
- Not a duplicate of the cited precedents. WI-4893 and WI-5004 touch the LO-side
  (`.claude|.codex|.cursor/skills/verify/helpers/write_verdict.py`,
  `.claude/hooks/bridge-compliance-gate.py`, `scripts/check_protected_commit_authorization.py`).
  WI-4837 touches the Prime-side auth gate (`implementation_authorization.py`,
  `implementation_start_gate.py`) — a distinct surface. Good separation.
- Spec linkage and preflights are clean (see Applicability Preflight below). Non-scope
  discipline is strong (fail-closed, exact paths, no destructive ops). Requirement Sufficiency,
  Risk/Rollback, and Recommended Commit Type are all present and coherent.

## Applicability Preflight

- packet_hash: `sha256:d7880e668ec8f0e907c8cae6eef6d7fef3e186317db5fa68ea88c16d70e74a0c`
- bridge_document_name: `gtkb-wi4837-post-verified-finalization-recovery`
- operative_file: `bridge/gtkb-wi4837-post-verified-finalization-recovery-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4837-post-verified-finalization-recovery`

## Clause Applicability

- Clauses evaluated: 5; must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4837-post-verified-finalization-recovery`

The preflights are clean; this NO-GO is a design/premise verdict, not a spec-linkage or
clause-gap verdict.

## Findings

### F1 [P1] The premise "no sanctioned Prime-side route" is overstated; the existing pre-commit terminal-VERIFIED clearance is not acknowledged or reconciled

Claim: The Summary states finalization of an already-`VERIFIED` file set "leaves no sanctioned
Prime-side route for an owner-waived finalization-only commit of already-verified files." That
is not accurate at the commit layer.

Evidence: `scripts/check_protected_commit_authorization.py._verified_authorization`
(lines 170-204) ALREADY clears a protected staged path at commit time when (a) a by-bridge
packet JSON names the thread, (b) the thread's live latest status is `VERIFIED`, and (c) the
path is within the GO-approved proposal's `target_paths`. It does this with NO owner-waiver —
it reads the packet JSON directly and does not call `_validate_packet`, so even the original
(now-expired) GO packet satisfies it. `_evaluate_protected_path` (lines 207-219) treats this as
a first-class "cleared" evidence class (`terminal_verified_bridge_thread`).

Risk/impact: The real gap is narrower than the proposal describes. It is ONLY the PreToolUse
staging step (`git add`) in `implementation_start_gate.py` that blocks; the pre-commit
`git commit` gate would already clear the same paths. Designing against the overstated premise
risks building more machinery than the actual gap requires and leaving the two gates
inconsistent (see F2).

Recommended action: Correct the premise to describe the real gap — the PreToolUse `git add`
step on a terminal-`VERIFIED` thread — and explicitly reconcile the new behavior with
`check_protected_commit_authorization.py._verified_authorization`.

### F2 [P2] Design inconsistency: the proposed owner-waiver packet mode is asymmetric with the existing gate, and a simpler parity alternative is not considered

Claim: The proposal requires a NEW packet mode (`post_verified_finalization_recovery`) plus a
mandatory `--owner-waiver-deliberation-id`, exact `--include` paths, and a live claim, to
authorize the SAME logical action (finalizing paths within the approved `target_paths` of a
terminal-`VERIFIED` thread) that the pre-commit gate already clears with NO owner-waiver.

Evidence: Pre-commit clearance predicate = (terminal `VERIFIED`) AND (path in approved
`target_paths`) — `check_protected_commit_authorization.py` lines 170-204. Proposed PreToolUse
predicate = (terminal `VERIFIED`) AND (owner-waiver deliberation) AND (exact include) AND (live
claim). The two gates would then disagree on what evidence authorizes finalizing the same path.

Risk/impact: This cements gate drift — the exact "de-control / inconsistency across a
functioning surface" the tracked-surface-bias directive warns against. It is also a plausible
over-engineering: a heavyweight new packet mode where a lightweight gate-parity clearance would
close the deadlock.

Recommended action (simpler alternative to evaluate): teach `implementation_start_gate.py` to
recognize the SAME terminal-`VERIFIED`-in-approved-`target_paths` clearance the pre-commit gate
already uses, bounded to simple git finalization commands (`git add`/`git commit`) — no new
packet mode, no owner-waiver deliberation, and symmetric with the existing gate. If the owner
DOES require a per-instance waiver (see F3), then the pre-commit gate's no-waiver clearance
should be tightened in the SAME slice so the two gates stay consistent. Either way, the proposal
must pick one evidence bar and apply it to both gates.

### F3 [P2] Requirement disambiguation: is a per-instance owner waiver actually required to finalize already-VERIFIED paths?

Claim: The proposal builds the recovery mode around a MANDATORY owner-waiver deliberation, but
the cited authority does not establish that requirement in general.

Evidence: `DELIB-20266123` (as described in the proposal's Prior Deliberations) waived the
Loyal-Opposition atomic-commit rule for WI-4813 and authorized Prime finalization of four
specific paths. That is an owner waiver of the LO-atomic-commit rule for one instance; it does
not, on its face, establish that EVERY post-`VERIFIED` finalization requires a fresh owner
waiver. The pre-commit gate embodies the opposite policy (automatic clearance, no waiver).

Risk/impact: This single requirement question determines the entire implementation shape
(waiver-gated packet mode vs. automatic gate-parity clearance). Resolving it after GO would risk
building the wrong design.

Recommended action: Disambiguate owner intent (this is a legitimate LO requirement-
disambiguation NO-GO per the operating model): (a) automatic clearance for paths within the
approved `target_paths` — parity with the pre-commit gate; or (b) per-instance owner waiver
required — and then reconcile/tighten the pre-commit gate accordingly. Capture the answer as an
owner decision before the REVISED proposal.

### F4 [P2] Blast radius of a validation-passing recovery packet is not scoped

Claim: To make a recovery packet usable by the PreToolUse gate, `_validate_packet` (or an
equivalent path) must PASS for a terminal-`VERIFIED` thread in recovery mode. The proposal does
not bound what that change does to the many OTHER consumers of the packet-validation path.

Evidence: `load_named_packet`/`list_named_packets`/`_validate_packet` in
`implementation_authorization.py` are consumed well beyond the PreToolUse gate — e.g.
`check_protected_commit_authorization.py._live_go_authorization` (calls `list_named_packets`
and treats any `valid=True` packet as GO evidence), `_named_packets_authorizing_targets`,
`list_named_packets_compact`, and dispatcher/reconcile surfaces. A recovery packet that newly
passes validation for a terminal thread could leak terminal-`VERIFIED` authorization into these
consumers (e.g. a `git add` on an UNRELATED protected path could be cleared as `live_go_packet`
because a validation-passing recovery packet exists).

Risk/impact: Silent widening of implementation authority is the most dangerous failure mode for
this gate — exactly the "accidentally reopening terminal VERIFIED for new implementation edits"
risk the proposal's own Risk section names, but via the packet-validation blast radius rather
than the gate command classification.

Recommended action: The REVISED proposal must specify that recovery-mode packets are inert to
(or explicitly and narrowly handled by) EVERY existing consumer of the packet-validation path,
with a named regression per consumer. If the simpler gate-parity approach (F2) is taken,
`_validate_packet` need not change at all, which removes this blast radius entirely — another
reason to prefer it.

### F5 [P3] Verification plan omits the end-to-end two-gate finalization path

Claim: Finalization requires BOTH gates to pass — the PreToolUse `git add` gate AND the
pre-commit `git commit` gate (`check_protected_commit_authorization.py`). The verification plan
and acceptance criteria exercise only `implementation_authorization.py` /
`implementation_start_gate.py` in isolation.

Evidence: The Spec-Derived Verification Plan and Acceptance Criteria enumerate unit behavior of
the new packet mode and gate command classification; neither runs a full staging -> commit
sequence through `check_protected_commit_authorization.py`.

Risk/impact: A recovery packet could authorize `git add` yet the resulting commit could
interact unexpectedly with the pre-commit gate (see F1/F4), leaving the deadlock only
half-closed and undetected by the proposed tests.

Recommended action: Add an end-to-end verification step demonstrating that a recovery-mode
finalization stages AND commits successfully through both gates (including
`check_protected_commit_authorization.py`), and that it does NOT clear an unrelated protected
path (F4 negative control).

## Recommended Revision Path (summary)

1. Restate the gap precisely: only the PreToolUse `git add` staging step blocks; the pre-commit
   gate already clears terminal-`VERIFIED` paths within approved `target_paths`.
2. Resolve F3 with the owner (waiver-required vs. automatic parity) via AskUserQuestion, and
   record the decision.
3. Prefer the gate-parity approach (F2): mirror `check_protected_commit_authorization.py`'s
   terminal-`VERIFIED` clearance in `implementation_start_gate.py`, bounded to simple git
   finalization commands — unless the owner decision in step 2 requires a waiver, in which case
   apply that same bar to BOTH gates.
4. If a validation-passing packet mode is retained, scope its blast radius across every
   packet-validation consumer with per-consumer regressions (F4).
5. Add the end-to-end two-gate verification (F5).

## Prior Deliberations

Reviewed the proposal's cited lineage: `DELIB-20266123`, `DELIB-20266102`,
`DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL`,
`bridge/gtkb-wi4893-false-verified-finalization-recovery-004.md`, and
`bridge/gtkb-wi5004-verified-finalization-include-set-repair-006.md`. Read
`bridge/gtkb-wi4893-false-verified-finalization-recovery-001.md` in full to confirm the
precedent touches the LO-side verify helper / commit-authorization gate, not the Prime-side
implementation-start gate. No prior deliberation was found that resolves the F3 requirement
question (per-instance owner waiver vs. automatic clearance) for the Prime-side surface.

## Methodology / Evidence Trail

Files inspected: `bridge/gtkb-wi4837-post-verified-finalization-recovery-001.md`;
`scripts/implementation_authorization.py` (packet lifecycle, `approved_files_for_go`,
`_validate_packet`, `_verified`/named-packet loaders, `clear_active_packet_if_terminal`);
`scripts/implementation_start_gate.py` (`gate_decision`, `changed_paths`, `_is_safe_command`,
`_is_simple_git_finalization_command`, `GIT_FINALIZATION_SUBCOMMANDS`, `MUTATING_COMMAND_RE`);
`scripts/check_protected_commit_authorization.py` (`_verified_authorization`,
`_live_go_authorization`, `_evaluate_protected_path`);
`bridge/gtkb-wi4893-false-verified-finalization-recovery-001.md`.
Commands run: `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` for this
bridge id (both clean). Bridge state re-checked immediately before filing: only `-001` present,
latest status NEW (actionable). Review independence: reviewer session context differs from the
proposal author's `author_session_context_id` (Codex A).

## Owner Decisions / Input

None required to file this LO proposal-review verdict. F3 raises an owner decision that Prime
Builder must obtain (via AskUserQuestion) before the REVISED proposal, not one this reviewer
can or should make.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
