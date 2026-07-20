# WI-5172 Shared Carrier Finalization Waiver

Owner decision: approve WI-5172 carrier waiver.

## Decision

Mike approves a by-reference / combined-sequenced finalization waiver for the shared `groundtruth.db` carrier in `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator`.

## Context

The WI-5172 implementation report at `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-013.md` is non-terminal because `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-014.md` rejected finalization on shared-carrier grounds. The blocking path is `groundtruth.db`, which is a binary MemBase carrier and cannot be hunk-split. The same non-terminal report blocks the Envelope Protocol Slice A implementation-start gate through `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.

## Authorized Use

Prime Builder may re-file WI-5172 with an explicit by-reference / combined-sequenced finalization waiver section citing this decision. The waiver authorizes Loyal Opposition to evaluate WI-5172 terminal verification without treating the co-resident `groundtruth.db` carrier appends as unapproved merely because they share the same binary carrier.

The waiver does not approve unrelated source/config/test changes, does not bypass bridge review, does not authorize Git history rewrite, push, release, deployment, credentials, or destructive cleanup, and does not mark WI-5172 or the Envelope Protocol program complete without independent `VERIFIED`.

## Owner Evidence

Prompted owner decision: approve the WI-5172 by-reference / combined-sequenced finalization waiver for the shared `groundtruth.db` carrier, or keep pursuing the committed-baseline path first.

Owner answer: `Approve WI-5172 carrier waiver`.

## Linked Artifacts

- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-013.md`
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-014.md`
- `bridge/gtkb-envelope-protocol-slice-a-authority-set-004.md`
- `WI-5172`
- `PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL`
