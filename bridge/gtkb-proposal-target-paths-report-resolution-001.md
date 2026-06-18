NEW

# gtkb-proposal-target-paths-report-resolution - Resolve Proposal Target-Paths Preflight Against Proposals Only

bridge_kind: prime_proposal
Document: gtkb-proposal-target-paths-report-resolution
Version: 001
Author: Codex Prime Builder automation
Date: 2026-06-18T09:15:00Z

author_identity: codex/A
author_harness_id: A
author_session_context_id: automation:keep-working:2026-06-18
author_model: GPT-5
author_model_version: 2026-06-18 Codex desktop
author_model_configuration: Prime Builder automation, danger-full-access filesystem, approval-policy never

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4640

target_paths: ["scripts/proposal_target_paths_coverage_preflight.py", "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4640 captures a resolver defect in `scripts/proposal_target_paths_coverage_preflight.py`: when invoked with `--bridge-id`, the tool can select a later `NEW` post-implementation report instead of the operative implementation proposal. In the live `gtkb-target-paths-coverage-preflight` thread this caused the preflight to report missing `target_paths` even though the original proposal contains them.

This proposal authorizes a narrow source/test fix so bridge-id resolution selects implementation proposal/revision files and skips implementation reports. The implementation-start gate remains strict; this change only makes the proposal-target-paths preflight inspect the correct bridge artifact before review/approval.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep fixtures synthetic and avoid credential-shaped examples. | Bridge helper credential scan and focused diff review. | |
| CQ-PATHS-001 | Yes | Mutate only the declared in-root source and test target paths. | Applicability preflight, implementation-start target path packet, and `git diff --name-only -- scripts/proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py`. | |
| CQ-COMPLEXITY-001 | Yes | Keep the resolver change narrow: classify and choose proposal files without redesigning bridge state. | Focused regression for proposal/report chain selection. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing bridge status/kind constants or introduce small local constants if needed. | Ruff and focused tests. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed/out-of-root handling and do not weaken target path authorization. | Existing out-of-root test plus focused regression. | |
| CQ-DOCS-001 | Yes | Limit documentation to bridge proposal/report evidence; no durable rule/doc mutation in this slice. | LO review of proposal and eventual implementation report. | |
| CQ-TESTS-001 | Yes | Add a focused test proving bridge-id resolution skips implementation reports and selects proposal/revision files. | `python -m pytest platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | This read-only preflight emits structured JSON/markdown results and does not write runtime logs. | Existing output assertions remain sufficient. | No logging surface is changed. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, and Ruff format-check before filing the implementation report. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — dispatcher/TAFE state plus numbered bridge files are the bridge workflow authority; the resolver must derive the operative proposal from that chain without treating report files as proposals.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation proposals must carry parseable target paths and verification evidence; this preflight exists to catch under-scoped proposal packets before GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal carries project authorization, project, and work-item metadata so the scoped May29 Hygiene authorization can be validated.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the regression test must prove the resolver selects the proposal artifact needed for spec-derived verification planning rather than a later verification request/report.
- `GOV-STANDING-BACKLOG-001` — WI-4640 is a governed MemBase backlog item under `PROJECT-GTKB-MAY29-HYGIENE`; this proposal advances that canonical work item through bridge review.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the session-discovered defect is preserved as a work item and advanced through an implementation proposal instead of remaining transient chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix keeps bridge proposal, implementation report, test evidence, and resolver behavior aligned as durable lifecycle artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the proposal treats WI-4640 as an unresolved-new defect moving into bridge review without silently changing its lifecycle state.

## Prior Deliberations

- `INTAKE-e7d44d40` — Intake: GO-implementation claims are time-boxed with an owner-extendable deadline to produce the implementation report
- `INTAKE-5a61f299` — Intake: Claim-gated implementation-start: holding the GO-implementation claim is required before editing a GO'd thread's target paths
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` — Owner reconciles duplicate WI-4510 cutover proposals: new canonical, withdraw old
- `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` — Owner gate-1 approval: proceed to file the WI-4510 governed-cutover proposal
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — S382 owner decisions: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS completion scope (Slice 1 + Slice 4)

The first two intake records are relevant because this defect occurs at the boundary between GO authorization, implementation reports, and proposal target-path extraction. The WI4510 cutover records are relevant as dispatcher/TAFE bridge-state context. `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` is relevant because this change hardens the proposal-quality preflight surface created by the proposal-standards work.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-2442` — seed=search; bridge_thread; Loyal Opposition Review - Codex Skill-Loading Failure Cleanup Slice 1
- DA: `DELIB-20263935` — seed=search; bridge_thread; Loyal Opposition Review - Codex Skill-Loading Failure Cleanup Slice 1
- DA: `DELIB-20261443` — seed=search; bridge_thread; Loyal Opposition Verification - GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH Slice 7-prime P
- DA: `DELIB-2595` — seed=search; bridge_thread; Loyal Opposition Verification - GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH Slice 7-prime P
- DA: `DELIB-2246` — seed=search; bridge_thread; Loyal Opposition Review: ChromaDB Vector Continuity v1 Cut Scoping

## Owner Decisions / Input

No new owner decision is required for this proposal. Owner authorization already exists through `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` and active project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, which authorizes proposing implementation for unimplemented May29 Hygiene work items. This proposal does not request formal GOV/SPEC/ADR/DCL mutation, credential action, deployment, destructive cleanup, or production release.

## Requirement Sufficiency

Existing requirements sufficient. WI-4640 states the required behavior: proposal target-paths coverage preflight must resolve implementation proposals/revisions and skip implementation reports when given a bridge id. The linked bridge-governance specifications above are sufficient to constrain the implementation and verification.

## Spec-Derived Verification Plan

Spec-to-test mapping:

```text
GOV-FILE-BRIDGE-AUTHORITY-001
  -> Add/adjust a focused regression in platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py proving bridge-id resolution ignores later implementation-report files and selects the original proposal/revision file.

DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  -> The regression must assert that target_paths are extracted from the proposal file, not from a report that lacks proposal target_paths metadata.

DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
  -> Run bridge applicability preflight and ADR/DCL clause preflight on this proposal before filing; expect no missing required/advisory specs and no blocking gaps.

DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  -> Run the focused pytest module after implementation and report observed pass/fail results in the post-implementation report.

GOV-STANDING-BACKLOG-001
  -> Keep the implementation scoped to WI-4640 and the two target paths named in this proposal.

GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
  -> Preserve the lifecycle trail in this bridge proposal and the eventual implementation report; do not perform untracked KB, GOV, ADR, DCL, or formal artifact mutation.
```

Expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py -q --tb=short
python -m ruff check scripts/proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py
python -m ruff format --check scripts/proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py
```

## Risk / Rollback

Risk is limited to the advisory proposal target-paths coverage preflight. The main behavioral risk is choosing the wrong bridge-chain artifact for unusual thread histories; regression coverage should include at least one proposal -> GO -> NEW report shape so the report is skipped. Rollback is a single commit reverting the source/test changes and leaving prior bridge files intact.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-proposal-target-paths-report-resolution`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: the proposed change repairs incorrect bridge-id resolution in an existing preflight tool and adds regression coverage for that defect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
