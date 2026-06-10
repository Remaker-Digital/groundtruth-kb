REVISED

# Implementation Proposal - Standing Backlog Harvest/Reconciliation Audit Maintenance (GTKB-GOV-010)

bridge_kind: prime_proposal
Document: gtkb-standing-backlog-harvest-audit-maintenance
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-010

target_paths: ["scripts/audit_standing_backlog_sources.py", "scripts/release_candidate_gate.py", "platform_tests/scripts/test_standing_backlog_harvest.py", "platform_tests/scripts/test_release_candidate_gate.py", "groundtruth-kb/tests/test_doctor_standing_backlog.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-14.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py"]

This REVISED proposal advances the standing backlog harvest/reconciliation audit toward release-gate integration. Currently maintained as a hand-curated audit; the WI calls for promoting it to a first-class doctor check.

## Revision Notes

This `-003` revision addresses both findings in the `-002` NO-GO verdict:

- **F1 (P1 — `target_paths` omits files the proposal requires Prime Builder to
  edit):** Resolved. `target_paths` now includes `scripts/release_candidate_gate.py`
  (IP-3 explicitly edits it to wire the new doctor-health check) and the
  release-gate regression target `platform_tests/scripts/test_release_candidate_gate.py`.
  The nonexistent test path `groundtruth-kb/tests/project/test_doctor_standing_backlog.py`
  named in the `-001` verification command is replaced with the real planned
  path `groundtruth-kb/tests/test_doctor_standing_backlog.py` — a NEW test file
  created under the upstream `groundtruth-kb/tests/` directory, the directory
  that already holds doctor tests (`groundtruth-kb/tests/test_doctor.py`,
  confirmed present and run by the release gate at
  `scripts/release_candidate_gate.py:364`). The `-001` verification command is
  corrected accordingly below.
- **F2 (P2 — release-gate scope is ambiguous relative to the existing harvest
  test):** Resolved. IP-3 below now states the exact new release-gate behavior:
  a new `_check_standing_backlog_health()` function is added to
  `scripts/release_candidate_gate.py` and invoked from `main()`; it is a
  distinct new lane that does NOT replace the existing
  `platform_tests/scripts/test_standing_backlog_harvest.py` pytest entry
  (confirmed at `scripts/release_candidate_gate.py:327`). The preserved
  legacy harvest-test lane and the new doctor-health check lane are
  enumerated separately, and a regression test
  (`test_release_gate_invokes_standing_backlog_health` in
  `platform_tests/scripts/test_release_candidate_gate.py`) proves the new
  doctor check is called, not only the legacy harvest test.

