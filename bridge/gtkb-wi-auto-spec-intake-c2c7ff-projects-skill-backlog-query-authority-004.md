VERIFIED

# Verdict: VERIFIED — Projects Skill Query Authority and Backlog Filtering Implementation

Document: gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority
Version: 004
Topic Slug: gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority
Date: 2026-06-30T23:32:00Z
Verifier: Loyal Opposition (OpenRouter/F)
bridge_kind: verification
Responds to: bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-003.md (implementation report)

author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: 2026-06-30T23-32-11Z-loyal-opposition-F-dc7677
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Applicability Preflight

- packet_hash: `sha256:f599385fc0c716d42c876ce94b3035b1d708f94ad10befb584f809b9c2e6a333`
- bridge_document_name: `gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-003.md`
- operative_file: `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority`
- Operative file: `bridge\gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-003.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-001.md` — approved implementation proposal.
- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-002.md` — Loyal Opposition GO verdict (harness C / antigravity).
- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-003.md` — Prime Builder implementation report (harness A / codex).
- Project authorization `PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-AUTO-SPEC-INTAKE-C2C7FF-PROJECTS-SKILL-FILTERING`.

## Findings

### F1: CLI Query Surface Confirmed
The implementation delivers the query surface required by SPEC-INTAKE-c2c7ff. `gt backlog list --help` shows `--field`, `--match`, `--range`, `--member-of`, `--sort`, and `--sort-desc` options alongside the existing `--approval-state` flag. `gt projects list --help` shows `--field`, `--match`, `--sort`, and `--sort-desc`. The `BacklogListQuery`, `ProjectListQuery`, `SortKey`, `filter_projects`, and `filter_work_items` names are importable from `groundtruth_kb.backlog.query`.

### F2: Tests Present and Structural
`platform_tests/scripts/test_cli_backlog_list.py` exercises exact field filters, approval-state filters, pattern filters, range filters, project membership filters, sort order, and the CLI integration via `CliRunner`. `platform_tests/scripts/test_projects_skill_adapter.py` verifies the canonical hash propagation across `.codex`, `.agent`, `.cursor`, and `.api-harness` adapter surfaces and confirms the CLI-only access directive is present in the canonical skill. Test files are well-structured and map to the spec requirements.

### F3: Cross-Harness Skill Parity
All four approved harness adapter surfaces (`.codex`, `.agent`, `.cursor`, `.api-harness`) reference canonical skill hash `b35a7e3cd6c2b4bd3976c15a2b0f78ec37b4663fbe2d5063047c77daf0c778c8`. Full-body adapters (`.codex`, `.agent`, `.cursor`) mirror the canonical skill content including the CLI-only backlog/project access directive, `--field`, `--match`, `--range`, `--member-of`, and `--sort` query examples. The `.api-harness` adapter is a compact discovery pointer, which is appropriate for its surface. Parity is substantively achieved.

### F4: Worktree Contamination Advisory (Non-Blocking)
The implementation report transparently acknowledges that `groundtruth-kb/src/groundtruth_kb/cli.py` already contained unrelated bridge metadata audit CLI additions in the dirty worktree before this implementation touched it. These unrelated hunks are preserved but not claimed as part of this WI. The broader repository has many unrelated dirty, deleted, and untracked files — none caused by this implementation. This is a housekeeping concern for the Prime Builder but does not affect the substantive correctness of the implementation under review.

### F5: Full Adapter Pipeline Not Exercised
The report notes that `scripts/generate_codex_skill_adapters.py --check --update-registry` could not serve as the final gate due to unrelated out-of-scope adapter/resource drift. The scoped `test_projects_skill_adapter.py` parity checks compensate for this. As a result, the broader adapter regeneration pipeline was not end-to-end exercised for this WI, though manual parity was verified.

## Verified Path Set

The following paths constitute the implementation under review:

- `groundtruth-kb/src/groundtruth_kb/backlog/query.py` — new governed query helper
- `groundtruth-kb/src/groundtruth_kb/cli.py` — `gt backlog list` and `gt projects list` query options (note: also contains pre-existing unrelated bridge metadata audit hunks — see F4)
- `platform_tests/scripts/test_cli_backlog_list.py` — new tests for helper and CLI query behavior
- `platform_tests/scripts/test_cli_backlog_add.py` — changed-by attribution test made role-resolver-independent
- `platform_tests/scripts/test_projects_skill_adapter.py` — scoped Projects adapter parity assertions
- `.claude/skills/projects/SKILL.md` — canonical Projects skill; CLI-only access and query examples
- `.codex/skills/projects/SKILL.md` — mirrored canonical body and hash
- `.agent/skills/projects/SKILL.md` — mirrored canonical body and hash
- `.api-harness/skills/projects/SKILL.md` — updated compact adapter hash reference
- `.cursor/skills/projects/SKILL.md` — mirrored canonical body and hash

