NEW

# Implementation Proposal - AI-Assisted Delivery Maturity Model Scoping (GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL)

bridge_kind: implementation_proposal
Document: gtkb-ai-assisted-delivery-maturity-model-scoping
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-METHODOLOGY-AI-MATURITY-METHODOLOGY-AI-MATURITY-BATCH
Project: PROJECT-GTKB-METHODOLOGY-AI-MATURITY
Work Item: GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL

target_paths: ["docs/ai-assisted-delivery-maturity-model.md", "groundtruth-kb/src/groundtruth_kb/maturity/model.py", "tests/maturity/test_maturity_model.py"]

This NEW scoping proposal initializes implementation of `GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL`. Per WI description, owner asked LO to formalize a revised Claude Code maturity-model discussion (advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md`). The proposed model reframes maturity as layered delivery capability: prompting, project memory, task processing, etc.

## Claim

Three-part scoping: (1) author a methodology document codifying the layered model; (2) build a self-assessment module that maps a project's current GT-KB usage to a maturity layer; (3) defer deeper implementation (adopter-side advice, scoring rubrics) to follow-on slices.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - methodology framing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-15 UTC, S350+: owner approved GTKB-METHODOLOGY-AI-MATURITY authorization including this WI.
- 2026-05-03 S330: original advisory request.

## Requirement Sufficiency

Existing requirements sufficient. Advisory document provides operative content.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-METHODOLOGY-AI-MATURITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (doc) + IP-2 (self-assessment) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Methodology document

`docs/ai-assisted-delivery-maturity-model.md`: codifies the layered model:
- L1 Prompting (ad-hoc agent invocation)
- L2 Project Memory (CLAUDE.md, MEMORY.md, persistent state)
- L3 Task Processing (skills, agents, tool integration)
- L4 Governance (bridge, MemBase, approval packets)
- L5 Lifecycle (autonomous project lifecycle, release gates)

Each layer: capability description, evidence patterns, common pitfalls, GT-KB surfaces that support the layer.

### IP-2: Self-assessment module

`groundtruth-kb/src/groundtruth_kb/maturity/model.py`:
- `assess_project_maturity(project_root)` returns a per-layer score (0-1) + dominant-layer estimate.
- Heuristics: presence of CLAUDE.md/MEMORY.md → L2; skills/ → L3; groundtruth.db + bridge/ → L4; release-candidate gate + project authorizations → L5.

### IP-3: Tests

Tests verify scoring heuristics on fixture project states.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Empty project scores L1 dominant | `test_empty_project_l1` |
| CLAUDE.md only scores L2 | `test_claude_md_only_l2` |
| Skills present scores L3 | `test_skills_l3` |
| Bridge + groundtruth.db scores L4 | `test_governance_l4` |
| Project authorizations scores L5 | `test_lifecycle_l5` |
| Score is monotonic with capability | `test_scoring_monotonic` |

Run: `python -m pytest tests/maturity/test_maturity_model.py -v`.

## Acceptance Criteria

- IP-1 doc landed.
- IP-2, IP-3 landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: heuristic scoring oversimplifies. Mitigation: scope is intentionally first-cut; refinement in follow-on slices.
- Rollback: remove docs + module.

## Recommended Commit Type

`feat` - new methodology + assessment surface. ~150 LOC + docs.
