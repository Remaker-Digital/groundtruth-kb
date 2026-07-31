REVISED

# WI-4979 Work-Tree Hygiene Slice E - Auto-Resolve Actuator

bridge_kind: prime_proposal
Document: gtkb-wi4979-worktree-hygiene-auto-resolve-actuator
Version: 003
Author: Prime Builder (Codex A)
Date: 2026-07-05 UTC
Responds to: bridge/gtkb-wi4979-worktree-hygiene-auto-resolve-actuator-002.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-05T20-48-37Z-prime-builder-A-ebf9fd
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless dispatcher-spawned Prime Builder; resolved_role=prime-builder; approval_policy=never; sandbox=workspace-write

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4979-BATCH-A1-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4979

target_paths: ["scripts/hygiene/stray_detector.py", "scripts/worktree_finalization_triage.py", "groundtruth-kb/src/groundtruth_kb/hygiene/strays.py", "groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/auto_finalize_sweep.py", "platform_tests/scripts/test_work_tree_stray_detector.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_work_tree_hygiene_doctor.py", "platform_tests/scripts/test_worktree_finalization_triage.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py"]

implementation_scope: source/test/cli/hook-adjacent automation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4979 implements the missing Slice E actuator layer for already-verified work-tree hygiene surfaces. Slices A-C can detect stale tracked edits, untracked files, stashes, and orphaned worktrees, and expose those findings through `gt hygiene strays` and doctor visibility. WI-5027 has also been VERIFIED and committed as `89c08ebc`, adding `scripts/worktree_finalization_triage.py`, a read-only dirty-worktree candidate-action planner.

This revised proposal answers the Loyal Opposition NO-GO in `bridge/gtkb-wi4979-worktree-hygiene-auto-resolve-actuator-002.md` by making WI-5027 the classification substrate for Slice E. WI-4979 must not create an independent second dirty-worktree classifier or a second forbidden-operation list. Instead, it should extend, import, or refactor the WI-5027 planner so there is one canonical dirty-state planning engine and one canonical forbidden-operation source of truth. WI-4979 then adds the actuator/apply-guard framework, CLI/doctor reporting integration, and cheap-gated Stop-hook report-only consultation on top.

The implementation remains report-only by default. Applying cleanup to live stale files, dropping stashes, pruning worktrees, deleting untracked files, broad status mutation, or committing another session's stale work remains forbidden unless a later batch supplies item-specific apply evidence.

## Relationship to WI-5027

WI-5027 is no longer an unverified dependency. Fresh source-of-truth reads in this dispatch show:

