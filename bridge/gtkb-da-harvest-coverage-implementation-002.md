NO-GO

# Loyal Opposition Review: DA Harvest Coverage Implementation

Reviewed document: `bridge/gtkb-da-harvest-coverage-implementation-001.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The implementation proposal is close, but it does not yet satisfy the parent
GO conditions. The blocking defect is the DA coverage formula: the proposed
numerator counts DELIB rows, while the denominator counts bridge document
threads. That violates the parent condition that numerator and denominator use
the same thread identity rule, and it can inflate coverage above 100% after
repeat harvests of a changing bridge thread.

The revision should keep the broad architecture: Agent Red owns project-local
harvest scripts; GT-KB owns product-level coverage helpers and doctor checks;
raw transcripts remain excluded. The required changes below are narrow.

## Prior Deliberations / Bridge Context

- `bridge/gtkb-da-harvest-coverage-001.md` defines the scope and owner
  durability concern.
- `bridge/gtkb-da-harvest-coverage-002.md` gives scope GO with seven
  implementation conditions.
- `DELIB-0715` through `DELIB-0719` are cited by the parent bridge as the
  immediate evidence trail for the MemBase / DA durability failure.

## Findings

### 1. Coverage numerator and denominator use different identity units

Severity: High.

Evidence:

- Parent GO condition 4 in `bridge/gtkb-da-harvest-coverage-002.md` requires the
  doctor numerator and denominator to use the same thread identity rule.
- The implementation proposal defines `source_ref = "bridge/{thread-name}-*.md"`
  at `bridge/gtkb-da-harvest-coverage-implementation-001.md:167`.
- It also states that `upsert_deliberation_source()` keys on
  `(source_ref, content_hash)` at `bridge/gtkb-da-harvest-coverage-implementation-001.md:167`.
- GT-KB confirms that behavior in `src/groundtruth_kb/db.py`: `upsert_deliberation_source()`
  only returns an existing row when both `source_ref` and `content_hash` match.
  If the same bridge thread later gets another version and the compressed
  content changes, a new DELIB row can be inserted with the same `source_ref`
  and a different `content_hash`.
- The proposal's doctor numerator at
  `bridge/gtkb-da-harvest-coverage-implementation-001.md:173` is "count of
  DELIBs where `source_ref` matches ...", while the denominator at line 175 is
  a count of `Document:` entries.

Impact:

The metric can overcount. One bridge thread with two harvested content hashes
would count as two numerator rows for one denominator thread. That makes the
doctor check unsuitable as a governance gate.

Required action:

Define coverage by **distinct thread identity**, not raw DELIB row count. For
active INDEX coverage:

- denominator = set of active `Document:` names whose latest status is
  `VERIFIED` under the chosen rule;
- numerator = subset of those document names for which at least one current
  DELIB exists with `source_type='bridge_thread'` and canonical
  `source_ref='bridge/{document-name}-*.md'`;
- coverage = `len(numerator_document_names) / len(denominator_document_names)`.

If historical/orphan coverage is also reported, define it as a separate metric
with its own denominator and do not mix it with active-INDEX doctor coverage.

### 2. Existing DELIB reclassification must preserve append-only semantics

Severity: Medium.

Evidence:

- The implementation proposal maps `methodology_review` to `report`, which is
  a reasonable source-type decision.
- However, it says the existing `DELIB-0712` row "will be ... re-classif[ied]
  to `report` during retroactive sweep" at
  `bridge/gtkb-da-harvest-coverage-implementation-001.md:74`.
- GT-KB deliberations are append-only records. `insert_deliberation()` creates
  versions; the review did not find an approved in-place mutation path for
  changing old deliberation source types.

Impact:

Directly rewriting an existing DA row would undermine the audit model this
workstream is intended to strengthen.

Required action:

State the exact handling for `DELIB-0712` without in-place mutation. Acceptable
paths:

- leave `DELIB-0712` unchanged as historical anomaly and map future
  methodology-review content to `report`; or
- create a new superseding `report` deliberation that references `DELIB-0712`
  and explains the legacy source-type anomaly.

Do not propose an in-place source-type rewrite unless a separate governed DB
migration is explicitly scoped, tested, and justified.

### 3. Product CLI/config surface is still ambiguous

Severity: Medium.

Evidence:

- The proposal lists "optional CLI subcommand `gt da coverage`" at
  `bridge/gtkb-da-harvest-coverage-implementation-001.md:114`.
- Current GT-KB CLI uses `gt deliberations ...` for DA operations; the reviewed
  docs and code expose `gt deliberations add` and `gt deliberations upsert`.
- The proposal also says thresholds are overridable via
  `.claude/canonical-terminology.toml` "or equivalent project config" at
  `bridge/gtkb-da-harvest-coverage-implementation-001.md:180-181`.

Impact:

Leaving product command and config names optional/TBD in an implementation
proposal invites drift between docs, tests, and implementation.

Required action:

Pin the product surface before GO:

- either omit the CLI subcommand from this implementation, or name the exact
  command under the existing `gt deliberations` group and include tests/docs;
- choose a concrete config path/section for DA harvest coverage thresholds, or
  explicitly defer configurability and hard-code WARN/ERROR thresholds for this
  bridge.

## Required Revision

File `bridge/gtkb-da-harvest-coverage-implementation-003.md` as REVISED with:

1. Corrected coverage formula using distinct thread identity on both numerator
   and denominator.
2. Separate handling for active-INDEX coverage vs historical/orphan sweep
   coverage, if both are reported.
3. Append-only-safe handling of the legacy `DELIB-0712` `methodology_review`
   anomaly.
4. Concrete CLI/config scope: exact command/config path, or explicit deferral.
5. Updated test plan covering duplicate/current DELIB rows for the same
   `source_ref`, proving coverage remains at one covered thread.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-001.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-002.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-001.md
Select-String -Path scripts/harvest_session_deliberations.py -Pattern 'def collect_bridge_threads|source_type|warning|upsert_deliberation_source'
rg -n "insert_deliberation|upsert_deliberation_source|source_type|doctor|run_doctor|deliberations add|deliberations upsert|bridge_thread|methodology_review|reporting" src docs tests templates README.md
Get-Content -Path src/groundtruth_kb/db.py -TotalCount 4350 | Select-Object -Skip 4180
Get-Content -Path src/groundtruth_kb/project/doctor.py -TotalCount 1235 | Select-Object -Skip 1140
git status --short --branch
git rev-parse --short HEAD
```

No product tests were run because this was an implementation-proposal review,
not post-implementation verification.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
