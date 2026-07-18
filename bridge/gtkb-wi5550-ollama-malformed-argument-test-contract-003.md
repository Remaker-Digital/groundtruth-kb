NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5550-ollama-malformed-argument-test-contract - 003

bridge_kind: implementation_report
Document: gtkb-wi5550-ollama-malformed-argument-test-contract
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5550-ollama-malformed-argument-test-contract-002.md
Approved proposal: bridge/gtkb-wi5550-ollama-malformed-argument-test-contract-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5550
Recommended commit type: test:

## Implementation Claim

Replaced only
`test_tool_loop_rejects_malformed_tool_arguments` in
`platform_tests/scripts/test_ollama_harness.py` with
`test_tool_loop_recovers_from_malformed_tool_arguments`.

The regression now executes two deterministic provider turns. The first emits
a `Read` tool call with stable id `bad_1` and malformed JSON arguments. On the
second turn, the test requires the provider payload to contain a correlated
`role=tool`, `name=Read`, `tool_call_id=bad_1` result whose content starts with
`ERROR:` and contains the malformed-JSON diagnostic. The simulated provider
then returns `recovered`, and the test requires the loop to return that final
text after exactly two calls.

No provider source, dispatcher configuration, TAFE/runtime state, lease, role,
eligibility, route, cap, allowance, or unrelated dirty path was changed.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`

## Owner Decisions / Input

No new owner decision is required. The implementation remains within
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, whose owner-decision evidence
is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing owner authorization
  for bounded reliability fixes meeting the fast-lane criteria.
- No other relevant prior deliberation was found for this exact stale
  malformed-argument test contract, as independently recorded in the GO
  verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Exact one-test diff; focused regression passed `1/1`, affected module passed `77/77`, and shared resilience module passed `4/4`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Current bridge status read back as GO v002; claim row 33286, schema-v3 start packet, and operation-time target validation were live before each mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5550 and linked TEST-11630 were read from MemBase; this numbered implementation report preserves the implementation evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passed with `missing_required_specs: []` and no blocking errors. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused, full affected-module, shared resilience, Ruff, compile, and diff checks were executed with results below. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Active PAUTH, project, WI-5550, TEST-11630, and the exact one-file target were read back before implementation. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Applicability preflight passed; no new owner decision or AUQ dependency was introduced. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The only changed path is the approved in-root platform test file; `git diff --check` passed. |
| `GOV-STANDING-BACKLOG-001` | WI-5550 remains the canonical P0 reliability carrier with TEST-11630; the implementation did not create a duplicate work item. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Operation-time authorization was self-enforced before the edit and formatter mutation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Proposal, independent GO, linked test, implementation evidence, and this verification request remain in canonical carriers. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The completed implementation is routed through this NEW report for independent LO verification before commit. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | The affected Ollama module passed `77/77` and the cross-shim malformed-call resilience module passed `4/4`; no provider source changed. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_ollama_harness.py::test_tool_loop_recovers_from_malformed_tool_arguments -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_shim_toolcall_arg_resilience.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check platform_tests/scripts/test_ollama_harness.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check platform_tests/scripts/test_ollama_harness.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile platform_tests/scripts/test_ollama_harness.py`
- `git diff --check -- platform_tests/scripts/test_ollama_harness.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5550-ollama-malformed-argument-test-contract`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5550-ollama-malformed-argument-test-contract`

## Observed Results

- Focused regression: `1 passed`.
- Complete affected module: `77 passed`.
- Shared cloud/Ollama malformed-call resilience module: `4 passed`.
- Ruff check: `All checks passed!`.
- Ruff format check: `1 file already formatted`.
- `py_compile`: exit 0 with no diagnostics.
- `git diff --check`: exit 0 with no diagnostics.
- Applicability preflight: `preflight_passed: true`,
  `missing_required_specs: []`, and `blocking_errors: []`.
- Clause preflight: five clauses evaluated, zero must-apply evidence gaps,
  zero blocking gaps, exit 0.
- Pytest emitted only the repository-wide
  `PytestConfigWarning: Unknown config option: asyncio_mode`; no test failed.

## Files Changed

- `platform_tests/scripts/test_ollama_harness.py`

Excluded out-of-scope dirty paths: 1871.

## Recommended Commit Type

- Recommended commit type: `test:`
- Diff-stat justification: All changed paths are test paths.

```text
     platform_tests/scripts/test_ollama_harness.py | 23 +++++++++++++++++++----
     1 file changed, 19 insertions(+), 4 deletions(-)
```

## Acceptance Criteria Status

- PASS - The focused affected-module regression proves malformed JSON is
  returned as a correlated `ERROR:` tool result and a corrected next turn
  completes without immediate worker abort.
- PASS - The complete `platform_tests/scripts/test_ollama_harness.py` module
  passes `77/77`.
- PASS - `platform_tests/scripts/test_shim_toolcall_arg_resilience.py` passes
  `4/4`; Ruff check and format check pass for the one target file.

## Risk And Rollback

Residual risk is limited to test-fixture fidelity: the regression uses a
deterministic simulated provider payload rather than a paid provider call.
That is appropriate for this contract and is reinforced by the full affected
module and shared cloud/Ollama resilience suite. Independent LO should inspect
the exact diff and rerun the recorded commands.

Rollback restores only the replaced test function in
`platform_tests/scripts/test_ollama_harness.py`. Numbered bridge audit files
remain append-only and are not deleted by rollback.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
