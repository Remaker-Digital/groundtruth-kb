GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-hygiene-sweep-cli-scoping
Version: 003
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-28 UTC
Responds to: `bridge/gtkb-hygiene-sweep-cli-scoping-002.md`
Verdict: GO

# Loyal Opposition Review - Deterministic CLI: gt hygiene sweep Scoping

## Verdict

GO for scoping. This verdict approves the proposed design direction for a future `gt hygiene sweep` deterministic CLI and its follow-on implementation proposal shape. It does not authorize implementation, source/config mutation, or per-slice project authorization.

## Prior Deliberations

Deliberation Archive search was run before review through the repository API:

```text
KnowledgeDB(db_path="groundtruth.db").search_deliberations("hygiene sweep", limit=5)
KnowledgeDB(db_path="groundtruth.db").search_deliberations("deterministic services", limit=5)
```

Relevant records returned:

- `DELIB-2142` - prior verified `gtkb-gov-010-followup-observations-s342` hygiene sweep thread.
- `DELIB-2496` - artifact recorder CLI GO; adjacent deterministic CLI precedent.
- `DELIB-2471`, `DELIB-2470`, `DELIB-2469` - discoverability CLI NO-GO/GO history; relevant precedent for deterministic CLI scope and review cycles.

The proposal also cites `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `DELIB-1473`, `DELIB-2070`, `DELIB-1416`, `DELIB-2142`, `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`, and `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

## Review Notes

### Confirmation - Scoping boundary is clear

Observation: REVISED-2 states that it is a non-mutating scoping proposal, claims no implementation authorization, and lists `target_paths: []`.

Evidence:

- `bridge/gtkb-hygiene-sweep-cli-scoping-002.md:19-23` declares project/work metadata, no implementation authorization, and empty `target_paths`.
- `bridge/gtkb-hygiene-sweep-cli-scoping-002.md:45-53` says the proposal does not authorize implementation and that follow-on implementation bridges are required.
- `bridge/gtkb-hygiene-sweep-cli-scoping-002.md:154-158` makes "does NOT authorize implementation; per-slice bridges required" an acceptance criterion.

Impact: GO on this thread should not be read as permission to edit `config/governance/hygiene-sweep-patterns.toml`, `groundtruth-kb/src/groundtruth_kb/cli.py`, or tests. Those remain future implementation-slice work.

### Advisory - Carry the missing advisory spec into the implementation slice

Observation: Applicability preflight for REVISED-2 passes with no missing required specs, but reports missing advisory spec `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

Evidence:

- Applicability preflight below reports `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`.
- `bridge/gtkb-hygiene-sweep-cli-scoping-002.md:86-107` lists specification links and omits `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

Impact: This advisory omission does not block a scoping GO because required specs and mandatory clauses pass. The implementation proposal should cite or explicitly justify the DCL if the CLI creates lifecycle-triggering inventory, remediation, or artifact-routing behavior.

Recommended action: In the follow-on implementation bridge, include `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` in `Specification Links` if the CLI output participates in lifecycle decisions or child-WI creation workflow.

## Applicability Preflight

- packet_hash: `sha256:0b022a695cbab9d52274a5ff29cc70be2021c34cae1b5f6c20fe2d5e0f77ce7a`
- bridge_document_name: `gtkb-hygiene-sweep-cli-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-hygiene-sweep-cli-scoping-002.md`
- operative_file: `bridge/gtkb-hygiene-sweep-cli-scoping-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-hygiene-sweep-cli-scoping`
- Operative file: `bridge\gtkb-hygiene-sweep-cli-scoping-002.md`
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

## Verification Performed

- Read live `bridge/INDEX.md`; latest status was `REVISED: bridge/gtkb-hygiene-sweep-cli-scoping-002.md`.
- Read `bridge/gtkb-hygiene-sweep-cli-scoping-001.md` and `bridge/gtkb-hygiene-sweep-cli-scoping-002.md`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hygiene-sweep-cli-scoping`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-sweep-cli-scoping`.
- Ran Deliberation Archive searches through `KnowledgeDB.search_deliberations(...)`.

## Prime Builder Implementation Context

Future implementation work needs a new implementation bridge with concrete `target_paths`, project authorization, owner decision evidence where required, and executed tests. This scoping GO does not permit immediate mutation of the CLI, TOML registry, or test files.

