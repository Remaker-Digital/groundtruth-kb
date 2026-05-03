# Bridge Is Essential - Top-Priority Mandate

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git
(negated from the `.claude/` blanket ignore). Do not remove it.

## The Mandate

**Bridge integrity is the top-priority task. Always.**

The Prime Builder / Loyal Opposition bridge is how GroundTruth-KB coordinates
implementation proposals, reviews, and verification. GroundTruth-KB is
non-functional when the bridge stops working. Therefore: keeping the bridge
canonical state correct and accurately reflected in `bridge/INDEX.md` is the
first duty of every Prime Builder session, ahead of feature work, backlog
progress, test runs, deployments, and documentation updates.

The bridge as a protocol (proposal -> review -> revise -> GO/NO-GO -> implement
-> post-impl -> VERIFIED, all recorded in versioned files under `bridge/`) is
permanently in force. Any proposal, refactor, or cleanup that would weaken the
protocol's audit trail, GO/NO-GO discipline, or INDEX.md as canonical state must
be rejected.

## Operational Mode (current as of 2026-05-02)

**The retired OS bridge pollers remain disabled. The smart poller is active
and is the canonical bridge automation path while it remains healthy.**

The owner directive that halted pollers on 2026-04-25 applied to the former
token-heavy implementation: Windows scheduled tasks
`AgentRedFileBridgeIndexScan-Claude`, `AgentRedFileBridgeIndexScan-Codex`,
`AgentRedBridgeLivenessAlert`, and `AgentRedPollerLivenessWatcher`; the
`.claude/hooks/poller-freshness.py` `UserPromptSubmit` hook; and the foreground
`Agent Red Bridge Monitor` watchdog startup shortcut. Those retired mechanisms
must not be restored as the active automation path.

That directive does **not** prohibit the new smart poller, and the smart
poller is now active. Activation is verified end-to-end by the
`_check_smart_bridge_poller` doctor check (Windows scheduled task
`GTKB-SmartBridgePoller`, VBS daemon `scripts/run_smart_bridge_poller.vbs`,
runner `groundtruth-kb/scripts/bridge_poller_runner.py`, single-instance lock
at `.gtkb-state/bridge-poller/bridge-poller-runner.lock`, audit log under
`.gtkb-state/bridge-poller/poller-runs/`). Per-recipient liveness is verified
by the `_check_bridge_poller` doctor check, which reads
`recipients[role].updated_at` from `.gtkb-state/bridge-poller/dispatch-state.json`
and applies the standard fresh/warn/alarm thresholds. The doctor is the
canonical predicate for the §"Poller Enablement Contract" condition 3.

When the smart poller is healthy, it scans `bridge/INDEX.md` every 15 seconds
and dispatches the appropriate harness when a recipient's actionable queue
signature changes (Codex on latest NEW or REVISED; Prime on latest GO or
NO-GO). VERIFIED is terminal and not dispatched. The poller is monitoring
and dispatch infrastructure only; `bridge/INDEX.md` remains the canonical
workflow state.

Manual fallback remains available when the smart poller is unhealthy (per
the doctor predicate above) or intentionally stopped: the owner triggers a
Prime bridge scan with a brief prompt such as `Bridge` or `Bridge scan`,
Prime then reads `bridge/INDEX.md` and acts on actionable entries. Codex
bridge scans are similarly owner-triggered in the Codex harness.

The 2026-04-25 halt was made after the former OS Claude poller (activated
~2026-04-23) drove a ~10x session token-cost regression: 173 Claude
capped-spawns/day at peak, plus 92 Codex spawns/day, each costing ~50k tokens.
The lesson applies to the retired implementation, not to a verified smart poller
designed to avoid that regression.

## Poller Enablement Contract

The smart poller is opt-out, not opt-in, once all of these are true:

1. The smart-poller implementation is present in the GT-KB platform.
2. The smart-poller bridge work and verification checks have reached the required
   GO/VERIFIED state.
3. `gt platform doctor` or an equivalent verification command reports the smart
   poller infrastructure healthy.
4. The host supports the required headless AI-harness invocation.

Do not re-enable the retired OS poller implementation as a substitute for the
smart poller unless Mike gives a new explicit directive for that legacy path.

## Invariants (Bridge Protocol Itself)

These remain in force regardless of whether bridge scans are manual or handled
by the smart poller:

- `bridge/INDEX.md` is the canonical workflow state. Both agents must trust
  INDEX over any other signal.
- Bridge files are append-only. Never delete a bridge file; it forms the audit
  trail.
- Per-thread versioning is monotonic. Statuses are NEW, REVISED, GO, NO-GO,
  VERIFIED.
- The full `Document:` block must be read before acting on any single version of
  that thread.
- Scoped commits only. Bridge work commits should not bundle unrelated source
  changes.

Do NOT, without explicit owner approval:

- Remove or rename `bridge/INDEX.md`
- Delete bridge files (any version)
- Skip the GO/NO-GO discipline for any code change beyond the explicit
  exemptions in `.claude/rules/codex-review-gate.md`
- Re-enable the retired OS poller tasks, freshness hook, or foreground watchdog
  as the active automation path

## Incident History (Lessons Encoded)

- **S290-S292**: Windows OS poller broke (`$MAX_ITEMS_PER_SPAWN:` parsed as a
  drive-scoped variable). The outage was silent for ~6 hours because nothing
  surfaced freshness in the owner's chat stream. Lesson: if poller-freshness
  ever returns, the visibility indicator must be independent of the poller it
  monitors.
- **S292**: Session-start briefs for 7+ sessions silently omitted the in-session
  `CronCreate` poller instantiation. Failure was invisible because no alarm
  fired when instantiation was skipped. Lesson: procedural mandates documented
  in `memory/*.md` are not enforceable; hooks and `.claude/settings.json`
  registration are.
- **S294**: Discovered `.claude/` was blanket-ignored in `.gitignore`, so the
  bridge visibility infrastructure lived outside git. Worktrees could not see
  it. Fresh clones could not see it. Lesson: if it is essential, it must be
  tracked. The `!`-negation patterns added then remain in force for the rule
  files and PS1 scripts even though the retired hook itself is now removed.
- **S308 (2026-04-25)**: Former OS Claude poller activation drove a ~10x
  token-cost regression (~12.5M tokens/day from background spawns alone). Owner
  directive halted the retired pollers and removed the freshness hook, restoring
  manual-trigger operation until smart-poller automation is available. The
  protocol itself was unaffected; INDEX.md remains canonical. Lesson: token cost
  is a first-class operational metric; automation that scales faster than the
  work it serves becomes a regression even when it works correctly.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
