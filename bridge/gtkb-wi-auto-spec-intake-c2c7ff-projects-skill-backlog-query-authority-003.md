NEW

# GT-KB Bridge Implementation Report - gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority - 003

bridge_kind: implementation_report
Document: gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority
Version: 003 (NEW; post-implementation report)
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-AUTO-SPEC-INTAKE-C2C7FF
Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-AUTO-SPEC-INTAKE-C2C7FF-PROJECTS-SKILL-FILTERING
Responds to GO: bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-002.md
Approved proposal: bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-001.md
Implementation-start packet hash: sha256:e045a8a656d01650ecc3b09836a36e32d2fa9d2410a7e78d8bfcbfc4edf9d8dc
Recommended commit type: feat:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f19c4-f49d-7283-8c0c-20fe4ec6fb98
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; filesystem=danger-full-access; owner-declared role=::init gtkb pb
author_metadata_source: implementation_report_content

## Implementation Claim

Implemented the governed backlog/project query surface required by SPEC-INTAKE-c2c7ff.

`gt backlog list` now supports repeatable approval-state filters, generic exact field filters, field-specific glob matching, inclusive ranges, active project-membership filtering, and compound sort keys. `gt projects list` now supports generic exact field filters, field-specific glob matching, and compound sort keys. These filters are exposed through the CLI rather than requiring agents to open `groundtruth.db`, import `KnowledgeDB`, fetch the whole backlog, or post-filter raw MemBase rows locally.

The Projects skill now documents the CLI-only backlog/project access requirement and the new backlog/project query controls. The approved target harness adapters were brought current for `.codex`, `.agent`, `.cursor`, and `.api-harness` with canonical Projects skill hash `b35a7e3cd6c2b4bd3976c15a2b0f78ec37b4663fbe2d5063047c77daf0c778c8`.

## Specification Links

- `SPEC-INTAKE-c2c7ff` - owner-stated requirement: Projects skill/CLI must be the only supported way agents access or update backlog/project information; direct MemBase/SQLite access for backlog/project work is prohibited; query/filter/sort support must cover all backlog values, pattern matching, and range specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation proceeded through proposal, LO GO, work-intent claim, implementation-start authorization, and this implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation is tied to the governing specification and approved bridge proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - report carries project, work item, and project authorization metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps the query-authority requirement to concrete CLI and skill-adapter tests.
- `GOV-STANDING-BACKLOG-001` - the MemBase backlog remains canonical; this adds governed CLI access rather than a second backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - no application-placement authority or Agent Red surface was changed.
- `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Projects skill guidance changes were mirrored across the approved harness adapter paths.

## Owner Decisions / Input

- `DELIB-20260630-PROJECT-BTH-PB-AUTOPROCESS-APPROVAL` authorizes implementation of all active child work items in `PROJECT-BACKLOG-TRIAGE-AND-HYGIENE`, subject to normal governance gates.
- Owner message in this thread clarified that if Codex did not author the GO, Codex may implement it. The GO author metadata identifies `loyal-opposition/antigravity`, harness `C`, session context `3103313d-e759-4636-b3a8-0f99aa71f435`.
- No new owner decision is required by this report.

## Prior Deliberations

- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-001.md` - approved implementation proposal.
- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-002.md` - Loyal Opposition GO verdict.
- Project authorization `PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-AUTO-SPEC-INTAKE-C2C7FF-PROJECTS-SKILL-FILTERING`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-INTAKE-c2c7ff` CLI-only backlog/project access and broad query support | `python -m pytest platform_tests/scripts/test_cli_backlog_list.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py -q --tb=short` passed with 38 tests. Expanded proposal-derived backlog/project pytest set passed with 85 tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge latest status was `GO`; work-intent claim acquired for `go_implementation`; implementation-start packet created with hash `sha256:e045a8a656d01650ecc3b09836a36e32d2fa9d2410a7e78d8bfcbfc4edf9d8dc`; this report is filed through the governed implementation-report helper. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority` passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | New tests cover exact field filters, approval-state filters, pattern filters, range filters, project membership filters, terminal inclusion, sort order, project filter helper behavior, and skill adapter parity. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Approved target paths were limited to GT-KB platform CLI, backlog helper, platform tests, and Projects skill adapters. No application subtree changed for this implementation. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Projects skill adapters for `.codex`, `.agent`, `.cursor`, and `.api-harness` now reference canonical hash `b35a7e3cd6c2b4bd3976c15a2b0f78ec37b4663fbe2d5063047c77daf0c778c8`; scoped adapter parity tests passed. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_cli_backlog_list.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_cli_backlog_add.py platform_tests/scripts/test_cli_backlog_add_work_item.py platform_tests/scripts/test_cli_backlog_authorize_implementation.py platform_tests/scripts/test_cli_backlog_list.py platform_tests/scripts/test_cli_backlog_status.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/backlog.py groundtruth-kb/src/groundtruth_kb/backlog groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_cli_backlog*.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/backlog.py groundtruth-kb/src/groundtruth_kb/backlog groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_cli_backlog*.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority`

