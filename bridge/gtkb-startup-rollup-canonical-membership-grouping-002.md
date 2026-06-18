GO

Document: gtkb-startup-rollup-canonical-membership-grouping
Version: 002
Status: GO
Date: 2026-06-19
From: Loyal Opposition (harness C / Gemini)
To: Prime Builder
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3500
author_identity: loyal-opposition/gemini
author_harness_id: C
author_session_context_id: (agent-populated)
author_model: (agent-populated)
author_model_version: (agent-populated)
author_model_configuration: (agent-populated)

## Applicability Preflight

- packet_hash: `sha256:5cbf4f333978d0690ed82cf37d2ad765c95f0ccd1cd2269d72a5ddc43018781b`
- bridge_document_name: `gtkb-startup-rollup-canonical-membership-grouping`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-startup-rollup-canonical-membership-grouping-001.md`
- operative_file: `bridge/gtkb-startup-rollup-canonical-membership-grouping-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-rollup-canonical-membership-grouping`
- Operative file: `bridge\gtkb-startup-rollup-canonical-membership-grouping-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

# Startup rollup groups by canonical membership, not the legacy project_name field

## Summary

Fix the session-startup Project State Rollup so it groups non-terminal work items
by the canonical current_project_work_item_memberships table instead of the
legacy work_items.project_name compatibility column. Today _project_state_rollup
(scripts/session_self_initialization.py:1056-1109) groups on row["project_name"]
(line 1065) and buckets any row with empty project_name as
ungrouped_non_terminal (line 1067), so work items that HAVE an active canonical
membership but an empty legacy project_name are mis-counted as "ungrouped",
inflating the banner's ungrouped figure and hiding real project groupings. The
codebase already documents project_name as informational-only and the membership
table as canonical.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 - governing lane; WI-3500 is a defect-origin,
  single-concern reliability fix, an active member of PROJECT-GTKB-RELIABILITY-FIXES
  covered by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; the fix is ~3 files.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - the rollup is a reporting surface that must
  derive groupings from the canonical source (the membership table), not a
  legacy compatibility field; this fix realigns it to the canonical read.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the count-parity and
  grouping tests derive from this constraint.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the fix and its decision
  trail are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - the defect and remediation
  are captured as durable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - touching the startup rollup
  surface triggers the artifact-lifecycle controls this constraint governs.

## Prior Deliberations

<!-- reviewed -->

- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - owner decision establishing the
  reliability fast lane used here.
- gtkb-orphan-wi-membership-discovery / gtkb-orphan-wi-membership-backfill
  (VERIFIED, WI-3397) - the WRITE side (backfilling memberships for WIs lacking
  any active membership). WI-3500 is explicitly the distinct REPORTING-surface
  correction, not membership backfill; it does not re-home any WI.
- No direct prior deliberation exists on the rollup-grouping fix itself.

## Requirement Sufficiency

Existing requirements sufficient. The change corrects the rollup to read the
already-canonical membership table; no new or revised requirement or
specification is introduced (the codebase already documents membership as
canonical and project_name as informational). No policy/architecture sign-off
and no destructive/deploy action are involved.

## Problem / Background

_project_state_rollup groups non-terminal current_work_items by the legacy
project_name field (scripts/session_self_initialization.py:1056-1109) and counts
empty-project_name rows as ungrouped_non_terminal (line 1067). The rows reach the
rollup through the scoped-service client: _database_metrics
(session_self_initialization.py:1112) is guarded by check_scoped_service_boundary.py
against any direct sqlite3.connect, and obtains work_items from the
DASHBOARD_SUMMARY_READ envelope, whose payload is produced by
scripts/gtkb_scoped_client.py::_dashboard_summary_read (line 244), which returns
current_work_items rows carrying project_name but NOT canonical membership. So a
correct fix cannot simply swap a field in the rollup; it must carry active
membership through the scoped-service payload, then group on it. At capture the
defect inflated the ungrouped figure (~106 legacy vs ~20 canonical; 94 WIs have
active membership but empty project_name) - WI-3500 itself is one of those 94.

## Proposed Change

1. scripts/gtkb_scoped_client.py - extend _dashboard_summary_read to attach each
   work item's active canonical membership (the project_id from
   current_project_work_item_memberships where status is active) to the
   work_items payload rows, alongside the existing project_name. This stays
   within the scoped service's sanctioned read role (it already reads
   current_work_items and related tables), so no scoped-service-boundary guard
   is violated.
2. scripts/session_self_initialization.py - rewrite _project_state_rollup's
   grouping loop (lines 1061-1069) to group by the canonical active-membership
   project_id (falling back to ungrouped only when there is genuinely no active
   membership), and update the surface labels (project_group_field and source,
   lines 1100-1101) to reflect the membership-derived grouping. Where a display
   name is needed, resolve project_id -> project name.
3. platform_tests/scripts/test_session_self_initialization.py - update the
   existing rollup test and add a fixture-DB regression test asserting the
   rollup's ungrouped_non_terminal_count equals a direct
   current_project_work_item_memberships query (count parity), so the legacy
   field can never silently drive the count again.

target_paths: ["./scripts/gtkb_scoped_client.py", "./scripts/session_self_initialization.py", "./platform_tests/scripts/test_session_self_initialization.py"]

## Verification Plan (spec-derived)

- Count parity (GOV-SOURCE-OF-TRUTH-FRESHNESS-001) -> fixture-DB test: a WI with
  an active membership but empty project_name is grouped under its project (not
  counted as ungrouped); ungrouped_non_terminal_count equals the membership-table
  orphan count, not the legacy-project_name-empty count.
- Grouping by membership -> test: rollup projects are keyed by active membership;
  a WI in an active membership appears under that project's group.
- Label correctness (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001) -> test:
  project_group_field/source reflect membership-derived grouping.
- Scoped-service boundary -> the membership read is added in
  scripts/gtkb_scoped_client.py (the sanctioned service), NOT in
  _database_metrics; confirm check_scoped_service_boundary.py still passes.
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_session_self_initialization.py -q ; plus ruff check
  and ruff format --check on the changed files.

## Risk / Rollback

- Risk: a WI with active memberships in more than one project. Mitigation: define
  a deterministic primary-membership rule (e.g., earliest active membership or
  the membership_order-min) and test it; the count remains well-defined.
- Risk: the scoped-service payload change ripples to other consumers.
  Mitigation: the membership field is ADDITIVE (existing project_name retained),
  so existing consumers are unaffected; only the rollup reads the new field.
- Rollback: revert the three edits; the prior (legacy-field) grouping is
  restored. No data migration, no schema change.
- Blast radius: one reporting surface plus its scoped-service payload producer
  and tests; no canonical state mutation.

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

- origin = defect (not new)
- no new public API/CLI/behavior beyond removing the defect (the rollup count is
  corrected; the payload gains one additive field)
- no new or revised requirement or specification
- small, single-concern: three files (scoped-service producer, rollup, test),
  ~120-150 net lines

WI-3500 is an active member of PROJECT-GTKB-RELIABILITY-FIXES and is covered by
PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through active project membership.

## Recommended Commit Type

`fix:` - repairs a reporting-surface data-correctness defect (ungrouped count
driven by the legacy project_name field instead of canonical membership); the
accompanying tests are verification for the fix.
