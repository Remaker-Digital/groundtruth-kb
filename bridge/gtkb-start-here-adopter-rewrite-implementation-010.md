# VERIFIED Review: GT-KB Start Here Adopter Rewrite Revised Post-Implementation v2

**Verdict:** VERIFIED
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed report:** `bridge/gtkb-start-here-adopter-rewrite-implementation-009.md`
**Prior NO-GO:** `bridge/gtkb-start-here-adopter-rewrite-implementation-008.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Verification worktree inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb-start-here-remediation`
**Verified commit:** `1b0bde4`

## Claim

The revised filing is VERIFIED for commit `1b0bde4`. The two defects from
`-008.md` are closed: the named feature branch now points at the same commit
being verified, and the required evidence gate passes at that target in an
isolated worktree with no tracked modifications.

This verification applies to the committed tree at `1b0bde4`. The shared main
checkout of `groundtruth-kb` currently has unrelated working-tree dirt, so it
must not be treated as the verified artifact surface until cleaned or reset to
the verified commit.

## Evidence

- `bridge/gtkb-start-here-adopter-rewrite-implementation-009.md:8` names
  `1b0bde4` as the single verification tip and current branch tip.
- `bridge/gtkb-start-here-adopter-rewrite-implementation-009.md:30` states
  that the branch-tip/evidence-tip mismatch from `-008.md` is closed by
  regenerating evidence artifacts at the canonical-terminology tip.
- In the target repo, `git rev-parse --short HEAD` and
  `git rev-parse --short feat/start-here-adopter-rewrite` both returned
  `1b0bde4`.
- `git diff --name-status 1b0bde4..feat/start-here-adopter-rewrite` returned
  no output, confirming the feature branch points exactly at the reported
  verification commit.
- The isolated verification worktree was on `1b0bde4` and `git diff
  --name-status` plus `git diff --cached --name-status` returned no output.
  `git status --short --branch` showed only untracked verification logs and
  site-output folders.
- `scripts/collect_evidence_metrics.py:67` defines the gate-bound comparison
  fields, and `scripts/collect_evidence_metrics.py:344`,
  `scripts/collect_evidence_metrics.py:355`, and
  `scripts/collect_evidence_metrics.py:379` enforce gate commit consistency,
  live-snapshot schema sanity, and rendered-markdown consistency.
- `scripts/render_evidence_md.py:1` defines `docs/evidence.md` as rendered from
  `docs/_generated/evidence_metrics.json`, and
  `scripts/render_evidence_md.py:287` writes the generated markdown.
- `scripts/starthere_ids.txt:1` through `scripts/starthere_ids.txt:12` list the
  exact `SPEC-STARTHERE-*` IDs; no wildcard assertion command is required.
- `mkdocs.yml:56` through `mkdocs.yml:62` include the adopter pages in nav, and
  `README.md:27` through `README.md:30` link the adopter path.

## Verification Commands Run

All commands below were run in
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb-start-here-remediation`
at `1b0bde4`.

| Gate | Command | Result |
|------|---------|--------|
| Branch target | `git rev-parse --short HEAD` | `1b0bde4` |
| Tracked clean check | `git diff --name-status`; `git diff --cached --name-status` | no output |
| Evidence verify | `python scripts/collect_evidence_metrics.py --verify` | exit 0; `3 gate-bound metrics agree at commit 1b0bde4`; markdown matches fresh render; live snapshots informational only |
| Link integrity | `python scripts/check_doc_links.py` | exit 0; `Links checked: 140`; `Failures: 0` |
| Docs CLI coverage | `python scripts/check_docs_cli_coverage.py` | exit 0; `All documentation checks passed.` |
| MkDocs strict | `python -m mkdocs build --strict --site-dir _site_verify_codex_010` | exit 0; documentation built in 1.39s; informational out-of-nav reports only |
| Pytest | `python -m pytest tests/ -q --deselect tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs` | exit 0; `1265 passed, 1 deselected, 1 warning in 333.63s` |
| Exact-ID CLI assertions | PowerShell loop over `scripts/starthere_ids.txt` invoking `python -m groundtruth_kb assert --spec <id>` | exit 0; `Summary: pass=12 fail=0` |
| Exact-ID Python API assertions | `run_all_assertions(db, repo, spec_id=<id>)` loop over `scripts/starthere_ids.txt` | exit 0; `Python API sweep: 12/12 specs passed across 12 IDs.` |
| Render output | `python scripts/render_evidence_md.py --to .render_check_codex_010.md` plus SHA-256 comparison | raw-byte-identical output file; committed and rendered-file SHA-256 both `c3ab3d6ec2752d6b8858d2c2ef57186bda930cb215532c0521d8d7c2fa2bd00b` |

The pytest result differs slightly from the transcript in `-009.md`
(`1265 passed` locally rather than `1253 passed, 12 skipped`), but the gate
still passes and the total collected/deselected shape is consistent with the
evidence metric value of `1266`.

## Findings

No blocking findings remain.

### Non-blocking residual note - shared checkout is dirty

The main `groundtruth-kb` checkout is currently dirty despite `HEAD` pointing at
`1b0bde4`; observed working-tree entries included modified evidence files,
modified `scripts/collect_evidence_metrics.py`, and deleted
`scripts/render_evidence_md.py` / `scripts/starthere_ids.txt`.

This does not block VERIFIED because the isolated worktree verifies the commit
that the named branch points to, and the branch itself has no commits after
`1b0bde4`. It is still operationally important: any merge, PR update, or
follow-up filing should be based on the clean committed tree, not the dirty
shared checkout.

### Non-blocking residual note - verification outputs are untracked

The isolated worktree has untracked logs and MkDocs site-output directories,
including outputs created during this Codex verification pass. `git diff` and
`git diff --cached` are empty, so these files did not affect the verified
tracked tree.

## Decision

VERIFIED for `feat/start-here-adopter-rewrite` at commit `1b0bde4`. No owner
decision is required for this verification.

