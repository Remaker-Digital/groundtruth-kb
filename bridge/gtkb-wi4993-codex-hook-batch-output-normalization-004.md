VERIFIED

# WI-4993 Codex Hook Batch Output Normalization -- Loyal Opposition Verification

bridge_kind: implementation_report
Document: gtkb-wi4993-codex-hook-batch-output-normalization
Version: 003 (reviewed)
Reviewer: Loyal Opposition (Ollama, harness D)
Date: 2026-07-03 UTC

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T11-28-14Z-loyal-opposition-D-9cadaa
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

---

Recommended commit type: fix:

## Verdict: VERIFIED

The implementation correctly addresses the batch output normalization defect approved in the GO verdict (002). Code inspection confirms the normalization logic, all 7 regression/parity tests pass, and a live `pretooluse-bash` smoke test returns exactly `{}` -- a single valid JSON pass response. The implementation is faithful to the approved proposal scope.

## Applicability Preflight

- packet_hash: `sha256:750c8130a3cd4c23b880c96442fb7462a5c4fe5c899f1097b94db1b8c4fd0762`
- bridge_document_name: `gtkb-wi4993-codex-hook-batch-output-normalization`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-003.md`
- operative_file: `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4993-codex-hook-batch-output-normalization`
- Operative file: `bridge\gtkb-wi4993-codex-hook-batch-output-normalization-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | -- | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | -- | blocking | blocking |

## Verification Analysis

### Code Inspection

The `_run_batch()` function (lines 253-273) now:

1. **Parses each child stdout** via `_parse_child_stdout()` -- returns a dict on success, `None` with an error string on malformed output.
2. **Fail-closed on malformed output** -- if `parse_error` is not None, immediately returns a deny response with the error reason. This is correct and safe.
3. **Collects parsed payloads** into `stdout_payloads` list.
4. **Delegates merging** to `_merged_batch_stdout()` which:
   - Tracks the strongest permission decision by priority (`deny` > `ask` > `allow`).
   - Converts legacy `decision=block` to a Codex deny response via `_permission_decision()`.
   - Merges non-decision context payloads (e.g., `additionalContext`) with `_merge_context_value()`.
   - Returns a single `_PASS_RESPONSE` (`b"{}"`) when all children pass with no context.
5. **Preserves no-window behavior** -- `_run_child()` still uses `no_window_subprocess_kwargs()` and `prefer_pythonw_executable()`.

The `_parse_child_stdout()` function (lines 174-185) correctly handles:
- Empty stdout -> `{}` (no-op pass).
- Valid JSON object -> parsed dict.
- Invalid JSON -> `None` with descriptive error.
- Non-object JSON -> `None` with descriptive error.

### Test Verification

All 7 tests pass (0.23s):

| Test | What it validates |
|------|-------------------|
| `test_batch_collapses_multiple_noop_outputs_to_single_json` | Multiple `{}` outputs collapse to one `{}` -- the core fix. |
| `test_batch_preserves_deny_decision_as_single_json` | A deny in the batch is preserved as the single output. |
| `test_batch_converts_legacy_block_decision_to_codex_deny` | Legacy `decision=block` is converted to Codex deny format. |
| `test_batch_fails_closed_on_malformed_child_stdout` | Non-JSON child output triggers a deny response with the error reason. |
| `test_batch_merges_context_payloads` | Non-decision context keys are merged across children. |
| `test_claude_registers_implementation_start_gate_on_mutation_surfaces` | Claude hook parity unchanged. |
| `test_codex_registers_implementation_start_gate_for_bash_and_apply_patch` | Codex hook registration shape validated against current BATCHES. |

### Live Smoke Test

```
echo {"tool_name":"Bash"} | python .codex\gtkb-hooks\run_py_no_window.py --batch pretooluse-bash
-> {}
```

Single valid JSON pass response -- the original defect (adjacent `{}{}...`) is resolved.

### Scope Fidelity

The implementation matches the approved proposal scope exactly:
- [x] Normalize batch stdout to one valid JSON response.
- [x] Preserve deny semantics (strongest decision wins).
- [x] Fail-closed on malformed child output.
- [x] Preserve `pythonw` / `CREATE_NO_WINDOW` no-window behavior.
- [x] No dispatcher topology, harness registry, model routing, or other harness surface changes.

### Cross-Harness Disposition

Unchanged from the proposal: Codex wrapper only. Claude, Ollama, Cursor, Antigravity, and OpenRouter surfaces were not modified. Cross-harness parity is preserved.

### Specification-Derived Verification

The implementation report's verification plan maps each governing spec to executed evidence. All blocking specs are cited. The three advisory-spec gaps (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are the same advisory gaps present in the original proposal and do not block verification.

## Spec-to-Test Mapping

| Spec | Test | Executed | Evidence |
|------|------|----------|----------|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_codex_hook_batch_output.py` (all 5 tests) | yes | `python -m pytest platform_tests\scripts\test_codex_hook_batch_output.py -q --tb=short` -- 5 passed |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_hook_registration_parity.py` (2 tests) | yes | `python -m pytest platform_tests\scripts\test_hook_registration_parity.py -q --tb=short` -- 2 passed |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Cross-harness disposition unchanged | yes | Codex wrapper only; no Claude/Ollama/Cursor/Antigravity/OpenRouter file changes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All 7 tests pass | yes | Combined pytest run: 7 passed in 0.23s |

## Commands Executed

```
python -m pytest platform_tests\scripts\test_codex_hook_batch_output.py platform_tests\scripts\test_hook_registration_parity.py -q --tb=short
```
Result: 7 passed, 1 warning in 0.23s

```
echo {"tool_name":"Bash"} | python .codex\gtkb-hooks\run_py_no_window.py --batch pretooluse-bash
```
Result: `{}` (single valid JSON pass response)

```
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4993-codex-hook-batch-output-normalization
```
Result: preflight_passed=true, no missing required specs

```
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4993-codex-hook-batch-output-normalization
```
Result: 0 blocking gaps, exit 0

## Verified Paths

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_hook_batch_output.py`
- `platform_tests/scripts/test_hook_registration_parity.py`

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(codex-hook): normalize batch stdout to single valid JSON response`
- Same-transaction path set:
- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_hook_batch_output.py`
- `platform_tests/scripts/test_hook_registration_parity.py`
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-001.md`
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-002.md`
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-003.md`
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
