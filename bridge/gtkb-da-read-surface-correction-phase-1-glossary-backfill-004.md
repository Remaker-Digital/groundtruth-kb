NO-GO

# Loyal Opposition Review - DA Read Surface Correction Phase 1 Glossary Backfill REVISED

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md`
Verdict: NO-GO

## Claim

The revised proposal resolves the two prior structural blockers from
`bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-002.md`: it
now places narrative-artifact approval before the protected-file write, and it
includes full proposed text for all 30 entries.

It still cannot proceed because several proposed `Source:` lines do not resolve
to a Deliberation Archive record, rule file, or MemBase specification. That is
the central invariant of `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`, and it is
also part of the proposal's own verification plan.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-1-glossary-backfill
```

Observed:

- packet_hash: `sha256:9c6f1148261fa0ff575551b3bce3a6030682630f85d22ca3a57e6fad67090e9d`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-1-glossary-backfill
```

Observed:

- operative_file: `bridge\gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md`
- clauses evaluated: `5`
- must_apply: `5`
- may_apply: `0`
- not_applicable: `0`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings

### F1 - P1 - Proposed Source lines do not all resolve

Evidence:

- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` requires every glossary entry's
  `Source:` line to resolve to at least one Deliberation Archive record, rule
  file, or MemBase specification. The revised proposal cites this constraint at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md:44`.
- The proposal's verification plan also requires citation resolution for each
  new entry at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md:454`.
- The proposed `bias case` entry's source line is only free-text S331 framing:
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md:133`.
- The proposed `salience case` entry's source line is likewise only free-text
  S331 framing:
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md:143`.
- Searches for a corresponding S331 deliberation did not find a stable record:

```text
python -m groundtruth_kb deliberations search "S331 bias salience placement owner articulation" --limit 10
python -m groundtruth_kb deliberations search "S331 glossary DA read surface owner approved framing" --limit 10
rg -n "DELIB-S331|S331 owner articulation|S331 owner-articulated|S331 owner agreement|bias.*salience|placement.*enforcement|ZIP-portability|scope-bound write" . groundtruth-kb
```

The searches found prior general records such as `DELIB-0722`, `DELIB-0877`,
and operational notes in `memory/`, but no resolvable `DELIB-S331-*` record for
the bias/salience/placement owner statements.

Risk / impact:

This backfill's purpose is to make the glossary a reliable DA read surface. A
canonical entry whose only source is unanchored session prose recreates the
same failure class: the glossary would look authoritative, but a future agent
or doctor check could not trace the definition to governed evidence.

Recommended action:

Revise the proposed entries so every `Source:` line contains at least one
machine-resolvable authority. For the S331-only concepts, either:

1. Cite an existing MemBase artifact that already contains the same owner
   decision; or
2. First capture the S331 owner statements into Deliberation Archive records,
   then cite the new `DELIB-S331-*` IDs in the glossary entries.

At minimum, the revised proposal should repair `bias case` and `salience case`.
Prime should also run a simple resolver over all 30 proposed `Source:` lines
before refiling and include the pass/fail table in the next revision.

### F2 - P2 - The approval-preview fallback weakens the full-content display rule

Evidence:

- The revised implementation pattern correctly requires a narrative-artifact
  packet before writing `.claude/rules/canonical-terminology.md` at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md:421`
  through
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md:430`.
- Step 5 then allows the AUQ to omit the full new file content if it is too
  large, using only a draft path, audit-list summary, and sha256 in the preview:
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md:427`.
- `GOV-ARTIFACT-APPROVAL-001` requires the full proposed native content before
  treating the artifact as canonical, and the narrative-artifact packet schema
  requires `presented_to_user=true` and `transcript_captured=true`.

Risk / impact:

If the AUQ preview does not actually display the full proposed file content or
an explicit owner-visible full-content review packet, the resulting approval
packet could claim `presented_to_user=true` for content the owner did not see in
the approval surface.

Recommended action:

Revise the implementation pattern to require one explicit full-content review
surface before approval. Acceptable forms include the full AUQ preview, a
separate owner-visible draft/review packet whose complete content is displayed
before AUQ, or another documented review surface that makes it true that the
full content was presented before `presented_to_user=true` is written. A path +
hash alone is not sufficient unless the owner explicitly acknowledges that exact
path/hash as the reviewed full-content packet.

## Non-Blocking Notes

The two original NO-GO findings are materially addressed:

- Prior F1 is addressed by generating the narrative-artifact approval packet
  before writing the protected rule file.
- Prior F2 is addressed by drafting all 30 entries in the revised proposal.

The remaining blocker is narrower: the proposed full text still needs resolvable
source anchors before it can become canonical startup-loaded terminology.

## Decision

NO-GO. Refile with resolvable `Source:` lines for every proposed entry and a
full-content approval presentation path that satisfies the narrative-artifact
approval rule.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
