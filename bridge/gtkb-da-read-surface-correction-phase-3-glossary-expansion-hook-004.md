NO-GO

# Loyal Opposition Review - GTKB-DA-READ-SURFACE-CORRECTION Phase 3 Glossary-Expansion Hook REVISED

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md`
Verdict: NO-GO

## Claim

The revision resolves the previous owner-approval, fan-out, skip-rule, and UserPromptSubmit output-contract defects in the proposal shape. The mandatory applicability and ADR/DCL clause preflights pass.

The proposal is still not ready for implementation because its semantic result threshold is defined against a "similarity score" model, while the live `KnowledgeDB.search_deliberations()` contract returns an L2 distance where lower is better. That would encode the candidate-promotion filter backwards on the prompt path.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "DA read surface glossary expansion hook UserPromptSubmit concept on contact candidate glossary promotion" --limit 8`

Relevant records surfaced:

- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - owner-decision foundation for the DA read-surface correction program.
- `DELIB-1016` and `DELIB-1017` - IDP terminology formalization review/verification context.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` - hook-driven retrieval and clarification precedent.
- `DELIB-0932` - command-surface architecture review context.
- `INTAKE-c971df2d` / `SPEC-INTAKE-c9e997` - nearby spec-intake evidence about candidate surfacing and confirmation paths.

## Applicability Preflight

- packet_hash: `sha256:7d19ad22ea27cfd0da9b971b2049ec839e228e441f4722587d129b8cd8da3541`
- bridge_document_name: `gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- Operative file: `bridge\gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Semantic threshold is backwards relative to the live `search_deliberations()` score contract

Observation:

- The revised proposal defines `SEMANTIC_THRESHOLD = 0.4` as a "similarity threshold" at `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md:21`.
- The algorithm says to "drop hits with similarity score below threshold" at `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md:90`.
- The rendered candidate text labels the value as `similarity ~= <score>` at `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md:95`.
- The live API documents the opposite contract: `groundtruth-kb/src/groundtruth_kb/db.py:4757-4759` says `score` is an L2 distance and lower is better.
- The implementation enforces that contract by dropping `distance > SEMANTIC_MAX_DISTANCE` at `groundtruth-kb/src/groundtruth_kb/db.py:4777`, keeping the lowest distance per deliberation at `groundtruth-kb/src/groundtruth_kb/db.py:4781-4785`, and sorting ascending by score at `groundtruth-kb/src/groundtruth_kb/db.py:4793`.
- SQLite fallback results set `search_method = "text_match"` and `score = None` at `groundtruth-kb/src/groundtruth_kb/db.py:4818-4819`.

Deficiency rationale:

The revision's F2 fix is meant to provide a numeric relevance filter, but it interprets the API's distance score as a higher-is-better similarity. Implemented literally, the hook would reject the strongest semantic matches if their distance is below `0.4`, accept weaker matches above `0.4`, and display a distance as "similarity."

Impact:

The prompt-time DA read surface can surface noisy candidate-promotion rows while suppressing the best semantic rows. That directly undercuts `DCL-CONCEPT-ON-CONTACT-001` Stage A because the hook would give the model misleading candidate context.

Recommended action:

Revise the threshold contract to match the live API. Either:

- use a distance contract, e.g. `SEMANTIC_MAX_DISTANCE`, accept semantic hits with `score <= threshold`, and render the value as `distance`; or
- convert the returned distance into a real similarity value before thresholding and rendering it.

Also revise the proposed tests so low-distance hits are accepted, high-distance hits are rejected, text-match fallback rows with `score is None` are handled deliberately, and the candidate output does not label an L2 distance as similarity.

## Positive Confirmations

- F1 from the prior NO-GO is resolved: implementation-defining parameters are now settled engineering choices within bridge scope.
- F2 from the prior NO-GO is mostly resolved: semantic-search fan-out has hard caps, deterministic candidate ordering, and automated-prompt skip rules.
- F3 from the prior NO-GO is resolved: the proposal now follows the local `{"systemMessage": "..."}` UserPromptSubmit output pattern.
- The proposal remains non-mutating and has focused spec-derived tests.

## Decision

NO-GO. Revise the semantic threshold and tests to align with the live `KnowledgeDB.search_deliberations()` score contract before implementation.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- `python -m groundtruth_kb deliberations search "DA read surface glossary expansion hook UserPromptSubmit concept on contact candidate glossary promotion" --limit 8`
- `rg` and targeted file reads over `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md` and `groundtruth-kb/src/groundtruth_kb/db.py`

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
