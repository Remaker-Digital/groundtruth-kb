NEW

# WI-4994 Prime Builder Fan-Out Dispatcher Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4994-prime-builder-fanout-dispatcher
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Extra High reasoning; Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4994-PB-FANOUT
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4994

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/bridge_dispatch_concurrency.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py"]

---

## Claim

Headless worker spawning is available through the governed dispatcher path, but Prime Builder work is not yet parallelized in a reliable, bounded way. Live dispatcher evidence on 2026-07-03 shows one Codex PB worker and one Ollama LO worker can run concurrently, yet additional PB opportunities are suppressed behind single-recipient work-intent/signature state instead of being admitted through the existing role-aware Prime Builder capacity.

Implement dispatcher-managed PB fan-out so separate unheld Prime Builder-actionable bridge threads can spawn independent Codex headless workers up to the role-aware Prime Builder capacity, while preserving work-intent exclusion, direct-harness-launch prohibition, model pins, and the current A/B/D topology.

## Defect / Reproduction

Observed during the 2026-07-03 bridge stability soak:

- `gt bridge dispatch report --json` showed a live Codex PB worker: `2026-07-03T10-11-51Z-prime-builder-A-4a4cc1`.
- After another PB candidate became available, `prime-builder:A` remained at one live PB worker and reported `last_result="unchanged"` or `work_intent_already_held` instead of launching an independent second PB worker.
- The dispatcher has `scripts/bridge_dispatch_concurrency.py` with role defaults `prime-builder: 2` and `loyal-opposition: 3`, but the module header states live dispatch wiring was deferred.
- `scripts/gtkb_dispatcher_daemon.py` currently filters held PB work, recomputes one selected-batch signature, and compares it with `last_dispatched_signature` for the single recipient lane. That is useful dedupe, but it does not provide independent PB worker slots for independent unheld documents.

This is not a request to directly spawn Codex from this interactive session. The defect is that the dispatcher does not yet convert available PB role capacity into independent dispatcher-owned PB workers.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_dispatcher_daemon.py`, `scripts/dispatcher_runtime.py`, `scripts/bridge_dispatch_concurrency.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`, and `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires stable unattended dispatcher processing; PB fan-out is part of stable headless processing when multiple independent PB items are available.
- `ADR-DISPATCHER-ARCHITECTURE-001` - governs the dispatcher as the control-plane path for cross-harness work and excludes ad hoc direct harness launch.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct append-only bridge state and work-intent discipline for implementation/report transitions.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded project implementation authorization before protected dispatcher source/test mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH/project/WI metadata and target paths in this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete links to all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation verification to map each linked requirement to executed evidence.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatcher prompts and spawned workers must retain the approved dispatch envelope and role boundaries.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended headless bridge processing with Codex A as PB and Claude/Ollama as LO, and authorized governed stability WIs under the dispatcher-modernization project.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner prohibited direct harness-to-harness standby/fallback. This proposal keeps all spawning inside the dispatcher.
- `DELIB-202665265` - earlier bridge-stability authorization evidence for creating necessary WIs and fixing stability defects discovered during the live soak.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` - verified direct harness launch guard, which this proposal preserves.
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-003.md` - contemporaneous Codex hook fix report; it does not address PB fan-out.

## Owner Decisions / Input

- Owner directive, 2026-07-03: "Can you spawn headless workers and parallelize the PB work?"
- Owner directive, 2026-07-03: direct harness-to-harness interaction is prohibited and must be mechanically enforced.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` records owner authority to create governed WIs and bounded authorizations needed to stabilize unattended headless dispatch.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4994-PB-FANOUT` authorizes only bridge, dispatcher runtime/source, and focused tests for WI-4994. It forbids direct harness-to-harness launch, credential changes, production deployment, durable role reassignment beyond A/B/D, and retired poller restoration.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and `ADR-DISPATCHER-ARCHITECTURE-001` already require dispatcher-governed stable headless processing; `scripts/bridge_dispatch_concurrency.py` already records the intended per-role capacity shape with Prime Builder default 2. This proposal asks to wire that existing concept into the live daemon path with tests, not to establish a new product requirement.

