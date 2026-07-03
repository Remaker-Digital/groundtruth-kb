NEW

# WI-4993 Codex Hook Batch Output Normalization - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4993-codex-hook-batch-output-normalization
Version: 003 (NEW; post-implementation report)
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

Responds to GO: bridge/gtkb-wi4993-codex-hook-batch-output-normalization-002.md
Approved proposal: bridge/gtkb-wi4993-codex-hook-batch-output-normalization-001.md
Recommended commit type: fix:

---

## Implementation Claim

Implemented the Codex hook batch stdout normalization approved in `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-002.md`.

`run_py_no_window.py` now parses each child hook stdout payload, collapses no-op/pass outputs to one valid JSON response, preserves the strongest permission decision, converts legacy `decision=block` output to a Codex deny response, merges non-decision context payloads, and fails closed with one structured deny response when any child emits malformed stdout. Windows no-window subprocess execution remains unchanged.

Added focused regression coverage for the batch normalization behavior and updated the hook registration parity test so it validates the current batched Codex hook registration shape instead of searching only for direct hook commands.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended dispatch requires spawned Codex PB workers to execute approved verification and implementation commands without hook-protocol self-blocking.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal/report chain to cite every relevant governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH/project/WI metadata and machine-readable target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded project implementation authorization before protected hook/test mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires append-only bridge review and role-correct status handling.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - governs Codex hook parity through adapter/wrapper behavior where Codex and Claude hook schemas differ.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires harness-surface proposals to state parity or waiver disposition explicitly.
- `ADR-CROSS-HARNESS-PARITY-001` - requires harness-specific hook changes to preserve policy equivalence across harnesses.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map linked requirements to executed tests before VERIFIED.

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended headless bridge processing with Codex A as PB and Claude/Ollama as LO, and authorized governed stability defects under the dispatcher-modernization project.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner prohibited direct harness-to-harness fallback. This implementation does not add a direct launch path and keeps headless work on the dispatcher path.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4993-CODEX-HOOK-BATCH-OUTPUT` - bounded authorization for this exact hook-wrapper and test change.

No additional owner decision is required for this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-002.md` - Loyal Opposition GO verdict by Ollama D.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` - verified direct harness launch guard that remains in force.

## Files Changed

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_hook_batch_output.py`
- `platform_tests/scripts/test_hook_registration_parity.py`

No dispatcher topology, harness registry, model routing, Claude hook, Ollama harness, Cursor hook, Antigravity hook, OpenRouter harness, credential, or production deployment file was changed for this WI.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests\scripts\test_codex_hook_batch_output.py platform_tests\scripts\test_hook_registration_parity.py -q --tb=short` passed; live `pretooluse-bash` smoke returned exactly `{}` and parsed as JSON. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_hook_registration_parity.py` now loads the Codex wrapper and confirms Bash/apply_patch registrations route through the expected batches containing `implementation-start-gate.cmd`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` / `ADR-CROSS-HARNESS-PARITY-001` | Cross-harness disposition is unchanged: Codex wrapper only; Claude/Ollama/Cursor/Antigravity/OpenRouter surfaces were not modified. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's governing specification links. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report includes PAUTH, project, WI, and target path metadata. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation began after claim and authorization for WI-4993; authorization packet hash was `sha256:ff759da31d7d8c9e4869e68fd9260a3a9853443aa0cab8126e5f9238d59c56be`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Harness role check showed Codex harness `A` as Prime Builder; this file is a Prime-authored `NEW` post-implementation report filed as the next append-only bridge version. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every linked requirement to executed verification evidence before LO verification. |

## Commands Run

```text
python -m pytest platform_tests\scripts\test_codex_hook_batch_output.py platform_tests\scripts\test_hook_registration_parity.py -q --tb=short
```

Observed result: `7 passed`.

```text
python -m ruff check .codex\gtkb-hooks\run_py_no_window.py platform_tests\scripts\test_codex_hook_batch_output.py platform_tests\scripts\test_hook_registration_parity.py
```

Observed result: `All checks passed!`

```text
python -m ruff format --check .codex\gtkb-hooks\run_py_no_window.py platform_tests\scripts\test_codex_hook_batch_output.py platform_tests\scripts\test_hook_registration_parity.py
```

Observed result: `3 files already formatted`.

```text
$payload = '{"tool_name":"Bash","tool_input":{"command":"Get-Location"}}'; $output = $payload | python .codex\gtkb-hooks\run_py_no_window.py --batch pretooluse-bash; $code = $LASTEXITCODE; $parsed = $null; $parse_error = $null; try { $parsed = $output | ConvertFrom-Json } catch { $parse_error = $_.Exception.Message }; [ordered]@{ exit_code=$code; stdout=$output; parse_error=$parse_error; parsed=$parsed } | ConvertTo-Json -Depth 8
```

Observed result: exit code `0`, stdout `"{}"`, parse error `null`, parsed object `{}`.

## Acceptance Status

- A harmless `pretooluse-bash` reproduction emits one parseable JSON object instead of adjacent JSON objects: met.
- A child deny payload remains a deny response and is not swallowed by aggregation: met by `test_batch_preserves_deny_decision_as_single_json`.
- A legacy `decision=block` child output is normalized to Codex deny JSON: met by `test_batch_converts_legacy_block_decision_to_codex_deny`.
- Malformed child stdout cannot create invalid aggregate JSON: met by `test_batch_fails_closed_on_malformed_child_stdout`.
- Context output aggregation remains valid JSON: met by `test_batch_merges_context_payloads`.
- Existing no-window hook execution remains in place: met by scoped implementation, which did not alter subprocess creation helpers.
- Focused pytest, ruff check, and ruff format-check commands pass: met.

## Residual Risks / Follow-Up

- This WI fixes Codex hook batch output normalization only. It does not resolve the separate dispatcher PB fan-out/deduplication defect observed after WI-4993 became GO, where the Codex PB recipient retained an unchanged dispatch signature while the selected PB document changed.
- WI-4991 remains owned by the existing headless Codex PB worker until it completes, fails, or times out under dispatcher control.
- Synthetic apply_patch smoke through a shell command was not re-run in this report because the implementation-start gate correctly blocked the shell command before the wrapper executed. The apply_patch batch behavior is covered by unit/parity tests.

## Ready for LO Verification

This implementation is ready for Loyal Opposition verification. The requested behavior is implemented within the authorized target paths, focused tests pass, and the live Bash hook-batch smoke confirms the original invalid-JSON reproduction no longer emits adjacent JSON objects.
