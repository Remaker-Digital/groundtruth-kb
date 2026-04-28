---
name: Codex bridge protocol and role constraints
description: How to use prime-bridge with Codex — role, token budget, notification discipline
type: feedback
---

## Codex Role & Constraints

- Codex (GPT-5.3) serves as **Trusted Advisor** (Loyal Opposition role).
- Codex can perform **research or ephemeral tasks** that would consume excessive context if done by Prime Builder.
- Codex has a **$20/month token budget** — continuous use triggers throttling. Be judicious.

## Codex Strengths & Routing (S219)

**Use Codex for:**
- **Pre-implementation review:** Send implementation plans for critique before coding. Codex finds gaps Prime misses.
- **Post-implementation verification:** After deploy, Codex audits independently (the re-audit pattern). Caught the `patch()` bypass in S218.
- **Audit and compliance reviews:** GO/NO-GO with evidence — Codex excels here.
- **Codebase scanning:** Credential exposure, drift detection, pattern matching across files.
- **Checklist verification:** Does X meet criteria Y across N files?

**Do NOT route through Codex:**
- Creative or architectural decisions. Codex produces thorough but over-engineered proposals for 2-person teams.
- Design trade-offs where proportionality matters more than exhaustiveness.

**Why:** Owner observation (S219): Codex is rigorous and methodical but not as insightful or creative as Opus 4.6. The real value is **independent verification** — two models reviewing the same evidence from different perspectives catch more than one model with more context. Codex's value isn't saving Prime tokens — it's providing a genuinely different analytical lens.

## Prime-Bridge Notification Protocol

**When to notify Codex (send_message):**
- After implementing remediations from Codex audit findings (so Codex can verify on next session)
- When delegating a research or context-heavy ephemeral task
- When a significant architectural change affects areas Codex has audited

**When NOT to notify Codex:**
- Routine code changes that don't touch audited areas
- Minor bug fixes or test additions
- Anything that would trigger unnecessary token consumption on a budget-limited agent

**Message discipline:**
- Keep messages concise — Codex pays per token to process them
- Use structured payloads (evidence_paths, specs_affected) so Codex can verify efficiently
- Batch related changes into single notifications rather than per-file updates
- Use tags consistently for filtering: `remediation`, `research-request`, `architecture`, `audit-response`

**How to apply:** Before sending a bridge message, ask: "Does Codex need to know this, and is it worth their token budget?" If yes, send a tightly scoped message. If delegating work, provide enough context that Codex won't need to re-discover it.
