VERIFIED

# Loyal Opposition Verification - Projects Skill + gt projects Lifecycle Commands

bridge_kind: loyal_opposition_verdict
Document: gtkb-projects-skill-001
Version: 007
Reviewer: Codex (harness A, Loyal Opposition dispatch mode)
Date: 2026-05-13 UTC
Reviewed report: `bridge/gtkb-projects-skill-001-006.md`
Prior GO: `bridge/gtkb-projects-skill-001-004.md`
Verdict: VERIFIED

## Claim

The implementation report is verified. The approved project lifecycle service,
plural `gt projects` CLI surface, canonical Claude `projects` skill, generated
Codex adapter, registry entry, and focused tests are present in the live
worktree and satisfy the approved proposal scope.

No blocking findings remain. The implementation preserves the no-second-backlog
authority boundary by wrapping the existing MemBase project, membership,
dependency, artifact-link, and `current_work_items` surfaces. `gt projects
link-bridge` records a project artifact link and does not mutate
`bridge/INDEX.md`.

## Review Scope

- Live `bridge/INDEX.md` showed `gtkb-projects-skill-001` latest status `NEW`
  at `bridge/gtkb-projects-skill-001-006.md` before this verdict.
- Durable role resolution maps Codex to harness `A`; harness `A` has both
  `loyal-opposition` and `prime-builder`, and this dispatch carried mode `lo`.
- I reviewed the full version chain:
  `bridge/gtkb-projects-skill-001-001.md` through
  `bridge/gtkb-projects-skill-001-006.md`.
- The broader worktree has many unrelated staged/dirty files. Verification here
  is scoped to the files claimed by `-006` and their already-VERIFIED dependency
  on `gtkb-first-class-project-artifacts`.

## Applicability Preflight

- packet_hash: `sha256:168c332ca1d40ba1c57b7701ef34cdd9376adcd5cf6071cdc91a54808327430e`
- bridge_document_name: `gtkb-projects-skill-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-projects-skill-001-006.md`
- operative_file: `bridge/gtkb-projects-skill-001-006.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-projects-skill-001`
- Operative file: `bridge\gtkb-projects-skill-001-006.md`
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
must_apply applicability fail the gate (exit 5) when evidence is absent and no
`Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with
`enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Deliberation searches were run before verification for `WI-3259`, projects
skill lifecycle work, deterministic services, MemBase backlog authority, and
harness skill adapter parity.

Relevant records and thread evidence:

- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` supports MemBase-backed
  backlog/project authority and the no-fragmentation constraint.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` supports generated Codex
  adapter parity.
- `DELIB-1564` and `DELIB-1565` are relevant precedent for canonical Claude
  skill bodies with generated Codex adapters.
- `DELIB-1791` is relevant backlog-source review history and reinforces no
  second backlog authority.
- Direct `WI-3259` deliberation linkage search returned no matching rows.

No reviewed deliberation contradicts verification of this implementation.

## Verification Evidence

Source inspection:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:29` defines
  `ProjectLifecycleService`.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:75` lists existing
  MemBase projects through `KnowledgeDB.list_projects`.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:78` returns project,
  work items, dependencies, and artifact links.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:89` appends project
  updates through `insert_project`.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:170` requires reorder
  to name the active membership set exactly before appending membership
  versions.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:240` records bridge
  links through `KnowledgeDB.add_project_artifact_link` with
  `artifact_type="bridge_thread"`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:462` through `:841` exposes
  `list`, `show`, `create`, `update`, `add-item`, `reorder`, `retire`, and
  `link-bridge`; mutating commands require `--change-reason`.
- `.claude/skills/projects/SKILL.md:11` through `:21` defers authority to the
  operating model and canonical terminology and rejects a second backlog
  authority.
- `.codex/skills/projects/SKILL.md:5` through `:12` marks the Codex skill as a
  generated adapter from `.claude/skills/projects/SKILL.md`.
- `config/agent-control/harness-capability-registry.toml:349` through `:365`
  registers `skill.projects` and points Codex at the generated adapter.
- `.codex/skills/MANIFEST.json:136` through `:142` includes the
  `skill.projects` adapter entry.

Executed checks:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-skill-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-skill-001
python -m compileall -q groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py
python -m pytest platform_tests/scripts/test_projects_cli.py -q
python -m pytest platform_tests/scripts/test_projects_skill_adapter.py -q
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q
python scripts/generate_codex_skill_adapters.py --check --update-registry
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/project/__init__.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_projects_skill_adapter.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/project/__init__.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_projects_skill_adapter.py
git diff --cached --check -- <implementation-scoped files>
```

Observed results:

- Applicability preflight: PASS; `missing_required_specs: []`;
  `missing_advisory_specs: []`.
- Clause preflight: PASS; evidence gaps `0`; blocking gaps `0`.
- Compileall: passed with no output.
- Projects CLI tests: `3 passed`, 1 ChromaDB deprecation warning.
- Projects skill adapter tests: `3 passed`.
- Harness parity tests: `6 passed`.
- Governing-spec preservation tests: `8 passed`, 1 ChromaDB deprecation warning.
- Adapter generation check: `Codex skill adapters: PASS (27 adapters current)`.
- Ruff check: `All checks passed!`.
- Ruff format check: `5 files already formatted`.
- Diff whitespace check: passed with no output.

## Acceptance Criteria Disposition

- `gt projects create/show/list/update/add-item/reorder/retire/link-bridge`:
  verified in CLI code and tests.
- Existing MemBase project tables used, no second backlog authority created:
  verified by service inspection and by the already-VERIFIED
  `gtkb-first-class-project-artifacts` dependency.
- Append-only project and membership versions: verified by
  `test_projects_lifecycle_cli_preserves_append_only_versions`.
- `gt projects show --json` returns project, work items, dependencies, and
  artifact links: verified by CLI implementation and tests.
- `gt projects link-bridge` does not edit `bridge/INDEX.md`: verified by
  `test_projects_link_bridge_records_artifact_without_editing_bridge_index`.
- Canonical Claude skill and generated Codex adapter: verified by source
  inspection, registry/manifest inspection, adapter check, and adapter tests.
- Bulk-operation visibility condition: satisfied by the `-006` report section
  and by implementation/tests requiring one explicit work item for `add-item`
  and exact active membership-set naming for `reorder`.
- Bulk-operation future guard: any future bulk project/work-item operation must
  produce an inventory artifact, review packet, and `DECISION DEFERRED` marker
  before apply, unless a future explicit formal-artifact-approval packet
  authorizes that bulk action.
- Recommended commit type `feat:` matches the net-new service, CLI verbs, skill,
  adapter, and tests.

## Findings

No blocking findings.

## Post-Write Sanity Check

After inserting this verdict in `bridge/INDEX.md`, the live document entry lists
`VERIFIED: bridge/gtkb-projects-skill-001-007.md` above the two implementation
report `NEW` rows. Post-write mechanical checks also pass:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-skill-001`
  still resolves the operative implementation report `-006` and reports
  `preflight_passed: true`, `missing_required_specs: []`, and
  `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-skill-001`
  evaluates this `-007` verdict with evidence gaps `0` and blocking gaps `0`.

## Result

VERIFIED. `gtkb-projects-skill-001` satisfies the approved implementation scope
and may be treated as closed for this bridge thread.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
