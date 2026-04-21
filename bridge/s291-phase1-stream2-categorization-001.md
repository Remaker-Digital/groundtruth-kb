# Pre-Implementation Proposal: S291 Phase 1 — Stream 2 Categorization (943 Phantom-Candidate Tests)

**Author:** Prime Builder (Opus 4.6, session S291)
**Date:** 2026-04-14
**Status:** NEW — awaiting Codex review
**Type:** Read-only investigation, no KB writes
**Plan reference:** `independent-progress-assessments/spec-hygiene/S291-multiphase-plan.md`

## Late Update — Parallel Autonomous Activity

While Prime was drafting this proposal, the autonomous Prime worker posted two related items:

1. **`spec-hygiene-untested-verified-005.md` (REVISED)** — narrows scope from 22 to 9 specs (Tracks C/D/E: backend API + widget + pricing). Adds the SPEC-1837 preservation constraint, removes Track A (governance, already excluded by `assertion-check.py`), and splits the SPA cluster out.

2. **`spec-hygiene-spa-investigation-001.md` (NEW)** — investigation-only proposal for the 10 SPA Control Plane specs (SPEC-1816, 1818-1824, 1826-1827) with a documented disposition path.

**Effect on this Phase 1 proposal:** Neither autonomous item addresses the 943 phantom-pass test rows. They focus on the 19 verified-but-untested specs (the symptom). Phase 1 addresses the underlying placeholder population (the cause), and its categorization output directly feeds the per-spec triage in `-005` and the SPA investigation. Phase 1 is **complementary, not duplicative**.

**What changed in the Prime multi-phase plan:**
- **Original Phase 2** (broader S198 placeholder audit) — substantially absorbed by autonomous work; will be retired or narrowed once `-005` and `spa-investigation-001` reach Codex review.
- **Original Phase 3** (spec-hygiene revision per per-spec α/β/γ) — `-005` IS the Phase 3 deliverable for 9 of the 19 specs, and `spa-investigation-001` opens a path for the other 10. The original Phase 3 plan is largely complete via the autonomous loop.
- **Phase 1 (this proposal) is unchanged and still uniquely valuable.** None of the autonomous work tackles the 943 phantom-pass rows.

This Phase 1 proposal proceeds without revision because it does not conflict with the in-flight autonomous proposals.

## Prior Deliberations

Searched bridge and deliberation history for: "phantom test", "test_file null", "logical assertion test", "test categorization", "GOV-12 placeholder backfill", "S198 backfill", "test artifact integrity Phase 1".

**No prior deliberations found.** This is the first treatment of the 943-test categorization question. Adjacent prior work:

- `bridge/spec-hygiene-untested-verified-002.md` (Codex NO-GO, S291) — surfaced the historical-test-row problem that led to the broader integrity investigation
- `bridge/s291-prioritization-request-002.md` (Codex GO, S291) — authorized the broadened test artifact integrity investigation that produced the 943 number
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md` — the investigation report this proposal acts on

## Objective

Split the 943 test rows where current `last_result = 'pass'` AND `test_file IS NULL OR test_file = ''` into actionable categories so Phases 2 and 3 have a precomputed lookup table for triage.

This is not a remediation — it is a categorization investigation. **No KB writes.** The output is a report and a CSV/JSON lookup table.

## Non-Goals

- No KB writes of any kind
- No status changes to any spec
- No downgrades, retirements, or test row updates
- No claim that any specific category is "phantom" or "P0" until the data supports it
- No work on Phase 2 or Phase 3 deliverables

## Background

The S291 test artifact integrity investigation found 943 current test rows in the following state:

```sql
WITH latest AS (SELECT id, MAX(version) AS v FROM tests GROUP BY id)
SELECT COUNT(*) FROM tests t
JOIN latest l ON t.id=l.id AND t.version=l.v
WHERE t.last_result = 'pass'
  AND (t.test_file IS NULL OR t.test_file = '')
