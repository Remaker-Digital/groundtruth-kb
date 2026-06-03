# _test_golden_dual_agent — File Bridge Index

<!-- This file is the single coordination artifact for the Prime Builder ↔
     Loyal Opposition file bridge. Both agents read and write this file.
     Newest entries are at the top. -->

## Statuses

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime | Fresh proposal awaiting review |
| REVISED | Prime | Updated proposal after a NO-GO |
| GO | Codex | Proposal approved for implementation |
| NO-GO | Codex | Proposal requires changes before approval |
| VERIFIED | Codex | Post-implementation verification passed |
| ADVISORY | Loyal Opposition | Owner-initiated advisory report; non-dispatchable |
| DEFERRED | Owner | Owner-directed parked bridge state; non-actionable |
| WITHDRAWN | Owner / governed correction | Terminal withdrawal or retirement state |

## Prime Workflow

1. Write proposal as `bridge/{{name}}-001.md`
2. Insert `NEW: bridge/{{name}}-001.md` at the top of this file
3. On GO: implement; on NO-GO: revise and insert REVISED entry; skip ADVISORY, DEFERRED, WITHDRAWN, and VERIFIED

## Codex Workflow

1. Scan this file for NEW or REVISED entries; skip ADVISORY, DEFERRED, WITHDRAWN, and VERIFIED
2. Review the indicated file, write response as next incremented version
3. Insert GO or NO-GO verdict line at the top of that document entry

<!-- Add new document entries below this line -->
