# Codex Decision Ledger - Agent Red Customer Engagement

Purpose: persistent record of owner decisions and standing operating choices that materially affect Codex review behavior.

## Usage Rules

- Record only durable decisions that future sessions should honor.
- Prefer one entry per decision.
- Include source, impact, and whether the decision is still active.

## Entries

### 2026-03-25 - Codex primary role is review and investigation

- source:
  Owner request in session on 2026-03-25.
- decision:
  Codex's primary role in this project is:
  1. reviews of proposals and code
  2. investigations of alternatives and solutions to technical challenges or decisions
- impact:
  Analysis-first behavior is the default expectation for Codex sessions in this repo.
  Implementation should not be assumed unless explicitly requested.
- status:
  Active

### 2026-03-25 - Review-mode artifacts adopted

- source:
  Owner approval to implement the Codex review configuration proposal.
- decision:
  The project adopts dedicated Codex review artifacts:
  - `CODEX-REVIEW-OPERATING-CONTRACT.md`
  - `CODEX-REVIEW-CHECKLISTS.md`
  - `CODEX-DEAD-ENDS-AND-FALSE-POSITIVES.md`
  - `TEMPLATE-CODE-REVIEW.md`
  - `TEMPLATE-DECISION-MEMO.md`
- impact:
  Future review and investigation work should use these artifacts as the default operating scaffold.
- status:
  Active

### 2026-03-28 - Extensibility investigation is the next prepared design track

- source:
  Owner request to summarize the proposed agent-extensibility model and send it to Prime for evaluation and implementation planning.
- decision:
  The next prepared investigation track is the `agent extensibility` design:
  - distinguish `skills` from `peer agents`
  - evaluate tenant-scoped custom MCP as per-agent skills
  - evaluate direct team-member access to peer agents through Chat UI
  - have Prime prepare an implementation proposal for later Codex review
- impact:
  A fresh Codex session should be ready to immediately resume this design track without rediscovering the recent S227 Tier 3/4 review history.
- status:
  Active

### 2026-04-01 - Widget functionality is a hard deployment gate

- source:
  Owner directive in session on 2026-04-01 during S251 closeout.
- decision:
  A deployment is a failure if the chat widget is non-functional in the target environment.
  The only exception is an explicit owner approval to deploy with the widget disabled.
- impact:
  Future review and release verdicts must treat widget failures as blockers or rollback-required conditions, not advisory defects.
- status:
  Active

### 2026-04-01 - GroundTruth distribution contract is GitHub-installable, not PyPI-required

- source:
  Owner clarification in session on 2026-04-01 after the GroundTruth closeout checkpoint.
- decision:
  `groundtruth-kb` should be a versioned Python package installable directly from GitHub by outside users.
  PyPI publication is not required at this time.
- impact:
  Packaging audits and implementation proposals must distinguish:
  1. GitHub-installable package
  2. release-artifact installable package
  3. PyPI-published package
  and must not assume PyPI as the contract unless the owner later says so explicitly.
- status:
  Active

### 2026-04-01 - Non-disruptive deployment operating model adopted

- source:
  Owner agreement with the operating-model findings and Prime response `9fa11da0` on 2026-04-01.
- decision:
  The accepted release model is:
  1. `release_pipeline.py` is the canonical production GO/NO-GO path
  2. widget, chat, auth, tenant-routing, and config changes are `Class C`
  3. `Class C` promotion requires live widget proof
  4. widget failure means promotion blocked or rollback required
- impact:
  Future release and verification proposals should be reviewed against the OM Wave 1-3 program, not against older smoke-only deployment assumptions.
- status:
  Active

### 2026-04-01 - Artifact immutability and lane separation are prerequisites for trustworthy hotfixes

- source:
  Owner agreement on spec request `ad40ba38` and the hotfix/WIP separation specs on 2026-04-01.
- decision:
  Urgent fixes must ultimately be supported by three explicit separations:
  1. code lane separation (`git worktree` or equivalent clean hotfix lane from the deployed SHA)
  2. environment lane separation (`integration-staging` vs `release-staging`)
  3. artifact lane separation (manifest-based build-once, promote-the-same-artifact release flow)
- impact:
  OM Wave 2/3 proposals should treat immutable artifact promotion and staging-lane separation as prerequisites, not optional polish.
- status:
  Active

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
