VERIFIED

bridge_kind: verification_verdict
Document: gtkb-sp1a-ollama-lo-prompt-restructure
Version: 006
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-08 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-sp1a-ollama-lo-prompt-restructure-005.md
Verdict: VERIFIED

# Loyal Opposition Verification - Ollama LO Prompt Restructure

## Verdict

VERIFIED.

The system prompt builder in `scripts/ollama_harness.py:build_system_prompt()` has been restructured from a preflight-blocking design to a verdict-first pattern. Preflight check failures are correctly treated as advisory notes to attach to the verdict body, and the claim command instruction has been correctly ordered at the top of the prompt. Spec-derived tests cleanly verify all behaviors and constraints.

## Verification Scope

- Read live `bridge/INDEX.md` and the full version chain for `gtkb-sp1a-ollama-lo-prompt-restructure`.
- Inspected the implementation in `scripts/ollama_harness.py`.
- Ran the new spec-derived tests in `platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py`.
- Ran the mechanical applicability preflight and clause-applicability preflight.

## Evidence

### E1 - Test Suite Execution
Command:
```bash
python -m pytest platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py -v
```
Observed outcome:
```text
platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py::test_build_system_prompt_uses_verdict_first_language PASSED
platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py::test_build_system_prompt_enforces_claim_first PASSED
platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py::test_build_system_prompt_retains_preflight_commands PASSED
3 passed in 0.18s
```

### E2 - Applicability Preflight
Command:
```bash
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sp1a-ollama-lo-prompt-restructure
```
Observed outcome:
```text
preflight_passed: true
missing_required_specs: []
```

### E3 - Clause Applicability Preflight
Command:
```bash
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-sp1a-ollama-lo-prompt-restructure
```
Observed outcome:
```text
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Spec-Derived Verification Mapping

- `GOV-FILE-BRIDGE-AUTHORITY-001`: verified by running applicability preflight and confirming the prompt retains the preflight commands.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: verified by ensuring the prompt instructs models to include preflight outputs as advisory evidence of spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: verified by creating and successfully running the targeted pytest suite.
- `.claude/rules/file-bridge-protocol.md`: verified that the claim command is prominently ordered at the top of the prompt.

## Owner Decisions / Input

No owner decisions are requested by this verdict.
