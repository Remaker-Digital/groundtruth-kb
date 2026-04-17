# NO-GO: WI-3162 LO Report Backfill Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-015.md`
**Prior reviews:** `bridge/lo-report-backfill-002.md`, `bridge/lo-report-backfill-004.md`, `bridge/lo-report-backfill-006.md`, `bridge/lo-report-backfill-008.md`, `bridge/lo-report-backfill-010.md`, `bridge/lo-report-backfill-012.md`, `bridge/lo-report-backfill-014.md`
**Verdict:** NO-GO

## Claim

The v8 proposal correctly adds support for bullet-style `- verdict:` metadata.
It still does not fix standalone `Verdict:` blocks with multiple verdict
bullets, because the inherited field regex consumes the newline after the
colon and captures the first bullet as if it were an ordinary single-line
field. The adjacent contradictory verdict is still ignored.

## Evidence

- `bridge/lo-report-backfill-015.md` says a standalone `Verdict:` label with an
  empty captured value will trigger a block scan of subsequent lines.
- The inherited field regex uses `\s*[:=]\s*(.+)`. In Python, `\s*` consumes
  newlines, so a label such as `Verdict:\n\n- Conditional GO...` does not
  produce an empty capture. It captures the first bullet line.
- Corpus example:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE-OVERLAYS-BINDINGS-PLAN-REVIEW.md:5`
    has `Verdict:`
  - line `7` has `- \`Conditional GO\` ...`
  - line `8` has `- \`NO-GO\` ...`
- Probe using the v8 proposed top-field logic on that file returned:
  - field capture: `- \`Conditional GO\` ...`
  - signals: `[("top_field", "go")]`
  It did not collect the line 8 `NO-GO` signal and would not produce the
  promised mixed-outcome warning.
- The v8 bullet metadata regex does work for lines such as:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md:10`
    (`- verdict: \`NO-GO\``)
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-01-15-S230-INTENT-ROUTER-PHASE2-ADVISORY-REVIEW.md:7`
    (`- verdict: \`conditional no-go as written\``)
- GroundTruth KB inspection confirms this remains a prerequisite, not an
  already-landed storage-boundary fix:
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3112-3130`
    currently has generic redaction patterns but no raw `ar_live_`,
    `ar_user_`, `ar_spa_plat_`, `pk_live_`, or `arsk_` redaction patterns.
  - GroundTruth verification commands passed in the current checkout:
    `python -m pytest tests/test_deliberations.py -q --tb=short` returned
    `52 passed, 11 skipped`; `python -m ruff check .` returned
    `All checks passed!`; `python -m ruff format --check .` returned
    `50 files already formatted`.

## Findings

### P1 - Standalone `Verdict:` blocks still collapse mixed outcomes

The proposed fix depends on detecting an empty capture after `Verdict:`, but
the regex as written will usually capture the first bullet below the label.
That reproduces the exact failure mode from the prior review: a mixed
`Conditional GO` plus `NO-GO` block becomes a clean `go` signal.

**Risk/impact:** Mixed verdict blocks can still be stored as approvals without
a warning. This corrupts the single structured `outcome` field and forces the
owner or future agents to reread the report body to discover the blocking
line.

**Required action:** Make standalone verdict-block detection line-oriented.
Options:

1. Change the field regex so post-colon whitespace does not consume newlines,
   for example use `[^\S\r\n]*` instead of `\s*` after `[:=]`.
2. Treat a line ending with `Verdict:` as a block opener before applying the
   single-line verdict-field parser.
3. Once a block opener is detected, collect all verdict-bearing lines in the
   bounded window and feed every parsed signal into the conflict resolver.

Add a regression test using
`INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE-OVERLAYS-BINDINGS-PLAN-REVIEW.md`
that proves the result is `informational` with a mixed-verdict warning, not a
clean `go`.

### P2 - The proposal should test the newline-consumption edge directly

The v8 test list includes standalone block cases, but the pseudocode and probe
show the proposed regex shape will not enter the empty-capture branch. The
test must use the same multiline shape as the real corpus: `Verdict:` followed
by a blank line and multiple bullets.

**Required action:** Add a focused unit test asserting the field regex does not
consume newline-delimited verdict bullets as a single-line field.

## Required Conditions For GO

1. Fix line-oriented standalone `Verdict:` block parsing so newline-consuming
   `\s*` cannot hide later verdict bullets.
2. Collect all verdict-bearing lines from standalone verdict blocks and apply
   the existing mixed-outcome conflict policy.
3. Add corpus-derived regression coverage for the S230 Cosmos persistence
   mixed `Verdict:` block.
4. Keep all prior requirements: bullet-style verdict metadata, structured
   warnings, GroundTruth redaction before import with all five Agent Red key
   families, Agent Red project-KB target, dry-run/apply gate, ordered SPEC/WI
   extraction, decimal SPEC regex, missing-ID reporting, conflict warnings,
   narrowed body-warning scope, and temp-DB tests.

## Decision Needed From Owner

No owner decision is needed. Prime should revise the standalone verdict-block
parser before implementation.
