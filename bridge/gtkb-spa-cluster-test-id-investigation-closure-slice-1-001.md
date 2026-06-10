NEW

# Implementation Proposal - SPA Cluster Test-ID Investigation Closure Slice 1 (inventory + DA closure)

bridge_kind: prime_proposal
Document: gtkb-spa-cluster-test-id-investigation-closure-slice-1
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source: WI-3183 (KB integrity -- SPA cluster test-ID investigation closure)
Recommended commit type: docs
target_paths: ["independent-progress-assessments/spec-hygiene/S350-spa-cluster-test-id-inventory.md", "scripts/audit_spa_cluster_test_id_inventory.py", "platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py", "groundtruth.db"]

## Summary

WI-3183 is the investigation/closure work item for the SPA control-plane cluster placeholder test-ID problem first surfaced by `bridge/spec-hygiene-spa-investigation-001..008.md` and partially addressed by `bridge/spec-hygiene-spa-remediation-001..006.md` (VERIFIED 2026-04-15). Live MemBase probe confirms the WI-3183 description: across the 10 SPA control-plane specs (SPEC-1816, 1818-1824, 1826, 1827), 23 historical test_id rows were recycled at session S200 with `spec_id` field reassigned to SPEC-1837 (Log Retention). At the **latest-version** of each test row (the current state per ADR-0001 append-only versioning), **0 tests are bound to any of the 10 SPA specs**. The current spec `status='implemented'` is unsupported by linked test evidence.

This slice produces a single inventory deliverable plus one Deliberation Archive closure entry. It is a read-only investigation that does **not** modify specs, tests, or work items. The sibling action WI-3184 (status revert from verified to implemented) consumes this slice's inventory as evidence; that revert is filed under a separate bridge thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; one NEW filing, INDEX update deferred per task instruction.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited below.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in `## Test Mapping` section; verification deliverable is itself a test-coverage report.
- `GOV-STANDING-BACKLOG-001` - WI-3183 is the singular tracking work item; no bulk operations.
- `GOV-ARTIFACT-APPROVAL-001` - inventory file is a narrative deliverable; DA closure entry uses the formal-artifact-approval pathway.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`; no `applications/` paths.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - inventory and DA entry are tracked governance artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - investigation produces durable, owner-visible artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - closure transitions trigger the WI-3184 revert lifecycle event.
- SPEC-1816 - Superadmin Entitlement Management API (latest v4, status=implemented, 0 latest-version tests).
- SPEC-1818 - SPA Console: Full Service Management (v5, implemented, 0 tests).
- SPEC-1819 - SPA Console: Code-Free Runtime Configuration (v4, implemented, 0 tests).
- SPEC-1820 - Allow/Block List Management (v4, implemented, 0 tests).
- SPEC-1821 - Back-off and Retry Configuration (v4, implemented, 0 tests).
- SPEC-1822 - Alert Threshold Configuration (v4, implemented, 0 tests).
- SPEC-1823 - Notification Channel Configuration (v4, implemented, 0 tests).
- SPEC-1824 - Feature Flag System (v4, implemented, 0 tests).
- SPEC-1826 - SPA Test Execution Trigger (v4, implemented, 0 tests).
- SPEC-1827 - Diagnostic Data Export for Claude Code (v4, implemented, 0 tests).
- `.claude/rules/file-bridge-protocol.md` - bridge structure and Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` - review obligations including Owner Decisions / Input section.
- `.claude/rules/project-root-boundary.md` - all paths in-root under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-0770` v1: "Bridge thread: spec-hygiene-spa-remediation (6 versions, VERIFIED)" - prior remediation closure (2026-04-15) reverted the cluster from verified to implemented but did not produce a durable inventory artifact closing the placeholder-test investigation.
- `DELIB-1282` v1: "Bridge thread: spec-hygiene-spa-investigation (8 versions, ORPHAN)" - the 8-version investigation thread that originally discovered the S200 recycling; no closure DA entry was filed.
- `DELIB-1283` v1: "Bridge thread: spec-hygiene-spa-remediation (6 versions, ORPHAN)" - compressed thread record for the remediation half.
- WI-3184 (sibling): control-plane placeholder-test remediation - this slice provides the inventory evidence the WI-3184 revert depends on. Live MemBase probe shows the 10 specs already at `status=implemented` (the prior remediation_006 revert landed) so WI-3184's eventual proposal will need to disambiguate "revert from verified to implemented" against the current state. WI-3183's inventory is the disambiguating evidence.
- `bridge/spec-hygiene-spa-remediation-006.md` (VERIFIED 2026-04-15) - referenced by WI-3184 description as Option A source.
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md` - referenced by WI-3184 description; informs methodology of this slice's inventory.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 - AUQ-resolved batch authorization).

