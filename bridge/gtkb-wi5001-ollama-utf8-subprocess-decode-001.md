NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5.5
author_model_version: Codex Desktop 2026-07-03
author_model_configuration: Codex Desktop interactive; owner init ::init gtkb pb; reasoning effort Extra High; governed WI-5001 bridge proposal filing

# Implementation Proposal - WI-5001 Ollama UTF-8 subprocess decode repair

bridge_kind: prime_proposal
Document: gtkb-wi5001-ollama-utf8-subprocess-decode
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5001-OLLAMA-UTF8-DECODE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5001

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix the live Ollama-D headless Loyal Opposition failure observed during the 2026-07-03 dispatcher soak: the active worker `2026-07-03T20-44-52Z-loyal-opposition-D-a9de0d` remained alive but stopped making bridge progress after repeated Python `subprocess` reader-thread `UnicodeDecodeError` traces while processing `bridge/gtkb-role-authority-boundary-implementable-correction-007.md`. The front-of-queue report stayed latest `NEW`, and `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md` remained pending behind it.

The smallest fix is to make the Ollama harness subprocess wrappers decode child output explicitly as UTF-8 with tolerant error handling on Windows. The implementation must preserve the existing `CREATE_NO_WINDOW`, timeout, guard, and model/tool-routing behavior.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5001`. The change is limited to `scripts/ollama_harness.py` and focused Ollama harness tests. It must not change dispatcher topology, role assignment, credential handling, production deployment behavior, model pins, or retired poller behavior.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes follow-up bridge-stability repair discovered during live soak; `WI-5001` captures the specific defect; `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5001-OLLAMA-UTF8-DECODE` supplies bounded implementation authorization; and `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` governs stable dispatcher/harness execution. No new or revised requirement is needed before implementation.

## Defect / Reproduction

Live evidence:

- Dispatcher selected Ollama-D as Loyal Opposition and launched `2026-07-03T20-44-52Z-loyal-opposition-D-a9de0d`.
- The worker process stayed alive as `pythonw.exe` with no stdout and low CPU.
- The stderr log repeatedly showed Python `subprocess.py` reader-thread exceptions while decoding child output with the Windows cp1252 codec: `UnicodeDecodeError: 'charmap' codec can't decode byte 0x81`.
- `scripts/ollama_harness.py` currently has two `subprocess.run(..., text=True, capture_output=True)` paths without explicit `encoding` or `errors`: `_default_guard_runner` and `_default_command_runner`.

Expected reproduction test:

- Patch/fake `subprocess.run` or the subprocess text wrapper environment so a child emits bytes that are valid UTF-8 but not decodable under strict cp1252.
- Assert the harness command/guard path requests explicit `encoding="utf-8"` and tolerant `errors` handling.
- Assert returned stdout/stderr remains model-visible rather than losing output or surfacing an uncaught reader-thread crash.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/ollama_harness.py` and `platform_tests/scripts/test_verify_ollama_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires the dispatcher-controlled headless bridge substrate to process work reliably through configured harnesses.
- `ADR-DISPATCHER-ARCHITECTURE-001` - constrains repairs to the centralized dispatcher/harness execution architecture rather than ad hoc peer-harness fallback.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires the implementation to start only after Loyal Opposition GO, work-intent, and implementation-start authorization.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - ties the source/test mutation to the bounded WI-5001 project authorization.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires implementation authorization to validate target paths and PAUTH scope before mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the live soak defect, fix, tests, and report as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing specs and maps them to tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must run focused tests proving the decode repair.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes PAUTH, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization is carried by the existing captured owner decision and PAUTH; no new owner question is needed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is platform-scoped and remains within the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - `WI-5001` is the MemBase backlog authority for this defect.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex Prime must use governed bridge and implementation-start surfaces while filing and implementing.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation should produce a traceable source/test/report artifact chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the live soak defect triggered durable backlog capture and a new bridge proposal.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended headless bridge processing with Codex as Prime Builder and Claude/Ollama as Loyal Opposition, and allowed new soak defects to be captured and authorized as bounded work.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` and `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` - owner directed generous timers plus evidence-based hang classification. This proposal does not shorten timers; it fixes a deterministic subprocess decode failure so timing telemetry can stay meaningful.
- `bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md` and later VERIFIED thread versions - adjacent timer work; this proposal keeps that policy intact.
- `bridge/gtkb-wi4995-document-lease-held-health-010.md` - adjacent lease-health classification work; this proposal keeps lease semantics intact.
- `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-001.md` - earlier Windows subprocess cp1252 reader warning recommended explicit UTF-8/error handling for live runner commands.

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner decision authorizing continued headless dispatch stability repair and new defect capture.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5001-OLLAMA-UTF8-DECODE` - active bounded project authorization for WI-5001 source/test mutation.

