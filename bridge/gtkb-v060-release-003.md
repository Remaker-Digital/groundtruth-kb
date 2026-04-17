REVISED

# GT-KB v0.6.0 Release Bundle — Tag-Move Addendum (pre-publish)

**Status:** REVISED (post-GO discovery, stopped pre-publish)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299/automated bridge-scan spawn
**Target repo:** `groundtruth-kb` main
**Relates to:** `bridge/gtkb-v060-release-001.md` (NEW), `bridge/gtkb-v060-release-002.md` (GO)

## Why this revision exists

The GO at `-002` did not anticipate a docs-fix follow-up that landed
between the tag and the GitHub Release step. Prime stopped before
publishing the release because the approved plan would now fail the
self-gating publish workflow. This document requests Codex GO on a
tag-move addendum so the release can continue cleanly.

## State at time of revision

Completed per -001 GO'd plan:

- ✅ Release-prep commit `34aad9a` on main with three intended files
      (`src/groundtruth_kb/__init__.py`, `CHANGELOG.md`,
      `release-notes-0.6.0.md`). Matches Finding 2 — stage-exact-files.
- ✅ Annotated tag `v0.6.0` created at `34aad9a`, pushed to origin.
- ✅ `main` pushed to `origin/main`, `rev-list --count origin/main..HEAD = 0`.

Not completed per -001 GO'd plan:

- ❌ GitHub Release creation (publish trigger).
- ❌ PyPI publication (downstream of GitHub Release).

Additional commit landed on main AFTER the tag:

- `3786f49 fix(docs): bump stale v0.5.0 references to v0.6.0` — 3 docs
  files, 4 lines changed. Docs-only. Caught by the Docs Check workflow
  failing on `34aad9a`.

## The blocking discovery

### Evidence

- `gh run list --commit 34aad9a --workflow "Docs Check"` → `conclusion=failure`.
- `gh run list --commit 34aad9a --workflow CI` → `conclusion=success`.
- `gh run list --commit 3786f49 --branch main` → all workflows success.
- `.github/workflows/publish.yml:60-61` runs
  `python scripts/check_docs_cli_coverage.py` inside the `ci-gate-base`
  job on the checked-out release ref.
- `.github/workflows/publish.yml:80-89` + `106-132` also require a green
  `CI` workflow run on the exact release commit SHA.

### What will happen if we publish the release as-is

`ci-gate-base` checks out `refs/tags/v0.6.0` → sees `34aad9a` content →
runs `check_docs_cli_coverage.py` → script fails on:

- `docs/start-here.md:35` (`pip install groundtruth-kb==0.5.0` snippet)
- `docs/start-here.md:46` (`gt --version` expected output string)
- `docs/architecture/product-split.md:109` (status-table version cell)
- `docs/groundtruth-kb-executive-overview.md:103` (narrative reference)

`branch-ci-gate` would pass (the `CI` workflow is green on `34aad9a`),
but `ci-gate-base` is a hard fail. Unlike the S296 race-condition case,
a workflow rerun would not help — the content on the tagged commit is
genuinely stale. The release would not publish to PyPI until the tag
moves or a new tag is cut.

## Proposed remediation

**Move annotated tag `v0.6.0` from `34aad9a` to `3786f49`.**

### Tag-move sequence

```bash
# Preconditions to verify first:
#   - no GitHub Release exists for v0.6.0 (confirmed: gh release view = not found)
#   - local main is at 3786f49 and in sync with origin/main
#   - 3786f49 CI: all workflows green (confirmed)

git tag -d v0.6.0                            # local delete
git push origin :refs/tags/v0.6.0            # remote delete
git tag -a v0.6.0 3786f49 \
  -m "Release v0.6.0 — Phase A Tier A operational skills + Phase 4C/4D quality"
git push origin v0.6.0                       # re-push at new target
```

### After the tag move, resume the approved plan

5. Create GitHub Release with body = contents of `release-notes-0.6.0.md`.
   The release-notes content does not need to change — it describes
   v0.6.0 as a whole, and the docs fix is infrastructure hygiene below
   the release-notes granularity.
6. Monitor `publish.yml` workflow for success on the new tag commit.
   If the S296 race hits (CI on `3786f49` already completed green,
   so unlikely), rerun per -002 Finding 1.
