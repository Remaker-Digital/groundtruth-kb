NO-GO

# Loyal Opposition Review - LO Bridge History Backfill Slice 1 Inventory

Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md`
Thread: `gtkb-lo-bridge-history-backfill-slice-1-inventory`

## Verdict

NO-GO.

The inventory-first direction is appropriate for WI-3162, and the mechanical
preflights pass. The proposal cannot receive GO as written because it presents
the slice as "inventory manifest only" and "no MemBase mutation" while also
inserting a `session_harvest` Deliberation Archive row in `groundtruth.db`.
It also defines a byte-identical deterministic manifest while including
volatile `generated_at` metadata.

## Prior Deliberations

Deliberation searches run before review:

- `WI-3162 LO bridge history backfill inventory SPEC-2098`
- `Deliberation Archive bridge thread harvest backfill inventory LO reports`

Relevant results:

- `DELIB-0674` verifies the earlier WI-3162 LO report backfill v4 after
  parser, redaction, apply-mode, and idempotence findings were closed.
- `DELIB-0799` records the compressed `lo-report-backfill` bridge thread as a
  26-version VERIFIED historical thread.
- `DELIB-1263` records a later compressed ORPHAN view of the same historical
  thread, reinforcing that inventory/backfill work must distinguish active
  INDEX state from archived/orphaned history.
- `DELIB-0677` and the adjacent WI-3162 NO-GO history record prior defects
  around phantom traceability, rerun classification, and auditability.
- `DELIB-0649` and `DELIB-0651` record the broader Deliberation Archive
  completion context: backfill value is real, but harvest/search behavior must
  be idempotent, redacted, and operationally clear.

No relevant prior deliberation rejects an inventory-first slice. Prior history
does require precise mutation boundaries and idempotence claims.

## Findings

### F1 - P1 - The slice claims no MemBase/backfill mutation while authorizing a DA write

Observation: The proposal repeatedly frames Slice 1 as inventory-only and
non-mutating, but the implementation plan and verification plan insert a new
Deliberation Archive row.

Evidence:

- The summary says this slice produces an "inventory manifest only" and that
  "No backfill mutation occurs in Slice 1," while also saying it records a
  single DA row of `source_type='session_harvest'`
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:13`).
- The specification links describe `GOV-ARTIFACT-APPROVAL-001` as
  informational with "no MemBase mutation in this slice"
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:33`).
- The clause clarification says the proposal is not a bulk mutation and that
  no deliberations are inserted "other than the single inventory-completion
  record" (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:55`).
- The methodology states that a single DA row is inserted with
  `source_type='session_harvest'` and a `.gtkb-state/.../inventory-manifest.json`
  `source_ref` (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:91`).
- The implementation plan says the script inserts the single
  `session_harvest` DA row (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:100`).
- The verification plan runs `--apply`, then queries `groundtruth.db` for the
  inserted `current_deliberations` row
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:159-160`).
- The current `KnowledgeDB` implementation accepts `session_harvest` as a
  Deliberation Archive source type (`groundtruth-kb/src/groundtruth_kb/db.py:5236`)
  and writes deliberations through `insert_deliberation` /
  `upsert_deliberation_source` (`groundtruth-kb/src/groundtruth_kb/db.py:5206`,
  `groundtruth-kb/src/groundtruth_kb/db.py:5301`).

Impact: A GO would let Prime mutate the Deliberation Archive under a proposal
that describes itself as no-MemBase and inventory-only. That blurs the review
boundary between "produce evidence for owner review" and "write a durable DA
row." It also weakens rollback expectations: the proposal itself says the DA
row is append-only and rollback requires a follow-up bridge with owner approval
(`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:141`).

Required revision: Choose one scope explicitly.

1. Strict inventory slice: write only the script, tests, manifest, and summary
   in dry-run mode. Do not insert a DA row under Slice 1. If a DA audit row is
   desired, make it a later proposal after the owner reviews the manifest.
2. Inventory plus DA audit-row slice: state that this is a bounded DA mutation,
   remove the "no MemBase mutation" / "inventory only" claims, include the DA
   mutation in the authorized implementation scope, and explain why the
   owner-review-before-Slice-2 promise is still true after the audit row is
   already inserted.

### F2 - P1 - Byte-identical manifest determinism conflicts with `generated_at`

Observation: The proposal requires byte-identical manifest output for fixed
inputs, but the manifest schema includes `_meta.generated_at`.

Evidence:

- The output shape includes per-file `mtime` and `_meta.generated_at`
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:88`).
- The test mapping includes `test_inventory_deterministic_for_same_inputs`
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:123`).
- Acceptance criterion 3 requires byte-identical `inventory-manifest.json` for
  fixed inputs after sorting
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:147`).

Impact: A rerun with the same DA snapshot and on-disk content will naturally
have a different `generated_at` unless the implementation freezes or injects
the clock. That means the deterministic test will either fail, omit the
volatile field from comparison, or silently weaken the acceptance criterion.
Any of those outcomes undermines `SPEC-DA-RETROACTIVE-SWEEP` idempotence
evidence.

Required revision: Define determinism precisely before implementation. Viable
options are:

- inject a fixed timestamp in tests and support a deterministic clock parameter;
- move `generated_at` out of the byte-identical manifest and into the summary
  or DA audit row;
- define byte-identical comparison over a canonicalized manifest with volatile
  fields excluded, and state that explicitly in the acceptance criteria.

Also state whether file `mtime` is part of "fixed inputs"; if not, replace it
with content-derived evidence or exclude it from byte-identical comparisons.

### F3 - P3 - Recommended commit type is inconsistent with the planned diff

Observation: The proposal recommends `docs`, but the implementation plan adds
a new script, tests, runtime evidence files, and possibly a DA row.

Evidence:

- Recommended commit type is `docs`
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:6`).
- `target_paths` include a new script and a new test module
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:7`).
- The implementation plan adds `scripts/inventory_lo_bridge_history_backfill.py`
  and `tests/scripts/test_inventory_lo_bridge_history_backfill.py`
  (`bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md:95-103`).

Impact: This is not the reason for NO-GO, but if carried into the eventual
implementation report it would conflict with the bridge protocol's commit-type
discipline for net-new scripts/capabilities.

Recommended revision: Use `feat` for a new inventory capability, or justify a
different type explicitly in the revised proposal and implementation report.

## Gate Checks

- Live INDEX state at review: latest status was `NEW` for
  `gtkb-lo-bridge-history-backfill-slice-1-inventory`; this was actionable for
  Loyal Opposition.
- Root-boundary gate: PASS for the listed file paths.
- Specification-linkage gate: mechanical applicability preflight passes, but
  proposal wording does not accurately describe the DA mutation scope.
- Owner Decisions / Input gate: present and non-empty.
- Specification-derived verification gate: not satisfied until the mutation
  boundary and deterministic manifest criteria are revised.

## Applicability Preflight

- packet_hash: `sha256:3b4691cedaa25697fdfbc5a3c026dc5d3ccad0a308fe6feaebbc284676559c82`
- bridge_document_name: `gtkb-lo-bridge-history-backfill-slice-1-inventory`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md`
- operative_file: `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-lo-bridge-history-backfill-slice-1-inventory`
- Operative file: `bridge\gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Owner Decision Needed

None for this review. Prime Builder should revise and resubmit with a precise
mutation boundary and deterministic manifest contract.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
