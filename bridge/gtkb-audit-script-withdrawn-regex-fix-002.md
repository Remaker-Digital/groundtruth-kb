NO-GO

# Loyal Opposition Review - audit_standing_backlog_sources.py WITHDRAWN Regex Fix

Document: gtkb-audit-script-withdrawn-regex-fix
Reviewed file: `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-15 UTC
Verdict: NO-GO

## Verdict Summary

NO-GO. The bridge preflights pass, but the proposal is stale against the current repository state. The source file already contains the proposed `WITHDRAWN` and `ADVISORY` status recognition, while the proposed regression-test path and pytest command point at non-existent files. Prime Builder should revise this as a current-state-aware test-only coverage proposal if regression coverage is still needed, or withdraw it if the intended code change already landed elsewhere.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - confirms owner authorization for the batch-5 GTKB-SPEC-TEST-QUALITY groupings, including this work item family.
- Deliberation search command run: `python -m groundtruth_kb deliberations search "WI-3276 audit_standing_backlog_sources WITHDRAWN ADVISORY" --limit 5`.
- No directly relevant prior deliberation was found for this exact parser defect. The closest returned items were unrelated LO-report-backfill/application-boundary review records and do not establish that this stale implementation shape remains current.

## Findings

### FINDING-P1-001 - The claimed source defect no longer exists in the current file

Observation: The proposal says `scripts/audit_standing_backlog_sources.py` still uses `^(NEW|REVISED|GO|NO-GO|VERIFIED):` and proposes changing it to include `WITHDRAWN` and `ADVISORY`.

Evidence:
- `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md:18` states that the current regex excludes `WITHDRAWN`.
- `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md:61` proposes extending the regex to `^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):`.
- Current repo state at `scripts/audit_standing_backlog_sources.py:39` already uses `r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|WITHDRAWN):\s+(bridge/[^\s]+)"`.
- `git diff -- scripts/audit_standing_backlog_sources.py` is empty, so this is not a Loyal Opposition review-side edit or uncommitted drift in that file.

Deficiency Rationale: A GO would approve a source change that is already present. That blurs the bridge audit trail because the eventual implementation report could not honestly show IP-1 as newly implemented under this GO.

Impact: Prime Builder cannot implement the proposal as written without either producing a no-op source diff or rewriting the proposal meaning during implementation.

Recommended Action: Revise the thread to acknowledge current source state. If the remaining need is regression coverage, narrow the proposal to the missing tests and remove the obsolete claim that line 39 lacks `WITHDRAWN`/`ADVISORY`.

### FINDING-P1-002 - The verification plan uses stale/non-existent audit test paths

Observation: The proposal mixes a legacy `tests/scripts/...` target with a `platform_tests/...` target, but neither audit-test file exists, and the only pytest command uses the legacy `tests/scripts/...` path.

Evidence:
- `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md:16` lists both `tests/scripts/test_audit_standing_backlog_sources.py` and `platform_tests/scripts/test_audit_standing_backlog_sources.py` in `target_paths`.
- `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md:77` says to run `python -m pytest tests/scripts/test_audit_standing_backlog_sources.py -v`.
- `Test-Path 'tests/scripts/test_audit_standing_backlog_sources.py'` returned `False`.
- `Test-Path 'platform_tests/scripts/test_audit_standing_backlog_sources.py'` returned `False`.
- Repository search found those paths only inside this proposal, not in the current test tree.

Deficiency Rationale: A proposal may create a new test file, but the verification command must point to the intended current path. Here the command targets the legacy tree and the proposal authorizes two different candidate paths without explaining which one should be created.

Impact: The implementation-start packet and post-implementation verification would be ambiguous. Prime could add tests under one path while the proposal's required command still fails or exercises a different location.

Recommended Action: Revise with a single intended test path under the current platform test layout, update the pytest command to that path, and keep `target_paths` aligned with the file actually created.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-audit-script-withdrawn-regex-fix`

- packet_hash: `sha256:52bf477203eb182c0d1538da29db1e1c91f9a4d94cf4cc0f2b8d61f87c205c6e`
- bridge_document_name: `gtkb-audit-script-withdrawn-regex-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md`
- operative_file: `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md`
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

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-audit-script-withdrawn-regex-fix`

- Bridge id: `gtkb-audit-script-withdrawn-regex-fix`
- Operative file: `bridge\gtkb-audit-script-withdrawn-regex-fix-001.md`
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

1. Reconcile the proposal with current source state at `scripts/audit_standing_backlog_sources.py:39`.
2. Choose one current test target path and remove the stale `tests/scripts/...` command unless a current `tests/` tree is intentionally reintroduced and justified.
3. Make the verification plan executable against the actual target path.
