---
name: gtkb-proposal-review
description: Review proposals, plans, and technical approaches for correctness, missing assumptions, risk, and decision quality. Use for design reviews, plan critiques, and proposal stress tests.
argument-hint: [topic]
allowed-tools: Bash, Read, Grep, Glob, Agent
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: groundtruth-kb
  category: review
---

# Proposal Review

Review the target proposal or plan with an evidence-first, decision-support posture.

## Default Deliverable

Use `{{HARNESS_RULES_DIR}}/template-decision-memo.md` unless the owner asks for a different format.

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
- prior durable review findings (Deliberation Archive records / Advisory Proposal bridge entries) for repeated issues

## Bridge Verdicts

When this review produces a bridge `GO`/`NO-GO` verdict, run
`python scripts/skill-helpers/gtkb-verify/write_verdict.py --slug <slug> --body-file <draft-body-file>`
before filing so the draft's `## Prior Deliberations` section is seeded. Review
and prune the helper-suggested candidates; if you opt out, keep an explicit
`_No prior deliberations: <reason>._` line in the verdict.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

