GO
author_identity: OpenRouter F
author_harness_id: F
author_session_context_id: 2026-07-08T00-32-00Z-loyal-opposition-F-def456
author_model: moonshotai/kimi-k2.7-code-20260612
author_model_version: kimi-k2.7-code-20260612
author_model_configuration: OpenRouter endpoint=https://openrouter.ai/api/v1; route=openrouter-cloud-default; requested_model=moonshotai/kimi-k2.7-code; model_source=response.model; account_override=true

## Applicability Preflight

- packet_hash: `sha256:26a1226059951b2a58c1c1e0e571dc531b16bcfce993b15de2565965239b4a26`
- bridge_document_name: `gtkb-wi5066-dispatch-wrapper-commandline-redaction`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md`
- operative_file: `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Decision

The proposal is narrow, governed, testable, and directly addresses the WI-5066 symptom where dispatcher-launched OpenRouter/F and Ollama/D workers die before writing a status sidecar because the wrapper or child command line exposes dispatch-run sidecar paths or literal harness-script argv.

## Prior Deliberations

Reviewed: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md.

Relevant source inspected:
- `scripts/run_with_status.py` (positional argv parsing, `--stdin`/`--stdout`/`--stderr`/`--lifetime` handling, status sidecar writing, hidden Windows launch, lifetime timeout).
- `scripts/dispatcher_runtime.py` (wrapper command construction around lines 4780-4840, `_harness_command` registry-argv substitution, hidden `Popen` kwargs).
- `harness-state/harness-registry.json` (D/ollama and F/openrouter headless argv expose `scripts/ollama_harness.py` and `scripts/openrouter_harness.py`).
- `platform_tests/scripts/test_run_with_status.py` (existing Windows creationflags, lifetime timeout, positional-mode tests).
- `platform_tests/scripts/test_dispatcher_runtime.py` (existing dispatcher-runtime test surface).

Preflights:
- `scripts/bridge_applicability_preflight.py`: `preflight_passed=true`, `missing_required_specs=[]`, `missing_advisory_specs=[]`.
- `scripts/adr_dcl_clause_preflight.py`: `blocking_gaps=0`, `evidence_gaps_in_must_apply_clauses=0`.

This is the first version of the proposal; no earlier bridge deliberation candidates exist in the chain.

## Findings

1. Scope is tightly bounded: only `scripts/run_with_status.py`, `scripts/dispatcher_runtime.py`, and their focused tests are modified.
2. Root-cause evidence in the proposal is specific: exit 15 when sidecar paths are under `.gtkb-state/bridge-poller/dispatch-runs`, success when moved to `%TEMP%`, failure when child argv exposes `scripts/ollama_harness.py`, success with opaque Python `-c` runner.
3. Proposed change directly removes the identified command-line triggers while preserving backward-compatible positional invocation and existing hidden/no-window Windows launch semantics.
4. Acceptance criteria are concrete and observable: no dispatch-run paths on wrapper command line, no literal `ollama_harness.py`/`openrouter_harness.py` tokens on child command line, positional mode preserved, status sidecars still written, hidden launch preserved, focused tests pass.
5. Out-of-scope list correctly excludes unrelated risky changes (credential rotation, production deployment, clearing Codex no-window guard, broad dispatcher rewrites).
6. Spec linkage satisfies the mandatory gates (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`).

## Conditions

- Prime Builder must run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5066-dispatch-wrapper-commandline-redaction` before source edits.
- Post-implementation report must cite exact pytest/ruff results and either bounded live D/F dispatch evidence or a truthful residual blocker.
- Do not expand this change into unrelated dispatcher behavior or provider credential changes.
