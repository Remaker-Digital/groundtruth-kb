# Review: POR Step 16.D Phantom Spec-Link Cleanup

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Input:
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/INDEX.md` entry `por-step16d-phantom-link-cleanup`
- `bridge/por-step16d-phantom-link-cleanup-001.md`
- `docs/plans/PLAN-OF-RECORD-production-readiness.md`
- `groundtruth.db`, opened read-only for baseline/schema checks
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py`

## Claim

The live baseline correction is directionally valid, but the proposal cannot be
approved as written. Three executable details conflict with the current KB/API
surface: SQL NULL cannot be written to `tests.spec_id`, the proposed
deliberation `source_type` is rejected by the KB API, and one verification
command is presently a no-op.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched deliberations before
review.

Relevant current rows:

```text
DELIB-0711 | owner_conversation | owner_decision | S297 |
  Owner Decision: SPEC-GTKB-SCOPE test-evidence invariant exception |
  bridge/por-step16a-verified-spec-closure-005.md

DELIB-0712 | methodology_review | owner_decision_pending | S297 |
  POR Step 16.B methodology review: Phase 1.5 pattern does not generalize;
  5-stream multi-remediation scope for 16.C |
  bridge/por-step16b-methodology-review-002.md

DELIB-0713 | owner_conversation | owner_decision | S297 |
  Owner Decisions: POR 16.C Scope and Stream Configuration |
  bridge/por-step16b-methodology-review-006.md

DELIB-0714 | bridge_thread | informational | S297 |
  POR Step 16.C COMPLETE: All 193 implemented-untested specs remediated |
  bridge/por-step16c-implemented-untested-remediation-002.md

DELIB-0750 | bridge_thread | go |
  Bridge thread: por-step16c-implemented-untested-remediation (4 versions, VERIFIED)

DELIB-0751 | bridge_thread | go |
  Bridge thread: por-step16b-methodology-review (6 versions, VERIFIED)

DELIB-0754 | bridge_thread | go |
  Bridge thread: por-step16a-verified-spec-closure (10 versions, VERIFIED)
```

No prior deliberation contradicts the need to correct the POR 16.D baseline.
The blockers below are implementation/verification defects in the proposed
Phase 1 mechanics.

## Evidence Verified

The proposal's headline count is reproducible against the live Agent Red KB:

```text
baseline query:
{'total': 11142, 'empty_spec_id': 254, 'phantom_spec_id': 2068, 'valid_spec_link': 8820}

WI-prefixed phantom: 5
distinct phantom ids: 10
top phantom ids:
SPEC-100=816, SPEC-400=650, SPEC-general=298, SPEC-700=226, SPEC-500=73,
WI-1592=1, WI-1593=1, WI-1594=1, WI-1595=1, WI-1596=1
```

The stale POR text is also present at
`docs/plans/PLAN-OF-RECORD-production-readiness.md:193`, and Phase 16.D still
describes the old 10,440-test framing at `:203`.

## Findings

### F1: The proposed NULL mutation is impossible under the current `tests` schema

Severity: Critical.

The proposal says to set the 2,068 phantom-linked latest tests to SQL NULL at
`bridge/por-step16d-phantom-link-cleanup-001.md:50` through `:55`, repeats
`spec_id = NULL` in the files-touched table at `:99`, and expects `--apply` to
insert 2,068 row versions with `spec_id = NULL` at `:121` through `:123`.

The live schema does not allow that:

```text
PRAGMA table_info(tests) for spec_id:
{'cid': 4, 'name': 'spec_id', 'type': 'TEXT', 'notnull': 1, 'dflt_value': None, 'pk': 0}

empty representation:
{'null_spec_id': 0, 'empty_string_spec_id': 254}
```

The package schema matches this: `tests.spec_id TEXT NOT NULL` is defined in
`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:176`
through `:178`. The existing orphan state is therefore the empty string, not
SQL NULL.

Risk/impact: `--apply` will fail on the first attempted NULL insert/update, or
Prime will need an unapproved schema migration. Either outcome breaks Phase 1's
core operation and leaves the POR correction only partially implemented.

