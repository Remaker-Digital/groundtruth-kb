---
name: alternatives-investigation
description: Investigate technical alternatives and recommend the least-regret option with evidence, tradeoffs, reversibility, and implementation impact. Use for architecture choices, tool selection, and solution comparison.
argument-hint: [decision]
allowed-tools: Bash, Read, Grep, Glob, Agent
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: investigation
---

# Alternatives Investigation

Investigate distinct solution paths and recommend the best option under the real project constraints.

## Default Deliverable

Use `independent-progress-assessments/TEMPLATE-DECISION-MEMO.md`.

## Required Comparison Dimensions

Check each option for:

1. implementability now
2. dependency or approval requirements
3. reversibility
4. migration cost
5. operational burden
6. failure mode
7. evidence quality

## Output Rules

- Compare only materially distinct options.
- Reject fake options that are not actually available in the current environment.
- Name the minimum-regret recommendation, not just the most ambitious one.
- If the evidence is thin, say so and identify the next discriminating check.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

