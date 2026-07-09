---
name: advisory-disposition
description: Convert Loyal Opposition advisory findings into the correct governed next artifact path without treating advisory capture as implementation approval.
---

# /advisory-disposition

Use this skill when a Loyal Opposition advisory finding, advisory bridge entry,
or advisory report needs a Prime Builder disposition. The disposition must route
the finding into the correct governed artifact path: no-op, work item,
specification intake, project authorization, bridge proposal, or deferred
candidate.

This skill absorbs the prior WI-3303 advisory-disposition precedent:
`bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-004.md` VERIFIED
that an advisory can be closed as `adapt` by preserving the disposition in the
Deliberation Archive, resolving or routing the work item, and filing a
separately gated follow-on build thread. That precedent did not verify a
reusable skill implementation; WI-4840 provides the reusable routing procedure.

## When To Use

- A Loyal Opposition advisory proposes future work, a deterministic service, a
  governance correction, a specification change, or a process improvement.
- A bridge entry is `ADVISORY` or an advisory report is cited as source evidence
  for a follow-on Prime Builder action.
- Prime Builder must decide whether the advisory is duplicate, already handled,
  a backlog candidate, a specification candidate, a project-authorization
  candidate, an implementation-proposal candidate, or a deferral candidate.

## When Not To Use

- Do not use this skill to implement the advisory's recommended change.
- Do not use this skill to bypass the bridge, project authorization,
  AskUserQuestion, formal-artifact approval, root-boundary, credential-safety, or
  implementation-start gates.
- Do not treat an advisory disposition, a work item, a specification candidate,
  or a project authorization as implementation approval. Only a live bridge
  `GO` plus implementation-start packet authorizes protected implementation
  edits.
- Do not mutate retired aggregate queue artifacts or infer current bridge state
  from summaries. Use dispatcher/TAFE state and numbered bridge files.

## Required Inputs

- Source advisory reference: bridge slug, report path, DELIB-ID, or WI evidence.
- Advisory finding text, severity or opportunity class, and recommended action.
- Existing related work items, specifications, deliberations, bridge threads,
  project records, and project authorizations.
- Owner-decision evidence when the route depends on owner approval.
- Target-path and verification-plan evidence if the route may become a bridge
  proposal.

## Advisory Disposition Decision Tree

Choose exactly one primary disposition. Record secondary notes only when they
clarify follow-on dependencies.

1. **No-op**: choose this when the advisory is duplicate, superseded, already
   resolved, outside GT-KB scope, contradicted by durable owner decision, or
   too vague to preserve as a concrete candidate. Record the evidence that makes
   no further artifact appropriate. Record the disposition WITHOUT flipping
   the thread into a Prime-authored, Loyal-Opposition-actionable status: keep
   the thread `ADVISORY` with a recorded Prime disposition note (e.g., a
   Deliberation Archive entry), or move it to a terminal `WITHDRAWN` status
   with cited rationale and owner-decision evidence. Do NOT write a `NO-ACTION`
   bridge entry to close an advisory: `NO-ACTION` is a Prime Builder rejection
   of a prior Loyal Opposition `GO`/`NO-GO` verdict (per
   `DCL-NO-ACTION-STATUS-SEMANTICS-001`) and is invalid on an advisory thread
   with no prior verdict; the bridge-compliance-gate blocks it.
2. **Work item**: choose this when the advisory describes actionable future work
   that is not already tracked, does not itself create or revise a governing
   specification, and is not yet implementation-approved. Create or update a
   MemBase work item through the governed backlog workflow and cite the source
   advisory.
3. **Specification intake**: choose this when the advisory asserts or implies a
   behavior, constraint, requirement, ADR, DCL, GOV, PB, or acceptance criterion
   that would govern implementation or verification. Route through spec intake
   or formal artifact approval; do not silently promote the advisory into a
   canonical specification.
4. **Project authorization**: choose this when multiple related work items are
   ready for owner-scoped implementation approval, but no active project
   authorization covers the work. Prepare the authorization candidate and keep
   implementation blocked until owner approval is captured.
5. **Bridge proposal**: choose this only when a concrete work item or bounded
   work scope already has sufficient requirements, active owner or project
   authorization where required, target paths, specification links, and
   spec-derived verification. File a normal implementation proposal and cite the
   advisory as source evidence; wait for Loyal Opposition `GO`.
6. **Deferred candidate**: choose this when the advisory is plausible and worth
   preserving, but a missing owner decision, dependency, external event, release
   constraint, or insufficient evidence blocks useful action. Record the
   deferral reason and clear/resume condition.

## Artifact Routing Rules

- Preserve advisory source evidence in the destination artifact: `Source
  advisory`, `Prior Deliberations`, related bridge thread, or related WI fields.
- Search existing deliberations, backlog items, specifications, and bridge
  threads before creating a new artifact. Duplicate work routes to no-op or an
  update of the existing artifact, not a second competing record.
- If the route requires owner input and the session can ask the owner, use the
  AskUserQuestion path. In headless auto-dispatch, record the missing decision
  as a blocker in the bridge artifact or implementation report and stop.
- If the route creates or updates a formal artifact, use the governed approval
  path for that artifact class.
- If the route creates an implementation proposal, use the bridge proposal
  workflow and include project-linkage metadata when the scope is
  project-authorized.

## Mandatory Steps

1. Load the source advisory and the latest live bridge state for any cited
   thread.
2. Search for prior deliberations and existing backlog/spec/bridge records that
   could already cover the finding.
3. Classify the advisory using the decision tree above and write the rationale
   in the destination artifact or report.
4. Keep consideration capture separate from implementation approval. A work item
   or specification candidate makes the work visible; it does not authorize code
   or configuration changes.
5. For a bridge proposal route, carry forward the source advisory, prior
   deliberations, target paths, linked specifications, owner/project
   authorization evidence, and spec-derived verification plan.
6. For a deferral route, record a concrete clear/resume condition so future
   sessions can tell when the item becomes actionable.

## Verification Evidence

An implementation report using this skill should include:

- The selected disposition and the rejected alternative routes.
- Source advisory citation and prior deliberation citations.
- Evidence that duplicate backlog, specification, and bridge records were
  checked.
- Destination artifact path or MemBase ID, if one was created or updated.
- For bridge-proposal routes, the new bridge slug and proof that no protected
  implementation started before Loyal Opposition `GO`.
- For no-op or deferred routes, the concrete evidence or trigger condition that
  makes the route appropriate.

## Cross-Harness Disposition

- Claude Code: canonical managed-skill source lives at
  `.claude/skills/advisory-disposition/SKILL.md`.
- Codex: generated adapter lives at
  `.codex/skills/advisory-disposition/SKILL.md` and is declared in
  `.codex/skills/MANIFEST.json`.
- Antigravity, Cursor, and API harnesses: no direct skill adapter surface is
  created by WI-4840. Projection to additional harnesses requires a separate
  target-path-covered proposal or typed parity disposition.

## Non-Goals

- This skill does not decide the owner's priorities.
- This skill does not create implementation approval.
- This skill does not replace `kb-work-item`, `gtkb-spec-intake`, `projects`,
  `gtkb-propose`, `gtkb-bridge-propose`, or `gtkb-bridge`; it chooses the
  correct next artifact path before those workflows run.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
