# VERIFIED: GroundTruth-KB v0.4.0 Release Ratification

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed ratification:** `bridge/gtkb-v0.4.0-release-005.md`
**Prior NO-GO:** `bridge/gtkb-v0.4.0-release-004.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

VERIFIED.

The only remaining blocker from `gtkb-v0.4.0-release-004.md` was process
evidence: owner ratification for the already-executed `v0.4.0` tag and PyPI
publish at `993f31b8d42ac272b9716c191527b599d08ba632`, plus confirmation that
no new destination-changing action was needed.

`gtkb-v0.4.0-release-005.md` provides a post-facto owner quote,
`"Ratified: v0.4.0 at 993f31b."` I accept this as satisfying the closure
condition because it is presented as the response to the exact `-004.md`
ratification request, it names the release, and the abbreviated SHA resolves
unambiguously to the verified release commit. The technical release artifacts
remain valid.

No retag, republish, source change, or workflow change is requested.

## Evidence

- Read the full `bridge/INDEX.md` entry and all referenced versions
  `bridge/gtkb-v0.4.0-release-001.md` through
  `bridge/gtkb-v0.4.0-release-005.md`.
- `bridge/gtkb-v0.4.0-release-004.md:130-136` required exact-SHA owner
  approval evidence or owner ratification for the already-executed release, and
  confirmation that no new destination-changing action was needed.
- `bridge/gtkb-v0.4.0-release-005.md:17-22` quotes that condition and then
  quotes the owner ratification: `"Ratified: v0.4.0 at 993f31b."`
- `bridge/gtkb-v0.4.0-release-005.md:47-54` confirms no retag, no republish,
  no source changes, and no workflow changes.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, the following
  commands all returned `993f31b8d42ac272b9716c191527b599d08ba632`:
  `git rev-parse HEAD`, `git rev-parse origin/main`,
  `git rev-parse --verify 993f31b`,
  `git rev-parse --verify 993f31b8d42ac272b9716c191527b599d08ba632`, and
  `git rev-list -n 1 v0.4.0`.
- `git ls-remote --tags origin "refs/tags/v0.4.0*"` returned tag object
  `5e191d6d5ff405fad6ed5caeca23b6664d1a8ed2` and peeled commit
  `993f31b8d42ac272b9716c191527b599d08ba632`.
- `git status --short --branch` returned `## main...origin/main` with only
  untracked `_site_verify/` and `release-notes-0.4.0.md`; no tracked source
  change was present.
- `gh release view v0.4.0 --repo Remaker-Digital/groundtruth-kb --json ...`
  returned `isDraft=false`, `isPrerelease=false`, `tagName=v0.4.0`, and URL
  `https://github.com/Remaker-Digital/groundtruth-kb/releases/tag/v0.4.0`.
- `gh run view 24417719826 --repo Remaker-Digital/groundtruth-kb --json ...`
  returned `status=completed`, `conclusion=success`, `event=release`, and
  `headSha=993f31b8d42ac272b9716c191527b599d08ba632`.
- The same run reported these jobs successful: `ci-gate-base`,
  `ci-gate-search`, `branch-ci-gate`, `build-verify`,
  `smoke-test-cross-platform (ubuntu-latest)`,
  `smoke-test-cross-platform (macos-latest)`,
  `smoke-test-cross-platform (windows-latest)`, and `publish-pypi`.
- PyPI JSON for `groundtruth-kb` returned latest version `0.4.0`, releases
  `0.3.1,0.4.0`, and wheel
  `groundtruth_kb-0.4.0-py3-none-any.whl` with SHA256
  `40590192784f60329c14f1451eb8baa63bbfafd2d44fa794fcc0377a0659f28b`.
- `src/groundtruth_kb/__init__.py:16` declares `__version__ = "0.4.0"`.
- `CHANGELOG.md:10` and `docs/changelog.md:10` contain
  `[0.4.0] - 2026-04-14`.
- `pyproject.toml:17` keeps the classifier at
  `Development Status :: 3 - Alpha`, consistent with the release scope.

## Findings

### 1. PASS - Ratification closes the prior process blocker

The owner quote in `-005.md` is terse, but in the file-bridge context it is a
ratification of the already-executed `v0.4.0` release at the named commit.
The short SHA `993f31b` resolves to the full release commit, and no evidence
shows a competing commit or ambiguous tag target.

**Risk/impact:** Low. The earlier risk was process ambiguity, not artifact
integrity. The ratification now provides closure evidence.

**Required action:** None.

### 2. PASS - Release artifacts remain technically valid

The local checkout, remote `main`, annotated tag, GitHub Release, Release
workflow run, package metadata, and PyPI JSON all align on `v0.4.0` at
`993f31b8d42ac272b9716c191527b599d08ba632`.

**Risk/impact:** Low. No evidence indicates a wrong tag target, failed release
workflow, missing PyPI artifact, or classifier drift.

**Required action:** None.

### 3. FOLLOW-UP - publish.yml smoke status bug remains non-blocking

The known workflow issue from `gtkb-v0.4.0-release-004.md` remains a future
release hardening item: the smoke step should capture the direct exit code from
`gt deliberations rebuild-index` rather than the surrounding `if` compound
status. This was independently mitigated for v0.4.0 by post-publish package
smoke, so it does not block this verification.

**Risk/impact:** Medium for future release diagnostics, low for the already
published v0.4.0 artifact.

**Recommended action:** Open a separate bridge round to patch the workflow with
`set +e`, assert `EC -eq 1`, and assert the `groundtruth-kb[search]` guidance
appears in output.

## Required Action Items

None before closure.

## Decision Needed From Owner

None.

