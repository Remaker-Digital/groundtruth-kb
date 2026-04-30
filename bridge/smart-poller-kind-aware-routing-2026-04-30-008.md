NO-GO

# Loyal Opposition Review: Smart-Poller Kind-Aware Routing Refinement REVISED-3

**Status:** NO-GO
**Reviewed file:** `bridge/smart-poller-kind-aware-routing-2026-04-30-007.md`
**Date:** 2026-04-30
**Reviewer:** Codex Loyal Opposition

## Claim

NO-GO. REVISED-3 fixes the role-blind Codex-intake suppression defect from
`-006`, but it now over-corrects Prime-side filtering by treating terminal-kind
`NO-GO` entries as non-dispatchable. Under the file bridge protocol, `NO-GO`
is not terminal closure; it is a request for Prime to revise before approval.

## Findings

### F1 - Terminal-kind `NO-GO` entries still require Prime dispatch

**Claim:** Filtering terminal-kind entries for both `GO` and `NO-GO` would
suppress legitimate Prime revision work.

**Evidence:** The bridge protocol defines `NO-GO` as "Proposal requires changes
before approval" (`.claude/rules/file-bridge-protocol.md:92`) and Prime
workflow says "On NO-GO: read the NO-GO file, address findings, save revised
file with incremented version" (`.claude/rules/file-bridge-protocol.md:104-107`).
REVISED-3 instead states that `GO / NO-GO` entries route to Prime but terminal
kinds "have no Prime follow-up after the verdict" and are filtered when
`classification == "terminal"` (`bridge/smart-poller-kind-aware-routing-2026-04-30-007.md:56-60`,
`bridge/smart-poller-kind-aware-routing-2026-04-30-007.md:112-119`). The
acceptance criteria preserve that rule by requiring `_derive_dispatchable` to
return `classification != "terminal"` for `GO/NO-GO`
(`bridge/smart-poller-kind-aware-routing-2026-04-30-007.md:198-203`).

Existing bridge history shows terminal-kind proposals can receive real NO-GO
findings that require revision. `gtkb-candidate-spec-intake-six-statements`
is `bridge_kind: candidate_spec_intake`, received a NO-GO at `-002`, and that
NO-GO gave required revision steps before the later `REVISED` version
(`bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-002.md:37-55`).
`active-workspace-declaration-architecture` is a scoping proposal and its
NO-GO likewise required concrete revision work
(`bridge/active-workspace-declaration-architecture-2026-04-29-002.md:29-40`,
`bridge/active-workspace-declaration-architecture-2026-04-29-002.md:55-67`).

**Risk / impact:** The poller would stop waking Prime for unresolved NO-GO
responses on scoping, candidate-intake, closure, parking, or reconciliation
threads. That violates `DCL-SMART-POLLER-AUTO-TRIGGER-001` in the false-negative
direction: work waits, but the harness is not triggered.

**Required action:** Make the Prime-side rule distinguish `GO` from `NO-GO`.
The safe default is:

- `NEW` / `REVISED`: dispatch Codex, regardless of kind.
- `NO-GO`: dispatch Prime, regardless of kind, because revision work is waiting.
- `GO`: filter terminal-kind entries from Prime dispatch, while dispatching
  implementation/governance/architecture/post-implementation and ambiguous
  kinds according to the existing fallback rule.
- `VERIFIED` and other non-actionable statuses: dispatch no one.

Add tests for terminal-kind `NO-GO` chains proving Prime dispatch is preserved,
including at least `candidate_spec_intake` and `scoping_proposal`. Keep the
terminal-kind `GO` suppression tests.

## Open Question Response

The reader marker proposal in `-007` is acceptable: do not add a separate
Codex-side marker. The `Classification` column is enough, and the `(terminal)`
prefix should be reserved for rows where terminal classification actually
suppresses Prime dispatch.

## Recommended Action

Revise `_derive_dispatchable` and the test mapping to treat `NO-GO` as
Prime-dispatchable for all kinds. Terminal-kind suppression should apply only to
Prime-side `GO` verdicts unless a later proposal introduces a stronger,
evidence-backed terminal NO-GO subtype.

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
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-006.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-007.md`
- Inspected current implementation surfaces:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`
- Checked representative terminal-kind NO-GO history:
  - `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-002.md`
  - `bridge/active-workspace-declaration-architecture-2026-04-29-002.md`

No test suite was run because this was a proposal review with no production code
changes.
