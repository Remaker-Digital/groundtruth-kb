NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-17-da-chroma-read-path
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-17-da-chroma-read-path-001.md

# Loyal Opposition Review - FAB-17 DA/Chroma Read Path

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-17-da-chroma-read-path-001.md`
for WI-4429 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-17 is independent of the FAB-11/FAB-13 database retention work because it changes the
Deliberation Archive read path and derived Chroma index handling, not canonical DA/MemBase records.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path`
  passed with `missing_required_specs=[]` and no advisory omissions. It warned that
  `groundtruth-kb/src/groundtruth_kb/benchmarks/**` has a missing parent directory, which is
  acceptable only if the proposal intends to create that package path.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB17-REMEDIATION-20260610` confirms the owner selected
  `count()` fallback hardening, bounded timeout/retry, benchmark CLI repair, and Chroma triplication
  resolution.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB17-20260610` for WI-4429, allowing Chroma index deduplication while forbidding canonical
  MemBase/DA record mutation.
- `gt backlog list --json --id WI-4429` confirms WI-4429 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Blocking Finding

### F1 - Chroma deduplication/removal paths are not in target_paths

The proposal's Area 3 says to consolidate/remove duplicate Chroma index copies and ensure all read paths
resolve to a single canonical `.groundtruth-chroma` index. The target set includes the source/config
that would describe the canonical path, but it does not include:

- `.groundtruth-chroma/**`
- any duplicate Chroma index copy paths
- any bounded glob/path set for Chroma deduplication or deletion

The active PAUTH allows `chroma_index_deduplication`, but bridge implementation scope is still
path-scoped. If the implementation deletes, moves, or rewrites derived Chroma index directories, the
proposal must name that perimeter so Loyal Opposition can verify it does not touch canonical DA records
or unrelated runtime state.

## Required Revision

Submit a REVISED proposal that either:

1. Adds concrete target paths for the canonical Chroma index and every duplicate index path/glob to be
   removed or consolidated, with verification that canonical `groundtruth.db` / DA records are not mutated;
   or
2. Defers Chroma deduplication to a separate bridge item and limits FAB-17 to the DA search fallback,
   benchmark CLI, timeout/retry, and read-path config changes.

The revised proposal should also explain whether `groundtruth-kb/src/groundtruth_kb/benchmarks/**` is a
new package path being created or whether that target should be removed.

## Verdict

NO-GO until the Chroma deduplication target paths are concrete or the deduplication work is deferred.
