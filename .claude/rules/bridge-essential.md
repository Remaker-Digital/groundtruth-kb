# Bridge Is Essential — Top-Priority Mandate

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git
(negated from the `.claude/` blanket ignore). Do not remove it.

## The Mandate

**Bridge integrity is the top-priority task. Always.**

The Prime Builder / Loyal Opposition bridge is how GroundTruth-KB
coordinates implementation proposals, reviews, and verification.
GroundTruth-KB is non-functional when the bridge stops working.
Therefore: keeping the bridge canonical state correct and accurately
reflected in `bridge/INDEX.md` is the first duty of every Prime Builder
session, ahead of feature work, backlog progress, test runs, deployments,
and documentation updates.

The bridge as a *protocol* (proposal → review → revise → GO/NO-GO →
implement → post-impl → VERIFIED, all recorded in versioned files under
`bridge/`) is permanently in force. Any proposal, refactor, or cleanup
that would weaken the protocol's audit trail, GO/NO-GO discipline, or
INDEX.md as canonical state must be rejected.

## Operational Mode (current as of 2026-04-25)

**Automated bridge pollers are HALTED by owner directive.** The Windows
scheduled tasks `AgentRedFileBridgeIndexScan-Claude`,
`AgentRedFileBridgeIndexScan-Codex`, `AgentRedBridgeLivenessAlert`, and
`AgentRedPollerLivenessWatcher` are all `Disabled`. The
`.claude/hooks/poller-freshness.py` `UserPromptSubmit` hook has been
removed. The foreground `Agent Red Bridge Monitor` watchdog startup
shortcut has also been removed so the retired poller liveness monitor
does not relaunch on login. Bridge scans are now **manual** in both
directions.

Owner triggers a Prime bridge scan with a brief prompt such as `Bridge`
or `Bridge scan`. Prime then reads `bridge/INDEX.md`, identifies any
NEW/REVISED entries that need Prime action (responding to a Codex GO →
implement; responding to a Codex NO-GO → revise) or any GO/NO-GO entries
that need Prime acknowledgement, and acts. Codex bridge scans are
similarly owner-triggered in the Codex harness.

The change was made on 2026-04-25 (S308) after the OS Claude poller
(activated ~2026-04-23) drove a ~10× session token-cost regression: 173
Claude capped-spawns/day at peak, plus 92 Codex spawns/day, each costing
~50k tokens. See the audit-trail bridge entry filed in the same change
for the full investigation and decision record.

## Re-Enabling Pollers (Future Sessions)

The poller infrastructure is preserved but disabled — not removed. To
re-enable:

1. `Enable-ScheduledTask -TaskName AgentRedFileBridgeIndexScan-Claude`
   (and the other three tasks as needed).
2. Restore the `UserPromptSubmit` hook in `.claude/settings.json` and
   recreate `.claude/hooks/poller-freshness.py` from git history
   (commit pre-S308) — or replace with a lighter freshness mechanism.
3. Recreate the `Agent Red Bridge Monitor Watchdog.lnk` startup shortcut
   only if the new design requires a visible monitor.
4. Update this rule's "Operational Mode" section to reflect the change.

Re-enabling requires explicit owner approval and a written
cost/benefit analysis demonstrating the regression has been mitigated
(e.g., reduced bridge thread depth, capped per-thread version count,
narrower spawn predicates).

## Invariants (Bridge Protocol Itself)

These are unchanged by the poller halt and remain in force:

- `bridge/INDEX.md` is the canonical workflow state. Both agents must
  trust INDEX over any other signal.
- Bridge files are append-only. Never delete a bridge file — it forms
  the audit trail.
- Per-thread versioning is monotonic. Statuses are NEW, REVISED, GO,
  NO-GO, VERIFIED.
- The full `Document:` block must be read before acting on any single
  version of that thread.
- Scoped commits only. Bridge work commits should not bundle unrelated
  source changes.

Do NOT, without explicit owner approval:

- Remove or rename `bridge/INDEX.md`
- Delete bridge files (any version)
- Skip the GO/NO-GO discipline for any code change beyond the explicit
  exemptions in `.claude/rules/codex-review-gate.md`
- Re-enable the OS pollers without the cost/benefit analysis above

## Incident History (Lessons Encoded)

- **S290–S292**: Windows OS poller broke (`$MAX_ITEMS_PER_SPAWN:` parsed
  as a drive-scoped variable). The outage was silent for ~6 hours
  because nothing surfaced freshness in the owner's chat stream.
  Lesson: if poller-freshness ever returns, the visibility indicator
  must be independent of the poller it monitors.

- **S292**: Session-start briefs for 7+ sessions silently omitted the
  in-session `CronCreate` poller instantiation. Failure was invisible
  because no alarm fired when instantiation was skipped. Lesson:
  procedural mandates documented in `memory/*.md` are not enforceable;
  hooks and `.claude/settings.json` registration are.

- **S294**: Discovered `.claude/` was blanket-ignored in `.gitignore`,
  so the bridge visibility infrastructure lived outside git. Worktrees
  couldn't see it. Fresh clones couldn't see it. Lesson: if it is
  essential, it must be tracked. The `!`-negation patterns added then
  remain in force for the rule files and PS1 scripts even though the
  hook itself is now removed.

- **S308 (2026-04-25)**: OS Claude poller activation drove a ~10×
  token-cost regression (~12.5M tokens/day from background spawns
  alone). Owner directive halted both pollers and removed the
  freshness hook, restoring manual-trigger operation. The protocol
  itself was unaffected — INDEX.md remains canonical. Lesson: token
  cost is a first-class operational metric; automation that scales
  faster than the work it serves becomes a regression even when it
  works correctly.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
