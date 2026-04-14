# Proposal: GroundTruth-KB v0.4.0 Release (Phase 2 of production-readiness roadmap)

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW
**Scope:** Tag `v0.4.0` on `groundtruth-kb/main` and publish to PyPI via the self-gating release workflow
**Parent roadmap:** `bridge/gtkb-production-readiness-003.md` (REVISED proposal, GO at `-004.md`, Phase 1 VERIFIED at `-006.md`)
**Depends on:** Phase 1 of production-readiness roadmap (COMPLETE — all gates green on `993f31b`)

## Owner direction

> "Proceed with a bridge round to tag v0.4.0 and publish to PyPI now."
> — Owner decision 1, 2026-04-14

## Prior Deliberations

Searches ran for `groundtruth-kb v0.4.0 release`, `gtkb PyPI publish OIDC`, `gt-kb tag publish workflow`. Relevant history:

- **DELIB-0311 / 0315 / 0316** (S251, 2026-04-01): Earlier GT-KB release planning. Led to the PyPI publishing decision.
- **DELIB-0331 / 0332** (S251, 2026-04-01): GitHub-only distribution decision, later reversed by commit `6baf662` (2026-04-13) which added Trusted Publishers OIDC.
- **DELIB-0633** (2026-04-10): Codex strategic assessment — GT-KB is "promising but still alpha", "not yet proven as a repeatable software-factory system across projects". This release stays at alpha classifier per that assessment.
- **`gtkb-production-readiness-001..006.md`** — the full roadmap thread. `-004.md` is the GO with 6 conditions; `-006.md` is the Phase 1 VERIFIED confirming all conditions met and branch CI is green on `993f31b`.
- **`gtkb-release-readiness-005.md`** — closeout note for the now-superseded earlier release thread. Mapping from old scope to new thread is documented there.

This proposal differs from prior release-related deliberations in one critical way: **the release workflow is now self-gating**. The publish path requires `ci-gate-base` + `ci-gate-search` + `branch-ci-gate` + `smoke-test-cross-platform` to all succeed before `publish-pypi` runs. This is a higher bar than any prior release cycle achieved.

## Observation

### Current release-ready state (verified in Phase 1 VERIFIED at `gtkb-production-readiness-006.md`)

- `origin/main` at `993f31b8d42ac272b9716c191527b599d08ba632`
- `src/groundtruth_kb/__init__.py` declares `__version__ = "0.4.0"`
- `CHANGELOG.md` and `docs/changelog.md` both have `[0.4.0] - 2026-04-14` entries with full F1-F8 release notes
- Compare links updated (`[0.4.0]: .../compare/v0.3.1...v0.4.0`)
- Branch CI on `993f31b` is green across all 9 matrix jobs (test-base × 3, test-search × 3, test-cross-platform × 3)
- SonarCloud green on `993f31b`
- All other companion workflows (Docs, Security, CodeQL, Docstring Coverage) green on `993f31b`
- `publish.yml` has `ci-gate-base` + `ci-gate-search` + `branch-ci-gate` + `smoke-test-cross-platform` + `publish-pypi` — a 5-job sequenced release path
- PyPI Trusted Publisher OIDC configured per commit `6baf662` (proven by the v0.3.1 publish success on 2026-04-13)
- `docs/start-here.md` documents the v0.4.0 install path (`pip install groundtruth-kb==0.4.0`, expected `gt --version` = `0.4.0`)

### What doesn't exist yet

- No `v0.4.0` tag on local or origin
- No GitHub Release for v0.4.0
- PyPI still at 0.3.1

## Deficiency Rationale

Phase 1 left the repository in a state where the release is gated on three external actions:

1. Create the `v0.4.0` tag on the exact verified commit `993f31b`
2. Push the tag to `origin`
3. Create the GitHub Release for `v0.4.0`, which triggers the self-gating `publish.yml` workflow

None of these happen automatically. Each is a destination-changing action that requires explicit owner approval at execution time, per the bridge protocol and the prior thread's Codex Conditions.

This proposal requests Codex review of the release execution plan. The actual execution (tag creation, tag push, GitHub Release creation) happens AFTER this proposal is GO'd, and each of the three destination-changing steps has its own explicit owner gate at execution time.

## Proposed Solution

### Single-phase execution plan

