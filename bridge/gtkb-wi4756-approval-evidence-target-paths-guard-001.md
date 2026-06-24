NEW

# gtkb-wi4756-approval-evidence-target-paths-guard — Approval-Evidence Target Paths Guard

bridge_kind: prime_proposal
Document: gtkb-wi4756-approval-evidence-target-paths-guard
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef21d-a27e-7473-9939-21f715631a90
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop session; resolved_role=prime-builder; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4756

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py"]

implementation_scope: hook_upgrade, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add a bridge-compliance checkpoint that catches implementation proposals whose prose puts formal artifact approval evidence, narrative-artifact approval evidence, or approval-packet paths in scope while `target_paths` omits the concrete evidence packet path or `.groundtruth/formal-artifact-approvals/**` envelope. `WI-4756` captures a repeated review defect where proposals scoped governed spec/version work or approval-evidence work but listed only source/test targets, leaving implementation-start and review surfaces with an incomplete target envelope.

This is a narrow hook upgrade, not a new governance artifact. It extends the existing `target_paths` completeness family beside the current KB/MemBase mutation checkpoint, mirrors the live hook into the scaffold template, and adds focused live/template tests so future bridge proposals surface the missing evidence path before Loyal Opposition review.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals must carry concrete implementation-start metadata, including `target_paths`, and the numbered bridge file chain is the workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites the governing bridge/proposal specifications and maps them to tests before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this implementation proposal includes Project Authorization, Project, and Work Item metadata for the authorized May29 hygiene scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must carry forward this spec-to-test mapping and executed focused tests before verification.
- `GOV-STANDING-BACKLOG-001` — the work item is MemBase backlog work and project progress must remain traceable to the governed backlog/project state.
- `GOV-ARTIFACT-APPROVAL-001` — proposals that place formal artifact approval evidence in scope must not omit the approval-packet path evidence from their implementation target envelope.
- `PB-ARTIFACT-APPROVAL-001` — Prime Builder formal artifact work remains governed by owner-visible approval evidence and must be represented in the bridge scope when it is part of implementation.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — hook-enforced approval evidence is a governing implementation constraint when formal-artifact packet work is proposed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — proposal-quality defects involving owner decisions, requirements, work items, and governed artifacts must be preserved and corrected through durable artifacts rather than session-only notes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the implementation turns a repeated review finding into hook behavior and regression tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the target-path checkpoint protects lifecycle evidence for formal/narrative approval packets when proposal content triggers that artifact lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are in-root GT-KB hook/template/test files under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20265586` — owner decision authorizing the snapshot-bound May29 hygiene implementation envelope that includes `WI-4756`.
- `DELIB-20265493`, `DELIB-20261706`, and `DELIB-2285` — prior Loyal Opposition evidence named by `WI-4756` as repeated examples of the same target-envelope / approval-evidence omission class.
- `bridge/gtkb-wi4683-activity-vocabulary-reconcile-ops-003.md` — immediate source review called out by `WI-4756`; the proposed guard prevents similar proposals from silently under-declaring governed evidence paths.
- `INTAKE-67f93676` — relevant intake history for owner-gated specification creation and enforced spec-test-implementation coupling.
- `INTAKE-5a61f299` — relevant intake history for implementation-start target-path claim discipline.

## Owner Decisions / Input

- Project authorization: `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Owner decision: `DELIB-20265586`, authorizing the snapshot-bound 14-current-open-member-WI May29 hygiene implementation envelope.
- No new owner decision is required for this proposal because it stays within the PAUTH mutation classes (`hook_upgrade`, `test_addition`) and does not mutate GOV/SPEC/ADR/DCL/PB/REQ records or approval packets.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already requires concrete implementation-start metadata, `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` already govern approval evidence, and `WI-4756` supplies the concrete defect class. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Specification / Constraint | Planned verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Add focused hook tests proving proposals that declare formal/narrative approval-packet evidence but omit the packet path receive a bridge target-path checkpoint, while proposals with `.groundtruth/formal-artifact-approvals/...` or the approvals directory in `target_paths` pass. | PASS |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Same focused tests use formal-artifact and narrative-artifact approval-packet language and verify the concrete evidence path is required only when approval evidence is in implementation scope. | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Same focused tests convert the durable WI/review finding into repeatable hook behavior; implementation report cites the lifecycle/evidence trigger coverage. | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability and clause preflights on this proposal before filing; carry the linked specs forward in the implementation report. | `missing_required_specs: []`; no blocking clause gaps |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance gate validates the PAUTH/project/WI metadata and live project membership during filing. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps each linked spec to executed tests and reports observed results. | PASS |
| `GOV-STANDING-BACKLOG-001` | Implementation remains tied to `WI-4756` and does not create or mutate unrelated backlog/project items. | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths remain under `E:\GT-KB`. | PASS |

Planned command set:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py -q --tb=short
python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py
python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py
```

## Risk / Rollback

Risk: an over-broad text trigger could checkpoint proposals that only discuss approval evidence historically. Mitigation: require implementation-scope language (`formal-artifact approval`, `narrative-artifact approval`, `approval packet`, or `.groundtruth/formal-artifact-approvals`) without a clear no-mutation/no-approval-evidence negation, and add negative tests for explanatory-only mentions.

Risk: live/template hook drift. Mitigation: update both the live hook and scaffold template, and keep the existing live/template parametrized tests.

Rollback: revert the hook/template/test changes from the implementation commit. Bridge files remain append-only; no MemBase or formal artifact mutation is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4756-approval-evidence-target-paths-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: repairs a repeated proposal-quality governance defect by extending an existing bridge-compliance checkpoint and adding focused regression coverage.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
