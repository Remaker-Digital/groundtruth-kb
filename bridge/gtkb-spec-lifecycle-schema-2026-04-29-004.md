GO

# Loyal Opposition Review - GTKB Spec Lifecycle Schema Migration REVISED-1

**Document:** `gtkb-spec-lifecycle-schema-2026-04-29`
**Reviewed version:** `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-29

## Verdict

GO. REVISED-1 closes the three blocking findings from `bridge/gtkb-spec-lifecycle-schema-2026-04-29-002.md` sufficiently for scoping approval. This GO authorizes the recovery-program shape and follow-on slice proposals only. It does not pre-approve schema edits, backfill mutation, owner-triage execution, API changes, or cleanup; each implementation slice still requires its own bridge proposal with full specification links, spec-to-test mapping, execution plan, and verification evidence.

## Prior Deliberations

I searched deliberations before review with:

```text
python -m groundtruth_kb deliberations search "spec lifecycle schema migration parent attribute implementation_verified_at retired_at" --limit 8
```

Relevant hit:

- `DELIB-0707` - owner decision that existing specs must be migrated to the enriched schema using implementation as reference. This supports a real migration and makes deterministic backfill evidence mandatory.

The proposal also carries forward `DELIB-0636`, `DELIB-0791`, `DELIB-0808`, `DELIB-1196`, `DELIB-1245`, and `DELIB-1403`; I found no contrary deliberation that blocks the revised lifecycle-date direction.

## Closure Checks

### F1 - `parent NOT NULL` sequencing

Closed for scoping. The revised plan adds `parent` as nullable in Slice 1 (`-003` lines 61-70), defers `NOT NULL CHECK` enforcement to a table rebuild in Slice 1.5 (`-003` lines 94-112), and revises deployment order so the rebuild runs only after backfill proves zero null `parent` rows (`-003` lines 237-241). This directly addresses the populated SQLite-table failure identified in `-002` lines 30-47. The live schema remains populated and currently lacks `parent` (`groundtruth-kb/src/groundtruth_kb/db.py` lines 56-74 and 413-416), so the populated-fixture test remains mandatory for Slice 1 and Slice 1.5.

### F2 - `parent` backfill misclassification

Closed for scoping. The broad `GOV-*` / governance auto-classification was replaced with a conflict-aware classifier: only demonstrably non-conflicting prefixes auto-classify, while `GOV-*`, `ADR-*`, `DCL-*`, broad `GTKB-*`, and unknown cases route to owner-review triage (`-003` lines 134-158). The revised acceptance criterion explicitly tests `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-ARTIFACT-APPROVAL-001` as triage cases rather than silently stamping either value (`-003` lines 223-234).

### F3 - `implementation_verified_at` timestamp authority

Closed for scoping. The proposal no longer depends on a non-protocol bridge `changed_at` field. It defines a precedence order: harvested deliberation `changed_at` for the linked bridge thread, deterministic git commit timestamp as fallback, and NULL plus owner-review triage when no authoritative bridge thread can be linked (`-003` lines 202-208). This is compatible with the file bridge protocol, which defines status lines but no per-status timestamp field (`.claude/rules/file-bridge-protocol.md` lines 68-93).

## Carry-Forward Constraints

These are not blockers to this scoping GO, but they are approval constraints for later slice bridges:

1. Slice 4 must split its pre-API backfill/dry-run work from post-API write-path migration. `-003` line 239 moves "Slice 4 phases 3.1.b through 3.1.e" before Slice 1.5 and Slice 2, while `-003` lines 126-130 still describe Slice 4 as "write-path migration + conflict-aware backfill." The implementation bridge must make clear that only dry-run, triage, timestamp backfill, and parent backfill work can run before Slice 2 APIs/gates exist; intake/scaffold write-path changes must wait until the required API and gate methods exist.
2. The Slice 4 classifier fixture wording should be tightened. `-003` lines 160-168 list five fixture rows but then says pass 1 auto-classifies "the four unambiguous rows"; the listed rows appear to contain two auto-classified cases and three triage cases. The implementation bridge should correct the count and include `SHOPIFY-*` and `CUSTOMER-*` positive fixtures if those remain pass-1 auto rules.
3. Triage artifacts are working files, not canonical state. Any mutation pass that applies owner-confirmed `parent`, `implementation_verified_at`, or `retired_at` values must cite the owner approval packet and produce a stable machine-checkable input/output summary before verification.
4. Future slice proposals must repeat full `Specification Links` and test derivation for their own scope. References back to `-001`/`-003` are useful history, but implementation approval requires the active slice proposal itself to expose the governing specs and exact tests.

## Decision Needed From Owner

None for this GO. The proposal correctly leaves the timestamp precedence, triage approval shape, and compat-window timing visible as owner decisions before the relevant implementation/backfill slice executes.

## Scan Result

File bridge scan: 1 entry processed.
