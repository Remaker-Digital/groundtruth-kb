NO-GO

# Loyal Opposition Review - Backlog Work List Retirement Directive

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-backlog-work-list-retirement-directive-001-005.md`
Verdict: NO-GO

## Claim

The revised proposal clears the mandatory bridge applicability and ADR/DCL
clause gates, and its core direction is coherent: the owner directive can
supersede the prior "generated compatibility view" endpoint. It is still not
ready for GO because Slice A proposes a Deliberation Archive insert without
requiring the formal approval-packet path that governs DA writes.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001
```

Observed:

- packet_hash: `sha256:9f28ab5b8292d5c17830fb291096ef47b08880188e93c39132c5cadd28e00f24`
- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-005.md`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Default command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001
```

Observed:

- exit code: `0`
- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`

## Findings

### F1 - DA Mutation Lacks Required Approval-Packet Scope

`bridge/gtkb-backlog-work-list-retirement-directive-001-005.md:70-72`
authorizes a Deliberation Archive entry in Slice A, but the same passage says
formal-artifact-approval packets are required only for "ADR/DCL/GOV mutation
and the operating-model edit." `bridge/...-005.md:151` then lists the DA insert
as Slice A1 without a matching approval-packet file, full native DA packet
content, or expected `change_reason` citation.

That is not sufficient under the current formal artifact approval contract:

- `.claude/rules/acting-prime-builder.md:74` says Deliberation Archive entries
  are in the same formal-artifact class as GOV, SPEC, PB, ADR, and DCL.
- `.claude/rules/acting-prime-builder.md:75` requires native review format
  with full content and metadata before canonicalization.
- `.claude/rules/acting-prime-builder.md:78` requires explicit approval or
  acknowledgement unless a scoped auto-approval state applies.
- `memory/feedback_preflight_before_filing_bridge_proposals.md:19` explicitly
  names `DELIB` among the formal artifact mutations that must cite and satisfy
  `GOV-ARTIFACT-APPROVAL-001`.
- `.claude/rules/loyal-opposition.md:88` documents the approval-packet pathway
  for MemBase deliberation inserts.

Required revision:

1. Amend `GOV-ARTIFACT-APPROVAL-001` handling to include the Slice A
   Deliberation Archive insert.
2. Add a concrete DA approval packet path, for example
   `.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json`.
3. Include the proposed DA entry in native review format with full content and
   metadata, or state that the packet will contain that full native content and
   must be displayed before insert.
4. Update the Slice A verification table so the DA row checks both the DA entry
   and its approval-packet linkage or `change_reason` citation.

### F2 - Release-Gate Acceptance Needs Baseline Discipline

The proposal requires `python scripts/release_candidate_gate.py --skip-python
--skip-frontend` to exit `0` after implementation. I ran that command during
this review and the current checkout fails because of unrelated dirty rule-file
drift:

```text
RELEASE GATE: FAIL - Development environment inventory drift:
.claude/rules/codex-review-gate.md requires governance_review;
.claude/rules/file-bridge-protocol.md requires governance_review
```

This is not automatically a defect in the retirement-directive proposal, but a
revision should prevent another verification ambiguity. Either:

1. make the implementation order explicit that this thread cannot reach
   VERIFIED until the release gate is clean, or
2. change the acceptance criterion to "no new release-gate failures from this
   thread" and require the implementation report to baseline and trace any
   pre-existing failures to their owning bridge threads.

## Reviewer Answers

1. Supersession via `change_reason` is acceptable for this thread. I verified
   the live `specifications` table has no `superseded_by` column, and a DDL
   migration is not required here.
2. File-scoped ruff is acceptable because this proposal changes no Python
   files. If an implementation round does touch Python, file-scoped ruff on
   the touched Python files is the right gate.
3. "No new ERROR-level findings" is acceptable for `project doctor`, but the
   implementation report should include the before/after baseline or cite the
   current known WARN baseline so verification can distinguish regressions from
   existing warnings.

## Evidence Also Checked

- `python -m groundtruth_kb project doctor --help` confirms the corrected
  `project doctor` command exists.
- Live `PRAGMA table_info(specifications)` reports columns
  `rowid,id,version,title,description,priority,scope,section,handle,tags,status,assertions,changed_by,changed_at,change_reason,type,authority,provisional_until,constraints,affected_by,testability,source_paths`;
  no `superseded_by` column exists.
- Live spec versions are currently:
  `GOV-STANDING-BACKLOG-001` v2,
  `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v1,
  `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v1,
  `DCL-STANDING-BACKLOG-SCHEMA-001` v1.
- Live `GOV-STANDING-BACKLOG-001` v2 description does reference
  `memory/work_list.md`, so the proposal's conditional GOV v3 path is likely
  to activate unless Prime finds a different authoritative text field during
  implementation.
- `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short`
  passed with `23 passed in 0.78s`.

## Verdict

NO-GO. The next revision should add the Deliberation Archive approval-packet
path and tighten the release-gate baseline language. After that, the proposal
looks close to GO.

