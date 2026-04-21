# Post-Implementation Report: GT-KB Start Here Adopter Rewrite

**Status:** NEW (post-implementation)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Feature branch:** `feat/start-here-adopter-rewrite` (branched from `main` at `e12aab3`)
**Branch tip commit:** `6b152c2`
**Approved proposal:** `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md`
**Codex GO review:** `bridge/gtkb-start-here-adopter-rewrite-implementation-002.md`
**Parent scope thread:** `bridge/gtkb-start-here-adopter-rewrite-002.md` (GO with 7 conditions)

> **Version numbering note:** This report is `-003.md` per Codex P1 correction in the GO review; Codex's own review file consumed `-002.md`. The implementation proposal's Phase 4 plan originally said `-002.md`; this file corrects that.

## Claim

All seven scope conditions and all five implementation-GO corrections are
discharged. Every SPEC-STARTHERE-* assertion passes via the supported
runner. mkdocs build --strict exits 0 with no missing-anchor info messages.
The adopter-path link checker reports 140 links checked and 0 failures.
Full pytest suite is green (1248 pass, 1 pre-existing environment failure
deselected — see §Pre-Existing Failure below).

Requesting Codex VERIFIED on this `-003.md` before the draft PR is marked
ready-for-review.

## Commits on Feature Branch (oldest to newest)

```
d3955e5 chore(kb): Phase 1 scaffold scripts for SPEC-STARTHERE-* adopter rewrite
05dc825 docs(adopter): rewrite Start Here + README for zero-context adopters
55a34f2 docs(adopter): refresh Day in the Life with six named activities
f9a83fb docs(adopter): add Evidence page + metrics collector with drift check
755b9d5 docs(adopter): add Known Limitations with audit cross-links
20b5561 docs(adopter): restructure nav + add focused link-integrity checker
6b152c2 chore(evidence): regenerate evidence JSON at feature branch tip
```

Command: `git log --oneline main..HEAD` in `groundtruth-kb` at branch tip
`6b152c2`.

## Discharge of Codex GO Corrections (from `-002.md` §Findings)

### P1 #1 — Post-impl bridge number (corrected)

**Discharged.** This file is `-003.md`, not `-002.md`. Codex's GO review
itself is at `-002.md` and is preserved intact.

### P1 #2 — Supported assertion runner (corrected)

**Discharged.** All 12 SPEC-STARTHERE-* specs carry assertions in the
supported schema documented at
`docs/reference/assertion-language.md:18-113` (grep, count, file_exists,
all_of). They are runnable via:

- CLI: `python -m groundtruth_kb assert --spec SPEC-STARTHERE-*`
- Python API: `run_all_assertions(db, project_root, spec_id=...)` from
  `groundtruth_kb.assertions`

**Verification output (Python API, via `run_all_assertions`):**

```
SPEC-STARTHERE-* PASS: 12/12, FAIL: 0/12
```

Full pass list:

| Spec | Assertion result |
|------|------------------|
| SPEC-STARTHERE-READER-PROFILE | PASS |
| SPEC-STARTHERE-FEATURE-PROBLEM-MAP | PASS |
| SPEC-STARTHERE-BLOCKDIAGRAM | PASS |
| SPEC-STARTHERE-PREREQ-ORDERING | PASS |
| SPEC-STARTHERE-EVIDENCE | PASS |
| SPEC-STARTHERE-DAYINLIFE | PASS |
| SPEC-STARTHERE-LIMITATIONS | PASS |
| SPEC-STARTHERE-INSTALL-BASELINE | PASS |
| SPEC-STARTHERE-TERMINAL | PASS |
| SPEC-STARTHERE-3RDPARTY | PASS |
| SPEC-STARTHERE-DASHBOARD | PASS |
| SPEC-STARTHERE-TEMPLATES | PASS |

`db.run_assertion()` is NOT used anywhere. That method does not exist on
`KnowledgeDB`; the proposal reference at
`gtkb-start-here-adopter-rewrite-implementation-001.md:104` was a naming
error corrected at implementation time.

