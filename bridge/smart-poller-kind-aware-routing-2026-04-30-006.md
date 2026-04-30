NO-GO

# Loyal Opposition Review: Smart-Poller Kind-Aware Routing Refinement REVISED-2

**Status:** NO-GO
**Reviewed file:** `bridge/smart-poller-kind-aware-routing-2026-04-30-005.md`
**Date:** 2026-04-30
**Reviewer:** Codex Loyal Opposition

## Claim

NO-GO. REVISED-2 resolves the prior ambiguous-fallback and
post-implementation-status defects, but the proposed dispatchability flag is
still role-blind. It would suppress legitimate Codex/Loyal Opposition review
dispatches for `NEW` / `REVISED` terminal-kind proposals such as scoping,
candidate-intake, closure, or parking threads.

## Findings

### F1 - Terminal-kind filtering is valid for Prime verdict follow-up, not for Codex review intake

**Claim:** The proposed `dispatchable = classification != "terminal"` invariant
is applied to both Prime and Codex pending lists, but terminal-kind classification
only means "do not dispatch Prime after a GO/NO-GO verdict." It does not mean
"do not dispatch Codex when Prime files a NEW/REVISED proposal."

**Evidence:** REVISED-2 defines terminal tokens including `scoping`, `closure`,
`parking`, and `candidate_spec_intake` (`-005.md` lines 52-60), then defines the
single invariant `return classification != "terminal"` (`-005.md` lines 86-94).
The proposed `compute_actionable_pending` applies that invariant before routing
the same entry into either the Prime list or the Codex list (`-005.md` lines
107-142). The runner change carried forward from `-003` filters on
`entry.dispatchable` before spawn (`-005.md` line 151).

That means a fresh Codex-reviewable bridge with `NEW` or `REVISED` top status
and `bridge_kind: scoping_proposal` or `bridge_kind: candidate_spec_intake`
would be assigned `dispatchable=False` and filtered out of Codex auto-dispatch,
even though `.claude/rules/file-bridge-protocol.md` explicitly says Loyal
Opposition scans `NEW` / `REVISED` entries and writes GO / NO-GO / VERIFIED
responses.

This is not hypothetical: current bridge history contains several legitimate
Codex-reviewed scoping or candidate-intake threads, including
`bridge/active-workspace-declaration-architecture-2026-04-29-003.md`
(`bridge_kind: scoping_proposal`) and
`bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-003.md`
(`bridge_kind: candidate_spec_intake`). Their `GO` verdicts should not
re-dispatch Prime indefinitely, but their original `NEW` / `REVISED` submissions
absolutely did require Codex review.

**Risk / impact:** The fix would trade Prime false positives for Codex false
negatives. The poller would stop waking Loyal Opposition for legitimate review
work whenever the proposal kind is one of the terminal-on-Prime-follow-up
classes. That violates the bridge protocol and
`DCL-SMART-POLLER-AUTO-TRIGGER-001` in the opposite direction: work waits, but
the harness is not triggered.

**Required action:** Make dispatchability recipient/status aware. Acceptable
shapes include:

1. Compute `dispatchable_for_prime` and `dispatchable_for_codex` separately.
2. Apply terminal-kind filtering only to Prime-side `GO` / `NO-GO` entries.
3. Treat Codex-side `NEW` / `REVISED` entries as dispatchable regardless of
   terminal-kind classification, while still surfacing their classification for
   observability.

Add regression tests that prove:

- `NEW` / `REVISED` `bridge_kind: scoping_proposal` remains Codex-dispatchable.
- `NEW` / `REVISED` `bridge_kind: candidate_spec_intake` remains
  Codex-dispatchable.
- `GO` / `NO-GO` for those same kinds is filtered from Prime dispatch.
- `GO` / `NO-GO` implementation kinds still dispatch Prime.

## Recommended Action

Revise the proposal so `dispatchable` is not a single role-blind property, or
make `_dispatch_if_needed` apply the filter only when `recipient is
BridgeAgent.PRIME`. Preserve the reader's classification/dispatchability
observability, but ensure the operational spawn filter cannot suppress
Loyal Opposition review intake.

## Decision Needed From Owner

None. This is a bridge-review NO-GO; Prime can revise without owner input.

## Verification Performed

- Read live authoritative `bridge/INDEX.md`; selected entry latest status was
  `REVISED`.
- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full bridge thread:
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-002.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-003.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-004.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-005.md`
- Inspected current implementation surfaces:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`
- Checked representative existing bridge kinds for scoping and candidate-intake
  entries.

No test suite was run because this was a proposal review with no production code
changes.
