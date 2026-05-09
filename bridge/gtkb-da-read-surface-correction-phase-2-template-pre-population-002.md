NO-GO

# Loyal Opposition Review - DA Read Surface Correction Phase 2 Template Pre-Population

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md`
Verdict: NO-GO

## Claim

Phase 2 is not ready for GO.

The mandatory bridge preflights pass and the direction is valid: moving prior
deliberation retrieval into the bridge-propose helper is the right placement
pattern. However, the proposal has two blocking gaps before it can authorize
implementation:

1. It omits required cross-harness skill-adapter and scaffold-template parity
   work from the implementation scope and tests.
2. Its S331 replay test assumes a plain DA search for `isolation` will surface
   all four lifecycle-independence anchor records, but the current
   `KnowledgeDB.search_deliberations()` behavior does not support that
   assertion without an additional mechanism.

## Prior Deliberations

- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - S331 owner-decision foundations for placement-over-coercion and bridge-template pre-population.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle-independence contract; one of the isolation anchor records.
- `DELIB-0877` - industry-alignment critique for GT-KB/application separation; one of the isolation anchor records.
- `DELIB-0879` - GTKB-ISOLATION-002 Phase 2 root and repository topology plan; one of the isolation anchor records.
- `DELIB-S321-PLATFORM-APP-NON-SPECIFIC` - S321 owner directive referenced by the Phase 1 isolation glossary entry.
- Phase 0 closure: `bridge/gtkb-da-read-surface-correction-phase-0-formalization-006.md`.
- Phase 1 closure: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-010.md`.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-2-template-pre-population
```

Observed:

- packet_hash: `sha256:30ebeeeb6479a505f40183e6f68f80cb972b92b445e4381ab1268d8ccf626d3f`
- bridge_document_name: `gtkb-da-read-surface-correction-phase-2-template-pre-population`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-2-template-pre-population
```

Observed:

- Bridge id: `gtkb-da-read-surface-correction-phase-2-template-pre-population`
- Operative file: `bridge\gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md`
- Clauses evaluated: `5`
- must_apply: `4`, may_apply: `1`, not_applicable: `0`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`
- Mode: mandatory default invocation; exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

### F1 - Missing skill-adapter and template parity scope

Priority: P1

Observation:

- The proposal updates the canonical Claude bridge-propose helper and SKILL file at
  `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md:82`
  through `:111`.
- The same proposal acknowledges that
  `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` must be
  updated if it exists at `:101`.
- That file does exist in the checkout.
- The `skill.bridge-propose` capability is registered as parity-required with a
  Codex generated adapter at `config/agent-control/harness-capability-registry.toml:60`
  through `:77`.
- The Codex adapter file exists at `.codex/skills/bridge-propose/SKILL.md` and is
  generated from `.claude/skills/bridge-propose/SKILL.md`.
- The implementation file list at
  `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md:183`
  through `:191` does not include:
  `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`,
  `groundtruth-kb/templates/skills/bridge-propose/SKILL.md`,
  `.codex/skills/bridge-propose/SKILL.md`, or
  `config/agent-control/harness-capability-registry.toml`.
- The proposal does not mention running
  `python scripts/generate_codex_skill_adapters.py --update-registry --check`
  or the non-check generation command after changing the canonical skill body.

Deficiency rationale:

The proposed change is explicitly a bridge-propose helper/skill behavior change.
Leaving the scaffold template and Codex adapter out of scope would make the live
Claude helper, scaffolded helper, and Codex skill instructions drift immediately.
That contradicts the proposal's own harness-agnostic claim and the required
skill-adapter parity registry.

Recommended action:

Revise the proposal to either:

1. Include the template/helper/adapter/registry files in implementation scope
   and add tests/checks for them, including `scripts/generate_codex_skill_adapters.py --update-registry --check`; or
2. Explicitly carve adopter-template propagation into a separate follow-on with
   an owner-visible rationale and remove the claim that the existing template is
   updated in this slice.

Given this helper is used to file bridge proposals, the safer revision is option
1: keep all bridge-propose surfaces in sync in the same slice.

### F2 - S331 replay test is not supported by the proposed retrieval mechanism

Priority: P1

Observation:

The test plan says the known-DA-match test invokes the helper with topic slug
`"isolation"` and verifies that the populated `Prior Deliberations` section
contains all four lifecycle-independence anchor records:
`DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, `DELIB-0879`, and
the S321 owner directive.

Direct checks against the current `KnowledgeDB.search_deliberations()` behavior
do not support that assertion:

```text
search_deliberations("isolation", limit=10)
DELIB-1438
DELIB-0877
DELIB-1327
DELIB-1424
DELIB-S310-ROLE-DEFINITION-ASSESSMENT
DELIB-1099
DELIB-0884
DELIB-1449
DELIB-1098
DELIB-1447
```

Only `DELIB-0877` appears in the top 10 for the plain `isolation` query. A
more specific query such as `platform app non specific isolation lifecycle
independence` surfaces `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` and
`DELIB-0877`, with `DELIB-0879` at rank 9. The proposal does not add a mechanism
to read the Phase 1 glossary source lines or otherwise expand the query with the
known anchor IDs.

Deficiency rationale:

The original S331 failure case is the reason this phase exists. A test that
asserts all four anchor records appear from a plain topic-slug DA query is not
currently grounded in the search API. Without a query-expansion mechanism, exact
ID extraction from the Phase 1 glossary entry, or an explicit curated seed path,
the proposed S331 replay test is likely to fail or become brittle.

Recommended action:

Revise the helper design to make the S331 replay deterministic. Acceptable
patterns include:

- When the topic slug matches a canonical glossary heading, read that heading's
  `Source:` block and seed exact `DELIB-*` IDs into the candidate set before
  semantic search.
- Add an explicit query-expansion step that incorporates canonical-term aliases
  and source IDs, then prove the resulting query returns all four anchors.
- Narrow the acceptance criterion to "at least one relevant DA record" only if
  the owner agrees that this no longer needs to close the original S331
  isolation failure. That would be a material requirement change.

## Decision

NO-GO. Revise Phase 2 to include the missing parity/template scope and to make
the S331 replay test mechanically achievable against the current DA retrieval
surface.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
