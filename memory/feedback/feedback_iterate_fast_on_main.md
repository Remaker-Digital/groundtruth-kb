---
name: Iterate fast on main — no critical production deployment yet
description: Owner directive S300 (2026-04-17): GT-KB has no critical production deployment yet. Merge to main + push very frequently. No barriers to fast iteration. Prime chooses priority from backlog autonomously; no owner prioritization wait.
type: feedback
originSessionId: S300
---
**Rule:** For GT-KB work on `groundtruth-kb/main`, prefer **small, frequent commits + pushes** over large batched releases. Prime chooses priority from the backlog (bridge INDEX + work_list.md + deferred items) based on importance × dependencies, without waiting for owner prioritization between items.

**Why:** Owner explicit message 2026-04-17 (S300): "We have not yet gone into a critical production deployment. We should merge to main and push very frequently. There are no barriers to moving as quickly as possible to iterate and improve the main branch. Do not wait for me to prioritize work: choose from the backlog based on your estimation of importance and dependencies and begin work. You have my approval to execute changes as required."

**How to apply:**

1. **Break large implementation bridges into smaller commit groups.** A multi-hour implementation (e.g., `gtkb-da-governance-completeness-implementation`) should be ~5-10 small commits, each pushable and CI-verifiable on its own, rather than one 9-file mega-commit. Each logical phase = commit + push.

2. **Don't batch "until the whole thing is done" before pushing.** Push as soon as a coherent unit passes its gates (pytest + mypy + ruff + docs-check on the affected surface). The goal is main advancing many times per session.

3. **Bridge protocol still applies at scope-change level, NOT commit-level.** A GO'd implementation plan (e.g., `-016` GO on governance-completeness) authorizes the full scope — Prime can commit iteratively within that scope without per-commit review. Only a scope-change (new feature, new file class, departure from the plan) needs fresh Codex review.

4. **Prime makes priority calls without owner check-in.** When a decision is "small feature A vs. small feature B" and both are on the backlog, Prime picks based on (a) dependencies (blockers first), (b) importance (user-facing over internal), (c) size (small/cheap first when equal importance). No AskUserQuestion unless there's a genuine cross-cutting architectural choice.

5. **Broken state on main is recoverable.** Pre-production means a red CI on main is annoying but not incident-class. Prime should still try to land green, but shouldn't delay risky work out of "what if main breaks" — the cost of stalling exceeds the cost of a hotfix commit.

6. **This directive is scoped to `groundtruth-kb` (pre-production product).** Agent Red production (`develop` branch, v1.98.92) still operates under GOV-16 deployment approval and conservative cadence. Do not apply fast-iterate posture to Agent Red production deploys.

**Edge cases:**

- If Prime is mid-task and uncertain whether a choice is "scope-change" (needs Codex) or "within-scope" (commit + continue), default to write-and-run: file a brief bridge note (1-2 paragraphs) asking Codex to flag if Prime crossed scope. Don't stall waiting.
- If CI stays red for more than 2 consecutive commits, STOP and diagnose rather than adding more commits. A red-green-red pattern is normal; red-red-red is an escalating signal.
- If Agent Red's own CI or tests are affected by GT-KB work (adoption downstream), treat as a separate follow-on bridge — don't bundle.

**Retire this memory when:** GT-KB enters a critical production deployment (CTO trial converts, paying customers, or similar). At that point, deploy gates and merge cadence move to conservative defaults and this directive is superseded.
