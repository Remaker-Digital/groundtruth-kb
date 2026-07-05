# Loyal Opposition Insight — Shared-DB VERIFIED Finalization Divergence Across LO Harnesses

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-05T08-57-24Z-loyal-opposition-B-c6e8c3
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatch Loyal Opposition worker (dispatch 2026-07-05T08-57-24Z-loyal-opposition-B-c6e8c3); resolved role loyal-opposition

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-3400, WI-5023
Date: 2026-07-05 UTC (dispatch 2026-07-05T08-57-24Z)

## Context

This dispatch fanned two NEW post-implementation reports to more than one Loyal
Opposition harness. While this Claude-B worker performed canonical-state
verification, an interactive Antigravity-C (gemini-2.5-pro, session
`2026-07-05T09-08-00Z-loyal-opposition-C-e8d75a`) filed terminal verdicts on both
first: `bridge/gtkb-wi3400-...-004.md` = **VERIFIED**;
`bridge/gtkb-dispatcher-complex-watchdog-cli-parity-004.md` = **NO-GO**. This
worker stood down on both (append-only guard correctly refused the -004
overwrite). The thread-2 NO-GO matched this worker's independent conclusion.
This insight concerns only the thread-1 VERIFIED.

## Finding 1 — [P2] Non-deterministic LO finalization policy for the shared `groundtruth.db` blob

- **Claim.** Two LO harnesses would finalize the same governance-only KB-capture
  report (`gtkb-wi3400-...-003`, `target_paths: ["groundtruth.db"]`) in opposite
  ways, and the divergence is invisible to the dispatcher's first-writer-wins
  race resolution.
- **Evidence.**
  - Peer C's VERIFIED created commit `b5a2d0db` ("docs(governance): verify
    Antigravity V1 release strategy advisory disposition capture"). `git show
    --stat b5a2d0db` shows the same-transaction path set committed
    `groundtruth.db | Bin 550453248 -> 553639936 bytes` (+~3.2 MB) alongside the
    four bridge files. `git status --short -- groundtruth.db` remained ` M`
    immediately after, confirming the commit snapshotted the entire live
    multi-session blob, not just WI-3400's DELIB + WI rows.
  - At verdict time the working tree carried ~400+ dirty paths (`git status
    --short` = 417 entries) from concurrent sessions (e.g. the in-flight
    `gtkb-dispatch-selection-binding-sot-consolidation` chain), so the commit
    folded many other threads' **unverified** MemBase mutations into a
    WI-3400-labeled `docs:` commit.
  - This Claude-B worker, applying the `write_verdict.py`
    `_assert_include_set_covers_report_claims` gate + the absence of a
    `## By-Reference Finalization Waiver` in the -003 report, would have filed
    **NO-GO on finalization scope** (substance fully verified correct; only the
    commit scope blocked), per the established "owner-authorized direct
    finalization for entangled shared files" convention.
- **Substance is not in dispute.** Independent canonical reads confirm the
  WI-3400 capture is correct: `DELIB-S363-ANTIGRAVITY-V1-ADVISORY-DISPOSITION`
  (rowid 10150) has the claimed fields and records all three advisory
  dispositions exactly as scoped; `WI-3400` is resolved with completion
  evidence; both preflights clean. The VERIFIED verdict's *conclusion* is right;
  the concern is its *commit scope*.
- **Risk / impact (P2, audit-trail + determinism; not data loss).** MemBase is
  append-only, so no rows are lost. But (a) per-thread VERIFIED commits that
  sweep the whole shared blob make commit provenance misleading (a
  "verify WI-3400" commit contains unrelated cross-thread inserts), and (b)
  bridge verdicts become non-deterministic across harnesses for shared-DB
  finalization — the same report can VERIFY or NO-GO purely by which LO wins the
  dispatch race. The recent commit log (WI-5019/5015/5018/5014 finalizations)
  suggests blob-sweep finalization is already the de-facto pattern, which makes
  this a policy question, not a one-off peer error.
- **Recommended action (owner decision).** Standardize the VERIFIED-finalization
  policy for the shared `groundtruth.db` so all LO harnesses behave
  identically. Candidate policies: (1) require a `## By-Reference Finalization
  Waiver` for governance-only KB captures so VERIFIED commits only the verdict
  artifact and leaves `groundtruth.db` for an owner sweep; (2) explicitly accept
  blob-sweep finalization as policy and update the LO verify skill + memory so
  Claude-B stops issuing NO-GO-on-scope; (3) route all shared-DB finalization
  through an owner-authorized batch sweep. This is a `GOV-FILE-BRIDGE-AUTHORITY-001`
  / verify-skill policy call for Prime Builder to convert into a backlog item and
  an owner AUQ.

## Handoff to Prime Builder

- No thread action required: both dispatched entries are terminal
  (wi3400 VERIFIED, dispatcher-complex NO-GO by peer C).
- Consider filing a backlog item under bridge-protocol reliability to
  standardize shared-`groundtruth.db` VERIFIED finalization (Finding 1), then an
  owner AUQ to pick the policy. This worker is headless and cannot open the AUQ.
- The dispatcher-complex NO-GO (WI-5023) correctly directs resumption of the
  doctor watchdog check; note that the `doctor.py` go_implementation reservation
  that blocked the report has since lapsed (the `gtkb-dispatch-selection-binding-sot-consolidation`
  slug now carries only a draft claim at NO-GO), so Prime may be able to resume now.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
