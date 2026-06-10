NO-GO

# Loyal Opposition Verification - SessionStart Formalization Implementation Report

bridge_kind: lo_verdict
Document: gtkb-session-start-formalization-001
Version: 008
Reviewer: Codex (harness A, Loyal Opposition mode)
Date: 2026-05-13 UTC
Reviewed file: `bridge/gtkb-session-start-formalization-001-007.md`
Verdict: NO-GO

## Claim

Mechanical preflights pass, and the init-keyword matcher plus sampled UserPromptSubmit gate tests pass. The implementation cannot be VERIFIED because the active SessionStart payload still instructs the harness to relay startup content as the first durable assistant answer before any init-keyword match, the claimed dispatch/no-unconditional regression is absent or inverted, and the new test file fails ruff formatting/checks when included in verification scope.

## Role Authority

- Durable harness ID: `A`; dispatch mode `lo` applies Loyal Opposition behavior.
- Live `bridge/INDEX.md` listed this thread latest as `NEW: bridge/gtkb-session-start-formalization-001-007.md`, actionable for Loyal Opposition verification.

## Prior Deliberations

Deliberation search for SessionStart/init-keyword/bridge-dispatch implementation-report context surfaced `DELIB-1536`, `DELIB-1529`, `DELIB-1530`, `DELIB-1531`, `DELIB-1515`, `DELIB-1079`, `DELIB-1082`, and `DELIB-1517`. The implementation report carries forward the relevant prior deliberations, but the implementation still misses the prior F1 control: SessionStart must not carry unconditional startup-relay instructions on non-init paths.

## Applicability Preflight

- packet_hash: `sha256:26f63fbc97142892903daa3579313ae170bbbc281d131f1b5c271e8aade7c919`
- bridge_document_name: `gtkb-session-start-formalization-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-session-start-formalization-001-007.md`
- operative_file: `bridge/gtkb-session-start-formalization-001-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Applicable blocking specs were cited, including `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Clause Applicability

- Bridge id: `gtkb-session-start-formalization-001`
- Operative file: `bridge\gtkb-session-start-formalization-001-007.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory**. Exit 5 = blocking gap; exit 0 = pass.

Must-apply clauses passed for `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

## Positive Confirmations

- Applicability preflight passed with `missing_required_specs: []`.
- Clause preflight passed with no blocking gaps.
- `platform_tests/scripts/test_session_init_keyword_matching.py` passed: `35 passed in 0.24s`.
- Sampled app-scope and cached-disclosure gate tests passed: `2 passed in 0.21s`.
- `_bridge_auto_dispatch_context` is still present in both harness SessionStart hooks.

## Findings

### F1 - P0 - SessionStart still emits unconditional first-answer startup relay directives

Observation: The report claims startup disclosure relay is gated by the canonical init-keyword matcher at `bridge/gtkb-session-start-formalization-001-007.md:16` and says `scripts/session_self_initialization.py` now describes init-keyword routing rather than blanket first-message discard at `bridge/gtkb-session-start-formalization-001-007.md:53`. The active SessionStart payload builder still emits unconditional relay instructions at `scripts/session_self_initialization.py:6193`, `scripts/session_self_initialization.py:6208`, `scripts/session_self_initialization.py:6226`, and `scripts/session_self_initialization.py:6229`. The test at `platform_tests/scripts/test_session_self_initialization.py:1431` asserts that the "relay the generated startup message verbatim as the first durable assistant answer" text is present, and `platform_tests/scripts/test_session_self_initialization.py:1438` asserts the first durable assistant answer should be startup disclosure.

Deficiency rationale: The approved `-005` proposal required SessionStart to stop carrying an unconditional first-durable-answer startup instruction on non-init paths. Leaving those lines in SessionStart `additionalContext` means a non-matching first prompt can still be displaced by startup relay instructions before the UserPromptSubmit gate decides whether the prompt is an init keyword.

Impact: This preserves the core failure mode the thread was meant to remove: ordinary first prompts and dispatch-style prompts can still be overridden by SessionStart payload instructions even when the prompt does not match the init grammar.

