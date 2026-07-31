# Loyal Opposition Insight — Second independent review of WI-5027 (post-GO advisory)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T17-54-12Z-loyal-opposition-B-eb4982
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; explanatory output style; resolved role loyal-opposition via ::init gtkb lo

Specs: GOV-WORK-TREE-HYGIENE-001, GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
WIs: WI-5027, WI-4979, WI-4356
Bridge: bridge/gtkb-wi5027-worktree-finalization-triage-001.md (proposal), -002.md (peer GO)
Reviewer: Loyal Opposition (claude, harness B), session 2026-07-05T17-54-12Z-loyal-opposition-B-eb4982
Date: 2026-07-05 UTC

## Why this report exists (not a bridge verdict)

The dispatcher fanned the same NEW proposal (`gtkb-wi5027-worktree-finalization-triage-001`)
to two Loyal Opposition harnesses. Antigravity (harness C) filed **GO** at `-002.md`
(11:08) while this Claude LO session (harness B) was independently reviewing and
concluding **NO-GO**. The thread's latest status is now GO and is no longer
LO-actionable, so this session does **not** file a competing `-003` verdict
(that would create a two-LO GO/NO-GO oscillation with no owner available to
adjudicate in a headless run). Instead, this report preserves the concerns the
GO did not surface, as advisory input for Prime Builder's implementation of the
already-GO'd WI-5027 and for owner awareness.

The peer GO is a valid independent review (harness C, session dad818f3…, distinct
from the proposal author). Its mechanical checks (root boundary, applicability
preflight, clause preflight) match this session's and are correct. The gaps below
are architectural-fit / backlog-coordination dimensions the GO's checks did not
reach.

## Finding 1 [P2] — Standalone script fragments the GOV-WORK-TREE-HYGIENE-001-designated authoritative surface

- Claim: The proposal's `target_paths` add a top-level standalone
  `scripts/worktree_finalization_triage.py` with its own CLI entry point, but
  `GOV-WORK-TREE-HYGIENE-001` (cited by the proposal AND listed in the governing
  PAUTH's `included_spec_ids`) already designates the authoritative work-tree
  hygiene surfaces as `scripts/hygiene/stray_detector.py`, the `gt hygiene`
  command group, and the doctor check.
- Evidence: `gt spec show GOV-WORK-TREE-HYGIENE-001` → "The authoritative
  implementation surfaces are the verified WI-4356 slices: 1. Slice A read-only
  detector: scripts/hygiene/stray_detector.py. 2. Slice B dry-run CLI:
  gt hygiene strays. 3. Slice C doctor visibility check." `gt hygiene --help`
  already exposes `strays` (read-only work-tree/stash/orphaned-worktree triage),
  `supersession-scan`, `sweep`; `ls scripts/hygiene/` is a populated package.
  The proposed planner is read-only work-tree triage — the same problem domain as
  `gt hygiene strays`. The governing PAUTH's `allowed_mutation_classes` include
  `cli_extension`, and its `scope_summary` authorizes "reporting/CLI/test
  support" — i.e., the authorized delivery mechanism is a CLI extension.
- Severity: P2 (governance drift / surface fragmentation; not a correctness or
  safety defect — the proposal is read-only/dry-run).
- Impact: Implementing as a parallel top-level script splits the work-tree
  hygiene surface across two entry points, contradicting the cited spec's
  authoritative-surface clause and the GT-KB tracked-surface / simplicity bias.
- Recommended action (adoptable under the existing GO): Site the planner under
  `scripts/hygiene/` (e.g. `scripts/hygiene/finalization_triage.py`) and expose
  it as a `gt hygiene` subcommand (e.g. `gt hygiene finalization`), reusing the
  `gt hygiene strays` read-only detector pattern. This is a strengthening move
  within the authorized `cli_extension` scope and does not require a fresh
  review. If finalization-triage is intentionally distinct from stray-triage,
  document that distinction and justify the separate surface against the spec's
  authoritative-surface clause.

## Finding 2 [P2] — Unreconciled scope overlap with open sibling Batch A1 items WI-4979 / WI-4356

- Claim: WI-5027 was approved (DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL)
  alongside WI-4979 and WI-4356 in the same Batch A1, and its "per-stream
  finalization triage" overlaps their scope without reconciliation.
- Evidence: `gt backlog show` → WI-4979 ("Work-tree hygiene Slice E: generalized
  recurring actuator with auto-resolve triage", subproject "Work-Tree Hygiene",
  open) and WI-4356 ("recurring work-tree hygiene + stash-stray-cleanup
  mechanism", open), both under PROJECT-GTKB-RELIABILITY-FIXES. The peer GO's
  duplicate-effort check confirmed WI-5027 is open but did not compare against
  these siblings. (The peer GO's own Prior Deliberations cite DELIB-202665165 and
  DELIB-202665192 — WI-4356 / work-tree-hygiene-spec NO-GOs — which further shows
  the surfaces share a decision history that should be reconciled.)
- Severity: P2 (backlog coordination / duplicate-effort risk).
- Impact: Risk of three overlapping triage implementations (WI-5027 planner,
  WI-4979 actuator, WI-4356 mechanism).
- Recommended action: Declare the dependency direction — the natural partition is
  WI-5027 delivers the read-only classifier that WI-4979's recurring actuator
  later consumes. Record this so the actuator builds on the planner, not beside it.

## Finding 3 [P3] — Proposal Prior Deliberations section is a non-canonical placeholder

- Claim: The proposal's `## Prior Deliberations` reads "_No prior deliberations
  auto-loaded; author must confirm before review._" — a placeholder deferring the
  search, not the canonical `_No prior deliberations: <reason>._` opt-out, and it
  omits relevant priors (DELIB-20266278 dispatch-treadmill-drain program that
  built the WI-4889 auto-finalization sweep this WI's own description says "is not
  keeping pace"; DELIB-20266272 PHASE-Y go-live).
- Evidence: proposal `-001.md` line 64; `gt deliberations show DELIB-20266278 /
  DELIB-20266272`.
- Severity: P3 (traceability; partially mitigated because the peer GO populated a
  real Prior Deliberations section at the thread level).
- Impact: The omitted DELIB-20266278 is the design predecessor and raises the
  Finding-1 question (relationship of the new planner to the existing sweep).
- Recommended action: On any future REVISED version, populate the section with
  DELIB-20266278 / DELIB-20266272 / DELIB-20260705 and state how the planner
  relates to the WI-4889 sweep.

## Positive confirmations (agree with the peer GO)

- Premise verified against live runtime: 389 dirty files / 222 untracked bridge
  files, matching the WI's "~390 / 222" claim.
- Authorization is real and correctly scoped: active
  PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5027-BATCH-A1-20260705 (included WI-5027;
  forbidden_operations cover destructive_bulk_cleanup and committing another
  session's stale work) and owner-decision DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL.
- Root boundary clean; both preflights pass (packet_hash
  sha256:f5db79d4…; clause preflight exit 0, 0 blocking gaps).
- Safety posture (read-only, dry-run, blocked destructive outcomes) is the right
  shape and aligns with the PAUTH forbidden_operations.

## Net

The work is authorized and worth doing, and the GO's approval of the read-only
direction is defensible. This session's independent review recommends Prime
Builder adopt Finding 1 (site under `gt hygiene`) during implementation and
record the Finding 2 dependency, both achievable within the current GO's
authorized scope.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
