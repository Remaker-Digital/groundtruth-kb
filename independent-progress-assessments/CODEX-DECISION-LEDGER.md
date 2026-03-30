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

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