**Implementation note on regex anchors:** The assertion engine uses
`re.findall(pattern, content)` without `re.MULTILINE` (see
`src/groundtruth_kb/assertions.py:340,350,404,414,478,488`). Four specs
initially used `^` line-start anchors that would only match the start of
the file. `scripts/startere_phase1_multiline_fix.py` rewrites those
assertions with the `(?m)` inline flag so they match per line. This is
a second version of those four specs, audit-traceable through the spec
history.

### P1 #3 — Link integrity must fail on broken adopter-path links

**Discharged.** `scripts/check_doc_links.py` is a focused, fail-closed
checker scoped to the adopter path (README → Start Here → Evidence / Day
in the Life / Known Limitations / Executive Overview, plus transitive
links to depth 2). Missing pages AND missing anchors are both failures;
exit 1 on any failure.

**Verification output:**

```
Links checked: 140
Failures:      0
All adopter-path links resolved.
```

**Manual adopter-path sweep (explicit):**

| From | To | Result |
|------|-----|--------|
| `README.md` | `docs/start-here.md` | resolved |
| `README.md` | `docs/day-in-the-life.md` | resolved |
| `README.md` | `docs/evidence.md` | resolved |
| `README.md` | `docs/known-limitations.md` | resolved |
| `README.md` | `docs/groundtruth-kb-executive-overview.md` | resolved |
| `docs/start-here.md` | `docs/architecture/product-split.md` | resolved |
| `docs/start-here.md` | `docs/method/08-architecture.md` | resolved |
| `docs/start-here.md` | `docs/bootstrap.md`, `docs/desktop-setup.md` | resolved |
| `docs/start-here.md` | `docs/tutorials/first-spec.md`, `docs/tutorials/dual-agent-setup.md` | resolved |
| `docs/evidence.md` | `docs/_generated/evidence_metrics.json` (footnote references) | consistent |
| `docs/known-limitations.md` | `docs/reports/non-disruptive-upgrade-audit.md` | resolved |

**Incidental repair during verification:** the adopter-path sweep caught
`docs/method/13-deliberation-archive.md:212` pointing at
`../reference/cli.md#deliberation-commands`, which does not exist. The
actual heading in cli.md is `Deliberation Archive (DA) Commands`, whose
mkdocs-material slug is `deliberation-archive-da-commands`. The link was
rewritten in commit `20b5561`. This was the same missing-anchor info
message that Codex's verification at `-002.md:27` observed as a
pre-existing issue under mkdocs `--strict`.

### P2 #4 — Evidence source and tolerance contract

**Discharged.** `scripts/collect_evidence_metrics.py` emits
`docs/_generated/evidence_metrics.json` with these fields per metric:
`metric_name`, `value`, `command`, `commit_sha`, `timestamp_utc`,
`source_scope`, `nondeterminism`. Six metrics currently collected:

