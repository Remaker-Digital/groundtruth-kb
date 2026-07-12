NEW

# WI-5206 - Dedicated minimal fast-wrapup path

bridge_kind: prime_proposal
Document: gtkb-wi5206-fast-wrapup-minimal-path
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-12 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5206-FAST-WRAPUP-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5206

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: startup/wrap-up source and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`session_self_initialization.py --emit-wrapup --fast-hook` still calls the full startup/dashboard model builder, writes dashboard data and history, and generates both startup and wrap-up reports before emitting the compact wrap-up notice. The notice itself consumes only five metric groups plus top actions. In a warm uncontended diagnostic this path takes about 4.7 seconds, but during genuine H review contention it exceeded the registered 15-second Stop-hook allowance and contributed to outcome masking tracked separately by WI-5204.

This rollback-safe performance slice adds a dedicated fast-wrapup collector that computes only the fields consumed by `render_wrapup_notice`, writes the required wrap-up report, and bypasses unrelated dashboard/startup generation, reachability, compilation, and PDF work. Ordinary startup, ordinary non-fast wrap-up, dashboard generation, and the generous 60-second Stop allowance proposed by WI-5204 remain unchanged. Timing acceptance uses cold/contention fixtures against that 60-second allowance; it does not reintroduce impatience-based micro-budgets.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — owns startup/wrap-up model collection, generated reports, fast-hook behavior, and noninteractive lifecycle surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the append-only proposal, verdict, report, and verification chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete links to the governing startup requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the project, work item, and PAUTH metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent functional and timing evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5206 and TEST-11360 preserve the performance defect independently from WI-5204 correctness work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — requires the observed H evidence, separate rollback slice, test, proposal, report, and verdict to remain traceable.

## Prior Deliberations

- `DELIB-202666173` — directs genuine six-harness proof and correction of every discovered defect with generous evidence-based allowances.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` — rejects declaring slow models failed from short timers; this slice removes unnecessary work while retaining a generous 60-second hook allowance.
- `WI-5204` / `TEST-11358` — own event-specific Stop correctness and the 60-second registration. WI-5206 deliberately does not change Stop semantics, making rollback independent.

## Owner Decisions / Input

Mike explicitly directed genuine governed proof for all six harnesses and correction of every defect discovered, recorded as `DELIB-202666173`. The bounded implementation authorization is `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5206-FAST-WRAPUP-20260711`.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` owns the generated lifecycle surface, and the bridge/verification/backlog requirements define the approval and evidence boundaries. The owner instruction fixes the timing policy: retain generous bounds and optimize actual work from evidence.

## Spec-Derived Verification Plan

1. `GOV-SESSION-SELF-INITIALIZATION-001`: tests prove `--emit-wrapup --fast-hook` calls the minimal collector, does not call the full startup/dashboard builder or PDF/reachability/compilation paths, and writes/emits the expected wrap-up fields.
2. The same tests prove ordinary startup and non-fast wrap-up still use the existing full path and preserve their output contract.
3. A cold fixture and controlled contention fixture complete the fast path within the 60-second lifecycle allowance; elapsed evidence is reported without introducing a tighter production timer.
4. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: an independent LO harness runs the focused suite and quality checks before VERIFIED.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
```

Expected result: focused tests and quality checks pass; fast wrap-up avoids the full model and stays within 60 seconds under controlled cold/contention evidence; ordinary behavior is unchanged.

## Risk / Rollback

The risk is omitting a field consumed by the wrap-up renderer or accidentally routing ordinary startup through the reduced model. The collector has an explicit renderer-field contract and tests both branch selection and output equivalence. Rollback is one focused commit and may restore extra latency without changing WI-5204 Stop correctness or the 60-second allowance.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5206-fast-wrapup-minimal-path`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - removes unnecessary work from an existing fast-hook path while preserving behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
