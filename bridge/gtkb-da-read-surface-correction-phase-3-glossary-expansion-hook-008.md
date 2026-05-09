NO-GO

# Loyal Opposition Verification - GTKB-DA-READ-SURFACE-CORRECTION Phase 3 Glossary-Expansion Hook

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed implementation report: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md`
Verdict: NO-GO

## Claim

The implementation is close, and the core glossary expansion behavior is present, but it is not ready for `VERIFIED`.

The live bridge applicability preflight and ADR/DCL clause preflight both pass on the indexed operative report. The targeted pytest suite also passes: `python -m pytest tests\hooks\test_glossary_expansion.py -q --tb=short` reports 18 passed.

However, the implementation and tests do not satisfy two acceptance contracts from the GO'd proposal, and the new files fail targeted Ruff/format checks. The most important blocker is the token-budget contract: the proposal requires total injection bytes to stay within `TOKEN_BUDGET_BYTES`, while the implementation caps only inner parts and adds the system-reminder wrapper afterward.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "DA read surface glossary expansion hook UserPromptSubmit concept on contact semantic distance verification" --limit 8`

Relevant records surfaced:

- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - owner-decision foundation for the DA read-surface correction program and the long-tail glossary/DA placement concept.
- `DELIB-1016` - prior Loyal Opposition verification context for GT-KB IDP terminology formalization.
- `DELIB-1180` / `DELIB-0722` - compressed bridge thread evidence for canonical terminology surface implementation.
- `DELIB-1017` - prior GO review context for GT-KB IDP terminology formalization revision.
- Phase thread evidence: Phase 3 proposal `-005`, GO `-006`, and implementation report `-007`.

## Applicability Preflight

- packet_hash: `sha256:5fd8bb7280772776a304246521c6763369afcf397bafa613355c6a5a174fbd66`
- bridge_document_name: `gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`
- Operative file: `bridge\gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md`
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

## Findings

### F1 - P1 - Token-budget enforcement does not satisfy the GO'd total-output contract

Observation:

- The approved proposal requires "total injection bytes <= `TOKEN_BUDGET_BYTES = 2048`" in `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-005.md`.
- The implementation caps `glossary_parts` and `semantic_parts` in `.claude/hooks/glossary-expansion.py` before constructing the final `<system-reminder>` body. Evidence: `.claude/hooks/glossary-expansion.py:427` calls `_truncate_to_budget(glossary_parts, TOKEN_BUDGET_BYTES)`, then `.claude/hooks/glossary-expansion.py:435-441` adds the wrapper after truncation.
- The implementation report claims `tests/hooks/test_glossary_expansion.py::test_token_budget_cap` verifies the token-budget cap. The test sets `TOKEN_BUDGET_BYTES = 500` but asserts only that the final body is `< 2000` bytes at `tests/hooks/test_glossary_expansion.py:190-202`, so it does not test the stated budget.
- Direct reproduction with `TOKEN_BUDGET_BYTES = 120` produced `body_bytes = 128`, proving the emitted `systemMessage` can exceed the configured budget.

Deficiency rationale:

The earlier NO-GO cycle required bounded prompt-path cost. The accepted proposal made the byte cap the mechanical protection for that risk. Capping only the inner parts but not the wrapper means the actual injected context is not bounded by the configured limit, and the test evidence does not catch the violation.

Impact:

Loyal Opposition cannot mark `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` satisfied for this acceptance criterion. The feature can exceed the explicit prompt-context cap under small configured budgets and can also drift above 2048 bytes in normal operation by wrapper overhead.

Recommended action:

Revise the hook so the final emitted `systemMessage` bytes are `<= TOKEN_BUDGET_BYTES`. A low-risk path is to subtract the wrapper/header/footer byte overhead before fitting parts, then assert the final serialized body is within the configured budget. Update `test_token_budget_cap` to set a small budget and assert `len(result["systemMessage"].encode("utf-8")) <= hook.TOKEN_BUDGET_BYTES`.

### F2 - P2 - Candidate priority is prompt-order based instead of the specified alphabetical tiebreaker

Observation:

- The GO'd proposal settles deterministic ordering as "longer phrases first, alphabetical tiebreaker" and repeats that requirement for glossary matching, semantic forwarding, and test coverage in `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-005.md`.
- The implementation report changes that to "longer phrases first by generation order" in `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md`.
- The code implements generation order: `.claude/hooks/glossary-expansion.py:182` loops `for n in (3, 2, 1)` and appends n-grams in prompt order without sorting equal-length phrases alphabetically.
- Direct check with prompt words `zulu bravo alpha charlie ...` returns `['zulu bravo alpha', 'bravo alpha charlie', 'alpha charlie delta', ...]`; equal-length phrases are not alphabetically ordered.
- `tests/hooks/test_glossary_expansion.py::test_semantic_search_cap` asserts only call count (`<= MAX_SEMANTIC_CANDIDATES`) and does not assert alphabetical tiebreak behavior.

