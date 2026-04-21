# GT-KB v0.6.1 Release Bundle

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S300
**Target repo:** `groundtruth-kb` main
**Current main HEAD:** `e12aab3` (registry consolidation; 7 commits ahead of `v0.6.0` tag at `3786f49`)
**Current version string:** `__version__ = "0.6.0"` at `src/groundtruth_kb/__init__.py`
**Prior release tag:** `v0.6.0` at `3786f49` (tag-moved from `34aad9a` per S299 GO)
**Owner directive:** S300 AskUserQuestion 2026-04-17 evening (DELIB-S300-001) — "All 3 branches in v0.6.1 (recommended)"

## Summary

Prepare and publish GT-KB v0.6.1 to PyPI. v0.6.1 bundles three VERIFIED
feature branches (all branched from `e12aab3`): canonical-terminology-surface
+ start-here-adopter-rewrite (co-located on `feat/start-here-adopter-rewrite`),
DA harvest coverage (`feat/da-harvest-coverage`), and artifact ownership
matrix (`feature/ownership-matrix`). Plus the pre-existing registry
consolidation commit `e12aab3` already on main.

This bridge covers **merge + release prep + publish + GitHub Release**. It
does NOT ship:

- `gtkb-da-governance-completeness-implementation` (newly GO'd at `-016`
  overnight 2026-04-17 — implementation work is separate, targets v0.6.2
  or parallel track).
- `agent-red-session-wrap-automation` hook family (retired, absorbed into
  governance-completeness per `-005` VERIFIED retirement).
- `gtkb-rollback-receipts` (still at NO-GO `-008`, not ready).

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, DA searched before drafting.

Directly relevant:

- **DELIB-S300-001** (archived this turn) — Owner decision: "All 3 branches
  in v0.6.1 (recommended)"; INDEX-drift repair authorized (already
  self-healed overnight).
- **DELIB-0820** — S299 final wrap listing 4 VERIFIED threads. Note:
  bootstrap memo was written BEFORE overnight ownership-matrix `-006`
  VERIFIED and governance-completeness `-016` GO; this proposal corrects
  the "4 VERIFIED threads" framing to "3 merge-able branches + 1 retired
  thread".
- **DELIB-0730** — Prior v0.6.0 release bridge (6 versions, VERIFIED).
  Precedent for release-bridge structure, PyPI publish via `publish.yml`
  workflow, tag-move addendum pattern.
- **DELIB-0715** — MemBase canonical definition (owner settlement).
  Relevant because `feat/start-here-adopter-rewrite` is the first release
  to codify MemBase/DA/GT-KB vocabulary across always-loaded surfaces.

Searched for "v0.6.1 release" — no prior entries (confirms first-time thread).

## Scope — Three branches to merge

### Branch 1 — `feat/start-here-adopter-rewrite` (11 commits)

Discharges TWO VERIFIED implementation bridges on a single branch:

- `gtkb-canonical-terminology-surface-implementation-012` VERIFIED
  (commit `f475c8b`)
- `gtkb-start-here-adopter-rewrite-implementation-010` VERIFIED
  (commit `1b0bde4` — branch tip)

Commit log (newest first):

```
1b0bde4 docs(evidence): regenerate artifacts at canonical-terminology tip
f475c8b feat(terminology): canonical terminology surface via managed rule artifacts
b60f98d docs(evidence): regenerate artifacts at remediation tip
2790e11 docs(evidence): reconcile provenance, tighten verify gate
6b152c2 chore(evidence): regenerate evidence JSON at feature branch tip
20b5561 docs(adopter): restructure nav + add focused link-integrity checker
755b9d5 docs(adopter): add Known Limitations with audit cross-links
f9a83fb docs(adopter): add Evidence page + metrics collector with drift check
55a34f2 docs(adopter): refresh Day in the Life with six named activities
05dc825 docs(adopter): rewrite Start Here + README for zero-context adopters
d3955e5 chore(kb): Phase 1 scaffold scripts for SPEC-STARTHERE-* adopter rewrite
```

CHANGELOG: adds `[Unreleased] — Canonical terminology surface` section
(~80 lines).

### Branch 2 — `feat/da-harvest-coverage` (1 commit)

Discharges:

- `gtkb-da-harvest-coverage-implementation-011` VERIFIED
  (commit `cf29738`)

Commit:

```
cf29738 feat(reporting): DA harvest coverage helper + doctor check
```

CHANGELOG: no changes (branch does not touch CHANGELOG). Release notes
must add coverage helper / doctor check / loud-wrap.

### Branch 3 — `feature/ownership-matrix` (1 commit)

Discharges:

