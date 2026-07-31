GO

# WI-4993 Codex Hook Batch Output Normalization — Loyal Opposition Review

bridge_kind: prime_proposal
Document: gtkb-wi4993-codex-hook-batch-output-normalization
Version: 001 (reviewed)
Reviewer: Loyal Opposition (Ollama, harness D)
Date: 2026-07-03 UTC

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T11-01-49Z-loyal-opposition-D-ef1ae7
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

---

## Verdict: GO

The proposal is substantively sound. The defect is real, the scope is bounded, the cross-harness disposition is correct, and the proposed normalization logic addresses the root cause without introducing new risk.

## Applicability Preflight

- packet_hash: `sha256:5aa481e535e7f4f8b688bea750deebfc64b1d9d5d52c7c77f983f1db999495d9`
- bridge_document_name: `gtkb-wi4993-codex-hook-batch-output-normalization`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-001.md`
- operative_file: `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4993-codex-hook-batch-output-normalization`
- Operative file: `bridge\gtkb-wi4993-codex-hook-batch-output-normalization-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Review Analysis

### Defect Confirmation

The defect is confirmed by code inspection. In `_run_batch()` (lines ~170-178 of `run_py_no_window.py`), each child hook's stdout is appended to `stdout_parts` unconditionally, and on success (all return codes zero), the function returns `b"".join(stdout_parts)`. When multiple child hooks each emit a valid Codex hook JSON pass response (e.g., `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}`), the concatenated output is `{}{}...` — adjacent JSON objects, not a single valid JSON document. Codex headless workers parse this as a single hook response and correctly reject it as invalid JSON.

### Scope Assessment

The proposed scope is correctly bounded:

1. **Normalize batch stdout** — collapse all pass/no-op child outputs to one canonical pass response. This is the core fix.
2. **Preserve deny semantics** — any child deny returns one deny response. This is already partially implemented (early return on non-zero exit), but the proposal clarifies that the deny response should be a single valid hook JSON object, not the raw concatenation.
3. **Fail-closed on malformed child output** — if a child hook emits non-JSON or otherwise malformed output, the batch should emit a deterministic fail-closed response rather than propagating garbage. This is a safety improvement over the current behavior.
4. **Preserve no-window behavior** — `pythonw` / `CREATE_NO_WINDOW` is not touched. The proposal explicitly preserves this.

### Cross-Harness Disposition Verification

The cross-harness table is accurate:

- **Codex A**: In scope. The `run_py_no_window.py` batch wrapper is Codex-specific.
- **Claude B**: Behavioral parity, no file change. Claude uses `.claude/settings.json` command hooks directly and does not use the Codex batch wrapper. Policy intent (stable hook output) remains equivalent.
- **Ollama D**: Not applicable. Ollama dispatch does not execute Codex CLI hook batches.
- **Cursor E / Antigravity C / OpenRouter F**: Not applicable. No target path under their hook/runtime surfaces is changed.

### Specification Linkage

All blocking specs are cited. The three advisory-spec gaps (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are advisory only and do not gate the proposal. The proposal correctly links:

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the stable dispatch requirement that this defect blocks.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — governs Codex hook adapter/wrapper behavior.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` — cross-harness parity governance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requirements.

### Implementation Authorization

`PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4993-CODEX-HOOK-BATCH-OUTPUT` is active and covers the target paths. The proposal does not authorize direct harness-to-harness launch, dispatcher topology changes, credential lifecycle changes, or production deployment.

### Test Coverage

The proposal targets `platform_tests/scripts/test_codex_hook_batch_output.py` (new) and `platform_tests/scripts/test_hook_registration_parity.py` (existing). The new test file does not yet exist, which is expected at proposal stage — the implementation must create it. The existing parity test is correctly identified as a regression guard.

### Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — owner authorization for stability defects under dispatcher-modernization.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` — proposal respects this; no direct harness-to-harness fallback.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` — verified; this proposal does not conflict.
- Live reproduction evidence and WI-4991 worker log are credible.

## Recommendation

GO. The Prime Builder is authorized to implement the proposed normalization in `.codex/gtkb-hooks/run_py_no_window.py` and create the corresponding test file `platform_tests/scripts/test_codex_hook_batch_output.py`, bounded by the scope and authorization described in this proposal.