No new owner decision required for this slice's read-only investigation. If Codex GO is granted, implementation produces (a) inventory report and (b) DA closure entry; both routes through standard formal-artifact-approval packet for the DA insert and standard bridge VERIFIED for the inventory file.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is **not** a bulk operation against the standing backlog or any MemBase table. It is a single investigation deliverable producing **one** inventory file (`independent-progress-assessments/spec-hygiene/S350-spa-cluster-test-id-inventory.md`) plus **one** Deliberation Archive entry (closure record citing this inventory). The deterministic inventory script (`scripts/audit_spa_cluster_test_id_inventory.py`) is regenerable evidence, not a mutating CLI. The implementation does not insert, update, or version any spec, test, work_item, or bulk-create deliberation rows beyond the single closure entry. The single closure entry uses the formal-artifact-approval pathway per `GOV-ARTIFACT-APPROVAL-001`. The sibling status-revert WI-3184 is filed as a separate proposal under its own bridge thread and is the only spec-status mutation in the WI-3183/WI-3184 pair.

Evidence-pattern tokens: `inventory`, `formal-artifact-approval`.

## SPA Cluster Inventory Pre-Read

The 10 affected SPEC IDs and current state (from live MemBase probe, 2026-05-14):

| Spec ID | Latest Version | Status | Latest-Version Tests Linked |
|---------|----------------|--------|-----------------------------|
| SPEC-1816 | v4 | implemented | 0 |
| SPEC-1818 | v5 | implemented | 0 |
| SPEC-1819 | v4 | implemented | 0 |
| SPEC-1820 | v4 | implemented | 0 |
| SPEC-1821 | v4 | implemented | 0 |
| SPEC-1822 | v4 | implemented | 0 |
| SPEC-1823 | v4 | implemented | 0 |
| SPEC-1824 | v4 | implemented | 0 |
| SPEC-1826 | v4 | implemented | 0 |
| SPEC-1827 | v4 | implemented | 0 |

Historical test IDs recycled (per `bridge/spec-hygiene-spa-investigation-001..008.md` and live MemBase probe): TEST-10481..TEST-10499 and TEST-10503..TEST-10506 (23 IDs). At v1 each row carried `spec_id` in the SPA set; at v2 (session S200) the same row was re-versioned with `spec_id='SPEC-1837'` (Log Retention) and the test content rewritten for Log Retention assertions. Per ADR-0001 append-only versioning, latest-version state is canonical; the SPA specs therefore have 0 linked test rows in current state.

## Requirement Sufficiency

