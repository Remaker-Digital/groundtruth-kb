GO

# GT-KB v0.6.0 Release Bundle Review - Tag-Move Addendum

**Status:** GO with tag-move safety conditions
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed revision:** `bridge/gtkb-v060-release-003.md`
**Prior context reviewed:** `bridge/gtkb-v060-release-001.md`, `bridge/gtkb-v060-release-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO. Moving annotated tag `v0.6.0` from `34aad9a` to `3786f49` is the preferred
remediation, provided Prime performs the safety checks below immediately before
deleting or re-pushing the tag.

The original tag target is not publishable through the repo's self-gating
release workflow because it contains stale v0.5.0 documentation text. The new
target is a docs-only follow-up commit on `origin/main`, and the required
branch workflows are green on that exact SHA. Because no GitHub Release exists
and PyPI has no `0.6.0` artifact yet, the tag move is lower-risk than publishing
a known-failing release or cutting a semantically empty `v0.6.1`.

## Evidence

- `git log --oneline --decorate -5` in `groundtruth-kb` shows `3786f49`
  (`fix(docs): bump stale v0.5.0 references to v0.6.0`) at
  `HEAD -> main, origin/main, origin/HEAD`, followed by `34aad9a`
  (`chore(release): prepare v0.6.0`) with local tag `v0.6.0`.
- `git show-ref --dereference refs/tags/v0.6.0` shows local annotated tag
  object `d677b9e1ef4f8b0a618bb2f1398f99fea146fbfb` dereferencing to
  `34aad9a591b79f77eb6eb7bf7d25e75908ef6f5e`.
- `git ls-remote --tags origin 'refs/tags/v0.6.0*'` shows the remote annotated
  tag also dereferencing to `34aad9a591b79f77eb6eb7bf7d25e75908ef6f5e`.
- `gh release view v0.6.0 --json tagName,url,isDraft,isPrerelease,publishedAt,targetCommitish`
  returned `release not found`.
- `python -m pip index versions groundtruth-kb` reports latest available
  version `0.5.0`; available versions are `0.5.0`, `0.4.0`, and `0.3.1`.
- `git diff --name-status 34aad9a..3786f49` reports only:
  `docs/architecture/product-split.md`,
  `docs/groundtruth-kb-executive-overview.md`, and `docs/start-here.md`.
  `git diff --stat 34aad9a..3786f49` reports 3 files changed, 4 insertions,
  and 4 deletions.
- `git show 34aad9a:docs/start-here.md | rg -n "0\.5\.0|0\.6\.0"` shows stale
  `0.5.0` text at lines 35 and 46. The same check against
  `docs/architecture/product-split.md` and
  `docs/groundtruth-kb-executive-overview.md` shows stale `0.5.0` text at
  lines 112 and 106 respectively.
- Current `docs/start-here.md:35`, `docs/start-here.md:46`,
  `docs/architecture/product-split.md:112`, and
  `docs/groundtruth-kb-executive-overview.md:106` now reference `0.6.0`.
- `python scripts/check_docs_cli_coverage.py` at `3786f49` passed with
  `All documentation checks passed.`
- `gh run list --branch main --json ... --limit 50` shows all seven workflows
  on `3786f4921ce85780f6c797e1d3362787e126ab24` completed successfully:
  `Docstring Coverage`, `Docs Check`, `Docs`, `Security`, `CodeQL`,
  `SonarCloud`, and `CI`.
- The same run list shows the `Docs Check` workflow on
  `34aad9a591b79f77eb6eb7bf7d25e75908ef6f5e` completed with conclusion
  `failure`, while `CI` on that SHA completed with conclusion `success`.
- `.github/workflows/publish.yml:18-20` triggers publication on a published
  GitHub Release. `.github/workflows/publish.yml:39-61` runs the base gate,
  including `python scripts/check_docs_cli_coverage.py`. The branch CI gate at
  `.github/workflows/publish.yml:89-132` resolves annotated tags with
  `git rev-list -n 1 "$TAG"` and requires a completed successful `CI` run for
  that exact commit.

## Rationale

The publish workflow checks the release ref content, not just the state of
`main`. Leaving `v0.6.0` at `34aad9a` would make `ci-gate-base` evaluate stale
docs and fail deterministically. Rerunning that workflow would not help unless
the tag target changes.

Cutting `v0.6.1` instead would leave a public `v0.6.0` tag with no matching
GitHub Release or PyPI artifact. That creates needless release taxonomy debt
for a four-line docs correction. Amending `34aad9a` is worse because it would
rewrite `main`; the proposed tag move preserves branch history.

The tag move remains a shared-state mutation, but the risk is bounded by the
verified absence of a GitHub Release and PyPI artifact for `0.6.0`, and by the
fact that `34aad9a` remains preserved as normal commit history.

## Required Action Items

1. Immediately before deleting the tag, re-run the external-state checks:
   `gh release view v0.6.0`, `python -m pip index versions groundtruth-kb`, and
   `git ls-remote --tags origin 'refs/tags/v0.6.0*'`. Stop and return to the
   bridge if a GitHub Release exists, PyPI already lists `0.6.0`, or the remote
   tag no longer dereferences to `34aad9a591b79f77eb6eb7bf7d25e75908ef6f5e`.
2. Execute the proposed tag-move sequence only after the preflight checks pass:
   delete local tag, delete remote tag, recreate annotated `v0.6.0` at
   `3786f4921ce85780f6c797e1d3362787e126ab24`, then push the tag.
3. Before creating the GitHub Release, verify both local and remote tag refs
   dereference to `3786f4921ce85780f6c797e1d3362787e126ab24`.
4. Create the GitHub Release only after the tag verification passes. Use the
   existing `release-notes-0.6.0.md` body; no release-note edit is required for
   this docs-only stale-version fix.
5. Monitor `publish.yml` through completion. If it fails, do not publish an
   alternate version until the failing job evidence is captured and reviewed.
6. In the post-implementation report, include the tag dereference evidence,
   GitHub Release URL, `publish.yml` result, PyPI `0.6.0` evidence, fresh-venv
   install evidence, `gt --version`, package `__version__`, and wheel contents
   for the three Tier A skill trees.

## Decision Needed From Owner

None. Prime may proceed with the tag move and release publish under the required
action items above.

