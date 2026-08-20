---
name: gtkb-advisory-proposal
description: Draft Loyal Opposition ADVISORY bridge entries from reusable external or peer solutions while preserving owner confirmation and non-approval semantics.
---
# /advisory-proposal

Use this skill when Loyal Opposition, advisory mode, or a review session finds a
reusable external solution, peer-harness suggestion, research result, or process
improvement that should be preserved as an ADVISORY bridge entry for later Prime
Builder disposition.

The skill is draft-first: it helps capture advisory evidence, ask for final owner
confirmation when required, cite the source advisory and prior deliberations, and
make clear that advisory capture is not implementation approval.

## When To Use

- A review or investigation identifies reusable guidance that is worth
  preserving but is not itself ready for implementation.
- A peer harness, external tool, or advisory report suggests a future GT-KB
  improvement that needs owner consideration before any build proposal exists.
- Loyal Opposition needs to draft an ADVISORY bridge entry that can later be
  routed by Prime Builder through backlog, specification, project authorization,
  or implementation-proposal workflows.

## When Not To Use

- Do not use this skill to authorize implementation, edit protected files, or
  open an implementation-start packet.
- Do not use this skill to file `NEW`, `REVISED`, `GO`, `NO-GO`, or `VERIFIED`
  bridge entries.
- Do not treat a captured advisory, a draft advisory, owner interest, a work
  item, or a project candidate as implementation approval.
- Do not bypass the bridge, project authorization, owner-decision,
  root-boundary, credential-safety, formal-artifact, or verification gates.
- Do not mutate retired aggregate queue artifacts or infer live bridge state
  from summaries. Use dispatcher/TAFE state and numbered bridge files.

## Required Inputs

- Source advisory reference: bridge slug, report path, peer-harness output,
  external source, DELIB-ID, or owner transcript citation.
- The advisory claim, supporting evidence, recommended next action, and any
  known risk or opportunity class.
- Existing related deliberations, work items, projects, bridge threads,
  specifications, and prior advisory entries.
- Owner confirmation evidence, or a clear note that the advisory remains a draft
  waiting for final owner confirmation.
- The intended downstream route when known: no-op, backlog candidate,
  specification intake, project authorization, bridge proposal, or deferral.

## Advisory Draft Contract

Every filed ADVISORY entry created through this skill must preserve:

1. The source advisory and enough context for a future session to re-check it.
2. Prior deliberations and related work items that affect interpretation.
3. A concise statement of the claim, evidence, risk or value, and recommended
   next artifact path.
4. The owner confirmation or explicit unresolved owner question that controls
   whether the advisory can be filed or only kept as a draft.
5. A plain statement that the advisory is not implementation approval and does
   not bypass later Prime Builder proposal, Loyal Opposition GO, or
   implementation-start gates.

## Mandatory Steps

1. Load the source advisory and the latest live bridge state for any cited
   thread from numbered bridge files and dispatcher/TAFE state.
2. Search for duplicate or superseding deliberations, work items,
   specifications, bridge entries, and reports before drafting a new advisory.
3. Decide whether the material should be no-op, updated into an existing
   artifact, filed as ADVISORY, or held as a draft pending owner confirmation.
4. When owner confirmation is required and the session can ask the owner, ask
   one question at a time and preserve the resulting DELIB-ID or transcript
   evidence.
5. Draft the ADVISORY with source advisory, prior deliberations, evidence,
   recommended action, and non-approval language.
6. After filing, leave implementation intake to Prime Builder disposition; do
   not proceed directly into protected edits or implementation proposal filing
   from the advisory alone.

## Verification Evidence

When this skill is implemented or used in a governed workflow, preserve:

- The source advisory citation and any owner confirmation evidence.
- Duplicate-search evidence across related backlog, specification, deliberation,
  and bridge records.
- The ADVISORY bridge file path, or the draft path and the reason it stayed
  unfiled.
- The non-approval statement showing that advisory capture is not implementation
  approval.
- Any proposed next artifact route and the governance gate that still applies to
  that route.

## Cross-Harness Disposition

- Claude Code: canonical managed-skill source lives at
  `.harness-baseline-configuration/skills/advisory-proposal/SKILL.md`.
- Codex: generated adapter lives at
  `.harness-baseline-configuration/skills/advisory-proposal/SKILL.md` and is declared in
  `.harness-baseline-configuration/skills/MANIFEST.json`.
- Antigravity, Cursor, and API harnesses: no direct skill adapter surface is
  created by WI-5055. Projection to additional harnesses requires a separate
  target-path-covered proposal or typed parity disposition.

## Non-Goals

- This skill does not implement advisory recommendations.
- This skill does not replace `advisory-disposition`, `gtkb-propose`,
  `gtkb-bridge-propose`, `gtkb-bridge`, `kb-work-item`, or
  `gtkb-spec-intake`.
- This skill does not convert owner confirmation into build approval. Advisory
  filing only preserves the idea for later governed disposition.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
