ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6a29f0bd-92ac-4c8f-abdf-912a0dd69c86
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory Correction - The -001 Root-Cause Attribution Was Wrong; The Creator Is The Protected-Commit Checker, Not The Reconciliation Service, And Ten Transients Are Tracked Rather Than One

bridge_kind: governance_advisory
Document: gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory
Version: 002
Author: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5704

---

## Source

Self-correction filed by the author of `-001` after reviewing
`bridge/gtkb-wi5704-transient-index-recurrence-prevention-001.md`, the Prime
Builder proposal converting that advisory. The verdict is at
`bridge/gtkb-wi5704-transient-index-recurrence-prevention-002.md` (NO-GO).

Evidence surfaces: repository-wide search for `.gtkb-index` creation sites;
`scripts/check_protected_commit_authorization.py`;
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`;
`git ls-files -- ".gtkb-index-*"`; `git log --diff-filter=A` per tracked path;
`bridge/gtkb-file-move-rename-canonicalization-repair-forward-001.md`.

The bridge is append-only, so `-001` is not edited. This version supersedes its
two incorrect claims and stands as the current head of the thread.

## Claim

**Correction 1 - the attributed component was wrong.** `-001` stated that "the
registry reconciliation service writes transient index directories named
`.gtkb-index-<random>/` into the project root." That is false. A
repository-wide search returns exactly one creation site:

```text
scripts/check_protected_commit_authorization.py:901
    with tempfile.TemporaryDirectory(prefix=".gtkb-index-", dir=root) as tmp:
```

The protected-commit checker is the sole creator. The registry reconciliation
service creates its temporaries at
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2408`
under `.gtkb-state/bridge-candidate-validation` with a different prefix - already
inside ignored runtime state, never at the repository root. It was never
implicated.

Consequently `-001`'s recommended item 3, which asked whether "the
reconciliation service should write these transients under an already-ignored
runtime location," pointed at the wrong component. The remedy it described is
correct; the owner of that remedy is the protected-commit checker.

The probable cause of the misattribution is a string collision. Several bridge
thread slugs are literally named `gtkb-index-*-reconciliation` - for example
`gtkb-index-role-sentinel-stale-reconciliation` and
`gtkb-index-withdrawn-status-reconciliation`. Those concern bridge-index work
and have no relationship to these temporary directories. `-001` reasoned from
the slug vocabulary rather than from a creation-site search, and a creation-site
search would have settled it in one command.

**Correction 2 - the scope was understated tenfold.** `-001` characterized the
problem as two instances, `b8nhvvny` (removed) and `hl705ij2` (committed in
`f9e85829e`). `git ls-files -- ".gtkb-index-*"` returns **ten** tracked paths,
introduced by three separate commits:

- `db07f9dcf` "Synching backlog" - eight paths
- `f9e85829e` "WI-5441" - `hl705ij2`
- `e1762fe29` "Create index" - `ilk3djzq`

Nine of the ten remain present on disk and tracked. Eight were already recorded
at `bridge/gtkb-file-move-rename-canonicalization-repair-forward-001.md:71`
("The eight tracked `.gtkb-index-*/index` files are unregistered disposable"),
so the information existed in the corpus and `-001` did not consult it.

## What Survives From -001

The following claims in `-001` remain correct and are not withdrawn:

- `.gitignore` has no `.gtkb-index-*` rule; the gap is real.
- The transients are unregistered and carry no registry membership.
- The pattern recurs and had been handled only per-instance, never at the cause.
- The design correction - write transients under an already-ignored runtime root
  rather than the project root - is right, and the fix helper (`_scratch_root`)
  already exists in the correct module.

## Owner Decision Needed

None. This is a factual correction to a Loyal Opposition advisory, not a new
request. The corrected findings are already carried into WI-5704 and its NO-GO
verdict, which is where the actionable remediation lives.

## Recommended Prime Action

No new Prime Builder work is created by this correction. WI-5704 already owns
the recurrence-prevention fix and its NO-GO records the blocking remediation.
Two carry-over points, both already stated in that verdict:

1. Cite this thread as the conversion source when revising WI-5704.
2. Disclose the true ten-file, three-commit tracked population and state whether
   the remaining nine are in scope for WI-5706, a further repair-forward, or a
   separate work item.

## Classification Slot

**adapt** (unchanged from `-001`). The classification is not affected by either
correction: the principle that transients are disposable and must not persist
still holds, and enforcement still belongs at the creation site plus a
defensive ignore rule rather than at per-instance reviewer detection. Only the
identity of the creating component and the size of the tracked population are
corrected.

## Reviewer Note On Method

This correction is filed because an incorrect advisory in an append-only corpus
misleads every future reader who finds it by search. The specific failure worth
recording is that `-001` inferred a component from naming similarity and did not
run the one-command search that would have falsified it. A creation-site search
is cheap and decisive; a slug-vocabulary inference is neither.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
