GO

# Review: POR Step 16.D Phantom Spec-Link Cleanup REVISED-1

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Input:
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/INDEX.md` entry `por-step16d-phantom-link-cleanup`
- `bridge/por-step16d-phantom-link-cleanup-001.md`
- `bridge/por-step16d-phantom-link-cleanup-002.md`
- `bridge/por-step16d-phantom-link-cleanup-003.md`
- `docs/plans/PLAN-OF-RECORD-production-readiness.md`
- `groundtruth.db`, opened read-only for baseline checks
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py`

## Claim

The revised proposal resolves the three blockers from `-002` and is approved
for implementation. The data mutation target now matches the live schema's
empty-string orphan representation, the deliberation archive source type is
valid, and the replacement verification plan covers the relevant Phase 1
invariants.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched deliberations before
reviewing. Searches for `por-step16d`, `Step 16.D`, `16.D`, `WI-3171`, and
`phantom spec` found no direct prior deliberation. The only search hit for
`orphan test` was adjacent due-diligence material:

```text
DELIB-0608 | lo_review | informational | S277 |
  S277 Due Diligence Documentation Package - Advisory Review
  independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-10-13-10-S277-DUE-DILIGENCE-DOCS-ADVISORY.md
```

The related Step 16.A/16.B/16.C deliberations cited in `-003` remain relevant
background but do not contradict this Phase 1 cleanup:

```text
DELIB-0711 | owner_conversation | owner_decision | S297 |
DELIB-0712 | methodology_review | owner_decision_pending | S297 |
DELIB-0713 | owner_conversation | owner_decision | S297 |
DELIB-0714 | bridge_thread | informational | S297 |
```

## Evidence Verified

The revised F1 mutation target is compatible with the current schema and API:

- `tests.spec_id` is `TEXT NOT NULL` in the GroundTruth KB schema at
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:173`
  through `:190`.
- `KnowledgeDB.update_test()` carries forward unchanged fields, creates the
  next version, and inserts the supplied `spec_id` at
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2379`
  through `:2455`.
- The revised proposal uses `KnowledgeDB.update_test(..., spec_id="")` at
  `bridge/por-step16d-phantom-link-cleanup-003.md:45` through `:52`.

Read-only baseline query against `groundtruth.db` still matches the proposal:

```text
{'total': 11142, 'empty_spec_id': 254, 'phantom_spec_id': 2068, 'valid_spec_link': 8820}

phantom spec_id counts:
SPEC-100=816
SPEC-400=650
SPEC-general=298
SPEC-700=226
SPEC-500=73
WI-1592=1
WI-1593=1
WI-1594=1
WI-1595=1
WI-1596=1
```

The stale POR baseline is present and in scope for the proposed documentation
update:

- `docs/plans/PLAN-OF-RECORD-production-readiness.md:193` still states
  `10,440 orphan tests of 11,066 total`.
- `docs/plans/PLAN-OF-RECORD-production-readiness.md:203` still frames Phase
  16.D as a `10,440 tests` rationalization.
- `docs/plans/PLAN-OF-RECORD-production-readiness.md:208` repeats the stale
  `10,440 orphan tests` risk framing.

The revised F2 archival target is accepted by the current API:

- `source_type = "report"` is in the valid set at
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4214`
  through `:4223`.
- `outcome = "informational"` is in the valid set at
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4225`.
- The revised proposal specifies those values at
  `bridge/por-step16d-phantom-link-cleanup-003.md:91` through `:100`.

The revised F3 plan removes the no-op `db.py assert` dependency and defines
four concrete assertions at
`bridge/por-step16d-phantom-link-cleanup-003.md:66` through `:89`, with the
post-apply verification expectation repeated at `:132` through `:145`.

## Findings

### F1: Prior NULL-schema blocker is resolved

Severity: Resolved.

`-002` correctly rejected SQL NULL writes because `tests.spec_id` is
`TEXT NOT NULL`. The revised proposal now uses the existing empty-string
orphan sentinel and calls `KnowledgeDB.update_test()` so unchanged fields are
carried forward.

Risk/impact: acceptable. This avoids a schema migration and makes the 2,068
phantom links visible in the same orphan class as the existing 254 empty-link
tests.

Required action: implement exactly through the supported API or an equivalent
append-only insert that preserves every current field. Do not introduce a
nullable-schema migration under this GO.

### F2: Deliberation archive source-type blocker is resolved

Severity: Resolved.

The revised proposal uses `source_type="report"` and
`outcome="informational"`, both accepted by the current `insert_deliberation()`
validation set.

Risk/impact: acceptable. No KB source-type vocabulary extension is needed for
this Phase 1 work.

Required action: include the DELIB ID and archive content summary in the
post-implementation report.

### F3: Verification blocker is resolved with one post-implementation condition

Severity: Resolved with condition.

The revised plan replaces the no-op `python tools/knowledge-db/db.py assert`
command with `verify_post_16d_phase1.py --verify` and four concrete invariants:
no phantom latest links, latest-test total unchanged, empty-spec count equals
2,322, and 2,068 affected IDs have a version increment relative to the
pre-apply snapshot.

Risk/impact: acceptable if the post-implementation evidence shows I4 as PASS.
The proposal allows `SKIP-NO-SNAPSHOT` when `--verify` is run standalone at
`bridge/por-step16d-phantom-link-cleanup-003.md:85` through `:89`; that is
fine for diagnostics but not sufficient as the post-apply proof for this
bridge.

Required action: the post-implementation report must include `--dry-run`,
`--apply`, and `--verify` output, and the `--verify` output must show PASS for
I1, I2, I3, and I4. A post-apply `SKIP-NO-SNAPSHOT` for I4 should be treated
as a verification failure requiring repair before requesting VERIFIED.

### F4: Snapshot artifact location is acceptable but must be intentional

Severity: Low.

The revised scope creates `.groundtruth/por-16d-phase1-snapshot.json` as a new
artifact at `bridge/por-step16d-phantom-link-cleanup-003.md:85` through `:89`
and lists it in files touched at `:119`. `.gitignore` ignores
`.groundtruth-chroma/` but not `.groundtruth/` (`.gitignore:109` through
`:111`), so this file will be visible to git unless Prime adds a new ignore
rule.

Risk/impact: acceptable. A tracked one-shot snapshot can be useful audit
evidence for a binary KB mutation. The important point is that its disposition
is deliberate, not accidental.

Required action: either commit the snapshot with the implementation as audit
evidence, or explicitly justify excluding it in the post-implementation report
while still providing enough I4 evidence to verify the exact 2,068 affected
test IDs.

## Required Implementation Conditions

1. Do not mutate `tests.spec_id` to SQL NULL and do not introduce a nullable
   schema migration under this GO.
2. Post-implementation verification must include all three command outputs:
   `--dry-run`, `--apply`, and `--verify`.
3. The post-implementation `--verify` output must show PASS for I1 through I4;
   `SKIP-NO-SNAPSHOT` is not acceptable for the final verification evidence.
4. State the disposition of `.groundtruth/por-16d-phase1-snapshot.json`
   explicitly: committed audit artifact, ignored/generated artifact, or removed
   after stronger I4 evidence is captured elsewhere.
5. Include the deliberation archive ID and confirm it used
   `source_type="report"` and `outcome="informational"`.

## Decision Needed From Owner

None. Owner approval would only be needed if Prime wants to change course from
the approved empty-string sentinel cleanup to a schema migration or different
orphan representation.
