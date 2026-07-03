NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5.5
author_model_version: Codex Desktop 2026-07-03
author_model_configuration: Codex Desktop interactive; owner init ::init gtkb pb; reasoning effort Extra High; governed WI-5001 implementation

# WI-5001 Ollama UTF-8 Subprocess Decode Repair - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5001-ollama-utf8-subprocess-decode
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-002.md
Approved proposal: bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-001.md
Recommended commit type: feat:

## Implementation Claim

Implementation complete for the scoped GO in `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-002.md`.

I updated both Ollama harness subprocess capture paths to force UTF-8 text decoding with tolerant replacement:

- `scripts/ollama_harness.py` `_default_guard_runner(...)`
- `scripts/ollama_harness.py` `_default_command_runner(...)`

Both `subprocess.run(...)` calls now pass:

- `encoding="utf-8"`
- `errors="replace"`

This prevents Windows from falling back to cp1252 when child stdout/stderr is captured with `text=True`, which was the source of the live `UnicodeDecodeError` reader-thread traces.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision was required. This implementation is covered by:

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5001-OLLAMA-UTF8-DECODE`

## Prior Deliberations

- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5001-OLLAMA-UTF8-DECODE` - bounded implementation authorization for this defect.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Ollama headless subprocess output decoding is deterministic across Windows locale settings; focused test file passes and covers default runner behavior. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Repair is inside the Ollama harness shim, preserving centralized dispatcher routing and avoiding direct harness-to-harness launch. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work proceeded only after GO, work-intent claim, and implementation authorization begin. Claim row `29745`; implementation packet `sha256:e09104a859d0fecc67dc70220aecb07247178c76f3489c08ebfad6edeb74e810`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Mutations are limited to the PAUTH target path globs: `scripts/ollama_harness.py` and `platform_tests/scripts/test_verify_ollama_dispatch.py`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests assert both the subprocess-runner configuration contract and cp1252-invalid UTF-8 output behavior. |

## Tests Added

- `test_default_subprocess_runners_pin_utf8_decode_options`
  - Verifies both default subprocess runners pass `text=True`, `encoding="utf-8"`, and `errors="replace"` into `subprocess.run(...)`.
- `test_default_guard_runner_captures_utf8_bytes_invalid_under_cp1252`
  - Runs a real Python child process that emits UTF-8 bytes containing `0x81`, which is invalid under cp1252, and verifies stdout/stderr are captured safely.

## Commands Run

```powershell
python -m pytest platform_tests\scripts\test_verify_ollama_dispatch.py -q --tb=short
python -m ruff check scripts\ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py
python -m ruff format --check scripts\ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py
```

## Observed Results

- `22 passed, 1 skipped in 0.46s`
- `All checks passed!`
- `2 files already formatted`

## Files Changed

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

## Acceptance Criteria Status

- [x] Add explicit UTF-8 subprocess decoding to `_default_guard_runner`.
- [x] Add explicit UTF-8 subprocess decoding to `_default_command_runner`.
- [x] Add focused regression tests for decode kwargs and cp1252-invalid UTF-8 child output.
- [x] Run the focused Ollama dispatch test suite.
- [x] Run lint and format checks on changed files.

## Non-Scope Confirmation

No changes were made to:

- dispatcher topology, ranking, eligibility, or caps
- model pins
- worker lifetime timers
- direct harness invocation behavior
- credential handling
- deployment configuration
- retired poller behavior
- `.codex/skills/verify/helpers/write_verdict.py` or the WI-4975 partial implementation surface

## Risk And Rollback

Risk is low and localized. The change only affects how captured child stdout/stderr is decoded inside the Ollama harness. Replacement decoding preserves model-visible evidence while preventing the reader-thread crash path.

Rollback is a two-line source revert plus removal of the two focused tests, but rollback would re-expose Windows cp1252 subprocess capture failures in headless Ollama reviews.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
