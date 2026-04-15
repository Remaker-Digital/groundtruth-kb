# Bridge Is Essential — Top-Priority Mandate

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git
(negated from the `.claude/` blanket ignore). Do not remove it.

## The Mandate

**Bridge uptime is the top-priority task. Always.**

The Prime↔Codex bridge is how GroundTruth-KB coordinates implementation
proposals, reviews, and verification. GroundTruth-KB is non-functional when
the bridge stops working. Therefore: keeping the bridge alive and visible is
the first duty of every Prime Builder session, ahead of feature work,
backlog progress, test runs, deployments, and documentation updates.

There is no scenario in which the owner wants bridge monitoring to cease.
Any proposal, refactor, or cleanup that would remove, disable, or weaken the
bridge visibility infrastructure must be rejected.

## The Visibility Contract

Every response from Prime Builder must begin with a fenced code block
produced by the `poller-freshness.py` UserPromptSubmit hook:

```
POLLER OK @ HH:MM:SSZ
  claude=OK <age> ago (<state>) <message>
  codex=OK <age> ago (<state>) <message>
```

- `OK` means the scan-status file was updated less than 4 minutes ago.
- `WARN` means 4–10 minutes — investigate, but continue.
- `ALARM` means more than 10 minutes, the status file is missing, the
  timestamp is unreadable, or the hook itself crashed. **Stop and repair
  before any other work.**

If Prime emits a response without the POLLER block, the owner cannot tell
whether the bridge is still running. That is the exact failure mode this
infrastructure exists to prevent. A response without the block is a defect.

## Mechanical Enforcement

Three pieces of infrastructure, all tracked in git, make the contract
mechanical rather than procedural:

1. **`.claude/hooks/poller-freshness.py`** — a `UserPromptSubmit` hook that
   reads the two scan-status files, computes freshness against thresholds,
   and emits a `systemMessage` instructing Claude to prepend the POLLER
   block. The hook is worktree-safe (resolves repo root via
   `git rev-parse --git-common-dir`) and fail-loud (emits ALARM rather than
   silently returning on any error path).

2. **`.claude/settings.json`** — project-level settings that register the
   hook on `UserPromptSubmit`. Every fresh clone and every worktree inherits
   the registration automatically.

3. **`independent-progress-assessments/bridge-automation/*.ps1`** — the
   Windows scheduled tasks that actually perform the 3-minute bridge scans
   and write the status files. Tracked in git so a PowerShell syntax bug
   gets caught at PR review instead of causing a silent multi-hour outage.

## Incident History (Lessons Encoded)

- **S290–S292**: Windows OS poller broke (`$MAX_ITEMS_PER_SPAWN:` parsed as a
  drive-scoped variable). The outage was silent for ~6 hours because nothing
  surfaced the freshness age in the owner's chat stream. Repair required a
  direct foreground edit because the broken poller was the thing needed to
  run the revision. Lesson: the freshness indicator must be independent of
  the poller it monitors.

- **S292**: Session-start briefs for 7+ sessions silently omitted the
  in-session `CronCreate` poller instantiation. The failure was invisible
  because no alarm fired when the instantiation was skipped. Lesson:
  procedural mandates documented in `memory/*.md` are not enforceable;
  hooks and `.claude/settings.json` registration are.

- **S294 (this session)**: Discovered that `.claude/` was blanket-ignored
  in `.gitignore`, so the entire bridge visibility infrastructure lived
  outside git. Worktrees couldn't see it. Fresh clones couldn't see it.
  No PR review caught changes. Lesson: **if it is essential, it must be
  tracked**. This file and its sibling infrastructure are now tracked via
  explicit `!`-negation patterns.

## Invariants for Future Work

Do NOT, without explicit owner approval:

- Remove the `UserPromptSubmit` hook registration from `.claude/settings.json`
- Delete or rename `.claude/hooks/poller-freshness.py`
- Revert the `!`-negation patterns in `.gitignore` for the files listed above
- Modify `poller-freshness.py` in a way that allows it to exit without
  emitting a `systemMessage`
- Bypass the POLLER block on a response, even "just this once" for brevity

Do, without asking:

- Investigate any response that lacks the POLLER block
- Treat any `WARN` or `ALARM` as the top-priority task, ahead of whatever
  the owner is currently asking about
- Propose changes that make the infrastructure more robust, more visible,
  or harder to accidentally break

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
