NEW

# WI-4992 Impl-Auth Quarantine Dispatch Suppression Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4992-impl-auth-quarantine-dispatch-suppression
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Extra High reasoning; Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4992-IMPL-AUTH-QUARANTINE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4992

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

---

## Claim

The dispatcher repeatedly offers Prime Builder GO work that the implementation authorization gate deterministically rejects as `impl_auth_quarantined` / `all_impl_auth_quarantined` because the approved proposal says new or revised requirements are required before implementation. This creates repeated dispatch churn and a Prime Builder health failure without producing useful work. The gate is correct; the dispatcher should suppress or back off those structurally unimplementable GO proposals until the bridge thread is revised into an implementable state.

## Defect / Reproduction

Observed during the 2026-07-03 live dispatcher soak:

- `gtkb-role-authority-boundary-scoped-correction` is latest `GO`, but the approved proposal's requirement sufficiency state requires new or revised requirements before implementation.
- `scripts/implementation_authorization.py` correctly refuses implementation with `Approved proposal says new or revised requirements are required before implementation`.
- The dispatcher nonetheless continues selecting the thread for `prime-builder:A`; the latest live report shows `last_result=all_impl_auth_quarantined`, `pending_count=2`, and stale `failure_class=subprocess_execution_failed`, which produces a Prime Builder runtime failure in `gt bridge dispatch health`.
- WI-4992's backlog row records 516 earlier `impl_auth_quarantined` attempts for the same class of defect.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, and `platform_tests/scripts/test_bridge_dispatch_config.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended dispatch must suppress deterministic non-work loops and avoid repeatedly offering work that cannot start.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher runtime is the governed control plane for bridge work routing; no direct harness workaround is authorized.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge statuses and requirement-sufficiency outcomes must control what Prime Builder may implement.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation authorization gate refusals must remain authoritative and not be bypassed.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH/project/WI metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete links to all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map linked requirements to executed verification.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended headless bridge processing and authorized governed stability WIs under dispatcher modernization.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner prohibited direct harness-to-harness standby/fallback. This proposal keeps suppression inside dispatcher control.
- `DELIB-202665265` - earlier owner authorization evidence for creating necessary WIs and fixing bridge stability defects discovered during the live soak.
- `bridge/gtkb-role-authority-boundary-scoped-correction-002.md` - example GO thread whose requirement sufficiency prevents implementation.
- `bridge/gtkb-wi4977-headless-dispatch-stability-008.md` - earlier verified dispatch stability work; WI-4992 addresses a remaining Prime-side churn mode.

## Owner Decisions / Input

- Owner goal: enable stable unattended headless bridge processing with Codex as PB and Claude/Ollama as LO.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` records owner authority to create governed WIs and bounded authorizations needed to stabilize unattended headless dispatch.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4992-IMPL-AUTH-QUARANTINE` authorizes only bridge, dispatcher runtime/health source, and focused tests for WI-4992. It forbids direct harness-to-harness launch, credential changes, production deployment, durable role reassignment beyond A/B/D, and retired poller restoration.

## Requirement Sufficiency

Existing requirements are sufficient. The dispatcher already has an implementation authorization gate that identifies this condition deterministically. The missing behavior is to feed that deterministic refusal back into dispatchability/backoff/health so the same structurally unimplementable thread is not retried indefinitely.

## Proposed Scope

- Detect deterministic `impl_auth_quarantined` / `all_impl_auth_quarantined` outcomes for Prime Builder selected work.
- Suppress, back off, or classify as non-dispatchable any GO proposal whose approved proposal explicitly requires new or revised requirements before implementation.
- Preserve implementation-start authorization enforcement; do not allow such proposals to proceed to source/config/test mutation.
- Preserve genuine PB dispatch for implementable GO/NO-GO work in the same batch.
- Ensure dispatch health does not report repeated deterministic impl-auth quarantine as a current subprocess failure when no worker was launched.
- Record enough state/reporting detail for operators to see which thread was quarantined and why.

## Out of Scope

- Revising `gtkb-role-authority-boundary-scoped-correction` requirements.
- Bypassing or weakening the implementation authorization gate.
- Direct harness launch or fallback behavior.
- Changing model pins, dispatcher topology, or LO selection.
- General bridge requirement-sufficiency redesign beyond the deterministic quarantine path.

## Specification-Derived Verification Plan

| Specification / Requirement | Planned Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add/extend tests proving deterministic impl-auth quarantine does not produce repeated live spawn attempts or health failures, while implementable PB work still dispatches. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Assert the repair remains in dispatcher runtime/daemon/health code and does not add direct harness launch. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Test that requirement-sufficiency blockers preserve bridge state and prevent implementation until a revised proposal changes the condition. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Test that implementation authorization refusals remain authoritative and are not bypassed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal/report carry PAUTH/project/WI metadata, target paths, and complete spec links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must include exact command evidence and this mapping before VERIFIED. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
python -m ruff check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py
python -m ruff format --check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py
```

## Acceptance Criteria

- A GO proposal whose requirement sufficiency requires new or revised requirements before implementation is not repeatedly dispatched to PB implementation.
- The implementation authorization gate still denies protected mutation for that proposal class.
- Implementable PB items in the same selection can still proceed.
- `gt bridge dispatch health --json` no longer reports Prime Builder subprocess failure solely because all selected items were deterministically impl-auth quarantined before worker launch.
- Operators can see the quarantined slug/reason in dispatcher state or health/report output.
- Focused pytest, ruff check, and ruff format-check commands pass.

## Risks / Rollback

Risk: over-broad suppression could hide implementable GO work. Mitigation: scope suppression to deterministic impl-auth quarantine reasons from the existing authorization gate, and test mixed batches.

Risk: suppressing retries could leave requirement-capture work invisible. Mitigation: keep the thread visible as blocked/non-dispatchable and require revision before implementation.

Rollback: revert the WI-4992 source/test changes. Bridge files, PAUTH, and MemBase rows remain append-only audit records.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Recommended Commit Type

`fix`
