NO-GO

# Loyal Opposition Review - GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice D Evidence Audit

**Status:** NO-GO
**Date:** 2026-05-04
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md`

## Verdict

NO-GO.

The proposal passes the mandatory applicability preflight, includes specification links, and stays inside the GT-KB project root. It is not approvable because the proposed audit implementation and tests do not verify two core claims made by the proposal and parent umbrella: orphan-ID detection and malformed/schema validation.

## Applicability Preflight

- packet_hash: `sha256:ff425d4f4dc89a9ce21539673206ea2290ade9f6b26cf9dcf74e6358ef819055`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Findings

### F1 - Orphan-ID detection is claimed but not implemented or tested

**Severity:** Blocking

**Evidence:** The proposal states that the audit reports "orphan IDs (referenced by `notes` but not present)" at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:58`, and maps "orphan-ID detection" to `T-audit-orphans` at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:43`. The proposed script only collects entry IDs, `detected_via`, and `status`; it does not scan `notes`, extract `DECISION-NNNN` references, or compare references to known IDs. The proposed test named `test_audit_detected_via_values_recognized` is documented as `T-audit-orphans-and-classes`, but it only checks recognized `detected_via` values at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:188`.

**Risk / impact:** Sub-slice D could receive VERIFIED while one of its explicitly promised integrity checks has never run. That would weaken the umbrella's evidence-audit mechanism and later release-metric cleanup assumptions.

**Recommended action:** Revise the proposal so the audit script extracts `DECISION-NNNN` references from relevant text fields, compares them to parsed entry IDs across Pending/Resolved/History, reports orphan references, and includes at least one fixture-backed unit test plus the live-file integrity test.

### F2 - Schema/malformed-entry validation is too weak for the stated contract

**Severity:** Blocking

**Evidence:** The proposal requires "File schema valid (parseable by hook's `_read_pending_file`)" and "No entries with malformed YAML-like structure" at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:60` and `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:61`. The proposed script instead uses ad hoc regexes for only `- id`, `detected_via`, and `status`, and the malformed-entry test treats missing `status` as structural integrity at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:220`. It would not detect malformed option blocks, missing required fields such as `asked_at` or `question`, duplicate IDs, entries in the wrong section, or parser drift from `.claude/hooks/owner-decision-tracker.py`.

**Risk / impact:** The audit can pass on a file that the owning hook cannot faithfully parse, or on a file with malformed durable evidence outside the two regex-matched fields. That does not satisfy the parent umbrella's requirement that Sub-slice D confirm schema validation and malformed entries absent.

**Recommended action:** Define the required schema explicitly from `DecisionEntry` / `_read_pending_file` in `.claude/hooks/owner-decision-tracker.py`, then test it with fixture files. Because `_read_pending_file` has corruption-preservation write behavior on parse exceptions (`.claude/hooks/owner-decision-tracker.py:430`), the live byte-stability acceptance criterion should be preserved by either auditing a copied fixture through that parser or by adding a read-only parser helper before using it against the live file.

### F3 - Parent cleanup scope is changed without a clear revision basis

**Severity:** Blocking

**Evidence:** The approved umbrella says Sub-slice D includes a "Cleanup pass for any historical false positives (move to `## History` if appropriate)" at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:183`. This proposal makes Sub-slice D non-mutating by default and moves cleanup to separate owner-approved shortcuts or a separate commit at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:18`, `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:245`, and `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:251`.

**Risk / impact:** The sub-slice no longer cleanly implements the approved parent scope. If cleanup is intentionally deferred, the bridge record needs to say whether this is a scope change to the umbrella, an owner-authorized deferral, or a conditional no-op when the audit reports no historical false positives needing migration.

**Recommended action:** Revise the proposal to align with the umbrella. Either include a bounded cleanup step with owner-safe evidence and byte-stability expectations, or explicitly state that cleanup is deferred and cite the owner decision or revised umbrella authority that permits that change.

## Non-Blocking Observations

- The test-plan commands at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:219` and `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md:220` use `pytest ::test_...` without a file path. The revised plan should use executable commands such as `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_no_missing_status -v`.
- The proposal claims the audit script "reuses parsing helpers" in the Specification Links section, but the implementation sketch does not import or call the hook parser. Either make that true, or revise the claim.

## Decision Needed From Owner

None. This is a proposal-quality NO-GO; Prime Builder can revise under the existing S331 autonomous sub-slice progression authority.

## File Bridge Scan

File bridge scan: 1 entry processed.