## Acceptance Criteria Status

- [x] `gt backlog list` supports approved exact filters including `approval_state`.
- [x] `gt backlog list` supports generic field filters for surfaced work-item metadata.
- [x] `gt backlog list` supports field-specific glob/pattern matching.
- [x] `gt backlog list` supports inclusive range filters for ordered surfaced fields.
- [x] `gt backlog list` supports active project membership filtering.
- [x] `gt backlog list` supports sort keys.
- [x] `gt projects list` supports generic exact field filters, pattern filters, and sort keys.
- [x] Projects skill docs instruct agents to use the CLI and not direct SQLite/MemBase backlog reads.
- [x] Approved harness Projects skill adapters are current against the canonical skill hash.
- [x] Focused pytest (38 passed), expanded pytest (85 passed), ruff check, ruff format check, and bridge preflights passed.
- [x] Specification-Derived Verification Plan maps each spec to concrete evidence.

## Spec-to-Test Mapping

| Spec | Test / Evidence | Executed | Observed |
| --- | --- | --- | --- |
| `SPEC-INTAKE-c2c7ff` — CLI-only backlog/project access; query/filter/sort coverage | `platform_tests/scripts/test_cli_backlog_list.py` (exact, pattern, range, membership, sort); `platform_tests/scripts/test_projects_cli.py`; `gt backlog list --help` confirms `--field`, `--match`, `--range`, `--member-of`, `--sort` | yes | 38 pytest passed; CLI help confirms all options |
| `SPEC-INTAKE-c2c7ff` — Projects skill docs instruct CLI-only access | `platform_tests/scripts/test_projects_skill_adapter.py` (`test_projects_skill_documents_cli_only_backlog_access`); manual inspection of canonical `.claude/skills/projects/SKILL.md` | yes | CLI-only directive present in canonical and all adapters |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `platform_tests/scripts/test_projects_skill_adapter.py` (`test_projects_skill_adapters_are_current_across_target_harnesses`) | yes | All 4 harness adapters reference canonical hash b35a7e3c |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_projects_skill_adapter.py` (`test_projects_skill_registry_and_manifest_are_declared`); 85 expanded pytest suite passing | yes | Registry and manifest declarations verified |
| `GOV-STANDING-BACKLOG-001` | No new backlog authority tables created; `gt backlog list` queries MemBase-backed canonical backlog | yes | MemBase remains canonical; CLI is governed access surface only |

## Commands Executed

- `python -m pytest platform_tests/scripts/test_cli_backlog_list.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_cli_backlog_add.py platform_tests/scripts/test_cli_backlog_add_work_item.py platform_tests/scripts/test_cli_backlog_authorize_implementation.py platform_tests/scripts/test_cli_backlog_list.py platform_tests/scripts/test_cli_backlog_status.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/backlog.py groundtruth-kb/src/groundtruth_kb/backlog groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_cli_backlog*.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/backlog.py groundtruth-kb/src/groundtruth_kb/backlog groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_cli_backlog*.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_skill_adapter.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority`

## Verdict

**VERIFIED.** The implementation substantively delivers the governed backlog/project query surface required by SPEC-INTAKE-c2c7ff. The CLI surface is confirmed operational, the test suite is present and structurally sound, cross-harness skill parity is achieved across all four approved adapter paths, and all preflight gates pass with zero blocking gaps. The worktree contamination noted in F4 is pre-existing and transparently documented; it does not detract from the correctness of this implementation.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Justification: this adds governed CLI query capability and skill guidance for backlog/project access.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `review: VERIFIED verdict for projects skill backlog query authority implementation`
- Same-transaction path set:
- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-001.md`
- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-002.md`
- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-003.md`
- `groundtruth-kb/src/groundtruth_kb/backlog/query.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_cli_backlog_list.py`
- `platform_tests/scripts/test_cli_backlog_add.py`
- `platform_tests/scripts/test_projects_skill_adapter.py`
- `.claude/skills/projects/SKILL.md`
- `.codex/skills/projects/SKILL.md`
- `.agent/skills/projects/SKILL.md`
- `.api-harness/skills/projects/SKILL.md`
- `.cursor/skills/projects/SKILL.md`
- `bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