Required action:
- Revise the cleanup target to the existing orphan sentinel `spec_id = ''`, or
  explicitly propose and justify a schema migration that makes `tests.spec_id`
  nullable.
- Prefer `KnowledgeDB.update_test(id, ..., spec_id="")` over raw `insert_test`
  recreation so unchanged fields are carried forward by the API. If `insert_test`
  is retained, the proposal must require copying every current column.
- Update all wording and expected output from "NULL"/"nulled" to the chosen
  representation.

### F2: `source_type = "prime_methodology_correction"` is not accepted by the KB API

Severity: High.

The proposal requires archiving the baseline correction with
`source_type = "prime_methodology_correction"` at
`bridge/por-step16d-phantom-link-cleanup-001.md:90` through `:91`.

Current `KnowledgeDB.insert_deliberation()` accepts only:

```text
['bridge_thread', 'lo_review', 'owner_conversation', 'proposal', 'report', 'session_harvest']
```

Evidence:
- Valid source-type set:
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4214`
  through `:4223`
- Dry-run API check:

```text
ValueError: Invalid source_type 'prime_methodology_correction'; must be one of
['bridge_thread', 'lo_review', 'owner_conversation', 'proposal', 'report', 'session_harvest']
```

Risk/impact: the deliberation archival step will fail if implemented through
the supported KB API. Bypassing the API with direct SQL would create an
inconsistent source-type vocabulary and should not be approved silently.

Required action:
- Use an accepted source type, likely `report` or `bridge_thread`, with
  `outcome='informational'`; or
- File a separate GroundTruth KB/source-type extension proposal before relying
  on `prime_methodology_correction`.

### F3: The proposed `db.py assert` verification command currently verifies nothing

Severity: High.

The verification plan says to run `python tools/knowledge-db/db.py assert` and
expect "no new failures" at
`bridge/por-step16d-phantom-link-cleanup-001.md:128` through `:130`.

In this checkout, `tools/knowledge-db/db.py` is a re-export shim. It sets
`DB_PATH` at `tools/knowledge-db/db.py:42`, defines the wrapper
`KnowledgeDB` at `:98`, and exports symbols at `:126`, but it has no CLI
entrypoint. Running the proposed command produced no output and a success code:

```text
python tools/knowledge-db/db.py assert
EXIT=0
```

Risk/impact: the post-implementation report could claim assertion coverage from
a command that performed no assertion work. That is especially risky because
Phase 1 mutates 2,068 append-only test rows in `groundtruth.db`.

Required action:
- Replace `python tools/knowledge-db/db.py assert` with a working assertion
  command for the current GroundTruth KB package/API, and require the
  post-implementation report to include its stdout.
- If no project-native assertion CLI exists, make the new
  `verify_post_16d_phase1.py --verify` script explicitly cover the invariants
  Phase 1 needs: no phantom latest test links, total latest-test count unchanged,
  exactly 2,322 latest tests with `spec_id=''`, and row-version increment count
  for the 2,068 affected IDs.

## Non-Blocking Notes

- The corrected baseline itself is supported by read-only SQL: 11,142 latest
  tests, 254 existing empty-string orphans, 2,068 phantom links, and 8,820 valid
  current spec links.
- Updating the POR's stale `10,440 orphan tests of 11,066 total` statement is
  appropriate, but the text should reflect the actual storage representation
  chosen after F1 is resolved.

## Required Action Items

1. Revise the proposal's data mutation from SQL NULL to the current empty-string
   orphan representation, unless a separate schema migration is explicitly
   proposed and approved.
2. Revise the deliberation archival step to use a valid KB `source_type`, or
   split a source-type extension into separate work.
3. Replace the no-op `db.py assert` verification command with a real current
   verification command and specify the required post-implementation evidence.
4. Refile as `bridge/por-step16d-phantom-link-cleanup-003.md` with these changes.

## Decision Needed From Owner

None for this NO-GO. An owner decision is only needed if Prime wants to change
the KB schema to allow nullable `tests.spec_id` instead of using the existing
empty-string orphan sentinel.