Existing requirements sufficient. WI-3183 (description + `source_spec_id=SPEC-1816`) is the governing work item; the 10 SPA specs (cited above) are the requirement surface; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` is the governing constraint that surfaced the defect. No new or revised requirement is required for this investigation/closure slice.

## Investigation Methodology

The deterministic resolver `scripts/audit_spa_cluster_test_id_inventory.py` accepts no arguments and produces a stable, idempotent inventory:

1. **Spec enumeration**: For each of the 10 spec_ids in the SPA set, query `SELECT id, MAX(version), status FROM specifications WHERE id=? GROUP BY id` to resolve the latest-version row.
2. **Test resolution per spec**: Use the latest-version CTE pattern
   ```sql
   WITH latest AS (SELECT id, MAX(version) AS mv FROM tests GROUP BY id)
   SELECT t.id, t.version, t.spec_id, t.title, t.test_file, t.test_function, t.last_result
   FROM tests t JOIN latest l ON l.id=t.id AND l.mv=t.version
   WHERE t.spec_id=?
   ```
   to enumerate tests currently bound to each SPA spec (latest-version semantics).
3. **Historical recycled-ID enumeration**: For each of TEST-10481..TEST-10499 and TEST-10503..TEST-10506, query all versions:
   `SELECT id, version, spec_id, title FROM tests WHERE id=? ORDER BY version` and record the v1 -> v2 spec_id transition (SPA spec -> SPEC-1837).

4. **Classification per spec** (four-state taxonomy, deterministic):
   - `placeholder_test_id_unresolved` - spec cites or historically cited test_ids whose latest version has `spec_id != this_spec_id` (i.e., recycled-away).
   - `real_test_linked_pass` - latest-version test with `spec_id=this_spec_id` exists AND `last_result='pass'` AND `test_file IS NOT NULL`.
   - `real_test_linked_fail` - latest-version test with `spec_id=this_spec_id` exists AND `last_result != 'pass'`.
   - `no_test_id_field` - no latest-version test row references this spec_id at all.

   Live probe shows all 10 SPA specs classify as `placeholder_test_id_unresolved` (each has v1 historical tests now recycled to SPEC-1837) overlapping with `no_test_id_field` (0 latest-version rows bound). Classification rule precedence: if BOTH conditions hold (the SPA case), classification is reported as `placeholder_test_id_unresolved` with a `no_current_linkage: true` flag.

5. **Output shape**: A single markdown file at `independent-progress-assessments/spec-hygiene/S350-spa-cluster-test-id-inventory.md` with:
   - Header: WI-3183 source, S350 session, generation timestamp, generating commit SHA, source query text.
   - Per-spec section: spec_id, latest version, status, classification, list of historical recycled test_ids with their v1 spec_id and v2 spec_id.
   - Closure summary: total rows classified per category, list of recycled test IDs, recommended downstream action (cite WI-3184 revert).

6. **Idempotence**: The script is regenerable; rerunning produces byte-identical output (deterministic ordering by spec_id then test_id; timestamps emitted as a single "generated_at" header field that callers can diff-strip).

## Deliverables

- **Inventory file**: `independent-progress-assessments/spec-hygiene/S350-spa-cluster-test-id-inventory.md` - per-spec classification, recycled-ID transitions, closure summary.
- **Audit script**: `scripts/audit_spa_cluster_test_id_inventory.py` - deterministic CLI emitting the inventory file. Read-only against `groundtruth.db`.
- **Test file**: `platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py` - regression tests covering the four classification rules, idempotence, output reproducibility, and per-spec resolver correctness.
- **Deliberation Archive closure entry**: A single DA insert (via formal-artifact-approval packet) titled "SPA cluster test-ID investigation closure (WI-3183 S350)" with `source_type='prime_builder_investigation'`, `outcome='closure_with_evidence'`, and `body` citing the inventory file path, the 10 spec IDs, the 23 recycled test IDs, and the recommended downstream action.

The classification mapping is:
```
placeholder_test_id_unresolved  -> spec's historical test_ids exist but were recycled away (spec_id != this_spec)
real_test_linked_pass           -> latest-version test row spec_id matches AND result=pass AND test_file present
real_test_linked_fail           -> latest-version test row spec_id matches AND result != pass
no_test_id_field                -> 0 latest-version test rows with spec_id=this_spec
```

## Test Mapping

Specification-to-test mapping per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

1. **TM-1**: `test_resolver_returns_latest_version_per_spec` - verifies methodology step 1 (`MAX(version)` semantics) against fixtures with multi-version spec rows. Maps to `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
2. **TM-2**: `test_resolver_returns_latest_version_per_test_with_recycled_spec_id` - verifies methodology step 2 CTE join correctness against fixtures where TEST-X v1 has spec_id=A and v2 has spec_id=B; resolver must return B. Maps to the 10 SPA spec rows.
3. **TM-3**: `test_classification_placeholder_unresolved` - given fixture where TEST has v1 spec_id=A and v2 spec_id=B, classifier reports `placeholder_test_id_unresolved` for spec A. Maps to SPEC-1816..1824, 1826, 1827.
4. **TM-4**: `test_classification_real_test_linked_pass` - given fixture with latest-version test spec_id=A, result=pass, test_file set, classifier reports `real_test_linked_pass`. Maps to all 10 SPA specs as negative control.
5. **TM-5**: `test_classification_real_test_linked_fail` - given fixture with latest-version test spec_id=A, result=fail, classifier reports `real_test_linked_fail`.
6. **TM-6**: `test_classification_no_test_id_field` - given fixture spec with zero linked tests, classifier reports `no_test_id_field`.
7. **TM-7**: `test_idempotent_run_produces_byte_identical_output` - run audit script twice (mod generated_at header) and assert byte-identical inventory output. Maps to methodology step 6.
8. **TM-8**: `test_inventory_lists_all_ten_spa_specs` - resolver output contains exactly 10 spec_ids (the SPA set). Maps to SPEC-1816..1824, 1826, 1827 enumeration.
9. **TM-9**: `test_inventory_lists_23_recycled_test_ids` - resolver records exactly 23 historical-recycled test_ids (TEST-10481..TEST-10499 + TEST-10503..TEST-10506). Maps to historical-recycling investigation.
10. **TM-10**: `test_audit_trail_completeness` - output includes generation timestamp, commit SHA, source query text, and WI-3183 source citation. Maps to `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
11. **TM-11**: `test_classification_precedence_no_current_linkage_flag` - given a spec where BOTH `placeholder_test_id_unresolved` AND `no_test_id_field` apply, classifier reports `placeholder_test_id_unresolved` with `no_current_linkage=true`. Maps to all 10 SPA specs (real-state).
12. **TM-12**: `test_read_only_against_groundtruth_db` - audit script does not mutate `groundtruth.db` (verify by sha256-before / sha256-after on a snapshot DB). Maps to `## Clause Scope Clarification`.

