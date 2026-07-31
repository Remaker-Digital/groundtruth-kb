ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6a29f0bd-92ac-4c8f-abdf-912a0dd69c86
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory - Transient Reconciliation Index Directories Are Not Gitignored, So Each Reconciliation Run Leaves A Multi-Megabyte Binary Candidate For The Next Broad Commit

bridge_kind: governance_advisory
Document: gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

---

## Source

Read-only observation during a scheduled Loyal Opposition queue run in session
`6a29f0bd-92ac-4c8f-abdf-912a0dd69c86`, branch `research`, 2026-07-28 UTC. The
LO queue was empty; this finding comes from verifying the WI-5441 finalization
commit that the owner made at `f9e85829e`.

Evidence surfaces read: `git show --format="" --name-only f9e85829e`,
`.gitignore`, `config/registry/sot-artifacts.toml`,
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-013.md`,
`gt backlog list --contains gtkb-index`, and the on-disk
`.gtkb-index-hl705ij2/` directory.

## Claim

The registry reconciliation service writes transient index directories named
`.gtkb-index-<random>/` into the project root. `.gitignore` contains no entry
matching that pattern, so each one is immediately visible to `git status` as an
untracked directory and is swept into any subsequent broad `git add`.

This has now recurred and escalated. It was previously handled per-instance,
never at the root cause.

## Evidence

**Prior instance, caught and removed manually.**
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-013.md` F3 records:
"The canonical registry reader plus `RegistryResolver` returned no membership for
`.gtkb-index-b8nhvvny/`. After resolving the absolute path inside `E:/GT-KB`,
that disposable transient reconciliation index was removed." That was detection
and cleanup of one instance, not prevention.

**Current instance, committed to permanent history.** `f9e85829e` contains 17
files. Sixteen are the intended WI-5441 finalization set. The seventeenth is
`.gtkb-index-hl705ij2/index`, a 2,510,618-byte binary written 2026-07-28
08:37:06 local, during the reconciliation runs. Because GT-KB bridge and git
history are append-only, that blob is now permanent absent a history rewrite.

**Root cause is a missing ignore rule.** `Select-String` for `gtkb-index` against
`.gitignore` returns no matches. Nothing prevents the next occurrence.

**No existing coverage.** A `Select-String` sweep of `bridge/*.md` for
`gtkb-index` returns matches only in (a) unrelated bridge threads whose slugs
begin `gtkb-index-*` and concern bridge-index work, and (b) the WI-5441 thread
files that record the per-instance `b8nhvvny` cleanup. `gt backlog list --json
--contains "gtkb-index"` returns zero rows. No advisory or work item addresses
the ignore-rule gap.

## Risk And Impact

**Confirmed, low severity now.** The committed transient is not a registry
member: `config/registry/sot-artifacts.toml` contains no `gtkb-index` record. So
this does not corrupt current membership state and does not invalidate the
WI-5441 VERIFIED verdict at `-020`.

**Repository weight.** Roughly 2.5 MB of binary per occurrence, permanently. Two
occurrences are known within two days.

**The escalation path is the real concern.** The transient is now git-tracked.
The reconciliation service admits candidates through typed observers that include
`physical_census` and `registered_dependency_closure`. A tracked file is a
stronger candidate signal than an untracked one. A future reconciliation run
could therefore propose the transient index as a load-bearing member of the very
registry whose completeness this program exists to establish. That would be a
self-inflicted membership defect on the same subsystem.

**Recurrence is the multiplier.** Because the cause is a missing ignore rule
rather than a one-off mistake, every reconciliation run followed by a broad
commit reproduces it. The per-instance remedy used at `-013` requires a reviewer
to notice the directory each time; the `f9e85829e` commit is the case where
nobody did.

## Recommended Prime Action

The prior response pattern (detect and delete per instance) is correct in kind
but wrong in placement.

1. Add an ignore rule covering the transient pattern, e.g. `.gtkb-index-*/` in
   `.gitignore`. This is the whole preventive fix and is a one-line change.
2. Decide the disposition of the already-committed `.gtkb-index-hl705ij2/index`.
   Removing it from the working tree and committing the deletion is
   straightforward; removing it from history is a rewrite and is almost certainly
   not worth it for 2.5 MB. This advisory recommends deleting it going forward
   and leaving history alone.
3. Consider whether the reconciliation service should write these transients
   under an already-ignored runtime location such as `.gtkb-state/` instead of the
   project root. Root-level scratch directories are visible to every `git status`
   and every broad commit, and the project root is exactly where the root-boundary
   rule concentrates attention. This is the more durable fix and is the reason
   this advisory is classified `adapt` rather than `adopt`.
4. Add a deterministic check that fails when a `.gtkb-index-*` path is staged, so
   the guard does not depend on a reviewer noticing.

Items 1 and 4 are cheap and prevent recurrence. Item 3 is the design correction
and is the appropriate subject of a future implementation proposal.

## Owner Decision Needed

None to file this advisory. Two decisions arise only if Prime Builder converts
it: whether to accept the design correction in item 3 (relocating transients out
of the project root), and whether to leave the already-committed 2.5 MB blob in
history rather than rewrite. Prime Builder should route items 1 through 4
through the normal owner-grilling and proposal path before implementing; this
advisory is not implementation approval.

## Classification Slot

**adapt.** The core pattern from `-013` (transient indexes are disposable and
must not persist) is correct and is adopted unchanged. What is adapted is its
placement: enforcement moves from per-instance reviewer detection to a
preventive ignore rule plus a staged-path check, and ideally to writing the
transients under an already-ignored runtime location. Prime Builder should file
a normal implementation proposal converting items 1 through 4.

## Prior Deliberations

- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-010.md` - the
  original F3 detection of `.gtkb-index-b8nhvvny/`.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-013.md` - the
  per-instance removal of that directory.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-020.md` - the
  terminal VERIFIED whose finalization commit swept in the current instance.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - the
  authoritative-hygiene direction this finding serves.

A `gt deliberations search` on registry transient index and worktree hygiene
terms surfaced no prior decision on the ignore-rule question. No prior decision
is revisited or contradicted by this advisory.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
