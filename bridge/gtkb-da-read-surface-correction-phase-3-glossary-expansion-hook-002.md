NO-GO

# Loyal Opposition Review - GTKB-DA-READ-SURFACE-CORRECTION Phase 3 Glossary-Expansion Hook

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md`
Verdict: NO-GO

## Claim

The proposal has the right general goal - making glossary and Deliberation Archive context available at prompt time - but it is not ready for implementation.

The mandatory applicability and clause preflights pass. The proposal cites the DA read-surface specs, includes a spec-derived test plan, and correctly treats the hook as non-mutating. However, the proposed hook is installed on every `UserPromptSubmit` path while its semantic-search fan-out is not mechanically bounded, and the proposal explicitly defers implementation-defining owner approvals until after GO. Those gaps can create prompt-time latency/context pollution and leave Prime Builder without an approved algorithm contract.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "DA read surface glossary expansion hook UserPromptSubmit concept on contact candidate glossary promotion" --limit 8`

Relevant records and thread evidence:

- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - establishes placement-over-coercion and the long-tail auto-injection concept.
- `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION` - startup context authority; per-prompt context expansion must not confuse placement surfaces.
- `DELIB-S324-OM-DELTA-0001-CHOICE` and `DELIB-S324-OM-DELTA-0003-CHOICE` - operating-model framing and Loyal Opposition authority to question cited requirements.
- `DELIB-0835` - strict artifact-approval discipline; relevant because this hook must remain read-only and must not create glossary/DA artifacts by implication.
- `INTAKE-c971df2d` / `SPEC-INTAKE-c9e997` - nearby spec-intake evidence surfaced by the DA search; reinforces that prompt-time detection surfaces need explicit confirmation paths.

## Applicability Preflight

- packet_hash: `sha256:eadc80167b41d81a32ba179ee44170525c8fbfdcbbb3ee1c21397d7a0aa1e925`
- bridge_document_name: `gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- Operative file: `bridge\gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - The proposal defers implementation-defining owner approvals until after GO

Observation:

- The `Owner Decisions / Input` section lists authorizing context, then says "Future owner approvals this proposal will surface" at `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md:71`.
- Those future approvals are not incidental. They include approval of "the hook's matching algorithm parameters (glossary-index build strategy; tokenization rules; semantic threshold; token-budget cap)" at line 73, approval of the candidate-promotion surfacing format at line 74, and confirmation of harness-parity scope at line 75.
- The implementation plan nevertheless specifies concrete behavior using those same unapproved parameters: tokenization at lines 83-88, semantic search at lines 89-92, output format at lines 93-98, and token budget at lines 96 and 110.

Deficiency rationale:

A GO verdict authorizes Prime Builder to implement the proposal as written. This proposal says the algorithm parameters and surfacing format still require future owner approval, but it also asks for GO on a concrete implementation. That leaves Prime Builder without a settled contract for the exact behavior to implement.

Impact:

Prime could implement values that later fail owner approval, or pause mid-implementation to collect decisions that should have been resolved before bridge authorization. Either outcome weakens the bridge as the pre-implementation review gate.

Recommended action:

Revise one of two ways:

- If the listed values are engineering choices, remove the "future owner approvals" claim and make the proposal's parameters authoritative within the bridge scope.
- If owner approval is required, collect and cite the decisions before resubmission, then update the `Owner Decisions / Input` section with the concrete approval evidence.

### F2 - P1 - Semantic-search fan-out is not bounded for a hook that runs on every UserPromptSubmit path

Observation:

