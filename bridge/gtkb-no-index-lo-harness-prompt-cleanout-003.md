NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc9e-ca08-7b40-8eb2-23994cc2029d
author_model: gpt-5-codex
author_model_configuration: Codex desktop

# Prime Builder Implementation Report - No-Index LO Harness Prompt Cleanout

bridge_kind: implementation_report
Document: gtkb-no-index-lo-harness-prompt-cleanout
Version: 003
Implemented GO: bridge/gtkb-no-index-lo-harness-prompt-cleanout-002.md
Date: 2026-06-16 America/Los_Angeles

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`

## Implementation Summary

Updated the Ollama and OpenRouter Loyal Opposition bridge-review system prompts
so they no longer instruct reviewers to read, update, or expect
`bridge/INDEX.md`.

The prompts now instruct LO harnesses to:

- read the full versioned bridge-file chain for the target document;
- use `gt bridge dispatch config`, `gt bridge dispatch status`, and
  `gt bridge dispatch health` for dispatcher topology and readiness;
- write the next numbered bridge verdict through guarded bridge-writer paths;
- treat helpers that require the retired bridge index as defective.

The Bash tool descriptions were also changed to describe denied bridge artifact
and retired-index mutations without naming the retired index as an active file.

Focused tests now assert that both Ollama and OpenRouter bridge-review prompts
exclude `bridge/INDEX.md` and include the versioned bridge-file and dispatch CLI
instructions.

## Specification-Derived Verification

| Requirement / Spec | Verification | Result |
|---|---|---|
| Owner no-index directive / `GOV-FILE-BRIDGE-AUTHORITY-001` | `Test-Path bridge\INDEX.md` | PASS: `False` |
| Prompt cleanup scope | `rg -n -F "bridge/INDEX.md" scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py` | PASS: remaining hits are negative prompt assertions or explicit denied/historical test commands only |
| LO harness prompt behavior | `python -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py -q --tb=short` | PASS: `37 passed` |
| Code quality | `python -m ruff check scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py` | PASS |
| Formatting | `python -m ruff format --check scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py` | PASS: `7 files already formatted` |

## Commands Run

```powershell
Test-Path bridge\INDEX.md
rg -n -F "bridge/INDEX.md" scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py
python -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py -q --tb=short
python -m ruff check scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py
python -m ruff format --check scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py
```

## Files Changed

- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py`
- `platform_tests/scripts/test_openrouter_harness.py`

## Residual Risk

This slice removes retired-index instructions from Ollama and OpenRouter prompt
surfaces. It does not resolve the separate hook-registration failures currently
blocking several broader dispatch verification reports; those are scoped in
`bridge/gtkb-dispatch-orthogonality-config-status-cli-008.md`.