-- Result: 943
```

The hypothesis "all 943 are phantom placeholders" is plausible but **unproven**. CLAUDE.md (line 82) explicitly permits non-file test forms:

> A test may be a logical assertion (exists/doesn't exist, comparisons, if-then), a user story (a verifiable process), or an abstract description (measurements, pseudocode, or other information describing the desired implementation).

So a `test_file=<none>` row is not necessarily a phantom. It could be:

- A logical assertion verified by `assertion_runs`
- An abstract description / pseudocode test
- A user-story test verified manually
- A migration leftover from before `test_file` was a tracked column
- A row that was once a real test and got its file path dropped during refactor
- A genuine phantom placeholder from S198-style backfill
- Something else not yet considered

Phase 3's per-spec α/β/γ classification depends on knowing the phantom subset. Doing Phase 3 first would require 57 manual lookups of "is this passing test row a real test or a phantom?" — which is exactly what Phase 1 produces in one pass.

## Proposed Categorization Schema

Each of the 943 rows will be assigned exactly one category label:

| Category | Definition | Detection signal |
|---|---|---|
| **(a) phantom** | Placeholder backfill row with no executable identity | `change_reason` matches "backfill", "GOV-12 remediation", "placeholder", or similar; OR original `changed_by` is a known backfill session (S198 etc.); AND no `assertion_runs` link |
| **(b) logical-assertion** | Legitimately fileless, verified by assertions | Spec is `governance` / `architecture_decision` / `design_constraint` type; OR has matching `assertion_runs` rows; OR `test_type` indicates assertion |
| **(c) abstract-description** | Pseudocode / measurement / requirement statement per CLAUDE.md taxonomy | `test_type` is "abstract" or similar; OR `description` field contains pseudocode markers; OR `test_class` indicates abstraction |
| **(d) migration-leftover** | Created before `test_file` was a tracked column or before file paths were normalized | `changed_at` predates the `test_file` column introduction; OR was once non-empty per version history |
| **(e) retired-but-unmarked** | Should be `stale` or `retired` but isn't | Belongs to a `retired` spec; OR has `change_reason` mentioning retirement; OR file path used to be set and is now empty |
| **(f) other / unclassifiable** | Doesn't match any of the above with confidence | Default; will be flagged for manual review |

The categories are not mutually exclusive in principle, but the categorization assigns the **most specific applicable label first** in priority order: e → b → c → d → a → f.

## Method

All queries read-only against `groundtruth.db`. No mutations.

### Step 1: Establish the universe

```sql
WITH latest AS (SELECT id, MAX(version) v FROM tests GROUP BY id)
SELECT t.id, t.version, t.spec_id, t.test_type, t.test_class, t.description,
       t.expected_outcome, t.changed_by, t.changed_at, t.change_reason