- The proposal installs a `UserPromptSubmit` hook at `.claude/hooks/glossary-expansion.py` and registers it in `.claude/settings.json`: lines 13, 40-43, 81, and 165-173.
- The algorithm extracts 1- to 4-word candidate phrases at line 85, forwards concept-shaped non-matches to semantic search at line 88, and says "for each forwarded phrase, call `db.search_deliberations(phrase, limit=2)`" at line 91.
- No maximum number of forwarded phrases, no dedupe rule, no candidate priority order, and no total semantic-query budget is specified. The only explicit size bound is the output injection cap at lines 96 and 110, which does not bound query count or hook latency.
- The proposal treats the input as "the owner's prompt" at line 13, but current harness behavior routes automated bridge dispatch text through `UserPromptSubmit` as well. Evidence: `.codex/gtkb-hooks/last-wrapup-trigger-input.json` records the current "Bridge auto-dispatch notification (cross-harness trigger)" prompt with `"hook_event_name":"UserPromptSubmit"`.

Deficiency rationale:

The hook is on the prompt submission path, so latency and context pollution matter. A long prompt or automated bridge-dispatch payload can generate many concept-shaped non-matches and therefore many DA searches before any 2 KB output cap is applied. The proposal's stated failure modes are not actually bounded at the work-cost layer.

Impact:

Every prompt can pay unpredictable semantic-search cost. Automated bridge dispatches can also receive irrelevant glossary-expansion context, which increases the chance of review-context noise exactly where the bridge protocol requires tight scope.

Recommended action:

Revise the algorithm and tests to include:

- A deterministic candidate dedupe and priority strategy.
- A hard `MAX_SEMANTIC_CANDIDATES` / max-query cap with an override only if explicitly configured.
- A numeric similarity threshold and test coverage for accepting/rejecting semantic results.
- A skip rule for automated bridge-dispatch/session-lifecycle prompts, keyed to the dispatch marker or prompt prefix.
- Tests proving long prompts and bridge auto-dispatch prompts do not exceed the query cap and do not inject irrelevant context.

### F3 - P2 - The stdout contract is not tied to the existing UserPromptSubmit hook patterns

Observation:

- The proposal says the hook outputs JSON `{"continue": true, "additionalContext": "<injected text>"}` at `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md:97`.
- Existing local Claude `UserPromptSubmit` hooks use other patterns: `.claude/hooks/spec-classifier.py:14` and `.claude/hooks/scheduler.py:10` document `{"systemMessage": "..."}` output, and `.claude/hooks/owner-decision-tracker.py:46` documents raw markdown text for UserPromptSubmit nudges.
- The proposed test plan checks "empty `additionalContext`" and settings registration, but it does not require a harness-compatible output envelope by executing the hook through the local parser or by matching the established `systemMessage`/raw-text convention.

Deficiency rationale:

This may be a valid external hook shape, but the proposal does not cite local evidence or tests proving the current harness will inject it. A prompt-time context hook that silently emits an ignored payload would appear implemented while providing no DA read surface.

Impact:

The implementation could pass unit tests around formatting but fail at the harness integration boundary.

Recommended action:

Revise the proposal to select and test one local output contract:

- Use the same `systemMessage` JSON shape as the current Claude `UserPromptSubmit` hooks; or
- Emit raw markdown text like `owner-decision-tracker.py`; or
- Cite a verified local parser/contract for `additionalContext` on UserPromptSubmit and add an integration test that proves the hook output is injected.

## Positive Confirmations

- The non-mutating hook posture is correct.
- The proposed audit log avoids storing raw full prompts by using a prompt hash.
- The phase separation is directionally right: Stage A owner-prompt detection can precede Phase 6 bridge/rule-file enforcement if its output remains advisory.
- The test plan covers useful local behavior: glossary match, no-match, DA failure, parse failure, audit schema, and Codex parity registration.

## Decision

NO-GO. Revise Phase 3 to settle the owner-approval contract, bound semantic-search work on the prompt path, skip automated dispatch prompts, and prove the UserPromptSubmit output shape is harness-compatible.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "DA read surface glossary expansion hook UserPromptSubmit concept on contact candidate glossary promotion" --limit 8`
- `rg` and targeted file reads over hook contracts, current UserPromptSubmit registrations, and the proposal.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
