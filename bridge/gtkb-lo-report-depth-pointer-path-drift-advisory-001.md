ADVISORY
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; recurring build review

bridge_kind: governance_advisory
Document: gtkb-lo-report-depth-pointer-path-drift-advisory
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-07-28 America/Los_Angeles

# Loyal Opposition Advisory — GT-KB Agent-Control Report-Depth Pointer Resolves to a Missing File

## Classification Slot

**adapt** — preserve the HYG-027 single-canonical-plus-pointer design, but adapt
the agent-control projection so its relative pointer resolves inside that
projection tree. Severity: **P2**. The defect degrades governance loading and
cross-harness parity but does not itself authorize or mutate implementation.

## Advisory Status

This entry preserves a startup/control-surface defect for Prime Builder
disposition. It is not implementation approval and does not authorize edits to
`config/`, `.claude/`, skills, tests, generated projections, bridge runtime,
dispatcher/TAFE state, or any other protected surface.

## Source

- Source: live Loyal Opposition startup and bridge-review context load during
  the recurring task session `019fac54-c55c-75c0-8332-d7fdaf03b20a`.
- Owner confirmation: the current owner instruction explicitly requires Loyal
  Opposition to create and file an Advisory Proposal for defects or poor GT-KB
  design choices found outside the bridge items being processed.
- This advisory therefore may be filed now; no additional owner question is
  required for capture. Any implementation still requires normal Prime Builder
  intake, project authorization, proposal, independent GO, claim, and
  implementation-start gates.

## Claim

The retained agent-control compatibility pointer
`config/agent-control/gtkb-report-depth-prime-builder-context.md` directs readers
to a relative `report-depth.md` file that does not exist in that directory. The
actual agent-control copy is `config/agent-control/gtkb-report-depth.md`.

The parallel `.claude/rules/report-depth-prime-builder-context.md` pointer is
valid because `.claude/rules/report-depth.md` exists. Copying the same relative
link into the `gtkb-`-prefixed agent-control projection silently broke the
pointer target.

## Evidence

1. `config/agent-control/gtkb-report-depth-prime-builder-context.md` says the
   canonical standard is maintained in `[report-depth.md](report-depth.md)` and
   instructs readers to consult that path.
2. `config/agent-control/report-depth.md` is absent.
3. `config/agent-control/gtkb-report-depth.md` exists and contains the full
   Report Depth and Prime Builder Context Standard.
4. `.claude/rules/report-depth-prime-builder-context.md` contains the same
   pointer text, but its sibling `.claude/rules/report-depth.md` exists, so the
   relative target is valid only on the canonical Claude rules surface.
5. `.claude/skills/gtkb-bridge/SKILL.md` explicitly sends Loyal Opposition to
   `config/agent-control/gtkb-report-depth-prime-builder-context.md` for verdict
   depth, making the broken projected pointer part of the active review load
   path rather than dead documentation.

## Risk / Impact

- A harness following the active bridge skill reaches the pointer stub but
  cannot resolve its stated canonical target in the same projection tree.
- Review depth can become dependent on a harness already knowing the separate
  `.claude/rules/` layout, undermining the purpose of the agent-control
  projection and cross-harness startup contract.
- Tests may validate that a pointer stub exists without validating that its
  relative target exists, allowing a resolved hygiene item to regress while
  still appearing structurally complete.
- Future projection or packaging consumers may treat the missing target as an
  absent governance dependency and silently skip the report-quality contract.

## Duplicate and Supersession Search

- `WI-4417` / `gtkb-fab-05-rule-file-retirement` is the resolved FAB-05 work
  that implemented HYG-027 by retaining pointer stubs and making
  `report-depth.md` canonical.
- Versions 001, 003, and 005 of that thread explicitly describe the HYG-027
  pointer branch; version 006 is terminal evidence for the resolved work.
- No active MemBase work item matched `report depth`; the only HYG-027 work item
  found was resolved WI-4417.
- No current specification matched `report depth`, and no existing live bridge
  advisory was found for this projected relative-link defect.
- This advisory is therefore a regression/follow-on to resolved WI-4417, not a
  duplicate implementation front and not a request to rewrite its history.

## Recommended Prime Action

Prime Builder should disposition this advisory into a small successor hygiene
work item, or reopen the issue through the project path selected by current
backlog policy, with a protected implementation proposal that:

1. chooses one canonical projection-safe target convention;
2. corrects the agent-control pointer to `gtkb-report-depth.md`, or renames the
   projected canonical file and all governed consumers atomically;
3. adds a regression test that every retained relative pointer resolves inside
   its own projection tree;
4. verifies `.claude/rules/`, `config/agent-control/`, generated Codex adapters,
   adoption checks, and bridge skill references remain semantically aligned;
5. preserves WI-4417 and the FAB-05 bridge chain as append-only history.

The narrow pointer correction is the lower-risk default because it avoids
renaming the live agent-control canonical file and changing all its consumers.

## Owner Decision Needed

None for advisory capture. Before any derived implementation proposal, Prime
Builder must apply the normal advisory-disposition and owner-grilling gates and
capture any route or scope decision those gates require. The owner's current
instruction authorizes advisory filing only, not implementation.

## Non-Approval Boundary

This ADVISORY records evidence and a recommended next artifact path only. It is
not a specification, work item, project authorization, implementation proposal,
GO verdict, work-intent claim, implementation-start packet, or permission to
modify protected files.

## Skills Applied

- `gtkb-advisory-proposal`
- `gtkb-bridge`
- `gtkb-query`

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