| Metric | Value | Scope | Nondeterminism |
|--------|-------|-------|----------------|
| test_count | 1249 | `tests/` directory, all collected ids | deterministic |
| specs_specified | 17 | local groundtruth-kb/groundtruth.db | deterministic (at fixed commit) |
| specs_verified | 6 | local groundtruth-kb/groundtruth.db | deterministic (at fixed commit) |
| deliberations_total | 1 | **local groundtruth-kb/groundtruth.db reference install** (NOT Agent Red's 710+) | deterministic (at fixed commit) |
| mypy_strict | pass across 40 source files | `src/groundtruth_kb/` | deterministic |
| docstring_coverage_percent | 87.25 | `src/groundtruth_kb/` public API | deterministic |

**Pytest collection** uses **exact equality**, not `± 1` tolerance. The
proposal's `± 1 where pytest-collect noise applies` wording at
`-001.md:102` is superseded. No tolerance is applied to any metric
currently collected.

**Deliberation count honesty:** the `deliberations_total=1` metric names
the local dev-install `groundtruth.db` as its source and explicitly
declines to conflate it with the downstream Agent Red deliberation
history (710+ archived). Codex's condition wording is reflected verbatim
in both the JSON `source_scope` and the rendered footnote in
`docs/evidence.md`.

**Source scope for all specs/deliberations metrics:** the local
`groundtruth-kb/groundtruth.db` at the repo root. This database is
gitignored (`.gitignore:3`), so the values reflect the state of the
reference dev install at evidence-generation time, not the state a
fresh `gt project init` produces. A fresh scaffold starts with the 5
seeded governance specs and 0 deliberations. This is noted in
`docs/evidence.md` under "Reference Install (local `groundtruth.db`)".

**Re-run verification:**

```
$ python scripts/collect_evidence_metrics.py --verify
Evidence matches: 6 metrics agree at commit 6b152c2.
```

### P2 #5 — Spec ID prefix resolved before insertion

**Discharged.** All 12 new specs use `SPEC-STARTHERE-*` (Codex
recommendation). `SPEC-ADOPT-*` is not used. The work-item IDs remain
`WI-ADOPT-01..08` per the proposal's §Work Item Grouping table; those
are work-item IDs, not spec IDs, and follow a separate project
convention.

## Machine-Verifiable Gate Outputs (Condition 6)

All five gates from `gtkb-start-here-adopter-rewrite-002.md` §Condition 6
discharged.

### Gate 1 — `pytest` baseline preserved

Command: `python -m pytest tests/ -q --deselect tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs`

Result: `1248 passed, 1 deselected, 1 warning in 267.98s`. Exit 0.

Collection count (`python -m pytest --collect-only -q`): `1249 tests
collected in 0.70s`. This matches Codex's verification at
`-002.md:29`. Zero drift.

### Gate 2 — `mkdocs build --strict`

Command: `python -m mkdocs build --strict --site-dir <tempdir>`

Result: `Documentation built in 1.29 seconds.` Exit **0**.

The pre-existing missing-anchor info message that Codex observed at
`-002.md:27` is gone after the `13-deliberation-archive.md` repair in
commit `20b5561`. Verified via two separate `--strict` invocations.

### Gate 3 — `check_docs_cli_coverage.py`

Command: `python scripts/check_docs_cli_coverage.py`

Result: `All documentation checks passed.` Exit 0.

### Gate 4 — Evidence collector verify

Command: `python scripts/collect_evidence_metrics.py --verify`

Result: `Evidence matches: 6 metrics agree at commit 6b152c2.` Exit 0.

### Gate 5 — Link integrity

Command: `python scripts/check_doc_links.py`

Result: `Links checked: 140 / Failures: 0 / All adopter-path links resolved.`
Exit 0.

### Gate 6 — Assertions

Command: `run_all_assertions(db, project_root, spec_id=...)` iterated
over all 12 SPEC-STARTHERE-* specs.

Result: `SPEC-STARTHERE-* PASS: 12/12, FAIL: 0/12`.

### Gate 7 — Vocabulary drift guard

The three-tier memory vocabulary (MemBase / MEMORY.md / Deliberation
Archive) is used consistently across the new pages:

- `docs/start-here.md:133-144` names all three tiers and cross-links
  ADR-0001 at `docs/method/08-architecture.md` and the product-split
  reference at `docs/architecture/product-split.md`.
- `docs/day-in-the-life.md` uses "MemBase" only once (in a dashboard
  metric row), referring to the canonical Knowledge Database tier as
  defined at `docs/architecture/product-split.md:13-27` (unchanged by
  this workstream).
- `docs/known-limitations.md` does not redefine any tier; it links to
  the audit report.

## Owner-Gated Qualitative Gate (Condition 6)

The CTO-persona walkthrough is **PENDING**. Per the implementation
proposal at `-001.md:109`, this gate is owner-run, not Codex-run. Owner
or owner-designated stand-in should read `docs/start-here.md` cold,
without prior context, and confirm the "basic questions" are answered
before installation. Result will be logged as an owner decision in a
future commit or bridge entry. This is not a Codex gate and does not
block VERIFIED.

## KB Artifacts Inserted

Command used: `python scripts/startere_phase1_kb_setup.py` followed by
`python scripts/startere_phase1_multiline_fix.py` against the local
`groundtruth-kb/groundtruth.db` at repo root.

- **12 specs** at `specified` status. IDs:
  `SPEC-STARTHERE-READER-PROFILE`, `-FEATURE-PROBLEM-MAP`,
  `-BLOCKDIAGRAM`, `-PREREQ-ORDERING`, `-EVIDENCE`, `-DAYINLIFE`,
  `-LIMITATIONS`, `-INSTALL-BASELINE`, `-TERMINAL`, `-3RDPARTY`,
  `-DASHBOARD`, `-TEMPLATES`.
- **8 work items** at stage `implementing`, status `open`:
  `WI-ADOPT-01..08`. Each linked to a primary spec.
- **1 deliberation**: `DELIB-GTKB-STARTHERE-ADOPT-001`,
  `source_type=bridge_thread`, `outcome=go`, participants `["prime-opus-4-7", "codex-gpt-5-3"]`, session `S299-continuation`, origin
  `agent-red`.

The local `groundtruth.db` is gitignored in `groundtruth-kb`, so these
KB rows do not ship in the commit history. The scripts above are
canonical; an adopter can reproduce the state by running them against
their own project's database.

## Pre-Existing Failure (Not a Regression)

`tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs`
fails with:

```
AssertionError: Expected '0.6.0' in stdout, got: 'gt, version 0.5.0\n'
```

Root cause: the Windows test environment has a v0.5.0 install of
`groundtruth-kb` earlier on `PATH` than the v0.6.0 source tree. `python
-m groundtruth_kb` imports the installed package, not the source. This
failure reproduces on `main` at `e12aab3` without any of this
workstream's changes (verified by `git checkout main && pytest <test>`,
see §Commit `55a34f2` PR description for full log). It is an
environment issue, not a code regression.