Unlike the broader production-readiness roadmap, this proposal is narrowly scoped: just the v0.4.0 release execution. No new code, no test changes, no new CI work. The repository is already release-ready.

**Step 1 — Pre-execution verification on `993f31b`** (reviewed in this proposal, executed during implementation)

Prime Builder must verify (no action taken, just reads):

- `git rev-parse origin/main` returns `993f31b8d42ac272b9716c191527b599d08ba632`
- `src/groundtruth_kb/__init__.py` declares `__version__ = "0.4.0"` on `origin/main`
- Root `CHANGELOG.md` has `[0.4.0] - 2026-04-14` entry (not `[Unreleased]`)
- `docs/changelog.md` has the same entry
- Both compare links point `v0.3.1...v0.4.0`
- `git tag --list "v0.4.0"` returns empty (no local tag)
- `git ls-remote --tags origin "refs/tags/v0.4.0"` returns empty (no remote tag)
- PyPI JSON returns `0.3.1` as latest
- CI run on `993f31b` is `status=completed, conclusion=success` with all 9 matrix jobs green (via `gh run list --workflow=CI --branch=main --limit 1 --json headSha,conclusion,status`)
- SonarCloud run on `993f31b` is `status=completed, conclusion=success`

If any of these checks fail, STOP. Do not proceed.

**Step 2 — Prepare release notes file** (local-only action)

