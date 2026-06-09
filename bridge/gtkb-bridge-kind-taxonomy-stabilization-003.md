REVISED

# Implementation Proposal — GT-KB Bridge Kind Taxonomy Stabilization

**Status:** REVISED
**Document name:** `gtkb-bridge-kind-taxonomy-stabilization`
**Version:** 003
**Author:** Prime Builder (antigravity/pb)
**Session:** S509 (2026-06-09)
**Builds on:** [LOYAL-OPPOSITION-LOG.md](file:///E:/GT-KB/independent-progress-assessments/LOYAL-OPPOSITION-LOG.md) entry from 2026-06-04 ("LO autonomous /loop: empty queue + bridge_kind taxonomy drift").

## Specification Links

- [GOV-FILE-BRIDGE-AUTHORITY-001](file:///E:/GT-KB/config/governance/gov-file-bridge-authority-001.md) — Live bridge index authority and permanent bridge repair authority.
- [DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Bridge proposal spec linkage must be relevance-complete.
- [DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Verification must execute spec-derived tests.
- [ADR-ISOLATION-APPLICATION-PLACEMENT-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Placement contract for application isolation.
- [DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Artifact lifecycle transitions and validation triggers.
- [GOV-ARTIFACT-ORIENTED-GOVERNANCE-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Governance over design, specification, and implementation records.

## Implementation Scope

- **Project:** `PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION`
- **Work Item:** `WI-4341`
- **Project Authorization:** `PAUTH-PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION-IMPL`
- **Requirement Sufficiency:** Existing requirements sufficient
- **target_paths:**
  - `groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py`
  - `scripts/lint_bridge_proposals.py`
  - `scripts/migrate_bridge_kind_taxonomy.py`
  - `scan_bridge.py`
  - `bridge/*.md` (in-place edits only)

All target paths and implementation artifacts reside under the project root (`E:\GT-KB`), satisfying the in-root requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Proposed Design Constraints

- **DCL-BRIDGE-KIND-TAXONOMY-ENUM-001:** The allowed values for the `bridge_kind` field in all bridge markdown files are restricted to the canonical set: `PRIME_PROPOSAL`, `LO_VERDICT`, `IMPLEMENTATION_REPORT`, `GOVERNANCE_ADVISORY`, `INDEX_RECONCILIATION`, `OPERATIONAL_STATE_CHANGE`.
- **DCL-BRIDGE-KIND-VS-STATUS-001:** `BridgeKind` represents the classification of the document/thread type, which is independent of the `BridgeStatus` (NEW, GO, NO-GO, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN) that tracks the workflow state of a specific file version in `bridge/INDEX.md`.

## Proposed Changes

### 1. Canonical Enum
- Implement `groundtruth_kb.bridge.taxonomy.BridgeKind` containing:
  - `PRIME_PROPOSAL`
  - `LO_VERDICT`
  - `IMPLEMENTATION_REPORT`
  - `GOVERNANCE_ADVISORY`
  - `INDEX_RECONCILIATION`
  - `OPERATIONAL_STATE_CHANGE`

### 2. Lint and Validation
- Implement `scripts/lint_bridge_proposals.py` to check that the `bridge_kind` field in every versioned file in `bridge/` matches one of the canonical enum values.
- Integrate this lint into the pre-file bridge compliance hook to block non-compliant writes.

### 3. Migration and Safety
- Implement `scripts/migrate_bridge_kind_taxonomy.py` to update the existing bridge corpus in `bridge/*.md` to use canonical `bridge_kind` values.
- **Safety / No-Delete Guarantee:** No files will be deleted or removed from the directory. The script only updates the `bridge_kind: <value>` headers in-place.
- **Reversibility / Rollback Plan:** Before running the migration, the script will back up the entire `bridge/` directory to `.gtkb-state/bridge-backup-taxonomy-migration/`. If rollback is triggered, the files from the backup directory will be restored.

## Specification-Derived Verification Plan

- **Test for Lint Compliance:** Verify that `scripts/lint_bridge_proposals.py` blocks invalid `bridge_kind` values and accepts valid ones.
- **Test for Migration Safety & Rollback:** Verify that the migration script updates `bridge_kind` successfully and that rollback restores the exact original files.

### Automated Tests
- Run `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_kind_taxonomy.py -q --tb=short`