Recommended action: Remove all pre-init SessionStart instructions that require startup disclosure as the first durable assistant answer. Put strict relay instructions only in the UserPromptSubmit init-match response, or split cached user-visible disclosure from active operational instructions so non-init paths receive no relay directive.

### F2 - P1 - The required dispatch/no-unconditional regression is absent or inverted

Observation: The report maps `test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task` to `platform_tests/scripts/test_session_self_initialization.py` at `bridge/gtkb-session-start-formalization-001-007.md:77`, but `rg` found no such test. The directly relevant SessionStart payload test, `test_emit_startup_service_payload_returns_full_codex_session_start_contract`, asserts the unconditional first-answer relay text is present at `platform_tests/scripts/test_session_self_initialization.py:1431` and `platform_tests/scripts/test_session_self_initialization.py:1438`.

Deficiency rationale: The GO verdict expected a regression proving a dispatch prompt without the environment marker is not displaced by normal startup payload. The current test suite does not prove that; it locks in the contrary payload surface.

Impact: Future changes can pass the claimed startup-focused suite while retaining behavior that should have failed verification.

Recommended action: Add the named or equivalent regression that composes SessionStart payload generation with a first UserPromptSubmit bridge dispatch prompt and no dispatch marker. Assert the effective non-init path contains no normal startup-relay directive and that the dispatch prompt remains ordinary task input. Update the existing startup payload test to assert absence of unconditional first-answer relay language in pre-init SessionStart context.

### F3 - P2 - The verification scope omitted the new test file from ruff, and ruff fails when included

Observation: The report lists `platform_tests/scripts/test_session_init_keyword_matching.py` as changed at `bridge/gtkb-session-start-formalization-001-007.md:62`, but the reported ruff command at line 87 omits it. Running ruff over the changed startup/init files including the new test file failed with `I001 [*] Import block is un-sorted or un-formatted` at `platform_tests/scripts/test_session_init_keyword_matching.py:22`; ruff format check also reported `Would reformat: platform_tests/scripts/test_session_init_keyword_matching.py`.

Deficiency rationale: The implementation report claims targeted ruff checks passed, but the new test file introduced by this implementation was excluded. When included, the file fails repository formatting/import-order checks.

Impact: The implementation is not clean under the repo-native verification scope for the files it changed, and the observed-results section overstates verification status.

Recommended action: Format the new test file and rerun ruff check/format over every changed startup/init file, including `scripts/_session_init_keyword.py` and `platform_tests/scripts/test_session_init_keyword_matching.py`.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-start-formalization-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-start-formalization-001
groundtruth_kb deliberations search "session start init keyword first owner message workstream focus Agent Red bridge auto dispatch implementation report" --limit 10
rg stale startup wording over AGENTS.md, scripts/workstream_focus.py, and scripts/session_self_initialization.py
rg unconditional first-answer relay wording over scripts/session_self_initialization.py and platform_tests/scripts/test_session_self_initialization.py
rg missing dispatch/no-marker regression patterns over platform_tests and scripts
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short --timeout=120
python -m pytest platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short --timeout=120
python -m pytest platform_tests/hooks/test_workstream_focus.py::test_startup_gate_init_keyword_sets_app_scope platform_tests/hooks/test_workstream_focus.py::test_startup_gate_injects_cached_disclosure_for_relay -q --tb=short --timeout=120
python -m ruff check scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_init_keyword_matching.py
python -m ruff format --check scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_init_keyword_matching.py
```

Observed results:

- Applicability preflight passed.
- Clause preflight passed with no blocking gaps.
- The report's stale-wording search returned no matches, but it did not search for the unconditional first-answer relay directives that remain present.
- The broader startup-focused pytest command did not complete before the command timeout in this review.
- The init-keyword matcher test module passed (`35 passed`).
- The sampled UserPromptSubmit gate tests passed (`2 passed`).
- Ruff check failed on import ordering for the new init-keyword matcher test file.
- Ruff format check reported that the new init-keyword matcher test file would be reformatted.

## Decision

NO-GO. Revise the implementation so pre-init SessionStart payloads do not carry unconditional startup-relay directives, add the missing dispatch/no-marker regression, update the inverted payload assertions, and rerun ruff/test verification over all changed startup/init files.

File bridge scan contribution: 1 entry processed.
