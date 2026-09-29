# GTKB and Git

**Status:** Current concise model
**Reviewed:** 2026-09-26

Git is the durable source of the authored work product and its history. GTKB's
native service coordinates specifications, tests, projects, work items,
authorization, review, and finalization; Git is not used as a replacement
workflow database or approval log.

## Project completion

A project is the unit that completes together. Its work items can be reviewed
independently, but a verified work product is held until every work item in the
project is `VERIFIED` in its final form.

When the last item is verified, the verifying Loyal Opposition context performs
one project commit that:

- contains the complete verified project work product;
- cites every retired work item as `(WI-NNNN)`;
- excludes bridge payloads;
- excludes generated harness projections and other operational derivations; and
- preserves unrelated and foreign worktree content.

That project commit activates the work product and establishes work-item
terminality. Publication to the registered remote provides durability and
sharing; it is not a second activation decision.

## Review and byte identity

`VERIFIED` records review of exact final bytes. It does not claim that a commit
exists. If verified bytes change before the project commit, the affected work
item returns for fresh independent verification.

If project finalization fails, preserve the reviewed bytes and record the typed
failure in canonical state. Do not invent a Dispatcher-authored verdict or
rewrite Git history to force completion.

## Repository discipline

- Use isolated checkouts for independent work when required.
- Keep commits limited to the reviewed project cohort.
- Do not sweep unrelated, generated, bridge, or foreign bytes into the commit.
- Do not rewrite ordinary or formal history; reversal is new forward work.
- Do not treat a pull-request merge, branch name, or remote publication as a
  substitute for GTKB review and project finalization.
