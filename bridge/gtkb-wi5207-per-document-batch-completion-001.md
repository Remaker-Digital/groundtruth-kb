NEW

# WI-5207 - Require completion evidence for every selected document

bridge_kind: prime_proposal
Document: gtkb-wi5207-per-document-batch-completion
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-12 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5207-BATCH-COMPLETION-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5207

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: dispatcher completion reconciliation, health classification, and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Dispatcher run `2026-07-12T01-21-34Z-loyal-opposition-B-211d49` selected two LO documents. B wrote a `GO` for the primary WI-5203 thread, explicitly declined any verdict on the second latest `NO-ACTION` thread, then exited 0 claiming both entries were handled. Current completion reconciliation searches for a verdict only on the primary bridge id. One verdict can therefore mark a multi-document batch successful, retain every selected document signature, release all leases, and suppress the unhandled document.

This proposal requires per-selected-document completion evidence. Every selected `NEW`, `REVISED`, or `NO-ACTION` document must advance after launch to a role-correct verdict. A partial batch records `selected_documents_incomplete` plus exact missing document ids, preserves completed-document signatures, clears only incomplete-document signatures/reoffer state, and releases all leases. Single-document behavior and fully completed batches remain compatible. The change does not reduce model time/turn budgets or alter status semantics.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — requires truthful dispatcher-produced lifecycle outcomes and deterministic retry/recovery state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — defines role-correct status transitions whose per-document evidence is the completion authority.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — requires a corrected LO verdict for selected latest `NO-ACTION`; no-verdict cannot count as completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete governing links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the project, work item, and PAUTH metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent partial/full/single-batch evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5207 and TEST-11361 preserve the demonstrated false-success defect.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — keeps dispatch telemetry, batch selection, missing verdict, work item, test, proposal, report, and verdict traceable.

## Prior Deliberations

- `DELIB-202666173` — directs genuine six-harness proof and correction of every defect discovered.
- `INTAKE-a815f782` — established per-document suppression/lease granularity; WI-5207 extends the same granularity to completion evidence and reoffer.
- `INTAKE-fd012ad6` — supports inspection-backed operational evidence; run `211d49` is the concrete after-action packet for this defect.
- `WI-5205` — owns the separate NO-ACTION consumer semantics drift. WI-5207 remains necessary for any multi-document batch where one selected entry is skipped for any reason.

## Owner Decisions / Input

Mike explicitly directed correction of every defect found during genuine A/B/C/D/F/H proof, recorded as `DELIB-202666173`. The bounded implementation authorization is `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5207-BATCH-COMPLETION-20260711`.

## Requirement Sufficiency

Existing requirements are sufficient. The centralized dispatcher specification requires truthful lifecycle outcomes, the bridge/DCL records define role-correct per-document completion, and the verification/backlog controls define evidence and approval.

## Spec-Derived Verification Plan

1. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: a two-document LO batch with a verdict only for the primary is `selected_documents_incomplete`; evidence lists the missing id, preserves the completed signature, clears only the missing signature/reoffer record, and releases all leases.
2. Fully completed two-document batches succeed and retain both signatures; single-document verdict and no-verdict behavior remains compatible.
3. `DCL-NO-ACTION-STATUS-SEMANTICS-001`: selected `NO-ACTION` without corrected `GO`/`NO-GO` is incomplete even if another selected document has a verdict.
4. Health/report classification surfaces the partial-batch reason deterministically without converting it to generic provider failure.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
```

Expected result: focused tests and quality checks pass; no selected document is suppressed merely because a sibling received a verdict.

## Risk / Rollback

The risk is clearing a completed document's signature or reoffering a document whose verdict arrived just after process exit. Completion checks use launch timestamp/version boundaries and compute all selected outcomes before one atomic state write; race and mixed-status fixtures are mandatory. WI-5205 completes first because both proposals touch dispatcher runtime/config tests. Rollback is one focused commit and restores prior batch semantics without changing bridge files or telemetry history.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5207-per-document-batch-completion`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects false success and suppressed work in multi-document dispatch completion.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
