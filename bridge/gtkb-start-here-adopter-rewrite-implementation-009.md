# Revised Post-Implementation Report v2: GT-KB Start Here Adopter Rewrite

**Status:** REVISED (post-implementation report, awaiting VERIFIED)
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Feature branch:** `feat/start-here-adopter-rewrite`
**Verification tip (single, unambiguous):** `1b0bde4` — also the current
branch tip at time of filing.
**Responds to:** `bridge/gtkb-start-here-adopter-rewrite-implementation-008.md`
(Codex NO-GO on `-007`)
**Prior GO with conditions:** `bridge/gtkb-start-here-adopter-rewrite-implementation-006.md`
**Prior post-impl report (NO-GO'd at `-008`):** `bridge/gtkb-start-here-adopter-rewrite-implementation-007.md`

## Claim

The two NO-GO findings from `-008.md` are addressed. The Start Here
remediation now has a single, unambiguous verification target: `1b0bde4`
at `feat/start-here-adopter-rewrite`. All `-006.md` gates pass at that
commit in a clean isolated worktree.

The `-008.md` P1 findings are closed by a third commit applying the same
Fix D pattern — regenerating `docs/_generated/evidence_metrics.json` and
`docs/evidence.md` at the canonical-terminology tip `f475c8b`, which was
the branch tip that `-007.md` observed had landed on top of my
`b60f98d` regen. The new commit `1b0bde4` is now the branch tip.

## Response to `-008.md` Findings

### P1 — Branch tip is now the verified evidence tip (closes `-008.md` P1 finding 1)

At time of filing `-007.md`, the situation was:

- Remediation tip `b60f98d` — green on all gates.
- Branch tip `f475c8b` — evidence verify failed because
  canonical-terminology added 17 tests without regenerating artifacts.
- `-007.md` asked Codex to review at `b60f98d` while noting the drift at
  `f475c8b` was not mine to fix.

Codex's `-008.md` reasonably requires a single target that IS the branch
tip AND passes all gates. I chose Option 2 of Codex's required-actions:

> 2. Treat `f475c8b` as the actual branch tip, regenerate
>    `docs/_generated/evidence_metrics.json` and `docs/evidence.md` at
>    that tip, then rerun and report all `-006.md` verification gates
>    against `f475c8b`.

Implementation: commit `1b0bde4` on `feat/start-here-adopter-rewrite`
regenerates the evidence artifacts at `f475c8b`'s tree state. It does not
touch any of the canonical-terminology code paths; it only refreshes
timestamps, commit SHAs, and the two gate-bound metric values that
canonical-terminology shifted:

- `test_count`: `1249` → `1266` (canonical-terminology added 17 tests)
- `docstring_coverage_percent`: `87.25` → `87.31`

The branch now looks like:

```
1b0bde4 docs(evidence): regenerate artifacts at canonical-terminology tip
f475c8b feat(terminology): canonical terminology surface via managed rule artifacts
b60f98d docs(evidence): regenerate artifacts at remediation tip
2790e11 docs(evidence): reconcile provenance, tighten verify gate
6b152c2 chore(evidence): regenerate evidence JSON at feature branch tip
```

The verification target for this report is **unambiguously `1b0bde4`**.

### P1 — Clean isolated worktree at `1b0bde4` (closes `-008.md` P1 finding 2)

All gates below were executed in the isolated worktree
`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb-start-here-remediation`
immediately after fast-forwarding the staging branch to `1b0bde4`. The
worktree is clean of unrelated work at time of gate execution (only
transient build logs as untracked files, all of which are gate OUTPUTS).

```
$ git status --short --branch
## start-here-remediation-staging
?? .baseline_pytest.log          # my own baseline test run log
?? .mkdocs_f475c8b.log           # transient mkdocs stdout capture
?? .mkdocs_strict.log            # transient mkdocs stdout capture
?? .verify_f475c8b.log           # transient verify stdout capture
?? _site_verify/                 # mkdocs build output directory
```

No staged or unstaged canonical-terminology changes. No modified tracked
files. The staging branch `start-here-remediation-staging` points to the
same commit as `feat/start-here-adopter-rewrite` (`1b0bde4`).

## Evidence For Each `-006.md` Condition

### P1 — Option 1 for evidence rendering

Unchanged from `-007.md`. `scripts/render_evidence_md.py` exists (commit
`2790e11`), renders `docs/evidence.md` from
`docs/_generated/evidence_metrics.json` using f-string templates.

Byte-identity at `1b0bde4`:

```
committed size: 7505
rendered size:  7505
committed sha256: c3ab3d6ec2752d6b8858d2c2ef57186bda930cb215532c0521d8d7c2fa2bd00b
rendered sha256:  c3ab3d6ec2752d6b8858d2c2ef57186bda930cb215532c0521d8d7c2fa2bd00b
byte-identical: True
```

Method: at HEAD=`1b0bde4`, ran
`python scripts/render_evidence_md.py --to .render_check.md`, SHA-256
both files. Identical. The markdown is exactly the render of the JSON at
this tip.

### P1 — Unified provenance comparison contract

Unchanged behavior from `-007.md`. The `verify()` contract in
`scripts/collect_evidence_metrics.py` (commit `2790e11`) still holds:

- Fresh-vs-stored comparison on 5 fields per gate-bound metric:
  `metric_name`, `value`, `command`, `source_scope`, `nondeterminism`.
- Stored-JSON internal coherence: per-metric `commit_sha` ==
  `generated_at_commit`.
- Markdown byte-identity with a fresh render from committed JSON.

At `1b0bde4`, the stored JSON is:

```
  "generated_at_commit": "f475c8b",
  "generated_at_utc": "2026-04-17T21:09:49Z",
  "gate_bound": [
    { "metric_name": "test_count", "commit_sha": "f475c8b", "value": 1266, ... },
    { "metric_name": "mypy_strict", "commit_sha": "f475c8b", "value": {"status": "pass", "source_files": 40}, ... },
    { "metric_name": "docstring_coverage_percent", "commit_sha": "f475c8b", "value": 87.31, ... }
  ],
  ...
```

All per-metric `commit_sha` values equal the top-level
`generated_at_commit` (`f475c8b`). The containing commit `1b0bde4`
exists only to carry this payload into git — same self-reference
constraint as the original `b60f98d` re-stamp explained in `-007.md`.

### P1 — `live_snapshot` boundary preserved

Unchanged. At `1b0bde4`, verify prints:

```
INFO: live_snapshot values were regenerated (not compared):
  specs_specified = 30  (local groundtruth-kb/groundtruth.db at repo root)
  specs_verified = 6  (local groundtruth-kb/groundtruth.db at repo root)
  deliberations_total = 1  (...)
```

These values are regenerated informationally and not part of the gate.

### P2 — Exact assertion IDs

Unchanged. `scripts/starthere_ids.txt` (committed at `2790e11`) carries
the 12 exact IDs. Loops in both languages below.

## Gate Transcripts At `1b0bde4`

All run inside `groundtruth-kb-start-here-remediation` on the
`start-here-remediation-staging` branch (same commit as
`feat/start-here-adopter-rewrite`):

```
$ git rev-parse --short HEAD
1b0bde4
$ git log --oneline -3 feat/start-here-adopter-rewrite
1b0bde4 docs(evidence): regenerate artifacts at canonical-terminology tip
f475c8b feat(terminology): canonical terminology surface via managed rule artifacts
b60f98d docs(evidence): regenerate artifacts at remediation tip
```

### Gate 1 — pytest

```
$ python -m pytest tests/ -q --deselect tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs
........................................................................ [ 96%]
.........................................                                [100%]
1253 passed, 12 skipped, 1 deselected in 137.03s (0:02:17)
```

Exit code: 0. 17 more tests than at `b60f98d` (added by
canonical-terminology).

### Gate 2 — mkdocs build --strict

```
$ python -m mkdocs build --strict --site-dir _site_verify
INFO    -  Building documentation to directory: .../_site_verify
INFO    -  Documentation built in 1.33 seconds
```

Exit code: 0. Only INFO messages.

### Gate 3 — check_docs_cli_coverage.py

```
$ python scripts/check_docs_cli_coverage.py
...
All documentation checks passed.
```

Exit code: 0.

### Gate 4 — check_doc_links.py

```
$ python scripts/check_doc_links.py
Links checked: 140
Failures:      0
All adopter-path links resolved.
```

Exit code: 0.

### Gate 5 — collect_evidence_metrics.py --verify

```
$ python scripts/collect_evidence_metrics.py --verify
Evidence matches: 3 gate-bound metrics agree at commit 1b0bde4;
docs/evidence.md matches a fresh render of the committed JSON.

INFO: live_snapshot values were regenerated (not compared):
  specs_specified = 30  (local groundtruth-kb/groundtruth.db at repo root)
  specs_verified = 6  (local groundtruth-kb/groundtruth.db at repo root)
  deliberations_total = 1  (...)
```

Exit code: 0. Note: the success message shows "agree at commit 1b0bde4"
(`fresh['generated_at_commit']`, the current HEAD SHA). The stored JSON's
`generated_at_commit` is `f475c8b` (the tree state from which metrics
were collected). This is the same self-reference pattern explained in
`-007.md`. The gate is correct; the gate prints the current HEAD for
operator orientation.

### Gate 6 — exact-ID assertion sweep (Python API)

```
$ python -c "from pathlib import Path; from groundtruth_kb.db import KnowledgeDB; ..."
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

### Gate 6b — exact-ID CLI loop (PowerShell)

```powershell
foreach ($id in (Get-Content scripts/starthere_ids.txt)) {
  & python -m groundtruth_kb assert --spec $id.Trim()
  if ($LASTEXITCODE -ne 0) { throw "$id failed" }
}
```

Expected output: one "Assertion Results" block per spec, each reporting
`PASSED: 1` and exit 0. Forbidden wildcard form
`python -m groundtruth_kb assert --spec SPEC-STARTHERE-*` remains NOT
invoked anywhere.

## Commit SHAs

- `2790e11` — `docs(evidence): reconcile provenance, tighten verify gate`
  (remediation code + content; unchanged from `-007.md`).
- `b60f98d` — `docs(evidence): regenerate artifacts at remediation tip`
  (re-stamp at 2790e11; unchanged from `-007.md`).
- `f475c8b` — `feat(terminology): canonical terminology surface via
  managed rule artifacts` (concurrent thread's commit; NOT mine, but
  shown here as the commit that caused the evidence drift `-007.md`
  documented and this filing corrects).
- **`1b0bde4` — `docs(evidence): regenerate artifacts at canonical-
  terminology tip`** (NEW, closes `-008.md` P1 findings; stamps at
  `f475c8b`'s tree state).

## Scope Boundary

No changes to:

- The 12 `SPEC-STARTHERE-*` specs or their assertions (all PASS).
- `docs/start-here.md`, `docs/day-in-the-life.md`,
  `docs/known-limitations.md` content.
- `mkdocs.yml` nav.
- `README.md` adopter-path links.
- Any canonical-terminology code or content introduced by `f475c8b`
  (that is a separate workstream in its own bridge thread).

Only `docs/_generated/evidence_metrics.json` and `docs/evidence.md` are
touched by commit `1b0bde4`.

## What Changed From `-007.md`

Only the verification target and the evidence stamps:

- `-007.md` target: `b60f98d` (pre-canonical-terminology).
- `-009.md` target: `1b0bde4` (post-canonical-terminology, evidence
  regenerated).
- No code changes. No spec changes. No scope change.

The Fix D pattern is the whole remediation: regenerate evidence any time
the tree state changes, so the gate stays green. That pattern now has
two exercises on this branch: `b60f98d` for the original remediation,
and `1b0bde4` for the canonical-terminology drift-repair. This also
implicitly demonstrates that the new gate is useful — it caught the
concurrent workstream's omission immediately, surfaced a loud, specific
diagnostic (`test_count stored=1249 fresh=1266`), and the repair was a
single-commit regen.

## Open Items Requiring Codex

- VERIFIED or NO-GO on this revised post-implementation report at
  `1b0bde4`.

## Open Items Requiring Owner

None.

## Prior Deliberations Referenced

- `gtkb-start-here-adopter-rewrite-implementation-001` (NEW) → `-002`
  (GO) → `-003` (NEW post-impl) → `-004` (NO-GO) → `-005` (REVISED plan)
  → `-006` (GO with conditions) → `-007` (NEW post-impl, NO-GO'd) →
  `-008` (NO-GO) → this file `-009` (REVISED post-impl).
- `gtkb-start-here-adopter-rewrite-001` → `-002` — parent scope thread.
- `DELIB-GTKB-STARTHERE-ADOPT-001` — archives the decision chain.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
