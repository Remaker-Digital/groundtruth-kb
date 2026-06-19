VERIFIED

# Loyal Opposition Verification - Ollama Harness UTF-8-Safe Output

bridge_kind: verification_verdict
Document: gtkb-ollama-harness-utf8-output
Version: 004
Responds-To: bridge/gtkb-ollama-harness-utf8-output-003.md
Verdict: VERIFIED
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-18 UTC

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: codex-lo-20260618-ollama-utf8-verification
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive LO verification

---

## Verdict

VERIFIED.

The implementation report's claimed UTF-8 output hardening for
`scripts/ollama_harness.py` is present in the live checkout and the focused
verification commands pass.

This canonical numbered verdict supersedes the noncanonical evidence file
`bridge/gtkb-ollama-harness-utf8-output-003.lo-verdict.md` for bridge workflow
purposes. The `.lo-verdict.md` file was useful as context only; it is not formal
bridge authority.

## Evidence Reviewed

- Implementation report:
  `bridge/gtkb-ollama-harness-utf8-output-003.md`
- Approved proposal:
  `bridge/gtkb-ollama-harness-utf8-output-001.md`
- Prior GO:
  `bridge/gtkb-ollama-harness-utf8-output-002.md`
- Noncanonical context artifact:
  `bridge/gtkb-ollama-harness-utf8-output-003.lo-verdict.md`
- Applicability preflight:
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-harness-utf8-output`
- Clause preflight:
  `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-harness-utf8-output`
- Source check:
  `rg -n "ensure_utf8_output_streams|reconfigure|backslashreplace|RIGHTWARDS|utf8_output" scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py`
- Diff check:
  `git diff -- scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py`

## Mandatory Gates

- Applicability preflight passed with `missing_required_specs: []`.
- ADR/DCL clause preflight passed with zero blocking gaps.
- The changed files match the approved target paths:
  `scripts/ollama_harness.py` and
  `platform_tests/scripts/test_ollama_harness.py`.
- `git diff -- scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py`
  returned no current uncommitted diff, so the verified implementation is
  already present in the live checkout state being reviewed.

## Reproduced Verification

```powershell
python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short
```

Observed: `33 passed in 4.38s`.

```powershell
python -m ruff check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
```

Observed: `All checks passed!`.

```powershell
python -m ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
```

Observed: `2 files already formatted`.

## Implementation Evidence

- `scripts/ollama_harness.py` defines `ensure_utf8_output_streams()` and calls
  it from `main()`.
- The helper uses stream `reconfigure(encoding="utf-8",
  errors="backslashreplace")` where supported.
- `platform_tests/scripts/test_ollama_harness.py` includes
  `test_utf8_output_stream_setup_allows_non_cp1252_final_text`, covering the
  right-arrow Unicode output path that originally crashed the Ollama worker.

## Spec-Derived Verification

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: the focused test proves a dispatch
  worker response containing non-cp1252 text no longer fails in the output
  transport layer.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`: the full Ollama harness test file
  passed, preserving existing prompt, routing, tool-loop, guard, and parser
  behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: no bridge file format, dispatcher state, or
  routing config code changed under this implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the verification commands
  were rerun by LO and mapped to the report's acceptance criteria.

## Residual Risk

This verifies the UTF-8 output-transport fix only. It does not by itself repair
the broader canonical `.lo-verdict.md` emission/liveness problem, which is now
GO under `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-004.md`.

## File Bridge Scan

File bridge scan: 1 entry processed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
