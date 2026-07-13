NEW

# WI-5220 - Restore dispatcher test fixtures to current role and lifetime contracts

bridge_kind: prime_proposal
Document: gtkb-wi5220-dispatcher-test-fixture-parity
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-13 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5220-DISPATCHER-TEST-FIXTURES-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5220

target_paths: ["platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Broad WI-5217 verification exposed at least five pre-existing dispatcher-suite
failures. Synthetic daemon registries omit canonical `can_receive_dispatch`,
claim fixtures forge worker session IDs without required role envelopes,
lifetime assertions retain retired 3,600/5,400-second expectations instead of
the preserved 29,400-second floor, and an isolated lease test depends on module
visibility established accidentally by earlier tests.

Correct only the two test modules so they exercise current production
contracts independently and together. No dispatcher or harness production
source, registry, routing, role, model, eligibility, or allowance changes.

## Specification Links

- `DCL-DISPATCH-ENVELOPE-RULES-001` - fixtures must preserve the 29,400-second worker and 29,700-second lease contracts.
- `GOV-SESSION-ROLE-AUTHORITY-001` - synthetic dispatch claims require valid worker-session role provenance.
- `DCL-SESSION-ROLE-RESOLUTION-001` - fixture claims must resolve through the same durable session authority as production.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - receive-capable fixture targets must declare canonical dispatchability.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - broad parity verification depends on deterministic isolated test execution.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the test correction follows the governed bridge lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - current contracts are linked before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, WI, PAUTH, and targets are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must run both modules alone and together.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - baseline failures are tracked rather than normalized as noise.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - test evidence remains linked to WI, TEST, PAUTH, and bridge artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - reproducible stale-suite failures trigger a governed regression correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both targets remain in the GT-KB test tree.

## Prior Deliberations

- `DELIB-202666173` - correct every discovered six-harness proof/parity defect while preserving generous allowances.
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-008.md` - VERIFIED authority for the current generous provider ceilings that stale tests must not lower.
- `INTAKE-c5792b0c` - dispatcher coordination tests must reflect the governed role/claim lifecycle rather than bypassing it.

## Owner Decisions / Input

- `DELIB-202666173` supplies owner authority for discovered proof and parity defects.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5220-DISPATCHER-TEST-FIXTURES-20260712` permits only these two test paths and the governed bridge chain.

## Requirement Sufficiency

Existing requirements sufficient - canonical dispatchability, role-envelope
authority, isolated test determinism, and generous lifetime requirements are
already specified and implemented in production.

## Proposed Scope

- Add canonical receive capability to synthetic active dispatcher targets that are expected to launch.
- Establish valid in-root worker session envelopes before acquiring synthetic Prime claims.
- Replace stale 3,600/5,400-second expectations with assertions that preserve the 29,400-second floor and do not use a lower env override as a valid case.
- Make isolated bridge-lease imports deterministic without depending on test order.
- Run the full modules alone and together, then correct any additional fixture-only drift found in the same two paths.
- Do not change production source or reduce any runtime allowance.

## Spec-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| Canonical receive capability | Live daemon fixture tests | Expected synthetic target reaches the mocked spawn path. |
| Role/session authority | Prime claim/fanout fixture tests | Claims acquire only after a valid worker envelope and reconcile normally. |
| Generous lifetime contract | Runtime and daemon lifetime tests | 29,400-second floor remains authoritative; no lower allowance is encoded. |
| Isolated determinism | Run each module in a fresh pytest process | No import-order dependency or missing canonical module. |
| Combined behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` | Both modules pass together. |
| Style | Ruff check/format on both targets | Clean. |

## Acceptance Criteria

- Both test modules pass alone and together from a fresh process.
- Synthetic launch rows use canonical `can_receive_dispatch` rather than legacy aliases.
- Synthetic claim sessions carry accepted worker role provenance.
- Lifetime tests preserve 29,400 seconds and never normalize a lower ceiling.
- No production path changes and no foreign test hunks are claimed.
- WI-5217 test hunks in the shared runtime test remain excluded until that thread is independently finalized.

## Risk / Rollback

The risk is weakening tests to fit current output. Every correction must instead
construct the canonical prerequisite and retain the original behavioral
assertion. Rollback reverts the test-only focused commit; production is untouched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5220-dispatcher-test-fixture-parity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - repairs stale fixtures and assertions without changing runtime behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
