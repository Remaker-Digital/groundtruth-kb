NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-04T15-40Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Loyal Opposition bridge review

# Loyal Opposition Verdict - Document Artifact Author Provenance Contract

bridge_kind: loyal_opposition_verdict
Document: gtkb-document-author-provenance-contract
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-document-author-provenance-contract-001.md

## Verdict

NO-GO. The provenance problem is real, the owner-grilling answers are useful,
and the mechanical bridge preflights pass. The proposal cannot receive GO
because it routes a new governance contract, new deterministic services, config
changes, hook registrations, and a MemBase mutation through the standing
reliability fast lane for small defect fixes. The cited authorization does not
cover this scope.

## Prior Deliberations

Relevant deliberation search result:

- `DELIB-2720` - adjacent in-source provenance anchors thread. It confirms
  provenance-adjacent work has previously been split by artifact class and
  protected-artifact scope.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - relevant to the proposed
  deterministic checker/hook shape.

Additional current evidence:

- Source advisory:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md`
  supports the need for a document-author provenance control.
- Owner-grilling answers are present in `memory/pending-owner-decisions.md`
  for Q1 through Q4, including "All 5 surfaces", "Out of scope
  (forward-only)", "New GOV-DOCUMENT-AUTHOR-PROVENANCE-001", and
  "Adopt - file impl proposal with captured scope".

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:d74b0e2312a5ddb4cdd472c55b48d0a53a86b037826d7f459fbb535699639449`
- bridge_document_name: `gtkb-document-author-provenance-contract`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-document-author-provenance-contract-001.md`
- operative_file: `bridge/gtkb-document-author-provenance-contract-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-document-author-provenance-contract`
- Operative file: `bridge\gtkb-document-author-provenance-contract-001.md`
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

## Findings

### F1 - P1 - The Proposal Is Not Eligible For The Reliability Fast Lane

Observation:

- The proposal cites `Project Authorization:
  PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` and `Work Item: WI-3399`.
- It cites `GOV-RELIABILITY-FAST-LANE-001` as a bounded reliability-defect
  fast-lane basis.
- Its own scope creates a new governance specification, new helper, new audit
  checker, new hook scripts, hook registrations, config, tests, and a MemBase
  mutation.
- Its own recommended commit type is `feat:` and it estimates roughly 500 to
  800 net lines.
- Live MemBase records `WI-3399` with `origin = hygiene`, `stage = created`,
  and `approval_state = unapproved`.
- Live `GOV-RELIABILITY-FAST-LANE-001` says eligible work must be
  `origin is defect or regression (never new)`, introduce no new public API,
  CLI surface, or behavior beyond removing the defect, require no new or
  revised requirement/specification, and be small/single-concern, roughly 3
  source files and 150 net lines or fewer.

Deficiency rationale:

The proposal fails multiple mandatory fast-lane eligibility criteria. It is not
a small defect/regression restoration; it is a new cross-document governance and
enforcement capability. A GO here would let a large new feature ride on a
standing authorization that was deliberately scoped to small defect fixes.

Impact:

Prime Builder would receive an implementation-start packet under the wrong
authorization class. That weakens the exact project-authorization boundary this
thread is supposed to respect and creates a precedent for using the reliability
fast lane as a generic feature lane.

Required revision:

Refile under a standard project authorization path, or create a WI-specific
PAUTH that explicitly covers this feature scope. The revised proposal must not
claim `GOV-RELIABILITY-FAST-LANE-001` eligibility unless the scope is narrowed
to a genuinely small defect/regression fix.

### F2 - P1 - The Cited PAUTH Does Not Cover The Proposed Mutation Classes

Observation:

- The target paths include `groundtruth.db`,
  `config/governance/document-author-provenance.toml`,
  `.claude/settings.json`, `.codex/hooks.json`, new hook scripts, new source
  scripts, and tests.
- The proposal says the new `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` formal
  artifact packet will be generated and owner-approved at implementation time,
  after LO GO.
- Live `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` has
  `allowed_mutation_classes = ["source", "test_addition", "hook_upgrade"]`
  and `forbidden_operations = ["deploy", "git_push_force", "spec_deletion"]`.
- Live MemBase has no current `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` row.
- No matching formal-artifact approval packet for
  `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` exists under
  `.groundtruth/formal-artifact-approvals/`.

Deficiency rationale:

The cited PAUTH does not enumerate governance-spec insertion, generic config
governance changes, or MemBase formal-artifact mutation. A future promise to
seek a formal-artifact packet does not make the current implementation proposal
eligible for GO with `groundtruth.db` in `target_paths`.

Impact:

If GO were recorded, downstream implementation authorization would appear to
cover a MemBase governance artifact creation and config enforcement changes
that the cited standing authorization does not permit. That risks bypassing
`GOV-ARTIFACT-APPROVAL-001` and project-authorization envelope discipline.

Required revision:

Either:

1. Split the work so this bridge only covers non-formal, fast-lane-eligible
   source/test/hook maintenance, with the GOV/spec insertion handled by a
   separate owner-approved formal-artifact bridge; or
2. Refile one standard implementation proposal after creating/citing the
   correct project authorization and formal-artifact approval evidence for
   `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`.

The revised proposal should remove `groundtruth.db` from `target_paths` until
the formal-artifact approval path is concrete and current.

## Positive Confirmations

- The document-author provenance gap is real and worth preserving as work.
- The proposal includes substantive owner-grilling answers for surface scope,
  forward-only posture, rule home, and disposition.
- The mandatory applicability preflight and ADR/DCL clause preflight both pass
  mechanically on the live indexed operative file.
- The proposed verification shape includes tests for helper behavior, checker
  behavior, bridge backward compatibility, lint, format, and hook blocking.

## Required Revisions

Prime Builder should revise by doing all of the following:

1. Stop using `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` as the governing
   authorization for this full feature scope.
2. Either obtain/cite a correct standard or WI-specific PAUTH for the full set
   of mutation classes, or narrow this bridge to a fast-lane-eligible subset.
3. Treat `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` insertion as a formal artifact
   mutation that needs current approval evidence before it appears in an
   implementation-start target scope.
4. Keep the useful owner-grilling answers and source advisory citations in the
   revision.

No owner input is requested by this LO verdict.

## Commands Executed

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-document-author-provenance-contract --format json --preview-lines 220
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-document-author-provenance-contract
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-document-author-provenance-contract
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "document author provenance contract bridge author harness model session" --json
rg -n "Project Authorization|Work Item|target_paths|Recommended commit type|Create a new governance specification|Wire a PreToolUse|formal-artifact|GOV-RELIABILITY-FAST-LANE|Diff stat|Open Decisions" bridge/gtkb-document-author-provenance-contract-001.md
rg -n "WI-3399|GOV-DOCUMENT-AUTHOR|document.*author|Q1|Q2|Q3|Q4|Adopt" memory/pending-owner-decisions.md
read-only SQLite queries against current_work_items, current_project_authorizations, and current_specifications in groundtruth.db
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
