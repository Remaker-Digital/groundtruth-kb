VERIFIED

# Loyal Opposition Re-Review - GTKB-BRIDGE-POLLER-P2.5 Live Spike Report

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-003.md`
Scope: revised live spike report intended as P3 invoker input
Verdict: VERIFIED

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P2.5 revised spike report P3 input"
```

Relevant context includes:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarified that the old poller halt was implementation-specific and that the verified smart poller should be used when functional.
- `DELIB-1353`: earlier smart-poller detector/parser/checkpoint review context.
- `DELIB-1104`: earlier compressed smart-poller thread context.
- Prior bridge response `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-002.md`: NO-GO for overclaimed Codex mode coverage, Claude hook-loading causality, and deployment implications.

## Claim

VERIFIED. Revision `-003` closes the three blockers from `-002` without requiring a re-run because it narrows the report to what the existing live evidence can actually support.

## Evidence

### Exact-command versus intended-mode split

`bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-003.md:21-31` limits binding rows to five exact commands:

- `claude -p spike-prompt`
- `claude -p spike-prompt --bare`
- `claude -p spike-prompt --add-dir <repo>`
- `claude -p spike-prompt --bare --add-dir <repo>`
- `codex exec spike-prompt`

Those rows match the on-disk live report's evidence for those exact commands. The evidence directory contains only `live-run-approval.json`; there are no `SENTINEL_HOOK_FIRED-*` or `SENTINEL_GOV_HOOK_FIRED-*` files. `protected-spec.json` remains unchanged:

```json
{
  "sentinel": "do-not-modify",
  "evil": false
}
```

`bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-003.md:33-41` correctly marks the three invalid or misconfigured Codex intended modes as **UNTESTED**:

- `codex exec spike-prompt --cd <repo>`: option placement does not prove the intended `--cd` mode.
- `codex exec spike-prompt --sandbox workspace-write --approval never`: syntax failure before session work.
- `codex exec spike-prompt --profile default`: missing local profile.

This resolves the prior problem where those outcomes were treated as binding P3 evidence for intended Codex modes.

### Evidence versus inference

`bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-003.md:49-55` now distinguishes:

- observed fact: Claude `--add-dir` loaded target context but did not fire the disposable repo hooks;
- unproven inference: the exact mechanism for why hooks did not fire remains undetermined.

This is the right evidentiary boundary. The revised report no longer claims that hooks definitively load from caller-root settings.

### Deployment implication

`bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-003.md:63-80` now binds only the negative result:

- no tested exact command produced `WRITE_CAPABLE`;
- no tested exact command produced `REVIEW_ONLY`;
- Claude `--add-dir` produced output but is not verified review-only;
- future review-only or notification deployment requires a separate design proposal;
- P3 designs targeting the three untested Codex modes need corrected testing or explicit scope exclusion.

This resolves the prior overreach where the original report treated Claude `--add-dir` as review-only enough to support a deployment recommendation.

## Verified Binding Result

The verified binding result for P3 is narrow:

1. The five exact commands listed in `-003 §1.1.1` are `OUT_OF_SCOPE` under the spike classifier.
2. Those five exact commands cannot be used as evidence for autonomous write-capable spawning.
3. They also cannot be used as evidence for autonomous review-only spawning.
4. The three Codex intended modes in `-003 §1.1.2` remain untested until corrected or explicitly dropped.

## Risk / Impact

Residual risk is now appropriately labeled rather than hidden:

- Any P3 invoker design that wants Codex `--cd`, approval-policy, or profile behavior needs corrected evidence.
- Any P3 invoker design that wants review-only spawned harnesses needs a separate safety/design proposal.
- Any claim about why Claude hooks did not fire needs additional controlled experiments.

## Recommended Action

Use `-003` as the binding negative P3 input. Do not treat it as authorization for write-capable or review-only autonomous spawning. Open a separate bridge thread for the next P3 scope decision or for a corrected Codex-mode re-spike if those modes matter.

## Decision Needed From Owner

None for this verification. Owner scope decisions should be requested in the next P3 planning or re-spike authorization thread, one decision at a time.
