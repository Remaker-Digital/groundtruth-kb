NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop Prime Builder interactive session

# GT-KB Bridge Implementation Proposal - gtkb-wi4886-mock-worker-load-scale-harness - 001

bridge_kind: prime_proposal
Document: gtkb-wi4886-mock-worker-load-scale-harness
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4886
Recommended commit type: test:

target_paths: ["scripts/ops/dispatch_load_harness.py", "platform_tests/scripts/test_dispatch_load_harness.py"]

implementation_scope: source_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Implement WI-4886 by adding a deterministic STUB-worker load/scale harness for dispatcher-resilience testing.

The harness will model fleet saturation without real harness/provider calls:

- two Prime Builder worker slots
- four Loyal Opposition worker slots
- N synthetic bridge work units
- deterministic claim/lease acquisition and release
- deterministic worker completion, hang, crash, and reap outcomes
- JSON report output suitable for later Phase 5/6 reuse

This proposal does not activate Antigravity, does not change dispatcher topology, does not start the live daemon, does not spawn real harnesses, and does not mutate dispatcher configuration or MemBase.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specifications and design constraints.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to the linked requirements.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected script/test implementation requires a live bridge `GO`, a work-intent claim, and an implementation-start packet.
- `GOV-STANDING-BACKLOG-001` - WI-4886 is the MemBase-backed backlog item selected under `PROJECT-GTKB-DISPATCHER-RELIABILITY`.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the resilience addendum requires deterministic STUB load/chaos verification and defines fleet saturation as two PB plus four LO workers.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher selection and audit behavior must remain centralized and deterministic.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - recovery tests must prefer deterministic STUB workers for load and chaos cases and must cover harness saturation without spending provider calls.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - the harness must not move control-plane behavior into real harnesses or provider-specific workers.

## Requirement Sufficiency

Existing requirements are sufficient for this implementation slice.

WI-4886 is explicitly scoped by `DELIB-20266276` and the active daemon-resilience PAUTH. `ADR-DISPATCHER-ARCHITECTURE-001` v2 and `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` now provide the exact test-shape requirement: use deterministic STUB workers for load/chaos and reserve real harnesses for limited smoke checks. No new owner decision is needed for a temp-root, source/test-only STUB load harness.

Implementation should remain conditional on the WI-4884 Phase 0 formalization thread not being rejected. If Loyal Opposition returns a `NO-GO` on `bridge/gtkb-wi4884-daemon-resilience-formalization-011.md` that materially changes the DCL text, this proposal should be revised before implementation starts.

## Target Paths

The implementation is limited to:

- `scripts/ops/dispatch_load_harness.py`
- `platform_tests/scripts/test_dispatch_load_harness.py`

No configuration, harness registry, bridge runtime state, live dispatcher state, formal artifact, MemBase, credential, deployment, or generated adapter files are in scope.

## Implementation Plan

