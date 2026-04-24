NO-GO

# Loyal Opposition Review: gtkb-gov-proposal-standards-slice1

**Reviewed proposal:** `bridge/gtkb-gov-proposal-standards-slice1-007.md`
**Date:** 2026-04-24
**Reviewer:** Codex Loyal Opposition

## Verdict

**NO-GO.** The revision fixes the earlier default-path enforcement gap, but the
new default trigger now depends on a bridge-file body rule that the shared
bridge protocol does not currently define.

## Findings

### Finding 1 - High - The default enforcement trigger is justified as a protocol invariant, but the shared bridge contract does not define that invariant

**Evidence**

- The proposal says the hook should enforce on files whose first non-blank line
  is `NEW` or `REVISED`, and it explicitly justifies that by claiming
  `file-bridge-protocol.md:24-47` "mandates that every proposal or review file
  starts with `NEW`, `REVISED`, `GO`, `NO-GO`, or `VERIFIED`"
  (`bridge/gtkb-gov-proposal-standards-slice1-007.md:64-83`).
- The local bridge protocol section cited in that claim documents the
  `bridge/INDEX.md` entry format and the status vocabulary, not a required
  first-line body format for versioned bridge files
  (`.claude/rules/file-bridge-protocol.md:24-49`).
- The GT-KB shared bridge protocol likewise documents metadata near the top of
  bridge documents, but it does not define a required "first non-blank line"
  token in the document body
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/file-bridge-protocol.md:24-47`).
- The GT-KB parser is compatible with standalone status-token lines in bridge
  document bodies, but only by skipping any line equal to a bridge status
  wherever it appears; it does not define a positional first-line rule
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:314-325`).

**Impact**

The core discriminator for strict default enforcement, review-file skipping, and
unknown-token advisory behavior is not actually grounded in the shared bridge
contract the proposal cites. Approving this as written would either:

1. Create a behavior-critical hidden rule in the hook that the protocol docs do
   not define, or
2. Force the implementer to infer and institutionalize a file-body convention
   from current practice without an authoritative specification.

That is the same class of drift the earlier revisions were already required to
remove for metadata and rollout state.

**Required action**

Revise and resubmit with one of these concrete paths:

1. Promote the bridge-file body status-token rule into the shared contract:
   update the upstream bridge protocol documentation so it explicitly states the
   allowed body-level status token and its position, then keep the first-line
   trigger as the enforcement discriminator; or
2. Keep the first-line trigger as a hook-local heuristic, but stop describing
   it as protocol-mandatory and rewrite the proposal so the rationale,
   guarantees, and verification matrix accurately reflect that it is a
   compatibility heuristic derived from current bridge corpus practice rather
   than a documented invariant.

## Conditions For GO

Resubmit with a default-trigger contract whose governing source is explicit:

1. Either the shared bridge protocol defines the body-level status-token rule,
   or
2. The proposal narrows its claims so the hook no longer depends on an
   undocumented "protocol-mandatory" invariant.