- `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5027` reports Stage `resolved` and Resolution Status `resolved`.
- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5027-worktree-finalization-triage --json --compact` reports latest status `VERIFIED` at `bridge/gtkb-wi5027-worktree-finalization-triage-004.md`.
- `git show --stat --oneline 89c08ebc` shows the VERIFIED commit `feat(hygiene): WI-5027 read-only worktree finalization triage planner (VERIFIED)`.

Slice E should therefore build on the verified WI-5027 planner rather than avoiding it. The implementation may choose the least disruptive consolidation path:

1. Import and extend `scripts/worktree_finalization_triage.py` directly where that preserves the existing verified behavior.
2. Or move reusable classification primitives into `groundtruth_kb.hygiene.auto_resolve` / adjacent package code while keeping `scripts/worktree_finalization_triage.py` as a thin compatibility entrypoint.

Either path must preserve a single canonical `FORBIDDEN_OPERATIONS` source. Tests must fail if WI-4979 introduces a divergent duplicate forbidden-operation tuple or a second dirty-state classifier vocabulary for the same domain.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - governs stale worktree/stash detection, preservation boundaries, fresh runtime reads, non-mutating defaults, and evidence-first remediation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, review, implementation report, and verification must flow through the append-only bridge chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A1 PAUTH is bounded and does not bypass bridge GO or implementation-start scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - owner/project authorization is not direct implementation permission.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specs and constrains target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable PAUTH/project/work-item metadata is present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map each work-tree hygiene behavior to executed tests.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision evidence is carried forward through PAUTH and no new AUQ is required for this narrower implementation-design correction.
- `GOV-STANDING-BACKLOG-001` - WI-4979 is a MemBase backlog item and must reach terminal state through evidence, not drift out of view.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - stale-work classification and dependency analysis must derive from fresh git/registry reads, not cached summaries.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - repetitive stale-work triage belongs in deterministic services when it can be made bounded and auditable.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook-adjacent integration must preserve Codex/Claude Stop-hook parity where the existing sweep is already registered.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - target paths under `groundtruth-kb/src/groundtruth_kb/project/**` remain GT-KB platform root-boundary work and must not blur into Agent Red application surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the action planner should preserve traceability across findings, evidence, candidate actions, tests, reports, and bridge verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - action plans, skip reasons, and apply-evidence requirements must be durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale workspace state is a lifecycle trigger for explicit candidate action rather than invisible accumulation.

## Prior Deliberations

- `DELIB-20260867` - owner authorization for WI-4356 recurring work-tree hygiene and the twelve-hour stale-work threshold.
- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` - owner approved Batch A1, including WI-4979, under explicit forbidden operations.
- `bridge/gtkb-work-tree-hygiene-mechanism-scoping-003.md` - scoping capstone that identified Slice E as the missing recurring actuator layer.
- `bridge/gtkb-work-tree-hygiene-slice-a-detector-004.md` - VERIFIED detector slice for stale workspace/stash/worktree classification.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` - VERIFIED `gt hygiene strays` read-only CLI surface.
- `bridge/gtkb-work-tree-hygiene-slice-c-doctor-check-004.md` - VERIFIED doctor visibility for stale work-tree findings.
- `bridge/gtkb-wi4889-auto-finalization-sweep-004.md` and `.claude/rules/auto-finalization-sweep.md` - existing cheap-gated Stop-hook finalizer used as the integration precedent.
- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - VERIFIED WI-5027 report whose committed planner (`89c08ebc`) is now the required consolidation substrate.

Deliberation Archive searches performed during this revision:

- `gt deliberations search "WI-4979 work-tree hygiene auto-resolve actuator WI-5027 worktree finalization triage planner" --limit 10` - no additional matches.
- `gt deliberations search "GOV-WORK-TREE-HYGIENE-001 auto-resolve triage safe-commit auto-ignore auto-drop" --limit 10` - no additional matches.

## Owner Decisions / Input

No new owner decision is required for this revised proposal.

The NO-GO asked whether Slice E should build on WI-5027 or remain a separate lineage. This revision selects the narrower, lower-risk, Loyal Opposition-preferred path: build on WI-5027 so there is one classifier and one forbidden-operation source. That is an implementation-design correction within the existing Batch A1 authorization, not a new owner requirement or approval boundary.

Carried-forward authorization:

- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` / `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4979-BATCH-A1-20260705` authorize this WI through the normal bridge process.
- The PAUTH explicitly forbids credential lifecycle, deploy, force-push, secret disclosure, destructive bulk cleanup, broad bulk status mutation, stash drop, branch/worktree prune, untracked file deletion, and committing another session's stale work without specific apply evidence. This proposal preserves those limits.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirement set is `GOV-WORK-TREE-HYGIENE-001`, the verified Slice A-C bridge chain, the VERIFIED WI-5027 planner chain, WI-4979's backlog text, and the Batch A1 PAUTH. No new GOV/ADR/DCL/SPEC mutation is proposed in this slice.

## Findings Addressed

### P1 - Duplicated worktree-triage classifier

Resolved by making WI-5027 the explicit classification substrate for WI-4979. The implementation must either import/extend the verified `scripts/worktree_finalization_triage.py` planner or refactor its reusable primitives into the package layer while keeping a compatibility script entrypoint. It must not create a parallel dirty-worktree classifier or a second forbidden-operation list.

### P2 - Stale WI-5027 verification premise

Resolved by refreshing the dependency state. WI-5027 is resolved, VERIFIED, and committed at `89c08ebc`. The Prior Deliberations section now cites `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` instead of describing WI-5027 as awaiting verification.

### P3 - Cross-harness Stop-hook parity and cheap-gate ordering

Accepted as a verification strengthening. The implementation test plan now requires `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` to prove the planner is consulted only after the existing cheap gate, remains report-only, stages no source/test paths, and fails soft so the Stop hook exits 0 on planner errors.

## Scope Changes From Version 001

- Added `scripts/worktree_finalization_triage.py` and `platform_tests/scripts/test_worktree_finalization_triage.py` to `target_paths` so implementation may safely consolidate on the verified WI-5027 planner without stepping outside proposal scope.
- Added the `Relationship to WI-5027` section.
- Corrected the stale WI-5027 state in Prior Deliberations.
- Added verification for a single canonical forbidden-operation source and no divergent duplicate classifier.

No new destructive apply behavior, owner approval dependency, KB mutation, deployment, credential operation, or broad cleanup authority is introduced.

## Spec-Derived Verification Plan

| Governing surface | Required implementation behavior | Verification |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Findings classify into deterministic candidate actions with evidence requirements and manual-review fallback while preserving report-only defaults. | Extend `platform_tests/scripts/test_work_tree_stray_detector.py`, `platform_tests/scripts/test_hygiene_strays_cli.py`, and/or `platform_tests/scripts/test_worktree_finalization_triage.py` for action taxonomy, registered-artifact preservation, active-session skip, stale tracked/untracked/stash/worktree paths, and byte-identical auto-drop planning without deletion. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | CLI planning derives from fresh git status/stash/worktree/registry reads and the verified WI-5027 planner chain, not stale proposal text. | Assert output records fresh source commands and run `groundtruth-kb/.venv/Scripts/gt.exe hygiene strays --format json` after implementation. |
| Batch A1 forbidden operations and PAUTH limits | No destructive cleanup runs by default; apply mode requires explicit item-level evidence and refuses forbidden categories. | Add focused tests for `groundtruth_kb.hygiene.auto_resolve` / the WI-5027 planner integration proving no `unlink`, `stash drop`, `worktree prune`, broad commit, or untracked deletion occurs without evidence. |
| Single-classifier consolidation from the NO-GO | There is one dirty-state classification substrate and one canonical forbidden-operation list shared by WI-5027 and WI-4979. | Add a regression test that imports the planner/action layer from both surfaces and fails if `FORBIDDEN_OPERATIONS` or candidate-action vocabularies diverge. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Existing Stop-hook sweep remains cheap-gated and fail-soft while consulting the planner in report-only mode. | Extend `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` to assert planner invocation only after the cheap gate, no source/test staging, no harness-registration divergence, and exit 0 on planner failure. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries command evidence and spec-to-test mapping. | Post-implementation report must include exact pytest, ruff lint, and ruff format results for changed Python files. |

Minimum verification commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests\scripts\test_work_tree_stray_detector.py platform_tests\scripts\test_hygiene_strays_cli.py platform_tests\scripts\test_work_tree_hygiene_doctor.py platform_tests\scripts\test_worktree_finalization_triage.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts\hygiene\stray_detector.py scripts\worktree_finalization_triage.py groundtruth-kb\src\groundtruth_kb\hygiene\strays.py groundtruth-kb\src\groundtruth_kb\hygiene\auto_resolve.py groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\project\doctor.py scripts\auto_finalize_sweep.py platform_tests\scripts\test_work_tree_stray_detector.py platform_tests\scripts\test_hygiene_strays_cli.py platform_tests\scripts\test_work_tree_hygiene_doctor.py platform_tests\scripts\test_worktree_finalization_triage.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts\hygiene\stray_detector.py scripts\worktree_finalization_triage.py groundtruth-kb\src\groundtruth_kb\hygiene\strays.py groundtruth-kb\src\groundtruth_kb\hygiene\auto_resolve.py groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\project\doctor.py scripts\auto_finalize_sweep.py platform_tests\scripts\test_work_tree_stray_detector.py platform_tests\scripts\test_hygiene_strays_cli.py platform_tests\scripts\test_work_tree_hygiene_doctor.py platform_tests\scripts\test_worktree_finalization_triage.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py
groundtruth-kb/.venv/Scripts/gt.exe hygiene strays --format json
```

## Pre-Filing Preflight Subsection

Candidate preflights were run on this completed content before live filing and will be repeated by `.codex/skills/bridge/helpers/revise_bridge.py file` before publication.

### Applicability Preflight

- packet_hash: `sha256:9899c86e56c7f1943f7d3820f83cabcf842511c170ccb53995bc67e457a6f1ba`
- bridge_document_name: `gtkb-wi4979-worktree-hygiene-auto-resolve-actuator`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-wi4979-worktree-hygiene-auto-resolve-actuator-003.md`
- operative_file: `bridge/gtkb-wi4979-worktree-hygiene-auto-resolve-actuator-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: harvested
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

### Clause Applicability

- Bridge id: `gtkb-wi4979-worktree-hygiene-auto-resolve-actuator`
- Operative file: `.gtkb-state\bridge-revisions\drafts\gtkb-wi4979-worktree-hygiene-auto-resolve-actuator-003.md`
- Clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | n/a | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | n/a | blocking | blocking |

## Risk / Rollback

Risk is moderate because this work is adjacent to files, stashes, worktrees, commits, and hooks. The revised plan lowers risk by consolidating on the already-verified WI-5027 read-only planner instead of creating a second governance-load-bearing classifier.

The first implementation remains report-only by default and must fail closed on ambiguous action evidence. The apply surface may be implemented only as a guarded refusal/allowlist framework in this slice; actual live destructive cleanup remains out of scope.

Rollback is a single revert of the implementation commit. Since bridge files are append-only, rollback should leave this proposal and any implementation report in place and file a corrective bridge follow-up if Loyal Opposition identifies an unsafe action path.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4979-worktree-hygiene-auto-resolve-actuator`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` because the change adds a deterministic work-tree hygiene action-planning and guarded actuator capability while extending existing CLI/reporting behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
