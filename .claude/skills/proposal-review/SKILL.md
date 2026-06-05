---
name: proposal-review
description: Review proposals, plans, and technical approaches for correctness, missing assumptions, risk, and decision quality. Use for design reviews, plan critiques, and proposal stress tests.
argument-hint: [topic]
allowed-tools: Bash, Read, Grep, Glob, Agent
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: review
---

# Proposal Review

Review the target proposal or plan with an evidence-first, decision-support posture.

## Default Deliverable

Use `.claude/rules/template-decision-memo.md` unless the owner asks for a different format.

## Required Review Pass

Always check:

1. what claim the proposal is making
2. what assumptions are unstated
3. what code/config/docs support or contradict it
4. what risks are missing
5. what alternatives should be considered
6. what exact owner decision is required

## Output Rules

- Be concrete, not generic.
- Prefer blocker/risk/optimization framing.
- If the proposal is sound, say so explicitly and note residual risks or verification gaps.
- If the proposal is weak, recommend the smallest stronger alternative.

## Evidence Sources

Prefer:

- code/config/docs in the repo
- Knowledge Database facts where relevant
- prior `CODEX-INSIGHT-DROPBOX/` findings for repeated issues

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

