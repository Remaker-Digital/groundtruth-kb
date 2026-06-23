NEW

# WI-4403 Advisory Router Compact Skipped-Existing Test

bridge_kind: prime_proposal
Document: gtkb-wi4403-advisory-router-compact-skipped-existing-test
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ef218-0e11-7133-939d-e1d62c0025f0
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; owner-declared Prime Builder role via `::init gtkb pb`

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-LO-ADVISORY-ROUTING
Work Item: WI-4403

target_paths: ["platform_tests/scripts/test_advisory_backlog_router.py"]

implementation_scope: test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal adds focused regression coverage for WI-4403, "Compact Summary Router Mode." The live router already exposes `--compact` and `RouterResult.as_json(compact=True)`, but the current focused test only proves that compact mode omits `staged` and reports staged/expired counts. WI-4403 specifically calls out suppressing `skipped_existing` items from JSON output, so this slice adds a test that exercises the skipped-existing/idempotent path and asserts compact JSON contains `skipped_existing_count` without the full `skipped_existing` list.

No source behavior, MemBase row, project membership, bridge dispatch rule, hook registration, or generated artifact changes are in scope. This is a test-only verification slice that creates project-scoped evidence for the authorized LO Advisory Routing project without expanding the owner's snapshot-bound authorization.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — implementation work proceeds only through the file bridge, with this `NEW` proposal awaiting Loyal Opposition review before any test edit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal links the governing backlog, project-authorization, bridge, and verification requirements that constrain the test-only change.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the required `Project Authorization`, `Project`, and `Work Item` headers are present for implementation-targeting bridge work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must map the added test assertion to WI-4403 and execute the focused test evidence before verification.
- `GOV-STANDING-BACKLOG-001` — WI-4403 is the governed work item; this slice preserves backlog/project authority and does not add new WIs to the snapshot-bound project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — owner authorization `PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23` permits bounded implementation for WI-4403 under allowed mutation class `test_addition`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the only target path is under `E:\GT-KB`; no Agent Red or out-of-root surface is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — prior advisory findings and the work item are preserved as durable bridge/test evidence instead of chat-only disposition.

## Prior Deliberations

- `DELIB-20261059` — Deep Scan Log and Backlog Gap Review identified verbose advisory-router skipped-existing output and recommended compact dry-run output under the LO advisory project family.
- `DELIB-20261060` and `DELIB-20261061` — follow-up deep-scan capture/delta reviews repeated that advisory-route debt and verbose router output were legitimate backlog gaps.
- `DELIB-20262490` — Stage 3 advisory-router approval-staged intake verification confirmed the router candidate path and existing focused router test surface.
- `bridge/gtkb-fable-investigation-advisory-001.md` — Fable Investigation advisory lists WI-4403 as overlap under FAB-21 startup/load-cost reduction.
- `bridge/gtkb-platform-observability-hygiene-003.md` / `-008.md` and commit `e387b67c8` — existing implementation history introduced compact router behavior and test coverage, but not project-scoped VERIFIED evidence for WI-4403.

## Owner Decisions / Input

This proposal depends on the owner project authorization recorded as `PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23`, backed by owner decision `DELIB-20265586` on 2026-06-23. The authorization is snapshot-bound to the 19 current open member WIs, includes WI-4403, and permits `test_addition`. No new owner decision is required because this proposal does not add a work item, broaden project scope, change source behavior, mutate formal artifacts, or exceed the allowed mutation classes.

## Requirement Sufficiency

Existing requirements sufficient. WI-4403 states the required behavior: compact summary mode should suppress `skipped_existing` items from JSON output and optimize token consumption for recurring runs. The current project authorization covers the work item, and the existing router API already exposes the behavior. This slice only adds missing focused test evidence for the skipped-existing compact-output branch.

## Spec-Derived Verification Plan

| Linked specification / rule | Verification command or evidence | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4403-advisory-router-compact-skipped-existing-test --format json --preview-lines 80` after filing | Thread exists as append-only bridge state and awaits LO review. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4403-advisory-router-compact-skipped-existing-test` | `preflight_passed: true`, no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / WI-4403 | Add a focused assertion in `platform_tests/scripts/test_advisory_backlog_router.py` proving compact JSON omits `skipped_existing` and reports `skipped_existing_count` for an idempotent rerun. Then run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_advisory_backlog_router.py -q --tb=short`. | Focused test passes and maps directly to WI-4403. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet after GO: `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4403-advisory-router-compact-skipped-existing-test` | Packet authorizes only `platform_tests/scripts/test_advisory_backlog_router.py`. |
| Python code-quality gate | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_advisory_backlog_router.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_advisory_backlog_router.py` | Lint and format checks pass separately. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path inspection plus clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4403-advisory-router-compact-skipped-existing-test` | In-root target path and zero blocking gaps. |

Focused verification command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_advisory_backlog_router.py -q --tb=short
```

## Risk / Rollback

Risk is low and limited to test expectations around the existing compact JSON contract. If the test reveals the implementation does not suppress `skipped_existing`, Prime Builder will either adjust the source in a revised GO scope or file a narrow follow-up source proposal; this proposal itself authorizes only the test path. Rollback is a single test-file revert before commit if the assertion is wrong or too brittle.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4403-advisory-router-compact-skipped-existing-test`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test:` — the implementation changes only focused regression coverage for an existing CLI/API behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
