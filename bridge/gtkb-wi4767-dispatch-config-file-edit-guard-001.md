NEW

# Implementation Proposal - WI-4767 dispatcher config file-edit guard

bridge_kind: prime_proposal
Document: gtkb-wi4767-dispatch-config-file-edit-guard
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef3a8-fefa-7382-a13c-c93e5ee51026
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive session; approval_policy=never; sandbox=danger-full-access; resolved Prime Builder by owner init keyword ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4767
Project: PROJECT-GTKB-DISPATCHER-CONTROL-CLI
Work Item: WI-4767

target_paths: ["scripts/implementation_start_gate.py", "scripts/protected_mutation_guard.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protected_mutation_guard.py", "groundtruth-kb/tests/test_doctor.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4767 by mechanically blocking direct file edits to `config/dispatcher/rules.toml` through the shared protected-mutation preflight path, while preserving the governed `gt bridge dispatch config ...` transaction commands from WI-4766 as the allowed mutation surface.

The implementation will add an explicit dispatcher-config direct-edit denial reason to the active implementation-start gate and to the legacy protected-mutation decision helper so both enforcement surfaces agree. It will also add a bridge-profile doctor check that verifies the guard is present and registered for mutation hooks, and that the CLI transaction surface exists as the sanctioned path for dispatcher config changes.

This proposal does not authorize editing the live `config/dispatcher/rules.toml`. Tests must use temporary project roots or synthetic hook payloads and prove direct Write/Edit/apply_patch/shell-path mutations are blocked even when a GO packet would otherwise authorize the file.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires dispatcher reporting and configuration control under the governed `gt bridge dispatch` CLI and skill surface.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - requires dispatcher configuration mutation to occur through governed CLI transactions and prohibits raw direct file edits.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge files and role-specific status tokens are the canonical proposal, review, report, and verification chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH bounds implementation authority for the selected project/work item.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - active PAUTH and proposal scope must cite the governing specifications.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge `GO`, target paths, implementation-start packet, implementation report, or Loyal Opposition verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves owner decision, requirement, DCL, project, WI, proposal, report, verification, and audit evidence as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links governing specs and maps implementation tests to those specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must carry this spec-to-test mapping forward and report executed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this implementation proposal includes PAUTH, project, work item, and inline JSON `target_paths`.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner approval evidence comes from AUQ-backed owner decision `DELIB-20265795`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation artifacts and tests must stay under `E:\GT-KB`; tests should use temp project roots.
- `GOV-STANDING-BACKLOG-001` - WI-4767 is the MemBase work item authority for this slice.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use helper-mediated bridge filing and explicit fallback checks when hook parity matters.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - direct dispatcher config edits are replaced by deterministic CLI transactions with audit evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner requirement, implementation plan, test mapping, report, and verification remain lifecycle-visible.

## Prior Deliberations

- `DELIB-20265795` - owner AUQ-backed decision requiring a dispatcher reporting/configuration control surface under `gt bridge dispatch`.
- `DELIB-20265540` - prior NO-GO showing dispatcher config mutation must be covered by cited authorization; relevant because this WI prevents future file-edit bypasses.
- `DELIB-20265490` - WI-4700 harness metadata freshness guard precedent; relevant because it added a dispatcher-related doctor check to surface stale operational control-plane assumptions.
- `bridge/gtkb-wi4765-dispatch-report-cli-001.md` through `bridge/gtkb-wi4765-dispatch-report-cli-004.md` - predecessor project slice implementing and verifying the dispatcher reporting surface.
- `bridge/gtkb-wi4766-dispatch-config-transactions-001.md` through `bridge/gtkb-wi4766-dispatch-config-transactions-004.md` - predecessor project slice implementing and verifying the governed config transaction surface that this WI protects as the exclusive mutation path.

DA/search context reviewed before proposal drafting:

```text
gt bridge propose --kind implementation --wi WI-4767 --slug gtkb-wi4767-dispatch-config-file-edit-guard --target-path ...
python -m groundtruth_kb.cli projects show PROJECT-GTKB-DISPATCHER-CONTROL-CLI --json
```

The scaffold and project state surfaced the same owner decision, DCL, and predecessor dispatcher-control workstream. A duplicate-thread check was run before helper filing:

```text
python -m groundtruth_kb.cli bridge threads --wi WI-4767 --json
```

Result: exit 0; `match_count: 0`; `threads: []`. The command reports its normal caveat that only threads with Work Item metadata are found by WI id; predecessor dispatcher-control threads were also reviewed while drafting.

## Owner Decisions / Input

- `DELIB-20265795` - owner AUQ-backed decision requiring the dispatcher control/reporting surface.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4767` - active project authorization for WI-4767, allowing `source`, `test_addition`, and `config` while forbidding production deployment and credential lifecycle work.

No new owner decision is required before implementation because WI-4767 is directly inside the captured dispatcher-control project and has a bounded PAUTH derived from `DELIB-20265795`.

## Requirement Sufficiency

Existing requirements sufficient.

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` specifies the dispatcher reporting/configuration control surface under `gt bridge dispatch`.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` specifies the direct-file-edit prohibition and the requirement for governed CLI transactions.
- `DELIB-20265795` is the AUQ-backed owner decision that created this workstream.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4767` is active and bounds this WI to guard/doctor source and tests, while forbidding production deployment and credential lifecycle work.

## Proposed Scope

In scope:

- Add an explicit direct-edit prohibition for `config/dispatcher/rules.toml` in `scripts/implementation_start_gate.py` before normal GO packet target authorization can allow the file.
- Add the same explicit prohibition/reason code to `scripts/protected_mutation_guard.py` so the shared protected-target taxonomy and legacy decision helper agree.
- Preserve the governed CLI transaction commands from WI-4766 as the allowed path; do not block `gt bridge dispatch config ...` transaction execution.
- Add focused tests proving direct `apply_patch`, Write/Edit-style payloads, and shell commands targeting `config/dispatcher/rules.toml` are blocked.
- Add focused tests proving the lower-level protected-mutation helper reports the dispatcher-config CLI-only denial.
- Add a bridge-profile doctor check verifying:
  - the implementation-start gate carries the dispatcher-config CLI-only denial;
  - the protected-mutation helper carries the same denial reason;
  - Claude and Codex tracked hooks register the implementation-start gate on mutation surfaces;
  - the WI-4766 dispatcher config transaction module exists with the sanctioned transaction helper functions.

Out of scope:

- No edit to the live `config/dispatcher/rules.toml`.
- No new dispatcher config transaction commands beyond WI-4766.
- No live-state reconciliation between `rules.toml` and the harness registry; that is WI-4768.
- No dispatcher-control skill work; that is WI-4769.
- No dispatcher scheduling, ranking, runtime worker, provider retry, circuit-breaker, bridge queue, or harness registry role behavior change.
- No credential lifecycle, production deployment, force-push, or external service action.

## Spec-Derived Verification Plan

| Specification / requirement | Proposed verification |
| --- | --- |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` direct file-edit prohibition | Add implementation-start gate tests proving `apply_patch` and direct shell-path writes to `config/dispatcher/rules.toml` block with a dispatcher-config CLI-only reason even when ordinary protected-path authorization would otherwise apply. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` shared guard consistency | Add protected-mutation helper tests proving direct dispatcher config targets return a stable `dispatcher_config_cli_only` denial reason. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` governed CLI mutation surface | Add doctor tests proving the bridge-profile doctor check passes only when the guard markers, hook registrations, and WI-4766 transaction helper surface are present. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` dispatcher control surface | Doctor check must report that dispatcher config mutation is governed by `gt bridge dispatch config` transactions, not raw file edits. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This proposal carries PAUTH, project, work item, and inline JSON `target_paths` metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal links governing specs and maps tests back to the linked requirements. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must carry this mapping forward and include executed pytest, ruff check, and ruff format evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests use pytest temp roots/synthetic payloads and all implementation target paths remain under `E:\GT-KB`. |

Required verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py groundtruth-kb/tests/test_doctor.py -q --tb=short
python -m ruff check scripts/implementation_start_gate.py scripts/protected_mutation_guard.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py groundtruth-kb/tests/test_doctor.py
python -m ruff format --check scripts/implementation_start_gate.py scripts/protected_mutation_guard.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py groundtruth-kb/tests/test_doctor.py
```

## Pre-Filing Preflight

Applicability preflight run before filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4767-dispatch-config-file-edit-guard-001.md --bridge-id gtkb-wi4767-dispatch-config-file-edit-guard
```

Observed result: exit 0; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; packet hash `sha256:e4c99796422ac0d6c8d236ac5cc8fd56f18417e2a9e4f0680a1e8288e3d28f8b`.

Clause preflight run before filing:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4767-dispatch-config-file-edit-guard-001.md --bridge-id gtkb-wi4767-dispatch-config-file-edit-guard
```

Observed result: exit 0; clauses evaluated: 5; must_apply: 4; may_apply: 1; evidence gaps in must_apply clauses: 0; blocking gaps: 0.

## Risk / Rollback

Primary risk: over-broad command classification could block legitimate `gt bridge dispatch config ...` transaction invocations. The implementation must preserve CLI transaction execution by blocking only direct path-bearing file writes to `config/dispatcher/rules.toml`.

Secondary risk: too-narrow command classification could allow a shell command that directly rewrites `rules.toml`. The implementation must cover the path-extraction cases already recognized by the implementation-start gate and explicitly fail closed when that path is present.

Rollback: remove the dispatcher-config special-case denial, remove the doctor check, and remove the focused tests. No live dispatcher config migration is proposed or required by this implementation.

## Bridge Filing

This proposal will be filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4767-dispatch-config-file-edit-guard`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `feat:`. The implementation adds guard and doctor enforcement around the governed dispatcher configuration transaction surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
