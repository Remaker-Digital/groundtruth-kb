NEW

# Implementation Proposal - Critical Quality + Consistency Audit of Early-Project Specs (WI-3247)

bridge_kind: prime_proposal
Document: gtkb-early-project-specs-quality-audit
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SPEC-TEST-QUALITY-SPEC-TEST-QUALITY-BATCH
Project: PROJECT-GTKB-SPEC-TEST-QUALITY
Work Item: WI-3247

target_paths: ["scripts/early_project_spec_audit.py", "tests/scripts/test_early_project_spec_audit.py", "independent-progress-assessments/EARLY-PROJECT-SPECS-AUDIT-REPORT.md"]

This NEW proposal lands a one-shot critical quality + consistency audit of early-project specifications in MemBase. Per WI-3247, early specs were authored before current quality standards (GOV-18 assertion quality, GOV-09 input classification, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001) and may carry stale or contradictory content.

## Claim

A read-only audit script enumerates specs older than 2026-04-01 (configurable threshold), checks each against current quality criteria (assertions present, source paths, test linkage, no contradictions with later-version specs), and emits a triage report classifying each spec into: healthy / needs-update / contradicts-newer / candidate-for-retirement.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-18` - assertion quality standard the audit measures against.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping the audit checks.
- `GOV-09` - input classification rule that affects spec phrasing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `GOV-08` - KB is truth; audit operates within KB.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `GOV-STANDING-BACKLOG-001` - WI-3247 tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SPEC-TEST-QUALITY authorization including WI-3247.

## Requirement Sufficiency

Existing requirements sufficient. WI-3247 description is the operative scope.

## Clause Scope Clarification (Not a Bulk Operation)

Audit IS a read-side bulk-style operation (it inspects many specs) but it is NOT a bulk mutation. Read-only by design. Outputs a triage report; remediation lands in follow-on per-spec work. Per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json` WI-3247 is a member of PROJECT-GTKB-SPEC-TEST-QUALITY. Review-packet inventory: IP-1 (audit script) + IP-2 (report) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Audit script

`scripts/early_project_spec_audit.py`:

For each spec where v1 `changed_at < threshold` (default 2026-04-01):
1. Load current version.
2. Check: has any assertion? (GOV-18 quality)
3. Check: has any test in `tests` table linked to it? (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001)
4. Check: has source_paths set?
5. Check: contradicts any newer spec (heuristic: title/handle overlap with newer spec; flag for review)
6. Emit per-spec row: id, version, age_days, has_assertions, has_tests, has_source_paths, contradicts_with, classification.

CLI: `python scripts/early_project_spec_audit.py [--threshold YYYY-MM-DD] [--out REPORT-PATH]`.

### IP-2: Report

Generate `independent-progress-assessments/EARLY-PROJECT-SPECS-AUDIT-REPORT.md` with the per-spec table + summary counts by classification.

### IP-3: Tests

Tests: fixture specs (one each: healthy, needs-update, contradicting-newer, retirement-candidate) and assert classification + report output.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Healthy spec classified correctly | `test_audit_classifies_healthy` |
| Spec without assertions flagged | `test_audit_flags_missing_assertions` |
| Spec without linked tests flagged | `test_audit_flags_missing_tests` |
| Contradicting-newer spec flagged | `test_audit_flags_contradicting_newer` |
| Report file emitted with expected structure | `test_audit_emits_report_structure` |
| Threshold parameter respected | `test_audit_threshold_parameter` |
| Read-only (no DB writes) | `test_audit_makes_no_db_writes` |

Run: `python -m pytest tests/scripts/test_early_project_spec_audit.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 7 tests PASS.
- Audit report contains entries for >= 50 specs (estimated; depends on actual age distribution).
- Both preflights PASS.

## Risks / Rollback

- Risk: heuristic "contradicts newer" may over-flag. Mitigation: classification is informational, not blocking; owner reviews report before any spec retirement.
- Risk: audit run-time on large MemBase. Mitigation: targeted threshold + indexed query; expected sub-minute.
- Rollback: remove script; report stays as historical doc.

## Recommended Commit Type

`feat` - new audit tool + report. ~150 LOC.
