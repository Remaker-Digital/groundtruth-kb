# NO-GO: WI-3162 LO Report Backfill Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-007.md`
**Prior reviews:** `bridge/lo-report-backfill-002.md`, `bridge/lo-report-backfill-004.md`, `bridge/lo-report-backfill-006.md`
**Verdict:** NO-GO

## Claim

The v4 proposal fixes the prior filename `GOVERNANCE` false positive and adds
explicit `owner_decision` handling. It still should not be approved because
the proposed structured parser misses verdict formats that already exist in
the 648-file LO report corpus, and the redaction prerequisite regresses by
omitting an Agent Red key family present in existing reports.

## Evidence

- `bridge/lo-report-backfill-007.md:112-114` proposes this top-of-file verdict
  regex:
  `(?:^|\n)\s*\*?\*?[Vv]erdict\*?\*?\s*[:=]\s*(.+)`.
- Existing LO reports use Markdown forms that this regex does not parse:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-28-02-38-PHASE5-PLAN-REREVIEW.md:6`
    has `Verdict: \`GO\``.
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-27-07-52.md:6`
    has `**Verdict:** \`GO\` for Phase 1`.
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-27-09-37.md:6`
    has `**Verdict:** \`GO\` for Phase 2`.
- Probe using the proposed parser on all
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`
  files returned:
  - `go`: 87
  - `no_go`: 167
  - `informational`: 394
  - warnings: 8
  - top `Verdict: \`GO\`` fields not parsed: 8
  - top `**Verdict:** ...` fields not parsed: 3
- Concrete parser repro:
  - `INSIGHTS-2026-03-28-02-38-PHASE5-PLAN-REREVIEW.md` returned
    `informational` with no signals, despite its top field being `GO`.
  - `INSIGHTS-2026-03-27-07-52.md` returned `informational` with no signals,
    despite its top field being `GO`.
- `bridge/lo-report-backfill-007.md:122-124` only detects a heading exactly
  matching `## Verdict`.
- Existing reports also use `# Final Verdict`:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-11-54-S231-PHASE4A-ADMIN-AGENT-API-CODE-REVIEW.md:77-79`
    has `# Final Verdict` followed by a `NO-GO` bullet.
- Probe against the proposed parser found 10 reports with `# Final Verdict`;
  9 were classified as `informational`.
- `bridge/lo-report-backfill-007.md:219-220` lists the GroundTruth redaction
  prerequisite as `ar_live_`, `ar_user_`, `ar_spa_plat_`, and `pk_live_`.
  It omits `arsk_`.
- Redacted scan of existing LO reports for Agent Red key-shaped values found
  8 matches across 2 files, including 3 `arsk` matches:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-08-21-14-15-DEPLOY-PIPELINE-HEAD-bfb27252-CARRY-FORWARD.md:78-80`
    contain `arsk`-prefixed values.
  - The same file also contains `ar_spa_plat`, `ar_user`, and `pk_live`
    values at lines 81-83.
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-28-08-07-LIVE-STOREFRONT-CHAT-VERIFICATION.md:44`
    and `:49` contain `pk_live` values.
- Current GroundTruth redaction is implemented at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3111-3146`.
  The existing pattern list does not include raw Agent Red key-family patterns.
- GroundTruth accepts `owner_decision` as an outcome at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3188-3190`.

## Findings

### P1 - Top-of-file verdict parsing still misses real report syntax

The proposed regex does not handle common Markdown verdict fields used by the
actual report corpus:

- `Verdict: \`GO\`` is captured, but `_parse_verdict_text()` does not strip
  inline-code backticks, so `GO` is not recognized.
- `**Verdict:** ...` is not captured because the colon appears before the
  closing bold markers, while the regex expects optional asterisks before the
  colon.

**Risk/impact:** Existing GO approvals are imported as `informational`. That
undermines the structured deliberation archive and preserves the manual
reconciliation burden the backfill is meant to remove.

**Required action:** Normalize Markdown wrappers before parsing verdict text
and fix the field regex to accept at least:

1. `Verdict: GO`
2. `Verdict: \`GO\``
3. `**Verdict:** GO`
4. `**Verdict:** \`GO\` for Phase N`
5. the same forms for `NO-GO`, `VERIFIED`, `LGTM`, and `owner_decision`

Add tests using actual corpus-derived examples, including the three files
cited above.

### P1 - Verdict section parsing ignores `# Final Verdict`

The proposal only parses `## Verdict`. The corpus includes `# Final Verdict`
sections where the first verdict-bearing line is a bullet below the heading.
The probe found that the proposed parser classified 9 of 10 `# Final Verdict`
reports as `informational`; the cited S231 admin-agent API review contains a
clear `NO-GO` final verdict.

**Risk/impact:** Negative reviews and approvals written in the older
`# Final Verdict` format will lose their outcome metadata during the bulk
import.

**Required action:** Generalize the section parser to handle heading levels
`#` through `######`, optional qualifiers such as `Final` or `Advisory`, blank
lines after the heading, and verdict bullets. Add tests for `# Final Verdict`
with a `NO-GO` bullet and a GO bullet.

### P1 - Redaction prerequisite omits an existing Agent Red key family

The latest prerequisite lists four raw Agent Red key families but omits
`arsk_`. Existing LO reports contain three `arsk` matches, so implementing the
v4 prerequisite literally would still allow those values to be copied into the
deliberation archive.

The earlier v2 proposal included `arsk_`, so this is a regression in the v4
summary, not a new scope request.

**Required action:** Keep `arsk_` in the GroundTruth redaction prerequisite and
tests. The redaction patterns should also use the valid generated-key character
set for each family, including hyphen support where Agent Red keys can contain
hyphens. The dry-run survivor scan must fail or warn if any
`ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_`, or `arsk_` values remain
after redaction.

## Required Conditions For GO

1. Fix top-of-file verdict parsing for Markdown bold and inline-code verdict
   fields used by existing reports.
2. Parse `# Final Verdict` / qualified verdict headings and bullet verdict
   lines, not only exact `## Verdict` headings.
3. Include `arsk_` in the GroundTruth redaction prerequisite and tests, with
   generated-key character classes that cover real Agent Red key shapes.
4. Add parser tests derived from the cited corpus examples.
5. Keep all prior requirements: GroundTruth redaction before import, Agent Red
   project-KB target, dry-run/apply gate, ordered SPEC/WI extraction, decimal
   SPEC regex, missing-ID reporting, conflict warnings, and temp-DB tests.

## Decision Needed From Owner

No owner decision is needed. Prime should revise the parser to match the
actual report corpus and keep the complete Agent Red key-family redaction
prerequisite before implementation.
