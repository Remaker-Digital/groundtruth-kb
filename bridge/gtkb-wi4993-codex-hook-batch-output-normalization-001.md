NEW

# WI-4993 Codex Hook Batch Output Normalization

bridge_kind: prime_proposal
Document: gtkb-wi4993-codex-hook-batch-output-normalization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Extra High reasoning; Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4993-CODEX-HOOK-BATCH-OUTPUT
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4993

target_paths: [".codex/gtkb-hooks/run_py_no_window.py", "platform_tests/scripts/test_codex_hook_batch_output.py", "platform_tests/scripts/test_hook_registration_parity.py"]

implementation_scope: codex-hook-wrapper
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Fix the Codex hook batch invalid-JSON blocker found during the live headless bridge soak. A harmless `pretooluse-bash` reproduction currently emits adjacent pass objects (`{}{}...`) instead of one valid Codex hook JSON response, so Codex headless PB workers can hit `hook returned invalid pre-tool-use JSON output` before pytest or other verification commands execute.

The implementation must normalize `.codex/gtkb-hooks/run_py_no_window.py` batch stdout: pass/no-op child outputs collapse to one pass response, deny outputs remain one deny response, malformed child output is fail-closed, and Windows no-window process creation remains intact.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — stable unattended dispatch requires spawned Codex PB workers to execute approved verification and implementation commands without hook-protocol self-blocking.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite every relevant governing specification for the implementation slice.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires PAUTH/project/WI metadata and machine-readable target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — requires bounded project implementation authorization before protected hook/test mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires append-only bridge review and role-correct status handling.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — governs Codex hook parity through adapter/wrapper behavior where Codex and Claude hook schemas differ.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — requires harness-surface proposals to state parity or waiver disposition explicitly.
- `ADR-CROSS-HARNESS-PARITY-001` — requires harness-specific hook changes to preserve policy equivalence across harnesses.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires implementation reports to map linked requirements to executed tests before VERIFIED.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — owner directed stable unattended headless bridge processing with Codex A as PB and Claude/Ollama as LO, and authorized new governed defects under the dispatcher-modernization project when needed for stability.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` — owner prohibited direct harness-to-harness fallback; this proposal preserves dispatcher-only operation and does not add a direct launch path.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` — verified direct harness launch guard.
- Live reproduction, 2026-07-03: `.codex/gtkb-hooks/run_py_no_window --batch pretooluse-bash` with a harmless `Get-Location` payload returned multiple adjacent JSON objects instead of one hook response.
- Live WI-4991 worker `2026-07-03T10-11-51Z-prime-builder-A-4a4cc1` logged `hook: PreToolUse Failed` before pytest commands, and no `.gtkb-state/pytest-tmp/wi4991` output was created.

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` is the owner-decision evidence for adding this stability defect and bounded authorization.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4993-CODEX-HOOK-BATCH-OUTPUT` is active and covers only bridge, Codex hook-wrapper, and tests for WI-4993.
- This proposal does not authorize direct harness-to-harness launch or fallback, dispatcher topology or eligibility changes, credential lifecycle changes, or production deployment.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` states the stable dispatcher requirement; `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, and `ADR-CROSS-HARNESS-PARITY-001` govern the Codex-specific hook-wrapper surface; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` governs verification. No new requirement is needed before implementation.

## Cross-Harness Disposition

| Harness | Disposition |
| --- | --- |
| Codex A | In scope. Normalize `.codex/gtkb-hooks/run_py_no_window.py` because Codex hook batches produce the invalid JSON output blocking Codex headless PB workers. |
| Claude Code B | Behavioral parity, no file change. Claude uses `.claude/settings.json` command hooks directly and does not use the Codex batch wrapper; policy intent remains equivalent. |
| Ollama D | Not applicable. Ollama dispatch does not execute Codex CLI hook batches; no Ollama routing or model configuration change is authorized. |
| Cursor E / Antigravity C / OpenRouter F | Not applicable for this slice. No target path under their hook/runtime surfaces is changed. |

## Proposed Scope

- Normalize `run_py_no_window.py` batch stdout so a successful batch emits exactly one valid Codex hook JSON object instead of concatenating child pass outputs.
- Preserve child deny semantics by returning one deny `hookSpecificOutput` when any child hook denies.
- Treat malformed child hook stdout as a deterministic fail-closed hook response.
- Preserve `pythonw` / `CREATE_NO_WINDOW` no-window behavior for child hook execution.
- Add regression tests for pass aggregation, deny preservation, malformed child output handling, and current `.codex/hooks.json` registration shape.

## Specification-Derived Verification Plan

| Specification / Requirement | Planned Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused test proves a harmless Codex PreToolUse batch emits one parseable JSON object and no longer blocks verification commands via invalid hook output. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Hook registration/parity tests cover Codex Bash/apply_patch batch registrations and wrapper behavior. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` / `ADR-CROSS-HARNESS-PARITY-001` | Implementation report confirms this cross-harness disposition and no non-Codex hook surfaces changed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal and report carry all relevant governing spec links. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start authorization validates exact target paths before protected mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact commands, observed results, and this spec-to-test mapping. |

Expected commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_hook_batch_output.py platform_tests/scripts/test_hook_registration_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_hook_batch_output.py platform_tests/scripts/test_hook_registration_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_hook_batch_output.py platform_tests/scripts/test_hook_registration_parity.py
```

## Acceptance Criteria

- A harmless `pretooluse-bash` reproduction emits one parseable JSON object, not adjacent JSON objects.
- A child deny payload remains a deny response and is not swallowed by aggregation.
- Malformed child stdout cannot create invalid aggregate JSON; behavior is deterministic and tested.
- Existing no-window hook execution remains in place.
- Focused pytest, ruff check, and ruff format-check commands pass.

## Risks / Rollback

Risk: normalization could hide a child hook denial. Mitigation: parse child output and preserve the first deny decision with regression coverage.

Risk: pass aggregation could discard advisory output. Mitigation: Codex hook stdout must be machine-readable JSON; advisory text belongs in stderr or durable hook state files.

Rollback: revert changes to `.codex/gtkb-hooks/run_py_no_window.py` and the focused tests. Bridge files and MemBase/PAUTH rows are append-only audit records and must not be deleted.

## Bridge Filing

This proposal is filed under `bridge/` as `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-001.md`; no prior bridge version is rewritten. Dispatcher/TAFE state plus the numbered bridge file chain remain the live workflow state.

## Recommended Commit Type

fix