## Proposed Scope

- Wire dispatcher-managed role-aware worker capacity into the live daemon spawn path for Prime Builder work.
- Permit independent PB workers only for separate, unheld Prime Builder-actionable bridge documents and only through dispatcher-owned spawning.
- Preserve the work-intent registry as the per-document mutual exclusion mechanism; held PB documents must continue to be filtered.
- Preserve same-signature dedupe for the same document/selection while avoiding suppression of a different unheld document merely because one PB worker is already live.
- Record enough recipient/slot metadata in dispatch state to distinguish multiple PB workers without replacing dispatcher/TAFE bridge authority.
- Keep the active topology unchanged: Codex A remains PB, Claude B and Ollama D remain LO.
- Do not change model pins: Codex PB remains `gpt-5.5` with `model_reasoning_effort="xhigh"`.
- Do not add any interactive or direct harness-to-harness launch path.

## Out of Scope

- Re-enabling disabled harnesses or changing dispatcher eligibility.
- Directly launching Claude, Codex, Ollama, Cursor, Antigravity, or OpenRouter from an interactive harness command.
- Modifying Claude/Ollama model routing or per-model timeout policy.
- Fixing WI-4991 implementation behavior, except as necessary to prove PB fan-out does not collide with work-intent claims.
- Broad dispatcher refactors unrelated to bounded PB fan-out.

## Specification-Derived Verification Plan

| Specification / Requirement | Planned Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add/extend a daemon regression test showing two independent unheld PB bridge items can produce bounded independent Codex PB spawn attempts when PB capacity is available. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `DCL-DISPATCH-ENVELOPE-RULES-001` | Assert spawned PB workers still use dispatcher `_spawn_harness` and the existing Codex headless invocation envelope; no direct harness launch helper is introduced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify held work-intent items remain filtered and unheld items acquire/release claims correctly. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start authorization must cover only WI-4994 target paths before protected mutation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal/report carry PAUTH/project/WI metadata, target paths, and complete spec links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must include exact command evidence and this mapping before VERIFIED. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py -q --tb=short
python -m ruff check scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
python -m ruff format --check scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
```

## Acceptance Criteria

- With two independent unheld PB-actionable bridge threads and Prime Builder capacity greater than one, dispatcher live-spawn logic launches independent Codex PB workers through dispatcher-owned `_spawn_harness`.
- Held PB work-intent items remain excluded and do not cause duplicate implementation claims.
- Same document/signature dedupe still suppresses duplicate dispatch for an already-dispatched item.
- Multiple PB workers are bounded by role-aware capacity and global runaway guards.
- Dispatcher state/reporting can distinguish multiple live PB workers well enough for operators to understand what is running.
- No direct harness-to-harness launch path is added.
- Focused pytest, ruff check, and ruff format-check commands pass.

## Risks / Rollback

Risk: PB fan-out could revive dispatch storms if slot accounting is wrong. Mitigation: wire role-aware capacity, preserve global live-process cap, and test at-cap suppression.

Risk: fan-out could duplicate implementation of the same document. Mitigation: preserve per-document work-intent claims and test held-item filtering.

Risk: recipient-level signature state could become ambiguous with multiple PB workers. Mitigation: keep per-worker/slot metadata and avoid using a single recipient signature as the sole gate for independent documents.

Rollback: revert the WI-4994 changes to dispatcher runtime/daemon/concurrency wiring and tests. Bridge files, PAUTH, and MemBase records remain append-only audit records.

## Files Expected To Change

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/dispatcher_runtime.py`
- `scripts/bridge_dispatch_concurrency.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
- `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`

## Recommended Commit Type

`fix`
