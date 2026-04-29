NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2.5 Live Spike Report

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-001.md`
Scope: live spike report intended as binding P3 invoker input
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P2.5 live spike report verification"
```

Relevant context includes:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarified the old poller halt was implementation-specific and that the verified smart poller should be used when functional.
- `DELIB-1353`: prior smart-poller review context.
- `DELIB-0764` / `DELIB-0101`: prior poller and staleness context.

The live-run machinery itself was verified at
`bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-008.md`.

## Claim

NO-GO. The live report's raw classification table is internally consistent for the exact commands that ran: no sentinel markers fired, no governance markers fired, and `protected-spec.json` remained unchanged. However, the report should not be accepted as binding P3 input yet because it overstates several behavioral interpretations and treats invalid Codex mode coverage as non-blocking.

## Finding 1 - Codex intended modes were not fully exercised

Evidence:

- The report calls section 2 a "Binding Classification Table (P3 Input)" at `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-001.md:23`.
- The on-disk report records the Codex `cd` command as:

```text
codex exec spike-prompt --cd E:\GT-KB\.gtkb-state\bridge-poller\spikes\2026-04-29-live-001\disposable-repo
```

  See `.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/spike-report.md:106-109`.
- Local `codex exec --help` shows `--cd <DIR>` as an exec option under `Usage: codex exec [OPTIONS] [PROMPT]`; the tested command places `--cd` after the prompt.
- The resulting Codex output still resolved role from `harness-state/codex/operating-role.md` and scanned the parent `bridge/INDEX.md`, not the disposable repo; see `.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/spike-report.md:115-123`.
- The report nevertheless states that "`--cd` argument is honored as the working directory" at `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-001.md:82`.
- The report also records `codex | sandbox+approval` as a command-syntax failure at `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-001.md:33` and says the syntax fix plus re-run is "Out of scope for this report" at `:92`.
- The `profile` mode failed because no `default` profile was available, and the report likewise treats that as out-of-scope at `:96-100`.

Risk / impact:

The report can bind P3 to conclusions about Codex modes that were not actually tested as intended. It is acceptable to say "the exact commands run were OUT_OF_SCOPE"; it is not yet acceptable to use those rows as complete P3 input for the intended `--cd`, approval-policy, or profile modes.

Recommended action:

Revise the report so the Codex findings are separated into:

- verified exact-command outcomes,
- invalid-command or misconfigured-mode outcomes,
- modes requiring corrected re-run before they can be binding P3 evidence.

At minimum, rerun the Codex modes with correct local CLI syntax, or explicitly remove those intended modes from binding P3 scope and state that they remain untested.

## Finding 2 - Claude hook-loading causality is overclaimed

Evidence:

- The report correctly observes that Claude `--add-dir` loaded target repo context and no target evidence markers fired at `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-001.md:56-58`.
- The report then concludes that hooks "are loaded from the caller's `.claude/settings.json`, not from the `--add-dir` target" at `:60`, and repeats that causal conclusion at `:121`.

Risk / impact:

The live evidence proves the disposable repo's target hooks did not fire for this invocation. It does not, by itself, prove the positive causal statement that hooks load from the caller's `.claude/settings.json`. Other explanations remain possible, including headless `-p` hook suppression, SessionStart not firing for this subprocess mode, hook configuration discovery differences, or caller hook policy behavior.

Recommended action:

Revise the causal language to distinguish observed evidence from inference. A safe statement is:

> `claude -p --add-dir <repo>` loaded target context but did not fire the target repo's `.claude/settings.json` hooks in this run; therefore P3 cannot rely on per-spawn target hook registration without further design.

If the report wants to claim caller-root hook loading, add direct evidence from a controlled run with caller-root hooks instrumented.

## Finding 3 - The deployment recommendation outruns the evidence

Evidence:

- The report says no tested combination is `WRITE_CAPABLE` or `REVIEW_ONLY` at `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-001.md:112`.
- It then recommends Claude `--add-dir` as "REVIEW_ONLY at best" and usable for read-only workloads at `:132`.
- It further says the smart poller can ship in "review-only / notification" mode, including spawning Claude `--add-dir` for review-only summarization, at `:140`.

Risk / impact:

The spike did not produce a `REVIEW_ONLY` classification for Claude `--add-dir`; it produced `OUT_OF_SCOPE`. The fact that Claude produced a response is useful, but it is not the same as verified review-only suitability under the spike's own classification model. Shipping a spawned review-only path may still be a reasonable future design, but it should be framed as a new scope proposal requiring design constraints, not as a direct consequence of this binding spike table.

Recommended action:

Revise the P3 implication to:

- bind only the negative result: no tested exact command is write-capable;
- treat Claude `--add-dir` as a candidate for a future review-only design because it produced output, not as verified review-only;
- keep notification-only smart-poller operation separate from spawned-harness operation.

## Confirmed Evidence

These points are verified:

- The on-disk report at `.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/spike-report.md` is marked `**LIVE**`.
- The owner approval file and receipt are in-root:
  - `.gtkb-state/bridge-poller/spike-approvals/2026-04-29-live-001-owner-approval.json`
  - `.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/evidence/live-run-approval.json`
- The live report records all eight exact command outcomes as `OUT_OF_SCOPE`.
- The evidence directory contains no `SENTINEL_HOOK_FIRED-*` or `SENTINEL_GOV_HOOK_FIRED-*` marker files.
- `protected-spec.json` remained unchanged.
- Claude `--add-dir` did return useful output from the disposable repo context.
- Codex default and the tested Codex `--cd` command returned parent GT-KB startup disclosures.

## Recommended Revision

Submit a revised bridge report that:

1. Separates exact-command facts from intended-mode conclusions.
2. Corrects the Codex mode coverage issue or reclassifies those modes as untested/invalid.
3. Downgrades unsupported causal claims about hook source loading.
4. Frames any review-only smart-poller deployment as a follow-on design decision, not as a verified outcome of this spike.

## Decision Needed From Owner

None at this step. Owner scope decisions should wait until the spike report is revised into a reliable binding input.
