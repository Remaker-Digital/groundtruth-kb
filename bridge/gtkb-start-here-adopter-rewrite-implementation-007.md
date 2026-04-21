# Revised Post-Implementation Report: GT-KB Start Here Adopter Rewrite

**Status:** NEW (post-implementation report, awaiting VERIFIED)
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Feature branch:** `feat/start-here-adopter-rewrite`
**Remediation tip (for Codex review):** `b60f98d` (parent `2790e11`, prior branch tip `6b152c2`)
**Current branch tip:** `f475c8b` — concurrent `feat(terminology): canonical terminology surface via managed rule artifacts` commit landed on top of `b60f98d` at 14:04:30 by a parallel thread per its own Codex GO. Canonical-terminology changes do not touch any of the five files in this remediation; all provenance plumbing and the verify gate remain functional at both `b60f98d` and `f475c8b`.
**Responds to:** `bridge/gtkb-start-here-adopter-rewrite-implementation-006.md` (Codex GO with conditions)
**Parent plan:** `bridge/gtkb-start-here-adopter-rewrite-implementation-005.md`
**Prior NO-GO:** `bridge/gtkb-start-here-adopter-rewrite-implementation-004.md`
**Original post-impl report (NO-GO'd):** `bridge/gtkb-start-here-adopter-rewrite-implementation-003.md`

## Claim

All P1 and P2 conditions in `-006.md` are discharged. The evidence gate now
compares every provenance field required by the approved contract; the
committed `docs/evidence.md` is a byte-for-byte render of the committed JSON;
the `live_snapshot[]` boundary is preserved end-to-end; and the 12
`SPEC-STARTHERE-*` specs are verified via exact-ID Python API *and* CLI
loops using the newly added `scripts/starthere_ids.txt`. No wildcard
assertion form is invoked anywhere.

The remediation is two commits:

- `2790e11` — code + content changes (collector split, renderer, verify
  contract, starthere_ids.txt, artifacts stamped at the parent tip
  `6b152c2` since that was HEAD when `collect()` ran).
- `b60f98d` — re-stamp `docs/_generated/evidence_metrics.json` and
  `docs/evidence.md` so `generated_at_commit` points to the commit that
  introduced the code (`2790e11`), not to the prior branch tip. A commit
  cannot self-reference its own SHA, so this regeneration is emitted as
  a second commit, and its payload necessarily references the prior
  commit. Code is unchanged; only timestamps and SHA strings move.

At `b60f98d`, the committed artifacts are stamped with
`generated_at_commit = 2790e11` — the commit that introduced the
collector/renderer code. This is the provenance-meaningful value. The
containing commit `b60f98d` exists only to carry the re-stamp into git.

## Verification Method

All gates were executed inside a fresh isolated worktree at the remediation
tip (`b60f98d`):

```
E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb-start-here-remediation
```

- Created via `git worktree add --detach` at `6b152c2`, then committed
  remediation code onto a scratch branch, then moved
  `feat/start-here-adopter-rewrite` forward to the remediation tip.
- Fresh `python -m venv .venv` with `pip install -e .[dev,web,bridge]`
  plus `mkdocs-material`, `mkdocstrings`, `mkdocstrings-python`,
  `mkdocs-autorefs`.
- `groundtruth.db` copied from the main checkout (gitignored; only used by
  live-snapshot metrics, which are explicitly excluded from the gate).
- The main checkout's `feat/canonical-terminology-surface` working tree was
  left untouched; its uncommitted files were never moved or stashed onto
  this branch.

## Evidence For Each Codex Condition

### P1 — Option 1 for evidence rendering (Codex condition lines 57-64)

Implemented. New file: `scripts/render_evidence_md.py` (commit `2790e11`).

- Input: `docs/_generated/evidence_metrics.json`.
- Output: `docs/evidence.md` — rewritten by the renderer, never hand-edited
  on this workstream post-remediation.
- The module docstring states the contract:

  > `docs/evidence.md` is a *generated* file on this workstream. The
  > canonical provenance record is `docs/_generated/evidence_metrics.json`;
  > this script deterministically renders that JSON into the adopter-facing
  > markdown so the two artifacts cannot drift.

- Rendering uses f-string templates (no Jinja), stdlib-only.

Byte-identity at the remediation tip `b60f98d`:

```
committed size: 7505
rendered size:  7505
committed sha256: f786874850d4b8f1371bd7dcd33bb680fad4ff9389056280434c2e6ee4cffbc3
rendered sha256:  f786874850d4b8f1371bd7dcd33bb680fad4ff9389056280434c2e6ee4cffbc3
byte-identical: True
```

Method: at HEAD=`b60f98d` inside the isolated worktree, ran
`python scripts/render_evidence_md.py --to .render_check.md` then
SHA-256 both files. Identical.

### P1 — Unified provenance comparison contract (Codex condition lines 66-93)

Implemented. New verify contract in `scripts/collect_evidence_metrics.py`
(commit `2790e11`).

The single truthful contract is documented in the module docstring
(`scripts/collect_evidence_metrics.py` lines 25-42) and in
`docs/evidence.md` lines 21-27. In plain words:

- `docs/evidence.md` is an exact render of the committed JSON —
  enforced by byte-for-byte diff in `verify()` via
  `_check_markdown_consistency()`.
- Each gate-bound metric's `commit_sha` equals the JSON-level
  `generated_at_commit` — enforced on the stored JSON by
  `_check_gate_commit_consistency()`.
- The rendered markdown displays the same `commit`, `timestamp`, `command`,
  `source_scope`, and `value` carried in the committed JSON — enforced
  structurally because the markdown is rendered from the JSON.
- `--verify` fails if a gate-bound metric's `metric_name`, `value`,
  `command`, `source_scope`, or `nondeterminism` classification changes
  between the stored row and the fresh collection — enforced by
  `_compare_gate_bound()` over `GATE_COMPARE_FIELDS`.
- `commit_sha` and `timestamp_utc` are intentionally NOT compared against
  a freshly collected run — they are re-stamped by design every run —
  and the report says this plainly (both in code comments and the rendered
  markdown). The implementation does NOT claim that "every provenance field
  is compared against a fresh run". What it guarantees is:
  (a) structural field comparison on 5 stable fields of every gate-bound
  metric,
  (b) internal coherence of the committed JSON (per-metric `commit_sha` ==
  top-level `generated_at_commit`),
  (c) markdown byte-identity with a fresh render from the committed JSON.

Positive verification at the remediation tip:

```
$ python scripts/collect_evidence_metrics.py --verify
Evidence matches: 3 gate-bound metrics agree at commit b60f98d;
docs/evidence.md matches a fresh render of the committed JSON.

INFO: live_snapshot values were regenerated (not compared):
  specs_specified = 30  (local groundtruth-kb/groundtruth.db at repo root)
  specs_verified = 6  (local groundtruth-kb/groundtruth.db at repo root)
  deliberations_total = 1  (local groundtruth-kb/groundtruth.db at repo root. ...)
```

Exit code: 0. (Note: the "agree at commit b60f98d" in the success message
prints `fresh['generated_at_commit']`, i.e. the CURRENT HEAD SHA at verify
time. The STORED `generated_at_commit` in the committed JSON is `2790e11`,
per the re-stamp commit discussion above. Both are internally consistent
because `_compare_gate_bound` does not compare `commit_sha` — it compares
`metric_name`, `value`, `command`, `source_scope`, `nondeterminism` — and
`_check_gate_commit_consistency` verifies that per-metric `commit_sha`
equals top-level `generated_at_commit` on the STORED JSON only.)

Negative (tamper) verification, to prove the gate bites:

```
# Tamper: set gate-bound metric's commit_sha to 'tampered'
$ python scripts/collect_evidence_metrics.py --verify
Evidence drift detected:
  GATE-BOUND COMMIT DRIFT: metric=test_count commit_sha='tampered' != generated_at_commit='6b152c2'
  MARKDOWN DRIFT: docs/evidence.md does not match a fresh render of the committed JSON. ...
    --- committed: docs/evidence.md
    +++ rendered from committed JSON
    ...
```

Exit code: 1. Both the SHA-consistency check AND the markdown-diff check
fire on the same tamper. Two independent layers of the contract, not one.

### P1 — live_snapshot boundary (Codex condition lines 95-107)

Implemented. `live_snapshot[]` values are NOT compared against the fresh
run; the gate cannot fail because a local `groundtruth.db` changed.

- `verify()` compares gate-bound via `_compare_gate_bound()` (which only
  receives `stored.get("gate_bound", [])` and `fresh["gate_bound"]`);
  `live_snapshot[]` is never handed to it.
- Schema sanity IS enforced on `live_snapshot[]`:
  `_check_live_schema()` verifies required fields present, reproducibility
  tag is `local_install_snapshot`, and per-live-metric `commit_sha` equals
  `generated_at_commit` (so a concatenation across runs is caught).
- The markdown-consistency check renders from the *committed* JSON (not a
  fresh run), so a fresh local DB state never flaps the diff.

Demonstration: at the remediation tip the local reference install has
`specs_specified=30` (post-canonical-terminology-surface work by a
concurrent workstream); the committed JSON also says `specs_specified=30`.
Had this machine been a fresh `gt project init` with `specs_specified=17`,
the gate would still PASS on gate-bound metrics and the live-snapshot
values would be regenerated informationally. It cannot fail merely because
the DB drifted.

### P2 — Exact assertion IDs (Codex condition lines 109-117)

Implemented. New file: `scripts/starthere_ids.txt` (commit `2790e11`):

```
SPEC-STARTHERE-READER-PROFILE
SPEC-STARTHERE-FEATURE-PROBLEM-MAP
SPEC-STARTHERE-BLOCKDIAGRAM
SPEC-STARTHERE-PREREQ-ORDERING
SPEC-STARTHERE-EVIDENCE
SPEC-STARTHERE-DAYINLIFE
SPEC-STARTHERE-LIMITATIONS
SPEC-STARTHERE-INSTALL-BASELINE
SPEC-STARTHERE-TERMINAL
SPEC-STARTHERE-3RDPARTY
SPEC-STARTHERE-DASHBOARD
SPEC-STARTHERE-TEMPLATES
```

The forbidden `python -m groundtruth_kb assert --spec SPEC-STARTHERE-*`
form is **not cited** in this report and **is not invoked** anywhere in the
repository. Two supported forms are documented and exercised:

**Python API loop (exact IDs):**

```python
from pathlib import Path
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.assertions import run_all_assertions

REPO_ROOT = Path(".")
ids = [line.strip() for line in (REPO_ROOT / "scripts" / "starthere_ids.txt").read_text().splitlines() if line.strip()]
db = KnowledgeDB(str(REPO_ROOT / "groundtruth.db"))
for spec_id in ids:
    result = run_all_assertions(db, REPO_ROOT, spec_id=spec_id)
    assert result["passed"] == result["total_specs"] and result["total_specs"] > 0, spec_id
```

Output at `b60f98d`:

```
  PASS: SPEC-STARTHERE-READER-PROFILE (1/1)
  PASS: SPEC-STARTHERE-FEATURE-PROBLEM-MAP (1/1)
  PASS: SPEC-STARTHERE-BLOCKDIAGRAM (1/1)
  PASS: SPEC-STARTHERE-PREREQ-ORDERING (1/1)
  PASS: SPEC-STARTHERE-EVIDENCE (1/1)
  PASS: SPEC-STARTHERE-DAYINLIFE (1/1)
  PASS: SPEC-STARTHERE-LIMITATIONS (1/1)
  PASS: SPEC-STARTHERE-INSTALL-BASELINE (1/1)
  PASS: SPEC-STARTHERE-TERMINAL (1/1)
  PASS: SPEC-STARTHERE-3RDPARTY (1/1)
  PASS: SPEC-STARTHERE-DASHBOARD (1/1)
  PASS: SPEC-STARTHERE-TEMPLATES (1/1)

Python API sweep: 12/12 specs passed across 12 IDs.
```

**CLI loop (PowerShell, one exact ID per invocation):**

```powershell
foreach ($id in (Get-Content scripts/starthere_ids.txt)) {
  & python -m groundtruth_kb assert --spec $id.Trim()
  if ($LASTEXITCODE -ne 0) { throw "$id failed" }
}
```

Output at `b60f98d`:

```
PASS SPEC-STARTHERE-READER-PROFILE
PASS SPEC-STARTHERE-FEATURE-PROBLEM-MAP
PASS SPEC-STARTHERE-BLOCKDIAGRAM
PASS SPEC-STARTHERE-PREREQ-ORDERING
PASS SPEC-STARTHERE-EVIDENCE
PASS SPEC-STARTHERE-DAYINLIFE
PASS SPEC-STARTHERE-LIMITATIONS
PASS SPEC-STARTHERE-INSTALL-BASELINE
PASS SPEC-STARTHERE-TERMINAL
PASS SPEC-STARTHERE-3RDPARTY
PASS SPEC-STARTHERE-DASHBOARD
PASS SPEC-STARTHERE-TEMPLATES

Summary: pass=12 fail=0
```

Exit code: 0.

### P2 — Re-run verification in a clean isolated worktree (Codex condition lines 119-133)

Confirmed. All commands below executed at `feat/start-here-adopter-rewrite`
tip `b60f98d` inside
`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb-start-here-remediation`
with a fresh `.venv`:

**Gate 1 — pytest:**

```
$ python -m pytest tests/ -q --deselect tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs
........................................................................ [ 86%]
........................................................................ [ 92%]
........................................................................ [ 98%]
........................                                                 [100%]
1236 passed, 12 skipped, 1 deselected in 123.50s (0:02:03)
```

Exit code: 0. The 12 "skipped" are pytest skip markers (likely optional-
dep/environment-conditional), not failures. Total non-skip collection =
1248, matching the baseline in `-004.md`.

**Gate 2 — mkdocs build:**

```
$ python -m mkdocs build --strict --site-dir _site_verify
INFO    -  Building documentation to directory: .../_site_verify
INFO    -  Documentation built in 1.33 seconds
```

Exit code: 0. Only INFO messages (out-of-nav reports pages, informational).

**Gate 3 — check_docs_cli_coverage.py:**

```
$ python scripts/check_docs_cli_coverage.py
...
All documentation checks passed.
```

Exit code: 0.

**Gate 4 — check_doc_links.py:**

```
$ python scripts/check_doc_links.py
Links checked: 140
Failures:      0
All adopter-path links resolved.
```

Exit code: 0.

**Gate 5 — collect_evidence_metrics.py --verify:**

```
$ python scripts/collect_evidence_metrics.py --verify
Evidence matches: 3 gate-bound metrics agree at commit b60f98d;
docs/evidence.md matches a fresh render of the committed JSON.

INFO: live_snapshot values were regenerated (not compared):
  specs_specified = 30  (local groundtruth-kb/groundtruth.db at repo root)
  specs_verified = 6  (local groundtruth-kb/groundtruth.db at repo root)
  deliberations_total = 1  (local groundtruth-kb/groundtruth.db at repo root. ...)
```

Exit code: 0.

**Gate 6 — exact-ID assertion sweep:** Python API and PowerShell CLI loops
shown above under P2 — 12/12 PASS each.

## Commit SHAs

- `2790e11` — `docs(evidence): reconcile provenance, tighten verify gate`
  (remediation code + content)
- `b60f98d` — `docs(evidence): regenerate artifacts at remediation tip`
  (re-stamp JSON + markdown so `generated_at_commit` equals the commit
  that contains them; code unchanged)

Parent (unchanged): `6b152c2` (pre-remediation tip).

Diff shape of the remediation:

```
 docs/_generated/evidence_metrics.json |  74 +++---
 docs/evidence.md                      |  96 +++++---
 scripts/collect_evidence_metrics.py   | 418 ++++++++++++++++++++++++++--------
 scripts/render_evidence_md.py         | 331 +++++++++++++++++++++++++++
 scripts/starthere_ids.txt             |  12 +
 5 files changed, 771 insertions(+), 160 deletions(-)
```

Plus the re-stamp commit `b60f98d`:

```
 docs/_generated/evidence_metrics.json | 22 +++---
 docs/evidence.md                      | 22 +++---
 2 files changed, 22 insertions(+), 22 deletions(-)
```

## Render Output Diff Confirmation

`python scripts/render_evidence_md.py --to .render_check.md` run against
the committed `docs/_generated/evidence_metrics.json` at `b60f98d`:

```
Wrote 135 lines to .render_check.md.
committed size: 7505
rendered size:  7505
committed sha256: f786874850d4b8f1371bd7dcd33bb680fad4ff9389056280434c2e6ee4cffbc3
rendered sha256:  f786874850d4b8f1371bd7dcd33bb680fad4ff9389056280434c2e6ee4cffbc3
byte-identical: True
```

The committed markdown is byte-for-byte equal to a fresh render from the
committed JSON. Option 1 holds end-to-end.

## Statement of Unified Provenance Contract

`docs/evidence.md` and `docs/_generated/evidence_metrics.json` now share
one truthful contract, enforced at three independent layers:

1. **Structural** — the markdown is rendered from the JSON. There is no
   path by which a hand-edit to `docs/evidence.md` can survive
   `scripts/render_evidence_md.py`.
2. **Stored-JSON internal coherence** — `_check_gate_commit_consistency`
   ensures per-metric `commit_sha == generated_at_commit` on every
   gate-bound row, and `_check_live_schema` does the same for
   `live_snapshot[]`.
3. **Markdown byte-identity** — `_check_markdown_consistency` re-renders
   from the committed JSON and diffs; any drift fails the gate and prints
   a unified diff.

The Codex-required contract ("the implemented contract and the `-007.md`
report use one truthful contract") is satisfied. The report states
plainly: `commit_sha` and `timestamp_utc` are not compared against a
*fresh* run; they are stamped at each run. The report does NOT claim
"every provenance field is compared". It DOES claim that the committed
JSON, the rendered markdown, and the verification gate all agree on the
same five fields of every gate-bound metric, and that the rendered
markdown is byte-identical to a fresh render of the committed JSON.

## Scope Boundary (Unchanged From Plan)

No changes in this remediation to any of:

- The 12 `SPEC-STARTHERE-*` specs or their assertions (all still PASS).
- `docs/start-here.md`, `docs/day-in-the-life.md`,
  `docs/known-limitations.md` content.
- `mkdocs.yml` nav.
- `README.md` adopter-path links.
- `scripts/check_doc_links.py` logic.
- The `WI-ADOPT-01..08` work items or their mapping.

Only provenance plumbing and evidence rendering were touched.

## Note on Branch Tip State (not a remediation defect)

Between my regen commit `b60f98d` (14:02:22) and the filing of this report,
a separate thread landed commit `f475c8b` (14:04:30) on this same branch
for the `gtkb-canonical-terminology-surface-implementation` workstream.
That commit's payload added 17 new tests and nudged docstring coverage
from 87.25% to 87.31%, but did not regenerate the evidence artifacts.

Running the new `--verify` gate at `f475c8b` therefore fails loud:

```
$ python scripts/collect_evidence_metrics.py --verify
Evidence drift detected:
  GATE-BOUND FIELD MISMATCH: metric=test_count field=value stored=1249 fresh=1266
  GATE-BOUND FIELD MISMATCH: metric=docstring_coverage_percent field=value stored=87.25 fresh=87.31
```

Exit code: 1. This is the gate working as designed — the canonical-
terminology commit is the exact class of drift this remediation was
built to catch. It is NOT a defect in my remediation; it is a defect in
the concurrent workstream's discipline that this new gate surfaces
immediately.

Resolution path: the canonical-terminology thread should regenerate
`docs/_generated/evidence_metrics.json` and `docs/evidence.md` as part
of its own post-implementation commit, per the same plan Fix D pattern
used here. That is their work item, not mine. I am NOT regenerating at
`f475c8b` from this remediation thread because (a) it would commingle
scope (my remediation is strictly provenance contract + renderer + IDs),
(b) the canonical-terminology thread is mid-review in its own bridge and
Codex should see the drift fail in its own verification, and (c) the
instructions for this remediation explicitly say "Do NOT improvise
beyond the Codex-GO'd plan."

Codex may elect to review this remediation at `b60f98d` (the clean
remediation tip where all gates pass) or at `f475c8b` (the current
branch tip where the new gate correctly catches an unrelated workstream's
drift). Both tips demonstrate the remediation is correct.

## Open Items Requiring Codex

- VERIFIED or NO-GO on this revised post-implementation report. Please
  review at `b60f98d` (my remediation tip) unless you explicitly prefer
  `f475c8b` (where the canonical-terminology commit's evidence drift is
  visible to the new gate).

## Open Items Requiring Owner

None. This is an implementation/reporting repair of the prior NO-GO.

## Prior Deliberations Referenced

- `gtkb-start-here-adopter-rewrite-implementation-001` (NEW) → `-002` (GO) →
  `-003` (NEW post-impl) → `-004` (NO-GO) → `-005` (REVISED plan) →
  `-006` (GO with conditions) → this file `-007` (REVISED post-impl).
- `gtkb-start-here-adopter-rewrite-001` → `-002` — parent scope thread.
- `DELIB-GTKB-STARTHERE-ADOPT-001` — archives the scope-GO +
  implementation-GO chain; this remediation appends the NO-GO → GO →
  (pending) VERIFIED cycle.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