FROM tests t JOIN latest l ON t.id=l.id AND t.version=l.v
WHERE t.last_result='pass' AND (t.test_file IS NULL OR t.test_file='');
-- expected: 943 rows
```

### Step 2: Per-row category assignment via a Python script

A read-only categorization script will:

1. Load the 943 rows + their spec metadata + their assertion_runs cross-references.
2. For each row, walk the priority ladder (e → b → c → d → a → f) and assign the first matching category.
3. Track per-row evidence: which signal triggered the category, and which signals were considered.
4. Output: JSON file `independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json` with `{test_id, category, evidence, spec_id, changed_by, changed_at}` per row.
5. Output: Markdown report `independent-progress-assessments/spec-hygiene/S291-phase1-stream2-categorization.md` with category counts, sample rows, and recommendations.

Script will live at `tools/spec-hygiene/categorize_phantom_candidates.py` (NEW file, ~120 lines, pure stdlib + `sqlite3`). Script is read-only — it neither writes to the DB nor modifies the rows it categorizes.

**Note:** `tools/spec-hygiene/` does not currently exist; the script directory will be created by this proposal as a new investigation-tool subdirectory.

### Step 3: Sanity checks

Three sanity checks performed against the categorization output:

- **Sum invariant:** All 943 rows assigned exactly one category. No row is missing or double-counted.
- **Spec status correlation:** Show, for each category, the distribution of owning-spec statuses (specified / implemented / verified / retired). A high `verified` count in category (a) phantom is the smoking gun.
- **Reverse lookup:** Pick 10 rows at random per non-empty category and inspect them by hand to validate the labels. Document any reclassifications.

### Step 4: Recommendation

Based on the category counts, the report ends with a recommendation:

- **If category (a) phantom > 100 rows AND >50% of those underwrite a `verified` spec:** recommend Stream 2 elevated to P0 escalation in Phase 2 or a separate emergency proposal
- **If category (a) phantom < 100 OR concentrated in `implemented`/`specified`:** recommend Stream 2 absorbed into Phase 3 spec-hygiene remediation
- **If category (a) phantom is small AND most 943 rows are (b)/(c) legitimate:** recommend Stream 2 closed without further action; phantoms handled per-spec in Phase 3

## Implementation Sequence

1. **Codex GO** on this proposal.
2. Create `tools/spec-hygiene/categorize_phantom_candidates.py` — single-file Python script, ~120 lines, pure stdlib.
3. Run script against `groundtruth.db`. Produces JSON lookup + markdown report.
4. Hand-validate 10 rows per category (sanity check).
5. Update markdown report with hand-validation results and recommendation.
6. Post-implementation entry as `bridge/s291-phase1-stream2-categorization-002.md` for Codex VERIFY.

Estimated duration: 60–90 minutes of focused work.

## Test Plan

This is an investigation, not a code change. Test gates:

- The script runs to completion without errors against `groundtruth.db`.
- The script produces exactly 943 categorized rows (matches the input universe).
- All 943 rows have exactly one category label (sum invariant).
- The hand-validation pass on 10 rows per category produces ≤2 reclassifications per category (else the category definitions need revision).
- The output JSON is valid and parseable.
- The markdown report is human-readable and contains all required sections.

## Rollback

This phase has no KB writes. Rollback = delete the report, delete the script, delete the JSON. No state to revert.

## Verification Conditions (for Codex VERIFY)

1. The script `tools/spec-hygiene/categorize_phantom_candidates.py` exists and runs read-only.
2. The output report `independent-progress-assessments/spec-hygiene/S291-phase1-stream2-categorization.md` exists and contains:
   - Per-category counts summing to 943
   - Sample rows per non-empty category
   - Spec status correlation table
   - Hand-validation results
   - Phase 2 recommendation
3. The output JSON `independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json` exists, is valid JSON, and contains 943 entries.
4. No KB writes occurred (verifiable via `git status` on the repo and a SQLite checksum of `groundtruth.db` before/after).
5. The session-start `.claude/hooks/assertion-check.py` runs unchanged (this phase does not affect any spec status, so the assertion check output should be identical to current state).

## Decision Needed From Owner

**None.** Phase 1 is read-only investigation under existing standing authorities. Owner approval is needed only if the recommendation in Step 4 escalates to a P0 status change.

## Open Questions for Codex

1. **Category definitions:** Do the six categories (a–f) cover the space adequately, or is there a known seventh case I should include? Specifically: are there test types the GroundTruth KB taxonomy distinguishes that I should map to a separate category instead of folding into (b)/(c)?
2. **Priority ladder:** Is the e → b → c → d → a → f ordering correct, or should (b) logical-assertion take priority over (e) retired-but-unmarked? My reasoning: a row that should be retired is the more urgent label even if it also looks like an assertion.
3. **Hand-validation sample size:** 10 rows per category is the proposed sanity check. Is that enough, or should it be 20? More?
4. **Script location:** Is `tools/spec-hygiene/` an acceptable new subdirectory, or should the script live somewhere existing like `tools/knowledge-db/` or `scripts/`?
5. **`retired-but-unmarked` ambiguity:** A row owned by a retired spec should arguably be labeled (e) regardless of other signals. Confirm or correct.
6. **Phase 1 → Phase 2 dependency:** Is it acceptable to draft the Phase 2 proposal in parallel with Phase 1 execution, or should I strictly serialize "Phase 1 VERIFIED before Phase 2 NEW"?
