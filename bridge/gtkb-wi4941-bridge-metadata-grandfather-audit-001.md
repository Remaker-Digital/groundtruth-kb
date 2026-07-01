NEW

# Defect-Fix Proposal — Slice 4: grandfather audit record (append-only-safe)

bridge_kind: prime_proposal
Document: gtkb-wi4941-bridge-metadata-grandfather-audit
Version: 001
Author: Prime Builder Cursor
Date: 2026-06-30T22:25:00Z

author_identity: Prime Builder Cursor
author_harness_id: E
author_session_context_id: cursor-pb-s522-metadata-compliance-wi4941
author_model: Composer
author_model_version: 2.5
author_model_configuration: Cursor interactive; session role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE-BRIDGE-AUTHOR-METADATA-COMPLIANCE-REMEDIATION-FORWARD-PREVENTION
Project: PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE
Work Item: WI-4941

target_paths: ["scripts/bridge_metadata_audit.py", ".gtkb-state/bridge-metadata-grandfather-audit/grandfather-audit-2026-06-30.json", "groundtruth-kb/docs/method/12-file-bridge-automation.md"]

implementation_scope: source,docs
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

748 historical bridge threads lack parseable session ids; mass re-VERIFIED is infeasible.
WI-4941 records a one-time grandfather audit artifact (append-only JSON + summary) using
the WI-4938 scanner output, documenting non-compliance baseline without mutating committed
bridge history. Active GO blockers (49 threads) remain a separate repair queue.

## Defect / Reproduction

Full-tree scan (2026-06-30): 748 missing / 127 synthetic on latest GO/VERIFIED; PAUTH forbids
rewrite of historical committed bridge files.

## In-Root Placement Evidence

Scanner script, grandfather record under `.gtkb-state/`, operator doc update in-root.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20266647` — grandfather policy for historical non-compliance.

## Owner Decisions / Input

Authorized by project PAUTH. Forbidden operations include historical bridge rewrite.

## Requirement Sufficiency

Existing requirements sufficient.

## Proposed Scope

1. Extend WI-4938 scanner with `--grandfather-report` mode emitting stable JSON snapshot.
2. Write `.gtkb-state/bridge-metadata-grandfather-audit/grandfather-audit-2026-06-30.json`.
3. Document grandfather policy in `12-file-bridge-automation.md` (forward-prevention vs repair queue).
4. No mutation of `bridge/*.md` committed history.

Depends on WI-4938 scanner (GO required first).

## Specification-Derived Verification Plan

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_metadata_audit.py --grandfather-report --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_metadata_audit.py -q --no-header
```

## Risks / Rollback

Read-only + one new state file. Revert commit removes record.

## Recommended Commit Type

docs — WI-4941 grandfather audit record.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
