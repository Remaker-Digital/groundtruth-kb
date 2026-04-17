# Evidence

This page documents **live metrics from the reference implementation**.
Every row carries a generating command, a commit SHA, and a generation date
as a footnote. Numbers without provenance are forbidden on this page.

!!! note "This page is generated"
    `docs/evidence.md` is rendered from `docs/_generated/evidence_metrics.json`
    by `scripts/render_evidence_md.py`. Do not hand-edit this file.
    Edit the JSON via `python scripts/collect_evidence_metrics.py`, then
    regenerate this page via `python scripts/render_evidence_md.py`.

!!! note "Reading this page"
    A single snapshot is not a trend. The metrics below answer the
    question: "at commit X, on a fresh install, what is true?" They do
    not answer "how fast is this moving?" That is what session wrap-up
    reports are for.

## Machine-Verifiable Metrics (reproducible at commit `2790e11`)

These metrics are deterministic at a fixed commit. `scripts/collect_evidence_metrics.py --verify`
compares each row's `metric_name`, `value`, `command`, `source_scope`, and
`nondeterminism` classification against the committed JSON, and fails on any
mismatch. `commit_sha` and `timestamp_utc` are re-stamped on every run and are
NOT compared against the fresh run (they would diverge by design), but the
committed JSON's `commit_sha` must equal the top-level `generated_at_commit`
and that value is surfaced in the section heading above.

| Metric | Value | Notes |
|--------|-------|-------|
| Tests collected | 1249[^gate1] | deterministic; exact equality enforced on re-run |
| `mypy --strict` | pass across 40 source files[^gate2] | src/groundtruth_kb/ |
| Docstring coverage | 87.25%[^gate3] | public API only, per `scripts/audit_docstrings.py` |

[^gate1]: `python -m pytest --collect-only -q` — commit `2790e11` — generated 2026-04-17T21:02:03Z. Scope: tests/ directory, all collected test ids.
[^gate2]: `python -m mypy --strict src/groundtruth_kb/` — commit `2790e11` — generated 2026-04-17T21:02:03Z. Scope: src/groundtruth_kb/ (all modules).
[^gate3]: `python scripts/audit_docstrings.py` — commit `2790e11` — generated 2026-04-17T21:02:03Z. Scope: src/groundtruth_kb/ public API (audit_docstrings.py scope).

## Live Reference-Install Snapshot (local dev DB, regenerated on every run)

These metrics are pulled from the gitignored local `groundtruth.db`. They
are informative, not gate-bound: a fresh `gt project init` creates an empty
database, so these values will differ on any other machine. They are
regenerated on every `scripts/collect_evidence_metrics.py` run, but
`--verify` does NOT compare them.

| Metric | Value | Notes |
|--------|-------|-------|
| Specs (specified) | 30[^live1] | count at last `scripts/collect_evidence_metrics.py` run |
| Specs (verified) | 6[^live2] | count at last `scripts/collect_evidence_metrics.py` run |
| Deliberations (local archive) | 1[^live3] | count at last `scripts/collect_evidence_metrics.py` run. Reference install only, not Agent Red. |

[^live1]: `sqlite3 groundtruth.db 'SELECT status, COUNT(*) FROM (...) GROUP BY status'` — commit `2790e11` — generated 2026-04-17T21:02:03Z. Scope: local groundtruth-kb/groundtruth.db at repo root. Reproducibility: `local_install_snapshot` — **this value will differ on a fresh `gt project init` and is NOT compared by `--verify`**.
[^live2]: `sqlite3 groundtruth.db 'SELECT status, COUNT(*) FROM (...) GROUP BY status'` — commit `2790e11` — generated 2026-04-17T21:02:03Z. Scope: local groundtruth-kb/groundtruth.db at repo root. Reproducibility: `local_install_snapshot` — **this value will differ on a fresh `gt project init` and is NOT compared by `--verify`**.
[^live3]: `sqlite3 groundtruth.db 'SELECT COUNT(DISTINCT id) FROM deliberations'` — commit `2790e11` — generated 2026-04-17T21:02:03Z. Scope: local groundtruth-kb/groundtruth.db at repo root. This is the reference install's local archive, NOT the downstream Agent Red deliberation history which is measured separately. Reproducibility: `local_install_snapshot` — **this value will differ on a fresh `gt project init` and is NOT compared by `--verify`**.

## Deterministic vs. Non-Deterministic Metrics

Every machine-verifiable metric above is classified as **deterministic**:
at a fixed commit, running the generating command twice returns the same
value. No tolerance is applied. Evidence drift is surfaced by
`scripts/collect_evidence_metrics.py --verify` as an exact mismatch.

Live-snapshot metrics are **reproducibility: local_install_snapshot** — a
deterministic query against a non-deterministic database. They carry full
provenance but are explicitly excluded from the fail-closed gate.

If a future metric is introduced that is genuinely non-deterministic (for
example, timing-based measurements), it must declare the nondeterminism
source and the allowed tolerance in both the collector code and this page.
A vague "+/-1 for test-collection noise" is not an acceptable contract;
deterministic metrics get exact equality.

## Curated Context

Some evidence cannot be auto-collected from a single commit. These
sections are curated from session wrap-up reports and bridge threads:

### Bridge Round-Trip Cycle Times (reference project)

From recent VERIFIED bridge threads on Agent Red:

- `gtkb-start-here-adopter-rewrite-implementation` scope review cycle:
  proposal -> Codex GO in under 30 minutes on 2026-04-17.
- `gtkb-non-disruptive-upgrade-investigation-006` VERIFIED:
  scope draft -> Codex GO -> 1023-line investigation report -> VERIFIED in
  a single session (S299-continuation).
- `gtkb-phase-a-metrics-collector-004` VERIFIED: headless Claude thread
  implementation (pid-spawned) -> Codex verification in ~13 minutes total
  round-trip.

These are **representative samples from the Agent Red reference project**,
not claims about what every adopter project will achieve. An adopter's
cycle time depends on Codex availability, proposal complexity, and
whether the proposal needs one revision or several.

### Phase A Shipping Summary (reference project)

As of 2026-04-17, the Agent Red reference project has completed the
GT-KB Operational Skills Tier A Phase A workstream. Six implementation
bridges VERIFIED, 14 commits from v0.5.0 to v0.6.0, wheel shipped to
PyPI.

This is curated, not auto-collected. It ages the moment the next release
ships; the bridge index and KB are the authoritative sources.

## How to Regenerate This Page

```powershell
cd groundtruth-kb
python scripts/collect_evidence_metrics.py
python scripts/render_evidence_md.py
```

The collector rewrites `docs/_generated/evidence_metrics.json` (both
gate-bound and live-snapshot sections). The renderer then rewrites this
page from the JSON.

To verify the stored JSON matches the current state of the repo AND that
the rendered markdown matches the committed markdown:

```powershell
python scripts/collect_evidence_metrics.py --verify
```

Exit code 0 means the stored gate-bound metrics match the fresh collection
*and* `docs/evidence.md` is byte-identical to a fresh render from the
committed JSON. Exit code 1 means drift was detected; the offending rows
or markdown lines are printed.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

*Generated from `docs/_generated/evidence_metrics.json` at commit `2790e11` on 2026-04-17T21:02:03Z.*
