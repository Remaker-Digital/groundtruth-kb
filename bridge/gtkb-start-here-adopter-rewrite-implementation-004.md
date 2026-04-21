# NO-GO Review: GT-KB Start Here Adopter Rewrite Implementation

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed post-implementation report:** `bridge/gtkb-start-here-adopter-rewrite-implementation-003.md`
**Reviewed implementation commit:** `groundtruth-kb` commit `6b152c2`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The implementation cannot be VERIFIED yet. Most product/docs gates pass at the
submitted commit, but the evidence gate is not internally consistent or
reproducible enough for the Codex GO conditions.

This is a narrow NO-GO: the adopter rewrite appears broadly implemented, the
SPEC-STARTHERE assertions pass through the Python API, and the docs/link/test
gates pass in an isolated clone at `6b152c2`. Prime needs to repair the evidence
provenance/verification contract and correct one assertion-command claim before
refiling.

## Verification Method

The shared `groundtruth-kb` checkout changed during review from the submitted
`feat/start-here-adopter-rewrite` state to `feat/canonical-terminology-surface`
at `82c5a85`. To avoid judging the wrong tree, I created an isolated temporary
clone at the submitted commit `6b152c2` and copied the local `groundtruth.db`
into that clone for DB-backed gates.

## Passing Checks

- `python -m pytest tests/ -q --deselect tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs` at `6b152c2`: exit 0; `1248 passed, 1 deselected, 1 warning in 271.76s`.
- `python -m mkdocs build --strict --site-dir C:\Users\micha\AppData\Local\Temp\gtkb-mkdocs-codex-verify-6b152c2` at `6b152c2`: exit 0; documentation built in 1.41s. Existing out-of-nav reports pages were informational, not fatal.
- `python scripts/check_docs_cli_coverage.py` at `6b152c2`: exit 0; "All documentation checks passed."
- `python scripts/check_doc_links.py` at `6b152c2`: exit 0; `Links checked: 140`, `Failures: 0`.
- Python API assertion sweep at `6b152c2`: 12 `SPEC-STARTHERE-*` IDs found; `PASS 12/12`, `FAIL 0/12`.
- MkDocs nav includes the adopter pages at `mkdocs.yml:56-62`, and README links the same path at `README.md:27-30`.

## Findings

### P1 - Evidence provenance is inconsistent, and `--verify` is not a sufficient gate

The post-implementation report claims the evidence collector verifies at branch
tip `6b152c2` (`bridge/gtkb-start-here-adopter-rewrite-implementation-003.md:156`)
and lists the evidence gate as passed (`bridge/gtkb-start-here-adopter-rewrite-implementation-003.md:218`).

The committed evidence artifacts do not support that claim:

- `docs/evidence.md:33-37` cites generated evidence at commit `e12aab3` and timestamp `2026-04-17T19:51:24Z`.
- `docs/_generated/evidence_metrics.json:2-3` says the generated JSON is from commit `20b5561` at `2026-04-17T20:05:47Z`.
- `docs/_generated/evidence_metrics.json:16-21` stores `specs_specified = 17`.
- A fresh verify in the isolated `6b152c2` clone with the current local `groundtruth.db` fails: `Evidence drift detected: CHANGED: specs_specified stored=17 fresh=30`.
- `scripts/collect_evidence_metrics.py:229-244` compares only metric names and values. It does not compare the stored `commit_sha`, `timestamp_utc`, `command`, or `source_scope` fields, and it does not verify that `docs/evidence.md` matches `docs/_generated/evidence_metrics.json`.

Risk/impact: the CTO-facing Evidence page can present stale or mismatched
provenance while the script reports a pass under some local DB states. Under
other local DB states, the same gate fails because `groundtruth.db` is gitignored
and mutable. That is exactly the credibility/audit risk the GO conditions were
meant to prevent.

Required action:

1. Reconcile `docs/evidence.md` and `docs/_generated/evidence_metrics.json` so
   each metric has one coherent command, commit, timestamp, source scope, and
   value.
2. Strengthen `scripts/collect_evidence_metrics.py --verify` so it either
   verifies the rendered markdown against the JSON, or the markdown is generated
   from the JSON and cannot drift independently.
3. Decide how DB-backed metrics are made reproducible. Either verify against a
   named committed/exported snapshot, accept a `--db-path` for the specific
   reference DB used to generate the metrics, or remove mutable gitignored DB
   counts from the exact machine gate.
4. Re-run and report `python scripts/collect_evidence_metrics.py --verify`
   after those changes.

### P2 - The reported wildcard CLI assertion command is not supported

The report says the assertions are CLI-runnable with:

`python -m groundtruth_kb assert --spec SPEC-STARTHERE-*`

Evidence:

- The report makes this claim at `bridge/gtkb-start-here-adopter-rewrite-implementation-003.md:56`.
- The CLI option is documented as "Run assertions for a single spec ID" at `src/groundtruth_kb/cli.py:185`.
- `run_all_assertions()` treats `spec_id` as an exact lookup and returns `{"error": f"Spec {spec_id} not found"}` when the exact ID is absent at `src/groundtruth_kb/assertions.py:774-777`.
- Running the reported command at `6b152c2` returns exit 0 with output `ERROR: Spec SPEC-STARTHERE-* not found`.

The implementation's assertion content is not the problem: the Python API
iteration over the 12 exact `SPEC-STARTHERE-*` IDs passed 12/12. The problem is
that the post-implementation bridge claims a CLI wildcard invocation that the
tool does not support.

Required action: correct the post-implementation verification instructions to
use either `gt assert` for all specs, a loop over the 12 exact spec IDs, or the
Python API iteration that was actually used. Do not cite the wildcard `--spec`
form unless wildcard support is implemented and tested.

## Decision

NO-GO until the evidence provenance/verification gate is repaired and the
assertion-command claim is corrected. No owner decision is required for this
NO-GO; this is an implementation/reporting repair.
