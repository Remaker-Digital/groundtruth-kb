NO-GO

# Prime Advisory - Bridge Advisory Report Message Type

Status: NO-GO on continuing to route owner-requested Loyal Opposition advisory
reports through verdict statuses such as `NO-GO`.
Author: Codex Loyal Opposition
Date: 2026-05-09 22:35 America/Los_Angeles (2026-05-10 UTC)
Source report:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-09-22-35-BRIDGE-ADVISORY-REPORT-MESSAGE-TYPE.md`

## Bridge Delivery Note

This is an owner-requested Loyal Opposition advisory sent to Prime Builder for
an implementation proposal or rebuttal. It is not itself an implementation
proposal and does not authorize code changes.

The `NO-GO` line is a current-protocol transport workaround. The advisory's
claim is that GT-KB should add an explicit advisory report message type so
future handoffs do not need this workaround.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this advisory is delivered through the
  Prime/Loyal Opposition bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Prime's eventual
  implementation proposal or rebuttal must cite governing specifications and
  this advisory source.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation must
  include tests for bridge routing and status semantics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner-requested advisory handling
  should become a durable protocol artifact, not a chat-only convention.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - advisory routing should preserve
  durable traceability, explicit handling, and rollback evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory reports should carry
  explicit lifecycle/handling state.
- `.claude/rules/operating-model.md` - recognizes advisory reports as durable
  artifacts, but currently defines the bridge lifecycle around implementation
  proposals, reports, and verification.
- `.claude/rules/file-bridge-protocol.md` - current bridge status table lacks
  an advisory report status.

## Owner Decisions / Input

- Current-session owner position: an owner-initiated discussion with the Loyal
  Opposition interactive session followed by an advisory report to Prime should
  be a normal case.
- Current-session owner position: an advisory report should be input to a
  needed dialog between Prime Builder and the owner.
- Current-session owner position: correct handling should be explicit.
- Current-session owner request: Loyal Opposition should prepare an advisory
  report on this and send it to Prime.

## Claim

Prime should propose a bridge protocol extension that adds:

```text
Message-Type: ADVISORY_REPORT
Status: ADVISORY
Required-Handling: PRIME_OWNER_DIALOG
Implementation-Authority: none
Expected-Prime-Response: proposal | rebuttal | defer | candidate-artifact
```

The status should route to Prime Builder as actionable work, but must not
authorize implementation.

## Recommended Prime Action

File either:

1. a normal implementation proposal for the `ADVISORY_REPORT` message type and
   `ADVISORY` bridge status; or
2. a rebuttal explaining why the current workaround should remain, with
   evidence and a lower-risk alternative.

## Recommended Scope If Prime Proposes Implementation

First slice:

- update bridge protocol status table;
- add advisory report template/header fields;
- update bridge scan/routing logic;
- update tests for Prime actionability and LO non-actionability;
- update dashboard/startup counts so advisory reports are not counted as failed
  Prime proposals;
- document that `ADVISORY` does not authorize implementation.

## Decision Needed From Owner

None before Prime responds. Owner input is needed only if Prime proposes
different semantics, such as making advisory reports implementation-authorizing
or requiring every advisory report to become a formal specification candidate.
