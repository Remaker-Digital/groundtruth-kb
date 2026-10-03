---
name: gtkb-structural-hygiene-review
description: Use when reviewing or correcting project structure, naming, artifact authority, glossary alignment, stale or historical artifacts, source-of-truth confusion, generated-vs-authoritative surfaces, or agent-behavior drift caused by directories, filenames, schemas, CLI names, docs, tests, or generated outputs.
metadata:
  project: groundtruth-kb
  category: architecture and standards
  references:
    - ../gtkb-work-item/references/taxonomy.md
  license: "Proprietary - (c) 2026 Remaker Digital"
---
# Structural Hygiene Review

## Goal

Make the project teach agents the correct operating model through its visible
structure. Directory names, artifact names, schema names, commands, docs, tests,
and generated outputs must align with the canonical glossary and current
authorities.

## Required Inputs

Read the smallest relevant set:

- `.harness-baseline-configuration/rules/canonical-terminology.md`
- `.harness-baseline-configuration/rules/operating-model.md`
- current canonical records for the concept under review, read through the `gt`
  readers
- relevant docs, tests, scripts, generated artifacts, and archive paths

## Workflow

1. Identify canonical terms and authority records.
2. Inventory physical and textual cues: directory names, file names, commands,
   schema/table names, docs, tests, generated outputs, and cross-references.
3. Build an authority map for each concept: canonical term, authoritative
   source, read path, mutation path, generated views, historical artifacts, and
   deprecated aliases.
4. Flag competing cues:
   - active-looking historical artifacts
   - duplicate sources of truth
   - generated files without generated labels
   - docs/tests preserving obsolete concepts as current behavior
   - schema/API/CLI names using non-canonical terms
   - archive material still used as live input
5. Classify findings:
   - `P0`: competing authority or source-of-truth conflict
   - `P1`: active-looking obsolete artifact likely to mislead agents
   - `P2`: terminology drift across docs/schema/API/tests
   - `P3`: clutter or weak naming that reduces intuitiveness
6. Report findings as corrective work items or ADVISORY; correct only under a
   dispatched work item and its chain. File unmatched work through
   `gtkb-work-item` into `PROJECT-GTKB-NEW-WORK-INTAKE`, with its specification
   and executable test, and name any related project in its description.

## Correction Rules

- Remove obsolete material at its source.
- Generated files must say they are generated.
- Compatibility files must not be mutation surfaces.
- Prefer canonical glossary terms in APIs, schema, docs, and CLI.
- Do not leave old names in tests unless the test is explicitly checking legacy
  compatibility.
- Archive paths must be clearly named as archive, history, deprecated, or
  superseded.

## Report Format

Include:

- claim
- evidence
- risk/impact
- correction applied or recommended
- verification
- residual risk
