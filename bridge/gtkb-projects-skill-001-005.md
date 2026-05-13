NEW

# GT-KB Bridge Implementation Report - gtkb-projects-skill-001 - 005

bridge_kind: implementation_report
Document: gtkb-projects-skill-001
Version: 005 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A, pb dispatch)
Date: 2026-05-13 UTC
Work Item: WI-3259
Responds to GO: bridge/gtkb-projects-skill-001-004.md
Approved proposal: bridge/gtkb-projects-skill-001-003.md
Recommended commit type: feat:

## Implementation Claim

Implemented the approved Projects Skill + `gt projects` lifecycle surface.

The implementation adds a deterministic `ProjectLifecycleService` over existing
MemBase project, project-work-item membership, dependency, and artifact-link
tables. It extends the plural `gt projects` CLI group with:

- `create`
- `show`
- `list`
- `update`
- `add-item`
- `reorder`
- `retire`
- `link-bridge`

The implementation also adds the canonical Claude `projects` skill, registers
`skill.projects` in the harness capability registry, regenerates the Codex
adapter and manifest, and adds focused tests for CLI lifecycle behavior and
adapter parity.

No database schema, new project table, new backlog authority, or `bridge/INDEX.md`
mutation behavior was added to `gt projects link-bridge`. The command records a
MemBase project artifact link with `artifact_type="bridge_thread"` only.

## Implementation Authorization

Prime Builder created the required implementation-start authorization packet
before protected implementation edits.

Command:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python scripts/implementation_authorization.py begin --bridge-id gtkb-projects-skill-001
```

Observed:

- latest_status: `GO`
- proposal_file: `bridge/gtkb-projects-skill-001-003.md`
- go_file: `bridge/gtkb-projects-skill-001-004.md`
- requirement_sufficiency: `sufficient`
- packet_hash: `sha256:10b3d5a2480245242036ce9cdc1cfd8984c4784be8c277e05d6c37c27509fe87`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`
- `DCL-CONCEPT-ON-CONTACT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`

## Owner Decisions / Input

- Owner current-priority heartbeat on 2026-05-13 identified
  `GTKB-DETERMINISTIC-SERVICES-001` as the active project and listed `WI-3259`
  as the next safe P1 item after the topology-deferred `WI-3265`.
- `WI-3259` was created under owner-directed umbrella project creation on
  2026-05-10 and names the exact target: "Projects skill + gt projects CLI group
  (8 verbs: create/show/list/update/add-item/reorder/retire/link-bridge)."
- No new owner decision was required during implementation.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports moving repetitive AI
  procedure into deterministic service-mediated infrastructure.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - supports MemBase-backed
  backlog/project authority.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - supports Codex harness
  parity and generated adapter coverage.
- `DELIB-1564` and `DELIB-1565` - precedent for canonical Claude skill bodies
  with generated Codex adapters.
- `DELIB-1791` - backlog-source review history reinforcing no second backlog
  authority.
- `bridge/gtkb-projects-skill-001-003.md` - approved implementation proposal.
- `bridge/gtkb-projects-skill-001-004.md` - Loyal Opposition GO verdict.

## Files Changed

Implementation-scoped files changed:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/project/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `.claude/skills/projects/SKILL.md`
- `.codex/skills/projects/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/scripts/test_projects_cli.py`
- `platform_tests/scripts/test_projects_skill_adapter.py`

Out-of-scope dirty worktree note:

The implementation-report helper's `plan` mode detected many pre-existing dirty
files unrelated to this GO scope. This report claims only the implementation
files listed above.

## Implementation Details

### Project lifecycle service

`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` adds
`ProjectLifecycleService`, a thin deterministic service over existing
`KnowledgeDB` methods:

- `create_project` calls `KnowledgeDB.insert_project`.
- `list_projects` calls `KnowledgeDB.list_projects`.
- `show_project` returns the current project with work items, dependencies, and
  artifact links.
- `update_project` appends a new project version by carrying forward unchanged
  fields and calling `insert_project` with the existing project id.
- `add_project_item` calls `KnowledgeDB.link_project_work_item`.
- `reorder_project_items` appends new membership versions for the active
  membership set inside one selected project only.
- `retire_project` appends a terminal project version with `status="retired"`.
- `link_bridge_thread` calls `KnowledgeDB.add_project_artifact_link` with
  `artifact_type="bridge_thread"`.

The service intentionally does not add DB tables and does not edit `db.py`.

### CLI verbs

`groundtruth-kb/src/groundtruth_kb/cli.py` now routes `gt projects` through the
service. Existing `list` and `show` remain backward compatible. New mutating
verbs require `--change-reason` and support `--json` output.

### Skill surfaces and parity registry

`.claude/skills/projects/SKILL.md` is the canonical source. It defers terminology
to `.claude/rules/operating-model.md` and `.claude/rules/canonical-terminology.md`,
states the no-second-backlog-authority boundary, and documents safe command use.

