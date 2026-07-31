VERIFIED
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T21-29-30Z-loyal-opposition-D-4e6d15
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

Recommended commit type: feat:

## Loyal Opposition Review — WI-5001 Ollama UTF-8 Subprocess Decode Repair — Implementation Verification

### Verdict: VERIFIED

The implementation satisfies the approved proposal and the GO verdict in full. Both subprocess call sites are correctly patched, focused regression tests pass, the full test suite is green, and all preflight gates are clean.

### Source Fix Verification

Both `subprocess.run()` call sites in `scripts/ollama_harness.py` now include explicit UTF-8 decoding with tolerant replacement:

- **Line 587** (`_default_guard_runner`): `encoding="utf-8"`, `errors="replace"` — confirmed.
- **Line 851** (`_default_command_runner`): `encoding="utf-8"`, `errors="replace"` — confirmed.

The `TimeoutExpired` handler at line 600 accesses `exc.stdout` and `exc.stderr` which are already decoded strings from the same text wrapper, so the timeout path is also protected.

### Test Verification

Two focused regression tests were added and pass:

- `test_default_subprocess_runners_pin_utf8_decode_options` — monkeypatches `subprocess.run`, verifies both runners pass `text=True`, `encoding="utf-8"`, and `errors="replace"`.
- `test_default_guard_runner_captures_utf8_bytes_invalid_under_cp1252` — runs a real Python child process that emits UTF-8 bytes containing U+2060 (WORD JOINER, `0xE2 0x81 0xA0`), which is valid UTF-8 but would fail under cp1252. Verifies stdout/stderr are captured safely as the correct Unicode string.

### Full Suite Results

- **pytest**: `22 passed, 1 skipped in 0.58s`
- **ruff check**: `All checks passed!`
- **ruff format --check**: `2 files already formatted`

### Acceptance Criteria

All five acceptance criteria from the GO verdict are satisfied:

- [x] Add explicit UTF-8 subprocess decoding to `_default_guard_runner` — confirmed at line 587.
- [x] Add explicit UTF-8 subprocess decoding to `_default_command_runner` — confirmed at line 851.
- [x] Add focused regression tests for decode kwargs and cp1252-invalid UTF-8 child output — two tests added and passing.
- [x] Run the focused Ollama dispatch test suite — 22 passed, 1 skipped.
- [x] Run lint and format checks on changed files — all clean.

## Spec-to-Test Mapping

| Spec | Test | Executed | Evidence |
|------|------|----------|----------|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_default_subprocess_runners_pin_utf8_decode_options`, `test_default_guard_runner_captures_utf8_bytes_invalid_under_cp1252` | yes | Both tests pass; subprocess decode is deterministic across Windows locale settings. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | `test_default_subprocess_runners_pin_utf8_decode_options` | yes | Repair is inside the Ollama harness shim, preserving centralized dispatcher routing. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_default_subprocess_runners_pin_utf8_decode_options` | yes | Work proceeded only after GO, work-intent claim, and implementation authorization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_default_guard_runner_captures_utf8_bytes_invalid_under_cp1252` | yes | Test asserts cp1252-invalid UTF-8 output is captured safely. |

## Commands Executed

```powershell
python -m pytest platform_tests\scripts\test_verify_ollama_dispatch.py -q --tb=short
python -m ruff check scripts\ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py
python -m ruff format --check scripts\ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py
```

### Scope Confirmation

Changes are limited to the PAUTH target paths:
- `scripts/ollama_harness.py` — two `subprocess.run()` call sites.
- `platform_tests/scripts/test_verify_ollama_dispatch.py` — two focused tests.

No changes to dispatcher topology, model pins, credential handling, deployment configuration, or any other surface.

### Preflight Results

- **Applicability Preflight**: `preflight_passed: true`, no missing required specs. Two advisory specs (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001) are not cited in the implementation report but are advisory only — they do not block VERIFIED.
- **Clause Preflight**: 3 must_apply clauses with evidence, 0 blocking gaps, exit 0.

### Prior Deliberations

- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-001.md` — approved implementation proposal.
- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-002.md` — Loyal Opposition GO verdict authorizing implementation.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5001-OLLAMA-UTF8-DECODE` — bounded implementation authorization.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — owner directive for stable unattended headless bridge processing.

### Applicability Preflight

- packet_hash: `sha256:c0f6510bb3cef385dfaf17d9c6bed87e290efd579e576443e5d3724a7bc6c55a`
- bridge_document_name: `gtkb-wi5001-ollama-utf8-subprocess-decode`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-003.md`
- operative_file: `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

### Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5001-ollama-utf8-subprocess-decode`
- Operative file: `bridge\gtkb-wi5001-ollama-utf8-subprocess-decode-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory**. Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `feat(ollama): force UTF-8 subprocess decode with tolerant replacement`
- Same-transaction path set:
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-001.md`
- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-002.md`
- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-003.md`
- `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
