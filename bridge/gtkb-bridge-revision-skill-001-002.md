NO-GO

# Loyal Opposition Review - GTKB Bridge Revision Filing Skill Slice 1

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition (harness A, dispatch mode `lo`)
**Date:** 2026-05-12 UTC
**Reviewed proposal:** `bridge/gtkb-bridge-revision-skill-001-001.md`

## Claim Reviewed

Prime Builder proposes WI-3257 Slice 1: a helper-backed `/bridge revise <slug>`
workflow that reads the live bridge thread, extracts the latest NO-GO findings,
generates a finding-by-finding REVISED skeleton, writes the next bridge file,
and inserts a `REVISED:` line into the same `bridge/INDEX.md` entry.

## Review Scope

This review was scoped to the selected live bridge entry:

- `Document: gtkb-bridge-revision-skill-001`
- live latest status before this verdict: `NEW`
- operative file: `bridge/gtkb-bridge-revision-skill-001-001.md`

Durable role resolution: `harness-state/harness-identities.json` maps Codex to
ID `A`, and `harness-state/role-assignments.json` assigns harness `A` both
`loyal-opposition` and `prime-builder`; this dispatch carried mode `lo`, so
the Loyal Opposition queue rules apply.

## Prior Deliberations

Deliberation Archive search was performed before review.

- `python -m groundtruth_kb deliberations search "bridge revision filing skill WI-3257 deterministic services" --limit 8` returned relevant bridge-helper history including `DELIB-1795` and `DELIB-1565`.
- `python -m groundtruth_kb deliberations search "DELIB-S312 deterministic services bridge helper" --limit 8` returned related deterministic-service and bridge-helper context including `DELIB-1552`, `DELIB-1553`, `DELIB-1840`, `DELIB-1841`, and `DELIB-1795`.
- `python -m groundtruth_kb deliberations search "gtkb bridge revision skill bridge-propose helper" --limit 8` returned `DELIB-1239`, `DELIB-0734`, `DELIB-1897`, `DELIB-1813`, `DELIB-1814`, and `DELIB-1963`.
- `DELIB-1795` is especially relevant: it accepted deterministic bridge plumbing directionally but rejected designs that did not preserve bridge transition and atomicity controls.
- `DELIB-1239` and `DELIB-0734` are relevant predecessor records for governed bridge skill/helper behavior.
- `DELIB-1897` is relevant because this proposal modifies the canonical bridge skill surface and must preserve generated Codex adapter parity.

No reviewed deliberation authorizes filing incomplete bridge revisions or
bypassing pre-filing checks.

## Positive Evidence

- The proposal cites concrete governing specifications and rule surfaces in
  `Specification Links` (`bridge/gtkb-bridge-revision-skill-001-001.md:19`).
- The proposal includes substantive `Prior Deliberations` and
  `Owner Decisions / Input` sections (`bridge/gtkb-bridge-revision-skill-001-001.md:43`,
  `bridge/gtkb-bridge-revision-skill-001-001.md:59`).
- The proposal keeps the expected implementation paths inside `E:\GT-KB`
  (`bridge/gtkb-bridge-revision-skill-001-001.md:155`).
- The mechanical applicability and clause preflights both pass for the
  proposal packet, with no missing required specs and no blocking clause gaps.

## Findings

### F1 - P1 Blocking: write mode would file an incomplete REVISED skeleton as an actionable bridge entry

**Observation:** The proposal says the helper will "generate a
finding-by-finding REVISED skeleton, write the new bridge file ..., and insert
the REVISED line at the top of the same INDEX entry"
(`bridge/gtkb-bridge-revision-skill-001-001.md:17`). IP-1 repeats that the
helper must generate a skeleton and then insert
`REVISED: bridge/<slug>-<next>.md` into `bridge/INDEX.md`
(`bridge/gtkb-bridge-revision-skill-001-001.md:97`,
`bridge/gtkb-bridge-revision-skill-001-001.md:111`). IP-2 then says the skill
documentation must make clear the helper creates a skeleton, "not a final
substantive revision", and that the author must fill concrete fixes and run
required preflights "before filing for review"
(`bridge/gtkb-bridge-revision-skill-001-001.md:116`).

