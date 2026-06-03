# File Bridge Protocol

The bridge between Prime Builder and Loyal Opposition uses a shared directory
of versioned markdown files governed by a single index file.

## Directory

`bridge/` at project root. All proposal, review, and verification documents
live here as numbered markdown files.

## Mandatory Specification Linkage Gate

Every implementation proposal must include a `Specification Links` section
before it can receive `GO`. The section must cite every relevant governing
specification, rule, ADR, DCL, proposal standard, or other durable specification
artifact that constrains the proposed implementation. A proposal with no linked
specification surface is invalid and must receive `NO-GO`.

Codex/Loyal Opposition MUST reject all implementation proposals that are not
linked to specifications. Without linked specifications, there MUST NOT be an
approved implementation plan.

The proposal must also state how the proposed tests derive from those linked
specifications. Codex/Loyal Opposition review must independently check the list
for omissions. If any relevant specification is missing, or if the proposed tests
do not map back to the linked specifications, the only valid verdict is `NO-GO`.

## Mandatory Specification-Derived Verification Gate

An implementation cannot receive `VERIFIED` unless the verification procedure
creates or identifies tests derived from the specifications linked in the
implementation proposal and executes those tests against the implementation.

The post-implementation report must include:

- the linked specifications carried forward from the proposal;
- a spec-to-test mapping showing which tests cover which specification clauses
  or acceptance criteria;
- the exact commands used to execute those tests;
- the observed results.

If a linked specification has no executed test coverage, Codex/Loyal Opposition
must issue `NO-GO` unless the owner explicitly approves a documented waiver for
that specific specification and risk.

## File Naming

`{descriptive-name}-{NNN}.md`

- `descriptive-name`: kebab-case description of the proposal or review topic
- `NNN`: zero-padded version number starting at 001, incremented for each
  revision or review response

Examples:
- `widget-refactor-001.md` (Prime's initial proposal)
- `widget-refactor-002.md` (Codex's review with GO or NO-GO)
- `widget-refactor-003.md` (Prime's revision after NO-GO)

## Index File

`bridge/INDEX.md` is the single coordination file. Both agents read and write
it. Format:

```
Document: {descriptive-name}
{STATUS}: bridge/{descriptive-name}-{NNN}.md
```

Each document entry starts with a `Document:` line followed by one or more
versioned file lines. The latest version is always at the top of the version
list within each entry. New document entries are inserted at the top of the
index file (after the header comments).

## Statuses

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime | Fresh proposal awaiting review |
| REVISED | Prime | Updated proposal after a NO-GO |
| GO | Codex | Proposal approved for implementation |
| NO-GO | Codex | Proposal requires changes before approval |
| VERIFIED | Codex | Post-implementation verification passed |
| ADVISORY | Loyal Opposition | Owner-initiated advisory report; non-dispatchable. |
| DEFERRED | Owner | Owner-directed parked bridge state; non-actionable until the clear/resume condition is met. |
| WITHDRAWN | Owner / governed correction | Terminal withdrawal or retirement state. |

## DEFERRED Status

`DEFERRED` is owner-only bridge parking state. It is indexed workflow state,
not a parked draft and not a Loyal Opposition verdict. A `DEFERRED` bridge file
must start with `DEFERRED`, include concrete Owner Decisions / Input evidence,
state a deferral reason, and state a clear/resume condition.

## Prime Workflow

1. Write the proposal as `bridge/{name}-001.md`
2. Open `bridge/INDEX.md` and insert a new entry at the top:
   ```
   Document: {name}
   NEW: bridge/{name}-001.md
   ```
3. Continue working on other tasks
4. Periodically scan the index for GO or NO-GO responses; skip ADVISORY, DEFERRED, WITHDRAWN, and VERIFIED as non-actionable
5. On GO: proceed with implementation
6. On NO-GO: read the NO-GO file, address findings, save revised file with
   incremented version, and insert a REVISED line at the top of that entry

## Codex Workflow

1. Periodically scan the index for NEW or REVISED entries; skip ADVISORY, DEFERRED, WITHDRAWN, and VERIFIED as non-actionable
2. Process entries starting from the oldest (bottom of the index)
3. Read the indicated file and perform the review
4. Save review findings as a new version with incremented number
5. Insert the verdict line at the top of that entry's version list (GO or NO-GO)

## Post-Implementation Verification

After Prime implements a GO'd proposal:
1. Prime saves a post-implementation report as a new version with incremented number
2. Prime inserts a NEW line at the top of that entry
3. Codex reviews and responds with VERIFIED or NO-GO

## Index Maintenance

When `INDEX.md` exceeds ~200 lines, the agent inserting a new entry may remove
the oldest entries from the bottom of the file. Archived entries and their
corresponding bridge files remain on disk for historical reference.

## Guardrails

- Both agents must read the full entry (all versions) before acting on any
  single version
- Never delete bridge files — they form the audit trail
- If both agents write to INDEX.md simultaneously, the second writer must
  re-read and merge (simple append conflict resolution)
- The index is the source of truth for workflow state — not the files themselves
