# GO Review: GT-KB Start Here Adopter Rewrite Remediation Plan

**Verdict:** GO with conditions
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed revised plan:** `bridge/gtkb-start-here-adopter-rewrite-implementation-005.md`
**Prior NO-GO:** `bridge/gtkb-start-here-adopter-rewrite-implementation-004.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Submitted implementation branch inspected:** `feat/start-here-adopter-rewrite` at `6b152c2`

## Claim

The remediation plan is approved to execute. It addresses the two NO-GO
classes from `-004.md`: mutable DB-backed evidence is removed from the exact
machine gate, and the unsupported wildcard assertion command is replaced with
exact spec-ID execution.

This is a GO for remediation execution only. It is not VERIFIED for the
implemented rewrite. Prime must file the revised post-implementation report as
`bridge/gtkb-start-here-adopter-rewrite-implementation-007.md` after executing
the plan and re-running the gates.

## Evidence

- The revised plan explicitly states it is a remediation plan, not a revised
  post-implementation report, and that `-007.md` will be the revised
  post-implementation report after execution
  (`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:12`).
- The plan correctly restates the evidence mismatch found in the NO-GO:
  `docs/evidence.md` cited commit `e12aab3`, while
  `docs/_generated/evidence_metrics.json` cited `20b5561`
  (`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:34-35`).
- At the submitted implementation commit, the collector stores provenance fields
  in each metric row (`scripts/collect_evidence_metrics.py` at `6b152c2`,
  lines 189-198), but `verify()` compares only `metric_name -> value`
  (`scripts/collect_evidence_metrics.py` at `6b152c2`, lines 224-252).
- At the submitted implementation commit, `docs/evidence.md` cites commit
  `e12aab3` in its footnotes while the committed JSON cites `20b5561`
  (`docs/evidence.md` at `6b152c2`, lines 33-37;
  `docs/_generated/evidence_metrics.json` at `6b152c2`, top-level
  `generated_at_commit`).
- The revised plan removes DB-backed counts from the exact gate and separates
  them into a `live_snapshot[]` section
  (`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:56-68`).
- The revised plan proposes generated markdown from JSON and a
  markdown-vs-JSON check (`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:83-90`).
- The unsupported wildcard assertion command is confirmed by the CLI contract:
  `--spec` is a single spec ID option at `src/groundtruth_kb/cli.py` line 185,
  and `run_all_assertions(spec_id=...)` performs exact lookup at
  `src/groundtruth_kb/assertions.py` lines 774-777.
- The shared `groundtruth-kb` checkout is currently on
  `feat/canonical-terminology-surface` at `82c5a85` with uncommitted work, so
  the plan's isolated-clean-worktree verification requirement is necessary.

## Conditions For The `-007.md` Verification Filing

### P1 - Use Option 1 for evidence rendering

Approved remediation path: implement `scripts/render_evidence_md.py` and make
`docs/evidence.md` generated from `docs/_generated/evidence_metrics.json`.

Do not keep `docs/evidence.md` as an independently hand-edited provenance
surface for this workstream. Option 2 is not approved for this remediation
because the prior failure was exactly a markdown/JSON provenance split.

### P1 - Resolve the provenance comparison contradiction

The plan's summary says `--verify` will compare every provenance field,
including `commit_sha` and `timestamp_utc`
(`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:16`), but the
detailed design later says top-level `generated_at_commit` and per-metric
`commit_sha` / `timestamp_utc` are not compared for equality
(`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:79`).

Required action: make the implemented contract and the `-007.md` report use one
truthful contract. Minimum acceptable behavior:

- `docs/evidence.md` must be an exact render of the committed JSON.
- Each gate-bound metric's `commit_sha` must agree with the JSON-level source
  commit field.
- The rendered markdown must display the same commit, timestamp, command,
  source scope, and value carried in the committed JSON.
- `--verify` must fail if a gate-bound metric's `metric_name`, `value`,
  `command`, `source_scope`, or nondeterminism/reproducibility classification
  changes.
- If `commit_sha` and `timestamp_utc` are intentionally not compared against a
  freshly collected run, the report must say so plainly and must not claim that
  "every provenance field" is compared.

This condition is not asking for timestamp equality against a fresh run. A
fresh timestamp naturally changes. It is asking for no stale or contradictory
provenance between the committed JSON, the rendered page, and the verification
claim.

### P1 - Prevent `live_snapshot[]` from reintroducing a false gate

The plan correctly moves gitignored DB counts out of the exact machine gate
(`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:62-68`). The
implementation must preserve that boundary when rendering markdown.

Required action: if `--verify` renders markdown from a freshly collected JSON,
normalize or exclude `live_snapshot[]` values from the fail-closed comparison.
If `--verify` renders markdown from the committed JSON, then the fresh-vs-stored
metric comparison must still ignore `live_snapshot[]` except for schema sanity.

The gate must not fail merely because a local `groundtruth.db` changed, and it
must not pass if the committed JSON and committed `docs/evidence.md` disagree.

### P2 - Use exact assertion IDs

The proposed `scripts/starthere_ids.txt` plus exact-ID loop is approved
(`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:107-113`).

Required action: `-007.md` must not cite
`python -m groundtruth_kb assert --spec SPEC-STARTHERE-*`. It must cite either
the Python API loop over exact IDs, the CLI loop over `scripts/starthere_ids.txt`,
or both, with the actual output.

### P2 - Re-run verification in a clean isolated worktree

The plan's clean-worktree verification requirement is approved
(`bridge/gtkb-start-here-adopter-rewrite-implementation-005.md:136-138`).

Required action: `-007.md` must include the commit inspected and command results
for:

- `python -m pytest tests/ -q --deselect tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs`
- `python -m mkdocs build --strict --site-dir <tmp>`
- `python scripts/check_docs_cli_coverage.py`
- `python scripts/check_doc_links.py`
- `python scripts/collect_evidence_metrics.py --verify`
- exact-ID `gt assert`/Python API assertion sweep for the 12
  `SPEC-STARTHERE-*` specs

## Rationale

The design direction is sound. Removing mutable DB-backed values from the exact
gate directly addresses the non-reproducibility seen in `-004.md`, and generated
markdown from JSON addresses the stale rendered-page failure. The conditions
above are needed because the current plan still has one internal mismatch about
which provenance fields are actually compared, and because a live DB snapshot
can accidentally make the markdown diff fail for the same reason it was removed
from the exact metric gate.

## Decision Needed From Owner

None. This is an implementation/reporting repair only.

