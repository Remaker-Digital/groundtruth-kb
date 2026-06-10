NEW

# Implementation Proposal - MemBase Effective Use Recovery: Next Slice (GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY)

bridge_kind: prime_proposal
Document: gtkb-membase-effective-use-recovery-next-slice
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY

target_paths: ["groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py", "tests/scripts/test_membase_effective_use_audit.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-AUDIT-2026-05-14.md"]

This NEW proposal advances `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` to the next slice: an audit script that scans for MemBase under-utilization patterns flagged in the Codex assessment (`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`).

## Claim

The parent `gtkb-membase-effective-use-recovery-2026-04-29` thread is at GO with 6 non-blocking follow-on conditions. This proposal lands the audit infrastructure that operationalizes those conditions: a script that detects (a) bridge entries referencing VERIFIED state out of sync with MemBase spec status, (b) memory/*.md files duplicating canonical MemBase content, (c) DELIB drafts in chat that should be archived.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-0001` - three-tier memory architecture; MemBase is canonical.
- `GOV-08` - KB is truth.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented framing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - audit surface as policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - originating Codex assessment.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - Codex Loyal Opposition assessment that motivated this WI.
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md` - parent thread GO at -002.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-MEMBASE-EFFECTIVE-USE authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. Parent GO + Codex assessment fully specify the audit scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-MEMBASE-EFFECTIVE-USE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (audit script) + IP-2 (report) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: MemBase under-utilization audit script

`groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py`:

Three audit lenses:
1. **VERIFIED-state mismatch**: Cross-reference bridge VERIFIED threads against MemBase spec status. Flag specs cited as VERIFIED in bridge but still `specified` or `implemented` in MemBase (and vice versa).
2. **Duplicated canonical content**: Scan `memory/*.md` for content patterns that match MemBase spec descriptions (heuristic: 3+ consecutive sentence matches). Flag candidates for migration.
3. **In-chat DELIB drafts**: Scan recent conversation logs (if accessible) for DELIB candidates not archived. (Reduced scope: out-of-band detection via conversation transcript hooks is sibling work; this WI implements the audit lens that downstream consumers can use.)

CLI: `python -m groundtruth_kb membase audit [--out REPORT-PATH]`.

### IP-2: Report

Generate `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-AUDIT-2026-05-14.md` with per-lens findings + summary counts. Note: this consumes the audit script output; the report is a one-shot snapshot, not a recurring artifact.

### IP-3: Tests

Tests verify each lens with fixture data: VERIFIED-mismatch detected, content-duplication candidates found, audit emits expected report schema.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| VERIFIED-mismatch flag fires | `test_audit_flags_verified_mismatch` |
| MemBase-status-current passes | `test_audit_no_flag_when_aligned` |
| Duplicated content candidate detected | `test_audit_detects_content_duplication` |
| Report file emitted with expected schema | `test_audit_report_schema` |
| Audit read-only (no DB writes) | `test_audit_no_db_writes` |
| CLI flag passes through | `test_audit_cli_flag_invocation` |

Run: `python -m pytest tests/scripts/test_membase_effective_use_audit.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Audit report emitted with substantive findings (S350 state).
- Both preflights PASS.

## Risks / Rollback

- Risk: content-duplication heuristic over-flags (false positives). Mitigation: severity is informational; report is reviewer-curated.
- Risk: audit run-time on large MemBase. Mitigation: configurable WI age threshold (default 6 months); indexed queries.
- Rollback: remove script; report stays as historical doc.

## Recommended Commit Type

`feat` - new audit infrastructure. ~150 LOC + tests.
