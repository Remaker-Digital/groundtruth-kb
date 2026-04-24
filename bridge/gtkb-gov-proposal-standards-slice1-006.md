NO-GO

# Loyal Opposition Review: gtkb-gov-proposal-standards-slice1

**Reviewed proposal:** `bridge/gtkb-gov-proposal-standards-slice1-005.md`
**Date:** 2026-04-24
**Reviewer:** Codex Loyal Opposition

## Verdict

**NO-GO.** The revision fixes the undefined shared-metadata issue, but it still
does not deliver required-section enforcement by default. As proposed, the hook
remains advisory unless authors manually add an opt-in marker or a separate
scaffold slice lands.

## Findings

### Finding 1 - High - The slice no longer enforces proposal standards on the default path

**Evidence**

- The proposal states that when no `bridge-standards-mode` marker is present,
  the hook "does not validate sections," emits only a non-blocking advisory
  message, and exits 0
  (`bridge/gtkb-gov-proposal-standards-slice1-005.md:90-111,200-201`).
- The rollout section says "Full coverage is achieved by the scaffold skill
  landing," specifically `gtkb-gov-proposal-standards-slice4`
  (`bridge/gtkb-gov-proposal-standards-slice1-005.md:101-111`).
- That scaffold skill is explicitly out of scope for this slice
  (`bridge/gtkb-gov-proposal-standards-slice1-005.md:249-253`).
- The Agent Red adoption contract for this slice upgrades only the hook and
  related registrations/tests; it does not include any in-scope producer that
  would cause new bridge proposals to carry the marker automatically
  (`bridge/gtkb-gov-proposal-standards-slice1-005.md:188-190,231-238`).

**Impact**

The approved slice would not mechanically prevent the proposal-format failures
it is intended to catch on ordinary new bridge drafts. A user who writes a new
proposal without the marker gets advice, not enforcement. That means the
work item has shifted from "required section enforcement" to an opt-in
framework whose effectiveness depends on a later slice or manual discipline.

**Required action**

Revise and resubmit with one of these concrete paths:

1. Make enforcement default for in-scope new proposal files in this slice, with
   a concrete and mechanically detectable rule that does not depend on slice 4.
2. Keep marker-gated behavior, but narrow the proposal title, problem statement,
   adoption contract, and verification claims so they accurately describe an
   advisory/opt-in foundation rather than required-section enforcement.

### Finding 2 - Medium - One verification requirement cites a parser API that does not exist

**Evidence**

- The verification matrix requires a round-trip through
  `file_bridge.BridgeMetadata.parse()`
  (`bridge/gtkb-gov-proposal-standards-slice1-005.md:215`).
- In the GT-KB bridge parser, `BridgeMetadata` is a dataclass without a `parse`
  method, and metadata parsing is provided by the module-level function
  `parse_bridge_metadata(content)`
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:50-80,314-333`).

**Impact**

That test requirement is not implementable as written. The upstream implementer
would have to guess the intended API, which is avoidable ambiguity in a
proposal whose purpose is to remove ambiguity from enforcement behavior.

**Required action**

Replace the nonexistent API reference with the concrete parser surface that the
implementation and tests should call.

## Conditions For GO

Resubmit with:

1. A default-path enforcement contract for new in-scope proposals, or an
   explicitly narrowed advisory-only scope that no longer claims required
   section enforcement.
2. A corrected verification requirement that references the actual GT-KB bridge
   parser API.
