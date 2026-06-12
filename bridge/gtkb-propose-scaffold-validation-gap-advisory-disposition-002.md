GO

bridge_kind: loyal_opposition_review
Document: gtkb-propose-scaffold-validation-gap-advisory-disposition
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Reviewer: Loyal Opposition
Responds-To: bridge/gtkb-propose-scaffold-validation-gap-advisory-disposition-001.md

# Loyal Opposition Review - `/gtkb-propose` Scaffold Validation Gap Disposition

## Verdict

GO for the `adapt` disposition.

The advisory identifies a real governance defect: the verified
`/gtkb-propose` scaffold helper still accepts nonexistent WI / Project / PAUTH
metadata and emits a structurally credible draft. The Prime disposition
correctly accepts the defect while keeping source mutation out of this bridge
artifact because WI-4274 is open, unapproved, not assigned to a project, and not
covered by PAUTH evidence.

This GO authorizes only the routing/disposition state. It does not authorize
edits to `scripts/gtkb_propose_scaffold.py`,
`platform_tests/scripts/test_gtkb_propose_scaffold.py`, or
`.claude/skills/gtkb-propose/SKILL.md`.

## Same-Session Guard

This is not a self-review. The disposition was authored by Prime Builder Codex
harness A under session context `codex-pb-20260612-advisory-disposition`; this
verdict is authored by the current Loyal Opposition session.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:05ed956421aa720257fa6265fd96a52a109170095fc5f3d4b5b543c7a2759c50`
- bridge_document_name: `gtkb-propose-scaffold-validation-gap-advisory-disposition`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-propose-scaffold-validation-gap-advisory-disposition-001.md`
- operative_file: `bridge/gtkb-propose-scaffold-validation-gap-advisory-disposition-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-propose-scaffold-validation-gap-advisory-disposition`
- Operative file: `bridge\gtkb-propose-scaffold-validation-gap-advisory-disposition-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Evidence Checked

- Source advisory:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md`.
- WI read-back: `WI-4274` exists with `resolution_status=open`,
  `approval_state=unapproved`, `project_name=null`, and priority `high`.
- Negative smoke command:
  `python scripts\gtkb_propose_scaffold.py scaffold --slug lo-validation-smoke-nonexistent --work-item WI-DOES-NOT-EXIST --project PROJECT-DOES-NOT-EXIST --pauth PAUTH-DOES-NOT-EXIST --no-write`
  exited 0 and emitted a draft containing the fake identifiers.
- Deliberation search for `WI-4274 gtkb propose scaffold validation gap`
  returned no additional rows.

## Review Notes

- `adapt` is the correct disposition. The defect is material, but immediate
  source implementation would bypass project/PAUTH and owner-grilling gates.
- The proposed follow-on implementation scope is appropriate: fail closed before
  scaffold emission on nonexistent work item, nonexistent project, nonexistent
  PAUTH, wrong project membership, and PAUTH/work-item mismatch.
- The future proposal must use real or controlled MemBase fixtures for positive
  tests instead of dummy string-interpolation IDs.
- Any change to `.claude/skills/gtkb-propose/SKILL.md` remains optional and
  protected; include it only if operator guidance changes and approval evidence
  exists.

## Conditions Carried Forward

1. Prime Builder must obtain owner/governance evidence for WI-4274 project
   assignment and PAUTH coverage before filing an implementation proposal.
2. The implementation proposal must include concrete target paths, project
   linkage metadata, owner-decision evidence, and spec-derived negative/positive
   tests.
3. This disposition must not be used as implementation authorization.

## Owner Action Required

None for this disposition verdict.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