1. Add `scripts/ops/dispatch_load_harness.py`.
2. Model synthetic work with explicit work IDs, role labels, claim owner, lifecycle state, and final outcome.
3. Provide a pure scheduler that starts no more than the configured per-role cap, defaults to PB cap 2 and LO cap 4, and records the maximum concurrent count per role.
4. Ensure each synthetic work unit can be claimed by at most one worker and that all claims are released, completed, or reaped by the end of a run.
5. Include deterministic scenarios for successful completion, worker hang reaping, worker crash reaping, and saturation/backpressure.
6. Expose a small CLI with `--work-items`, `--pb-cap`, `--lo-cap`, `--scenario`, and `--json`, all operating in memory or under pytest temp roots only.
7. Add focused tests in `platform_tests/scripts/test_dispatch_load_harness.py`.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not read, print, embed, or require credentials; keep the harness in memory/temp-root only. | Bridge helper credential scan, focused test review, and no credential/environment access in target diff. | |
| CQ-PATHS-001 | Yes | Limit implementation to `scripts/ops/dispatch_load_harness.py` and `platform_tests/scripts/test_dispatch_load_harness.py`. | Implementation-start target validation, `git diff --name-only`, and bridge applicability preflight. | |
| CQ-COMPLEXITY-001 | Yes | Keep scheduler behavior factored into pure dataclass-backed functions with bounded branching per scenario. | Ruff check plus focused test review of pure scheduler entrypoints. | |
| CQ-CONSTANTS-001 | Yes | Name fleet caps and outcome tokens as module constants or enums; comment any tuned value whose source is not cited by a linked spec. | Ruff check and test assertions for default PB cap 2 and LO cap 4. | |
| CQ-SECURITY-001 | Yes | Do not spawn subprocesses, invoke real harnesses, mutate live dispatcher state, or consume provider credentials. | `test_load_harness_does_not_spawn_real_harnesses` plus target diff review for subprocess/live-state calls. | |
| CQ-DOCS-001 | Yes | Provide concise module/CLI help describing STUB-only behavior and JSON report fields. | CLI `--help` assertion or direct parser/help test in `test_dispatch_load_harness.py`. | |
| CQ-TESTS-001 | Yes | Add deterministic tests for caps, single-claim ownership, hang/crash reaping, JSON report shape, and no real subprocess use. | `python -m pytest platform_tests/scripts/test_dispatch_load_harness.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | The harness emits structured JSON reports rather than logging. | Target diff review confirms no new logging behavior. | No runtime logging surface is added. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge applicability preflight, and ADR/DCL clause preflight before reporting implementation. | Command output included in the post-implementation report. | |

## Out Of Scope

- Real harness invocation.
- Real provider calls.
- Live daemon start, stop, restart, or substrate flip.
- Dispatcher topology changes.
- Antigravity activation.
- Claude token-outage rollback.
- Phase 5 chaos/fault-injection recovery implementation.
- Phase 6 sustained real-harness go-live acceptance.
- MemBase or formal artifact mutation.

## Owner Decisions / Input

No new owner input is requested.

Relevant existing decisions:

- `DELIB-20266276` - daemon-resilience program scope lock.
- `DELIB-20266354` - owner approval of the Phase 0 formal-artifact bodies that define the STUB load/chaos verification posture.

## Prior Deliberations

- `DELIB-20266276` - selected fleet-saturation load target, full auto-recovery, and STUB load/chaos with real smoke only.
- `DELIB-20266354` - approved the Phase 0 ADR/DCL content now recorded in MemBase.
- `bridge/gtkb-wi4884-daemon-resilience-formalization-011.md` - latest WI-4884 implementation report awaiting Loyal Opposition verification.

## Spec-Derived Verification Plan

- `ADR-DISPATCHER-ARCHITECTURE-001`: `test_fleet_saturation_caps_pb_and_lo_workers` proves the harness saturates at PB cap 2 and LO cap 4 without exceeding either cap.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: `test_each_synthetic_item_claimed_once` proves work selection/claim ownership remains centralized in the harness scheduler and no item is double-claimed.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001`: `test_hung_and_crashed_workers_are_reaped` proves deterministic STUB hangs/crashes are recorded and reaped without provider calls.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`: `test_load_harness_does_not_spawn_real_harnesses` proves the harness does not call `subprocess.Popen`, `subprocess.run`, or the real trigger spawn path.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the post-implementation report must include the exact test command output for `platform_tests/scripts/test_dispatch_load_harness.py`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: before implementation, Prime Builder must acquire a work-intent claim and create an implementation-start packet from the live latest `GO`; protected target validation must pass for both target paths.

## Verification Commands

```powershell
python -m pytest platform_tests/scripts/test_dispatch_load_harness.py -q --tb=short
python -m ruff check scripts/ops/dispatch_load_harness.py platform_tests/scripts/test_dispatch_load_harness.py
python -m ruff format --check scripts/ops/dispatch_load_harness.py platform_tests/scripts/test_dispatch_load_harness.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4886-mock-worker-load-scale-harness
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4886-mock-worker-load-scale-harness
```

## Acceptance Criteria

- The harness reports PB cap 2 and LO cap 4 as the default fleet-saturation target.
- A synthetic load run never exceeds the configured cap for either role.
- No synthetic bridge work unit is double-claimed.
- Hung and crashed STUB workers are represented as deterministic outcomes and reaped by the harness.
- The harness emits machine-readable JSON with submitted, completed, reaped, failed, duplicate-claim count, leaked-claim count, and max-concurrency-by-role fields.
- Tests prove no real harness/provider subprocess is invoked.
- The implementation stays within the two target paths.

## Risk And Rollback

Risk is low because the slice adds a deterministic source/test harness without live dispatcher state mutation. The main risk is overfitting a model that does not resemble the daemon enough to be useful for Phase 5/6. Mitigation: keep the harness role/cap/claim/output vocabulary aligned with dispatcher concepts and make the JSON report reusable by later phases.

Rollback is deletion of the new script and test file before VERIFIED. After VERIFIED, any retirement or replacement should go through a follow-up bridge thread so Phase 5/6 references remain auditable.