## Observed Results

- Focused pytest: `38 passed, 1 warning in 24.31s`.
- Expanded proposal-derived pytest set: `85 passed, 1 warning in 49.17s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `14 files already formatted`.
- Bridge applicability preflight: PASS; `preflight_passed: true`; no missing required specs. Advisory-only missing references remained advisory and non-blocking: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
- ADR/DCL clause preflight: PASS; `must_apply` count 2, evidence gaps 0, blocking gaps 0.
- The literal PowerShell command `python -m pytest platform_tests/scripts/test_cli_backlog*.py ...` failed before collection because PowerShell passed the wildcard literally. The same intended file set was rerun with expanded filenames and passed with 85 tests.

`python scripts/generate_codex_skill_adapters.py --check --update-registry` was not used as the final gate because the current worktree contains unrelated out-of-scope adapter/resource drift outside this project's approved target paths. Instead, `platform_tests/scripts/test_projects_skill_adapter.py` now performs scoped Projects adapter parity checks for the approved paths and passed.

## Files Changed

Implementation-authored changes in approved target paths:

- `groundtruth-kb/src/groundtruth_kb/backlog/query.py` - new governed query helper for backlog/project CLI filtering and sorting.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - added `gt backlog list` query options and `gt projects list` query options wired to the helper.
- `platform_tests/scripts/test_cli_backlog_list.py` - new tests for helper and CLI query behavior.
- `platform_tests/scripts/test_cli_backlog_add.py` - made the changed-by attribution test independent of the host's live durable role assignment by mocking the role resolver.
- `platform_tests/scripts/test_projects_skill_adapter.py` - scoped Projects adapter parity assertions to the approved target adapter paths.
- `.claude/skills/projects/SKILL.md` - documented CLI-only backlog/project access and query examples.
- `.codex/skills/projects/SKILL.md` - mirrored canonical Projects skill body and hash.
- `.agent/skills/projects/SKILL.md` - mirrored canonical Projects skill body and hash.
- `.api-harness/skills/projects/SKILL.md` - updated compact adapter hash references.
- `.cursor/skills/projects/SKILL.md` - mirrored canonical Projects skill body and hash.

Known pre-existing dirty context preserved:

- `groundtruth-kb/src/groundtruth_kb/cli.py` already contained unrelated bridge metadata audit CLI additions in the dirty worktree. Those hunks were preserved and are not claimed as part of this WI implementation.
- The broader repository has many unrelated dirty, deleted, and untracked files. This implementation did not revert or sweep them.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Justification: this adds governed CLI query capability and skill guidance for backlog/project access.

## Acceptance Criteria Status

- [x] `gt backlog list` supports approved exact filters including `approval_state`.
- [x] `gt backlog list` supports generic field filters for surfaced work-item metadata.
- [x] `gt backlog list` supports field-specific glob/pattern matching.
- [x] `gt backlog list` supports inclusive range filters for ordered surfaced fields.
- [x] `gt backlog list` supports active project membership filtering.
- [x] `gt backlog list` supports sort keys.
- [x] `gt projects list` supports generic exact field filters, pattern filters, and sort keys.
- [x] Projects skill docs instruct agents to use the CLI and not direct SQLite/MemBase backlog reads for routine workflows.
- [x] Approved harness Projects skill adapters are current against the canonical skill hash.
- [x] Focused pytest, expanded proposal-derived pytest, ruff check, ruff format check, and bridge preflights passed.

## Risk And Rollback

Residual risk is mainly in generic field vocabulary breadth: the helper exposes surfaced row fields and rejects unsupported fields with clear CLI errors, but future MemBase row fields may need explicit addition if they become part of the supported CLI contract. Rollback is limited to the approved paths listed above: remove `groundtruth_kb.backlog.query`, remove the new CLI options/imports, restore the prior Projects skill text/adapters, and remove or revert the added/scoped tests.

No staging or commit was performed by this implementation report.

## Loyal Opposition Asks

1. Verify that the CLI query surface satisfies `SPEC-INTAKE-c2c7ff` without creating a second backlog authority.
2. Verify that the skill guidance is clear enough to route agents away from direct SQLite/MemBase backlog reads for routine backlog/project workflows.
3. Return `VERIFIED` if the implementation satisfies the approved proposal, otherwise return `NO-GO` with concrete findings.
