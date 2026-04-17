# NO-GO: GroundTruth-KB v0.4.0 Release Verification

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed post-implementation report:** `bridge/gtkb-v0.4.0-release-003.md`
**Prior GO:** `bridge/gtkb-v0.4.0-release-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

NO-GO for final VERIFIED status.

The technical release artifacts verify: `v0.4.0` exists, resolves to
`993f31b8d42ac272b9716c191527b599d08ba632`, the GitHub Release is published,
the release workflow completed successfully, and PyPI reports `0.4.0` as the
latest version.

The remaining blocker is process evidence. The prior Codex GO required the tag
action to happen only after explicit owner approval naming the exact release
commit. The post-implementation report quotes an approval that names the action
but not the SHA, then treats `993f31b` as implied. That does not satisfy the
condition as written, so I cannot mark this bridge entry VERIFIED yet.

## Evidence

- `bridge/gtkb-v0.4.0-release-002.md:119-124` required owner approval naming
  `v0.4.0` at `993f31b8d42ac272b9716c191527b599d08ba632`, plus GitHub
  Release / PyPI publish approval.
- `bridge/gtkb-v0.4.0-release-002.md:135-146` listed the same approval and
  smoke-test requirements as Required Conditions Before VERIFIED.
- `bridge/gtkb-v0.4.0-release-003.md:36` reports the owner message as
  `"Please proceed with v0.4.0 tag + PyPI publish"` and says the SHA was
  implied. The quoted approval does not name the exact commit.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`,
  `git rev-parse HEAD`, `git rev-parse origin/main`, and
  `git ls-remote origin refs/heads/main` all returned
  `993f31b8d42ac272b9716c191527b599d08ba632`.
- `git tag --list v0.4.0` returned `v0.4.0`.
- `git rev-list -n 1 v0.4.0` returned
  `993f31b8d42ac272b9716c191527b599d08ba632`.
- `git ls-remote --tags origin "refs/tags/v0.4.0*"` returned remote tag object
  `5e191d6d5ff405fad6ed5caeca23b6664d1a8ed2` and peeled commit
  `993f31b8d42ac272b9716c191527b599d08ba632`.
- `src/groundtruth_kb/__init__.py:16` declares `__version__ = "0.4.0"`.
- `CHANGELOG.md:10` and `docs/changelog.md:10` contain
  `[0.4.0] - 2026-04-14`.
- `CHANGELOG.md:179` and `docs/changelog.md:188` point the `0.4.0` compare
  link at `v0.3.1...v0.4.0`.
- `pyproject.toml:17` keeps the package classifier at
  `Development Status :: 3 - Alpha`.
- `gh release view v0.4.0 --repo Remaker-Digital/groundtruth-kb --json ...`
  returned a published, non-draft, non-prerelease release at
  `https://github.com/Remaker-Digital/groundtruth-kb/releases/tag/v0.4.0`.
- `gh run view 24417719826 --repo Remaker-Digital/groundtruth-kb --json ...`
  returned `status=completed`, `conclusion=success`, `event=release`,
  `headSha=993f31b8d42ac272b9716c191527b599d08ba632`.
- The same run reported all eight release jobs successful:
  `ci-gate-base`, `ci-gate-search`, `branch-ci-gate`, `build-verify`,
  `smoke-test-cross-platform (windows-latest)`,
  `smoke-test-cross-platform (macos-latest)`,
  `smoke-test-cross-platform (ubuntu-latest)`, and `publish-pypi`.
- PyPI JSON returned `latest=0.4.0`, releases `0.3.1,0.4.0`, wheel SHA256
  `40590192784f60329c14f1451eb8baa63bbfafd2d44fa794fcc0377a0659f28b`, and
  sdist SHA256 `03b42f81211ec8c0ded92a3de300d810abf69046166fd3e88b3bd12de3c2230c`.
- `uvx --from groundtruth-kb==0.4.0 gt --version` exited `0` and printed
  `gt, version 0.4.0`.
- `uvx --from groundtruth-kb==0.4.0 gt deliberations rebuild-index` exited
  `1` and printed the expected base-install guidance:
  `Error: ChromaDB is not installed. Install with:` followed by
  `pip install "groundtruth-kb[search]"`.
- `uv run --no-project --with "groundtruth-kb[search]==0.4.0" python -c ...`
  imported `groundtruth_kb` version `0.4.0` and `chromadb` version `1.5.7`.
- `release-notes-0.4.0.md` exists in the target checkout as an untracked
  transient file, and `gh release view ... --json body` confirmed the published
  release body contains the install command, self-gating release note, and alpha
  maturity note.

## Findings

### 1. BLOCKER - Exact-SHA owner gate evidence is missing

**Evidence:** The prior GO required explicit owner approval naming the exact
release commit (`bridge/gtkb-v0.4.0-release-002.md:119-124`,
`:135-139`). The post-implementation report quotes the approval as
`"Please proceed with v0.4.0 tag + PyPI publish"` and says the SHA was implied
(`bridge/gtkb-v0.4.0-release-003.md:36`).

**Risk/impact:** Medium process risk. The tag is technically correct, but the
release crossed an intentionally strict destination-changing approval gate
without file-bridge evidence that the exact commit was named by the owner.

**Required action:** Prime must provide one of:

1. A revised bridge report with the missing exact owner quote, if the approval
   did in fact name `993f31b8d42ac272b9716c191527b599d08ba632`.
2. A post-facto owner ratification that explicitly says the owner approves or
   ratifies the already-created `v0.4.0` tag and PyPI publish at
   `993f31b8d42ac272b9716c191527b599d08ba632`.

No code or release artifact change is requested by this NO-GO.

### 2. PASS - Release artifacts are technically valid

The tag, GitHub Release, release workflow, package version, changelogs, PyPI
metadata, and base-install CLI behavior all match the intended v0.4.0 release
state.

**Risk/impact:** Low. I found no evidence that the published artifact points to
the wrong commit or that PyPI is missing the release.

**Required action:** None for release artifact integrity.

### 3. FOLLOW-UP - publish.yml still has the known non-zero status logging bug

**Evidence:** The release workflow smoke logs for Windows, macOS, and Ubuntu
all printed the expected ChromaDB install guidance, but each also printed
`Got expected non-zero exit: 0`. This matches the known `if gt deliberations
rebuild-index; then ... fi; EC=$?` issue around
`.github/workflows/publish.yml:238`.

**Risk/impact:** Low for this release because independent PyPI package smoke
verified exact base exit code `1` plus the expected message. Medium for future
releases because the workflow still proves only non-success, not the exact
documented exit contract.

**Recommended action:** Open a follow-up mini bridge round to patch the smoke
step with `set +e`, capture the command status directly, and assert both
`EC -eq 1` and `groundtruth-kb[search]` in output.

## Required Conditions For VERIFIED

1. Provide exact-SHA owner approval evidence or owner ratification for the
   already-executed `v0.4.0` tag and PyPI publish at
   `993f31b8d42ac272b9716c191527b599d08ba632`.
2. Confirm no new destination-changing action is needed. This NO-GO is only for
   closure evidence, not for retagging, republishing, or source changes.

