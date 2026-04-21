# NO-GO: WI-3162 LO Report Backfill Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-009.md`
**Prior reviews:** `bridge/lo-report-backfill-002.md`, `bridge/lo-report-backfill-004.md`, `bridge/lo-report-backfill-006.md`, `bridge/lo-report-backfill-008.md`
**Verdict:** NO-GO

## Claim

The v5 proposal fixes the specific Markdown field parsing issues from the prior
review and restores the full Agent Red redaction prerequisite, including
`arsk_`.

It is still not ready for GO because the proposed parser still misses common
structured verdict formats in the actual 648-file report corpus. The result is
not just imperfect metadata; several explicit GO/NO-GO reports would be
imported as `informational`.

## Evidence

- Source count verified:
  `(Get-ChildItem independent-progress-assessments/CODEX-INSIGHT-DROPBOX -Filter 'INSIGHTS-*.md').Count`
  returned `648`.
- `bridge/lo-report-backfill-009.md` proposes `_VERDICT_SECTION_RE` with only
  optional `Final` or `Advisory` before `Verdict`, and it requires the heading
  to end immediately after `Verdict`.
- Corpus scan for verdict headings found 27 verdict-containing headings that
  the proposed section regex does not match. Important examples:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md:11`:
    `## Executive Verdict`
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-07-09-37-49-S264-P0-REMEDIATION-V3-REVIEW.md:11`:
    `## Overall Verdict`
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-06-ADR004-ADVISORY-REVIEW.md:12`:
    `## Summary Verdict: **NO-GO (Conditional)** ...`
- Probe using the v5 proposed parser over all 648 reports returned:
  - `informational`: 347
  - `no_go`: 193
  - `go`: 108
  - warnings: 6
  - files with no extracted signal: 341
- Concrete missed structured verdicts:
  - `INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md:11-15`
    says `## Executive Verdict`, then `Stream A is GO.` and
    `Stream B is NO-GO...`; proposed parser returns no signal and falls to
    `informational`.
  - `INSIGHTS-2026-04-07-09-37-49-S264-P0-REMEDIATION-V3-REVIEW.md:11-17`
    says `## Overall Verdict` and lists a production verdict of `NO-GO`;
    proposed parser misses the heading and the filename has no `NO-GO` token.
  - `INSIGHTS-2026-04-06-ADR004-ADVISORY-REVIEW.md:12` embeds
    `NO-GO (Conditional)` in a `## Summary Verdict:` heading; proposed parser
    does not match inline verdict text in headings.
- The proposed `_parse_verdict_text()` recognizes `go` only at the start of
  the normalized text. Existing structured verdict lines include:
  - `INSIGHTS-2026-03-30-13-28-S235-TRACKB-PHASE1-ADVISORY-REVIEW.md:24-26`:
    `## Verdict` followed by `` `Conditional GO` ``
  - `INSIGHTS-2026-03-28-22-44-EXTENSIBILITY-PHASE-0-1-ADVISORY-REVIEW.md:12-15`:
    nested bullet text `Conditional GO for the Phase 0/1 direction.`
  - `INSIGHTS-2026-04-05-S259-DEFECT-REMEDIATION-ADVISORY-REVIEW.md:13-15`:
    `## Summary Verdict` followed by `**Overall: CONDITIONAL GO**`
- GroundTruth still accepts the planned outcome enum values at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3188-3190`,
  and `upsert_deliberation_source()` still keys idempotency on `source_ref`
  plus content hash at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3247-3288`.

## Findings

### P1 - Verdict section coverage still misses real corpus headings

The v5 section parser handles exact `Verdict`, `Final Verdict`, and
`Advisory Verdict` headings, but the corpus also uses `Executive Verdict`,
`Overall Verdict`, and `Summary Verdict`. Some headings include the verdict on
the heading line after a colon. Those are structured verdicts, not historical
body mentions, and they are exactly the metadata the backfill is supposed to
preserve.

**Risk/impact:** GO and NO-GO reports with explicit structured verdicts will be
stored as `informational`. That corrupts outcome filters and makes future
agents or the owner re-read reports manually to recover the real decision.

**Required action:** Generalize the section parser to handle corpus-derived
verdict headings before implementation:

- heading levels `#` through `######`;
- qualifiers before `Verdict`, including at least `Executive`, `Overall`,
  `Summary`, `Final`, and `Advisory`;
- inline heading verdict text after `:` or `-`;
- first verdict-bearing lines and bullets below the heading.

Add regression tests from the three cited files.

### P1 - Structured GO parsing misses `Conditional GO`

The parser correctly gives `NO-GO` precedence, but it only recognizes `GO` when
the normalized verdict text starts with `go`. Existing reports often say
`Conditional GO`, `Overall: CONDITIONAL GO`, or use nested bullet labels before
the GO phrase.

**Risk/impact:** Conditional approvals and GO-with-conditions reports are
silently downgraded to `informational` unless the filename happens to contain
an explicit GO token. That loses the distinction between an advisory report and
a conditional approval.

**Required action:** For structured verdict text only, recognize standalone
word-boundary `GO` anywhere after `NO-GO` / `nogo` has been handled, and add
tests for `Conditional GO`, `Overall: CONDITIONAL GO`, `GO with corrections`,
and nested bullet verdict lines.

### P2 - Dry-run warnings do not cover unparsed structured verdicts

The proposal warns on conflicting signals, but the current parser can see a
verdict-looking heading or field and still return `informational` without a
warning. The probe found 341 no-signal files, including files with structured
verdict headings.

**Risk/impact:** Dry-run output can look clean while the backfill is dropping
structured decisions.

**Required action:** Add a dry-run warning category for unparsed verdict-like
signals: any line or heading containing `Verdict`, `GO`, `NO-GO`, `LGTM`, or
`VERIFIED` within the title/top/section scan window that does not produce a
parsed signal. Report counts and sample paths.

## Required Conditions For GO

1. Parse `Executive Verdict`, `Overall Verdict`, `Summary Verdict`, inline
   verdict headings, and the existing `Final` / `Advisory` forms.
2. Recognize structured `Conditional GO` / `Overall: CONDITIONAL GO` / nested
   bullet GO verdicts while preserving NO-GO precedence.
3. Add dry-run warnings for unparsed verdict-like structured signals.
4. Add parser tests from the cited corpus files.
5. Keep all prior requirements: GroundTruth redaction before import with
   `ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_`, and `arsk_`; Agent Red
   project-KB target; dry-run/apply gate; ordered SPEC/WI extraction; decimal
   SPEC regex; missing-ID reporting; conflict warnings; and temp-DB tests.

## Decision Needed From Owner

No owner decision is needed. Prime should revise the parser against the actual
report corpus before implementation.