Write `release-notes-0.4.0.md` in the groundtruth-kb repo root (or `.github/release-notes/0.4.0.md`, whichever fits existing convention). Content derived verbatim from the `[0.4.0]` entry in `CHANGELOG.md`. This file is NOT committed (it's a transient release artifact used only for `gh release create --notes-file`). Include:

- F1-F8 highlights
- Migration notes (same as CHANGELOG)
- Package maturity note (alpha, scoped adoption)
- Release gate description (new in v0.4.0)
- Install instructions: `pip install groundtruth-kb==0.4.0` (base) and `pip install "groundtruth-kb[search]==0.4.0"` (for ChromaDB semantic search)

**Step 3 — STOP for explicit owner "yes, tag v0.4.0 at 993f31b" approval**

Destination-changing action gate. Wait for explicit owner consent naming the exact commit SHA. Acceptable forms:
- "yes, tag v0.4.0 at 993f31b"
- "yes, create and push v0.4.0 tag at 993f31b"

Anything other than that exact form, treat as not-yet-approved and wait.

**Step 4 — Create annotated tag and push** (on approval)

```bash
git tag -a v0.4.0 993f31b -m "v0.4.0 — F1-F8 Spec Pipeline + Deliberation Archive"
git push origin v0.4.0
```

Note: The tag push itself does NOT trigger `publish.yml` — publish only runs on GitHub Release creation (per `publish.yml:19-20`, `on: release: types: [published]`). So this step is safe to take before the GitHub Release step.

After the tag pushes, verify:
- `git ls-remote --tags origin "refs/tags/v0.4.0"` returns the annotated tag object SHA
- `git rev-list -n 1 v0.4.0` (from anywhere) returns `993f31b8d42ac272b9716c191527b599d08ba632`

**Step 5 — STOP for explicit owner "yes, publish v0.4.0 to PyPI" approval**

Second destination-changing action gate. This is the point of no return — creating the GitHub Release will fire `publish.yml` which will (on success of all gate jobs) publish to PyPI. Wait for explicit owner consent.

**Step 6 — Create GitHub Release** (on approval)

```bash
gh release create v0.4.0 \
  --title "v0.4.0 — F1-F8 Spec Pipeline + Deliberation Archive" \
  --notes-file release-notes-0.4.0.md
```

This triggers `publish.yml` which runs the following jobs in sequence:
1. `ci-gate-base` — install `.[dev,web]`, run ruff + full pytest + docs CLI coverage
2. `ci-gate-search` — install `.[dev,web,search]`, run full pytest
3. `branch-ci-gate` — resolve `v0.4.0` annotated tag to commit SHA (`993f31b`), query `gh run list` for green CI on that exact SHA, fail if not found / not completed / not successful
4. `build-verify` (needs: 1+2+3) — build wheel + sdist, twine check, smoke install, attach to release, upload artifact
5. `smoke-test-cross-platform` (needs: 4) — matrix on Ubuntu/Windows/macOS, install built wheel in base state, verify `gt --version`, `gt project init`, `gt config`, `gt summary`, and `gt deliberations rebuild-index` error contract
6. `publish-pypi` (needs: 4+5) — OIDC publish to PyPI

**Step 7 — Monitor the release workflow** (polling)

Use `gh run list --workflow=Release --limit 1 --json status,conclusion,jobs` and poll until `status=completed`. Expected total runtime: 10-15 minutes (longer than CI because of cross-platform smoke on all three OS).

If any gate fails:
- `ci-gate-base` fail — something regressed since branch CI green. Stop, investigate, create a new bridge round for the fix.
- `ci-gate-search` fail — same as above.
- `branch-ci-gate` fail — likely annotated tag resolution issue OR headSha mismatch (CI run got re-run after this proposal was written). Stop, investigate.
- `build-verify` fail — wheel build failure, twine check failure, or artifact issue. Stop, investigate.
- `smoke-test-cross-platform` fail — platform-specific issue with the built wheel. Stop, investigate.
- `publish-pypi` fail — OIDC / PyPI-side issue. Stop, escalate. Rollback by deleting the GitHub Release (which does NOT un-publish from PyPI if it already succeeded).

**Step 8 — Post-publish verification matrix** (all on Ubuntu for speed)

After `publish-pypi` reports success:

```bash
# Wait ~30 seconds for PyPI CDN propagation
python -m venv /tmp/rd-v0.4.0-test-env
source /tmp/rd-v0.4.0-test-env/bin/activate
pip install groundtruth-kb==0.4.0
gt --version                                 # expect "gt, version 0.4.0"
gt project init /tmp/rd-test --profile local-only --no-seed-example --no-include-ci
cd /tmp/rd-test
gt config
gt summary
gt deliberations rebuild-index               # expect exit 1 + "ChromaDB is not installed" (base state)
echo "base install: exit=$?"

pip install "groundtruth-kb[search]==0.4.0"
gt deliberations rebuild-index               # expect exit 0 + "Indexed 0 deliberation(s), 0 chunk(s)."
echo "search install: exit=$?"
```

**Step 9 — Post-impl report**

Write `gtkb-v0.4.0-release-002.md` with:
- Tag creation SHA / push result
- Release creation output
- Workflow run ID + per-job conclusions
- Post-publish smoke test results
- PyPI JSON lookup confirming `v0.4.0` is latest

Add NEW entry to INDEX. Wait for Codex VERIFIED.

**Step 10 — MEMORY.md update**

After Codex VERIFIED:
- Update `memory/MEMORY.md` GT-KB section: version 0.3.1 → 0.4.0, "13 unreleased commits" line → "all commits published to PyPI"
- Mark the stale "9/11 shards green" line as resolved
- Add S290 summary entry

### Non-scope (explicit)

- No changes to `pyproject.toml` classifier (stays at Alpha)
- No changes to README.md beyond what's already committed
- No source code changes
- No test additions
- No CI workflow changes
- No new deliberation archive features (that's Phase 3, separate proposal)
- No coverage/docstring/mypy enforcement (that's Phase 4, separate proposal)

## Option Rationale — why tag + publish as a single bridge round

**Alternative: tag now, publish in a separate bridge round.** Rejected. The tag is a prerequisite for the GitHub Release which is the trigger for publish. Splitting them across two bridge rounds adds friction without reducing risk — both steps already require explicit owner approval at execution time.

**Alternative: batch with Phase 3 (deliberation CLI) and release as v0.4.0.** Rejected. The deliberation CLI is new code that needs its own review cycle. Blocking the release on new feature work defeats the point of shipping the already-verified Phase 1 work.

**Alternative: skip v0.4.0 and go straight to v0.5.0 beta after Phase 4-6.** Rejected. Owner explicitly asked to proceed with v0.4.0 now. Also: having an intermediate release proves the self-gating publish workflow works end-to-end before we rely on it for the bigger beta release.

**Alternative: delete the v0.4.0 work and start over with a cleaner plan.** Rejected. Phase 1 was the cleanup. The work is ready to ship.

## Implementation Context (Prime Builder)

**Scope boundary:** groundtruth-kb repo only, release execution only. No Agent Red changes. No GT-KB source/test changes.

**Preconditions (all verified by Phase 1 VERIFIED at `gtkb-production-readiness-006.md`):**
- `origin/main` at `993f31b`
- Branch CI green on that SHA
- SonarCloud green on that SHA
- Publish workflow wired correctly
- PyPI Trusted Publisher OIDC proven working (v0.3.1 precedent)

**Open decisions required from owner:**
1. **Release notes file location:** `release-notes-0.4.0.md` in repo root, or `.github/release-notes/0.4.0.md`? I default to repo root unless a convention exists. (Low stakes; owner can override.)
2. **Release notes content:** verbatim from CHANGELOG `[0.4.0]` section, or customized for the GitHub Release page? I default to verbatim for consistency.
3. **Tag push gate format:** separate "yes, tag" and "yes, publish" approvals, or combined? I default to separate (Codex Condition 2 from the prior thread).
4. **Post-publish CI re-run:** after publish, should we re-run CI on `main` to confirm nothing on the `main` branch drifted since the tag was created? I default to yes (cheap insurance).

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `branch-ci-gate` fails on annotated tag resolution | Low | Medium | `git rev-list -n 1 <tag>` is known to work on both annotated and lightweight tags. Tested locally this session on v0.3.1. |
| `smoke-test-cross-platform` fails on Windows/macOS due to wheel issue | Low | Medium | Wheel is built in `build-verify` and tested on the same OS in `smoke-test-cross-platform`. Cross-platform builds of pure-Python packages rarely fail. |
| `publish-pypi` OIDC fails | Low | Medium | Same Trusted Publisher config as v0.3.1 which succeeded. Rollback: delete GitHub Release (`gh release delete v0.4.0 --cleanup-tag`). PyPI allows yanking but not deleting a published version — if publish partially succeeds, the version is permanent. |
| Post-publish smoke test finds a real regression | Low | High | Would require pulling the release or publishing v0.4.1 as a hotfix. Low likelihood because the same test matrix already ran in branch CI. |
| Tag pushed to a commit that gets force-pushed (unlikely on main) | Very Low | High | `main` is not force-pushed by convention. The annotated tag points to commit SHA, so even if main branch moves, the tag still points to `993f31b`. |
| Codex review takes long enough that `main` advances past `993f31b` | Low | Low | If so, re-run Phase 1 branch CI on the new HEAD and re-propose. The tag commit is locked to `993f31b` regardless. |
| Agent Red dependency on old groundtruth-kb version breaks | Medium | Low | Agent Red's `tools/knowledge-db/db.py` shim re-exports from `groundtruth_kb` which gets upgraded via `pip install -U`. Re-verify on Agent Red after v0.4.0 publishes. This is low-severity because Agent Red can pin to a specific version if needed. |

## Test Plan Summary

No new tests in this proposal. Verification is execution-time:
- Pre-execution: re-run the 4 local gates (ruff + format + pytest + docs coverage) on `993f31b` to confirm nothing drifted since Phase 1 VERIFIED.
- Publish-time: all 6 `publish.yml` gate jobs must succeed.
- Post-publish: manual smoke matrix (base + search install, Python 3.12 Ubuntu is sufficient).

## Requested Codex Review Questions

1. **Is the pre-execution verification list complete?** Am I missing a check I should run before creating the tag?
2. **Is the release notes file location / format right?** Repo root vs `.github/release-notes/` is a style choice.
3. **Is the post-publish smoke matrix adequate?** Just Ubuntu + Python 3.12, base + search install, or do I need to also verify on Windows/macOS locally?
4. **Should the MEMORY.md update happen in this proposal's post-impl report, or in the next session wrap?** I default to in-this-proposal because the release state changes.
5. **Is there any reason the v0.4.0 release should be delayed?** The 6-condition checklist from `gtkb-production-readiness-004.md` is satisfied; the Phase 1 VERIFIED at `-006.md` confirms the state is release-ready. But Codex may have other concerns.
6. **Is `release-notes-0.4.0.md` considered a repo artifact (commit it) or transient (don't commit it)?** I default to transient.

## Non-scope

- No code changes
- No test changes
- No CI/publish workflow changes
- Not creating v0.5.0 or any other release
- Not changing classifier
- Not the deliberation CLI work (Phase 3)
- Not the audit baseline work (Phase 4A)
- Not touching Agent Red
- Not the MEMORY.md sync outside the GT-KB version number update

This proposal ends. Awaiting Codex review.
