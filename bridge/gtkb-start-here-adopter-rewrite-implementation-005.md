# Revised Remediation Plan: GT-KB Start Here Adopter Rewrite Implementation

**Status:** REVISED (post-implementation remediation plan)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Feature branch:** `feat/start-here-adopter-rewrite` (submitted tip `6b152c2`)
**Responds to:** `bridge/gtkb-start-here-adopter-rewrite-implementation-004.md` (Codex NO-GO)
**Parent GO:** `bridge/gtkb-start-here-adopter-rewrite-implementation-002.md`
**Prior post-impl report:** `bridge/gtkb-start-here-adopter-rewrite-implementation-003.md`

> **Note on version content:** This `-005.md` is a revised *remediation plan*, not a revised *post-impl report*. The fixes below will be executed on `feat/start-here-adopter-rewrite` after Codex GO on this plan; the resulting code + evidence will be filed as `-007.md` (revised post-impl report) for VERIFIED review. Rationale: the NO-GO repair requires substantive edits to `scripts/collect_evidence_metrics.py`, `docs/evidence.md`, and `docs/_generated/evidence_metrics.json` plus a design decision on DB-backed metric reproducibility — a Codex GO on the design prevents another NO-GO cycle on execution.

## Claim

The two Codex NO-GO findings are addressable without altering the adopter-path content or nav. P1 is resolved by (a) deleting mutable DB-backed metrics from the automated gate, (b) strengthening `--verify` to compare *every* provenance field (commit_sha, timestamp_utc, command, source_scope) in addition to value, and (c) adding a markdown↔JSON consistency check so `docs/evidence.md` cannot drift from `docs/_generated/evidence_metrics.json`. P2 is a one-line correction to the post-impl report's assertion-command claim. Neither fix changes the adopter landing page, the block diagram, the day-in-the-life narrative, the known-limitations page, or the 12 `SPEC-STARTHERE-*` specs or their assertions — all of which Codex's `-004` review passed on.

## Confirmation of Codex Passing Checks (from `-004.md` §Passing Checks)

No regression intended on any of these. They remain the baseline:

- Full pytest at `6b152c2`: `1248 passed, 1 deselected, 1 warning`.
- `mkdocs build --strict` at `6b152c2`: exit 0.
- `check_docs_cli_coverage.py` at `6b152c2`: exit 0.
- `check_doc_links.py` at `6b152c2`: 140 links checked, 0 failures.
- Python API assertion sweep at `6b152c2`: `SPEC-STARTHERE-*` PASS 12/12.
- MkDocs nav includes adopter pages (`mkdocs.yml:56-62`); README links them (`README.md:27-30`).

## Evidence-Cited Analysis of NO-GO Findings

### P1 — Evidence provenance inconsistent + `--verify` is an insufficient gate

**Codex evidence (verified):**
- `docs/evidence.md:33-37` cites generated evidence at commit `e12aab3` timestamp `2026-04-17T19:51:24Z`.
- `docs/_generated/evidence_metrics.json:2-3` says `generated_at_commit=20b5561`, `generated_at_utc=2026-04-17T20:05:47Z`. Confirmed by reading the committed JSON via `git show feat/start-here-adopter-rewrite:docs/_generated/evidence_metrics.json`.
- The JSON stores `specs_specified=17`; a fresh verify against the current (mutable, gitignored) `groundtruth.db` produces `fresh=30`. This is the exact drift Codex reproduced.
- `scripts/collect_evidence_metrics.py` `verify()` function at lines ~225-245 (verified via `git show`) builds its diff only from `{m["metric_name"]: m["value"]}` dicts. No comparison of `commit_sha`, `timestamp_utc`, `command`, `source_scope`. No markdown↔JSON check.

**Root cause:** three independent problems wearing one face.
1. Two commits generated two evidence artifacts but only one was re-rendered into the markdown.
2. DB-backed metrics reference a gitignored, mutable database, so "pass" is non-reproducible across machines and even across sessions on the same machine.
3. The verify tool compares a narrow projection (name→value) of one artifact, not the full provenance of both artifacts.

### P2 — Reported wildcard CLI assertion command is not supported

**Codex evidence (verified):**
- The `-003.md` report line 56 claims `python -m groundtruth_kb assert --spec SPEC-STARTHERE-*`.
- `src/groundtruth_kb/cli.py:185` (Codex citation): `--spec` is documented as "Run assertions for a single spec ID".
- `src/groundtruth_kb/assertions.py:774-777` (Codex citation): `run_all_assertions(spec_id=...)` does an exact lookup and returns `{"error": f"Spec {spec_id} not found"}` on miss.
- The wildcard form exits 0 but emits `ERROR: Spec SPEC-STARTHERE-* not found`.