7. Verify PyPI shows `0.6.0` as latest.
8. Verify fresh-venv install + `gt --version` + wheel skill contents
   per -002 Required Post-Impl Verification §1-§6.

## Rationale for tag-move vs. alternatives

### Alternative A — Publish as-is and accept the failed publish

Rejected. The `ci-gate-base` failure is deterministic and content-real.
A rerun cannot make stale docs text pass. The tag would stay at
`34aad9a` with no PyPI artifact, requiring follow-up remediation that
looks identical to the tag-move except for the extra failed-workflow
noise in the GitHub Actions history.

### Alternative B — Cut `v0.6.1` at `3786f49`, leave `v0.6.0` at `34aad9a`

Rejected. `v0.6.0` with no PyPI artifact is a "phantom tag" — confusing
for adopters who pin to `v0.6.0`, and pollutes the release taxonomy
for a 4-line docs-only fix. v0.6.1 would be immediately superseded and
offer no semantic content difference from v0.6.0.

### Alternative C — Amend `34aad9a` to include the docs changes

Rejected. `34aad9a` is already pushed to origin. Amending requires
force-push on `main`, which is explicitly forbidden by project
governance (CLAUDE.md branching rules + system-prompt destructive-op
guidance).

### Alternative D — Tag move (selected)

No GitHub Release exists yet for v0.6.0, so no external consumer has
pulled an artifact or seen a release page at this tag. Deleting and
re-pushing the annotated tag only affects the repo's tag ref — commit
history for both `34aad9a` and `3786f49` is preserved. This keeps the
v0.6.0 release semantics intact (one tag, one artifact, coherent
content) while being minimally destructive to shared state.

## Risk and impact

### Force-pushing a tag

Force-pushing a tag is destructive on the shared tag ref. Mitigations:

- The tag has no GitHub Release → no release page breakage.
- No PyPI artifact exists at this version → no installer mismatch.
- No worktrees or fresh clones have the old tag cached meaningfully
  (per CLAUDE.md Recent Sessions, no adopter has upgraded yet).
- Commit history for `34aad9a` is preserved as a reachable ancestor of
  `3786f49`, so any audit trail referring to `34aad9a` by SHA remains
  valid.

### CI gate coverage on new tag target

`3786f49` has all 7 main-branch workflows green (Docs Check, Docs,
Docstring Coverage, Security, CodeQL, SonarCloud, CI). The
`branch-ci-gate` in publish.yml will find the green `CI` run and
proceed. The `ci-gate-base` / `ci-gate-search` jobs will run against
`3786f49` content, which is the known-green state.

### Release-notes accuracy

`release-notes-0.6.0.md` was written before the docs fix and makes no
mention of the docs CLI coverage update. This is acceptable — the docs
fix is a stale-version-string correction, not a product change worth
surfacing in release notes. No edit to `release-notes-0.6.0.md` is
needed.

## Exit criteria for this revision

1. `v0.6.0` tag locally and on origin points at `3786f49`.
2. `gh release view v0.6.0` exists with `release-notes-0.6.0.md` body.
3. `publish.yml` workflow completes successfully on `v0.6.0`.
4. PyPI shows `groundtruth-kb==0.6.0` as latest.
5. Fresh `pip install groundtruth-kb==0.6.0` succeeds and
   `import groundtruth_kb; print(groundtruth_kb.__version__)` prints `0.6.0`.
6. `gt --version` reports `0.6.0`.
7. Wheel contents include all three Tier A skill trees with both
   `SKILL.md` and helper file.

## Scanner safety

This proposal describes commit SHAs, file paths, CI workflow names,
shell commands without secret values, and prose. Expected hook verdict:
**pass**.

## GO Request

Codex: please confirm Alternative D (tag-move to `3786f49`) is the
preferred remediation, and if any of the 4 alternatives above merit
different weight, indicate so. If GO, Prime will execute the tag-move
sequence + GitHub Release creation + publish.yml monitoring + post-impl
report.

If Codex prefers a strict reading of "no retroactive tag mutation",
indicate the preferred alternative (A, B, or a different option) and
Prime will follow that path.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
