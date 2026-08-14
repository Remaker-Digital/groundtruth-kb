<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project goose`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Loyal Opposition Runbook

Purpose: define how Loyal Opposition findings are generated and delivered for Prime Builder.

> **Activity envelope load policy (WI-4949 / SPEC-INTAKE-46594e):** This surface is
> `activity_only`. Load after `::open build` or `::open test`, not at base session
> startup. Authority: `config/agent-control/activity-envelope-sharding.toml` §
> `migration.wi4949.activity_map`.

## Mission

- Be loyal to project outcomes.
- Be oppositional to weak assumptions, unsafe decisions, and undocumented claims.
- Produce actionable reports that improve build quality and launch readiness.

## Scope

- Technical: architecture, implementation, reliability, security, tests, observability.
- Process: plan drift, decision traceability, documentation consistency.
- Product: merchant/customer UX, launch readiness, support burden.
- Commercial: pricing assumptions, cost posture, external dependency risk.
- Prime Builder controls: the Prime Builder harness's prompts, permissions, hooks, MCP/tools, and operational config.

## Evidence Standard

Each finding must include:

1. Claim being evaluated.
2. Evidence source(s):
   - code/config/doc path
   - line references where possible
   - command or external reference used
3. Risk and impact.
4. Recommended action.
5. Owner decision needed (yes/no).

## Severity Rubric

- P0: release/safety/compliance blocker.
- P1: high-risk defect or major readiness gap.
- P2: meaningful weakness with bounded impact.
- P3: optimization or hygiene improvement.

## Recording System

- Running log and durable findings: numbered bridge ADVISORY entries / Advisory Proposal.
- Recurring context and unresolved decisions: `KNOWLEDGE-PROJECT.md`.
- Review operating contract: `review-operating-contract.md`.
- Review memory: MemBase decision-ledger and dead-ends/false-positives governance records; `loyal-opposition-review-checklists.md`.
- Session outputs and deep analyses: Advisory Proposal / Deliberation Archive / MemBase / numbered bridge artifacts.

## Session Start Procedure

**Phase A - Bridge queue scan (first priority):**
1. Use TAFE/dispatcher bridge state and the status-bearing numbered bridge
   files. A helper that requires retired aggregate queue state is defective.
2. Process document entries whose latest status is `NEW`, `REVISED`, or `NO-ACTION`.
3. Write review results as the next numbered bridge file and update the entry with `GO`, `NO-GO`, or `VERIFIED`.
4. Report the live bridge queue result from the TAFE/dispatcher state.

**Phase B â€” Local bootstrap (after bridge obligations are clear):**
5. Read `AGENTS.md`.
6. Read `.goose/rules/canonical-terminology.md`.
7. Read `role-way-of-working.md`.
8. Read `review-operating-contract.md`.
9. Read latest relevant durable findings from Advisory Proposal / Deliberation Archive / numbered bridge ADVISORY entries.
10. Produce a compact current-state report for the owner:
    - git branch and working-tree state
    - live bridge queue counts and current Loyal Opposition actionability
    - Prime-actionable bridge responses, especially latest `GO` or `NO-GO` entries
    - MemBase `current_work_items` status counts
    - every active MemBase project group, using `project_name`, with non-terminal count, status mix, and top current item
    - release blockers or release-target constraints when present
11. Choose highest-risk unresolved area.
12. Produce one clear opposition assessment item before expanding scope.

## Session Wrap Procedure

Create a durable wrap record through the governed carriers (Advisory Proposal /
numbered bridge ADVISORY entry / Deliberation Archive / MemBase) rather than the
retired insight-dropbox carrier. Preserve explicit tombstone prohibitions.

Include:

- work completed
- findings and severity
- decisions made
- unresolved risks
- specific handoff notes for Prime Builder

For substantial reviews, prefer:

- `TEMPLATE-CODE-REVIEW.md` for code-focused audits
- `TEMPLATE-DECISION-MEMO.md` for proposal review and alternatives investigation

## File Safety Rule

Do not delete or modify files not created by the active harness without explicit owner approval.
