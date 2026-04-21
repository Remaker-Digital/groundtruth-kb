# NO-GO: WI-3162 LO Report Backfill Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-005.md`
**Prior reviews:** `bridge/lo-report-backfill-002.md`, `bridge/lo-report-backfill-004.md`
**Verdict:** NO-GO

## Claim

The latest revision preserves the important safety requirements from v2:
GroundTruth redaction first, Agent Red project-KB target, dry-run by default,
SPEC/WI linking, deterministic ID extraction, and decimal SPEC support.

It is still not ready for GO because the revised outcome parser does not match
its own stated behavior or test plan. That matters because this is a bulk import
into structured deliberation metadata, and wrong outcomes will be expensive to
repair after apply.

## Evidence

- `bridge/lo-report-backfill-005.md:18` promises a section-based and
  filename-based parser with conflict fallback.
- `bridge/lo-report-backfill-005.md:49-60` checks a `## Verdict` section only
  after filename matching.
- `bridge/lo-report-backfill-005.md:43-45` uses
  `re.search(r'(?<!NO-)GO(?!OD)', fn_upper)` for filename GO detection.
- `bridge/lo-report-backfill-005.md:66-70` says `owner_decision` is set only
  from an explicit `Verdict: owner_decision` field and ambiguous evidence falls
  back to `informational`.
- `bridge/lo-report-backfill-005.md:120-128` includes tests expecting
  `Verdict: owner_decision` to return `owner_decision`.
- The proposed function, copied directly into a probe, returned:
  - `**Verdict:** owner_decision` -> `informational`
  - `INSIGHTS-2026-03-30-10-57-ARCH-TECH-GOVERNANCE-AUDIT.md` with
    `## Verdict` / `Not yet.` -> `go`
  - `## Verdict` / `NO-GO` -> `no_go`
- The concrete governance report starts with `# Architecture / Technology-Choice
  Governance Audit` and has `## Verdict` / `Not yet.` at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-30-10-57-ARCH-TECH-GOVERNANCE-AUDIT.md:14-16`.
- GroundTruth accepts `owner_decision` as a valid outcome at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3188-3190`.

## Findings

### P1 - `owner_decision` is promised and tested but not parsed

The code sample handles `no_go`, `go`, `lgtm`, and `verified`, but it never
returns `owner_decision` for an explicit `Verdict: owner_decision` field. The
test plan says this case should pass, and GroundTruth has `owner_decision` as a
valid enum.

**Risk/impact:** True owner decisions would be stored as `informational`, hiding
the exact records the owner and agents most need to retrieve as binding
decisions.

**Required action:** Add explicit parsing for `owner_decision` in both the
top-of-file verdict field and the `## Verdict` section parser. Add the proposed
test before implementation is considered complete.

### P1 - Filename GO detection can override a structured non-GO verdict

The parser checks filenames before it checks `## Verdict` sections. Its GO regex
also matches `GO` inside words such as `GOVERNANCE`. The existing governance
audit report has a structured `## Verdict` value of `Not yet.`, but the proposed
function returns `go` because the filename contains `GOVERNANCE`.

**Risk/impact:** Informational audits and negative/unfinished assessments can be
imported as GO approvals. That poisons the deliberation archive's structured
filters and creates false historical approvals.

**Required action:** Parse structured verdict sections before filename fallback,
and tokenize filename verdicts instead of searching for raw `GO` substrings.
For example, split the stem on non-alphanumeric separators and accept `GO`,
`FINAL-GO`, `REREVIEW-GO`, or `VERIFIED` only as explicit tokens/phrases. Add a
regression test for the governance-audit filename.

### P2 - Conflict fallback is stated but not implemented

The proposal says conflicting or ambiguous evidence returns `informational`, but
the code returns as soon as it sees the first matching signal. There is no
collection of signals and no conflict check.

**Risk/impact:** A report with inconsistent top matter, filename, and section
signals can still be forced into a structured outcome instead of being surfaced
in dry-run warnings for human review.

**Required action:** Implement conflict handling explicitly: collect structured
field, section, and filename signals; if multiple non-identical signals are
present, return `informational` and add the source file to the dry-run warning
list.

## Required Conditions For GO

1. Parse explicit `owner_decision` verdicts.
2. Check top-of-file verdict fields and `## Verdict` sections before filename
   fallback.
3. Replace substring filename matching with token/phrase-based verdict matching.
4. Implement the promised conflict-to-`informational` behavior and dry-run
   warning list.
5. Keep the v3 improvements: GroundTruth redaction prerequisite, Agent Red
   project-KB target, dry-run/apply gate, ordered SPEC/WI extraction, decimal
   SPEC regex, missing-ID reporting, and temp-DB tests.

## Decision Needed From Owner

No owner decision is needed. Prime should revise the parser details and keep
the rest of the v3 backfill plan.
