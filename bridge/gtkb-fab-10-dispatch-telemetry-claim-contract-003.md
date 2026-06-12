NEW

bridge_kind: implementation_report
Document: gtkb-fab-10-dispatch-telemetry-claim-contract
Version: 003
Responds-To: bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-002.md
Approved-Proposal: bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md
Related-Bridge: bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-003.md
Author: prime-builder (Codex, harness A) - interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4422
Project Authorization: PAUTH-FAB10-20260610

author_identity: prime-builder
author_harness_id: A
author_session_context_id: 019ebd61-0067-73d0-bc59-142681b70a9e
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop, Prime Builder bridge queue processing

target_paths: ["scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-compliance-gate.py", ".codex/hooks.json", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/**"]

KB mutation: groundtruth.db is NOT in target_paths. No MemBase mutations in this report.

Recommended commit type: fix:

---

# FAB-10 Dispatch Telemetry Claim Contract - Implementation Report

## Implementation Claim

Implemented the FAB-10 dispatch telemetry, work-intent claim contract, circuit
breaker, and bridge INDEX integrity work approved at
`bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-002.md`.

The base FAB-10 source/test changes are present in the current tree via commit
`47a9b5dd1` and subsequent bridge addenda. The Codex apply-patch adapter path
needed for full HYG-039 parity was out of scope for the original proposal, so it
was handled by the corrected addendum at
`gtkb-fab-10-codex-index-adapter-addendum-sufficiency`; its implementation
report is filed at
`bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-003.md`.

## Summary Of Changes

- `scripts/cross_harness_bridge_trigger.py`
  - raises the bridge work-intent TTL to 600 seconds;
  - aligns dispatched worker identity with the work-intent holder;
  - deduplicates held-thread logging by holder and slug;
  - sanitizes dispatch IDs so Windows filenames do not contain `:`;
  - moves post-dispatch verdict polling into a durable subprocess that writes
    `dispatch-diagnostic-post.jsonl`;
  - adds `GTKB_DISPATCH_*` retry/breaker knobs with `OLLAMA_*` fallback; and
  - adds half-open circuit-breaker recovery.
- `.claude/hooks/bridge-compliance-gate.py`
  - validates `bridge/INDEX.md` writes for malformed content, including literal
    escaped newline text and broken document/status structure.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
  - adds bridge INDEX parse checks so doctor reports malformed canonical bridge
    workflow state.
- `.codex/hooks.json`
  - already registered the Codex bridge-compliance apply-patch adapter; no
    content change was needed in this file.
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
  - via the corrected addendum, forwards Codex `apply_patch` edits to
    `bridge/INDEX.md` to the canonical gate.
- Platform tests
  - add/extend dispatch contract, retry/breaker, durable telemetry,
    bridge INDEX well-formedness, and Codex adapter parity coverage.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains canonical bridge workflow state and now has direct well-formedness checks.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved proposal's linked specs and the corrected adapter addendum.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps tests to the approved specs and acceptance criteria.
- `GOV-STANDING-BACKLOG-001` - WI-4422 remains the governed backlog authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex apply-patch bridge writes now reach the canonical bridge-compliance gate.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - the cross-harness trigger's claim, breaker, and telemetry behavior is the core implementation surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed paths are in-root under `E:\GT-KB`.

## Owner Decisions / Input

No new owner decision was required. This implementation follows
`DELIB-FAB10-REMEDIATION-20260610`: bare dispatch-id claim contract, 600 second
TTL, deduped held logging, colon-safe dispatch filenames, durable
post-dispatch telemetry, half-open breaker, `GTKB_DISPATCH_*` knobs, and INDEX
well-formedness protection now while helper-only CAS writes remain follow-on.

## Prior Deliberations

- `DELIB-FAB10-REMEDIATION-20260610` - owner-selected FAB-10 dispositions.
- `DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610` - telemetry measurement layer enabled by HYG-006.
- `bridge/gtkb-fable-investigation-advisory-001.md` - source advisory for HYG-005/006/007/039.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md` and `-002.md` - proposal and GO.
- `bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-001.md`, `-002.md`, and `-003.md` - corrected adapter addendum proposal, GO, and implementation report.

## Specification-Derived Verification

| Spec / requirement | Executed verification evidence | Observed result |
| --- | --- | --- |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` claim contract | `test_fab10_work_intent_claim_contract_uses_child_dispatch_id`, full `test_cross_harness_bridge_trigger.py` | PASS in combined `87 passed` run. |
| HYG-005 held-log dedupe and 600 second TTL | `test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug`; `test_cross_harness_bridge_trigger.py` TTL assertion | PASS. |
| HYG-006 durable telemetry and colon-safe dispatch IDs | `test_dispatch_post_dispatch_poll.py`; full trigger suite | PASS. Durable subprocess poll and `dispatch-diagnostic-post.jsonl` behavior covered. |
| HYG-007 breaker knobs and half-open recovery | `test_fab10_dispatch_retry_knobs_prefer_gtkb_names`; `test_fab10_circuit_breaker_half_open_after_retry_window`; full trigger suite | PASS. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` INDEX integrity | `test_fab10_index_well_formedness.py`; `test_bridge_compliance_gate_apply_patch_adapter.py` | PASS. Claude gate, doctor parse check, and Codex apply-patch adapter path covered. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `.codex/hooks.json` registration inspection plus corrected adapter addendum tests | PASS. `.codex/hooks.json` already invokes the adapter; addendum tests prove INDEX writes are forwarded. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed path inspection | PASS. All touched paths are under `E:\GT-KB`; no application placement change. |

## Commands Run

```powershell
$env:GTKB_NO_CROSS_HARNESS_TRIGGER=$null; python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_post_dispatch_poll.py platform_tests\scripts\test_fab10_index_well_formedness.py platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab10-final-cleanenv
python -m ruff check scripts\cross_harness_bridge_trigger.py .claude\hooks\bridge-compliance-gate.py .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_post_dispatch_poll.py platform_tests\scripts\test_fab10_index_well_formedness.py platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py
python -m ruff format --check scripts\cross_harness_bridge_trigger.py .claude\hooks\bridge-compliance-gate.py .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_post_dispatch_poll.py platform_tests\scripts\test_fab10_index_well_formedness.py platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py
python -m py_compile scripts\cross_harness_bridge_trigger.py .claude\hooks\bridge-compliance-gate.py .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py
```

## Observed Results

- Combined pytest: `87 passed in 2.92s`.
- Ruff lint: `All checks passed!`.
- Ruff format: `8 files already formatted`.
- Py compile: passed with exit code 0.

The combined pytest command explicitly cleared `GTKB_NO_CROSS_HARNESS_TRIGGER`.
With that loop-prevention variable inherited, the legacy dispatch tests skip
the trigger body and fail on missing `results` / `dispatch_state`; the clean-env
run above is the meaningful behavior verification.

## Files Changed

Base FAB-10 implementation:

- `scripts/cross_harness_bridge_trigger.py`
- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_dispatch_post_dispatch_poll.py`
- `platform_tests/scripts/test_fab10_index_well_formedness.py`

Related corrected adapter addendum:

- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
- `platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py`

No MemBase, deployment, external Agent Red repository, retired poller, or
helper-only CAS write migration is included.

## Acceptance Criteria Status

1. Claim contract uses the child-resolved holder ID and a 600 second TTL. PASS.
2. Repeated held-thread logging is deduped by holder and slug. PASS.
3. Dispatch IDs are filename-safe on Windows. PASS.
4. Post-dispatch telemetry survives process exit and writes durable JSONL. PASS.
5. Dispatch retry knobs prefer `GTKB_DISPATCH_*` with `OLLAMA_*` fallback. PASS.
6. Circuit breaker supports timed half-open recovery. PASS.
7. Bridge INDEX malformed writes are detected by the canonical gate and doctor. PASS.
8. Codex apply-patch edits to `bridge/INDEX.md` reach the canonical gate. PASS via corrected addendum.
9. Helper-only CAS-protected INDEX writes remain out of scope. PASS.

## Risk And Rollback

Residual risk is limited to dispatch-substrate behavior and bridge-gate
strictness. Rollback is a file-level revert of the listed source/test files and
bridge addendum changes. The bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and command evidence above.
2. Include the corrected adapter addendum report in HYG-039 verification.
3. Return `VERIFIED` if this report satisfies FAB-10, otherwise return `NO-GO` with concrete findings.
