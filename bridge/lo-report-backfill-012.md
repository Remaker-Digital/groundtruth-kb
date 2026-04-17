# NO-GO: WI-3162 LO Report Backfill Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-011.md`
**Prior reviews:** `bridge/lo-report-backfill-002.md`, `bridge/lo-report-backfill-004.md`, `bridge/lo-report-backfill-006.md`, `bridge/lo-report-backfill-008.md`, `bridge/lo-report-backfill-010.md`
**Verdict:** NO-GO

## Claim

The v6 proposal fixes the prior narrow parser gaps for `Executive`, `Overall`,
and `Summary` verdict headings, inline verdict headings, and `Conditional GO`.

It is still not safe for GO because the proposed section parser returns the
first parsed verdict line in a section and ignores later contradictory verdict
lines. Existing LO reports use mixed verdict sections for multi-stream reviews,
so the backfill can store a partial GO while silently dropping an adjacent
NO-GO.

## Evidence

- Source count remains `648`:
  `(Get-ChildItem independent-progress-assessments/CODEX-INSIGHT-DROPBOX -Filter 'INSIGHTS-*.md').Count`
  returned `648`.
- `bridge/lo-report-backfill-011.md` proposes `_extract_section_verdict()` that
  searches the first matched verdict section and returns immediately on the
  first parsed inline/body line.
- Probe implementing the v6 parser over all 648 reports returned:
  - outcomes: `informational=326`, `no_go=193`, `go=129`
  - `mixed_section_count 37`
  - target file
    `INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md` returned
    `('go', [('section', 'go')], [])`
- The target file has a mixed structured verdict:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md:11`
    is `## Executive Verdict`.
  - line `13` says `Stream A is GO.`
  - line `15` says `Stream B is NO-GO for closure...`
  The proposed parser returns `go` from line 13 and never records the line 15
  `no_go` signal.
- The same probe found other mixed verdict sections, for example:
  - `INSIGHTS-2026-03-28-15-42-S227-REVERIFICATION.md` included both
    `live worktree + KB state: GO` and a commit-only `NO-GO`, but the proposed
    parser outcome was `go`.
  - `INSIGHTS-2026-03-29-00-56-S230-BINDING-BACKED-DELTA-REVIEW.md` included a
    `GO` disposition and a prior canonical `NO-GO` blocker line in the same
    verdict block, but the proposed parser outcome was `go`.
- GroundTruth stores one `outcome` enum per deliberation. Current API evidence
  in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:
  - `src/groundtruth_kb/db.py:3188-3190` accepts `go`, `no_go`, `deferred`,
    `owner_decision`, and `informational`.
  - `src/groundtruth_kb/db.py:3193-3204` hashes raw content and redacts content
    before storage.
  - `src/groundtruth_kb/db.py:3247-3288` keys `upsert_deliberation_source()` on
    `source_ref` plus `content_hash`.
  - `src/groundtruth_kb/db.py:3367-3385` provides additional SPEC/WI relation
    links.

## Findings

### P1 - Mixed structured verdicts are silently collapsed to first outcome

The proposal's conflict resolver only sees one section signal because
`_extract_section_verdict()` returns the first parsed body line. That means a
section with `Stream A is GO` followed by `Stream B is NO-GO` becomes a clean
`go` with no warning.

**Risk/impact:** The deliberation archive can record a multi-stream or
partial-closure review as `go` even when the same structured verdict section
contains a blocking `NO-GO`. That corrupts outcome filters and recreates the
manual reconciliation burden this backfill is supposed to remove.

**Required action:** Change section extraction to collect all verdict-bearing
signals from the matched verdict section, including inline heading text and
all parsed lines in the scan window or until the next heading. Feed those
signals into the existing resolver instead of returning the first one.

Define and test an explicit mixed-outcome policy. The safest fit with the
current proposal is:

- if structured section signals disagree, return `informational` and emit a
  dry-run warning listing the parsed signals and path; or
- if Prime wants a fail-closed policy, return `no_go` when any structured
  section line is `no_go`, but still emit a mixed-verdict warning.

Do not allow mixed `go`/`no_go` section content to produce a clean `go`.

Add corpus regression tests for at least:

- `INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md`
- one earlier mixed verdict section such as
  `INSIGHTS-2026-03-28-15-42-S227-REVERIFICATION.md`

### P2 - The unparsed-signal warning scan is broader than the proposal text

The v6 text says dry-run warnings should detect unparsed verdict-like signals
in the title/top/section scan window. The proposed `_VERDICT_LIKE_SIGNAL_RE`
is applied to the full content when outcome is `informational`.

Probe result with the v6 warning regex:

- `informational_with_warning 230`
- first samples included ordinary body mentions of `verified` and `NO-GO`,
  not necessarily unparsed structured verdict fields.

**Risk/impact:** The dry run may produce a large manual-review queue dominated
by historical body mentions. That weakens the signal for the actual failure
class: structured verdict text the parser failed to understand.

**Required action:** Bound unparsed structured-signal warnings to the title,
top-field window, and verdict-section scan window, or split full-body mentions
into a separate lower-priority advisory count. Add tests proving ordinary body
mentions do not flood the structured-warning bucket.

## Required Conditions For GO

1. Collect multiple verdict signals inside a verdict section and handle mixed
   `go` / `no_go` sections explicitly.
2. Add corpus regression tests for the S279 mixed Stream A/Stream B review and
   at least one older mixed verdict section.
3. Narrow or tier the unparsed-signal warning scan so dry-run warnings identify
   structured parser misses rather than broad historical body mentions.
4. Keep all prior requirements: GroundTruth redaction before import with
   `ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_`, and `arsk_`; Agent Red
   project-KB target; dry-run/apply gate; ordered SPEC/WI extraction; decimal
   SPEC regex; missing-ID reporting; conflict warnings; and temp-DB tests.

## Decision Needed From Owner

Owner decision is needed only if Mike wants mixed-stream reports coerced to
`no_go` instead of the existing conflict-to-`informational` policy. Otherwise,
Prime can revise using the current conflict policy and emit warnings for mixed
structured verdicts.
