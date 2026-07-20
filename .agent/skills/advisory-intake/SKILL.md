---
name: gtkb-advisory-intake
description: Consume live ADVISORY entries through Prime Builder owner-grilling, explicit project/work-item approval, and child proposal filing without treating advisories as implementation approval.
---


# /advisory-intake

Use this skill when Prime Builder needs to triage a live ADVISORY bridge entry
or advisory report and decide whether it should become no-op evidence, a backlog
candidate, a specification candidate, a project/work item package, or a child
implementation proposal.

This skill keeps advisory intake separate from build approval. A live advisory
can inform source summarization and owner-grilling, but protected edits only
begin after explicit owner approval or active project authorization, a concrete
work item, a child proposal, Loyal Opposition `GO`, and an implementation-start
packet.

## When To Use

- A bridge thread or advisory report has latest `ADVISORY` status and is ready
  for Prime Builder disposition.
- A live ADVISORY includes enough source material to summarize, compare against
  existing work, and present a bounded owner-grilling question.
- The owner has asked Prime Builder to process advisory recommendations into
  governed project, work item, or bridge-proposal artifacts.

## When Not To Use

- Do not use this skill for Loyal Opposition advisory authoring; use
  `advisory-proposal` for draft-first ADVISORY capture.
- Do not use this skill to treat ADVISORY as dispatchable implementation work.
- Do not start protected edits from advisory content alone.
- Do not file a child implementation proposal until explicit owner approval or
  active project authorization, work item scope, target paths, specification
  links, and a spec-derived verification plan are present.
- Do not bypass bridge `GO`, implementation-start, root-boundary,
  credential-safety, formal-artifact, or verification gates.

## Required Inputs

- Source live advisory reference: bridge slug, report path, DELIB-ID, work-item
  citation, or other governed in-root evidence.
- Source summarization of the advisory claim, evidence, recommended action,
  affected project area, and expected value or risk.
- Existing related projects, work items, specifications, deliberations, bridge
  threads, and project authorizations.
- Owner-grilling question and answer evidence when owner approval is needed.
- Target paths, specification links, and verification plan if a child proposal
  is the selected route.

## Intake Decision Tree

Choose one route and record why other routes were rejected.

1. **No-op**: choose this when the advisory is duplicate, obsolete, already
   handled, contradicted by owner decision, outside GT-KB scope, or too vague to
   convert.
2. **Backlog candidate**: choose this when the advisory describes useful future
   work but lacks immediate owner/project authorization or proposal readiness.
3. **Specification intake**: choose this when the advisory asserts a durable
   requirement, constraint, ADR, DCL, GOV, or acceptance criterion.
4. **Project/work item package**: choose this when the advisory needs explicit
   project scoping, a work item, or owner approval before implementation can be
   proposed.
5. **Child proposal**: choose this only after explicit owner approval or active
   project authorization, concrete work item scope, target paths, specification
   links, and spec-derived verification are present.
6. **Deferred**: choose this when the advisory is valuable but blocked by a
   missing owner answer, external state, dependency, or release constraint.

## Mandatory Steps

1. Confirm the advisory is live by checking the latest numbered bridge state and
   any governed scanner/helper output. Exclude promoted, rejected, superseded,
   and already-work-item-backed advisories when the helper marks them non-live.
2. Summarize the source advisory in neutral terms: claim, evidence, risk/value,
   recommended action, and likely affected surfaces.
3. Search for duplicate or related deliberations, specifications, work items,
   projects, and bridge threads.
4. Apply the intake decision tree and record the selected route.
5. If owner input is required, ask one owner-grilling question at a time and
   preserve the answer as governed decision evidence.
6. Before filing any child proposal, confirm explicit owner approval or active
   project authorization, work item scope, target paths, specification links,
   and verification plan.
7. File only the governed artifact selected by the route. Do not begin protected
   implementation until Loyal Opposition returns `GO` for a child proposal and
   Prime Builder records implementation-start authorization.

## Verification Evidence

When this skill is implemented or used in a governed workflow, preserve:

- Live advisory source and status evidence.
- Source summarization and duplicate-search evidence.
- Owner-grilling question, explicit owner approval, project authorization, or
  the blocker showing why approval is absent.
- Work item, project, child proposal, specification candidate, no-op, or
  deferral artifact path.
- Proof that ADVISORY intake did not start protected edits before child proposal
  `GO` and implementation-start authorization.

## Cross-Harness Disposition

- Claude Code: canonical managed-skill source lives at
  `.claude/skills/advisory-intake/SKILL.md`.
- Codex: generated adapter lives at
  `.codex/skills/advisory-intake/SKILL.md` and is declared in
  `.codex/skills/MANIFEST.json`.
- Antigravity, Cursor, and API harnesses: no direct skill adapter surface is
  created by WI-5056. Projection to additional harnesses requires a separate
  target-path-covered proposal or typed parity disposition.

## Non-Goals

- This skill does not author Loyal Opposition ADVISORY entries.
- This skill does not replace `advisory-disposition`, `kb-work-item`,
  `gtkb-spec-intake`, `projects`, `gtkb-propose`, `gtkb-bridge-propose`, or
  `gtkb-bridge`.
- This skill does not convert advisory material, source summarization,
  owner-grilling, or a work item into implementation approval.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