- `gtkb-artifact-ownership-matrix-006` VERIFIED (commit `bfedd40`,
  Codex-verified overnight 2026-04-18 UTC; INDEX self-healed post
  `-006` by overnight worker)

Commit:

```
bfedd40 feat(ownership): Artifact Ownership Matrix (ownership-glob + resolver + classify-tree)
```

CHANGELOG: adds `[Unreleased] — Artifact Ownership Matrix` section
(~70 lines).

### Pre-existing on main (included in v0.6.1 by range)

Between `v0.6.0` tag (`3786f49`) and current main HEAD (`e12aab3`):

```
e12aab3 feat(registry): consolidate _MANAGED_* lists into declarative TOML registry  (merged via gtkb-managed-artifact-registry-010 VERIFIED)
82c5a85 docs: add Azure readiness visuals and wiki source                           (merged via bridge thread, not in v0.6.0)
33f1c5a Revert "docs(azure): taxonomy remediation per Codex GO - subtopics + review gates + KB script"
98563fc docs(azure): taxonomy remediation per Codex GO - subtopics + review gates + KB script  (reverted; will be re-applied in future release)
67197ed docs(upgrade): non-disruptive upgrade investigation report
90cfd99 docs(azure): enterprise readiness taxonomy + vision reconciliation
```

These 6 commits already on main represent post-v0.6.0 merged work that
release notes must document.

## Merge order and conflict plan

All three branches branch from the same merge-base (`e12aab3`). Conflict
analysis:

| Branch | CHANGELOG | Other conflicts |
|--------|-----------|-----------------|
| feat/start-here-adopter-rewrite | Adds [Unreleased] §canonical-terminology | None predicted |
| feat/da-harvest-coverage | No CHANGELOG changes | None predicted |
| feature/ownership-matrix | Adds [Unreleased] §ownership-matrix | None predicted |

**Predicted conflict:** feat/start-here-adopter-rewrite and
feature/ownership-matrix both insert an `## [Unreleased]` section
after the header boilerplate. A straight merge will produce a duplicate-
header conflict.

**Resolution strategy (recommended): merge in three steps, resolve
CHANGELOG at merge-2 and merge-3:**

1. Merge `feat/start-here-adopter-rewrite` → main via `--no-ff` merge
   commit. No conflicts expected. `[Unreleased]` populated with
   canonical-terminology content only.
2. Merge `feat/da-harvest-coverage` → main via `--no-ff`. No conflicts.
3. Merge `feature/ownership-matrix` → main via `--no-ff`. CHANGELOG
   conflict expected at the `[Unreleased]` section; resolution
   appends ownership-matrix content under the same section, produces
   unified [Unreleased] with two `### Added` subsections.
4. Release-prep commit (below) renames `## [Unreleased]` to
   `## [0.6.1] - 2026-04-17` and adds a new empty `## [Unreleased]`
   placeholder above it.

**Alternative: single rebase-all-three merge** — higher risk of conflict
reordering; not recommended for a release bundle where per-branch
attribution is desired.

## Release-prep commit

Single commit on main after step 3 above, before tag:

1. `src/groundtruth_kb/__init__.py` — bump `__version__` from `"0.6.0"`
   to `"0.6.1"`. Single-line change.
2. `CHANGELOG.md`:
   - Rename `## [Unreleased]` → `## [0.6.1] - 2026-04-17`.
   - Insert new `## [Unreleased]` placeholder at top.
   - Add a new `### Added — DA harvest coverage` subsection under
     `## [0.6.1]` (branch 2 had no CHANGELOG entry).
   - Add `### Changed / Infrastructure` subsection summarizing the
     6 pre-existing main commits (registry consolidation,
     Azure taxonomy docs, non-disruptive upgrade report).
3. `release-notes-0.6.1.md` (new) — human-readable summary following
   the shape of `release-notes-0.6.0.md` (if present) or the
   `release-notes-0.4.0.md` pattern. Sections: Highlights,
   Adopter-visible changes, Technical changes, Breaking changes
   (should be "none"), Upgrade path.

Commit message (single line per convention):

```
chore(release): prepare v0.6.1
```

## Tag + publish

After release-prep commit:

1. Tag: `git tag -a v0.6.1 -m "GT-KB v0.6.1: canonical terminology + adopter docs + harvest coverage + ownership matrix"` at release-prep commit HEAD.
2. Push main + tag: `git push origin main && git push origin v0.6.1`.
3. PyPI publish: GitHub Actions `publish.yml` workflow triggers on tag
   push. Monitor via `gh workflow view publish.yml` and
   `gh run list --workflow=publish.yml --limit 3`.
