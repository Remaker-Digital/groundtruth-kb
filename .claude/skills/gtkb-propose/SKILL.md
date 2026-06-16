---
name: gtkb-propose
description: Scaffold a structurally compliant bridge proposal body (status token, project-linkage metadata, inline-JSON target_paths, seeded Prior Deliberations, spec-derived verification heading, required sections) and run a self-review checklist BEFORE filing, then hand off to gtkb-bridge-propose for the write. Use when starting a NEW bridge implementation proposal and you want it to clear the bridge-compliance gates on the first review instead of in a revise loop.
---

This skill is the **composer** front-end to the `gtkb-bridge-propose`
**writer**. It produces a gate-compliant draft; `gtkb-bridge-propose` performs
the credential-scanned no-index bridge write and dispatcher/TAFE state
publication. This skill never writes to `bridge/` or MemBase itself.

After the 2026-06-15 TAFE/dispatcher cutover, the bridge writer must publish
versioned bridge files and dispatcher/TAFE state without creating or requiring
aggregate queue artifacts.

# /gtkb-propose

## What this skill does

Operationalizes `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` (Slices 1-3 enforce
proposal structure mechanically; this Slice 4 surface helps authors *produce*
that structure). It invokes `scripts/gtkb_propose_scaffold.py` to emit a draft
proposal body under `.gtkb-state/propose-drafts/<slug>-001.md` with every
gate-satisfying element pre-populated, plus a self-review checklist of the
mandatory preflights.

## When to invoke

Use when drafting a **NEW** bridge implementation proposal. Not for REVISED
versions of an existing thread, verdict files, or advisory entries.

## Inputs to collect from the author

- `slug` — kebab-case thread name (e.g. `gtkb-widget-refactor`).
- `work_item` — the governing WI id (`WI-NNNN` / `GTKB-*`).
- `project` — the `PROJECT-*` id grouping the work.
- `pauth` — the active `PAUTH-*` authorization id covering the work item.
- optional `slice` number, `bridge_kind` (default `implementation_proposal`),
  and one or more `target_path` globs the implementation will touch.

## Procedure

1. **Emit the scaffold draft:**

   ```text
   python scripts/gtkb_propose_scaffold.py scaffold \
       --slug <slug> --work-item <WI> --project <PROJECT-ID> --pauth <PAUTH-ID> \
       [--slice <N>] [--bridge-kind <kind>] \
       [--target-path <glob> --target-path <glob> ...]
   ```

   The helper validates the slug (kebab-case and safe bridge-file name),
   validates the work-item/project/authorization triple read-only against
   MemBase, seeds `## Prior Deliberations` from a Deliberation Archive search,
   pre-lists the always-applicable governing specs in `## Specification Links`,
   and writes the draft to `.gtkb-state/propose-drafts/<slug>-001.md`. It prints
   a self-review checklist.

2. **Fill the `TODO:` placeholders** in the draft with real content: the title,
   author/model metadata, summary, the operative `Requirement Sufficiency`
   state, the spec-to-test mapping under the verification heading, risk/rollback,
   and the recommended commit type. Prune the seeded Prior-Deliberations and
   Specification-Links candidates to the genuinely relevant ones.

3. **Run the self-review checklist** the helper printed — at minimum the two
   mandatory preflights, the phantom-spec sweep (confirm every cited id exists in
   the live `specifications` table), the inline-JSON `target_paths` parse check,
   and the verification-heading-token check. Fix any failure and re-check.

4. **Hand off to the writer.** When the checklist is green, file the completed
   body via the `gtkb-bridge-propose` skill, which credential-scans the body,
   writes `bridge/<slug>-001.md`, and publishes the bridge state through the
   no-index dispatcher/TAFE path. Do **not** write `bridge/` from this skill.

## Boundaries

- Read-only against MemBase; writes only the draft under `.gtkb-state/`.
- Does not replace Loyal Opposition review, the implementation-start packet, or
  the formal-artifact / narrative-artifact approval packets — it only reduces
  the structural-revise-loop friction before review.
- The scaffold is a starting point, not a substitute for substantive authoring:
  every `TODO:` must be replaced before filing.

## Source

`PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` Slice 4;
owner decision `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`;
GO at `bridge/gtkb-proposal-standards-propose-scaffold-skill-002.md`.
Helper: `scripts/gtkb_propose_scaffold.py`. Tests:
`platform_tests/scripts/test_gtkb_propose_scaffold.py`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