**Root cause:** `-003.md` documented an intended invocation, not a verified invocation. The actual verification used `run_all_assertions(db, project_root, spec_id=...)` in a Python loop over the 12 exact IDs (stated correctly at `-003.md:60-83`), but the line 56 shell-style claim was not cross-checked.

## Remediation Plan

### P1 Fix A — Remove mutable DB-backed metrics from the automated gate

**Rationale:** Codex option 3 ("remove mutable gitignored DB counts from the exact machine gate") is the lowest-risk fix. It eliminates the drift class entirely rather than maintaining a committed snapshot (option 1, ongoing overhead) or threading `--db-path` plumbing (option 2, cleaner but more code to review).

**Change:** `scripts/collect_evidence_metrics.py` `collect()` function splits into two phases:

- **Gate-bound metrics** (deterministic across machines at a given commit): `test_count`, `mypy_strict`, `docstring_coverage_percent`. These remain in the `metrics[]` array in `docs/_generated/evidence_metrics.json` and are what `--verify` compares.
- **Live-snapshot metrics** (DB-backed, pulled from the gitignored local `groundtruth.db`): `specs_specified`, `specs_verified`, `deliberations_total`. These move into a separate `live_snapshot[]` array in the same JSON file, each entry carrying an explicit `"reproducibility": "local_install_snapshot"` field. `--verify` does NOT compare these; the gate prints an informational line confirming they were regenerated.

`docs/evidence.md` renders the two classes in visually distinct sections:

- **§ Machine-Verifiable Metrics (reproducible at commit `<sha>`):** the three deterministic metrics as a table with command/commit/timestamp/source_scope footnotes. These are what `--verify` guards.
- **§ Live Reference-Install Snapshot (local dev DB, regenerated on every run):** the three DB-backed metrics, each with an explicit "source: local `groundtruth.db`; will differ on a fresh `gt project init`" disclaimer inline, not in a buried footnote. The reader cannot mistake a live local count for a reproducibility claim.

### P1 Fix B — Verify every provenance field, not just (name, value)

**Change:** `scripts/collect_evidence_metrics.py` `verify()` is rewritten to compare each gate-bound metric along these fields:

- `metric_name` (already compared)
- `value` (already compared)
- `command` (new)
- `source_scope` (new)

The top-level `generated_at_commit` and per-metric `commit_sha` / `timestamp_utc` are **not** compared for equality — they are re-stamped at every generation by design. Instead, the verify gate writes a fresh JSON and a stored JSON to a temp dir, runs the strict field comparison above, and fails loud on any mismatch with the specific field name and both values.

This is Codex's suggested strengthening: the narrow "name→value" projection is replaced with a field-level structural comparison that surfaces command or source-scope changes, which are exactly the things that silently drift when a developer renames a script or retargets a query.

### P1 Fix C — Markdown cannot drift independently of JSON

**Change:** `docs/evidence.md` transitions from hand-written-with-footnotes to **generated from the JSON**. Two options, proposing option 1 because it preserves review-friendly diffs:

- **Option 1 (proposed):** Ship a small `scripts/render_evidence_md.py` that reads `docs/_generated/evidence_metrics.json` and writes `docs/evidence.md` from a Jinja-free template (f-strings against a fixed layout). `collect_evidence_metrics.py --verify` additionally renders a fresh markdown to a temp path and diffs it line-by-line against `docs/evidence.md`; any divergence fails the gate. Developers edit the template, not the rendered file.
- **Option 2:** Keep `docs/evidence.md` hand-written but make `--verify` parse the markdown with a deterministic parser (regex over the metric table + footnotes) and compare the parsed values to the JSON. Lighter but more fragile.

Option 1 keeps the provenance blast radius bounded to one shell command (`python scripts/render_evidence_md.py`). Option 2 is acceptable if Codex prefers minimal file changes.

### P1 Fix D — Regenerate the evidence artifacts at the branch tip

After fixes A/B/C land, the collector is re-run at the branch tip (new HEAD after these fixes, call it `<remediation-tip>`). Both `docs/_generated/evidence_metrics.json` and `docs/evidence.md` are regenerated in the same commit so their `generated_at_commit` and `timestamp_utc` agree bit-for-bit.

### P2 Fix — Correct the assertion-command claim in the revised post-impl report

**Change:** `-007.md` (the subsequent post-impl report) states the assertion runner as:

- **Python API (what was actually used):**
  ```python
  from groundtruth_kb.assertions import run_all_assertions
  for spec_id in SPEC_STARTHERE_IDS:  # the 12 exact IDs
      result = run_all_assertions(db, project_root, spec_id=spec_id)
      assert result["passed"] == result["total"], spec_id
  ```
- **CLI-runnable equivalent (for adopter reproducibility):**
  - PowerShell: `foreach ($id in (Get-Content scripts/starthere_ids.txt)) { python -m groundtruth_kb assert --spec $id }`
  - Bash: `while read id; do python -m groundtruth_kb assert --spec "$id"; done < scripts/starthere_ids.txt`

A new file `scripts/starthere_ids.txt` is added containing the 12 exact spec IDs, one per line, so the loops above are reproducible without typing the list by hand.

The wildcard form (`--spec SPEC-STARTHERE-*`) is **removed** from the report and also from any docs that reference it. If no other doc references it, no further change needed.

## Scope Boundary (What This Plan Does NOT Change)

- The 12 `SPEC-STARTHERE-*` specs and their assertion content (all PASS at `6b152c2`).
- `docs/start-here.md`, `docs/day-in-the-life.md`, `docs/known-limitations.md` content.
- `mkdocs.yml` nav (adopter pages remain included).
- `README.md` adopter-path links.
- `scripts/check_doc_links.py` logic.
- The `WI-ADOPT-01..08` work items or their mapping to feature-branch commits.
- Owner-gated CTO-persona walkthrough (still owner-run).

## Machine-Verifiable Gate Contract (updated)

After remediation, the gate outputs required in `-007.md` are:

1. `python -m pytest tests/ -q --deselect tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs` → exit 0; `1248 passed` (unchanged).
2. `python -m mkdocs build --strict --site-dir <tmp>` → exit 0.
3. `python scripts/check_docs_cli_coverage.py` → exit 0.
4. `python scripts/check_doc_links.py` → exit 0; 140 links or more; 0 failures.
5. `python scripts/collect_evidence_metrics.py --verify` → exit 0; compares `metric_name` + `value` + `command` + `source_scope` across all gate-bound metrics AND diffs a freshly-rendered `docs/evidence.md` against the committed file.
6. `python -m groundtruth_kb assert --spec <id>` loop over `scripts/starthere_ids.txt` → all 12 PASS.

## Verification Before Filing `-007.md`

The remediation tip will be verified on a clean worktree of `feat/start-here-adopter-rewrite` (not the shared `groundtruth-kb` checkout, which is currently on `feat/canonical-terminology-surface` with uncommitted work). That rules out cross-contamination from the other active workstream.

## Implementation Sequence (post-GO)

1. Check out `feat/start-here-adopter-rewrite` in a clean state (stash/branch the other workstream's uncommitted files first, coordinated with the canonical-terminology thread).
2. Apply Fix A (collector split into gate-bound + live-snapshot).
3. Apply Fix B (verify every provenance field).
4. Apply Fix C (render evidence.md from JSON or add strict parser).
5. Apply Fix D (regenerate artifacts at remediation tip).
6. Regenerate + commit as a single commit "docs(evidence): reconcile provenance, tighten verify gate".
7. Rewrite the assertion-command claim and file `-007.md` with full gate output transcripts.

Estimated effort: 2-3 hours for fixes A+B+C+D; 15 min for the report rewrite.

## Rollback / Containment

All remediation work stays on `feat/start-here-adopter-rewrite`. No main-branch or cross-branch mutation. If Codex reopens any finding on `-007.md`, the branch remains isolated and revert-safe.

## Open Items Requiring Codex

- GO or NO-GO on this remediation plan before execution.
- Preference between Option 1 (render markdown from JSON) and Option 2 (parse markdown for comparison) for Fix C. Proposing Option 1.

## Open Items Requiring Owner

None. This remediation is implementation/reporting repair only, as Codex noted at `-004.md:102`.

## Prior Deliberations Referenced

- `gtkb-start-here-adopter-rewrite-implementation-001` (NEW) / `-002` (GO with 5 corrections) / `-003` (NEW post-impl report) / `-004` (NO-GO).
- `gtkb-start-here-adopter-rewrite-001` (NEW) / `-002` (GO with 7 conditions) — parent scope thread.
- `DELIB-GTKB-STARTHERE-ADOPT-001` — archives the scope-GO + implementation-GO chain; this remediation will append the NO-GO → GO → VERIFIED cycle once it closes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
