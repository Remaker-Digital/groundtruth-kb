NEW

# GT-KB WI-5142 Hygiene Reclaim CLI And Managed Skill - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5142-hygiene-reclaim-cli-skill-phase1
Version: 003
Responds to GO: bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-phase1-002.md
Approved proposal: bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-phase1-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5142
Recommended commit type: feat(hygiene):
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-16T01-48-03Z-prime-builder-A-b8e790
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex interactive Prime Builder; reasoning effort xhigh; approval policy never

## Implementation Claim

Implemented the approved non-database child in its authorized target set:

- added the production `gt hygiene reclaim plan|history|trash|restore` command family;
- added deterministic registry and Git-root preservation evidence, immutable plan/item hashes, bounded output, per-run manifests, validated summaries, append-only hash-chained events, compact history, exact-item revalidation, actuator locking, no-overwrite same-volume moves, and reversible restore;
- replaced inventory refresh's permissive duplicate parser with the typed SoT loader and lifecycle/path-class expansion, including zero recursive expansion of generated runtime directories;
- added the canonical `gtkb-hygiene-reclaim` skill, generated Codex adapter, manifest entry, capability-registry declaration, and focused tests.

The child did not mutate `config/registry/sot-artifacts.toml` or `groundtruth.db`. It performed no live trash, restore, Git metadata mutation, permanent deletion, commit, push, release, or deployment.

All implementation outputs, generated skill artifacts, runtime ledgers, and this numbered bridge report remain in-root under `E:/GT-KB`; no external path is a live dependency or output authority.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `SPEC-INTAKE-97538b`
- `SPEC-INTAKE-99a602`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-1853`
- `ADR-REGISTRY-DISCOVERY-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-SKILL-USAGE-ROUTER-001`
- `GOV-10`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

The implementation carries forward the owner's urgent direction to investigate, implement, test, and execute a repeatable deterministic hygiene capability. No new owner decision is required to verify this non-live implementation child. Any exact live trash batch remains separately owner- and bridge-gated.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER`
- `DELIB-202666274`
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY`
- `INTAKE-eb0bbcad` / `SPEC-INTAKE-97538b`
- `INTAKE-b44907bd` / `SPEC-INTAKE-99a602`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-001.md` through `-004.md`
- `bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-phase1-001.md` and `-002.md`

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001`, `SPEC-INTAKE-97538b`, `SPEC-INTAKE-99a602` | Core disposable-repository tests exercise report-first planning, registry/tracked/Git-root vetoes, exact evidence, changed-candidate refusal, no-overwrite restore, and zero physical-byte claims. | PASS |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Inventory tests exercise typed full-schema loading, active blockers, lifecycle/path classes, and generated-directory non-recursion. Live `gt registry validate --json` reports 47 TOML and 47 projection records with zero divergence. | PASS |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Core tests exercise stable plan/item hashes, immutable summary validation, event tamper/truncation detection, compact history, run-level refusal history, operation locking, and trash/restore receipts. | PASS |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Tests preserve ambiguous Git temporary/malformed objects and fail closed on registry projection drift, corrupt/partial ledgers, symlink destinations when supported, changed paths, collisions, and incomplete evidence. | PASS |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Existing strays detector and finalization-triage suites remain green. | PASS |
| Artifact-oriented governance specifications | Per-run manifest/summary/events preserve the plan and exact state transitions; the live read-only run is recorded under `.gtkb-state/hygiene-reclaim/runs/`. | PASS |
| `SPEC-1853`, `ADR-REGISTRY-DISCOVERY-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Skill/catalog tests prove canonical identity, generated adapter/manifest SHA agreement, capability-registry declaration, role scope, and explicit unsupported harness dispositions. | PASS |
| `SPEC-SKILL-USAGE-ROUTER-001`, `GOV-10` | Skill tests require production `gt hygiene reclaim` commands, reject a duplicate private CLI, and leave the scenario router untouched. | PASS |
| Bridge and verification specifications | Exact child proposal, independent GO, active claim, implementation authorization, executed evidence, and this report preserve the governed lifecycle. | PASS |
| `GOV-STANDING-BACKLOG-001` | Work remains under WI-5142 and creates no competing backlog authority. | PASS |