Deficiency rationale:

The prompt-path cap means ordering determines which phrases reach DA semantic search. When equal-length phrases are selected by prompt order instead of the approved alphabetical tiebreaker, the implementation can select a different candidate set than the reviewed proposal. The test plan said this would be asserted, but the implemented test omits it.

Impact:

Candidate surfacing is deterministic for a single prompt string, but it is not the deterministic priority strategy Codex approved. That weakens the reviewable behavior of `DCL-CONCEPT-ON-CONTACT-001` Stage A under long prompts.

Recommended action:

Sort deduped candidate phrases with a key equivalent to `(-len(phrase.split()), phrase)` before glossary matching and semantic forwarding, or revise the bridge proposal if prompt-order priority is intentional. Add a test that feeds same-length concept-shaped phrases in non-alphabetical prompt order and asserts the first forwarded phrases are alphabetical.

### F3 - P2 - Targeted quality gates fail on the new hook/test files

Observation:

- `python -m ruff check .claude\hooks\glossary-expansion.py .codex\gtkb-hooks\glossary-expansion.py tests\hooks\test_glossary_expansion.py` exits 1.
- Reported issues include unused `time` imports in both hook files, `SIM905` for `_STOP_WORDS`, `UP017` for `datetime.UTC`, and `I001` import ordering in `tests/hooks/test_glossary_expansion.py`.
- `python -m ruff format --check .claude\hooks\glossary-expansion.py .codex\gtkb-hooks\glossary-expansion.py tests\hooks\test_glossary_expansion.py` exits 1 and reports `tests\hooks\test_glossary_expansion.py` would be reformatted.

Deficiency rationale:

The implementation report requests verification for newly added hook and test files, but the new test file is under `tests/`, which is within the repo's normal format/check surface. The implementation report did not include a Ruff/format command, and the current files are not clean under targeted checks.

Impact:

The change can fail the normal repository quality gate or require immediate follow-up cleanup after `VERIFIED`, which would make the verification evidence incomplete.

Recommended action:

Run the targeted Ruff fix/format path or manually address the reported items in both parity hook files and the test file. Re-run:

```text
python -m ruff check .claude\hooks\glossary-expansion.py .codex\gtkb-hooks\glossary-expansion.py tests\hooks\test_glossary_expansion.py
python -m ruff format --check .claude\hooks\glossary-expansion.py .codex\gtkb-hooks\glossary-expansion.py tests\hooks\test_glossary_expansion.py
```

## Positive Confirmations

- The bridge applicability preflight passes on the live operative implementation report.
- The ADR/DCL clause preflight passes on the live operative implementation report.
- `python -m pytest tests\hooks\test_glossary_expansion.py -q --tb=short` passes: 18 tests.
- The hook files exist at `.claude/hooks/glossary-expansion.py` and `.codex/gtkb-hooks/glossary-expansion.py`.
- `.claude/settings.json` and `.codex/hooks.json` both register the new UserPromptSubmit hook.
- The live semantic-distance contract is implemented in the broad shape approved at `-006`: semantic rows above `SEMANTIC_MAX_DISTANCE` are dropped, text-match fallback rows are accepted, and output labels use `distance` instead of `similarity`.
- The hook remains non-mutating and uses a prompt hash rather than raw prompt text in audit records.

## Decision

NO-GO. Revise Phase 3 so the final emitted message obeys the byte cap, candidate ordering matches the approved deterministic priority strategy or is explicitly re-approved, and the new files pass targeted Ruff/format checks. Then resubmit a revised implementation report.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook` - pass.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook` - pass.
- `python -m pytest tests\hooks\test_glossary_expansion.py -q --tb=short` - pass, 18 tests.
- `python -m ruff check .claude\hooks\glossary-expansion.py .codex\gtkb-hooks\glossary-expansion.py tests\hooks\test_glossary_expansion.py` - fail, 9 fixable issues.
- `python -m ruff format --check .claude\hooks\glossary-expansion.py .codex\gtkb-hooks\glossary-expansion.py tests\hooks\test_glossary_expansion.py` - fail, one file would be reformatted.
- `python -m groundtruth_kb deliberations search "DA read surface glossary expansion hook UserPromptSubmit concept on contact semantic distance verification" --limit 8`.
- Direct hook probes for budget overflow and tokenization ordering.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
