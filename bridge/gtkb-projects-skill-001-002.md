NO-GO

# Loyal Opposition Review - Projects Skill + gt projects Lifecycle Commands

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-13 UTC
Reviewed proposal: `bridge/gtkb-projects-skill-001-001.md`
Verdict: NO-GO

## Claim

The proposal direction is sound and the mandatory bridge preflights pass on the
live indexed file, but the proposal cannot receive GO yet because it omits the
current implementation-start authorization metadata required before Prime
Builder can begin protected implementation work.

This is a narrow blocking NO-GO. The proposal should be revised, not discarded.
The substantive project lifecycle scope, MemBase authority boundary, harness
skill parity direction, and spec-derived test intent are reviewable after the
missing metadata is corrected.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-skill-001
```

Observed:

- packet_hash: `sha256:dece9216a092b84a3870b9e44da0279878798d2da1ca2c972eefe0572b569e8b`
- bridge_document_name: `gtkb-projects-skill-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-projects-skill-001-001.md`
- operative_file: `bridge/gtkb-projects-skill-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-skill-001
```

Observed:

- Bridge id: `gtkb-projects-skill-001`
- Operative file: `bridge\gtkb-projects-skill-001-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched the Deliberation
Archive before review.

Commands:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search 'WI-3259 projects skill gt projects lifecycle' --limit 10 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search 'GTKB-DETERMINISTIC-SERVICES-001 projects work item backlog MemBase' --limit 10 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations list --work-item-id WI-3259 --limit 20
```

Relevant results:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports converting recurring
  deterministic AI procedure into service-mediated infrastructure.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` supports MemBase-backed
  backlog/project authority and reinforces fresh discovery at implementation
  time.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` supports the cross-harness
  Codex parity direction for generated adapters.
- `DELIB-1564` and `DELIB-1565` are useful precedent for canonical Claude skill
  plus generated Codex adapter review and verification.
- `DELIB-1791` is relevant backlog-source review history and reinforces the
  need to avoid creating a second backlog authority.
- No deliberation linked directly to `WI-3259` was found by
  `gt deliberations list --work-item-id WI-3259`.

No prior deliberation found contradicts the proposal's core direction.

## Finding F1 - Implementation-start metadata is missing or not in the accepted form

Severity: P1 governance gate blocker.

Observation:

The proposal requests source, test, configuration, and skill-surface work, but
does not include the implementation-start metadata in the form required by the
current gate.

Evidence:

- `.claude/rules/file-bridge-protocol.md:37` through
  `.claude/rules/file-bridge-protocol.md:48` require proposals for protected
  implementation work to include `target_paths` metadata, a `Requirement
  Sufficiency` subsection with one operative state, and a specification-derived
  verification plan.
- `bridge/gtkb-projects-skill-001-001.md:129` through
  `bridge/gtkb-projects-skill-001-001.md:138` provide a human-readable
  `## Target Paths` list, but not `target_paths: [...]` metadata and not the
  fallback `## Files Expected To Change` section recognized by the authorization
  parser.
- `bridge/gtkb-projects-skill-001-001.md` has no `## Requirement Sufficiency`
  section.
- `bridge/gtkb-projects-skill-001-001.md:140` through
  `bridge/gtkb-projects-skill-001-001.md:171` provide a `## Test Plan`, but the
  implementation authorization parser recognizes `## Specification-Derived
  Verification`, `## Specification-Derived Verification Plan`,
  `## Spec-Derived Test Plan`, or `## Verification Plan`.
- `scripts/implementation_authorization.py:25` through
  `scripts/implementation_authorization.py:28` define the accepted
  `target_paths` metadata pattern.
- `scripts/implementation_authorization.py:143` through
  `scripts/implementation_authorization.py:164` show that the fallback section
  name is `Files Expected To Change`, not `Target Paths`.
- `scripts/implementation_authorization.py:167` through
  `scripts/implementation_authorization.py:185` define the accepted
  `Requirement Sufficiency` and spec-derived verification headings.
- `scripts/implementation_authorization.py:216` through
  `scripts/implementation_authorization.py:228` make those checks part of
  authorization packet creation before implementation can begin.

Parser probe:

```text
target_paths_error: Approved proposal is missing concrete target_paths or Files Expected To Change
has_spec_derived_verification: False
requirement_sufficiency_state: missing
```

Deficiency rationale:

A GO verdict would authorize a proposal that cannot produce the required local
implementation authorization packet. That creates a false bridge state: latest
GO in `bridge/INDEX.md`, but Prime Builder blocked immediately by
`python scripts/implementation_authorization.py begin --bridge-id
gtkb-projects-skill-001`.

Impact:

Prime Builder would either fail closed before implementation, or be tempted to
work around the implementation-start gate. Either outcome undermines the
purpose of the new implementation-start authorization control.

Required action:

Revise the proposal to add the exact gate-readable surfaces before resubmitting:

1. Add `target_paths: [...]` metadata with the concrete in-root files/globs
   authorized for implementation. Use forward slashes for normalized paths.
2. Add `## Requirement Sufficiency` with exactly one operative state. If the
   existing linked requirements are sufficient, state `Existing requirements
   sufficient` and cite the governing requirements.
3. Rename or duplicate the current test plan under `## Specification-Derived
   Verification Plan`, `## Spec-Derived Test Plan`, or `## Verification Plan`
   while preserving the existing spec-to-test mapping.

Decision needed from owner:

None. This is Prime-fixable metadata/section alignment.

## Verified Proposal Claims

- Live `bridge/INDEX.md` showed `gtkb-projects-skill-001` latest status as
  `NEW` at `bridge/gtkb-projects-skill-001-001.md`, actionable for Loyal
  Opposition.
- Durable role resolution: `harness-state/harness-identities.json` maps Codex
  to harness `A`, and `harness-state/role-assignments.json` assigns harness `A`
  both `loyal-opposition` and `prime-builder`; this dispatch carried mode `lo`.
- `python scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-projects-skill-001` returned `preflight_passed: true`,
  `missing_required_specs: []`, and `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-projects-skill-001` returned exit code 0 with `Blocking gaps
  (gate-failing): 0`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:461` through
  `groundtruth-kb/src/groundtruth_kb/cli.py:525` confirm the current `gt
  projects` surface contains `list` and `show`.
- `groundtruth-kb/src/groundtruth_kb/db.py:295` through
  `groundtruth-kb/src/groundtruth_kb/db.py:360` and
  `groundtruth-kb/src/groundtruth_kb/db.py:3584` through
  `groundtruth-kb/src/groundtruth_kb/db.py:3878` confirm the existing MemBase
  project, membership, dependency, and artifact-link tables and methods the
  proposal intends to wrap.
- Bulk-operation visibility evidence was reviewed: the proposal scopes `reorder`
  to membership ordering inside one selected project and says any discovered
  multi-project or bulk work-item operation must split out or produce a dry-run
  inventory artifact, a review packet, and a `DECISION DEFERRED` marker before
  any apply path.
- `WI-3259` exists in MemBase and names the requested eight verbs:
  create/show/list/update/add-item/reorder/retire/link-bridge.
- `.claude/skills/projects/SKILL.md`, `.codex/skills/projects/SKILL.md`,
  `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, and
  `platform_tests/scripts/test_projects_cli.py` are absent before
  implementation, matching the proposal baseline.

## Required Revision

File `bridge/gtkb-projects-skill-001-003.md` as `REVISED` after adding the
gate-readable implementation-start metadata and section headings listed in F1.
After that revision, this proposal is likely reviewable for GO without changing
the core implementation scope.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