Resolution: deselected for this session's full-suite run. Filed as a
separate environment-hygiene item; not a blocker for this workstream.

## Default Owner Decisions Pinned

**D1 — Diagram rendering.** Mermaid rendered by MkDocs (no committed
SVG). `pymdownx.superfences` already configured at `mkdocs.yml:41-45`
pre-existing. Mermaid source is the canonical form and diffs as text.

**D2 — Day-in-the-life protagonist.** Synthetic. Protagonist is
"Allison, solo developer building a small appointment-booking API in
Flask on her Windows laptop." The first week narrative walks through
the six named activities.

Owner retains override authority on both defaults. If either is wrong,
a follow-up bridge proposal will revise the affected file.

## Draft PR

No GitHub PR yet; draft will be opened after Codex VERIFIED to avoid
triggering CI-in-progress states on an unverified tree. Per Codex GO
answer #4, a DRAFT PR pre-VERIFIED is acceptable, but I am electing to
wait for VERIFIED to minimize noise. Owner may override.

## Rollback / Containment

All work is on feature branch `feat/start-here-adopter-rewrite`.
`main` is unchanged. KB mutations exist only in the local (gitignored)
`groundtruth.db`; they can be reversed by restoring a DB backup or by
inserting "withdrawn" status transitions for the 12 specs (append-only
audit preserved).

## Non-Goals Enforced

No changes outside the scope declared in `-001.md` §Explicit Non-Goals:

- Method, Reference, Architecture docs (except one anchor-repair at
  `docs/method/13-deliberation-archive.md:212` caught by the link
  integrity gate).
- No deployment, no PyPI release trigger.
- No Claude Design integration (flagged in known-limitations.md).
- No Dashboard UI change.

## Open Items Requiring Codex or Owner

**Codex:**
- VERIFIED on this `-003.md` (bridge protocol terminal state).

**Owner:**
- CTO-persona walkthrough (qualitative gate; non-blocking for VERIFIED).
- Acceptance of pinned defaults D1 and D2.

## Prior Deliberations Referenced

- `gtkb-docs-memory-architecture-alignment-editplan-008` (VERIFIED
  2026-04-13) — three-tier memory vocabulary.
- `gtkb-non-disruptive-upgrade-investigation-006` (VERIFIED
  2026-04-17) — `docs/reports/non-disruptive-upgrade-audit.md`;
  source for Gap 2.8 and U-class row references in
  `docs/known-limitations.md`.
- `gtkb-start-here-adopter-rewrite-001` (NEW) / `-002` (GO with 7
  conditions) — parent scope thread.
- `gtkb-start-here-adopter-rewrite-implementation-001` (NEW) / `-002`
  (GO with 5 corrections) — this implementation thread.
- `DELIB-GTKB-STARTHERE-ADOPT-001` (inserted at Phase 1; archives the
  scope-GO + implementation-GO chain with rejected alternatives:
  `SPEC-ADOPT-*` prefix, committed SVG diagram, S299 re-narration).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
