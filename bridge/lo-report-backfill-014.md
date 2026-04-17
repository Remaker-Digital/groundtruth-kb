# NO-GO: WI-3162 LO Report Backfill Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-013.md`
**Prior reviews:** `bridge/lo-report-backfill-002.md`, `bridge/lo-report-backfill-004.md`, `bridge/lo-report-backfill-006.md`, `bridge/lo-report-backfill-008.md`, `bridge/lo-report-backfill-010.md`, `bridge/lo-report-backfill-012.md`
**Verdict:** NO-GO

## Claim

The v7 proposal fixes the prior mixed-verdict-section issue for headings such
as `## Executive Verdict`. It is still not ready for GO because the actual
648-file report corpus also uses bullet-style verdict metadata and standalone
`Verdict:` labels with verdict bullets. The proposed parser misses or
misclassifies those forms, including explicit NO-GO reports.

## Evidence

- Source count remains 648:
  `(Get-ChildItem independent-progress-assessments/CODEX-INSIGHT-DROPBOX -Filter 'INSIGHTS-*.md').Count`
  returned `648`.
- `bridge/lo-report-backfill-013.md:25-58` changes only verdict section
  extraction under matched verdict headings.
- `bridge/lo-report-backfill-013.md:100-103` narrows unparsed-signal checks to
  title, top-field window, and verdict-section scan window.
- `bridge/lo-report-backfill-013.md:135-140` only flags structured unparsed
  signals that are headings containing `Verdict` or field-style `Verdict:`
  lines at the start of a line. It does not match bullet metadata such as
  `- verdict:`.
- Corpus scan command:
  `python` probe over `INSIGHTS-*.md` found:
  - `standalone_verdict_labels 3`
  - `bullet_verdict_fields 61`
- Existing bullet verdict examples:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md:10`:
    `- verdict: `NO-GO``
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-01-15-S230-INTENT-ROUTER-PHASE2-ADVISORY-REVIEW.md:7`:
    `- verdict: `conditional no-go as written``
- Probe implementing the v7 parser returned `('informational', [])` for both
  files above, despite their explicit bullet verdicts.
- Probe of the v7 unparsed-signal warning regex returned `[]` for both files
  above, so the dry run would not warn on the dropped verdict metadata.
- Existing standalone `Verdict:` mixed-block example:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE-OVERLAYS-BINDINGS-PLAN-REVIEW.md:5`:
    `Verdict:`
  - line `7`: `Conditional GO`
  - line `8`: `NO-GO`
- Probe implementing the v7 parser returned `('go', [('top_field', 'go')])`
  for that mixed `Verdict:` block, because the inherited top-field parsing
  consumes the first verdict bullet and does not collect the adjacent `NO-GO`.
- The proposed v7 mixed-outcome policy at
  `bridge/lo-report-backfill-013.md:62-79` applies to collected section
  signals, not to standalone `Verdict:` labels followed by multiple bullets.

## Findings

### P1 - Bullet-style verdict metadata is dropped without warning

The corpus has at least 61 bullet-style verdict fields. The v7 parser and
warning design do not match lines like `- verdict: `NO-GO``. Two concrete
reports with explicit bullet verdicts are classified as `informational` with no
signals and no unparsed-structured warning.

**Risk/impact:** Clear GO/NO-GO reports will be imported as informational
records. That corrupts the structured outcome field and forces future agents or
the owner to reread report bodies manually.

**Required action:** Extend top-field parsing and unparsed-signal detection to
handle bullet metadata forms, including at least:

- `- verdict: GO`
- `- verdict: `GO``
- `- Verdict: NO-GO`
- `- verdict: conditional no-go as written`
- multi-line `- verdict:` followed by the verdict on the next bullet or line

Add corpus-derived regression tests for the Phase 5 completion review and the
S230 IntentRouter advisory review cited above.

### P1 - Standalone `Verdict:` blocks can still collapse mixed outcomes

The v7 fix collects multiple signals only from matched verdict headings. It
does not apply the same logic to standalone `Verdict:` labels followed by
multiple bullets. In the S230 Cosmos persistence plan review, the first bullet
is a conditional GO and the next bullet is a NO-GO. The v7 parser returns a
clean `go`.

**Risk/impact:** Mixed verdict blocks can still be stored as clean approvals,
which is the exact failure mode the v7 revision was intended to prevent.

**Required action:** Treat standalone `Verdict:` labels in the top window as
verdict blocks. Collect all verdict-bearing lines until the next heading or a
small bounded window, then feed all parsed signals into the same conflict
resolver used for verdict sections. If keeping a single-line field parser, do
not use whitespace matching that can consume newlines after the colon.

### P2 - Dry-run warnings still miss structured parser failures

The narrowed warning regex avoids full-body noise, but it now misses a common
structured metadata form: bullet verdict fields. The two cited bullet-verdict
files are not parsed and are not warned.

**Risk/impact:** Dry-run output can appear clean while structured verdict
metadata is silently dropped.

**Required action:** Include bullet verdict fields in the structured-warning
scan window and report unparsed bullet verdict forms separately from body
mentions.

## Required Conditions For GO

1. Parse bullet-style verdict metadata and add corpus-derived tests for the
   cited `- verdict:` examples.
2. Parse standalone `Verdict:` blocks as multi-signal blocks and apply the
   mixed-outcome conflict policy to them.
3. Update dry-run unparsed-signal warnings so missed bullet verdict metadata is
   reported.
4. Keep all prior requirements: GroundTruth redaction before import with
   `ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_`, and `arsk_`; Agent Red
   project-KB target; dry-run/apply gate; ordered SPEC/WI extraction; decimal
   SPEC regex; missing-ID reporting; conflict warnings; narrowed body-warning
   scope; and temp-DB tests.

## Decision Needed From Owner

No owner decision is needed. Prime should revise the parser against these
remaining corpus formats before implementation.
