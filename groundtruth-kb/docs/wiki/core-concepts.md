# Core concepts

**Status:** Current concise model
**Reviewed:** 2026-09-26

## Programs, projects, and work items

A program plans and sequences projects. A project is the authorization,
completion, commit, and activation unit. A work item belongs to one project.

Project authorization is one field on the project record: `authorized` or
`not authorized`. It orders work. It is not a permission token, artifact,
packet, receipt, or agent security mechanism.

## Specifications and tests

Current formal records define applicable behavior. New implementation work
requires specification linkage and an executable test. A recorded test
definition is not proof that the test ran or passed.

## Roles and contexts

Prime Builder and Loyal Opposition roles belong to immutable session contexts,
not to tools, vendors, models, or permanent agent identities. Prime Builder
proposes and implements. Loyal Opposition independently reviews, tests,
verifies, and performs the project commit when the complete project is ready.

## Bridge coordination

A bridge item is authoritative only when dispatched and received for its next
coordination action. It is ephemeral thereafter. A claim reserves the right to
deliver one exact next artifact; it does not give an agent ownership of the
work-item thread.

The ordinary implementation sequence is:

```text
NEW proposal -> GO -> implementation -> READY report -> VERIFIED
```

Rejected proposals return through `NO-GO` and `REVISED`. Rejected reports return
through `NOT-READY` and a corrected `READY`. Dispatcher may select work but never
authors proposals or verdicts.

## Verification, commit, and activation

`VERIFIED` records independent review of exact work-product bytes. It does not
assert that a commit exists. When every work item in the project is verified in
its final form, the verifying role commits the complete project as one cohort.
That Git commit activates the work and establishes terminality.

## Current authority

Canonical records are served by the native PostgreSQL domain service through
supported CLI and service APIs. Do not use retired SQLite/`groundtruth.db`,
MemBase, Deliberation Archive, PAUTH, DECISION records, raw coordination tables,
or persistent bridge content as current authority.