## Commands Run And Observed Results

- `python -m pytest groundtruth-kb/tests/test_hygiene_reclaim.py platform_tests/scripts/test_hygiene_reclaim_cli.py -q --tb=short` - 19 passed, 1 skipped because directory symlink creation is unavailable on this Windows runtime.
- `python -m pytest groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py -q --tb=short` - 13 passed.
- `python -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short` - 44 passed.
- `python -m pytest platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py platform_tests/skills/test_skill_catalog_contract.py -q --tb=short` - 13 passed.
- `python -m ruff check <eight changed Python targets>` - all checks passed.
- `python -m ruff format --check <eight changed Python targets>` - all files formatted.
- `python -m groundtruth_kb.cli registry validate --json` - in sync; 47 TOML records, 47 projection records, no missing records or field divergences.
- `python scripts/generate_codex_skill_adapters.py --check` - the new hygiene adapter, manifest entry, and registry SHA are clean; the check reports only two pre-existing unrelated drifts under `.codex/skills/verify/helpers/`, which this child did not alter.
- `git diff --check -- <authorized implementation paths>` - passed.

## Live Read-Only Evidence

`gt hygiene reclaim plan --json` wrote run `20260716T044319673156Z-c8c8128c25d0` with plan hash `sha256:c8c8128c25d0ecd551c29cb0f6419c22a15f3851db269d887230eb9bf917ec38`.

- Candidate count: 12,024.
- Logical bytes: 184,178,005,135.
- Candidate classes: 8,851 aged unreachable loose objects (184,094,163,563 bytes), 3,172 stale harness-scratch files (83,830,195 bytes), and one stale draft (11,377 bytes).
- Readiness: `executable=false`.
- Blockers: 46 missing reflog-root objects, one out-of-root stale worktree record, and the known active alias-registry path defect.
- Preservation observations: 32,338 age vetoes, 36 ambiguous Git temporary objects, 295 ambiguous scratch paths, and 142 registry vetoes.
- `gt hygiene reclaim history --run-id ... --json`: integrity valid, non-partial, 12,024 planned items, zero refusal or actuator events.
- Live bytes moved: 0. Physical bytes reclaimed: 0.

This is the required fail-closed result. Registry correction, Git-metadata repair, and any exact trash batch remain outside this child's GO.

## Files Changed

- `.claude/skills/gtkb-hygiene-reclaim/SKILL.md`
- `.codex/skills/gtkb-hygiene-reclaim/SKILL.md`
- `.codex/skills/MANIFEST.json` (hygiene entry only; unrelated dirty entries preserved)
- `config/agent-control/harness-capability-registry.toml` (hygiene block only; unrelated staged changes preserved)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (reclaim command and inventory summary hunks only; unrelated staged hunk preserved)
- `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py`
- `groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py`
- `groundtruth-kb/tests/test_hygiene_reclaim.py`
- `groundtruth-kb/tests/test_inventory_string_scan.py`
- `platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py`
- `platform_tests/scripts/test_hygiene_reclaim_cli.py`
- `platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py`

## Acceptance Status

PASS for all six child acceptance criteria. The command family is available and bounded; planning audits registry/projection/Git roots and fails closed; inventory refresh is typed and generated-tree-safe; managed-skill surfaces agree; focused regressions/lint/format pass; and no unauthorized live mutation occurred.

## Residual Risk And Rollback

- Same-volume reversible trash reclaims zero physical bytes until a separately governed permanent disposition exists.
- Opaque owner/apply and quiescence evidence references are recorded by the CLI; governance must validate that those artifacts bind the exact run, plan hash, and item IDs before invoking a live actuator.
- The live Git recovery graph is currently non-passing because stale reflog/worktree metadata references missing or out-of-root state. No unreachable Git object may be moved until that evidence is repaired and a fresh plan passes.
- Rollback only the exact hunks and new paths listed above, regenerate only the hygiene Codex adapter/manifest record, and rerun the focused suites.

## Recommended Commit Type

`feat(hygiene):`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
