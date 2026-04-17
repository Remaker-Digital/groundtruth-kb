# GT-KB v0.6.0 Release Bundle

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**Target repo:** `groundtruth-kb` main
**Current HEAD:** `9629091` (Tier A #5 VERIFIED)
**Current version string:** `__version__ = "0.5.0"` at `src/groundtruth_kb/__init__.py`
**Prior release tag:** `v0.5.0` at `64e59e3`
**Owner directive:** S299 owner selected Option A (ship v0.6.0 now, then open both post-Phase-A scope bridges in parallel)

## Summary

Prepare and publish GT-KB v0.6.0 to PyPI. v0.6.0 bundles Phase A Tier
A (6 bridges, now all VERIFIED) plus Phase 4C/4D quality work and
operational governance hooks that landed between v0.5.0 and now.

This bridge covers **release prep only**. Post-impl verifies PyPI
publication and wheel installability. Opening the two post-Phase-A
scope bridges (non-disruptive upgrade investigation + Azure
enterprise readiness taxonomy) is separate work that follows VERIFIED
of this bridge.

## Prior Deliberations

- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (owner directive S299 —
  post-Phase-A parallelization; v0.6.0 is the gating milestone)
- All six Phase A bridge VERIFIEDs (see `bridge/INDEX.md`)
- Prior releases: v0.4.0 via `publish.yml` workflow (S290 memory),
  v0.5.0 via same workflow (S296 memory — note race-condition
  learning)

## Scope

### Commits to include in v0.6.0

Range: `v0.5.0..HEAD` (13 commits). Grouped by track:

**Phase A Tier A (6 commits):**

- `862045d` feat(governance): canonical credential patterns module (Tier A #1)
- `b5e5c6c` feat(governance): scanner-safe-writer PreToolUse hook (Tier A #2)
- `37a88cc` fix(governance): scanner-safe-writer post-impl fixes per bridge -010
- `d9325c9` feat(governance): decision-capture skill + scaffold/doctor/upgrade (Tier A #4)
- `0a60054` feat(governance): bridge-propose skill (Tier A #3)
- `41ac869` feat(metrics): Phase A scanner-safe-writer metrics collector (Tier A #6)
- `9629091` feat(governance): spec-intake skill + intake.py changed_by extension (Tier A #5)

**Phase 4 quality track (2 commits):**

- `b1c3359` feat(quality): Phase 4C structured logging migration
- `23cdf09` feat(quality): Phase 4D broad exception governance

**Operational governance (2 commits):**

- `b9a2071` feat(governance): Phase 1 operational governance hooks + source_paths migration
- `8efcbb1` fix(governance): C1 source_paths carry-forward + C3 test coverage gaps

**Docs + CI (2 commits):**

- `71ef2b0` docs(memory-architecture): align 30 files to ADR-0001 three-tier vocabulary
- `a3fa4d2` fix(ci): add tests/__init__.py for 4C print guard import resolution

### Files changed in this release-prep commit

1. `src/groundtruth_kb/__init__.py` — bump `__version__` from
   `"0.5.0"` to `"0.6.0"`. Single-line change.
2. `CHANGELOG.md` — rename existing `## [Unreleased]` section to
   `## [0.5.0] - 2026-04-15` (retrospective — v0.5.0 shipped without
   a CHANGELOG update), and add a new `## [0.6.0] - 2026-04-17`
   section at the top listing the Phase A + 4C/4D + governance +
   docs changes from the 13-commit range above.
3. `release-notes-0.6.0.md` (new) — human-readable release summary
   following the same shape as the untracked `release-notes-0.4.0.md`
   artifact already in the repo.

No production source or test file edits. No dependency changes.

### Commit, tag, push plan

1. Single commit on main with the above three changes and message:

   ```
   chore(release): prepare v0.6.0
   ```

   (Follows the "chore(release)" prefix convention from prior
   releases; keeps the release-prep commit separate from the Phase
   A feature commits for clean tag association.)

2. Push `main` to `origin/main`. This pushes all 14 commits (13
   Phase A / 4C / 4D / governance / docs + 1 release prep).

3. Create annotated tag `v0.6.0` at the release-prep commit:

   ```
   git tag -a v0.6.0 -m "Release v0.6.0 — Phase A Tier A operational skills + Phase 4C/4D quality"
   ```

4. Push tag: `git push origin v0.6.0`.

5. Create GitHub release with the contents of
   `release-notes-0.6.0.md` as the body. GitHub Release creation
   triggers the self-gating `publish.yml` workflow which builds and
   uploads the wheel to PyPI.

### Verification plan (for post-impl)

After GitHub Release + publish workflow completes:

1. `pip install groundtruth-kb==0.6.0` in a fresh venv succeeds.
2. `python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"`
   prints `0.6.0`.
3. `groundtruth-kb --help` (or equivalent CLI entry point) runs
   without error.
4. `unzip -l groundtruth_kb-0.6.0-*.whl | grep skills/` shows all
   three skill trees (`decision-capture`, `bridge-propose`,
   `spec-intake`) with both `SKILL.md` and helper.
5. PyPI project page at https://pypi.org/project/groundtruth-kb/
   shows version `0.6.0` as latest.

### Known risk: publish.yml race condition

Per S296 memory: v0.5.0's first publish attempt failed because
`publish.yml` checked release-gate status while CI was still
`in_progress`. The re-run succeeded. If this happens for v0.6.0,
the post-impl action is to re-run the failed workflow manually.
This is known behavior; not a blocker for this bridge.

## Out of scope

1. Opening the two post-Phase-A parallel scope bridges
   (`gtkb-non-disruptive-upgrade-investigation-001` and
   `gtkb-azure-enterprise-readiness-taxonomy-001`). Those are
   separate bridges filed after this one VERIFIEDs.
2. Announcement communication (if any) — owner handles externally.
3. Agent Red upgrade to v0.6.0 — separate bridge cycle.
4. CTO environment upgrade — separate bridge cycle (tests the
   non-disruptive upgrade claim).
5. `pyproject.toml` dependency bumps or constraint changes.

## Exit Criteria

1. `src/groundtruth_kb/__init__.py` has `__version__ = "0.6.0"`.
2. `CHANGELOG.md` has a `## [0.6.0] - 2026-04-17` section as the
   first version section after `## [Unreleased]` (empty or absent)
   and a `## [0.5.0] - 2026-04-15` section for retroactive v0.5.0
   content.
3. `release-notes-0.6.0.md` exists in the repo root and is tracked
   in git.
4. A single `chore(release): prepare v0.6.0` commit lands on main
   at the head of the 14-commit range.
5. `v0.6.0` annotated tag exists at that commit on both local and
   origin.
6. GitHub Release exists with the release notes body.
7. PyPI shows `groundtruth-kb==0.6.0` available.
8. Clean install + version lookup + CLI help all work in a fresh
   venv (verified in post-impl report).

## Review Gates

No binding gates from Phase A scope — this bridge is a release
bundle, not a Phase A child bridge.

## GO Request

Codex: please verify the release plan for:

1. **Commit grouping**: 13 feature commits + 1 release-prep commit.
   The release-prep commit is the one v0.6.0 points at. This keeps
   the tag pointing at a "ready-to-ship" snapshot distinct from the
   last feature commit. Preferred, or should I tag the Phase A #5
   commit directly and skip a release-prep commit?
2. **CHANGELOG retrospection**: adding a `[0.5.0]` section today
   for content that was shipped to PyPI two sessions ago. Accept
   as corrective hygiene, or require a separate bridge to reconstruct
   the full v0.5.0 changelog faithfully?
3. **Version bump only** (no dep or constraint changes). Correct
   for a Phase A + quality bundle?
4. **PyPI publish via GitHub Release** (same workflow as v0.4.0 and
   v0.5.0). No changes to `publish.yml`. OK?
5. **Verification scope in post-impl**: fresh-venv install + wheel
   skill contents + PyPI page. Sufficient, or add anything?

If approved: I execute the 3-file edit + commit + push + tag + push
+ GitHub Release creation, then monitor publish.yml. Post-impl
report after PyPI shows v0.6.0.

## Scanner Safety

Pre-flight scan: this proposal describes commit SHAs, version
strings, CHANGELOG structure, and workflow behavior in prose only.
No literal credential values appear. Expected hook verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
