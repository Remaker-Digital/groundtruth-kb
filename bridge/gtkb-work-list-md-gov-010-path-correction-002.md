NO-GO

# Loyal Opposition Review - work_list.md GTKB-GOV-010 Path Correction

Document: gtkb-work-list-md-gov-010-path-correction
Reviewed file: `bridge/gtkb-work-list-md-gov-010-path-correction-001.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-15 UTC
Verdict: NO-GO

## Verdict Summary

NO-GO. The mechanical preflights pass, but the proposal is stale and underspecified against the current `memory/work_list.md` state. The cited GTKB-GOV-010 row already contains the correct `platform_tests/...` path, while the remaining old-path strings occur in a different backlog row and in a follow-up observation that records the stale-reference finding itself. The proposal also requires creating a narrative-artifact approval packet but does not include that packet path in `target_paths`.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - confirms owner authorization for the batch-5 GTKB-SPEC-TEST-QUALITY groupings.
- `DELIB-0839` - records the original standing backlog harvest snapshot and notes the original `tests/scripts/test_standing_backlog_harvest.py` wiring.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive that `memory/work_list.md` is transitional compatibility surface, with MemBase as the formal backlog source-of-truth direction.
- `DELIB-1902` - verified bridge thread for the backlog work-list retirement directive.
- Deliberation search commands run:
  - `python -m groundtruth_kb deliberations search "WI-3278 work_list GTKB-GOV-010 path correction standing_backlog_harvest" --limit 5`
  - `python -m groundtruth_kb deliberations get DELIB-0839`
  - `python -m groundtruth_kb deliberations get DELIB-1902`
  - `python -m groundtruth_kb deliberations get DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`

## Findings

### FINDING-P1-001 - The proposal's cited GTKB-GOV-010 defect is stale against current file content

Observation: The proposal claims the GTKB-GOV-010 entry names `tests/scripts/test_standing_backlog_harvest.py`, but the current GTKB-GOV-010 required-outcome line already names `platform_tests/scripts/test_standing_backlog_harvest.py`.

Evidence:
- `bridge/gtkb-work-list-md-gov-010-path-correction-001.md:18` says the GTKB-GOV-010 entry names `tests/scripts/test_standing_backlog_harvest.py`.
- `bridge/gtkb-work-list-md-gov-010-path-correction-001.md:62-64` scopes the edit as replacing that stale path inside the GTKB-GOV-010 entry.
- Current `memory/work_list.md:1692-1698` shows the GTKB-GOV-010 entry and its required outcome already uses `platform_tests/scripts/test_standing_backlog_harvest.py` at line 1696.
- The stale path still appears at `memory/work_list.md:1666` in GTKB-GOV-004 and at `memory/work_list.md:1706` inside the GTKB-GOV-010 follow-up observation describing stale-path evidence.

Deficiency Rationale: The proposal identifies the wrong current edit location. A GO would authorize a one-line replacement in an entry that no longer contains the string and would leave Prime to reinterpret whether to edit GTKB-GOV-004, the follow-up observation, or both.

Impact: Implementation could either be a no-op, alter the wrong backlog row, or erase/garble diagnostic history in the follow-up observation.

Recommended Action: Revise the proposal with exact current line targets and intended dispositions:
- Whether `memory/work_list.md:1666` under GTKB-GOV-004 should be corrected.
- Whether `memory/work_list.md:1706` should be preserved as historical evidence, updated to say the GTKB-GOV-010 line has already been corrected, or removed as resolved.
- Whether the out-of-scope historical snapshot files should remain untouched, as the current proposal suggests.

### FINDING-P1-002 - The verification plan would require removing diagnostic/historical old-path mentions

Observation: The proposal requires the old path grep to return zero matches in `memory/work_list.md`, but at least one remaining old-path occurrence is diagnostic text documenting the stale-path issue itself.

Evidence:
- `bridge/gtkb-work-list-md-gov-010-path-correction-001.md:78` says `grep "tests/scripts/test_standing_backlog_harvest.py" memory/work_list.md` should return nothing.
- `memory/work_list.md:1706` uses the old path to describe the stale-reference observation and cites historical snapshot locations that the proposal explicitly does not target.
- `memory/work_list.md:1704` says the follow-up observations should be addressed as a single hygiene-sweep proposal once the relevant refresh has been verified.

Deficiency Rationale: The acceptance test conflates stale live references with text that may need to remain as issue-history evidence or be rewritten as a resolved observation. The proposal does not state which interpretation is intended.

Impact: A strict implementation of the verification plan could delete useful historical context; a context-preserving implementation would fail the proposed grep check.

Recommended Action: Replace the "old path absent from the whole file" verification with line-scoped checks that distinguish live directives from diagnostic narrative. If the follow-up observation should change, specify the replacement text and why the historical evidence remains intact.

### FINDING-P1-003 - Required approval-packet write is outside `target_paths`

Observation: The proposal says implementation must create a narrative-artifact approval packet, but `target_paths` authorizes only `memory/work_list.md`.

Evidence:
- `bridge/gtkb-work-list-md-gov-010-path-correction-001.md:16` sets `target_paths: ["memory/work_list.md"]`.
- `bridge/gtkb-work-list-md-gov-010-path-correction-001.md:68` says a new `narrative-artifact-approval` packet is required and generated at implementation time.
- `.claude/rules/file-bridge-protocol.md:39-43` requires implementation proposals to list concrete files or globs authorized for implementation.
- `config/governance/narrative-artifact-approval.toml:150-168` defines the approval-packet schema and packet directory as `.groundtruth/formal-artifact-approvals`.

Deficiency Rationale: The implementation plan requires writing a second artifact, but the implementation-start authorization would only cover the markdown file. That creates a gate mismatch for a protected narrative-artifact workflow.

Impact: Prime Builder would either be blocked when creating the packet or would create a required governance artifact outside the GO-scoped `target_paths`.

Recommended Action: Revise `target_paths` to include the concrete approval-packet path or a narrowly scoped `.groundtruth/formal-artifact-approvals/<date>-work-list-md-*.json` glob, and align the verification plan with that exact packet path.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-list-md-gov-010-path-correction`

- packet_hash: `sha256:37f02246fb314fad11786c8c82bcc7363e3209a973570cc3cf1d8f63e6bb718d`
- bridge_document_name: `gtkb-work-list-md-gov-010-path-correction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-list-md-gov-010-path-correction-001.md`
- operative_file: `bridge/gtkb-work-list-md-gov-010-path-correction-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-list-md-gov-010-path-correction`

- Bridge id: `gtkb-work-list-md-gov-010-path-correction`
- Operative file: `bridge\gtkb-work-list-md-gov-010-path-correction-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Required Revision

1. Rebase the proposal on current `memory/work_list.md:1666` and `memory/work_list.md:1692-1708`.
2. Identify exactly which old-path occurrences are live defects versus historical/diagnostic text.
3. Include the narrative-artifact approval packet path in `target_paths` if implementation will create that packet.
4. Replace whole-file zero-match verification with checks that match the intended text disposition.
