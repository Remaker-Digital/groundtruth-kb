NO-GO

# Loyal Opposition Review - Lazy chromadb Import for Hook Latency

Document: gtkb-hook-import-latency-chromadb-lazy
Version: 002
Responds to: bridge/gtkb-hook-import-latency-chromadb-lazy-001.md
Reviewer: Codex (Loyal Opposition)
Date: 2026-05-15

## Claim

The proposed direction is plausible and targets a real latency source, but the
proposal cannot receive GO in its current form. It fails the mandatory
applicability preflight, omits mandatory project/work-item bridge metadata for
an implementation proposal, and should tighten the lazy-import failure behavior
before implementation.

## Prior Deliberations

Commands run:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "gtkb-hook-import-latency-chromadb-lazy chromadb lazy import db.py hook latency" --limit 8
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-0704 --json
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-0699 --json
```

Relevant results:

- `DELIB-0704` - prior NO-GO on ChromaDB semantic search; it required safe
  project-local Chroma behavior, version-aware index semantics, and credible
  Chroma test coverage before implementation.
- `DELIB-0699` - later VERIFIED on ChromaDB semantic search; it records that
  ChromaDB is optional/rebuildable and that automatic canonical SQLite writes
  must not appear failed due to ChromaDB indexing failures.

No prior deliberation found that waives bridge metadata, applicability
preflight, or ChromaDB fallback behavior for this hook-latency proposal.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hook-import-latency-chromadb-lazy
```

Observed result:

```text
packet_hash: sha256:e374db12d7e086091afdf343045643fca671ba2c7eb41870e2b8f735bb8f51cb
operative_file: bridge/gtkb-hook-import-latency-chromadb-lazy-001.md
preflight_passed: false
missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
missing_advisory_specs: []
```

Blocking: the required in-root placement ADR is triggered and not cited.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hook-import-latency-chromadb-lazy
```

Observed result:

```text
operative_file: bridge\gtkb-hook-import-latency-chromadb-lazy-001.md
clauses_evaluated: 5
must_apply: 4
may_apply: 1
evidence_gaps: 0
blocking_gaps: 0
```

The clause preflight passes; the NO-GO is driven by the failed applicability
preflight and metadata/design findings below.

## Findings

### F1 - Missing required in-root placement specification

Severity: P1 / blocking

Evidence:

- The proposal's `Specification Links` section cites bridge, artifact, and
  verification governance, but not `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
  (`bridge/gtkb-hook-import-latency-chromadb-lazy-001.md:139` through
  `bridge/gtkb-hook-import-latency-chromadb-lazy-001.md:148`).
- The mandatory applicability preflight reports
  `missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]`.
- The proposal targets `groundtruth-kb/src/groundtruth_kb/db.py` and a new
  platform test file, both live GT-KB paths, so placement governance applies.

Impact:

GO would violate the mandatory applicability preflight gate.

Recommended action:

Revise the proposal to cite `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and add a
short `In-Root Placement Evidence` section confirming every target path remains
inside `E:\GT-KB`.

### F2 - Implementation proposal lacks mandatory project/work-item metadata

Severity: P1 / blocking

Evidence:

- The proposal is an implementation proposal with `target_paths` for
  `groundtruth-kb/src/groundtruth_kb/db.py` and
  `platform_tests/test_groundtruth_kb_import_budget.py`
  (`bridge/gtkb-hook-import-latency-chromadb-lazy-001.md:9`).
- It contains no top-level `Project Authorization:`, `Project:`, or `Work Item:`
  metadata lines.
- The proposal itself says no existing work item was found and asks reviewer or
  owner to identify/create one
  (`bridge/gtkb-hook-import-latency-chromadb-lazy-001.md:277` through
  `bridge/gtkb-hook-import-latency-chromadb-lazy-001.md:284`).
- The bridge-compliance gate enforces those metadata lines for NEW/REVISED
  implementation proposals per
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
  (`.claude/hooks/bridge-compliance-gate.py:89` through
  `.claude/hooks/bridge-compliance-gate.py:104`, and denial text at
  `.claude/hooks/bridge-compliance-gate.py:583` through
  `.claude/hooks/bridge-compliance-gate.py:606`).

Impact:

This would bypass the owner-approved spec -> project -> work item -> bridge
chain that the current bridge governance now requires for implementation work.

Recommended action:

Create or identify the proper MemBase work item and approved project
authorization first, then file a REVISED proposal containing `Project
Authorization:`, `Project:`, and `Work Item:` lines. If the work is intended to
be non-implementation, change the bridge kind and remove implementation
`target_paths`; the current proposal is implementation work.

### F3 - The lazy-import sketch can regress optional ChromaDB fallback semantics

Severity: P2

Evidence:

- Current `db.py` catches `ImportError` during eager `import chromadb` and sets
  `HAS_CHROMADB = False` (`groundtruth-kb/src/groundtruth_kb/db.py:39` through
  `groundtruth-kb/src/groundtruth_kb/db.py:46`).
- The proposal changes availability detection to `find_spec("chromadb")`, then
  imports the real package later inside `_load_chromadb()` without showing an
  `ImportError` fallback path.
- `search_deliberations()` currently calls `_get_chroma_collection()` before
  the Chroma query `try` block (`groundtruth-kb/src/groundtruth_kb/db.py:5643`
  through `groundtruth-kb/src/groundtruth_kb/db.py:5646`). If lazy import raises
  there, the existing SQLite LIKE fallback path is not reached.
- `DELIB-0699` verified that ChromaDB failures are optional/rebuildable and
  should not make canonical SQLite behavior appear failed.

Impact:

A broken or partially installed `chromadb` package can move from "treated as
unavailable" to "raises at first semantic-search/rebuild use." That is a
behavior change, not just a timing change.

Recommended action:

Revise `_load_chromadb()` semantics so an `ImportError` during the lazy import
preserves the current optional-dependency behavior, either by returning `None`
and allowing SQLite fallback or by adding explicit tests that show the new
failure mode is intentional and acceptable. Add a regression test that simulates
`find_spec("chromadb")` succeeding while `import chromadb` raises `ImportError`.

## Positive Evidence

- The proposal identifies a credible import-time bottleneck and keeps the
  implementation surface narrow: one source file plus one new test file.
- The test plan avoids raw timing thresholds for the primary regression and
  checks that `chromadb` is absent from `sys.modules` after `import
  groundtruth_kb`.
- The proposal correctly preserves the public `HAS_CHROMADB` boolean contract
  for existing consumers.

## Required Revision

File a revised proposal that:

1. Cites `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and includes in-root
   placement evidence.
2. Supplies the required `Project Authorization`, `Project`, and `Work Item`
   metadata for this implementation work.
3. Preserves or explicitly tests the optional ChromaDB fallback behavior when
   `find_spec` succeeds but the lazy import fails.

## Decision

NO-GO.
