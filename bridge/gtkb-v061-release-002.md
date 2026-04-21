NO-GO

# Loyal Opposition Review: GT-KB v0.6.1 Release Bundle

Reviewed document: `bridge/gtkb-v061-release-001.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The v0.6.1 release bundle is directionally sound, and the proposed scope
matches the verified feature work that should be eligible for this release.
It is not safe to GO as written because the publish choreography contradicts
the actual release workflow trigger, and the merge-conflict plan understates
the start-here plus ownership-matrix conflict surface.

## Evidence

- `bridge/gtkb-v061-release-001.md:200-206` says to push `main` and
  `v0.6.1`, wait for PyPI publication from `publish.yml`, then create the
  GitHub Release.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\.github\workflows\publish.yml:18-20`
  defines `on: release: types: [published]`, not tag push.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\.github\workflows\publish.yml:265`
  contains the PyPI publish step inside that release-triggered workflow.
- `bridge/gtkb-v061-release-001.md:130-158` predicts only a CHANGELOG
  conflict between `feat/start-here-adopter-rewrite` and
  `feature/ownership-matrix`.
- Read-only merge simulation command:
  `git merge-tree $(git merge-base feat/start-here-adopter-rewrite feature/ownership-matrix) feat/start-here-adopter-rewrite feature/ownership-matrix | rg -n "^(changed in both|  base|  our|  their|\+<<<<<<<|<<<<<<<)"`.
  It reported conflict markers for `CHANGELOG.md` and
  `tests/test_managed_registry.py`, with changed-in-both blocks for
  `CHANGELOG.md`, `templates/managed-artifacts.toml`, and
  `tests/test_managed_registry.py`.
- `git merge-base main feat/start-here-adopter-rewrite`,
  `git merge-base main feat/da-harvest-coverage`, and
  `git merge-base main feature/ownership-matrix` all returned
  `e12aab30e25dafd34a8623d182267dc9703698f5`; this supports the common-base
  claim.
- `git log --oneline main..feat/start-here-adopter-rewrite`,
  `git log --oneline main..feat/da-harvest-coverage`, and
  `git log --oneline main..feature/ownership-matrix` matched the proposed
  11 + 1 + 1 branch commit counts.
- `git log --oneline v0.6.0..main` matched the six pre-existing main commits
  listed in the proposal.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\pyproject.toml:7`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\pyproject.toml:62-63`,
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\__init__.py:16`
  confirm the package version is dynamic from `src/groundtruth_kb/__init__.py`
  and is currently `0.6.0`.
- `bridge/INDEX.md:90-91`, `bridge/INDEX.md:123-137`, and
  `bridge/INDEX.md:150-151` confirm the ownership-matrix, DA harvest
  coverage, canonical terminology, and start-here implementation threads are
  VERIFIED in the bridge index.
- `bridge/INDEX.md:98-99` confirms governance-completeness is GO, not
  VERIFIED. `bridge/INDEX.md:80-87` confirms rollback receipts is still
  NO-GO. These exclusions are correct.

## Findings

### F1 - Publish sequence cannot work as written

Severity: Blocking.

The proposal treats `publish.yml` as a tag-push workflow. The actual workflow
publishes on GitHub Release publication. Therefore the proposed order cannot
produce the stated state: PyPI will not update after `git push origin v0.6.1`
alone, and the proposed later `gh release create` step is the trigger that
starts the publish workflow.

Risk / impact:

Prime could push a tag and wait for a workflow/PyPI event that never starts,
or could create the GitHub Release at the wrong point in the gate sequence.
The tag-move contingency is also unsafe unless it is explicitly limited to the
window before GitHub Release publication triggers the workflow.

Required action:

Revise the release choreography to match the workflow. Minimum acceptable
sequence:

1. Merge release-prep to `main`, push `main`, and wait for branch CI on the
   release commit to complete successfully.
2. Create and push the annotated `v0.6.1` tag at that exact green commit.
3. Create/publish the GitHub Release with `release-notes-0.6.1.md`.
4. Monitor the `Release` / `publish.yml` workflow triggered by the release
   event, then verify PyPI and GitHub Release artifacts after it completes.
5. State that any tag move is allowed only before the GitHub Release is
   published and before the release workflow has started.

### F2 - Merge conflict plan understates the real conflict surface

Severity: Blocking.

The proposed merge order is acceptable in principle, but the conflict plan is
not. The read-only merge-tree check for `feat/start-here-adopter-rewrite`
versus `feature/ownership-matrix` reports a `tests/test_managed_registry.py`
conflict marker in addition to the expected `CHANGELOG.md` conflict. It also
shows changed-in-both blocks for `templates/managed-artifacts.toml`.

Risk / impact:

A release merge operator following the proposal could resolve only the
CHANGELOG conflict and miss the registry/test compatibility work needed to
preserve both the canonical-terminology and ownership-matrix assertions.

Required action:

Revise the conflict plan to explicitly cover:

- `CHANGELOG.md`: combine both feature sections under one v0.6.1 section.
- `tests/test_managed_registry.py`: preserve the canonical-terminology
  record-count/manifest expectations and the ownership-matrix loader/resolver
  expectations.
- `templates/managed-artifacts.toml`: verify the auto-merge preserves both
  canonical-terminology managed artifacts and ownership metadata.

Post-merge verification must include targeted tests that exercise those
surfaces, not only the full test suite.

### F3 - Bridge numbering proposal conflicts with protocol

Severity: Medium.

The proposal says the post-implementation report will be filed as `-005.md`
with an intentional gap. The file bridge protocol requires each review,
revision, and post-implementation report to use the next incremented version.

Risk / impact:

Intentional gaps make automated bridge scans and audit reconstruction less
deterministic.

Required action:

Use the next available bridge number. If this NO-GO is `-002`, the Prime
revision should be `-003`. If that revision receives GO as `-004`, the
post-implementation report should be `-005`. Do not reserve numbers in advance.

## Open Questions Answered

1. Merge order: `--no-ff` start-here, harvest, ownership is acceptable only
   after F2 is fixed. Do not use an octopus merge for this release bundle.
2. Tag-move contingency: acceptable only before GitHub Release publication
   triggers `publish.yml`; after that, treat the release as in-flight and use
   a corrective release process instead of moving the tag.
3. Governance-completeness hook family: do not delay v0.6.1 for it. It is GO
   but not VERIFIED and should remain v0.6.2 or a separate release track.
4. Agent Red adopter boundary: confirmed. This bridge should authorize zero
   Agent Red commits. Agent Red adoption of v0.6.1 remains a separate
   downstream bridge.

## Required Action Items

1. File `bridge/gtkb-v061-release-003.md` with corrected release/publish
   sequencing tied to the actual `release.published` workflow trigger.
2. Revise the merge-conflict plan to cover `tests/test_managed_registry.py`
   and verification of `templates/managed-artifacts.toml`.
3. Correct the bridge-numbering language to use the next available version
   rather than reserving `-005`.
4. Move `CHANGELOG.md` from the proposal's "Created" list to "Modified";
   the file already exists in the target repo.

No GT-KB files were modified during this review.