**Deficiency rationale:** Those requirements conflict. In the bridge protocol,
adding a `REVISED:` line to `bridge/INDEX.md` is filing for review and makes
the entry actionable for Loyal Opposition. A helper cannot both insert the live
`REVISED:` line and also leave the author to fill in the substantive revision
before filing. The mandatory pre-filing rule requires preflight after drafting
and before INDEX update or before re-saving the file
(`.claude/rules/file-bridge-protocol.md:37`). A skeleton-first live filing
would create dispatchable review work that is known not to contain the actual
finding responses yet.

**Impact:** If implemented as proposed, `/bridge revise <slug>` can produce
premature Loyal Opposition dispatches, noisy NO-GO cycles, and misleading audit
state. It also weakens the deterministic-services goal: the helper would
automate the mechanical ceremony but preserve the high-risk manual step of
remembering that a live `REVISED` bridge row still needs author completion.

**Required action:** Revise the design to choose one explicit lifecycle:

1. Scaffold mode: create a draft file outside live queue state, or create the
   next bridge file without inserting `REVISED:` until the author completes the
   content and preflights pass.
2. Filing mode: accept completed revision content or a completed patch-to-body
   input, run all required checks, reject placeholders/incomplete sections, and
   only then insert the `REVISED:` line into `bridge/INDEX.md`.

The proposed helper may still generate finding-by-finding shells, but the
INDEX mutation must be gated on the final revision being ready for review.

### F2 - P1 Blocking: the implementation scope omits the generated-revision preflight gate required by WI-3257 and bridge rules

**Observation:** The MemBase WI-3257 acceptance summary says the helper must
run pre-filing applicability and clause preflights against the new file
(`bridge/gtkb-bridge-revision-skill-001-001.md:69`,
`bridge/gtkb-bridge-revision-skill-001-001.md:73`). However IP-1 does not
require the helper to invoke either
`scripts/bridge_applicability_preflight.py` or
`scripts/adr_dcl_clause_preflight.py` before INDEX mutation
(`bridge/gtkb-bridge-revision-skill-001-001.md:90`). The regression test list
does not include a test proving generated revisions run and pass those
preflights before a `REVISED:` line is inserted
(`bridge/gtkb-bridge-revision-skill-001-001.md:122`). The verification plan
only runs preflights on this proposal's bridge id, not on a generated revision
artifact produced by the helper (`bridge/gtkb-bridge-revision-skill-001-001.md:135`).

**Deficiency rationale:** The proposal can pass every listed test while the new
helper never performs the pre-filing gate on the revision file it creates.
That misses both the explicit WI-3257 acceptance summary and the bridge rule
that any missing preflight findings must be resolved before INDEX update
(`.claude/rules/file-bridge-protocol.md:51`).

**Impact:** The deterministic helper would encode a known governance gap into
the repeatable workflow. Future revisions could be mechanically filed without
the exact checks this work item is supposed to make easier and harder to skip.

**Required action:** Add implementation requirements and tests that prove:

- generated revision content is checked by applicability preflight before
  live INDEX mutation;
- generated revision content is checked by clause preflight before live INDEX
  mutation;
- any non-empty missing required specs, blocking clause gaps, or placeholder
  section markers abort before file/INDEX mutation or before INDEX mutation
  when using a two-phase draft-then-file workflow;
- the implementation report includes observed results from those generated
  revision fixture tests, not only preflights against
  `gtkb-bridge-revision-skill-001`.

## Recommended Revision

Submit a revised proposal that:

1. Separates scaffold/draft creation from live bridge filing, or makes filing
   mode require final completed revision content.
2. States the exact order of operations for file write, preflight execution,
   credential scan, INDEX insertion, and conflict handling.
3. Adds regression tests for preflight-before-INDEX behavior on generated
   revision files.
4. Adds a test that an incomplete skeleton cannot become the live latest
   `REVISED` row.

## Applicability Preflight

- packet_hash: `sha256:07a94a68668f7dd393123e6d981b7264aac256c445595440ee57d8c041320005`
- bridge_document_name: `gtkb-bridge-revision-skill-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-revision-skill-001-001.md`
- operative_file: `bridge/gtkb-bridge-revision-skill-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-bridge-revision-skill-001`
- Operative file: `bridge\gtkb-bridge-revision-skill-001-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Decision Needed From Owner

None.

## Verdict

NO-GO until the proposal resolves the scaffold-versus-filing lifecycle
conflict and makes generated-revision preflight gates part of the helper's
implementation and regression test contract.

File bridge scan: 1 entry processed.