4. Wait for PyPI wheel to appear at
   `https://pypi.org/project/groundtruth-kb/0.6.1/`.
5. GitHub Release: `gh release create v0.6.1 --title "GT-KB v0.6.1" --notes-file release-notes-0.6.1.md`.

**Race condition guard (v0.5.0 lesson per MEMORY.md S296):** Release-prep
commit MUST land on main with CI green before tagging, otherwise
`publish.yml`'s release-gate check can see `in_progress` CI and fail.
Verify by polling `gh run list --branch main --workflow ci.yml` until
latest shows `completed` + `success` BEFORE pushing the tag.

## Post-implementation verification criteria

To be discharged by the post-impl report (filed as `-005.md` after
execution):

1. `git log v0.6.0..v0.6.1 --oneline` shows: all 13 new commits merged
   (11 from start-here + 1 harvest + 1 ownership) plus release-prep
   commit.
2. `python -m pytest -q` on merged main: all 1300+ tests pass. Spot
   check: `test_managed_registry`, `test_ownership_resolver`,
   `test_doctor`, `test_harvest`.
3. `python -m mypy --strict src/groundtruth_kb/` clean.
4. `python -m ruff check src/groundtruth_kb/ tests/` clean.
5. `pip install groundtruth-kb==0.6.1` from PyPI completes without
   error (run from clean venv).
6. Fresh scaffold test: `gt project init /tmp/v061-smoke && cd
   /tmp/v061-smoke && gt project doctor` passes, `.claude/rules/
   canonical-terminology.md` present (proves Branch-1 ships).
7. `release-notes-0.6.1.md` committed and included in GitHub Release.
8. CHANGELOG `## [0.6.1]` section complete; `## [Unreleased]`
   placeholder empty and present.

## Open review questions for Codex

Per S299 post-impl hygiene (`feedback_postimpl_report_hygiene.md`):

1. **Merge-order audit** — Is the 3-step `--no-ff` merge order
   (start-here → harvest-coverage → ownership-matrix) preferred vs.
   a single octopus merge or a rebase-merge cascade? The recommended
   order minimizes CHANGELOG conflict footprint (one conflict at
   step 3 only).
2. **Tag-move contingency** — If post-impl verification reveals a
   late-breaking docs fix (v0.6.0 precedent), is pre-publish tag-move
   acceptable provided (a) no `pip install` has occurred at the
   initial tag, and (b) the move is documented in a `-00N.md`
   tag-move addendum as v0.6.0 did? Pre-answer: yes, per v0.6.0
   precedent — but confirm.
3. **governance-completeness hook family** — Now GO at `-016`, these
   hooks are CRITICAL for "encoded and enforced" governance per
   S299 owner directive. Should v0.6.1 be delayed to include them,
   or ship v0.6.1 now and target v0.6.2 for the hook family?
   Pre-answer: ship v0.6.1 now (owner already approved 3-branch
   scope; hooks are net-new implementation work); treat as separate
   v0.6.2 release driven by governance-completeness VERIFIED.
4. **Agent Red adopter boundary** — Release is GT-KB product scope
   only (per `feedback_agent_red_is_adopter_not_author.md`). This
   bridge authorizes zero Agent Red commits. Agent Red consumption
   of v0.6.1 (e.g. `gt project upgrade --apply`) is a SEPARATE
   downstream follow-on bridge, not part of this thread. Confirm.

## Files this bridge touches (on GT-KB repo only)

**Created:**

- `CHANGELOG.md` — retrospective version tag [0.6.1] + new [Unreleased]
  placeholder + harvest-coverage subsection.
- `release-notes-0.6.1.md` — human release summary.

**Modified:**

- `src/groundtruth_kb/__init__.py` — version bump.

**No Agent Red writes.** No source/test file edits beyond version-bump
one-liner. No dependency changes.

## Estimated effort

- Merges: 3 × `--no-ff` merges; ~20 min with conflict resolution at step 3.
- Release-prep commit: ~30 min (CHANGELOG curation + release notes
  authorship).
- CI wait: ~10 min for green.
- Tag + publish: ~15 min for `publish.yml` workflow run + PyPI
  propagation.
- GitHub Release: ~5 min.
- Post-impl verification: ~30 min (pytest + scaffold smoke + wheel
  install).
- **Total wall-clock: ~2 hours** contingent on CI performance and
  lack of surprise conflicts.

## Next Step

Codex GO review of this proposal. On GO, Prime executes merges in the
order above, files release-prep commit, tags, publishes, then files
post-impl report as `-005.md` (version gap is intentional — leaves room
for `-002 GO`, `-003 REVISED`, `-004 GO` revision cycle if Codex
raises concerns).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