`config/agent-control/harness-capability-registry.toml` now includes
`skill.projects`. `scripts/generate_codex_skill_adapters.py --update-registry`
generated `.codex/skills/projects/SKILL.md`, updated
`.codex/skills/MANIFEST.json`, and stamped the registry `source_sha256`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is being filed through the bridge helper as `NEW: bridge/gtkb-projects-skill-001-005.md`, preserving `bridge/INDEX.md` as queue authority. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | GO proposal links are carried forward in this report; implementation authorization was created from the live latest GO. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused CLI, adapter, parity, and governing-spec tests executed and are mapped in this table. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed implementation files are under `E:\GT-KB`; tests used temporary in-root pytest directories and no external checkout. |
| `GOV-STANDING-BACKLOG-001` | `test_projects_lifecycle_cli_preserves_append_only_versions` verifies project operations organize existing work items without replacing work-item authority. |
| `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` | `test_projects_lifecycle_cli_preserves_append_only_versions` verifies existing MemBase project and membership tables are used and append-only versions are preserved. |
| `DCL-CONCEPT-ON-CONTACT-001` | `test_projects_skill_adapter.py` verifies the skill surface preserves the terminology deferral and no-second-backlog-authority language. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q` passed with the new `skill.projects` registry entry. |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | `python scripts/generate_codex_skill_adapters.py --check --update-registry` and `test_projects_skill_adapter.py` passed. |
| `.claude/rules/file-bridge-protocol.md` | Implementation authorization packet was created before protected edits; this report carries spec links, command evidence, files changed, and acceptance status. |
| `.claude/rules/codex-review-gate.md` | Work began only after latest GO and local authorization packet; report is filed for Loyal Opposition verification. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Project lifecycle operations preserve durable MemBase records and this bridge report preserves implementation evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The work replaces repeated manual project lifecycle edits with deterministic service and CLI artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No formal artifact mutation outside the approved skill/registry/test scope was performed. |
| `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` | Implementation files, tests, and linked requirements are mapped in this report. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Existing governing-spec preservation tests passed after the new surface landed. |
| `.claude/rules/operating-model.md` | The skill and CLI preserve project/work item/backlog terminology and do not treat project as application. |
| `.claude/rules/canonical-terminology.md` | Skill and CLI text defer glossary authority to the canonical terminology rule. |

## Commands Run

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python scripts/implementation_authorization.py begin --bridge-id gtkb-projects-skill-001
python -m compileall -q groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py
python -m pytest platform_tests/scripts/test_projects_cli.py -q
python scripts/generate_codex_skill_adapters.py --check --update-registry
python -m pytest platform_tests/scripts/test_projects_skill_adapter.py -q
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/project/__init__.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_projects_skill_adapter.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/project/__init__.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_projects_skill_adapter.py
```

## Observed Results

- Implementation authorization: passed; latest status `GO`, proposal `-003`, GO
  file `-004`, requirement sufficiency `sufficient`.
- `compileall`: passed with no output.
- `python -m pytest platform_tests/scripts/test_projects_cli.py -q`: 3 passed,
  1 ChromaDB deprecation warning.
- `python scripts/generate_codex_skill_adapters.py --check --update-registry`:
  `Codex skill adapters: PASS (27 adapters current)`.
- `python -m pytest platform_tests/scripts/test_projects_skill_adapter.py -q`:
  3 passed.
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q`:
  6 passed.
- `python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q`:
  8 passed, 1 ChromaDB deprecation warning.
- Targeted Ruff check: `All checks passed!`
- Targeted Ruff format check: `5 files already formatted`

## Acceptance Criteria Status

- [x] `gt projects create/show/list/update/add-item/reorder/retire/link-bridge`
  exists and uses the existing MemBase project tables.
- [x] Mutating commands preserve append-only versioning and require useful
  change reasons.
- [x] `gt projects show --json` returns project, work_items, dependencies, and
  artifact_links.
- [x] `gt projects link-bridge` records a bridge-thread artifact link without
  editing `bridge/INDEX.md`.
- [x] `.claude/skills/projects/SKILL.md` exists and
  `.codex/skills/projects/SKILL.md` is generated from it.
- [x] Harness capability registry includes `skill.projects` and adapter check
  passes.
- [x] Spec-derived tests pass and are reported in this post-implementation
  bridge report.
- [ ] Loyal Opposition verification remains pending on this report.

## Bulk-Operation Visibility Condition

The implementation respects the GO verdict's bulk-operation condition:

- `add-item` accepts one explicit work item id.
- `reorder` operates on one project id and requires the caller to name that
  project's active membership set exactly.
- No multi-project operation, bulk work-item rewrite, or second backlog authority
  was introduced.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Justification: the scoped implementation adds a deterministic lifecycle
  service, new CLI verbs, a canonical skill, generated adapter parity, and
  focused tests.

## Risk And Rollback

Residual risk is low and centered on CLI semantics for future operator
workflows. The implementation is bounded by focused tests and does not change
the database schema or backlog authority tables.

Rollback path:

1. Revert the implementation-scoped files listed above.
2. Regenerate Codex adapters if the registry or canonical skill is reverted.
3. Preserve bridge audit files and `bridge/INDEX.md` append-only history.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed
   command evidence.
2. Confirm no second backlog/project authority was introduced.
3. Confirm `gt projects link-bridge` does not mutate `bridge/INDEX.md`.
4. Return `VERIFIED` if the report and implementation satisfy the approved
   proposal; otherwise return `NO-GO` with findings.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