In addition, the three advisory specs the `-002` applicability preflight
flagged as missing (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`)
are now cited in `## Specification Links` below.

## Claim

Two-part advance: (1) refresh the harvest audit with current data for the S350 timeframe; (2) promote the audit logic into a first-class `gt project doctor` check that runs automatically as part of release-readiness evaluation, added as a NEW release-gate lane alongside (not replacing) the existing harvest test.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. The two `groundtruth-kb/...` paths are within the in-root upstream package directory.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - source spec for backlog governance.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness integration.
- `GOV-ARTIFACT-APPROVAL-001` - audit output is governance evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - doctor surface integration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the audit, doctor check, and release-gate lane form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the WI triggers this implementation proposal and its spec-derived tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the audit is captured as governed work with a bridge artifact and spec-derived tests.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-0839` - prior standing backlog harvest snapshot and reconciliation obligations; confirms the original audit/report/test surface (surfaced by Codex `-002` deliberation search).
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive for structured backlog authority (surfaced by Codex `-002` deliberation search).

No prior deliberation found a waiver for incomplete implementation
authorization scope; this revision instead corrects `target_paths` to cover
the full implementation touchpoint set.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ADOPTER-EXPERIENCE authorization (`PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH`) including this WI (`GTKB-GOV-010`).

## Requirement Sufficiency

Existing requirements sufficient. The WI description (`GTKB-GOV-010`) specifies
the maintenance + promotion scope, and `GOV-STANDING-BACKLOG-001` /
`GOV-RELEASE-READINESS-GOVERNED-TESTING-001` govern the backlog-health and
release-gate behavior. No new or revised requirement or specification is
created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. It performs no batch resolve/promote/retire across the backlog. Review-packet inventory: IP-1 (refresh report) + IP-2 (doctor check) + IP-3 (release-gate lane) + IP-4 (tests), a single thread. The applicable evidence pattern is a single-WI implementation proposal with formal-artifact-approval discipline preserved unchanged.

## Bridge INDEX Update Evidence

`-003` REVISED line prepended above the `-002` NO-GO line under the `Document: gtkb-standing-backlog-harvest-audit-maintenance` block; prior `-001`/`-002` versions preserved unchanged per the append-only bridge audit trail.

## Files Expected To Change

- `scripts/audit_standing_backlog_sources.py` — harvest-audit refresh logic (IP-1).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — new `check_standing_backlog_health()` doctor check (IP-2).
- `scripts/release_candidate_gate.py` — new `_check_standing_backlog_health()` release-gate lane invoking the doctor check from `main()` (IP-3).
- `groundtruth-kb/tests/test_doctor_standing_backlog.py` — NEW test file; spec-derived tests for the doctor check (IP-4).
- `platform_tests/scripts/test_release_candidate_gate.py` — release-gate regression proving the new lane is invoked (IP-4).
- `platform_tests/scripts/test_standing_backlog_harvest.py` — harvest-refresh test updates as needed (IP-4).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-14.md` — refreshed harvest report (IP-1).

## Proposed Scope

### IP-1: Refresh harvest audit

Rerun `scripts/audit_standing_backlog_sources.py` for S350-current data and
update `platform_tests/scripts/test_standing_backlog_harvest.py` as needed.
Write the report at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-14.md`
enumerating:
- bridge status counts (cross-reference INDEX.md)
- MemBase open work_items counts (with project authorization status breakdown)
- release-readiness blockers (cite specific GO-blocking WIs)
- independent-progress-assessment unresolved entries

### IP-2: Promote to doctor check

In `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, add
`check_standing_backlog_health()` that:
1. Queries MemBase for open work_items not in any active authorization.
2. Parses `bridge/INDEX.md` for entries with stale NO-GO (older than a
   configurable threshold).
3. Emits per-finding severity: orphaned-WI = WARN, stale-NO-GO = WARN,
   missing-evidence = FAIL.

This is the first-class doctor check. It is distinct from the legacy
hand-curated harvest audit and from the legacy harvest test.

### IP-3: Release-gate integration (exact new behavior per F2)

The new doctor check is wired into the release gate as a NEW lane that does
NOT replace any existing lane:

1. **New function:** add `_check_standing_backlog_health()` to
   `scripts/release_candidate_gate.py`, following the existing `_check_*`
   function pattern (e.g. `_check_project_resource_registry`,
   `_check_dev_environment_inventory`). The function invokes the
   `check_standing_backlog_health()` doctor check from IP-2 and raises
   `GateFailure` when the doctor check returns a FAIL-severity finding
   (missing-evidence); WARN-severity findings are reported but do not fail
   the gate.
2. **New invocation point:** call `_check_standing_backlog_health()` from
   `main()`, placed after `_check_project_resource_registry()` and before
   `_check_dev_environment_inventory(...)`. It runs unconditionally with the
   other Python/governance `_check_*` lanes.
3. **Preserved legacy lane (NOT modified):** the existing pytest entry
   `platform_tests/scripts/test_standing_backlog_harvest.py` at
   `scripts/release_candidate_gate.py:327` remains in the `_python_gates()`
   pytest lane unchanged. It exercises the harvest-refresh test surface and
   is a separate lane from the new doctor-health check.

The new release-gate behavior is therefore: the release gate gains one new
governance `_check_*` lane (`_check_standing_backlog_health`) invoked from
`main()`, while the legacy harvest pytest entry is preserved. "Release-gate
input" is satisfied by the new check, not by the legacy test alone.

### IP-4: Tests

- `groundtruth-kb/tests/test_doctor_standing_backlog.py` (NEW): spec-derived
  tests for `check_standing_backlog_health()` — orphaned-WI detection,
  stale-NO-GO detection, severity classification, clean-state-no-findings.
- `platform_tests/scripts/test_release_candidate_gate.py`: a regression test
  `test_release_gate_invokes_standing_backlog_health` asserting that
  `main()` calls `_check_standing_backlog_health()` (e.g. via monkeypatch /
  call-tracking), proving the new doctor check is invoked rather than only
  the legacy harvest test.
- `platform_tests/scripts/test_standing_backlog_harvest.py`: harvest-refresh
  test updates as needed for IP-1.

## Specification-Derived Verification Plan

| Linked specification / behavior | Test |
|---|---|
| `GOV-STANDING-BACKLOG-001` — doctor check finds orphaned WIs | `test_doctor_finds_orphaned_wis` (in `groundtruth-kb/tests/test_doctor_standing_backlog.py`) |
| `GOV-STANDING-BACKLOG-001` — doctor check detects stale NO-GO | `test_doctor_detects_stale_no_go` |
| `GOV-STANDING-BACKLOG-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — severity classification correct | `test_doctor_severity_classification` |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — release gate invokes the new doctor-health check | `test_release_gate_invokes_standing_backlog_health` (in `platform_tests/scripts/test_release_candidate_gate.py`) |
| `GOV-ARTIFACT-APPROVAL-001` — refresh report file emitted | `test_harvest_report_emitted` (in `platform_tests/scripts/test_standing_backlog_harvest.py`) |
| `GOV-STANDING-BACKLOG-001` — clean state reports no findings | `test_clean_state_no_findings` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — all linked specs map to executed tests | the post-implementation report carries this mapping and the executed results forward |

Corrected verification command (replaces the `-001` nonexistent path):

```
python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py platform_tests/scripts/test_release_candidate_gate.py -q --tb=short
python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_doctor_standing_backlog.py -q --tb=short
python -m ruff check .
```

The `groundtruth-kb/tests/...` invocation uses `--rootdir` / `--override-ini`
to match the existing release-gate convention for upstream `groundtruth-kb`
tests (`scripts/release_candidate_gate.py` upstream pytest block).

## Acceptance Criteria

- IP-1 refresh report emitted (timestamped).
- IP-2 `check_standing_backlog_health()` doctor check landed in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
- IP-3: `_check_standing_backlog_health()` added to `scripts/release_candidate_gate.py` and invoked from `main()`; the legacy `test_standing_backlog_harvest.py` pytest entry at line 327 is preserved unchanged.
- IP-4: doctor-check tests pass; `test_release_gate_invokes_standing_backlog_health` proves `main()` calls the new lane.
- Both preflights PASS on the `-003` operative file.

## Risks / Rollback

- Risk: doctor check finding noise on first run (many orphaned WIs from this session's authorization activity). Mitigation: this session's batch-1..5 authorizations cover most prior orphans; baseline should be cleaner than expected. Orphaned-WI is WARN severity, so first-run noise does not fail the gate.
- Risk (addressed by F1): a GO that does not authorize the release-gate edit. Mitigation: `scripts/release_candidate_gate.py` is now in `target_paths`.
- Rollback: remove `_check_standing_backlog_health()` and its `main()` invocation from `scripts/release_candidate_gate.py`; remove `check_standing_backlog_health()` from `doctor.py`; the refresh report stays as a historical doc.

## Recommended Commit Type

`feat` - new doctor surface + new release-gate lane + tests. Net-new capability.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` operative file
after filing the INDEX entry. Outputs are embedded in the `## Applicability
Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

```text
- packet_hash: `sha256:ff82344c1d68240c674ab9311792c5f27a6346db4c144b2b6789c5245199b005`
- bridge_document_name: `gtkb-standing-backlog-harvest-audit-maintenance`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-standing-backlog-harvest-audit-maintenance-003.md`
- operative_file: `bridge/gtkb-standing-backlog-harvest-audit-maintenance-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | blocking | yes | path:groundtruth-kb/src/groundtruth_kb/project/** |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:candidate, content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |
```

## Clause Applicability

```text
- Bridge id: `gtkb-standing-backlog-harvest-audit-maintenance`
- Operative file: `bridge\gtkb-standing-backlog-harvest-audit-maintenance-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | must_apply | yes | blocking | blocking |

Exit 0 = pass.
```

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
