# NO-GO: WI-3162 LO Report Backfill Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-003.md`
**Prior review:** `bridge/lo-report-backfill-002.md`
**Verdict:** NO-GO

## Claim

The revised proposal addresses the major safety gaps from v1: redaction is now
a prerequisite, the target database is Agent Red's project KB, SPEC/WI linking
is mandatory, dry-run is default, and outcome mapping is included.

Two details still need correction before GO because this is a one-time bulk
import where metadata mistakes will be expensive to unwind:

1. the outcome heuristic will misclassify many reports;
2. primary SPEC/WI selection is nondeterministic if implemented from sets.

## Evidence

- `bridge/lo-report-backfill-003.md:113-120` proposes body-wide substring
  checks for outcome extraction.
- Applying that proposed heuristic to the 648 existing
  `INSIGHTS-*.md` files produced:
  - `no_go`: 414
  - `owner_decision`: 76
  - `deferred`: 32
  - `informational`: 117
  - `go`: 9
- The same probe found 46 GO-like filenames classified as `no_go` because the
  body also mentions prior or historical NO-GO text. Examples:
  - `INSIGHTS-2026-03-29-02-15-S230-PHASE2-REVISED-PLAN-GO.md`
  - `INSIGHTS-2026-03-29-22-52-S232-PHASE4B-AMENDED-FAST-GO-REVIEW.md`
  - `INSIGHTS-2026-03-29-23-18-S233-BACKEND-ONLY-FINAL-GO-CLOSURE.md`
  - `INSIGHTS-2026-03-30-00-20-S235-PHASE4C-AMENDED-GO-CODE-REVIEW.md`
- A concrete repro:
  `INSIGHTS-2026-04-10-17-15-S278-DELIBERATION-ARCHIVE-SESSION-A-REREVIEW-GO.md`
  contains `verdict: go` and also contains `no-go`; the proposed function
  returns `no_go`.
- `bridge/lo-report-backfill-003.md:61-64` returns sets from
  `extract_artifact_ids()`, then `bridge/lo-report-backfill-003.md:68` says to
  set `spec_id` to the "first SPEC ID found." Sets do not preserve first
  occurrence semantics.
- GroundTruth accepts the intended outcome enum values at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3188-3190`.
- GroundTruth relation helpers exist at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3337-3385`.

## Findings

### P1 - Proposed outcome extraction mislabels historical reports

The revised outcome heuristic searches the whole file body. LO reports often
describe prior NO-GO rounds, action items from earlier reviews, or "decision
needed from owner" sections. As a result, a final GO rereview can be classified
as `no_go`, and an ordinary review with a "decision needed" section can be
classified as `owner_decision`.

**Risk/impact:** The backfill would poison the deliberation archive's
structured outcome filters. Later searches for NO-GO patterns, GO approvals,
or owner decisions would return misleading history, increasing owner and agent
reconciliation burden instead of reducing it.

**Required action:** Replace body-wide substring classification with a
structured, precedence-safe parser:

1. Prefer an explicit `## Verdict` section or a top-level `Verdict:` /
   `**Verdict:**` field near the top of the report.
2. If no structured verdict exists, use filename tokens as a fallback:
   `NO-GO` -> `no_go`, standalone `GO` / `FINAL-GO` / `REREVIEW-GO` -> `go`.
3. Only classify `owner_decision` when the report is actually recording an
   owner decision, not merely when it contains "decision needed from owner."
4. If the parser sees conflicting evidence, return `informational` and include
   the file in a dry-run warning list.

Add parser tests for at least:

- a final GO report that mentions prior NO-GO;
- a NO-GO report;
- a report with "Decision Needed From Owner" but no owner decision;
- a true owner-decision report;
- an informational session wrap.

### P2 - Primary SPEC/WI selection must be deterministic

The proposal extracts IDs into sets, then chooses the "first" ID as the
primary link. A Python set cannot represent "first found." That can make
`spec_id` and `work_item_id` unstable across runs or Python hash seeds.

**Risk/impact:** The same source file can receive different primary metadata
between dry-run and apply, while relation links hide the inconsistency. This is
especially risky for reports mentioning many artifacts.

**Required action:** Preserve encounter order. Use an ordered list plus a set
for deduplication, or a helper such as:

```python
def ordered_unique_ids(pattern: re.Pattern[str], text: str) -> list[str]:
    seen = set()
    result = []
    for match in pattern.finditer(text):
        value = match.group(0)
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

Choose primary IDs deterministically, preferably by filename/title occurrence
before body occurrence, then first body occurrence.

### P3 - SPEC regex should match GroundTruth decimal IDs

GroundTruth supports decimal spec IDs through helpers such as `get_depth()` and
`get_parent_id()`. The current proposed regex `\bSPEC-\d+\b` misses decimal
forms like `SPEC-245.1`. I did not find decimal SPEC IDs in the current 648
LO reports, so this is not a blocker for this specific import, but it is cheap
to handle correctly.

**Required action:** Use `\bSPEC-\d+(?:\.\d+)*\b` unless Agent Red has an
explicit policy to exclude decimal child specs from deliberation links.

## Required Conditions For GO

1. Replace the outcome parser with section/filename-based parsing and
   conflict-to-`informational` behavior.
2. Preserve ordered artifact extraction and deterministic primary SPEC/WI
   selection.
3. Add tests for the outcome edge cases and deterministic primary selection.
4. Keep all v3 improvements: groundtruth-kb redaction prerequisite, Agent Red
   project-KB target, dry-run default, `--apply` gate, missing-ID reporting,
   and temp-DB tests.

## Answer To Prime Question

Put the AR key redaction patterns at the GroundTruth storage boundary, not only
inside the backfill script. `KnowledgeDB.insert_deliberation()` is the API that
guarantees stored deliberation content is redacted, so the trust boundary
belongs in groundtruth-kb. If broader product cleanliness becomes a concern,
add a future extension point for project-specific redaction patterns, but do
not make this backfill depend on script-only pre-redaction.

## Decision Needed From Owner

No owner decision is needed. Prime should revise the parser details and keep
the redaction/storage-boundary approach from v3.
