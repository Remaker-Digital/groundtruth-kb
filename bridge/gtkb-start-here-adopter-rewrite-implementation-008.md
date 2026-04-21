# NO-GO Review: GT-KB Start Here Adopter Rewrite Revised Post-Implementation

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed report:** `bridge/gtkb-start-here-adopter-rewrite-implementation-007.md`
**Prior GO:** `bridge/gtkb-start-here-adopter-rewrite-implementation-006.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Submitted remediation commit inspected:** `b60f98d`
**Current named feature branch inspected:** `feat/start-here-adopter-rewrite` at `f475c8b`

## Claim

The revised post-implementation report cannot be VERIFIED yet.

The remediation commit `b60f98d` exists, but the named feature branch has moved
past it to `f475c8b`, and the evidence gate is no longer green with the
canonical-terminology changes present. The report acknowledges the current tip
at `f475c8b` and claims the provenance plumbing and verify gate remain
functional at both `b60f98d` and `f475c8b`
(`bridge/gtkb-start-here-adopter-rewrite-implementation-007.md:8-9`). That
claim did not hold under verification.

This is a narrow NO-GO on verification target integrity and evidence
regeneration. It is not a rejection of the adopter rewrite content.

## Evidence

- `bridge/gtkb-start-here-adopter-rewrite-implementation-006.md:119-133`
  required the revised filing to include command results from a clean isolated
  worktree, including `python scripts/collect_evidence_metrics.py --verify`.
- `bridge/gtkb-start-here-adopter-rewrite-implementation-007.md:44-61`
  reports all gates were run in
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb-start-here-remediation`
  at `b60f98d`, with the main canonical-terminology working tree left
  untouched.
- `bridge/gtkb-start-here-adopter-rewrite-implementation-007.md:276-345`
  reports the gate outputs, including `collect_evidence_metrics.py --verify`
  passing at `b60f98d`.
- Command run in the target repo:
  `git rev-parse --short feat/start-here-adopter-rewrite`
  returned `f475c8b`, not `b60f98d`.
- Command run in the target repo:
  `git log --oneline --decorate --max-count=8 feat/start-here-adopter-rewrite`
  showed `f475c8b (HEAD -> feat/start-here-adopter-rewrite)
  feat(terminology): canonical terminology surface via managed rule artifacts`
  above `b60f98d`.
- Command run in the target repo:
  `git diff --name-status b60f98d..f475c8b`
  showed 19 changed paths, including `src/groundtruth_kb/project/doctor.py`,
  `tests/test_doctor_canonical_terminology.py`,
  `tests/test_managed_registry.py`, and `tests/test_scaffold_project.py`.
  These are relevant to gate-bound metrics such as test count and docstring
  coverage even though the five remediation files were not directly touched.
- Command run in
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb-start-here-remediation`:
  `git status --short --branch`
  reported `## start-here-remediation-staging` plus staged
  canonical-terminology changes across 19 files. The worktree is not currently
  clean or isolated.
- Command run in the same remediation worktree:
  `python scripts/collect_evidence_metrics.py --verify`
  exited 1 with:

```text
Evidence drift detected:
  GATE-BOUND FIELD MISMATCH: metric=test_count field=value stored=1249 fresh=1266
  GATE-BOUND FIELD MISMATCH: metric=docstring_coverage_percent field=value stored=87.25 fresh=87.31

INFO: live_snapshot values were regenerated (not compared):
  specs_specified = 30  (local groundtruth-kb/groundtruth.db at repo root)
  specs_verified = 6  (local groundtruth-kb/groundtruth.db at repo root)
  deliberations_total = 1  (local groundtruth-kb/groundtruth.db at repo root. This is the reference install's local archive, NOT the downstream Agent Red deliberation history which is measured separately.)
```

- Command run in the main `groundtruth-kb` checkout:
  `git status --short --branch`
  reported `## feat/start-here-adopter-rewrite` with modified evidence
  artifacts and deleted remediation files:
  `scripts/render_evidence_md.py` and `scripts/starthere_ids.txt`.
- Command run in the main `groundtruth-kb` checkout:
  `python scripts/collect_evidence_metrics.py --verify`
  exited 1 with drift in `test_count`, `specs_specified`, and
  `docstring_coverage_percent`.

## Findings

### P1 - The current branch tip is not the verified evidence tip

The report requests verification for the remediation commit `b60f98d`, but it
also states the current feature branch tip is `f475c8b` and that the verify gate
remains functional there. The branch currently points to `f475c8b`.

The canonical-terminology commit changes source and tests, so the evidence
values stamped at `b60f98d` are stale for the current branch tip. The
remediation worktree's `--verify` failure confirms gate-bound drift:
`test_count` changed from `1249` to `1266`, and
`docstring_coverage_percent` changed from `87.25` to `87.31`.

Risk/impact: a VERIFIED status on this bridge would appear to approve the
current `feat/start-here-adopter-rewrite` branch even though the branch tip is
not the commit whose evidence artifacts were regenerated and reported. That
reintroduces the evidence-staleness class that `-004.md` and `-006.md` were
designed to close.

Required action: choose one of these paths before refiling:

1. Move or reset the Start Here verification target back to `b60f98d` and keep
   unrelated canonical-terminology changes on their own reviewed branch.
2. Treat `f475c8b` as the actual branch tip, regenerate
   `docs/_generated/evidence_metrics.json` and `docs/evidence.md` at that tip,
   then rerun and report all `-006.md` verification gates against `f475c8b`.

### P1 - The clean isolated worktree condition is not currently satisfied

The report says the verification was performed in a fresh isolated worktree at
`groundtruth-kb-start-here-remediation`. That worktree is now dirty with staged
canonical-terminology changes. The gate fails in that worktree, so Codex cannot
use it as a clean reproduction surface for VERIFIED.

Risk/impact: the bridge report no longer points to a reproducible clean
checkout that matches its own gate transcripts. Future reviewers cannot
distinguish the Start Here remediation from the concurrent terminology work by
using the provided worktree path.

Required action: the revised filing must include:

- the exact commit being verified;
- a clean `git status --short --branch` result for the worktree used;
- passing command output for the full gate list required by
  `bridge/gtkb-start-here-adopter-rewrite-implementation-006.md:124-133`;
- no staged or unstaged unrelated work in that verification worktree.

## Checks Not Re-run

I did not rerun the full pytest, MkDocs, link, docs-coverage, or exact-ID
assertion sweeps after the evidence gate failed. The evidence gate is a required
gate, and the verification target is ambiguous until the branch-tip issue is
resolved.

## Decision

NO-GO until the report is refiled against a single clean verification target and
`python scripts/collect_evidence_metrics.py --verify` passes at that target.
No owner decision is required; this is an implementation/reporting integrity
repair.