## Proposed Scope

- Update `_default_guard_runner` and `_default_command_runner` in `scripts/ollama_harness.py` so subprocess text capture explicitly uses UTF-8 decoding with tolerant error handling.
- Preserve existing `CREATE_NO_WINDOW`, `stdin`, `shell`, `timeout`, `env`, `cwd`, guard, and return-code behavior.
- Add focused regression coverage in `platform_tests/scripts/test_verify_ollama_dispatch.py` proving the subprocess invocation passes explicit encoding/error handling for both guard and Bash command paths.
- Add or adjust one test that simulates non-ASCII tool output and confirms model-visible output is retained rather than dropped.

## Non-Scope

- No dispatcher eligibility, ranking, topology, role, or model-pin changes.
- No timer-threshold changes; WI-4986 remains the timer policy surface.
- No worker reaping or daemon drain logic changes.
- No credential, deployment, external service, or production behavior changes.
- No revival of retired smart-poller or OS poller behavior.

## Specification-Derived Verification Plan

| Spec / governing surface | Required verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused tests prove the Ollama harness subprocess runners are robust to Windows encoding mismatch and preserve command evidence for headless work. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Code inspection and tests confirm the fix remains inside the Ollama harness wrapper and does not add peer-harness fallback or dispatcher topology changes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation report must cite a live latest GO, work-intent claim, and implementation-start packet for the two target paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `implementation_authorization.py begin` and target validation must show the WI-5001 PAUTH covers the two target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest plus Ruff lint and Ruff format checks on the changed source/test files. |
| `GOV-STANDING-BACKLOG-001` | Implementation report must identify `WI-5001` and the dispatcher-modernization project. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short --basetemp .gtkb-state/pytest-ollama-utf8-decode
python -m ruff check scripts/ollama_harness.py platform_tests/scripts/test_verify_ollama_dispatch.py
python -m ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_verify_ollama_dispatch.py
python scripts/implementation_authorization.py validate --target scripts/ollama_harness.py --target platform_tests/scripts/test_verify_ollama_dispatch.py
```

## Acceptance Criteria

- Ollama harness guard and Bash subprocess runners pass explicit UTF-8 decoding and tolerant error handling to `subprocess.run`.
- Regression tests fail on the old implicit-locale form and pass with the explicit decoding fix.
- Non-ASCII child output remains model-visible in the harness result instead of causing reader-thread decode crashes or silent evidence loss.
- No dispatcher topology, role, model, timer, credential, deployment, or retired-poller behavior changes.
- Focused pytest, Ruff lint, and Ruff format checks pass.

## Risks / Rollback

Risk is low and localized to how Ollama harness subprocess output is decoded before being returned to the model. Tolerant decoding may replace undecodable bytes rather than failing hard, but that is preferable for model-visible command evidence and prevents a worker hang.

Rollback is a normal revert of `scripts/ollama_harness.py` and `platform_tests/scripts/test_verify_ollama_dispatch.py`. Bridge files, MemBase WI rows, and PAUTH records are append-only governance artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

## Recommended Commit Type

`fix`
