GO

# Loyal Opposition Review - DA Read Surface Correction Phase 2 Template Pre-Population REVISED

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md`
Verdict: GO

## Claim

The revised Phase 2 proposal is ready for implementation.

The `-003` revision closes both blockers from `-002`:

1. F1 is addressed by adding explicit parity-required surfaces, Codex adapter
   regeneration, harness-capability-registry hash verification, and
   template-parity tests.
2. F2 is addressed by replacing the brittle plain semantic-search S331 replay
   with deterministic glossary-source seeding from
   `.claude/rules/canonical-terminology.md`, followed by semantic search for
   broader candidates.

The mandatory applicability preflight and ADR/DCL clause preflight both pass
against the live operative `REVISED` file.

## Prior Deliberations

Deliberation search was run for bridge-template pre-population, DA read-surface
correction, and isolation/lifecycle-independence context. Relevant records and
thread evidence:

- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - S331 owner-decision foundations for placement-over-coercion and bridge-template pre-population.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle-independence contract; one of the isolation anchor records.
- `DELIB-0877` - industry-alignment critique for GT-KB/application separation; one of the isolation anchor records.
- `DELIB-0879` - GTKB-ISOLATION-002 Phase 2 root and repository topology plan; one of the isolation anchor records.
- `DELIB-S321-PLATFORM-APP-NON-SPECIFIC` - S321 owner directive referenced by the Phase 1 isolation glossary entry.
- `DELIB-0136` - Bridge Optimization Follow-Up; surfaced in DA searches for bridge template pre-population.
- Phase 0 closure: `bridge/gtkb-da-read-surface-correction-phase-0-formalization-006.md`.
- Phase 1 closure: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-010.md`.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-2-template-pre-population
```

Observed:

- packet_hash: `sha256:90d0a3e4ef5e9ffbf9244e8f71a716b534f49e99e3edeb3eabcca8b2b4effe2a`
- bridge_document_name: `gtkb-da-read-surface-correction-phase-2-template-pre-population`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md`
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
- Operative file: `bridge\gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md`
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

## Review Evidence

### F1 Closure - Parity/template scope is now explicit

Evidence:

- `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md:124`
  through `:131` adds Change 2a for parity-required surfaces.
- The implementation pattern at `:145` through `:149` requires updates to the
  bridge-propose scaffold templates, regeneration of the Codex skill adapter,
  and post-regeneration `--check`.
- The file list at `:216` through `:220` includes
  `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`,
  `groundtruth-kb/templates/skills/bridge-propose/SKILL.md`,
  `.codex/skills/bridge-propose/SKILL.md`, and
  `config/agent-control/harness-capability-registry.toml`.
- The test plan at `:184` through `:185` adds explicit adapter and template
  parity checks.
- Current checkout sanity check: the template helper, template SKILL, and Codex
  adapter files exist; `python scripts\generate_codex_skill_adapters.py --update-registry --check`
  currently reports `PASS`.

Deficiency rationale:

No remaining deficiency. The revised scope now prevents the canonical Claude
skill, Codex adapter, and scaffold templates from drifting as a result of this
helper behavior change.

### F2 Closure - S331 replay is grounded in glossary-source seeding

Evidence:

- The revised design at `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md:92`
  through `:111` adds deterministic glossary-source seeding before semantic
  search.
- The revised tests at `:178` through `:182` assert seed-set membership rather
  than semantic-search ranking.
- Direct check of the current `### isolation` glossary block shows the proposed
  regex can extract the expected ID-shaped anchors:

```text
ids [
  'DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT',
  'DELIB-0877',
  'DELIB-0879',
  'DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS',
  'ADR-ISOLATION-APPLICATION-PLACEMENT-001'
]
missing []
```

Deficiency rationale:

No remaining deficiency. The S331 anti-regression test no longer depends on the
current ranking behavior of `KnowledgeDB.search_deliberations("isolation")`.
The canonical glossary entry provides a deterministic source path for the
load-bearing IDs, and semantic search remains useful as broader context.

## Non-Blocking Notes

- The proposal text at `-003:111` says the helper "extracts all five" from the
  `isolation` source block, while the test plan later correctly treats the S321
  owner directive as a by-title source that may be returned as-is or filtered to
  ID-shaped tokens. During implementation, keep that distinction explicit:
  do not make the test depend on a nonexistent S321 `DELIB-*` token unless the
  helper deliberately resolves by-title DA sources to IDs.
- The implementation report should include the exact owner approval evidence for
  the protected `.claude/rules/codex-review-gate.md` edit, including preview
  path, preview hash, packet path, packet `full_content_sha256`, and
  `scripts/check_narrative_artifact_evidence.py --paths .claude/rules/codex-review-gate.md`.

## GO Conditions For Later Verification

- Implementation must update all canonical, template, Codex-adapter, and
  registry surfaces listed in the revised file list.
- Implementation must prove glossary-source seeding extracts the current
  `isolation` anchor IDs from `.claude/rules/canonical-terminology.md`.
- Implementation must run the helper tests, adapter-generation check, template
  parity checks, narrative-artifact evidence check, and any existing helper
  regression tests affected by the new default `propose_bridge()` behavior.
- Implementation report must carry forward the linked specifications and include
  executed spec-to-test mapping for every linked specification.

## Decision

GO. Prime Builder may implement Phase 2 within the revised scope in
`bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md`.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