All 12 tests live at `platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py`. Execution: `pytest platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py -v`.

## Risk and Rollback

- **Risk - DB modification**: Mitigated by TM-12 (sha256 invariance assertion). Audit script opens `groundtruth.db` with read-only intent.
- **Risk - Inventory drift**: If WI-3184 lands between this slice's filing and Codex GO, the spec status state may change. Mitigated by including the generation timestamp in the inventory header so reviewers can date-correlate.
- **Risk - DA closure entry premature**: The DA closure entry cites the inventory as evidence; if the inventory turns out to be wrong, the DA entry can be append-only superseded (`outcome='superseded'` + new closure entry) without rollback of the inventory file (since the inventory is regenerable). Rollback = re-run audit script + file superseding DA entry.
- **Rollback**: This slice has no destructive operations. Rollback = `git rm` the three new files (`scripts/audit_spa_cluster_test_id_inventory.py`, `platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py`, `independent-progress-assessments/spec-hygiene/S350-spa-cluster-test-id-inventory.md`) and (if the DA entry was inserted) append a superseding DA entry citing rollback.

## Acceptance Criteria

1. `scripts/audit_spa_cluster_test_id_inventory.py` runs without error against live `groundtruth.db` and produces the inventory file.
2. All 12 test cases in `platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py` pass.
3. The inventory file contains exactly 10 SPA spec sections and exactly 23 recycled test_id transitions.
4. The DA closure entry is inserted via formal-artifact-approval packet with `source_type='prime_builder_investigation'` and cites the inventory file path.
5. `groundtruth.db` SHA256 is unchanged across an audit-script run (read-only invariant).
6. WI-3183 work_item `resolution_status` may be advanced to `closed_with_evidence` only after the DA entry insert and inventory file land (separately tracked, not in this slice's scope).

## Verification Plan

1. Manual review of inventory file accuracy against live MemBase probe (`SELECT` queries reproducing methodology steps 1-3).
2. Execute `pytest platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py -v` and confirm 12/12 pass.
3. Run audit script twice and confirm byte-identical output (mod generated_at header strip).
4. Verify formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-DELIB-spa-cluster-closure-S350.json` matches the inserted DA row's `body_hash`.
5. Re-query `SELECT COUNT(DISTINCT id) FROM tests t JOIN (SELECT id, MAX(version) mv FROM tests GROUP BY id) l ON l.id=t.id AND l.mv=t.version WHERE t.spec_id IN ('SPEC-1816',...)` and confirm result is 0 (state-of-record unchanged by this read-only slice).
6. Confirm `bridge/INDEX.md` is not touched by this slice (Prime task instruction: do not update INDEX in this filing).

## Applicability Preflight

Embedded result from `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-spa-cluster-test-id-investigation-closure-slice-1 --content-file bridge/gtkb-spa-cluster-test-id-investigation-closure-slice-1-001.md`:

- packet_hash: `sha256:225da76c278dbb8e802f181ea5217dcd99b6e7232ec2255874f7e3c9daa08675`
- bridge_document_name: `gtkb-spa-cluster-test-id-investigation-closure-slice-1`
- content_source: `pending_content`
- content_file: `bridge/gtkb-spa-cluster-test-id-investigation-closure-slice-1-001.md`
- operative_file: `(none)`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

Clause preflight (`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-spa-cluster-test-id-investigation-closure-slice-1 --content-file bridge/gtkb-spa-cluster-test-id-investigation-closure-slice-1-001.md`) exits 0; 5 must_apply clauses (CLAUSE-IN-ROOT, CLAUSE-INDEX-IS-CANONICAL, CLAUSE-CONCRETE-LINKS, CLAUSE-SPEC-TO-TEST-MAPPING, CLAUSE-VISIBILITY-BULK-OPS) all have satisfying evidence found; 0 blocking gaps.

End of proposal.
