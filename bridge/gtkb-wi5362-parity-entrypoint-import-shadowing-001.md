NEW

# WI-5362: Make the Phase-One Parity Entrypoint Resolve Local Generators

bridge_kind: prime_proposal
Document: gtkb-wi5362-parity-entrypoint-import-shadowing
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5362-PARITY-ENTRYPOINT-IMPORT-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5362

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity_entrypoint_import.py"]

implementation_scope: source and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The mandatory Phase 1 command currently crashes before parity evaluation. Direct execution places `E:\GT-KB\scripts` at the front of `sys.path`; `from scripts import ...` then resolves the unrelated `win32.scripts` namespace from site-packages and raises `ImportError`, which the current `ModuleNotFoundError` fallback does not catch. Root-level module import happens to work because the untracked `scripts/__init__.py` candidate changes package resolution, but that file is not an authoritative dependency.

Make generator loading deterministic by bootstrapping the checker's own resolved script directory and importing its sibling generator modules through that explicit local path. Do not catch broad `ImportError`: a real failure inside a local generator must remain visible. Add a new subprocess-focused regression that supplies a conflicting external `scripts` package, proves direct execution reaches parity output, confirms generator provenance is repository-local, and does not depend on `scripts/__init__.py`. Preserve all existing parity evaluation, lifecycle filtering, waiver, and exit-status semantics.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - governs the Phase 1 parity evaluator and requires deterministic, truthful cross-harness parity evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent review before either protected target is changed.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds implementation to the active WI-5362 project authorization and exact proposal paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the requirements that derive its tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the machine-readable PAUTH, project, work-item, and target-path linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the independent verdict to evaluate the mapped direct-entrypoint and parity checks.
- `GOV-STANDING-BACKLOG-001` - governs preservation of the reproduced defect as WI-5362 and linked TEST-11478 before implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the reproduced failure, authorization, proposal, test, and eventual verdict to remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - establishes the artifact-first workflow used to move this defect from evidence through independent verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the concrete parity failure to trigger a work item and governed implementation proposal rather than an untracked repair.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every source, test, draft, and bridge artifact used by this repair to remain within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers for newly reproduced fleet black-box defects while preserving every normal bridge, claim, start, verification, and commit gate.
- `DELIB-S364-SKILL-MODERNIZATION-SLICE-0-PAUTH` - prior checker-and-tests-only scope precedent; this proposal is narrower and does not regenerate adapters or mutate the capability registry.

## Owner Decisions / Input

No new owner decision is required. `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` directly authorizes this bounded defect carrier. PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5362-PARITY-ENTRYPOINT-IMPORT-20260716` allows only bridge, metadata, source, and test work for WI-5362 and forbids dispatcher/runtime mutation, credentials, destructive cleanup, push, deployment, and release.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` requires an executable parity evaluator; the bridge and project-authorization requirements fully govern the implementation workflow. This repair changes module resolution only and does not introduce a new parity policy or harness lifecycle rule.

## Spec-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `python scripts/check_harness_parity.py --all --markdown` | Reaches the parity report with no `win32.scripts` provenance and no import traceback; the command's eventual parity status remains data-driven. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, TEST-11478 | `python -m pytest platform_tests/scripts/test_check_harness_parity_entrypoint_import.py -q --tb=short` | Conflicting external `scripts` package cannot shadow local generators; local module provenance and genuine import-failure visibility pass. |
| Regression preservation | `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py -q --tb=short` | Existing checker and generator behavior remains green. |
| Phase parity integration | `python scripts/harness_parity_phase2.py --project-root . --format markdown` and `python scripts/parity_discovery_diff.py --project-root . --markdown` | Both later parity phases execute with their existing semantics after the Phase 1 import repair. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | applicability preflight, clause preflight, live claim, implementation-start packet, and exact target validation after GO | Every governance gate passes before protected mutation. |
| Source quality | repo-venv Ruff check/format on both target paths plus `git diff --check -- <two targets>` | No lint, format, or whitespace errors. |

## Risk / Rollback

The main risk is changing import precedence for the three adapter-generator modules. The implementation must add only the checker's resolved script directory, must verify each generator's local provenance, and must allow internal generator import errors to propagate. Rollback is a single focused revert of the checker bootstrap and its new focused test after normal bridge authorization; no registry, adapter, dispatcher, TAFE, or runtime state is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5362-parity-entrypoint-import-shadowing`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix`: the focused commit restores the mandatory parity command's direct-entrypoint behavior and adds its regression test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
