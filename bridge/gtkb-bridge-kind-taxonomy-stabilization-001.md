NEW

# Implementation Proposal — GT-KB Bridge Kind Taxonomy Stabilization

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-bridge-kind-taxonomy-stabilization`
**Builds on:** LO finding 2026-06-04 (Bridge Kind Taxonomy Drift)

## 1. Scope

Consolidates 25+ distinct `bridge_kind` values and 11+ synonyms for Loyal Opposition verdicts into a canonical enum. Implements a bridge-compliance-gate lint to prevent future drift.

## 2. Deliverables

### 2.1 Canonical Enum (`groundtruth_kb.bridge.taxonomy.BridgeKind`)

- `PRIME_PROPOSAL`
- `LO_VERDICT`
- `IMPLEMENTATION_REPORT`
- `GOVERNANCE_ADVISORY`
- `INDEX_RECONCILIATION`
- `OPERATIONAL_STATE_CHANGE`

### 2.2 Bridge Compliance Lint (`scripts/lint_bridge_proposals.py`)

- Validates `bridge_kind` against the canonical enum.
- Blocks execution of non-compliant proposals.

### 2.3 Migration Script (`scripts/migrate_bridge_kind_taxonomy.py`)

- Automates the re-versioning backfill of the existing bridge corpus to use canonical values.

## 3. Execution Plan

1. Land the enum and the lint.
2. Run migration across `bridge/*.md`.
3. Update `scan_bridge.py` to use the new enum.

## 4. Reversibility

- Revert to free-text strings by removing the lint.
