GO
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T21-09-00Z-loyal-opposition-D-d772a9
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Loyal Opposition Review — WI-5001 Ollama UTF-8 subprocess decode repair

### Verdict: GO

The proposal is well-scoped, the defect is real and confirmed by source inspection, the fix is minimal and correct, and all preflight checks pass cleanly.

### Defect Confirmation

I inspected the two `subprocess.run()` call sites in `scripts/ollama_harness.py`:

- **Line 587** (`_default_guard_runner`): `subprocess.run(..., text=True, capture_output=True, ...)` — no `encoding` or `errors`.
- **Line 849** (`_default_command_runner`): `subprocess.run(..., text=True, capture_output=True, ...)` — no `encoding` or `errors`.

On Windows, `text=True` without explicit `encoding` defaults to `locale.getpreferredencoding(False)`, which is typically cp1252. When a child process emits bytes that are valid UTF-8 but not valid cp1252 (e.g., byte 0x81 in a bridge verdict containing Unicode), the subprocess reader thread raises `UnicodeDecodeError`. This matches the live-soak evidence: the worker stayed alive but stopped making bridge progress after repeated decode traces.

The harness already uses `encoding="utf-8"` consistently for its own file I/O (lines 740, 759, 780, 790, 815) and `ensure_utf8_output_streams()` for its own stdout/stderr. The two `subprocess.run()` calls are the only remaining paths that lack explicit UTF-8 encoding — they are the root cause.

### Fix Assessment

Adding `encoding="utf-8"` and a tolerant `errors` value (I recommend `errors="replace"` for subprocess output — consistent with Python's standard text wrapper behavior and simpler than `backslashreplace` for model-visible text) to both call sites is the correct minimal fix. The `_default_guard_runner`'s `TimeoutExpired` handler (line 21) accesses `exc.stdout` and `exc.stderr` which are already decoded strings from the same text wrapper, so the fix also prevents the timeout path from crashing on undecodable partial output.

### Scope Verification

- **Source change**: `scripts/ollama_harness.py` only — two `subprocess.run()` call sites.
- **Test change**: `platform_tests/scripts/test_verify_ollama_dispatch.py` — focused tests for the decode repair.
- **No KB mutation**, no dispatcher topology change, no credential handling change, no model pin change.
- **In-root**: Both target paths are under `E:\GT-KB`.

### Preflight Results

Both preflight checks pass cleanly:

- **Applicability Preflight**: `preflight_passed: true`, no missing required specs, no missing advisory specs.
- **Clause Preflight**: All 4 must_apply clauses have evidence; 0 blocking gaps; exit 0.

### Specification Linkage

The proposal links the governing specs adequately. The defect is a platform-specific subprocess encoding issue on Windows; it does not require cross-cutting specs like credential handling or deployment topology. The linked specs cover the relevant governance surface: dispatcher stability (SPEC-CENTRALIZED-DISPATCH-SERVICE-001), bridge authority (GOV-FILE-BRIDGE-AUTHORITY-001), project authorization (GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001), and artifact governance (GOV-ARTIFACT-ORIENTED-GOVERNANCE-001).

### Recommendation

GO. Prime Builder may proceed with implementation under WI-5001. The implementation should:

1. Add `encoding="utf-8", errors="replace"` to both `subprocess.run()` calls (lines 587 and 849).
2. Add focused tests in `platform_tests/scripts/test_verify_ollama_dispatch.py` that:
   - Verify the encoding/errors kwargs are present in both call sites.
   - Verify that child output containing bytes undecodable under cp1252 is safely captured.
3. Run the existing Ollama dispatch test suite to confirm no regression.

### Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — owner directed stable unattended headless bridge processing; this repair directly serves that goal.
- `WI-5001` — MemBase backlog authority for this specific defect.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5001-OLLAMA-UTF8-DECODE` — bounded implementation authorization.

### Applicability Preflight

- packet_hash: `sha256:f3fa1a4d52ad8377560f2e9367c373a8cd930483f7d54683f42c2be55b1be4c7`
- bridge_document_name: `gtkb-wi5001-ollama-utf8-subprocess-decode`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-001.md`
- operative_file: `bridge/gtkb-wi5001-ollama-utf8-subprocess-decode-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: `{"status": "harvested", "candidate_heading": null}`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

### Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5001-ollama-utf8-subprocess-decode`
- Operative file: `bridge\gtkb-wi5001-ollama-utf8-subprocess-decode-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
